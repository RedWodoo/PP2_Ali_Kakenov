"""
TSIS 2 — Расширенная рисовалка (Paint)
Расширение Practice 10-11:
  1. Карандаш — непрерывное рисование
  2. Прямая линия с предпросмотром
  3. Три размера кисти (маленький/средний/большой)
  4. Заливка (flood fill)
  5. Ctrl+S сохраняет холст в PNG
  6. Инструмент текста: кликнуть, набрать, Enter для подтверждения
  7. GUI-панель с кнопками для всех инструментов и цветов
  8. Предпросмотр фигур при перетаскивании
"""
import pygame, sys, math
from datetime import datetime
from collections import deque
from pygame.locals import *

pygame.init()

WIDTH, HEIGHT = 900, 700
TOOLBAR_H = 80   # высота панели инструментов
CANVAS_Y = TOOLBAR_H

WHITE=(255,255,255); BLACK=(0,0,0); GREEN=(0,255,0); RED=(255,0,0)
BLUE=(0,0,255); YELLOW=(255,255,0); ORANGE=(255,140,0); PURPLE=(160,0,200)
GRAY=(180,180,180); DARK=(50,50,50); LGRAY=(220,220,220)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint — TSIS 2 (Full Drawing Suite)")
clock = pygame.time.Clock()

# отдельная поверхность-холст для сохранения нарисованного
canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_H))
canvas.fill(WHITE)

# ---- СОСТОЯНИЕ ----
current_tool = "pencil"
current_color = BLACK
brush_sizes = [2, 5, 10]  # маленький, средний, большой
brush_idx = 0
eraser_size = 20

start_pos = None   # начало фигуры (координаты холста)
prev_pos = None    # предыдущая точка для карандаша

# состояние текстового инструмента
text_mode = False
text_pos = None     # где вводим текст (координаты холста)
text_buffer = ""
text_font = pygame.font.SysFont("Arial", 24)

# ---- СПИСОК ИНСТРУМЕНТОВ ----
TOOLS = [
    ("pencil",    "Pencil"),  ("line",      "Line"),     ("rect",      "Rect"),
    ("circle",    "Circle"),  ("square",    "Square"),   ("right_tri", "RightTri"),
    ("eq_tri",    "EqTri"),   ("rhombus",   "Rhombus"),  ("eraser",    "Eraser"),
    ("fill",      "Fill"),    ("text",      "Text"),
]
SHAPE_TOOLS = {"line", "rect", "circle", "square", "right_tri", "eq_tri", "rhombus"}
PALETTE = [BLACK, RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, WHITE]


# ============================================================
# ЗАЛИВКА (BFS)
# ============================================================
def flood_fill(surface, start_x, start_y, fill_color):
    """Заливаем связную область одного цвета через BFS."""
    target_color = surface.get_at((start_x, start_y))
    if target_color == fill_color: return
    w, h = surface.get_size()
    queue = deque([(start_x, start_y)])
    visited = {(start_x, start_y)}
    while queue:
        x, y = queue.popleft()
        if surface.get_at((x, y)) != target_color: continue
        surface.set_at((x, y), fill_color)
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited:
                visited.add((nx, ny)); queue.append((nx, ny))


# ============================================================
# ПОСТРОЕНИЕ ФИГУР
# ============================================================
def build_shape(tool, x1, y1, x2, y2):
    """Формируем данные фигуры для предпросмотра или финального рисования."""
    if tool == "line": return ("line", (x1,y1), (x2,y2))
    elif tool == "rect":
        return ("rect", pygame.Rect(min(x1,x2), min(y1,y2), abs(x2-x1), abs(y2-y1)))
    elif tool == "circle":
        return ("circle", (x1,y1), int(math.hypot(x2-x1, y2-y1)))
    elif tool == "square":
        side = max(abs(x2-x1), abs(y2-y1))
        sx, sy = (1 if x2>=x1 else -1), (1 if y2>=y1 else -1)
        return ("rect", pygame.Rect(x1 if sx>0 else x1-side, y1 if sy>0 else y1-side, side, side))
    elif tool == "right_tri":
        return ("polygon", [(x1,y1),(x2,y1),(x1,y2)])
    elif tool == "eq_tri":
        side = abs(x2-x1); h = int(side*math.sqrt(3)/2)
        sy = -1 if y2<y1 else 1; mid = (x1+x2)//2
        return ("polygon", [(x1,y1),(x2,y1),(mid,y1+sy*h)])
    elif tool == "rhombus":
        cx,cy = (x1+x2)//2,(y1+y2)//2; dx,dy = abs(x2-x1)//2,abs(y2-y1)//2
        return ("polygon", [(cx,cy-dy),(cx+dx,cy),(cx,cy+dy),(cx-dx,cy)])
    return None

