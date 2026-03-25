# main.py (增强版复古俄罗斯方块)
# 版本: 2.5 (稳定版)
# 开发工程师: aistudio Gemini
# 日期: 2025-06-23
# 更新日志:
# - [移除] 为保证游戏稳定性，彻底移除了导致按键锁死的“暂存(Hold)”功能。
# - [修复] 将所有可配置参数整合到顶部的“配置中心”，方便用户自定义。
# - [调整] 增加了游戏结束画面按钮的垂直间距，优化布局。
# - [修复] 再次重构事件处理逻辑，彻底解决主菜单和游戏内侧边栏按钮无法点击的问题。
# - [修复] 将“影子”按钮的文字改为英文，以解决因字体不支持中文而导致的乱码问题。
# - [新增] 增加“影子方块”开关功能。
# - [调整] 将“旋转”功能改回空格键，“硬降落”移至“上箭头(↑)”键。

import pygame
import random
import sys
import os
from collections import deque

# =================================================================================
# ====================== ⭐️ 游戏核心配置中心 (可在此处调整) ⭐️ =====================
# =================================================================================
CONFIG = {
    # --- 界面文本与字体 (UI Text & Fonts) ---
    "title_text": "Retro Tetris",
    "font_sizes": {
        "large": 26,  # 大号字体，用于标题
        "medium": 24, # 中号字体 (未使用，备用)
        "small": 16,  # 小号字体，用于UI文本
    },

    # --- 布局与尺寸 (Layout & Sizing) ---
    "scale": 1.2,                 # 全局缩放比例
    "base_block_size": 30,        # 方块的基础像素尺寸
    "sidebar_width": 220,         # 侧边栏宽度
    "padding": 30,                # 窗口内边距
    "gap_between_areas": 30,      # 游戏区与侧边栏的间距
    "game_over_buttons_y_offset": 80, # 游戏结束画面按钮与上方文字的垂直距离

    # --- 游戏难度与手感 (Gameplay & Feel) ---
    "initial_fall_speed": 800,      # 初始下落速度(毫秒)，数字越大越慢
    "speed_increase_per_level": 70, # 每升一级，速度加快多少毫秒
    "lock_delay": 500,              # 方块触底后的锁定延迟(毫秒)
    "move_sideways_delay": 180,     # 长按左右键的初始延迟(毫秒)
    "move_sideways_interval": 40,   # 长按左右键的移动间隔(毫秒)
}
# =================================================================================

# --- 从配置中心计算全局常量 ---
SCALE = CONFIG['scale']
GRID_WIDTH, GRID_HEIGHT = 10, 20
BASE_BLOCK_SIZE = CONFIG['base_block_size']
BLOCK_SIZE = int(BASE_BLOCK_SIZE * SCALE)
SIDEBAR_WIDTH = int(CONFIG['sidebar_width'] * SCALE)
PADDING = int(CONFIG['padding'] * SCALE)
GAP_BETWEEN_AREAS = int(CONFIG['gap_between_areas'] * SCALE)
GAME_AREA_WIDTH = GRID_WIDTH * BLOCK_SIZE
GAME_AREA_HEIGHT = GRID_HEIGHT * BLOCK_SIZE
SCREEN_WIDTH = GAME_AREA_WIDTH + SIDEBAR_WIDTH + PADDING * 2 + GAP_BETWEEN_AREAS
SCREEN_HEIGHT = GAME_AREA_HEIGHT + PADDING * 2
GAME_AREA_X, GAME_AREA_Y = PADDING, PADDING

# --- 颜色定义 ---
BLACK = (20, 20, 30)
WHITE = (224, 224, 224)
GRID_COLOR = (40, 40, 50)
GHOST_COLOR_ALPHA = 80
BUTTON_COLOR = (45, 45, 60)
BUTTON_HOVER_COLOR = (80, 80, 100)
OVERLAY_COLOR = (0, 0, 0, 180)

# --- 方块与计分定义 ---
TETROMINO_DATA = {
    'I': {'shape': [[1, 1, 1, 1]], 'color': (30, 180, 210)},
    'O': {'shape': [[1, 1], [1, 1]], 'color': (230, 200, 40)},
    'T': {'shape': [[0, 1, 0], [1, 1, 1]], 'color': (180, 60, 220)},
    'J': {'shape': [[1, 0, 0], [1, 1, 1]], 'color': (50, 100, 230)},
    'L': {'shape': [[0, 0, 1], [1, 1, 1]], 'color': (220, 130, 30)},
    'S': {'shape': [[0, 1, 1], [1, 1, 0]], 'color': (80, 200, 90)},
    'Z': {'shape': [[1, 1, 0], [0, 1, 1]], 'color': (220, 50, 80)}
}
SCORE_VALUES = {0: 0, 1: 100, 2: 300, 3: 500, 4: 800}
LINES_PER_LEVEL = 10

