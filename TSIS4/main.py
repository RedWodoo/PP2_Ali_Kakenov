"""
TSIS 4 — Змейка с базой данных и продвинутым геймплеем
Машина состояний: МЕНЮ -> ИМЯ -> ИГРА -> КОНЕЦ -> ЛИДЕРЫ -> НАСТРОЙКИ

Возможности:
  - Таблица лидеров в PostgreSQL (players + game_sessions)
  - Взвешенная еда + исчезающая еда (из Practice 11)
  - Ядовитая еда (укорачивает змейку, смерть если слишком короткая)
  - 3 усиления: ускорение, замедление, щит
  - Препятствия с 3-го уровня (стены)
  - Настройки сохраняются в settings.json
  - 4 экрана: главное меню, конец игры, лидеры, настройки
"""
import pygame, sys, random, json, os
from pygame.locals import *

# пробуем подключить модуль БД; если PostgreSQL нет — работаем без него
try:
    from db import setup_database, save_result, get_top10, get_personal_best
    DB_AVAILABLE = True
except Exception:
    DB_AVAILABLE = False

pygame.init()

# ---- ОКНО И СЕТКА ----
W, H = 500, 540  # доп. высота для панели сверху
GRID_Y = 40       # сетка начинается ниже панели
GRID_W, GRID_H = 500, 500
CELL = 20
COLS = GRID_W // CELL
ROWS = GRID_H // CELL

screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Snake — TSIS 4")
clock = pygame.time.Clock()

# ---- ЦВЕТА ----
BLACK   = (0, 0, 0)
WHITE   = (255, 255, 255)
GREEN   = (0, 255, 0)
DGREEN  = (0, 180, 0)
RED     = (255, 0, 0)
DRED    = (139, 0, 0)
ORANGE  = (255, 165, 0)
GOLD    = (255, 215, 0)
CYAN    = (0, 220, 220)
BLUE    = (0, 100, 255)
PURPLE  = (180, 0, 255)
GRAY    = (120, 120, 120)
DARK    = (30, 30, 30)
BROWN   = (100, 60, 20)

# ---- ШРИФТЫ ----
font_big = pygame.font.SysFont("Verdana", 36, bold=True)
font_med = pygame.font.SysFont("Verdana", 20)
font_sm  = pygame.font.SysFont("Verdana", 14)

# ---- ТИПЫ ЕДЫ ----
FOOD_TYPES = [
    {"color": RED,    "value": 10, "lifetime": 8000},
    {"color": ORANGE, "value": 20, "lifetime": 6000},
    {"color": GOLD,   "value": 50, "lifetime": 4000},
]
FOOD_WEIGHTS = [60, 30, 10]

# ---- НАСТРОЙКИ ----
SETTINGS_FILE = "settings.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE) as f:
                return json.load(f)
        except: pass
    return {"snake_color": [0,255,0], "grid": True, "sound": True}

def save_settings(s):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(s, f, indent=2)


# ---- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ----
def cell_to_pixel(cx, cy):
    return (cx * CELL, GRID_Y + cy * CELL)

def draw_cell(surface, cx, cy, color):
    x, y = cell_to_pixel(cx, cy)
    pygame.draw.rect(surface, color, (x, y, CELL, CELL))

def draw_btn(surface, text, rect, font, mouse_pos, base=(80,80,80)):
    hover = tuple(min(c+40,255) for c in base)
    color = hover if rect.collidepoint(mouse_pos) else base
    pygame.draw.rect(surface, color, rect, border_radius=8)
    pygame.draw.rect(surface, WHITE, rect, 2, border_radius=8)
    txt = font.render(text, True, WHITE)
    surface.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))


