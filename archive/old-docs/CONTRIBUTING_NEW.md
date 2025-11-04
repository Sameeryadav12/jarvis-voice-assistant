# 🤝 Contributing to Jarvis

Thank you for your interest in contributing to Jarvis! This document provides guidelines for contributing.

---

## 🎯 Ways to Contribute

### 1. Report Bugs
- Use GitHub Issues
- Include steps to reproduce
- Provide console logs
- Mention your OS and Python version

### 2. Suggest Features
- Open a feature request issue
- Explain the use case
- Provide examples if possible

### 3. Submit Code
- Fork the repository
- Create a feature branch
- Make your changes
- Submit a pull request

---

## 🔧 Development Setup

### 1. Fork and Clone

```bash
git clone https://github.com/yourusername/jarvis.git
cd jarvis
```

### 2. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Dev dependencies
pip install pytest black flake8 mypy
```

### 4. Verify Setup

```bash
python CHECK_EVERYTHING.py
python test_simple.py
```

---

## 📝 Code Guidelines

### Python Style:
- Follow PEP 8
- Use type hints where possible
- Write docstrings for functions
- Keep functions focused and small

### Example:
```python
def process_command(self, command: str) -> str:
    """
    Process user command.
    
    Args:
        command: User input text
        
    Returns:
        Response message
    """
    intent = self.classifier.classify(command)
    return self.router.route(intent)
```

### File Organization:
- Core functionality in `core/`
- UI code in `apps/` or root
- Tests in `tests/` or `test_*.py`
- Documentation in `docs/` or root `.md` files

---

## 🧪 Testing

### Before Submitting:

```bash
# Run basic tests
python CHECK_EVERYTHING.py
python test_simple.py

# Test your specific feature
python test_your_feature.py
```

### Adding Tests:
- Create `test_your_feature.py`
- Test both success and error cases
- Include logging output
- Keep tests simple and focused

---

## 🎨 Adding New Features

### Adding a New Intent:

**1. Add to IntentType enum** (`core/nlu/intents.py`):
```python
class IntentType(Enum):
    YOUR_INTENT = "your_intent"
```

**2. Add patterns** (same file):
```python
IntentType.YOUR_INTENT: [
    "pattern one", "pattern two", "pattern three",
    "pattern four", "pattern five", "pattern six"
],
```

**3. Create skill handler** (`core/skills/your_skill.py`):
```python
def handle_your_intent(self, intent: Intent) -> SkillResult:
    # Your logic here
    return SkillResult(
        success=True,
        message="Your response"
    )
```

**4. Register handler** (in UI or main file):
```python
router.register_handler(IntentType.YOUR_INTENT, skill.handle_intent)
```

---

## 🔊 Adding TTS Voices

Edit `simple_tts.py`:

```python
# Change voice
tts = SimpleTTS(voice="en-US-GuyNeural")  # Male voice
# or
tts = SimpleTTS(voice="en-GB-SoniaNeural")  # British
```

Available voices: https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/language-support

---

## 📚 Documentation

### When Adding Features:
- Update README.md with new capabilities
- Add usage examples
- Update QUICKSTART.md if UI changes
- Document configuration options

### Documentation Style:
- Clear and concise
- Include code examples
- Add screenshots for UI changes
- Use emojis for visual clarity ✨

---

## 🐛 Debugging

### Console Logging:

```python
import logging
logger = logging.getLogger(__name__)

logger.info("✅ Operation successful")
logger.warning("⚠️ Warning message")
logger.error("❌ Error occurred")
```

### Running with Debug Output:

```bash
python jarvis_simple_working.py
# Watch console for detailed logs
```

---

## 🔀 Git Workflow

### Creating a Feature Branch:

```bash
git checkout -b feature/your-feature-name
```

### Making Commits:

```bash
git add .
git commit -m "Add: your feature description"
```

**Commit message format:**
- `Add:` for new features
- `Fix:` for bug fixes
- `Update:` for improvements
- `Docs:` for documentation

### Submitting Pull Request:

1. Push your branch to GitHub
2. Create Pull Request
3. Describe what you changed
4. Reference any related issues
5. Wait for review

---

## ✅ Pull Request Checklist

Before submitting:

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Console shows no errors
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] No unnecessary files included
- [ ] Feature works on Windows

---

## 🚫 What Not to Do

### Don't:
- ❌ Change core functionality without discussion
- ❌ Add large dependencies without reason
- ❌ Break existing features
- ❌ Commit API keys or secrets
- ❌ Include personal configuration files
- ❌ Remove error handling
- ❌ Make UI changes that break layout

### Do:
- ✅ Test thoroughly before submitting
- ✅ Ask questions if unsure
- ✅ Keep changes focused
- ✅ Update documentation
- ✅ Follow existing code style
- ✅ Add logging for debugging

---

## 💬 Communication

### Getting Help:
- GitHub Issues for bugs
- GitHub Discussions for questions
- Pull Request comments for code review

### Be Respectful:
- Be kind and constructive
- Help others learn
- Give credit where due
- Follow code of conduct

---

## 🏆 Recognition

Contributors will be:
- Added to CONTRIBUTORS.md
- Mentioned in release notes
- Recognized in README.md

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## 🎓 Learning Resources

### Python:
- [PEP 8 Style Guide](https://pep8.org/)
- [Python Docs](https://docs.python.org/3/)

### Qt/PySide6:
- [PySide6 Docs](https://doc.qt.io/qtforpython/)
- [Qt Documentation](https://doc.qt.io/)

### NLP:
- [spaCy Docs](https://spacy.io/)
- [NLU Patterns](https://spacy.io/usage/rule-based-matching)

### Voice:
- [Faster Whisper](https://github.com/guillaumekln/faster-whisper)
- [Edge TTS](https://github.com/rany2/edge-tts)

---

## ❓ Questions?

Feel free to:
- Open an issue
- Start a discussion
- Comment on existing issues

We're here to help! 🚀

---

**Thank you for contributing to Jarvis!** 🤖✨

