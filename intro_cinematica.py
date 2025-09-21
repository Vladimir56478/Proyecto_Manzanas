import pygame
import sys
import random
import math
import time
import requests
from io import BytesIO
from audio_manager import get_audio_manager

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_x = random.uniform(-0.5, 0.5)
        self.vel_y = random.uniform(-2.5, -1.2)  # Velocidad más alta para subir más
        self.size = random.uniform(2, 6)
        self.alpha = random.uniform(100, 255)
        self.fade_rate = random.uniform(0.3, 1.2)  # Duran más tiempo visibles
        self.float_speed = random.uniform(0.8, 1.5)  # Mayor velocidad de flotación
        
    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y * self.float_speed
        self.alpha -= self.fade_rate
        
        # Si la partícula sale de la pantalla o se desvanece, reiniciarla
        if self.alpha <= 0 or self.y < -50:  # Permitir que suban mucho más arriba
            self.reset()
    
    def reset(self):
        self.x = random.uniform(0, 1000)
        self.y = random.uniform(700, 750)
        self.alpha = random.uniform(100, 255)
        self.size = random.uniform(2, 6)
    
    def draw(self, screen):
        if self.alpha > 0:
            # Color amarillento dorado
            color = (255, 215, 0, int(self.alpha))
            # Crear superficie temporal para alpha
            temp_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surface, color, (self.size, self.size), self.size)
            screen.blit(temp_surface, (self.x - self.size, self.y - self.size))

