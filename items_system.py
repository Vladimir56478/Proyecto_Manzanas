import pygame
import random
import math

class Item:
    def __init__(self, item_type, x, y):
        self.type = item_type  # 'apple' o 'potion'
        self.x = x
        self.y = y
        self.collected = False
        self.animation_timer = 0
        self.bob_offset = 0
        
        # Tamaños
        self.width = 32
        self.height = 32
        
        # Crear visual
        self.surface = self.create_item_surface()
        
    def create_item_surface(self):
        """Crea la superficie visual del item"""
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        if self.type == 'apple':
            # Manzana roja
            pygame.draw.circle(surface, (220, 20, 60), (16, 20), 12)
            pygame.draw.circle(surface, (34, 139, 34), (16, 12), 4)  # Hoja
            pygame.draw.rect(surface, (101, 67, 33), (15, 8, 2, 6))  # Tallo
        elif self.type == 'potion':
            # Poción azul
            pygame.draw.rect(surface, (0, 100, 200), (8, 16, 16, 12))
            pygame.draw.circle(surface, (0, 100, 200), (16, 16), 8)
            pygame.draw.rect(surface, (139, 69, 19), (14, 12, 4, 6))  # Tapón
            
        return surface
    
    def update(self):
        """Actualiza la animación del item"""
        if self.collected:
            return
            
        self.animation_timer += 0.1
        self.bob_offset = int(3 * math.sin(self.animation_timer))
    
    def draw(self, screen, camera_x, camera_y):
        """Dibuja el item en pantalla"""
        if self.collected:
            return
            
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y + self.bob_offset
        
        # Solo dibujar si está en pantalla
        if -50 < screen_x < screen.get_width() + 50 and -50 < screen_y < screen.get_height() + 50:
            screen.blit(self.surface, (screen_x, screen_y))
            
            # Brillo sutil
            pygame.draw.circle(screen, (255, 255, 255, 50), 
                             (screen_x + 16, screen_y + 16), 20, 2)
    
    def get_rect(self):
        """Obtiene el rectángulo de colisión"""
        return pygame.Rect(self.x, self.y, self.width, self.height)

