import pygame
import sys
from PIL import Image
import requests
from io import BytesIO
import random
import math
import os

# Importar sistemas de ataque y enemigos
from adan_attacks import AdanAttack
from juan_attacks import JuanAttack
from worm_enemy import WormEnemy, WormSpawner

# Importar clases de personajes
from adan_character_animation import AdanCharacter
from juan_character_animation import JuanCharacter

# Importar intro cinematográfica
from intro_cinematica import IntroCinematica

# Importar sistema de IA
from character_ai import CharacterAI

# Importar sistema de audio
from audio_manager import get_audio_manager

# Importar sistema de pantalla de carga
from loading_screen import LoadingScreen

class Background:
    def __init__(self, image_url, width, height):
        self.width = width
        self.height = height
        self.image = None
        self.load_background(image_url)
        
    def load_background(self, url):
        """Carga la imagen de fondo desde caché local o crea un fondo de respaldo"""
        cache_file = "nivel1_escenario.cache"
        
        try:
            # Intentar cargar desde caché primero
            if os.path.exists(cache_file):
                print("📦 Cargando escenario desde caché...")
                with open(cache_file, 'rb') as f:
                    image_data = BytesIO(f.read())
                    pil_image = Image.open(image_data)
                    
                    # Convertir a superficie de pygame
                    image_data = pil_image.tobytes()
                    self.image = pygame.image.fromstring(image_data, pil_image.size, pil_image.mode)
                    
                    print(f"✅ Escenario cargado desde caché: {pil_image.size}")
                    return
            
            # Si no hay caché, mostrar mensaje y crear fondo de respaldo
            print("ℹ️ No se encontró caché del escenario, usando fondo generado")
            self.create_fallback_background()
            
        except Exception as e:
            print(f"⚠️ Error cargando escenario: {e}")
            print("🎨 Creando fondo de respaldo...")
            self.create_fallback_background()
    
    def create_fallback_background(self):
        """Crea un fondo de respaldo visualmente atractivo"""
        # Crear superficie base
        self.image = pygame.Surface((self.width, self.height))
        
        # Gradiente de cielo (azul claro a azul más oscuro)
        for y in range(self.height):
            color_ratio = y / self.height
            r = int(135 * (1 - color_ratio) + 70 * color_ratio)
            g = int(206 * (1 - color_ratio) + 130 * color_ratio)  
            b = int(235 * (1 - color_ratio) + 180 * color_ratio)
            pygame.draw.line(self.image, (r, g, b), (0, y), (self.width, y))
        
        # Agregar algunas "colinas" verdes en el fondo
        hill_points = [
            (0, self.height * 0.7),
            (self.width * 0.3, self.height * 0.6),
            (self.width * 0.7, self.height * 0.65),
            (self.width, self.height * 0.7),
            (self.width, self.height),
            (0, self.height)
        ]
        pygame.draw.polygon(self.image, (34, 139, 34), hill_points)  # Verde bosque
        
        # Agregar suelo
        ground_rect = pygame.Rect(0, self.height * 0.8, self.width, self.height * 0.2)
        pygame.draw.rect(self.image, (139, 69, 19), ground_rect)  # Marrón tierra
        
        print("✅ Fondo de respaldo creado exitosamente")
    
    def draw(self, screen, camera_x, camera_y, screen_width, screen_height):
        """Dibuja el fondo con desplazamiento de cámara"""
        if self.image:
            # Calcular posición del fondo
            bg_x = -camera_x % self.width
            bg_y = -camera_y % self.height
            
            # Dibujar múltiples copias del fondo para crear efecto infinito
            for x in range(-self.width, screen_width + self.width, self.width):
                for y in range(-self.height, screen_height + self.height, self.height):
                    screen.blit(self.image, (x + bg_x, y + bg_y))

