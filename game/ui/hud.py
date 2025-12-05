import pygame
from config.settings import *


class HUD:
    def __init__(self):
        self.font = pygame.font.Font(FONT_PATH, 36)

        # --- 配置区域：在这里修改你想要的大小和位置 ---
        # TODO 12.04修改替换
        # 1. 定义想要显示的尺寸 (宽, 高)
        # 假设我们希望两个框都是 200像素宽，80像素高
        self.hud_size = (130, 80)

        # TODO 12.04修改替换
        # 2. 定义位置 (左, 上)
        self.time_pos = (1430, 740)  # 时间框的位置
        self.money_pos = (1430, 650)  # 金钱框的位置 (手动指定，不再依赖上一张图的高度)

        # --- 加载并强制缩放 ---

        # 加载原图
        raw_time_img = pygame.image.load('assets/images/icons/clock.png')
        raw_money_img = pygame.image.load('assets/images/icons/money.png')

        # 立即执行缩放适配 (Transform Scale)
        self.bg_time = pygame.transform.scale(raw_time_img, self.hud_size)
        self.bg_money = pygame.transform.scale(raw_money_img, self.hud_size)

    def render(self, screen, money, current_time, total_duration):
        # 准备文字数据
        remaining = max(0, total_duration - current_time)
        time_str = f"{int(remaining // 60):02}:{int(remaining % 60):02}"
        money_str = f"${int(money)}"

        # ==========================================
        # 1. 渲染时间 HUD
        # ==========================================
        # 步骤 A: 画缩放后的背景图 (底层)
        screen.blit(self.bg_time, self.time_pos)

        # 步骤 B: 画文字 (顶层) - 基于图片矩形自动居中
        # 获取图片在屏幕上的矩形区域
        bg_rect_time = self.bg_time.get_rect(topleft=self.time_pos)

        # 计算文字居中位置
        time_surf = self.font.render(time_str, True, COLOR_WHITE)
        time_text_rect = time_surf.get_rect(center=bg_rect_time.center)
        screen.blit(time_surf, time_text_rect)

        # ==========================================
        # 2. 渲染金钱 HUD
        # ==========================================
        # 步骤 A: 画缩放后的背景图 (底层)
        screen.blit(self.bg_money, self.money_pos)

        # 步骤 B: 画文字 (顶层) - 基于图片矩形自动居中
        bg_rect_money = self.bg_money.get_rect(topleft=self.money_pos)

        color = COLOR_WHITE
        money_surf = self.font.render(money_str, True, color)
        money_text_rect = money_surf.get_rect(center=bg_rect_money.center)
        screen.blit(money_surf, money_text_rect)