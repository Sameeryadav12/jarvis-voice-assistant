# Contributing to Jarvis

Thank you for your interest in contributing to Jarvis! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow the project's coding standards

## Getting Started

### 1. Fork and Clone

```bash
# Fork on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/jarvis.git
cd jarvis
git remote add upstream https://github.com/ORIGINAL_OWNER/jarvis.git
```

### 2. Set Up Development Environment

#### Windows
```powershell
.\scripts\bootstrap_dev.ps1
```

#### Linux/macOS
```bash
chmod +x scripts/bootstrap_dev.sh
./scripts/bootstrap_dev.sh
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

## Development Workflow

### Running Tests

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\Activate.ps1  # Windows

# Run all tests
pytest tests/

# Run specific test
pytest tests/test_audio_capture.py

# Run with coverage
pytest --cov=core tests/
```

### Code Style

#### Python

We follow PEP 8 with some modifications:

```bash
# Format code
black core/ tests/

# Check style
flake8 core/ tests/

# Type checking
mypy core/
```

**Key conventions**:
- Line length: 100 characters
- Use type hints for all public functions
- Docstrings: Google style
- Imports: `black` formatting

**Example**:
```python
def process_audio(
    audio_data: np.ndarray,
    sample_rate: int = 16000
) -> Optional[str]:
    """
    Process audio data and return transcript.
    
    Args:
        audio_data: Audio samples as numpy array
        sample_rate: Sample rate in Hz
        
    Returns:
        Transcript text, or None if processing fails
        
    Raises:
        ValueError: If audio_data is empty
    """
    if len(audio_data) == 0:
        raise ValueError("Empty audio data")
    # ...
```

#### C++

We follow the [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html) with modifications:

**Key conventions**:
- Naming: `camelCase` for functions, `PascalCase` for classes
- Braces: K&R style
- Pointers: `Type* name` (not `Type *name`)
- Use modern C++ (C++17+): RAII, smart pointers, move semantics

**Example**:
```cpp
class AudioEndpoint {
public:
    /// Set master volume level
    /// @param level Volume level (0.0 to 1.0)
    /// @throws std::invalid_argument if level out of range
    void setMasterVolume(float level);

private:
    IAudioEndpointVolume* endpointVolume_{nullptr};
};
```

### Documentation

- Update relevant `.md` files in `docs/`
- Add docstrings to all public functions/classes
- Include examples for complex features
- Update `README.md` if adding user-facing features

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(audio): add streaming Whisper support
fix(nlu): correct intent confidence calculation
docs(readme): update installation instructions
refactor(tts): simplify edge TTS implementation
test(skills): add tests for reminder skills
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `test`: Adding or updating tests
- `perf`: Performance improvement
- `chore`: Maintenance tasks

## Pull Request Process

### 1. Ensure Quality

Before submitting:

```bash
# Run tests
pytest tests/

# Check style
black core/ tests/
flake8 core/ tests/
mypy core/

# Build C++ (if modified)
cd core/bindings/cpphooks/build
cmake --build . --config Release
```

### 2. Update Documentation

- Add/update docstrings
- Update relevant `.md` files
- Add examples if applicable

### 3. Write Good PR Description

```markdown
## Summary
Brief description of changes

## Motivation
Why is this change needed?

## Changes
- Added X feature
- Fixed Y bug
- Refactored Z component

## Testing
How was this tested?

## Screenshots (if UI changes)
[Add screenshots]

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Code follows style guide
- [ ] Commit messages follow convention
```

### 4. Submit PR

```bash
git push origin feature/your-feature-name
```

Then open a PR on GitHub.

### 5. Code Review

- Address reviewer feedback promptly
- Keep PR focused (one feature/fix per PR)
- Squash commits if requested

## Contributing Areas

### Easy (Good First Issues)

- Add new intent patterns
- Improve error messages
- Add unit tests
- Fix typos in documentation
- Add examples to README

### Medium

