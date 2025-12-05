"""
Lost & Found Office Game - Main Entry Point
"""

import sys
from game.game_manager import GameManager

def main():
    # 实例化管理器
    game = GameManager()

    # 启动游戏
    game.run()

    # 退出
    sys.exit()

if __name__ == "__main__":
    main()