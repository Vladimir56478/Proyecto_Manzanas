"""
Utilidades comunes del juego
Funciones helper que se usan en múltiples módulos
"""

import pygame
import math
from typing import Tuple, List, Optional
from config import *

def load_image(path: str, size: Optional[Tuple[int, int]] = None) -> pygame.Surface:
    """
    Carga una imagen desde archivo y opcionalmente la redimensiona
    
    Args:
        path: Ruta al archivo de imagen
        size: Tuple (width, height) para redimensionar, None mantiene tamaño original
    
    Returns:
        pygame.Surface: Imagen cargada
    """
    try:
        image = pygame.image.load(path)
        if size:
            image = pygame.transform.scale(image, size)
        return image.convert_alpha()
    except pygame.error as e:
        print(f"Error cargando imagen {path}: {e}")
        # Crear superficie de color sólido como fallback
        surf = pygame.Surface(size if size else (64, 64))
        surf.fill(RED)
        return surf

def load_sound(path: str, volume: float = 1.0) -> Optional[pygame.mixer.Sound]:
    """
    Carga un archivo de sonido
    
    Args:
        path: Ruta al archivo de sonido
        volume: Volumen del sonido (0.0 a 1.0)
    
    Returns:
        pygame.mixer.Sound o None si falla
    """
    try:
        sound = pygame.mixer.Sound(path)
        sound.set_volume(volume * MASTER_VOLUME)
        return sound
    except pygame.error as e:
        print(f"Error cargando sonido {path}: {e}")
        return None

def calculate_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
    """
    Calcula la distancia euclidiana entre dos puntos
    
    Args:
        pos1: Primera posición (x, y)
        pos2: Segunda posición (x, y)
    
    Returns:
        float: Distancia entre los puntos
    """
    dx = pos2[0] - pos1[0]
    dy = pos2[1] - pos1[1]
    return math.sqrt(dx * dx + dy * dy)

def normalize_vector(vector: Tuple[float, float]) -> Tuple[float, float]:
    """
    Normaliza un vector a longitud 1
    
    Args:
        vector: Vector (x, y)
    
    Returns:
        Tuple[float, float]: Vector normalizado
    """
    length = math.sqrt(vector[0] ** 2 + vector[1] ** 2)
    if length == 0:
        return (0, 0)
    return (vector[0] / length, vector[1] / length)

