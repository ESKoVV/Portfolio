import pygame
import sys
import random
import time
import os
import math
import sqlite3
import hashlib

# Инициализация Pygame
pygame.init()

# Константы
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
BLACK = (0, 0, 0)
DARK_GRAY = (20, 20, 30)
BLUE = (0, 100, 255)
CYAN = (0, 255, 255)
GREEN = (0, 255, 100)
RED = (255, 50, 50)
PURPLE = (180, 0, 255)
WHITE = (255, 255, 255)
GRAY = (100, 100, 120)

# Настройки уровней
LEVELS = [
    {"wins_required": 1, "losses_allowed": 0, "description": "ОДНА ПОБЕДА"},
    {"wins_required": 2, "losses_allowed": 0, "description": "ДВЕ ПОБЕДЫ ПОДРЯД"},
    {"wins_required": 3, "losses_allowed": 1, "description": "3 ПОБЕДЫ / 1 ПОРАЖЕНИЕ"},
    {"wins_required": 4, "losses_allowed": 1, "description": "4 ПОБЕДЫ / 1 ПОРАЖЕНИЕ"},
    {"wins_required": 5, "losses_allowed": 2, "description": "5 ПОБЕД / 2 ПОРАЖЕНИЯ"},
    {"wins_required": 3, "losses_allowed": 0, "description": "3 ПОБЕДЫ ПОДРЯД"},
    {"wins_required": 4, "losses_allowed": 0, "description": "4 ПОБЕДЫ ПОДРЯД"},
    {"wins_required": 5, "losses_allowed": 0, "description": "5 ПОБЕД ПОДРЯД"},
    {"wins_required": 6, "losses_allowed": 2, "description": "6 ПОБЕД / 2 ПОРАЖЕНИЯ"},
    {"wins_required": 7, "losses_allowed": 2, "description": "7 ПОБЕД / 2 ПОРАЖЕНИЯ"}
]

