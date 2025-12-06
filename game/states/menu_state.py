"""
主菜单状态 (极简版：单层菜单 + 透明按钮)
"""

import pygame
import sys
from config.settings import *
from game.ui.button import Button

class MenuState:
    """主菜单状态"""

    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.font_title = pygame.font.Font(FONT_PATH, 80)
        self.font_subtitle = pygame.font.Font(FONT_PATH, 40)

        # 背景图片
        self.background = pygame.transform.scale(
            pygame.image.load(ASSETS['bg_menu']),
            (WINDOW_WIDTH, WINDOW_HEIGHT)
        )

        # 按钮布局参数
        self.btn_width = 260
        self.btn_height = 60
        self.menu_x = int(WINDOW_WIDTH * 0.75) - (self.btn_width // 2)
        self.start_y = 350
        self.spacing = 70

        # 初始化按钮
        self.buttons = self._create_buttons()

        # 播放音乐
        self._play_menu_music()

    def _play_menu_music(self):
        try:
            pygame.mixer.music.load('assets/sounds/bgm_menu.ogg')
            pygame.mixer.music.set_volume(0.6)
            pygame.mixer.music.play(-1)
        except: pass

    def _create_buttons(self):
        """创建按钮并应用透明样式"""
        buttons = []

        # 定义按钮：显示文本 -> 回调函数
        # 点击 NEW GAME 直接开始 Normal 难度游戏
        options = [
            ("NEW GAME", self._start_game),
            ("QUIT GAME", self._quit_game)
        ]

        for i, (text, func) in enumerate(options):
            y = self.start_y + i * self.spacing
            btn = Button(self.menu_x, y, self.btn_width, self.btn_height,
                        text, func, style='transparent')
            buttons.append(btn)

        return buttons

    def _start_game(self):
        from game.game_manager import GameState
        self.game_manager.change_state(GameState.GAMEPLAY)

    def _quit_game(self):
        pygame.quit()
        sys.exit()

    def exit(self):
        pygame.mixer.music.stop()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for btn in self.buttons:
                btn.handle_click(mouse_pos)

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.update(mouse_pos)

    def render(self, screen):
        # 1. 背景
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill(COLOR_DARK_GRAY)

        center_x = self.menu_x + self.btn_width // 2

        # 2. 标题 (位置可调)
        title_y = 200 # 调整这个数字改变垂直位置

        title_surf = self.font_title.render("Lost But Found", True, COLOR_WHITE)
        title_shadow = self.font_title.render("Lost But Found", True, COLOR_BLACK)

        # 稍微旋转一点，更活泼
        title_surf = pygame.transform.rotate(title_surf, 2)
        title_shadow = pygame.transform.rotate(title_shadow, 2)

        screen.blit(title_shadow, title_shadow.get_rect(center=(center_x + 6, title_y + 6)))
        screen.blit(title_surf, title_surf.get_rect(center=(center_x, title_y)))

        # 4. 按钮
        for btn in self.buttons:
            btn.render(screen)