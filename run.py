#!/usr/bin/env python3
"""
Giraffe Game Launcher
This script checks for required dependencies and launches the game.
"""

import sys
import subprocess
import importlib.util

def check_pygame():
    """Check if pygame is installed, install if not."""
    if importlib.util.find_spec("pygame") is None:
        print("Pygame is not installed. Installing now...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
            print("Pygame installed successfully!")
        except subprocess.CalledProcessError:
            print("Failed to install pygame. Please install it manually with:")
            print("pip install pygame")
            sys.exit(1)
    else:
        print("Pygame is already installed.")

def main():
    """Main function to run the game."""
    print("Starting Giraffe Game...")
    print("Controls:")
    print("  - LEFT/RIGHT arrows: Move giraffe body left/right")
    print("  - UP/DOWN arrows: Move giraffe head up/down")
    print("  - ESC: Quit game (after game over)")
    
    # Check for pygame
    check_pygame()
    
    # Import and run the game
    try:
        import main
        main.main()
    except ImportError:
        print("Error: Could not find main.py. Make sure you're running this script from the game directory.")
        sys.exit(1)
    except Exception as e:
        print(f"Error running the game: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()