class IntroCinematica:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()  # Inicializar el mixer de audio
        
        self.screen_width = 1000
        self.screen_height = 700
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("🍎 La Tierra de las Manzanas - Intro")
        
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Cargar y reproducir música de fondo
        self.load_background_music()
        
        # Colores
        self.bg_color = (45, 25, 85)  # Morado oscuro
        self.text_color = (255, 255, 255)  # Blanco
        self.title_color = (255, 215, 0)  # Dorado
        
        # Fuentes
        self.title_font = pygame.font.Font(None, 64)
        self.text_font = pygame.font.Font(None, 32)
        self.button_font = pygame.font.Font(None, 36)
        
        # Sistema de partículas
        self.particles = [Particle(random.uniform(0, self.screen_width), 
                                 random.uniform(0, self.screen_height)) for _ in range(50)]
        
        # Historia dividida en fragmentos cinematográficos
        self.story_fragments = [
            "En un rincón soleado del valle, rodeado de montañas y árboles frutales,",
            "existía un pequeño huerto de manzanas donde la vida era tranquila",
            "y dulce como la miel.",
            "",
            "Allí vivían Adán, Juan y María.",
            "",
            "Pero no te confundas...",
            "",
            "Aunque Adán y Juan eran fuertes y trabajadores,",
            "la verdadera líder del huerto era María",
            "—una mujer decidida, inteligente y con el corazón más grande del mundo.",
            "",
            "Bajo su guía, los tres cuidaban los manzanos,",
            "cosechaban frutas jugosas y compartían risas",
            "desde el amanecer hasta el atardecer.",
            "",
            "Cada día era una fiesta de colores, sabores y amistad.",
            "",
            "Todo parecía perfecto...",
            "",
            "Hasta que un día...",
            "",
            "Desde lo profundo del bosque, llegó una figura misteriosa:",
            "un chamán encapuchado, montado en una vieja carreta",
            "tirada por un caballo oscuro.",
            "",
            "Sin previo aviso, el chamán lanzó una nube de polvo extraño...",
            "y secuestró a María.",
            "",
            "Adán y Juan, aún atónitos, no pudieron hacer nada.",
            "La carreta se perdió entre la neblina del bosque.",
            "",
            "El huerto, que antes rebosaba de vida, quedó en silencio.",
            "",
            "Pero una cosa era segura:",
            "",
            "Adán y Juan harían todo lo posible para traer de vuelta",
            "a su jefa... su amiga... su familia."
        ]
        
        # Estado de la intro
        self.current_fragment = 0
        self.fragment_timer = 0
        self.fragment_display_time = 120  # 2 segundos a 60 FPS
        self.intro_complete = False
        self.show_menu = False
        
        # Botones del menú
        self.buttons = {
            'jugar': pygame.Rect(self.screen_width//2 - 100, 400, 200, 50),
            'creditos': pygame.Rect(self.screen_width//2 - 100, 470, 200, 50),
            'salir': pygame.Rect(self.screen_width//2 - 100, 540, 200, 50)
        }
        
        self.selected_button = 'jugar'
        self.character_selection = False
        self.selected_character = None
        
    def load_background_music(self):
        """Carga y reproduce la música de fondo de la intro"""
        try:
            audio = get_audio_manager()
            audio.play_music("Melodia_Interfaz_intro", loop=-1)
            print("✅ Música de intro reproduciéndose")
        except Exception as e:
            print(f"⚠️ Error con AudioManager: {e}")
        
    def show_loading_screen(self, screen, selected_character):
        """Muestra pantalla de carga REAL mientras descarga assets del juego"""
        font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 24)
        
        # Lista de assets que necesita el juego con sus URLs
        assets_to_load = [
            {
                "name": "Escenario Nivel 1",
                "url": "https://github.com/user-attachments/assets/00593769-04d2-4083-a4dc-261e6a3fb3e6",
                "filename": "nivel1_escenario.cache"
            },
            {
                "name": "Sprites de Juan",
                "url": "https://github.com/user-attachments/assets/99c2f1aa-aa9e-45b7-9fc0-a4c4b7e63f8c",
                "filename": "juan_sprites.cache"
            },
            {
                "name": "Sprites de Adán", 
                "url": "https://github.com/user-attachments/assets/92e3b5b0-aece-4ab9-8e5a-a9b1a1c50a02",
                "filename": "adan_sprites.cache"
            },
            {
                "name": "Enemigos Worm",
                "url": "https://github.com/user-attachments/assets/6aa0e088-9a4b-42fe-bb58-65bfe2b84a5a", 
                "filename": "worm_enemy.cache"
            }
        ]
        
        total_assets = len(assets_to_load)
        loaded_assets = 0
        
        for i, asset in enumerate(assets_to_load):
            # Actualizar pantalla antes de cargar cada asset
            screen.fill((0, 0, 0))
            
            # Calcular progreso
            progress = i / total_assets
            
            # Título
            title_text = font.render(f"Cargando Nivel 1 - {selected_character.upper()}", True, (255, 255, 255))
            title_rect = title_text.get_rect(center=(screen.get_width()//2, 200))
            screen.blit(title_text, title_rect)
            
            # Estado actual
            state_text = small_font.render(f"Descargando: {asset['name']}...", True, (200, 200, 200))
            state_rect = state_text.get_rect(center=(screen.get_width()//2, 250))
            screen.blit(state_text, state_rect)
            
            # Barra de progreso
            bar_width = 400
            bar_height = 20
            bar_x = (screen.get_width() - bar_width) // 2
            bar_y = 300
            
            # Fondo de la barra
            pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
            
            # Progreso
            progress_width = int(bar_width * progress)
            pygame.draw.rect(screen, (0, 255, 100), (bar_x, bar_y, progress_width, bar_height))
            
            # Borde de la barra
            pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)
            
            # Porcentaje
            percent_text = small_font.render(f"{int(progress * 100)}%", True, (255, 255, 255))
            percent_rect = percent_text.get_rect(center=(screen.get_width()//2, bar_y + 40))
            screen.blit(percent_text, percent_rect)
            
            pygame.display.flip()
            
            # DESCARGA REAL del asset
            try:
                print(f"📥 Descargando {asset['name']}...")
                response = requests.get(asset['url'], timeout=30)
                response.raise_for_status()
                
                # Guardar en caché para futuras cargas más rápidas
                with open(asset['filename'], 'wb') as f:
                    f.write(response.content)
                
                print(f"✅ {asset['name']} descargado ({len(response.content)} bytes)")
                loaded_assets += 1
                
            except Exception as e:
                print(f"⚠️ Error descargando {asset['name']}: {e}")
                # Continuar con el siguiente asset
            
            # Procesar eventos para evitar que se cuelgue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
        
        # Mostrar carga completa
        screen.fill((0, 0, 0))
        
        # Título
        title_text = font.render(f"Nivel 1 - {selected_character.upper()} LISTO", True, (0, 255, 0))
        title_rect = title_text.get_rect(center=(screen.get_width()//2, 200))
        screen.blit(title_text, title_rect)
        
        # Estado final
        state_text = small_font.render("¡Todos los assets cargados! Iniciando juego...", True, (200, 255, 200))
        state_rect = state_text.get_rect(center=(screen.get_width()//2, 250))
        screen.blit(state_text, state_rect)
        
        # Barra completa
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 100), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)
        
        # 100%
        percent_text = small_font.render("100%", True, (255, 255, 255))
        percent_rect = percent_text.get_rect(center=(screen.get_width()//2, bar_y + 40))
        screen.blit(percent_text, percent_rect)
        
        # Efecto de partículas de éxito
        for _ in range(30):
            x = random.randint(bar_x, bar_x + bar_width)
            y = random.randint(bar_y - 10, bar_y + bar_height + 10)
            color = (random.randint(100, 255), random.randint(200, 255), random.randint(100, 255))
            pygame.draw.circle(screen, color, (x, y), random.randint(2, 5))
        
        pygame.display.flip()
        pygame.time.wait(1000)  # Mostrar resultado por 1 segundo
        
        return True
        
    def handle_events(self):
        """Maneja eventos de la intro"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            elif event.type == pygame.KEYDOWN:
                if not self.intro_complete:
                    # Saltar intro con cualquier tecla
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        self.intro_complete = True
                        self.show_menu = True
                elif self.show_menu and not self.character_selection:
                    # Navegación del menú principal
                    if event.key == pygame.K_UP:
                        buttons = list(self.buttons.keys())
                        current_index = buttons.index(self.selected_button)
                        self.selected_button = buttons[(current_index - 1) % len(buttons)]
                    elif event.key == pygame.K_DOWN:
                        buttons = list(self.buttons.keys())
                        current_index = buttons.index(self.selected_button)
                        self.selected_button = buttons[(current_index + 1) % len(buttons)]
                    elif event.key == pygame.K_RETURN:
                        if self.selected_button == 'jugar':
                            self.character_selection = True
                            self.selected_character = 'juan'
                        elif self.selected_button == 'creditos':
                            return 'creditos'
                        elif self.selected_button == 'salir':
                            return 'quit'
                elif self.character_selection:
                    # Selección de personaje
                    if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                        self.selected_character = 'adan' if self.selected_character == 'juan' else 'juan'
                    elif event.key == pygame.K_RETURN:
                        # Mostrar pantalla de carga antes de iniciar el juego
                        if self.show_loading_screen(self.screen, self.selected_character):
                            return f'start_game_{self.selected_character}'
                        else:
                            return 'exit'
                    elif event.key == pygame.K_ESCAPE:
                        self.character_selection = False
        return 'continue'
    
    def update(self):
        """Actualiza la lógica de la intro"""
        # Actualizar partículas
        for particle in self.particles:
            particle.update()
        
        # Actualizar progreso de la historia
        if not self.intro_complete:
            self.fragment_timer += 1
            if self.fragment_timer >= self.fragment_display_time:
                self.fragment_timer = 0
                self.current_fragment += 1
                
                if self.current_fragment >= len(self.story_fragments):
                    self.intro_complete = True
                    self.show_menu = True
    
    def draw_particles(self):
        """Dibuja las partículas amarillentas"""
        for particle in self.particles:
            particle.draw(self.screen)
    
    def draw_story(self):
        """Dibuja el fragmento actual de la historia"""
        if self.current_fragment < len(self.story_fragments):
            text = self.story_fragments[self.current_fragment]
            if text.strip():  # Solo dibujar si no es línea vacía
                # Dividir texto largo en múltiples líneas
                words = text.split()
                lines = []
                current_line = ""
                
                for word in words:
                    test_line = current_line + " " + word if current_line else word
                    text_surface = self.text_font.render(test_line, True, self.text_color)
                    if text_surface.get_width() > self.screen_width - 100:
                        lines.append(current_line)
                        current_line = word
                    else:
                        current_line = test_line
                lines.append(current_line)
                
                # Centrar las líneas
                total_height = len(lines) * 40
                start_y = self.screen_height // 2 - total_height // 2
                
                for i, line in enumerate(lines):
                    text_surface = self.text_font.render(line, True, self.text_color)
                    text_rect = text_surface.get_rect(center=(self.screen_width//2, start_y + i * 40))
                    self.screen.blit(text_surface, text_rect)
        
        # Indicador para continuar
        if self.current_fragment < len(self.story_fragments) - 1:
            continue_text = self.text_font.render("Presiona ESPACIO para continuar...", True, (200, 200, 200))
            continue_rect = continue_text.get_rect(center=(self.screen_width//2, self.screen_height - 50))
            self.screen.blit(continue_text, continue_rect)
    
    def draw_menu(self):
        """Dibuja el menú principal"""
        # Título
        title_surface = self.title_font.render("🍎 La Tierra de las Manzanas", True, self.title_color)
        title_rect = title_surface.get_rect(center=(self.screen_width//2, 150))
        self.screen.blit(title_surface, title_rect)
        
        # Botones
        for button_name, button_rect in self.buttons.items():
            # Color del botón según selección
            if button_name == self.selected_button:
                button_color = (100, 60, 140)  # Morado más claro
                text_color = self.title_color
            else:
                button_color = (60, 40, 100)  # Morado oscuro
                text_color = self.text_color
            
            # Dibujar botón
            pygame.draw.rect(self.screen, button_color, button_rect)
            pygame.draw.rect(self.screen, text_color, button_rect, 2)
            
            # Texto del botón
            button_text = button_name.upper()
            text_surface = self.button_font.render(button_text, True, text_color)
            text_rect = text_surface.get_rect(center=button_rect.center)
            self.screen.blit(text_surface, text_rect)
        
        # Instrucciones
        instructions = ["↑↓ - Navegar", "ENTER - Seleccionar"]
        for i, instruction in enumerate(instructions):
            text_surface = self.text_font.render(instruction, True, (180, 180, 180))
            text_rect = text_surface.get_rect(center=(self.screen_width//2, 620 + i * 30))
            self.screen.blit(text_surface, text_rect)
    
    def draw_character_selection(self):
        """Dibuja la selección de personaje"""
        # Título
        title_surface = self.title_font.render("Elige tu personaje", True, self.title_color)
        title_rect = title_surface.get_rect(center=(self.screen_width//2, 150))
        self.screen.blit(title_surface, title_rect)
        
        # Opciones de personajes
        characters = [
            {'name': 'juan', 'display': 'JUAN', 'desc': 'Maestro del combate combo'},
            {'name': 'adan', 'display': 'ADÁN', 'desc': 'Especialista en ataques a distancia'}
        ]
        
        for i, char in enumerate(characters):
            x_pos = self.screen_width//2 + (i - 0.5) * 200
            y_pos = 350
            
            # Rectángulo del personaje
            char_rect = pygame.Rect(x_pos - 80, y_pos - 60, 160, 120)
            
            if char['name'] == self.selected_character:
                char_color = (100, 60, 140)
                text_color = self.title_color
            else:
                char_color = (60, 40, 100)
                text_color = self.text_color
            
            # Dibujar selección
            pygame.draw.rect(self.screen, char_color, char_rect)
            pygame.draw.rect(self.screen, text_color, char_rect, 3)
            
            # Nombre del personaje
            name_surface = self.button_font.render(char['display'], True, text_color)
            name_rect = name_surface.get_rect(center=(x_pos, y_pos - 20))
            self.screen.blit(name_surface, name_rect)
            
            # Descripción
            desc_surface = self.text_font.render(char['desc'], True, text_color)
            desc_rect = desc_surface.get_rect(center=(x_pos, y_pos + 10))
            self.screen.blit(desc_surface, desc_rect)
        
        # Instrucciones
        instructions = ["← → - Cambiar personaje", "ENTER - Comenzar", "ESC - Volver"]
        for i, instruction in enumerate(instructions):
            text_surface = self.text_font.render(instruction, True, (180, 180, 180))
            text_rect = text_surface.get_rect(center=(self.screen_width//2, 500 + i * 30))
            self.screen.blit(text_surface, text_rect)
    
    def draw(self):
        """Dibuja toda la intro"""
        # Fondo morado
        self.screen.fill(self.bg_color)
        
        # Partículas amarillentas
        self.draw_particles()
        
        if not self.intro_complete:
            # Mostrar historia
            self.draw_story()
        elif self.character_selection:
            # Mostrar selección de personaje
            self.draw_character_selection()
        elif self.show_menu:
            # Mostrar menú principal
            self.draw_menu()
        
        pygame.display.flip()
    
    def run(self):
        """Bucle principal de la intro"""
        print("🎬 Iniciando intro cinematográfica...")
        
        running = True
        while running:
            result = self.handle_events()
            
            if result == 'quit':
                running = False
                return 'quit'
            elif result == 'creditos':
                running = False
                return 'creditos'
            elif result.startswith('start_game_'):
                character = result.split('_')[-1]
                running = False
                return f'start_game_{character}'
            
            self.update()
            self.draw()
            self.clock.tick(self.fps)
        
        return 'quit'

if __name__ == "__main__":
    intro = IntroCinematica()
    result = intro.run()
    print(f"Resultado de la intro: {result}")
    pygame.quit()
    sys.exit()