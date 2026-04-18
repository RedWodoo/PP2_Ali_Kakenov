import pygame
import sys
import datetime
import math
import os

def main():
    pygame.init()
    WIDTH, HEIGHT = 600, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mickey's Clock")
    clock = pygame.time.Clock()
    
    font = pygame.font.SysFont(None, 48)

    hand_img = None
    img_path = os.path.join("images", "mickey_hand.png")
    if os.path.exists(img_path):
        hand_img = pygame.image.load(img_path).convert_alpha()

    center = pygame.math.Vector2(WIDTH // 2, HEIGHT // 2)

    def draw_hand(angle, length, width, color, image=None):
        if image:
            img_rect = image.get_rect()
            scale_factor = length / max(img_rect.width, img_rect.height)
            scaled_img = pygame.transform.scale(image, (int(img_rect.width * scale_factor), int(img_rect.height * scale_factor)))
            

            pivot_y = scaled_img.get_height() / 3 
            
            offset = pygame.math.Vector2(0, pivot_y)
            rotated_offset = offset.rotate(angle)
            
            rotated_img = pygame.transform.rotate(scaled_img, -angle)
            

            rect = rotated_img.get_rect(center=center - rotated_offset)
            screen.blit(rotated_img, rect.topleft)
        else:
            rad = math.radians(angle - 90) 
            end_x = center.x + length * math.cos(rad)
            end_y = center.y + length * math.sin(rad)
            pygame.draw.line(screen, color, center, (end_x, end_y), width)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        now = datetime.datetime.now()
        minute_angle = now.minute * 6
        second_angle = now.second * 6 
        hour_angle = (now.hour % 12 + now.minute / 60) * 30 

        screen.fill((255, 255, 255))
        pygame.draw.circle(screen, (0, 0, 0), center, 250, 5)

        for i in range(1, 13):
            a = math.radians(i * 30 - 90)
            x = center.x + 210 * math.cos(a)
            y = center.y + 210 * math.sin(a)
            num_text = font.render(str(i), True, (0, 0, 0))
            num_rect = num_text.get_rect(center=(x, y))
            screen.blit(num_text, num_rect)


        draw_hand(hour_angle, 150, 15, (0, 0, 0), hand_img)
        draw_hand(minute_angle, 200, 10, (255, 0, 0), hand_img)
        draw_hand(second_angle, 230, 5, (0, 0, 255), hand_img)

        pygame.draw.circle(screen, (0, 0, 0), center, 20)

        pygame.display.flip()
        clock.tick(10)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()