import pygame
import math
import random
from PIL import Image
import os

class WormEnemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.max_health = 40
        self.health = self.max_health
        self.speed = 2
        self.attack_damage = 15
        self.attack_range = 60
        self.attack_cooldown = 1500
        self.last_attack_time = 0
        
        # Escalado de tamaño (56% más grande)
        self.scale_factor = 1.56
        self.width = int(64 * self.scale_factor)
        self.height = int(64 * self.scale_factor)
        
        # Marcador para drops (evitar drops múltiples)
        self.dropped = False
        self.alive = True
        self.pending_drops = []  # Para almacenar drops pendientes
        
        # Estados de IA
        self.state = "patrol"  # patrol, chase, attack, hurt
        self.target = None
        self.patrol_points = []
        self.current_patrol = 0
        self.detection_range = 200
        self.give_up_range = 400
        
        # Animación con GIF
        self.current_direction = "down"
        self.animation_frame = 0
        self.animation_speed = 0.15
        self.moving = False
        
        # URL del GIF de movimiento del gusano desde archivo local Issues
        self.worm_gif_url = "assets/enemies/worm/worm gif.gif"
        
        # Diccionario para almacenar los frames de animación
        self.animations = {}
        self.load_worm_animation()
        
        # Movimiento
        self.vel_x = 0
        self.vel_y = 0
        self.friction = 0.8
        
        # Estado visual
        self.hurt_timer = 0
        self.hurt_duration = 200
        
        # Generar puntos de patrulla aleatorios
        self.generate_patrol_points()
        
        self.alive = True
    
    def load_worm_animation(self):
        """Carga el GIF del gusano y extrae sus frames"""
        print("Cargando animación del gusano desde archivo local...")
        
        try:
            print(f"📥 Cargando GIF del gusano desde archivo local...")
            
            # Descargar el GIF desde archivo local
            # Cargar desde archivo local
            gif = Image.open(self.worm_gif_url)
            frames = []
            
            # Extraer todos los frames del GIF
            for frame_num in range(gif.n_frames):
                gif.seek(frame_num)
                frame = gif.copy().convert("RGBA")
                
                # Convertir PIL image a superficie de Pygame
                frame_data = frame.tobytes()
                pygame_surface = pygame.image.fromstring(frame_data, frame.size, "RGBA")
                
                # Hacer transparente el fondo blanco
                pygame_surface = pygame_surface.convert_alpha()
                pygame_surface.set_colorkey((255, 255, 255))
                
                # Escalar el frame según el factor de escalado
                if hasattr(self, 'scale_factor') and self.scale_factor != 1.0:
                    original_size = pygame_surface.get_size()
                    new_size = (int(original_size[0] * self.scale_factor), 
                              int(original_size[1] * self.scale_factor))
                    pygame_surface = pygame.transform.scale(pygame_surface, new_size)
                
                frames.append(pygame_surface)
            
            # Crear frames para diferentes direcciones
            flipped_frames = []
            for frame in frames:
                # Voltear horizontalmente los frames para la dirección derecha
                flipped_frame = pygame.transform.flip(frame, True, False)
                flipped_frames.append(flipped_frame)
            
            self.animations = {
                "up": frames,
                "down": frames,
                "left": frames,          # Frames originales para la izquierda
                "right": flipped_frames, # Frames volteados para la derecha
                "idle": [frames[0]] if frames else []  # Primer frame para estado idle
            }
            print(f"✅ Cargada animación del gusano: {len(frames)} frames")
            
        except Exception as e:
            print(f"❌ Error cargando animación del gusano: {e}")
            # Crear frame de respaldo en caso de error
            backup_surface = pygame.Surface((100, 100))  # 64 * 1.56 = 100
            backup_surface.fill((100, 50, 0))  # Marrón como placeholder
            self.animations = {
                "up": [backup_surface],
                "down": [backup_surface],
                "left": [backup_surface],
                "right": [backup_surface],
                "idle": [backup_surface]
            }
    
    def generate_patrol_points(self):
        """Genera puntos de patrulla aleatorios alrededor de la posición inicial"""
        base_x, base_y = self.x, self.y
        for _ in range(4):
            patrol_x = base_x + random.randint(-200, 200)
            patrol_y = base_y + random.randint(-200, 200)
            self.patrol_points.append((patrol_x, patrol_y))
    
    def find_nearest_player(self, players):
        """Encuentra el jugador más cercano"""
        nearest = None
        min_distance = float('inf')
        
        for player in players:
            distance = math.sqrt((self.x - player.x)**2 + (self.y - player.y)**2)
            if distance < min_distance:
                min_distance = distance
                nearest = player
        
        return nearest, min_distance
    
    def update_ai(self, players):
        """Actualiza la inteligencia artificial del gusano"""
        if not self.alive:
            return
        
        nearest_player, distance = self.find_nearest_player(players)
        
        # Máquina de estados de IA
        if self.state == "patrol":
            if distance < self.detection_range:
                self.state = "chase"
                self.target = nearest_player
                print(f"🐛 Gusano detectó jugador a {distance:.1f} unidades")
            else:
                self.patrol_behavior()
        
        elif self.state == "chase":
            if distance > self.give_up_range:
                self.state = "patrol"
                self.target = None
                print("🐛 Gusano perdió al jugador")
            elif distance < self.attack_range:
                self.state = "attack"
            else:
                self.chase_behavior(nearest_player)
        
        elif self.state == "attack":
            if distance > self.attack_range * 1.5:
                self.state = "chase"
            else:
                self.attack_behavior(nearest_player)
        
        elif self.state == "hurt":
            # Estado temporal cuando recibe daño
            self.hurt_timer -= 16  # Asumiendo 60 FPS
            if self.hurt_timer <= 0:
                self.state = "chase" if self.target else "patrol"
    
    def patrol_behavior(self):
        """Comportamiento de patrulla"""
        if not self.patrol_points:
            return
        
        target_x, target_y = self.patrol_points[self.current_patrol]
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < 30:  # Llegó al punto de patrulla
            self.current_patrol = (self.current_patrol + 1) % len(self.patrol_points)
            self.moving = False
        else:
            # Moverse hacia el punto de patrulla
            if distance > 0:
                self.vel_x += (dx / distance) * 0.5
                self.vel_y += (dy / distance) * 0.5
                self.moving = True
    
    def chase_behavior(self, target):
        """Comportamiento de persecución"""
        dx = target.x - self.x
        dy = target.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            # Moverse hacia el objetivo
            self.vel_x += (dx / distance) * self.speed * 0.8
            self.vel_y += (dy / distance) * self.speed * 0.8
            self.moving = True
            
            # Actualizar dirección de animación
            if abs(dx) > abs(dy):
                self.current_direction = "right" if dx > 0 else "left"
            else:
                self.current_direction = "down" if dy > 0 else "up"
    
    def attack_behavior(self, target):
        """Comportamiento de ataque"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            self.perform_attack(target)
            self.last_attack_time = current_time
    
    def perform_attack(self, target):
        """Realiza un ataque contra el objetivo"""
        # Verificar si el objetivo está en rango
        dx = target.x - self.x
        dy = target.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance <= self.attack_range:
            # Determinar si el objetivo tiene IA (personaje inactivo)
            # Esto se determina por si el objeto tiene un atributo 'attacks' pero no está siendo usado activamente
            is_ai_controlled = self.is_ai_controlled_character(target)
            
            if is_ai_controlled:
                # Buscar el sistema de IA asociado en el juego principal
                # Esto es un poco hacky pero funcional para nuestro sistema
                if hasattr(target, 'name'):
                    # Acceder al juego principal a través del display
                    import pygame
                    if pygame.display.get_surface():
                        # El damage reducido se maneja en la IA
                        damage = self.attack_damage
                        # Simular daño para el personaje con IA
                        # Esto se debería manejar desde el sistema principal del juego
                        reduced_damage = int(damage * 0.6)  # 60% del daño
                        target.health = max(0, target.health - reduced_damage)
                        print(f"🐛 Gusano atacó a {target.name} (IA)! ({reduced_damage} daño reducido)")
            else:
                # Daño normal para el personaje activo
                if hasattr(target, 'take_damage'):
                    target.take_damage(self.attack_damage)
                    print(f"🐛 Gusano atacó al jugador activo! ({self.attack_damage} daño)")
            
            # Empujar al jugador
            if distance > 0:
                push_force = 3
                target.x += (dx / distance) * push_force
                target.y += (dy / distance) * push_force
    
    def is_ai_controlled_character(self, target):
        """Determina si un personaje está controlado por IA"""
        # Un personaje controlado por IA tiene atributos específicos
        # Por ahora, asumimos que si tiene 'attacks' pero no está siendo controlado activamente
        # es un personaje con IA
        if hasattr(target, 'attacks') and hasattr(target, 'name'):
            return True  # Simplificado - en un juego real esto sería más sofisticado
        return False
    
    def take_damage(self, damage):
        """Recibe daño"""
        if not self.alive:
            return
            
        self.health -= damage
        self.hurt_timer = self.hurt_duration
        self.state = "hurt"
        
        # Efecto de empuje cuando recibe daño
        push_x = random.uniform(-2, 2)
        push_y = random.uniform(-2, 2)
        self.vel_x += push_x
        self.vel_y += push_y
        
        print(f"🐛 Gusano recibió {damage} daño (Vida: {self.health}/{self.max_health})")
        
        if self.health <= 0:
            self.alive = False
            self.pending_drops = self.drop_items()  # Guardar drops generados
            print("💀 Gusano eliminado (+drops generados)")
    
    def drop_items(self):
        """Genera drops cuando el gusano muere"""
        if self.dropped:  # Evitar drops múltiples
            return []
            
        self.dropped = True
        drops = []
        
        # Siempre otorga algo de curación (50% de probabilidad)
        if random.random() < 0.5:
            drops.append({
                'type': 'heal',
                'x': self.x + random.randint(-10, 10),
                'y': self.y + random.randint(-10, 10),
                'collected': False
            })
            
        # 30% probabilidad de mejora de vida máxima
        if random.random() < 0.3:
            drops.append({
                'type': 'health',
                'x': self.x + random.randint(-15, 15),
                'y': self.y + random.randint(-15, 15),
                'collected': False
            })
            
        # 25% probabilidad de mejora de daño
        if random.random() < 0.25:
            drops.append({
                'type': 'damage',
                'x': self.x + random.randint(-15, 15),
                'y': self.y + random.randint(-15, 15),
                'collected': False
            })
            
        # 20% probabilidad de mejora de velocidad
        if random.random() < 0.2:
            drops.append({
                'type': 'speed',
                'x': self.x + random.randint(-15, 15),
                'y': self.y + random.randint(-15, 15),
                'collected': False
            })
        
        return drops
    
    def get_and_clear_drops(self):
        """Obtiene y limpia los drops pendientes"""
        drops = self.pending_drops[:]
        self.pending_drops = []
        return drops
    
    def update(self, players):
        """Actualiza el gusano"""
        if not self.alive:
            return
        
        # Actualizar IA
        self.update_ai(players)
        
        # Detectar si se está moviendo
        prev_moving = self.moving
        self.moving = abs(self.vel_x) > 0.1 or abs(self.vel_y) > 0.1
        
        # Actualizar física
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_x *= self.friction
        self.vel_y *= self.friction
        
        # Actualizar animación
        if self.moving:
            # Si se está moviendo, animar normalmente
            self.animation_frame += self.animation_speed
            current_animation = self.current_direction
            if current_animation in self.animations and len(self.animations[current_animation]) > 0:
                if self.animation_frame >= len(self.animations[current_animation]):
                    self.animation_frame = 0
        else:
            # Cuando está quieto, mantener la dirección hacia el objetivo si existe
            self.animation_frame = 0
            if self.target:
                # Calcular la dirección hacia el objetivo cuando está quieto
                dx = self.target.x - self.x
                dy = self.target.y - self.y
                
                # Determinar dirección de mirada hacia el objetivo
                if abs(dx) > abs(dy):
                    self.current_direction = "right" if dx > 0 else "left"
                else:
                    self.current_direction = "down" if dy > 0 else "up"
            # Si no hay objetivo, mantener la última dirección conocida (no cambiar a "idle")
    
    def draw(self, screen, camera_x, camera_y):
        """Dibuja el gusano"""
        if not self.alive:
            return
        
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Dibujar animación del gusano si está disponible
        if self.current_direction in self.animations and len(self.animations[self.current_direction]) > 0:
            current_frames = self.animations[self.current_direction]
            frame_index = int(self.animation_frame) % len(current_frames)
            current_sprite = current_frames[frame_index]
            
            # Aplicar efecto de daño si está herido
            if self.hurt_timer > 0:
                # Crear superficie temporal para el efecto de daño
                hurt_surface = current_sprite.copy()
                hurt_surface.fill((255, 100, 100), special_flags=pygame.BLEND_ADD)
                screen.blit(hurt_surface, (screen_x, screen_y))
            else:
                screen.blit(current_sprite, (screen_x, screen_y))
        else:
            # Fallback: dibujar representación básica del gusano
            color = (100, 50, 0)  # Marrón
            
            # Efecto de daño
            if self.hurt_timer > 0:
                color = (255, 100, 100)  # Rojo cuando está herido
            
            # Dibujar cuerpo del gusano (varios segmentos)
            segments = 3
            segment_size = 20
            
            for i in range(segments):
                segment_x = screen_x + i * segment_size - 10
                segment_y = screen_y
                segment_color = tuple(max(0, c - i * 20) for c in color)
                
                pygame.draw.circle(screen, segment_color, 
                                 (segment_x, segment_y + segment_size), segment_size - i * 2)
        
        # Dibujar barra de vida
        if self.health < self.max_health:
            bar_width = 60
            bar_height = 6
            bar_x = screen_x - bar_width // 2 + 32
            bar_y = screen_y - 10
            
            # Fondo de la barra
            pygame.draw.rect(screen, (100, 0, 0), 
                           (bar_x, bar_y, bar_width, bar_height))
            
            # Vida actual
            health_width = int((self.health / self.max_health) * bar_width)
            pygame.draw.rect(screen, (0, 255, 0), 
                           (bar_x, bar_y, health_width, bar_height))
        
        # Indicador de estado eliminado para mejor apariencia visual
    
    def get_rect(self):
        """Obtiene rectángulo de colisión"""
        return pygame.Rect(self.x, self.y, 83, 83)  # 64 * 1.3 = 83

class WormSpawner:
    def __init__(self, max_worms=5):
        self.worms = []
        self.max_worms = max_worms
        self.spawn_cooldown = 5000  # 5 segundos base entre spawns
        self.last_spawn_time = 0
        self.spawn_areas = []  # Áreas donde pueden aparecer gusanos
        self.total_spawned = 0  # Contador de gusanos spawneados
        
        # Variables para spawn dinámico
        self.base_spawn_cooldown = 5000  # 5 segundos base
        self.min_spawn_cooldown = 3000   # 3 segundos mínimo
        self.spawn_acceleration = 200    # Reducir 200ms por cada gusano spawneado
    
    def add_spawn_area(self, x, y, width, height):
        """Añade un área donde pueden aparecer gusanos"""
        self.spawn_areas.append((x, y, width, height))
    
    def spawn_worm(self, players, collision_manager=None):
        """Genera gusanos gradualmente alrededor de los personajes, respetando bloques de colisión"""
        # Verificar si ya hemos spawneado todos los gusanos
        if self.total_spawned >= self.max_worms:
            return
        
        current_time = pygame.time.get_ticks()
        
        # Spawn dinámico: se acelera con el tiempo
        current_cooldown = max(self.min_spawn_cooldown, 
                             self.base_spawn_cooldown - (self.total_spawned * self.spawn_acceleration))
        
        if current_time - self.last_spawn_time < current_cooldown:
            return
        
        if not players:
            return
        
        # Intentar hasta 20 veces encontrar una posición válida alrededor de los personajes
        for attempt in range(20):
            # Elegir un jugador aleatorio como punto de referencia
            target_player = random.choice(players)
            
            # Generar posición en un radio variable (más lejos para los primeros gusanos)
            base_distance = 180 - (self.total_spawned * 2)  # Se acercan gradualmente
            min_distance = max(120, base_distance)
            max_distance = min_distance + 250
            
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(min_distance, max_distance)
            
            spawn_x = int(target_player.x + math.cos(angle) * distance)
            spawn_y = int(target_player.y + math.sin(angle) * distance)
            
            # Asegurar que esté dentro de los límites del mundo
            spawn_x = max(50, min(spawn_x, 5890))  # Límites del mundo
            spawn_y = max(50, min(spawn_y, 1030))
            
            # Verificar que no esté muy cerca de ningún jugador (mínimo 120px)
            too_close = False
            for player in players:
                distance_to_player = math.sqrt((spawn_x - player.x)**2 + (spawn_y - player.y)**2)
                if distance_to_player < 120:
                    too_close = True
                    break
            
            if too_close:
                continue
            
            # Verificar que no esté bloqueado por bloques de colisión
            if collision_manager:
                worm_rect = pygame.Rect(spawn_x - 40, spawn_y - 40, 83, 83)  # Área del gusano
                collision_found = False
                for block in collision_manager.blocks:
                    if worm_rect.colliderect(block.rect):
                        collision_found = True
                        break
                
                if collision_found:
                    continue  # Intentar otra posición
            
            # Verificar que no esté muy cerca de otros gusanos
            too_close_to_worm = False
            for existing_worm in self.worms:
                distance_to_worm = math.sqrt((spawn_x - existing_worm.x)**2 + (spawn_y - existing_worm.y)**2)
                if distance_to_worm < 100:  # Mínimo 100px entre gusanos
                    too_close_to_worm = True
                    break
            
            if too_close_to_worm:
                continue
            
            # Posición válida encontrada
            new_worm = WormEnemy(spawn_x, spawn_y)
            self.worms.append(new_worm)
            self.last_spawn_time = current_time
            self.total_spawned += 1
            
            # Calcular tiempo hasta el próximo spawn
            next_cooldown = max(self.min_spawn_cooldown, 
                              self.base_spawn_cooldown - ((self.total_spawned) * self.spawn_acceleration))
            
            print(f"🐛 Gusano {self.total_spawned}/{self.max_worms} apareció en ({spawn_x}, {spawn_y}) - Próximo en {next_cooldown/1000:.1f}s")
            return
        
        print("⚠️ No se pudo encontrar posición válida para spawn de gusano")
    
    def update(self, players, collision_manager=None):
        """Actualiza todos los gusanos y maneja spawn gradual"""
        # Intentar generar nuevos gusanos gradualmente
        self.spawn_worm(players, collision_manager)
        
        # Actualizar gusanos existentes
        for worm in self.worms[:]:
            if worm.alive:
                worm.update(players)
            else:
                self.worms.remove(worm)
    
    def draw(self, screen, camera_x, camera_y):
        """Dibuja todos los gusanos"""
        for worm in self.worms:
            worm.draw(screen, camera_x, camera_y)
    
    def get_worms(self):
        """Obtiene lista de gusanos vivos"""
        return [worm for worm in self.worms if worm.alive]