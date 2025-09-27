import pygame
import sys
from PIL import Image
import os

class AdanCharacter:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 5
        self.current_direction = "down"
        self.moving = False
        self.animation_frame = 0
        self.animation_speed = 0.3  # Aumentado de 0.2 para animaciones más fluidas y visibles
        
        self.gif_urls = {
            "up": "assets/characters/adan/animations/up.gif",
            "down": "assets/characters/adan/animations/down.gif",
            "left": "assets/characters/adan/animations/left.gif",
            "right": "assets/characters/adan/animations/right.gif"
        }
        
        self.animations = {}
        self.max_health = 100
        self.health = self.max_health
        self.invulnerable = False
        self.invulnerable_time = 0
        self.invulnerable_duration = 1000
        self.name = "Adán"
        
        self.load_animations()
        
    def load_animations(self):
        print("Cargando animaciones de Adán desde archivo local...")
        
        for direction, file_path in self.gif_urls.items():
            try:
                print(f"📥 Cargando {direction} desde {file_path}...")
                
                # Verificar si el archivo existe
                if not os.path.exists(file_path):
                    print(f"⚠️  Archivo no encontrado: {file_path}")
                    raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
                
                # Cargar desde archivo local
                gif = Image.open(file_path)
                frames = []
                
                for frame_num in range(gif.n_frames):
                    gif.seek(frame_num)
                    frame = gif.copy().convert("RGBA")
                    
                    frame_data = frame.tobytes()
                    pygame_surface = pygame.image.fromstring(frame_data, frame.size, "RGBA")
                    
                    pygame_surface = pygame_surface.convert_alpha()
                    pygame_surface.set_colorkey((255, 255, 255))
                    
                    # Escalar 56% más grande (30% + 20% adicional)
                    original_size = pygame_surface.get_size()
                    new_size = (int(original_size[0] * 1.56), int(original_size[1] * 1.56))
                    pygame_surface = pygame.transform.scale(pygame_surface, new_size)
                    
                    frames.append(pygame_surface)
                
                self.animations[direction] = frames
                print(f"✅ Cargada animación '{direction}': {len(frames)} frames")
                
            except Exception as e:
                print(f"❌ Error cargando {direction}: {e}")
                backup_surface = pygame.Surface((100, 100))  # 64 * 1.56 = 100
                backup_surface.fill((255, 0, 255))
                self.animations[direction] = [backup_surface]
    
    def take_damage(self, damage):
        if self.invulnerable:
            return False
        
        self.health -= damage
        self.health = max(0, self.health)
        
        self.invulnerable = True
        self.invulnerable_time = pygame.time.get_ticks()
        
        print(f"💔 {self.name} recibió {damage} daño (Vida: {self.health}/{self.max_health})")
        
        if self.health <= 0:
            print(f"💀 {self.name} ha sido derrotado")
            return True
        
        return False
    
    def update(self, keys_pressed=None, ai_controlled=False, ai_direction=None):
        self.moving = False
        
        if self.invulnerable:
            current_time = pygame.time.get_ticks()
            if current_time - self.invulnerable_time >= self.invulnerable_duration:
                self.invulnerable = False
        
        # Si está controlado por IA
        if ai_controlled:
            if ai_direction:
                # IA se está moviendo
                self.current_direction = ai_direction
                self.moving = True
                self.animation_frame += self.animation_speed
                if self.current_direction in self.animations and len(self.animations[self.current_direction]) > 0:
                    if self.animation_frame >= len(self.animations[self.current_direction]):
                        self.animation_frame = 0
            else:
                # IA está quieto, mantener dirección actual sin animación
                self.moving = False
                self.animation_frame = 0
            return
        
        # Control manual normal - Solo WASD
        if keys_pressed:
            if keys_pressed[pygame.K_w]:
                self.y -= self.speed
                self.current_direction = "up"
                self.moving = True
                
            elif keys_pressed[pygame.K_s]:
                self.y += self.speed
                self.current_direction = "down"
                self.moving = True
                
            elif keys_pressed[pygame.K_a]:
                self.x -= self.speed
                self.current_direction = "left"
                self.moving = True
                
            elif keys_pressed[pygame.K_d]:
                self.x += self.speed
                self.current_direction = "right"
                self.moving = True
        
        if self.moving:
            self.animation_frame += self.animation_speed
            if self.current_direction in self.animations and len(self.animations[self.current_direction]) > 0:
                if self.animation_frame >= len(self.animations[self.current_direction]):
                    self.animation_frame = 0
        else:
            self.animation_frame = 0
    
    def draw(self, screen, camera_x=0, camera_y=0):
        if (self.current_direction in self.animations and 
            len(self.animations[self.current_direction]) > 0):
            
            current_frames = self.animations[self.current_direction]
            frame_index = int(self.animation_frame) % len(current_frames)
            current_sprite = current_frames[frame_index]
            
            # Crear superficie temporal con mejor manejo de transparencia
            temp_surface = current_sprite.copy()
            
            # Aplicar transparencia para fondos (negro y blanco)
            if temp_surface.get_bitsize() >= 24:
                temp_surface = temp_surface.convert_alpha()
            temp_surface.set_colorkey((0, 0, 0))  # Negro transparente
            
            # Efecto de invulnerabilidad
            if self.invulnerable:
                current_time = pygame.time.get_ticks()
                if (current_time // 100) % 2:
                    temp_surface.set_alpha(128)
            
            screen.blit(temp_surface, (self.x - camera_x, self.y - camera_y))
        # Si no hay animación válida, NO dibujar nada (evita recuadros oscuros)

    def draw_health_bar(self, screen, camera_x, camera_y):
        if self.health < self.max_health:
            bar_width = 60
            bar_height = 8
            bar_x = self.x - camera_x + 2
            bar_y = self.y - camera_y - 15
            
            pygame.draw.rect(screen, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            
            health_width = int((self.health / self.max_health) * bar_width)
            health_color = (0, 255, 0) if self.health > 30 else (255, 255, 0) if self.health > 15 else (255, 0, 0)
            pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height))
    
    def start_ai_attack(self, direction):
        """Inicia animación de ataque desde IA"""
        if hasattr(self, 'attacks') and self.attacks:
            self.attacks.start_attack_animation(direction)
            return True
        return False
