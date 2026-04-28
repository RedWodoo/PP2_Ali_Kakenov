"""
Practice 11 — Гоночная игра (Racer)
Расширение Practice 10:
  1. Случайная генерация монет с разным весом на дороге
  2. Увеличение скорости врага при наборе N монет
  3. Весь код прокомментирован
"""
import pygame, sys, random, time
from pygame.locals import *

pygame.init()  # запускаем движок pygame

# --------------- ШРИФТЫ ---------------
font = pygame.font.SysFont("Verdana", 60)          # крупный шрифт для Game Over
font_small = pygame.font.SysFont("Verdana", 20)    # мелкий шрифт для интерфейса
game_over_text = font.render("Game Over", True, (0, 0, 0))

# --------------- НАСТРОЙКИ ЭКРАНА ---------------
scr_width = 400
scr_height = 600
speed = 5          # начальная скорость врагов и монет
score = 0          # очки за обгон
coinscore = 0      # суммарная стоимость собранных монет

# Через сколько очков за монеты враг ускоряется
COINS_PER_SPEEDUP = 5  
last_speedup_at = 0     # порог, при котором последний раз увеличили скорость

disp = pygame.display.set_mode((scr_width, scr_height))
pygame.display.set_caption("Racer — Practice 11 (Weighted Coins & Speed Scaling)")
FPS = pygame.time.Clock()

# загружаем фоновую картинку дороги
background = pygame.image.load("AnimatedStreet.png")

# --------------- ТИПЫ МОНЕТ ---------------
# у каждой монеты свой цвет и стоимость (вес)
COIN_TYPES = [
    {"color": (205, 127, 50),  "value": 1, "radius": 8,  "label": "B"},   # бронза — часто, мало очков
    {"color": (192, 192, 192), "value": 3, "radius": 10, "label": "S"},   # серебро — реже
    {"color": (255, 215, 0),   "value": 5, "radius": 12, "label": "G"},   # золото — редко, много очков
]

# вероятности выпадения (бронза чаще всего)
COIN_WEIGHTS = [60, 30, 10]


# =================== КЛАССЫ ===================

class Enemy(pygame.sprite.Sprite):
    """Вражеская машина, движется вниз. Если проехала — игроку +1 очко."""
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Enemy.png")
        self.rect = self.image.get_rect()
        self.respawn()

    def move(self):
        """Двигаем врага вниз; если ушёл за экран — респавним наверху."""
        global score
        self.rect.move_ip(0, speed)
        if self.rect.bottom > scr_height:
            score += 1       # игрок объехал этого врага
            self.respawn()

    def respawn(self):
        """Ставим врага наверху в случайной позиции,
        чтобы он не появлялся прямо на игроке."""
        while True:
            self.rect.top = 0
            self.rect.centerx = random.randint(30, scr_width - 30)
            try:
                # создаём зону безопасности вокруг игрока
                safe_zone = P.rect.inflate(100, 250)
                if not self.rect.colliderect(safe_zone):
                    break
            except NameError:
                # игрок ещё не создан (первый запуск)
                break


