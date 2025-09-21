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
        
        # Configuración
        self.current_state = self.STATE_FOLLOW
        self.follow_distance = 150  # Distancia a la que sigue al personaje
        self.attack_range = 120     # Distancia a la que ataca enemigos
        self.low_health_threshold = 30  # % de vida considerado bajo
        self.attack_cooldown = 0
        self.attack_cooldown_max = 45  # Frames entre ataques
        self.damage_reduction = 0.6  # Recibe 60% del daño normal
        
        # Variables para la IA
        self.current_target = None
        self.time_since_last_state_change = 0
        self.revival_timer = 0
        self.revival_time = 600  # 10 segundos a 60 FPS
        self.is_being_revived = False
        
        # Variables de movimiento
        self.last_x = character.x
        self.last_y = character.y
        self.movement_timer = 0
        
        print(f"🤖 IA de {self.character.name} inicializada")
    
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
        
        # Incrementar contadores
        self.time_since_last_state_change += 1
        
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
                print(f"⚠️ {self.character.name} tiene poca vida ({health_percent:.1f}%), retrocediendo!")
                self.current_state = self.STATE_RETREAT
                self.time_since_last_state_change = 0
        elif self.current_target and self.current_target.alive:
            target_distance = self.distance_to(self.current_target.x, self.current_target.y)
            if target_distance <= self.attack_range:
                if self.current_state != self.STATE_ATTACK:
                    print(f"🗡️ {self.character.name} detectó enemigo y está atacando!")
                    self.current_state = self.STATE_ATTACK
                    self.time_since_last_state_change = 0
            else:
                if self.current_state != self.STATE_FOLLOW:
                    print(f"👣 {self.character.name} siguiendo al jugador")
                    self.current_state = self.STATE_FOLLOW
                    self.time_since_last_state_change = 0
        else:
            if self.current_state != self.STATE_FOLLOW:
                self.current_state = self.STATE_FOLLOW
                self.time_since_last_state_change = 0
        
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
        """Busca el enemigo más cercano"""
        nearest_enemy = None
        min_distance = float('inf')
        
        for enemy in enemies:
            if hasattr(enemy, 'alive') and enemy.alive:
                dist = self.distance_to(enemy.x, enemy.y)
                if dist < min_distance and dist <= self.attack_range * 2:  # Rango extendido para detección
                    min_distance = dist
                    nearest_enemy = enemy
        
        self.current_target = nearest_enemy
        return nearest_enemy
    
    def follow_behavior(self):
        """Comportamiento de seguir al jugador"""
        dist_to_target = self.distance_to(self.target_character.x, self.target_character.y)
        
        if dist_to_target > self.follow_distance:
            # Moverse hacia el jugador
            self.move_towards(self.target_character.x, self.target_character.y)
        else:
            # Detenerse si está cerca
            pass
    
    def attack_behavior(self):
        """Comportamiento de ataque"""
        if not self.current_target or not hasattr(self.current_target, 'alive') or not self.current_target.alive:
            self.current_state = self.STATE_FOLLOW
            return
            
        # Distancia al enemigo
        dist_to_enemy = self.distance_to(self.current_target.x, self.current_target.y)
        
        # Si el enemigo está fuera de rango, acercarse
        if dist_to_enemy > self.attack_range:
            self.move_towards(self.current_target.x, self.current_target.y)
        else:
            # Si está en rango, atacar
            if self.attack_cooldown <= 0:
                # Actualizar dirección hacia el enemigo
                self.update_direction_to_target(self.current_target.x, self.current_target.y)
                
                # Simular ataque básico
                self.perform_attack()
                self.attack_cooldown = self.attack_cooldown_max
    
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
        
        # Verificar si la salud ha mejorado
        health_percent = (self.character.health / self.character.max_health) * 100
        if health_percent > self.low_health_threshold + 15:  # Histéresis
            self.current_state = self.STATE_FOLLOW
            print(f"✅ {self.character.name} se ha recuperado y vuelve al combate")
    
    def perform_attack(self):
        """Realiza un ataque contra el enemigo actual"""
        if self.current_target and hasattr(self.current_target, 'alive') and self.current_target.alive:
            # Simular daño al enemigo
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
        """Mueve al personaje hacia una posición objetivo"""
        # Calcular dirección
        dx = target_x - self.character.x
        dy = target_y - self.character.y
        
        # Normalizar para movimiento consistente
        distance = max(1, math.sqrt(dx*dx + dy*dy))
        dx /= distance
        dy /= distance
        
        # Aplicar movimiento con velocidad del personaje
        speed = getattr(self.character, 'speed', 3)
        self.character.x += dx * speed
        self.character.y += dy * speed
        
        # Actualizar dirección para animación
        self.update_direction_to_target(target_x, target_y)
    
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
    
    def get_status_info(self):
        """Retorna información del estado actual para debugging"""
        return {
            'state': self.current_state,
            'health_percent': (self.character.health / self.character.max_health) * 100,
            'is_being_revived': self.is_being_revived,
            'revival_progress': self.revival_timer / self.revival_time if self.is_being_revived else 0,
            'has_target': self.current_target is not None,
            'attack_cooldown': self.attack_cooldown
        }