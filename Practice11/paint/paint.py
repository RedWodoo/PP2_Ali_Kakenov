"""
Practice 11 — Рисовалка (Paint)
Расширение Practice 10 с новыми фигурами:
  1. Квадрат  2. Прямоугольный треугольник
  3. Равносторонний треугольник  4. Ромб
GUI-панель с кнопками, непрерывный карандаш, предпросмотр фигур.
"""
import pygame, sys, math
from pygame.locals import *

pygame.init()

WIDTH, HEIGHT = 800, 650
TOOLBAR_H = 70
CANVAS_Y = TOOLBAR_H

WHITE=(255,255,255); BLACK=(0,0,0); GREEN=(0,255,0); RED=(255,0,0)
BLUE=(0,0,255); YELLOW=(255,255,0); ORANGE=(255,140,0); PURPLE=(160,0,200)
GRAY=(180,180,180); DARK=(50,50,50); LGRAY=(220,220,220)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint — Practice 11 (Extra Shapes + GUI)")
clock = pygame.time.Clock()

# холст для сохранения рисунка
canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_H))
canvas.fill(WHITE)

# состояние
current_tool = "pen"
current_color = BLACK
brush_size = 4
eraser_size = 20
start_pos = None   # начало фигуры
prev_pos = None    # предыдущая точка карандаша

TOOLS = [("pen","Pen"),("rect","Rect"),("circle","Circle"),("eraser","Eraser"),
         ("square","Square"),("right_tri","RightTri"),("eq_tri","EqTri"),("rhombus","Rhombus")]
PALETTE = [BLACK, RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, WHITE]

# --- построение фигур ---
def build_shape(tool, x1, y1, x2, y2):
    """Формируем данные фигуры по двум точкам."""
    if tool == "rect":
        return ("rect", pygame.Rect(min(x1,x2), min(y1,y2), abs(x2-x1), abs(y2-y1)))
    elif tool == "circle":
        return ("circle", (x1, y1), int(math.hypot(x2-x1, y2-y1)))
    elif tool == "square":
        side = max(abs(x2-x1), abs(y2-y1))
        sx, sy = (1 if x2>=x1 else -1), (1 if y2>=y1 else -1)
        return ("rect", pygame.Rect(x1 if sx>0 else x1-side, y1 if sy>0 else y1-side, side, side))
    elif tool == "right_tri":
        return ("polygon", [(x1,y1),(x2,y1),(x1,y2)])
    elif tool == "eq_tri":
        side = abs(x2-x1); h = int(side*math.sqrt(3)/2)
        sy = -1 if y2<y1 else 1; mid = (x1+x2)//2
        return ("polygon", [(x1,y1),(x2,y1),(mid, y1+sy*h)])
    elif tool == "rhombus":
        cx,cy = (x1+x2)//2,(y1+y2)//2; dx,dy = abs(x2-x1)//2, abs(y2-y1)//2
        return ("polygon", [(cx,cy-dy),(cx+dx,cy),(cx,cy+dy),(cx-dx,cy)])
    return None

def draw_shape(surface, info, color, width=2):
    """Рисуем фигуру на поверхности."""
    if not info: return
    k = info[0]
    if k=="rect": pygame.draw.rect(surface, color, info[1], width)
    elif k=="circle": pygame.draw.circle(surface, color, info[1], info[2], width)
    elif k=="polygon" and len(info[1])>=3: pygame.draw.polygon(surface, color, info[1], width)

