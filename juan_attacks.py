import pygame
import math
from PIL import Image
import requests
from io import BytesIO

class JuanAttack:
    def __init__(self, character):
        self.character = character
        self.combo_hits = []
        self.special_effects = []
        self.last_attack_time = 0
        self.attack_cooldown = 300
        self.combo_count = 0
        self.max_combo = 3
        
        # Variables para animaciones de ataque
        self.is_attacking = False
        self.attack_animation_frame = 0
        self.attack_animation_speed = 0.3
        self.attack_direction = "down"
        self.attack_damage_pending = None  # Almacena el daño pendiente hasta el final de la animación
        self.attack_enemies_target = []    # Lista de enemigos que serán afectados al final
        
        # URLs de los GIFs de ataque de Juan desde GitHub Issues (INVERTIDAS)
        self.attack_gif_urls = {
            "up": "https://github.com/user-attachments/assets/bcd29b68-808b-4840-a6bb-1691c94581b1",    # Era "down"
            "down": "https://github.com/user-attachments/assets/dd75fe07-fdbc-44af-b96c-e02d24f1a541",  # Era "up"
            "left": "https://github.com/user-attachments/assets/dd1ed297-05f1-468b-83fb-266d510595f3",  # Era "right"
            "right": "https://github.com/user-attachments/assets/e1db84b2-d37d-4bc4-87f8-cce531c51300"  # Era "left"
        }
        
        # Diccionario para almacenar los frames de cada dirección de ataque
        self.attack_animations = {}
        self.load_attack_animations()
        
    def load_attack_animations(self):
        """Carga todos los GIFs de ataque y extrae sus frames"""
        print("⚔️ Cargando animaciones de ataque de Juan desde GitHub...")
        
        for direction, url in self.attack_gif_urls.items():
            try:
                print(f"📥 Descargando ataque {direction} desde GitHub...")
                
                # Descargar el GIF desde GitHub
                response = requests.get(url, timeout=10)  # Timeout de 10 segundos
                response.raise_for_status()
                gif_data = BytesIO(response.content)
                
                # Abrir el GIF con PIL
                gif = Image.open(gif_data)
                frames = []
                
                # Extraer todos los frames del GIF
                for frame_num in range(gif.n_frames):
                    gif.seek(frame_num)
                    frame = gif.copy().convert("RGBA")
                    
                    # Procesar cada pixel para eliminar fondos blancos/grises
                    pixels = frame.load()
                    for y in range(frame.height):
                        for x in range(frame.width):
                            r, g, b, a = pixels[x, y]
                            # Eliminar fondos blancos, grises claros y similares
                            if r > 200 and g > 200 and b > 200:
                                pixels[x, y] = (r, g, b, 0)  # Hacer transparente
                            elif abs(r - g) < 30 and abs(r - b) < 30 and abs(g - b) < 30 and r > 180:
                                pixels[x, y] = (r, g, b, 0)  # Eliminar grises claros
                    
                    # Convertir PIL image a superficie de Pygame
                    frame_data = frame.tobytes()
                    pygame_surface = pygame.image.fromstring(frame_data, frame.size, "RGBA")
                    
                    # Aplicar transparencia adicional y suavizado
                    pygame_surface = pygame_surface.convert_alpha()
                    pygame_surface.set_colorkey((255, 255, 255))
                    
                    frames.append(pygame_surface)
                
                self.attack_animations[direction] = frames
                print(f"✅ Cargada animación de ataque '{direction}': {len(frames)} frames")
                
            except Exception as e:
                print(f"❌ Error cargando ataque {direction}: {e}")
                # Crear frame de respaldo en caso de error
                backup_surface = pygame.Surface((64, 64), pygame.SRCALPHA)
                backup_surface.fill((0, 255, 0, 128))  # Verde semitransparente
                self.attack_animations[direction] = [backup_surface]
    
    def start_attack_animation(self, direction):
        """Inicia la animación de ataque en la dirección especificada"""
        self.is_attacking = True
        self.attack_direction = direction
        self.attack_animation_frame = 0
        print(f"🎬 Juan iniciando animación de ataque hacia {direction}")
        
        # Verificar que la animación existe
        if direction in self.attack_animations:
            frames_count = len(self.attack_animations[direction])
            print(f"✅ Animación encontrada: {frames_count} frames para dirección {direction}")
        else:
            print(f"❌ No se encontró animación para dirección {direction}")
            print(f"🔍 Direcciones disponibles: {list(self.attack_animations.keys())}")
        
    def update_attack_animation(self):
        """Actualiza la animación de ataque - Siguiendo estructura de movimientos"""
        if self.is_attacking:
            self.attack_animation_frame += self.attack_animation_speed
            
            # Verificar que la dirección existe en las animaciones
            if self.attack_direction in self.attack_animations:
                # Si terminó la animación, aplicar daño y resetear
                if self.attack_animation_frame >= len(self.attack_animations[self.attack_direction]):
                    # Aplicar daño al final de la animación
                    if self.attack_damage_pending is not None:
                        self.apply_pending_damage()
                    
                    self.attack_animation_frame = 0
                    # Terminar ataque después de una animación completa
                    self.is_attacking = False
                    self.attack_damage_pending = None
                    self.attack_enemies_target = []
            else:
                # Si no existe la dirección, terminar ataque
                self.is_attacking = False
                self.attack_animation_frame = 0
                self.attack_damage_pending = None
                self.attack_enemies_target = []
    
    def handle_attack_input(self, keys_pressed, enemies):
        """Maneja la entrada de ataque (tecla ESPACIO)"""
        if keys_pressed[pygame.K_SPACE] and not self.is_attacking:
            # Determinar dirección de ataque basada en las teclas actuales presionadas
            # Seguir exactamente la misma lógica que los movimientos
            direction = "down"  # Dirección por defecto
            
            # Detectar dirección actual basada en teclas presionadas (INVERTIDO para control manual)
            if keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w]:
                direction = "down"  # INVERTIDO: era "up"
            elif keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_s]:
                direction = "up"    # INVERTIDO: era "down"
            elif keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]:
                direction = "right" # INVERTIDO: era "left"
            elif keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]:
                direction = "left"  # INVERTIDO: era "right"
            else:
                # Si no hay teclas presionadas, usar dirección actual del personaje
                direction = getattr(self.character, 'current_direction', 'down')
            
            print(f"🎯 Juan atacando hacia: {direction}")
            
            # Iniciar animación de ataque
            self.start_attack_animation(direction)
            
            # Preparar ataque combo (daño se aplicará al final de la animación)
            return self.prepare_combo_attack(enemies)
        
        return False
        
    def prepare_combo_attack(self, enemies):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time < self.attack_cooldown:
            return False
        
        self.last_attack_time = current_time
        self.combo_count = (self.combo_count + 1) % self.max_combo
        
        base_damage = 15 + (self.combo_count * 5)
        range_multiplier = 1 + (self.combo_count * 0.5)
        
        # Crear área de ataque direccional CORREGIDA para IA
        attack_range = int(70 * range_multiplier)
        if self.attack_direction == "up":
            # Cuando IA dice "up", debe atacar hacia ARRIBA (enemigo está arriba)
            attack_rect = pygame.Rect(self.character.x - 20, self.character.y - attack_range, 104, attack_range + 32)
        elif self.attack_direction == "down":
            # Cuando IA dice "down", debe atacar hacia ABAJO (enemigo está abajo)
            attack_rect = pygame.Rect(self.character.x - 20, self.character.y + 32, 104, attack_range)
        elif self.attack_direction == "left":
            # Cuando IA dice "left", debe atacar hacia IZQUIERDA (enemigo está a la izquierda)
            attack_rect = pygame.Rect(self.character.x - attack_range, self.character.y - 20, attack_range + 32, 104)
        elif self.attack_direction == "right":
            # Cuando IA dice "right", debe atacar hacia DERECHA (enemigo está a la derecha)
            attack_rect = pygame.Rect(self.character.x + 32, self.character.y - 20, attack_range, 104)
        else:
            # Ataque circular por defecto
            attack_rect = pygame.Rect(
                self.character.x - attack_range//2, 
                self.character.y - attack_range//2, 
                attack_range + 64, 
                attack_range + 64
            )
        
        combo_effect = {
            'rect': attack_rect,
            'start_time': current_time,
            'duration': 150,
            'combo_level': self.combo_count,
            'direction': self.attack_direction
        }
        self.combo_hits.append(combo_effect)
        
        # Preparar daño para aplicar al final de la animación
        self.attack_damage_pending = base_damage
        self.attack_enemies_target = []
        
        for enemy in enemies:
            enemy_rect = pygame.Rect(enemy.x, enemy.y, 64, 64)
            if attack_rect.colliderect(enemy_rect):
                self.attack_enemies_target.append(enemy)
        
        print(f"🎯 Juan preparando combo x{self.combo_count + 1} hacia {self.attack_direction} ({base_damage} daño pendiente)")
        return len(self.attack_enemies_target) > 0
    
    def apply_pending_damage(self):
        """Aplica el daño pendiente al final de la animación de ataque"""
        if self.attack_damage_pending is None:
            return
        
        for enemy in self.attack_enemies_target:
            if hasattr(enemy, 'alive') and enemy.alive:
                enemy.take_damage(self.attack_damage_pending)
                print(f"👊 Juan combo x{self.combo_count + 1} impactó hacia {self.attack_direction} ({self.attack_damage_pending} daño)")
        
        print(f"💥 Juan finalizó ataque combo - {len(self.attack_enemies_target)} enemigos impactados")
    
    def is_character_attacking(self):
        """Retorna True si el personaje está atacando (para bloquear movimiento)"""
        return self.is_attacking
    
    def special_attack(self, enemies):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time < self.attack_cooldown * 2:
            return False
        
        self.last_attack_time = current_time
        
        special_range = 150
        attack_rect = pygame.Rect(
            self.character.x - special_range//2, 
            self.character.y - special_range//2, 
            special_range + 64, 
            special_range + 64
        )
        
        special_effect = {
            'rect': attack_rect,
            'start_time': current_time,
            'duration': 300,
            'type': 'special'
        }
        self.special_effects.append(special_effect)
        
        special_damage = 35
        hit_enemy = False
        
        for enemy in enemies:
            enemy_rect = pygame.Rect(enemy.x, enemy.y, 64, 64)
            if attack_rect.colliderect(enemy_rect):
                enemy.take_damage(special_damage)
                hit_enemy = True
                print(f"💥 Juan ataque especial ({special_damage} daño)")
        
        self.combo_count = 0
        
        return hit_enemy
    
    def update(self, enemies):
        current_time = pygame.time.get_ticks()
        
        # Actualizar animación de ataque
        self.update_attack_animation()
        
        self.combo_hits = [hit for hit in self.combo_hits 
                          if current_time - hit['start_time'] < hit['duration']]
        
        self.special_effects = [effect for effect in self.special_effects 
                              if current_time - effect['start_time'] < effect['duration']]
    
    def draw(self, screen, camera_x, camera_y):
        current_time = pygame.time.get_ticks()
        
        # Dibujar animación de ataque si está activa - Siguiendo estructura de movimientos
        if self.is_attacking and self.attack_direction in self.attack_animations and len(self.attack_animations[self.attack_direction]) > 0:
            current_frames = self.attack_animations[self.attack_direction]
            frame_index = int(self.attack_animation_frame) % len(current_frames)
            current_sprite = current_frames[frame_index]
            
            # Dibujar en la posición del personaje (igual que movimientos)
            screen.blit(current_sprite, (self.character.x - camera_x, self.character.y - camera_y))
            
            # Debug solo al cambiar de frame
            if frame_index != getattr(self, '_last_frame', -1):
                print(f"🎮 Juan ataque {self.attack_direction} - Frame {frame_index}/{len(current_frames)-1}")
                self._last_frame = frame_index
        
        # Dibujar efectos de combo con colores progresivos
        for hit in self.combo_hits:
            progress = (current_time - hit['start_time']) / hit['duration']
            alpha = int(255 * (1 - progress))
            
            # Colores más vibrantes para los combos
            colors = [(100, 255, 100), (150, 255, 50), (200, 255, 0)]
            color = colors[hit['combo_level']]
            
            effect_surface = pygame.Surface((hit['rect'].width, hit['rect'].height), pygame.SRCALPHA)
            effect_surface.set_alpha(alpha)
            effect_surface.fill(color)
            
            screen.blit(effect_surface, (hit['rect'].x - camera_x, hit['rect'].y - camera_y))
        
        # Dibujar efectos especiales con animación pulsante
        for effect in self.special_effects:
            progress = (current_time - effect['start_time']) / effect['duration']
            alpha = int(255 * (1 - progress))
            
            # Efecto pulsante para ataques especiales
            pulse = abs(math.sin(current_time * 0.01)) * 0.3 + 0.7
            
            effect_surface = pygame.Surface((effect['rect'].width, effect['rect'].height), pygame.SRCALPHA)
            effect_surface.set_alpha(int(alpha * pulse))
            effect_surface.fill((255, 255, 100))
            
            screen.blit(effect_surface, (effect['rect'].x - camera_x, effect['rect'].y - camera_y))
    
    def draw_ui(self, screen):
        font = pygame.font.Font(None, 24)
        
        combo_text = f"Combo: {self.combo_count + 1}/{self.max_combo}"
        combo_surface = font.render(combo_text, True, (100, 255, 100))
        screen.blit(combo_surface, (300, 10))
        
        current_time = pygame.time.get_ticks()
        cooldown_remaining = max(0, self.attack_cooldown - (current_time - self.last_attack_time))
        if cooldown_remaining > 0:
            cooldown_text = f"Cooldown: {cooldown_remaining}ms"
            cooldown_surface = font.render(cooldown_text, True, (255, 255, 100))
            screen.blit(cooldown_surface, (300, 35))