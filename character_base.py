"""
Clase base para personajes - Elimina duplicación de código
"""
import pygame
import os
from PIL import Image
from config import *
from utils import *


class CharacterBase:
    """Clase base para todos los personajes del juego"""
    
    def __init__(self, x, y, name, animations_path):
        # Posición y movimiento
        self.x = x
        self.y = y
        self.speed = CHARACTER_SPEED
        self.current_direction = "down"
        self.moving = False
        
        # Animación
        self.animation_frame = 0
        self.animation_speed = ANIMATION_SPEED
        
        # Dimensiones del personaje para colisiones y efectos (escaladas como ataques)
        self.width = int(CHARACTER_SIZE[0] * 1.56)
        self.height = int(CHARACTER_SIZE[1] * 1.56)
        
        # Estado
        self.max_health = 100
        self.health = self.max_health
        self.invulnerable = False
        self.invulnerable_time = 0
        self.invulnerable_duration = 1000
        self.name = name
        
        # Rutas de animaciones
        self.animations_path = animations_path
        self.gif_urls = {
            "up": f"{animations_path}/up.gif",
            "down": f"{animations_path}/down.gif",
            "left": f"{animations_path}/left.gif",
            "right": f"{animations_path}/right.gif"
        }
        
        self.animations = {}
        self.load_animations()
    
    def load_animations(self):
        """Carga las animaciones desde archivos locales"""
        print(f"Cargando animaciones de {self.name}...")
        
        for direction, file_path in self.gif_urls.items():
            try:
                if not os.path.exists(file_path):
                    print(f"⚠️  Archivo no encontrado: {file_path}")
                    raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
                
                gif = Image.open(file_path)
                frames = []
                
                for frame_num in range(gif.n_frames):
                    gif.seek(frame_num)
                    frame = gif.copy().convert("RGBA")
                    
                    frame_data = frame.tobytes()
                    try:
                        pygame_surface = pygame.image.fromstring(frame_data, frame.size, "RGBA")
                        pygame_surface = pygame_surface.convert_alpha()
                        
                        # Eliminar fondo blanco y colores similares
                        pygame_surface.set_colorkey((255, 255, 255))  # Blanco puro
                        pygame_surface.set_colorkey((254, 254, 254))  # Casi blanco
                        pygame_surface.set_colorkey((253, 253, 253))  # Gris muy claro
                        
                        # Procesar píxel por píxel para eliminar fondos blancos/claros
                        width, height = pygame_surface.get_size()
                        for x in range(width):
                            for y in range(height):
                                pixel = pygame_surface.get_at((x, y))
                                # Si el píxel es muy claro (fondo), hacerlo transparente
                                if pixel[0] > 250 and pixel[1] > 250 and pixel[2] > 250:
                                    pygame_surface.set_at((x, y), (0, 0, 0, 0))
                                    
                    except pygame.error as e:
                        print(f"⚠️  Error convirtiendo frame {frame_num} de {direction}: {e}")
                        # Crear un sprite temporal para debug
                        pygame_surface = pygame.Surface(frame.size, pygame.SRCALPHA)
                        pygame_surface.fill((255, 0, 255, 128))  # Magenta semi-transparente para debug
                    
                    frames.append(pygame_surface)
                
                self.animations[direction] = frames
                print(f"✅ Cargada animación {direction}: {len(frames)} frames")
                
            except Exception as e:
                print(f"❌ Error cargando {direction}: {e}")
                # Crear animación de respaldo
                self.animations[direction] = [self.create_fallback_sprite()]
    
    def create_fallback_sprite(self):
        """Crea un sprite de respaldo si falla la carga"""
        try:
            surface = pygame.Surface(CHARACTER_SIZE, pygame.SRCALPHA)
            # Color base según el personaje
            color = BLUE if self.name == "Juan" else RED
            center = (CHARACTER_SIZE[0] // 2, CHARACTER_SIZE[1] // 2)
            pygame.draw.circle(surface, color, center, 30)
            return surface
        except pygame.error as e:
            print(f"⚠️  Error creando sprite de respaldo para {self.name}: {e}")
            # Crear sprite temporal sin pygame.draw
            return None
    
    def update(self, keys_pressed=None, ai_controlled=False, ai_direction=None):
        """Actualiza el personaje"""
        # Manejar invulnerabilidad
        if self.invulnerable:
            self.invulnerable_time -= 1000 // FPS  # Basado en FPS configurado
            if self.invulnerable_time <= 0:
                self.invulnerable = False
        
        # Movimiento
        old_x, old_y = self.x, self.y
        self.moving = False
        
        if ai_controlled and ai_direction:
            # Movimiento controlado por IA
            self.current_direction = ai_direction
            self.moving = True
        elif keys_pressed:
            # Movimiento controlado por jugador
            if keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]:
                self.x -= self.speed
                self.current_direction = "left"
                self.moving = True
            elif keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]:
                self.x += self.speed
                self.current_direction = "right"
                self.moving = True
            elif keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w]:
                self.y -= self.speed
                self.current_direction = "up"
                self.moving = True
            elif keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_s]:
                self.y += self.speed
                self.current_direction = "down"
                self.moving = True
        
        # Actualizar animación
        if self.moving:
            self.animation_frame += self.animation_speed
            if self.animation_frame >= len(self.animations.get(self.current_direction, [1])):
                self.animation_frame = 0
    
    def draw(self, screen, camera_x, camera_y):
        """Dibuja el personaje en pantalla"""
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Obtener frame actual con inversión especial para Juan
        if self.name == "Juan":
            # Invertir direcciones arriba/abajo para Juan
            direction_map = {
                "up": "down",    # Arriba usa animación de abajo
                "down": "up",    # Abajo usa animación de arriba
                "left": "left",  # Izquierda mantiene (se invierte horizontalmente después)
                "right": "right" # Derecha mantiene (se invierte horizontalmente después)
            }
            animation_direction = direction_map.get(self.current_direction, self.current_direction)
        else:
            animation_direction = self.current_direction
        
        current_animation = self.animations.get(animation_direction, [])
        if current_animation:
            frame_index = int(self.animation_frame) % len(current_animation)
            current_frame = current_animation[frame_index]
            
            # Escalar a tamaño final alineado con ataques (1.56x como los ataques)
            original_size = current_frame.get_size()
            scaled_size = (int(original_size[0] * 1.56), int(original_size[1] * 1.56))
            scaled_frame = pygame.transform.scale(current_frame, scaled_size)
            
            # Invertir horizontalmente los movimientos de Juan
            if self.name == "Juan":
                scaled_frame = pygame.transform.flip(scaled_frame, True, False)
            
            # Efecto de invulnerabilidad
            if self.invulnerable and (self.invulnerable_time // 100) % 2:
                # Hacer el sprite semi-transparente
                temp_surface = scaled_frame.copy()
                temp_surface.set_alpha(128)
                screen.blit(temp_surface, (screen_x, screen_y))
            else:
                screen.blit(scaled_frame, (screen_x, screen_y))
    
    def take_damage(self, damage):
        """El personaje recibe daño"""
        if not self.invulnerable and self.health > 0:
            self.health = max(0, self.health - damage)
            if self.health > 0:
                self.invulnerable = True
                self.invulnerable_time = self.invulnerable_duration
            return True
        return False
    
    def heal(self, amount):
        """Cura al personaje"""
        if self.health > 0:
            self.health = min(self.max_health, self.health + amount)
            return True
        return False
    
    def is_alive(self):
        """Verifica si el personaje está vivo"""
        return self.health > 0