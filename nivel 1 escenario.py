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


class Background:
    """Maneja el fondo del juego con scroll y carga desde GitHub"""
    
    def __init__(self, image_url, width=None, height=None):
        self.image_url = image_url
        self.width = width or 1980
        self.height = height or 1080
        self.surface = None
        self.load_background(image_url)
        
    def load_background(self, url):
        """Carga el fondo desde GitHub"""
        try:
            print("📥 Descargando escenario desde GitHub...")
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            image_data = BytesIO(response.content)
            pil_image = Image.open(image_data)
            
            # Información de la imagen original
            original_width, original_height = pil_image.size
            print(f"📐 Dimensiones originales de tu PNG: {original_width}x{original_height}")
            
            # Usar dimensiones originales
            self.width = original_width
            self.height = original_height
            print(f"✅ Usando dimensiones originales: {self.width}x{self.height}")
            
            # Convertir a formato pygame
            pil_image = pil_image.convert('RGB')
            image_data = pil_image.tobytes()
            
            self.surface = pygame.image.fromstring(image_data, pil_image.size, 'RGB')
            self.surface = self.surface.convert()
            
            print(f"✅ Escenario cargado exitosamente: {self.width}x{self.height}")
            
        except Exception as e:
            print(f"❌ Error cargando escenario: {e}")
            self.create_fallback_background()
    
    def create_fallback_background(self):
        """Crea un fondo de respaldo si falla GitHub"""
        print("🎨 Creando fondo de respaldo...")
        self.surface = pygame.Surface((self.width, self.height))
        
        # Gradiente verde para simular césped
        for y in range(self.height):
            green_intensity = 50 + (y * 100) // self.height
            color = (20, min(green_intensity, 150), 20)
            pygame.draw.line(self.surface, color, (0, y), (self.width, y))
        
        # Añadir algunos elementos decorativos
        for _ in range(50):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(10, 30)
            color = (30, random.randint(80, 120), 30)
            pygame.draw.circle(self.surface, color, (x, y), size)
    
    def draw(self, screen, camera_x, camera_y, screen_width, screen_height):
        """Dibuja el fondo con soporte para scroll de cámara"""
        if not self.surface:
            return
            
        # Calcular la región visible
        visible_rect = pygame.Rect(camera_x, camera_y, screen_width, screen_height)
        
        # Limitar camera a los bounds del mundo
        camera_x = max(0, min(camera_x, self.width - screen_width))
        camera_y = max(0, min(camera_y, self.height - screen_height))
        
        # Dibujar la porción visible
        source_rect = pygame.Rect(camera_x, camera_y, screen_width, screen_height)
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
        
        escenario_url = "https://github.com/user-attachments/assets/03339362-2bb5-4bf7-b4f5-b3ea4babbb92"
        self.background = Background(escenario_url)
        self.world_width = self.background.width
        self.world_height = self.background.height
        
        # === CARGA DE PERSONAJES ===
        self.loading_screen.update_progress("Personajes", "Cargando Juan...")
        self.loading_screen.draw()
        
        self.juan = JuanCharacter(400, 300)
        self.juan.max_health = 100
        self.juan.health = 100
        self.juan.speed = 4
        self.juan.name = "Juan"
        
        self.loading_screen.update_progress("Personajes", "Cargando Adán...")
        self.loading_screen.draw()
        
        self.adan = AdanCharacter(500, 300)
        self.adan.max_health = 100
        self.adan.health = 100
        self.adan.speed = 4
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
        """Crea sprites para manzanas y pociones"""
        # Manzana
        self.apple_image = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(self.apple_image, (220, 50, 50), (16, 18), 12)
        pygame.draw.circle(self.apple_image, (255, 100, 100), (12, 14), 8)
        pygame.draw.rect(self.apple_image, (139, 69, 19), (14, 4, 4, 8))
        pygame.draw.ellipse(self.apple_image, (34, 139, 34), (10, 2, 8, 6))
        
        # Poción
        self.potion_image = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.rect(self.potion_image, (100, 100, 100), (12, 14, 8, 14))
        pygame.draw.ellipse(self.potion_image, (20, 100, 220), (10, 18, 12, 10))
        pygame.draw.rect(self.potion_image, (50, 150, 255), (14, 10, 4, 12))
        pygame.draw.circle(self.potion_image, (100, 200, 255), (16, 22), 4)
    
    # === MANEJO DE EVENTOS ===
    
    def handle_events(self):
        """Maneja todos los eventos del juego"""
        keys_pressed = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_r and (self.game_over or self.victory):
                    self.restart_game()
                elif event.key == pygame.K_TAB:
                    self.switch_character()
                elif event.key == pygame.K_x:
                    self.perform_special_attack()
                elif self.show_upgrade_menu and event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                    self.handle_upgrade_selection(event.key)
                    self.show_upgrade_menu = False
        
        # Manejo de revivir con E
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
        
        # Manejo de ataques básicos con ESPACIO
        if keys_pressed[pygame.K_SPACE]:
            self.perform_basic_attack()
        
        return True
    
    def switch_character(self):
        """Cambia entre Juan y Adán"""
        if self.switch_cooldown <= 0 and not self.game_over and not self.victory:
            self.active_character, self.inactive_character = self.inactive_character, self.active_character
            self.active_attack_system, self.inactive_attack_system = self.inactive_attack_system, self.active_attack_system
            self.switch_cooldown = 30
            print(f"🔄 Cambiado a {self.active_character.name}")
    
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
            if hit:
                for enemy in worms:
                    if hasattr(enemy, 'health') and enemy.health <= 0:
                        self.enemies_defeated += 1
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
        
        # Actualizar personaje activo
        if not self.active_attack_system.is_character_attacking():
            self.active_character.update(keys_pressed)
            self.enforce_boundaries(self.active_character)
        
        # Actualizar IA del personaje inactivo
        if self.inactive_character.health > 0 or self.inactive_ai.is_being_revived:
            worms = self.worm_spawner.get_worms()
            self.inactive_ai.detection_range = 300
            self.inactive_ai.update(worms)
            self.enforce_boundaries(self.inactive_character)
        
        # Actualizar sistemas de ataque
        worms = self.worm_spawner.get_worms()
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
        """Procesa drops de gusanos muertos"""
        for worm in self.worm_spawner.get_worms():
            if (hasattr(worm, 'health') and worm.health <= 0 and 
                not getattr(worm, 'drop_processed', False)):
                
                worm.drop_processed = True
                self.enemies_defeated += 1
                
                # 60% probabilidad de drop
                if random.random() < 0.6:
                    drop_x = worm.x + random.randint(-30, 30)
                    drop_y = worm.y + random.randint(-30, 30)
                    
                    if random.random() < 0.6:  # 60% manzana, 40% poción
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
        """Actualiza la posición de la cámara"""
        target_x = self.active_character.x - self.screen_width // 2
        target_y = self.active_character.y - self.screen_height // 2
        
        # Suavizar movimiento de cámara
        self.camera_x += (target_x - self.camera_x) * 0.1
        self.camera_y += (target_y - self.camera_y) * 0.1
        
        # Limitar cámara a bounds del mundo
        self.camera_x = max(0, min(self.camera_x, self.world_width - self.screen_width))
        self.camera_y = max(0, min(self.camera_y, self.world_height - self.screen_height))
    
    def check_game_conditions(self):
        """Verifica condiciones de victoria y derrota"""
        # Victoria: 15 gusanos derrotados
        if self.enemies_defeated >= self.victory_condition:
            self.victory = True
            print("🎉 ¡VICTORIA! Has derrotado a todos los gusanos")
        
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
        """Aplica límites del mapa"""
        margin = 50
        character.x = max(margin, min(self.world_width - margin - 64, character.x))
        character.y = max(margin, min(self.world_height - margin - 64, character.y))
    
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
    
    # === RENDERIZADO ===
    
    def draw(self):
        """Dibuja todo el juego"""
        # Limpiar pantalla
        self.screen.fill((50, 100, 50))
        
        # Dibujar fondo
        self.background.draw(self.screen, self.camera_x, self.camera_y, 
                           self.screen_width, self.screen_height)
        
        # Dibujar personajes
        if self.inactive_character.health > 0:
            if not self.inactive_attack_system.is_character_attacking():
                self.inactive_character.draw(self.screen, self.camera_x, self.camera_y)
        
        if not self.active_attack_system.is_character_attacking():
            self.active_character.draw(self.screen, self.camera_x, self.camera_y)
        
        # Dibujar efectos de ataque
        self.juan_attack.draw(self.screen, self.camera_x, self.camera_y)
        self.adan_attack.draw(self.screen, self.camera_x, self.camera_y)
        
        # Dibujar enemigos
        self.worm_spawner.draw(self.screen, self.camera_x, self.camera_y)
        
        # Dibujar coleccionables
        self.draw_collectibles()
        
        # Dibujar UI
        self.draw_ui()
        
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
        """Dibuja interfaz de usuario"""
        font = pygame.font.Font(None, 72)
        font_small = pygame.font.Font(None, 48)
        
        # Personaje activo
        active_text = font.render(f"🎮 {self.active_character.name}", True, (255, 255, 255))
        self.screen.blit(active_text, (20, 20))
        
        # Vidas
        juan_health = font_small.render(f"Juan: {self.juan.health}/{self.juan.max_health}", 
                                       True, (255, 255, 255) if self.juan.health > 0 else (255, 100, 100))
        self.screen.blit(juan_health, (20, 90))
        
        adan_health = font_small.render(f"Adán: {self.adan.health}/{self.adan.max_health}", 
                                       True, (255, 255, 255) if self.adan.health > 0 else (255, 100, 100))
        self.screen.blit(adan_health, (300, 90))
        
        # Progreso
        progress_text = font_small.render(f"Gusanos: {self.enemies_defeated}/{self.victory_condition}", 
                                        True, (255, 255, 255))
        self.screen.blit(progress_text, (20, 140))
        
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
        
        progress = self.inactive_ai.revival_progress / self.inactive_ai.revival_duration
        
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
        font_small = pygame.font.Font(None, 72)
        
        # Título
        victory_text = font_large.render("🎉 ¡VICTORIA!", True, (255, 215, 0))
        victory_rect = victory_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 100))
        self.screen.blit(victory_text, victory_rect)
        
        # Mensaje
        message_text = font_small.render("¡Has liberado la Tierra de las Manzanas!", True, (255, 255, 255))
        message_rect = message_text.get_rect(center=(self.screen_width//2, self.screen_height//2))
        self.screen.blit(message_text, message_rect)
        
        # Instrucción
        restart_text = font_small.render("Presiona R para jugar de nuevo", True, (200, 200, 200))
        restart_rect = restart_text.get_rect(center=(self.screen_width//2, self.screen_height//2 + 100))
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