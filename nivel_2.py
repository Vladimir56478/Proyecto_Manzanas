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
        
        # Loading screen
        self.loading_screen = LoadingScreen(self.screen)
        assets_to_load = [
            {"name": "Escenario", "description": "Bosque del Chamán Malvado"},
            {"name": "Personajes", "description": "Juan y Adán (escalados)"},
            {"name": "Chamán Malvado", "description": "Jefe final del nivel"},
            {"name": "Sistema de combate", "description": "Ataques y proyectiles mágicos"},
            {"name": "IA Mejorada", "description": "Comportamiento inteligente"},
            {"name": "Sistema de Coleccionables", "description": "Manzanas y pociones"}
        ]
        self.loading_screen.start_loading(assets_to_load)
        
        # Mostrar mensaje inicial
        self.loading_screen.set_custom_message("Preparando el enfrentamiento final...")
        self.loading_screen.draw()
        
        # Cargar escenario del nivel 2 (placeholder hasta recibir URL)
        self.loading_screen.update_progress("Escenario", "Cargando bosque maldito...")
        self.loading_screen.draw()
        self.background_color = (15, 25, 15)  # Verde muy oscuro para ambiente siniestro
        self.background_image = None
        
        # Cargar personajes con escalado aumentado
        self.loading_screen.update_progress("Personajes", "Invocando a los héroes...")
        self.loading_screen.draw()
        
        # Juan con tamaño aumentado
        self.juan = JuanCharacter(300, 400)
        self.juan.max_health = 120  # Más vida para el nivel 2
        self.juan.health = 120
        self.juan.speed = 4.5
        # Escalar sprites de Juan 25% más grande
        self.scale_character_sprites(self.juan, 1.25)
        
        # Adán con tamaño aumentado
        self.adan = AdanCharacter(400, 400)
        self.adan.max_health = 120
        self.adan.health = 120
        self.adan.speed = 4.5
        # Escalar sprites de Adán 25% más grande
        self.scale_character_sprites(self.adan, 1.25)
        
        # Cargar sistemas de ataque mejorados
        self.loading_screen.update_progress("Sistema de combate", "Mejorando habilidades de combate...")
        self.loading_screen.draw()
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
        self.loading_screen.update_progress("IA Mejorada", "Configurando comportamiento inteligente...")
        self.loading_screen.draw()
        self.inactive_ai = CharacterAI(self.inactive_character, self.active_character)
        # Mejorar la IA para ser más agresiva
        self.inactive_ai.detection_range = 400
        self.inactive_ai.attack_range = 150
        
        # Cargar Chamán Malvado - El jefe final
        self.loading_screen.update_progress("Chamán Malvado", "Despertando al enemigo final...")
        self.loading_screen.draw()
        self.chaman = ChamanMalvado(self.screen_width//2, self.screen_height//4)
        
        # Sistema de audio
        self.audio = get_audio_manager()
        
        # Cámara mejorada
        self.camera_x = 0
        self.camera_y = 0
        self.camera_smooth_factor = 0.08  # Más suave para combate con jefe
        
        # Estados del juego
        self.game_over = False
        self.victory = False
        self.switch_cooldown = 0
        self.revival_key_pressed = False
        self.show_revival_prompt = False
        self.revival_distance = 100
        
        # Sistema de coleccionables mejorado
        self.loading_screen.update_progress("Sistema de Coleccionables", "Preparando recompensas...")
        self.loading_screen.draw()
        self.item_manager = ItemManager()  # Nuevo sistema de items
        
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
        
        # Finalizar carga
        self.loading_screen.update_progress("Completado", "¡Iniciando batalla contra el Chamán!")
        self.loading_screen.draw()
        pygame.time.wait(1500)  # Pausa dramática
        
        print(f"🎮 Nivel 2 iniciado - Personaje activo: {self.active_character.name}")
        print(f"🤖 IA controlando: {self.inactive_character.name}")
        print(f"👹 Chamán Malvado despertado con {self.chaman.health} HP")
    
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
    
    def load_collectible_images(self):
        """Carga imágenes para manzanas y pociones"""
        try:
            # URLs de coleccionables
            apple_url = "https://github.com/user-attachments/assets/8d98de91-3834-456d-8dac-484029df9a02"
            potion_url = "https://github.com/user-attachments/assets/5365c2ea-ad1e-4055-8d3b-de1547e10396"
            
            # Cargar manzana
            print("📥 Descargando imagen de manzana...")
            response = requests.get(apple_url, timeout=10)
            response.raise_for_status()
            apple_data = BytesIO(response.content)
            apple_pil = Image.open(apple_data).convert("RGBA")
            apple_data = apple_pil.tobytes()
            self.apple_image = pygame.image.fromstring(apple_data, apple_pil.size, "RGBA")
            self.apple_image = pygame.transform.scale(self.apple_image, (40, 40))  # Tamaño visible
            
            # Cargar poción
            print("📥 Descargando imagen de poción...")
            response = requests.get(potion_url, timeout=10)
            response.raise_for_status()
            potion_data = BytesIO(response.content)
            potion_pil = Image.open(potion_data).convert("RGBA")
            potion_data = potion_pil.tobytes()
            self.potion_image = pygame.image.fromstring(potion_data, potion_pil.size, "RGBA")
            self.potion_image = pygame.transform.scale(self.potion_image, (40, 40))  # Tamaño visible
            
            print("✅ Imágenes de coleccionables cargadas exitosamente")
        except Exception as e:
            print(f"❌ Error cargando imágenes de coleccionables: {e}")
            # Crear placeholders coloridos
            self.apple_image = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(self.apple_image, (255, 0, 0), (20, 20), 18)
            pygame.draw.circle(self.apple_image, (255, 100, 100), (20, 20), 12)
            
            self.potion_image = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(self.potion_image, (0, 0, 255), (20, 20), 18)
            pygame.draw.circle(self.potion_image, (100, 100, 255), (20, 20), 12)
    
    def handle_events(self):
        """Maneja eventos del juego"""
        keys_pressed = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Alternar pantalla completa
                    if self.screen.get_flags() & pygame.FULLSCREEN:
                        self.screen = pygame.display.set_mode((1000, 700))
                        self.screen_width = 1000
                        self.screen_height = 700
                    else:
                        self.screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
                        self.screen_width = 1920
                        self.screen_height = 1080
                elif event.key == pygame.K_TAB and not self.game_over and not self.victory:
                    if self.switch_cooldown <= 0 and self.juan.health > 0 and self.adan.health > 0:
                        self.switch_character()
                        self.switch_cooldown = 30
                elif event.key == pygame.K_r and (self.game_over or self.victory):
                    self.restart_game()
                elif event.key == pygame.K_SPACE and not self.game_over and not self.victory:
                    # Ataque básico
                    self.perform_basic_attack()
                elif event.key == pygame.K_x and not self.game_over and not self.victory:
                    # Ataque especial - proyectil mágico para el chamán
                    if isinstance(self.active_character, ChamanMalvado):
                        self.active_character.shoot_magic_projectile()
                    else:
                        self.perform_special_attack()
                # Manejo del menú de mejoras
                elif self.show_upgrade_menu:
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                        self.handle_upgrade_selection(event.key)
                        self.show_upgrade_menu = False
        
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
        if self.game_over or self.victory:
            if self.switch_cooldown > 0:
                self.switch_cooldown -= 1
            return
        
        keys_pressed = pygame.key.get_pressed()
        
        # Actualizar personaje activo
        if not self.active_attack_system.is_character_attacking():
            self.active_character.update(keys_pressed)
            # Aplicar límites del mundo
            self.enforce_boundaries(self.active_character)
        
        # Actualizar IA del personaje inactivo enfocada en el Chamán
        if self.inactive_character.health > 0 or self.inactive_ai.is_being_revived:
            # La IA se enfoca en el chamán como objetivo principal
            self.inactive_ai.update([self.chaman])
            
            ai_animation_state = self.inactive_ai.get_animation_state()
            self.inactive_character.update(keys_pressed=None, ai_controlled=True, ai_direction=ai_animation_state)
            self.enforce_boundaries(self.inactive_character)
        
        # Actualizar sistema de escudo
        self.update_shield_system()
        
        # Manejar ataques del personaje activo
        self.active_attack_system.handle_attack_input(keys_pressed, [self.chaman])
        
        # Actualizar chamán (IA vs personaje activo)
        players = [self.active_character, self.inactive_character]
        self.chaman.update(players)
        
        # Comprobar impactos de proyectiles del chamán en ambos personajes
        self.chaman.check_projectile_collisions(players)
        
        # Actualizar cámara para seguir la batalla
        target_camera_x = self.active_character.x - self.screen_width // 2
        target_camera_y = self.active_character.y - self.screen_height // 2
        
        # Suavizar movimiento de cámara
        self.camera_x += (target_camera_x - self.camera_x) * self.camera_smooth_factor
        self.camera_y += (target_camera_y - self.camera_y) * self.camera_smooth_factor
        
        # Limitar cámara a los bordes del mundo
        self.limit_camera()
        
        # Actualizar sistemas de ataque
        self.juan_attack.update([self.chaman])
        self.adan_attack.update([self.chaman])
        
        # Actualizar sistema de items (reemplaza update_collectibles)
        self.item_manager.update([self.active_character, self.inactive_character])
        
        # Manejar entrada del menú de mejoras
        keys = pygame.key.get_pressed()
        self.item_manager.handle_upgrade_input(keys, self.active_character)
        
        # Procesar drops de gusanos muertos
        self.process_worm_drops()
        
        # Verificar condición de victoria/derrota
        if self.chaman.health <= 0:
            self.victory = True
            print("🎉 ¡VICTORIA ÉPICA! Has derrotado al Chamán Malvado")
        
        if self.active_character.health <= 0:
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
        """Procesa drops de gusanos invocados por el chamán"""
        if not hasattr(self.chaman, 'summoned_worms'):
            return
            
        for worm in self.chaman.summoned_worms[:]:
            if not worm.alive and hasattr(worm, 'pending_drops') and worm.pending_drops:
                # Agregar drops del gusano al sistema de items
                drops = worm.get_and_clear_drops()
                for drop in drops:
                    self.item_manager.add_item(drop['type'], drop['x'], drop['y'])
                    print(f"🎁 Drop generado: {drop['type']} en ({drop['x']}, {drop['y']})")
    
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
        
        # Dibujar sistema de items (reemplaza draw_collectibles)
        self.item_manager.draw(self.screen, self.camera_x, self.camera_y)
        
        # Dibujar barras de vida
        self.draw_health_bars()
        
        # Dibujar efectos de ataque
        self.juan_attack.draw(self.screen, self.camera_x, self.camera_y)
        self.adan_attack.draw(self.screen, self.camera_x, self.camera_y)
        
        # Dibujar interfaz de usuario
        self.draw_ui()
        
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
        """Dibuja manzanas y pociones en el suelo"""
        for item in self.dropped_items:
            if not item['collected']:
                # Efecto de brillo
                glow_surface = pygame.Surface((60, 60), pygame.SRCALPHA)
                glow_alpha = int(100 + 50 * math.sin(pygame.time.get_ticks() * 0.005))
                
                if item['type'] == 'apple':
                    pygame.draw.circle(glow_surface, (255, 0, 0, glow_alpha), (30, 30), 25)
                else:  # potion
                    pygame.draw.circle(glow_surface, (0, 0, 255, glow_alpha), (30, 30), 25)
                
                self.screen.blit(glow_surface, 
                               (item['x'] - self.camera_x - 10, item['y'] - self.camera_y - 10))
                
                # Imagen del item
                if item['image']:
                    self.screen.blit(item['image'], 
                                   (item['x'] - self.camera_x, item['y'] - self.camera_y))
    
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
        
        # Opciones
        options = [
            "1 - 🚀 Velocidad (+0.7)",
            "2 - ⚔️ Daño (+8/+5)",
            "3 - ⚡ Vel. Ataque (-50ms)",
            "4 - ❤️ Vida Máxima (+25)"
        ]
        
        for i, option in enumerate(options):
            option_text = font_option.render(option, True, (255, 255, 255))
            option_rect = option_text.get_rect(center=(menu_width//2, 120 + i * 60))
            menu_surface.blit(option_text, option_rect)
        
        # Instrucciones
        instruction_text = font_option.render("Presiona el número de la mejora que deseas", True, (200, 200, 200))
        instruction_rect = instruction_text.get_rect(center=(menu_width//2, 350))
        menu_surface.blit(instruction_text, instruction_rect)
        
        self.screen.blit(menu_surface, (menu_x, menu_y))
    
    def draw_ui(self):
        """Dibuja la interfaz de usuario"""
        font_large = pygame.font.Font(None, 84)
        font_medium = pygame.font.Font(None, 56)
        font_small = pygame.font.Font(None, 42)
        
        # Personaje activo
        active_text = font_large.render(f"🎮 {self.active_character.name}", True, (255, 255, 255))
        self.screen.blit(active_text, (30, 30))
        
        # Estado del personaje inactivo
        if self.inactive_character.health > 0:
            inactive_status = "🤖 Luchando"
            inactive_color = (150, 255, 150)
        else:
            inactive_status = "💀 Derribado"
            inactive_color = (255, 100, 100)
        
        inactive_text = font_medium.render(f"{self.inactive_character.name}: {inactive_status}", True, inactive_color)
        self.screen.blit(inactive_text, (30, 100))
        
        # Información del chamán
        chaman_health_percent = int((self.chaman.health / self.chaman.max_health) * 100)
        if chaman_health_percent > 50:
            chaman_color = (255, 100, 255)
        elif chaman_health_percent > 20:
            chaman_color = (255, 150, 0)
        else:
            chaman_color = (255, 0, 0)
        
        chaman_text = font_large.render(f"👹 Chamán: {chaman_health_percent}%", True, chaman_color)
        chaman_rect = chaman_text.get_rect(topright=(self.screen_width - 30, 30))
        self.screen.blit(chaman_text, chaman_rect)
        
        # Mejoras actuales
        upgrades_text = [
            f"🚀 Velocidad: +{self.upgrades['speed']}",
            f"⚔️ Daño: +{self.upgrades['damage']}",
            f"⚡ Vel.Ataque: +{self.upgrades['attack_speed']}",
            f"❤️ Vida: +{self.upgrades['health']}"
        ]
        
        for i, upgrade_text in enumerate(upgrades_text):
            upgrade_surface = font_small.render(upgrade_text, True, (200, 255, 200))
            self.screen.blit(upgrade_surface, (30, 160 + i * 35))
        
        # Controles
        controls = [
            "🎮 CONTROLES NIVEL 2:",
            "WASD/Flechas - Mover",
            "ESPACIO - Ataque básico",
            "X - Ataque especial/Proyectil",
            "TAB - Cambiar personaje",
            "E - Revivir/Consumir poción",
            "ESC - Pantalla completa"
        ]
        
        for i, control in enumerate(controls):
            control_surface = font_small.render(control, True, (255, 255, 255))
            self.screen.blit(control_surface, (30, self.screen_height - 320 + i * 40))
        
        # Estado de escudo
        if hasattr(self.active_character, 'shield_active') and self.active_character.shield_active:
            shield_time_left = (self.active_character.shield_duration - self.active_character.shield_timer) // 60
            shield_text = font_medium.render(f"🛡️ Escudo: {shield_time_left}s", True, (100, 150, 255))
            shield_rect = shield_text.get_rect(topright=(self.screen_width - 30, 120))
            self.screen.blit(shield_text, shield_rect)
    
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