- Add new skills (e.g., timer, calculator)
- Improve UI components
- Add TTS voice options
- Implement new notification backends
- Add configuration validation

### Hard

- Platform support (macOS/Linux)
- STT model optimization
- Advanced NLU features
- Performance optimization
- Security enhancements

## Skill Development

### Creating a New Skill

1. **Create skill file**: `core/skills/my_skill.py`

```python
from core.nlu.intents import Intent, IntentType
from core.nlu.router import SkillResult

class MySkill:
    def __init__(self):
        # Initialize skill
        pass
    
    def handle_intent(self, intent: Intent) -> SkillResult:
        # Process intent
        return SkillResult(
            success=True,
            message="Skill executed successfully"
        )
```

2. **Register intent**: Update `core/nlu/intents.py`

```python
class IntentType(Enum):
    # ... existing intents ...
    MY_INTENT = "my_intent"
```

3. **Add patterns**: Update `IntentClassifier._init_patterns()`

```python
IntentType.MY_INTENT: [
    "trigger phrase",
    "another trigger"
]
```

4. **Register handler**: Update `jarvis.py`

```python
self.command_router.register_handler(
    IntentType.MY_INTENT,
    self.my_skill.handle_intent
)
```

5. **Add tests**: `tests/test_my_skill.py`

```python
import pytest
from core.skills.my_skill import MySkill

def test_my_skill():
    skill = MySkill()
    # ... test cases ...
```

### Skill Best Practices

- **Single Responsibility**: One skill per domain
- **Error Handling**: Graceful failure with helpful messages
- **Async Support**: Use `async` for I/O-bound operations
- **Configuration**: Use `config/settings.yaml` for skill settings
- **Permissions**: Declare required permissions in skill registry

## C++ Development

### Adding New Hooks

See [docs/CPP_HOOKS.md](docs/CPP_HOOKS.md) for detailed guide.

**Quick checklist**:
1. Create `.h` and `.cpp` files
2. Implement functionality with RAII
3. Add pybind11 bindings
4. Update `CMakeLists.txt`
5. Rebuild and test
6. Document in `CPP_HOOKS.md`

### C++ Best Practices

- **RAII**: All resources acquired in constructor, released in destructor
- **Exception Safety**: Strong guarantee preferred
- **Const Correctness**: Mark non-modifying methods as `const`
- **Move Semantics**: Use move constructors/assignment for efficiency
- **Comments**: Doxygen-style comments for public API

## Testing Guidelines

### Unit Tests

- Test each function/method independently
- Mock external dependencies
- Cover edge cases and error conditions
- Aim for 80%+ code coverage

### Integration Tests

- Test component interactions
- Use realistic data
- Test both success and failure paths

### Performance Tests

- Benchmark critical paths
- Ensure latency targets met
- Check for memory leaks

### Test Organization

```
tests/
├── unit/
│   ├── test_audio.py
│   ├── test_nlu.py
│   └── test_skills.py
├── integration/
│   ├── test_end_to_end.py
│   └── test_stt_nlu.py
└── performance/
    └── test_latency.py
```

## Documentation

### README

- Keep installation instructions up-to-date
- Add clear examples
- Include screenshots/GIFs for UI features

### Architecture Docs

- Explain design decisions
- Include diagrams
- Describe data flow
- Document performance characteristics

### API Docs

- Docstrings for all public functions/classes
- Include examples
- Document exceptions
- Specify time/space complexity (for DSA showcase)

## Release Process

### Versioning

We use [Semantic Versioning](https://semver.org/):
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

### Release Checklist

1. Update version in `core/__init__.py`
2. Update `CHANGELOG.md`
3. Run full test suite
4. Build and test package
5. Create git tag: `git tag v0.1.0`
6. Push tag: `git push --tags`
7. Create GitHub release with notes

## Getting Help

- **Issues**: Open an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions
- **Email**: [maintainer email]

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be:
- Listed in `README.md`
- Credited in release notes
- Mentioned in project documentation

Thank you for contributing to Jarvis! 🚀