# ==================================================================
# ЭКРАНЫ
# ==================================================================
def main_menu():
    """Главное меню. Возвращает: 'play', 'leaderboard', 'settings', 'quit'"""
    btns = {
        "play":        pygame.Rect(W//2-80, 200, 160, 45),
        "leaderboard": pygame.Rect(W//2-80, 265, 160, 45),
        "settings":    pygame.Rect(W//2-80, 330, 160, 45),
        "quit":        pygame.Rect(W//2-80, 395, 160, 45),
    }
    while True:
        mp = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == QUIT: return "quit"
            if e.type == MOUSEBUTTONDOWN and e.button == 1:
                for k, r in btns.items():
                    if r.collidepoint(e.pos): return k
        screen.fill(DARK)
        title = font_big.render("SNAKE", True, GREEN)
        screen.blit(title, (W//2-title.get_width()//2, 70))
        sub = font_med.render("TSIS 4 — Advanced", True, GRAY)
        screen.blit(sub, (W//2-sub.get_width()//2, 130))
        draw_btn(screen, "Play", btns["play"], font_med, mp, (0,150,0))
        draw_btn(screen, "Leaderboard", btns["leaderboard"], font_med, mp, (0,80,200))
        draw_btn(screen, "Settings", btns["settings"], font_med, mp)
        draw_btn(screen, "Quit", btns["quit"], font_med, mp, (180,0,0))
        pygame.display.update()
        clock.tick(30)


def username_screen():
    """Экран ввода имени. Возвращает строку."""
    name = ""
    while True:
        for e in pygame.event.get():
            if e.type == QUIT: return ""
            if e.type == KEYDOWN:
                if e.key == K_RETURN and name.strip(): return name.strip()
                elif e.key == K_BACKSPACE: name = name[:-1]
                elif e.unicode.isprintable() and len(name) < 15: name += e.unicode
        screen.fill(DARK)
        screen.blit(font_big.render("Enter Name", True, WHITE), (W//2-120, 150))
        box = pygame.Rect(W//2-100, 230, 200, 40)
        pygame.draw.rect(screen, WHITE, box, 2, border_radius=4)
        screen.blit(font_med.render(name+"|", True, GOLD), (box.x+8, box.y+8))
        screen.blit(font_sm.render("Press ENTER", True, GRAY), (W//2-45, 285))
        pygame.display.update()
        clock.tick(30)


def game_over_screen(score, level, personal_best):
    """Экран конца игры. Возвращает 'retry' или 'menu'."""
    btn_r = pygame.Rect(W//2-110, 350, 100, 40)
    btn_m = pygame.Rect(W//2+10,  350, 100, 40)
    while True:
        mp = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == QUIT: return "menu"
            if e.type == MOUSEBUTTONDOWN and e.button == 1:
                if btn_r.collidepoint(e.pos): return "retry"
                if btn_m.collidepoint(e.pos): return "menu"
        screen.fill((120, 20, 20))
        screen.blit(font_big.render("GAME OVER", True, WHITE), (W//2-130, 80))
        y = 170
        for txt in [f"Score: {score}", f"Level: {level}", f"Personal Best: {personal_best}"]:
            screen.blit(font_med.render(txt, True, (220,220,220)), (W//2-80, y))
            y += 35
        draw_btn(screen, "Retry", btn_r, font_med, mp, (0,150,0))
        draw_btn(screen, "Menu", btn_m, font_med, mp)
        pygame.display.update()
        clock.tick(30)


def leaderboard_scr():
    """Экран лидеров — топ 10 из базы."""
    entries = get_top10() if DB_AVAILABLE else []
    btn = pygame.Rect(W//2-50, H-60, 100, 40)
    while True:
        mp = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == QUIT: return
            if e.type == MOUSEBUTTONDOWN and e.button == 1:
                if btn.collidepoint(e.pos): return
        screen.fill(DARK)
        screen.blit(font_big.render("LEADERBOARD", True, GOLD), (W//2-140, 20))
        y = 80
        header = font_sm.render(f"{'#':<4}{'Name':<14}{'Score':<8}{'Lvl':<5}{'Date':<12}", True, WHITE)
        screen.blit(header, (30, y)); y += 25
        pygame.draw.line(screen, GRAY, (30, y), (W-30, y)); y += 5
        for i, e in enumerate(entries[:10]):
            c = GOLD if i==0 else (192,192,192) if i==1 else (205,127,50) if i==2 else WHITE
            date_str = str(e[3])[:10] if e[3] else "?"
            row = font_sm.render(f"{i+1:<4}{str(e[0]):<14}{e[1]:<8}{e[2]:<5}{date_str}", True, c)
            screen.blit(row, (30, y)); y += 22
        if not entries:
            screen.blit(font_med.render("No scores yet!", True, GRAY), (W//2-80, 150))
        draw_btn(screen, "Back", btn, font_med, mp)
        pygame.display.update()
        clock.tick(30)


def settings_scr():
    """Настройки: цвет змейки, сетка, звук."""
    settings = load_settings()
    colors = [(0,255,0), (0,150,255), (255,255,0), (255,100,100), (200,0,255)]
    ci = 0
    for i, c in enumerate(colors):
        if list(c) == settings.get("snake_color", [0,255,0]): ci = i
    grid_on = settings.get("grid", True)
    sound_on = settings.get("sound", True)

    btn_cl = pygame.Rect(W//2-100, 160, 40, 35)
    btn_cr = pygame.Rect(W//2+60, 160, 40, 35)
    btn_grid = pygame.Rect(W//2-60, 230, 120, 35)
    btn_snd = pygame.Rect(W//2-60, 290, 120, 35)
    btn_save = pygame.Rect(W//2-50, H-60, 100, 40)

    while True:
        mp = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == QUIT: return
            if e.type == MOUSEBUTTONDOWN and e.button == 1:
                if btn_cl.collidepoint(e.pos): ci = (ci-1) % len(colors)
                elif btn_cr.collidepoint(e.pos): ci = (ci+1) % len(colors)
                elif btn_grid.collidepoint(e.pos): grid_on = not grid_on
                elif btn_snd.collidepoint(e.pos): sound_on = not sound_on
                elif btn_save.collidepoint(e.pos):
                    settings["snake_color"] = list(colors[ci])
                    settings["grid"] = grid_on
                    settings["sound"] = sound_on
                    save_settings(settings)
                    return

        screen.fill(DARK)
        screen.blit(font_big.render("SETTINGS", True, WHITE), (W//2-100, 40))
        # выбор цвета змейки
        draw_btn(screen, "<", btn_cl, font_med, mp)
        draw_btn(screen, ">", btn_cr, font_med, mp)
        pygame.draw.rect(screen, colors[ci], (W//2-15, 165, 30, 25))
        lbl = font_sm.render("Snake Color", True, GRAY)
        screen.blit(lbl, (W//2 - lbl.get_width()//2, 200))
        # переключатель сетки
        gc = (0,180,0) if grid_on else (150,0,0)
        draw_btn(screen, f"Grid: {'ON' if grid_on else 'OFF'}", btn_grid, font_med, mp, gc)
        # переключатель звука
        sc = (0,180,0) if sound_on else (150,0,0)
        draw_btn(screen, f"Sound: {'ON' if sound_on else 'OFF'}", btn_snd, font_med, mp, sc)
        draw_btn(screen, "Save", btn_save, font_med, mp, (0,150,0))
        pygame.display.update()
        clock.tick(30)


# ==================================================================
# ИГРОВАЯ ЛОГИКА
# ==================================================================
def run_game(username, settings):
    """Запускаем одну игровую сессию. Возвращает (score, level)."""
    snake_color = tuple(settings.get("snake_color", [0,255,0]))
    show_grid = settings.get("grid", True)

    snake = [(COLS//2, ROWS//2)]
    direction = (1, 0)
    next_dir = direction

    # препятствия нужно создать ДО gen_food (используются в замыкании)
    obstacles = set()

    # генерация еды
    def gen_food():
        while True:
            pos = (random.randint(0, COLS-1), random.randint(0, ROWS-1))
            if pos not in snake and pos not in obstacles:
                return pos

    def pick_type():
        return random.choices(FOOD_TYPES, weights=FOOD_WEIGHTS, k=1)[0]

    food_pos = gen_food()
    food_type = pick_type()
    food_time = pygame.time.get_ticks()

    # ядовитая еда
    poison_pos = gen_food()
    poison_time = pygame.time.get_ticks()
    POISON_LIFETIME = 10000

    # усиление
    powerup_pos = None
    powerup_kind = None  # "speed", "slow", "shield"
    powerup_spawn_time = 0
    POWERUP_FIELD_TIMEOUT = 8000
    active_pu = None  # (вид, время_истечения)
    shield_active = False

    score = 0
    level = 1
    foods_eaten = 0
    base_speed = 5
    speed = base_speed

    # личный рекорд из базы
    pbest = 0
    if DB_AVAILABLE:
        pbest = get_personal_best(username)

    def spawn_obstacles(count):
        """Расставляем стены, не блокируя змейку."""
        placed = 0
        for _ in range(count * 20):
            ox = random.randint(1, COLS-2)
            oy = random.randint(1, ROWS-2)
            pos = (ox, oy)
            if pos in snake or pos == food_pos or pos == poison_pos:
                continue
            hx, hy = snake[0]
            if abs(ox-hx) <= 2 and abs(oy-hy) <= 2:
                continue
            obstacles.add(pos)
            placed += 1
            if placed >= count: break

    def maybe_spawn_powerup():
        nonlocal powerup_pos, powerup_kind, powerup_spawn_time
        if powerup_pos is None and random.random() < 0.02:
            powerup_kind = random.choice(["speed", "slow", "shield"])
            p = gen_food()
            if p not in obstacles:
                powerup_pos = p
                powerup_spawn_time = pygame.time.get_ticks()

    running = True
    while running:
        now = pygame.time.get_ticks()

        for e in pygame.event.get():
            if e.type == QUIT:
                pygame.quit(); sys.exit()
            if e.type == KEYDOWN:
                if e.key == K_UP and direction != (0,1): next_dir = (0,-1)
                elif e.key == K_DOWN and direction != (0,-1): next_dir = (0,1)
                elif e.key == K_LEFT and direction != (1,0): next_dir = (-1,0)
                elif e.key == K_RIGHT and direction != (-1,0): next_dir = (1,0)

        direction = next_dir

        # исчезающая еда
        if now - food_time >= food_type["lifetime"]:
            food_pos = gen_food()
            food_type = pick_type()
            food_time = now

        # исчезающий яд
        if now - poison_time >= POISON_LIFETIME:
            poison_pos = gen_food()
            poison_time = now

        # тайм-аут усиления на поле
        if powerup_pos and now - powerup_spawn_time >= POWERUP_FIELD_TIMEOUT:
            powerup_pos = None

        # проверяем активное усиление
        actual_speed = speed
        if active_pu:
            kind, expire = active_pu
            if now > expire:
                active_pu = None
                shield_active = False
            else:
                if kind == "speed": actual_speed = speed + 4
                elif kind == "slow": actual_speed = max(2, speed - 3)

        maybe_spawn_powerup()

        # двигаем змейку
        hx, hy = snake[0]
        nx, ny = hx + direction[0], hy + direction[1]

        # столкновение со стеной
        if nx < 0 or nx >= COLS or ny < 0 or ny >= ROWS:
            if shield_active:
                shield_active = False; active_pu = None
                nx = max(0, min(COLS-1, nx)); ny = max(0, min(ROWS-1, ny))
            else:
                running = False; continue

        # столкновение с собой
        if (nx, ny) in snake:
            if shield_active:
                shield_active = False; active_pu = None
            else:
                running = False; continue

        # столкновение с препятствием
        if (nx, ny) in obstacles:
            if shield_active:
                shield_active = False; active_pu = None
                obstacles.discard((nx, ny))
            else:
                running = False; continue

        snake.insert(0, (nx, ny))

        # подобрали еду
        if (nx, ny) == food_pos:
            score += food_type["value"]
            foods_eaten += 1
            food_pos = gen_food()
            food_type = pick_type()
            food_time = now
            if foods_eaten % 3 == 0:
                level += 1
                speed = base_speed + level - 1
                # с 3-го уровня появляются стены
                if level >= 3:
                    spawn_obstacles(random.randint(2, 4))
        # съели яд
        elif (nx, ny) == poison_pos:
            for _ in range(2):
                if len(snake) > 1: snake.pop()
            if len(snake) <= 1:
                running = False; continue
            poison_pos = gen_food()
            poison_time = now
            snake.pop()
        # подобрали усиление
        elif powerup_pos and (nx, ny) == powerup_pos:
            if active_pu is None:
                if powerup_kind == "speed": active_pu = ("speed", now + 5000)
                elif powerup_kind == "slow": active_pu = ("slow", now + 5000)
                elif powerup_kind == "shield":
                    shield_active = True; active_pu = ("shield", now + 999999)
            powerup_pos = None
            snake.pop()
        else:
            snake.pop()

        # ---- ОТРИСОВКА ----
        screen.fill(BLACK)

        # сетка
        if show_grid:
            for gx in range(COLS + 1):
                pygame.draw.line(screen, (25,25,25), (gx*CELL, GRID_Y), (gx*CELL, GRID_Y+GRID_H))
            for gy in range(ROWS + 1):
                pygame.draw.line(screen, (25,25,25), (0, GRID_Y+gy*CELL), (GRID_W, GRID_Y+gy*CELL))

        # препятствия
        for ox, oy in obstacles:
            draw_cell(screen, ox, oy, BROWN)

        # еда
        draw_cell(screen, food_pos[0], food_pos[1], food_type["color"])
        # полоска таймера
        elapsed = now - food_time
        ratio = max(0, 1.0 - elapsed / food_type["lifetime"])
        bar_w = int(CELL * ratio)
        bx, by = cell_to_pixel(food_pos[0], food_pos[1])
        bar_color = (int(255*(1-ratio)), int(255*ratio), 0)
        pygame.draw.rect(screen, bar_color, (bx, by+CELL, bar_w, 3))

        # ядовитая еда
        draw_cell(screen, poison_pos[0], poison_pos[1], DRED)
        px, py = cell_to_pixel(poison_pos[0], poison_pos[1])
        skull = font_sm.render("X", True, WHITE)
        screen.blit(skull, (px + CELL//2 - skull.get_width()//2, py + 2))

        # усиление
        if powerup_pos:
            pu_colors = {"speed": ORANGE, "slow": CYAN, "shield": BLUE}
            pu_labels = {"speed": "Sp", "slow": "Sl", "shield": "Sh"}
            draw_cell(screen, powerup_pos[0], powerup_pos[1], pu_colors.get(powerup_kind, WHITE))
            px2, py2 = cell_to_pixel(powerup_pos[0], powerup_pos[1])
            plbl = font_sm.render(pu_labels.get(powerup_kind, "?"), True, BLACK)
            screen.blit(plbl, (px2+2, py2+2))

        # змейка (голова ярче тела)
        for i, (sx, sy) in enumerate(snake):
            c = snake_color if i > 0 else tuple(min(ci+40,255) for ci in snake_color)
            draw_cell(screen, sx, sy, c)
            if shield_active and i == 0:
                cx, cy = cell_to_pixel(sx, sy)
                pygame.draw.rect(screen, CYAN, (cx, cy, CELL, CELL), 2)

        # верхняя панель
        pygame.draw.rect(screen, DARK, (0, 0, W, GRID_Y))
        screen.blit(font_sm.render(f"Score:{score}  Lvl:{level}  Best:{pbest}", True, WHITE), (5, 5))
        screen.blit(font_sm.render(f"Spd:{actual_speed}  {username}", True, GRAY), (5, 22))

        if active_pu:
            kind, expire = active_pu
            rem = max(0, (expire - now) // 1000)
            pu_txt = f"[{kind.upper()}] {rem}s" if kind != "shield" else "[SHIELD]"
            screen.blit(font_sm.render(pu_txt, True, CYAN), (W-120, 5))

        pygame.display.update()
        clock.tick(actual_speed)

    return score, level


# ==================================================================
# МАШИНА СОСТОЯНИЙ
# ==================================================================
def main():
    if DB_AVAILABLE:
        setup_database()

    username = ""

    while True:
        action = main_menu()
        if action == "quit":
            break
        elif action == "leaderboard":
            leaderboard_scr()
        elif action == "settings":
            settings_scr()
        elif action == "play":
            if not username:
                username = username_screen()
                if not username:
                    continue
            settings = load_settings()
            while True:
                score, level = run_game(username, settings)
                if DB_AVAILABLE:
                    save_result(username, score, level)
                pbest = get_personal_best(username) if DB_AVAILABLE else score
                result = game_over_screen(score, level, pbest)
                if result == "retry": continue
                else: break

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
