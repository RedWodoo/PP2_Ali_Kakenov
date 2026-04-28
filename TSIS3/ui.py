"""
TSIS 3 — ui.py
Экраны игры: главное меню, конец игры, лидеры, настройки.
Всё рисуется через Pygame (без внешних библиотек для UI).
"""
import pygame
from persistence import load_leaderboard, load_settings, save_settings

# цвета
WHITE = (255,255,255); BLACK = (0,0,0); GRAY = (120,120,120)
DARK = (40,40,40); GREEN = (0,200,0); RED = (200,0,0)
BLUE = (0,100,255); GOLD = (255,215,0)

CAR_COLORS = {
    "blue": (0,100,255), "red": (220,50,50), "green": (50,200,50),
    "yellow": (255,220,0), "white": (240,240,240),
}
DIFFICULTIES = ["easy", "normal", "hard"]


def draw_button(surface, text, rect, font, mouse_pos, base_color=GRAY, hover_color=None):
    """Рисуем кнопку с эффектом наведения."""
    if hover_color is None:
        hover_color = tuple(min(c + 40, 255) for c in base_color)
    color = hover_color if rect.collidepoint(mouse_pos) else base_color
    pygame.draw.rect(surface, color, rect, border_radius=8)
    pygame.draw.rect(surface, WHITE, rect, 2, border_radius=8)
    txt = font.render(text, True, WHITE)
    surface.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))
    return rect


