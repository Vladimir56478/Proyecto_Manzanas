import pygame
import math
from PIL import Image
import os

class AdanAttack:
    def __init__(self, character):
        self.character = character
        self.projectiles = []
        self.combo_hits = []
        self.special_effects = []
        self.melee_attacks = []  # Añadir atributo faltante
        self.last_attack_time = 0
        self.attack_cooldown = 500
        
        # Atributos de daño para compatibilidad
        self.melee_damage = 40
        self.projectile_damage = 25
        
        # Variables para animaciones de ataque
        self.is_attacking = False
        self.attack_animation_frame = 0
        self.attack_animation_speed = 0.3
        self.attack_direction = "down"
        self.attack_damage_pending = None  # Almacena el daño pendiente hasta el final de la animación
        self.attack_enemies_target = []    # Lista de enemigos que serán afectados al final
        
        # URLs de los GIFs de ataque de Adán desde archivo local Issues
        self.attack_gif_urls = {
            "up": "assets/characters/adan/attacks/up.gif",
            "down": "assets/characters/adan/attacks/down.gif",
            "left": "assets/characters/adan/attacks/left.gif",
            "right": "assets/characters/adan/attacks/right.gif"
        }        # Diccionario para almacenar los frames de cada dirección de ataque
        self.attack_animations = {}
        self.load_attack_animations()
        
    def load_attack_animations(self):
        """Carga todos los GIFs de ataque y extrae sus frames"""
        print("🔥 Cargando animaciones de ataque de Adán desde archivo local...")
        
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
                    backup_surface.fill((0, 255, 255, 128))  # Cian semitransparente
                    frames.append(backup_surface)
                
                self.attack_animations[direction] = frames
                print(f"✅ Cargada animación de ataque '{direction}': {len(frames)} frames")
                
            except Exception as e:
                print(f"❌ Error cargando ataque {direction}: {e}")
                # Crear frame de respaldo en caso de error
                backup_surface = pygame.Surface((100, 100), pygame.SRCALPHA)  # 64 * 1.56 = 100
                backup_surface.fill((255, 0, 0, 128))  # Rojo semitransparente
                self.attack_animations[direction] = [backup_surface]
    
    def start_attack_animation(self, direction):
        """Inicia la animación de ataque en la dirección especificada"""
        self.is_attacking = True
        self.attack_direction = direction
        self.attack_animation_frame = 0
        print(f"🔥 Adán iniciando animación de ataque hacia {direction}")
        
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
            # Seguir exactamente la misma lógica que los movimientos de Adán
            direction = "down"  # Dirección por defecto
            
            # Detectar dirección actual basada en teclas presionadas - Solo WASD
            if keys_pressed[pygame.K_w]:
                direction = "up"    # Adán no tiene inversión
            elif keys_pressed[pygame.K_s]:
                direction = "down"  # Adán no tiene inversión
            elif keys_pressed[pygame.K_a]:
                direction = "left"  # Adán no tiene inversión
            elif keys_pressed[pygame.K_d]:
                direction = "right" # Adán no tiene inversión
            else:
                # Si no hay teclas presionadas, usar dirección actual del personaje
                direction = getattr(self.character, 'current_direction', 'down')
            
            print(f"🔥 Adán atacando hacia: {direction}")
            
            # Iniciar animación de ataque
            self.start_attack_animation(direction)
            
            # Realizar ataque cuerpo a cuerpo
            return self.prepare_melee_attack(enemies)
        
        return False
    
    def prepare_melee_attack(self, enemies):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time < self.attack_cooldown:
            return False
        
        self.last_attack_time = current_time
        
        # Crear área de ataque más grande y direccional
        # Escalar el rango de ataque 1.56x para coincidir con sprites escalados
        attack_range = int(80 * 1.56)
        if self.attack_direction == "up":
            attack_rect = pygame.Rect(self.character.x - 20, self.character.y - attack_range, 104, attack_range + 32)
        elif self.attack_direction == "down":
            attack_rect = pygame.Rect(self.character.x - 20, self.character.y + 32, 104, attack_range)
        elif self.attack_direction == "left":
            attack_rect = pygame.Rect(self.character.x - attack_range, self.character.y - 20, attack_range + 32, 104)
        elif self.attack_direction == "right":
            attack_rect = pygame.Rect(self.character.x + 32, self.character.y - 20, attack_range, 104)
        else:
            # Ataque circular por defecto
            attack_rect = pygame.Rect(self.character.x - 30, self.character.y - 30, 120, 120)
        
        melee_effect = {
            'rect': attack_rect,
            'start_time': current_time,
            'duration': 200,
            'direction': self.attack_direction
        }
        self.melee_attacks.append(melee_effect)
        
        # Preparar daño para aplicar al final de la animación
        self.attack_damage_pending = 40
        self.attack_enemies_target = []
        
        for enemy in enemies:
            enemy_rect = pygame.Rect(enemy.x, enemy.y, 100, 100)  # 64 * 1.56 = 100
            if attack_rect.colliderect(enemy_rect):
                self.attack_enemies_target.append(enemy)
        
        print(f"🎯 Adán preparando ataque cuerpo a cuerpo hacia {self.attack_direction} (40 daño pendiente)")
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
                print(f"⚔️ Adán golpeó con ataque cuerpo a cuerpo hacia {self.attack_direction} ({self.attack_damage_pending} daño)")
        
        print(f"💥 Adán finalizó ataque cuerpo a cuerpo - {len(self.attack_enemies_target)} enemigos impactados")
    
    def is_character_attacking(self):
        """Retorna True si el personaje está atacando (para bloquear movimiento)"""
        return self.is_attacking
    
    def ranged_attack(self, target_x, target_y):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time < self.attack_cooldown:
            return False
        
        self.last_attack_time = current_time
        
        dx = target_x - (self.character.x + 32)
        dy = target_y - (self.character.y + 32)
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            dx /= distance
            dy /= distance
        
        projectile = {
            'x': self.character.x + 32,
            'y': self.character.y + 32,
            'dx': dx,
            'dy': dy,
            'speed': 400,
            'damage': 25,
            'active': True,
            'start_time': current_time
        }
        self.projectiles.append(projectile)
        print(f"🏹 Adán lanzó proyectil")
        return True
    
    def update(self, enemies):
        current_time = pygame.time.get_ticks()
        dt = 1/60
        
        # Actualizar animación de ataque
        self.update_attack_animation()
        
        for projectile in self.projectiles[:]:
            if not projectile['active']:
                continue
                
            projectile['x'] += projectile['dx'] * projectile['speed'] * dt
            projectile['y'] += projectile['dy'] * projectile['speed'] * dt
            
            projectile_rect = pygame.Rect(projectile['x'] - 5, projectile['y'] - 5, 10, 10)
            for enemy in enemies:
                enemy_rect = pygame.Rect(enemy.x, enemy.y, 100, 100)  # 64 * 1.56 = 100
                if projectile_rect.colliderect(enemy_rect) and projectile['active']:
                    enemy.take_damage(projectile['damage'])
                    projectile['active'] = False
                    print(f"🎯 Proyectil de Adán impactó ({projectile['damage']} daño)")
                    break
            
            if (projectile['x'] < -100 or projectile['x'] > 1100 or 
                projectile['y'] < -100 or projectile['y'] > 800 or
                current_time - projectile['start_time'] > 3000):
                projectile['active'] = False
        
        self.projectiles = [p for p in self.projectiles if p['active']]
        
        self.melee_attacks = [attack for attack in self.melee_attacks 
                            if current_time - attack['start_time'] < attack['duration']]
    
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
                print(f"🔥 Adán ataque {self.attack_direction} - Frame {frame_index}/{len(current_frames)-1}")
                self._last_frame = frame_index
        
        # Dibujar proyectiles con efectos mejorados
        for projectile in self.projectiles:
            if projectile['active']:
                x = int(projectile['x'] - camera_x)
                y = int(projectile['y'] - camera_y)
                # Efecto de brillo para proyectiles
                pygame.draw.circle(screen, (255, 150, 100), (x, y), 7)
                pygame.draw.circle(screen, (255, 200, 150), (x, y), 5)
                pygame.draw.circle(screen, (255, 255, 200), (x, y), 3)
        
        # Efectos de ataque cuerpo a cuerpo eliminados para mejor visibilidad