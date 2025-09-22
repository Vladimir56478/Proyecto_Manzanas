import pygame
import math
import random

class CharacterAI:
    def __init__(self, character, target_character):
        self.character = character
        self.target_character = target_character
        
        # Estados de la IA
        self.STATE_FOLLOW = "follow"
        self.STATE_ATTACK = "attack"
        self.STATE_RETREAT = "retreat"
        self.STATE_DOWNED = "downed"
        
        # Configuración mejorada
        self.current_state = self.STATE_FOLLOW
        self.follow_distance = 120  # Reducido para seguir más cerca
        self.attack_range = 100     # Rango de ataque
        self.detection_range = 180  # Rango de detección de enemigos (nuevo)
        self.low_health_threshold = 25  # % de vida considerado bajo
        self.attack_cooldown = 0
        self.attack_cooldown_max = 30  # Reducido para ataques más frecuentes
        self.damage_reduction = 0.6  # Recibe 60% del daño normal
        
        # Variables para la IA
        self.current_target = None
        self.time_since_last_state_change = 0
        self.revival_timer = 0
        self.revival_time = 600  # 10 segundos a 60 FPS
        self.is_being_revived = False
        
        # Variables de movimiento y animación mejoradas
        self.last_x = character.x
        self.last_y = character.y
        self.movement_timer = 0
        self.is_moving = False
        self.movement_direction = None
        self.is_attacking = False
        self.attack_timer = 0
        self.stop_timer = 0  # Para controlar cuándo detenerse
        
        print(f"🤖 IA de {self.character.name} inicializada con configuración agresiva")
    
    def update(self, enemies):
        """Actualiza la lógica de la IA"""
        # No hacer nada si está derribado y no está siendo revivido
        if self.character.health <= 0 and not self.is_being_revived:
            self.current_state = self.STATE_DOWNED
            return
            
        # Manejar la recuperación
        if self.is_being_revived:
            self.revival_timer += 1
            if self.revival_timer >= self.revival_time:
                self.character.health = self.character.max_health
                self.is_being_revived = False
                self.revival_timer = 0
                self.current_state = self.STATE_FOLLOW
                print(f"✨ {self.character.name} ha sido revivido con {self.character.health} HP!")
            return
        
        # Incrementar contadores y actualizar timers
        self.time_since_last_state_change += 1
        self.update_timers()
        
        # Resetear indicador de movimiento al inicio
        self.is_moving = False
        
        # Enfriar el ataque
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # Calcular la distancia al personaje objetivo
        dist_to_target = self.distance_to(self.target_character.x, self.target_character.y)
        
        # Determinar estado según la salud
        health_percent = (self.character.health / self.character.max_health) * 100
        
        # Buscar enemigos cercanos
        self.find_nearest_enemy(enemies)
        
        # Cambiar estado según condiciones
        if health_percent <= self.low_health_threshold:
            if self.current_state != self.STATE_RETREAT:
                self.current_state = self.STATE_RETREAT
                self.time_since_last_state_change = 0
                self.is_attacking = False
        elif self.current_target and self.current_target.alive:
            target_distance = self.distance_to(self.current_target.x, self.current_target.y)
            if target_distance <= self.attack_range * 1.5:  # Rango ampliado para detección
                if self.current_state != self.STATE_ATTACK:
                    self.current_state = self.STATE_ATTACK
                    self.time_since_last_state_change = 0
            else:
                if self.current_state != self.STATE_FOLLOW:
                    self.current_state = self.STATE_FOLLOW
                    self.time_since_last_state_change = 0
                    self.is_attacking = False
        else:
            if self.current_state != self.STATE_FOLLOW:
                self.current_state = self.STATE_FOLLOW
                self.time_since_last_state_change = 0
                self.is_attacking = False
        
        # Ejecutar comportamiento según estado actual
        if self.current_state == self.STATE_FOLLOW:
            self.follow_behavior()
        elif self.current_state == self.STATE_ATTACK:
            self.attack_behavior()
        elif self.current_state == self.STATE_RETREAT:
            self.retreat_behavior()
        
        # Actualizar posición previa
        self.last_x = self.character.x
        self.last_y = self.character.y
    
    def find_nearest_enemy(self, enemies):
        """Busca el enemigo más cercano con rango de detección ampliado"""
        nearest_enemy = None
        min_distance = float('inf')
        
        for enemy in enemies:
            if hasattr(enemy, 'alive') and enemy.alive:
                dist = self.distance_to(enemy.x, enemy.y)
                if dist < min_distance and dist <= self.detection_range:
                    min_distance = dist
                    nearest_enemy = enemy
        
        # Solo cambiar objetivo si encontró uno más cercano o no tenía objetivo
        if nearest_enemy or not self.current_target:
            self.current_target = nearest_enemy
        
        return nearest_enemy
    
    def follow_behavior(self):
        """Comportamiento de seguir al jugador con animaciones realistas"""
        dist_to_target = self.distance_to(self.target_character.x, self.target_character.y)
        
        if dist_to_target > self.follow_distance:
            # Moverse hacia el jugador
            self.move_towards(self.target_character.x, self.target_character.y)
        else:
            # Detenerse si está cerca - animación idle
            self.is_moving = False
            self.movement_direction = None
    
    def attack_behavior(self):
        """Comportamiento de ataque mejorado - no puede moverse y atacar a la vez"""
        if not self.current_target or not hasattr(self.current_target, 'alive') or not self.current_target.alive:
            self.current_state = self.STATE_FOLLOW
            self.is_attacking = False
            return
            
        # Distancia al enemigo
        dist_to_enemy = self.distance_to(self.current_target.x, self.current_target.y)
        
        # Si el enemigo está muy lejos, acercarse primero
        if dist_to_enemy > self.attack_range * 1.2:
            self.current_state = self.STATE_FOLLOW
            self.is_attacking = False
            return
        
        # Si está fuera del rango óptimo de ataque, moverse para posicionarse
        if dist_to_enemy > self.attack_range * 0.8:
            print(f"� {self.character.name} posicionándose para atacar (distancia: {dist_to_enemy:.1f})")
            self.move_towards(self.current_target.x, self.current_target.y)
            self.is_attacking = False
        else:
            # DETENERSE para atacar - no puede moverse y atacar a la vez
            self.is_moving = False
            self.movement_direction = None
            
            if self.attack_cooldown <= 0:
                print(f"⚔️ {self.character.name} se detiene y ataca")
                self.is_attacking = True
                self.attack_timer = 30  # Duración de la animación de ataque
                self.perform_attack()
                self.attack_cooldown = self.attack_cooldown_max
            else:
                # Mantener posición y orientación hacia el enemigo mientras espera cooldown
                direction = self.calculate_movement_direction(self.current_target.x, self.current_target.y)
                if hasattr(self.character, 'current_direction'):
                    self.character.current_direction = direction
                self.is_attacking = False
        
        # Si la salud está baja durante combate, considerar retirarse
        health_percent = (self.character.health / self.character.max_health) * 100
        if health_percent <= self.low_health_threshold:
            print(f"⚠️ {self.character.name} tiene poca vida durante combate, retirándose")
            self.current_state = self.STATE_RETREAT
            self.is_attacking = False
    
    def retreat_behavior(self):
        """Comportamiento de retirada cuando tiene poca vida"""
        dist_to_target = self.distance_to(self.target_character.x, self.target_character.y)
        
        # Siempre mantenerse cerca del jugador
        if dist_to_target > self.follow_distance * 0.7:
            self.move_towards(self.target_character.x, self.target_character.y)
        else:
            # Si hay un enemigo cerca, alejarse
            if self.current_target and hasattr(self.current_target, 'alive') and self.current_target.alive:
                enemy_dist = self.distance_to(self.current_target.x, self.current_target.y)
                
                if enemy_dist < self.attack_range * 1.5:
                    # Calcular vector de escape
                    dx = self.character.x - self.current_target.x
                    dy = self.character.y - self.current_target.y
                    
                    # Normalizar
                    length = max(1, math.sqrt(dx*dx + dy*dy))
                    dx /= length
                    dy /= length
                    
                    # Moverse alejándose del enemigo
                    escape_x = self.character.x + dx * 8
                    escape_y = self.character.y + dy * 8
                    
                    self.move_towards(escape_x, escape_y)
                    return
            
            # Si no hay amenaza cerca, quedarse quieto
            self.is_moving = False
            self.movement_direction = None
        
        # Verificar si la salud ha mejorado
        health_percent = (self.character.health / self.character.max_health) * 100
        if health_percent > self.low_health_threshold + 15:  # Histéresis
            self.current_state = self.STATE_FOLLOW
            self.is_attacking = False
    
    def perform_attack(self):
        """Realiza un ataque con animación contra el enemigo actual"""
        if self.current_target and hasattr(self.current_target, 'alive') and self.current_target.alive:
            # Calcular dirección hacia el enemigo
            dx = self.current_target.x - self.character.x
            dy = self.current_target.y - self.character.y
            
            # Determinar dirección de ataque base
            if abs(dx) > abs(dy):
                base_attack_direction = "right" if dx > 0 else "left"
            else:
                base_attack_direction = "down" if dy > 0 else "up"
            
            # INVERSIÓN ESPECÍFICA PARA JUAN en ataques IA
            if hasattr(self.character, 'name') and self.character.name == "Juan":
                # Invertir direcciones de ataque para Juan IA
                direction_map = {
                    "up": "down",
                    "down": "up", 
                    "left": "right",
                    "right": "left"
                }
                attack_direction = direction_map.get(base_attack_direction, base_attack_direction)
            else:
                # Adán usa direcciones naturales
                attack_direction = base_attack_direction
            
            # Iniciar animación de ataque real
            if hasattr(self.character, 'start_ai_attack'):
                attack_started = self.character.start_ai_attack(attack_direction)
                if attack_started:
                    print(f"🎨 {self.character.name} (IA) iniciando animación de ataque hacia {attack_direction}")
            
            # Simular daño usando el sistema de ataques real
            if hasattr(self.character, 'attacks'):
                # Crear lista temporal con el enemigo objetivo
                enemies_list = [self.current_target]
                
                # Usar el sistema de ataques del personaje
                if hasattr(self.character.attacks, 'prepare_combo_attack'):
                    # Para Juan - sistema de combos
                    self.character.attacks.attack_direction = attack_direction
                    hit_result = self.character.attacks.prepare_combo_attack(enemies_list)
                    if hit_result:
                        # Aplicar daño inmediatamente para IA
                        self.character.attacks.apply_pending_damage()
                        print(f"⚔️ {self.character.name} (IA) ejecutó combo attack")
                        
                elif hasattr(self.character.attacks, 'prepare_melee_attack'):
                    # Para Adán - ataque cuerpo a cuerpo
                    self.character.attacks.attack_direction = attack_direction
                    hit_result = self.character.attacks.prepare_melee_attack(enemies_list)
                    if hit_result:
                        # Aplicar daño inmediatamente para IA
                        self.character.attacks.apply_pending_damage()
                        print(f"🔥 {self.character.name} (IA) ejecutó melee attack")
            else:
                # Fallback: daño simple si no hay sistema de ataques
                damage = random.randint(15, 25)
                if hasattr(self.current_target, 'health'):
                    self.current_target.health -= damage
                    if self.current_target.health <= 0:
                        self.current_target.alive = False
                        print(f"💀 {self.character.name} derrotó a un enemigo!")
                    else:
                        print(f"⚔️ {self.character.name} atacó por {damage} de daño")
    
    def start_revival(self):
        """Inicia el proceso de revivir al personaje"""
        if self.character.health <= 0 and not self.is_being_revived:
            self.is_being_revived = True
            self.revival_timer = 0
            print(f"🔄 Comenzando a revivir a {self.character.name}...")
            return True
        return False
    
    def take_damage(self, damage):
        """Aplica daño reducido al personaje con IA"""
        actual_damage = int(damage * self.damage_reduction)
        self.character.health = max(0, self.character.health - actual_damage)
        
        print(f"💢 {self.character.name} (IA) recibió {actual_damage} de daño (reducido de {damage})")
        
        if self.character.health <= 0:
            print(f"💀 {self.character.name} ha sido derribado!")
            self.current_state = self.STATE_DOWNED
        
        return actual_damage
    
    def distance_to(self, x, y):
        """Calcula la distancia a una posición"""
        dx = self.character.x - x
        dy = self.character.y - y
        return math.sqrt(dx*dx + dy*dy)
    
    def move_towards(self, target_x, target_y):
        """Mueve al personaje hacia una posición objetivo en líneas rectas como el jugador"""
        # Calcular diferencias
        dx = target_x - self.character.x
        dy = target_y - self.character.y
        
        # Verificar si realmente necesita moverse
        distance = math.sqrt(dx*dx + dy*dy)
        if distance < 10:  # Si está muy cerca, no moverse
            self.movement_direction = None
            self.is_moving = False
            return
        
        # Aplicar movimiento con velocidad del personaje
        speed = getattr(self.character, 'speed', 3)
        
        # NUEVO: Movimiento como jugador - primero X, luego Y
        # Priorizar movimiento horizontal si la diferencia es significativa
        if abs(dx) > 15:  # Umbral para movimiento horizontal
            # Mover solo en X
            if dx > 0:
                self.character.x += speed
                self.movement_direction = "right"
            else:
                self.character.x -= speed
                self.movement_direction = "left"
        elif abs(dy) > 15:  # Luego mover en Y
            # Mover solo en Y
            if dy > 0:
                self.character.y += speed
                self.movement_direction = "down"
            else:
                self.character.y -= speed
                self.movement_direction = "up"
        else:
            # Ya está cerca, detenerse
            self.movement_direction = None
            self.is_moving = False
            return
        
        # Determinar dirección de movimiento
        self.movement_direction = self.calculate_movement_direction(target_x, target_y)
        
        # Marcar que se está moviendo para las animaciones
        self.is_moving = True
    
    def calculate_movement_direction(self, target_x, target_y):
        """Calcula la dirección correcta de movimiento con inversión para Juan"""
        dx = target_x - self.character.x
        dy = target_y - self.character.y
        
        # Determinar dirección predominante
        if abs(dx) > abs(dy):
            base_direction = "right" if dx > 0 else "left"
        else:
            base_direction = "down" if dy > 0 else "up"
        
        # INVERSIÓN ESPECÍFICA PARA JUAN en modo IA
        if hasattr(self.character, 'name') and self.character.name == "Juan":
            # Invertir direcciones para Juan IA para que mire correctamente
            direction_map = {
                "up": "down",
                "down": "up", 
                "left": "right",
                "right": "left"
            }
            return direction_map.get(base_direction, base_direction)
        else:
            # Adán y otros personajes usan direcciones naturales
            return base_direction
    
    def update_direction_to_target(self, target_x, target_y):
        """Actualiza la dirección del personaje según el objetivo"""
        dx = target_x - self.character.x
        dy = target_y - self.character.y
        
        # Determinar dirección predominante
        if abs(dx) > abs(dy):
            direction = "right" if dx > 0 else "left"
        else:
            direction = "down" if dy > 0 else "up"
            
        # Aplicar dirección al personaje
        if hasattr(self.character, 'current_direction'):
            self.character.current_direction = direction
        elif hasattr(self.character, 'direction'):
            self.character.direction = direction
    
    def get_animation_state(self):
        """Devuelve el estado actual de animación para el personaje"""
        # Si está atacando, no mostrar movimiento
        if self.is_attacking:
            return None  # Mantendrá la animación actual
        
        # Si se está moviendo, devolver dirección
        if self.is_moving and self.movement_direction:
            return self.movement_direction
        
        # Si no se mueve, no animar (frame 0)
        return None
    
    def update_timers(self):
        """Actualiza los timers internos"""
        # Timer de ataque
        if self.attack_timer > 0:
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.is_attacking = False
        
        # Timer de parada
        if self.stop_timer > 0:
            self.stop_timer -= 1
        
        # Timer de movimiento - resetear después de un tiempo sin moverse
        if not self.is_moving:
            self.movement_timer += 1
            if self.movement_timer > 10:  # Si no se ha movido en 10 frames
                self.movement_direction = None
        else:
            self.movement_timer = 0
    
    def get_status_info(self):
        """Retorna información del estado actual para debugging"""
        return {
            'state': self.current_state,
            'health_percent': (self.character.health / self.character.max_health) * 100,
            'is_being_revived': self.is_being_revived,
            'revival_progress': self.revival_timer / self.revival_time if self.is_being_revived else 0,
            'has_target': self.current_target is not None,
            'attack_cooldown': self.attack_cooldown,
            'is_moving': self.is_moving,
            'movement_direction': self.movement_direction,
            'is_attacking': self.is_attacking
        }