def main_menu_screen(surface, clock, scr_w, scr_h):
    """Главное меню. Возвращает: 'play', 'leaderboard', 'settings' или 'quit'."""
    font_big = pygame.font.SysFont("Verdana", 48, bold=True)
    font = pygame.font.SysFont("Verdana", 22)
    buttons = {
        "play":        pygame.Rect(scr_w//2-100, 200, 200, 50),
        "leaderboard": pygame.Rect(scr_w//2-100, 270, 200, 50),
        "settings":    pygame.Rect(scr_w//2-100, 340, 200, 50),
        "quit":        pygame.Rect(scr_w//2-100, 410, 200, 50),
    }
    while True:
        mp = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for key, rect in buttons.items():
                    if rect.collidepoint(event.pos): return key
        surface.fill(DARK)
        title = font_big.render("RACER", True, GOLD)
        surface.blit(title, (scr_w//2 - title.get_width()//2, 80))
        sub = font.render("TSIS 3 — Advanced", True, GRAY)
        surface.blit(sub, (scr_w//2 - sub.get_width()//2, 140))
        draw_button(surface, "Play", buttons["play"], font, mp, GREEN)
        draw_button(surface, "Leaderboard", buttons["leaderboard"], font, mp, BLUE)
        draw_button(surface, "Settings", buttons["settings"], font, mp, GRAY)
        draw_button(surface, "Quit", buttons["quit"], font, mp, RED)
        pygame.display.update()
        clock.tick(30)


def username_entry_screen(surface, clock, scr_w, scr_h):
    """Экран ввода имени. Возвращает введённое имя."""
    font_big = pygame.font.SysFont("Verdana", 30)
    font = pygame.font.SysFont("Verdana", 24)
    name = ""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return ""
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip(): return name.strip()
                elif event.key == pygame.K_BACKSPACE: name = name[:-1]
                elif event.unicode.isprintable() and len(name) < 15: name += event.unicode
        surface.fill(DARK)
        prompt = font_big.render("Enter Your Name", True, WHITE)
        surface.blit(prompt, (scr_w//2 - prompt.get_width()//2, 150))
        # поле ввода
        box = pygame.Rect(scr_w//2-120, 230, 240, 40)
        pygame.draw.rect(surface, WHITE, box, 2, border_radius=4)
        surface.blit(font.render(name + "|", True, GOLD), (box.x+10, box.y+6))
        hint = pygame.font.SysFont("Verdana", 16).render("Press ENTER to start", True, GRAY)
        surface.blit(hint, (scr_w//2 - hint.get_width()//2, 290))
        pygame.display.update()
        clock.tick(30)


def game_over_screen(surface, clock, scr_w, scr_h, score, distance, coins):
    """Экран конца игры. Возвращает 'retry' или 'menu'."""
    font_big = pygame.font.SysFont("Verdana", 42, bold=True)
    font = pygame.font.SysFont("Verdana", 20)
    btn_retry = pygame.Rect(scr_w//2-110, 350, 100, 45)
    btn_menu = pygame.Rect(scr_w//2+10, 350, 100, 45)
    while True:
        mp = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "menu"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_retry.collidepoint(event.pos): return "retry"
                if btn_menu.collidepoint(event.pos): return "menu"
        surface.fill((150, 30, 30))
        title = font_big.render("GAME OVER", True, WHITE)
        surface.blit(title, (scr_w//2 - title.get_width()//2, 80))
        y = 180
        for s in [f"Score: {score}", f"Distance: {distance}m", f"Coins: {coins}"]:
            txt = font.render(s, True, (230,230,230))
            surface.blit(txt, (scr_w//2 - txt.get_width()//2, y)); y += 35
        draw_button(surface, "Retry", btn_retry, font, mp, GREEN)
        draw_button(surface, "Menu", btn_menu, font, mp, GRAY)
        pygame.display.update()
        clock.tick(30)


def leaderboard_screen(surface, clock, scr_w, scr_h):
    """Таблица лидеров — топ 10. Возвращает при нажатии Back."""
    font_big = pygame.font.SysFont("Verdana", 32, bold=True)
    font = pygame.font.SysFont("Verdana", 18)
    entries = load_leaderboard()
    btn_back = pygame.Rect(scr_w//2-60, scr_h-70, 120, 40)
    while True:
        mp = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_back.collidepoint(event.pos): return
        surface.fill(DARK)
        title = font_big.render("LEADERBOARD", True, GOLD)
        surface.blit(title, (scr_w//2 - title.get_width()//2, 20))
        # заголовок таблицы
        header = font.render(f"{'#':<4}{'Name':<12}{'Score':<8}{'Dist':<8}", True, WHITE)
        surface.blit(header, (scr_w//2-130, 75))
        pygame.draw.line(surface, GRAY, (scr_w//2-130, 100), (scr_w//2+130, 100))
        y = 110
        for i, e in enumerate(entries[:10]):
            c = GOLD if i==0 else (192,192,192) if i==1 else (205,127,50) if i==2 else WHITE
            row = font.render(
                f"{i+1:<4}{e.get('name','?'):<12}{e.get('score',0):<8}{e.get('distance',0):<8}",
                True, c)
            surface.blit(row, (scr_w//2-130, y)); y += 28
        if not entries:
            empty = font.render("No scores yet!", True, GRAY)
            surface.blit(empty, (scr_w//2 - empty.get_width()//2, 150))
        draw_button(surface, "Back", btn_back, font, mp, GRAY)
        pygame.display.update()
        clock.tick(30)


def settings_screen(surface, clock, scr_w, scr_h):
    """Настройки: звук, цвет машины, сложность."""
    font_big = pygame.font.SysFont("Verdana", 30, bold=True)
    font = pygame.font.SysFont("Verdana", 18)
    settings = load_settings()
    color_keys = list(CAR_COLORS.keys())
    color_idx = color_keys.index(settings.get("car_color", "blue")) if settings.get("car_color") in color_keys else 0
    diff_idx = DIFFICULTIES.index(settings.get("difficulty", "normal")) if settings.get("difficulty") in DIFFICULTIES else 1
    sound_on = settings.get("sound", True)

    btn_sound = pygame.Rect(scr_w//2-80, 130, 160, 40)
    btn_color_l = pygame.Rect(scr_w//2-110, 200, 40, 40)
    btn_color_r = pygame.Rect(scr_w//2+70, 200, 40, 40)
    btn_diff_l = pygame.Rect(scr_w//2-110, 270, 40, 40)
    btn_diff_r = pygame.Rect(scr_w//2+70, 270, 40, 40)
    btn_save = pygame.Rect(scr_w//2-60, scr_h-70, 120, 40)

    while True:
        mp = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_sound.collidepoint(event.pos): sound_on = not sound_on
                elif btn_color_l.collidepoint(event.pos): color_idx = (color_idx-1) % len(color_keys)
                elif btn_color_r.collidepoint(event.pos): color_idx = (color_idx+1) % len(color_keys)
                elif btn_diff_l.collidepoint(event.pos): diff_idx = (diff_idx-1) % len(DIFFICULTIES)
                elif btn_diff_r.collidepoint(event.pos): diff_idx = (diff_idx+1) % len(DIFFICULTIES)
                elif btn_save.collidepoint(event.pos):
                    settings["sound"] = sound_on
                    settings["car_color"] = color_keys[color_idx]
                    settings["difficulty"] = DIFFICULTIES[diff_idx]
                    save_settings(settings); return

        surface.fill(DARK)
        surface.blit(font_big.render("SETTINGS", True, WHITE), (scr_w//2-100, 40))
        # переключатель звука
        snd_color = GREEN if sound_on else RED
        draw_button(surface, f"Sound: {'ON' if sound_on else 'OFF'}", btn_sound, font, mp, snd_color)
        # выбор цвета машины
        draw_button(surface, "<", btn_color_l, font, mp)
        draw_button(surface, ">", btn_color_r, font, mp)
        cl = font.render(f"Car: {color_keys[color_idx].upper()}", True, WHITE)
        surface.blit(cl, (scr_w//2 - cl.get_width()//2, 210))
        pygame.draw.rect(surface, CAR_COLORS[color_keys[color_idx]], (scr_w//2-15, 245, 30, 20))
        # выбор сложности
        draw_button(surface, "<", btn_diff_l, font, mp)
        draw_button(surface, ">", btn_diff_r, font, mp)
        dl = font.render(f"Difficulty: {DIFFICULTIES[diff_idx].upper()}", True, WHITE)
        surface.blit(dl, (scr_w//2 - dl.get_width()//2, 280))
        draw_button(surface, "Save", btn_save, font, mp, GREEN)
        pygame.display.update()
        clock.tick(30)
