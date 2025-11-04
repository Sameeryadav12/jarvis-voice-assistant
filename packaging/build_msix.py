"""
Build MSIX package for Jarvis

Requirements:
- Windows SDK (for makeappx.exe)
- PyInstaller (for creating exe)
- Assets folder with required images

Usage:
    python packaging/build_msix.py
"""

import sys
import os
import shutil
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
PACKAGING_DIR = PROJECT_ROOT / "packaging"
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
MSIX_BUILD_DIR = PACKAGING_DIR / "msix_build"


def find_makeappx():
    """Find makeappx.exe in Windows SDK."""
    possible_paths = [
        r"C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\makeappx.exe",
        r"C:\Program Files (x86)\Windows Kits\10\bin\10.0.19041.0\x64\makeappx.exe",
        r"C:\Program Files (x86)\Windows Kits\10\App Certification Kit\makeappx.exe",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None


def build_exe():
    """Build executable with PyInstaller."""
    print("Building executable with PyInstaller...")
    
    spec_file = PROJECT_ROOT / "jarvis_ui.spec"
    
    if not spec_file.exists():
        print("Creating PyInstaller spec file...")
        # Create basic spec file
        pyinstaller_cmd = [
            sys.executable, "-m", "PyInstaller",
            "--name=jarvis_ui",
            "--onefile",
            "--windowed",
            "--icon=assets/jarvis_icon.ico",
            str(PROJECT_ROOT / "jarvis_ui.py"),
        ]
        subprocess.run(pyinstaller_cmd, check=True, cwd=PROJECT_ROOT)
    else:
        print("Using existing spec file...")
        subprocess.run([sys.executable, "-m", "PyInstaller", str(spec_file)], check=True, cwd=PROJECT_ROOT)
    
    print("✓ Executable built")


def prepare_msix_package():
    """Prepare MSIX package directory."""
    print("Preparing MSIX package directory...")
    
    # Clean and create build directory
    if MSIX_BUILD_DIR.exists():
        shutil.rmtree(MSIX_BUILD_DIR)
    MSIX_BUILD_DIR.mkdir(parents=True, exist_ok=True)
    
    # Copy executable
    exe_src = DIST_DIR / "jarvis_ui.exe"
    exe_dst = MSIX_BUILD_DIR / "jarvis_ui.exe"
    
    if not exe_src.exists():
        raise FileNotFoundError(f"Executable not found: {exe_src}")
    
    shutil.copy2(exe_src, exe_dst)
    print(f"  Copied: {exe_src.name}")
    
    # Copy manifest
    manifest_src = PACKAGING_DIR / "AppxManifest.xml"
    manifest_dst = MSIX_BUILD_DIR / "AppxManifest.xml"
    shutil.copy2(manifest_src, manifest_dst)
    print(f"  Copied: {manifest_src.name}")
    
    # Create Assets directory
    assets_dir = MSIX_BUILD_DIR / "Assets"
    assets_dir.mkdir(exist_ok=True)
    
    # Create placeholder assets if they don't exist
    create_placeholder_assets(assets_dir)
    
    print("✓ Package directory prepared")


def create_placeholder_assets(assets_dir: Path):
    """Create placeholder asset images."""
    from PIL import Image, ImageDraw, ImageFont
    
    assets = {
        "StoreLogo.png": (50, 50),
        "Square44x44Logo.png": (44, 44),
        "Square150x150Logo.png": (150, 150),
        "Wide310x150Logo.png": (310, 150),
        "SplashScreen.png": (620, 300),
    }
    
    for filename, size in assets.items():
        filepath = assets_dir / filename
        if not filepath.exists():
            # Create simple gradient image
            img = Image.new('RGB', size, color=(30, 30, 50))
            draw = ImageDraw.Draw(img)
            
            # Add text
            text = "J"
            try:
                font = ImageFont.truetype("arial.ttf", size[0] // 2)
            except:
                font = ImageFont.load_default()
            
            # Center text
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
            
            draw.text(position, text, fill=(100, 150, 255), font=font)
            img.save(filepath)
            print(f"  Created: {filename}")


def build_msix():
    """Build MSIX package."""
    print("Building MSIX package...")
    
    makeappx = find_makeappx()
    
    if not makeappx:
        print("ERROR: makeappx.exe not found. Please install Windows SDK.")
        print("Download: https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/")
        return False
    
    output_file = DIST_DIR / "Jarvis.msix"
    output_file.parent.mkdir(exist_ok=True)
    
    cmd = [
        makeappx,
        "pack",
        "/d", str(MSIX_BUILD_DIR),
        "/p", str(output_file),
        "/o",  # Overwrite
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"ERROR: {result.stderr}")
        return False
    
    print(f"✓ MSIX package created: {output_file}")
    print(f"  Size: {output_file.stat().st_size / (1024*1024):.1f} MB")
    return True


def main():
    """Main build process."""
    print("=" * 60)
    print("JARVIS MSIX PACKAGE BUILDER")
    print("=" * 60)
    
    try:
        # Step 1: Build executable
        build_exe()
        
        # Step 2: Prepare package
        prepare_msix_package()
        
        # Step 3: Build MSIX
        success = build_msix()
        
        if success:
            print("\n" + "=" * 60)
            print("[SUCCESS] MSIX package built successfully!")
            print("=" * 60)
            print("\nNext steps:")
            print("1. Sign the package with a certificate")
            print("2. Test installation on clean machine")
            print("3. Submit to Microsoft Store (optional)")
        else:
            print("\n[FAILED] MSIX build failed")
            return 1
        
        return 0
    
    except Exception as e:
        print(f"\n[ERROR] Build failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

