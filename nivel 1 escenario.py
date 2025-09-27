#!/usr/bin/env python3
"""
NIVEL 1 - LA TIERRA DE LAS MANZANAS
Juego completo con 15 gusanos, sistema de mejoras, y mecánicas optimizadas.
Creado desde cero de forma limpia y organizada.
"""

import pygame
import sys
import random
import math
import os
from PIL import Image
import requests
from io import BytesIO

# Importaciones de módulos del juego
from adan_attacks import AdanAttack
from adan_character_animation import AdanCharacter
from audio_manager import get_audio_manager
from character_ai import CharacterAI
from intro_cinematica import IntroCinematica
from juan_attacks import JuanAttack
from juan_character_animation import JuanCharacter
from loading_screen import LoadingScreen
from worm_enemy import WormEnemy, WormSpawner


class CollisionBlock:
    """Bloque invisible de colisión para restringir movimiento"""
    def __init__(self, x, y, width=32, height=32):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
    
    def draw_editor(self, screen, camera_x, camera_y):
        """Dibuja el bloque en modo editor"""
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Solo dibujar si está visible
        if (-self.width < screen_x < screen.get_width() + self.width and 
            -self.height < screen_y < screen.get_height() + self.height):
            
            # Bloque semi-transparente rojo
            block_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            block_surface.fill((255, 0, 0, 128))
            screen.blit(block_surface, (screen_x, screen_y))
            
            # Borde blanco
            pygame.draw.rect(screen, (255, 255, 255), 
                           (screen_x, screen_y, self.width, self.height), 2)


