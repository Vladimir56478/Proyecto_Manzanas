#!/usr/bin/env python3
"""
NIVEL 1 - LA TIERRA DE LAS MANZANAS
Juego optimizado con sistema completo de mejoras, audio e items estáticos.
"""
import pygame
import sys
import math
import random
import requests
from PIL import Image
from io import BytesIO

# Importaciones de configuración y utilidades
from config import *
from utils import *

# Importaciones del juego
from adan_attacks import AdanAttack
from adan_character_animation import AdanCharacter
from audio_manager import get_audio_manager
from character_ai import CharacterAI
from game_data_manager import get_game_data_manager
from intro_cinematica import IntroCinematica
from juan_attacks import JuanAttack
from juan_character_animation import JuanCharacter
from loading_screen import LoadingScreen
from worm_enemy import WormSpawner
from sound_generator import get_sound_generator, play_sound


# Clases de colisión movidas a utils.py para evitar duplicación


class StaticItem:
    """Representa un item estático en el mapa que se activa con E"""
    def __init__(self, x, y, item_type):
        self.x = x
        self.y = y
        self.item_type = item_type  # 'apple' o 'potion'
        self.width = ITEM_SIZE[0]
        self.height = ITEM_SIZE[1]
        self.active = False  # Inicia inactivo para spawn paulatino
        self.cooldown = 0
        self.respawn_time = ITEM_DESPAWN_TIME
        self.animation_offset = 0
        self.spawn_time = pygame.time.get_ticks()
        self.spawn_delay = 0  # Delay para aparición paulatina
        
    def update(self):
        """Actualiza el item con animación y spawn paulatino"""
        current_time = pygame.time.get_ticks()
        
        # Spawn inicial paulatino
        if not self.active and self.spawn_delay > 0 and current_time >= self.spawn_delay:
            self.active = True
            self.spawn_time = current_time
            print(f"✨ {self.item_type.capitalize()} apareció en ({self.x}, {self.y})")
        
        # Animación de flotación solo si está activo
        if self.active:
            self.animation_offset = int(2 * math.sin((current_time - self.spawn_time) / 400))
        
        # Sistema de respawn (NO reaparecen más después de ser usados)
        # Se eliminó para que solo aparezcan 10 items total
        
        return True
    
    def use_item(self):
        """Usa el item y lo pone en cooldown"""
        if self.active:
            self.active = False
            self.cooldown = pygame.time.get_ticks()
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
            scaled_image = pygame.transform.scale(image, (self.width, self.height))
            screen.blit(scaled_image, screen_pos)
        else:
            # Fallback: círculo de color
            color = (255, 50, 50) if self.item_type == 'apple' else (50, 100, 255)
            center = (int(screen_pos[0] + self.width//2), int(screen_pos[1] + self.height//2))
            pygame.draw.circle(screen, color, center, self.width//2)
        
        # Indicador "E" simplificado
        font = pygame.font.Font(None, 24)
        text = font.render("E", True, (255, 255, 255))
        text_pos = (screen_pos[0] + self.width//2 - 8, screen_pos[1] - 18)
        pygame.draw.rect(screen, (0, 0, 0, 120), (*text_pos, 16, 16))
        screen.blit(text, text_pos)
    
    def get_rect(self):
        """Obtiene el rectángulo para detección de colisiones"""
        return pygame.Rect(self.x, self.y, self.width, self.height)



class CollisionManager:
    """Maneja las colisiones con bloques invisibles"""
    def __init__(self, world_width=1980, world_height=1080):
        self.blocks = []
        self.editor_mode = False
        self.block_size = CHARACTER_SIZE[0] // 2
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
        self.data_manager = get_game_data_manager()
        self.load_collision_data()
    
    def load_collision_data(self):
        """Carga bloques de colisión desde archivo"""
        try:
            collision_data = self.data_manager.load_collision_data()
            self.blocks = []
            
            for block_data in collision_data.get("blocks", []):
                x = block_data["x"]
                y = block_data["y"]
                self.blocks.append(CollisionBlock(x, y, self.block_size, self.block_size))
            
            print(f"🧱 Bloques de colisión cargados: {len(self.blocks)} bloques")
        except Exception as e:
            print(f"⚠️ Error cargando bloques: {e}")
            self.blocks = []
    
    def save_collision_data(self, silent=True):
        """Guarda bloques de colisión en archivo"""
        try:
            blocks_data = [(block.x, block.y) for block in self.blocks]
            self.data_manager.save_collision_data(blocks_data, silent)
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
        
        # Verificar límites del mundo
        if (new_x < 0 or new_x + 64 > self.world_width or 
            new_y < 0 or new_y + 64 > self.world_height):
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
        
        # Información del editor - OCULTA pero funcional
        # Los bloques y cursor se siguen mostrando, pero sin texto de ayuda
        # para mantener el juego limpio visualmente
    
    def handle_editor_input(self, keys_pressed, keys_just_pressed, mouse_events, camera_x, camera_y):
        """Maneja input del modo editor con sistema de arrastre"""
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
                print(f"� Bloque eliminado y guardado automáticamente")
    
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
    




class Background:
    """Maneja el fondo del juego optimizado"""
    
    def __init__(self, image_url):
        self.image_url = image_url
        self.width = 1980
        self.height = 1080
        self.surface = None
        self.load_background(image_url)
        
    def load_background(self, file_path):
        """Carga el fondo desde archivo local"""
        try:
            pil_image = Image.open(file_path)
            self.width, self.height = pil_image.size
            
            pil_image = pil_image.convert('RGB')
            image_data = pil_image.tobytes()
            
            self.surface = pygame.image.fromstring(image_data, pil_image.size, 'RGB')
            self.surface = self.surface.convert()
            
        except Exception as e:
            self.create_fallback_background()
    
    def create_fallback_background(self):
        """Crea un fondo de respaldo"""
        self.surface = pygame.Surface((1980, 1080))
        for y in range(1080):
            green_intensity = 50 + (y * 100) // 1080
            color = (20, min(green_intensity, 150), 20)
            pygame.draw.line(self.surface, color, (0, y), (1980, y))
        
        # Añadir elementos decorativos distribuidos en el escenario largo
        for _ in range(150):  # Más elementos para el escenario más largo
            x = random.randint(0, 1980)
            y = random.randint(0, 1080)
            size = random.randint(10, 30)
            color = (30, random.randint(80, 120), 30)
            pygame.draw.circle(self.surface, color, (x, y), size)
    
    def draw(self, screen, camera_x, camera_y, screen_width, screen_height):
        """Dibuja el fondo con scroll completo respetando dimensiones originales"""
        if not self.surface:
            return
            
        # Limitar cámara a los bounds del escenario (dimensiones reales)
        # Permitir scroll completo en ambas direcciones si el escenario es más grande
        max_camera_x = max(0, self.width - screen_width)
        max_camera_y = max(0, self.height - screen_height)
        
        camera_x = max(0, min(camera_x, max_camera_x))
        camera_y = max(0, min(camera_y, max_camera_y))
        
        # Calcular región visible del escenario
        visible_width = min(screen_width, self.width - camera_x)
        visible_height = min(screen_height, self.height - camera_y)
        
        # Dibujar la porción visible del escenario
        source_rect = pygame.Rect(camera_x, camera_y, visible_width, visible_height)
        screen.blit(self.surface, (0, 0), source_rect)


class Game:
    """Clase principal del juego Nivel 1"""
    
    def __init__(self, selected_character='juan'):
        """Inicializa el juego optimizado"""
        pygame.init()
        
        # Configuración de pantalla
        self.screen_width, self.screen_height = 1920, 1080
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        pygame.display.set_caption("🍎 Nivel 1 - Tierra de las Manzanas")
        
        # Actualizar dimensiones reales
        self.screen_width, self.screen_height = self.screen.get_size()
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Sistema de carga
        self.loading_screen = LoadingScreen(self.screen)
        assets = [
            {"name": "Escenario", "description": "Cargando fondo"},
            {"name": "Personajes", "description": "Cargando Juan y Adán"},
            {"name": "Ataques", "description": "Sistemas de combate"},
            {"name": "Enemigos", "description": "25 gusanos enemigos"},
            {"name": "Audio", "description": "Música y efectos"},
            {"name": "IA", "description": "Inteligencia artificial"}
        ]
        self.loading_screen.start_loading(assets)
        
        # Carga de escenario
        self.loading_screen.update_progress("Escenario", "Cargando desde assets locales...")
        self.loading_screen.draw()
        
        self.background = Background("assets/backgrounds/escenario.png")
        self.world_width = self.background.width
        self.world_height = self.background.height
        
        # Carga de personajes
        self.loading_screen.update_progress("Personajes", "Cargando Juan...")
        self.loading_screen.draw()
        
        self.juan = JuanCharacter(400, 300)
        self.juan.max_health = 100
        self.juan.health = 100
        self.juan.speed = 6.5
        self.juan.damage = 22
        self.juan.attack_speed = 1.0
        self.juan.name = "Juan"
        
        self.loading_screen.update_progress("Personajes", "Cargando Adán...")
        self.loading_screen.draw()
        
        self.adan = AdanCharacter(500, 300)
        self.adan.max_health = 125
        self.adan.health = 125
        self.adan.speed = 5.5
        self.adan.damage = 28
        self.adan.attack_speed = 0.8
        self.adan.name = "Adán"
        
        # Sistemas de ataque
        self.loading_screen.update_progress("Ataques", "Configurando combate...")
        self.loading_screen.draw()
        
        self.juan_attack = JuanAttack(self.juan)
        self.adan_attack = AdanAttack(self.adan)
        
        # Configuración de personaje activo
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
        
        # Sistema de enemigos
        self.loading_screen.update_progress("Enemigos", "Preparando 25 gusanos únicos...")
        self.loading_screen.draw()
        
        self.worm_spawner = WormSpawner(max_worms=25)
        self.setup_enemy_spawns()
        self.enemies_defeated = 0
        
        # Sistema de items estáticos
        self.static_items = []
        self.setup_static_items()
        
        # Sistema de drops de enemigos
        self.drops = []
        
        # IA y Audio
        self.loading_screen.update_progress("IA", "Configurando inteligencia artificial...")
        self.loading_screen.draw()
        
        self.inactive_ai = CharacterAI(self.inactive_character, self.active_character)
        self.inactive_ai.detection_range = 400
        self.inactive_ai.attack_range = 150
        
        self.loading_screen.update_progress("Audio", "Cargando sonidos...")
        self.loading_screen.draw()
        
        self.audio = get_audio_manager()
        self.sound_generator = get_sound_generator()
        
        # Estado del juego
        self.game_over = False
        self.victory = False
        self.game_paused = False
        self.data_manager = get_game_data_manager()
        
        # Sistema de transición
        self.transition_to_level_2_flag = False
        self.victory_message = "¡Victoria! Presiona N para ir al Nivel 2"
        
        # Sistemas adicionales
        self.dropped_items = []
        self.upgrades = {'speed': 0, 'damage': 0, 'attack_speed': 0, 'health': 0}
        self.show_upgrade_menu = False
        self.upgrade_menu_timer = 0
        self.revival_distance = 100
        self.show_revival_prompt = False
        self.revival_key_pressed = False
        self.shield_duration = 900
        
        # Sistema de cámara
        self.camera_x = 0
        self.camera_y = 0
        self.switch_cooldown = 0
        
        # === SISTEMA DE COLISIONES Y EDITOR ===
        self.collision_manager = CollisionManager(self.world_width, self.world_height)
        self.collision_manager.load_collision_data()  # Cargar colisiones guardadas
        
        # Mostrar información sobre el sistema de colisiones
        if len(self.collision_manager.blocks) == 0:
            print("📋 Escenario sin obstáculos - Usa F1 para crear colisiones personalizadas")
        else:
            print(f"� Cargados {len(self.collision_manager.blocks)} bloques de colisión existentes")
        
        print("�🛠️ CONTROLES DEL EDITOR:")
        print("   F1: Activar/Desactivar modo editor")
        print("   Click y arrastrar: Crear rectángulo de bloques")  
        print("   Click simple: Colocar bloque individual")
        print("   Backspace: Eliminar bloque en cursor del mouse")
        print("   💾 GUARDADO AUTOMÁTICO: Cada bloque se guarda instantáneamente")
        print("   📁 Archivo: collision_data.txt")
        
        # Inicializar keys_last_frame como lista
        temp_keys = pygame.key.get_pressed()
        self.keys_last_frame = list(temp_keys)
        
        # === CREAR IMÁGENES DE COLECCIONABLES ===
        self.create_collectible_images()
        
        # === SISTEMA DE TRANSICIÓN ===
        self.transition_to_level_2_flag = False
        self.victory_message = "¡Victoria! Presiona N para ir al Nivel 2"
        
        # === FINALIZAR CARGA ===
        self.loading_screen.update_progress("Completado", "¡Iniciando batalla!")
        self.loading_screen.draw()
        pygame.time.wait(1000)
        
        print("✅ Nivel 1 inicializado correctamente")
    
    def setup_enemy_spawns(self):
        """Configura spawn dinámico alrededor de los personajes (25 gusanos únicos)"""
        # No configuramos áreas fijas, el spawn será dinámico alrededor de los personajes
        print("✅ Sistema de spawn dinámico configurado para 25 gusanos únicos")
    
    def setup_static_items(self):
        """Crea items estáticos distribuidos por todo el mapa evitando bloques de colisión - máximo 10 items"""
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
        
        print(f"✅ Sistema de spawn distribuido configurado - 1 item cada 5 segundos (máximo {self.max_items})")
        print("📍 Items aparecerán aleatoriamente por todo el mapa evitando bloques de colisión")
    
    def spawn_random_item(self):
        """Crea un item en una posición aleatoria válida del mapa"""
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
            x = random.randint(100, self.world_width - 100)
            y = random.randint(100, self.world_height - 100)
            
            # Verificar que no esté en un bloque de colisión
            item_rect = pygame.Rect(x, y, ITEM_SIZE[0], ITEM_SIZE[1])
            
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
                
                # Crear item
                new_item = StaticItem(x, y, selected_type)
                new_item.active = True  # Activar inmediatamente
                new_item.spawn_time = current_time
                self.static_items.append(new_item)
                
                self.items_spawned += 1
                self.last_item_spawn_time = current_time
                
                print(f"✨ Item {selected_type} spawneado en ({x}, {y}) - {self.items_spawned}/{self.max_items}")
                return new_item
            
            attempts += 1
        
        print(f"⚠️ No se pudo encontrar posición válida para item después de {max_attempts} intentos")
        return None
    

    def create_collectible_images(self):
        """Crea sprites optimizados para manzanas y pociones con URLs de GitHub"""
        # URLs de GitHub para sprites de alta calidad
        self.github_item_urls = {
            'apple': 'https://github.com/user-attachments/assets/8d98de91-3834-456d-8dac-484029df9a02',
            'potion': 'https://github.com/user-attachments/assets/5365c2ea-ad1e-4055-8d3b-de1547e10396'
        }
        
        # Intentar cargar desde GitHub, con fallback a sprites simples
        self.apple_image = self.load_collectible_from_github('apple') or self.create_fallback_apple()
        self.potion_image = self.load_collectible_from_github('potion') or self.create_fallback_potion()
    
    def load_collectible_from_github(self, item_type):
        """Carga un coleccionable desde GitHub"""
        try:
            url = self.github_item_urls.get(item_type)
            if not url:
                return None
                
            print(f"📥 Descargando {item_type} desde GitHub...")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            image_data = BytesIO(response.content)
            pil_image = Image.open(image_data)
            try:
                # Intentar usar el método moderno primero
                if hasattr(Image, 'Resampling'):
                    pil_image = pil_image.convert('RGBA').resize(ITEM_SIZE, Image.Resampling.LANCZOS)
                else:
                    # Fallback para versiones más antiguas
                    pil_image = pil_image.convert('RGBA').resize(ITEM_SIZE)
            except AttributeError:
                pil_image = pil_image.convert('RGBA').resize(ITEM_SIZE)
            
            pygame_surface = pygame.image.fromstring(
                pil_image.tobytes(), pil_image.size, 'RGBA'
            ).convert_alpha()
            
            print(f"✅ {item_type.capitalize()} cargado desde GitHub")
            return pygame_surface
            
        except Exception as e:
            print(f"⚠️ Error cargando {item_type}: {e}, usando fallback")
            return None
    
    def create_fallback_apple(self):
        """Crea sprite de manzana de respaldo optimizado"""
        surface = pygame.Surface(ITEM_SIZE, pygame.SRCALPHA)
        center_x, center_y = ITEM_SIZE[0] // 2, ITEM_SIZE[1] // 2
        pygame.draw.circle(surface, (220, 50, 50), (center_x, center_y + 2), 10)
        pygame.draw.circle(surface, (255, 100, 100), (center_x - 2, center_y), 8)
        pygame.draw.rect(surface, (139, 69, 19), (center_x - 1, 4, 4, 8))
        pygame.draw.ellipse(surface, (34, 139, 34), (center_x - 3, 2, 8, 6))
        pygame.draw.circle(surface, (255, 200, 200, 80), (center_x - 2, center_y - 2), 5)
        return surface
    
    def create_fallback_potion(self):
        """Crea sprite de poción de respaldo optimizado"""
        surface = pygame.Surface(ITEM_SIZE, pygame.SRCALPHA)
        center_x, center_y = ITEM_SIZE[0] // 2, ITEM_SIZE[1] // 2
        pygame.draw.rect(surface, (100, 100, 100), (center_x - 2, center_y, 4, 10))
        pygame.draw.ellipse(surface, (20, 100, 220), (center_x - 4, center_y + 2, 8, 8))
        pygame.draw.rect(surface, (50, 150, 255), (center_x - 1, center_y - 3, 2, 9))
        pygame.draw.circle(surface, (100, 200, 255), (center_x, center_y + 4), 3)
        pygame.draw.circle(surface, (150, 220, 255, 60), (center_x + 8, center_y + 14), 10)
        return surface
    
    # === MANEJO DE EVENTOS ===
    
    def handle_events(self):
        """Maneja todos los eventos del juego"""
        keys_pressed = pygame.key.get_pressed()
        
        # Detectar teclas presionadas este frame
        keys_just_pressed = {}
        for key in range(512):  # Cubrir todas las teclas
            if key < len(keys_pressed) and key < len(self.keys_last_frame):
                keys_just_pressed[key] = keys_pressed[key] and not self.keys_last_frame[key]
            else:
                keys_just_pressed[key] = False
        
        # Convertir a lista para poder usar copy()
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
                    return False
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
                    self.return_to_main_menu()
                    return False
                elif event.key == pygame.K_F1:
                    # Toggle modo editor
                    self.collision_manager.editor_mode = not self.collision_manager.editor_mode
                    mode = "activado" if self.collision_manager.editor_mode else "desactivado"
                    print(f"🛠️ Modo editor {mode}")
                    if self.collision_manager.editor_mode:
                        print("🔄 GUARDADO AUTOMÁTICO ACTIVADO")
                        print("✨ Todos los bloques se guardan instantáneamente")
                        print("📁 Archivo: collision_data.txt")
                    else:
                        # Guardado final al salir del editor
                        self.collision_manager.save_collision_data(silent=False)
                        print(f"💾 Configuración final guardada: {len(self.collision_manager.blocks)} bloques")
                elif event.key == pygame.K_r and (self.game_over or self.victory):
                    # Reiniciar juego (funciona tanto para game over como victoria)
                    print("🔄 Reintentando nivel...")
                    self.restart_game()
                elif event.key == pygame.K_m and (self.game_over or self.victory):
                    # Volver al menú principal
                    print("🏠 Regresando al menú principal...")
                    self.return_to_main_menu()
                    return False
                elif event.key == pygame.K_n and self.victory:
                    # Ir al Nivel 2
                    print("🌟 Transición al Nivel 2...")
                    self.launch_level_2()
                    return False
                elif event.key == pygame.K_TAB and not self.collision_manager.editor_mode:
                    self.switch_character()
                # ELIMINADO: Ataque especial de bolitas (tecla X)
                # elif event.key == pygame.K_x and not self.collision_manager.editor_mode:
                #     self.perform_special_attack()
                elif self.show_upgrade_menu and event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    self.handle_upgrade_selection(event.key)
                    self.show_upgrade_menu = False
                    self.game_paused = False  # Reanudar juego después de selección
            elif event.type == pygame.USEREVENT + 1:
                # Transición automática al nivel 2
                if self.transition_to_level_2_flag:
                    print("🎯 Iniciando transición automática al Nivel 2...")
                    self.launch_level_2()
                    return False
        
        # Manejo del modo editor - PAUSAR JUEGO
        if self.collision_manager.editor_mode:
            self.game_paused = True
            self.collision_manager.handle_editor_input(keys_pressed, keys_just_pressed, mouse_events, self.camera_x, self.camera_y)
            # En modo editor, no procesar otros inputs
            return True
        else:
            self.game_paused = False
        
        # Manejo de revivir con E (solo si no está en modo editor)
        e_key_pressed = keys_pressed[pygame.K_e]
        if not self.game_over and self.inactive_character.health <= 0:
            distance = self.distance_between_characters()
            if distance <= self.revival_distance:
                self.show_revival_prompt = True
                if e_key_pressed and not self.revival_key_pressed:
                    if self.inactive_ai.start_revival():
                        print(f"🔄 Comenzando a revivir a {self.inactive_character.name}...")
                        self.show_revival_prompt = False
            else:
                self.show_revival_prompt = False
        else:
            self.show_revival_prompt = False
        
        # Interacción con items estáticos con E
        if e_key_pressed and not self.revival_key_pressed and not self.game_over:
            self.check_static_item_interaction()
        
        self.revival_key_pressed = e_key_pressed
        
        # Manejo de ataques básicos con ESPACIO (solo si no está en modo editor)
        if keys_pressed[pygame.K_SPACE]:
            self.perform_basic_attack()
        
        return True
    
    def check_static_item_interaction(self):
        """Verifica si el jugador puede interactuar con items estáticos"""
        player_rect = pygame.Rect(self.active_character.x, self.active_character.y, 64, 64)
        
        for item in self.static_items:
            if item.active:
                item_rect = item.get_rect()
                # Aumentar el área de interacción
                interaction_rect = pygame.Rect(item_rect.x - 20, item_rect.y - 20, 
                                             item_rect.width + 40, item_rect.height + 40)
                
                if player_rect.colliderect(interaction_rect):
                    # Verificar que el item no esté ya recolectado
                    if not getattr(item, 'collected', False) and getattr(item, 'active', True):
                        self.collect_static_item(item, self.active_character)
                        break  # Solo un item por presión de E
    
    def collect_static_item(self, item, character):
        """Recolecta un item estático"""
        # IMPORTANTE: Desactivar el item inmediatamente para que desaparezca
        item.active = False
        item.collected = True
        
        if item.item_type == 'apple':
            # SONIDO: Recoger item + menú
            play_sound('collect_item', 0.8)
            play_sound('upgrade_menu', 0.6)
            self.collect_apple()
            print(f"🍎 {character.name} recolectó una manzana - Item desactivado")
        elif item.item_type == 'potion':
            # SONIDO: Recoger item + escudo
            play_sound('collect_item', 0.8)
            play_sound('shield_activate', 0.7)
            self.collect_potion(character)
            print(f"🧪 {character.name} consumió una poción - Item desactivado")
    
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
            # CONFIGURACIÓN EXACTA DEL NIVEL 2
            self.inactive_ai.detection_range = 400
            self.inactive_ai.attack_range = 150
            
            self.switch_cooldown = 30
            print(f"🔄 Cambiado a {self.active_character.name} - IA configurada para {self.inactive_character.name}")
    
    def perform_basic_attack(self):
        """Realiza ataque básico"""
        if self.game_over or self.victory:
            return
        
        # SONIDO: Ataque básico
        play_sound('attack_basic', 0.8)
        
        worms = self.worm_spawner.get_worms()
        self.active_attack_system.handle_attack_input(pygame.key.get_pressed(), worms)
    
    def perform_special_attack(self):
        """Realiza ataque especial (X)"""
        if self.game_over or self.victory:
            return
        
        worms = self.worm_spawner.get_worms()
        
        if self.active_character == self.juan:
            # SONIDO: Combo de Juan
            play_sound('combo_attack', 0.9)
            hit = self.juan_attack.special_attack(worms)
            # El conteo se maneja en process_worm_drops()
        else:  # Adán
            if worms:
                # SONIDO: Proyectil de Adán
                play_sound('projectile_shoot', 0.8)
                target = min(worms, key=lambda w: 
                    ((w.x - self.adan.x)**2 + (w.y - self.adan.y)**2)**0.5)
                self.adan_attack.ranged_attack(target.x + 32, target.y + 32)
                print(f"🏹 Adán dispara proyectil hacia gusano")
    
    def distance_between_characters(self):
        """Calcula distancia entre personajes"""
        return math.sqrt((self.active_character.x - self.inactive_character.x)**2 + 
                        (self.active_character.y - self.inactive_character.y)**2)
    
    # === LÓGICA DE ACTUALIZACIÓN ===
    
    def update(self):
        """Actualiza toda la lógica del juego"""
        if self.game_over or self.victory or self.game_paused:
            if self.switch_cooldown > 0:
                self.switch_cooldown -= 1
            return
        
        # Actualizar solo si el juego no está pausado
        if self.game_paused:
            return
            
        keys_pressed = pygame.key.get_pressed()
        
        # Actualizar personaje activo
        if not self.active_attack_system.is_character_attacking() and not self.collision_manager.editor_mode:
            old_x, old_y = self.active_character.x, self.active_character.y
            self.active_character.update(keys_pressed)
            
            if not self.collision_manager.can_move_to(self.active_character, 
                                                     self.active_character.x, 
                                                     self.active_character.y):
                self.active_character.x, self.active_character.y = old_x, old_y
            
            self.enforce_boundaries(self.active_character)
        
        # Actualizar IA del personaje inactivo con ATAQUE A GUSANOS
        if (self.inactive_character.health > 0 or self.inactive_ai.is_being_revived) and not self.collision_manager.editor_mode:
            old_x, old_y = self.inactive_character.x, self.inactive_character.y
            
            worms = self.worm_spawner.get_worms()
            
            # NUEVA FUNCIONALIDAD: Hacer que la IA ataque gusanos cercanos
            target_worm = None
            min_distance = float('inf')
            
            # Buscar el gusano más cercano
            for worm in worms:
                if worm.alive:
                    distance = math.sqrt((worm.x - self.inactive_character.x)**2 + (worm.y - self.inactive_character.y)**2)
                    if distance < min_distance:
                        min_distance = distance
                        target_worm = worm
            
            # Si hay un gusano cerca, atacarlo; si no, seguir al jugador
            if target_worm and min_distance < 150:  # Rango de detección
                # La IA ya maneja el targeting internamente
                self.inactive_ai.update(worms)
                
                # Intentar atacar si está cerca
                if min_distance < 100:  # Rango de ataque
                    # Determinar dirección de ataque hacia el gusano
                    dx = target_worm.x - self.inactive_character.x
                    dy = target_worm.y - self.inactive_character.y
                    
                    # Crear teclas virtuales para ataque IA (usando valores por defecto para todas las teclas)
                    attack_keys = {key: False for key in range(512)}  # Inicializar todas las teclas como False
                    attack_keys[pygame.K_SPACE] = True
                    if abs(dx) > abs(dy):
                        if dx > 0:
                            attack_keys[pygame.K_d] = True  # Derecha
                        else:
                            attack_keys[pygame.K_a] = True  # Izquierda
                    else:
                        if dy > 0:
                            attack_keys[pygame.K_s] = True  # Abajo
                        else:
                            attack_keys[pygame.K_w] = True  # Arriba
                    
                    # Ejecutar ataque según el personaje (sin from_ai para compatibilidad)
                    if self.inactive_character.name == "Adan":
                        if self.adan_attack.handle_attack_input(attack_keys, worms):
                            print(f"🔥 Adán IA atacando gusano a {min_distance:.1f} unidades")
                    elif self.inactive_character.name == "Juan":
                        if self.juan_attack.handle_attack_input(attack_keys, worms):
                            print(f"🔥 Juan IA atacando gusano a {min_distance:.1f} unidades")
            else:
                # Comportamiento normal: seguir al jugador
                self.inactive_ai.update(worms)
            
            ai_animation_state = self.inactive_ai.get_animation_state()
            self.inactive_character.update(keys_pressed=None, ai_controlled=True, ai_direction=ai_animation_state)
            
            if not self.collision_manager.can_move_to(self.inactive_character,
                                                     self.inactive_character.x,
                                                     self.inactive_character.y):
                self.inactive_character.x, self.inactive_character.y = old_x, old_y
            
            self.enforce_boundaries(self.inactive_character)
        
        # Manejar ataques del personaje activo
        worms = self.worm_spawner.get_worms()
        self.active_attack_system.handle_attack_input(keys_pressed, worms)
        
        # Sistema de ataques automáticos de IA
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
                    self.juan_attack.handle_attack_input(FakeKeys(), worms)
                else:
                    self.adan_attack.handle_attack_input(FakeKeys(), worms)
        
        # Actualizar sistemas de ataque
        self.juan_attack.update(worms)
        self.adan_attack.update(worms)
        
        # Spawn automático de items distribuidos
        self.spawn_random_item()
        
        # Actualizar items existentes
        for item in self.static_items:
            item.update()
        
        # Actualizar enemigos con sistema de bloqueo de spawn
        players = [self.juan, self.adan]
        self.worm_spawner.update(players, self.collision_manager)
        
        # Verificar ataques de gusanos
        self.check_worm_attacks(players)
        
        # Procesar drops y coleccionables
        self.process_worm_drops()
        self.update_collectibles()
        
        # Sistema de escudo
        self.update_shield_system()
        
        # Actualizar cámara
        self.update_camera()
        
        # Reducir cooldowns
        if self.switch_cooldown > 0:
            self.switch_cooldown -= 1
        if self.upgrade_menu_timer > 0:
            self.upgrade_menu_timer -= 1
            if self.upgrade_menu_timer <= 0:
                self.show_upgrade_menu = False
        
        # Verificar condiciones de fin
        self.check_game_conditions()
        
        # Verificar victoria: todos los gusanos spawneados y eliminados
        self.check_victory_condition()
        
        # Verificar game over: jugador principal muerto
        self.check_player_death()
    
    def check_worm_attacks(self, players):
        """Verifica ataques de gusanos contra jugadores"""
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
                                    # SONIDO: Daño recibido
                                    play_sound('damage_taken', 0.7)
                                    player.take_damage(worm.attack_damage)
                                    print(f"💥 {player.name} recibió {worm.attack_damage} daño")
                                else:
                                    print(f"🛡️ {player.name} bloqueó el ataque con escudo")
                                worm.last_attack_time = current_time
    
    def process_worm_drops(self):
        """Procesa drops de gusanos muertos (DESHABILITADO - usar items estáticos)"""
        # SISTEMA DESHABILITADO: Los gusanos ya no sueltan drops
        # Los items están ahora como objetos estáticos en el mapa
        
        # Limpiar drops pendientes de gusanos sin procesar
        for worm in self.worm_spawner.worms[:]:
            if not worm.alive and worm.pending_drops:
                worm.get_and_clear_drops()  # Limpiar sin generar drops
        
        # Actualizar drops existentes y eliminar los expirados
        self.drops = [drop for drop in self.drops if drop.update()]
        
        # Verificar colisiones de drops con jugadores
        self.check_drop_collection()
    
    def check_drop_collection(self):
        """Verifica si los jugadores han recogido algún drop"""
        # Rectangulos de colisión para ambos personajes
        juan_rect = pygame.Rect(self.juan.x, self.juan.y, 64, 64)
        adan_rect = pygame.Rect(self.adan.x, self.adan.y, 64, 64)
        
        # Verificar colisiones con drops
        for drop in self.drops[:]:
            if drop.collected:
                continue
                
            drop_rect = drop.get_rect()
            
            # Verificar colisión con Juan
            if juan_rect.colliderect(drop_rect) and self.juan.health > 0:
                self.apply_drop_effect(drop, self.juan)
                drop.collected = True
                self.drops.remove(drop)
                
            # Verificar colisión con Adán
            elif adan_rect.colliderect(drop_rect) and self.adan.health > 0:
                self.apply_drop_effect(drop, self.adan)
                drop.collected = True
                self.drops.remove(drop)
    
    def apply_drop_effect(self, drop, character):
        """Aplica el efecto del drop al personaje"""
        if drop.drop_type == 'heal':
            # Curación inmediata
            old_health = character.health
            character.health = min(character.max_health, character.health + 15)
            healing = character.health - old_health
            print(f"✚ {character.__class__.__name__} se curó {healing} puntos de vida ({character.health}/{character.max_health})")
            
        elif drop.drop_type == 'health':
            # Aumenta vida máxima y cura completamente
            character.max_health += 10
            old_health = character.health
            character.health = character.max_health
            healing = character.health - old_health
            print(f"❤️ {character.__class__.__name__} aumentó vida máxima en 10 (+{healing} curación) ({character.health}/{character.max_health})")
            
        elif drop.drop_type == 'damage':
            # Aumenta daño base
            if hasattr(character, 'base_damage'):
                character.base_damage += 3
            else:
                character.base_damage = character.attack_damage + 3
                character.attack_damage += 3
            print(f"⚔️ {character.__class__.__name__} aumentó daño en 3 puntos")
            
        elif drop.drop_type == 'speed':
            # Aumenta velocidad de movimiento
            character.speed += 0.8
            print(f"⚡ {character.__class__.__name__} aumentó velocidad en 0.8 ({character.speed})")
    
    def update_collectibles(self):
        """Actualiza coleccionables y items estáticos"""
        current_time = pygame.time.get_ticks()
        
        # Actualizar items estáticos (animación y respawn)
        for item in self.static_items:
            item.update()
        
        # Eliminar items viejos (30 segundos) - DEPRECADO
        self.dropped_items = [item for item in self.dropped_items 
                            if current_time - item['spawn_time'] < 30000]
        
        # Verificar colisiones (DEPRECADO - usar items estáticos)
        active_rect = pygame.Rect(self.active_character.x, self.active_character.y, 100, 100)  # 64 * 1.56 = 100
        inactive_rect = pygame.Rect(self.inactive_character.x, self.inactive_character.y, 100, 100)  # 64 * 1.56 = 100
        
        for item in self.dropped_items[:]:
            item_rect = pygame.Rect(item['x'], item['y'], 32, 32)
            
            collected = False
            if active_rect.colliderect(item_rect):
                self.collect_item(item, self.active_character)
                collected = True
            elif (self.inactive_character.health > 0 and 
                  inactive_rect.colliderect(item_rect)):
                self.collect_item(item, self.inactive_character)
                collected = True
            
            if collected:
                self.dropped_items.remove(item)
    
    def collect_item(self, item, character):
        """Recolecta un item"""
        if item['type'] == 'apple':
            self.collect_apple()
        elif item['type'] == 'potion':
            self.collect_potion(character)
    
    def update_shield_system(self):
        """Actualiza el sistema de escudo"""
        for character in [self.juan, self.adan]:
            if getattr(character, 'shield_active', False):
                character.shield_timer = getattr(character, 'shield_timer', 0) + 1
                if character.shield_timer >= self.shield_duration:
                    character.shield_active = False
                    character.shield_timer = 0
                    print(f"🛡️ Escudo de {character.name} terminado")
    
    def update_camera(self):
        """Actualiza la posición de la cámara para seguir al personaje en el escenario completo"""
        # Centrar cámara en el personaje activo
        target_x = self.active_character.x - self.screen_width // 2
        target_y = self.active_character.y - self.screen_height // 2
        
        # Suavizar movimiento de cámara (más rápido para mejor respuesta)
        self.camera_x += (target_x - self.camera_x) * 0.15
        self.camera_y += (target_y - self.camera_y) * 0.15
        
        # Limitar cámara a bounds del escenario con dimensiones reales
        max_camera_x = max(0, self.world_width - self.screen_width)
        max_camera_y = max(0, self.world_height - self.screen_height)
        
        self.camera_x = max(0, min(self.camera_x, max_camera_x))
        self.camera_y = max(0, min(self.camera_y, max_camera_y))
    
    def check_game_conditions(self):
        """Verifica condiciones de victoria y derrota"""
        # La transición automática al Nivel 2 se maneja en check_victory_condition()
        # La muerte del jugador principal se maneja en check_player_death()
        
        # Derrota: ambos personajes muertos (solo si no se activó game over por jugador principal)
        if self.juan.health <= 0 and self.adan.health <= 0 and not self.game_over:
            self.game_over = True
            print("💀 GAME OVER - Ambos personajes han caído")
    
    def check_victory_condition(self):
        """Verifica si todos los gusanos han sido spawneados y eliminados, y si el jugador llegó al final"""
        # Verificar si todos los gusanos han sido spawneados
        all_spawned = self.worm_spawner.total_spawned >= self.worm_spawner.max_worms
        
        # Verificar si no quedan gusanos vivos
        living_worms = len([worm for worm in self.worm_spawner.worms if worm.alive])
        
        # Actualizar estadística de enemigos derrotados
        self.enemies_defeated = self.worm_spawner.total_spawned - living_worms
        
        # Verificar si ya se eliminaron todos los gusanos
        all_worms_defeated = (all_spawned and living_worms == 0 and self.worm_spawner.total_spawned > 0)
        
        # Solo verificar victoria si ya se eliminaron todos los gusanos
        if all_worms_defeated and not self.victory and not self.game_over:
            
            # Verificar si el personaje activo llegó al final del escenario (lado derecho)
            end_zone_x = self.world_width - 200  # 200 píxeles del final
            player_at_end = self.active_character.x >= end_zone_x
            
            if player_at_end:
                # SONIDO: Victoria
                play_sound('victory', 1.0)
                
                print("🌟 ¡TODOS LOS GUSANOS ELIMINADOS Y FINAL ALCANZADO! Transición automática al Nivel 2...")
                print(f"🏆 Victoria conseguida: {self.worm_spawner.total_spawned}/{self.worm_spawner.max_worms} gusanos eliminados + final alcanzado")
                
                self.victory = True
                self.transition_to_level_2_flag = True
                self.victory_message = "¡Nivel completado! Cargando Nivel 2..."
                
                # Transición automática inmediata
                pygame.time.set_timer(pygame.USEREVENT + 1, 3000)  # 3 segundos para ver el mensaje
                print("⏰ Transición automática en 3 segundos...")
            else:
                # Mostrar mensaje guía para ir al final
                if not hasattr(self, 'end_message_shown'):
                    print("🎯 ¡Todos los gusanos eliminados! Dirígete al FINAL DEL ESCENARIO (→) para completar el nivel")
                    self.end_message_shown = True
                    self.victory_message = "¡Gusanos eliminados! Ve al final del escenario (→)"
    
    def check_player_death(self):
        """Verifica si el jugador principal (activo) ha muerto"""
        if self.active_character.health <= 0 and not self.game_over:
            # SONIDO: Game Over
            play_sound('game_over', 0.9)
            
            self.game_over = True
            print(f"💀 GAME OVER - {self.active_character.name} (jugador principal) ha muerto")
            print("🔄 Presiona R para reintentar o ESC para salir")
    
    # === SISTEMA DE MEJORAS ===
    
    def collect_apple(self):
        """Recolecta manzana y muestra menú de mejoras con pausa"""
        print("🍎 ¡Manzana recogida! Selecciona mejora:")
        print("1-Velocidad | 2-Daño | 3-Vida")
        self.show_upgrade_menu = True
        self.game_paused = True  # Pausar juego durante selección
        self.upgrade_menu_timer = 0  # Sin timer automático, esperar selección
    
    def collect_potion(self, character):
        """Recolecta poción y activa escudo"""
        print(f"🧪 {character.name} consumió poción de escudo")
        character.shield_active = True
        character.shield_timer = 0
        print(f"🛡️ Escudo activado para {character.name}")
    
    def handle_upgrade_selection(self, key):
        """Maneja selección de mejora - 3 opciones principales"""
        # SONIDO: Selección de mejora
        play_sound('upgrade_select', 0.8)
        
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
    
    # === UTILIDADES ===
    
    def enforce_boundaries(self, character):
        """Aplica límites exactos del escenario con dimensiones originales"""
        # Límites dinámicos basados en el tamaño real del escenario
        left_limit = 0
        right_limit = self.world_width - 100  # Ancho del personaje (64 * 1.56 = 100)
        top_limit = 0
        bottom_limit = self.world_height - 100  # Alto del personaje (64 * 1.56 = 100)
        
        # Aplicar límites con rebote suave
        if character.x < left_limit:
            character.x = left_limit
        elif character.x > right_limit:
            character.x = right_limit
            
        if character.y < top_limit:
            character.y = top_limit
        elif character.y > bottom_limit:
            character.y = bottom_limit
    
    def restart_game(self):
        """Reinicia el juego"""
        # Reiniciar personajes
        self.juan.health = self.juan.max_health
        self.adan.health = self.adan.max_health
        self.juan.x, self.juan.y = 400, 300
        self.adan.x, self.adan.y = 500, 300
        
        # Limpiar enemigos y reiniciar spawner
        self.worm_spawner.worms.clear()
        self.worm_spawner.total_spawned = 0
        self.worm_spawner.last_spawn_time = 0
        
        # Reiniciar estado
        self.game_over = False
        self.victory = False
        self.transition_to_level_2_flag = False
        
        # Limpiar items
        self.dropped_items.clear()
        
        print("🔄 Juego reiniciado - 25 gusanos aparecerán gradualmente")
        print("🎯 Elimina todos los gusanos para avanzar al Nivel 2")
    
    def launch_level_2(self):
        """Lanza el Nivel 2 del juego con transferencia de estadísticas y pantalla de carga"""
        try:
            from loading_screen import LoadingScreen
            
            print("🚀 Cargando Nivel 2...")
            
            # Crear pantalla de carga
            loading_screen = LoadingScreen(self.screen)
            
            # Lista de assets a cargar
            assets_to_load = [
                {'name': 'nivel2', 'description': 'Preparando el mundo...'},
                {'name': 'characters', 'description': 'Cargando personajes...'},
                {'name': 'chaman', 'description': 'Inicializando Chamán Malvado...'},
                {'name': 'attacks', 'description': 'Cargando sistemas de ataque...'},
                {'name': 'animations', 'description': 'Configurando animaciones...'},
                {'name': 'audio', 'description': 'Preparando efectos de sonido...'},
                {'name': 'physics', 'description': 'Estableciendo físicas...'},
                {'name': 'final', 'description': '¡Casi listo!'}
            ]
            
            loading_screen.start_loading(assets_to_load)
            
            # Simular carga con pantalla de progreso
            for i, asset in enumerate(assets_to_load):
                # Mostrar pantalla de carga
                loading_screen.draw()
                pygame.display.flip()
                
                # Simular tiempo de carga
                pygame.time.wait(400)  # 400ms por asset
                
                # Actualizar progreso
                loading_screen.update_progress(asset['name'], asset['description'])
                
                # Manejar eventos para evitar que se cuelgue
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return
            
            # Pantalla final de carga
            loading_screen.set_custom_message("¡Listo para el combate!")
            loading_screen.draw()
            pygame.display.flip()
            pygame.time.wait(500)
            
            # Determinar personaje seleccionado
            selected_character = 'juan' if self.active_character == self.juan else 'adan'
            
            # Preparar estadísticas para transferir al nivel 2
            level1_stats = {
                'juan': {
                    'max_health': self.juan.max_health,
                    'health': self.juan.health,
                    'speed': self.juan.speed,
                    'damage': self.juan.damage
                },
                'adan': {
                    'max_health': self.adan.max_health,
                    'health': self.adan.health,
                    'speed': self.adan.speed,
                    'damage': self.adan.damage
                }
            }
            
            print(f"📊 Transfiriendo estadísticas del Nivel 1:")
            print(f"   Juan: {level1_stats['juan']}")
            print(f"   Adán: {level1_stats['adan']}")
            
            # Cerrar pygame del nivel actual
            pygame.quit()
            
            # Importar y ejecutar Nivel 2
            from nivel_2 import Nivel2
            
            # Crear e iniciar Nivel 2 con estadísticas transferidas
            nivel2 = Nivel2(selected_character, level1_stats)
            nivel2.run()
            
        except ImportError:
            print("❌ Error: No se pudo cargar el archivo nivel_2.py")
            print("Asegúrate de que el archivo nivel_2.py esté en la misma carpeta")
        except Exception as e:
            print(f"❌ Error lanzando Nivel 2: {e}")
            
        # Reinicializar pygame para este nivel si hay error
        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)

    def return_to_main_menu(self):
        """Regresa al menú principal (intro cinematográfica)"""
        print("🏠 Cerrando juego y regresando al menú principal...")
        
        # Detener música del juego
        audio_manager = get_audio_manager()
        audio_manager.stop_music()
        
        # Cerrar ventana del juego
        pygame.quit()
        
        # Reiniciar la intro cinematográfica
        intro = IntroCinematica()
        result = intro.run()
        
        if result and result.startswith('start_game_'):
            # Extraer personaje seleccionado
            selected_character = result.split('_')[-1]
            print(f"🎮 Reiniciando juego con {selected_character.upper()}")
            
            # Cerrar ventana de intro
            pygame.quit()
            
            # Crear y ejecutar el nuevo juego
            game = Game(selected_character)
            game.run()
        else:
            print("👋 Saliendo del juego...")
            pygame.quit()
            sys.exit()
    
    # === RENDERIZADO ===
    
    def draw_character_status_ui(self):
        """Dibuja la UI de estado de personajes para nivel 1"""
        # Fondo semitransparente para la UI superior
        ui_surface = pygame.Surface((450, 120), pygame.SRCALPHA)
        ui_surface.fill((0, 0, 0, 180))
        self.screen.blit(ui_surface, (10, 10))
        
        # Fuentes
        font_large = pygame.font.Font(None, 36)
        font_medium = pygame.font.Font(None, 28)
        font_small = pygame.font.Font(None, 24)
        
        # 🎮 Indicador de personaje ACTIVO
        active_color = (0, 255, 100)  # Verde brillante
        active_text = font_large.render(f"🎮 JUGADOR: {self.active_character.name}", True, active_color)
        self.screen.blit(active_text, (20, 25))
        
        # 🤖 Indicador de personaje IA
        ia_color = (255, 200, 50)  # Amarillo
        ia_text = font_large.render(f"🤖 IA: {self.inactive_character.name}", True, ia_color)
        self.screen.blit(ia_text, (20, 55))
        
        # ❤️ Vida del jugador activo
        health_percent = self.active_character.health / self.active_character.max_health
        if health_percent > 0.6:
            health_color = (100, 255, 100)
        elif health_percent > 0.3:
            health_color = (255, 255, 100)
        else:
            health_color = (255, 100, 100)
            
        health_text = font_medium.render(f"❤️ Vida: {self.active_character.health}/{self.active_character.max_health}", True, health_color)
        self.screen.blit(health_text, (20, 85))
        
        # 🔄 Instrucción de cambio
        switch_text = font_small.render("🔄 TAB: Cambiar personaje", True, (180, 180, 180))
        self.screen.blit(switch_text, (280, 85))
        
        # 🎯 Estado de batalla en la esquina superior derecha
        battle_surface = pygame.Surface((280, 80), pygame.SRCALPHA)
        battle_surface.fill((0, 50, 0, 150))
        self.screen.blit(battle_surface, (self.screen_width - 300, 10))
        
        # 🐛 Gusanos restantes
        worms_alive = len([w for w in self.worm_spawner.get_worms() if w.alive])
        worms_text = font_medium.render(f"🐛 Gusanos: {worms_alive}/25", True, (150, 255, 150))
        self.screen.blit(worms_text, (self.screen_width - 290, 25))
        
        # 🏆 Progreso
        progress_text = font_small.render(f"🏆 Eliminados: {self.enemies_defeated}", True, (255, 255, 100))
        self.screen.blit(progress_text, (self.screen_width - 290, 50))
        
        # 🎮 Nivel 1 indicator
        level_text = font_small.render("🌍 NIVEL 1 - CÁMARA DINÁMICA", True, (100, 255, 150))
        self.screen.blit(level_text, (self.screen_width - 290, 70))

    def draw(self):
        """Dibuja todo el juego"""
        # Pantallas de fin - renderizar SOLO estas sin fondo si están activas
        if self.game_over:
            self.screen.fill((0, 0, 0))  # Fondo negro sólido para Game Over
            self.draw_game_over()
            pygame.display.flip()
            return
        elif self.victory:
            self.screen.fill((0, 0, 0))  # Fondo negro sólido para Victoria
            self.draw_victory()
            pygame.display.flip()
            return
        
        # Renderizado normal del juego solo si NO hay Game Over o Victory
        # Limpiar pantalla
        self.screen.fill((50, 100, 50))
        
        # Dibujar UI de estado de personajes primero
        self.draw_character_status_ui()
        
        # Dibujar fondo (escenario principal PNG 1980x1080)
        self.background.draw(self.screen, self.camera_x, self.camera_y, 
                           self.screen_width, self.screen_height)
        
        # EXACTAMENTE COMO EN NIVEL 2: Dibujar personajes (inactivo primero para orden de capas)
        if not self.inactive_attack_system.is_character_attacking():
            # Dibujar personaje inactivo (vivo o derrotado)
            self.inactive_character.draw(self.screen, self.camera_x, self.camera_y)
            
            # Aplicar efecto gris si está derrotado
            if self.inactive_character.health <= 0:
                self.draw_defeated_effect(self.inactive_character)
            
            # Efecto de escudo si está activo (solo si tiene vida)
            if (self.inactive_character.health > 0 and 
                hasattr(self.inactive_character, 'shield_active') and 
                self.inactive_character.shield_active):
                self.draw_shield_effect(self.inactive_character)
        
        # EXACTAMENTE COMO EN NIVEL 2: Personaje activo
        if not self.active_attack_system.is_character_attacking():
            self.active_character.draw(self.screen, self.camera_x, self.camera_y)
            # Efecto de escudo si está activo
            if hasattr(self.active_character, 'shield_active') and self.active_character.shield_active:
                self.draw_shield_effect(self.active_character)
        
        # Mostrar indicador de combate de IA (exacto como nivel 2)
        # ELIMINADO - Sin indicadores visuales de IA
        
        # EXACTAMENTE COMO EN NIVEL 2: Dibujar efectos de ataque
        self.juan_attack.draw(self.screen, self.camera_x, self.camera_y)
        self.adan_attack.draw(self.screen, self.camera_x, self.camera_y)
        
        # Dibujar enemigos
        self.worm_spawner.draw(self.screen, self.camera_x, self.camera_y)
        
        # Dibujar coleccionables
        self.draw_collectibles()
        
        # Dibujar barras de vida flotantes
        self.draw_floating_health_bars()
        
        # Dibujar UI simplificada
        self.draw_ui()
        
        # Dibujar indicador de pausa
        if self.game_paused:
            self.draw_pause_screen()
        
        # Dibujar modo editor si está activo
        if self.collision_manager.editor_mode:
            self.collision_manager.draw_editor_mode(self.screen, self.camera_x, self.camera_y)
        
        # Menú de mejoras
        if self.show_upgrade_menu:
            self.draw_upgrade_menu()
        
        # Prompt de revivir
        if self.show_revival_prompt:
            self.draw_revival_prompt()
        
        # Progreso de revivir
        if (self.inactive_character.health <= 0 and 
            self.inactive_ai.is_being_revived):
            self.draw_revival_progress()
        
        pygame.display.flip()
    
    def draw_shield_effect(self, character):
        """Dibuja efecto visual de escudo mejorado"""
        if not hasattr(character, 'shield_active') or not character.shield_active:
            return
            
        # Círculo pulsante alrededor del personaje
        shield_alpha = int(100 + 50 * math.sin(pygame.time.get_ticks() * 0.01))
        shield_surface = pygame.Surface((125, 125), pygame.SRCALPHA)  # 80 * 1.56 = 125
        
        # Efecto de escudo con múltiples capas (escalado 56%)
        pygame.draw.circle(shield_surface, (0, 150, 255, shield_alpha//2), (62, 62), 55)  # 40*1.56=62, 35*1.56=55
        pygame.draw.circle(shield_surface, (100, 200, 255, shield_alpha), (62, 62), 47)    # 30*1.56=47
        pygame.draw.circle(shield_surface, (150, 220, 255, shield_alpha//3), (62, 62), 39) # 25*1.56=39
        
        shield_x = character.x - self.camera_x - 12  # -8*1.56 ≈ -12
        shield_y = character.y - self.camera_y - 12
        self.screen.blit(shield_surface, (shield_x, shield_y))
    
    def draw_defeated_effect(self, character):
        """Dibuja efecto gris sobre personaje derrotado"""
        # Crear superficie gris semitransparente
        gray_surface = pygame.Surface((100, 100), pygame.SRCALPHA)  # 64 * 1.56 = 100
        gray_surface.fill((128, 128, 128, 160))  # Gris con transparencia
        
        # Aplicar el efecto gris sobre el personaje derrotado
        defeat_x = character.x - self.camera_x
        defeat_y = character.y - self.camera_y
        self.screen.blit(gray_surface, (defeat_x, defeat_y))
        
        # Indicador visual de "derrotado" - cruz roja
        center_x = defeat_x + 50  # 100 / 2 = 50
        center_y = defeat_y + 50
        
        # Cruz roja sobre el personaje
        pygame.draw.line(self.screen, (255, 50, 50), 
                        (center_x - 15, center_y - 15), (center_x + 15, center_y + 15), 4)
        pygame.draw.line(self.screen, (255, 50, 50), 
                        (center_x + 15, center_y - 15), (center_x - 15, center_y + 15), 4)
        
        # Borde de la cruz en blanco para mejor visibilidad
        pygame.draw.line(self.screen, (255, 255, 255), 
                        (center_x - 15, center_y - 15), (center_x + 15, center_y + 15), 6)
        pygame.draw.line(self.screen, (255, 255, 255), 
                        (center_x + 15, center_y - 15), (center_x - 15, center_y + 15), 6)
        pygame.draw.line(self.screen, (255, 50, 50), 
                        (center_x - 15, center_y - 15), (center_x + 15, center_y + 15), 4)
        pygame.draw.line(self.screen, (255, 50, 50), 
                        (center_x + 15, center_y - 15), (center_x - 15, center_y + 15), 4)
    
    def draw_collectibles(self):
        """Dibuja todos los coleccionables: items estáticos y drops antiguos"""
        current_time = pygame.time.get_ticks()
        
        # Dibujar items estáticos nuevos
        for item in self.static_items:
            item.draw(self.screen, self.camera_x, self.camera_y, 
                     self.apple_image, self.potion_image)
        
        # Dibujar items del sistema antiguo (DEPRECADO)
        for item in self.dropped_items:
            screen_x = item['x'] - self.camera_x
            screen_y = item['y'] - self.camera_y
            
            # Solo dibujar si está en pantalla
            if (-50 < screen_x < self.screen_width + 50 and 
                -50 < screen_y < self.screen_height + 50):
                
                # Efecto de brillo y fade
                age = current_time - item['spawn_time']
                alpha = max(50, 255 - min(200, age // 100))
                
                # Usar superficie del sistema de items si existe, sino fallback
                if 'surface' in item and item['surface']:
                    temp_surface = item['surface'].copy()
                else:
                    # Fallback a imágenes locales
                    if item['type'] == 'apple':
                        temp_surface = self.apple_image.copy()
                    else:
                        temp_surface = self.potion_image.copy()
                
                temp_surface.set_alpha(alpha)
                
                # Efecto de flotación
                float_offset = int(5 * math.sin(current_time * 0.005 + item['x'] * 0.01))
                self.screen.blit(temp_surface, (screen_x, screen_y + float_offset))
        
        # Dibujar drops optimizados con sprites del juego
        for drop in self.drops:
            if not drop.collected:
                drop.draw(self.screen, self.camera_x, self.camera_y, 
                         self.apple_image, self.potion_image)
    
    def draw_floating_health_bars(self):
        """Dibuja barras de vida flotantes sobre los personajes"""
        for character in [self.juan, self.adan]:
            if hasattr(character, 'x') and hasattr(character, 'y'):
                # Posición en pantalla (ajustada por cámara)
                screen_x = character.x - self.camera_x
                screen_y = character.y - self.camera_y
                
                # Solo dibujar si está visible
                if (-100 < screen_x < self.screen_width + 100 and 
                    -100 < screen_y < self.screen_height + 100):
                    
                    # Configuración de la barra
                    bar_width = 80
                    bar_height = 8
                    bar_x = screen_x + 10  # Centrado sobre el personaje
                    bar_y = screen_y - 25  # Por encima del personaje
                    
                    # Fondo de la barra (negro)
                    pygame.draw.rect(self.screen, (50, 50, 50), 
                                   (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4))
                    
                    # Barra de vida actual
                    health_ratio = max(0, character.health / character.max_health)
                    current_bar_width = int(bar_width * health_ratio)
                    
                    # Color de la barra según la vida
                    if health_ratio > 0.6:
                        health_color = (100, 255, 100)  # Verde
                    elif health_ratio > 0.3:
                        health_color = (255, 255, 100)  # Amarillo
                    else:
                        health_color = (255, 100, 100)  # Rojo
                    
                    # Dibujar barra de vida
                    if current_bar_width > 0:
                        pygame.draw.rect(self.screen, health_color, 
                                       (bar_x, bar_y, current_bar_width, bar_height))
                    
                    # Nombre del personaje encima de la barra
                    font_small = pygame.font.Font(None, 24)
                    name_text = font_small.render(character.name, True, (255, 255, 255))
                    name_x = bar_x + (bar_width - name_text.get_width()) // 2
                    self.screen.blit(name_text, (name_x, bar_y - 20))
                    
                    # Indicador de escudo si está activo
                    if getattr(character, 'shield_active', False):
                        shield_surface = pygame.Surface((bar_width + 6, bar_height + 6), pygame.SRCALPHA)
                        pygame.draw.rect(shield_surface, (100, 200, 255, 100), 
                                       (0, 0, bar_width + 6, bar_height + 6))
                        self.screen.blit(shield_surface, (bar_x - 3, bar_y - 3))
                        
                        # Texto "ESCUDO"
                        shield_text = font_small.render("🛡️", True, (100, 200, 255))
                        self.screen.blit(shield_text, (bar_x + bar_width + 8, bar_y - 5))
    
    def draw_ui(self):
        """Dibuja interfaz de usuario simplificada (sin estadísticas de vida)"""
        font = pygame.font.Font(None, 72)
        font_small = pygame.font.Font(None, 48)
        
        # Mostrar pantalla de victoria si está activa
        if self.victory:
            self.draw_victory_screen()
            return
        
        # Mostrar pantalla de game over si está activa
        if self.game_over:
            self.draw_game_over_screen()
            return
        
        # UI simplificada del juego
        # Personaje activo con icono
        active_text = font.render(f"🎮 {self.active_character.name}", True, (255, 255, 255))
        self.screen.blit(active_text, (20, 20))
        
        # Mostrar progreso de gusanos (informativo)
        living_worms = len([worm for worm in self.worm_spawner.worms if worm.alive])
        progress_text = font_small.render(f"🐛 Spawneados: {self.worm_spawner.total_spawned}/{self.worm_spawner.max_worms} | Vivos: {living_worms}", 
                                        True, (200, 200, 200))
        self.screen.blit(progress_text, (20, 90))
        
        # Mostrar número de items disponibles
        active_items = len([item for item in self.static_items if item.active])
        if active_items > 0:
            items_text = font_small.render(f"💎 Items disponibles: {active_items}", True, (255, 215, 0))
            self.screen.blit(items_text, (20, 120))
    
    def draw_victory_screen(self):
        """Dibuja pantalla de victoria"""
        # Fondo semi-transparente
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 100, 0, 200))  # Verde oscuro
        self.screen.blit(overlay, (0, 0))
        
        font_huge = pygame.font.Font(None, 150)
        font_large = pygame.font.Font(None, 96)
        font_medium = pygame.font.Font(None, 72)
        
        # Título de victoria
        title = font_huge.render("🎉 ¡VICTORIA! 🎉", True, (255, 255, 100))
        title_rect = title.get_rect(center=(self.screen_width//2, 300))
        self.screen.blit(title, title_rect)
        
        # Mensaje
        msg = font_large.render("¡Todos los gusanos eliminados!", True, (255, 255, 255))
        msg_rect = msg.get_rect(center=(self.screen_width//2, 450))
        self.screen.blit(msg, msg_rect)
        
        # Estado
        status = font_medium.render("Cargando Nivel 2...", True, (200, 255, 200))
        status_rect = status.get_rect(center=(self.screen_width//2, 550))
        self.screen.blit(status, status_rect)
    
    def draw_game_over_screen(self):
        """Dibuja pantalla de game over"""
        # Fondo semi-transparente
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((100, 0, 0, 200))  # Rojo oscuro
        self.screen.blit(overlay, (0, 0))
        
        font_huge = pygame.font.Font(None, 150)
        font_large = pygame.font.Font(None, 96)
        font_medium = pygame.font.Font(None, 72)
        
        # Título de game over
        title = font_huge.render("💀 GAME OVER 💀", True, (255, 100, 100))
        title_rect = title.get_rect(center=(self.screen_width//2, 300))
        self.screen.blit(title, title_rect)
        
        # Mensaje
        msg = font_large.render(f"{self.active_character.name} ha caído", True, (255, 255, 255))
        msg_rect = msg.get_rect(center=(self.screen_width//2, 450))
        self.screen.blit(msg, msg_rect)
        
        # Opciones
        restart = font_medium.render("R - Reintentar", True, (200, 255, 200))
        restart_rect = restart.get_rect(center=(self.screen_width//2, 520))
        self.screen.blit(restart, restart_rect)
        
        menu = font_medium.render("M - Menú Principal", True, (200, 200, 255))
        menu_rect = menu.get_rect(center=(self.screen_width//2, 580))
        self.screen.blit(menu, menu_rect)
        
        exit_text = font_medium.render("ESC - Salir", True, (255, 200, 200))
        exit_rect = exit_text.get_rect(center=(self.screen_width//2, 640))
        self.screen.blit(exit_text, exit_rect)
    
    def draw_upgrade_menu(self):
        """Dibuja menú de mejoras"""
        # Fondo semi-transparente
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        font = pygame.font.Font(None, 72)
        font_small = pygame.font.Font(None, 48)
        
        # Título
        title = font.render("🍎 MEJORAS DISPONIBLES", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen_width//2, 300))
        self.screen.blit(title, title_rect)
        
        # Opciones simplificadas y limpias (sin estadísticas de daño)
        options = [
            "1 - 🚀 Velocidad de Movimiento",
            "2 - ⚔️ Poder de Ataque",
            "3 - ❤️ Resistencia Vital"
        ]
        
        # Texto de pausa
        pause_text = font.render("⏸️ JUEGO PAUSADO", True, (255, 255, 100))
        pause_rect = pause_text.get_rect(center=(self.screen_width//2, 200))
        self.screen.blit(pause_text, pause_rect)
        
        for i, option in enumerate(options):
            option_text = font_small.render(option, True, (200, 255, 200))
            option_rect = option_text.get_rect(center=(self.screen_width//2, 400 + i * 60))
            self.screen.blit(option_text, option_rect)
    
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
    
    def draw_game_over(self):
        """Dibuja pantalla de game over"""
        # Ya no necesitamos overlay porque tenemos fondo negro sólido
        
        font_large = pygame.font.Font(None, 144)
        font_small = pygame.font.Font(None, 72)
        
        # Título
        game_over_text = font_large.render("💀 GAME OVER", True, (255, 50, 50))
        game_over_rect = game_over_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 100))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Instrucciones con espaciado consistente
        restart_text = font_small.render("R - Reintentar  |  M - Menú Principal", True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(self.screen_width//2, self.screen_height//2 + 50))
        self.screen.blit(restart_text, restart_rect)
        
        esc_text = font_small.render("ESC - Salir del juego", True, (200, 200, 200))
        esc_rect = esc_text.get_rect(center=(self.screen_width//2, self.screen_height//2 + 100))
        self.screen.blit(esc_text, esc_rect)
        
        # Estadísticas con espaciado consistente (50 píxeles como los demás)
        stats_text = font_small.render(f"Gusanos derrotados: {self.enemies_defeated}", True, (200, 200, 200))
        stats_rect = stats_text.get_rect(center=(self.screen_width//2, self.screen_height//2 + 150))
        self.screen.blit(stats_text, stats_rect)
    
    def draw_victory(self):
        """Dibuja pantalla de victoria"""
        # Ya no necesitamos overlay porque tenemos fondo negro sólido
        
        font_large = pygame.font.Font(None, 144)
        font_medium = pygame.font.Font(None, 96)
        font_small = pygame.font.Font(None, 72)
        
        # Título
        victory_text = font_large.render("🎉 ¡NIVEL 1 COMPLETADO!", True, (255, 215, 0))
        victory_rect = victory_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 150))
        self.screen.blit(victory_text, victory_rect)
        
        # Mensaje dinámico (normal o transición automática)
        if self.transition_to_level_2_flag:
            message_text = font_medium.render(self.victory_message, True, (255, 215, 0))
            # Transición automática inmediata (solo 0.5 segundos para mostrar mensaje)
            if not hasattr(self, 'transition_timer'):
                self.transition_timer = pygame.time.get_ticks()
            elif pygame.time.get_ticks() - self.transition_timer >= 500:
                print("🌟 Transición automática iniciando...")
                self.launch_level_2()
                return
        else:
            message_text = font_medium.render("¡Has liberado la Tierra de las Manzanas!", True, (255, 255, 255))
        
        message_rect = message_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 50))
        self.screen.blit(message_text, message_rect)
        
        # Estadísticas
        stats_text = font_small.render(f"Gusanos derrotados: {self.enemies_defeated}", True, (200, 255, 200))
        stats_rect = stats_text.get_rect(center=(self.screen_width//2, self.screen_height//2 + 20))
        self.screen.blit(stats_text, stats_rect)
        
        # Botón para Nivel 2 (solo si no hay transición automática)
        if not self.transition_to_level_2_flag:
            nivel2_text = font_medium.render("⬆️ Presiona N para ir al NIVEL 2", True, (255, 100, 100))
            nivel2_rect = nivel2_text.get_rect(center=(self.screen_width//2, self.screen_height//2 + 80))
            
            # Fondo para el botón de Nivel 2
            button_bg = pygame.Rect(nivel2_rect.x - 20, nivel2_rect.y - 10, 
                                   nivel2_rect.width + 40, nivel2_rect.height + 20)
            pygame.draw.rect(self.screen, (50, 0, 50), button_bg)
            pygame.draw.rect(self.screen, (255, 100, 100), button_bg, 3)
            
            self.screen.blit(nivel2_text, nivel2_rect)
        else:
            # Mostrar indicador de transición automática
            auto_text = font_small.render("⏱️ Transición automática en curso...", True, (255, 215, 0))
            auto_rect = auto_text.get_rect(center=(self.screen_width//2, self.screen_height//2 + 80))
            self.screen.blit(auto_text, auto_rect)
        
        # Opción de reinicio (solo si no hay transición automática)
        if not self.transition_to_level_2_flag:
            restart_text = font_small.render("R - Reiniciar  |  M - Menú Principal", True, (200, 200, 200))
            restart_rect = restart_text.get_rect(center=(self.screen_width//2, self.screen_height//2 + 150))
            self.screen.blit(restart_text, restart_rect)
    
    def draw_pause_screen(self):
        """Dibuja la pantalla de pausa con opciones"""
        # Fondo semitransparente
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        # Título de pausa
        pause_font = pygame.font.Font(None, 96)
        pause_text = pause_font.render("⏸️ PAUSADO", True, (255, 255, 255))
        pause_rect = pause_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 100))
        self.screen.blit(pause_text, pause_rect)
        
        # Opciones del menú de pausa
        option_font = pygame.font.Font(None, 48)
        options = [
            "P - Continuar juego",
            "M - Menú Principal",
            "ESC - Salir del juego"
        ]
        
        for i, option in enumerate(options):
            color = (200, 200, 255) if "Continuar" in option else (255, 200, 200)
            option_text = option_font.render(option, True, color)
            option_rect = option_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 20 + i * 60))
            self.screen.blit(option_text, option_rect)
    
    def format_time(self, seconds):
        """Formatea el tiempo en minutos:segundos"""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    # === BUCLE PRINCIPAL ===
    
    def run(self):
        """Bucle principal del juego"""
        print("🚀 Iniciando Nivel 1 - Tierra de las Manzanas...")
        
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps)
        
        print("👋 ¡Gracias por jugar!")
        pygame.quit()
        sys.exit()


# === FUNCIÓN PRINCIPAL ===

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
    
    # Ejecutar intro (inicializa pygame internamente)
    intro = IntroCinematica()
    result = intro.run()
    
    if result and result.startswith('start_game_'):
        # Extraer personaje seleccionado
        selected_character = result.split('_')[-1]
        print(f"🎮 Iniciando juego con {selected_character.upper()}")
        
        # Cerrar ventana de intro
        pygame.quit()
        
        # Crear y ejecutar el juego
        game = Game(selected_character)
        game.run()
    else:
        print(f"❌ Resultado inesperado de intro: {result}")
        pygame.quit()
        sys.exit()