#!/usr/bin/env python3
"""
CHAMAN MALVADO - SISTEMA DE ANIMACIONES DE MOVIMIENTO
Sistema de animaciones para el jefe final del Nivel 2
"""

import pygame
import math
import os
from PIL import Image


class ChamanCharacter:
    """Clase para manejar las animaciones de movimiento del Chamán Malvado"""
    
    def __init__(self, x, y):
        """Inicializa el Chamán Malvado con sus propiedades base"""
        # Posición y física
        self.x = x
        self.y = y
        self.speed = 2.0  # Más lento que los héroes pero poderoso
        
        # Estadísticas del jefe
        self.max_health = 500  # Mucha vida como jefe final
        self.health = self.max_health
        self.damage = 35  # Alto daño
        self.defense = 8  # Resistencia alta
        self.name = "Chamán Malvado"
        
        # Estados de animación
        self.current_direction = "down"
        self.moving = False
        self.animation_frame = 0
        self.animation_speed = 0.12  # Animación más lenta y majestuosa
        self.last_frame_time = pygame.time.get_ticks()
        
        # URLs de animaciones de movimiento desde archivo local
        self.movement_urls = {
            "right": "assets/characters/chaman/animations/right.gif",
            "up": "assets/characters/chaman/animations/up.gif", 
            "down": "assets/characters/chaman/animations/down.gif",
            "left": "assets/characters/chaman/animations/left.gif"
        }
        
        # Diccionarios para almacenar frames
        self.movement_frames = {"up": [], "down": [], "left": [], "right": []}
        self.frames_loaded = False
        
        # Cargar animaciones
        self.load_all_animations()
        
        # Propiedades visuales
        self.width = 128  # Más grande que los héroes
        self.height = 128
        self.flip_horizontal = False
        
        print(f"🧙 Chamán Malvado creado en ({x}, {y}) - Vida: {self.health}")
    
    def load_all_animations(self):
        """Carga todas las animaciones de movimiento del chamán"""
        print("🎭 Cargando animaciones del Chamán Malvado...")
        
        for direction, url in self.movement_urls.items():
            try:
                frames = self.load_gif_from_url(url)
                if frames:
                    self.movement_frames[direction] = frames
                    print(f"✅ Animación {direction}: {len(frames)} frames")
                else:
                    print(f"⚠️ No se pudieron cargar frames para {direction}")
                    self.create_fallback_frame(direction)
            except Exception as e:
                print(f"❌ Error cargando {direction}: {e}")
                self.create_fallback_frame(direction)
        
        self.frames_loaded = True
        print("🎭 Animaciones del Chamán cargadas completamente")
    
    def load_gif_from_url(self, url):
        """Carga un GIF desde archivo local y extrae sus frames"""
        try:
            print(f"📥 Cargando animación desde archivo local...")
            # Cargar desde archivo local
            gif = Image.open(url)
            
            frames = []
            frame_count = 0
            
            try:
                while True:
                    # Convertir frame a RGBA para manejar transparencia
                    frame_rgba = gif.convert('RGBA')
                    
                    # Redimensionar para que sea más imponente (128x128)
                    frame_rgba = frame_rgba.resize((128, 128), Image.LANCZOS)
                    
                    # Convertir fondo blanco a transparente
                    pixel_data = frame_rgba.load()
                    for y in range(frame_rgba.height):
                        for x in range(frame_rgba.width):
                            r, g, b, a = pixel_data[x, y]
                            # Si el pixel es blanco o casi blanco, hacerlo transparente
                            if r > 240 and g > 240 and b > 240:
                                pixel_data[x, y] = (r, g, b, 0)  # Transparente
                    
                    # Convertir a pygame surface
                    frame_data = frame_rgba.tobytes()
                    pygame_surface = pygame.image.fromstring(frame_data, (128, 128), 'RGBA')
                    pygame_surface = pygame_surface.convert_alpha()
                    
                    frames.append(pygame_surface)
                    frame_count += 1
                    
                    # Ir al siguiente frame
                    gif.seek(gif.tell() + 1)
                    
            except EOFError:
                pass  # Fin del GIF
            
            print(f"✅ {frame_count} frames extraídos exitosamente")
            return frames
            
        except Exception as e:
            print(f"❌ Error procesando GIF: {e}")
            return []
    
    def create_fallback_frame(self, direction):
        """Crea un frame de respaldo si falla la carga"""
        surface = pygame.Surface((128, 128), pygame.SRCALPHA)
        
        # Dibujar chamán de respaldo (más grande e imponente)
        pygame.draw.circle(surface, (80, 20, 80), (64, 64), 50)  # Cuerpo morado
        pygame.draw.circle(surface, (120, 40, 120), (64, 45), 25)  # Cabeza
        pygame.draw.rect(surface, (60, 10, 60), (54, 85, 20, 35))  # Túnica
        
        # Ojos malvados
        pygame.draw.circle(surface, (255, 0, 0), (58, 40), 4)  # Ojo izquierdo rojo
        pygame.draw.circle(surface, (255, 0, 0), (70, 40), 4)  # Ojo derecho rojo
        
        # Bastón mágico
        pygame.draw.line(surface, (139, 69, 19), (35, 60), (25, 20), 6)  # Bastón
        pygame.draw.circle(surface, (255, 215, 0), (25, 20), 8)  # Orbe dorado
        
        self.movement_frames[direction] = [surface]
        print(f"🎨 Frame de respaldo creado para {direction}")
    
    def update(self, keys_pressed=None, ai_controlled=False, ai_direction=None):
        """Actualiza la animación y movimiento del chamán"""
        old_x, old_y = self.x, self.y
        self.moving = False
        
        # Determinar movimiento
        if ai_controlled and ai_direction:
            # Controlado por IA
            direction = ai_direction
            if direction in ["up", "down", "left", "right"]:
                self.move_in_direction(direction)
                self.moving = True
                self.current_direction = direction
        elif keys_pressed:
            # Control manual (para pruebas) - solo WASD
            if keys_pressed[pygame.K_w]:
                self.y -= self.speed
                self.moving = True
                self.current_direction = "up"
            elif keys_pressed[pygame.K_s]:
                self.y += self.speed
                self.moving = True
                self.current_direction = "down"
            elif keys_pressed[pygame.K_a]:
                self.x -= self.speed
                self.moving = True
                self.current_direction = "left"
            elif keys_pressed[pygame.K_d]:
                self.x += self.speed
                self.moving = True
                self.current_direction = "right"
        
        # Actualizar animación solo si nos movimos
        if self.moving and (old_x != self.x or old_y != self.y):
            self.update_animation()
    
    def move_in_direction(self, direction):
        """Mueve el chamán en la dirección especificada"""
        if direction == "up":
            self.y -= self.speed
        elif direction == "down":
            self.y += self.speed
        elif direction == "left":
            self.x -= self.speed
        elif direction == "right":
            self.x += self.speed
    
    def update_animation(self):
        """Actualiza los frames de animación"""
        current_time = pygame.time.get_ticks()
        
        if current_time - self.last_frame_time > (self.animation_speed * 1000):
            frames = self.movement_frames.get(self.current_direction, [])
            if frames:
                self.animation_frame = (self.animation_frame + 1) % len(frames)
                self.last_frame_time = current_time
    
    def get_current_frame(self):
        """Obtiene el frame actual de animación"""
        if not self.frames_loaded:
            return None
            
        frames = self.movement_frames.get(self.current_direction, [])
        if not frames:
            return None
            
        frame_index = int(self.animation_frame) % len(frames)
        return frames[frame_index]
    
    def draw(self, screen, camera_x, camera_y, attack_system=None):
        """Dibuja el chamán en pantalla"""
        # Calcular posición en pantalla
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Solo dibujar si está visible
        if (-self.width < screen_x < screen.get_width() + self.width and 
            -self.height < screen_y < screen.get_height() + self.height):
            
            # Si hay un sistema de ataque y está atacando, usar frame de ataque
            current_frame = None
            if attack_system and attack_system.is_character_attacking():
                current_frame = attack_system.get_attack_frame()
            
            # Si no hay frame de ataque, usar frame de movimiento
            if not current_frame:
                current_frame = self.get_current_frame()
            
            if current_frame:
                # Aplicar flip horizontal si es necesario
                if self.flip_horizontal:
                    current_frame = pygame.transform.flip(current_frame, True, False)
                
                # Dibujar frame (siempre del mismo tamaño)
                screen.blit(current_frame, (screen_x, screen_y))
                
                # Barra de vida del jefe
                self.draw_health_bar(screen, screen_x, screen_y)
            else:
                # Fallback si no hay frame
                pygame.draw.rect(screen, (80, 20, 80), 
                               (screen_x, screen_y, self.width, self.height))
    
    def draw_health_bar(self, screen, screen_x, screen_y):
        """Dibuja la barra de vida del jefe"""
        bar_width = self.width
        bar_height = 8
        bar_x = screen_x
        bar_y = screen_y - 15
        
        # Fondo de la barra
        pygame.draw.rect(screen, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        
        # Barra de vida
        health_percentage = self.health / self.max_health
        health_width = int(bar_width * health_percentage)
        
        # Color de la barra según la vida
        if health_percentage > 0.6:
            health_color = (0, 150, 0)  # Verde
        elif health_percentage > 0.3:
            health_color = (255, 255, 0)  # Amarillo
        else:
            health_color = (255, 0, 0)  # Rojo
        
        if health_width > 0:
            pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height))
        
        # Borde de la barra
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)
        
        # Texto de vida
        font = pygame.font.Font(None, 24)
        health_text = font.render(f"{self.health}/{self.max_health}", True, (255, 255, 255))
        text_x = screen_x + (self.width - health_text.get_width()) // 2
        text_y = screen_y - 35
        
        # Fondo del texto
        text_bg = pygame.Surface((health_text.get_width() + 4, health_text.get_height() + 2))
        text_bg.set_alpha(180)
        text_bg.fill((0, 0, 0))
        screen.blit(text_bg, (text_x - 2, text_y - 1))
        screen.blit(health_text, (text_x, text_y))
    
    def take_damage(self, damage):
        """El chamán recibe daño"""
        actual_damage = max(1, damage - self.defense)
        self.health = max(0, self.health - actual_damage)
        print(f"🧙 Chamán recibió {actual_damage} daño (Vida: {self.health}/{self.max_health})")
        
        return self.health <= 0  # Retorna True si murió
    
    def is_alive(self):
        """Verifica si el chamán sigue vivo"""
        return self.health > 0
    
    def get_rect(self):
        """Obtiene el rectángulo de colisión del chamán"""
        return pygame.Rect(self.x, self.y, self.width, self.height)