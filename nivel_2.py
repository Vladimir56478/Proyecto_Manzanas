import pygame
import sys
from PIL import Image
import requests
from io import BytesIO
import math
import random

# Importar configuración y utilidades
from config import *
from utils import *

# Importar clases necesarias
from adan_character_animation import AdanCharacter
from juan_character_animation import JuanCharacter
from adan_attacks import AdanAttack
from juan_attacks import JuanAttack
from chaman_malvado import ChamanMalvado
from character_ai import CharacterAI
from audio_manager import get_audio_manager

# Clase CollisionBlock para el Nivel 2
class CollisionBlock:
    """Un bloque de colisión invisible para el editor"""
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
    
    def draw_editor(self, screen, camera_x, camera_y):
        """Dibuja el bloque en modo editor"""
        # Calcular posición en pantalla
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Solo dibujar si está visible en pantalla
        if (-self.width <= screen_x <= SCREEN_WIDTH and 
            -self.height <= screen_y <= SCREEN_HEIGHT):
            
            # Fondo semitransparente
            block_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            block_surface.fill((255, 0, 0, 100))
            screen.blit(block_surface, (screen_x, screen_y))
            
            # Borde del bloque
            pygame.draw.rect(screen, (255, 0, 0), 
                           (screen_x, screen_y, self.width, self.height), 2)
from loading_screen import LoadingScreen
from items_system import ItemManager
from worm_enemy import WormSpawner  # Agregar gusanos al nivel 2
from sound_generator import get_sound_generator, play_sound

# Clase de colisión común (movida a utils para evitar duplicación)