# --- панель инструментов ---
def draw_toolbar():
    """Рисуем панель с кнопками инструментов и палитрой цветов."""
    pygame.draw.rect(screen, DARK, (0, 0, WIDTH, TOOLBAR_H))
    font = pygame.font.SysFont("Verdana", 12)
    mp = pygame.mouse.get_pos()
    # кнопки инструментов
    tr = {}; x = 8
    for tid, lbl in TOOLS:
        bw = 10 + font.size(lbl)[0]; r = pygame.Rect(x, 6, bw, 26); tr[tid] = r
        bg = (0,160,0) if tid==current_tool else (100,100,100) if r.collidepoint(mp) else (70,70,70)
        pygame.draw.rect(screen, bg, r, border_radius=5)
        pygame.draw.rect(screen, LGRAY, r, 1, border_radius=5)
        t = font.render(lbl, True, WHITE)
        screen.blit(t, (r.x+(r.w-t.get_width())//2, r.y+(r.h-t.get_height())//2))
        x += bw + 5
    # палитра цветов
    cr = {}; x = 8
    for i, col in enumerate(PALETTE):
        r = pygame.Rect(x, 38, 24, 24); cr[i] = r
        pygame.draw.rect(screen, col, r)
        pygame.draw.rect(screen, (0,255,0) if col==current_color else GRAY, r, 3 if col==current_color else 1)
        x += 28
    # превью цвета
    px = x + 10
    pygame.draw.rect(screen, current_color, (px, 38, 30, 24))
    pygame.draw.rect(screen, WHITE, (px, 38, 30, 24), 2)
    screen.blit(font.render(f"Brush: {brush_size}px", True, LGRAY), (px+40, 42))
    hf = pygame.font.SysFont("Verdana", 10)
    screen.blit(hf.render("Brush: +/- | Keys: 1-8 tools, R/G/B/Y/C/W colors", True, (140,140,140)), (350, 8))
    return tr, cr

def handle_toolbar_click(pos, tr, cr):
    """Обработка клика по панели."""
    global current_tool, current_color
    if pos[1] > TOOLBAR_H: return False
    for tid, r in tr.items():
        if r.collidepoint(pos): current_tool = tid; return True
    for i, r in cr.items():
        if r.collidepoint(pos): current_color = PALETTE[i]; return True
    return True

# --- главный цикл ---
tool_rects = {}; color_rects = {}
SHAPE_TOOLS = {"rect","circle","square","right_tri","eq_tri","rhombus"}

running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT: running = False
        if event.type == KEYDOWN:
            if event.key==K_1: current_tool="pen"
            elif event.key==K_2: current_tool="rect"
            elif event.key==K_3: current_tool="circle"
            elif event.key==K_4: current_tool="eraser"
            elif event.key==K_5: current_tool="square"
            elif event.key==K_6: current_tool="right_tri"
            elif event.key==K_7: current_tool="eq_tri"
            elif event.key==K_8: current_tool="rhombus"
            elif event.key==K_r: current_color=RED
            elif event.key==K_g: current_color=GREEN
            elif event.key==K_b: current_color=BLUE
            elif event.key==K_y: current_color=YELLOW
            elif event.key==K_c: current_color=BLACK
            elif event.key==K_w: current_color=WHITE
            elif event.key in (K_EQUALS,K_PLUS): brush_size=min(30,brush_size+2)
            elif event.key==K_MINUS: brush_size=max(1,brush_size-2)
        # нажатие мыши
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if handle_toolbar_click(event.pos, tool_rects, color_rects): continue
            cx, cy = event.pos[0], event.pos[1] - CANVAS_Y
            if current_tool in ("pen","eraser"):
                dc = WHITE if current_tool=="eraser" else current_color
                sz = eraser_size if current_tool=="eraser" else brush_size
                pygame.draw.circle(canvas, dc, (cx,cy), sz); prev_pos = (cx,cy)
            elif current_tool in SHAPE_TOOLS: start_pos = (cx,cy)
        # движение мыши (карандаш)
        if event.type == MOUSEMOTION and event.buttons[0]:
            cx, cy = event.pos[0], event.pos[1] - CANVAS_Y
            if current_tool in ("pen","eraser") and prev_pos:
                dc = WHITE if current_tool=="eraser" else current_color
                sz = eraser_size if current_tool=="eraser" else brush_size
                pygame.draw.line(canvas, dc, prev_pos, (cx,cy), sz*2)
                pygame.draw.circle(canvas, dc, (cx,cy), sz); prev_pos = (cx,cy)
        # отпускание мыши (фигура)
        if event.type == MOUSEBUTTONUP and event.button == 1:
            if current_tool in ("pen","eraser"): prev_pos = None
            if start_pos and current_tool in SHAPE_TOOLS:
                cx, cy = event.pos[0], event.pos[1] - CANVAS_Y
                draw_shape(canvas, build_shape(current_tool, *start_pos, cx, cy), current_color, 2)
                start_pos = None
    # --- рисуем ---
    screen.fill(DARK)
    screen.blit(canvas, (0, CANVAS_Y))
    # предпросмотр фигуры при перетаскивании
    if start_pos and current_tool in SHAPE_TOOLS and pygame.mouse.get_pressed()[0]:
        mx, my = pygame.mouse.get_pos()
        sh = build_shape(current_tool, *start_pos, mx, my - CANVAS_Y)
        if sh:
            if sh[0]=="rect":
                r=sh[1].copy(); r.y+=CANVAS_Y; pygame.draw.rect(screen, current_color, r, 2)
            elif sh[0]=="circle":
                pygame.draw.circle(screen, current_color, (sh[1][0],sh[1][1]+CANVAS_Y), sh[2], 2)
            elif sh[0]=="polygon":
                pts=[(p[0],p[1]+CANVAS_Y) for p in sh[1]]
                if len(pts)>=3: pygame.draw.polygon(screen, current_color, pts, 2)
    tool_rects, color_rects = draw_toolbar()
    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()
