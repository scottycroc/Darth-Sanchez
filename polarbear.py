import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dancing Polar Bear")

# Colors
WHITE = (255, 255, 255)

# Clock
clock = pygame.time.Clock()

# Load polar bear image (replace with your file path)
bear_img = pygame.image.load(r"C:\Users\scott\MyNew SC Folder\Polar_Bear.png").convert_alpha()
bear_img = pygame.transform.scale(bear_img, (150, 150))  # Resize

# Load background music
pygame.mixer.music.load(r"C:\Users\scott\MyNew SC Folder\baby-shark-122769.mp3")  # Replace with your music file
pygame.mixer.music.play(-1)  # Loop indefinitely

# Bear position
bear_x, bear_y = WIDTH // 2, HEIGHT // 2
angle = 0

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Clear screen
    screen.fill(WHITE)

    # Dancing motion synced to beat
    angle += 0.05
    offset_x = math.sin(angle) * 50
    offset_y = math.cos(angle) * 20

    # Rotate bear image for dance effect
    rotated_bear = pygame.transform.rotate(bear_img, math.sin(angle) * 20)

    # Draw bear
    rect = rotated_bear.get_rect(center=(bear_x + offset_x, bear_y + offset_y))
    screen.blit(rotated_bear, rect)

    # Update display
    pygame.display.flip()
    clock.tick(60)
