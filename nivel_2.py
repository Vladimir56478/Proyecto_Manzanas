import pygame
import sys
from PIL import Image
import requests
from io import BytesIO
import math
import random

# Importar clases necesarias
from adan_character_animation import AdanCharacter
from juan_character_animation import JuanCharacter
from adan_attacks import AdanAttack
from juan_attacks import JuanAttack
from chaman_malvado import ChamanMalvado
from character_ai import CharacterAI
from audio_manager import get_audio_manager
from loading_screen import LoadingScreen
from items_system import ItemManager
from worm_enemy import WormSpawner  # Agregar gusanos al nivel 2

# Importar sistema de colisiones del nivel 1
class CollisionBlock:
    """Bloque invisible de colisión para restringir movimiento"""
    def __init__(self, x, y, width=32, height=32):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
    
    def draw_editor(self, screen, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        pygame.draw.rect(screen, (255, 0, 0, 120), (screen_x, screen_y, self.width, self.height))
        pygame.draw.rect(screen, (255, 255, 255), (screen_x, screen_y, self.width, self.height), 2)

class CollisionManager:
    """Maneja las colisiones con bloques invisibles - Igual que nivel 1"""
    def __init__(self, world_width=1980, world_height=1080):
        self.blocks = []
        self.editor_mode = False
        self.block_size = 32
        self.world_width = world_width
        self.world_height = world_height
        self.editor_cursor_x = 0
        self.editor_cursor_y = 0
        self.is_dragging = False
        self.mouse_pressed = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.drag_current_x = 0
        self.drag_current_y = 0
    
    def load_collision_blocks(self, filename):
        """Carga bloques de colisión desde archivo"""
        try:
            with open(filename, 'r') as f:
                for line in f:
                    x, y = map(int, line.strip().split(','))
                    self.add_block(x, y)
            print(f"📂 Cargados {len(self.blocks)} bloques de colisión desde {filename}")
        except FileNotFoundError:
            print(f"⚠️ Archivo {filename} no encontrado")
        except Exception as e:
            print(f"⚠️ Error cargando colisiones: {e}")
    
    def add_block(self, x, y):
        block = CollisionBlock(x, y)
        if not any(b.x == x and b.y == y for b in self.blocks):
            self.blocks.append(block)
            return True
        return False
    
    def check_collision(self, character_rect):
        for block in self.blocks:
            if character_rect.colliderect(block.rect):
                return True
        return False
    
    def can_move_to(self, character, new_x, new_y):
        test_rect = pygame.Rect(new_x, new_y, 100, 100)  # 64 * 1.56 = 100
        return not self.check_collision(test_rect)
    
    def draw_editor_mode(self, screen, camera_x, camera_y):
        """Dibuja el modo editor con cursor visual tipo Windows"""
        if not self.editor_mode:
            return
        
        # Dibujar todos los bloques
        for block in self.blocks:
            block.draw_editor(screen, camera_x, camera_y)
        
        # CURSOR VISUAL TIPO WINDOWS - Copiado desde nivel 1
        # Dibujar cursor del editor con mejor feedback visual
        cursor_screen_x = self.editor_cursor_x - camera_x
        cursor_screen_y = self.editor_cursor_y - camera_y
        
        # Verificar si ya existe un bloque en esta posición
        block_exists = any(block.x == self.editor_cursor_x and block.y == self.editor_cursor_y 
                          for block in self.blocks)
        
        # Color del cursor: verde si es posición libre, rojo si ocupada
        cursor_color = (255, 100, 100) if block_exists else (100, 255, 100)
        border_color = (255, 0, 0) if block_exists else (0, 255, 0)
        
        # Fondo semitransparente del cursor
        cursor_surface = pygame.Surface((self.block_size, self.block_size), pygame.SRCALPHA)
        cursor_surface.fill((*cursor_color, 120))
        screen.blit(cursor_surface, (cursor_screen_x, cursor_screen_y))
        
        # Borde del cursor con animación
        import math
        time_factor = pygame.time.get_ticks() / 200
        border_width = int(3 + 2 * abs(math.sin(time_factor)))
        pygame.draw.rect(screen, border_color, 
                        (cursor_screen_x, cursor_screen_y, self.block_size, self.block_size), 
                        border_width)
        
        # Indicador de acción en el centro del cursor
        center_x = cursor_screen_x + self.block_size // 2
        center_y = cursor_screen_y + self.block_size // 2
        
        if block_exists:
            # Símbolo de eliminación (X)
            pygame.draw.line(screen, (255, 255, 255), 
                           (center_x - 8, center_y - 8), (center_x + 8, center_y + 8), 3)
            pygame.draw.line(screen, (255, 255, 255), 
                           (center_x + 8, center_y - 8), (center_x - 8, center_y + 8), 3)
        else:
            # Símbolo de adición (+)
            pygame.draw.line(screen, (255, 255, 255), 
                           (center_x - 8, center_y), (center_x + 8, center_y), 3)
            pygame.draw.line(screen, (255, 255, 255), 
                           (center_x, center_y - 8), (center_x, center_y + 8), 3)
        
        # Información del editor
        font = pygame.font.Font(None, 48)
        editor_info = [
            "🛠️ MODO EDITOR DE COLISIONES - NIVEL 2",
            "F1: Salir del editor | Flechas: Mover cursor",
            "ESPACIO: Colocar bloque | BACKSPACE: Eliminar",
            f"Bloques totales: {len(self.blocks)}"
        ]
        
        for i, info in enumerate(editor_info):
            text_surface = font.render(info, True, (255, 255, 0))
            screen.blit(text_surface, (20, 200 + i * 30))
    
    def handle_editor_input(self, keys_pressed, keys_just_pressed):
        if not self.editor_mode:
            return
        
        move_speed = 32
        if keys_just_pressed.get(pygame.K_UP, False):
            self.editor_cursor_y = max(0, self.editor_cursor_y - move_speed)
        if keys_just_pressed.get(pygame.K_DOWN, False):
            self.editor_cursor_y = min(self.world_height - self.block_size, self.editor_cursor_y + move_speed)
        if keys_just_pressed.get(pygame.K_LEFT, False):
            self.editor_cursor_x = max(0, self.editor_cursor_x - move_speed)
        if keys_just_pressed.get(pygame.K_RIGHT, False):
            self.editor_cursor_x = min(self.world_width - self.block_size, self.editor_cursor_x + move_speed)
        
        if keys_just_pressed.get(pygame.K_SPACE, False):
            self.add_block(self.editor_cursor_x, self.editor_cursor_y)

class Nivel2:
    def __init__(self, selected_character='juan'):
        pygame.init()
        self.screen_width = 1920
        self.screen_height = 1080
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        pygame.display.set_caption("🍎 Nivel 2 - La Tierra de las Manzanas - EL CHAMÁN MALVADO")
        
        # Verificar resolución real
        actual_size = self.screen.get_size()
        print(f"🖥️ Resolución Nivel 2: {actual_size[0]}x{actual_size[1]}")
        
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Carga directa sin loading screen molesto
        print("🎮 Iniciando Nivel 2 - El Chamán Malvado...")
        
        # Cargar escenario del nivel 2 - CORREGIDO para carga local
        self.background_color = (15, 25, 15)  # Fallback
        self.background_url = "assets/backgrounds/background.png"
        self.background_image = self.load_background_from_local(self.background_url)
        
        # Configurar dimensiones del mundo basadas en el fondo
        if self.background_image:
            self.world_width = self.background_image.get_width()
            self.world_height = self.background_image.get_height()
        else:
            self.world_width = 1920
            self.world_height = 1080
        
        # Cargar personajes con stats transferidos del nivel 1
        
        # Juan - Mantener progreso del nivel 1 
        self.juan = JuanCharacter(300, 400)
        # Stats base mejorados del nivel 1
        self.juan.max_health = 100 + (25 * 3)  # Base + mejoras típicas
        self.juan.health = self.juan.max_health
        self.juan.speed = 6.5 + (0.8 * 3)  # Base + mejoras típicas
        self.juan.damage = 22 + (8 * 3)  # Base + mejoras típicas
        self.juan.name = "Juan"
        
        # Adán - Mantener progreso del nivel 1
        self.adan = AdanCharacter(400, 400)
        # Stats base mejorados del nivel 1
        self.adan.max_health = 125 + (25 * 3)  # Base + mejoras típicas
        self.adan.health = self.adan.max_health
        self.adan.speed = 5.5 + (0.8 * 3)  # Base + mejoras típicas
        self.adan.damage = 28 + (8 * 3)  # Base + mejoras típicas
        self.adan.name = "Adán"
        
        # Cargar sistemas de ataque mejorados
        self.juan_attack = JuanAttack(self.juan)
        self.adan_attack = AdanAttack(self.adan)
        self.juan.attacks = self.juan_attack
        self.adan.attacks = self.adan_attack
        
        # Sistema de personajes activo/inactivo
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
        
        # Inicializar sistema de IA mejorada
        self.inactive_ai = CharacterAI(self.inactive_character, self.active_character)
        # Mejorar la IA para ser más agresiva
        self.inactive_ai.detection_range = 400
        self.inactive_ai.attack_range = 150
        
        # Cargar Chamán Malvado - El jefe final (más pequeño)
        self.chaman = ChamanMalvado(self.screen_width//2, self.screen_height//4)
        # Escalar chamán 30% más pequeño para mejor jugabilidad
        self.scale_chaman_sprites(0.7)
        
        # Cargar gusanos adicionales para mayor dificultad
        self.worm_spawner = WormSpawner(max_worms=15)  # 15 gusanos como solicitado
        self.setup_level2_worm_spawns()
        
        # Sistema de audio
        self.audio = get_audio_manager()
        
        # Cámara mejorada
        self.camera_x = 0
        self.camera_y = 0
        self.camera_smooth_factor = 0.08  # Más suave para combate con jefe
        
        # Sistema de colisiones (igual que nivel 1)
        self.collision_manager = CollisionManager(self.world_width, self.world_height)
        
        # Cargar bloques de colisión desde archivo (igual que nivel 1)
        try:
            self.collision_manager.load_collision_blocks("collision_data.txt")
            print(f"📂 Bloques de colisión cargados para nivel 2")
        except Exception as e:
            print(f"⚠️ Error cargando colisiones nivel 2: {e}")
            
        self.keys_last_frame = list(pygame.key.get_pressed())  # Para detectar pulsaciones
        self.game_paused = False  # Sistema de pausa para editor
        
        # Estados del juego
        self.game_over = False
        self.victory = False
        self.switch_cooldown = 0
        self.revival_key_pressed = False
        self.show_revival_prompt = False
        self.revival_distance = 100
        
        # Sistema de coleccionables simplificado (igual que nivel 1)
        self.dropped_items = []  # Items simples: gusano muere -> PNG aparece
        self.create_simple_collectible_images()  # Crear sprites simples
        
        # Variables de compatibilidad para código existente
        self.show_upgrade_menu = False
        self.upgrade_menu_timer = 0
        self.upgrades = {
            'speed': 0,
            'damage': 0,
            'attack_speed': 0,
            'health': 0
        }
        self.shield_duration = 15 * 60  # 15 segundos a 60 FPS
        
        # Límites del escenario (se ajustarán cuando se cargue la imagen real)
        self.world_boundaries = {
            'left': 0,
            'right': 1920,
            'top': 0,
            'bottom': 1080
        }
        
        # Listo para comenzar
        
        print(f"🎮 Nivel 2 iniciado - Personaje activo: {self.active_character.name}")
        print(f"🤖 IA controlando: {self.inactive_character.name}")
        print(f"👹 Chamán Malvado despertado con {self.chaman.health} HP")
    
    def load_background_from_local(self, file_path):
        """Carga el fondo desde archivo local - IGUAL QUE NIVEL 1"""
        try:
            print(f"📥 Cargando fondo del nivel 2 desde archivo local: {file_path}")
            
            # Cargar imagen local usando PIL
            pil_image = Image.open(file_path)
            
            # Información de la imagen original
            original_width, original_height = pil_image.size
            print(f"📐 Dimensiones originales del fondo nivel 2: {original_width}x{original_height}")
            
            # RESPETAR DIMENSIONES ORIGINALES - No redimensionar
            self.world_width = original_width
            self.world_height = original_height
            print(f"✅ Usando dimensiones originales del nivel 2: {self.world_width}x{self.world_height}")
            
            # Convertir a formato pygame
            pil_image = pil_image.convert('RGB')
            image_data = pil_image.tobytes()
            
            background = pygame.image.fromstring(image_data, pil_image.size, 'RGB')
            background = background.convert()
            
            print(f"✅ Fondo nivel 2 cargado exitosamente: {original_width}x{original_height}")
            return background
            
        except Exception as e:
            print(f"❌ Error cargando fondo nivel 2: {e}")
            print("🎨 Creando fondo de respaldo para nivel 2...")
            
            # Crear fondo de respaldo más oscuro y siniestro para el nivel 2
            fallback = pygame.Surface((1920, 1080))
            
            # Gradiente oscuro para el nivel del Chamán
            for y in range(1080):
                darkness_intensity = 20 + (y * 40) // 1080
                color = (darkness_intensity // 3, darkness_intensity // 2, darkness_intensity // 3)  # Verdoso oscuro
                pygame.draw.line(fallback, color, (0, y), (1920, y))
            
            # Añadir elementos decorativos siniestros
            import random
            for _ in range(80):
                x = random.randint(0, 1920)
                y = random.randint(0, 1080)
                size = random.randint(3, 8)
                darkness = random.randint(5, 15)
                pygame.draw.circle(fallback, (darkness, darkness//2, darkness), (x, y), size)
            
            print("✅ Fondo de respaldo del nivel 2 creado")
            return fallback

    def scale_character_sprites(self, character, scale_factor):
        """Escala todos los sprites de un personaje"""
        try:
            # Escalar animaciones de movimiento
            for direction in character.animations:
                for i, frame in enumerate(character.animations[direction]):
                    original_size = frame.get_size()
                    new_size = (int(original_size[0] * scale_factor), int(original_size[1] * scale_factor))
                    character.animations[direction][i] = pygame.transform.scale(frame, new_size)
            
            # Actualizar tamaño del personaje
            character.width = int(character.width * scale_factor)
            character.height = int(character.height * scale_factor)
            
            print(f"✅ Sprites de {character.name} escalados {scale_factor}x")
        except Exception as e:
            print(f"⚠️ Error escalando sprites de {character.name}: {e}")
    
    def scale_chaman_sprites(self, scale_factor):
        """Escala sprites del chamán para mejor jugabilidad"""
        try:
            # Escalar character del chamán
            if hasattr(self.chaman, 'character'):
                self.scale_character_sprites(self.chaman.character, scale_factor)
            
            # Escalar sprites de ataques del chamán si existen
            if hasattr(self.chaman, 'attack_system') and hasattr(self.chaman.attack_system, 'animations'):
                for direction in self.chaman.attack_system.animations:
                    for i, frame in enumerate(self.chaman.attack_system.animations[direction]):
                        original_size = frame.get_size()
                        new_size = (int(original_size[0] * scale_factor), int(original_size[1] * scale_factor))
                        self.chaman.attack_system.animations[direction][i] = pygame.transform.scale(frame, new_size)
            
            print(f"✅ Chamán escalado {scale_factor}x para mejor jugabilidad")
        except Exception as e:
            print(f"⚠️ Error escalando chamán: {e}")
    
    def create_simple_collectible_images(self):
        """Crea sprites simples para manzanas y pociones - Sin URLs complicadas"""
        # Manzana simple pero visible
        self.apple_image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(self.apple_image, (220, 50, 50), (20, 22), 16)
        pygame.draw.circle(self.apple_image, (255, 100, 100), (16, 18), 12)
        pygame.draw.rect(self.apple_image, (139, 69, 19), (18, 6, 6, 12))
        pygame.draw.ellipse(self.apple_image, (34, 139, 34), (14, 4, 12, 8))
        pygame.draw.circle(self.apple_image, (255, 200, 200, 80), (15, 15), 8)
        
        # Poción simple pero visible
        self.potion_image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.rect(self.potion_image, (100, 100, 100), (16, 18, 8, 16))
        pygame.draw.ellipse(self.potion_image, (20, 100, 220), (14, 22, 12, 12))
        pygame.draw.rect(self.potion_image, (50, 150, 255), (18, 14, 4, 14))
        pygame.draw.circle(self.potion_image, (100, 200, 255), (20, 26), 5)
        pygame.draw.circle(self.potion_image, (150, 220, 255, 60), (20, 26), 10)
    
    def setup_level2_worm_spawns(self):
        """Configura 4 áreas de spawn para los 8 gusanos del nivel 2"""
        spawn_areas = [
            (200, 200, 150, 150),    # Esquina superior izquierda  
            (1200, 200, 150, 150),   # Esquina superior derecha
            (200, 700, 150, 150),    # Esquina inferior izquierda
            (1200, 700, 150, 150),   # Esquina inferior derecha
        ]
        
        for x, y, w, h in spawn_areas:
            self.worm_spawner.add_spawn_area(x, y, w, h)
        
        print("✅ 4 áreas de spawn configuradas para 8 gusanos en Nivel 2")
    
    # Función eliminada - Ahora usamos create_simple_collectible_images()
    
    def handle_events(self):
        """Maneja eventos del juego"""
        keys_pressed = pygame.key.get_pressed()
        
        # Detectar teclas presionadas este frame
        keys_just_pressed = {}
        for key in range(512):
            if key < len(keys_pressed) and key < len(self.keys_last_frame):
                keys_just_pressed[key] = keys_pressed[key] and not self.keys_last_frame[key]
            else:
                keys_just_pressed[key] = False
        
        self.keys_last_frame = list(keys_pressed)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_F1:
                    # Toggle modo editor (igual que nivel 1)
                    self.collision_manager.editor_mode = not self.collision_manager.editor_mode
                    mode = "activado" if self.collision_manager.editor_mode else "desactivado"
                    print(f"🛠️ Modo editor {mode} en Nivel 2")
                elif event.key == pygame.K_TAB and not self.game_over and not self.victory and not self.collision_manager.editor_mode:
                    if self.switch_cooldown <= 0 and self.juan.health > 0 and self.adan.health > 0:
                        self.switch_character()
                        self.switch_cooldown = 30
                elif event.key == pygame.K_r and (self.game_over or self.victory):
                    self.restart_game()
                elif event.key == pygame.K_SPACE and not self.game_over and not self.victory and not self.collision_manager.editor_mode:
                    # Ataque básico
                    self.perform_basic_attack()
                elif event.key == pygame.K_x and not self.game_over and not self.victory and not self.collision_manager.editor_mode:
                    # Ataque especial
                    self.perform_special_attack()
                # Manejo del menú de mejoras (simplificado)
                elif self.show_upgrade_menu and event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    self.handle_upgrade_selection(event.key)
                    self.show_upgrade_menu = False
                    self.game_paused = False
        
        # Manejo del modo editor - PAUSAR JUEGO
        if self.collision_manager.editor_mode:
            self.game_paused = True
            self.collision_manager.handle_editor_input(keys_pressed, keys_just_pressed)
            return True
        else:
            self.game_paused = False
        
        # Manejar tecla E para revivir y consumir pociones
        e_key_pressed = keys_pressed[pygame.K_e]
        
        if not self.game_over and not self.victory:
            # Sistema de revival
            if self.inactive_character.health <= 0 and not self.inactive_ai.is_being_revived:
                distance_to_inactive = self.distance_between_characters()
                
                if distance_to_inactive <= self.revival_distance:
                    self.show_revival_prompt = True
                    
                    if e_key_pressed and not self.revival_key_pressed:
                        if self.inactive_ai.start_revival():
                            print(f"🔄 Comenzando a revivir a {self.inactive_character.name}...")
                            self.show_revival_prompt = False
                else:
                    self.show_revival_prompt = False
            
            # Consumir pociones
            self.handle_potion_consumption(e_key_pressed)
        
        self.revival_key_pressed = e_key_pressed
        return True
    
    def switch_character(self):
        """Alterna entre personajes"""
        self.active_character, self.inactive_character = self.inactive_character, self.active_character
        self.active_attack_system, self.inactive_attack_system = self.inactive_attack_system, self.active_attack_system
        self.inactive_ai = CharacterAI(self.inactive_character, self.active_character)
        # Mantener mejoras de IA
        self.inactive_ai.detection_range = 400
        self.inactive_ai.attack_range = 150
        print(f"🔄 Cambiado a: {self.active_character.name}")
    
    def distance_between_characters(self):
        """Calcula la distancia entre los dos personajes"""
        dx = self.juan.x - self.adan.x
        dy = self.juan.y - self.adan.y
        return math.sqrt(dx*dx + dy*dy)
    
    def perform_basic_attack(self):
        """Realiza ataque básico del personaje actual"""
        print(f"🎯 {self.active_character.name} iniciando ataque básico contra el Chamán")
        
    def perform_special_attack(self):
        """Realiza ataque especial del personaje actual"""
        print(f"💥 {self.active_character.name} realizando ataque especial")
    
    def handle_potion_consumption(self, e_pressed):
        """Maneja el consumo de pociones"""
        if not e_pressed:
            return
            
        # Buscar poción cerca del personaje activo
        for item in self.dropped_items[:]:
            if item['type'] == 'potion' and not item['collected']:
                item_rect = pygame.Rect(item['x'], item['y'], 40, 40)
                player_rect = pygame.Rect(self.active_character.x, self.active_character.y, 
                                        self.active_character.width, self.active_character.height)
                
                if item_rect.colliderect(player_rect):
                    self.collect_potion(self.active_character)
                    item['collected'] = True
                    self.dropped_items.remove(item)
                    break
    
    def collect_apple(self):
        """Recolectar manzana y mostrar menú de mejoras"""
        print("🍎 ¡Manzana recogida! Selecciona una mejora:")
        print("1 - Velocidad | 2 - Daño | 3 - Vel. Ataque | 4 - Vida Máxima")
        self.show_upgrade_menu = True
        self.upgrade_menu_timer = 300  # 5 segundos a 60 FPS
    
    def collect_potion(self, character):
        """Recolectar poción y activar escudo"""
        print(f"🧪 ¡{character.name} consumió poción de escudo!")
        
        # Activar escudo en el personaje específico
        character.shield_active = True
        character.shield_timer = 0
        character.shield_duration = self.shield_duration
        
        print(f"🛡️ Escudo activado para {character.name} (20 segundos)")
    
    def handle_upgrade_selection(self, key):
        """Maneja la selección de mejora con manzanas"""
        character = self.active_character
        
        if key == pygame.K_1:  # Velocidad
            character.speed += 0.7
            self.upgrades['speed'] += 1
            print(f"🚀 Velocidad de {character.name} mejorada: {character.speed:.1f}")
            
        elif key == pygame.K_2:  # Daño
            # Aumentar daño según el sistema de ataque
            if hasattr(self.active_attack_system, 'melee_damage'):
                self.active_attack_system.melee_damage += 8
            if hasattr(self.active_attack_system, 'projectile_damage'):
                self.active_attack_system.projectile_damage += 5
            self.upgrades['damage'] += 1
            print(f"⚔️ Daño de {character.name} mejorado (nivel {self.upgrades['damage']})")
            
        elif key == pygame.K_3:  # Velocidad de ataque
            if hasattr(self.active_attack_system, 'attack_cooldown'):
                self.active_attack_system.attack_cooldown = max(200, self.active_attack_system.attack_cooldown - 50)
            self.upgrades['attack_speed'] += 1
            print(f"⚡ Velocidad de ataque de {character.name} mejorada (nivel {self.upgrades['attack_speed']})")
            
        elif key == pygame.K_4:  # Vida máxima
            health_boost = 25
            character.max_health += health_boost
            character.health = min(character.health + health_boost, character.max_health)
            self.upgrades['health'] += 1
            print(f"❤️ Vida de {character.name} mejorada: {character.health}/{character.max_health}")
    
    def update(self):
        """Actualiza la lógica del juego"""
        if self.game_over or self.victory or self.game_paused:
            if self.switch_cooldown > 0:
                self.switch_cooldown -= 1
            return
        
        keys_pressed = pygame.key.get_pressed()
        
        # Actualizar personaje activo con sistema de colisiones
        if not self.active_attack_system.is_character_attacking() and not self.collision_manager.editor_mode:
            old_x, old_y = self.active_character.x, self.active_character.y
            self.active_character.update(keys_pressed)
            
            # Verificar colisiones y revertir movimiento si es necesario
            if not self.collision_manager.can_move_to(self.active_character, 
                                                     self.active_character.x, 
                                                     self.active_character.y):
                self.active_character.x, self.active_character.y = old_x, old_y
            
            # Aplicar límites del mundo
            self.enforce_boundaries(self.active_character)
        
        # Actualizar IA del personaje inactivo contra TODOS los enemigos
        if (self.inactive_character.health > 0 or self.inactive_ai.is_being_revived) and not self.collision_manager.editor_mode:
            old_x, old_y = self.inactive_character.x, self.inactive_character.y
            
            # Obtener todos los enemigos para que la IA pueda atacar a cualquiera
            worms = self.worm_spawner.get_worms()
            all_enemies_for_ai = [self.chaman] + worms  # Incluir Chamán y todos los gusanos
            
            # La IA ahora puede atacar tanto al chamán como a los gusanos
            self.inactive_ai.update(all_enemies_for_ai)
            
            ai_animation_state = self.inactive_ai.get_animation_state()
            self.inactive_character.update(keys_pressed=None, ai_controlled=True, ai_direction=ai_animation_state)
            
            # Verificar colisiones para IA también
            if not self.collision_manager.can_move_to(self.inactive_character,
                                                     self.inactive_character.x,
                                                     self.inactive_character.y):
                self.inactive_character.x, self.inactive_character.y = old_x, old_y
            
            self.enforce_boundaries(self.inactive_character)
        
        # Actualizar sistema de escudo
        self.update_shield_system()
        
        # Obtener todos los enemigos del nivel 2
        worms = self.worm_spawner.get_worms()
        all_enemies = [self.chaman] + worms  # Incluir Chamán y todos los gusanos
        
        # Manejar ataques del personaje activo contra TODOS los enemigos
        self.active_attack_system.handle_attack_input(keys_pressed, all_enemies)
        
        # Actualizar chamán (IA vs personaje activo)
        players = [self.active_character, self.inactive_character]
        self.chaman.update(players)
        
        # Actualizar gusanos adicionales del nivel 2
        self.worm_spawner.update(players)
        
        # Comprobar impactos de proyectiles del chamán en ambos personajes
        self.chaman.check_projectile_collisions(players)
        
        # Verificar ataques de gusanos contra jugadores
        self.check_worm_attacks(players)
        
        # Actualizar cámara para seguir la batalla
        target_camera_x = self.active_character.x - self.screen_width // 2
        target_camera_y = self.active_character.y - self.screen_height // 2
        
        # Suavizar movimiento de cámara
        self.camera_x += (target_camera_x - self.camera_x) * self.camera_smooth_factor
        self.camera_y += (target_camera_y - self.camera_y) * self.camera_smooth_factor
        
        # Limitar cámara a los bordes del mundo
        self.limit_camera()
        
        # Actualizar sistemas de ataque contra TODOS los enemigos
        worms = self.worm_spawner.get_worms()
        all_enemies = [self.chaman] + worms  # Incluir Chamán y todos los gusanos
        
        self.juan_attack.update(all_enemies)
        self.adan_attack.update(all_enemies)
        
        # Procesar drops simples: gusano muere -> PNG aparece
        self.process_worm_drops()
        
        # Actualizar coleccionables simples
        self.update_collectibles()
        
        # Verificar condición de victoria/derrota
        if self.chaman.health <= 0:
            self.victory = True
            print("🎉 ¡VICTORIA ÉPICA! Has derrotado al Chamán Malvado")
        
        if self.juan.health <= 0 and self.adan.health <= 0:
            self.game_over = True
            print("💀 Game Over - El Chamán Malvado ha triunfado")
        
        # Reducir cooldowns
        if self.switch_cooldown > 0:
            self.switch_cooldown -= 1
            
        if self.upgrade_menu_timer > 0:
            self.upgrade_menu_timer -= 1
            if self.upgrade_menu_timer <= 0:
                self.show_upgrade_menu = False
    
    def process_worm_drops(self):
        """Procesa drops de gusanos del nivel 2"""
        # Procesar drops de gusanos del spawner
        for worm in self.worm_spawner.worms[:]:
            if not worm.alive and not getattr(worm, 'drop_processed', False):
                worm.drop_processed = True
                
                # Generar drops con probabilidades (80% en nivel 2)
                drop_x = worm.x + random.randint(-40, 40)
                drop_y = worm.y + random.randint(-40, 40)
                
                drop_chance = random.random()
                if drop_chance < 0.80:
                    # 50% manzana, 30% poción
                    if random.random() < 0.625:  # 50/80 = 0.625
                        # Agregar manzana al sistema simple
                        self.dropped_items.append({
                            'type': 'apple',
                            'x': drop_x,
                            'y': drop_y,
                            'image': self.apple_image,
                            'collected': False,
                            'drop_time': pygame.time.get_ticks()
                        })
                        print("🍎 Drop: Manzana de poder (Nivel 2)")
                    else:
                        # Agregar poción al sistema simple
                        self.dropped_items.append({
                            'type': 'potion',
                            'x': drop_x,
                            'y': drop_y,
                            'image': self.potion_image,
                            'collected': False,
                            'drop_time': pygame.time.get_ticks()
                        })
                        print("🧪 Drop: Poción de escudo (Nivel 2)")
                
                # Remover el gusano muerto del spawner
                self.worm_spawner.worms.remove(worm)
        
        # Procesar drops de gusanos invocados por el chamán (si existen)
        if hasattr(self.chaman, 'summoned_worms'):
            for worm in self.chaman.summoned_worms[:]:
                if not worm.alive and hasattr(worm, 'pending_drops') and worm.pending_drops:
                    drops = worm.get_and_clear_drops()
                    for drop in drops:
                        self.item_manager.add_item(drop['type'], drop['x'], drop['y'])
                        print(f"🎁 Drop de gusano invocado: {drop['type']}")
    
    def check_worm_attacks(self, players):
        """Verifica ataques de gusanos contra jugadores en nivel 2"""
        for worm in self.worm_spawner.get_worms():
            if worm.state == "attack":
                for player in players:
                    if player.health > 0:
                        distance = math.sqrt((worm.x - player.x)**2 + (worm.y - player.y)**2)
                        if distance <= worm.attack_range:
                            current_time = pygame.time.get_ticks()
                            if current_time - worm.last_attack_time >= worm.attack_cooldown:
                                # Verificar escudo
                                if not getattr(player, 'shield_active', False):
                                    player.take_damage(worm.attack_damage)
                                    print(f"💥 {player.name} recibió {worm.attack_damage} daño de gusano")
                                else:
                                    print(f"🛡️ {player.name} bloqueó ataque de gusano con escudo")
                                worm.last_attack_time = current_time
    
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
    
    def process_boss_drops(self):
        """Procesa drops especiales del jefe cuando recibe mucho daño"""
        # El chamán puede soltar items cuando está herido
        if self.chaman.health < self.chaman.max_health * 0.7 and len(self.dropped_items) < 2:
            if random.random() < 0.02:  # 2% de probabilidad por frame cuando está herido
                drop_type = 'apple' if random.random() < 0.6 else 'potion'
                
                # Posición aleatoria cerca del chamán
                drop_x = self.chaman.x + random.randint(-80, 80)
                drop_y = self.chaman.y + random.randint(-80, 80)
                
                self.dropped_items.append({
                    'type': drop_type,
                    'x': drop_x,
                    'y': drop_y,
                    'image': self.apple_image if drop_type == 'apple' else self.potion_image,
                    'collected': False,
                    'drop_time': pygame.time.get_ticks()
                })
                
                print(f"💎 El Chamán soltó una {drop_type}!")
    
    def update_collectibles(self):
        """Actualiza los coleccionables en el campo"""
        current_time = pygame.time.get_ticks()
        
        # Verificar colisión con manzanas (auto-consumo)
        for item in self.dropped_items[:]:
            if not item['collected'] and item['type'] == 'apple':
                item_rect = pygame.Rect(item['x'], item['y'], 40, 40)
                player_rect = pygame.Rect(self.active_character.x, self.active_character.y, 
                                        self.active_character.width, self.active_character.height)
                
                if item_rect.colliderect(player_rect):
                    self.collect_apple()
                    item['collected'] = True
                    self.dropped_items.remove(item)
                    continue
            
            # Eliminar items después de 45 segundos
            if current_time - item['drop_time'] > 45000:
                self.dropped_items.remove(item)
    
    def enforce_boundaries(self, character):
        """Asegura que los personajes no salgan de los límites del mundo"""
        margin = 50
        
        if character.x < self.world_boundaries['left'] + margin:
            character.x = self.world_boundaries['left'] + margin
        elif character.x > self.world_boundaries['right'] - margin:
            character.x = self.world_boundaries['right'] - margin
        
        if character.y < self.world_boundaries['top'] + margin:
            character.y = self.world_boundaries['top'] + margin
        elif character.y > self.world_boundaries['bottom'] - margin:
            character.y = self.world_boundaries['bottom'] - margin
    
    def limit_camera(self):
        """Limita la cámara a los bordes del mundo"""
        min_camera_x = 0
        max_camera_x = max(0, self.world_boundaries['right'] - self.screen_width)
        min_camera_y = 0
        max_camera_y = max(0, self.world_boundaries['bottom'] - self.screen_height)
        
        self.camera_x = max(min_camera_x, min(self.camera_x, max_camera_x))
        self.camera_y = max(min_camera_y, min(self.camera_y, max_camera_y))
    
    def restart_game(self):
        """Reinicia el nivel"""
        # Restaurar salud completa
        self.chaman.health = self.chaman.max_health
        self.juan.health = self.juan.max_health
        self.adan.health = self.adan.max_health
        
        # Reposicionar personajes
        self.juan.x, self.juan.y = 300, 400
        self.adan.x, self.adan.y = 400, 400
        self.chaman.x, self.chaman.y = self.screen_width//2, self.screen_height//4
        
        # Limpiar proyectiles y items
        self.chaman.projectiles = []
        self.dropped_items = []
        
        # Resetear estados
        self.game_over = False
        self.victory = False
        self.show_upgrade_menu = False
        
        print("🔄 Nivel 2 reiniciado - ¡Nueva batalla contra el Chamán!")
    
    def draw(self):
        """Dibuja todo el nivel"""
        # Fondo del nivel
        self.screen.fill(self.background_color)
        
        # Si hay imagen de fondo, dibujarla
        if self.background_image:
            self.screen.blit(self.background_image, (-self.camera_x, -self.camera_y))
        
        # Dibujar personajes (inactivo primero para orden de capas)
        if self.inactive_character.health > 0:
            if not self.inactive_attack_system.is_character_attacking():
                self.inactive_character.draw(self.screen, self.camera_x, self.camera_y)
                # Efecto de escudo si está activo
                if hasattr(self.inactive_character, 'shield_active') and self.inactive_character.shield_active:
                    self.draw_shield_effect(self.inactive_character)
        
        # Personaje activo
        if not self.active_attack_system.is_character_attacking():
            self.active_character.draw(self.screen, self.camera_x, self.camera_y)
            # Efecto de escudo si está activo
            if hasattr(self.active_character, 'shield_active') and self.active_character.shield_active:
                self.draw_shield_effect(self.active_character)
        
        # Dibujar chamán malvado
        self.chaman.draw(self.screen, self.camera_x, self.camera_y)
        
        # Dibujar gusanos adicionales del nivel 2
        self.worm_spawner.draw(self.screen, self.camera_x, self.camera_y)
        
        # Dibujar coleccionables simples (gusano muere -> PNG aparece)
        self.draw_collectibles()
        
        # Dibujar efectos de ataque
        self.juan_attack.draw(self.screen, self.camera_x, self.camera_y)
        self.adan_attack.draw(self.screen, self.camera_x, self.camera_y)
        
        # Dibujar interfaz de usuario
        self.draw_ui()
        
        # Dibujar modo editor si está activo (igual que nivel 1)
        if self.collision_manager.editor_mode:
            self.collision_manager.draw_editor_mode(self.screen, self.camera_x, self.camera_y)
        
        # Menú de mejoras simplificado
        if self.show_upgrade_menu:
            self.draw_upgrade_menu()
        
        # Dibujar estados finales
        if self.game_over:
            self.draw_game_over()
        elif self.victory:
            self.draw_victory()
        
        pygame.display.flip()
    
    def draw_shield_effect(self, character):
        """Dibuja efecto visual de escudo"""
        # Círculo pulsante alrededor del personaje
        shield_alpha = int(100 + 50 * math.sin(pygame.time.get_ticks() * 0.01))
        shield_surface = pygame.Surface((character.width + 40, character.height + 40), pygame.SRCALPHA)
        
        pygame.draw.circle(shield_surface, (0, 150, 255, shield_alpha), 
                         (character.width//2 + 20, character.height//2 + 20), 
                         character.width//2 + 15)
        
        self.screen.blit(shield_surface, 
                        (character.x - self.camera_x - 20, character.y - self.camera_y - 20))
    
    def draw_collectibles(self):
        """Dibuja manzanas y pociones simples - Gusano muere -> PNG aparece"""
        current_time = pygame.time.get_ticks()
        
        for item in self.dropped_items:
            screen_x = item['x'] - self.camera_x
            screen_y = item['y'] - self.camera_y
            
            # Solo dibujar si está en pantalla
            if (-50 < screen_x < self.screen_width + 50 and 
                -50 < screen_y < self.screen_height + 50):
                
                # Efecto de flotación
                float_offset = int(5 * math.sin(current_time * 0.005 + item['x'] * 0.01))
                
                # Usar sprite simple según tipo
                if item['type'] == 'apple':
                    self.screen.blit(self.apple_image, (screen_x, screen_y + float_offset))
                else:  # potion
                    self.screen.blit(self.potion_image, (screen_x, screen_y + float_offset))
    
    def draw_health_bars(self):
        """Dibuja las barras de salud de todos los personajes"""
        # Barras de salud de héroes
        for character in [self.juan, self.adan]:
            if character.health > 0:
                health_ratio = character.health / character.max_health
                bar_width = 80
                bar_height = 10
                
                x = character.x - self.camera_x - bar_width // 2
                y = character.y - self.camera_y - 50
                
                # Fondo
                pygame.draw.rect(self.screen, (100, 100, 100), (x, y, bar_width, bar_height))
                
                # Vida
                if health_ratio > 0.7:
                    color = (0, 255, 0)
                elif health_ratio > 0.3:
                    color = (255, 255, 0)
                else:
                    color = (255, 0, 0)
                    
                pygame.draw.rect(self.screen, color, (x, y, int(bar_width * health_ratio), bar_height))
                
                # Borde
                pygame.draw.rect(self.screen, (255, 255, 255), (x, y, bar_width, bar_height), 2)
        
        # Barra de salud del chamán
        self.chaman.draw_health_bar(self.screen, self.camera_x, self.camera_y)
        
        # Mensaje de revival si es necesario
        if self.show_revival_prompt:
            self.draw_revival_prompt()
    
    def draw_revival_prompt(self):
        """Dibuja el mensaje de revival"""
        font = pygame.font.Font(None, 48)
        prompt_text = f"Presiona E para revivir a {self.inactive_character.name}"
        prompt_surface = font.render(prompt_text, True, (255, 255, 100))
        
        # Fondo
        bg_surface = pygame.Surface((prompt_surface.get_width() + 30, prompt_surface.get_height() + 20))
        bg_surface.set_alpha(200)
        bg_surface.fill((0, 0, 0))
        
        prompt_rect = prompt_surface.get_rect(center=(self.screen_width//2, 150))
        bg_rect = bg_surface.get_rect(center=(self.screen_width//2, 150))
        
        self.screen.blit(bg_surface, bg_rect)
        self.screen.blit(prompt_surface, prompt_rect)
    
    def draw_upgrade_menu(self):
        """Dibuja el menú de selección de mejoras"""
        # Fondo del menú
        menu_width = 600
        menu_height = 400
        menu_x = (self.screen_width - menu_width) // 2
        menu_y = (self.screen_height - menu_height) // 2
        
        menu_surface = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)
        pygame.draw.rect(menu_surface, (0, 0, 0, 220), (0, 0, menu_width, menu_height))
        pygame.draw.rect(menu_surface, (255, 215, 0), (0, 0, menu_width, menu_height), 4)
        
        # Título
        font_title = pygame.font.Font(None, 72)
        font_option = pygame.font.Font(None, 48)
        
        title_text = font_title.render("🍎 MEJORA OBTENIDA 🍎", True, (255, 215, 0))
        title_rect = title_text.get_rect(center=(menu_width//2, 50))
        menu_surface.blit(title_text, title_rect)
        
        # Opciones simplificadas (3 opciones como solicitaste)
        options = [
            "1 - 🚀 Velocidad de Movimiento (+0.8)",
            "2 - ⚔️ Daño de Ataque (+8)",
            "3 - ❤️ Vida Máxima (+25)"
        ]
        
        for i, option in enumerate(options):
            option_text = font_option.render(option, True, (200, 255, 200))
            option_rect = option_text.get_rect(center=(menu_width//2, 120 + i * 60))
            menu_surface.blit(option_text, option_rect)
        
        # Instrucciones
        instruction_text = font_option.render("Presiona el número de la mejora que deseas", True, (200, 200, 200))
        instruction_rect = instruction_text.get_rect(center=(menu_width//2, 350))
        menu_surface.blit(instruction_text, instruction_rect)
        
        self.screen.blit(menu_surface, (menu_x, menu_y))
    
    def draw_ui(self):
        """Dibuja interfaz de usuario idéntica al nivel 1"""
        font = pygame.font.Font(None, 72)
        font_small = pygame.font.Font(None, 48)
        font_large = pygame.font.Font(None, 96)  # Para contador de enemigos
        
        # UI normal del juego
        # Personaje activo con icono
        active_text = font.render(f"🎮 {self.active_character.name}", True, (255, 255, 255))
        self.screen.blit(active_text, (20, 20))
        
        # Vidas con barras gráficas y estadísticas mejoradas - IDÉNTICO AL NIVEL 1
        juan_health_text = font_small.render(f"Juan: {self.juan.health}/{self.juan.max_health}", 
                                       True, (255, 255, 255) if self.juan.health > 0 else (255, 100, 100))
        self.screen.blit(juan_health_text, (20, 90))
        
        # Estadísticas adicionales de Juan
        juan_speed = getattr(self.juan, 'speed', 5)
        juan_damage = getattr(self.juan, 'base_damage', getattr(self.juan, 'attack_damage', 15))
        juan_stats = font_small.render(f"⚡{juan_speed:.1f} ⚔️{juan_damage}", True, (200, 200, 200))
        self.screen.blit(juan_stats, (20, 120))
        
        adan_health_text = font_small.render(f"Adán: {self.adan.health}/{self.adan.max_health}", 
                                       True, (255, 255, 255) if self.adan.health > 0 else (255, 100, 100))
        self.screen.blit(adan_health_text, (300, 90))
        
        # Estadísticas adicionales de Adán
        adan_speed = getattr(self.adan, 'speed', 5)
        adan_damage = getattr(self.adan, 'base_damage', getattr(self.adan, 'attack_damage', 40))
        adan_stats = font_small.render(f"⚡{adan_speed:.1f} ⚔️{adan_damage}", True, (200, 200, 200))
        self.screen.blit(adan_stats, (300, 120))
        
        # Vida del Chamán - AHORA EN NÚMEROS ABSOLUTOS como Juan y Adán
        chaman_health_text = font_small.render(f"👹 Chamán: {self.chaman.health}/{self.chaman.max_health}", 
                                        True, (255, 100, 255) if self.chaman.health > 0 else (255, 100, 100))
        self.screen.blit(chaman_health_text, (600, 90))
        
        # Estadísticas del Chamán
        chaman_stats = font_small.render(f"⚡{self.chaman.speed:.1f} ⚔️{self.chaman.damage}", True, (200, 200, 200))
        self.screen.blit(chaman_stats, (600, 120))
        
        # Mostrar progreso de gusanos (informativo) - posición ajustada
        living_worms = len([worm for worm in self.worm_spawner.worms if worm.alive])
        progress_text = font_small.render(f"🐛 Spawneados: {self.worm_spawner.total_spawned}/{self.worm_spawner.max_worms} | Vivos: {living_worms}", 
                                        True, (200, 200, 200))
        self.screen.blit(progress_text, (20, 160))
        
        # Mostrar número de drops disponibles
        active_drops = len([drop for drop in self.dropped_items if not drop.get('collected', False)])
        if active_drops > 0:
            drops_text = font_small.render(f"💎 Drops disponibles: {active_drops}", True, (255, 215, 0))
            self.screen.blit(drops_text, (20, 190))
        
        # Indicador de escudo
        for i, char in enumerate([self.juan, self.adan]):
            if getattr(char, 'shield_active', False):
                shield_text = font_small.render(f"🛡️ {char.name}", True, (100, 200, 255))
                self.screen.blit(shield_text, (600 + i * 200, 160))
        
        # Controles - Simplificados
        font_small_controls = pygame.font.Font(None, 36)
        controls = [
            "🎮 CONTROLES NIVEL 2:",
            "WASD - Mover | ESPACIO - Ataque",
            "TAB - Cambiar | E - Revivir",
            "ESC - Salir"
        ]
        
        for i, control in enumerate(controls):
            control_surface = font_small_controls.render(control, True, (255, 255, 255))
            self.screen.blit(control_surface, (30, self.screen_height - 200 + i * 40))
    
    def draw_game_over(self):
        """Dibuja la pantalla de game over"""
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        font_huge = pygame.font.Font(None, 150)
        font_large = pygame.font.Font(None, 84)
        
        # Mensaje principal
        text = font_huge.render("GAME OVER", True, (255, 0, 0))
        text_rect = text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 80))
        self.screen.blit(text, text_rect)
        
        # Mensaje secundario
        subtitle = font_large.render("El Chamán Malvado ha triunfado...", True, (255, 100, 100))
        subtitle_rect = subtitle.get_rect(center=(self.screen_width//2, self.screen_height//2 + 20))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Instrucciones
        restart_text = font_large.render("Presiona R para reintentar", True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(self.screen_width//2, self.screen_height//2 + 120))
        self.screen.blit(restart_text, restart_rect)
    
    def draw_victory(self):
        """Dibuja la pantalla de victoria"""
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((255, 215, 0, 50))  # Dorado translúcido
        self.screen.blit(overlay, (0, 0))
        
        font_huge = pygame.font.Font(None, 150)
        font_large = pygame.font.Font(None, 84)
        
        # Mensaje principal
        text = font_huge.render("¡VICTORIA ÉPICA!", True, (255, 215, 0))
        text_rect = text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 100))
        self.screen.blit(text, text_rect)
        
        # Mensaje secundario
        subtitle = font_large.render("¡Has derrotado al Chamán Malvado!", True, (200, 255, 200))
        subtitle_rect = subtitle.get_rect(center=(self.screen_width//2, self.screen_height//2))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Estadísticas de la batalla
        stats = [
            f"Mejoras obtenidas: {sum(self.upgrades.values())}",
            f"Vida restante: {self.active_character.health}/{self.active_character.max_health}"
        ]
        
        for i, stat in enumerate(stats):
            stat_surface = font_large.render(stat, True, (255, 255, 255))
            stat_rect = stat_surface.get_rect(center=(self.screen_width//2, self.screen_height//2 + 80 + i * 50))
            self.screen.blit(stat_surface, stat_rect)
        
        # Instrucciones
        restart_text = font_large.render("Presiona R para volver a jugar", True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(self.screen_width//2, self.screen_height//2 + 200))
        self.screen.blit(restart_text, restart_rect)
    
    def run(self):
        """Ejecuta el nivel 2"""
        print("🎮 Iniciando Nivel 2 - Batalla contra el Chamán Malvado...")
        
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps)
        
        print("👋 Saliendo del Nivel 2...")

# Solo ejecutar si se llama directamente
if __name__ == "__main__":
    try:
        nivel2 = Nivel2('juan')
        nivel2.run()
    except Exception as e:
        print(f"❌ Error ejecutando Nivel 2: {e}")
    finally:
        pygame.quit()
        sys.exit()