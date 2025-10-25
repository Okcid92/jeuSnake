import pygame
import random
import sys
import json
import os
import math

# Initialisation
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1200, 800
CELL_SIZE = 20
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE

# Couleurs
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 150, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GOLD = (255, 215, 0)
PURPLE = (128, 0, 128)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

# Types de fruits
FRUIT_NORMAL = 0
FRUIT_BONUS = 1
FRUIT_SLOW = 2
FRUIT_SHRINK = 3

class PowerUp:
    def __init__(self, pos, fruit_type):
        self.pos = pos
        self.type = fruit_type
        self.timer = 0
        
    def get_color(self):
        colors = {
            FRUIT_NORMAL: RED,
            FRUIT_BONUS: BLUE,
            FRUIT_SLOW: GOLD,
            FRUIT_SHRINK: PURPLE
        }
        return colors[self.type]
        
    def get_points(self):
        points = {
            FRUIT_NORMAL: 1,
            FRUIT_BONUS: 5,
            FRUIT_SLOW: 2,
            FRUIT_SHRINK: 3
        }
        return points[self.type]

class Snake:
    def __init__(self):
        self.body = [(GRID_WIDTH//2, GRID_HEIGHT//2)]
        self.direction = (1, 0)
        self.slow_timer = 0
        
    def move(self):
        head = (self.body[0][0] + self.direction[0], self.body[0][1] + self.direction[1])
        self.body.insert(0, head)
        
    def grow(self):
        pass
        
    def shrink(self):
        if len(self.body) > 1:
            self.body.pop()
            
    def apply_shrink(self):
        # Réduire de 3 segments
        for _ in range(3):
            if len(self.body) > 1:
                self.body.pop()
        
    def check_collision(self):
        head = self.body[0]
        if head[0] < 0 or head[0] >= GRID_WIDTH or head[1] < 0 or head[1] >= GRID_HEIGHT:
            return True
        return head in self.body[1:]

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake Enhanced")
        self.clock = pygame.time.Clock()
        self.snake = Snake()
        self.foods = []
        self.score = 0
        self.best_score = self.load_best_score()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.sprinting = False
        self.base_speed = 8
        self.sprint_multiplier = 2
        self.slow_effect = False
        self.slow_timer = 0
        self.level = 1
        self.start_time = pygame.time.get_ticks()
        
        # Sons (créer des sons simples)
        self.create_sounds()
        
    def create_sounds(self):
        # Créer des sons basiques avec pygame
        try:
            # Son de manger (fréquence haute courte)
            self.eat_sound = pygame.mixer.Sound(buffer=self.generate_tone(800, 0.1))
            # Son de power-up (accord)
            self.powerup_sound = pygame.mixer.Sound(buffer=self.generate_tone(1200, 0.2))
            # Son de game over (fréquence descendante)
            self.gameover_sound = pygame.mixer.Sound(buffer=self.generate_tone(200, 0.5))
        except:
            self.eat_sound = None
            self.powerup_sound = None
            self.gameover_sound = None
    
    def generate_tone(self, frequency, duration):
        # Générer un ton simple
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = []
        for i in range(frames):
            wave = 4096 * math.sin(frequency * 2 * math.pi * i / sample_rate)
            arr.append([int(wave), int(wave)])
        return pygame.sndarray.array(arr)
        
    def load_best_score(self):
        try:
            if os.path.exists('best_score.json'):
                with open('best_score.json', 'r') as f:
                    return json.load(f)['best_score']
        except:
            pass
        return 0
        
    def save_best_score(self):
        try:
            with open('best_score.json', 'w') as f:
                json.dump({'best_score': self.best_score}, f)
        except:
            pass
            
    def maintain_foods(self):
        while len(self.foods) < 10:
            occupied = set(self.snake.body) | set([f.pos for f in self.foods])
            free_positions = []
            
            for x in range(GRID_WIDTH):
                for y in range(GRID_HEIGHT):
                    if (x, y) not in occupied:
                        free_positions.append((x, y))
            
            if not free_positions:
                break
                
            pos = random.choice(free_positions)
            
            # Probabilités des types de fruits
            rand = random.random()
            if rand < 0.7:  # 70% fruits normaux
                fruit_type = FRUIT_NORMAL
            elif rand < 0.85:  # 15% fruits bonus
                fruit_type = FRUIT_BONUS
            elif rand < 0.95:  # 10% fruits slow
                fruit_type = FRUIT_SLOW
            else:  # 5% fruits shrink
                fruit_type = FRUIT_SHRINK
                
            self.foods.append(PowerUp(pos, fruit_type))
                
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
        self.maintain_foods()
        
        # Mettre à jour les timers
        if self.slow_timer > 0:
            self.slow_timer -= 1
            if self.slow_timer == 0:
                self.slow_effect = False
        
        # Vérifier si le snake mange une nourriture
        head = self.snake.body[0]
        for food in self.foods[:]:
            if head == food.pos:
                self.snake.grow()
                self.foods.remove(food)
                points = food.get_points()
                self.score += points
                
                # Effets spéciaux
                if food.type == FRUIT_BONUS:
                    if self.powerup_sound:
                        self.powerup_sound.play()
                elif food.type == FRUIT_SLOW:
                    self.slow_effect = True
                    self.slow_timer = 300  # 5 secondes à 60 FPS
                    if self.powerup_sound:
                        self.powerup_sound.play()
                elif food.type == FRUIT_SHRINK:
                    self.snake.apply_shrink()
                    if self.powerup_sound:
                        self.powerup_sound.play()
                else:
                    if self.eat_sound:
                        self.eat_sound.play()
                
                # Calculer le niveau
                self.level = (self.score // 10) + 1
                break
        else:
            self.snake.shrink()
            
        if self.snake.check_collision():
            return False
        return True
        
    def get_current_speed(self):
        base = self.base_speed + (self.level - 1) * 2  # Vitesse augmente avec le niveau
        if self.slow_effect:
            base = max(4, base // 2)  # Ralentir mais pas trop
        if self.sprinting:
            base *= self.sprint_multiplier
        return min(base, 30)  # Limite maximale
        
    def draw(self):
        self.screen.fill(BLACK)
        
        # Dessiner le snake avec dégradé
        for i, segment in enumerate(self.snake.body):
            color = GREEN if i == 0 else DARK_GREEN  # Tête plus claire
            rect = pygame.Rect(segment[0] * CELL_SIZE, segment[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.screen, color, rect)
            if i == 0:  # Bordure pour la tête
                pygame.draw.rect(self.screen, WHITE, rect, 2)
            
        # Dessiner les nourritures avec effet scintillant
        for food in self.foods:
            color = food.get_color()
            # Effet scintillant pour les power-ups
            if food.type != FRUIT_NORMAL:
                brightness = abs(math.sin(pygame.time.get_ticks() * 0.01)) * 0.3 + 0.7
                color = tuple(int(c * brightness) for c in color)
            
            rect = pygame.Rect(food.pos[0] * CELL_SIZE, food.pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.screen, color, rect)
            
            # Bordure pour les power-ups
            if food.type != FRUIT_NORMAL:
                pygame.draw.rect(self.screen, WHITE, rect, 1)
        
        # Interface utilisateur
        self.draw_ui()
        pygame.display.flip()
        
    def draw_ui(self):
        # Score et meilleur score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        best_text = self.small_font.render(f"Meilleur: {self.best_score}", True, WHITE)
        level_text = self.small_font.render(f"Niveau: {self.level}", True, WHITE)
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(best_text, (10, 50))
        self.screen.blit(level_text, (10, 75))
        
        # Temps de jeu
        elapsed = (pygame.time.get_ticks() - self.start_time) // 1000
        time_text = self.small_font.render(f"Temps: {elapsed}s", True, WHITE)
        self.screen.blit(time_text, (10, 100))
        
        # Indicateurs d'état
        y_offset = 130
        if self.sprinting:
            sprint_text = self.small_font.render("SPRINT!", True, WHITE)
            self.screen.blit(sprint_text, (10, y_offset))
            y_offset += 25
            
        if self.slow_effect:
            slow_text = self.small_font.render("RALENTI", True, GOLD)
            self.screen.blit(slow_text, (10, y_offset))
            y_offset += 25
        
        # Légende des power-ups
        legend_x = WIDTH - 200
        legend_texts = [
            ("Rouge: +1 pt", RED),
            ("Bleu: +5 pts", BLUE),
            ("Or: Ralentit", GOLD),
            ("Violet: Réduit", PURPLE)
        ]
        
        for i, (text, color) in enumerate(legend_texts):
            legend_text = self.small_font.render(text, True, color)
            self.screen.blit(legend_text, (legend_x, 10 + i * 25))
        
    def game_over(self):
        if self.score > self.best_score:
            self.best_score = self.score
            self.save_best_score()
            
        if self.gameover_sound:
            self.gameover_sound.play()
            
        self.screen.fill(BLACK)
        
        # Messages de game over
        game_over_text = self.font.render("GAME OVER", True, WHITE)
        score_text = self.font.render(f"Score Final: {self.score}", True, WHITE)
        best_text = self.font.render(f"Meilleur Score: {self.best_score}", True, WHITE)
        level_text = self.font.render(f"Niveau Atteint: {self.level}", True, WHITE)
        
        elapsed = (pygame.time.get_ticks() - self.start_time) // 1000
        time_text = self.font.render(f"Temps de Jeu: {elapsed}s", True, WHITE)
        
        restart_text = self.small_font.render("ESPACE: Rejouer | ECHAP: Quitter", True, WHITE)
        
        # Centrer les textes
        texts = [game_over_text, score_text, best_text, level_text, time_text, restart_text]
        y_start = HEIGHT // 2 - len(texts) * 25
        
        for i, text in enumerate(texts):
            rect = text.get_rect(center=(WIDTH // 2, y_start + i * 50))
            self.screen.blit(text, rect)
            
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
                self.level = 1
                self.sprinting = False
                self.slow_effect = False
                self.slow_timer = 0
                self.start_time = pygame.time.get_ticks()
                
            self.draw()
            self.clock.tick(self.get_current_speed())
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()