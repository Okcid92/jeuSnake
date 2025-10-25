import pygame
import random
import sys

# Initialisation
pygame.init()
WIDTH, HEIGHT = 1200, 800
CELL_SIZE = 20
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE

# Couleurs
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

class Snake:
    def __init__(self):
        self.body = [(GRID_WIDTH//2, GRID_HEIGHT//2)]
        self.direction = (1, 0)
        
    def move(self):
        head = (self.body[0][0] + self.direction[0], self.body[0][1] + self.direction[1])
        self.body.insert(0, head)
        
    def grow(self):
        pass  # Ne pas supprimer la queue
        
    def shrink(self):
        self.body.pop()
        
    def check_collision(self):
        head = self.body[0]
        # Collision avec les bords
        if head[0] < 0 or head[0] >= GRID_WIDTH or head[1] < 0 or head[1] >= GRID_HEIGHT:
            return True
        # Collision avec soi-même
        return head in self.body[1:]

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.snake = Snake()
        self.foods = []
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        self.sprinting = False
        self.normal_speed = 10
        self.sprint_speed = 20
        
    def maintain_foods(self):
        # Maintenir 10 fruits en permanence
        while len(self.foods) < 10:
            # Créer une liste de toutes les positions libres
            occupied = set(self.snake.body) | set(self.foods)
            free_positions = []
            
            for x in range(GRID_WIDTH):
                for y in range(GRID_HEIGHT):
                    if (x, y) not in occupied:
                        free_positions.append((x, y))
            
            # Si aucune position libre, arrêter (grille pleine)
            if not free_positions:
                break
                
            # Choisir une position aléatoire parmi les libres
            pos = random.choice(free_positions)
            self.foods.append(pos)
                
    def handle_events(self):
        keys = pygame.key.get_pressed()
        self.sprinting = keys[pygame.K_SPACE]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and self.snake.direction != (0, 1):
                    self.snake.direction = (0, -1)
                elif event.key == pygame.K_DOWN and self.snake.direction != (0, -1):
                    self.snake.direction = (0, 1)
                elif event.key == pygame.K_LEFT and self.snake.direction != (1, 0):
                    self.snake.direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and self.snake.direction != (-1, 0):
                    self.snake.direction = (1, 0)
        return True
        
    def update(self):
        self.snake.move()
        
        # Maintenir 10 fruits
        self.maintain_foods()
        
        # Vérifier si le snake mange une nourriture
        head = self.snake.body[0]
        if head in self.foods:
            self.snake.grow()
            self.foods.remove(head)
            self.score += 1
        else:
            self.snake.shrink()
            
        # Vérifier les collisions
        if self.snake.check_collision():
            return False
        return True
        
    def draw(self):
        self.screen.fill(BLACK)
        
        # Dessiner le snake
        for segment in self.snake.body:
            rect = pygame.Rect(segment[0] * CELL_SIZE, segment[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.screen, GREEN, rect)
            
        # Dessiner les nourritures
        for food in self.foods:
            food_rect = pygame.Rect(food[0] * CELL_SIZE, food[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.screen, RED, food_rect)
        
        # Afficher le score et le sprint
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        if self.sprinting:
            sprint_text = self.font.render("SPRINT!", True, WHITE)
            self.screen.blit(sprint_text, (10, 50))
        
        pygame.display.flip()
        
    def game_over(self):
        self.screen.fill(BLACK)
        game_over_text = self.font.render("GAME OVER", True, WHITE)
        score_text = self.font.render(f"Score Final: {self.score}", True, WHITE)
        restart_text = self.font.render("Appuyez sur ESPACE pour rejouer ou ECHAP pour quitter", True, WHITE)
        
        self.screen.blit(game_over_text, (WIDTH//2 - 100, HEIGHT//2 - 50))
        self.screen.blit(score_text, (WIDTH//2 - 100, HEIGHT//2))
        self.screen.blit(restart_text, (WIDTH//2 - 300, HEIGHT//2 + 50))
        pygame.display.flip()
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    return False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    return True
                    
    def run(self):
        running = True
        while running:
            if not self.handle_events():
                break
                
            if not self.update():
                if not self.game_over():
                    break
                # Redémarrer le jeu
                self.snake = Snake()
                self.foods = []
                self.score = 0
                self.sprinting = False
                
            self.draw()
            speed = self.sprint_speed if self.sprinting else self.normal_speed
            self.clock.tick(speed)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
