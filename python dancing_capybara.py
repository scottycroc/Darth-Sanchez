import pygame
import sys
import math
import random

# Initialize pygame
pygame.init()

# Initialize mixer for music
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# Set up display
WIDTH, HEIGHT = 800, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dancing Capybara Disco")

# Load the PARTY TIME image (generated earlier)
image_path = r"C:\Users\scott\capybara.png"  # Save the generated image here
capybara_img = pygame.image.load(image_path)
capybara_img = pygame.transform.scale(capybara_img, (400, 400))

# Load Baby Shark music
music_path = r"C:\Users\scott\MyNew SC Folder\baby-shark-122769.wav"  # Ensure this file exists
try:
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.play(-1)  # Loop indefinitely
except pygame.error as e:
    print(f"Error loading music: {e}")
    print("Ensure the file exists and is in WAV format.")

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Animation parameters
angle = 0
scale_factor = 1.0
scale_direction = 1

# Beat sync parameters
beat_interval = 60.0 / 115.0  # Baby Shark ~115 BPM
last_beat_time = pygame.time.get_ticks() / 1000.0
bounce_amplitude = 50
y_center = HEIGHT // 2

# Disco lights parameters
lights = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.choice([(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255),(0,255,255)])) for _ in range(10)]

# Main loop
running = True
while running:
    current_time = pygame.time.get_ticks() / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Rotation
    angle += 2
    if angle >= 360:
        angle = 0

    # Scaling
    scale_factor += scale_direction * 0.02
    if scale_factor > 1.3 or scale_factor < 0.7:
        scale_direction *= -1

    # Beat-synced bounce
    if current_time - last_beat_time >= beat_interval:
        last_beat_time = current_time
        bounce_amplitude = random.randint(40, 60)

    phase = (current_time - last_beat_time) / beat_interval
    y_offset = math.sin(phase * math.pi) * bounce_amplitude
    y_pos = y_center + y_offset

    # Transform image
    rotated_img = pygame.transform.rotate(capybara_img, angle)
    new_width = int(rotated_img.get_width() * scale_factor)
    new_height = int(rotated_img.get_height() * scale_factor)
    scaled_img = pygame.transform.scale(rotated_img, (new_width, new_height))

    # Disco lights animation
    window.fill((0, 0, 0))
    for i in range(len(lights)):
        x, y, color = lights[i]
        pygame.draw.circle(window, color, (x, y), random.randint(30, 80))
        # Randomize positions and colors for flashing effect
        lights[i] = (random.randint(0, WIDTH), random.randint(0, HEIGHT), random.choice([(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255),(0,255,255)]))

    # Draw image
    x_pos = WIDTH // 2 - scaled_img.get_width() // 2
    window.blit(scaled_img, (x_pos, y_pos - scaled_img.get_height() // 2))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit() pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit() pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit() pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()me rate
    clock.tick(30)

# Quit pygame
pygame.quit()
sys.exit()