class Database:
    def __init__(self):
        self.db_name = "cyber_rps_game.db"
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица прогресса уровней
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                level INTEGER NOT NULL,
                unlocked BOOLEAN DEFAULT FALSE,
                best_score INTEGER DEFAULT 0,
                completed BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, level)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username, password):
        """Регистрация нового пользователя"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            password_hash = self.hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash)
            )
            user_id = cursor.lastrowid
            
            # Инициализация прогресса для всех уровней
            for level in range(10):
                unlocked = (level == 0)  # Только первый уровень разблокирован
                cursor.execute(
                    "INSERT INTO user_progress (user_id, level, unlocked) VALUES (?, ?, ?)",
                    (user_id, level, unlocked)
                )
            
            conn.commit()
            return True, "Регистрация успешна!"
        except sqlite3.IntegrityError:
            return False, "Пользователь уже существует!"
        finally:
            conn.close()
    
    def login_user(self, username, password):
        """Авторизация пользователя"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        cursor.execute(
            "SELECT id FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return True, result[0]  # user_id
        else:
            return False, "Неверный логин или пароль!"
    
    def get_user_progress(self, user_id):
        """Получение прогресса пользователя"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT level, unlocked, best_score, completed FROM user_progress WHERE user_id = ? ORDER BY level",
            (user_id,)
        )
        
        progress = cursor.fetchall()
        conn.close()
        
        return progress
    
    def unlock_level(self, user_id, level):
        """Разблокировка уровня"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE user_progress SET unlocked = TRUE WHERE user_id = ? AND level = ?",
            (user_id, level)
        )
        
        conn.commit()
        conn.close()
    
    def update_level_score(self, user_id, level, score, completed=False):
        """Обновление счета уровня"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE user_progress 
            SET best_score = ?, completed = ?
            WHERE user_id = ? AND level = ? AND (best_score < ? OR completed = FALSE)
        ''', (score, completed, user_id, level, score))
        
        conn.commit()
        conn.close()

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 4)
        self.speed = random.uniform(0.5, 2)
        self.angle = random.uniform(0, 2 * math.pi)
        self.life = random.uniform(30, 60)
        
    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        self.life -= 1
        self.size -= 0.1
        return self.life > 0 and self.size > 0
        
    def draw(self, screen):
        alpha = int(255 * (self.life / 60))
        color = (self.color[0], self.color[1], self.color[2], alpha)
        surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (self.size, self.size), self.size)
        screen.blit(surf, (int(self.x - self.size), int(self.y - self.size)))

class HiTechButton:
    def __init__(self, x, y, width, height, text, color=BLUE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = CYAN
        self.current_color = color
        self.hovered = False
        self.locked = False
        self.particles = []
        
    def draw(self, screen, font):
        if self.hovered:
            self.current_color = self.hover_color
        else:
            self.current_color = self.color
            
        pygame.draw.rect(screen, DARK_GRAY, self.rect, border_radius=8)
        pygame.draw.rect(screen, self.current_color, self.rect, 2, border_radius=8)
        
        if self.hovered:
            glow_rect = self.rect.inflate(10, 10)
            glow_surf = pygame.Surface(glow_rect.size, pygame.SRCALPHA)
            for i in range(5):
                alpha = 50 - i * 10
                pygame.draw.rect(glow_surf, (*self.current_color[:3], alpha), 
                               glow_surf.get_rect(), 2 + i, border_radius=12)
            screen.blit(glow_surf, glow_rect)
        
        text_surf = font.render(self.text, True, self.current_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
        if self.hovered and random.random() < 0.3:
            self.particles.append(Particle(
                random.randint(self.rect.left, self.rect.right),
                random.randint(self.rect.top, self.rect.bottom),
                self.current_color
            ))
        
        for particle in self.particles[:]:
            if not particle.update():
                self.particles.remove(particle)
            else:
                particle.draw(screen)
    
    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class TextInput:
    def __init__(self, x, y, width, height, placeholder="", is_password=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        self.is_password = is_password
        self.cursor_visible = True
        self.cursor_timer = 0
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if len(self.text) < 20:  # Максимальная длина
                    self.text += event.unicode
        return False
    
    def update(self):
        self.cursor_timer += 1
        if self.cursor_timer >= 30:  # Мерцание курсора каждые 0.5 секунды
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def draw(self, screen, font):
        color = CYAN if self.active else BLUE
        pygame.draw.rect(screen, DARK_GRAY, self.rect, border_radius=8)
        pygame.draw.rect(screen, color, self.rect, 2, border_radius=8)
        
        if self.text:
            display_text = "*" * len(self.text) if self.is_password else self.text
            text_surf = font.render(display_text, True, WHITE)
        else:
            text_surf = font.render(self.placeholder, True, GRAY)
        
        text_rect = text_surf.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
        screen.blit(text_surf, text_rect)
        
        # Курсор
        if self.active and self.cursor_visible:
            cursor_x = text_rect.right + 2
            pygame.draw.line(screen, WHITE, (cursor_x, self.rect.y + 10), 
                           (cursor_x, self.rect.y + self.rect.height - 10), 2)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("CYBER RPS - AI CHALLENGE")
        self.clock = pygame.time.Clock()
        
        # База данных
        self.db = Database()
        self.current_user_id = None
        self.user_progress = []
        
        # Шрифты
        self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
        self.main_font = pygame.font.SysFont('Arial', 20)
        self.small_font = pygame.font.SysFont('Arial', 16)
        
        # Загрузка изображений
        self.images = {}
        self.load_images()
        
        # Игровые переменные
        self.player_score = 0
        self.computer_score = 0
        self.current_level = 0
        self.level_wins = 0
        self.level_losses = 0
        self.player_choice = None
        self.computer_choice = None
        self.time_left = 5
        self.last_time = time.time()
        self.game_state = "auth"  # auth, level_select, playing, level_complete, game_over
        self.particles = []
        
        # Таймеры для задержек
        self.result_timer = 0
        self.show_result = False
        self.defeat_timer = 0
        
        # Поля ввода для авторизации
        self.login_input = TextInput(400, 300, 200, 40, "Логин")
        self.password_input = TextInput(400, 360, 200, 40, "Пароль", True)
        self.auth_buttons = [
            HiTechButton(400, 420, 200, 40, "ВОЙТИ", GREEN),
            HiTechButton(400, 480, 200, 40, "РЕГИСТРАЦИЯ", BLUE)
        ]
        self.auth_message = ""
        self.auth_message_color = GREEN
        
        # Создание кнопок выбора
        self.choice_buttons = [
            HiTechButton(150, 550, 200, 80, "КАМЕНЬ", BLUE),  # Перемещены ниже
            HiTechButton(400, 550, 200, 80, "НОЖНИЦЫ", GREEN),
            HiTechButton(650, 550, 200, 80, "БУМАГА", PURPLE)
        ]
        
        # Кнопки уровней
        self.level_buttons = []
        self.create_level_buttons()
        
        # Кнопка возврата к выбору уровня
        self.back_button = HiTechButton(50, 50, 120, 40, "УРОВНИ", CYAN)
        
        # Анимационные переменные
        self.pulse_value = 0
        self.grid_offset = 0
        
    def load_images(self):
        """Загрузка или создание изображений"""
        image_files = {
            "rock": "stone.png",
            "scissors": "nogh.png", 
            "paper": "pep.png",
            "question": "vopr.png"
        }
        
        for key, filename in image_files.items():
            try:
                if os.path.exists(filename):
                    img = pygame.image.load(filename)
                    self.images[key] = pygame.transform.scale(img, (120, 120))
                else:
                    self.create_fallback_image(key)
            except:
                self.create_fallback_image(key)
    
    def create_fallback_image(self, key):
        """Создание fallback изображений в hi-tech стиле"""
        surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        if key == "rock":
            color = BLUE
            points = [(60, 20), (100, 60), (60, 100), (20, 60)]
            pygame.draw.polygon(surf, color, points, 3)
        elif key == "scissors":
            color = GREEN
            pygame.draw.line(surf, color, (40, 30), (80, 90), 4)
            pygame.draw.line(surf, color, (80, 30), (40, 90), 4)
        elif key == "paper":
            color = PURPLE
            pygame.draw.rect(surf, color, (30, 30, 60, 60), 3)
        else:  # question
            color = CYAN
            pygame.draw.circle(surf, color, (60, 60), 40, 3)
            pygame.draw.circle(surf, color, (60, 40), 5, 0)
            pygame.draw.line(surf, color, (60, 50), (60, 80), 3)
        
        self.images[key] = surf
    
    def create_level_buttons(self):
        """Создание кнопок уровней"""
        for i in range(10):
            x = 200 + (i % 5) * 120
            y = 200 + (i // 5) * 100
            color = [BLUE, GREEN, PURPLE, CYAN, RED][i % 5]
            button = HiTechButton(x, y, 100, 60, f"LEVEL {i+1}", color)
            button.locked = True
            self.level_buttons.append(button)
    
    def update_level_buttons_from_db(self):
        """Обновление состояния кнопок уровней из БД"""
        if self.current_user_id:
            progress = self.db.get_user_progress(self.current_user_id)
            for i, (level, unlocked, best_score, completed) in enumerate(progress):
                if i < len(self.level_buttons):
                    self.level_buttons[i].locked = not unlocked
    
    def handle_auth_events(self, event):
        """Обработка событий авторизации"""
        if self.login_input.handle_event(event) or self.password_input.handle_event(event):
            self.attempt_login()
        
        mouse_pos = pygame.mouse.get_pos()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i, button in enumerate(self.auth_buttons):
                if button.is_clicked(mouse_pos, event):
                    if i == 0:  # Войти
                        self.attempt_login()
                    else:  # Регистрация
                        self.attempt_register()
    
    def attempt_login(self):
        """Попытка входа"""
        username = self.login_input.text
        password = self.password_input.text
        
        if not username or not password:
            self.auth_message = "Заполните все поля!"
            self.auth_message_color = RED
            return
        
        success, result = self.db.login_user(username, password)
        if success:
            self.current_user_id = result
            self.user_progress = self.db.get_user_progress(self.current_user_id)
            self.update_level_buttons_from_db()
            self.game_state = "level_select"
            self.auth_message = "Успешный вход!"
            self.auth_message_color = GREEN
        else:
            self.auth_message = result
            self.auth_message_color = RED
    
    def attempt_register(self):
        """Попытка регистрации"""
        username = self.login_input.text
        password = self.password_input.text
        
        if not username or not password:
            self.auth_message = "Заполните все поля!"
            self.auth_message_color = RED
            return
        
        success, message = self.db.register_user(username, password)
        self.auth_message = message
        self.auth_message_color = GREEN if success else RED
    
    def handle_events(self):
        """Обработка событий"""
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if self.game_state == "auth":
                self.handle_auth_events(event)
            else:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_state == "level_select":
                        for i, button in enumerate(self.level_buttons):
                            if button.is_clicked(mouse_pos, event) and not button.locked:
                                self.current_level = i
                                self.reset_level()
                                self.game_state = "playing"
                                break
                    
                    elif self.game_state == "playing" and not self.show_result:
                        for button in self.choice_buttons:
                            if button.is_clicked(mouse_pos, event):
                                choices = ["rock", "scissors", "paper"]
                                self.player_choice = choices[self.choice_buttons.index(button)]
                                self.computer_choice = random.choice(choices)
                                self.determine_winner()
                                self.time_left = max(3, 5 - self.current_level)
                                self.last_time = time.time()
                                
                                # Запускаем таймер для показа результата
                                self.result_timer = time.time()
                                self.show_result = True
                                
                                for _ in range(20):
                                    self.particles.append(Particle(
                                        mouse_pos[0], mouse_pos[1],
                                        button.color
                                    ))
                                break
                    
                    # Кнопка возврата к уровням
                    if self.back_button.is_clicked(mouse_pos, event) and self.game_state != "level_select":
                        self.game_state = "level_select"
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.game_state == "playing":
                            self.game_state = "level_select"
                        else:
                            return False
        
        # Обновление состояния hover для кнопок
        if self.game_state == "level_select":
            for button in self.level_buttons:
                button.check_hover(mouse_pos)
        elif self.game_state == "playing":
            for button in self.choice_buttons:
                button.check_hover(mouse_pos)
        
        if self.game_state == "auth":
            self.login_input.update()
            self.password_input.update()
            for button in self.auth_buttons:
                button.check_hover(mouse_pos)
        else:
            self.back_button.check_hover(mouse_pos)
        
        return True
    
    def update_timer(self):
        """Обновление таймера"""
        if self.show_result:
            # Проверяем, прошло ли 3 секунды для показа результата
            if time.time() - self.result_timer >= 3:
                self.show_result = False
                self.check_level_completion()
            return
        
        current_time = time.time()
        if current_time - self.last_time >= 1:
            self.time_left -= 1
            self.last_time = current_time
            
            if self.time_left <= 0:
                self.computer_choice = random.choice(["rock", "scissors", "paper"])
                self.level_losses += 1
                self.computer_score += 1
                self.time_left = max(3, 5 - self.current_level)
                self.last_time = time.time()
                self.result_timer = time.time()
                self.show_result = True
    
    def determine_winner(self):
        """Определение победителя раунда"""
        if self.player_choice == self.computer_choice:
            return
        
        wins = {
            "rock": "scissors",
            "scissors": "paper", 
            "paper": "rock"
        }
        
        if wins[self.player_choice] == self.computer_choice:
            self.level_wins += 1
            self.player_score += 1
        else:
            self.level_losses += 1
            self.computer_score += 1
    
    def check_level_completion(self):
        """Проверка завершения уровня"""
        level = LEVELS[self.current_level]
        
        if self.level_wins >= level["wins_required"]:
            self.game_state = "level_complete"
            # Сохраняем прогресс в БД
            if self.current_user_id:
                self.db.update_level_score(self.current_user_id, self.current_level, 
                                         self.player_score, True)
                # Разблокируем следующий уровень
                if self.current_level < 9:
                    self.db.unlock_level(self.current_user_id, self.current_level + 1)
                    self.update_level_buttons_from_db()
        elif self.level_losses > level["losses_allowed"]:
            self.game_state = "game_over"
            self.defeat_timer = time.time()
    
    def reset_level(self):
        """Сброс уровня"""
        self.level_wins = 0
        self.level_losses = 0
        self.player_choice = None
        self.computer_choice = None
        self.time_left = max(3, 5 - self.current_level)
        self.last_time = time.time()
        self.game_state = "playing"
        self.show_result = False
        self.result_timer = 0
    
    def draw_cyber_background(self):
        """Отрисовка hi-tech фона"""
        self.screen.fill(DARK_GRAY)
        
        self.grid_offset = (self.grid_offset + 0.5) % 40
        for x in range(0, SCREEN_WIDTH, 40):
            pygame.draw.line(self.screen, (30, 30, 40), 
                           (x + self.grid_offset, 0), (x + self.grid_offset, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(self.screen, (30, 30, 40), 
                           (0, y + self.grid_offset), (SCREEN_WIDTH, y + self.grid_offset), 1)
        
        self.pulse_value = (self.pulse_value + 0.05) % (2 * math.pi)
        pulse_alpha = int(100 + 50 * math.sin(self.pulse_value))
        
        pygame.draw.line(self.screen, (0, 100, 255, pulse_alpha), 
                        (0, 2), (SCREEN_WIDTH, 2), 3)
        pygame.draw.line(self.screen, (0, 100, 255, pulse_alpha), 
                        (0, SCREEN_HEIGHT-2), (SCREEN_WIDTH, SCREEN_HEIGHT-2), 3)
    
    def draw_auth_screen(self):
        """Отрисовка экрана авторизации"""
        self.draw_cyber_background()
        
        title = self.title_font.render("CYBER RPS - SYSTEM ACCESS", True, CYAN)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))
        
        # Поля ввода
        self.login_input.draw(self.screen, self.main_font)
        self.password_input.draw(self.screen, self.main_font)
        
        # Кнопки
        for button in self.auth_buttons:
            button.draw(self.screen, self.main_font)
        
        # Сообщение
        if self.auth_message:
            msg_surf = self.main_font.render(self.auth_message, True, self.auth_message_color)
            self.screen.blit(msg_surf, (SCREEN_WIDTH // 2 - msg_surf.get_width() // 2, 550))
    
    def draw_level_select(self):
        """Отрисовка экрана выбора уровня"""
        self.draw_cyber_background()
        
        title = self.title_font.render("CYBER RPS - SELECT MISSION", True, CYAN)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))
        
        for i, button in enumerate(self.level_buttons):
            if not button.locked:
                button.draw(self.screen, self.main_font)
            else:
                pygame.draw.rect(self.screen, (30, 30, 40), button.rect, border_radius=8)
                pygame.draw.rect(self.screen, GRAY, button.rect, 2, border_radius=8)
                lock_text = self.main_font.render("LOCKED", True, GRAY)
                self.screen.blit(lock_text, (button.rect.centerx - lock_text.get_width() // 2, 
                                           button.rect.centery - lock_text.get_height() // 2))
        
        instr = self.small_font.render("SELECT MISSION TO BEGIN CYBER CONFRONTATION", True, WHITE)
        self.screen.blit(instr, (SCREEN_WIDTH // 2 - instr.get_width() // 2, SCREEN_HEIGHT - 50))
    
    def draw_game(self):
        """Отрисовка игрового экрана"""
        self.draw_cyber_background()
        
        self.back_button.draw(self.screen, self.small_font)
        
        level_title = self.title_font.render(f"MISSION {self.current_level + 1}", True, CYAN)
        self.screen.blit(level_title, (SCREEN_WIDTH // 2 - level_title.get_width() // 2, 20))
        
        level_desc = self.main_font.render(LEVELS[self.current_level]["description"], True, GREEN)
        self.screen.blit(level_desc, (SCREEN_WIDTH // 2 - level_desc.get_width() // 2, 60))
        
        score_text = self.main_font.render(f"PLAYER: {self.player_score}  AI: {self.computer_score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH - 250, 20))
        
        progress_text = self.main_font.render(
            f"WINS: {self.level_wins}/{LEVELS[self.current_level]['wins_required']}  "
            f"LOSSES: {self.level_losses}/{LEVELS[self.current_level]['losses_allowed']}", 
            True, WHITE
        )
        self.screen.blit(progress_text, (SCREEN_WIDTH // 2 - progress_text.get_width() // 2, 90))
        
        # Таймер скрывается при показе результата
        if not self.show_result:
            timer_color = RED if self.time_left <= 3 else CYAN
            timer_scale = 1.0 + 0.2 * math.sin(self.pulse_value * 4) if self.time_left <= 3 else 1.0
            timer_font = pygame.font.SysFont('Arial', int(24 * timer_scale))
            timer_text = timer_font.render(f"TIME: {self.time_left}", True, timer_color)
            self.screen.blit(timer_text, (SCREEN_WIDTH // 2 - timer_text.get_width() // 2, 120))
        
        # Область противника
        enemy_text = self.main_font.render("AI SYSTEM", True, RED)
        self.screen.blit(enemy_text, (SCREEN_WIDTH // 2 - enemy_text.get_width() // 2, 170))
        
        pygame.draw.rect(self.screen, (30, 30, 40), (SCREEN_WIDTH // 2 - 80, 200, 160, 160), border_radius=15)
        pygame.draw.rect(self.screen, BLUE, (SCREEN_WIDTH // 2 - 80, 200, 160, 160), 2, border_radius=15)
        
        if self.computer_choice:
            computer_img = self.images[self.computer_choice]
        else:
            computer_img = self.images["question"]
        
        self.screen.blit(computer_img, (SCREEN_WIDTH // 2 - 60, 220))
        
        # Область игрока
        player_text = self.main_font.render("PLAYER", True, GREEN)
        self.screen.blit(player_text, (SCREEN_WIDTH // 2 - player_text.get_width() // 2, 400))
        
        if self.player_choice:
            player_img = self.images[self.player_choice]
            self.screen.blit(player_img, (SCREEN_WIDTH // 2 - 60, 430))
        
        # Кнопки выбора (скрываются при показе результата)
        if not self.show_result:
            for button in self.choice_buttons:
                button.draw(self.screen, self.main_font)
        
        for particle in self.particles[:]:
            if not particle.update():
                self.particles.remove(particle)
            else:
                particle.draw(self.screen)
    
    def draw_message(self, text, color):
        """Отрисовка сообщения"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        message_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 80, 400, 160)
        pygame.draw.rect(self.screen, DARK_GRAY, message_rect, border_radius=15)
        pygame.draw.rect(self.screen, color, message_rect, 3, border_radius=15)
        
        message_text = self.title_font.render(text, True, color)
        self.screen.blit(message_text, (message_rect.centerx - message_text.get_width() // 2, 
                                       message_rect.centery - 30))
        
        if self.game_state == "level_complete":
            continue_text = self.main_font.render("RETURNING TO MISSIONS...", True, CYAN)
            self.screen.blit(continue_text, (message_rect.centerx - continue_text.get_width() // 2, 
                                           message_rect.centery + 20))
        else:
            restart_text = self.main_font.render("RESTARTING MISSION...", True, CYAN)
            self.screen.blit(restart_text, (message_rect.centerx - restart_text.get_width() // 2, 
                                          message_rect.centery + 20))
    
    def draw(self):
        """Отрисовка игры"""
        if self.game_state == "auth":
            self.draw_auth_screen()
        elif self.game_state == "level_select":
            self.draw_level_select()
        else:
            self.draw_game()
            
            if self.game_state == "level_complete":
                self.draw_message("MISSION ACCOMPLISHED", GREEN)
                # Автоматический возврат через 2 секунды
                if time.time() - self.result_timer >= 2:
                    self.game_state = "level_select"
                    self.reset_level()
            elif self.game_state == "game_over":
                self.draw_message("SYSTEM FAILURE", RED)
                # Автоматический рестарт через 2 секунды
                if time.time() - self.defeat_timer >= 2:
                    self.reset_level()
        
        pygame.display.flip()
    
    def run(self):
        """Главный игровой цикл"""
        running = True
        while running:
            running = self.handle_events()
            
            if self.game_state == "playing":
                self.update_timer()
            
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
