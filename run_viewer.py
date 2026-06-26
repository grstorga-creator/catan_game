"""
Settlers of Catan - Visual Game Launcher
Simple launcher for the Pygame board viewer.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

try:
    import pygame
except ImportError:
    print("ERROR: Pygame is not installed!")
    print("\nTo install Pygame, run:")
    print("  pip install pygame")
    print("\nOr on some systems:")
    print("  pip install pygame --break-system-packages")
    sys.exit(1)

# Import and run the viewer
from client.game_viewer import main

if __name__ == "__main__":
    main()
