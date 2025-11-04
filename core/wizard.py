"""
First-Run Wizard for Jarvis

Interactive setup wizard that runs on first launch.
"""

import os
import sys
from pathlib import Path
from typing import Optional

from loguru import logger

# Configuration marker file
WIZARD_MARKER = Path.home() / ".jarvis" / "setup_complete.flag"


def has_run_before() -> bool:
    """Check if wizard has run before."""
    return WIZARD_MARKER.exists()


def mark_setup_complete() -> None:
    """Mark setup as complete."""
    WIZARD_MARKER.parent.mkdir(parents=True, exist_ok=True)
    WIZARD_MARKER.touch()
    logger.info("Setup wizard marked as complete")


def run_first_run_wizard() -> None:
    """
    Run interactive setup wizard.
    
    This is called on first launch to configure Jarvis.
    """
    # Check if stdin is interactive
    is_interactive = sys.stdin.isatty()
    
    print("\n" + "="*60)
    print("  WELCOME TO JARVIS!")
    print("="*60)
    print("\nLet's set up your personal assistant.\n")
    
    # Step 1: Personalization
    print("Step 1: Personalization")
    try:
        name = input("What would you like to call me? [Jarvis]: ").strip() or "Jarvis"
        print(f"Great! I'll answer to {name}.\n")
    except EOFError:
        name = "Jarvis"
        print(f"Using default name: {name}.\n")
    
    # Step 2: Voice Selection
    print("Step 2: Voice Selection")
    print("Available voices:")
    print("  1. Aria (Female - Default)")
    print("  2. Guy (Male)")
    print("  3. Jenny (Female)")
    
    try:
        voice_choice = input("Choose voice [1]: ").strip() or "1"
    except EOFError:
        voice_choice = "1"
        print("Using default voice.\n")
    
    voice_map = {
        "1": "en-US-AriaNeural",
        "2": "en-US-GuyNeural",
        "3": "en-US-JennyNeural",
    }
    
    voice = voice_map.get(voice_choice, "en-US-AriaNeural")
    print(f"Voice set to: {voice}\n")
    
    # Step 3: Preferences
    print("Step 3: Preferences")
    try:
        use_voice = input("Enable voice responses? [yes/no] [yes]: ").strip().lower() or "yes"
        voice_enabled = use_voice in ["yes", "y", "1"]
        print(f"Voice responses: {'enabled' if voice_enabled else 'disabled'}\n")
    except EOFError:
        voice_enabled = True
        print("Voice responses: enabled (default)\n")
    
    # Step 4: Save Configuration
    print("Saving configuration...")
    
    try:
        from core.config import get_config
        config = get_config()
        
        # Save preferences
        config.set('general.app_name', name)
        config.set('tts.edge.voice', voice)
        config.set('tts.enabled', voice_enabled)
        
        config.save()
        
        # Mark wizard as complete
        mark_setup_complete()
        
        print("Configuration saved!\n")
        
    except Exception as e:
        logger.error(f"Failed to save configuration: {e}")
        print(f"Warning: Could not save configuration: {e}\n")
    
    # Final message
    print("="*60)
    print(f"Setup Complete! Welcome, {name}!")
    print("="*60)
    print("\nJarvis is ready to assist you.")
    print("Type 'help' to see available commands.")
    print()


def should_run_wizard() -> bool:
    """
    Check if wizard should run.
    
    Returns:
        True if wizard should run, False otherwise
    """
    # Always run wizard in development mode (if not frozen)
    if not getattr(sys, 'frozen', False):
        return False  # Skip in dev mode
    
    # Run if not run before
    return not has_run_before()