def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Restringe un valor entre un mínimo y máximo
    
    Args:
        value: Valor a restringir
        min_val: Valor mínimo
        max_val: Valor máximo
    
    Returns:
        float: Valor restringido
    """
    return max(min_val, min(max_val, value))

def lerp(a: float, b: float, t: float) -> float:
    """
    Interpolación lineal entre dos valores
    
    Args:
        a: Valor inicial
        b: Valor final
        t: Factor de interpolación (0.0 a 1.0)
    
    Returns:
        float: Valor interpolado
    """
    return a + (b - a) * clamp(t, 0.0, 1.0)

def rect_collision(rect1: pygame.Rect, rect2: pygame.Rect) -> bool:
    """
    Verifica colisión entre dos rectángulos
    
    Args:
        rect1: Primer rectángulo
        rect2: Segundo rectángulo
    
    Returns:
        bool: True si hay colisión
    """
    return rect1.colliderect(rect2)

def point_in_rect(point: Tuple[int, int], rect: pygame.Rect) -> bool:
    """
    Verifica si un punto está dentro de un rectángulo
    
    Args:
        point: Punto (x, y)
        rect: Rectángulo
    
    Returns:
        bool: True si el punto está dentro
    """
    return rect.collidepoint(point)

def draw_health_bar(surface: pygame.Surface, pos: Tuple[int, int], 
                   current_health: int, max_health: int, 
                   width: int = HEALTH_BAR_WIDTH, height: int = HEALTH_BAR_HEIGHT):
    """
    Dibuja una barra de salud
    
    Args:
        surface: Superficie donde dibujar
        pos: Posición (x, y) de la barra
        current_health: Salud actual
        max_health: Salud máxima
        width: Ancho de la barra
        height: Alto de la barra
    """
    # Barra de fondo (roja)
    bg_rect = pygame.Rect(pos[0], pos[1], width, height)
    pygame.draw.rect(surface, RED, bg_rect)
    
    # Barra de salud (verde)
    if current_health > 0:
        health_width = int((current_health / max_health) * width)
        health_rect = pygame.Rect(pos[0], pos[1], health_width, height)
        pygame.draw.rect(surface, GREEN, health_rect)
    
    # Borde
    pygame.draw.rect(surface, WHITE, bg_rect, 2)

def format_time(milliseconds: int) -> str:
    """
    Formatea tiempo en milisegundos a formato MM:SS
    
    Args:
        milliseconds: Tiempo en milisegundos
    
    Returns:
        str: Tiempo formateado
    """
    seconds = milliseconds // 1000
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:02d}"

def ease_in_out(t: float) -> float:
    """
    Función de easing suave para animaciones
    
    Args:
        t: Tiempo normalizado (0.0 a 1.0)
    
    Returns:
        float: Valor con easing aplicado
    """
    return t * t * (3.0 - 2.0 * t)

def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> List[str]:
    """
    Divide texto en líneas que caben en un ancho máximo
    
    Args:
        text: Texto a dividir
        font: Fuente para medir el texto
        max_width: Ancho máximo por línea
    
    Returns:
        List[str]: Lista de líneas de texto
    """
    words = text.split(' ')
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return lines

class Timer:
    """
    Clase helper para manejar temporizadores
    """
    def __init__(self, duration: int):
        self.duration = duration
        self.start_time = 0
        self.active = False
    
    def start(self):
        """Inicia el temporizador"""
        self.start_time = pygame.time.get_ticks()
        self.active = True
    
    def is_finished(self) -> bool:
        """Verifica si el temporizador ha terminado"""
        if not self.active:
            return False
        return pygame.time.get_ticks() - self.start_time >= self.duration
    
    def get_progress(self) -> float:
        """Obtiene el progreso del temporizador (0.0 a 1.0)"""
        if not self.active:
            return 0.0
        elapsed = pygame.time.get_ticks() - self.start_time
        return min(elapsed / self.duration, 1.0)
    
    def reset(self):
        """Reinicia el temporizador"""
        self.active = False

class CollisionBlock:
    """Bloque invisible de colisión para restringir movimiento"""
    def __init__(self, x, y, width=None, height=None):
        self.x = x
        self.y = y
        self.width = width or COLLISION_BLOCK_SIZE
        self.height = height or COLLISION_BLOCK_SIZE
        self.rect = pygame.Rect(x, y, self.width, self.height)
    
    def draw_editor(self, screen, camera_x, camera_y):
        """Dibuja el bloque en modo editor"""
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Solo dibujar si está visible
        if (-self.width < screen_x < screen.get_width() + self.width and 
            -self.height < screen_y < screen.get_height() + self.height):
            
            # Bloque semi-transparente rojo
            block_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            block_surface.fill((255, 0, 0, 128))
            screen.blit(block_surface, (screen_x, screen_y))
            
            # Borde blanco
            pygame.draw.rect(screen, WHITE, 
                           (screen_x, screen_y, self.width, self.height), 2)

class CollisionManager:
    """Maneja las colisiones con bloques invisibles"""
    def __init__(self, world_width=None, world_height=None):
        self.blocks = []
        self.editor_mode = False
        self.block_size = COLLISION_BLOCK_SIZE
        self.world_width = world_width or SCREEN_WIDTH * 2
        self.world_height = world_height or SCREEN_HEIGHT * 2
        self.editor_cursor_x = 0
        self.editor_cursor_y = 0
        self.is_dragging = False
        self.mouse_pressed = False
        self.drag_start_x = 0
        self.drag_start_y = 0
    
    def add_block(self, x, y, width=None, height=None):
        """Añade un bloque de colisión"""
        block = CollisionBlock(x, y, width, height)
        self.blocks.append(block)
        return block
    
    def remove_block_at(self, x, y):
        """Elimina un bloque en la posición especificada"""
        for block in self.blocks[:]:
            if block.rect.collidepoint(x, y):
                self.blocks.remove(block)
                return True
        return False
    
    def check_collision(self, rect):
        """Verifica colisión con cualquier bloque"""
        for block in self.blocks:
            if rect.colliderect(block.rect):
                return True
        return False
    
    def get_collision_blocks(self, rect):
        """Obtiene todos los bloques que colisionan con el rectángulo"""
        colliding_blocks = []
        for block in self.blocks:
            if rect.colliderect(block.rect):
                colliding_blocks.append(block)
        return colliding_blocks
    
    def can_move_to(self, character, new_x, new_y):
        """Verifica si un personaje puede moverse a una nueva posición"""
        # Crear rectángulo de prueba en la nueva posición
        test_rect = pygame.Rect(new_x, new_y, 
                               getattr(character, 'width', 64), 
                               getattr(character, 'height', 64))
        
        # Verificar colisión con bloques
        return not self.check_collision(test_rect)
    
    def handle_editor_input(self, keys_pressed, keys_just_pressed):
        """Maneja la entrada del editor de colisiones"""
        if not self.editor_mode:
            return
        
        move_speed = 32
        if keys_just_pressed.get(pygame.K_UP, False):
            self.editor_cursor_y = max(0, self.editor_cursor_y - move_speed)
        if keys_just_pressed.get(pygame.K_DOWN, False):
            self.editor_cursor_y = min(self.world_height - self.block_size, self.editor_cursor_y + move_speed)
        if keys_just_pressed.get(pygame.K_LEFT, False):
            self.editor_cursor_x = max(0, self.editor_cursor_x - move_speed)
        if keys_just_pressed.get(pygame.K_RIGHT, False):
            self.editor_cursor_x = min(self.world_width - self.block_size, self.editor_cursor_x + move_speed)
        
        if keys_just_pressed.get(pygame.K_SPACE, False):
            self.add_editor_block(self.editor_cursor_x, self.editor_cursor_y)
        
        if keys_just_pressed.get(pygame.K_BACKSPACE, False):
            self.remove_block_at(self.editor_cursor_x, self.editor_cursor_y)
    
    def add_editor_block(self, x, y):
        """Añade un bloque de colisión desde el editor"""
        # Alinear a la cuadrícula
        grid_x = (x // self.block_size) * self.block_size
        grid_y = (y // self.block_size) * self.block_size
        
        # Verificar si ya existe un bloque en esta posición
        for block in self.blocks:
            if block.rect.x == grid_x and block.rect.y == grid_y:
                return  # Ya existe un bloque aquí
        
        # Crear nuevo bloque
        new_block = CollisionBlock(grid_x, grid_y, self.block_size, self.block_size)
        self.blocks.append(new_block)
        print(f"✅ Bloque añadido en ({grid_x}, {grid_y})")
    
    def draw_editor_mode(self, screen, camera_x, camera_y):
        """Dibuja el modo editor con cursor visual"""
        if not self.editor_mode:
            return
        
        # Dibujar todos los bloques en modo editor
        for block in self.blocks:
            screen_x = block.rect.x - camera_x
            screen_y = block.rect.y - camera_y
            
            # Solo dibujar si está en pantalla
            if (-50 < screen_x < screen.get_width() + 50 and 
                -50 < screen_y < screen.get_height() + 50):
                # Dibujar bloque con transparencia
                block_surface = pygame.Surface((block.rect.width, block.rect.height), pygame.SRCALPHA)
                block_surface.fill((255, 0, 0, 100))  # Rojo semi-transparente
                screen.blit(block_surface, (screen_x, screen_y))
                
                # Borde del bloque
                pygame.draw.rect(screen, (255, 0, 0), 
                               (screen_x, screen_y, block.rect.width, block.rect.height), 2)
        
        # Dibujar cursor del editor
        cursor_screen_x = self.editor_cursor_x - camera_x
        cursor_screen_y = self.editor_cursor_y - camera_y
        
        # Verificar si ya existe un bloque en esta posición
        block_exists = any(block.rect.x == (self.editor_cursor_x // self.block_size) * self.block_size and 
                          block.rect.y == (self.editor_cursor_y // self.block_size) * self.block_size 
                          for block in self.blocks)
        
        # Color del cursor
        cursor_color = (255, 100, 100) if block_exists else (100, 255, 100)
        border_color = (255, 0, 0) if block_exists else (0, 255, 0)
        
        # Fondo del cursor
        cursor_surface = pygame.Surface((self.block_size, self.block_size), pygame.SRCALPHA)
        cursor_surface.fill((*cursor_color, 120))
        screen.blit(cursor_surface, (cursor_screen_x, cursor_screen_y))
        
        # Borde del cursor
        pygame.draw.rect(screen, border_color, 
                        (cursor_screen_x, cursor_screen_y, self.block_size, self.block_size), 3)
        
        # Información del editor
        font = pygame.font.Font(None, 48)
        editor_info = [
            "🛠️ MODO EDITOR DE COLISIONES",
            "F1: Salir del editor | Flechas: Mover cursor",
            "ESPACIO: Colocar bloque | BACKSPACE: Eliminar",
            f"Bloques totales: {len(self.blocks)}"
        ]
        
        for i, info in enumerate(editor_info):
            text_surface = font.render(info, True, (255, 255, 0))
            screen.blit(text_surface, (20, 200 + i * 30))