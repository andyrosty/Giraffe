import pygame
import sys
import random
import time

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)
ROTTEN_COLOR = (165, 42, 42)

# Game variables
difficulty_factor = 1.0
start_time = time.time()

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Giraffe")
clock = pygame.time.Clock()

class Giraffe:
    def __init__(self):
        self.body_width = 40
        self.body_height = 80
        self.neck_width = 20
        self.min_neck_height = 40
        self.max_neck_height = 300
        self.neck_height = self.min_neck_height
        self.head_width = 30
        self.head_height = 40
        
        self.body_x = SCREEN_WIDTH // 2 - self.body_width // 2
        self.body_y = SCREEN_HEIGHT - self.body_height
        
        self.head_x = self.body_x + self.body_width // 2 - self.head_width // 2
        self.head_y = self.body_y - self.neck_height - self.head_height
        
        self.speed = 5
        self.head_speed = 5
        self.head_direction = 0  # -1 for up, 1 for down, 0 for stationary
    
    def move(self, direction):
        # Move the body left or right
        self.body_x += direction * self.speed * difficulty_factor
        
        # Keep the body within screen bounds
        self.body_x = max(0, min(self.body_x, SCREEN_WIDTH - self.body_width))
        
        # Update head position based on body position
        self.head_x = self.body_x + self.body_width // 2 - self.head_width // 2
    
    def move_head(self, direction):
        # Set the head direction
        self.head_direction = direction
    
    def update(self):
        # Move the head up or down based on direction
        if self.head_direction != 0:
            self.neck_height += self.head_direction * self.head_speed * difficulty_factor
            
            # Keep the neck height within limits
            self.neck_height = max(self.min_neck_height, min(self.neck_height, self.max_neck_height))
            
            # Update head position based on neck height
            self.head_y = self.body_y - self.neck_height - self.head_height
    
    def grow(self):
        # Grow the neck when eating a good leaf
        self.neck_height += 10
        if self.neck_height > self.max_neck_height:
            self.neck_height = self.max_neck_height
        self.head_y = self.body_y - self.neck_height - self.head_height
    
    def shrink(self):
        # Shrink the neck when eating a rotten leaf
        self.neck_height -= 20
        if self.neck_height < self.min_neck_height:
            self.neck_height = self.min_neck_height
        self.head_y = self.body_y - self.neck_height - self.head_height
    
    def draw(self):
        # Draw the body
        pygame.draw.rect(screen, BROWN, (self.body_x, self.body_y, self.body_width, self.body_height))
        
        # Draw the neck
        pygame.draw.rect(screen, BROWN, (
            self.body_x + self.body_width // 2 - self.neck_width // 2,
            self.body_y - self.neck_height,
            self.neck_width,
            self.neck_height
        ))
        
        # Draw the head
        pygame.draw.rect(screen, BROWN, (self.head_x, self.head_y, self.head_width, self.head_height))
    
    def get_head_rect(self):
        return pygame.Rect(self.head_x, self.head_y, self.head_width, self.head_height)

class Leaf:
    def __init__(self, is_good=True):
        self.width = 20
        self.height = 20
        self.x = random.randint(0, SCREEN_WIDTH - self.width)
        self.y = -self.height
        self.speed = random.uniform(2, 4)
        self.is_good = is_good
    
    def update(self):
        self.y += self.speed * difficulty_factor
    
    def draw(self):
        color = GREEN if self.is_good else ROTTEN_COLOR
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT

def spawn_leaf(leaves, difficulty):
    # Determine if we should spawn a leaf based on difficulty
    if random.random() < 0.02 * difficulty:
        # Determine if it's a good or rotten leaf (70% good, 30% rotten)
        is_good = random.random() < 0.7
        leaves.append(Leaf(is_good))

def main():
    global difficulty_factor
    
    giraffe = Giraffe()
    leaves = []
    
    game_over = False
    
    while not game_over:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    giraffe.move_head(-1)  # Move head up
                elif event.key == pygame.K_DOWN:
                    giraffe.move_head(1)   # Move head down
            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_UP, pygame.K_DOWN):
                    giraffe.move_head(0)   # Stop moving head
        
        # Get pressed keys for continuous movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            giraffe.move(-1)  # Move left
        if keys[pygame.K_RIGHT]:
            giraffe.move(1)   # Move right
        
        # Update game state
        giraffe.update()
        
        # Increase difficulty over time
        elapsed_time = time.time() - start_time
        difficulty_factor = 1.0 + (elapsed_time / 60.0)  # Increase by 100% every minute
        
        # Spawn leaves
        spawn_leaf(leaves, difficulty_factor)
        
        # Update leaves and check collisions
        for leaf in leaves[:]:
            leaf.update()
            
            # Check if leaf collides with giraffe's head
            if leaf.get_rect().colliderect(giraffe.get_head_rect()):
                if leaf.is_good:
                    giraffe.grow()
                else:
                    giraffe.shrink()
                leaves.remove(leaf)
            # Check if good leaf hits the ground
            elif leaf.is_off_screen():
                if leaf.is_good:
                    game_over = True
                leaves.remove(leaf)
        
        # Draw everything
        screen.fill(WHITE)
        
        # Draw the ground
        pygame.draw.rect(screen, GREEN, (0, SCREEN_HEIGHT - 10, SCREEN_WIDTH, 10))
        
        # Draw game objects
        giraffe.draw()
        for leaf in leaves:
            leaf.draw()
        
        # Draw timer
        font = pygame.font.SysFont(None, 36)
        timer_text = font.render(f"Time: {int(elapsed_time)}s", True, BLACK)
        screen.blit(timer_text, (10, 10))
        
        # Update display
        pygame.display.flip()
        clock.tick(FPS)
    
    # Game over screen
    font = pygame.font.SysFont(None, 72)
    game_over_text = font.render("GAME OVER", True, BLACK)
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 
                                SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2))
    
    score_font = pygame.font.SysFont(None, 48)
    score_text = score_font.render(f"You survived for {int(elapsed_time)} seconds", True, BLACK)
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 
                            SCREEN_HEIGHT // 2 + game_over_text.get_height()))
    
    pygame.display.flip()
    
    # Wait for a moment before quitting
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                waiting = False
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()