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
    def __init__(self, image_url, width=None, height=None):
        self.target_width = width
        self.target_height = height
        self.width = width
        self.height = height
        self.image = None
        self.load_background(image_url)
        
    def load_background(self, url):
        """Carga la imagen de fondo desde GitHub y detecta sus dimensiones originales"""
        try:
            print(f"📥 Descargando escenario desde GitHub...")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            image_data = BytesIO(response.content)
            pil_image = Image.open(image_data)
            
            # Obtener dimensiones originales
            original_width, original_height = pil_image.size
            print(f"📐 Dimensiones originales de tu PNG: {original_width}x{original_height}")
            
            # Si no se especificaron dimensiones, usar las originales
            if self.target_width is None or self.target_height is None:
                self.width = original_width
                self.height = original_height
                print(f"✅ Usando dimensiones originales: {self.width}x{self.height}")
            else:
                self.width = self.target_width
                self.height = self.target_height
                print(f"📏 Escalando a: {self.width}x{self.height}")
            
            # Convertir a superficie de pygame
            image_string = pil_image.convert('RGBA').tobytes()
            self.image = pygame.image.fromstring(image_string, pil_image.size, 'RGBA')
            self.image = self.image.convert_alpha()
            
            # Escalar solo si es necesario
            if original_width != self.width or original_height != self.height:
                self.image = pygame.transform.scale(self.image, (self.width, self.height))
                print(f"🔄 Imagen escalada de {original_width}x{original_height} a {self.width}x{self.height}")
            
            print(f"✅ Escenario cargado exitosamente: {self.width}x{self.height}")
            
        except Exception as e:
            print(f"⚠️ Error cargando escenario: {e}")
            print("🎨 Creando fondo de respaldo...")
            self.create_fallback_background()
    
    def create_fallback_background(self):
        """Crea un fondo de respaldo visualmente atractivo"""
        # Si no hay dimensiones definidas, usar pantalla completa
        if self.width is None or self.height is None:
            self.width = 1920
            self.height = 1080
        
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
        self.screen_width = 1920
        self.screen_height = 1080
        
        # Forzar resolución específica 1920x1080 en pantalla completa
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        pygame.display.set_caption("🍎 Nivel 1 - Tierra de las Manzanas - COMBATE")
        
        # Verificar resolución real obtenida
        actual_size = self.screen.get_size()
        print(f"🖥️ Resolución solicitada: {self.screen_width}x{self.screen_height}")
        print(f"🖥️ Resolución real: {actual_size[0]}x{actual_size[1]}")
        
        # Actualizar dimensiones reales si son diferentes
        if actual_size != (self.screen_width, self.screen_height):
            self.screen_width, self.screen_height = actual_size
            print(f"⚠️ Resolución ajustada por el sistema: {self.screen_width}x{self.screen_height}")
        
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
        
        # URLs del escenario desde GitHub - Nivel 1 actualizado (nueva imagen 1920x1080)
        escenario_url = "https://github.com/user-attachments/assets/03339362-2bb5-4bf7-b4f5-b3ea4babbb92"
        
        # Cargar escenario con progreso
        self.loading_screen.update_progress("Escenario", "Descargando fondo del nivel...")
        self.loading_screen.draw()
        # Usar dimensiones automáticas basadas en la imagen original
        self.background = Background(escenario_url, None, None)
        
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
                # Solo cerrar si NO estamos en game over
                if not self.game_over and not self.victory:
                    return False
                # Si estamos en game over, no cerrar automáticamente
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Alternar entre pantalla completa y ventana
                    if self.screen.get_flags() & pygame.FULLSCREEN:
                        self.screen = pygame.display.set_mode((1000, 700))
                        self.screen_width = 1000
                        self.screen_height = 700
                    else:
                        self.screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
                        self.screen_width = 1920
                        self.screen_height = 1080
                elif event.key == pygame.K_TAB and self.switch_cooldown <= 0 and not self.game_over:
                    # Solo permitir cambio si ambos personajes están vivos y no hay game over
                    if self.juan.health > 0 and self.adan.health > 0:
                        if not self.juan_attack.is_character_attacking() and not self.adan_attack.is_character_attacking():
                            self.switch_character()
                            self.switch_cooldown = 10
                        else:
                            print("⚠️ No se puede cambiar de personaje durante un ataque")
                    else:
                        print("❌ No puedes cambiar de personaje cuando uno está derribado")
                elif event.key == pygame.K_SPACE and not self.game_over:
                    # Ataque básico del personaje actual (solo si no hay game over)
                    self.perform_basic_attack()
                elif event.key == pygame.K_x and not self.game_over:
                    # Ataque especial (solo si no hay game over)
                    self.perform_special_attack()
                elif event.key == pygame.K_r and (self.game_over or self.victory):
                    # Reiniciar juego
                    self.restart_game()
        
        # Manejar tecla E para revivir solo si el juego no ha terminado
        e_key_pressed = keys_pressed[pygame.K_e]  # Mover al inicio
        
        if not self.game_over:
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
        # Si hay game over o victoria, solo actualizar cooldowns básicos
        if self.game_over or self.victory:
            # Reducir cooldown de cambio
            if self.switch_cooldown > 0:
                self.switch_cooldown -= 1
            return
            
        keys_pressed = pygame.key.get_pressed()
        
        # Actualizar personaje activo solo si no está atacando
        if not self.active_attack_system.is_character_attacking():
            self.active_character.update(keys_pressed)
        
        # Actualizar IA del personaje inactivo (si está vivo o siendo revivido)
        if self.inactive_character.health > 0 or self.inactive_ai.is_being_revived:
            worms = self.worm_spawner.get_worms()
            self.inactive_ai.update(worms)
            
            # Actualizar animaciones del personaje IA basado en su estado
            ai_animation_state = self.inactive_ai.get_animation_state()
            self.inactive_character.update(keys_pressed=None, ai_controlled=True, ai_direction=ai_animation_state)
        else:
            # Si está muerto, actualizar con animación parada en dirección actual
            self.inactive_character.update(keys_pressed=None, ai_controlled=True, ai_direction=None)
        
        # Manejar ataques del personaje activo con tecla ESPACIO
        worms = self.worm_spawner.get_worms()
        self.active_attack_system.handle_attack_input(keys_pressed, worms)
        
        # NUEVO: Verificar si el personaje controlado por el jugador ha muerto
        if self.active_character.health <= 0:
            self.game_over = True
            print(f"💀 GAME OVER - {self.active_character.name} ha muerto")
        
        # Verificar condición de victoria
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
        # Personaje inactivo (usando sistema de animación normal para mostrar GIFs en movimiento)
        if self.inactive_character.health > 0:
            if not self.inactive_attack_system.is_character_attacking():
                # Usar el método draw normal del personaje para animaciones fluidas
                self.inactive_character.draw(self.screen, self.camera_x, self.camera_y)
        
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
        font = pygame.font.Font(None, 72)  # Escalado 2x para 1920x1080
        font_small = pygame.font.Font(None, 48)  # Escalado 2x para 1920x1080
        
        # Personaje activo - Escalado para 1920x1080
        active_text = font.render(f"🎮 Jugando: {self.active_character.name}", True, (255, 255, 255))
        self.screen.blit(active_text, (20, 20))  # Posiciones escaladas 2x
        
        # Estado del personaje inactivo
        if self.inactive_character.health > 0:
            if hasattr(self.inactive_ai, 'current_state'):
                ai_status = self.inactive_ai.current_state.replace('_', ' ').title()
                inactive_text = font_small.render(f"🤖 {self.inactive_character.name}: {ai_status}", True, (150, 255, 150))
                self.screen.blit(inactive_text, (20, 80))
        else:
            inactive_text = font_small.render(f"💀 {self.inactive_character.name}: Derribado", True, (255, 100, 100))
            self.screen.blit(inactive_text, (20, 80))
        
        # Vidas de los personajes
        juan_color = (0, 255, 0) if self.juan.health > 30 else (255, 255, 0) if self.juan.health > 0 else (255, 0, 0)
        juan_health_text = font_small.render(f"Juan: {self.juan.health}/100 HP", True, juan_color)
        self.screen.blit(juan_health_text, (20, 140))
        
        adan_color = (0, 255, 0) if self.adan.health > 30 else (255, 255, 0) if self.adan.health > 0 else (255, 0, 0)
        adan_health_text = font_small.render(f"Adán: {self.adan.health}/100 HP", True, adan_color)
        self.screen.blit(adan_health_text, (300, 140))
        
        # Progreso
        progress_text = font_small.render(f"Gusanos derrotados: {self.enemies_defeated}/{self.victory_condition}", True, (255, 255, 255))
        self.screen.blit(progress_text, (20, 190))
        
        # UI específica del personaje activo
        if self.active_character == self.juan:
            self.juan_attack.draw_ui(self.screen)
        
        # Controles - Escalados para pantalla completa
        instructions = [
            "🎮 Controles:",
            "WASD/Flechas - Mover",
            "ESPACIO - Ataque direccional",
            "X - Ataque especial",
            "TAB - Cambiar personaje",
            "E - Revivir compañero (cerca)",
            "ESC - Salir de pantalla completa"
        ]
        
        for i, instruction in enumerate(instructions):
            text_surface = font_small.render(instruction, True, (255, 255, 255))
            self.screen.blit(text_surface, (20, self.screen_height - 280 + i * 40))  # Escalado 2x
        
        # Estados especiales - Escalados para pantalla completa
        if self.game_over:
            # Fuente más grande para game over
            big_font = pygame.font.Font(None, 96)
            game_over_text = big_font.render("💀 GAME OVER - Presiona R para reintentar", True, (255, 0, 0))
            text_rect = game_over_text.get_rect(center=(self.screen_width//2, self.screen_height//2))
            
            # Fondo semi-transparente para el texto
            overlay = pygame.Surface((self.screen_width, self.screen_height))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            self.screen.blit(game_over_text, text_rect)
        
        elif self.victory:
            big_font = pygame.font.Font(None, 96)
            victory_text = big_font.render("🏆 ¡VICTORIA! - Presiona R para reiniciar", True, (0, 255, 0))
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
        self.screen.blit(debug_surface, (600, 140))  # Posición escalada
    
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
