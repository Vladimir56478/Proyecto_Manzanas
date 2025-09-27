#!/usr/bin/env python3
"""
CHAMAN MALVADO - SISTEMA DE ATAQUES
Sistema de combate y hechi            try:
                while True:
                    frame_rgba = pil_gif.convert('RGBA')  # RGBA para transparencias
                    frame_rgba = frame_rgba.resize((128, 128), Image.LANCZOS)
                    
                    # Convertir fondo blanco a transparente
                    pixel_data = frame_rgba.load()
                    for y in range(frame_rgba.height):
                        for x in range(frame_rgba.width):
                            r, g, b, a = pixel_data[x, y]
                            # Si el pixel es blanco o casi blanco, hacerlo transparente
                            if r > 240 and g > 240 and b > 240:
                                pixel_data[x, y] = (r, g, b, 0)  # Transparente
                    
                    frame_data = frame_rgba.tobytes()
                    pygame_surface = pygame.image.fromstring(frame_data, (128, 128), 'RGBA')
                    pygame_surface = pygame_surface.convert_alpha()
                    
                    frames.append(pygame_surface)
                    frame_count += 1
                    
                    pil_gif.seek(pil_gif.tell() + 1)efe final
"""

import pygame
import math
import random
import requests
from PIL import Image
from io import BytesIO


