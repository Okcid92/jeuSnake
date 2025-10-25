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
DARK_BLUE = (0, 0, 50)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 150, 0)
LIGHT_GREEN = (100, 255, 100)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
GOLD = (255, 215, 0)
PURPLE = (128, 0, 128)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)

# Types de fruits et power-ups
FRUIT_NORMAL = 0
FRUIT_BONUS = 1
FRUIT_SLOW = 2
FRUIT_SHRINK = 3
FRUIT_GHOST = 4
FRUIT_SPEED = 5

# Modes de jeu
MODE_CLASSIC = 0
MODE_PORTAL = 1
MODE_OBSTACLES = 2

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.color = color
        self.life = 30
        self.max_life = 30
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        
    def draw(self, screen):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            color = (*self.color, alpha)
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 3)

class Obstacle:
    def __init__(self, x, y, moving=False):
        self.x = x
        self.y = y
        self.moving = moving
        self.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        self.move_timer = 0
        
    def update(self):
        if self.moving:
            self.move_timer += 1
            if self.move_timer > 60:  # Changer de direction toutes les secondes
                self.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
                self.move_timer = 0
                
            new_x = self.x + self.direction[0]
            new_y = self.y + self.direction[1]
            
            if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT:
                self.x = new_x
                self.y = new_y

class PowerUp:
    def __init__(self, pos, fruit_type):
        self.pos = pos
        self.type = fruit_type
        self.timer = 0
        self.animation_timer = 0
        
    def get_color(self):
        colors = {
            FRUIT_NORMAL: RED,
            FRUIT_BONUS: BLUE,
            FRUIT_SLOW: GOLD,
            FRUIT_SHRINK: PURPLE,
            FRUIT_GHOST: CYAN,
            FRUIT_SPEED: ORANGE
        }
        return colors[self.type]
        
    def get_points(self):
        points = {
            FRUIT_NORMAL: 1,
            FRUIT_BONUS: 5,
            FRUIT_SLOW: 2,
            FRUIT_SHRINK: 3,
            FRUIT_GHOST: 4,
            FRUIT_SPEED: 3
        }
        return points[self.type]

