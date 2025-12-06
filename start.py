"""
Lost but Found - Main Entry Point
"""

import sys
from game.game_manager import GameManager

def main():
    """
    main entry point
    """
    # Instantiate GameManager
    game = GameManager()

    # Run the game
    game.run()

    # Exit
    sys.exit()

if __name__ == "__main__":
    main()