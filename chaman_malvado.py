import pygame
import random
import math
from PIL import Image
import requests
from io import BytesIO
from worm_enemy import WormEnemy

class ChamanMalvado:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.max_health = 400
        self.health = self.max_health
        self.speed = 2.5
        self.attack_range = 250
        self.attack_cooldown = 2500
        self.last_attack_time = 0
        self.last_summon_time = 0
        self.summon_cooldown = 8000  # Invoca gusanos cada 8 segundos
        
        # Atributos base del Chamán
        self.damage = 30
        self.defense = 5
        self.magic_power = 25
        
        # Animaciones de movimiento y ataque
        self.current_direction = "down"
        self.moving = False
        self.attacking = False
        self.animation_frame = 0
        self.animation_speed = 0.15
        self.attack_animation_frame = 0
        self.attack_animation_speed = 0.2
        
        # URLs de las animaciones desde GitHub
        self.movement_gif_urls = {
            "right": "https://github.com/user-attachments/assets/53ca8eb3-4bb1-4148-b38c-7539c9f61c25",
            "up": "https://github.com/user-attachments/assets/8ef42a26-0937-401c-9368-6ecedd84a533",
            "down": "https://github.com/user-attachments/assets/c86c9214-bc8c-4513-8840-10918e85b05a",
            "left": "https://github.com/user-attachments/assets/a4dd4c92-0317-48dc-b592-c7085a08c7e2"
        }
        
        self.attack_gif_urls = {
            "right": "https://github.com/user-attachments/assets/4e6b6aac-8a4c-4888-8c69-607072814c03",
            "up": "https://github.com/user-attachments/assets/c1849aaf-af88-44d3-aabe-fb502948369d",
            "down": "https://github.com/user-attachments/assets/a1710bbf-ae65-4f71-9f6d-f1fbf2d3d02c",
            "left": "https://github.com/user-attachments/assets/805feee8-dfab-4799-a494-da3174678c8a"
        }
        
        # Diccionarios para almacenar las animaciones
        self.movement_animations = {}
        self.attack_animations = {}
        
        # Sistema de proyectiles mágicos
        self.projectiles = []
        
        # Sistema de invocación de gusanos
        self.summoned_worms = []
        
        # Estados del Chamán
        self.invulnerable = False
        self.invulnerable_time = 0
        self.invulnerable_duration = 800
        
        # Cargar todas las animaciones
        self.load_all_animations()
        
        print("👹 Chamán Malvado invocado con 400 HP y poderes arcanos")
    
    def load_all_animations(self):
        """Carga todas las animaciones de movimiento y ataque desde GitHub"""
        print("🔮 Cargando animaciones del Chamán Malvado desde GitHub...")
        
        # Cargar animaciones de movimiento
        print("🚶 Cargando animaciones de movimiento...")
        for direction, url in self.movement_gif_urls.items():
            try:
                print(f"📥 Descargando movimiento {direction}...")
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                gif_data = BytesIO(response.content)
                gif = Image.open(gif_data)
                frames = []
                
                for frame_num in range(gif.n_frames):
                    gif.seek(frame_num)
                    frame = gif.copy().convert("RGBA")
                    
                    # Escalar sprite del Chamán (más grande que los personajes)
                    frame = frame.resize((80, 80), Image.Resampling.LANCZOS)
                    
                    frame_data = frame.tobytes()
                    pygame_surface = pygame.image.fromstring(frame_data, frame.size, "RGBA")
                    pygame_surface = pygame_surface.convert_alpha()
                    pygame_surface.set_colorkey((255, 255, 255))  # Transparencia blanca
                    
                    frames.append(pygame_surface)
                
                self.movement_animations[direction] = frames
                print(f"✅ Movimiento '{direction}': {len(frames)} frames")
                
            except Exception as e:
                print(f"❌ Error cargando movimiento {direction}: {e}")
                # Crear sprite de respaldo
                backup_surface = pygame.Surface((80, 80))
                backup_surface.fill((120, 0, 120))  # Púrpura
                self.movement_animations[direction] = [backup_surface]
        
        # Cargar animaciones de ataque
        print("⚔️ Cargando animaciones de ataque...")
        for direction, url in self.attack_gif_urls.items():
            try:
                print(f"📥 Descargando ataque {direction}...")
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                gif_data = BytesIO(response.content)
                gif = Image.open(gif_data)
                frames = []
                
                for frame_num in range(gif.n_frames):
                    gif.seek(frame_num)
                    frame = gif.copy().convert("RGBA")
                    
                    # Escalar sprite de ataque del Chamán
                    frame = frame.resize((80, 80), Image.Resampling.LANCZOS)
                    
                    frame_data = frame.tobytes()
                    pygame_surface = pygame.image.fromstring(frame_data, frame.size, "RGBA")
                    pygame_surface = pygame_surface.convert_alpha()
                    pygame_surface.set_colorkey((255, 255, 255))
                    
                    frames.append(pygame_surface)
                
                self.attack_animations[direction] = frames
                print(f"✅ Ataque '{direction}': {len(frames)} frames")
                
            except Exception as e:
                print(f"❌ Error cargando ataque {direction}: {e}")
                # Crear sprite de respaldo
                backup_surface = pygame.Surface((80, 80))
                backup_surface.fill((255, 0, 120))  # Rosa mágico
                self.attack_animations[direction] = [backup_surface]
        
        print("✅ Todas las animaciones del Chamán Malvado cargadas")
    
    def update(self, players, enemy_list=None):
        """Actualiza la lógica del Chamán con IA inteligente"""
        current_time = pygame.time.get_ticks()
        
        # Actualizar invulnerabilidad
        if self.invulnerable:
            if current_time - self.invulnerable_time >= self.invulnerable_duration:
                self.invulnerable = False
        
        # Buscar el jugador más cercano vivo
        closest_player = None
        min_distance = float('inf')
        
        for player in players:
            if player.health > 0:
                distance = math.sqrt((self.x - player.x)**2 + (self.y - player.y)**2)
                if distance < min_distance:
                    min_distance = distance
                    closest_player = player
        
        if closest_player:
            # IA de movimiento inteligente
            self.ai_movement(closest_player, min_distance)
            
            # Sistema de ataque si está en rango
            if min_distance <= self.attack_range and current_time - self.last_attack_time >= self.attack_cooldown:
                self.magic_attack(closest_player)
                self.last_attack_time = current_time
            
            # Sistema de invocación de gusanos
            if current_time - self.last_summon_time >= self.summon_cooldown and enemy_list is not None:
                self.summon_worms(enemy_list, closest_player)
                self.last_summon_time = current_time
        
        # Actualizar animaciones
        self.update_animations()
        
        # Actualizar proyectiles
        self.update_projectiles()
    
    def ai_movement(self, target_player, distance):
        """IA de movimiento inteligente que se acerca al jugador"""
        # Calcular dirección hacia el jugador
        dx = target_player.x - self.x
        dy = target_player.y - self.y
        
        # Solo moverse si está lejos del jugador
        if distance > 180:
            self.moving = True
            
            # Determinar dirección principal de movimiento
            if abs(dx) > abs(dy):
                if dx > 0:
                    self.current_direction = "right"
                    self.x += self.speed
                else:
                    self.current_direction = "left"
                    self.x -= self.speed
            else:
                if dy > 0:
                    self.current_direction = "down"
                    self.y += self.speed
                else:
                    self.current_direction = "up"
                    self.y -= self.speed
        else:
            self.moving = False
    
    def magic_attack(self, target_player):
        """Ataque mágico mejorado del Chamán"""
        print("🔮 ¡Chamán lanza ataque mágico devastador!")
        
        # Iniciar animación de ataque
        self.attacking = True
        self.attack_animation_frame = 0
        
        # Calcular dirección hacia el jugador para la animación
        dx = target_player.x - self.x
        dy = target_player.y - self.y
        
        if abs(dx) > abs(dy):
            self.current_direction = "right" if dx > 0 else "left"
        else:
            self.current_direction = "down" if dy > 0 else "up"
        
        # Crear múltiples proyectiles mágicos (ataque más poderoso)
        base_damage = self.magic_power
        
        for i in range(3):  # 3 proyectiles por ataque
            # Calcular dirección con ligera variación
            angle_offset = (i - 1) * 0.3  # Dispersión
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0:
                # Normalizar y aplicar offset
                norm_dx = dx / distance
                norm_dy = dy / distance
                
                # Aplicar rotación para dispersión
                cos_offset = math.cos(angle_offset)
                sin_offset = math.sin(angle_offset)
                
                final_dx = norm_dx * cos_offset - norm_dy * sin_offset
                final_dy = norm_dx * sin_offset + norm_dy * cos_offset
                
                # Crear proyectil
                projectile = {
                    'x': self.x + 40,  # Centro del chamán
                    'y': self.y + 40,
                    'dx': final_dx * 180,  # Velocidad del proyectil
                    'dy': final_dy * 180,
                    'damage': base_damage + random.randint(-5, 5),
                    'lifetime': 4000,  # 4 segundos
                    'start_time': pygame.time.get_ticks(),
                    'type': 'magic'
                }
                
                self.projectiles.append(projectile)
    
    def summon_worms(self, enemy_list, target_player):
        """Invoca gusanos cerca del jugador"""
        print("🐛 ¡Chamán invoca criaturas malévolas!")
        
        # Crear 2-3 gusanos cerca del jugador
        num_worms = random.randint(2, 3)
        
        for _ in range(num_worms):
            # Posición aleatoria cerca del jugador
            offset_x = random.randint(-150, 150)
            offset_y = random.randint(-150, 150)
            
            worm_x = max(50, min(1800, target_player.x + offset_x))
            worm_y = max(50, min(1000, target_player.y + offset_y))
            
            # Crear gusano invocado (más fuerte que los normales)
            summoned_worm = WormEnemy(worm_x, worm_y)
            summoned_worm.health = 60  # Más resistente
            summoned_worm.damage = 20  # Más daño
            summoned_worm.speed = 2.5  # Más rápido
            summoned_worm.is_summoned = True  # Marcar como invocado
            
            enemy_list.append(summoned_worm)
            self.summoned_worms.append(summoned_worm)
        
        print(f"👹 Chamán invocó {num_worms} criaturas malévolas")
    
    def update_animations(self):
        """Actualiza las animaciones del Chamán"""
        if self.attacking:
            # Animación de ataque
            self.attack_animation_frame += self.attack_animation_speed
            if (self.current_direction in self.attack_animations and 
                len(self.attack_animations[self.current_direction]) > 0):
                if self.attack_animation_frame >= len(self.attack_animations[self.current_direction]):
                    self.attacking = False  # Terminar animación de ataque
                    self.attack_animation_frame = 0
        elif self.moving:
            # Animación de movimiento
            self.animation_frame += self.animation_speed
            if (self.current_direction in self.movement_animations and 
                len(self.movement_animations[self.current_direction]) > 0):
                if self.animation_frame >= len(self.movement_animations[self.current_direction]):
                    self.animation_frame = 0
        else:
            # Idle - primer frame de la animación actual
            self.animation_frame = 0
    
    def update_projectiles(self):
        """Actualiza todos los proyectiles mágicos"""
        current_time = pygame.time.get_ticks()
        
        for projectile in self.projectiles[:]:
            # Mover proyectil
            projectile['x'] += projectile['dx'] / 60  # 60 FPS
            projectile['y'] += projectile['dy'] / 60
            
            # Eliminar proyectiles viejos
            if current_time - projectile['start_time'] > projectile['lifetime']:
                self.projectiles.remove(projectile)
    
    def check_projectile_collisions(self, players):
        """Verifica colisiones de proyectiles con jugadores"""
        for projectile in self.projectiles[:]:
            projectile_rect = pygame.Rect(projectile['x'] - 12, projectile['y'] - 12, 24, 24)
            
            for player in players:
                if player.health > 0:
                    player_rect = pygame.Rect(player.x, player.y, 64, 64)
                    
                    if projectile_rect.colliderect(player_rect):
                        # Aplicar daño
                        if hasattr(player, 'take_damage'):
                            damage_dealt = projectile['damage'] - getattr(player, 'defense', 0)
                            damage_dealt = max(1, damage_dealt)  # Mínimo 1 de daño
                            player.take_damage(damage_dealt)
                            print(f"💥 Proyectil mágico impactó a {player.name} por {damage_dealt} daño")
                        
                        # Eliminar proyectil
                        if projectile in self.projectiles:
                            self.projectiles.remove(projectile)
                        break
    
    def take_damage(self, damage):
        """El Chamán recibe daño"""
        if self.invulnerable:
            return False
        
        # Aplicar defensa
        actual_damage = max(1, damage - self.defense)
        self.health -= actual_damage
        self.health = max(0, self.health)
        
        # Activar invulnerabilidad temporal
        self.invulnerable = True
        self.invulnerable_time = pygame.time.get_ticks()
        
        print(f"👹 Chamán Malvado recibió {actual_damage} daño (Vida: {self.health}/{self.max_health})")
        
        if self.health <= 0:
            print("💀 ¡Chamán Malvado ha sido derrotado!")
            self.summon_final_reward()
            return True
        return False
    
    def summon_final_reward(self):
        """Al morir, el Chamán suelta recompensas especiales"""
        print("✨ ¡El Chamán derrotado libera energía mágica y tesoros!")
        # Esta función será llamada por el juego principal para generar drops especiales
    
    def draw(self, screen, camera_x=0, camera_y=0):
        """Dibuja el Chamán con sus animaciones"""
        # Determinar qué animación usar
        if self.attacking and self.current_direction in self.attack_animations:
            current_animations = self.attack_animations[self.current_direction]
            frame_index = int(self.attack_animation_frame) % len(current_animations)
        elif self.current_direction in self.movement_animations:
            current_animations = self.movement_animations[self.current_direction]
            frame_index = int(self.animation_frame) % len(current_animations)
        else:
            # Fallback a sprite básico
            backup_surface = pygame.Surface((80, 80))
            backup_surface.fill((120, 0, 120))
            screen.blit(backup_surface, (self.x - camera_x, self.y - camera_y))
            self.draw_health_bar(screen, camera_x, camera_y)
            self.draw_projectiles(screen, camera_x, camera_y)
            return
        
        # Dibujar sprite actual
        if len(current_animations) > 0:
            current_sprite = current_animations[frame_index]
            
            # Efecto de invulnerabilidad
            if self.invulnerable:
                current_time = pygame.time.get_ticks()
                if (current_time // 100) % 2:  # Parpadeo
                    temp_sprite = current_sprite.copy()
                    temp_sprite.set_alpha(128)
                    screen.blit(temp_sprite, (self.x - camera_x, self.y - camera_y))
                else:
                    screen.blit(current_sprite, (self.x - camera_x, self.y - camera_y))
            else:
                screen.blit(current_sprite, (self.x - camera_x, self.y - camera_y))
        
        # Dibujar elementos adicionales
        self.draw_health_bar(screen, camera_x, camera_y)
        self.draw_projectiles(screen, camera_x, camera_y)
    
    def draw_health_bar(self, screen, camera_x, camera_y):
        """Dibuja la barra de vida del Chamán (más grande)"""
        bar_width = 100
        bar_height = 12
        bar_x = self.x - camera_x - 10
        bar_y = self.y - camera_y - 25
        
        # Fondo de la barra
        pygame.draw.rect(screen, (50, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        
        # Barra de vida con colores según la salud
        health_ratio = self.health / self.max_health
        health_width = int(health_ratio * bar_width)
        
        if health_ratio > 0.6:
            health_color = (255, 100, 255)  # Púrpura mágico
        elif health_ratio > 0.3:
            health_color = (255, 165, 0)   # Naranja
        else:
            health_color = (255, 0, 0)     # Rojo crítico
        
        pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height))
        
        # Borde de la barra
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)
    
    def draw_projectiles(self, screen, camera_x, camera_y):
        """Dibuja proyectiles mágicos con efectos especiales"""
        current_time = pygame.time.get_ticks()
        
        for projectile in self.projectiles:
            proj_x = int(projectile['x'] - camera_x)
            proj_y = int(projectile['y'] - camera_y)
            
            # Efecto pulsante para los proyectiles mágicos
            pulse = 1 + 0.3 * math.sin(current_time * 0.01)
            radius = int(12 * pulse)
            
            # Proyectil mágico con múltiples capas
            pygame.draw.circle(screen, (180, 0, 180), (proj_x, proj_y), radius)      # Aura exterior
            pygame.draw.circle(screen, (255, 100, 255), (proj_x, proj_y), radius-3) # Núcleo mágico
            pygame.draw.circle(screen, (255, 255, 255), (proj_x, proj_y), radius-6) # Centro brillante
            
            # Partículas mágicas aleatorias alrededor del proyectil
            for _ in range(3):
                particle_x = proj_x + random.randint(-15, 15)
                particle_y = proj_y + random.randint(-15, 15)
                pygame.draw.circle(screen, (255, 200, 255), (particle_x, particle_y), 2)