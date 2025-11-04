"""
Real-time Speech-to-Text using OpenAI Realtime API.
Supports bi-directional audio streaming and function calling.
"""

import asyncio
import json
import base64
from typing import Optional, Callable, Dict, Any
import websockets
from loguru import logger


class RealtimeSTT:
    """
    OpenAI Realtime API client for streaming speech recognition.
    Supports audio input/output and function calling.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-realtime-preview-2024-10-01",
        voice: str = "alloy",
        temperature: float = 0.8,
        on_transcript: Optional[Callable[[str], None]] = None,
        on_audio: Optional[Callable[[bytes], None]] = None,
        on_function_call: Optional[Callable[[str, Dict[str, Any]], Any]] = None
    ):
        """
        Initialize Realtime STT client.
        
        Args:
            api_key: OpenAI API key
            model: Model to use
            voice: Voice for TTS responses
            temperature: Response temperature
            on_transcript: Callback for transcribed text
            on_audio: Callback for audio responses
            on_function_call: Callback for function calls
        """
        self.api_key = api_key
        self.model = model
        self.voice = voice
        self.temperature = temperature
        
        self.on_transcript = on_transcript
        self.on_audio = on_audio
        self.on_function_call = on_function_call
        
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.is_connected = False
        
        logger.info(f"RealtimeSTT initialized: model={model}, voice={voice}")

    async def connect(self) -> None:
        """Connect to OpenAI Realtime API."""
        try:
            url = f"wss://api.openai.com/v1/realtime?model={self.model}"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "OpenAI-Beta": "realtime=v1"
            }
            
            self.ws = await websockets.connect(url, extra_headers=headers)
            self.is_connected = True
            
            # Configure session
            await self._configure_session()
            
            logger.info("Connected to OpenAI Realtime API")
        except Exception as e:
            logger.error(f"Failed to connect to Realtime API: {e}")
            raise

    async def _configure_session(self) -> None:
        """Configure the Realtime session."""
        config = {
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "voice": self.voice,
                "temperature": self.temperature,
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 500
                }
            }
        }
        await self.ws.send(json.dumps(config))

    async def send_audio(self, audio_data: bytes) -> None:
        """
        Send audio data to the API.
        
        Args:
            audio_data: Raw audio bytes (PCM16, 24kHz, mono)
        """
        if not self.is_connected or not self.ws:
            raise RuntimeError("Not connected to Realtime API")
        
        # Base64 encode audio
        audio_b64 = base64.b64encode(audio_data).decode()
        
        message = {
            "type": "input_audio_buffer.append",
            "audio": audio_b64
        }
        await self.ws.send(json.dumps(message))

    async def commit_audio(self) -> None:
        """Commit audio buffer for processing."""
        if not self.is_connected or not self.ws:
            return
        
        message = {"type": "input_audio_buffer.commit"}
        await self.ws.send(json.dumps(message))

    async def add_function(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any]
    ) -> None:
        """
        Register a function for function calling.
        
        Args:
            name: Function name
            description: Function description
            parameters: JSON schema for parameters
        """
        message = {
            "type": "session.update",
            "session": {
                "tools": [{
                    "type": "function",
                    "name": name,
                    "description": description,
                    "parameters": parameters
                }]
            }
        }
        await self.ws.send(json.dumps(message))
        logger.debug(f"Registered function: {name}")

    async def listen(self) -> None:
        """Listen for messages from the API."""
        if not self.ws:
            return
        
        try:
            async for message in self.ws:
                await self._handle_message(json.loads(message))
        except websockets.exceptions.ConnectionClosed:
            logger.info("Realtime API connection closed")
            self.is_connected = False
        except Exception as e:
            logger.error(f"Error in listen loop: {e}")
            raise

    async def _handle_message(self, message: Dict[str, Any]) -> None:
        """
        Handle incoming messages from API.
        
        Args:
            message: Parsed JSON message
        """
        msg_type = message.get("type")
        
        if msg_type == "conversation.item.input_audio_transcription.completed":
            # Transcript received
            transcript = message.get("transcript", "")
            logger.debug(f"Transcript: {transcript}")
            if self.on_transcript:
                self.on_transcript(transcript)
        
        elif msg_type == "response.audio.delta":
            # Audio response chunk
            audio_b64 = message.get("delta", "")
            audio_data = base64.b64decode(audio_b64)
            if self.on_audio:
                self.on_audio(audio_data)
        
        elif msg_type == "response.function_call_arguments.done":
            # Function call completed
            name = message.get("name")
            arguments = json.loads(message.get("arguments", "{}"))
            logger.debug(f"Function call: {name}({arguments})")
            
            if self.on_function_call:
                result = self.on_function_call(name, arguments)
                await self._send_function_result(
                    message.get("call_id"),
                    result
                )
        
        elif msg_type == "error":
            error = message.get("error", {})
            logger.error(f"Realtime API error: {error}")

    async def _send_function_result(
        self,
        call_id: str,
        result: Any
    ) -> None:
        """
        Send function call result back to API.
        
        Args:
            call_id: Function call ID
            result: Function result
        """
        message = {
            "type": "conversation.item.create",
            "item": {
                "type": "function_call_output",
                "call_id": call_id,
                "output": json.dumps(result)
            }
        }
        await self.ws.send(json.dumps(message))

    async def disconnect(self) -> None:
        """Disconnect from the API."""
        if self.ws:
            await self.ws.close()
            self.is_connected = False
            logger.info("Disconnected from Realtime API")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()