class Coin(pygame.sprite.Sprite):
    """Монетка, которая летит вниз.
    Случайный тип (бронза, серебро, золото) с разной стоимостью."""
    def __init__(self):
        super().__init__()
        self.assign_type()           # выбираем тип случайно
        self.rect = pygame.Rect(0, 0, self.coin_type["radius"] * 2, self.coin_type["radius"] * 2)
        self.respawn()

    def assign_type(self):
        """Случайно выбираем тип монеты с учётом вероятностей."""
        self.coin_type = random.choices(COIN_TYPES, weights=COIN_WEIGHTS, k=1)[0]

    def draw(self, surface):
        """Рисуем монету кружком с буквой типа по центру."""
        center = self.rect.center
        radius = self.coin_type["radius"]
        color = self.coin_type["color"]

        # рисуем сам кружок
        pygame.draw.circle(surface, color, center, radius)
        # обводка
        pygame.draw.circle(surface, (0, 0, 0), center, radius, 2)

        # буква типа (B, S, G) по центру монеты
        label_font = pygame.font.SysFont("Verdana", 12)
        label = label_font.render(self.coin_type["label"], True, (0, 0, 0))
        surface.blit(label, (center[0] - label.get_width() // 2,
                             center[1] - label.get_height() // 2))

    def move(self):
        """Двигаем монету вниз с текущей скоростью."""
        self.rect.move_ip(0, speed)
        if self.rect.bottom > scr_height:
            self.respawn()  # улетела вниз — респавним

    def collect(self):
        """Игрок подобрал монету — возвращаем стоимость и респавним с новым типом."""
        value = self.coin_type["value"]
        self.assign_type()   # следующий раз другой тип
        self.rect.width = self.coin_type["radius"] * 2
        self.rect.height = self.coin_type["radius"] * 2
        self.respawn()
        return value

    def respawn(self):
        """Ставим монету выше экрана в случайную позицию,
        подальше от врага (большая зона безопасности)."""
        while True:
            self.rect.top = random.randint(-100, -30)
            self.rect.centerx = random.randint(40, scr_width - 40)
            try:
                # широкая зона вокруг врага, чтобы монета не спавнилась рядом
                safe_zone = E.rect.inflate(140, 300)
                if not self.rect.colliderect(safe_zone):
                    break
            except NameError:
                break


class Player(pygame.sprite.Sprite):
    """Машина игрока, управляется стрелками."""
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Player.png")
        self.rect = self.image.get_rect()
        self.rect.center = (200, 500)  # стартовая позиция

    def move(self):
        """Двигаем машину стрелками, не выходя за границы экрана."""
        pressed_keys = pygame.key.get_pressed()
        if self.rect.left > 0 and pressed_keys[K_LEFT]:
            self.rect.move_ip(-5, 0)
        if self.rect.right < scr_width and pressed_keys[K_RIGHT]:
            self.rect.move_ip(5, 0)
        if self.rect.top > 0 and pressed_keys[K_UP]:
            self.rect.move_ip(0, -5)
        if self.rect.bottom < scr_height and pressed_keys[K_DOWN]:
            self.rect.move_ip(0, 5)


# =================== ИНИЦИАЛИЗАЦИЯ ===================
E = Enemy()     # один враг
C = Coin()      # одна монета
P = Player()    # игрок

Enemies = pygame.sprite.Group()
Enemies.add(E)
Coins = pygame.sprite.Group()
Coins.add(C)
all_sprites = pygame.sprite.Group()
all_sprites.add(E, P, C)

# каждые 10 секунд скорость растёт (базовая механика из Practice 10)
UP_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(UP_SPEED, 10000)


# =================== ГЛАВНЫЙ ЦИКЛ ===================
while True:
    for event in pygame.event.get():
        if event.type == UP_SPEED:
            speed += 1  # базовое ускорение по таймеру
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # --- рисуем фон ---
    disp.blit(background, (0, 0))

    # --- интерфейс: очки, монеты, скорость ---
    scores_txt = font_small.render(f"Score: {score}", True, (0, 0, 0))
    disp.blit(scores_txt, (10, 10))
    coins_txt = font_small.render(f"Coins: {coinscore}", True, (0, 0, 0))
    disp.blit(coins_txt, (scr_width - 130, 10))
    speed_txt = font_small.render(f"Speed: {speed}", True, (0, 0, 0))
    disp.blit(speed_txt, (10, 35))

    # --- двигаем и рисуем спрайты ---
    E.move()
    C.move()
    P.move()

    # рисуем врага и игрока через их картинки
    disp.blit(E.image, E.rect)
    disp.blit(P.image, P.rect)
    # монету рисуем отдельно (цветной кружок)
    C.draw(disp)

    # --- столкновение с врагом → конец игры ---
    if pygame.sprite.spritecollideany(P, Enemies):
        try:
            pygame.mixer.Sound("crash.wav").play()
        except:
            pass

        # экран Game Over с кнопками
        waiting_for_input = True
        while waiting_for_input:
            disp.fill((200, 50, 50))
            disp.blit(game_over_text, (30, 150))

            final_txt = font_small.render(
                f"Final Score: {score}   Coins: {coinscore}", True, (255, 255, 255))
            disp.blit(final_txt, (60, 230))

            mouse_pos = pygame.mouse.get_pos()
            btn_restart = pygame.Rect(50, 300, 140, 50)
            btn_quit = pygame.Rect(210, 300, 140, 50)

            # подсветка кнопок при наведении
            color_restart = (100, 255, 100) if btn_restart.collidepoint(mouse_pos) else (0, 200, 0)
            color_quit = (255, 100, 100) if btn_quit.collidepoint(mouse_pos) else (200, 0, 0)

            pygame.draw.rect(disp, color_restart, btn_restart, border_radius=10)
            pygame.draw.rect(disp, color_quit, btn_quit, border_radius=10)

            text_res = font_small.render("Restart", True, (0, 0, 0))
            text_q = font_small.render("Quit", True, (0, 0, 0))
            disp.blit(text_res, (btn_restart.centerx - text_res.get_width() // 2,
                                  btn_restart.centery - text_res.get_height() // 2))
            disp.blit(text_q, (btn_quit.centerx - text_q.get_width() // 2,
                                btn_quit.centery - text_q.get_height() // 2))

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    if btn_restart.collidepoint(event.pos):
                        # сбрасываем всё для новой игры
                        speed = 5
                        score = 0
                        coinscore = 0
                        last_speedup_at = 0
                        P.rect.center = (200, 500)
                        E.respawn()
                        C.assign_type()
                        C.respawn()
                        waiting_for_input = False
                    elif btn_quit.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()

    # --- подбор монеты (увеличенный хитбокс для удобства) ---
    coin_hitbox = C.rect.inflate(12, 12)  # чуть больше визуального кружка
    if P.rect.colliderect(coin_hitbox):
        try:
            coin_snd = pygame.mixer.Sound("bell.wav")
            coin_snd.set_volume(0.4)  # громкость 40% — тише чтоб не раздражало
            coin_snd.play()
        except:
            pass
        value = C.collect()    # забираем стоимость и респавним монету
        coinscore += value

        # ускоряем врага каждые COINS_PER_SPEEDUP монет
        if coinscore // COINS_PER_SPEEDUP > last_speedup_at // COINS_PER_SPEEDUP:
            speed += 1
            last_speedup_at = coinscore

    pygame.display.update()
    FPS.tick(60)
