"""
UI按钮组件 (支持多种样式：标准、灰色、红色、透明)
"""

import pygame
from config.settings import COLOR_WHITE, COLOR_BLACK, COLOR_BLUE, COLOR_RED


class Button:
    """可点击的按钮UI组件"""

    def __init__(self, x, y, width, height, text, callback, callback_arg=None, style='primary', font_size=36):
        """
        初始化按钮
        style: 'primary'(蓝), 'grey'(灰), 'danger'(红), 'transparent'(透明文字)
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.callback_arg = callback_arg

        self.is_hovered = False
        self.is_pressed = False

        # 字体 (请确保 settings.py 里定义了 FONT_PATH，否则这里用 None)
        try:
            from config.settings import FONT_PATH
            self.font = pygame.font.Font(FONT_PATH, font_size)
        except:
            self.font = pygame.font.Font(None, font_size)

        self.apply_style(style)

    def apply_style(self, style):
        """根据样式名设置颜色和边框"""
        self.border_width = 2 # 默认有边框

        if style == 'transparent':
            # [新增] 透明风格：平常完全透明，悬停微亮
            self.color_normal = (0, 0, 0, 0)      # 完全透明
            self.color_hover = (255, 255, 255, 30) # 悬停时淡淡白光
            self.color_pressed = (255, 255, 255, 60)
            self.text_color = COLOR_WHITE
            self.border_width = 0 # 无边框

        elif style == 'grey':
            # 灰色风格 (用于拒绝按钮)
            self.color_normal = (60, 60, 60)
            self.color_hover = (180, 180, 180)
            self.color_pressed = (30, 30, 30)
            self.text_color = COLOR_WHITE
            self.border_width = 0

        elif style == 'danger':
            # 红色风格
            self.color_normal = COLOR_RED       # TODO 12.04修改替换
            self.color_hover = (230, 80, 80)
            self.color_pressed = (150, 40, 40)
            self.text_color = COLOR_WHITE

        else:
            # 默认蓝色风格 (primary)
            self.color_normal = COLOR_BLUE
            self.color_hover = (120, 170, 255)
            self.color_pressed = (80, 130, 255)
            self.text_color = COLOR_WHITE

    def handle_click(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            if self.callback:
                if self.callback_arg is not None:
                    self.callback(self.callback_arg)
                else:
                    self.callback()
            return True
        return False

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def render(self, screen):
        # 1. 确定背景色
        if self.is_pressed:
            color = self.color_pressed
        elif self.is_hovered:
            color = self.color_hover
        else:
            color = self.color_normal

        # 2. 绘制背景 (支持透明度)
        # 如果是 (R, G, B, A) 格式，或者就是透明样式
        if len(color) == 4:
            s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            pygame.draw.rect(s, color, s.get_rect(), border_radius=8)
            screen.blit(s, self.rect.topleft)
        else:
            pygame.draw.rect(screen, color, self.rect, border_radius=8)

        # 3. 绘制边框 (如果有)
        if self.border_width > 0:
            pygame.draw.rect(screen, COLOR_WHITE, self.rect, self.border_width, border_radius=8)

        # 4. 绘制文字
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)