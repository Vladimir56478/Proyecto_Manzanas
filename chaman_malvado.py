import pygame
import random
import math
from chaman_character_animation import ChamanCharacter
from chaman_attacks import ChamanAttack
from worm_enemy import WormEnemy


class ChamanMalvado:
    def __init__(self, x, y):
        self.character = ChamanCharacter(x, y)
        self.attack_system = ChamanAttack(self.character)
        
        self.x = x
        self.y = y
        self.max_health = self.character.max_health
        self.health = self.character.health
        self.damage = self.character.damage
        self.speed = self.character.speed
        self.name = self.character.name
        
        self.state = "idle"
        self.target = None
        self.detection_range = 1000  # Aumentado de 700 para mayor agresividad
        self.attack_range = 650      # Aumentado de 500 para mayor alcance de ataque
        self.summon_range = 1000     # Aumentado para mayor rango de invocación
        
        self.last_summon_time = 0
        self.summon_cooldown = 15000
        self.state_change_timer = 0
        self.ai_decision_interval = 1000
        
        self.summoned_worms = []
        self.max_summoned_worms = 3
        
        self.attack_pattern = 0
        self.consecutive_attacks = 0
        self.max_consecutive_attacks = 3
        
        print("🧙 Chamán Malvado inicializado")
    
    def update(self, targets):
        current_time = pygame.time.get_ticks()
        
        self.x = self.character.x
        self.y = self.character.y
        self.health = self.character.health
        
        self.attack_system.update(targets)
        
        if current_time - self.state_change_timer >= self.ai_decision_interval:
            self.update_ai_behavior(targets)
            self.state_change_timer = current_time
        
        self.update_movement_by_state(targets)
        
        ai_direction = self.get_movement_direction(targets)
        self.character.update(ai_controlled=True, ai_direction=ai_direction)
        
        self.clean_dead_summons()
    
    def update_ai_behavior(self, targets):
        if not targets:
            self.state = "idle"
            return
        
        closest_target = self.find_closest_target(targets)
        self.target = closest_target
        
        if not closest_target:
            self.state = "idle"
            return
        
        distance_to_target = self.get_distance_to_target(closest_target)
        current_time = pygame.time.get_ticks()
        
        if distance_to_target <= self.attack_range:
            if self.attack_system.can_attack_basic():
                self.state = "attacking_basic"
                self.consecutive_attacks += 1
            else:
                self.state = "moving"
        elif distance_to_target <= self.detection_range:
            self.state = "moving"
        else:
            self.state = "idle"
    
    def update_movement_by_state(self, targets):
        if self.state == "attacking_basic":
            direction = self.get_attack_direction(self.target)
            self.attack_system.start_attack(direction, targets)
        elif self.state == "attacking_special":
            self.attack_system.special_attack_area(targets)
    
    def get_movement_direction(self, targets):
        if self.state != "moving" or not self.target:
            return None
        
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        
        if abs(dx) > abs(dy):
            return "right" if dx > 0 else "left"
        else:
            return "down" if dy > 0 else "up"
    
    def get_attack_direction(self, target):
        if not target:
            return "down"
        
        dx = target.x - self.x
        dy = target.y - self.y
        
        if abs(dx) > abs(dy):
            return "right" if dx > 0 else "left"
        else:
            return "down" if dy > 0 else "up"
    
    def find_closest_target(self, targets):
        closest = None
        min_distance = float('inf')
        
        for target in targets:
            if hasattr(target, 'health') and target.health > 0:
                distance = self.get_distance_to_target(target)
                if distance < min_distance:
                    min_distance = distance
                    closest = target
        
        return closest
    
    def get_distance_to_target(self, target):
        return math.sqrt((target.x - self.x)**2 + (target.y - self.y)**2)
    
    def clean_dead_summons(self):
        self.summoned_worms = [worm for worm in self.summoned_worms if worm.alive]
    
    def take_damage(self, damage):
        return self.character.take_damage(damage)
    
    def is_alive(self):
        return self.character.is_alive()
    
    def get_rect(self):
        return self.character.get_rect()
    
    def check_projectile_collisions(self, targets):
        """Verifica colisiones de proyectiles con objetivos"""
        # El sistema de ataques ya maneja las colisiones en update_projectiles
        # Este método existe para compatibilidad con nivel_2.py
        pass
    
    def draw_health_bar(self, screen, camera_x, camera_y):
        """Dibuja la barra de salud del chamán"""
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        self.character.draw_health_bar(screen, screen_x, screen_y)
    
    def draw(self, screen, camera_x, camera_y):
        # Usar el método de dibujo del personaje con información de ataques para consistencia de tamaño
        self.character.draw(screen, camera_x, camera_y, self.attack_system)
        
        # Dibujar efectos de ataque por separado (proyectiles, efectos mágicos)
        self.attack_system.draw(screen, camera_x, camera_y)
        
        # Dibujar gusanos invocados
        for worm in self.summoned_worms:
            worm.draw(screen, camera_x, camera_y)


def create_chaman_malvado(x, y):
    return ChamanMalvado(x, y)