class UpgradeMenu:
    def __init__(self):
        self.active = False
        self.selected_option = 0
        self.options = [
            {"name": "Daño +10", "type": "damage", "value": 10},
            {"name": "Vida +25", "type": "health", "value": 25}, 
            {"name": "Velocidad +0.5", "type": "speed", "value": 0.5}
        ]
        
        # Colores del menú
        self.bg_color = (50, 50, 50, 200)
        self.selected_color = (100, 150, 255)
        self.normal_color = (200, 200, 200)
        
    def show(self):
        """Muestra el menú de mejoras"""
        self.active = True
        self.selected_option = 0
        
    def hide(self):
        """Oculta el menú"""
        self.active = False
    
    def handle_input(self, keys):
        """Maneja la entrada del jugador"""
        if not self.active:
            return None
            
        if keys[pygame.K_UP] and self.selected_option > 0:
            self.selected_option -= 1
        elif keys[pygame.K_DOWN] and self.selected_option < len(self.options) - 1:
            self.selected_option += 1
        elif keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
            selected = self.options[self.selected_option]
            self.hide()
            return selected
        elif keys[pygame.K_ESCAPE]:
            self.hide()
            
        return None
    
    def draw(self, screen):
        """Dibuja el menú de mejoras"""
        if not self.active:
            return
            
        # Fondo semitransparente
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Menú central
        menu_width = 300
        menu_height = 200
        menu_x = (screen.get_width() - menu_width) // 2
        menu_y = (screen.get_height() - menu_height) // 2
        
        pygame.draw.rect(screen, self.bg_color, (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(screen, (100, 100, 100), (menu_x, menu_y, menu_width, menu_height), 3)
        
        # Título
        font_title = pygame.font.Font(None, 32)
        title = font_title.render("Elige una mejora:", True, (255, 255, 255))
        title_x = menu_x + (menu_width - title.get_width()) // 2
        screen.blit(title, (title_x, menu_y + 20))
        
        # Opciones
        font_option = pygame.font.Font(None, 24)
        for i, option in enumerate(self.options):
            color = self.selected_color if i == self.selected_option else self.normal_color
            
            option_text = font_option.render(option["name"], True, color)
            option_y = menu_y + 70 + i * 35
            
            # Resaltar opción seleccionada
            if i == self.selected_option:
                pygame.draw.rect(screen, (50, 100, 150), 
                               (menu_x + 10, option_y - 5, menu_width - 20, 30))
            
            screen.blit(option_text, (menu_x + 20, option_y))

class ShieldEffect:
    def __init__(self, duration=15000):  # 15 segundos
        self.active = False
        self.start_time = 0
        self.duration = duration
        self.damage_reduction = 0.5  # 50% reducción
        
    def activate(self):
        """Activa el escudo"""
        self.active = True
        self.start_time = pygame.time.get_ticks()
        
    def update(self):
        """Actualiza el estado del escudo"""
        if self.active:
            elapsed = pygame.time.get_ticks() - self.start_time
            if elapsed >= self.duration:
                self.active = False
                
    def reduce_damage(self, damage):
        """Reduce el daño si el escudo está activo"""
        if self.active:
            return int(damage * (1 - self.damage_reduction))
        return damage
    
    def get_remaining_time(self):
        """Obtiene el tiempo restante del escudo"""
        if not self.active:
            return 0
        elapsed = pygame.time.get_ticks() - self.start_time
        return max(0, self.duration - elapsed)
    
    def draw_indicator(self, screen, x, y):
        """Dibuja un indicador del escudo"""
        if not self.active:
            return
            
        remaining = self.get_remaining_time()
        progress = remaining / self.duration
        
        # Círculo de escudo
        radius = 40
        pygame.draw.circle(screen, (0, 150, 255, 100), (x, y), radius, 3)
        
        # Texto de tiempo restante
        font = pygame.font.Font(None, 20)
        time_text = font.render(f"Escudo: {remaining//1000}s", True, (0, 150, 255))
        screen.blit(time_text, (x - 40, y - 60))

class ItemManager:
    def __init__(self):
        self.items = []
        self.upgrade_menu = UpgradeMenu()
        self.shield_effect = ShieldEffect()
        
    def add_item(self, item_type, x, y):
        """Añade un nuevo item"""
        item = Item(item_type, x, y)
        self.items.append(item)
        
    def add_worm_drops(self, drops):
        """Añade drops de un gusano muerto"""
        for drop in drops:
            self.add_item(drop['type'], drop['x'], drop['y'])
    
    def update(self, players):
        """Actualiza todos los items y efectos"""
        # Actualizar items
        for item in self.items[:]:
            if item.collected:
                self.items.remove(item)
                continue
                
            item.update()
            
            # Verificar colisión con jugadores
            for player in players:
                if self.check_collision(item, player):
                    self.collect_item(item, player)
                    break
        
        # Actualizar escudo
        self.shield_effect.update()
    
    def check_collision(self, item, player):
        """Verifica colisión entre item y jugador"""
        item_rect = item.get_rect()
        player_rect = pygame.Rect(player.x, player.y, 64, 64)  # Asumir tamaño estándar
        return item_rect.colliderect(player_rect)
    
    def collect_item(self, item, player):
        """Maneja la recolección de un item"""
        item.collected = True
        
        if item.type == 'apple':
            # Mostrar menú de mejoras
            self.upgrade_menu.show()
        elif item.type == 'potion':
            # Activar escudo inmediatamente
            self.shield_effect.activate()
            print("🛡️ Escudo activado por 15 segundos!")
    
    def handle_upgrade_input(self, keys, player):
        """Maneja la entrada del menú de mejoras"""
        selected = self.upgrade_menu.handle_input(keys)
        if selected:
            self.apply_upgrade(selected, player)
            return True
        return False
    
    def apply_upgrade(self, upgrade, player):
        """Aplica una mejora al jugador"""
        if upgrade["type"] == "damage":
            if hasattr(player, 'damage'):
                player.damage += upgrade["value"]
                print(f"⚔️ Daño aumentado: +{upgrade['value']}")
        elif upgrade["type"] == "health":
            if hasattr(player, 'max_health'):
                player.max_health += upgrade["value"]
                player.health += upgrade["value"]  # También cura
                print(f"❤️ Vida máxima aumentada: +{upgrade['value']}")
        elif upgrade["type"] == "speed":
            if hasattr(player, 'speed'):
                player.speed += upgrade["value"]
                print(f"🏃 Velocidad aumentada: +{upgrade['value']}")
    
    def apply_shield_damage_reduction(self, damage):
        """Aplica reducción de daño del escudo"""
        return self.shield_effect.reduce_damage(damage)
    
    def draw(self, screen, camera_x, camera_y):
        """Dibuja todos los items y UI"""
        # Dibujar items
        for item in self.items:
            item.draw(screen, camera_x, camera_y)
        
        # Dibujar menú de mejoras
        self.upgrade_menu.draw(screen)
        
        # Dibujar indicador de escudo
        if self.shield_effect.active:
            self.shield_effect.draw_indicator(screen, 100, 100)