# Jarvis Architecture Deep Dive

## Overview

Jarvis follows a modular, event-driven architecture with clear separation of concerns. The system is designed for:

- **Low latency**: Critical path operations complete in <500ms
- **Extensibility**: Plugin system for custom skills
- **Reliability**: RAII patterns, exception safety, graceful degradation
- **Cross-platform**: Core in Python, platform-specific code in C++

## System Components

### 1. Audio Pipeline

```
Microphone → AudioCapture → Ring Buffer → [Wake Word Detection]
                                         ↓
                                    [STT Engine]
                                         ↓
                                      Text
```

#### AudioCapture (core/audio/capture.py)

- Uses `sounddevice` (PortAudio wrapper)
- Ring buffer for efficient memory management
- Callback-based for real-time processing
- **Data Structure**: `collections.deque` with O(1) append/pop

#### Ring Buffer Implementation

```python
class RingBuffer:
    def __init__(self, max_size):
        self.buffer = deque(maxlen=max_size)  # Auto-evicts oldest
```

**Complexity Analysis**:
- Append: O(1)
- Read: O(k) where k = items requested
- Space: O(n) where n = max_size

### 2. Wake Word Detection

Uses Picovoice Porcupine for on-device wake word detection.

**Algorithm**: DNN-based keyword spotting
- **Latency**: <100ms
- **False positive rate**: <0.1%
- **Memory**: ~2MB model

**Flow**:
1. Audio frames buffered
2. Porcupine processes frame-by-frame
3. On detection, trigger STT

### 3. Speech-to-Text (STT)

#### Offline Mode: whisper.cpp

- **Model**: GGML quantized Whisper
- **Latency**: 200-500ms (base model, CPU)
- **Accuracy**: ~95% WER on clean speech
- **Advantages**: Privacy, no internet required

#### Cloud Mode: OpenAI Realtime API

- **Latency**: 150-300ms
- **Advantages**: Function calling, bi-directional audio
- **Protocol**: WebSocket with base64-encoded audio

**Implementation** (core/audio/stt_realtime.py):
```python
async def send_audio(self, audio_data: bytes):
    audio_b64 = base64.b64encode(audio_data).decode()
    await self.ws.send(json.dumps({
        "type": "input_audio_buffer.append",
        "audio": audio_b64
    }))
```

### 4. Natural Language Understanding (NLU)

#### Intent Classification

**Algorithm**: Hybrid pattern matching + ML

1. **Pattern Matching** (O(n*m)):
   - Fast path for common intents
   - Keyword-based with confidence scoring
   - Example: "volume up" → `VOLUME_UP` (confidence: 0.9)

2. **spaCy NER** (O(n)):
   - Named entity recognition
   - Extracts: dates, names, numbers, locations

**Intent Priority Queue** (core/nlu/intents.py):
```python
class PriorityIntentQueue:
    def __init__(self):
        self.queue: List[Tuple[float, Intent]] = []
    
    def add_intent(self, intent):
        heapq.heappush(self.queue, (-intent.confidence, intent))
```

**Complexity**: 
- Insert: O(log n)
- Get best: O(log n)
- Space: O(n)

### 5. Command Router

**Pattern**: Function calling / Command pattern

```python
class CommandRouter:
    handlers: Dict[IntentType, Callable]
    
    async def route(self, intent: Intent) -> SkillResult:
        handler = self.handlers[intent.type]
        return handler(intent)
```

**Middleware** support for pre-processing:
- Logging
- Permission checks
- Context enrichment

### 6. Skills

#### System Skills (C++ Hooks)

**Architecture**: Python ↔ pybind11 ↔ C++ ↔ Win32/WASAPI

```
Python                  C++                     Windows
------                  ---                     -------
set_volume(0.5) → AudioEndpoint.setVolume() → IAudioEndpointVolume
                                              → SetMasterVolumeLevelScalar()
```

**C++ Design**:
- RAII for resource management
- Smart pointers for COM objects
- Exception safety
- Move semantics (no copy)

#### Reminder Skills

**Scheduler**: APScheduler
- **Backend**: In-memory or persistent (SQLite)
- **Trigger types**: Date, interval, cron
- **Threading**: Background thread pool

**Example**:
```python
scheduler.add_job(
    notification_callback,
    'date',
    run_date=datetime(2024, 1, 15, 10, 0),
    args=["Reminder", "Meeting in 5 minutes"]
)
```

### 7. Vector Memory (RAG)

**Backend**: ChromaDB (embedding-based similarity search)

**Algorithm**: Approximate nearest neighbors (ANN)
- **Index**: HNSW (Hierarchical Navigable Small World)
- **Query time**: O(log n) average case
- **Space**: O(n * d) where d = embedding dimension

**Usage**:
```python
# Store
memory.store("My Wi-Fi password is hunter2", metadata={"type": "fact"})

# Retrieve
results = memory.search("What's my Wi-Fi password?", n_results=3)
# Returns: [{"text": "My Wi-Fi password is hunter2", "distance": 0.12, ...}]
```

### 8. Text-to-Speech (TTS)

#### Piper (Offline)

- **Model**: VITS-based neural TTS
- **Latency**: 300-600ms
- **Quality**: Natural prosody, clear articulation
- **Format**: ONNX for cross-platform inference