class CollisionManager:
    """Maneja las colisiones con bloques invisibles"""
    def __init__(self, world_width=1980, world_height=1080):
        self.blocks = []
        self.editor_mode = False
        self.block_size = 32
        self.editor_cursor_x = 100
        self.editor_cursor_y = 100
        self.world_width = world_width
        self.world_height = world_height
    
    def add_block(self, x, y):
        """Añade un bloque de colisión"""
        # Alinear a la grilla
        grid_x = (x // self.block_size) * self.block_size
        grid_y = (y // self.block_size) * self.block_size
        
        # Verificar si ya existe un bloque en esa posición
        for block in self.blocks:
            if block.x == grid_x and block.y == grid_y:
                return False
        
        self.blocks.append(CollisionBlock(grid_x, grid_y, self.block_size, self.block_size))
        return True
    
    def remove_block(self, x, y):
        """Remueve un bloque de colisión"""
        grid_x = (x // self.block_size) * self.block_size
        grid_y = (y // self.block_size) * self.block_size
        
        for block in self.blocks[:]:
            if block.x == grid_x and block.y == grid_y:
                self.blocks.remove(block)
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
        test_rect = pygame.Rect(new_x, new_y, 64, 64)
        
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
        
        # Dibujar cursor del editor
        cursor_screen_x = self.editor_cursor_x - camera_x
        cursor_screen_y = self.editor_cursor_y - camera_y
        
        cursor_surface = pygame.Surface((self.block_size, self.block_size), pygame.SRCALPHA)
        cursor_surface.fill((0, 255, 0, 100))
        screen.blit(cursor_surface, (cursor_screen_x, cursor_screen_y))
        pygame.draw.rect(screen, (0, 255, 0), 
                        (cursor_screen_x, cursor_screen_y, self.block_size, self.block_size), 3)
        
        # Información del editor
        font = pygame.font.Font(None, 48)
        editor_info = [
            "🛠️ MODO EDITOR DE COLISIONES",
            "Flechas: Mover cursor | ESPACIO: Agregar bloque",
            "BACKSPACE: Eliminar bloque | E: Salir del editor",
            f"Cursor: ({self.editor_cursor_x}, {self.editor_cursor_y})",
            f"Bloques totales: {len(self.blocks)}"
        ]
        
        for i, info in enumerate(editor_info):
            color = (255, 255, 0) if i == 0 else (255, 255, 255)
            text = font.render(info, True, color)
            # Fondo semi-transparente para el texto
            text_bg = pygame.Surface((text.get_width() + 20, text.get_height() + 10), pygame.SRCALPHA)
            text_bg.fill((0, 0, 0, 180))
            screen.blit(text_bg, (10, 10 + i * 50))
            screen.blit(text, (20, 15 + i * 50))
    
    def handle_editor_input(self, keys_pressed, keys_just_pressed):
        """Maneja input del modo editor"""
        if not self.editor_mode:
            return
        
        move_speed = self.block_size
        
        # Mover cursor con flechas
        if keys_just_pressed.get(pygame.K_LEFT, False):
            self.editor_cursor_x = max(0, self.editor_cursor_x - move_speed)
        elif keys_just_pressed.get(pygame.K_RIGHT, False):
            self.editor_cursor_x = min(self.world_width - self.block_size, self.editor_cursor_x + move_speed)
        elif keys_just_pressed.get(pygame.K_UP, False):
            self.editor_cursor_y = max(0, self.editor_cursor_y - move_speed)
        elif keys_just_pressed.get(pygame.K_DOWN, False):
            self.editor_cursor_y = min(self.world_height - self.block_size, self.editor_cursor_y + move_speed)
        
        # Agregar bloque con ESPACIO
        if keys_just_pressed.get(pygame.K_SPACE, False):
            if self.add_block(self.editor_cursor_x, self.editor_cursor_y):
                print(f"✅ Bloque agregado en ({self.editor_cursor_x}, {self.editor_cursor_y})")
            else:
                print(f"⚠️ Ya existe un bloque en esa posición")
        
        # Eliminar bloque con BACKSPACE
        if keys_just_pressed.get(pygame.K_BACKSPACE, False):
            if self.remove_block(self.editor_cursor_x, self.editor_cursor_y):
                print(f"🗑️ Bloque eliminado en ({self.editor_cursor_x}, {self.editor_cursor_y})")
            else:
                print(f"⚠️ No hay bloque para eliminar en esa posición")
    
    def save_collision_data(self, filename="collision_data.txt"):
        """Guarda los datos de colisión en un archivo"""
        try:
            with open(filename, 'w') as f:
                f.write(f"# Datos de colisión del Nivel 1 - {len(self.blocks)} bloques\n")
                for block in self.blocks:
                    f.write(f"{block.x},{block.y},{block.width},{block.height}\n")
            print(f"💾 Datos de colisión guardados en {filename}")
        except Exception as e:
            print(f"❌ Error guardando datos: {e}")
    
    def load_collision_data(self, filename="collision_data.txt"):
        """Carga los datos de colisión desde un archivo"""
        try:
            if not os.path.exists(filename):
                print(f"📁 Archivo {filename} no existe, usando configuración por defecto")
                return
            
            self.blocks.clear()
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split(',')
                        if len(parts) >= 4:
                            x, y, w, h = map(int, parts[:4])
                            self.blocks.append(CollisionBlock(x, y, w, h))
            
            print(f"📂 Cargados {len(self.blocks)} bloques de colisión desde {filename}")
        except Exception as e:
            print(f"❌ Error cargando datos: {e}")


class Background:
    """Maneja el fondo del juego con scroll y carga desde GitHub"""
    
    def __init__(self, image_url):
        self.image_url = image_url
        # Dimensiones dinámicas basadas en la imagen original
        self.width = 1980  # Valor por defecto
        self.height = 1080  # Valor por defecto  
        self.surface = None
        self.load_background(image_url)
        
    def load_background(self, url):
        """Carga el fondo desde GitHub respetando las dimensiones originales"""
        try:
            print("📥 Descargando escenario desde GitHub...")
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            image_data = BytesIO(response.content)
            pil_image = Image.open(image_data)
            
            # Información de la imagen original
            original_width, original_height = pil_image.size
            print(f"📐 Dimensiones originales del PNG: {original_width}x{original_height}")
            
            # RESPETAR DIMENSIONES ORIGINALES - No redimensionar
            self.width = original_width
            self.height = original_height
            print(f"✅ Usando dimensiones originales del escenario: {self.width}x{self.height}")
            
            # Convertir a formato pygame
            pil_image = pil_image.convert('RGB')
            image_data = pil_image.tobytes()
            
            self.surface = pygame.image.fromstring(image_data, pil_image.size, 'RGB')
            self.surface = self.surface.convert()
            
            print(f"✅ Escenario cargado exitosamente: 1980x1080")
            
        except Exception as e:
            print(f"❌ Error cargando escenario: {e}")
            self.create_fallback_background()
    
    def create_fallback_background(self):
        """Crea un fondo de respaldo de 1980x1080 si falla GitHub"""
        print("🎨 Creando fondo de respaldo de 1980x1080...")
        self.surface = pygame.Surface((1980, 1080))
        
        # Gradiente verde para simular césped en todo el escenario
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
        """Inicializa el juego con todas las características optimizadas"""
        print("🔍 DEBUG: Iniciando constructor de Game...")
        pygame.init()
        
        # === CONFIGURACIÓN DE PANTALLA ===
        self.screen_width = 1920
        self.screen_height = 1080
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        pygame.display.set_caption("🍎 Nivel 1 - Tierra de las Manzanas")
        
        # Verificar resolución
        actual_size = self.screen.get_size()
        print(f"🖥️ Resolución: {actual_size[0]}x{actual_size[1]}")
        self.screen_width, self.screen_height = actual_size
        
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # === SISTEMA DE CARGA ===
        self.loading_screen = LoadingScreen(self.screen)
        assets = [
            {"name": "Escenario", "description": "Cargando fondo"},
            {"name": "Personajes", "description": "Cargando Juan y Adán"},
            {"name": "Ataques", "description": "Sistemas de combate"},
            {"name": "Enemigos", "description": "15 gusanos enemigos"},
            {"name": "Audio", "description": "Música y efectos"},
            {"name": "IA", "description": "Inteligencia artificial"}
        ]
        self.loading_screen.start_loading(assets)
        
        # === CARGA DE ESCENARIO ===
        self.loading_screen.update_progress("Escenario", "Descargando desde GitHub...")
        self.loading_screen.draw()
        
        # URL del escenario principal (PNG largo)
        escenario_url = "https://github.com/user-attachments/assets/0575a74a-96b6-4c69-b052-ad187ee067d4"
        
        # Cargar solo el escenario principal
        self.background = Background(escenario_url)
        
        # Configurar mundo con dimensiones dinámicas del escenario cargado
        self.world_width = self.background.width  # Ancho real del escenario
        self.world_height = self.background.height  # Alto real del escenario
        
        print(f"🗺️ Mundo configurado: {self.world_width}x{self.world_height}")
        
        # === CARGA DE PERSONAJES ===
        self.loading_screen.update_progress("Personajes", "Cargando Juan...")
        self.loading_screen.draw()
        
        self.juan = JuanCharacter(400, 300)
        self.juan.max_health = 100  # Menos vida que Adán
        self.juan.health = 100
        self.juan.speed = 6.5  # Más velocidad que Adán
        self.juan.damage = 22  # Menos daño que Adán
        self.juan.attack_speed = 1.0  # Velocidad de ataque estándar
        self.juan.name = "Juan"
        
        self.loading_screen.update_progress("Personajes", "Cargando Adán...")
        self.loading_screen.draw()
        
        self.adan = AdanCharacter(500, 300)
        self.adan.max_health = 125  # Más vida que Juan
        self.adan.health = 125
        self.adan.speed = 5.5  # Menos velocidad que Juan
        self.adan.damage = 28  # Más daño que Juan
        self.adan.attack_speed = 0.8  # Ataques más lentos pero potentes
        self.adan.name = "Adán"
        
        # === SISTEMAS DE ATAQUE ===
        self.loading_screen.update_progress("Ataques", "Configurando combate...")
        self.loading_screen.draw()
        
        self.juan_attack = JuanAttack(self.juan)
        self.adan_attack = AdanAttack(self.adan)
        
        # === SISTEMA DE PERSONAJES ACTIVO/INACTIVO ===
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
        
        # === SISTEMA DE ENEMIGOS (15 GUSANOS) ===
        self.loading_screen.update_progress("Enemigos", "Creando 15 gusanos...")
        self.loading_screen.draw()
        
        self.worm_spawner = WormSpawner(max_worms=15)
        self.setup_enemy_spawns()
        
        # === IA Y AUDIO ===
        self.loading_screen.update_progress("IA", "Configurando inteligencia artificial...")
        self.loading_screen.draw()
        
        self.inactive_ai = CharacterAI(self.inactive_character, self.active_character)
        # CONFIGURACIÓN EXACTA DEL NIVEL 2 - Mejorar la IA para ser más agresiva
        self.inactive_ai.detection_range = 400  # Igual que nivel 2
        self.inactive_ai.attack_range = 150     # Igual que nivel 2
        print(f"🤖 IA mejorada para {self.inactive_character.name}: Detección={self.inactive_ai.detection_range}px, Ataque={self.inactive_ai.attack_range}px")
        
        self.loading_screen.update_progress("Audio", "Cargando sonidos...")
        self.loading_screen.draw()
        
        self.audio = get_audio_manager()
        
        # === ESTADO DEL JUEGO ===
        self.game_over = False
        self.victory = False
        self.enemies_defeated = 0
        self.victory_condition = 15  # Derrotar 15 gusanos
        
        # === SISTEMA DE COLECCIONABLES ===
        self.dropped_items = []
        self.upgrades = {'speed': 0, 'damage': 0, 'attack_speed': 0, 'health': 0}
        self.show_upgrade_menu = False
        self.upgrade_menu_timer = 0
        
        # === SISTEMA DE REVIVIR ===
        self.revival_distance = 100
        self.show_revival_prompt = False
        self.revival_key_pressed = False
        
        # === SISTEMA DE ESCUDO ===
        self.shield_duration = 900  # 15 segundos a 60 FPS
        
        # === CÁMARA ===
        self.camera_x = 0
        self.camera_y = 0
        self.switch_cooldown = 0
        
        # === SISTEMA DE COLISIONES Y EDITOR ===
        self.collision_manager = CollisionManager(self.world_width, self.world_height)
        self.collision_manager.load_collision_data()  # Cargar colisiones guardadas
        
        # Si no hay datos guardados, empezar con escenario limpio
        if len(self.collision_manager.blocks) == 0:
            print("📋 Escenario sin obstáculos - Usa F1 para crear colisiones personalizadas")
            print("🛠️ CONTROLES DEL EDITOR:")
            print("   F1: Activar/Desactivar modo editor")
            print("   Flechas: Mover cursor")
            print("   Espacio: Colocar bloque invisible")  
            print("   Backspace: Eliminar bloque invisible")
            print("   Los bloques se guardan automáticamente al salir del editor")
        
        # Inicializar keys_last_frame como lista
        temp_keys = pygame.key.get_pressed()
        self.keys_last_frame = list(temp_keys)
        
        # === CREAR IMÁGENES DE COLECCIONABLES ===
        self.create_collectible_images()
        
        # === FINALIZAR CARGA ===
        self.loading_screen.update_progress("Completado", "¡Iniciando batalla!")
        self.loading_screen.draw()
        pygame.time.wait(1000)
        
        print("✅ Nivel 1 inicializado correctamente")
    
    def setup_enemy_spawns(self):
        """Configura 6 áreas de spawn para los 15 gusanos"""
        spawn_areas = [
            (100, 100, 200, 200),    # Esquina superior izquierda
            (800, 200, 200, 200),    # Centro superior
            (1400, 100, 200, 200),   # Esquina superior derecha
            (200, 600, 200, 200),    # Centro izquierda
            (1200, 600, 200, 200),   # Centro derecha
            (600, 800, 200, 200),    # Centro inferior
        ]
        
        for x, y, w, h in spawn_areas:
            self.worm_spawner.add_spawn_area(x, y, w, h)
        
        print("✅ 6 áreas de spawn configuradas para 15 gusanos")
    

    def create_collectible_images(self):
        """Crea sprites mejorados para manzanas y pociones"""
        # Manzana más grande y visible
        self.apple_image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(self.apple_image, (220, 50, 50), (20, 22), 16)  # Más grande
        pygame.draw.circle(self.apple_image, (255, 100, 100), (16, 18), 12)
        pygame.draw.rect(self.apple_image, (139, 69, 19), (18, 6, 6, 12))
        pygame.draw.ellipse(self.apple_image, (34, 139, 34), (14, 4, 12, 8))
        # Brillo para más visibilidad
        pygame.draw.circle(self.apple_image, (255, 200, 200, 80), (15, 15), 8)
        
        # Poción más grande y visible  
        self.potion_image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.rect(self.potion_image, (100, 100, 100), (16, 18, 8, 16))
        pygame.draw.ellipse(self.potion_image, (20, 100, 220), (14, 22, 12, 12))
        pygame.draw.rect(self.potion_image, (50, 150, 255), (18, 14, 4, 14))
        pygame.draw.circle(self.potion_image, (100, 200, 255), (20, 26), 5)
        # Efecto de brillo
        pygame.draw.circle(self.potion_image, (150, 220, 255, 60), (20, 26), 10)
    
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
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_F1:
                    # Toggle modo editor
                    self.collision_manager.editor_mode = not self.collision_manager.editor_mode
                    mode = "activado" if self.collision_manager.editor_mode else "desactivado"
                    print(f"🛠️ Modo editor {mode}")
                    if not self.collision_manager.editor_mode:
                        self.collision_manager.save_collision_data()
                elif event.key == pygame.K_r and (self.game_over or self.victory):
                    self.restart_game()
                elif event.key == pygame.K_n and self.victory:
                    # Ir al Nivel 2
                    print("🌟 Iniciando transición al Nivel 2...")
                    self.launch_level_2()
                    return False
                elif event.key == pygame.K_TAB and not self.collision_manager.editor_mode:
                    self.switch_character()
                elif event.key == pygame.K_x and not self.collision_manager.editor_mode:
                    self.perform_special_attack()
                elif self.show_upgrade_menu and event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                    self.handle_upgrade_selection(event.key)
                    self.show_upgrade_menu = False
        
        # Manejo del modo editor
        if self.collision_manager.editor_mode:
            self.collision_manager.handle_editor_input(keys_pressed, keys_just_pressed)
            # En modo editor, no procesar otros inputs
            return True
        
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
        
        self.revival_key_pressed = e_key_pressed
        
        # Manejo de ataques básicos con ESPACIO (solo si no está en modo editor)
        if keys_pressed[pygame.K_SPACE]:
            self.perform_basic_attack()
        
        return True
    
    def switch_character(self):
        """Cambia entre Juan y Adán manteniendo configuración avanzada de IA"""
        if self.switch_cooldown <= 0 and not self.game_over and not self.victory:
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
        
        worms = self.worm_spawner.get_worms()
        self.active_attack_system.handle_attack_input(pygame.key.get_pressed(), worms)
    
    def perform_special_attack(self):
        """Realiza ataque especial (X)"""
        if self.game_over or self.victory:
            return
        
        worms = self.worm_spawner.get_worms()
        
        if self.active_character == self.juan:
            hit = self.juan_attack.special_attack(worms)
            # El conteo se maneja en process_worm_drops()
        else:  # Adán
            if worms:
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
        if self.game_over or self.victory:
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
            
            self.enforce_boundaries(self.active_character)
        
        # Actualizar IA del personaje inactivo - SISTEMA DEL NIVEL 2 EXACTO
        if (self.inactive_character.health > 0 or self.inactive_ai.is_being_revived) and not self.collision_manager.editor_mode:
            old_x, old_y = self.inactive_character.x, self.inactive_character.y
            
            # Obtener enemigos para la IA (gusanos en nivel 1, chamán en nivel 2)
            worms = self.worm_spawner.get_worms()
            
            # EXACTAMENTE COMO EN NIVEL 2: La IA se enfoca en los enemigos
            self.inactive_ai.update(worms)
            
            # EXACTAMENTE COMO EN NIVEL 2: Obtener estado de animación y actualizar personaje
            ai_animation_state = self.inactive_ai.get_animation_state()
            self.inactive_character.update(keys_pressed=None, ai_controlled=True, ai_direction=ai_animation_state)
            
            # Verificar colisiones para IA
            if not self.collision_manager.can_move_to(self.inactive_character,
                                                     self.inactive_character.x,
                                                     self.inactive_character.y):
                self.inactive_character.x, self.inactive_character.y = old_x, old_y
            
            # Aplicar límites del mundo (igual que en nivel 2)
            self.enforce_boundaries(self.inactive_character)
        
        # EXACTAMENTE COMO EN NIVEL 2: Manejar ataques del personaje activo
        worms = self.worm_spawner.get_worms()
        self.active_attack_system.handle_attack_input(keys_pressed, worms)
        
        # SISTEMA DE ATAQUES AUTOMÁTICOS DE IA MEJORADO
        # Solo activar ataques si la IA está realmente en estado de ataque y tiene objetivo
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
                    pygame.K_UP: False, pygame.K_DOWN: False,
                    pygame.K_LEFT: False, pygame.K_RIGHT: False,
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
        
        # Actualizar enemigos
        players = [self.juan, self.adan]
        self.worm_spawner.update(players)
        
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
                                    player.take_damage(worm.attack_damage)
                                    print(f"💥 {player.name} recibió {worm.attack_damage} daño")
                                else:
                                    print(f"🛡️ {player.name} bloqueó el ataque con escudo")
                                worm.last_attack_time = current_time
    
    def process_worm_drops(self):
        """Procesa drops de gusanos muertos y conteo de derrotas"""
        # Procesar gusanos muertos del spawner
        for worm in self.worm_spawner.worms[:]:
            if not worm.alive and not getattr(worm, 'drop_processed', False):
                worm.drop_processed = True
                self.enemies_defeated += 1
                
                print(f"💀 Gusano derrotado! Total: {self.enemies_defeated}/{self.victory_condition}")
                
                # Generar drops con probabilidades mejoradas
                drop_x = worm.x + random.randint(-40, 40)
                drop_y = worm.y + random.randint(-40, 40)
                
                # 70% probabilidad total de drop
                drop_chance = random.random()
                if drop_chance < 0.70:
                    # 50% manzana, 20% poción
                    if random.random() < 0.714:  # 50/70 = 0.714
                        self.dropped_items.append({
                            'type': 'apple',
                            'x': drop_x, 'y': drop_y,
                            'spawn_time': pygame.time.get_ticks()
                        })
                        print("🍎 Drop: Manzana de poder")
                    else:
                        self.dropped_items.append({
                            'type': 'potion',
                            'x': drop_x, 'y': drop_y,
                            'spawn_time': pygame.time.get_ticks()
                        })
                        print("🧪 Drop: Poción de escudo")
                
                # Remover el gusano muerto del spawner
                self.worm_spawner.worms.remove(worm)
    
    def update_collectibles(self):
        """Actualiza coleccionables y colisiones"""
        current_time = pygame.time.get_ticks()
        
        # Eliminar items viejos (30 segundos)
        self.dropped_items = [item for item in self.dropped_items 
                            if current_time - item['spawn_time'] < 30000]
        
        # Verificar colisiones
        active_rect = pygame.Rect(self.active_character.x, self.active_character.y, 64, 64)
        inactive_rect = pygame.Rect(self.inactive_character.x, self.inactive_character.y, 64, 64)
        
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
        # Victoria: 15 gusanos derrotados -> Ir a Nivel 2
        if self.enemies_defeated >= self.victory_condition:
            self.victory = True
            print("🎉 ¡VICTORIA! Has completado el Nivel 1")
            print("🌟 Preparando transición al Nivel 2...")
        
        # Derrota: ambos personajes muertos
        if self.juan.health <= 0 and self.adan.health <= 0:
            self.game_over = True
            print("💀 GAME OVER - Ambos personajes han caído")
    
    # === SISTEMA DE MEJORAS ===
    
    def collect_apple(self):
        """Recolecta manzana y muestra menú de mejoras"""
        print("🍎 ¡Manzana recogida! Selecciona mejora:")
        print("1-Velocidad | 2-Daño | 3-Vel.Ataque | 4-Vida")
        self.show_upgrade_menu = True
        self.upgrade_menu_timer = 300  # 5 segundos
    
    def collect_potion(self, character):
        """Recolecta poción y activa escudo"""
        print(f"🧪 {character.name} consumió poción de escudo")
        character.shield_active = True
        character.shield_timer = 0
        print(f"🛡️ Escudo activado para {character.name}")
    
    def handle_upgrade_selection(self, key):
        """Maneja selección de mejora"""
        character = self.active_character
        
        if key == pygame.K_1:  # Velocidad
            character.speed += 0.5
            self.upgrades['speed'] += 1
            print(f"🚀 Velocidad mejorada: {character.speed:.1f}")
            
        elif key == pygame.K_2:  # Daño
            if hasattr(self.active_attack_system, 'melee_damage'):
                self.active_attack_system.melee_damage += 5
            if hasattr(self.active_attack_system, 'projectile_damage'):
                self.active_attack_system.projectile_damage += 3
            self.upgrades['damage'] += 1
            print(f"⚔️ Daño mejorado (nivel {self.upgrades['damage']})")
            
        elif key == pygame.K_3:  # Velocidad de ataque
            if hasattr(self.active_attack_system, 'attack_cooldown'):
                self.active_attack_system.attack_cooldown = max(200, 
                    self.active_attack_system.attack_cooldown - 30)
            self.upgrades['attack_speed'] += 1
            print(f"⚡ Velocidad de ataque mejorada")
            
        elif key == pygame.K_4:  # Vida
            character.max_health += 15
            character.health = min(character.health + 15, character.max_health)
            self.upgrades['health'] += 1
            print(f"❤️ Vida mejorada: {character.health}/{character.max_health}")
    
    # === UTILIDADES ===
    
    def enforce_boundaries(self, character):
        """Aplica límites exactos del escenario con dimensiones originales"""
        # Límites dinámicos basados en el tamaño real del escenario
        left_limit = 0
        right_limit = self.world_width - 64  # Ancho del personaje
        top_limit = 0
        bottom_limit = self.world_height - 64  # Alto del personaje
        
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
        
        # Limpiar enemigos
        self.worm_spawner.worms.clear()
        
        # Reiniciar estado
        self.game_over = False
        self.victory = False
        self.enemies_defeated = 0
        self.dropped_items.clear()
        
        print("🔄 Juego reiniciado")
    
    def launch_level_2(self):
        """Lanza el Nivel 2 del juego"""
        try:
            print("🚀 Cargando Nivel 2...")
            
            # Determinar personaje seleccionado
            selected_character = 'juan' if self.active_character == self.juan else 'adan'
            
            # Cerrar pygame del nivel actual
            pygame.quit()
            
            # Importar y ejecutar Nivel 2
            from nivel_2 import Nivel2
            
            # Crear e iniciar Nivel 2
            nivel2 = Nivel2(selected_character)
            nivel2.run()
            
        except ImportError:
            print("❌ Error: No se pudo cargar el archivo nivel_2.py")
            print("Asegúrate de que el archivo nivel_2.py esté en la misma carpeta")
        except Exception as e:
            print(f"❌ Error lanzando Nivel 2: {e}")
            
        # Reinicializar pygame para este nivel si hay error
        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
    
    # === RENDERIZADO ===
    
    def draw(self):
        """Dibuja todo el juego"""
        # Limpiar pantalla
        self.screen.fill((50, 100, 50))
        
        # Dibujar fondo (escenario principal PNG 1980x1080)
        self.background.draw(self.screen, self.camera_x, self.camera_y, 
                           self.screen_width, self.screen_height)
        
        # EXACTAMENTE COMO EN NIVEL 2: Dibujar personajes (inactivo primero para orden de capas)
        if self.inactive_character.health > 0:
            if not self.inactive_attack_system.is_character_attacking():
                self.inactive_character.draw(self.screen, self.camera_x, self.camera_y)
                # Efecto de escudo si está activo
                if hasattr(self.inactive_character, 'shield_active') and self.inactive_character.shield_active:
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
        
        # Dibujar UI
        self.draw_ui()
        
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
        
        # Pantallas de fin
        if self.game_over:
            self.draw_game_over()
        elif self.victory:
            self.draw_victory()
        
        pygame.display.flip()
    
    def draw_shield_effect(self, character):
        """Dibuja efecto visual de escudo mejorado"""
        if not hasattr(character, 'shield_active') or not character.shield_active:
            return
            
        # Círculo pulsante alrededor del personaje
        shield_alpha = int(100 + 50 * math.sin(pygame.time.get_ticks() * 0.01))
        shield_surface = pygame.Surface((80, 80), pygame.SRCALPHA)
        
        # Efecto de escudo con múltiples capas
        pygame.draw.circle(shield_surface, (0, 150, 255, shield_alpha//2), (40, 40), 35)
        pygame.draw.circle(shield_surface, (100, 200, 255, shield_alpha), (40, 40), 30)
        pygame.draw.circle(shield_surface, (150, 220, 255, shield_alpha//3), (40, 40), 25)
        
        shield_x = character.x - self.camera_x - 8
        shield_y = character.y - self.camera_y - 8
        self.screen.blit(shield_surface, (shield_x, shield_y))
    

    
    def draw_collectibles(self):
        """Dibuja manzanas y pociones"""
        current_time = pygame.time.get_ticks()
        
        for item in self.dropped_items:
            screen_x = item['x'] - self.camera_x
            screen_y = item['y'] - self.camera_y
            
            # Solo dibujar si está en pantalla
            if (-50 < screen_x < self.screen_width + 50 and 
                -50 < screen_y < self.screen_height + 50):
                
                # Efecto de brillo
                age = current_time - item['spawn_time']
                alpha = 255 - min(200, age // 100)
                
                if item['type'] == 'apple':
                    temp_surface = self.apple_image.copy()
                else:
                    temp_surface = self.potion_image.copy()
                
                temp_surface.set_alpha(alpha)
                self.screen.blit(temp_surface, (screen_x, screen_y))
    
    def draw_ui(self):
        """Dibuja interfaz de usuario mejorada"""
        font = pygame.font.Font(None, 72)
        font_small = pygame.font.Font(None, 48)
        font_large = pygame.font.Font(None, 96)  # Para contador de enemigos
        
        # Personaje activo con icono
        active_text = font.render(f"🎮 {self.active_character.name}", True, (255, 255, 255))
        self.screen.blit(active_text, (20, 20))
        
        # Vidas con barras gráficas
        juan_health_text = font_small.render(f"Juan: {self.juan.health}/{self.juan.max_health}", 
                                       True, (255, 255, 255) if self.juan.health > 0 else (255, 100, 100))
        self.screen.blit(juan_health_text, (20, 90))
        
        adan_health_text = font_small.render(f"Adán: {self.adan.health}/{self.adan.max_health}", 
                                       True, (255, 255, 255) if self.adan.health > 0 else (255, 100, 100))
        self.screen.blit(adan_health_text, (300, 90))
        
        # CONTADOR DE ENEMIGOS PROMINENTE
        # Fondo para el contador
        counter_bg = pygame.Surface((400, 80), pygame.SRCALPHA)
        counter_bg.fill((0, 0, 0, 180))
        self.screen.blit(counter_bg, (self.screen_width - 420, 20))
        
        # Texto del contador con colores dinámicos
        progress_color = (255, 255, 255)
        if self.enemies_defeated >= self.victory_condition:
            progress_color = (100, 255, 100)  # Verde cuando se completa
        elif self.enemies_defeated >= self.victory_condition * 0.75:
            progress_color = (255, 255, 100)  # Amarillo cuando está cerca
        
        progress_text = font_large.render(f"🐛 {self.enemies_defeated}/{self.victory_condition}", 
                                        True, progress_color)
        self.screen.blit(progress_text, (self.screen_width - 400, 30))
        
        # Texto descriptivo
        desc_text = font_small.render("Gusanos Derrotados", True, (200, 200, 200))
        self.screen.blit(desc_text, (self.screen_width - 380, 70))
        
        # Mejoras
        upgrades_text = [
            f"🚀 Velocidad: +{self.upgrades['speed']}",
            f"⚔️ Daño: +{self.upgrades['damage']}",
            f"⚡ Vel.Ataque: +{self.upgrades['attack_speed']}",
            f"❤️ Vida: +{self.upgrades['health']}"
        ]
        
        for i, upgrade in enumerate(upgrades_text):
            upgrade_surface = font_small.render(upgrade, True, (200, 255, 200))
            self.screen.blit(upgrade_surface, (20, 190 + i * 35))
        
        # Indicador de modo editor
        if self.collision_manager.editor_mode:
            editor_text = font_small.render("🛠️ MODO EDITOR ACTIVO (F1 para salir)", True, (255, 255, 0))
            self.screen.blit(editor_text, (20, 330))
        else:
            editor_text = font_small.render("F1 - Activar Modo Editor", True, (200, 200, 200))
            self.screen.blit(editor_text, (20, 330))
        
        # Indicador de escudo
        for i, char in enumerate([self.juan, self.adan]):
            if getattr(char, 'shield_active', False):
                shield_text = font_small.render(f"🛡️ {char.name}", True, (100, 200, 255))
                self.screen.blit(shield_text, (600 + i * 200, 90))
    
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
        
        # Opciones
        options = [
            "1 - 🚀 Velocidad (+0.5)",
            "2 - ⚔️ Daño (+5)",
            "3 - ⚡ Velocidad Ataque (-30ms)",
            "4 - ❤️ Vida Máxima (+15)"
        ]
        
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
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        font_large = pygame.font.Font(None, 144)
        font_small = pygame.font.Font(None, 72)
        
        # Título
        game_over_text = font_large.render("💀 GAME OVER", True, (255, 50, 50))
        game_over_rect = game_over_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 100))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Instrucción
        restart_text = font_small.render("Presiona R para reiniciar", True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(self.screen_width//2, self.screen_height//2 + 50))
        self.screen.blit(restart_text, restart_rect)
        
        # Estadísticas
        stats_text = font_small.render(f"Gusanos derrotados: {self.enemies_defeated}", True, (200, 200, 200))
        stats_rect = stats_text.get_rect(center=(self.screen_width//2, self.screen_height//2 + 120))
        self.screen.blit(stats_text, stats_rect)
    
    def draw_victory(self):
        """Dibuja pantalla de victoria"""
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        font_large = pygame.font.Font(None, 144)
        font_medium = pygame.font.Font(None, 96)
        font_small = pygame.font.Font(None, 72)
        
        # Título
        victory_text = font_large.render("🎉 ¡NIVEL 1 COMPLETADO!", True, (255, 215, 0))
        victory_rect = victory_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 150))
        self.screen.blit(victory_text, victory_rect)
        
        # Mensaje principal
        message_text = font_medium.render("¡Has liberado la Tierra de las Manzanas!", True, (255, 255, 255))
        message_rect = message_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 50))
        self.screen.blit(message_text, message_rect)
        
        # Estadísticas
        stats_text = font_small.render(f"Gusanos derrotados: {self.enemies_defeated}", True, (200, 255, 200))
        stats_rect = stats_text.get_rect(center=(self.screen_width//2, self.screen_height//2 + 20))
        self.screen.blit(stats_text, stats_rect)
        
        # Botón para Nivel 2 (destacado)
        nivel2_text = font_medium.render("⬆️ Presiona N para ir al NIVEL 2", True, (255, 100, 100))
        nivel2_rect = nivel2_text.get_rect(center=(self.screen_width//2, self.screen_height//2 + 80))
        
        # Fondo para el botón de Nivel 2
        button_bg = pygame.Rect(nivel2_rect.x - 20, nivel2_rect.y - 10, 
                               nivel2_rect.width + 40, nivel2_rect.height + 20)
        pygame.draw.rect(self.screen, (50, 0, 50), button_bg)
        pygame.draw.rect(self.screen, (255, 100, 100), button_bg, 3)
        
        self.screen.blit(nivel2_text, nivel2_rect)
        
        # Opción de reinicio
        restart_text = font_small.render("R - Reiniciar Nivel 1", True, (200, 200, 200))
        restart_rect = restart_text.get_rect(center=(self.screen_width//2, self.screen_height//2 + 150))
        self.screen.blit(restart_text, restart_rect)
    
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