class ChamanAttack:
    """Clase para manejar todos los ataques del Chamán Malvado"""
    
    def __init__(self, character):
        """Inicializa el sistema de ataques del chamán"""
        self.character = character
        
        # Configuración de ataques
        self.basic_attack_cooldown = 1200  # 1.2 segundos entre ataques básicos
        self.special_attack_cooldown = 3000  # 3 segundos entre ataques especiales
        self.last_basic_attack = 0
        self.last_special_attack = 0
        
        # Propiedades de daño
        self.basic_damage = 25
        self.special_damage = 45
        self.magic_range = 350  # Mayor alcance de hechizos
        
        # URLs de animaciones de ataque desde GitHub
        self.attack_urls = {
            "right": "https://github.com/user-attachments/assets/bd3f405c-b168-4894-8955-93855cac3d84",
            "up": "https://github.com/user-attachments/assets/baf8b14a-fb99-42ad-880b-850c66b8d288",
            "down": "https://github.com/user-attachments/assets/903bf678-94d2-4dca-a74c-bef232c6ca32", 
            "left": "https://github.com/user-attachments/assets/ef3d6aa1-563d-401b-b7ab-fc87b03fe13c"
        }
        
        # Frames de animación de ataques
        self.attack_frames = {"up": [], "down": [], "left": [], "right": []}
        self.attack_animation_frame = 0
        self.attack_animation_speed = 0.15
        self.is_attacking = False
        self.attack_direction = "down"
        self.attack_start_time = 0
        self.attack_duration = 800  # Duración de animación de ataque
        
        # Proyectiles mágicos
        self.magic_projectiles = []
        self.projectile_speed = 4.0
        
        # Efectos especiales
        self.magic_effects = []
        self.summon_effects = []
        
        # Cargar animaciones
        self.load_attack_animations()
        
        print("🔥 Sistema de ataques del Chamán inicializado")
    
    def load_attack_animations(self):
        """Carga todas las animaciones de ataque"""
        print("⚔️ Cargando animaciones de ataque del Chamán...")
        
        for direction, url in self.attack_urls.items():
            try:
                frames = self.load_gif_from_url(url)
                if frames:
                    self.attack_frames[direction] = frames
                    print(f"✅ Ataque {direction}: {len(frames)} frames")
                else:
                    self.create_fallback_attack_frame(direction)
            except Exception as e:
                print(f"❌ Error cargando ataque {direction}: {e}")
                self.create_fallback_attack_frame(direction)
        
        print("⚔️ Animaciones de ataque cargadas")
    
    def load_gif_from_url(self, url):
        """Carga un GIF de ataque desde GitHub"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            gif_data = BytesIO(response.content)
            pil_gif = Image.open(gif_data)
            
            frames = []
            frame_count = 0
            
            try:
                while True:
                    frame_rgba = pil_gif.convert('RGBA')  # RGBA para transparencias
                    frame_rgba = frame_rgba.resize((128, 128), Image.LANCZOS)
                    
                    # Convertir fondo blanco a transparente
                    pixel_data = frame_rgba.load()
                    for y in range(frame_rgba.height):
                        for x in range(frame_rgba.width):
                            r, g, b, a = pixel_data[x, y]
                            # Si el pixel es blanco o casi blanco, hacerlo transparente
                            if r > 240 and g > 240 and b > 240:
                                pixel_data[x, y] = (r, g, b, 0)  # Transparente
                    
                    frame_data = frame_rgba.tobytes()
                    pygame_surface = pygame.image.fromstring(frame_data, (128, 128), 'RGBA')
                    pygame_surface = pygame_surface.convert_alpha()
                    
                    frames.append(pygame_surface)
                    frame_count += 1
                    
                    pil_gif.seek(pil_gif.tell() + 1)
                    
            except EOFError:
                pass
            
            return frames
            
        except Exception as e:
            print(f"❌ Error procesando GIF de ataque: {e}")
            return []
    
    def create_fallback_attack_frame(self, direction):
        """Crea frame de respaldo para ataques"""
        surface = pygame.Surface((128, 128), pygame.SRCALPHA)
        
        # Chamán atacando (más dramático)
        pygame.draw.circle(surface, (100, 30, 100), (64, 64), 55)  # Cuerpo expandido
        pygame.draw.circle(surface, (150, 60, 150), (64, 45), 30)  # Cabeza brillante
        
        # Ojos brillando de poder
        pygame.draw.circle(surface, (255, 255, 0), (58, 40), 6)
        pygame.draw.circle(surface, (255, 255, 0), (70, 40), 6)
        
        # Energía mágica
        for i in range(5):
            angle = (i * 72) * math.pi / 180
            x = 64 + int(40 * math.cos(angle))
            y = 64 + int(40 * math.sin(angle))
            pygame.draw.circle(surface, (255, 100, 255), (x, y), 8)
        
        self.attack_frames[direction] = [surface]
        print(f"🎨 Frame de ataque de respaldo creado para {direction}")
    
    def can_attack_basic(self):
        """Verifica si puede hacer ataque básico"""
        current_time = pygame.time.get_ticks()
        return current_time - self.last_basic_attack >= self.basic_attack_cooldown
    
    def can_attack_special(self):
        """Verifica si puede hacer ataque especial"""
        current_time = pygame.time.get_ticks()
        return current_time - self.last_special_attack >= self.special_attack_cooldown
    
    def start_attack(self, direction, targets):
        """Inicia un ataque en la dirección especificada"""
        if not self.can_attack_basic():
            return False
        
        current_time = pygame.time.get_ticks()
        self.is_attacking = True
        self.attack_direction = direction
        self.attack_start_time = current_time
        self.attack_animation_frame = 0
        self.last_basic_attack = current_time
        
        # Lanzar proyectil mágico
        self.launch_magic_projectile(direction, targets)
        
        print(f"🧙 Chamán ataca hacia {direction}")
        return True
    
    def launch_magic_projectile(self, direction, targets):
        """Lanza 3 proyectiles mágicos dispersados"""
        # Calcular posición inicial del proyectil
        start_x = self.character.x + self.character.width // 2
        start_y = self.character.y + self.character.height // 2
        
        # Obtener ángulo base según dirección
        import math
        base_angle = 0
        if direction == "right":
            base_angle = 0  # 0 grados
        elif direction == "down":
            base_angle = 90  # 90 grados
        elif direction == "left":
            base_angle = 180  # 180 grados
        elif direction == "up":
            base_angle = 270  # 270 grados
        
        # Crear 3 proyectiles con mayor dispersión angular
        angles = [
            base_angle,      # Proyectil central (dirección exacta)
            base_angle - 60, # Proyectil izquierdo (-60°)
            base_angle + 60  # Proyectil derecho (+60°)
        ]
        
        for i, angle in enumerate(angles):
            # Convertir ángulo a radianes
            angle_rad = math.radians(angle)
            
            # Calcular velocidades usando trigonometría
            velocity_x = self.projectile_speed * math.cos(angle_rad)
            velocity_y = self.projectile_speed * math.sin(angle_rad)
            
            # Crear proyectil con dispersión angular
            projectile = {
                'x': start_x,
                'y': start_y,
                'velocity_x': velocity_x,
                'velocity_y': velocity_y,
                'damage': self.basic_damage,
                'max_range': self.magic_range,
                'traveled': 0,
                'active': True,
                'size': 12,  # Más pequeños para mejor balance
                'angle': angle  # Guardar ángulo para efectos visuales
            }
            
            self.magic_projectiles.append(projectile)
        
        print(f"🔮 3 Proyectiles mágicos dispersados lanzados hacia {direction} (ángulos: {angles})")
    
    def special_attack_area(self, targets):
        """Ataque especial de área"""
        if not self.can_attack_special():
            return False
        
        current_time = pygame.time.get_ticks()
        self.last_special_attack = current_time
        
        # Crear múltiples proyectiles en todas las direcciones
        directions = ["up", "down", "left", "right", "up-left", "up-right", "down-left", "down-right"]
        
        for i, direction in enumerate(directions):
            angle = (i * 45) * math.pi / 180
            velocity_x = self.projectile_speed * math.cos(angle)
            velocity_y = self.projectile_speed * math.sin(angle)
            
            projectile = {
                'x': self.character.x + self.character.width // 2,
                'y': self.character.y + self.character.height // 2,
                'velocity_x': velocity_x,
                'velocity_y': velocity_y,
                'damage': self.special_damage,
                'max_range': self.magic_range * 1.5,
                'traveled': 0,
                'active': True,
                'size': 20,
                'special': True
            }
            
            self.magic_projectiles.append(projectile)
        
        # Efecto visual especial
        self.create_area_effect()
        
        print(f"💥 Chamán usa ataque especial de área - {len(directions)} proyectiles")
        return True
    
    def create_area_effect(self):
        """Crea efecto visual de área"""
        effect = {
            'x': self.character.x + self.character.width // 2,
            'y': self.character.y + self.character.height // 2,
            'radius': 0,
            'max_radius': 150,
            'alpha': 255,
            'duration': 1000,  # 1 segundo
            'start_time': pygame.time.get_ticks()
        }
        
        self.magic_effects.append(effect)
    
    def update(self, targets):
        """Actualiza el sistema de ataques"""
        current_time = pygame.time.get_ticks()
        
        # Actualizar animación de ataque
        if self.is_attacking:
            elapsed = current_time - self.attack_start_time
            if elapsed >= self.attack_duration:
                self.is_attacking = False
            else:
                # Actualizar frame de animación
                frame_progress = elapsed / self.attack_duration
                frames = self.attack_frames.get(self.attack_direction, [])
                if frames:
                    self.attack_animation_frame = int(frame_progress * len(frames)) % len(frames)
        
        # Actualizar proyectiles
        self.update_projectiles(targets)
        
        # Actualizar efectos mágicos
        self.update_magic_effects()
    
    def update_projectiles(self, targets):
        """Actualiza todos los proyectiles mágicos"""
        for projectile in self.magic_projectiles[:]:
            if not projectile['active']:
                continue
            
            # Mover proyectil
            old_x, old_y = projectile['x'], projectile['y']
            projectile['x'] += projectile['velocity_x']
            projectile['y'] += projectile['velocity_y']
            
            # Calcular distancia recorrida
            distance = math.sqrt((projectile['x'] - old_x)**2 + (projectile['y'] - old_y)**2)
            projectile['traveled'] += distance
            
            # Verificar si excedió el rango
            if projectile['traveled'] >= projectile['max_range']:
                projectile['active'] = False
                self.magic_projectiles.remove(projectile)
                continue
            
            # Verificar colisiones con objetivos
            projectile_rect = pygame.Rect(projectile['x'] - projectile['size']//2,
                                        projectile['y'] - projectile['size']//2,
                                        projectile['size'], projectile['size'])
            
            for target in targets:
                if hasattr(target, 'health') and target.health > 0:
                    target_rect = pygame.Rect(target.x, target.y, 64, 64)  # Asumir tamaño estándar
                    
                    if projectile_rect.colliderect(target_rect):
                        # Aplicar daño
                        target.take_damage(projectile['damage'])
                        
                        # Crear efecto de impacto
                        self.create_impact_effect(projectile['x'], projectile['y'])
                        
                        # Remover proyectil
                        projectile['active'] = False
                        self.magic_projectiles.remove(projectile)
                        
                        print(f"💥 Proyectil mágico impactó a {getattr(target, 'name', 'objetivo')}")
                        break
    
    def update_magic_effects(self):
        """Actualiza efectos mágicos visuales"""
        current_time = pygame.time.get_ticks()
        
        for effect in self.magic_effects[:]:
            elapsed = current_time - effect['start_time']
            
            if elapsed >= effect['duration']:
                self.magic_effects.remove(effect)
                continue
            
            # Actualizar efecto
            progress = elapsed / effect['duration']
            effect['radius'] = int(effect['max_radius'] * progress)
            effect['alpha'] = int(255 * (1 - progress))
    
    def create_impact_effect(self, x, y):
        """Crea efecto visual de impacto"""
        effect = {
            'x': x,
            'y': y,
            'radius': 5,
            'max_radius': 30,
            'alpha': 255,
            'duration': 300,
            'start_time': pygame.time.get_ticks()
        }
        
        self.magic_effects.append(effect)
    
    def is_character_attacking(self):
        """Verifica si el personaje está atacando"""
        return self.is_attacking
    
    def get_attack_frame(self):
        """Obtiene el frame actual de ataque"""
        if not self.is_attacking:
            return None
        
        frames = self.attack_frames.get(self.attack_direction, [])
        if not frames:
            return None
        
        frame_index = int(self.attack_animation_frame) % len(frames)
        return frames[frame_index]
    
    def draw(self, screen, camera_x, camera_y):
        """Dibuja todos los efectos de ataque"""
        # Dibujar proyectiles mágicos
        for projectile in self.magic_projectiles:
            if projectile['active']:
                screen_x = int(projectile['x'] - camera_x)
                screen_y = int(projectile['y'] - camera_y)
                
                # Proyectil especial más grande y brillante
                if projectile.get('special', False):
                    color = (255, 100, 255)  # Magenta brillante
                    size = projectile['size']
                    # Efecto de brillo
                    for i in range(3):
                        alpha_surface = pygame.Surface((size + i*4, size + i*4), pygame.SRCALPHA)
                        pygame.draw.circle(alpha_surface, (*color, 100 - i*30), 
                                         (size//2 + i*2, size//2 + i*2), size//2 + i*2)
                        screen.blit(alpha_surface, (screen_x - size//2 - i*2, screen_y - size//2 - i*2))
                else:
                    color = (150, 0, 255)  # Púrpura
                    size = projectile['size']
                    pygame.draw.circle(screen, color, (screen_x, screen_y), size//2)
                    # Núcleo brillante
                    pygame.draw.circle(screen, (255, 150, 255), (screen_x, screen_y), size//4)
        
        # Dibujar efectos mágicos
        for effect in self.magic_effects:
            screen_x = int(effect['x'] - camera_x)
            screen_y = int(effect['y'] - camera_y)
            
            if effect['radius'] > 0:
                # Crear superficie con transparencia
                effect_surface = pygame.Surface((effect['radius']*2, effect['radius']*2), pygame.SRCALPHA)
                color_with_alpha = (255, 100, 255, effect['alpha'])
                pygame.draw.circle(effect_surface, color_with_alpha, 
                                 (effect['radius'], effect['radius']), effect['radius'])
                
                screen.blit(effect_surface, (screen_x - effect['radius'], screen_y - effect['radius']))
        
        # Dibujar frame de ataque si está atacando
        if self.is_attacking:
            attack_frame = self.get_attack_frame()
            if attack_frame:
                screen_x = self.character.x - camera_x
                screen_y = self.character.y - camera_y
                screen.blit(attack_frame, (screen_x, screen_y))
    
    def get_projectile_count(self):
        """Obtiene el número de proyectiles activos"""
        return len([p for p in self.magic_projectiles if p['active']])
    
    def clear_projectiles(self):
        """Limpia todos los proyectiles (para reinicio de nivel)"""
        self.magic_projectiles.clear()
        self.magic_effects.clear()
        print("🧹 Proyectiles del Chamán limpiados")