#### Edge TTS (Cloud)

- **Backend**: Microsoft Azure Cognitive Services
- **Latency**: 200-400ms
- **Voices**: 300+ voices, 75+ languages
- **Quality**: Production-grade neural voices

### 9. Desktop UI

**Framework**: PySide6 (Qt for Python)

**Architecture**: Model-View-Controller (MVC)
- **Model**: Application state, audio levels, logs
- **View**: QML for modern UI
- **Controller**: Python event handlers

**Features**:
- Real-time waveform visualization
- Transcript history
- Settings panel
- System tray integration

## Data Structures & Algorithms Showcase

### 1. Ring Buffer (Circular Queue)

**Use case**: Audio frame buffering

**Implementation**:
```python
class RingBuffer:
    def __init__(self, max_size):
        self.buffer = deque(maxlen=max_size)
        self.lock = threading.Lock()
```

**Operations**:
- Enqueue: O(1)
- Dequeue: O(1)
- Auto-eviction: O(1)

### 2. Priority Queue (Max Heap)

**Use case**: Intent arbitration

**Implementation**:
```python
heapq.heappush(queue, (-confidence, intent))
best_intent = heapq.heappop(queue)[1]
```

**Operations**:
- Insert: O(log n)
- Extract max: O(log n)

### 3. Hash Table (Dict)

**Use case**: Intent → Handler routing

**Operations**:
- Insert: O(1) average
- Lookup: O(1) average
- Delete: O(1) average

### 4. String Matching

**Use case**: Window title search

**Algorithm**: Case-insensitive substring search
- Boyer-Moore-inspired optimization
- Time: O(n * m) worst case, O(n) average

## Concurrency Model

### Threading

- **Audio capture**: Separate thread (callback-based)
- **UI**: Main thread (Qt event loop)
- **Skills**: Thread pool for I/O-bound tasks

### Async/Await

- **Realtime API**: WebSocket with `asyncio`
- **Web automation**: Playwright (async)
- **TTS (Edge)**: Async HTTP requests

**Example**:
```python
async def process_audio():
    async with RealtimeSTT(api_key) as stt:
        await stt.send_audio(audio_data)
        async for message in stt.listen():
            handle_message(message)
```

## Performance Characteristics

| Component | Latency | Memory | CPU |
|-----------|---------|--------|-----|
| Wake word | <100ms | 2MB | 2% |
| STT (offline) | 200-500ms | 500MB | 30-50% |
| STT (cloud) | 150-300ms | 50MB | 5% |
| NLU | <50ms | 100MB | <5% |
| C++ hooks | <10ms | <1MB | <1% |
| TTS (offline) | 300-600ms | 200MB | 20% |
| TTS (cloud) | 200-400ms | 20MB | 2% |

## Error Handling & Resilience

### RAII Pattern (C++)

```cpp
class AudioEndpoint {
public:
    AudioEndpoint() { initialize(); }
    ~AudioEndpoint() { cleanup(); }
    // No manual resource management needed
};
```

### Graceful Degradation

- If C++ hooks fail → Log warning, continue with Python fallbacks
- If STT offline fails → Offer cloud option
- If cloud services fail → Continue with local-only features

### Exception Safety

- Strong guarantee: Operations either succeed completely or have no effect
- No resource leaks (RAII, context managers)
- Detailed error messages with stack traces

## Security Considerations

### Credential Storage

- API keys encrypted at rest (Fernet)
- Never logged or transmitted in plain text

### Permission System

- Per-skill permissions
- Confirmation prompts for sensitive actions
- Audit log for all system modifications

### Privacy

- Local-first: Voice data never sent unless cloud STT enabled
- Opt-in telemetry
- Memory encryption option for sensitive facts

## Testing Strategy

### Unit Tests

- Each module tested independently
- Mock external dependencies (APIs, hardware)
- Coverage target: 80%+

### Integration Tests

- End-to-end command flow
- STT → NLU → Router → Skill
- Mock audio input

### Performance Tests

- Latency benchmarks
- Memory leak detection (valgrind for C++)
- Load testing (1000s of commands)

## Deployment

### Packaging

- **PyInstaller**: Single-file executable
- **Includes**: Python interpreter, dependencies, models (optional)
- **Size**: ~100MB (minimal), ~500MB (with models)

### Installation

1. Extract archive
2. Run first-time setup wizard
3. Configure API keys
4. Test microphone
5. Ready to use

## Future Enhancements

### Phase 2

- Multi-platform support (macOS CoreAudio, Linux PulseAudio)
- Distributed mode (Raspberry Pi as always-on listener)
- Custom wake word training
- Voice profile recognition

### Phase 3

- On-device LLM (Llama.cpp)
- Advanced RAG with document ingestion
- Multi-modal (vision, screen understanding)
- Home automation integration (Home Assistant, MQTT)

## References

- **Audio**: PortAudio documentation, WASAPI spec
- **STT**: Whisper paper, OpenAI Realtime API docs
- **NLU**: spaCy docs, RASA architecture
- **Vector DB**: ChromaDB docs, HNSW paper
- **C++ Interop**: pybind11 docs, COM programming guide
- **DSA**: CLRS (Cormen et al.), Algorithm Design Manual





