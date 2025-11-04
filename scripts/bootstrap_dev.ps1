# Jarvis Development Bootstrap Script (Windows/PowerShell)
# Sets up the development environment

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Jarvis Development Bootstrap (Windows)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "[1/8] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  Found: $pythonVersion" -ForegroundColor Green
    
    # Check if Python 3.10+
    $version = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    if ([double]$version -lt 3.10) {
        Write-Host "  ERROR: Python 3.10+ required, found $version" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  ERROR: Python not found. Please install Python 3.10+" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "[2/8] Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "  Virtual environment already exists" -ForegroundColor Green
} else {
    python -m venv venv
    Write-Host "  Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "[3/8] Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"
Write-Host "  Activated" -ForegroundColor Green

# Upgrade pip
Write-Host ""
Write-Host "[4/8] Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip
Write-Host "  pip upgraded" -ForegroundColor Green

# Install Python dependencies
Write-Host ""
Write-Host "[5/8] Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
Write-Host "  Dependencies installed" -ForegroundColor Green

# Download spaCy model
Write-Host ""
Write-Host "[6/8] Downloading spaCy model..." -ForegroundColor Yellow
python -m spacy download en_core_web_sm
Write-Host "  spaCy model downloaded" -ForegroundColor Green

# Create necessary directories
Write-Host ""
Write-Host "[7/8] Creating project directories..." -ForegroundColor Yellow
$directories = @(
    "logs",
    "data",
    "models",
    "models/piper",
    "chroma_db",
    "tts_cache"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "  Created: $dir" -ForegroundColor Green
    }
}

# Copy config template
Write-Host ""
Write-Host "[8/8] Setting up configuration..." -ForegroundColor Yellow
if (-not (Test-Path "config/settings.yaml")) {
    Copy-Item "config/settings.example.yaml" "config/settings.yaml"
    Write-Host "  Created config/settings.yaml from template" -ForegroundColor Green
    Write-Host "  IMPORTANT: Edit config/settings.yaml with your API keys" -ForegroundColor Yellow
} else {
    Write-Host "  config/settings.yaml already exists" -ForegroundColor Green
}

# Build C++ extension (optional, requires CMake and MSVC)
Write-Host ""
Write-Host "[Optional] Building C++ extension..." -ForegroundColor Yellow
Write-Host "  To build C++ hooks:" -ForegroundColor Cyan
Write-Host "    1. Install Visual Studio 2019+ with C++ tools" -ForegroundColor Cyan
Write-Host "    2. Install CMake (cmake.org)" -ForegroundColor Cyan
Write-Host "    3. Run the following commands:" -ForegroundColor Cyan
Write-Host "       cd core\bindings\cpphooks" -ForegroundColor White
Write-Host "       git clone https://github.com/pybind/pybind11.git" -ForegroundColor White
Write-Host "       mkdir build && cd build" -ForegroundColor White
Write-Host "       cmake .." -ForegroundColor White
Write-Host "       cmake --build . --config Release" -ForegroundColor White

# Done
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Bootstrap Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Edit config/settings.yaml with your API keys" -ForegroundColor White
Write-Host "  2. Test audio capture: python tests/test_audio_capture.py" -ForegroundColor White
Write-Host "  3. (Optional) Build C++ hooks (see instructions above)" -ForegroundColor White
Write-Host ""
Write-Host "To activate the virtual environment in future sessions:" -ForegroundColor Yellow
Write-Host "  .\\venv\\Scripts\\Activate.ps1" -ForegroundColor White
Write-Host ""