def resource_path(relative_path):
    try: base_path = sys._MEIPASS
    except Exception: base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# =================================================================================
# ======================== ⭐️ 资源加载模块 ⭐️ ===========================
# =================================================================================
class Assets:
    def __init__(self):
        self.large_font = self._load_font(CONFIG['font_sizes']['large'])
        self.medium_font = self._load_font(CONFIG['font_sizes']['medium'])
        self.small_font = self._load_font(CONFIG['font_sizes']['small'])
        self.sounds = self._load_sounds()
        self.icon = self._load_icon()
        self.set_sound_volumes()

    def _load_font(self, size):
        font_path = resource_path(os.path.join('assets', 'fonts', 'press-start-2p.ttf'))
        try:
            return pygame.font.Font(font_path, int(size * SCALE))
        except pygame.error:
            print(f"Warning: Font file not found at {font_path}. Using default font.")
            return pygame.font.Font(None, int(size * SCALE * 1.2))

    def _load_sounds(self):
        sounds = {}
        sound_files = {
            'drop': 'block-1-328874.mp3', 'clear': 'clear-bell-notification-sound-351709.mp3',
            'level_up': 'game-level-complete-143022.mp3', 'game_over': 'game-over-arcade-6435.mp3'
        }
        try:
            pygame.mixer.music.load(resource_path(os.path.join('assets', 'sounds', 'game-music-loop-6-144641.mp3')))
            for name, filename in sound_files.items():
                sounds[name] = pygame.mixer.Sound(resource_path(os.path.join('assets', 'sounds', filename)))
            return sounds
        except pygame.error as e:
            print(f"Warning: Could not load sounds. {e}. Game will be silent.")
            class DummySound:
                def play(self): pass
                def set_volume(self, v): pass
            return {name: DummySound() for name in sound_files.keys()}

    def _load_icon(self):
        try: return pygame.image.load(resource_path('favicon.ico'))
        except pygame.error: print("Warning: 'favicon.ico' not found."); return None

    def set_sound_volumes(self):
        self.volumes = {'music': 0.3, 'drop': 0.5, 'clear': 0.7, 'level_up': 0.8, 'game_over': 1.0}
        if pygame.mixer.get_init():
            pygame.mixer.music.set_volume(self.volumes['music'])
            for name, sound in self.sounds.items(): sound.set_volume(self.volumes[name])

# =================================================================================
# ======================== ⭐️ 游戏核心逻辑类 ⭐️ =========================
# =================================================================================
class Piece:
    def __init__(self, shape_name):
        self.shape_name = shape_name
        data = TETROMINO_DATA[shape_name]
        self.matrix = data['shape']
        self.color = data['color']
        self.x = GRID_WIDTH // 2 - len(self.matrix[0]) // 2
        self.y = 0

    def rotate(self): self.matrix = list(zip(*self.matrix[::-1]))

class PieceGenerator:
    def __init__(self): self.bag = []; self.refill_bag()
    def refill_bag(self): self.bag = list(TETROMINO_DATA.keys()); random.shuffle(self.bag)
    def next(self):
        if not self.bag: self.refill_bag()
        return Piece(self.bag.pop())

class Grid:
    def __init__(self): self.grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

    def is_valid_position(self, piece, ox=0, oy=0):
        for y, row in enumerate(piece.matrix):
            for x, cell in enumerate(row):
                if cell:
                    new_x, new_y = piece.x + x + ox, piece.y + y + oy
                    if not (0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT and self.grid[new_y][new_x] == BLACK):
                        return False
        return True

    def lock_piece(self, piece):
        for y, row in enumerate(piece.matrix):
            for x, cell in enumerate(row):
                if cell: self.grid[piece.y + y][piece.x + x] = piece.color

    def clear_lines(self):
        lines_to_clear = [i for i, row in enumerate(self.grid) if all(cell != BLACK for cell in row)]
        if lines_to_clear:
            for i in lines_to_clear:
                del self.grid[i]; self.grid.insert(0, [BLACK for _ in range(GRID_WIDTH)])
        return len(lines_to_clear)
    
    def reset(self): self.grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