class Game:
    def __init__(self, selected_character='juan'):
        pygame.init()
        self.screen_width = 1000
        self.screen_height = 700
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("🍎 Nivel 1 - Tierra de las Manzanas - COMBATE")
        
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Crear sistema de loading screen
        self.loading_screen = LoadingScreen(self.screen)
        
        # Lista de assets que se cargarán
        assets_to_load = [
            {"name": "Escenario", "description": "Fondo del nivel 1"},
            {"name": "Juan - Animaciones", "description": "Sprites de movimiento"},
            {"name": "Juan - Ataques", "description": "Animaciones de combate"},
            {"name": "Adan - Animaciones", "description": "Sprites de movimiento"},
            {"name": "Adan - Ataques", "description": "Animaciones de combate"},
            {"name": "Enemigos Worm", "description": "Sprites de gusanos"},
            {"name": "Sistema IA", "description": "Inteligencia artificial"},
            {"name": "Audio", "description": "Efectos de sonido"}
        ]
        
        # Iniciar pantalla de carga
        self.loading_screen.start_loading(assets_to_load)
        
        # Mostrar pantalla de carga inicial
        self.loading_screen.set_custom_message("Preparando el mundo...")
        self.loading_screen.draw()
        
        # URLs del escenario desde GitHub
        escenario_url = "https://github.com/user-attachments/assets/00593769-04d2-4083-a4dc-261e6a3fb3e6"
        
        # Cargar escenario con progreso
        self.loading_screen.update_progress("Escenario", "Descargando fondo del nivel...")
        self.loading_screen.draw()
        self.background = Background(escenario_url, 1536, 512)
        
        # Cargar personajes con progreso
        self.loading_screen.update_progress("Juan - Animaciones", "Cargando sprites de Juan...")
        self.loading_screen.draw()
        self.juan = JuanCharacter(400, 300)
        
        self.loading_screen.update_progress("Juan - Ataques", "Configurando ataques de Juan...")
        self.loading_screen.draw()
        # Configurar atributos de salud para Juan
        self.juan.max_health = 100
        self.juan.health = 100
        self.juan.speed = 4
        
        self.loading_screen.update_progress("Adan - Animaciones", "Cargando sprites de Adan...")
        self.loading_screen.draw()
        self.adan = AdanCharacter(500, 300)
        
        self.loading_screen.update_progress("Adan - Ataques", "Configurando ataques de Adan...")
        self.loading_screen.draw()
        # Configurar atributos de salud para Adan
        self.adan.max_health = 100
        self.adan.health = 100
        self.adan.speed = 4
        
        # Cargar sistemas de ataque con progreso
        self.loading_screen.update_progress("Juan - Ataques", "Inicializando sistema de combate Juan...")
        self.loading_screen.draw()
        self.juan_attack = JuanAttack(self.juan)
        
        self.loading_screen.update_progress("Adan - Ataques", "Inicializando sistema de combate Adan...")
        self.loading_screen.draw()
        self.adan_attack = AdanAttack(self.adan)
        
        # Asignar referencias de ataques a los personajes
        self.juan.attacks = self.juan_attack
        self.adan.attacks = self.adan_attack
        
        # Sistema de personajes activo/inactivo basado en selección de intro
        if selected_character == 'juan':
            self.active_character = self.juan
            self.inactive_character = self.adan
            self.active_attack_system = self.juan_attack
            self.inactive_attack_system = self.adan_attack
        else:
            self.active_character = self.adan
            self.inactive_character = self.juan
            self.active_attack_system = self.adan_attack
            self.inactive_attack_system = self.juan_attack
        
        # Cargar enemigos con progreso
        self.loading_screen.update_progress("Enemigos Worm", "Creando enemigos...")
        self.loading_screen.draw()
        
        # Inicializar sistema de IA para el personaje inactivo
        self.loading_screen.update_progress("Sistema IA", "Configurando inteligencia artificial...")
        self.loading_screen.draw()
        self.inactive_ai = CharacterAI(self.inactive_character, self.active_character)
        
        # Sistema de revival
        self.revival_key_pressed = False
        self.show_revival_prompt = False
        self.revival_distance = 80  # Distancia para poder revivir
        
        # Inicializar AudioManager con progreso
        self.loading_screen.update_progress("Audio", "Configurando sistema de audio...")
        self.loading_screen.draw()
        
        print(f"🎮 Personaje activo: {self.active_character.name}")
        print(f"🤖 IA controlando: {self.inactive_character.name}")
        
        # Sistema de audio
        self.audio = get_audio_manager()
        
        # Cámara
        self.camera_x = 0
        self.camera_y = 0
        
        # Control de alternancia
        self.switch_cooldown = 0
        
        # Sistema de enemigos con progreso
        self.loading_screen.update_progress("Sistema Enemigos", "Preparando generación de enemigos...")
        self.loading_screen.draw()
        self.worm_spawner = WormSpawner(max_worms=3)
        self.setup_enemy_spawns()
        
        # Finalizar carga
        self.loading_screen.update_progress("Completado", "¡Iniciando batalla!")
        self.loading_screen.draw()
        pygame.time.wait(1000)  # Mostrar mensaje final por 1 segundo
        
        # Estado del juego
        self.game_over = False
        self.victory = False
        self.enemies_defeated = 0
        self.victory_condition = 10  # Derrotar 10 gusanos para ganar
        
    def setup_enemy_spawns(self):
        """Configura las áreas donde pueden aparecer enemigos"""
        # Añadir varias áreas de spawn alejadas de los jugadores
        self.worm_spawner.add_spawn_area(100, 100, 200, 200)
        self.worm_spawner.add_spawn_area(800, 200, 200, 200)
        self.worm_spawner.add_spawn_area(300, 600, 200, 200)
        self.worm_spawner.add_spawn_area(700, 700, 200, 200)
        
    def handle_events(self):
        """Maneja todos los eventos del juego"""
        keys_pressed = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_TAB and self.switch_cooldown <= 0:
                    # Solo permitir cambio si ambos personajes están vivos
                    if self.juan.health > 0 and self.adan.health > 0:
                        if not self.juan_attack.is_character_attacking() and not self.adan_attack.is_character_attacking():
                            self.switch_character()
                            self.switch_cooldown = 10
                        else:
                            print("⚠️ No se puede cambiar de personaje durante un ataque")
                    else:
                        print("❌ No puedes cambiar de personaje cuando uno está derribado")
                elif event.key == pygame.K_SPACE:
                    # Ataque básico del personaje actual
                    self.perform_basic_attack()
                elif event.key == pygame.K_x:
                    # Ataque especial
                    self.perform_special_attack()
                elif event.key == pygame.K_r and (self.game_over or self.victory):
                    # Reiniciar juego
                    self.restart_game()
        
        # Manejar tecla E para revivir (verificar estado continuo)
        e_key_pressed = keys_pressed[pygame.K_e]
        
        # Verificar si se puede revivir al personaje inactivo
        if self.inactive_character.health <= 0 and not self.inactive_ai.is_being_revived:
            distance_to_inactive = self.distance_between_characters()
            
            if distance_to_inactive <= self.revival_distance:
                self.show_revival_prompt = True
                
                if e_key_pressed and not self.revival_key_pressed:
                    # Iniciar proceso de revivir
                    if self.inactive_ai.start_revival():
                        print(f"🔄 Comenzando a revivir a {self.inactive_character.name}...")
                        self.show_revival_prompt = False
            else:
                self.show_revival_prompt = False
        else:
            self.show_revival_prompt = False
        
        self.revival_key_pressed = e_key_pressed
        return True
    
    def switch_character(self):
        """Alterna entre personaje activo e inactivo"""
        # Intercambiar personajes
        self.active_character, self.inactive_character = self.inactive_character, self.active_character
        self.active_attack_system, self.inactive_attack_system = self.inactive_attack_system, self.active_attack_system
        
        # Recrear IA para el nuevo personaje inactivo
        self.inactive_ai = CharacterAI(self.inactive_character, self.active_character)
        
        print(f"🔄 Cambiado a: {self.active_character.name} (Activo)")
        print(f"🤖 IA controlando: {self.inactive_character.name}")
    
    def distance_between_characters(self):
        """Calcula la distancia entre los dos personajes"""
        dx = self.juan.x - self.adan.x
        dy = self.juan.y - self.adan.y
        return math.sqrt(dx*dx + dy*dy)
    
    def perform_basic_attack(self):
        """Realiza ataque básico del personaje actual"""
        if self.game_over or self.victory:
            return
        
        print(f"🎯 {self.active_character.name} iniciando ataque básico")
    
    def perform_special_attack(self):
        """Realiza ataque especial del personaje actual"""
        if self.game_over or self.victory:
            return
            
        worms = self.worm_spawner.get_worms()
        
        if self.current_character == self.juan:
            hit = self.juan_attack.special_attack(worms)
            if hit:
                for worm in worms:
                    if not worm.alive:
                        self.enemies_defeated += 1
        else:  # Adán
            # Ataque a distancia hacia el gusano más cercano
            if worms:
                nearest_worm = min(worms, key=lambda w: 
                    ((w.x - self.adan.x)**2 + (w.y - self.adan.y)**2)**0.5)
                hit = self.adan_attack.ranged_attack(nearest_worm.x + 32, nearest_worm.y + 32)
    
    def update(self):
        """Actualiza la lógica del juego"""
        if self.game_over or self.victory:
            return
            
        keys_pressed = pygame.key.get_pressed()
        
        # Actualizar personaje activo solo si no está atacando
        if not self.active_attack_system.is_character_attacking():
            self.active_character.update(keys_pressed)
        
        # Actualizar IA del personaje inactivo (si está vivo o siendo revivido)
        if self.inactive_character.health > 0 or self.inactive_ai.is_being_revived:
            worms = self.worm_spawner.get_worms()
            self.inactive_ai.update(worms)
        
        # Manejar ataques del personaje activo con tecla ESPACIO
        worms = self.worm_spawner.get_worms()
        self.active_attack_system.handle_attack_input(keys_pressed, worms)
        
        # Verificar si ambos personajes murieron
        if self.juan.health <= 0 and self.adan.health <= 0 and not self.inactive_ai.is_being_revived:
            self.game_over = True
            print("💀 GAME OVER - Ambos personajes han muerto")
        
        # Contar enemigos derrotados después de que los ataques se procesen
        # Contar enemigos derrotados después de que los ataques se procesen
        current_worm_count = len(self.worm_spawner.get_worms())
        total_worms_created = len(self.worm_spawner.worms)  # Incluye vivos y muertos
        self.enemies_defeated = total_worms_created - current_worm_count
        
        # Verificar condición de victoria
        if self.enemies_defeated >= self.victory_condition:
            self.victory = True
            print("🏆 ¡VICTORIA! Has derrotado a todos los gusanos")
        
        # Actualizar cámara para seguir al personaje activo
        target_camera_x = self.active_character.x - self.screen_width // 2
        target_camera_y = self.active_character.y - self.screen_height // 2
        
        # Suavizar movimiento de cámara
        self.camera_x += (target_camera_x - self.camera_x) * 0.1
        self.camera_y += (target_camera_y - self.camera_y) * 0.1
        
        # Actualizar sistemas de ataque
        worms = self.worm_spawner.get_worms()
        self.juan_attack.update(worms)
        self.adan_attack.update(worms)
        
        # Actualizar enemigos
        players = [self.juan, self.adan]
        self.worm_spawner.update(players)
        
        # Verificar ataques de gusanos a jugadores
        for worm in self.worm_spawner.get_worms():
            if worm.state == "attack":
                # Verificar si puede atacar a algún jugador
                for player in players:
                    distance = ((worm.x - player.x)**2 + (worm.y - player.y)**2)**0.5
                    if distance <= worm.attack_range:
                        current_time = pygame.time.get_ticks()
                        if current_time - worm.last_attack_time >= worm.attack_cooldown:
                            player.take_damage(worm.attack_damage)
                            worm.last_attack_time = current_time
        
        # Reducir cooldown de cambio
        if self.switch_cooldown > 0:
            self.switch_cooldown -= 1
    
    def restart_game(self):
        """Reinicia el juego"""
        # Reiniciar personajes
        self.juan.health = self.juan.max_health
        self.adan.health = self.adan.max_health
        self.juan.x, self.juan.y = 400, 300
        self.adan.x, self.adan.y = 500, 300
        
        # Reiniciar enemigos
        self.worm_spawner.worms.clear()
        
        # Reiniciar estado
        self.game_over = False
        self.victory = False
        self.enemies_defeated = 0
        
        print("🔄 Juego reiniciado")
    
    def draw(self):
        """Dibuja todo en la pantalla"""
        # Limpiar pantalla
        self.screen.fill((50, 100, 50))
        
        # Dibujar fondo con scroll
        self.background.draw(self.screen, self.camera_x, self.camera_y, self.screen_width, self.screen_height)
        
        # Dibujar ambos personajes si están vivos y no atacando
        # Personaje inactivo (con transparencia si está vivo)
        if self.inactive_character.health > 0:
            if not self.inactive_attack_system.is_character_attacking():
                inactive_surface = pygame.Surface((64, 64))
                inactive_surface.set_alpha(150)
                if hasattr(self.inactive_character, 'current_direction') and self.inactive_character.current_direction in self.inactive_character.animations:
                    frames = self.inactive_character.animations[self.inactive_character.current_direction]
                    if frames:
                        frame = frames[0]
                        inactive_surface.blit(frame, (0, 0))
                        self.screen.blit(inactive_surface, (self.inactive_character.x - self.camera_x, self.inactive_character.y - self.camera_y))
        
        # Personaje activo (normal)
        if not self.active_attack_system.is_character_attacking():
            self.active_character.draw(self.screen, self.camera_x, self.camera_y)
        
        # Dibujar barras de vida para ambos personajes
        self.draw_health_bars()
        
        # Dibujar mensaje de revival si está cerca del personaje derribado
        if self.show_revival_prompt:
            self.draw_revival_prompt()
        
        # Si un personaje está siendo revivido, mostrar barra de progreso
        if self.inactive_ai.is_being_revived:
            self.draw_revival_progress()
        
        # Dibujar enemigos
        self.worm_spawner.draw(self.screen, self.camera_x, self.camera_y)
        
        # Dibujar efectos de ataque
        self.juan_attack.draw(self.screen, self.camera_x, self.camera_y)
        self.adan_attack.draw(self.screen, self.camera_x, self.camera_y)
        
        # UI e información
        self.draw_ui()
        
        pygame.display.flip()
    
    def draw_health_bars(self):
        """Dibuja las barras de salud de ambos personajes"""
        for character in [self.juan, self.adan]:
            if hasattr(character, 'max_health') and character.max_health > 0:
                health_ratio = max(0, character.health / character.max_health)
                bar_width = 60
                bar_height = 8
                
                x = character.x - self.camera_x - bar_width // 2
                y = character.y - self.camera_y - 40
                
                # Fondo de la barra
                pygame.draw.rect(self.screen, (80, 80, 80), (x, y, bar_width, bar_height))
                
                # Color según porcentaje de vida
                if health_ratio > 0.7:
                    color = (0, 255, 0)  # Verde
                elif health_ratio > 0.3:
                    color = (255, 255, 0)  # Amarillo
                else:
                    color = (255, 0, 0)  # Rojo
                    
                # Barra de vida
                if character.health > 0:
                    pygame.draw.rect(self.screen, color, (x, y, int(bar_width * health_ratio), bar_height))
                
                # Si está derribado, mostrar texto
                if character.health <= 0:
                    font = pygame.font.Font(None, 24)
                    text = "¡Derribado!"
                    text_surf = font.render(text, True, (255, 100, 100))
                    text_rect = text_surf.get_rect(center=(x + bar_width // 2, y - 15))
                    self.screen.blit(text_surf, text_rect)
    
    def draw_revival_prompt(self):
        """Dibuja el mensaje de revival"""
        prompt_font = pygame.font.Font(None, 36)
        prompt_text = f"Presiona E para revivir a {self.inactive_character.name}"
        prompt_surface = prompt_font.render(prompt_text, True, (255, 255, 100))
        
        # Fondo semi-transparente
        bg_surface = pygame.Surface((prompt_surface.get_width() + 20, prompt_surface.get_height() + 10))
        bg_surface.set_alpha(180)
        bg_surface.fill((0, 0, 0))
        
        prompt_rect = prompt_surface.get_rect(center=(self.screen_width//2, 100))
        bg_rect = bg_surface.get_rect(center=(self.screen_width//2, 100))
        
        self.screen.blit(bg_surface, bg_rect)
        self.screen.blit(prompt_surface, prompt_rect)
    
    def draw_revival_progress(self):
        """Dibuja la barra de progreso de revival"""
        progress = self.inactive_ai.revival_timer / self.inactive_ai.revival_time
        
        # Posición sobre el personaje inactivo
        bar_width = 80
        bar_height = 12
        x = self.inactive_character.x - self.camera_x - bar_width // 2
        y = self.inactive_character.y - self.camera_y - 60
        
        # Fondo de la barra
        pygame.draw.rect(self.screen, (80, 80, 80), (x, y, bar_width, bar_height))
        # Borde
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, bar_width, bar_height), 2)
        # Progreso
        pygame.draw.rect(self.screen, (0, 255, 100), (x + 2, y + 2, int((bar_width - 4) * progress), bar_height - 4))
        
        # Texto de reviviendo
        revival_font = pygame.font.Font(None, 24)
        revival_text = f"Reviviendo... {int(progress * 100)}%"
        revival_surface = revival_font.render(revival_text, True, (255, 255, 255))
        revival_rect = revival_surface.get_rect(center=(x + bar_width // 2, y - 20))
        self.screen.blit(revival_surface, revival_rect)
        
        # UI e información
        self.draw_ui()
        
        pygame.display.flip()
    
    def draw_ui(self):
        """Dibuja la interfaz de usuario"""
        font = pygame.font.Font(None, 36)
        font_small = pygame.font.Font(None, 24)
        
        # Personaje activo
        active_text = font.render(f"🎮 Jugando: {self.active_character.name}", True, (255, 255, 255))
        self.screen.blit(active_text, (10, 10))
        
        # Estado del personaje inactivo
        if self.inactive_character.health > 0:
            if hasattr(self.inactive_ai, 'current_state'):
                ai_status = self.inactive_ai.current_state.replace('_', ' ').title()
                inactive_text = font_small.render(f"🤖 {self.inactive_character.name}: {ai_status}", True, (150, 255, 150))
                self.screen.blit(inactive_text, (10, 40))
        else:
            inactive_text = font_small.render(f"💀 {self.inactive_character.name}: Derribado", True, (255, 100, 100))
            self.screen.blit(inactive_text, (10, 40))
        
        # Vidas de los personajes
        juan_color = (0, 255, 0) if self.juan.health > 30 else (255, 255, 0) if self.juan.health > 0 else (255, 0, 0)
        juan_health_text = font_small.render(f"Juan: {self.juan.health}/100 HP", True, juan_color)
        self.screen.blit(juan_health_text, (10, 70))
        
        adan_color = (0, 255, 0) if self.adan.health > 30 else (255, 255, 0) if self.adan.health > 0 else (255, 0, 0)
        adan_health_text = font_small.render(f"Adán: {self.adan.health}/100 HP", True, adan_color)
        self.screen.blit(adan_health_text, (150, 70))
        
        # Progreso
        progress_text = font_small.render(f"Gusanos derrotados: {self.enemies_defeated}/{self.victory_condition}", True, (255, 255, 255))
        self.screen.blit(progress_text, (10, 95))
        
        # UI específica del personaje activo
        if self.active_character == self.juan:
            self.juan_attack.draw_ui(self.screen)
        
        # Controles
        instructions = [
            "🎮 Controles:",
            "WASD/Flechas - Mover",
            "ESPACIO - Ataque direccional",
            "X - Ataque especial",
            "TAB - Cambiar personaje",
            "E - Revivir compañero (cerca)",
            "ESC - Salir"
        ]
        
        for i, instruction in enumerate(instructions):
            text_surface = font_small.render(instruction, True, (255, 255, 255))
            self.screen.blit(text_surface, (10, self.screen_height - 140 + i * 20))
        
        # Estados especiales
        if self.game_over:
            game_over_text = font.render("💀 GAME OVER - Presiona R para reiniciar", True, (255, 0, 0))
            text_rect = game_over_text.get_rect(center=(self.screen_width//2, self.screen_height//2))
            self.screen.blit(game_over_text, text_rect)
        
        elif self.victory:
            victory_text = font.render("🏆 ¡VICTORIA! - Presiona R para reiniciar", True, (0, 255, 0))
            text_rect = victory_text.get_rect(center=(self.screen_width//2, self.screen_height//2))
            self.screen.blit(victory_text, text_rect)
        
        # Información de debug
        juan_status = "🗡️" if self.juan_attack.is_character_attacking() else ("�" if self.juan.health <= 0 else "�🔵")
        adan_status = "🔥" if self.adan_attack.is_character_attacking() else ("💀" if self.adan.health <= 0 else "🔴")
        
        # Información de IA
        ai_info = ""
        if hasattr(self.inactive_ai, 'current_state'):
            ai_info = f" | IA: {self.inactive_ai.current_state}"
        
        debug_text = f"Gusanos: {len(self.worm_spawner.get_worms())} | Juan: {juan_status} | Adán: {adan_status}{ai_info}"
        debug_surface = font_small.render(debug_text, True, (200, 200, 200))
        self.screen.blit(debug_surface, (300, 70))
    
    def run(self):
        """Bucle principal del juego"""
        print("🚀 Iniciando Nivel 1 - Tierra de las Manzanas (COMBATE)...")
        print("⏳ Cargando recursos...")
        
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps)
        
        print("👋 ¡Gracias por jugar!")
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    # Verificar dependencias
    try:
        import pygame
        import PIL
        import requests
        print("✅ Todas las dependencias están instaladas")
    except ImportError as e:
        print(f"❌ Falta instalar: {e}")
        print("Instala con: pip install pygame pillow requests")
        sys.exit(1)
    
    # Ejecutar intro cinematográfica
    print("🎬 Iniciando La Tierra de las Manzanas...")
    intro = IntroCinematica()
    result = intro.run()
    
    # Procesar resultado de la intro
    if result == 'quit':
        print("👋 ¡Hasta luego!")
        pygame.quit()
        sys.exit()
    elif result == 'creditos':
        print("📜 Créditos (próximamente)")
        pygame.quit()
        sys.exit()
    elif result.startswith('start_game_'):
        # Extraer personaje seleccionado
        selected_character = result.split('_')[-1]
        print(f"🎮 Iniciando juego con {selected_character.upper()}")
        
        # Cerrar ventana de intro y crear juego
        pygame.quit()
        
        # Crear y ejecutar el juego con el personaje seleccionado
        game = Game(selected_character)
        game.run()
    else:
        pygame.quit()
        sys.exit()
