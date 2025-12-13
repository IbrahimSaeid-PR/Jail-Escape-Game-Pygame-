import pygame
import random
import math
import sys

pygame.init()

# Window
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jail Escape - Grow on Apple")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)
big_font = pygame.font.SysFont(None, 60)

# Player composite geometry
x, y = 100, HEIGHT // 2
body_size = 50
head_size = 20
speed = 5
player_color = (0, 0, 255)
head_color = (0, 0, 0)  # starts black
angle = 0
scale = 1.0
head_glow_time = 0  # duration of glow effect

# Exit
exit_size = 60
exit_x, exit_y = WIDTH - 100, HEIGHT // 2

# Guards and keys
num_guards = 2
num_keys = 3
guards = []
keys = []

# Game state
score = 0
game_over = False

def generate_level():
    global guards, keys, exit_x, exit_y
    exit_x = random.randint(WIDTH // 2, WIDTH - 100)
    exit_y = random.randint(50, HEIGHT - exit_size - 50)
    guards = [{"x": random.randint(150, WIDTH-150), 
               "y": random.randint(50, HEIGHT-50), 
               "dir": random.choice([-2, 2])} for _ in range(num_guards)]
    keys.clear()
    for _ in range(num_keys):
        keys.append({
            "x": random.randint(50, WIDTH-50),
            "y": random.randint(50, HEIGHT-50),
            "collected": False
        })

def reset_player():
    global x, y, player_color, head_color, angle, scale, head_glow_time
    x, y = 100, HEIGHT // 2
    angle = 0
    scale = 1.0
    player_color = (0, 0, 255)
    head_color = (0, 0, 0)
    head_glow_time = 0

def draw_composite_player(surface, cx, cy, angle, scale, body_color, head_color):
    # Body
    body_rect = pygame.Rect(-body_size/2, -body_size/2, body_size, body_size)
    body_rect_scaled = pygame.Rect(body_rect.x*scale, body_rect.y*scale, body_rect.width*scale, body_rect.height*scale)
    
    # Head
    head_rect = pygame.Rect(-head_size/2, -body_size/2 - head_size, head_size, head_size)
    head_rect_scaled = pygame.Rect(head_rect.x*scale, head_rect.y*scale, head_rect.width*scale, head_rect.height*scale)
    
    # Surface for rotation
    surf_width = int(max(body_size, head_size)*scale*2)
    surf_height = int((body_size + head_size)*scale*2)
    surf = pygame.Surface((surf_width, surf_height), pygame.SRCALPHA)
    
    # Draw body
    pygame.draw.rect(surf, body_color, (surf_width/2 - body_rect_scaled.width/2, surf_height/2 - body_rect_scaled.height/2, body_rect_scaled.width, body_rect_scaled.height))
    # Draw head
    pygame.draw.rect(surf, head_color, (surf_width/2 - head_rect_scaled.width/2, surf_height/2 - body_rect_scaled.height/2 - head_rect_scaled.height, head_rect_scaled.width, head_rect_scaled.height))
    
    # Rotate surface
    rotated_surf = pygame.transform.rotate(surf, math.degrees(angle))
    rect = rotated_surf.get_rect(center=(cx, cy))
    surface.blit(rotated_surf, rect.topleft)

def player_rect():
    size = body_size * scale
    return pygame.Rect(x - size/2, y - size/2, size, size)

def guard_rect(g):
    return pygame.Rect(g["x"], g["y"], body_size, body_size)

def key_rect(k):
    return pygame.Rect(k["x"], k["y"], 30, 30)

# First level
generate_level()

running = True
while running:
    clock.tick(60)
    screen.fill((100, 100, 120))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys_pressed = pygame.key.get_pressed()

    if not game_over:
        # Movement
        if keys_pressed[pygame.K_LEFT]: x -= speed
        if keys_pressed[pygame.K_RIGHT]: x += speed
        if keys_pressed[pygame.K_UP]: y -= speed
        if keys_pressed[pygame.K_DOWN]: y += speed

        # Scaling
        if keys_pressed[pygame.K_w]: scale += 0.01
        if keys_pressed[pygame.K_s]: scale = max(0.5, scale - 0.01)

        # Rotation
        if keys_pressed[pygame.K_q]: angle -= 0.03
        if keys_pressed[pygame.K_e]: angle += 0.03

        # Keep inside screen
        size_scaled = body_size * scale
        x = max(size_scaled/2, min(WIDTH - size_scaled/2, x))
        y = max(size_scaled/2, min(HEIGHT - size_scaled/2, y))

        # Move guards
        for g in guards:
            g["x"] += g["dir"]
            if g["x"] < 50 or g["x"] > WIDTH - 100:
                g["dir"] *= -1

        # Collision with guards
        for g in guards:
            if player_rect().colliderect(guard_rect(g)):
                game_over = True

        # Collision with keys (apples)
        for k in keys:
            if not k["collected"] and player_rect().colliderect(key_rect(k)):
                k["collected"] = True
                score += 50
                head_glow_time = 30  # glow for 30 frames
                scale *= 1.23  # grow by 1.23×

        # Glow countdown
        if head_glow_time > 0:
            head_color = (0, 255, 255)  # bright blue light
            head_glow_time -= 1
        else:
            head_color = (0, 0, 0)  # back to black

        # Reaching exit
        exit_rect = pygame.Rect(exit_x, exit_y, exit_size, exit_size)
        if player_rect().colliderect(exit_rect):
            score += 100
            reset_player()
            generate_level()

    # Draw exit
    pygame.draw.rect(screen, (0, 255, 0), (exit_x, exit_y, exit_size, exit_size))

    # Draw keys
    for k in keys:
        if not k["collected"]:
            pygame.draw.rect(screen, (255, 255, 0), (k["x"], k["y"], 30, 30))

    # Draw guards
    for g in guards:
        pygame.draw.rect(screen, (255, 0, 0), (g["x"], g["y"], body_size, body_size))

    # Draw composite player
    draw_composite_player(screen, x, y, angle, scale, player_color, head_color)

    # HUD
    hud = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(hud, (10, 10))

    # Game Over
    if game_over:
        text = big_font.render("GAME OVER", True, (255, 0, 0))
        info = font.render("Press R to Restart", True, (255, 255, 255))
        screen.blit(text, (WIDTH//2 - 150, HEIGHT//2 - 50))
        screen.blit(info, (WIDTH//2 - 110, HEIGHT//2 + 20))
        if keys_pressed[pygame.K_r]:
            score = 0
            game_over = False
            reset_player()
            generate_level()

    pygame.display.flip()

pygame.quit()
sys.exit()