class ScoreManager:
    def __init__(self): self.reset()
        
    def reset(self):
        self.score = 0; self.level = 1; self.lines_cleared = 0
        self.fall_speed = CONFIG['initial_fall_speed']

    def update(self, cleared_lines):
        leveled_up = False
        self.score += SCORE_VALUES.get(cleared_lines, 0) * self.level
        self.lines_cleared += cleared_lines
        
        new_level = 1 + self.lines_cleared // LINES_PER_LEVEL
        if new_level > self.level:
            self.level = new_level
            self.fall_speed = max(100, CONFIG['initial_fall_speed'] - (self.level - 1) * CONFIG['speed_increase_per_level'])
            leveled_up = True
        return leveled_up

# =================================================================================
# ======================== ⭐️ UI 与渲染类 ⭐️ ===========================
# =================================================================================
class Button:
    def __init__(self, text, pos, size, font, callback):
        self.rect = pygame.Rect(pos, size)
        self.text = text; self.font = font; self.callback = callback
        self.is_hovered = False

    def draw(self, screen):
        color = BUTTON_HOVER_COLOR if self.is_hovered else BUTTON_COLOR
        pygame.draw.rect(screen, color, self.rect, border_radius=int(8 * SCALE))
        surf = self.font.render(self.text, True, WHITE)
        screen.blit(surf, surf.get_rect(center=self.rect.center))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            if self.callback: self.callback()

class UIManager:
    def __init__(self, game, assets):
        self.game = game; self.assets = assets
        self.buttons = {}; self._setup_buttons()

    def _setup_buttons(self):
        btn_w, btn_h = int(180 * SCALE), int(45 * SCALE)
        sidebar_x = GAME_AREA_X + GAME_AREA_WIDTH + GAP_BETWEEN_AREAS
        btn_x = sidebar_x + (SIDEBAR_WIDTH - btn_w) // 2
        btn_gap = int(55 * SCALE)
        
        btn_y_start = SCREEN_HEIGHT - PADDING - (btn_h + int(10*SCALE)) * 4
        self.buttons['in_game'] = [
            Button("Pause", (btn_x, btn_y_start), (btn_w, btn_h), self.assets.small_font, self.game.toggle_pause),
            Button("Restart", (btn_x, btn_y_start + btn_gap), (btn_w, btn_h), self.assets.small_font, self.game.reset),
            Button("Mute", (btn_x, btn_y_start + btn_gap * 2), (btn_w, btn_h), self.assets.small_font, self.game.toggle_mute),
            Button("Ghost:Off", (btn_x, btn_y_start + btn_gap * 3), (btn_w, btn_h), self.assets.small_font, self.game.toggle_ghost)
        ]

        menu_btn_x = SCREEN_WIDTH / 2 - btn_w / 2
        self.buttons['menu'] = [
            Button("Start Game", (menu_btn_x, SCREEN_HEIGHT / 2), (btn_w, btn_h), self.assets.small_font, self.game.start_game),
            Button("Quit", (menu_btn_x, SCREEN_HEIGHT / 2 + btn_gap), (btn_w, btn_h), self.assets.small_font, sys.exit)
        ]
        self.buttons['paused'] = [
            Button("Resume", (menu_btn_x, SCREEN_HEIGHT / 2 - btn_gap), (btn_w, btn_h), self.assets.small_font, self.game.toggle_pause),
            Button("Restart", (menu_btn_x, SCREEN_HEIGHT / 2), (btn_w, btn_h), self.assets.small_font, self.game.reset),
            Button("Quit", (menu_btn_x, SCREEN_HEIGHT / 2 + btn_gap), (btn_w, btn_h), self.assets.small_font, sys.exit)
        ]
        
        game_over_btn_y = SCREEN_HEIGHT/2 + int(CONFIG['game_over_buttons_y_offset'] * SCALE)
        self.buttons['game_over'] = [
            Button("Restart", (menu_btn_x, game_over_btn_y), (btn_w, btn_h), self.assets.small_font, self.game.reset),
            Button("Main Menu", (menu_btn_x, game_over_btn_y + btn_gap), (btn_w, btn_h), self.assets.small_font, self.game.go_to_menu)
        ]

    def get_buttons(self, state): return self.buttons.get(state, [])

