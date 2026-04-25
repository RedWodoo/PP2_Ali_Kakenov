import pygame, sys, random, time
from pygame.locals import *

pygame.init()

font = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)
game_over_text = font.render("Game Over", True, (0,0,0))

background = pygame.image.load("AnimatedStreet.png")

scr_width = 400
scr_height = 600
speed = 5
score = 0      
coinscore = 0  

disp = pygame.display.set_mode((scr_width, scr_height))
pygame.display.set_caption("Racer: Fair Spawns & Restart")
FPS = pygame.time.Clock()

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Enemy.png")
        self.rect = self.image.get_rect()
        self.respawn() 

    def move(self):
        global score 
        self.rect.move_ip(0, speed) 
        if (self.rect.bottom > scr_height):
            score += 1
            self.respawn()

    def respawn(self):
        while True:
            self.rect.top = 0
            self.rect.centerx = random.randint(30, scr_width-30)
            try:
                safe_zone = C.rect.inflate(100, 250)
                if not self.rect.colliderect(safe_zone):
                    break 
            except NameError:
                break

class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Coin.png")
        self.rect = self.image.get_rect()
        self.respawn()
    
    def move(self):
        self.rect.move_ip(0, speed)
        if (self.rect.bottom > scr_height):
            self.respawn() 

    def disappear(self):
        global coinscore
        coinscore += 1
        self.respawn() 
        
    def respawn(self):
        while True:
            self.rect.top = -50 
            self.rect.centerx = random.randint(40, scr_width-40)
            safe_zone = E.rect.inflate(100, 250)
            if not self.rect.colliderect(safe_zone):
                break 

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Player.png")
        self.rect = self.image.get_rect()
        self.rect.center = (200, 500) 

    def move(self):
        pressed_keys = pygame.key.get_pressed()
        if self.rect.left > 0 and pressed_keys[K_LEFT]:
            self.rect.move_ip(-5, 0)
        if self.rect.right < scr_width and pressed_keys[K_RIGHT]:
            self.rect.move_ip(5, 0)
        if self.rect.top > 0 and pressed_keys[K_UP]:
            self.rect.move_ip(0, -5)
        if self.rect.bottom < scr_height and pressed_keys[K_DOWN]:
            self.rect.move_ip(0, 5)

E = Enemy()
C = Coin()
P = Player()

Enemies = pygame.sprite.Group()
Enemies.add(E)
Coins = pygame.sprite.Group()
Coins.add(C)
all_sprites = pygame.sprite.Group()
all_sprites.add(E)
all_sprites.add(P)    
all_sprites.add(C) 

UP_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(UP_SPEED, 10000)

while True:
    for event in pygame.event.get():
        if event.type == UP_SPEED:
            speed += 1 
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    disp.blit(background, (0,0))
    
    scores = font_small.render(f"Score: {score}", True, (0,0,0))
    disp.blit(scores, (10,10))
    coinscores = font_small.render(f"Coins: {coinscore}", True, (0,0,0))       
    disp.blit(coinscores, (scr_width - 120, 10))

    for entity in all_sprites:
        disp.blit(entity.image, entity.rect)
        if hasattr(entity, 'move'): 
            entity.move()

    # --- ЛОГИКА АВАРИИ И ЭКРАНА GAME OVER ---
    if pygame.sprite.spritecollideany(P, Enemies):
        try:
            pygame.mixer.Sound("crash.wav").play()
        except: pass
        
        # Ставим игру на паузу и запускаем цикл экрана окончания
        waiting_for_input = True
        while waiting_for_input:
            # Рисуем красный полупрозрачный фон и текст
            disp.fill((200, 50, 50)) 
            disp.blit(game_over_text, (30, 150))
            
            # Показываем финальный счет
            final_score_txt = font_small.render(f"Final Score: {score}   Coins: {coinscore}", True, (255, 255, 255))
            disp.blit(final_score_txt, (60, 230))

            # Создаем кнопки (прямоугольники)
            mouse_pos = pygame.mouse.get_pos()
            btn_restart = pygame.Rect(50, 300, 140, 50)
            btn_quit = pygame.Rect(210, 300, 140, 50)

            # Подсветка кнопок при наведении мышки
            color_restart = (100, 255, 100) if btn_restart.collidepoint(mouse_pos) else (0, 200, 0)
            color_quit = (255, 100, 100) if btn_quit.collidepoint(mouse_pos) else (200, 0, 0)

            pygame.draw.rect(disp, color_restart, btn_restart, border_radius=10)
            pygame.draw.rect(disp, color_quit, btn_quit, border_radius=10)

            text_res = font_small.render("Restart", True, (0,0,0))
            text_q = font_small.render("Quit", True, (0,0,0))

            # Центруем текст на кнопках
            disp.blit(text_res, (btn_restart.centerx - text_res.get_width()//2, btn_restart.centery - text_res.get_height()//2))
            disp.blit(text_q, (btn_quit.centerx - text_q.get_width()//2, btn_quit.centery - text_q.get_height()//2))

            pygame.display.update()

            # Обрабатываем клики на Game Over экране
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    if btn_restart.collidepoint(event.pos):
                        # СБРОС ИГРЫ: обнуляем статы и расставляем всех по местам
                        speed = 5
                        score = 0
                        coinscore = 0
                        P.rect.center = (200, 500)
                        E.respawn()
                        C.respawn()
                        waiting_for_input = False # Выходим из этого цикла, чтобы продолжить гонку!
                    elif btn_quit.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()

    # --- ПРОВЕРКА МОНЕТОК ---
    if pygame.sprite.spritecollideany(P, Coins):
        try:
            pygame.mixer.Sound("bell.wav").play()
        except: pass
        C.disappear() 

    pygame.display.update()
    FPS.tick(60)