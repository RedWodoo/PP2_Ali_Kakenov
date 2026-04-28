"""
TSIS 3 — Гонки: продвинутый геймплей, лидеры и усиления
Точка входа: машина состояний (МЕНЮ -> ИГРА -> КОНЕЦ -> ЛИДЕРЫ -> НАСТРОЙКИ).

Возможности:
  - Дорожные ловушки (масло, зоны замедления) и дорожные события (барьеры, нитро-полосы)
  - Встречные машины + препятствия с безопасным спавном
  - Нарастающая сложность
  - 3 усиления: нитро, щит, ремонт
  - Очки = монеты + дистанция; счётчик дистанции
  - Таблица лидеров и настройки через JSON
  - Полноценная система меню
"""
import pygame, sys, random, os
from pygame.locals import *
from persistence import load_settings, add_leaderboard_entry
from ui import (main_menu_screen, username_entry_screen, game_over_screen,
                leaderboard_screen, settings_screen, CAR_COLORS)

pygame.init()
pygame.mixer.init()

# ---- ЭКРАН ----
SCR_W, SCR_H = 400, 600
screen = pygame.display.set_mode((SCR_W, SCR_H))
pygame.display.set_caption("Racer — TSIS 3")
clock = pygame.time.Clock()

# ---- ЗАГРУЗКА РЕСУРСОВ ----
ASSET_DIR = "assets"

def load_img(name):
    path = os.path.join(ASSET_DIR, name)
    if os.path.exists(path):
        return pygame.image.load(path).convert_alpha()
    return None

bg_img = load_img("AnimatedStreet.png")
player_img = load_img("Player.png")
enemy_img = load_img("Enemy.png")
coin_img = load_img("Coin.png")

def try_sound(name):
    path = os.path.join(ASSET_DIR, name)
    if os.path.exists(path):
        return pygame.mixer.Sound(path)
    return None

snd_crash = try_sound("crash.wav")
snd_bell = try_sound("bell.wav")
if snd_bell:
    snd_bell.set_volume(0.4)  # громкость 40% — чтоб не было слишком громко

# ---- ШРИФТЫ ----
font_big = pygame.font.SysFont("Verdana", 40, bold=True)
font_med = pygame.font.SysFont("Verdana", 20)
font_sm = pygame.font.SysFont("Verdana", 14)

# ---- ЦВЕТА ----
WHITE = (255,255,255); BLACK = (0,0,0); RED = (200,0,0)
GOLD = (255,215,0); SILVER = (192,192,192); BRONZE = (205,127,50)
CYAN = (0,220,220); PURPLE = (180,0,255); ORANGE = (255,140,0)
DARK_GRAY = (50,50,50); YELLOW = (255,255,0)

# ---- МОДИФИКАТОРЫ СЛОЖНОСТИ ----
DIFF_SPEED = {"easy": 3, "normal": 5, "hard": 7}
DIFF_TRAFFIC = {"easy": 1, "normal": 2, "hard": 3}

# ---- ПОЛОСЫ ДОРОГИ ----
LANES = [80, 160, 240, 320]


