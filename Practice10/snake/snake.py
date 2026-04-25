import pygame, sys, random, time
from pygame.locals import *

pygame.init() # стартуем пайгейм

# базовые настройки окна и сетки
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 400
CELL_SIZE = 20
# считаем, сколько клеток влезет по ширине и высоте (тут 20х20 получается)
COLS = WINDOW_WIDTH // CELL_SIZE
ROWS = WINDOW_HEIGHT // CELL_SIZE

# цвета, чтоб каждый раз rgb не прописывать руками
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Snake Game with Levels")
clock = pygame.time.Clock()

# функция, чтобы спавнить яблоко в рандомном месте
def generate_food(snake_body):
    while True:
        x = random.randint(0, COLS - 1)
        y = random.randint(0, ROWS - 1)
        # главное, чтобы еда не заспавнилась прямо внутри самой змеи
        if (x, y) not in snake_body:
            return (x, y)

# старт игры: змея состоит из одной клетки ровно по центру
snake = [(COLS // 2, ROWS // 2)]
direction = (1, 0) # по дефолту ползем вправо
food = generate_food(snake)

score = 0
level = 1
foods_eaten = 0
speed = 5 # стартовая скорость игры
running = True

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        # чекаем управление
        elif event.type == KEYDOWN:
            # проверки, чтобы змея не могла развернуться на 180 градусов и убить саму себя
            if event.key == K_UP and direction != (0, 1):
                direction = (0, -1)
            elif event.key == K_DOWN and direction != (0, -1):
                direction = (0, 1)
            elif event.key == K_LEFT and direction != (1, 0):
                direction = (-1, 0)
            elif event.key == K_RIGHT and direction != (-1, 0):
                direction = (1, 0)
                
    # берем координаты текущей головы и считаем, куда она наступит на следующем кадре
    head_x, head_y = snake[0]
    new_head = (head_x + direction[0], head_y + direction[1])
    
    # проверки на проигрыш: если вышли за карту или врезались в свой же хвост
    if new_head[0] < 0 or new_head[0] >= COLS or new_head[1] < 0 or new_head[1] >= ROWS or new_head in snake:
        running = False # гг
        
    # добавляем новую голову в начало списка (змея делает шаг)
    snake.insert(0, new_head)
    
    # проверяем, наступили ли мы на еду
    if new_head == food:
        score += 10
        foods_eaten += 1
        food = generate_food(snake) # спавним новую
        
        # каждые 3 яблока повышаем левел и разгоняем змею
        if foods_eaten % 3 == 0:
            level += 1
            speed += 1
    else:
        # если ничего не съели, отрезаем последний кусок хвоста 
        # (чтобы создавалась иллюзия движения, а не бесконечного роста)
        snake.pop()
        
    # отрисовка
    screen.fill(BLACK) # чистим старый кадр
    
    # рисуем яблоко
    food_rect = pygame.Rect(food[0] * CELL_SIZE, food[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, RED, food_rect)
    
    # рисуем саму змею, проходясь по всему списку
    for segment in snake:
        seg_rect = pygame.Rect(segment[0] * CELL_SIZE, segment[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, GREEN, seg_rect)
        
    # выводим текст со счетом и уровнем
    info_text = pygame.font.SysFont("Verdana", 20).render("Score: " + str(score) + "  Level: " + str(level), True, WHITE)
    screen.blit(info_text, (10, 10))
    
    pygame.display.update() # обновляем экран
    clock.tick(speed) # ограничиваем фпс, чтобы не летала как бешеная

pygame.quit()
sys.exit()