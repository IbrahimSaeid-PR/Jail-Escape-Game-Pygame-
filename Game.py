import pygame
import random
import math
import sys

pygame.init()

# Window
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Escape Game")

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

# Guards and keys
num_guards = 2
num_keys = 3
guards = []
keys = []

# Game state
score = 0
game_over = False
level_time_left = 10.0  # seconds per level

# Starfield for space background
stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(100, 255)) for _ in range(200)]

def draw_starfield(surface):
    
    for sx, sy, brightness in stars:
        pygame.draw.circle(surface, (brightness, brightness, brightness), (sx, sy), 1)

def all_keys_collected():
    return all(k["collected"] for k in keys) 

def generate_level():
    global guards, keys, level_time_left
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
    level_time_left = 10.0

def reset_player():
    global x, y, player_color, head_color, angle, scale, head_glow_time
    x, y = 100, HEIGHT // 2
    angle = 0
    scale = 1.0
    player_color = (0, 0, 255)
    head_color = (0, 0, 0)
    head_glow_time = 0

def draw_composite_player(surface, cx, cy, angle, scale, body_color, head_color):
    # Simple spaceship: triangle body + small fins + engine glow
    ship_len = body_size * 1.0 * scale
    ship_w = body_size * 0.8 * scale

    surf_w = int(ship_len * 1.4)
    surf_h = int(ship_w * 1.6)
    surf = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
    cx_local, cy_local = surf_w // 2, surf_h // 2

    nose = (cx_local + ship_len * 0.5, cy_local)
    tail_top = (cx_local - ship_len * 0.5, cy_local - ship_w * 0.35)
    tail_bottom = (cx_local - ship_len * 0.5, cy_local + ship_w * 0.35)

    # Main body (triangle)
    pygame.draw.polygon(surf, body_color, [nose, tail_top, tail_bottom])

    # Side fins
    fin_offset = ship_len * 0.05
    fin_span = ship_w * 0.6
    pygame.draw.line(surf, (180, 180, 220), (cx_local - fin_offset, cy_local - fin_span / 2), (cx_local - ship_len * 0.2, cy_local - ship_w * 0.15), 3)
    pygame.draw.line(surf, (180, 180, 220), (cx_local - fin_offset, cy_local + fin_span / 2), (cx_local - ship_len * 0.2, cy_local + ship_w * 0.15), 3)

    # Engine glow at tail
    glow_radius = int(body_size * 0.22 * scale)
    pygame.draw.circle(surf, head_color, (int(cx_local - ship_len * 0.5), cy_local), glow_radius)

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

def draw_space_part(surface, k):
    size = 30
    x0, y0 = k["x"], k["y"]
    cx, cy = x0 + size // 2, y0 + size // 2
    part_surf = pygame.Surface((size, size), pygame.SRCALPHA)

    # Base plate with beveled corners
    plate = [(5, 0), (size-6, 0), (size-1, 5), (size-1, size-6), (size-6, size-1), (5, size-1), (0, size-6), (0, 5)]
    pygame.draw.polygon(part_surf, (230, 210, 40), plate)
    pygame.draw.polygon(part_surf, (140, 120, 10), plate, width=2)

    # Central bolt
    pygame.draw.circle(part_surf, (255, 255, 180), (size//2, size//2), 6)
    pygame.draw.circle(part_surf, (120, 110, 60), (size//2, size//2), 6, width=2)

    # Diagonal struts
    pygame.draw.line(part_surf, (255, 240, 120), (6, size-8), (size-8, 6), 3)
    pygame.draw.line(part_surf, (255, 240, 120), (6, 6), (size-8, size-8), 3)

    surface.blit(part_surf, (x0, y0))

def draw_asteroid(surface, g):
    size = int(body_size * 1.5)
    x0, y0 = g["x"], g["y"]
    rock_surf = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Jagged asteroid shape
    points = [
        (size * 0.2, size * 0.1),
        (size * 0.5, size * 0.05),
        (size * 0.8, size * 0.15),
        (size * 0.9, size * 0.45),
        (size * 0.85, size * 0.8),
        (size * 0.5, size * 0.95),
        (size * 0.15, size * 0.85),
        (size * 0.05, size * 0.5),
    ]
    
    # Dark rocky color
    pygame.draw.polygon(rock_surf, (80, 70, 65), points)
    pygame.draw.polygon(rock_surf, (50, 40, 35), points, width=3)
    
    # Crater-like shadows
    pygame.draw.circle(rock_surf, (60, 50, 45), (int(size * 0.3), int(size * 0.3)), 4)
    pygame.draw.circle(rock_surf, (60, 50, 45), (int(size * 0.7), int(size * 0.6)), 5)
    pygame.draw.circle(rock_surf, (60, 50, 45), (int(size * 0.4), int(size * 0.75)), 3)
    
    surface.blit(rock_surf, (x0, y0))

# First level
generate_level()

running = True
while running:
    dt = clock.tick(60) / 1000.0
    screen.fill((5, 5, 20))  # Deep space dark background
    draw_starfield(screen)  # Draw stars
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys_pressed = pygame.key.get_pressed()
    mouse_buttons = pygame.mouse.get_pressed()

    if not game_over:
        # Movement (arrows/WASD or hold left mouse to steer)
        if keys_pressed[pygame.K_LEFT]: x -= speed
        if keys_pressed[pygame.K_RIGHT]: x += speed
        if keys_pressed[pygame.K_UP]: y -= speed
        if keys_pressed[pygame.K_DOWN]: y += speed

        if mouse_buttons[0]:
            x, y = pygame.mouse.get_pos() # allow player to use mouse

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

        # Level timer countdown
        level_time_left = max(0.0, level_time_left - dt)
        if level_time_left <= 0.0:
            game_over = True

        # Advance when all keys are collected (no exit square)
        if all_keys_collected():
            score += 100
            reset_player()
            generate_level()


    # Draw keys
    for k in keys:
        if not k["collected"]:
            draw_space_part(screen, k)

    # Draw guards as asteroids
    for g in guards:
        draw_asteroid(screen, g)

    # Draw composite player
    draw_composite_player(screen, x, y, angle, scale, player_color, head_color)

    # HUD
    hud = font.render(f"Score: {score}", True, (255, 255, 255))
    timer = font.render(f"Time: {int(math.ceil(level_time_left))}", True, (255, 255, 255))
    screen.blit(hud, (10, 10))
    screen.blit(timer, (10, 40))

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
