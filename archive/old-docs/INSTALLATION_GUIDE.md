# Jarvis Installation Guide

## Quick Install

### Option 1: Run Jarvis Directly (No Installation)
1. Download `jarvis.exe`
2. Double-click to run
3. Done! ✅

### Option 2: Install to System (Recommended)
1. Right-click `install.bat`
2. Select "Run as administrator"
3. Follow the prompts
4. Find Jarvis on your desktop or Start menu

## Uninstallation

### Remove Jarvis
1. Right-click `uninstall.bat`
2. Select "Run as administrator"
3. Confirm removal

## Manual Installation

If you prefer to install manually:

1. **Create folder**: `C:\Program Files\Jarvis`

2. **Copy files**:
   - Copy `dist\jarvis.exe` to `C:\Program Files\Jarvis\`
   - Copy `config\` folder to `C:\Program Files\Jarvis\config\`

3. **Create shortcuts** (optional):
   - Desktop: Right-click `jarvis.exe` → Send to → Desktop
   - Start menu: Drag to Start menu

## System Requirements

- **OS**: Windows 10/11
- **RAM**: 2GB minimum
- **Disk**: 200MB free space
- **Internet**: Optional (for cloud TTS)

## First Run

On first launch, Jarvis will:
- Initialize all systems
- Create configuration files
- Set up database
- Be ready to use!

## Troubleshooting

### "Access Denied" error
- Run as administrator

### "Cannot find file" error
- Make sure `jarvis.exe` exists in `dist\` folder
- Rebuild with: `pyinstaller jarvis.spec`

### "SpaCy model not found"
- Should be included in the executable
- Rebuild if missing

## Support

For issues or questions, check the README.md or project documentation.

## Enjoy Jarvis! 🤖




