#!/bin/bash
# Jarvis Development Bootstrap Script (Linux/macOS)
# Sets up the development environment

set -e

echo "========================================"
echo "  Jarvis Development Bootstrap (Unix)"
echo "========================================"
echo ""

# Check Python version
echo "[1/8] Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "  Found: $PYTHON_VERSION"
    
    # Check if Python 3.10+
    PYTHON_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")
    if [ "$PYTHON_MINOR" -lt 10 ]; then
        echo "  ERROR: Python 3.10+ required"
        exit 1
    fi
else
    echo "  ERROR: Python 3 not found. Please install Python 3.10+"
    exit 1
fi

# Create virtual environment
echo ""
echo "[2/8] Creating virtual environment..."
if [ -d "venv" ]; then
    echo "  Virtual environment already exists"
else
    python3 -m venv venv
    echo "  Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "[3/8] Activating virtual environment..."
source venv/bin/activate
echo "  Activated"

# Upgrade pip
echo ""
echo "[4/8] Upgrading pip..."
python -m pip install --upgrade pip
echo "  pip upgraded"

# Install Python dependencies
echo ""
echo "[5/8] Installing Python dependencies..."
pip install -r requirements.txt
echo "  Dependencies installed"

# Download spaCy model
echo ""
echo "[6/8] Downloading spaCy model..."
python -m spacy download en_core_web_sm
echo "  spaCy model downloaded"

# Create necessary directories
echo ""
echo "[7/8] Creating project directories..."
directories=(
    "logs"
    "data"
    "models"
    "models/piper"
    "chroma_db"
    "tts_cache"
)

for dir in "${directories[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo "  Created: $dir"
    fi
done

# Copy config template
echo ""
echo "[8/8] Setting up configuration..."
if [ ! -f "config/settings.yaml" ]; then
    cp config/settings.example.yaml config/settings.yaml
    echo "  Created config/settings.yaml from template"
    echo "  IMPORTANT: Edit config/settings.yaml with your API keys"
else
    echo "  config/settings.yaml already exists"
fi

# Build C++ extension (optional)
echo ""
echo "[Optional] Building C++ extension..."
echo "  To build C++ hooks:"
echo "    1. Install CMake: sudo apt-get install cmake  (Ubuntu/Debian)"
echo "                      brew install cmake           (macOS)"
echo "    2. Install build tools:"
echo "       sudo apt-get install build-essential       (Ubuntu/Debian)"
echo "       xcode-select --install                     (macOS)"
echo "    3. Run the following commands:"
echo "       cd core/bindings/cpphooks"
echo "       git clone https://github.com/pybind/pybind11.git"
echo "       mkdir build && cd build"
echo "       cmake .."
echo "       make"

# Done
echo ""
echo "========================================"
echo "  Bootstrap Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Edit config/settings.yaml with your API keys"
echo "  2. Test audio capture: python tests/test_audio_capture.py"
echo "  3. (Optional) Build C++ hooks (see instructions above)"
echo ""
echo "To activate the virtual environment in future sessions:"
echo "  source venv/bin/activate"
echo ""





