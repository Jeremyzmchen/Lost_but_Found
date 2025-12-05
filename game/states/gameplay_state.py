"""
游戏玩法状态 - 包含便签、呼叫警察、两阶段验证机制
"""
import pygame, random, math, os
from config.settings import *
from game.entities.item import Item
from game.entities.customer import Customer
from game.managers.inventory_manager import InventoryManager
from game.ui.hud import HUD
from game.ui.popup import FloatingText
from game.ui.button import Button
from game.entities.sticky_note import StickyNote
from game.entities.police import Police

class GameplayState:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.money = 0
        self.shift_time = 0
        self.shift_duration = 180
        if 'money' in game_manager.game_data:
            self.money = game_manager.game_data['money']

        self.inventory_manager = InventoryManager()
        self.customers = []
        self.customer_slots = [None] * len(CUSTOMER_SLOTS)
        self.customer_timer = 0
        self.conveyor_items = []
        self.item_spawn_timer = 0

        self.item_spawn_interval = ITEM_SPAWN_INTERVAL
        self.customer_interval = CUSTOMER_INTERVAL

        self.current_batch_id = 0
        self.batch_pause_states = {}
        self.conveyor_texture = None
        self.scroll_offset = 0
        self.scroll_speed = CONVEYOR_SPEED
        self.belt_width = 160
        self.hud = HUD()
        self.popups = []
        self._load_background()
        self._load_conveyor_texture()

        # [修复] 补回 label_image 的初始化逻辑
        self.label_image = None
        try:
            path = 'assets/images/icons/label.png'
            if os.path.exists(path):
                self.label_image = pygame.image.load(path)
        except: pass

        self.call_police_btn = Button(1430, 570, 130, 70, "Call Police", None, style='danger', font_size=27)

        self._init_game()
        self.dragging_item = None
        self.drag_offset = (0, 0)
        self.hovered_item = None
        self.font_small = pygame.font.Font(FONT_PATH, 24)

    def _load_background(self):
        """
        diaobeijing

        :parameter
        :return:
        """
        self.background = pygame.transform.scale(
            pygame.image.load(ASSETS['bg_main']),
            (WINDOW_WIDTH, WINDOW_HEIGHT)
        )

    # TODO 12.04修改替换
    def _load_conveyor_texture(self):
        try:
            # 直接加载图片 (请确保文件名匹配)
            self.conveyor_texture = pygame.image.load('assets/images/conveyor_belt.png')

            # [重要] 直接读取图片宽度，用于后续的居中计算
            # 这样无论您的图片是180px还是200px，都会自动居中
            self.belt_width = self.conveyor_texture.get_width()

        except Exception as e:
            print(f"无法加载传送带图片: {e}")
            # 备用：生成一个灰色矩形
            self.conveyor_texture = pygame.Surface((160, 100))
            self.conveyor_texture.fill((100, 100, 100))
            self.belt_width = 160

    def _spawn_popup(self, x, y, text, c=COLOR_WHITE):
        self.popups.append(FloatingText(x, y, text, c))

    def _init_game(self):
        self._spawn_item_on_conveyor()
        self._spawn_customer()
        try:
            pygame.mixer.music.load('assets/sounds/bgm_gameplay.mp3')
            pygame.mixer.music.set_volume(0.1)
            pygame.mixer.music.play(-1)
        except: pass

    # TODO 12.04修改替换
    def _spawn_item_on_conveyor(self):
        self.batch_pause_states[self.current_batch_id] = {'paused': False, 'timer': 0, 'triggered': False}

        for i in range(ITEMS_PER_BATCH):
            item = Item(random.choice(list(ITEM_DESCRIPTIONS.keys())))
            item.on_conveyor = True
            item.item_index = i
            item.batch_id = self.current_batch_id

            # [修改] 位置计算：
            # X轴：在传送带中心左右稍微随机偏移一点，看起来自然
            x_offset = random.randint(-30, 30)
            target_x = CONVEYOR_CENTER_X + x_offset - item.width // 2

            # Y轴：从屏幕上方(-150)开始，每个物品向上间隔 180 像素
            target_y = -150 - (i * 180)

            item.set_position(target_x, target_y)
            self.conveyor_items.append(item)

        self.current_batch_id += 1

    def _spawn_customer(self):
        empty = [i for i, c in enumerate(self.customer_slots) if c is None]
        if not empty: return
        idx = random.choice(empty)
        desk_items = self.inventory_manager.get_all_items()

        valid_items = [i for i in desk_items if i.item_type != 'sticky_note']

        type = random.choice(valid_items).item_type if valid_items and random.random() < 0.7 else random.choice(list(ITEM_DESCRIPTIONS.keys()))

        c = Customer(type, CUSTOMER_SLOTS[idx])
        self.customer_slots[idx] = c; self.customers.append(c)

    def _spawn_police(self):
        empty_indices = [i for i, slot in enumerate(self.customer_slots) if slot is None]
        if not empty_indices:
            self._spawn_popup(WINDOW_WIDTH//2, WINDOW_HEIGHT//2, "No Space!", COLOR_RED)
            return
        idx = empty_indices[0]
        p = Police(CUSTOMER_SLOTS[idx])
        self.customer_slots[idx] = p
        self.customers.append(p)
        self._spawn_popup(p.x, p.y-80, "Police Arrived!", COLOR_BLUE)

    def _remove_customer(self, c):
        if c in self.customers: self.customers.remove(c)
        if c in self.customer_slots: self.customer_slots[self.customer_slots.index(c)] = None

    # 警察
    def _handle_delivery(self, c, item):
        if isinstance(c, Police):
            if c.police_state == 'waiting_for_note':
                if isinstance(item, StickyNote):
                    c.receive_note(item)
                    self._spawn_popup(c.x, c.y-50, "File Accepted", COLOR_YELLOW)
                    return True
                else:
                    self._spawn_popup(c.x, c.y-50, "Need Case Note!", COLOR_RED)
                    return False
            elif c.police_state == 'waiting_for_evidence':
                if isinstance(item, StickyNote):
                    self._spawn_popup(c.x, c.y-50, "I have the file.", COLOR_YELLOW)
                    return False
                if item.item_type == c.target_item_type:
                    self.money += REWARD_CORRECT * 1.5
                    self._spawn_popup(c.x, c.y-50, "Case Solved!", COLOR_GREEN)
                    self._remove_customer(c)
                    return True
                else:
                    self.money += PENALTY_WRONG
                    self._spawn_popup(c.x, c.y-50, "Wrong Evidence!", COLOR_RED)
                    self._remove_customer(c)
                    return False
            return False

        if c.check_item_match(item):
            self.money += REWARD_CORRECT; self._spawn_popup(c.x, c.y-50, f"+${REWARD_CORRECT}", COLOR_GREEN)
            self._remove_customer(c); return True
        else:
            self.money += PENALTY_WRONG; self._spawn_popup(c.x, c.y-50, "WRONG!", COLOR_RED); return False

    def _handle_rejection(self, c):
        if isinstance(c, Police): return
        note = StickyNote(c.x, 350, c.sought_item_type)
        self.inventory_manager.add_item_to_desk(note)
        self._spawn_popup(c.x, c.y-50, "Filed Case", COLOR_YELLOW)
        self._remove_customer(c)

    def handle_event(self, event):
        mouse = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.call_police_btn.handle_click(mouse):
                    if any(isinstance(c, Police) for c in self.customers):
                        self._spawn_popup(mouse[0], mouse[1], "Police is here!", COLOR_YELLOW)
                    else:
                        self._spawn_police()
                    return
                for c in self.customers:
                    if c.is_arrived and c.reject_button.handle_click(mouse):
                        self._handle_rejection(c); return
                clicked = None
                for i in reversed(self.conveyor_items):
                    if i.contains_point(mouse): clicked = i; i.on_conveyor = False; self.conveyor_items.remove(i); break
                if not clicked:
                    clicked = self.inventory_manager.get_item_at_position(mouse)
                    if clicked: self.inventory_manager.remove_item(clicked)
                if clicked:
                    self.dragging_item = clicked; self.dragging_item.is_selected = True
                    self.drag_offset = (mouse[0]-clicked.x, mouse[1]-clicked.y)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.dragging_item:
                self.dragging_item.is_selected = False
                delivered = False
                for c in self.customers:
                    if c.is_arrived and c.get_delivery_rect().collidepoint(mouse):
                        if self._handle_delivery(c, self.dragging_item): delivered = True
                        break
                if not delivered:
                    new_x = mouse[0] - self.drag_offset[0]; new_y = mouse[1] - self.drag_offset[1]
                    self.dragging_item.set_position(new_x, new_y)
                    self.inventory_manager.add_item_to_desk(self.dragging_item)
                self.dragging_item = None
        elif event.type == pygame.MOUSEMOTION and self.dragging_item:
            self.dragging_item.set_position(mouse[0]-self.drag_offset[0], mouse[1]-self.drag_offset[1])

        self.call_police_btn.update(mouse)

    def update(self, dt):
        self.shift_time += dt
        should_scroll = False
        if self.conveyor_items:
            for item in self.conveyor_items:
                if not self.batch_pause_states.get(item.batch_id, {'paused': False})['paused']: should_scroll = True; break
        if should_scroll: self.scroll_offset += CONVEYOR_SPEED * dt

        self.inventory_manager.update(dt)
        for p in self.popups[:]:
            if not p.update(dt): self.popups.remove(p)

        mouse = pygame.mouse.get_pos()
        if not self.dragging_item:
            self.hovered_item = None
            for i in reversed(self.conveyor_items):
                if i.contains_point(mouse): self.hovered_item = i; break
            if not self.hovered_item: self.hovered_item = self.inventory_manager.get_item_at_position(mouse)
        else: self.hovered_item = None

        if self.shift_time >= self.shift_duration: self._end_shift(); return

        self.item_spawn_timer += dt
        if self.item_spawn_timer >= self.item_spawn_interval: self.item_spawn_timer = 0; self._spawn_item_on_conveyor()

        # TODO (THIS IS AI PROCESS)
        pause_dur = 3.0
        batch_items = {}
        for i in self.conveyor_items:
            if i.batch_id not in batch_items: batch_items[i.batch_id] = []
            batch_items[i.batch_id].append(i)
        for bid, items in batch_items.items():
            if bid in self.batch_pause_states:
                st = self.batch_pause_states[bid]
                t_idx = CONVEYOR_PAUSE_AT_INDEX
                target = next((i for i in items if i.item_index == t_idx), None)
                if target and not st['triggered'] and target.y >= CONVEYOR_PAUSE_TRIGGER_Y: st['paused'] = True; st['triggered'] = True
                if st['paused']:
                    st['timer'] += dt
                    if st['timer'] >= pause_dur: st['paused'] = False

        # TODO 12.04修改替换
        removes = []
        for i in self.conveyor_items[:]:
            if i.on_conveyor:
                paused = self.batch_pause_states.get(i.batch_id, {'paused': False})

                # [修改] 这一行调用去掉了 CONVEYOR_PATH 参数
                if i.update_conveyor_movement(dt, CONVEYOR_SPEED, paused):
                    removes.append(i)

        for r in removes: self.conveyor_items.remove(r)

        self.customer_timer += dt
        if self.customer_timer >= self.customer_interval:
            if None in self.customer_slots: self._spawn_customer(); self.customer_timer = 0
            else: self.customer_timer -= 2
        for c in self.customers[:]:
            c.update(dt)
            if c.is_timeout():
                self.money += PENALTY_TIMEOUT;
                self._spawn_popup(c.x, c.y-50, "Angry!", COLOR_RED);
                self._remove_customer(c)

    def _end_shift(self):
        from game.game_manager import GameState
        self.game_manager.change_state(GameState.GAME_OVER, money=self.money)

    # TODO 12.04修改替换
    def _render_conveyor_belt(self, screen):
        if not self.conveyor_texture: return

        # 获取纹理高度
        tex_h = self.conveyor_texture.get_height()

        # 计算垂直滚动的偏移量 (取模运算实现无限循环)
        y_offset = int(self.scroll_offset) % tex_h

        # 确定绘制的 X 坐标 (左上角)
        draw_x = CONVEYOR_CENTER_X - self.belt_width // 2

        # [修改] 垂直平铺绘制
        # 从 -tex_h 开始画，确保屏幕顶部没有空隙
        for y in range(-tex_h, WINDOW_HEIGHT + tex_h, tex_h):
            screen.blit(self.conveyor_texture, (draw_x, y + y_offset))

    def _draw_item_shadow(self, screen, item, off=(5,5), sc=1.0):
        if not item.image: return
        img = item.image
        if sc != 1.0: img = pygame.transform.scale(img, (int(img.get_width()*sc), int(img.get_height()*sc)))
        try:
            mask = pygame.mask.from_surface(img)
            shad = mask.to_surface(setcolor=(0,0,0,100), unsetcolor=None)
            if sc != 1.0:
                r = shad.get_rect(center=item.get_rect().center); r.x+=off[0]; r.y+=off[1]; screen.blit(shad, r)
            else: screen.blit(shad, (item.x+off[0], item.y+off[1]))
        except: pass

    def _render_item_tooltip(self, screen):
        if not self.hovered_item: return
        mouse_pos = pygame.mouse.get_pos()
        item_name = self.hovered_item.name
        name_surf = self.font_small.render(item_name, True, COLOR_WHITE)
        padding_x = 10; padding_y = 8
        width = name_surf.get_width() + padding_x * 2; height = name_surf.get_height() + padding_y * 2
        x = mouse_pos[0] + 20; y = mouse_pos[1] + 20
        if x + width > WINDOW_WIDTH: x = mouse_pos[0] - width - 10
        if y + height > WINDOW_HEIGHT: y = mouse_pos[1] - height - 10
        if self.label_image:
            bg = pygame.transform.scale(self.label_image, (width, height))
            screen.blit(bg, (x, y))
            text_x = x + (width - name_surf.get_width()) // 2
            text_y = y + (height - name_surf.get_height()) // 2
            screen.blit(name_surf, (text_x, text_y))

    def render(self, screen):
        if self.background: screen.blit(self.background, (0,0))
        else: screen.fill(COLOR_GRAY)
        self._render_conveyor_belt(screen)
        for i in self.conveyor_items: self._draw_item_shadow(screen, i); i.render(screen)
        for i in self.inventory_manager.desk_items: self._draw_item_shadow(screen, i)
        self.inventory_manager.render(screen)
        for c in self.customers: c.render(screen)
        self.hud.render(screen, self.money, self.shift_time, self.shift_duration)
        self.call_police_btn.render(screen)
        if self.dragging_item:
            sc = 1.15
            self._draw_item_shadow(screen, self.dragging_item, (20,20), sc)
            simg = pygame.transform.rotozoom(self.dragging_item.image, 0, sc)
            screen.blit(simg, simg.get_rect(center=self.dragging_item.get_rect().center))
        if self.hovered_item and not self.dragging_item: self._render_item_tooltip(screen)
        for p in self.popups: p.render(screen)