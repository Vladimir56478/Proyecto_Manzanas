import pygame
import math
from PIL import Image
import os

class JuanAttack:
    def __init__(self, character):
        self.character = character
        self.combo_hits = []
        self.special_effects = []
        self.last_attack_time = 0
        self.attack_cooldown = 300
        self.combo_count = 0
        self.max_combo = 3
        
        # Atributos de daño para compatibilidad
        self.melee_damage = 15
        self.projectile_damage = 10
        
        # Variables para animaciones de ataque
        self.is_attacking = False
        self.attack_animation_frame = 0
        self.attack_animation_speed = 0.3
        self.attack_direction = "down"
        self.attack_damage_pending = None  # Almacena el daño pendiente hasta el final de la animación
        self.attack_enemies_target = []    # Lista de enemigos que serán afectados al final
        
        # URLs de los GIFs de ataque de Juan desde assets locales (INVERTIDAS)
        self.attack_gif_urls = {
            "up": "assets/characters/juan/attacks/up.gif",    # Era "down"
            "down": "assets/characters/juan/attacks/down.gif",  # Era "up"
            "left": "assets/characters/juan/attacks/left.gif",  # Era "right"
            "right": "assets/characters/juan/attacks/right.gif"  # Era "left"
        }
        
        # Diccionario para almacenar los frames de cada dirección de ataque
        self.attack_animations = {}
        self.load_attack_animations()
        
    def load_attack_animations(self):
        """Carga todos los GIFs de ataque y extrae sus frames"""
        print("⚔️ Cargando animaciones de ataque de Juan desde archivo local...")
        
        for direction, url in self.attack_gif_urls.items():
            try:
                print(f"📥 Cargando ataque {direction} desde archivo local...")
                
                # Cargar el GIF desde archivo local
                gif = Image.open(url)
                frames = []
                
                # Extraer todos los frames del GIF
                try:
                    frame_count = getattr(gif, 'n_frames', 1)  # Usar getattr para evitar error
                    for frame_num in range(frame_count):
                        gif.seek(frame_num)
                        frame = gif.copy().convert("RGBA")
                        
                        # Procesar cada pixel para eliminar fondos blancos/grises
                        pixels = frame.load()
                        if pixels:  # Verificar que pixels no sea None
                            for y in range(frame.height):
                                for x in range(frame.width):
                                    try:
                                        r, g, b, a = pixels[x, y]
                                        # Eliminar fondos blancos, grises claros y similares
                                        if r > 200 and g > 200 and b > 200:
                                            pixels[x, y] = (r, g, b, 0)  # Hacer transparente
                                        elif abs(r - g) < 30 and abs(r - b) < 30 and abs(g - b) < 30 and r > 180:
                                            pixels[x, y] = (r, g, b, 0)  # Eliminar grises claros
                                    except (IndexError, TypeError):
                                        continue  # Ignorar errores de píxeles
                        
                        # Convertir PIL image a superficie de Pygame
                        frame_data = frame.tobytes()
                        pygame_surface = pygame.image.fromstring(frame_data, frame.size, "RGBA")
                        
                        # Aplicar transparencia adicional y suavizado
                        pygame_surface = pygame_surface.convert_alpha()
                        pygame_surface.set_colorkey((255, 255, 255))
                        
                        # Escalar 56% más grande (30% + 20% adicional)
                        original_size = pygame_surface.get_size()
                        new_size = (int(original_size[0] * 1.56), int(original_size[1] * 1.56))
                        pygame_surface = pygame.transform.scale(pygame_surface, new_size)
                        
                        frames.append(pygame_surface)
                        
                except (AttributeError, OSError, Exception) as e:
                    print(f"⚠️ Error procesando frames: {e}")
                    # Crear frame de respaldo
                    backup_surface = pygame.Surface((100, 100), pygame.SRCALPHA)
                    backup_surface.fill((255, 255, 0, 128))  # Amarillo semitransparente
                    frames.append(backup_surface)
                
                self.attack_animations[direction] = frames
                print(f"✅ Cargada animación de ataque '{direction}': {len(frames)} frames")
                
            except Exception as e:
                print(f"❌ Error cargando ataque {direction}: {e}")
                # Crear frame de respaldo en caso de error
                backup_surface = pygame.Surface((100, 100), pygame.SRCALPHA)  # 64 * 1.56 = 100
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
            
            # Control manual con DIRECCIONES INVERTIDAS (restaurado) - Solo WASD
            if keys_pressed[pygame.K_w]:
                direction = "down"  # INVERTIDO: era "up"
            elif keys_pressed[pygame.K_s]:
                direction = "up"    # INVERTIDO: era "down"
            elif keys_pressed[pygame.K_a]:
                direction = "right" # INVERTIDO: era "left"
            elif keys_pressed[pygame.K_d]:
                direction = "left"  # INVERTIDO: era "right"
            else:
                # Si no hay teclas presionadas, usar dirección actual del personaje INVERTIDA
                current_direction = getattr(self.character, 'current_direction', 'down')
                # APLICAR MISMAS INVERSIONES que a las teclas para consistencia
                if current_direction == "up":
                    direction = "down"    # INVERTIDO: up -> down
                elif current_direction == "down":
                    direction = "up"      # INVERTIDO: down -> up  
                elif current_direction == "left":
                    direction = "right"   # INVERTIDO: left -> right
                elif current_direction == "right":
                    direction = "left"    # INVERTIDO: right -> left
                else:
                    direction = "down"    # Fallback por defecto
                    
                print(f"🎯 Juan quieto - mirando {current_direction}, atacando hacia {direction} (invertido)")
            
            print(f"🎯 Juan atacando hacia: {direction}")
            
            # Iniciar animación de ataque
            self.start_attack_animation(direction)
            
            # Preparar ataque combo (daño se aplicará al final de la animación)
            return self.prepare_combo_attack(enemies)
        
        return False
        
    def prepare_combo_attack(self, enemies, from_ai=False):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time < self.attack_cooldown:
            return False
        
        self.last_attack_time = current_time
        self.combo_count = (self.combo_count + 1) % self.max_combo
        
        base_damage = 15 + (self.combo_count * 5)
        range_multiplier = 1 + (self.combo_count * 0.5)
        
        # Crear área de ataque direccional - CORREGIDO PARA AMBOS CASOS
        # Escalar el rango de ataque 1.56x para coincidir con sprites escalados
        attack_range = int(70 * range_multiplier * 1.56)
        
        # SISTEMA DUAL - Diferencia entre control manual (invertido) e IA (directo)
        # Control manual: teclas invertidas -> dirección invertida -> área compensada (doble inversión = normal)
        # IA: dirección directa -> área directa hacia el enemigo
        
        if from_ai:
            # PARA IA: Áreas directas hacia donde está el enemigo
            if self.attack_direction == "up":
                attack_rect = pygame.Rect(self.character.x - 20, self.character.y - attack_range, 104, attack_range + 32)
            elif self.attack_direction == "down":
                attack_rect = pygame.Rect(self.character.x - 20, self.character.y + 32, 104, attack_range)
            elif self.attack_direction == "left":
                attack_rect = pygame.Rect(self.character.x - attack_range, self.character.y - 20, attack_range + 32, 104)
            elif self.attack_direction == "right":
                attack_rect = pygame.Rect(self.character.x + 32, self.character.y - 20, attack_range, 104)
            else:
                attack_rect = pygame.Rect(self.character.x - attack_range//2, self.character.y - attack_range//2, attack_range + 64, attack_range + 64)
        else:
            # PARA CONTROL MANUAL: Áreas invertidas para compensar teclas invertidas
            if self.attack_direction == "up":
                # Control manual: tecla DOWN -> dirección "up" -> área hacia ABAJO (donde presionó)
                attack_rect = pygame.Rect(self.character.x - 20, self.character.y + 32, 104, attack_range)
            elif self.attack_direction == "down":
                # Control manual: tecla UP -> dirección "down" -> área hacia ARRIBA (donde presionó)
                attack_rect = pygame.Rect(self.character.x - 20, self.character.y - attack_range, 104, attack_range + 32)
            elif self.attack_direction == "left":
                # Control manual: tecla RIGHT -> dirección "left" -> área hacia DERECHA (donde presionó)
                attack_rect = pygame.Rect(self.character.x + 32, self.character.y - 20, attack_range, 104)
            elif self.attack_direction == "right":
                # Control manual: tecla LEFT -> dirección "right" -> área hacia IZQUIERDA (donde presionó)
                attack_rect = pygame.Rect(self.character.x - attack_range, self.character.y - 20, attack_range + 32, 104)
            else:
                # Ataque circular por defecto para control manual
                attack_rect = pygame.Rect(self.character.x - attack_range//2, self.character.y - attack_range//2, attack_range + 64, attack_range + 64)
        
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
            enemy_rect = pygame.Rect(enemy.x, enemy.y, 100, 100)  # 64 * 1.56 = 100
            if attack_rect.colliderect(enemy_rect):
                self.attack_enemies_target.append(enemy)
        
        print(f"🎯 Juan preparando combo x{self.combo_count + 1} hacia {self.attack_direction} ({base_damage} daño pendiente)")
        print(f"📍 Área de ataque: x={attack_rect.x}, y={attack_rect.y}, w={attack_rect.width}, h={attack_rect.height}")
        print(f"🎮 Personaje en: x={self.character.x}, y={self.character.y}")
        return len(self.attack_enemies_target) > 0
    
    def apply_pending_damage(self):
        """Aplica el daño pendiente al final de la animación de ataque"""
        if self.attack_damage_pending is None:
            return
        
        for enemy in self.attack_enemies_target:
            # Verificar si el enemigo está vivo (compatibilidad con gusanos y chamán)
            is_alive = False
            if hasattr(enemy, 'alive'):
                is_alive = enemy.alive  # Para gusanos
            elif hasattr(enemy, 'health'):
                is_alive = enemy.health > 0  # Para Chamán y otros enemies con solo health
            
            if is_alive:
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
            enemy_rect = pygame.Rect(enemy.x, enemy.y, 100, 100)  # 64 * 1.56 = 100
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
        
        # Efectos de combo eliminados para mejor visibilidad
        
        # Efectos especiales eliminados para mejor visibilidad
    
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