# ==================================================================
# ИГРОВЫЕ КЛАССЫ
# ==================================================================
class Player:
    def __init__(self, color_rgb):
        self.w, self.h = 40, 60
        if player_img:
            self.image = pygame.transform.scale(player_img, (self.w, self.h))
        else:
            self.image = pygame.Surface((self.w, self.h))
            self.image.fill(color_rgb)
        self.rect = self.image.get_rect(center=(SCR_W//2, SCR_H - 80))
        self.shield = False

    def move(self, keys):
        if self.rect.left > 5 and keys[K_LEFT]: self.rect.x -= 5
        if self.rect.right < SCR_W - 5 and keys[K_RIGHT]: self.rect.x += 5
        if self.rect.top > 0 and keys[K_UP]: self.rect.y -= 5
        if self.rect.bottom < SCR_H and keys[K_DOWN]: self.rect.y += 5

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        if self.shield:
            pygame.draw.circle(surface, CYAN, self.rect.center,
                               max(self.w, self.h)//2 + 5, 2)


class TrafficCar:
    """Встречная машина — используем Enemy.png с цветным тонированием."""
    TINTS = [(255,180,180), (180,180,255), (180,255,180), (255,255,180), (255,200,160)]

    def __init__(self, speed, player_rect):
        self.w, self.h = 36, 56
        if enemy_img:
            base = pygame.transform.scale(enemy_img, (self.w, self.h))
            # накладываем случайный оттенок, чтобы отличалась от игрока
            tint = random.choice(self.TINTS)
            self.image = base.copy()
            self.image.fill(tint, special_flags=pygame.BLEND_MULT)
        else:
            self.image = pygame.Surface((self.w, self.h))
            self.image.fill(random.choice([RED, ORANGE, PURPLE, (0,100,0)]))
        self.rect = self.image.get_rect()
        self.speed = speed
        self.respawn(player_rect)

    def respawn(self, player_rect):
        for _ in range(50):
            self.rect.centerx = random.choice(LANES)
            self.rect.top = random.randint(-300, -60)
            safe = player_rect.inflate(80, 200)
            if not self.rect.colliderect(safe): return
        self.rect.top = -300

    def move(self): self.rect.y += self.speed
    def off_screen(self): return self.rect.top > SCR_H
    def draw(self, surface): surface.blit(self.image, self.rect)


class Obstacle:
    """Дорожное препятствие (барьер, яма)."""
    def __init__(self, speed, player_rect):
        self.w = random.choice([30, 50, 60])
        self.h = 15
        self.color = random.choice([DARK_GRAY, (139,69,19), (100,100,100)])
        self.rect = pygame.Rect(0, 0, self.w, self.h)
        self.speed = speed
        self.respawn(player_rect)

    def respawn(self, player_rect):
        for _ in range(50):
            self.rect.centerx = random.randint(30, SCR_W - 30)
            self.rect.top = random.randint(-400, -30)
            if not self.rect.colliderect(player_rect.inflate(80, 200)): return
        self.rect.top = -400

    def move(self): self.rect.y += self.speed
    def off_screen(self): return self.rect.top > SCR_H
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 1)


class Coin:
    """Монета со взвешенной стоимостью — использует Coin.png если есть."""
    TYPES = [
        {"color": BRONZE, "value": 1, "r": 8},
        {"color": SILVER, "value": 3, "r": 10},
        {"color": GOLD,   "value": 5, "r": 12},
    ]
    WEIGHTS = [60, 30, 10]

    def __init__(self, speed, player_rect):
        self.ctype = random.choices(self.TYPES, weights=self.WEIGHTS, k=1)[0]
        self.rect = pygame.Rect(0, 0, self.ctype["r"]*2, self.ctype["r"]*2)
        self.speed = speed
        self._build_image()
        self.respawn(player_rect)

    def _build_image(self):
        """Создаём изображение монеты из Coin.png, тонированное под тип."""
        r = self.ctype["r"]; size = r * 2
        if coin_img:
            self.image = pygame.transform.scale(coin_img, (size, size))
            tint_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            tint_surf.fill((*self.ctype["color"], 180))
            self.image.blit(tint_surf, (0, 0), special_flags=pygame.BLEND_MULT)
        else:
            self.image = None

    def respawn(self, player_rect):
        """Респавним монету в случайной полосе, подальше от игрока."""
        self.ctype = random.choices(self.TYPES, weights=self.WEIGHTS, k=1)[0]
        self.rect.size = (self.ctype["r"]*2, self.ctype["r"]*2)
        self._build_image()
        for _ in range(50):
            self.rect.centerx = random.choice(LANES)
            self.rect.top = random.randint(-200, -30)
            safe = player_rect.inflate(140, 300)
            if not self.rect.colliderect(safe): break

    def move(self): self.rect.y += self.speed
    def off_screen(self): return self.rect.top > SCR_H
    def draw(self, surface):
        if self.image: surface.blit(self.image, self.rect)
        else:
            pygame.draw.circle(surface, self.ctype["color"], self.rect.center, self.ctype["r"])
            pygame.draw.circle(surface, BLACK, self.rect.center, self.ctype["r"], 2)


class PowerUp:
    """Подбираемое усиление: нитро, щит, ремонт."""
    KINDS = ["nitro", "shield", "repair"]
    COLORS = {"nitro": ORANGE, "shield": CYAN, "repair": (0,200,0)}
    LABELS = {"nitro": "N", "shield": "S", "repair": "R"}

    def __init__(self, speed, player_rect):
        self.kind = random.choice(self.KINDS)
        self.rect = pygame.Rect(0, 0, 24, 24)
        self.speed = speed
        self.spawn_time = pygame.time.get_ticks()
        self.timeout = 8000  # исчезает через 8 сек
        self.respawn(player_rect)

    def respawn(self, player_rect):
        self.kind = random.choice(self.KINDS)
        self.rect.centerx = random.choice(LANES)
        self.rect.top = random.randint(-300, -50)
        self.spawn_time = pygame.time.get_ticks()

    def move(self): self.rect.y += self.speed
    def off_screen(self): return self.rect.top > SCR_H
    def expired(self): return pygame.time.get_ticks() - self.spawn_time > self.timeout
    def draw(self, surface):
        color = self.COLORS.get(self.kind, WHITE)
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        label = font_sm.render(self.LABELS[self.kind], True, BLACK)
        surface.blit(label, (self.rect.centerx - label.get_width()//2,
                             self.rect.centery - label.get_height()//2))


class HazardZone:
    """Дорожная ловушка: масло, зона замедления или нитро-полоса."""
    def __init__(self, speed):
        self.w = random.randint(50, 80)
        self.h = random.randint(20, 40)
        self.rect = pygame.Rect(random.choice(LANES) - self.w//2, random.randint(-500, -50),
                                self.w, self.h)
        self.speed = speed
        self.kind = random.choice(["oil", "slowdown", "nitro_strip"])

    def move(self): self.rect.y += self.speed
    def off_screen(self): return self.rect.top > SCR_H
    def draw(self, surface):
        if self.kind == "oil":
            pygame.draw.ellipse(surface, (30, 30, 30), self.rect)
            lbl = font_sm.render("OIL", True, YELLOW)
        elif self.kind == "slowdown":
            pygame.draw.rect(surface, (100, 60, 0), self.rect)
            lbl = font_sm.render("SLOW", True, WHITE)
        else:
            pygame.draw.rect(surface, ORANGE, self.rect)
            lbl = font_sm.render("NITRO", True, BLACK)
        surface.blit(lbl, (self.rect.centerx - lbl.get_width()//2,
                           self.rect.centery - lbl.get_height()//2))


# ==================================================================
# ИГРОВОЙ ЦИКЛ
# ==================================================================
def run_game(player_name, settings):
    """Запускаем одну сессию. Возвращает (score, distance, coins)."""
    diff = settings.get("difficulty", "normal")
    sound_on = settings.get("sound", True)
    car_color_name = settings.get("car_color", "blue")
    car_color = CAR_COLORS.get(car_color_name, (0, 100, 255))

    base_speed = DIFF_SPEED.get(diff, 5)
    speed = base_speed
    max_traffic = DIFF_TRAFFIC.get(diff, 2)

    player = Player(car_color)
    bg_y = 0

    traffic = [TrafficCar(speed, player.rect) for _ in range(max_traffic)]
    obstacles = [Obstacle(speed, player.rect)]
    coins = [Coin(speed, player.rect) for _ in range(2)]
    hazards = [HazardZone(speed)]
    powerup = PowerUp(speed, player.rect)
    powerup_on_field = True

    score = 0; coin_count = 0; distance = 0
    active_powerup = None  # (вид, время_истечения)

    SPEED_TICK = pygame.USEREVENT + 1
    pygame.time.set_timer(SPEED_TICK, 8000)

    running = True
    while running:
        dt = clock.tick(60)
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == QUIT: pygame.quit(); sys.exit()
            if event.type == SPEED_TICK:
                speed += 1
                # масштабирование сложности: больше трафика и препятствий
                if len(traffic) < max_traffic + speed // 4:
                    traffic.append(TrafficCar(speed, player.rect))
                if random.random() < 0.5:
                    obstacles.append(Obstacle(speed, player.rect))
                if random.random() < 0.3:
                    hazards.append(HazardZone(speed))

        keys = pygame.key.get_pressed()

        # применяем эффекты активного усиления
        actual_speed = speed
        if active_powerup:
            kind, expire = active_powerup
            if now > expire:
                if kind == "shield": player.shield = False
                active_powerup = None
            elif kind == "nitro": actual_speed = speed + 4

        player.move(keys)
        distance += actual_speed

        # прокрутка фона
        bg_y += actual_speed
        if bg_y >= SCR_H: bg_y = 0

        # движение объектов
        for t in traffic:
            t.speed = actual_speed; t.move()
            if t.off_screen(): score += 1; t.respawn(player.rect)
        for o in obstacles:
            o.speed = actual_speed; o.move()
            if o.off_screen(): o.respawn(player.rect)
        for c in coins:
            c.speed = actual_speed; c.move()
            if c.off_screen(): c.respawn(player.rect)
        for h in hazards:
            h.speed = actual_speed; h.move()
            if h.off_screen(): hazards.remove(h)
        if powerup_on_field:
            powerup.speed = actual_speed; powerup.move()
            if powerup.off_screen() or powerup.expired(): powerup.respawn(player.rect)

        # ---- СТОЛКНОВЕНИЯ ----
        # с встречной машиной
        for t in traffic:
            if player.rect.colliderect(t.rect):
                if player.shield:
                    player.shield = False; active_powerup = None; t.respawn(player.rect)
                else:
                    if sound_on and snd_crash: snd_crash.play()
                    running = False
        # с препятствием
        for o in obstacles:
            if player.rect.colliderect(o.rect):
                if player.shield:
                    player.shield = False; active_powerup = None; obstacles.remove(o)
                else:
                    if sound_on and snd_crash: snd_crash.play()
                    running = False
        # эффекты ловушек
        for h in hazards:
            if player.rect.colliderect(h.rect):
                if h.kind == "oil": player.rect.x += random.choice([-3, 3])
                elif h.kind == "slowdown": actual_speed = max(2, speed - 3)
                elif h.kind == "nitro_strip": actual_speed = speed + 3
        # подбор монет (увеличенный хитбокс для удобства)
        for c in coins:
            hitbox = c.rect.inflate(8, 8)
            if player.rect.colliderect(hitbox):
                if sound_on and snd_bell: snd_bell.play()
                score += c.ctype["value"]; coin_count += c.ctype["value"]
                c.respawn(player.rect)
        # подбор усиления
        if powerup_on_field and player.rect.colliderect(powerup.rect):
            if active_powerup is None:
                kind = powerup.kind
                if kind == "nitro": active_powerup = ("nitro", now + 4000)
                elif kind == "shield":
                    player.shield = True; active_powerup = ("shield", now + 999999)
                elif kind == "repair":
                    if obstacles: obstacles.pop()
                    active_powerup = None
                powerup.respawn(player.rect)

        # ---- ОТРИСОВКА ----
        if bg_img:
            screen.blit(bg_img, (0, bg_y)); screen.blit(bg_img, (0, bg_y - SCR_H))
        else: screen.fill((80, 80, 80))

        for h in hazards: h.draw(screen)
        for o in obstacles: o.draw(screen)
        for c in coins: c.draw(screen)
        for t in traffic: t.draw(screen)
        if powerup_on_field: powerup.draw(screen)
        player.draw(screen)

        # верхняя панель
        screen.blit(font_med.render(f"Score: {score}", True, WHITE), (5, 5))
        screen.blit(font_med.render(f"Dist: {distance//100}m", True, WHITE), (5, 30))
        screen.blit(font_med.render(f"Coins: {coin_count}", True, GOLD), (SCR_W-140, 5))
        screen.blit(font_sm.render(f"Speed: {actual_speed}", True, WHITE), (SCR_W-100, 30))
        screen.blit(font_sm.render(f"Player: {player_name}", True, WHITE), (5, 55))

        if active_powerup:
            kind, expire = active_powerup
            rem = max(0, (expire - now) // 1000)
            pu_txt = f"[{kind.upper()}] {rem}s" if kind != "shield" else "[SHIELD]"
            screen.blit(font_med.render(pu_txt, True, CYAN), (SCR_W//2-50, 5))

        pygame.display.update()

    return score, distance // 100, coin_count


# ==================================================================
# МАШИНА СОСТОЯНИЙ
# ==================================================================
def main():
    settings = load_settings()
    player_name = ""

    while True:
        action = main_menu_screen(screen, clock, SCR_W, SCR_H)
        if action == "quit": break
        elif action == "leaderboard": leaderboard_screen(screen, clock, SCR_W, SCR_H)
        elif action == "settings":
            settings_screen(screen, clock, SCR_W, SCR_H)
            settings = load_settings()
        elif action == "play":
            if not player_name:
                player_name = username_entry_screen(screen, clock, SCR_W, SCR_H)
                if not player_name: continue
            while True:
                score, distance, coins = run_game(player_name, settings)
                add_leaderboard_entry(player_name, score, distance)
                result = game_over_screen(screen, clock, SCR_W, SCR_H, score, distance, coins)
                if result == "retry": continue
                else: break

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