class Renderer:
    def __init__(self, screen, assets):
        self.screen = screen; self.assets = assets
        self.crt_scanline_surface = self._create_crt_scanline_surface()

    def _create_crt_scanline_surface(self):
        w, h = self.screen.get_size()
        scanline_surface = pygame.Surface((w, h), pygame.SRCALPHA)
        for y in range(0, h, int(4 * SCALE)):
            pygame.draw.line(scanline_surface, (0, 0, 0, 40), (0, y), (w, y), int(2 * SCALE))
        return scanline_surface

    def draw(self, game):
        self.screen.fill(BLACK)
        if game.state == "menu": self.draw_main_menu(game)
        else:
            self.draw_game_area(game.grid)
            self.draw_piece(game.current_piece)
            if game.show_ghost: self.draw_ghost_piece(game)
            self.draw_sidebar(game)
            if game.state == "paused": self.draw_overlay("PAUSED", game.ui_manager.get_buttons('paused'))
            elif game.state == "game_over": self.draw_game_over_overlay(game)
        self.screen.blit(self.crt_scanline_surface, (0, 0))
        pygame.display.flip()

    def draw_piece(self, piece, ghost=False):
        if not piece: return
        for y, row in enumerate(piece.matrix):
            for x, cell in enumerate(row):
                if cell:
                    rect = (GAME_AREA_X + (piece.x + x) * BLOCK_SIZE, GAME_AREA_Y + (piece.y + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    if ghost:
                        surf = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
                        surf.fill((*piece.color, GHOST_COLOR_ALPHA))
                        self.screen.blit(surf, rect[:2])
                    else:
                        pygame.draw.rect(self.screen, piece.color, rect)
                        pygame.draw.rect(self.screen, WHITE, rect, 1)

    def draw_ghost_piece(self, game):
        if not game.current_piece: return
        ghost = Piece(game.current_piece.shape_name)
        ghost.matrix = game.current_piece.matrix
        ghost.x = game.current_piece.x; ghost.y = game.current_piece.y
        ghost.color = game.current_piece.color
        while game.grid.is_valid_position(ghost, oy=1): ghost.y += 1
        self.draw_piece(ghost, ghost=True)

    def draw_game_area(self, grid_obj):
        for y, row in enumerate(grid_obj.grid):
            for x, color in enumerate(row):
                if color != BLACK:
                    rect = (GAME_AREA_X + x * BLOCK_SIZE, GAME_AREA_Y + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    pygame.draw.rect(self.screen, color, rect); pygame.draw.rect(self.screen, WHITE, rect, 1)
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = (GAME_AREA_X + x * BLOCK_SIZE, GAME_AREA_Y + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(self.screen, GRID_COLOR, rect, 1)

    def draw_sidebar(self, game):
        sidebar_x = GAME_AREA_X + GAME_AREA_WIDTH + GAP_BETWEEN_AREAS
        sidebar_center_x = sidebar_x + SIDEBAR_WIDTH // 2
        def draw_info(label, value, y_pos):
            label_surf = self.assets.small_font.render(label, True, WHITE)
            self.screen.blit(label_surf, label_surf.get_rect(centerx=sidebar_center_x, top=y_pos))
            value_surf = self.assets.small_font.render(str(value), True, WHITE)
            self.screen.blit(value_surf, value_surf.get_rect(centerx=sidebar_center_x, top=y_pos + int(25 * SCALE)))
        draw_info("SCORE", game.score_manager.score, GAME_AREA_Y + int(40*SCALE))
        draw_info("LEVEL", game.score_manager.level, GAME_AREA_Y + int(110*SCALE))
        draw_info("LINES", game.score_manager.lines_cleared, GAME_AREA_Y + int(180*SCALE))

        next_title_y = GAME_AREA_Y + int(260*SCALE)
        next_label_surf = self.assets.small_font.render("NEXT", True, WHITE)
        self.screen.blit(next_label_surf, next_label_surf.get_rect(centerx=sidebar_center_x, top=next_title_y))
        if game.next_piece: self.draw_sidebar_piece(game.next_piece, sidebar_center_x, next_title_y + int(25*SCALE))
        
        
        for btn in game.ui_manager.get_buttons('in_game'): btn.draw(self.screen)

    def draw_sidebar_piece(self, piece, center_x, top_y):
        matrix = piece.matrix
        piece_w_pixels = len(matrix[0]) * BLOCK_SIZE
        start_x = center_x - piece_w_pixels // 2
        for y, row in enumerate(matrix):
            for x, cell in enumerate(row):
                if cell:
                    rect = (start_x + x * BLOCK_SIZE, top_y + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    pygame.draw.rect(self.screen, piece.color, rect); pygame.draw.rect(self.screen, WHITE, rect, 1)

    def draw_overlay(self, text, buttons):
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA); overlay.fill(OVERLAY_COLOR)
        self.screen.blit(overlay, (0, 0))
        main_surf = self.assets.large_font.render(text, True, WHITE)
        self.screen.blit(main_surf, main_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3)))
        for btn in buttons: btn.draw(self.screen)
            
    def draw_game_over_overlay(self, game):
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA); overlay.fill(OVERLAY_COLOR)
        self.screen.blit(overlay, (0, 0))
        
        title_surf = self.assets.large_font.render("GAME OVER", True, WHITE)
        self.screen.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)))
        
        y_start = SCREEN_HEIGHT / 4 + int(100*SCALE); line_height = int(40*SCALE)
        def draw_stat(label, value, y):
            text = f"{label}: {value}"
            surf = self.assets.small_font.render(text, True, WHITE)
            self.screen.blit(surf, surf.get_rect(centerx=SCREEN_WIDTH / 2, top=y))
        draw_stat("Final Score", game.score_manager.score, y_start)
        draw_stat("Level Reached", game.score_manager.level, y_start + line_height)
        draw_stat("Lines Cleared", game.score_manager.lines_cleared, y_start + line_height * 2)

        for btn in game.ui_manager.get_buttons('game_over'): btn.draw(self.screen)

    def draw_main_menu(self, game):
        surf = self.assets.large_font.render(CONFIG['title_text'], True, WHITE)
        self.screen.blit(surf, surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3)))
        for btn in game.ui_manager.get_buttons('menu'): btn.draw(self.screen)
            
