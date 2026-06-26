"""
Settlers of Catan - Interactive Game Launcher
Launch the full interactive game with building placement.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

try:
    import pygame
except ImportError:
    print("ERROR: Pygame is not installed!")
    print("\nTo install Pygame, run:")
    print("  pip install pygame")
    print("\nOr:")
    print("  py -3.12 -m pip install pygame")
    sys.exit(1)

from client.interactive_game import main

if __name__ == "__main__":
    main()
