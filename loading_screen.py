import pygame
import threading
import queue
import time

class LoadingScreen:
    """Sistema de pantalla de carga con barra de progreso real"""
    
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Fuentes
        self.title_font = pygame.font.Font(None, 48)
        self.text_font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 24)
        
        # Colores
        self.bg_color = (15, 15, 25)  # Azul muy oscuro
        self.text_color = (255, 255, 255)
        self.title_color = (255, 215, 0)  # Dorado
        self.progress_color = (0, 200, 100)  # Verde
        self.bar_bg_color = (50, 50, 50)
        
        # Estado de carga
        self.assets_to_load = []
        self.current_asset = 0
        self.current_message = "Iniciando..."
        self.progress = 0.0
        
        # Frases clásicas de carga
        self.loading_messages = [
            "Preparando el mundo...",
            "Cargando texturas...",
            "Inicializando personajes...",
            "Descargando sprites...",
            "Configurando animaciones...",
            "Cargando ataques especiales...",
            "Preparando enemigos...",
            "Optimizando graficos...",
            "Estableciendo fisicas...",
            "Sincronizando datos...",
            "Ultimos retoques...",
            "¡Casi listo!"
        ]
        
        # Para efectos visuales
        self.angle = 0
    
    def add_asset(self, name, description):
        """Agrega un asset a la lista de carga"""
        self.assets_to_load.append({'name': name, 'description': description})
    
    def start_loading(self, assets_list):
        """Inicia el proceso de carga con una lista de assets"""
        self.assets_to_load = assets_list
        self.current_asset = 0
        self.progress = 0.0
    
    def update_progress(self, asset_name, message=None):
        """Actualiza el progreso de carga"""
        if message:
            self.current_message = message
        else:
            # Usar mensaje clásico basado en el progreso
            progress_index = int(self.progress * (len(self.loading_messages) - 1))
            self.current_message = self.loading_messages[min(progress_index, len(self.loading_messages) - 1)]
        
        self.current_asset += 1
        if len(self.assets_to_load) > 0:
            self.progress = self.current_asset / len(self.assets_to_load)
        else:
            self.progress = min(self.progress + 0.1, 1.0)
    
    def set_custom_message(self, message):
        """Establece un mensaje personalizado"""
        self.current_message = message
    
    def draw(self):
        """Dibuja la pantalla de carga"""
        # Fondo
        self.screen.fill(self.bg_color)
        
        # Actualizar efecto visual
        self.angle += 2
        
        # Dibujar círculos de carga animados
        center_x = self.screen_width // 2
        center_y = 150
        for i in range(8):
            angle = self.angle + i * 45
            x = center_x + 60 * pygame.math.Vector2(1, 0).rotate(angle).x
            y = center_y + 20 * pygame.math.Vector2(1, 0).rotate(angle).y
            size = 4 + 2 * abs(pygame.math.Vector2(1, 0).rotate(angle * 2).x)
            alpha = int(128 + 127 * abs(pygame.math.Vector2(1, 0).rotate(angle * 3).x))
            color = (255, 215, 0, alpha)
            temp_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surface, color, (size, size), size)
            self.screen.blit(temp_surface, (x - size, y - size))
        
        # Título principal
        title_text = self.title_font.render("🍎 Cargando Nivel 1", True, self.title_color)
        title_rect = title_text.get_rect(center=(self.screen_width//2, 220))
        self.screen.blit(title_text, title_rect)
        
        # Mensaje actual
        message_text = self.text_font.render(self.current_message, True, self.text_color)
        message_rect = message_text.get_rect(center=(self.screen_width//2, 300))
        self.screen.blit(message_text, message_rect)
        
        # Barra de progreso
        bar_width = 500
        bar_height = 25
        bar_x = (self.screen_width - bar_width) // 2
        bar_y = 370
        
        # Fondo de la barra
        pygame.draw.rect(self.screen, self.bar_bg_color, (bar_x, bar_y, bar_width, bar_height))
        
        # Progreso
        progress_width = int(bar_width * self.progress)
        if progress_width > 0:
            pygame.draw.rect(self.screen, self.progress_color, (bar_x, bar_y, progress_width, bar_height))
        
        # Borde de la barra
        pygame.draw.rect(self.screen, self.text_color, (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Porcentaje
        percent = int(self.progress * 100)
        percent_text = self.text_font.render(f"{percent}%", True, self.text_color)
        percent_rect = percent_text.get_rect(center=(self.screen_width//2, bar_y + 50))
        self.screen.blit(percent_text, percent_rect)
        
        # Asset actual (si hay)
        if self.current_asset < len(self.assets_to_load):
            asset_info = self.assets_to_load[self.current_asset]
            asset_text = self.small_font.render(f"Cargando: {asset_info.get('name', 'Recurso')}", True, (180, 180, 180))
            asset_rect = asset_text.get_rect(center=(self.screen_width//2, bar_y + 80))
            self.screen.blit(asset_text, asset_rect)
        
        # Tips de carga
        if percent < 50:
            tip = "💡 Tip: Usa WASD para moverte y Espacio para atacar"
        elif percent < 80:
            tip = "💡 Tip: Presiona E para revivir a tu compañero"
        else:
            tip = "💡 Tip: Cambia entre personajes con TAB"
        
        tip_text = self.small_font.render(tip, True, (150, 150, 200))
        tip_rect = tip_text.get_rect(center=(self.screen_width//2, self.screen_height - 80))
        self.screen.blit(tip_text, tip_rect)
        
        pygame.display.flip()
    
    def is_complete(self):
        """Verifica si la carga está completa"""
        return self.progress >= 1.0
    
    def show_completion(self):
        """Muestra pantalla de carga completa"""
        self.screen.fill(self.bg_color)
        
        # Mensaje de éxito
        success_text = self.title_font.render("¡Listo para la aventura!", True, (0, 255, 100))
        success_rect = success_text.get_rect(center=(self.screen_width//2, self.screen_height//2))
        self.screen.blit(success_text, success_rect)
        
        # Efectos de éxito
        for i in range(20):
            angle = 18 * i
            x = self.screen_width//2 + 200 * pygame.math.Vector2(1, 0).rotate(angle).x
            y = self.screen_height//2 + 100 * pygame.math.Vector2(1, 0).rotate(angle).y
            size = 4 + 2 * abs(pygame.math.Vector2(1, 0).rotate(36 * i).x)
            color = (100 + 155 * abs(pygame.math.Vector2(1, 0).rotate(72 * i).x), 255, 100)
            pygame.draw.circle(self.screen, color, (int(x), int(y)), int(size))
        
        pygame.display.flip()
        pygame.time.wait(1000)  # Mostrar por 1 segundo