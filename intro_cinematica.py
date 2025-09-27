import pygame
import sys
import random
import math
import time
from audio_manager import get_audio_manager

class Particle:
    def __init__(self, x, y, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
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
        self.x = random.uniform(0, self.screen_width)  # Responsive a resolución actual
        self.y = random.uniform(self.screen_height, self.screen_height + 70)  # Responsive a resolución actual
        self.alpha = random.uniform(100, 255)
        self.size = random.uniform(3, 9)  # Partículas más grandes
    
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
        
        # Detección automática de resolución
        info = pygame.display.Info()
        self.screen_width = info.current_w
        self.screen_height = info.current_h
        
        # Asegurar un tamaño mínimo
        if self.screen_width < 800:
            self.screen_width = 800
        if self.screen_height < 600:
            self.screen_height = 600
        
        print(f"🖥️ Resolución detectada: {self.screen_width}x{self.screen_height}")
        
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        pygame.display.set_caption("🍎 La Tierra de las Manzanas - Intro")
        
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Factores de escala basados en resolución base (1920x1080)
        self.scale_x = self.screen_width / 1920.0
        self.scale_y = self.screen_height / 1080.0
        self.scale_factor = min(self.scale_x, self.scale_y)  # Escalar proporcionalmente
        
        print(f"📏 Factores de escala: X={self.scale_x:.2f}, Y={self.scale_y:.2f}, Factor={self.scale_factor:.2f}")
        
        # Cargar y reproducir música de fondo
        self.load_background_music()
        
        # Sistema de narrador con archivo unificado
        self.narrator_audio = None
        self.narrator_playing = False
        self.load_narrator_audio()
        
        # Colores
        self.bg_color = (45, 25, 85)  # Morado oscuro
        self.text_color = (255, 255, 255)  # Blanco
        self.title_color = (255, 215, 0)  # Dorado
        
        # Fuentes escaladas responsivamente
        base_title_size = 128
        base_text_size = 64
        base_button_size = 72
        
        self.title_font = pygame.font.Font(None, int(base_title_size * self.scale_factor))
        self.text_font = pygame.font.Font(None, int(base_text_size * self.scale_factor))
        self.button_font = pygame.font.Font(None, int(base_button_size * self.scale_factor))
        
        print(f"📝 Tamaños de fuente: Título={int(base_title_size * self.scale_factor)}, "
              f"Texto={int(base_text_size * self.scale_factor)}, "
              f"Botón={int(base_button_size * self.scale_factor)}")
        
        # Sistema de partículas escalado
        num_particles = max(30, int(50 * self.scale_factor))
        self.particles = [Particle(random.uniform(0, self.screen_width), 
                                 random.uniform(0, self.screen_height), 
                                 self.screen_width, self.screen_height) 
                         for _ in range(num_particles)]
        
        # Historia dividida en fragmentos cinematográficos - VERSIÓN CALIBRADA
        # Cada entrada tiene: [texto, tiempo_inicio_segundos, tiempo_fin_segundos]
        # NOTA: Timestamps calibrados con narrator_calibrator.py usando archivo completo
        self.story_fragments = [
            ["En un rincón soleado del valle, rodeado de montañas y árboles frutales,", 0.0, 4.5],
            ["existía un pequeño huerto de manzanas donde la vida era tranquila", 4.5, 8.6],
            ["y dulce como la miel.", 8.6, 9.9],
            ["Allí vivían Adán, Juan y María.", 9.9, 13.2],
            ["Pero no te confundas...", 13.2, 14.8],
            ["Aunque Adán y Juan eran fuertes y trabajadores,", 14.8, 18.1],
            ["la verdadera líder del huerto era María", 18.1, 20.8],
            ["Bajo su guía, los tres cuidaban los manzanos,", 20.8, 23.8],
            ["cosechaban frutas y compartían risas", 23.8, 26.5],
            ["hasta el amanecer.", 26.5, 27.7],
            ["Cada día era una fiesta de colores, sabores y amistad.", 27.7, 32.0],
            ["Todo parecía perfecto...", 32.0, 33.5],
            ["Hasta que un día...", 33.5, 35.2],
            ["Desde lo profundo del bosque, llegó una figura misteriosa:", 35.2, 39.2],
            ["un chamán encapuchado, montado en una vieja carreta", 39.2, 43.3],
            ["tirada por un caballo oscuro.", 43.3, 44.4],
            ["Sin previo aviso, el chamán lanzó una nube de polvo extraño...", 44.4, 50.0],
            ["y secuestró a María.", 50.0, 51.8],
            ["Adán y Juan, aún atónitos, no pudieron hacer nada.", 51.8, 56.3],
            ["La carreta se perdió entre la neblina del bosque.", 56.3, 58.9],
            ["El huerto, que antes rebosaba de vida, quedó en silencio.", 58.9, 62.3],
            ["Pero una cosa era segura:", 62.3, 64.4],
            ["Adán y Juan harían todo lo posible para traer de vuelta", 64.4, 67.9],
            ["a su jefa... su amiga... su familia.", 67.9, 71.3],
        ]

        # Duración total del narrador (actualizada según calibración completa)
        self.narrator_total_duration = 71.3  # Calibración completa
        
        # Estado de la intro
        self.current_fragment = 0
        self.narrator_start_time = None  # Tiempo cuando inició el narrador
        self.intro_complete = False
        self.show_menu = False
        
        # Botones del menú escalados responsivamente
        button_y_start = int(self.screen_height * 0.55)  # 55% de la altura
        button_spacing = int(120 * self.scale_factor)  # Espaciado escalado
        button_width = int(500 * self.scale_factor)
        button_height = int(80 * self.scale_factor)
        
        self.buttons = {
            'jugar': pygame.Rect(self.screen_width//2 - button_width//2, button_y_start, button_width, button_height),
            'salir': pygame.Rect(self.screen_width//2 - button_width//2, button_y_start + button_spacing, button_width, button_height)
        }
        
        print(f"🎛️ Botones configurados: {button_width}x{button_height} en posición Y={button_y_start}")
        
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
    
    def load_narrator_audio(self):
        """Carga el audio del narrador unificado"""
        try:
            audio = get_audio_manager()
            # Precargar el audio del narrador unificado pero no reproducirlo aún
            narrator_path = "sounds/music/Audio narrador del juego intro, COMPLETO.mp3"
            pygame.mixer.music.load(narrator_path)
            print("� Audio de historia cargado")
        except Exception as e:
            print(f"⚠️ Error cargando audio: {e}")
    
    def start_narrator(self):
        """Inicia la reproducción del audio del narrador unificado"""
        try:
            if not self.narrator_playing:
                # Detener música de fondo temporalmente
                audio = get_audio_manager()
                audio.stop_music()
                
                # Reproducir narrador unificado
                narrator_path = "sounds/music/Audio narrador del juego intro, COMPLETO.mp3"
                pygame.mixer.music.load(narrator_path)
                pygame.mixer.music.play()
                self.narrator_playing = True
                self.narrator_start_time = time.time()
                
                print("🎙️ Historia iniciada")
        except Exception as e:
            print(f"⚠️ Error reproduciendo audio: {e}")
    
    def stop_narrator(self):
        """Detiene el audio del narrador y restaura la música de fondo"""
        try:
            if self.narrator_playing:
                pygame.mixer.music.stop()
                self.narrator_playing = False
                self.narrator_start_time = None  # Reset del tiempo
                
                # Restaurar música de fondo
                audio = get_audio_manager()
                audio.play_music("Melodia_Interfaz_intro", loop=-1)
                print("🎙️ Historia completada")
        except Exception as e:
            print(f"⚠️ Error deteniendo audio: {e}")
    
    def is_narrator_playing(self):
        """Verifica si el narrador está reproduciendo"""
        return pygame.mixer.music.get_busy() and self.narrator_playing
    
    def get_current_fragment_by_time(self):
        """Obtiene el fragmento actual basado en el tiempo transcurrido del narrador"""
        if not self.narrator_playing or self.narrator_start_time is None:
            return 0
        
        elapsed_time = time.time() - self.narrator_start_time
        
        # Buscar el fragmento correspondiente al tiempo actual
        for i, fragment_data in enumerate(self.story_fragments):
            text, start_time, end_time = fragment_data
            if start_time <= elapsed_time < end_time:
                return i
        
        # Si estamos entre fragmentos (en una pausa), buscar el siguiente fragmento
        for i, fragment_data in enumerate(self.story_fragments):
            text, start_time, end_time = fragment_data
            if elapsed_time < start_time:
                # Estamos antes de este fragmento, mostrar el anterior si existe
                return max(0, i - 1)
        
        # Si hemos pasado todos los fragmentos, retornar el último índice
        if elapsed_time >= self.narrator_total_duration:
            return len(self.story_fragments)
        
        # Por defecto, retornar el último fragmento válido
        return len(self.story_fragments) - 1
    
    def get_current_fragment_text(self):
        """Obtiene el texto del fragmento actual"""
        fragment_index = self.get_current_fragment_by_time()
        if 0 <= fragment_index < len(self.story_fragments):
            text = self.story_fragments[fragment_index][0]
            # Solo retornar texto si no está vacío (evitar pausas)
            return text if text.strip() else ""
        return ""
        
    def show_loading_screen(self, screen, selected_character):
        """Muestra una transición elegante antes de iniciar el juego"""
        font = pygame.font.Font(None, 96)  # 2x escalado
        small_font = pygame.font.Font(None, 64)  # 2x escalado
        
        # Efecto de transición con fade
        for alpha in range(0, 255, 15):  # Fade in
            screen.fill((0, 0, 0))
            
            # Título principal
            title_text = font.render(f"Iniciando Nivel 1", True, (255, 255, 255))
            title_rect = title_text.get_rect(center=(screen.get_width()//2, 280))
            screen.blit(title_text, title_rect)
            
            # Personaje seleccionado
            char_text = small_font.render(f"Personaje: {selected_character.upper()}", True, (255, 215, 0))
            char_rect = char_text.get_rect(center=(screen.get_width()//2, 340))
            screen.blit(char_text, char_rect)
            
            # Mensaje motivacional
            message_text = small_font.render("¡Prepárate para rescatar a María!", True, (200, 255, 200))
            message_rect = message_text.get_rect(center=(screen.get_width()//2, 380))
            screen.blit(message_text, message_rect)
            
            # Efecto de partículas doradas
            for _ in range(20):
                x = random.randint(100, screen.get_width() - 100)
                y = random.randint(200, 500)
                size = random.randint(2, 6)
                color = (255, 215, 0, min(alpha, 200))
                # Crear superficie temporal para alpha
                temp_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surface, color, (size, size), size)
                screen.blit(temp_surface, (x - size, y - size))
            
            pygame.display.flip()
            pygame.time.wait(50)  # 50ms por frame = transición suave
            
            # Procesar eventos para evitar que se cuelgue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
        
        # Pausa final antes de iniciar
        pygame.time.wait(800)  # 0.8 segundos
        
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
                        # Detener narrador al saltar intro
                        self.stop_narrator()
                        self.intro_complete = True
                        self.show_menu = True
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
            # Iniciar narrador al comenzar el primer fragmento
            if self.current_fragment == 0 and not self.narrator_playing:
                self.start_narrator()
            
            # Actualizar fragmento basado en tiempo del narrador
            if self.narrator_playing and self.narrator_start_time:
                elapsed_time = time.time() - self.narrator_start_time
                new_fragment = self.get_current_fragment_by_time()
                
                # Cambiar fragmento si es necesario
                if new_fragment != self.current_fragment:
                    self.current_fragment = new_fragment
                    if self.current_fragment < len(self.story_fragments):
                        current_text = self.story_fragments[self.current_fragment][0]
                        if current_text.strip():  # Solo mostrar si no es una pausa vacía
                            print(f"📖 Fragmento {self.current_fragment + 1}: '{current_text[:50]}...'")
                
                # Verificar si el narrador debería haber terminado según la duración total
                if elapsed_time >= self.narrator_total_duration:
                    print("✅ Historia completada")
                    self.stop_narrator()
                    self.intro_complete = True
                    self.show_menu = True
                    return
                
                # Verificar si hemos pasado todos los fragmentos
                if self.current_fragment >= len(self.story_fragments):
                    print("📚 Todos los fragmentos completados")
                    self.stop_narrator()
                    self.intro_complete = True
                    self.show_menu = True
                    return
        
        # Verificar si el narrador terminó de reproducir naturalmente (backup check)
        if self.narrator_playing and not self.is_narrator_playing():
            print("🔊 Audio del narrador terminó de reproducirse")
            self.stop_narrator()
            if not self.intro_complete:
                self.intro_complete = True
                self.show_menu = True
    
    def draw_particles(self):
        """Dibuja las partículas amarillentas"""
        for particle in self.particles:
            particle.draw(self.screen)
    
    def draw_story(self):
        """Dibuja el fragmento actual de la historia sincronizado con el narrador"""
        current_text = self.get_current_fragment_text()
        
        if current_text and current_text.strip():  # Solo dibujar si no es línea vacía
            # Dividir texto largo en múltiples líneas
            words = current_text.split()
            lines = []
            current_line = ""
            
            # Margen responsivo
            margin = int(100 * self.scale_factor)
            max_width = self.screen_width - margin
            
            for word in words:
                test_line = current_line + " " + word if current_line else word
                text_surface = self.text_font.render(test_line, True, self.text_color)
                if text_surface.get_width() > max_width:
                    lines.append(current_line)
                    current_line = word
                else:
                    current_line = test_line
            lines.append(current_line)
            
            # Centrar las líneas con espaciado escalado
            line_spacing = int(40 * self.scale_factor)
            total_height = len(lines) * line_spacing
            start_y = self.screen_height // 2 - total_height // 2
            
            for i, line in enumerate(lines):
                text_surface = self.text_font.render(line, True, self.text_color)
                text_rect = text_surface.get_rect(center=(self.screen_width//2, start_y + i * line_spacing))
                self.screen.blit(text_surface, text_rect)
        
        # Indicador para continuar o saltar (posición escalada)
        if self.narrator_playing:
            skip_text = self.text_font.render("Presiona ESPACIO para saltar narración...", True, (200, 200, 200))
            skip_rect = skip_text.get_rect(center=(self.screen_width//2, self.screen_height - int(50 * self.scale_factor)))
            self.screen.blit(skip_text, skip_rect)
        
        # Indicador de historia removido para interfaz más limpia
        
        # Mostrar información de sincronización (solo para debug - comentar para versión final)
        # if self.narrator_playing and self.narrator_start_time:
        #     elapsed = time.time() - self.narrator_start_time
        #     debug_font = pygame.font.Font(None, 20)
        #     debug_text = debug_font.render(f"Tiempo: {elapsed:.1f}s | Fragmento: {self.current_fragment}", True, (100, 100, 100))
        #     self.screen.blit(debug_text, (10, self.screen_height - 30))
    
    # Función eliminada - draw_narrator_indicator no es necesaria
    # def draw_narrator_indicator(self):
    #     """Función removida para interface más limpia"""
    #     pass
    
    def draw_menu(self):
        """Dibuja el menú principal con elementos escalados"""
        # Título responsive
        title_surface = self.title_font.render("🍎 La Tierra de las Manzanas", True, self.title_color)
        title_y = int(150 * self.scale_factor)
        title_rect = title_surface.get_rect(center=(self.screen_width//2, title_y))
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
        
        # Instrucciones con posición escalada más arriba y mayor espaciado
        instructions = ["↑↓ - Navegar", "ENTER - Seleccionar"]
        instructions_y = int(500 * self.scale_factor)
        instruction_spacing = int(50 * self.scale_factor)  # Aumentado de 30 a 50
        for i, instruction in enumerate(instructions):
            text_surface = self.text_font.render(instruction, True, (180, 180, 180))
            text_rect = text_surface.get_rect(center=(self.screen_width//2, instructions_y + i * instruction_spacing))
            self.screen.blit(text_surface, text_rect)
    
    def draw_character_selection(self):
        """Dibuja la selección de personaje con elementos escalados"""
        # Título principal responsive
        title_surface = self.title_font.render("Elige tu Héroe", True, self.title_color)
        title_y = int(200 * self.scale_factor)
        title_rect = title_surface.get_rect(center=(self.screen_width//2, title_y))
        self.screen.blit(title_surface, title_rect)
        
        # Subtítulo responsive
        subtitle_surface = self.text_font.render("Cada personaje tiene habilidades únicas", True, (200, 200, 200))
        subtitle_y = int(280 * self.scale_factor)
        subtitle_rect = subtitle_surface.get_rect(center=(self.screen_width//2, subtitle_y))
        self.screen.blit(subtitle_surface, subtitle_rect)
        
        # Opciones de personajes mejoradas
        characters = [
            {
                'name': 'juan', 
                'display': 'JUAN',
                'line1': 'Guerrero a Distancia',
                'line2': 'Ágil',
                'emoji': '⚔️'
            },
            {
                'name': 'adan', 
                'display': 'ADÁN',
                'line1': 'Guerrero Cuerpo a Cuerpo',
                'line2': 'Fuerte',
                'emoji': '🏹'
            }
        ]
        
        # Posicionamiento en dos columnas escalado
        card_width = int(400 * self.scale_factor)
        card_height = int(180 * self.scale_factor)
        spacing = int(150 * self.scale_factor)
        start_x = (self.screen_width - (2 * card_width + spacing)) // 2
        card_y = int(400 * self.scale_factor)
        
        for i, char in enumerate(characters):
            x_pos = start_x + (i * (card_width + spacing))
            
            # Rectángulo de selección
            char_rect = pygame.Rect(x_pos, card_y, card_width, card_height)
            
            # Color según selección
            is_selected = char['name'] == self.selected_character
            
            if is_selected:
                border_color = (255, 215, 0)  # Dorado
                bg_color = (100, 60, 20)  # Marrón
                text_color = self.title_color
            else:
                border_color = (120, 120, 120)
                bg_color = (40, 40, 40)
                text_color = self.text_color
            
            # Fondo de la carta
            pygame.draw.rect(self.screen, bg_color, char_rect)
            pygame.draw.rect(self.screen, border_color, char_rect, 4)
            
            # Emoji del personaje escalado
            emoji_size = int(80 * self.scale_factor)
            emoji_font = pygame.font.Font(None, emoji_size)
            emoji_surface = emoji_font.render(char['emoji'], True, self.title_color)
            emoji_y = char_rect.y + int(40 * self.scale_factor)
            emoji_rect = emoji_surface.get_rect(center=(char_rect.centerx, emoji_y))
            self.screen.blit(emoji_surface, emoji_rect)
            
            # Nombre del personaje escalado
            name_surface = self.button_font.render(char['display'], True, text_color)
            name_y = char_rect.y + int(90 * self.scale_factor)
            name_rect = name_surface.get_rect(center=(char_rect.centerx, name_y))
            self.screen.blit(name_surface, name_rect)
            
            # Primera línea de descripción escalada
            line1_surface = self.text_font.render(char['line1'], True, text_color)
            line1_y = char_rect.y + int(125 * self.scale_factor)
            line1_rect = line1_surface.get_rect(center=(char_rect.centerx, line1_y))
            self.screen.blit(line1_surface, line1_rect)
            
            # Segunda línea de descripción escalada
            small_text_size = int(48 * self.scale_factor)
            small_text_font = pygame.font.Font(None, small_text_size)
            line2_surface = small_text_font.render(char['line2'], True, (180, 180, 180))
            line2_y = char_rect.y + int(155 * self.scale_factor)
            line2_rect = line2_surface.get_rect(center=(char_rect.centerx, line2_y))
            self.screen.blit(line2_surface, line2_rect)
        
        # Instrucciones mejoradas con posición escalada
        instructions_y = int(700 * self.scale_factor)
        instructions = ["← → - Cambiar Héroe", "ENTER - Comenzar Aventura", "ESC - Menú Principal"]
        instruction_spacing = int(50 * self.scale_factor)
        for i, instruction in enumerate(instructions):
            text_surface = self.text_font.render(instruction, True, (200, 200, 200))
            text_rect = text_surface.get_rect(center=(self.screen_width//2, instructions_y + i * instruction_spacing))
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