class StaticItemLevel2:
    """Representa un item estático en el mapa nivel 2 que se activa con E"""
    def __init__(self, x, y, item_type):
        self.x = x
        self.y = y
        self.item_type = item_type  # 'apple' o 'potion'
        self.width = 20
        self.height = 20
        self.active = False  # Inicia inactivo para spawn paulatino
        self.cooldown = 0
        self.respawn_time = 1800  # 30 segundos a 60 FPS
        self.animation_offset = 0
        self.spawn_time = pygame.time.get_ticks()
        self.spawn_delay = 0  # Delay para aparición paulatina
        
    def update(self):
        """Actualiza el item con animación y spawn paulatino"""
        current_time = pygame.time.get_ticks()
        
        # Spawn inicial paulatino
        if not self.active and self.spawn_delay > 0 and current_time >= self.spawn_delay:
            self.active = True
            print(f"✨ Item {self.item_type} activado en nivel 2")
        
        # Animación de flotación solo si está activo
        if self.active:
            self.animation_offset = int(3 * math.sin(current_time * 0.005))
        
        return True
    
    def use_item(self):
        """Usa el item y lo pone en cooldown"""
        if self.active:
            self.active = False
            self.cooldown = self.respawn_time
            return True
        return False
    
    def draw(self, screen, camera_x, camera_y, game_apple_image=None, game_potion_image=None):
        """Dibuja el item estático en pantalla"""
        # NO dibujar si está inactivo o recolectado
        if not self.active or getattr(self, 'collected', False):
            return
            
        screen_pos = (self.x - camera_x, self.y - camera_y + self.animation_offset)
        
        # Verificar visibilidad
        screen_width, screen_height = screen.get_size()
        if not (-50 < screen_pos[0] < screen_width + 50 and -50 < screen_pos[1] < screen_height + 50):
            return
        
        # Dibujar sprite del item
        image = game_apple_image if self.item_type == 'apple' else game_potion_image
        if image:
            screen.blit(image, screen_pos)
        else:
            # Fallback: rectángulo de color
            color = (255, 100, 100) if self.item_type == 'apple' else (100, 100, 255)
            pygame.draw.rect(screen, color, (*screen_pos, self.width, self.height))
        
        # Indicador "E" simplificado
        font = pygame.font.Font(None, 24)
        text = font.render("E", True, (255, 255, 255))
        text_pos = (screen_pos[0] + self.width//2 - 8, screen_pos[1] - 18)
        pygame.draw.rect(screen, (0, 0, 0, 120), (*text_pos, 16, 16))
        screen.blit(text, text_pos)
    
    def get_rect(self):
        """Obtiene el rectángulo para detección de colisiones"""
        return pygame.Rect(self.x, self.y, self.width, self.height)

# CollisionManager completo para Nivel 2 (igual que Nivel 1)
class CollisionManagerLevel2:
    """Maneja las colisiones con bloques invisibles - NIVEL 2"""
    def __init__(self, world_width=5940, world_height=1080):
        self.blocks = []
        self.editor_mode = False
        self.block_size = 32  # CHARACTER_SIZE[0] // 2
        self.editor_cursor_x = 100
        self.editor_cursor_y = 100
        self.world_width = world_width
        self.world_height = world_height
        
        # Nuevo sistema de editor con arrastre
        self.mouse_pressed = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.drag_current_x = 0
        self.drag_current_y = 0
        self.is_dragging = False
        
        # Sistema de persistencia
        self.load_collision_data()
    
    def load_collision_data(self):
        """Carga bloques de colisión desde archivo"""
        try:
            filename = "collision_data_nivel2.txt"
            with open(filename, 'r') as f:
                for line in f:
                    if line.strip():
                        x, y, w, h = map(int, line.strip().split(','))
                        self.blocks.append(CollisionBlock(x, y, w, h))
            print(f"🧱 Bloques de colisión cargados para Nivel 2: {len(self.blocks)} bloques")
        except Exception as e:
            print(f"⚠️ Error cargando bloques Nivel 2: {e}")
            self.blocks = []
    
    def save_collision_data(self, silent=True):
        """Guarda bloques de colisión en archivo"""
        try:
            filename = "collision_data_nivel2.txt"
            with open(filename, 'w') as f:
                for block in self.blocks:
                    f.write(f"{block.x},{block.y},{block.width},{block.height}\n")
            if not silent:
                print(f"💾 Bloques guardados en {filename}: {len(self.blocks)} bloques")
        except Exception as e:
            print(f"❌ Error guardando bloques: {e}")
    
    def add_block(self, x, y):
        """Añade un bloque de colisión y guarda automáticamente"""
        # Alinear a la grilla
        grid_x = (x // self.block_size) * self.block_size
        grid_y = (y // self.block_size) * self.block_size
        
        # Verificar si ya existe un bloque en esa posición
        for block in self.blocks:
            if block.x == grid_x and block.y == grid_y:
                return False
        
        self.blocks.append(CollisionBlock(grid_x, grid_y, self.block_size, self.block_size))
        print(f"✅ Bloque añadido en ({grid_x}, {grid_y})")
        
        # Guardar automáticamente
        self.save_collision_data(silent=True)
        return True
    
    def remove_block(self, x, y):
        """Remueve un bloque de colisión y guarda automáticamente"""
        grid_x = (x // self.block_size) * self.block_size
        grid_y = (y // self.block_size) * self.block_size
        
        for block in self.blocks[:]:
            if block.x == grid_x and block.y == grid_y:
                self.blocks.remove(block)
                print(f"🗑️ Bloque eliminado en ({grid_x}, {grid_y})")
                
                # Guardar automáticamente
                self.save_collision_data(silent=True)
                return True
        return False
    
    def check_collision(self, character_rect):
        """Verifica colisión con bloques"""
        for block in self.blocks:
            if character_rect.colliderect(block.rect):
                return True
        return False
    
    def can_move_to(self, character, new_x, new_y):
        """Verifica si un personaje puede moverse a una posición"""
        # Crear rectángulo temporal en la nueva posición
        test_rect = pygame.Rect(new_x, new_y, 100, 100)  # 64 * 1.56 = 100
        
        # Verificar colisión con bloques
        if self.check_collision(test_rect):
            return False
        
        # LÍMITES ESTRICTOS DEL MUNDO - NO PUEDE SALIR DEL PNG
        if (new_x < 0 or new_x + 100 > self.world_width or 
            new_y < 0 or new_y + 100 > self.world_height):
            return False
        
        return True
    
    def draw_editor_mode(self, screen, camera_x, camera_y):
        """Dibuja el modo editor"""
        if not self.editor_mode:
            return
        
        # Dibujar todos los bloques
        for block in self.blocks:
            block.draw_editor(screen, camera_x, camera_y)
        
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
        
        # Dibujar rectángulo de arrastre si se está arrastrando
        if self.is_dragging and self.mouse_pressed:
            rect_start_x = min(self.drag_start_x, self.drag_current_x) - camera_x
            rect_start_y = min(self.drag_start_y, self.drag_current_y) - camera_y
            rect_width = abs(self.drag_current_x - self.drag_start_x)
            rect_height = abs(self.drag_current_y - self.drag_start_y)
            
            # Alinear a la grilla visualmente
            grid_start_x = ((min(self.drag_start_x, self.drag_current_x) // self.block_size) * self.block_size) - camera_x
            grid_start_y = ((min(self.drag_start_y, self.drag_current_y) // self.block_size) * self.block_size) - camera_y
            grid_width = ((abs(self.drag_current_x - self.drag_start_x) // self.block_size) + 1) * self.block_size
            grid_height = ((abs(self.drag_current_y - self.drag_start_y) // self.block_size) + 1) * self.block_size
            
            # Rectángulo de previsualización
            preview_surface = pygame.Surface((grid_width, grid_height), pygame.SRCALPHA)
            preview_surface.fill((0, 255, 0, 100))
            screen.blit(preview_surface, (grid_start_x, grid_start_y))
            pygame.draw.rect(screen, (0, 255, 0), (grid_start_x, grid_start_y, grid_width, grid_height), 3)
    
    def handle_editor_input(self, keys_pressed, keys_just_pressed, mouse_events, camera_x, camera_y):
        """Maneja input del modo editor con sistema de arrastre - IGUAL QUE NIVEL 1"""
        if not self.editor_mode:
            return
        
        # Manejar eventos del mouse
        for event in mouse_events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Click izquierdo
                    self.mouse_pressed = True
                    mouse_world_x = event.pos[0] + camera_x
                    mouse_world_y = event.pos[1] + camera_y
                    self.drag_start_x = mouse_world_x
                    self.drag_start_y = mouse_world_y
                    self.drag_current_x = mouse_world_x
                    self.drag_current_y = mouse_world_y
                    self.is_dragging = False
                    
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.mouse_pressed:  # Soltar click izquierdo
                    self.mouse_pressed = False
                    if self.is_dragging:
                        # Crear rectángulo de bloques
                        self.create_block_rectangle()
                    else:
                        # Click simple - agregar un bloque
                        grid_x = (self.drag_start_x // self.block_size) * self.block_size
                        grid_y = (self.drag_start_y // self.block_size) * self.block_size
                        if self.add_block(grid_x, grid_y):
                            print(f"🔧 Bloque guardado automáticamente")
                    self.is_dragging = False
                    
            elif event.type == pygame.MOUSEMOTION:
                if self.mouse_pressed:
                    mouse_world_x = event.pos[0] + camera_x
                    mouse_world_y = event.pos[1] + camera_y
                    self.drag_current_x = mouse_world_x
                    self.drag_current_y = mouse_world_y
                    
                    # Detectar si se está arrastrando
                    distance = abs(self.drag_current_x - self.drag_start_x) + abs(self.drag_current_y - self.drag_start_y)
                    if distance > 10:  # Threshold para detectar arrastre
                        self.is_dragging = True
        
        # Teclas para eliminar (mantener funcionalidad de teclado)
        if keys_just_pressed.get(pygame.K_BACKSPACE, False):
            mouse_pos = pygame.mouse.get_pos()
            mouse_world_x = mouse_pos[0] + camera_x
            mouse_world_y = mouse_pos[1] + camera_y
            grid_x = (mouse_world_x // self.block_size) * self.block_size
            grid_y = (mouse_world_y // self.block_size) * self.block_size
            if self.remove_block(grid_x, grid_y):
                print(f"🗑️ Bloque eliminado y guardado automáticamente")
    
    def create_block_rectangle(self):
        """Crea un rectángulo de bloques desde drag_start hasta drag_current"""
        start_x = min(self.drag_start_x, self.drag_current_x)
        end_x = max(self.drag_start_x, self.drag_current_x)
        start_y = min(self.drag_start_y, self.drag_current_y)
        end_y = max(self.drag_start_y, self.drag_current_y)
        
        # Alinear a la grilla
        start_grid_x = (start_x // self.block_size) * self.block_size
        end_grid_x = (end_x // self.block_size) * self.block_size
        start_grid_y = (start_y // self.block_size) * self.block_size
        end_grid_y = (end_y // self.block_size) * self.block_size
        
        blocks_added = 0
        for x in range(int(start_grid_x), int(end_grid_x) + self.block_size, self.block_size):
            for y in range(int(start_grid_y), int(end_grid_y) + self.block_size, self.block_size):
                # Verificar si ya existe un bloque en esta posición
                block_exists = any(block.x == x and block.y == y for block in self.blocks)
                if not block_exists:
                    new_block = CollisionBlock(x, y, self.block_size, self.block_size)
                    self.blocks.append(new_block)
                    blocks_added += 1
        
        if blocks_added > 0:
            print(f"✅ {blocks_added} bloques agregados en rectángulo")
            # Guardar automáticamente después del rectángulo completo
            self.save_collision_data(silent=True)
            print("💾 Rectángulo guardado automáticamente")
    
    def auto_save(self):
        """Método de guardado automático para compatibilidad"""
        self.save_collision_data(silent=True)


class Nivel2:
    def __init__(self, selected_character='juan', level1_stats=None):
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
        
        # Cargar escenario completo del nivel 2 desde GitHub
        self.background_color = (15, 25, 15)  # Fallback
        self.github_background_url = "https://github.com/user-attachments/assets/591f8b6d-7a10-4cb5-ae8a-6997fd21ea65"
        self.background_image = self.load_background_from_github()
        
        # Configurar dimensiones del mundo completo basadas en el PNG
        if self.background_image:
            self.world_width = self.background_image.get_width()
            self.world_height = self.background_image.get_height()
            print(f"🌍 Mundo del Nivel 2: {self.world_width}x{self.world_height}")
        else:
            # Dimensiones grandes por defecto para permitir exploración vertical
            self.world_width = 1920
            self.world_height = 3000  # Altura aumentada para exploración vertical
        
        # Cargar personajes con transferencia de estadísticas del nivel 1 o stats base
        
        # Juan - Transferir progreso del nivel 1 o usar stats base
        self.juan = JuanCharacter(300, 400)
        if level1_stats and 'juan' in level1_stats:
            # Transferir estadísticas del nivel 1
            juan_stats = level1_stats['juan']
            self.juan.max_health = juan_stats.get('max_health', 100)
            self.juan.health = juan_stats.get('health', self.juan.max_health)
            self.juan.speed = juan_stats.get('speed', 6.5)
            self.juan.damage = juan_stats.get('damage', 22)
            print(f"📊 Juan - Stats transferidos del Nivel 1: Vida {self.juan.health}/{self.juan.max_health}, Velocidad {self.juan.speed}, Daño {self.juan.damage}")
        else:
            # Stats base si se juega directamente el nivel 2
            self.juan.max_health = 100
            self.juan.health = 100
            self.juan.speed = 6.5
            self.juan.damage = 22
            print(f"📊 Juan - Stats base: Vida {self.juan.health}/{self.juan.max_health}, Velocidad {self.juan.speed}, Daño {self.juan.damage}")
        self.juan.name = "Juan"
        
        # Adán - Transferir progreso del nivel 1 o usar stats base
        self.adan = AdanCharacter(400, 400)
        if level1_stats and 'adan' in level1_stats:
            # Transferir estadísticas del nivel 1
            adan_stats = level1_stats['adan']
            self.adan.max_health = adan_stats.get('max_health', 125)
            self.adan.health = adan_stats.get('health', self.adan.max_health)
            self.adan.speed = adan_stats.get('speed', 5.5)
            self.adan.damage = adan_stats.get('damage', 28)
            print(f"📊 Adán - Stats transferidos del Nivel 1: Vida {self.adan.health}/{self.adan.max_health}, Velocidad {self.adan.speed}, Daño {self.adan.damage}")
        else:
            # Stats base si se juega directamente el nivel 2
            self.adan.max_health = 125
            self.adan.health = 125
            self.adan.speed = 5.5
            self.adan.damage = 28
            print(f"📊 Adán - Stats base: Vida {self.adan.health}/{self.adan.max_health}, Velocidad {self.adan.speed}, Daño {self.adan.damage}")
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
        
        # Sistema de cámara ESTÁTICA para nivel 2 - NO SE MUEVE
        self.camera_x = 0
        self.camera_y = 0
        self.camera_follow_enabled = False  # Cámara estática
        self.camera_fixed = True  # Bandera para cámara fija
        
        # Sistema de colisiones - NIVEL 2 CON LÍMITES ESTRICTOS
        self.collision_manager = CollisionManagerLevel2(self.world_width, self.world_height)
        
        print(f"🛠️ CONTROLES DEL EDITOR NIVEL 2:")
        print(f"   F1: Activar/Desactivar modo editor")
        print(f"   Click y arrastrar: Crear rectángulo de bloques")  
        print(f"   Click simple: Colocar bloque individual")
        print(f"   Backspace: Eliminar bloque en cursor del mouse")
        print(f"   💾 GUARDADO AUTOMÁTICO: Cada bloque se guarda instantáneamente")
        print(f"   📁 Archivo: collision_data_nivel2.txt")
            
        self.keys_last_frame = list(pygame.key.get_pressed())  # Para detectar pulsaciones
        self.game_paused = False  # Sistema de pausa para editor
        
        # Estados del juego
        self.game_over = False
        self.victory = False
        self.switch_cooldown = 0
        self.revival_key_pressed = False
        self.show_revival_prompt = False
        self.revival_distance = 100
        
        # Sistema de coleccionables distribuidos (igual que nivel 1)
        self.dropped_items = []  # Items drops de enemigos
        self.static_items = []   # Items distribuidos por el mapa
        self.create_simple_collectible_images()  # Crear sprites simples
        self.setup_static_items_level2()  # Configurar sistema de spawn distribuido
        
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
        # Dimensiones expandidas para PNG completo con exploración vertical
        self.world_boundaries = {
            'left': 0,
            'right': 1920,
            'top': 0,
            'bottom': 2160  # Doble altura para exploración completa vertical
        }
        
        # Listo para comenzar
        
        print(f"🎮 Nivel 2 iniciado - Personaje activo: {self.active_character.name}")
        print(f"🤖 IA controlando: {self.inactive_character.name}")
        print(f"👹 Chamán Malvado despertado con {self.chaman.health} HP")
    
    def load_background_from_github(self):
        """Carga el fondo completo del Nivel 2 desde GitHub"""
        try:
            print("📥 Descargando fondo completo del Nivel 2 desde GitHub...")
            response = requests.get(self.github_background_url, timeout=15)
            response.raise_for_status()
            
            image_data = BytesIO(response.content)
            pil_image = Image.open(image_data)
            
            # Información de la imagen original
            original_width, original_height = pil_image.size
            print(f"📐 Dimensiones del PNG completo: {original_width}x{original_height}")
            
            # Convertir a formato pygame manteniendo dimensiones originales
            pil_image = pil_image.convert('RGB')
            image_data = pil_image.tobytes()
            
            background = pygame.image.fromstring(image_data, pil_image.size, 'RGB')
            background = background.convert()
            
            print(f"✅ Fondo completo del Nivel 2 cargado: {original_width}x{original_height}")
            return background
            
        except Exception as e:
            print(f"❌ Error cargando fondo desde GitHub: {e}")
            print("🎨 Usando fondo de respaldo...")
            return self.create_fallback_background()
    
    def create_fallback_background(self):
        """Crea un fondo de respaldo para el Nivel 2"""
        print("🎨 Creando fondo de respaldo del Nivel 2...")
        background = pygame.Surface((self.world_width, self.world_height))
        
        # Gradiente oscuro para ambiente del chamán
        for y in range(self.world_height):
            intensity = 10 + (y * 40) // self.world_height
            color = (intensity, intensity + 10, intensity)
            pygame.draw.line(background, color, (0, y), (self.world_width, y))
        
        # Elementos decorativos oscuros
        for _ in range(100):
            x = random.randint(0, self.world_width)
            y = random.randint(0, self.world_height)
            size = random.randint(15, 40)
            color = (random.randint(20, 60), random.randint(10, 40), random.randint(10, 40))
            pygame.draw.circle(background, color, (x, y), size)
        
        return background
    
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
            if hasattr(self.chaman, 'attack_system') and hasattr(self.chaman.attack_system, 'attack_frames'):
                try:
                    for direction in self.chaman.attack_system.attack_frames:
                        for i, frame in enumerate(self.chaman.attack_system.attack_frames[direction]):
                            original_size = frame.get_size()
                            new_size = (int(original_size[0] * scale_factor), int(original_size[1] * scale_factor))
                            self.chaman.attack_system.attack_frames[direction][i] = pygame.transform.scale(frame, new_size)
                except (AttributeError, KeyError):
                    pass  # Si no tiene attack_frames o falla, continuar
            
            print(f"✅ Chamán escalado {scale_factor}x para mejor jugabilidad")
        except Exception as e:
            print(f"⚠️ Error escalando chamán: {e}")
    
    def create_simple_collectible_images(self):
        """Crea sprites simples para manzanas y pociones - Reducidos para mejor FPS"""
        # Manzana simple pero visible (reducida a 20x20)
        self.apple_image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.apple_image, (220, 50, 50), (10, 11), 8)
        pygame.draw.circle(self.apple_image, (255, 100, 100), (8, 9), 6)
        pygame.draw.rect(self.apple_image, (139, 69, 19), (9, 3, 3, 6))
        pygame.draw.ellipse(self.apple_image, (34, 139, 34), (7, 2, 6, 4))
        pygame.draw.circle(self.apple_image, (255, 200, 200, 80), (7, 7), 4)
        
        # Poción simple pero visible (reducida a 20x20)
        self.potion_image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.rect(self.potion_image, (100, 100, 100), (8, 9, 4, 8))
        pygame.draw.ellipse(self.potion_image, (20, 100, 220), (7, 11, 6, 6))
        pygame.draw.rect(self.potion_image, (50, 150, 255), (9, 7, 2, 7))
        pygame.draw.circle(self.potion_image, (100, 200, 255), (10, 13), 2)
        pygame.draw.circle(self.potion_image, (150, 220, 255, 60), (10, 13), 5)
    
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
    
    def setup_static_items_level2(self):
        """Configura sistema de spawn de items distribuidos para nivel 2 - igual que nivel 1"""
        # Configurar spawn temporal de items (hasta 10 total)
        self.max_items = 10
        self.items_spawned = 0
        self.last_item_spawn_time = pygame.time.get_ticks()
        self.item_spawn_interval = 5000  # 5 segundos entre cada item
        
        # Lista de tipos de items con probabilidades
        self.item_types = [
            ('apple', 0.6),  # 60% manzanas
            ('potion', 0.4)  # 40% pociones
        ]
        
        print(f"✅ Sistema de spawn distribuido Nivel 2 configurado - 1 item cada 5 segundos (máximo {self.max_items})")
        print("📍 Items aparecerán aleatoriamente por todo el mapa evitando bloques de colisión")
    
    def spawn_random_item_level2(self):
        """Crea un item en una posición aleatoria válida del mapa nivel 2"""
        if self.items_spawned >= self.max_items:
            return None
            
        current_time = pygame.time.get_ticks()
        if current_time - self.last_item_spawn_time < self.item_spawn_interval:
            return None
        
        # Intentar encontrar una posición válida (máximo 50 intentos)
        attempts = 0
        max_attempts = 50
        
        while attempts < max_attempts:
            # Generar posición aleatoria dentro del mundo (con margen)
            x = random.randint(100, self.world_boundaries['right'] - 100)
            y = random.randint(100, self.world_boundaries['bottom'] - 100)
            
            # Verificar que no esté en un bloque de colisión
            item_rect = pygame.Rect(x, y, 20, 20)  # Tamaño del item
            
            # Revisar colisión con bloques invisibles
            collision_found = False
            for block in self.collision_manager.blocks:
                if item_rect.colliderect(block.rect):
                    collision_found = True
                    break
            
            # Verificar que no esté muy cerca de otros items existentes
            too_close = False
            for existing_item in self.static_items:
                if existing_item.active:
                    dist = math.sqrt((x - existing_item.x)**2 + (y - existing_item.y)**2)
                    if dist < 150:  # Mínimo 150 píxeles de separación
                        too_close = True
                        break
            
            # Verificar que no esté muy cerca de personajes o enemigos
            for char in [self.juan, self.adan, self.chaman]:
                dist = math.sqrt((x - char.x)**2 + (y - char.y)**2)
                if dist < 100:  # Mínimo 100 píxeles de los personajes/jefes
                    too_close = True
                    break
            
            if not collision_found and not too_close:
                # Posición válida encontrada
                # Seleccionar tipo de item basado en probabilidades
                rand_val = random.random()
                cumulative_prob = 0
                selected_type = 'apple'  # Por defecto
                
                for item_type, prob in self.item_types:
                    cumulative_prob += prob
                    if rand_val <= cumulative_prob:
                        selected_type = item_type
                        break
                
                # Crear item usando clase StaticItem local
                new_item = StaticItemLevel2(x, y, selected_type)
                new_item.active = True  # Activar inmediatamente
                new_item.spawn_time = current_time
                self.static_items.append(new_item)
                
                self.items_spawned += 1
                self.last_item_spawn_time = current_time
                
                print(f"✨ Item {selected_type} spawneado en nivel 2 ({x}, {y}) - {self.items_spawned}/{self.max_items}")
                return new_item
            
            attempts += 1
        
        print(f"⚠️ No se pudo encontrar posición válida para item nivel 2 después de {max_attempts} intentos")
        return None
    
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
        
        # Recopilar todos los eventos para el editor
        mouse_events = []
        
        for event in pygame.event.get():
            # Guardar eventos del mouse para el editor
            if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION]:
                mouse_events.append(event)
                
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_over or self.victory:
                        return False  # Salir en pantallas finales
                    else:
                        # Toggle pausa durante el juego
                        self.game_paused = not self.game_paused
                        print(f"⏸️ Juego {'pausado' if self.game_paused else 'reanudado'}")
                elif event.key == pygame.K_F1:
                    # Toggle modo editor (igual que nivel 1)
                    self.collision_manager.editor_mode = not self.collision_manager.editor_mode
                    mode = "activado" if self.collision_manager.editor_mode else "desactivado"
                    print(f"🛠️ Modo editor {mode} en Nivel 2")
                    if self.collision_manager.editor_mode:
                        print("🔄 GUARDADO AUTOMÁTICO ACTIVADO")
                        print("✨ Todos los bloques se guardan instantáneamente")
                        print("📁 Archivo: collision_data_nivel2.txt")
                    else:
                        # Guardado final al salir del editor
                        try:
                            self.collision_manager.auto_save()
                            print(f"💾 Configuración final guardada: {len(self.collision_manager.blocks)} bloques")
                        except:
                            print("💾 Guardado manual de bloques de colisión")
                elif event.key == pygame.K_p:
                    # Tecla de pausa
                    self.game_paused = not self.game_paused
                    if self.game_paused:
                        print("⏸️ Juego pausado - Presiona P para continuar")
                    else:
                        print("▶️ Juego reanudado")
                elif event.key == pygame.K_m and self.game_paused:
                    # Ir al menú principal desde pausa
                    print("🏠 Regresando al menú principal desde pausa...")
                    return "MAIN_MENU"
                elif event.key == pygame.K_TAB and not self.game_over and not self.victory and not self.collision_manager.editor_mode and not self.game_paused:
                    if self.switch_cooldown <= 0 and self.juan.health > 0 and self.adan.health > 0:
                        self.switch_character()
                        self.switch_cooldown = 30
                elif event.key == pygame.K_r and (self.game_over or self.victory):
                    self.restart_game()
                elif event.key == pygame.K_m and (self.game_over or self.victory or self.game_paused):
                    print("📋 Volviendo al menú principal...")
                    return "MAIN_MENU"
                elif event.key == pygame.K_SPACE and not self.game_over and not self.victory and not self.collision_manager.editor_mode and not self.game_paused:
                    # SONIDO: Ataque básico
                    play_sound('attack_basic', 0.8)
                    # Ataque básico
                    self.perform_basic_attack()
                elif event.key == pygame.K_x and not self.game_over and not self.victory and not self.collision_manager.editor_mode and not self.game_paused:
                    # ELIMINADO: Ataque especial de bolitas
                    print("❌ Ataque especial deshabilitado")
                # Manejo del menú de mejoras - EXACTAMENTE IGUAL QUE NIVEL 1 (3 opciones)
                elif self.show_upgrade_menu and event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    # SONIDO: Selección de mejora
                    play_sound('upgrade_select', 0.8)
                    self.handle_upgrade_selection(event.key)
                    self.show_upgrade_menu = False
                    self.game_paused = False
        
        # Manejo del modo editor - PAUSAR JUEGO
        if self.collision_manager.editor_mode:
            self.game_paused = True
            self.collision_manager.handle_editor_input(keys_pressed, keys_just_pressed, mouse_events, self.camera_x, self.camera_y)
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
            
            # Interacción con items estáticos distribuidos
            if e_key_pressed and not self.revival_key_pressed:
                self.check_static_item_interaction_level2()
        
        self.revival_key_pressed = e_key_pressed
        return True
    
    def switch_character(self):
        """Cambia entre Juan y Adán manteniendo configuración avanzada de IA"""
        if self.switch_cooldown <= 0 and not self.game_over and not self.victory:
            # NUEVO: Verificar que el personaje inactivo esté vivo antes de cambiar
            if self.inactive_character.health <= 0:
                print(f"❌ No puedes cambiar a {self.inactive_character.name} - está muerto")
                print(f"💊 Revívelo primero con 'E' cuando estés cerca")
                return
            
            # SONIDO: Cambio de personaje
            play_sound('character_switch', 0.7)
            # Cambiar personajes
            self.active_character, self.inactive_character = self.inactive_character, self.active_character
            self.active_attack_system, self.inactive_attack_system = self.inactive_attack_system, self.active_attack_system
            
            # Reconfigurar IA con parámetros mejorados
            self.inactive_ai = CharacterAI(self.inactive_character, self.active_character)
            # Mantener mejoras de IA - IDÉNTICO AL NIVEL 1
            self.inactive_ai.detection_range = 400
            self.inactive_ai.attack_range = 150
            
            self.switch_cooldown = 60  # Cooldown para evitar spam
            print(f"🔄 Cambiado a: {self.active_character.name}")
            
            # Posicionar nuevo personaje inactivo cerca del activo
            offset_x = 80
            self.inactive_character.x = self.active_character.x + offset_x
            self.inactive_character.y = self.active_character.y
        print(f"🔄 Cambiado a: {self.active_character.name}")
    
    def check_static_item_interaction_level2(self):
        """Verifica si el jugador puede interactuar con items estáticos nivel 2"""
        player_rect = pygame.Rect(self.active_character.x, self.active_character.y, 64, 64)
        
        for item in self.static_items:
            if item.active and not getattr(item, 'collected', False):
                item_rect = item.get_rect()
                if player_rect.colliderect(item_rect):
                    self.collect_static_item_level2(item, self.active_character)
                    break
    
    def collect_static_item_level2(self, item, character):
        """Recolecta un item estático nivel 2 - EXACTAMENTE IGUAL QUE NIVEL 1"""
        # IMPORTANTE: Desactivar el item inmediatamente para que desaparezca
        item.active = False
        item.collected = True
        
        if item.item_type == 'apple':
            # SONIDO: Recoger item + menú (igual que nivel 1)
            play_sound('collect_item', 0.8)
            play_sound('upgrade_menu', 0.6)
            self.collect_apple()
            print(f"🍎 {character.name} recolectó una manzana - Item desactivado")
        elif item.item_type == 'potion':
            # SONIDO: Recoger item + escudo (igual que nivel 1)
            play_sound('collect_item', 0.8)
            play_sound('shield_activate', 0.7)
            self.collect_potion(character)
            print(f"🧪 {character.name} consumió una poción - Item desactivado")
    
    def collect_apple(self):
        """Recolecta manzana y muestra menú de mejoras - EXACTAMENTE IGUAL QUE NIVEL 1"""
        print("🍎 ¡Manzana recogida! Selecciona mejora:")
        print("1-Velocidad | 2-Daño | 3-Vida")
        self.show_upgrade_menu = True
        self.game_paused = True  # Pausar juego durante selección
        self.upgrade_menu_timer = 0  # Sin timer automático, esperar selección
    
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
                item_rect = pygame.Rect(item['x'], item['y'], 20, 20)
                player_rect = pygame.Rect(self.active_character.x, self.active_character.y, 
                                        self.active_character.width, self.active_character.height)
                
                if item_rect.colliderect(player_rect):
                    self.collect_potion(self.active_character)
                    item['collected'] = True
                    self.dropped_items.remove(item)
                    break
    
    def collect_potion(self, character):
        """Recolectar poción y activar escudo"""
        print(f"🧪 ¡{character.name} consumió poción de escudo!")
        
        # Activar escudo en el personaje específico
        character.shield_active = True
        character.shield_timer = 0
        character.shield_duration = self.shield_duration
        
        print(f"🛡️ Escudo activado para {character.name} (20 segundos)")
    
    def handle_upgrade_selection(self, key):
        """Maneja la selección de mejora - EXACTAMENTE IGUAL QUE NIVEL 1 (3 opciones)"""
        character = self.active_character
        
        if key == pygame.K_1:  # Velocidad
            character.speed += 0.8
            self.upgrades['speed'] += 1
            print(f"🚀 Velocidad mejorada: {character.speed:.1f}")
            
        elif key == pygame.K_2:  # Daño
            character.damage += 8
            if hasattr(self.active_attack_system, 'melee_damage'):
                self.active_attack_system.melee_damage += 8
            if hasattr(self.active_attack_system, 'projectile_damage'):
                self.active_attack_system.projectile_damage += 5
            self.upgrades['damage'] += 1
            print(f"⚔️ Daño mejorado: +8 de ataque")
            
        elif key == pygame.K_3:  # Vida
            character.max_health += 25
            character.health = min(character.health + 25, character.max_health)
            self.upgrades['health'] += 1
            print(f"❤️ Vida mejorada: {character.health}/{character.max_health}")
    
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
        
        # Sistema de ataques automáticos de IA (IGUAL QUE NIVEL 1)
        if (hasattr(self.inactive_ai, 'current_state') and 
            self.inactive_ai.current_state == 'attack' and 
            hasattr(self.inactive_ai, 'current_target') and
            self.inactive_ai.current_target and
            hasattr(self.inactive_ai.current_target, 'alive') and
            self.inactive_ai.current_target.alive):
            
            # Verificar que realmente está en rango de ataque
            target_distance = math.sqrt(
                (self.inactive_ai.current_target.x - self.inactive_character.x)**2 + 
                (self.inactive_ai.current_target.y - self.inactive_character.y)**2
            )
            
            if target_distance <= self.inactive_ai.attack_range:
                # La IA está en rango - activar ataque automático
                fake_keys_dict = {
                    pygame.K_SPACE: True,  # Solo activar SPACE
                    pygame.K_w: False, pygame.K_s: False,
                    pygame.K_a: False, pygame.K_d: False
                }
                
                class FakeKeys:
                    def __getitem__(self, key):
                        return fake_keys_dict.get(key, False)
                        
                if self.inactive_character == self.juan:
                    print("⚔️ Juan IA atacando con animación de GIF")
                    self.juan_attack.handle_attack_input(FakeKeys(), all_enemies_for_ai)
                else:
                    print("🔥 Adán IA atacando con animación de GIF")
                    self.adan_attack.handle_attack_input(FakeKeys(), all_enemies_for_ai)
        
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
        
        # Aplicar límites del mundo a los gusanos también
        self.enforce_boundaries_worms()
        
        # Comprobar impactos de proyectiles del chamán en ambos personajes
        self.chaman.check_projectile_collisions(players)
        
        # Verificar ataques de gusanos contra jugadores
        self.check_worm_attacks(players)
        
        # CÁMARA ESTÁTICA - NO SE MUEVE PARA EVITAR MOSTRAR EL VACÍO
        # target_camera_x = self.active_character.x - self.screen_width // 2
        # target_camera_y = self.active_character.y - self.screen_height // 2
        # 
        # # Suavizar movimiento de cámara
        # self.camera_x += (target_camera_x - self.camera_x) * self.camera_smooth_factor
        # self.camera_y += (target_camera_y - self.camera_y) * self.camera_smooth_factor
        # 
        # # Limitar cámara a los bordes del mundo
        # self.limit_camera()
        
        # Actualizar sistemas de ataque contra TODOS los enemigos
        worms = self.worm_spawner.get_worms()
        all_enemies = [self.chaman] + worms  # Incluir Chamán y todos los gusanos
        
        self.juan_attack.update(all_enemies)
        self.adan_attack.update(all_enemies)
        
        # Spawn automático de items distribuidos (igual que nivel 1)
        self.spawn_random_item_level2()
        
        # Actualizar items estáticos existentes
        for item in self.static_items:
            item.update()
        
        # Procesar drops simples: gusano muere -> PNG aparece
        self.process_worm_drops()
        
        # Actualizar coleccionables simples
        self.update_collectibles()
        
        # Verificar condición de victoria/derrota
        if self.chaman.health <= 0 and not self.victory:
            self.victory = True
            print("🎉 ¡VICTORIA ÉPICA! Has derrotado al Chamán Malvado")
            print("")
            print("🌟 Y finalmente después de una gran batalla,")
            print("🌟 María fue rescatada de las garras del mal,")
            print("🌟 y nuestros héroes vivieron felices")
            print("🌟 para siempre...")
            print("")
        
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
                        # Añadir item directamente a la lista de drops
                        self.dropped_items.append({
                            'type': drop['type'],
                            'x': drop['x'],
                            'y': drop['y'],
                            'collected': False,
                            'spawn_time': pygame.time.get_ticks()
                        })
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
                item_rect = pygame.Rect(item['x'], item['y'], 20, 20)
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
        """LÍMITES ESTRICTOS - NO PUEDE SALIR DEL PNG (5940x1080)"""
        # Límites estrictos basados en las dimensiones REALES del PNG
        left_limit = 0
        right_limit = self.world_width - 100  # 5940 - 100 = 5840
        top_limit = 0
        bottom_limit = self.world_height - 100  # 1080 - 100 = 980
        
        # APLICAR LÍMITES ESTRICTOS - NO PUEDE SALIR DEL MAPA
        if character.x < left_limit:
            character.x = left_limit
            print(f"🚫 {character.name} llegó al límite izquierdo")
        elif character.x > right_limit:
            character.x = right_limit
            print(f"🚫 {character.name} llegó al límite derecho")
            
        if character.y < top_limit:
            character.y = top_limit
            print(f"🚫 {character.name} llegó al límite superior")
        elif character.y > bottom_limit:
            character.y = bottom_limit
            print(f"🚫 {character.name} llegó al límite inferior")
    
    def enforce_boundaries_worms(self):
        """LÍMITES ESTRICTOS PARA GUSANOS - NO PUEDEN SALIR DEL PNG"""
        worms = self.worm_spawner.get_worms()
        for worm in worms:
            # Límites estrictos para gusanos basados en el PNG real (5940x1080)
            left_limit = 0
            right_limit = self.world_width - 64  # 5940 - 64 = 5876
            top_limit = 0
            bottom_limit = self.world_height - 64  # 1080 - 64 = 1016
            
            # APLICAR LÍMITES ESTRICTOS A GUSANOS
            if worm.x < left_limit:
                worm.x = left_limit
            elif worm.x > right_limit:
                worm.x = right_limit
                
            if worm.y < top_limit:
                worm.y = top_limit
            elif worm.y > bottom_limit:
                worm.y = bottom_limit
    
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
        # Reiniciar proyectiles del chamán si tiene el atributo
        # (Comentado hasta verificar estructura exacta del chamán)
        # if hasattr(self.chaman, 'projectiles'):
        #     self.chaman.projectiles = []
        # elif hasattr(self.chaman, 'attack_system') and hasattr(self.chaman.attack_system, 'projectiles'):
        #     self.chaman.attack_system.projectiles = []
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
        
        # Dibujar barras de vida flotantes sobre personajes
        self.draw_floating_health_bars()
        
        # Dibujar gusanos adicionales del nivel 2
        self.worm_spawner.draw(self.screen, self.camera_x, self.camera_y)
        
        # Dibujar coleccionables simples (gusano muere -> PNG aparece)
        self.draw_collectibles()
        
        # Dibujar items estáticos distribuidos (igual que nivel 1)
        self.draw_static_items_level2()
        
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
        
        # Dibujar estados finales y menús
        if self.game_over:
            self.draw_game_over()
        elif self.victory:
            self.draw_victory()
        elif self.game_paused and not self.collision_manager.editor_mode:
            self.draw_pause_menu()
        
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
    
    def draw_static_items_level2(self):
        """Dibuja items estáticos distribuidos en el nivel 2"""
        for item in self.static_items:
            if item.active and not getattr(item, 'collected', False):
                item.draw(self.screen, self.camera_x, self.camera_y, 
                         self.apple_image, self.potion_image)
    
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
        
        # Mostrar progreso de revival
        if hasattr(self, 'inactive_ai') and self.inactive_ai and self.inactive_ai.is_being_revived:
            self.draw_revival_progress()
    
    def draw_floating_health_bars(self):
        """Dibuja barras de vida flotantes mejoradas encima de los personajes"""
        characters = [
            {'char': self.juan, 'name': 'Juan', 'color': (50, 150, 255)},
            {'char': self.adan, 'name': 'Adán', 'color': (255, 100, 50)}
        ]
        
        for char_data in characters:
            character = char_data['char']
            name = char_data['name']
            name_color = char_data['color']
            
            if character.health <= 0:
                continue
                
            # Posición en pantalla
            screen_x = character.x - self.camera_x
            screen_y = character.y - self.camera_y
            
            # Solo dibujar si está visible
            if -100 < screen_x < self.screen_width + 100 and -100 < screen_y < self.screen_height + 100:
                # Configuración de la barra
                bar_width = 80
                bar_height = 12
                name_offset = -70  # Altura sobre el personaje
                bar_offset = -55
                
                # Posición centrada sobre el personaje
                bar_x = screen_x + 32 - bar_width // 2  # 32 es la mitad del ancho del personaje
                bar_y = screen_y + bar_offset
                name_x = screen_x + 32
                name_y = screen_y + name_offset
                
                # Nombre del personaje
                font = pygame.font.Font(None, 24)
                name_text = font.render(name, True, name_color)
                name_rect = name_text.get_rect(center=(name_x, name_y))
                
                # Fondo semi-transparente para el nombre
                name_bg = pygame.Surface((name_rect.width + 8, name_rect.height + 4), pygame.SRCALPHA)
                name_bg.fill((0, 0, 0, 150))
                self.screen.blit(name_bg, (name_rect.x - 4, name_rect.y - 2))
                self.screen.blit(name_text, name_rect)
                
                # Calcular porcentaje de vida
                health_ratio = character.health / character.max_health
                
                # Fondo de la barra (negro semi-transparente)
                bg_surface = pygame.Surface((bar_width + 4, bar_height + 4), pygame.SRCALPHA)
                bg_surface.fill((0, 0, 0, 180))
                self.screen.blit(bg_surface, (bar_x - 2, bar_y - 2))
                
                # Barra de vida con gradiente de color
                if health_ratio > 0.7:
                    health_color = (0, 255, 0)  # Verde
                elif health_ratio > 0.4:
                    health_color = (255, 255, 0)  # Amarillo
                elif health_ratio > 0.2:
                    health_color = (255, 140, 0)  # Naranja
                else:
                    health_color = (255, 0, 0)  # Rojo
                
                # Dibujar barra de vida
                current_width = int(bar_width * health_ratio)
                if current_width > 0:
                    pygame.draw.rect(self.screen, health_color, (bar_x, bar_y, current_width, bar_height))
                
                # Borde de la barra
                pygame.draw.rect(self.screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)
                
                # Texto de vida (números)
                health_font = pygame.font.Font(None, 20)
                health_text = f"{character.health}/{character.max_health}"
                health_surface = health_font.render(health_text, True, (255, 255, 255))
                health_rect = health_surface.get_rect(center=(bar_x + bar_width // 2, bar_y + bar_height // 2))
                self.screen.blit(health_surface, health_rect)
                
                # Indicador de escudo si está activo
                if hasattr(character, 'shield_active') and character.shield_active:
                    shield_text = "🛡️"
                    shield_font = pygame.font.Font(None, 24)
                    shield_surface = shield_font.render(shield_text, True, (100, 200, 255))
                    shield_rect = shield_surface.get_rect(center=(bar_x + bar_width + 15, bar_y + bar_height // 2))
                    self.screen.blit(shield_surface, shield_rect)
    
    def draw_revival_prompt(self):
        """Dibuja prompt para revivir"""
        font = pygame.font.Font(None, 48)
        text = f"Presiona E para revivir a {self.inactive_character.name}"
        revival_text = font.render(text, True, (255, 255, 100))
        revival_rect = revival_text.get_rect(center=(self.screen_width//2, self.screen_height - 100))
        
        # Fondo del texto
        bg_surface = pygame.Surface((revival_rect.width + 20, revival_rect.height + 10), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 180))
        self.screen.blit(bg_surface, (revival_rect.x - 10, revival_rect.y - 5))
        self.screen.blit(revival_text, revival_rect)
    
    def draw_revival_progress(self):
        """Dibuja barra de progreso de revivir"""
        if not self.inactive_ai.is_being_revived:
            return
        
        progress = self.inactive_ai.revival_timer / self.inactive_ai.revival_time
        
        # Barra de progreso
        bar_width = 300
        bar_height = 20
        x = self.screen_width // 2 - bar_width // 2
        y = self.screen_height // 2
        
        # Fondo
        pygame.draw.rect(self.screen, (100, 0, 0), (x, y, bar_width, bar_height))
        
        # Progreso
        progress_width = int(bar_width * progress)
        pygame.draw.rect(self.screen, (0, 255, 100), (x + 2, y + 2, progress_width - 4, bar_height - 4))
        
        # Borde
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, bar_width, bar_height), 2)
        
        # Texto
        font = pygame.font.Font(None, 36)
        text = f"Reviviendo... {int(progress * 100)}%"
        revival_text = font.render(text, True, (255, 255, 255))
        text_rect = revival_text.get_rect(center=(x + bar_width//2, y - 30))
        self.screen.blit(revival_text, text_rect)
    
    def draw_upgrade_menu(self):
        """Dibuja el menú de selección de mejoras - EXACTAMENTE IGUAL QUE NIVEL 1"""
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
        
        # Opciones EXACTAMENTE IGUALES al nivel 1 (3 opciones)
        options = [
            "1 - 🚀 Velocidad de Movimiento (+0.8)",
            "2 - ⚔️ Daño de Ataque (+8)",
            "3 - ❤️ Vida Máxima (+25)"
        ]
        
        for i, option in enumerate(options):
            option_text = font_option.render(option, True, (255, 255, 255))
            option_rect = option_text.get_rect(center=(menu_width//2, 150 + i * 60))
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
        
        # Vidas SIN estadísticas innecesarias - LIMPIA COMO SOLICITA EL USUARIO
        juan_health_text = font_small.render(f"Juan: {self.juan.health}/{self.juan.max_health}", 
                                       True, (255, 255, 255) if self.juan.health > 0 else (255, 100, 100))
        self.screen.blit(juan_health_text, (20, 90))
        
        adan_health_text = font_small.render(f"Adán: {self.adan.health}/{self.adan.max_health}", 
                                       True, (255, 255, 255) if self.adan.health > 0 else (255, 100, 100))
        self.screen.blit(adan_health_text, (300, 90))
        
        # Vida del Chamán - Solo números de vida
        chaman_health_text = font_small.render(f"👹 Chamán: {self.chaman.health}/{self.chaman.max_health}", 
                                        True, (255, 100, 255) if self.chaman.health > 0 else (255, 100, 100))
        self.screen.blit(chaman_health_text, (600, 90))
        
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
        """Dibuja la pantalla de game over mejorada"""
        # Fondo sólido negro para coherencia visual
        self.screen.fill((0, 0, 0))
        
        font_huge = pygame.font.Font(None, 180)
        font_large = pygame.font.Font(None, 96)
        font_medium = pygame.font.Font(None, 72)
        
        # Título principal con efecto
        title = font_huge.render("💀 GAME OVER 💀", True, (255, 100, 100))
        title_rect = title.get_rect(center=(self.screen_width//2, 300))
        self.screen.blit(title, title_rect)
        
        # Mensaje temático
        subtitle = font_large.render("El Chamán Malvado ha triunfado...", True, (255, 150, 150))
        subtitle_rect = subtitle.get_rect(center=(self.screen_width//2, 420))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Opciones mejoradas
        restart = font_medium.render("R - Reintentar", True, (200, 255, 200))
        restart_rect = restart.get_rect(center=(self.screen_width//2, 520))
        self.screen.blit(restart, restart_rect)
        
        menu = font_medium.render("M - Menú Principal", True, (200, 200, 255))
        menu_rect = menu.get_rect(center=(self.screen_width//2, 580))
        self.screen.blit(menu, menu_rect)
        
        exit_text = font_medium.render("ESC - Salir", True, (255, 200, 200))
        exit_rect = exit_text.get_rect(center=(self.screen_width//2, 640))
        self.screen.blit(exit_text, exit_rect)
    
    def draw_victory(self):
        """Dibuja la pantalla de victoria mejorada"""
        # Fondo con gradiente dorado para coherencia visual
        self.screen.fill((30, 20, 0))
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((255, 215, 0, 40))  # Dorado translúcido
        self.screen.blit(overlay, (0, 0))
        
        font_huge = pygame.font.Font(None, 180)
        font_large = pygame.font.Font(None, 96)
        font_medium = pygame.font.Font(None, 72)
        font_small = pygame.font.Font(None, 48)
        
        # Título principal épico
        title = font_huge.render("🏆 ¡VICTORIA ÉPICA! 🏆", True, (255, 215, 0))
        title_rect = title.get_rect(center=(self.screen_width//2, 250))
        self.screen.blit(title, title_rect)
        
        # Mensaje de logro
        subtitle = font_large.render("¡Has derrotado al Chamán Malvado!", True, (200, 255, 200))
        subtitle_rect = subtitle.get_rect(center=(self.screen_width//2, 320))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Mensaje final del juego con mejor espaciado
        y_position = 420  # Posición inicial más abajo
        
        final_messages = [
            "Y finalmente después de una gran batalla,",
            "",  # Línea vacía para espaciado
            "María fue rescatada de las garras del mal,",
            "",  # Línea vacía para espaciado  
            "y nuestros héroes vivieron felices",
            "",  # Línea vacía para espaciado
            "para siempre..."
        ]
        
        for i, message in enumerate(final_messages):
            if message:  # Solo renderizar si no es línea vacía
                final_line = font_medium.render(message, True, (255, 255, 255))
                final_line_rect = final_line.get_rect(center=(self.screen_width//2, y_position + (i * 35)))
                self.screen.blit(final_line, final_line_rect)
            else:
                # Para líneas vacías, solo incrementar el espaciado
                pass
        
        # ESTADÍSTICAS REPOSICIONADAS MÁS ABAJO PARA EVITAR SUPERPOSICIÓN
        stats_title = font_medium.render("📊 Estadísticas de Batalla:", True, (255, 255, 255))
        stats_title_rect = stats_title.get_rect(center=(self.screen_width//2, 450))  # Movido más abajo
        self.screen.blit(stats_title, stats_title_rect)
        
        stats = [
            f"👤 Héroe activo: {self.active_character.name}",
            f"❤️ Vida restante: {self.active_character.health}/{self.active_character.max_health}",
            f"⚡ Mejoras obtenidas: {sum(self.upgrades.values())}",
            f"🐛 Gusanos derrotados: {self.worm_spawner.total_spawned}",
            f"⏱️ Tiempo de batalla: {self.format_time(pygame.time.get_ticks() // 1000)}"
        ]
        
        for i, stat in enumerate(stats):
            stat_surface = font_small.render(stat, True, (255, 255, 200))
            stat_rect = stat_surface.get_rect(center=(self.screen_width//2, 500 + i * 35))  # Mejor espaciado
            self.screen.blit(stat_surface, stat_rect)
        
        # OPCIONES REPOSICIONADAS MÁS ABAJO
        restart = font_medium.render("R - Volver a jugar", True, (200, 255, 200))
        restart_rect = restart.get_rect(center=(self.screen_width//2, 720))  # Movido más abajo
        self.screen.blit(restart, restart_rect)
        
        menu = font_medium.render("M - Menú Principal", True, (200, 200, 255))
        menu_rect = menu.get_rect(center=(self.screen_width//2, 780))  # Movido más abajo
        self.screen.blit(menu, menu_rect)
        
        exit_text = font_medium.render("ESC - Salir", True, (255, 200, 200))
        exit_rect = exit_text.get_rect(center=(self.screen_width//2, 840))  # Movido más abajo
        self.screen.blit(exit_text, exit_rect)
    
    def format_time(self, seconds):
        """Formatea el tiempo en minutos:segundos"""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def draw_pause_menu(self):
        """Dibuja el menú de pausa durante el juego"""
        # Fondo semitransparente
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        font_huge = pygame.font.Font(None, 150)
        font_large = pygame.font.Font(None, 84)
        font_medium = pygame.font.Font(None, 72)
        
        # Título del menú
        title = font_huge.render("⏸️ JUEGO PAUSADO", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen_width//2, 250))
        self.screen.blit(title, title_rect)
        
        # Información del estado actual
        hero_info = font_large.render(f"Héroe activo: {self.active_character.name}", True, (200, 200, 255))
        hero_rect = hero_info.get_rect(center=(self.screen_width//2, 350))
        self.screen.blit(hero_info, hero_rect)
        
        health_info = font_large.render(f"Vida: {self.active_character.health}/{self.active_character.max_health}", True, (255, 200, 200))
        health_rect = health_info.get_rect(center=(self.screen_width//2, 410))
        self.screen.blit(health_info, health_rect)
        
        # Opciones del menú actualizadas
        continue_text = font_medium.render("P - Continuar partida", True, (200, 255, 200))
        continue_rect = continue_text.get_rect(center=(self.screen_width//2, 520))
        self.screen.blit(continue_text, continue_rect)
        
        menu_text = font_medium.render("M - Menú Principal", True, (255, 200, 200))
        menu_rect = menu_text.get_rect(center=(self.screen_width//2, 580))
        self.screen.blit(menu_text, menu_rect)
        
        # Controles recordatorio (sin ataque especial)
        controls_title = font_large.render("🎮 Controles:", True, (255, 255, 200))
        controls_title_rect = controls_title.get_rect(center=(self.screen_width//2, 680))
        self.screen.blit(controls_title, controls_title_rect)
        
        controls = [
            "TAB - Cambiar héroe",
            "ESPACIO - Ataque básico", 
            "F1 - Editor de bloques"
        ]
        
        for i, control in enumerate(controls):
            control_surface = font_medium.render(control, True, (255, 255, 255))
            control_rect = control_surface.get_rect(center=(self.screen_width//2, 740 + i * 35))
            self.screen.blit(control_surface, control_rect)
    
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