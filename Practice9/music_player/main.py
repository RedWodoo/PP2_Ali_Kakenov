import pygame
import sys
from player import Player

def draw_btn(screen, text, rect, font, mouse_pos):
    color = (200, 200, 200) if rect.collidepoint(mouse_pos) else (150, 150, 150)
    pygame.draw.rect(screen, color, rect, border_radius=5)
    txt_surf = font.render(text, True, (0, 0, 0))
    txt_rect = txt_surf.get_rect(center=rect.center)
    screen.blit(txt_surf, txt_rect)

def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("Music Player")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 22)

    music_player = Player()
    slider_rect = pygame.Rect(20, 180, 560, 10)
    is_dragging = False

    b_prev = pygame.Rect(40, 230, 90, 40)
    b_play = pygame.Rect(145, 230, 90, 40)
    b_pause = pygame.Rect(250, 230, 90, 40)
    b_stop = pygame.Rect(355, 230, 90, 40)
    b_next = pygame.Rect(460, 230, 90, 40)

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p: music_player.play()
                elif event.key == pygame.K_SPACE: music_player.pause()
                elif event.key == pygame.K_s: music_player.stop()
                elif event.key == pygame.K_n: music_player.next_track()
                elif event.key == pygame.K_b: music_player.prev_track()
                elif event.key == pygame.K_q: running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if slider_rect.collidepoint(event.pos):
                        is_dragging = True
                    elif b_prev.collidepoint(event.pos): music_player.prev_track()
                    elif b_play.collidepoint(event.pos): music_player.play()
                    elif b_pause.collidepoint(event.pos): music_player.pause()
                    elif b_stop.collidepoint(event.pos): music_player.stop()
                    elif b_next.collidepoint(event.pos): music_player.next_track()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and is_dragging:
                    is_dragging = False
                    if music_player.total_length > 0:
                        click_x = event.pos[0] - slider_rect.x
                        ratio = max(0, min(click_x / slider_rect.width, 1))
                        music_player.set_position(ratio * music_player.total_length)

        screen.fill((30, 30, 30))
        
        text_track = font.render(f"Track: {music_player.get_track_name()}", True, (255, 255, 255))
        text_status = font.render(f"Status: {music_player.status}", True, (0, 255, 0))
        text_progress = font.render(f"Position: {music_player.get_progress_str()}", True, (255, 200, 0))
        
        screen.blit(text_track, (20, 30))
        screen.blit(text_status, (20, 80))
        screen.blit(text_progress, (20, 130))

        pygame.draw.rect(screen, (100, 100, 100), slider_rect, border_radius=5)
        if music_player.total_length > 0:
            if is_dragging:
                fill_width = max(0, min(mouse_pos[0] - slider_rect.x, slider_rect.width))
            else:
                ratio = music_player.get_current_time() / music_player.total_length
                fill_width = int(slider_rect.width * max(0, min(ratio, 1)))
            pygame.draw.rect(screen, (0, 200, 255), pygame.Rect(slider_rect.x, slider_rect.y, fill_width, slider_rect.height), border_radius=5)
            pygame.draw.circle(screen, (255, 255, 255), (slider_rect.x + fill_width, slider_rect.centery), 8)

        draw_btn(screen, "Prev", b_prev, font, mouse_pos)
        draw_btn(screen, "Play", b_play, font, mouse_pos)
        draw_btn(screen, "Pau/pl", b_pause, font, mouse_pos)
        draw_btn(screen, "Stop", b_stop, font, mouse_pos)
        draw_btn(screen, "Next", b_next, font, mouse_pos)

        hint = small_font.render("Подсказка: горячие клавиши - P (Play), Space (Pause), S (Stop), N (Next), B (Prev)", True, (150, 150, 150))
        screen.blit(hint, (20, 300))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()