def draw_shape(surface, info, color, width=2):
    """Рисуем фигуру на поверхности."""
    if not info: return
    k = info[0]
    if k == "line": pygame.draw.line(surface, color, info[1], info[2], width)
    elif k == "rect": pygame.draw.rect(surface, color, info[1], width)
    elif k == "circle": pygame.draw.circle(surface, color, info[1], info[2], width)
    elif k == "polygon" and len(info[1])>=3: pygame.draw.polygon(surface, color, info[1], width)

def draw_shape_preview(surface, info, color, oy, width=2):
    """Рисуем предпросмотр фигуры на экране (сдвиг на высоту панели)."""
    if not info: return
    k = info[0]
    if k == "line":
        pygame.draw.line(surface, color, (info[1][0],info[1][1]+oy), (info[2][0],info[2][1]+oy), width)
    elif k == "rect":
        r = info[1].copy(); r.y += oy; pygame.draw.rect(surface, color, r, width)
    elif k == "circle":
        pygame.draw.circle(surface, color, (info[1][0],info[1][1]+oy), info[2], width)
    elif k == "polygon":
        pts = [(p[0],p[1]+oy) for p in info[1]]
        if len(pts)>=3: pygame.draw.polygon(surface, color, pts, width)


# ============================================================
# ПАНЕЛЬ ИНСТРУМЕНТОВ
# ============================================================
def draw_toolbar():
    """Рисуем GUI панель: кнопки инструментов, палитра, размеры кисти."""
    pygame.draw.rect(screen, DARK, (0, 0, WIDTH, TOOLBAR_H))
    font = pygame.font.SysFont("Verdana", 12)
    mp = pygame.mouse.get_pos()
    # кнопки инструментов (ряд 1)
    tr = {}; x = 8
    for tid, lbl in TOOLS:
        bw = max(50, 10+font.size(lbl)[0]); r = pygame.Rect(x, 6, bw, 24); tr[tid] = r
        bg = (0,160,0) if tid==current_tool else (100,100,100) if r.collidepoint(mp) else (70,70,70)
        pygame.draw.rect(screen, bg, r, border_radius=5)
        pygame.draw.rect(screen, LGRAY, r, 1, border_radius=5)
        t = font.render(lbl, True, WHITE)
        screen.blit(t, (r.x+(r.w-t.get_width())//2, r.y+(r.h-t.get_height())//2))
        x += bw + 4
    # палитра цветов (ряд 2)
    cr = {}; x = 8
    for i, col in enumerate(PALETTE):
        r = pygame.Rect(x, 36, 24, 24); cr[i] = r
        pygame.draw.rect(screen, col, r)
        pygame.draw.rect(screen, (0,255,0) if col==current_color else GRAY, r, 3 if col==current_color else 1)
        x += 28
    # превью цвета
    px = x + 10
    pygame.draw.rect(screen, current_color, (px, 36, 30, 24))
    pygame.draw.rect(screen, WHITE, (px, 36, 30, 24), 2)
    # кнопки размера кисти
    br = {}; bx = px + 50
    for i, sz in enumerate(brush_sizes):
        r = pygame.Rect(bx, 36, 40, 24); br[i] = r
        bg = (100,200,100) if i==brush_idx else (100,100,100) if r.collidepoint(mp) else (70,70,70)
        pygame.draw.rect(screen, bg, r, border_radius=4)
        pygame.draw.rect(screen, LGRAY, r, 1, border_radius=4)
        t = font.render(f"{sz}px", True, WHITE)
        screen.blit(t, (r.x+(r.w-t.get_width())//2, r.y+(r.h-t.get_height())//2))
        bx += 46
    # подсказка
    hf = pygame.font.SysFont("Verdana", 10)
    screen.blit(hf.render("Ctrl+S = Save | Brush: +/- | Keys work too", True, (140,140,140)), (8, 65))
    return tr, cr, br

def handle_toolbar_click(pos, tr, cr, br):
    """Обработка клика по панели инструментов."""
    global current_tool, current_color, brush_idx
    if pos[1] > TOOLBAR_H: return False
    for tid, r in tr.items():
        if r.collidepoint(pos): current_tool = tid; return True
    for i, r in cr.items():
        if r.collidepoint(pos): current_color = PALETTE[i]; return True
    for i, r in br.items():
        if r.collidepoint(pos): brush_idx = i; return True
    return True


# ============================================================
# ГЛАВНЫЙ ЦИКЛ
# ============================================================
tool_rects = {}; color_rects = {}; brush_rects = {}

running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT: running = False
        # режим ввода текста
        if text_mode:
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    if text_buffer and text_pos:
                        canvas.blit(text_font.render(text_buffer, True, current_color), text_pos)
                    text_mode = False; text_buffer = ""; text_pos = None
                elif event.key == K_ESCAPE:
                    text_mode = False; text_buffer = ""; text_pos = None
                elif event.key == K_BACKSPACE: text_buffer = text_buffer[:-1]
                elif event.unicode and event.unicode.isprintable(): text_buffer += event.unicode
            continue
        # горячие клавиши
        if event.type == KEYDOWN:
            mods = pygame.key.get_mods()
            if event.key == K_s and (mods & KMOD_CTRL):
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                fn = f"canvas_{ts}.png"; pygame.image.save(canvas, fn)
                print(f"--- [OK] Сохранено: {fn}")
            elif event.key==K_p: current_tool="pencil"
            elif event.key==K_l: current_tool="line"
            elif event.key==K_r and not (mods&KMOD_CTRL): current_tool="rect"
            elif event.key==K_o: current_tool="circle"
            elif event.key==K_s and not (mods&KMOD_CTRL): current_tool="square"
            elif event.key==K_t: current_tool="right_tri"
            elif event.key==K_e: current_tool="eq_tri"
            elif event.key==K_d: current_tool="rhombus"
            elif event.key==K_x: current_tool="eraser"
            elif event.key==K_f: current_tool="fill"
            elif event.key==K_w: current_tool="text"
            elif event.key in (K_EQUALS,K_PLUS): brush_idx=min(len(brush_sizes)-1, brush_idx+1)
            elif event.key==K_MINUS: brush_idx=max(0, brush_idx-1)
        # нажатие мыши
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if handle_toolbar_click(event.pos, tool_rects, color_rects, brush_rects): continue
            cx, cy = event.pos[0], event.pos[1] - CANVAS_Y
            if current_tool == "text":
                text_mode = True; text_pos = (cx, cy); text_buffer = ""
            elif current_tool == "fill":
                if 0 <= cx < canvas.get_width() and 0 <= cy < canvas.get_height():
                    flood_fill(canvas, cx, cy, current_color)
            elif current_tool in ("pencil","eraser"):
                dc = WHITE if current_tool=="eraser" else current_color
                sz = eraser_size if current_tool=="eraser" else brush_sizes[brush_idx]
                pygame.draw.circle(canvas, dc, (cx,cy), sz); prev_pos = (cx,cy)
            elif current_tool in SHAPE_TOOLS: start_pos = (cx,cy)
        # движение мыши (непрерывный карандаш)
        if event.type == MOUSEMOTION and event.buttons[0]:
            cx, cy = event.pos[0], event.pos[1] - CANVAS_Y
            if current_tool in ("pencil","eraser") and prev_pos:
                dc = WHITE if current_tool=="eraser" else current_color
                sz = eraser_size if current_tool=="eraser" else brush_sizes[brush_idx]
                pygame.draw.line(canvas, dc, prev_pos, (cx,cy), sz*2)
                pygame.draw.circle(canvas, dc, (cx,cy), sz); prev_pos = (cx,cy)
        # отпускание мыши (фигура закрепляется)
        if event.type == MOUSEBUTTONUP and event.button == 1:
            if current_tool in ("pencil","eraser"): prev_pos = None
            if start_pos and current_tool in SHAPE_TOOLS:
                cx, cy = event.pos[0], event.pos[1] - CANVAS_Y
                draw_shape(canvas, build_shape(current_tool, *start_pos, cx, cy),
                           current_color, brush_sizes[brush_idx])
                start_pos = None
    # --- рисуем ---
    screen.fill(DARK)
    screen.blit(canvas, (0, CANVAS_Y))
    # предпросмотр фигуры при перетаскивании
    if start_pos and current_tool in SHAPE_TOOLS and pygame.mouse.get_pressed()[0]:
        mx, my = pygame.mouse.get_pos()
        sh = build_shape(current_tool, *start_pos, mx, my-CANVAS_Y)
        draw_shape_preview(screen, sh, current_color, CANVAS_Y, brush_sizes[brush_idx])
    # курсор текста
    if text_mode and text_pos:
        screen.blit(text_font.render(text_buffer+"|", True, current_color),
                    (text_pos[0], text_pos[1]+CANVAS_Y))
    # панель поверх всего
    tool_rects, color_rects, brush_rects = draw_toolbar()
    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()
