import pygame
import sys
import os
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 400
GRAVITY = 0.25
FLAP_STRENGTH = -4.5
PIPE_SPEED = 3
PIPE_GAP = 100
PIPE_FREQUENCY = 1500  # milliseconds

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pixel Art Flappy Bird")
clock = pygame.time.Clock()

# Load images
def load_image(name):
    try:
        image = pygame.image.load(os.path.join('assets', name))
        return image
    except:
        print(f"Warning: Could not load {name}, using placeholder")
        return None

bird_img = load_image('bird.png')
pipe_img = load_image('pole.png')

class Bird:
    def __init__(self):
        self.x = SCREEN_WIDTH // 3
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        if bird_img:
            self.rect = bird_img.get_rect()
            # Create a smaller collision rectangle (about 70% of the original size)
            self.collision_rect = pygame.Rect(
                self.rect.x + self.rect.width * 0.15,
                self.rect.y + self.rect.height * 0.15,
                self.rect.width * 0.7,
                self.rect.height * 0.7
            )
        else:
            self.rect = pygame.Rect(self.x, self.y, 30, 30)
            self.collision_rect = pygame.Rect(
                self.x + 5,
                self.y + 5,
                20,
                20
            )
        self.rect.x = self.x
        self.rect.y = self.y
        self.update_collision_rect()
        
    def flap(self):
        self.velocity = FLAP_STRENGTH
        
    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        self.rect.y = self.y
        self.update_collision_rect()
        
    def update_collision_rect(self):
        if bird_img:
            self.collision_rect.x = self.rect.x + self.rect.width * 0.15
            self.collision_rect.y = self.rect.y + self.rect.height * 0.15
        else:
            self.collision_rect.x = self.rect.x + 5
            self.collision_rect.y = self.rect.y + 5
        
    def draw(self, screen):
        if bird_img:
            screen.blit(bird_img, self.rect)
        else:
            pygame.draw.rect(screen, WHITE, self.rect)
        # Uncomment the following line to see the collision rectangle (for debugging)
        # pygame.draw.rect(screen, (255, 0, 0), self.collision_rect, 1)

class Pipe:
    def __init__(self):
        self.gap_y = random.randint(80, SCREEN_HEIGHT - 80)
        self.x = SCREEN_WIDTH
        self.top_height = self.gap_y - PIPE_GAP // 2
        self.bottom_height = SCREEN_HEIGHT - (self.gap_y + PIPE_GAP // 2)
        
        if pipe_img:
            # Get original pipe dimensions
            original_width, original_height = pipe_img.get_size()
            
            # Create top pipe (flipped)
            self.top_pipe = pygame.transform.flip(pipe_img, False, True)
            # Scale the top pipe vertically only
            self.top_pipe = pygame.transform.scale(self.top_pipe, (original_width, self.top_height))
            self.top_rect = self.top_pipe.get_rect()
            self.top_rect.x = self.x
            self.top_rect.bottom = self.gap_y - PIPE_GAP // 2
            
            # Create bottom pipe (original)
            # Scale the bottom pipe vertically only
            self.bottom_pipe = pygame.transform.scale(pipe_img, (original_width, self.bottom_height))
            self.bottom_rect = self.bottom_pipe.get_rect()
            self.bottom_rect.x = self.x
            self.bottom_rect.top = self.gap_y + PIPE_GAP // 2
        else:
            self.top_rect = pygame.Rect(self.x, 0, 50, self.top_height)
            self.bottom_rect = pygame.Rect(self.x, SCREEN_HEIGHT - self.bottom_height, 50, self.bottom_height)
        
    def update(self):
        self.x -= PIPE_SPEED
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x
        
    def draw(self, screen):
        if pipe_img:
            screen.blit(self.top_pipe, self.top_rect)
            screen.blit(self.bottom_pipe, self.bottom_rect)
        else:
            pygame.draw.rect(screen, GREEN, self.top_rect)
            pygame.draw.rect(screen, GREEN, self.bottom_rect)

def main():
    bird = Bird()
    pipes = []
    last_pipe = pygame.time.get_ticks()
    score = 0
    best_score = 0
    game_over = False
    
    while True:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    bird.flap()
                if event.key == pygame.K_SPACE and game_over:
                    # Reset game
                    bird = Bird()
                    pipes = []
                    last_pipe = current_time
                    score = 0
                    game_over = False
        
        if not game_over:
            # Update bird
            bird.update()
            
            # Generate new pipes
            if current_time - last_pipe > PIPE_FREQUENCY:
                pipes.append(Pipe())
                last_pipe = current_time
            
            # Update pipes
            for pipe in pipes[:]:
                pipe.update()
                if pipe.x < -50:
                    pipes.remove(pipe)
                    score += 1
                    # Update best score if current score is higher
                    if score > best_score:
                        best_score = score
                
                # Check for collisions using the smaller collision rectangle
                if bird.collision_rect.colliderect(pipe.top_rect) or bird.collision_rect.colliderect(pipe.bottom_rect):
                    game_over = True
            
            # Check if bird hits boundaries
            if bird.y < 0 or bird.y > SCREEN_HEIGHT:
                game_over = True
        
        # Draw everything
        screen.fill(BLACK)
        bird.draw(screen)
        for pipe in pipes:
            pipe.draw(screen)
            
        # Draw scores
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, WHITE)
        best_score_text = font.render(f"Best: {best_score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(best_score_text, (10, 50))
        
        if game_over:
            game_over_text = font.render("Game Over! Press SPACE to restart", True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2))
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main() 