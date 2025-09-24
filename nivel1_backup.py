import pygame
import sys
from PIL import Image
import requests
from io import BytesIO
import random
import math
import os

# Importaciones ordenadas
from adan_attacks import AdanAttack
from adan_character_animation import AdanCharacter
from audio_manager import get_audio_manager
from character_ai import CharacterAI
from chaman_malvado import ChamanMalvado
from intro_cinematica import IntroCinematica
from juan_attacks import JuanAttack
from juan_character_animation import JuanCharacter
from loading_screen import LoadingScreen
from worm_enemy import WormEnemy, WormSpawner

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
        """Dibuja el fondo estático (sin duplicar)"""
        if self.image:
            # Calcular posición para centrar la cámara sin duplicar
            draw_x = -camera_x
            draw_y = -camera_y
            
            # Limitar para no mostrar fuera de los bordes del PNG
            if draw_x > 0:
                draw_x = 0
            elif draw_x < screen_width - self.width:
                draw_x = screen_width - self.width
            
            if draw_y > 0:
                draw_y = 0
            elif draw_y < screen_height - self.height:
                draw_y = screen_height - self.height
            
            # Dibujar la imagen de fondo una sola vez
            screen.blit(self.image, (draw_x, draw_y))

class Game:
    def __init__(self, selected_character='juan'):
        print("🔍 DEBUG: Iniciando constructor de Game...")
        pygame.init()
        self.screen_width = 1920
        self.screen_height = 1080
        print("🔍 DEBUG: Pygame y dimensiones inicializadas...")
        
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
        
        # Inicializar estado del juego temprano para evitar errores
        self.game_over = False
        self.victory = False
        self.enemies_defeated = 0
        self.victory_condition = 15  # Derrotar 15 gusanos para ganar
        
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
        
        # URL del escenario original desde GitHub (optimizado)
        escenario_url = "https://github.com/user-attachments/assets/03339362-2bb5-4bf7-b4f5-b3ea4babbb92"
        
        # Cargar escenario optimizado con progreso
        self.loading_screen.update_progress("Escenario", "Cargando fondo desde GitHub...")
        self.loading_screen.draw()
        
        # Usar carga optimizada con las dimensiones originales
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
        
        print("🔍 DEBUG: Constructor continuando normalmente...")
    
    def load_collectible_images(self):
        """Carga imágenes optimizadas desde GitHub"""
        try:
            # URLs originales de GitHub
            apple_url = "https://github.com/user-attachments/assets/8d98de91-3834-456d-8dac-484029df9a02"
            potion_url = "https://github.com/user-attachments/assets/5365c2ea-ad1e-4055-8d3b-de1547e10396"
            
            # Headers para mejor compatibilidad con GitHub
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'image/png,image/jpeg,image/*,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive'
            }
            
            # Cargar manzana con mejores parámetros
            print("📥 Cargando manzana desde GitHub...")
            response = requests.get(apple_url, headers=headers, timeout=5, stream=True)
            response.raise_for_status()
            
            apple_content = BytesIO()
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    apple_content.write(chunk)
            apple_content.seek(0)
            
            apple_pil = Image.open(apple_content).convert("RGBA")
            apple_pygame_data = apple_pil.tobytes()
            self.apple_image = pygame.image.fromstring(apple_pygame_data, apple_pil.size, "RGBA")
            self.apple_image = pygame.transform.scale(self.apple_image, (32, 32))
            print("✅ Manzana descargada de GitHub")
            
            # Cargar poción con mejores parámetros
            print("📥 Cargando poción desde GitHub...")
            response = requests.get(potion_url, headers=headers, timeout=5, stream=True)
            response.raise_for_status()
            
            potion_content = BytesIO()
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    potion_content.write(chunk)
            potion_content.seek(0)
            
            potion_pil = Image.open(potion_content).convert("RGBA")
            potion_pygame_data = potion_pil.tobytes()
            self.potion_image = pygame.image.fromstring(potion_pygame_data, potion_pil.size, "RGBA")
            self.potion_image = pygame.transform.scale(self.potion_image, (32, 32))
            print("✅ Poción descargada de GitHub")
            
            print("✅ Todas las imágenes de GitHub cargadas correctamente")
            
        except requests.exceptions.RequestException as e:
            print(f"🌐 Error de conexión con GitHub: {e}")
            self.create_placeholder_images()
        except Exception as e:
            print(f"❌ Error procesando imágenes: {e}")
            self.create_placeholder_images()
    
    def create_placeholder_images(self):
        """Crea placeholders mejorados si falla GitHub"""
        print("🎨 Creando placeholders visuales...")
        # Placeholder de manzana con mejor diseño
        self.apple_image = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(self.apple_image, (220, 20, 20), (16, 18), 12)
        pygame.draw.ellipse(self.apple_image, (255, 50, 50), (10, 12, 12, 12))
        pygame.draw.rect(self.apple_image, (139, 69, 19), (15, 6, 2, 8))
        
        # Placeholder de poción con mejor diseño  
        self.potion_image = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.ellipse(self.potion_image, (20, 100, 220), (10, 18, 12, 10))
        pygame.draw.rect(self.potion_image, (50, 150, 255), (14, 10, 4, 12))
        pygame.draw.circle(self.potion_image, (100, 200, 255), (16, 22), 4)
        
        # Sistema de audio
        self.audio = get_audio_manager()
        
        # Cámara
        self.camera_x = 0
        self.camera_y = 0
        
        # Control de alternancia
        self.switch_cooldown = 0
        
        # Sistema de enemigos ya inicializado arriba
        self.loading_screen.update_progress("Sistema Enemigos", "Sistema de enemigos listo...")
        self.loading_screen.draw()
        
        # Finalizar carga
        self.loading_screen.update_progress("Completado", "¡Iniciando batalla!")
        self.loading_screen.draw()
        pygame.time.wait(1000)  # Mostrar mensaje final por 1 segundo
        
        print("🔍 DEBUG: Llegando a inicialización de estado del juego...")
        
        # Estado del juego
        self.game_over = False
        self.victory = False
        self.enemies_defeated = 0
        self.victory_condition = 15  # Derrotar 15 gusanos para ganar
        
        print("🔍 DEBUG: Estado del juego inicializado...")
        
        # IMPORTANTE: Inicializar worm_spawner PRIMERO antes que otros recursos
        print("🐛 Inicializando WormSpawner (movido al inicio)...")
        self.worm_spawner = WormSpawner(max_worms=15)  # Aumentado a 15 gusanos
        print("✅ WormSpawner inicializado correctamente")
        self.setup_enemy_spawns()
        print("✅ Areas de spawn configuradas")
        
        # Sistema de coleccionables
        self.dropped_items = []
        self.apple_image = None
        self.potion_image = None
        self.load_collectible_images()
        
        # Sistema de mejoras
        self.upgrades = {
            'speed': 0,
            'damage': 0,
            'attack_speed': 0,
            'health': 0
        }
        
        # Sistema de escudo para pociones
        self.shield_active = False
        self.shield_timer = 0
        self.shield_duration = 15 * 60  # 15 segundos a 60 FPS
        
        # Variables para menú de mejoras
        self.show_upgrade_menu = False
        self.upgrade_menu_timer = 0
    
    def setup_enemy_spawns(self):
        """Configura las áreas donde pueden aparecer enemigos"""
        # Añadir más áreas de spawn para 15 gusanos
        self.worm_spawner.add_spawn_area(100, 100, 200, 200)
        self.worm_spawner.add_spawn_area(800, 200, 200, 200)
        self.worm_spawner.add_spawn_area(300, 600, 200, 200)
        self.worm_spawner.add_spawn_area(700, 700, 200, 200)
        self.worm_spawner.add_spawn_area(1200, 300, 200, 200)
        self.worm_spawner.add_spawn_area(200, 900, 200, 200)
        
        print("🔍 DEBUG: Constructor completado exitosamente!")
        
        # CRÍTICO: Verificar que worm_spawner existe
        if hasattr(self, 'worm_spawner'):
            print("✅ VERIFICADO: worm_spawner existe")
        else:
            print("🚨 CRÍTICO: worm_spawner NO existe - creando fallback")
            self.worm_spawner = WormSpawner(max_worms=15)
        
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
                # Manejo del menú de mejoras
                elif self.show_upgrade_menu and event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                    self.handle_upgrade_selection(event.key)
                    self.show_upgrade_menu = False
                # Manejo del menú de mejoras
                elif self.show_upgrade_menu and event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                    self.handle_upgrade_selection(event.key)
                    self.show_upgrade_menu = False
        
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
        
        if self.active_character == self.juan:
            hit = self.juan_attack.special_attack(worms)
            if hit:
                for enemy in worms:
                    if hasattr(enemy, 'alive') and not enemy.alive:
                        self.enemies_defeated += 1
                    elif hasattr(enemy, 'health') and enemy.health <= 0:
                        self.enemies_defeated += 1
        else:  # Adán
            # Ataque a distancia hacia el gusano más cercano
            if worms:
                target = min(worms, key=lambda w: 
                    ((w.x - self.adan.x)**2 + (w.y - self.adan.y)**2)**0.5)
                hit = self.adan_attack.ranged_attack(target.x + 32, target.y + 32)
                print(f"🏹 Adán dispara proyectil hacia gusano")
    
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
            self.enforce_boundaries(self.active_character)
        
        # Actualizar IA del personaje inactivo (si está vivo o siendo revivido)
        if self.inactive_character.health > 0 or self.inactive_ai.is_being_revived:
            worms = self.worm_spawner.get_worms()
            self.inactive_ai.detection_range = 300  # Mejorar rango de detección
            self.inactive_ai.update(worms)
            
            # Actualizar animaciones del personaje IA basado en su estado
            ai_animation_state = self.inactive_ai.get_animation_state()
            self.inactive_character.update(keys_pressed=None, ai_controlled=True, ai_direction=ai_animation_state)
            self.enforce_boundaries(self.inactive_character)
        else:
            # Si está muerto, actualizar con animación parada en dirección actual
            self.inactive_character.update(keys_pressed=None, ai_controlled=True, ai_direction=None)
        
        # Procesar drops de gusanos muertos
        self.process_worm_drops()
        
        # Actualizar coleccionables
        self.update_collectibles()
        
        # Actualizar sistema de escudo
        self.update_shield_system()
        
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
        
        # Limitar cámara a los bordes del escenario
        min_camera_x = 0
        max_camera_x = max(0, self.background.width - self.screen_width)
        min_camera_y = 0
        max_camera_y = max(0, self.background.height - self.screen_height)
        
        self.camera_x = max(min_camera_x, min(self.camera_x, max_camera_x))
        self.camera_y = max(min_camera_y, min(self.camera_y, max_camera_y))
        
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
        
        # Reducir cooldowns
        if self.switch_cooldown > 0:
            self.switch_cooldown -= 1
            
        if self.upgrade_menu_timer > 0:
            self.upgrade_menu_timer -= 1
            if self.upgrade_menu_timer <= 0:
                self.show_upgrade_menu = False
    
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
    
    def collect_apple(self):
        """Recolectar manzana y mostrar menú de mejoras"""
        print("🍎 ¡Manzana recogida! Selecciona una mejora:")
        print("1 - Velocidad | 2 - Daño | 3 - Vel. Ataque | 4 - Vida Máxima")
        self.show_upgrade_menu = True
        self.upgrade_menu_timer = 300  # 5 segundos a 60 FPS
    
    def collect_potion(self, character):
        """Recolectar poción y activar escudo"""
        print(f"🧪 ¡{character.name} consumió poción de escudo!")
        character.shield_active = True
        character.shield_timer = 0
        character.shield_duration = self.shield_duration
        print(f"🛡️ Escudo activado para {character.name} (15 segundos)")
    
    def handle_upgrade_selection(self, key):
        """Maneja la selección de mejora con manzanas"""
        character = self.active_character
        
        if key == pygame.K_1:  # Velocidad
            character.speed += 0.5
            self.upgrades['speed'] += 1
            print(f"🚀 Velocidad de {character.name} mejorada: {character.speed:.1f}")
            
        elif key == pygame.K_2:  # Daño
            # Aumentar daño según el sistema de ataque
            if hasattr(self.active_attack_system, 'melee_damage'):
                original_damage = getattr(self.active_attack_system, 'melee_damage', 40)
                self.active_attack_system.melee_damage = original_damage + 5
            if hasattr(self.active_attack_system, 'projectile_damage'):
                original_damage = getattr(self.active_attack_system, 'projectile_damage', 25)
                self.active_attack_system.projectile_damage = original_damage + 3
            self.upgrades['damage'] += 1
            print(f"⚔️ Daño de {character.name} mejorado (nivel {self.upgrades['damage']})")
            
        elif key == pygame.K_3:  # Velocidad de ataque
            if hasattr(self.active_attack_system, 'attack_cooldown'):
                self.active_attack_system.attack_cooldown = max(200, self.active_attack_system.attack_cooldown - 30)
            self.upgrades['attack_speed'] += 1
            print(f"⚡ Velocidad de ataque de {character.name} mejorada (nivel {self.upgrades['attack_speed']})")
            
        elif key == pygame.K_4:  # Vida máxima
            health_boost = 15
            character.max_health += health_boost
            character.health = min(character.health + health_boost, character.max_health)
            self.upgrades['health'] += 1
            print(f"❤️ Vida de {character.name} mejorada: {character.health}/{character.max_health}")
    
    def enforce_boundaries(self, character):
        """Asegura que los personajes no salgan de los límites del escenario"""
        margin = 50
        
        # Obtener límites del escenario basados en la imagen de fondo
        left_limit = margin
        right_limit = self.background.width - margin
        top_limit = margin
        bottom_limit = self.background.height - margin
        
        if character.x < left_limit:
            character.x = left_limit
        elif character.x > right_limit:
            character.x = right_limit
        
        if character.y < top_limit:
            character.y = top_limit
        elif character.y > bottom_limit:
            character.y = bottom_limit
    
    def process_worm_drops(self):
        """Procesa los drops de los gusanos muertos"""
        worms = self.worm_spawner.worms
        for worm in worms[:]:
            if not worm.alive and not hasattr(worm, 'dropped'):
                worm.dropped = True
                # 30% probabilidad total de drop (15% manzana + 15% poción)
                drop_chance = random.random()
                if drop_chance < 0.15:  # 15% para manzana
                    self.dropped_items.append({
                        'type': 'apple',
                        'x': worm.x + random.randint(-20, 20),
                        'y': worm.y + random.randint(-20, 20),
                        'image': self.apple_image,
                        'collected': False,
                        'drop_time': pygame.time.get_ticks()
                    })
                    print("🍎 ¡Un gusano soltó una manzana!")
                elif drop_chance < 0.30:  # 15% para poción
                    self.dropped_items.append({
                        'type': 'potion',
                        'x': worm.x + random.randint(-20, 20),
                        'y': worm.y + random.randint(-20, 20),
                        'image': self.potion_image,
                        'collected': False,
                        'drop_time': pygame.time.get_ticks()
                    })
                    print("🧪 ¡Un gusano soltó una poción!")
    
    def update_collectibles(self):
        """Actualiza los coleccionables en el campo"""
        current_time = pygame.time.get_ticks()
        
        # Verificar colisión con items
        for item in self.dropped_items[:]:
            if not item['collected']:
                item_rect = pygame.Rect(item['x'], item['y'], 32, 32)
                player_rect = pygame.Rect(self.active_character.x, self.active_character.y, 64, 64)
                
                if item_rect.colliderect(player_rect):
                    if item['type'] == 'apple':
                        # Manzanas se recogen automáticamente
                        self.collect_apple()
                        item['collected'] = True
                        self.dropped_items.remove(item)
                        continue
                    elif item['type'] == 'potion':
                        # Pociones se recogen con E
                        keys_pressed = pygame.key.get_pressed()
                        if keys_pressed[pygame.K_e]:
                            self.collect_potion(self.active_character)
                            item['collected'] = True
                            self.dropped_items.remove(item)
                            continue
                
                # Eliminar items después de 30 segundos
                if current_time - item['drop_time'] > 30000:
                    self.dropped_items.remove(item)
    
    def update_shield_system(self):
        """Actualiza el sistema de escudo para ambos personajes"""
        for character in [self.juan, self.adan]:
            if hasattr(character, 'shield_active') and character.shield_active:
                if hasattr(character, 'shield_timer'):
                    character.shield_timer += 1
                    if character.shield_timer >= character.shield_duration:
                        character.shield_active = False
                        character.shield_timer = 0
                        print(f"🛡️ Escudo de {character.name} terminado")
    
    def collect_apple(self):
        """Recolectar manzana y mostrar menú de mejoras"""
        print("🍎 ¡Manzana recogida! Selecciona una mejora:")
        print("1 - Velocidad | 2 - Daño | 3 - Vel. Ataque | 4 - Vida Máxima")
        self.show_upgrade_menu = True
        self.upgrade_menu_timer = 300  # 5 segundos a 60 FPS
    
    def collect_potion(self, character):
        """Recolectar poción y activar escudo"""
        print(f"🧪 ¡{character.name} consumió poción de escudo!")
        character.shield_active = True
        character.shield_timer = 0
        character.shield_duration = self.shield_duration
        print(f"🛡️ Escudo activado para {character.name} (15 segundos)")
    
    def handle_upgrade_selection(self, key):
        """Maneja la selección de mejora con manzanas"""
        character = self.active_character
        
        if key == pygame.K_1:  # Velocidad
            character.speed += 0.5
            self.upgrades['speed'] += 1
            print(f"🚀 Velocidad de {character.name} mejorada: {character.speed:.1f}")
            
        elif key == pygame.K_2:  # Daño
            # Aumentar daño según el sistema de ataque
            if hasattr(self.active_attack_system, 'melee_damage'):
                original_damage = getattr(self.active_attack_system, 'melee_damage', 40)
                self.active_attack_system.melee_damage = original_damage + 5
            if hasattr(self.active_attack_system, 'projectile_damage'):
                original_damage = getattr(self.active_attack_system, 'projectile_damage', 25)
                self.active_attack_system.projectile_damage = original_damage + 3
            self.upgrades['damage'] += 1
            print(f"⚔️ Daño de {character.name} mejorado (nivel {self.upgrades['damage']})")
            
        elif key == pygame.K_3:  # Velocidad de ataque
            if hasattr(self.active_attack_system, 'attack_cooldown'):
                self.active_attack_system.attack_cooldown = max(200, self.active_attack_system.attack_cooldown - 30)
            self.upgrades['attack_speed'] += 1
            print(f"⚡ Velocidad de ataque de {character.name} mejorada (nivel {self.upgrades['attack_speed']})")
            
        elif key == pygame.K_4:  # Vida máxima
            health_boost = 15
            character.max_health += health_boost
            character.health = min(character.health + health_boost, character.max_health)
            self.upgrades['health'] += 1
            print(f"❤️ Vida de {character.name} mejorada: {character.health}/{character.max_health}")
    
    def enforce_boundaries(self, character):
        """Asegura que los personajes no salgan de los límites del escenario"""
        margin = 50
        
        # Obtener límites del escenario basados en la imagen de fondo
        left_limit = margin
        right_limit = self.background.width - margin
        top_limit = margin
        bottom_limit = self.background.height - margin
        
        if character.x < left_limit:
            character.x = left_limit
        elif character.x > right_limit:
            character.x = right_limit
        
        if character.y < top_limit:
            character.y = top_limit
        elif character.y > bottom_limit:
            character.y = bottom_limit
    
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
        
        # Dibujar coleccionables
        self.draw_collectibles()
        
        # UI e información
        self.draw_ui()
        
        # Dibujar menú de mejoras si está activo
        if self.show_upgrade_menu:
            self.draw_upgrade_menu()
        
        pygame.display.flip()
    
    def draw_collectibles(self):
        """Dibuja manzanas y pociones en el suelo"""
        current_time = pygame.time.get_ticks()
        
        for item in self.dropped_items:
            if not item['collected']:
                # Efecto de brillo pulsante
                pulse = 1 + 0.3 * math.sin(current_time * 0.005)
                glow_alpha = int(80 + 40 * math.sin(current_time * 0.008))
                
                # Crear superficie con brillo
                glow_size = int(40 * pulse)
                glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
                
                if item['type'] == 'apple':
                    # Brillo rojo para manzanas
                    pygame.draw.circle(glow_surface, (255, 100, 100, glow_alpha), 
                                     (glow_size//2, glow_size//2), glow_size//2)
                else:  # potion
                    # Brillo azul para pociones
                    pygame.draw.circle(glow_surface, (100, 100, 255, glow_alpha), 
                                     (glow_size//2, glow_size//2), glow_size//2)
                
                # Posición del brillo
                glow_x = item['x'] - self.camera_x - glow_size//2 + 16
                glow_y = item['y'] - self.camera_y - glow_size//2 + 16
                self.screen.blit(glow_surface, (glow_x, glow_y))
                
                # Imagen del item
                if item['image']:
                    self.screen.blit(item['image'], 
                                   (item['x'] - self.camera_x, item['y'] - self.camera_y))
                
                # Texto flotante para pociones (requieren E)
                if item['type'] == 'potion':
                    # Verificar si el jugador está cerca
                    item_rect = pygame.Rect(item['x'], item['y'], 32, 32)
                    player_rect = pygame.Rect(self.active_character.x, self.active_character.y, 64, 64)
                    
                    if item_rect.colliderect(player_rect):
                        font = pygame.font.Font(None, 24)
                        hint_text = font.render("Presiona E", True, (255, 255, 255))
                        text_x = item['x'] - self.camera_x - hint_text.get_width()//2 + 16
                        text_y = item['y'] - self.camera_y - 25
                        
                        # Fondo del texto
                        bg_rect = pygame.Rect(text_x - 5, text_y, hint_text.get_width() + 10, hint_text.get_height())
                        pygame.draw.rect(self.screen, (0, 0, 0, 180), bg_rect)
                        
                        self.screen.blit(hint_text, (text_x, text_y))
    
    def draw_upgrade_menu(self):
        """Dibuja el menú de selección de mejoras"""
        # Fondo del menú
        menu_width = 600
        menu_height = 400
        menu_x = (self.screen_width - menu_width) // 2
        menu_y = (self.screen_height - menu_height) // 2
        
        # Superficie del menú con transparencia
        menu_surface = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)
        pygame.draw.rect(menu_surface, (0, 0, 0, 220), (0, 0, menu_width, menu_height))
        pygame.draw.rect(menu_surface, (255, 215, 0), (0, 0, menu_width, menu_height), 4)
        
        # Título
        font_title = pygame.font.Font(None, 72)
        font_option = pygame.font.Font(None, 48)
        
        title_text = font_title.render("🍎 MEJORA OBTENIDA 🍎", True, (255, 215, 0))
        title_rect = title_text.get_rect(center=(menu_width//2, 50))
        menu_surface.blit(title_text, title_rect)
        
        # Opciones de mejora
        options = [
            "1 - 🚀 Velocidad (+0.5)",
            "2 - ⚔️ Daño (+5/+3)",
            "3 - ⚡ Vel. Ataque (-30ms)",
            "4 - ❤️ Vida Máxima (+15)"
        ]
        
        for i, option in enumerate(options):
            option_text = font_option.render(option, True, (255, 255, 255))
            option_rect = option_text.get_rect(center=(menu_width//2, 120 + i * 60))
            menu_surface.blit(option_text, option_rect)
        
        # Instrucciones
        instruction_text = font_option.render("Presiona el número de la mejora que deseas", True, (200, 200, 200))
        instruction_rect = instruction_text.get_rect(center=(menu_width//2, 350))
        menu_surface.blit(instruction_text, instruction_rect)
        
        # Temporizador
        time_left = self.upgrade_menu_timer // 60 + 1
        timer_text = pygame.font.Font(None, 36).render(f"Tiempo: {time_left}s", True, (255, 100, 100))
        timer_rect = timer_text.get_rect(topright=(menu_width - 10, 10))
        menu_surface.blit(timer_text, timer_rect)
        
        self.screen.blit(menu_surface, (menu_x, menu_y))
    
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
        
        # Progreso mejorado
        progress_text = font_small.render(f"Gusanos derrotados: {self.enemies_defeated}/{self.victory_condition}", True, (255, 255, 255))
        self.screen.blit(progress_text, (20, 190))
        
        # Mejoras actuales
        upgrades_text = [
            f"🚀 Velocidad: +{self.upgrades['speed']}",
            f"⚔️ Daño: +{self.upgrades['damage']}",
            f"⚡ Vel.Ataque: +{self.upgrades['attack_speed']}",
            f"❤️ Vida: +{self.upgrades['health']}"
        ]
        
        for i, upgrade_text in enumerate(upgrades_text):
            upgrade_surface = font_small.render(upgrade_text, True, (200, 255, 200))
            self.screen.blit(upgrade_surface, (20, 240 + i * 35))
        
        # UI específica del personaje activo
        if self.active_character == self.juan:
            self.juan_attack.draw_ui(self.screen)
        
        # Estado de escudo si está activo
        for character in [self.juan, self.adan]:
            if hasattr(character, 'shield_active') and character.shield_active:
                shield_time_left = (character.shield_duration - character.shield_timer) // 60
                shield_text = font_small.render(f"🛡️ {character.name}: {shield_time_left}s", True, (100, 150, 255))
                if character == self.juan:
                    self.screen.blit(shield_text, (400, 140))
                else:
                    self.screen.blit(shield_text, (400, 175))
        
        # Controles simplificados
        instructions = [
            "🎮 CONTROLES:",
            "WASD/Flechas - Mover",
            "ESPACIO - Ataque",
            "X - Ataque especial",
            "TAB - Cambiar personaje",
            "E - Revivir/Consumir poción",
            "ESC - Pantalla completa"
        ]
        
        for i, instruction in enumerate(instructions):
            text_surface = font_small.render(instruction, True, (255, 255, 255))
            self.screen.blit(text_surface, (20, self.screen_height - 300 + i * 40))
        
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
        
        status_text = f"Gusanos activos: {len(self.worm_spawner.get_worms())} | Juan: {juan_status} | Adán: {adan_status}"
        status_surface = font_small.render(status_text, True, (200, 200, 200))
        self.screen.blit(status_surface, (600, 140))
    
    def run(self):
        """Bucle principal del juego"""
        print("🚀 Iniciando Nivel 1 - Tierra de las Manzanas (COMBATE)...")
        print("⏳ Cargando recursos...")
        
        # FAILSAFE: Asegurar que todas las variables críticas existen
        if not hasattr(self, 'worm_spawner'):
            print("🚨 FAILSAFE: Variables faltantes detectadas, inicializando...")
            self.worm_spawner = WormSpawner(max_worms=15)
            # Variables de estado del juego
            self.game_over = False
            self.victory = False
            self.enemies_defeated = 0
            self.victory_condition = 15
            # Sistema de coleccionables
            self.dropped_items = []
            self.show_upgrade_menu = False
            self.upgrade_menu_timer = 0
            # Cámara
            self.camera_x = 0
            self.camera_y = 0
            # Control de alternancia
            self.switch_cooldown = 0
            # Sistema de escudos y mejoras
            if not hasattr(self, 'upgrades'):
                self.upgrades = {'speed': 0, 'damage': 0, 'attack_speed': 0, 'max_health': 0}
            if not hasattr(self, 'shield_timer'):
                self.shield_timer = 0
                self.shield_duration = 15 * 60
            print("✅ FAILSAFE: Todas las variables críticas inicializadas")
        
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
