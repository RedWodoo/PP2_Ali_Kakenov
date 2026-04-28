"""
Practice 11 — Змейка (Snake)
Расширение Practice 10:
  1. Случайная генерация еды с разным весом (стоимостью)
  2. Еда исчезает через таймер, если не успел съесть
  3. Весь код прокомментирован
"""
import pygame, sys, random
from pygame.locals import *

pygame.init()

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 400
CELL_SIZE = 20
COLS = WINDOW_WIDTH // CELL_SIZE
ROWS = WINDOW_HEIGHT // CELL_SIZE

BLACK  = (0, 0, 0)
WHITE  = (255, 255, 255)
GREEN  = (0, 255, 0)
RED    = (255, 0, 0)
ORANGE = (255, 165, 0)
GOLD   = (255, 215, 0)

# типы еды: цвет, очки, время жизни в миллисекундах
FOOD_TYPES = [
    {"color": RED,    "value": 10, "lifetime_ms": 8000, "label": "10"},
    {"color": ORANGE, "value": 20, "lifetime_ms": 6000, "label": "20"},
    {"color": GOLD,   "value": 50, "lifetime_ms": 4000, "label": "50"},
]
FOOD_WEIGHTS = [60, 30, 10]

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Snake — Practice 11 (Weighted & Disappearing Food)")
clock = pygame.time.Clock()

def generate_food(snake_body):
    """Генерируем еду в случайной клетке, не на змейке."""
    while True:
        x = random.randint(0, COLS - 1)
        y = random.randint(0, ROWS - 1)
        if (x, y) not in snake_body:
            return (x, y)

def pick_food_type():
    """Случайно выбираем тип еды с учётом вероятностей."""
    return random.choices(FOOD_TYPES, weights=FOOD_WEIGHTS, k=1)[0]

# начальное состояние
snake = [(COLS // 2, ROWS // 2)]
direction = (1, 0)
food_pos = generate_food(snake)
food_type = pick_food_type()
food_spawn_time = pygame.time.get_ticks()

score = 0
level = 1
foods_eaten = 0
speed = 5
running = True

while running:
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_UP and direction != (0, 1):
                direction = (0, -1)
            elif event.key == K_DOWN and direction != (0, -1):
                direction = (0, 1)
            elif event.key == K_LEFT and direction != (1, 0):
                direction = (-1, 0)
            elif event.key == K_RIGHT and direction != (-1, 0):
                direction = (1, 0)

    # исчезающая еда: если время вышло — респавним
    elapsed = current_time - food_spawn_time
    if elapsed >= food_type["lifetime_ms"]:
        food_pos = generate_food(snake)
        food_type = pick_food_type()
        food_spawn_time = current_time

    # двигаем змейку
    head_x, head_y = snake[0]
    new_head = (head_x + direction[0], head_y + direction[1])

    if (new_head[0] < 0 or new_head[0] >= COLS or
        new_head[1] < 0 or new_head[1] >= ROWS or
        new_head in snake):
        running = False

    snake.insert(0, new_head)

    if new_head == food_pos:
        score += food_type["value"]
        foods_eaten += 1
        food_pos = generate_food(snake)
        food_type = pick_food_type()
        food_spawn_time = current_time
        if foods_eaten % 3 == 0:
            level += 1
            speed += 1
    else:
        snake.pop()

    # --- отрисовка ---
    screen.fill(BLACK)

    # рисуем еду
    food_rect = pygame.Rect(food_pos[0]*CELL_SIZE, food_pos[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, food_type["color"], food_rect)
    lbl_font = pygame.font.SysFont("Verdana", 10)
    lbl = lbl_font.render(food_type["label"], True, BLACK)
    screen.blit(lbl, (food_rect.centerx - lbl.get_width()//2, food_rect.centery - lbl.get_height()//2))

    # полоска таймера под едой — показывает сколько осталось
    ratio = max(0, 1.0 - elapsed / food_type["lifetime_ms"])
    bar_w = int(CELL_SIZE * ratio)
    bar_color = (int(255*(1-ratio)), int(255*ratio), 0)
    pygame.draw.rect(screen, bar_color, (food_pos[0]*CELL_SIZE, food_pos[1]*CELL_SIZE+CELL_SIZE, bar_w, 3))

    # рисуем змейку (голова чуть ярче)
    for i, seg in enumerate(snake):
        color = (0, 255, 0) if i == 0 else (0, 200, 0)
        pygame.draw.rect(screen, color, (seg[0]*CELL_SIZE, seg[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # верхняя панель с инфой
    hud = pygame.font.SysFont("Verdana", 16).render(f"Score: {score}  Level: {level}  Speed: {speed}", True, WHITE)
    screen.blit(hud, (10, 5))

    pygame.display.update()
    clock.tick(speed)

pygame.quit()
sys.exit()
