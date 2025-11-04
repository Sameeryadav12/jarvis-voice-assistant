"""
Quick Dictation Skills

Features:
- Voice-to-text in any app
- System clipboard integration
- Punctuation control
- Format commands (bold, italic, etc.)
"""

import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
import re
from loguru import logger
import pyperclip
import time

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ..nlu.intents import Intent, IntentType
from ..nlu.router import SkillResult


class DictationSkills:
    """
    Quick dictation skills for voice-to-text conversion.
    
    Features:
    - Clipboard integration for universal text input
    - Punctuation control
    - Format commands
    - Text manipulation
    """
    
    def __init__(self):
        """Initialize dictation skills."""
        self.current_text = ""
        self.formatted_text = ""
        self.format_stack: List[str] = []
        logger.info("DictationSkills initialized")
    
    def start_dictation(self) -> SkillResult:
        """
        Start dictation mode (clear buffer).
        
        Returns:
            Skill result
        """
        self.current_text = ""
        self.formatted_text = ""
        self.format_stack.clear()
        
        return SkillResult(
            success=True,
            message="Dictation mode started. Speak your text."
        )
    
    def append_text(
        self,
        text: str,
        apply_punctuation: bool = True,
    ) -> SkillResult:
        """
        Append text to dictation buffer.
        
        Args:
            text: Text to append
            apply_punctuation: Whether to auto-apply punctuation rules
            
        Returns:
            Skill result
        """
        if apply_punctuation:
            text = self._apply_punctuation_rules(text)
        
        self.current_text += text + " "
        self.formatted_text += text + " "
        
        return SkillResult(
            success=True,
            message=f"Added text: {text[:50]}...",
            data={"current_length": len(self.current_text)}
        )
    
    def _apply_punctuation_rules(self, text: str) -> str:
        """
        Apply automatic punctuation rules.
        
        Args:
            text: Input text
            
        Returns:
            Text with punctuation applied
        """
        # Capitalize sentence starts
        if not self.current_text or self.current_text[-1] in '.!?':
            text = text.capitalize()
        
        # Add period at end if not punctuation
        if text and text[-1] not in '.!?,;:':
            # Check if it sounds like end of sentence
            if any(word in text.lower() for word in ['period', 'stop', 'done']):
                text = text.rstrip('period stop done') + '.'
        
        return text
    
    def add_punctuation(self, punctuation: str) -> SkillResult:
        """
        Add explicit punctuation.
        
        Args:
            punctuation: Punctuation mark (period, comma, exclamation, question)
            
        Returns:
            Skill result
        """
        punctuation_map = {
            "period": ".",
            "comma": ",",
            "exclamation": "!",
            "question": "?",
            "colon": ":",
            "semicolon": ";",
        }
        
        punct = punctuation_map.get(punctuation.lower(), punctuation)
        
        if self.current_text:
            self.current_text = self.current_text.rstrip() + punct + " "
            self.formatted_text = self.formatted_text.rstrip() + punct + " "
        
        return SkillResult(
            success=True,
            message=f"Added {punctuation}"
        )
    
    def start_format(self, format_type: str) -> SkillResult:
        """
        Start formatting (bold, italic, etc.).
        
        Args:
            format_type: Format type (bold, italic, underline)
            
        Returns:
            Skill result
        """
        format_map = {
            "bold": "**",
            "italic": "*",
            "underline": "__",
            "code": "`",
        }
        
        marker = format_map.get(format_type.lower(), "")
        
        if marker:
            self.format_stack.append(format_type.lower())
            self.formatted_text += marker
        
        return SkillResult(
            success=True,
            message=f"Started {format_type} formatting"
        )
    
    def end_format(self) -> SkillResult:
        """
        End current formatting.
        
        Returns:
            Skill result
        """
        if not self.format_stack:
            return SkillResult(
                success=False,
                message="No active formatting to end"
            )
        
        format_type = self.format_stack.pop()
        format_map = {
            "bold": "**",
            "italic": "*",
            "underline": "__",
            "code": "`",
        }
        
        marker = format_map.get(format_type, "")
        if marker:
            self.formatted_text += marker
        
        return SkillResult(
            success=True,
            message="Ended formatting"
        )
    
    def insert_to_clipboard(
        self,
        use_formatting: bool = False,
        simulate_paste: bool = False,
    ) -> SkillResult:
        """
        Insert text to clipboard and optionally paste.
        
        Args:
            use_formatting: Whether to use formatted text
            simulate_paste: Whether to simulate Ctrl+V (requires pyautogui)
            
        Returns:
            Skill result
        """
        try:
            text = self.formatted_text if use_formatting else self.current_text
            text = text.strip()
            
            if not text:
                return SkillResult(
                    success=False,
                    message="No text to insert"
                )
            
            # Copy to clipboard
            pyperclip.copy(text)
            logger.info(f"Copied {len(text)} characters to clipboard")
            
            result_message = f"Copied {len(text)} characters to clipboard"
            
            # Simulate paste if requested
            if simulate_paste:
                try:
                    import pyautogui
                    pyautogui.hotkey('ctrl', 'v')
                    result_message += " and pasted"
                except ImportError:
                    logger.warning("pyautogui not available, cannot simulate paste")
                except Exception as e:
                    logger.error(f"Failed to simulate paste: {e}")
            
            # Clear buffer after insertion
            self.current_text = ""
            self.formatted_text = ""
            self.format_stack.clear()
            
            return SkillResult(
                success=True,
                message=result_message,
                data={"text_length": len(text)}
            )
        
        except Exception as e:
            logger.error(f"Failed to insert to clipboard: {e}")
            return SkillResult(
                success=False,
                message=f"Failed to insert text: {str(e)}"
            )
    
    def clear_dictation(self) -> SkillResult:
        """
        Clear dictation buffer.
        
        Returns:
            Skill result
        """
        self.current_text = ""
        self.formatted_text = ""
        self.format_stack.clear()
        
        return SkillResult(
            success=True,
            message="Dictation buffer cleared"
        )
    
    def get_current_text(self) -> SkillResult:
        """
        Get current dictation text.
        
        Returns:
            Skill result with current text
        """
        return SkillResult(
            success=True,
            message=f"Current text: {self.current_text[:100]}...",
            data={"text": self.current_text, "length": len(self.current_text)}
        )
    
    def delete_word(self, count: int = 1) -> SkillResult:
        """
        Delete last N words.
        
        Args:
            count: Number of words to delete
            
        Returns:
            Skill result
        """
        words = self.current_text.split()
        if len(words) >= count:
            words = words[:-count]
            self.current_text = " ".join(words) + " "
            self.formatted_text = self.current_text  # Simplified
        
        return SkillResult(
            success=True,
            message=f"Deleted {count} word(s)"
        )
    
    def delete_all(self) -> SkillResult:
        """
        Delete all text.
        
        Returns:
            Skill result
        """
        return self.clear_dictation()
    
    def capitalize_word(self, position: str = "last") -> SkillResult:
        """
        Capitalize a word.
        
        Args:
            position: Which word ("last", "first", "all")
            
        Returns:
            Skill result
        """
        words = self.current_text.split()
        if not words:
            return SkillResult(
                success=False,
                message="No text to capitalize"
            )
        
        if position == "last":
            words[-1] = words[-1].capitalize()
        elif position == "first":
            words[0] = words[0].capitalize()
        elif position == "all":
            words = [w.capitalize() for w in words]
        
        self.current_text = " ".join(words) + " "
        self.formatted_text = self.current_text  # Simplified
        
        return SkillResult(
            success=True,
            message=f"Capitalized {position} word(s)"
        )
    
    def handle_intent(self, intent: Intent) -> SkillResult:
        """
        Handle dictation-related intents.
        
        Args:
            intent: Classified intent
            
        Returns:
            Skill result
        """
        # Map intent types to methods
        intent_handlers = {
            IntentType.START_DICTATION: self.start_dictation,
            IntentType.INSERT_TEXT: self.insert_to_clipboard,
            IntentType.CLEAR_TEXT: self.clear_dictation,
            # Add more as needed
        }
        
        handler = intent_handlers.get(intent.type)
        if handler:
            return handler()
        
        # Default: append text if it's a dictation intent
        if hasattr(intent, 'text') and intent.text:
            return self.append_text(intent.text)
        
        return SkillResult(
            success=False,
            message=f"Unknown dictation intent: {intent.type.value}"
        )