# =================================================================================
# ======================== ⭐️ 游戏主控类 ⭐️ ===========================
# =================================================================================
class TetrisGame:
    def __init__(self):
        pygame.init(); pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(f"{CONFIG['title_text']} - 复古方块 - 像素风俄罗斯方块挑战")
        self.assets = Assets()
        if self.assets.icon: pygame.display.set_icon(self.assets.icon)
            
        self.clock = pygame.time.Clock(); self.state = "menu"
        self.grid = Grid(); self.score_manager = ScoreManager()
        self.piece_generator = PieceGenerator(); self.renderer = Renderer(self.screen, self.assets)
        self.ui_manager = UIManager(self, self.assets)
        
        self.fall_time = 0; self.lock_timer = None
        self.current_piece = None; self.next_piece = None
        # --- [移除] 移除暂存功能相关的状态变量 ---
        self.is_muted = False; self.show_ghost = False
        self.move_sideways_time = 0; self.key_down_time = {'left': 0, 'right': 0}

    def reset(self):
        self.grid.reset(); self.score_manager.reset(); self.piece_generator.refill_bag()
        self.current_piece = self.piece_generator.next(); self.next_piece = self.piece_generator.next()
        self.fall_time = pygame.time.get_ticks(); self.lock_timer = None
        self.state = "playing"
        if not self.is_muted and pygame.mixer.get_init(): pygame.mixer.music.play(-1)

    def start_game(self): self.reset()
    def go_to_menu(self): self.state = "menu"; pygame.mixer.music.stop() if pygame.mixer.get_init() else None

    def toggle_pause(self):
        if self.state == "playing": self.state = "paused"; pygame.mixer.music.pause() if pygame.mixer.get_init() else None
        elif self.state == "paused": self.state = "playing"; pygame.mixer.music.unpause() if not self.is_muted and pygame.mixer.get_init() else None

    def toggle_mute(self):
        self.is_muted = not self.is_muted
        self.ui_manager.buttons['in_game'][2].text = "Unmute" if self.is_muted else "Mute"
        if pygame.mixer.get_init():
            music_vol = self.assets.volumes['music'] if not self.is_muted else 0
            pygame.mixer.music.set_volume(music_vol)
            for name, sound in self.assets.sounds.items(): sound.set_volume(self.assets.volumes[name] if not self.is_muted else 0)
    
    def toggle_ghost(self):
        self.show_ghost = not self.show_ghost
        self.ui_manager.buttons['in_game'][3].text = "Ghost: On" if self.show_ghost else "Ghost: Off"

    def move(self, dx, dy):
        if not self.current_piece: return False
        if self.grid.is_valid_position(self.current_piece, dx, dy):
            self.current_piece.x += dx; self.current_piece.y += dy
            self.reset_lock_delay(); return True
        return False

    def rotate(self):
        if not self.current_piece: return
        original_matrix = self.current_piece.matrix
        self.current_piece.rotate()
        if not self.grid.is_valid_position(self.current_piece):
            if self.grid.is_valid_position(self.current_piece, ox=1): self.current_piece.x += 1
            elif self.grid.is_valid_position(self.current_piece, ox=-1): self.current_piece.x -= 1
            else: self.current_piece.matrix = original_matrix; return
        self.reset_lock_delay()

    def hard_drop(self):
        if not self.current_piece: return
        while self.grid.is_valid_position(self.current_piece, oy=1): self.current_piece.y += 1
        self.lock_piece()

    def lock_piece(self):
        self.grid.lock_piece(self.current_piece)
        if self.assets.sounds.get('drop'): self.assets.sounds['drop'].play()
        
        cleared_lines = self.grid.clear_lines()
        if cleared_lines > 0:
            if self.assets.sounds.get('clear'): self.assets.sounds['clear'].play()
            if self.score_manager.update(cleared_lines):
                if self.assets.sounds.get('level_up'): self.assets.sounds['level_up'].play()

        self.current_piece = self.next_piece
        self.next_piece = self.piece_generator.next()
        self.lock_timer = None
        if not self.grid.is_valid_position(self.current_piece):
            self.state = "game_over"
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                if self.assets.sounds.get('game_over'): self.assets.sounds['game_over'].play()
    
    def reset_lock_delay(self):
        if self.current_piece and not self.grid.is_valid_position(self.current_piece, oy=1):
            self.lock_timer = pygame.time.get_ticks()

    def run(self):
        while True:
            now = pygame.time.get_ticks()
            self.handle_events(now)
            if self.state == "playing": self.update(now)
            self.renderer.draw(self)
            self.clock.tick(60)

    def handle_events(self, now):
        if self.state == "playing":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_DOWN] or keys[pygame.K_s]: self.move(0, 1)
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                if now - self.key_down_time.get('left', 0) > CONFIG['move_sideways_delay'] and now - self.move_sideways_time > CONFIG['move_sideways_interval']:
                    self.move(-1, 0); self.move_sideways_time = now
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                if now - self.key_down_time.get('right', 0) > CONFIG['move_sideways_delay'] and now - self.move_sideways_time > CONFIG['move_sideways_interval']:
                    self.move(1, 0); self.move_sideways_time = now
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if self.state == 'menu': self.handle_menu_events(event)
            elif self.state == 'playing': self.handle_playing_events(event, now)
            elif self.state == 'paused': self.handle_paused_events(event)
            elif self.state == 'game_over': self.handle_game_over_events(event)

    def handle_menu_events(self, event):
        for btn in self.ui_manager.get_buttons('menu'): btn.handle_event(event)

    def handle_playing_events(self, event, now):
        for btn in self.ui_manager.get_buttons('in_game'): btn.handle_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_LEFT, pygame.K_a]: self.move(-1, 0); self.key_down_time['left'] = now
            elif event.key in [pygame.K_RIGHT, pygame.K_d]: self.move(1, 0); self.key_down_time['right'] = now
            elif event.key in [pygame.K_SPACE, pygame.K_x, pygame.K_w]: self.rotate()
            elif event.key == pygame.K_UP: self.hard_drop()
            elif event.key == pygame.K_ESCAPE: self.toggle_pause()
        if event.type == pygame.KEYUP:
            if event.key in [pygame.K_LEFT, pygame.K_a]: self.key_down_time['left'] = 0
            if event.key in [pygame.K_RIGHT, pygame.K_d]: self.key_down_time['right'] = 0

    def handle_paused_events(self, event):
        for btn in self.ui_manager.get_buttons('paused'): btn.handle_event(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: self.toggle_pause()
            
    def handle_game_over_events(self, event):
        for btn in self.ui_manager.get_buttons('game_over'): btn.handle_event(event)
        if event.type == pygame.KEYDOWN and event.key in [pygame.K_r, pygame.K_RETURN]: self.reset()

    def update(self, now):
        if self.current_piece is None: return
        if now - self.fall_time > self.score_manager.fall_speed:
            self.fall_time = now
            if not self.move(0, 1):
                if self.lock_timer is None: self.lock_timer = now
        if self.lock_timer and now - self.lock_timer > CONFIG['lock_delay']:
            if not self.grid.is_valid_position(self.current_piece, oy=1): self.lock_piece()

if __name__ == '__main__':
    game = TetrisGame()
    game.run()