class Snake:
    def __init__(self, color=GREEN, start_pos=None):
        if start_pos is None:
            start_pos = (GRID_WIDTH//2, GRID_HEIGHT//2)
        self.body = [start_pos]
        self.direction = (1, 0)
        self.color = color
        self.ghost_timer = 0
        self.speed_boost_timer = 0
        
    def move(self):
        head = (self.body[0][0] + self.direction[0], self.body[0][1] + self.direction[1])
        self.body.insert(0, head)
        
    def grow(self):
        pass
        
    def shrink(self):
        if len(self.body) > 1:
            self.body.pop()
            
    def apply_shrink(self):
        for _ in range(3):
            if len(self.body) > 1:
                self.body.pop()
        
    def check_collision(self, obstacles=None, portal_mode=False):
        head = self.body[0]
        
        # Mode portail : téléportation
        if portal_mode:
            new_head = list(head)
            if head[0] < 0:
                new_head[0] = GRID_WIDTH - 1
            elif head[0] >= GRID_WIDTH:
                new_head[0] = 0
            if head[1] < 0:
                new_head[1] = GRID_HEIGHT - 1
            elif head[1] >= GRID_HEIGHT:
                new_head[1] = 0
            self.body[0] = tuple(new_head)
            head = self.body[0]
        else:
            # Collision avec les bords
            if head[0] < 0 or head[0] >= GRID_WIDTH or head[1] < 0 or head[1] >= GRID_HEIGHT:
                return True
        
        # Collision avec soi-même (sauf en mode fantôme)
        if self.ghost_timer <= 0 and head in self.body[1:]:
            return True
            
        # Collision avec obstacles
        if obstacles:
            for obstacle in obstacles:
                if head == (obstacle.x, obstacle.y):
                    return True
                    
        return False

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake Ultimate Edition")
        self.clock = pygame.time.Clock()
        
        # État du jeu
        self.game_mode = MODE_CLASSIC
        self.multiplayer = False
        self.snake1 = Snake(GREEN)
        self.snake2 = Snake(BLUE, (GRID_WIDTH//4, GRID_HEIGHT//2))
        
        self.foods = []
        self.obstacles = []
        self.particles = []
        
        # Scores et statistiques
        self.score1 = 0
        self.score2 = 0
        self.best_score = self.load_best_score()
        self.games_played = self.load_stats().get('games_played', 0)
        self.total_time = self.load_stats().get('total_time', 0)
        
        # Interface
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 48)
        
        # Effets et timers
        self.sprinting1 = False
        self.sprinting2 = False
        self.base_speed = 8
        self.sprint_multiplier = 2
        self.slow_effect = False
        self.slow_timer = 0
        self.level = 1
        self.start_time = pygame.time.get_ticks()
        
        # Menu
        self.in_menu = True
        self.menu_selection = 0
        self.menu_options = [
            "Mode Classique",
            "Mode Portails", 
            "Mode Obstacles",
            "Multijoueur Local",
            "Quitter"
        ]
        
        # Thèmes visuels
        self.theme = 0
        self.themes = [
            {"bg": BLACK, "grid": GRAY},
            {"bg": DARK_BLUE, "grid": BLUE},
            {"bg": (20, 20, 20), "grid": (40, 40, 40)}
        ]
        
        self.create_sounds()
        self.create_background_pattern()
        
    def create_sounds(self):
        try:
            self.eat_sound = pygame.mixer.Sound(buffer=self.generate_tone(800, 0.1))
            self.powerup_sound = pygame.mixer.Sound(buffer=self.generate_tone(1200, 0.2))
            self.gameover_sound = pygame.mixer.Sound(buffer=self.generate_tone(200, 0.5))
            self.level_up_sound = pygame.mixer.Sound(buffer=self.generate_chord([440, 554, 659], 0.3))
        except:
            self.eat_sound = None
            self.powerup_sound = None
            self.gameover_sound = None
            self.level_up_sound = None
    
    def generate_tone(self, frequency, duration):
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = []
        for i in range(frames):
            wave = 2048 * math.sin(frequency * 2 * math.pi * i / sample_rate)
            arr.append([int(wave), int(wave)])
        return pygame.sndarray.array(arr)
        
    def generate_chord(self, frequencies, duration):
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = []
        for i in range(frames):
            wave = 0
            for freq in frequencies:
                wave += 1024 * math.sin(freq * 2 * math.pi * i / sample_rate)
            arr.append([int(wave), int(wave)])
        return pygame.sndarray.array(arr)
        
    def create_background_pattern(self):
        self.bg_surface = pygame.Surface((WIDTH, HEIGHT))
        self.bg_surface.fill(self.themes[self.theme]["bg"])
            
    def load_best_score(self):
        try:
            if os.path.exists('game_data.json'):
                with open('game_data.json', 'r') as f:
                    return json.load(f).get('best_score', 0)
        except:
            pass
        return 0
        
    def load_stats(self):
        try:
            if os.path.exists('game_data.json'):
                with open('game_data.json', 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
        
    def save_game_data(self):
        try:
            data = {
                'best_score': self.best_score,
                'games_played': self.games_played,
                'total_time': self.total_time
            }
            with open('game_data.json', 'w') as f:
                json.dump(data, f)
        except:
            pass
            
    def create_obstacles(self, count=5):
        self.obstacles = []
        for _ in range(count):
            while True:
                x = random.randint(5, GRID_WIDTH-5)
                y = random.randint(5, GRID_HEIGHT-5)
                if (x, y) not in self.snake1.body and (not self.multiplayer or (x, y) not in self.snake2.body):
                    moving = random.random() < 0.3  # 30% chance d'obstacle mobile
                    self.obstacles.append(Obstacle(x, y, moving))
                    break
                    
    def maintain_foods(self):
        target_count = 15 if self.multiplayer else 10
        while len(self.foods) < target_count:
            occupied = set(self.snake1.body)
            if self.multiplayer:
                occupied |= set(self.snake2.body)
            occupied |= set([f.pos for f in self.foods])
            occupied |= set([(o.x, o.y) for o in self.obstacles])
            
            free_positions = []
            for x in range(GRID_WIDTH):
                for y in range(GRID_HEIGHT):
                    if (x, y) not in occupied:
                        free_positions.append((x, y))
            
            if not free_positions:
                break
                
            pos = random.choice(free_positions)
            
            # Probabilités étendues
            rand = random.random()
            if rand < 0.5:  # 50% fruits normaux
                fruit_type = FRUIT_NORMAL
            elif rand < 0.65:  # 15% fruits bonus
                fruit_type = FRUIT_BONUS
            elif rand < 0.75:  # 10% fruits slow
                fruit_type = FRUIT_SLOW
            elif rand < 0.85:  # 10% fruits shrink
                fruit_type = FRUIT_SHRINK
            elif rand < 0.95:  # 10% fruits ghost
                fruit_type = FRUIT_GHOST
            else:  # 5% fruits speed
                fruit_type = FRUIT_SPEED
                
            self.foods.append(PowerUp(pos, fruit_type))
            
    def handle_menu_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.menu_selection = (self.menu_selection - 1) % len(self.menu_options)
                elif event.key == pygame.K_DOWN:
                    self.menu_selection = (self.menu_selection + 1) % len(self.menu_options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if self.menu_selection == 0:  # Mode Classique
                        self.start_game(MODE_CLASSIC, False)
                    elif self.menu_selection == 1:  # Mode Portails
                        self.start_game(MODE_PORTAL, False)
                    elif self.menu_selection == 2:  # Mode Obstacles
                        self.start_game(MODE_OBSTACLES, False)
                    elif self.menu_selection == 3:  # Multijoueur
                        self.start_game(MODE_CLASSIC, True)
                    elif self.menu_selection == 4:  # Quitter
                        return False
                elif event.key == pygame.K_t:  # Changer de thème
                    self.theme = (self.theme + 1) % len(self.themes)
                    self.create_background_pattern()
        return True
        
    def start_game(self, mode, multiplayer):
        self.game_mode = mode
        self.multiplayer = multiplayer
        self.in_menu = False
        
        # Réinitialiser le jeu
        self.snake1 = Snake(GREEN)
        if multiplayer:
            self.snake2 = Snake(BLUE, (GRID_WIDTH//4, GRID_HEIGHT//2))
        
        self.foods = []
        self.obstacles = []
        self.particles = []
        self.score1 = 0
        self.score2 = 0
        self.level = 1
        self.start_time = pygame.time.get_ticks()
        
        if mode == MODE_OBSTACLES:
            self.create_obstacles()
            
    def handle_game_events(self):
        keys = pygame.key.get_pressed()
        
        # Contrôles Joueur 1
        self.sprinting1 = keys[pygame.K_SPACE]
        
        # Contrôles Joueur 2 (si multijoueur)
        if self.multiplayer:
            self.sprinting2 = keys[pygame.K_RSHIFT]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.in_menu = True
                    return True
                    
                # Contrôles Joueur 1 (flèches)
                if event.key == pygame.K_UP and self.snake1.direction != (0, 1):
                    self.snake1.direction = (0, -1)
                elif event.key == pygame.K_DOWN and self.snake1.direction != (0, -1):
                    self.snake1.direction = (0, 1)
                elif event.key == pygame.K_LEFT and self.snake1.direction != (1, 0):
                    self.snake1.direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and self.snake1.direction != (-1, 0):
                    self.snake1.direction = (1, 0)
                    
                # Contrôles Joueur 2 (WASD)
                if self.multiplayer:
                    if event.key == pygame.K_w and self.snake2.direction != (0, 1):
                        self.snake2.direction = (0, -1)
                    elif event.key == pygame.K_s and self.snake2.direction != (0, -1):
                        self.snake2.direction = (0, 1)
                    elif event.key == pygame.K_a and self.snake2.direction != (1, 0):
                        self.snake2.direction = (-1, 0)
                    elif event.key == pygame.K_d and self.snake2.direction != (-1, 0):
                        self.snake2.direction = (1, 0)
        return True
        
    def update_snake(self, snake, player_num):
        snake.move()
        
        # Mettre à jour les timers d'effets
        if snake.ghost_timer > 0:
            snake.ghost_timer -= 1
        if snake.speed_boost_timer > 0:
            snake.speed_boost_timer -= 1
        
        # Vérifier consommation de nourriture
        head = snake.body[0]
        for food in self.foods[:]:
            if head == food.pos:
                snake.grow()
                self.foods.remove(food)
                points = food.get_points()
                
                if player_num == 1:
                    self.score1 += points
                else:
                    self.score2 += points
                
                # Créer des particules
                for _ in range(10):
                    self.particles.append(Particle(
                        head[0] * CELL_SIZE + CELL_SIZE//2,
                        head[1] * CELL_SIZE + CELL_SIZE//2,
                        food.get_color()
                    ))
                
                # Effets spéciaux
                if food.type == FRUIT_BONUS:
                    if self.powerup_sound:
                        self.powerup_sound.play()
                elif food.type == FRUIT_SLOW:
                    self.slow_effect = True
                    self.slow_timer = max(self.slow_timer, 300)  # Ne pas cumuler, prendre le max
                    if self.powerup_sound:
                        self.powerup_sound.play()
                elif food.type == FRUIT_SHRINK:
                    snake.apply_shrink()
                    if self.powerup_sound:
                        self.powerup_sound.play()
                elif food.type == FRUIT_GHOST:
                    snake.ghost_timer = 180  # 3 secondes
                    if self.powerup_sound:
                        self.powerup_sound.play()
                elif food.type == FRUIT_SPEED:
                    snake.speed_boost_timer = 300  # 5 secondes
                    if self.powerup_sound:
                        self.powerup_sound.play()
                else:
                    if self.eat_sound:
                        self.eat_sound.play()
                
                # Calculer le niveau
                total_score = self.score1 + (self.score2 if self.multiplayer else 0)
                new_level = (total_score // 15) + 1
                if new_level > self.level:
                    self.level = new_level
                    if self.level_up_sound:
                        self.level_up_sound.play()
                break
        else:
            snake.shrink()
            
        # Vérifier collisions
        portal_mode = (self.game_mode == MODE_PORTAL)
        obstacles = self.obstacles if self.game_mode == MODE_OBSTACLES else None
        
        if snake.check_collision(obstacles, portal_mode):
            return False
            
        # Collision entre snakes en multijoueur
        if self.multiplayer:
            other_snake = self.snake2 if player_num == 1 else self.snake1
            if snake.ghost_timer <= 0 and head in other_snake.body:
                return False
                
        return True
        
    def update_game(self):
        # Mettre à jour les obstacles mobiles
        for obstacle in self.obstacles:
            obstacle.update()
            
        # Maintenir la nourriture
        self.maintain_foods()
        
        # Mettre à jour les timers globaux
        if self.slow_timer > 0:
            self.slow_timer -= 1
            if self.slow_timer == 0:
                self.slow_effect = False
        
        # Mettre à jour les particules
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)
        
        # Mettre à jour les snakes
        if not self.update_snake(self.snake1, 1):
            return False
            
        if self.multiplayer and not self.update_snake(self.snake2, 2):
            return False
            
        return True
        
    def get_current_speed(self, snake, sprinting):
        base = self.base_speed + (self.level - 1) * 1.5
        
        if self.slow_effect:
            base = max(4, base // 2)
            
        if snake.speed_boost_timer > 0:
            base *= 1.5
            
        if sprinting:
            base *= self.sprint_multiplier
            
        return min(int(base), 25)
        
    def draw_menu(self):
        self.screen.blit(self.bg_surface, (0, 0))
        
        # Titre avec effet
        title = self.big_font.render("SNAKE ULTIMATE", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH//2, 150))
        
        # Effet d'ombre
        shadow = self.big_font.render("SNAKE ULTIMATE", True, GRAY)
        shadow_rect = shadow.get_rect(center=(WIDTH//2 + 3, 153))
        self.screen.blit(shadow, shadow_rect)
        self.screen.blit(title, title_rect)
        
        # Options du menu
        for i, option in enumerate(self.menu_options):
            color = WHITE if i == self.menu_selection else GRAY
            if i == self.menu_selection:
                # Effet de sélection
                pygame.draw.rect(self.screen, (50, 50, 50), 
                               (WIDTH//2 - 150, 250 + i * 50 - 5, 300, 40))
            
            text = self.font.render(option, True, color)
            text_rect = text.get_rect(center=(WIDTH//2, 270 + i * 50))
            self.screen.blit(text, text_rect)
        
        # Instructions
        instructions = [
            "Flèches: Naviguer",
            "ENTRÉE/ESPACE: Sélectionner", 
            "T: Changer de thème",
            f"Meilleur score: {self.best_score}",
            f"Parties jouées: {self.games_played}"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, WHITE)
            text_rect = text.get_rect(center=(WIDTH//2, 500 + i * 25))
            self.screen.blit(text, text_rect)
            
    def draw_snake(self, snake):
        for i, segment in enumerate(snake.body):
            # Couleur avec dégradé
            if i == 0:  # Tête
                color = snake.color
                if snake.ghost_timer > 0:
                    # Effet fantôme
                    alpha = 128 + int(127 * math.sin(pygame.time.get_ticks() * 0.02))
                    color = (*color[:3], alpha)
            else:  # Corps
                fade = max(0.3, 1 - (i * 0.1))
                color = tuple(int(c * fade) for c in snake.color)
            
            rect = pygame.Rect(segment[0] * CELL_SIZE, segment[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.screen, color, rect)
            
            # Bordures et effets
            if i == 0:
                pygame.draw.rect(self.screen, WHITE, rect, 2)
                # Yeux
                eye_size = 3
                pygame.draw.circle(self.screen, WHITE, 
                                 (rect.centerx - 5, rect.centery - 3), eye_size)
                pygame.draw.circle(self.screen, WHITE,
                                 (rect.centerx + 5, rect.centery - 3), eye_size)
                pygame.draw.circle(self.screen, BLACK,
                                 (rect.centerx - 5, rect.centery - 3), 1)
                pygame.draw.circle(self.screen, BLACK,
                                 (rect.centerx + 5, rect.centery - 3), 1)
            else:
                pygame.draw.rect(self.screen, WHITE, rect, 1)
                
    def draw_game(self):
        self.screen.blit(self.bg_surface, (0, 0))
        
        # Dessiner les obstacles
        for obstacle in self.obstacles:
            rect = pygame.Rect(obstacle.x * CELL_SIZE, obstacle.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            color = ORANGE if obstacle.moving else GRAY
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, WHITE, rect, 2)
            
        # Dessiner les nourritures avec animations
        for food in self.foods:
            color = food.get_color()
            
            # Effets spéciaux selon le type
            if food.type != FRUIT_NORMAL:
                brightness = abs(math.sin(pygame.time.get_ticks() * 0.01)) * 0.4 + 0.6
                color = tuple(int(c * brightness) for c in color)
                
                # Effet de pulsation
                size_mod = int(3 * math.sin(pygame.time.get_ticks() * 0.02))
                rect = pygame.Rect(food.pos[0] * CELL_SIZE - size_mod//2, 
                                 food.pos[1] * CELL_SIZE - size_mod//2,
                                 CELL_SIZE + size_mod, CELL_SIZE + size_mod)
            else:
                rect = pygame.Rect(food.pos[0] * CELL_SIZE, food.pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            
            pygame.draw.rect(self.screen, color, rect)
            
            # Icônes pour les power-ups
            if food.type == FRUIT_BONUS:
                pygame.draw.circle(self.screen, WHITE, rect.center, 3)
            elif food.type == FRUIT_SLOW:
                pygame.draw.polygon(self.screen, WHITE, [
                    (rect.centerx, rect.centery - 5),
                    (rect.centerx - 4, rect.centery + 3),
                    (rect.centerx + 4, rect.centery + 3)
                ])
            elif food.type == FRUIT_GHOST:
                pygame.draw.circle(self.screen, WHITE, rect.center, 6, 2)
                
        # Dessiner les snakes
        self.draw_snake(self.snake1)
        if self.multiplayer:
            self.draw_snake(self.snake2)
            
        # Dessiner les particules
        for particle in self.particles:
            particle.draw(self.screen)
            
        # Interface utilisateur
        self.draw_game_ui()
        
    def draw_game_ui(self):
        # Scores
        if self.multiplayer:
            score1_text = self.font.render(f"Joueur 1: {self.score1}", True, GREEN)
            score2_text = self.font.render(f"Joueur 2: {self.score2}", True, BLUE)
            self.screen.blit(score1_text, (10, 10))
            self.screen.blit(score2_text, (10, 50))
        else:
            score_text = self.font.render(f"Score: {self.score1}", True, WHITE)
            best_text = self.small_font.render(f"Meilleur: {self.best_score}", True, WHITE)
            self.screen.blit(score_text, (10, 10))
            self.screen.blit(best_text, (10, 50))
        
        # Niveau et temps
        level_text = self.small_font.render(f"Niveau: {self.level}", True, WHITE)
        elapsed = (pygame.time.get_ticks() - self.start_time) // 1000
        time_text = self.small_font.render(f"Temps: {elapsed}s", True, WHITE)
        self.screen.blit(level_text, (10, 75))
        self.screen.blit(time_text, (10, 100))
        
        # Indicateurs d'état
        y_offset = 130
        if self.sprinting1 or (self.multiplayer and self.sprinting2):
            sprint_text = self.small_font.render("SPRINT!", True, WHITE)
            self.screen.blit(sprint_text, (10, y_offset))
            y_offset += 25
            
        if self.slow_effect:
            slow_text = self.small_font.render("RALENTI", True, GOLD)
            self.screen.blit(slow_text, (10, y_offset))
            y_offset += 25
            
        if self.snake1.ghost_timer > 0 or (self.multiplayer and self.snake2.ghost_timer > 0):
            ghost_text = self.small_font.render("MODE FANTÔME", True, CYAN)
            self.screen.blit(ghost_text, (10, y_offset))
            y_offset += 25
        
        # Légende des power-ups
        legend_x = WIDTH - 220
        legend_texts = [
            ("Rouge: +1 pt", RED),
            ("Bleu: +5 pts", BLUE),
            ("Or: Ralentit", GOLD),
            ("Violet: Réduit", PURPLE),
            ("Cyan: Fantôme", CYAN),
            ("Orange: Vitesse", ORANGE)
        ]
        
        for i, (text, color) in enumerate(legend_texts):
            legend_text = self.small_font.render(text, True, color)
            self.screen.blit(legend_text, (legend_x, 10 + i * 25))
            
        # Mode de jeu
        mode_names = ["Classique", "Portails", "Obstacles"]
        mode_text = self.small_font.render(f"Mode: {mode_names[self.game_mode]}", True, WHITE)
        self.screen.blit(mode_text, (legend_x, 200))
        
        # Contrôles
        if self.multiplayer:
            controls = [
                "J1: Flèches + ESPACE",
                "J2: WASD + SHIFT"
            ]
            for i, control in enumerate(controls):
                control_text = self.small_font.render(control, True, WHITE)
                self.screen.blit(control_text, (legend_x, 230 + i * 20))
        
    def game_over(self):
        # Mettre à jour les statistiques
        self.games_played += 1
        elapsed = (pygame.time.get_ticks() - self.start_time) // 1000
        self.total_time += elapsed
        
        if self.score1 > self.best_score:
            self.best_score = self.score1
            
        self.save_game_data()
        
        if self.gameover_sound:
            self.gameover_sound.play()
            
        # Écran de game over
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Messages
        if self.multiplayer:
            if self.score1 > self.score2:
                winner_text = self.big_font.render("JOUEUR 1 GAGNE!", True, GREEN)
            elif self.score2 > self.score1:
                winner_text = self.big_font.render("JOUEUR 2 GAGNE!", True, BLUE)
            else:
                winner_text = self.big_font.render("ÉGALITÉ!", True, WHITE)
            winner_rect = winner_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 100))
            self.screen.blit(winner_text, winner_rect)
            
            score_text = self.font.render(f"J1: {self.score1} - J2: {self.score2}", True, WHITE)
        else:
            game_over_text = self.big_font.render("GAME OVER", True, WHITE)
            game_over_rect = game_over_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 100))
            self.screen.blit(game_over_text, game_over_rect)
            
            score_text = self.font.render(f"Score Final: {self.score1}", True, WHITE)
            
        score_rect = score_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
        self.screen.blit(score_text, score_rect)
        
        # Statistiques
        stats = [
            f"Niveau Atteint: {self.level}",
            f"Temps de Jeu: {elapsed}s",
            f"Meilleur Score: {self.best_score}",
            f"Parties Jouées: {self.games_played}"
        ]
        
        for i, stat in enumerate(stats):
            stat_text = self.small_font.render(stat, True, WHITE)
            stat_rect = stat_text.get_rect(center=(WIDTH//2, HEIGHT//2 + i * 30))
            self.screen.blit(stat_text, stat_rect)
            
        restart_text = self.small_font.render("ESPACE: Menu | ECHAP: Quitter", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 150))
        self.screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    return False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.in_menu = True
                    return True
                    
    def run(self):
        running = True
        while running:
            if self.in_menu:
                if not self.handle_menu_events():
                    break
                self.draw_menu()
            else:
                if not self.handle_game_events():
                    break
                    
                if not self.update_game():
                    if not self.game_over():
                        break
                    continue
                    
                self.draw_game()
                
                # Vitesse adaptative
                speed1 = self.get_current_speed(self.snake1, self.sprinting1)
                if self.multiplayer:
                    speed2 = self.get_current_speed(self.snake2, self.sprinting2)
                    speed = max(speed1, speed2)  # Vitesse du plus rapide
                else:
                    speed = speed1
                    
                self.clock.tick(speed)
            
            pygame.display.flip()
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()