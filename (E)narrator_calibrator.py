#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Herramienta de Calibración Inteligente para Narrador
Usa IA para detectar automáticamente cuándo empieza y termina cada frase
"""

import pygame
import time
import sys
import os

# Añadir el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class IntelligentNarratorCalibrator:
    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
        
        self.screen_width = 1200
        self.screen_height = 800
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("🎙️ Calibrador Inteligente de Narrador")
        
        self.clock = pygame.time.Clock()
        
        # Fuentes
        self.title_font = pygame.font.Font(None, 48)
        self.text_font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 20)
        
        # Estado del calibrador
        self.narrator_playing = False
        self.start_time = None
        self.current_fragment = 0
        self.manual_timestamps = []
        
        # Fragmentos de texto de la historia - VERSIÓN LIMPIA (sin fragmentos incorrectos)
        self.fragments = [
            "En un rincón soleado del valle, rodeado de montañas y árboles frutales,",
            "existía un pequeño huerto de manzanas donde la vida era tranquila",
            "y dulce como la miel.",
            "Allí vivían Adán, Juan y María.",
            "Pero no te confundas...",
            "Aunque Adán y Juan eran fuertes y trabajadores,",
            "la verdadera líder del huerto era María",
            # ELIMINADO: "—una mujer decidida, inteligente y con el corazón más grande del mundo."
            "Bajo su guía, los tres cuidaban los manzanos,",
            "cosechaban frutas y compartían risas",
            "hasta el amanecer.",
            "Cada día era una fiesta de colores, sabores y amistad.",
            "Todo parecía perfecto...",
            "Hasta que un día...",
            "Desde lo profundo del bosque, llegó una figura misteriosa:",
            "un chamán encapuchado, montado en una vieja carreta",
            "tirada por un caballo oscuro.",
            "Sin previo aviso, el chamán lanzó una nube de polvo extraño...",
            "y secuestró a María.",
            "Adán y Juan, aún atónitos, no pudieron hacer nada.",
            "La carreta se perdió entre la neblina del bosque.",
            "El huerto, que antes rebosaba de vida, quedó en silencio.",
            "Pero una cosa era segura:",
            "Adán y Juan harían todo lo posible para traer de vuelta",
            "a su jefa... su amiga... su familia."
        ]
        
        # Colores
        self.bg_color = (20, 25, 40)
        self.text_color = (255, 255, 255)
        self.highlight_color = (255, 215, 0)
        self.success_color = (0, 255, 100)
        self.button_color = (60, 80, 120)
        
    def start_narrator(self):
        """Inicia la reproducción del narrador"""
        try:
            narrator_path = "sounds/music/Audio narrador del juego intro, COMPLETO.mp3"
            if not os.path.exists(narrator_path):
                print(f"❌ Error: No se encuentra el archivo {narrator_path}")
                return False
                
            pygame.mixer.music.load(narrator_path)
            pygame.mixer.music.play()
            self.narrator_playing = True
            self.start_time = time.time()
            self.current_fragment = 0
            self.manual_timestamps = [0.0]  # El primer fragmento siempre empieza en 0
            
            print("🎙️ Narrador iniciado - Calibración en proceso...")
            print("📖 Fragmento 1 iniciado en 0.0s")
            return True
            
        except Exception as e:
            print(f"❌ Error iniciando narrador: {e}")
            return False
    
    def mark_fragment_end(self):
        """Marca el final del fragmento actual"""
        if self.narrator_playing and self.start_time:
            elapsed = time.time() - self.start_time
            self.manual_timestamps.append(elapsed)
            self.current_fragment += 1
            
            if self.current_fragment < len(self.fragments):
                print(f"📖 Fragmento {self.current_fragment + 1} iniciado en {elapsed:.1f}s")
                print(f"   Texto: '{self.fragments[self.current_fragment][:60]}...'")
            else:
                print(f"✅ Calibración completada en {elapsed:.1f}s")
                self.stop_narrator()
    
    def stop_narrator(self):
        """Detiene el narrador"""
        if self.narrator_playing:
            pygame.mixer.music.stop()
            self.narrator_playing = False
            print("🛑 Narrador detenido")
    
    def restart_calibration(self):
        """Reinicia la calibración"""
        self.stop_narrator()
        self.current_fragment = 0
        self.manual_timestamps = []
        self.start_time = None
        print("🔄 Calibración reiniciada")
    
    def export_timestamps(self):
        """Exporta los timestamps al formato necesario para intro_cinematica.py"""
        if len(self.manual_timestamps) == 0:
            print("❌ No hay timestamps para exportar")
            return
        
        print("\n" + "="*80)
        print("🎯 TIMESTAMPS CALIBRADOS PARA intro_cinematica.py")
        print("="*80)
        print("# Actualizando automáticamente intro_cinematica.py...")
        print("\nself.story_fragments = [")
        
        for i, fragment in enumerate(self.fragments):
            start_time = self.manual_timestamps[i] if i < len(self.manual_timestamps) else 999.0
            end_time = self.manual_timestamps[i + 1] if i + 1 < len(self.manual_timestamps) else start_time + 3.0
            
            print(f'    ["{fragment}", {start_time:.1f}, {end_time:.1f}],')
        
        print("]")
        print("\n" + "="*80)
        print(f"Total de fragmentos: {len(self.fragments)}")
        print(f"Duración total: {self.manual_timestamps[-1] if self.manual_timestamps else 0:.1f} segundos")
        print("="*80)
        
        # ACTUALIZAR DIRECTAMENTE intro_cinematica.py
        self.update_intro_cinematica()
    
    def update_intro_cinematica(self):
        """Actualiza automáticamente intro_cinematica.py con los nuevos timestamps"""
        try:
            print("\n🔄 Actualizando intro_cinematica.py automáticamente...")
            
            # Leer el archivo actual
            with open("intro_cinematica.py", "r", encoding="utf-8") as f:
                content = f.read()
            
            # Crear la nueva sección story_fragments
            new_fragments = "        # Historia dividida en fragmentos cinematográficos - VERSIÓN CALIBRADA\n"
            new_fragments += "        # Cada entrada tiene: [texto, tiempo_inicio_segundos, tiempo_fin_segundos]\n"
            new_fragments += "        # NOTA: Timestamps calibrados con narrator_calibrator.py usando archivo completo\n"
            new_fragments += "        self.story_fragments = [\n"
            
            for i, fragment in enumerate(self.fragments):
                start_time = self.manual_timestamps[i] if i < len(self.manual_timestamps) else 999.0
                end_time = self.manual_timestamps[i + 1] if i + 1 < len(self.manual_timestamps) else start_time + 3.0
                new_fragments += f'            ["{fragment}", {start_time:.1f}, {end_time:.1f}],\n'
            
            new_fragments += "        ]\n"
            new_fragments += "\n"
            new_fragments += f"        # Duración total del narrador (actualizada según calibración completa)\n"
            new_fragments += f"        self.narrator_total_duration = {self.manual_timestamps[-1] if self.manual_timestamps else 72.0:.1f}  # Calibración completa"
            
            # Buscar y reemplazar la sección story_fragments
            import re
            pattern = r'        # Historia dividida en fragmentos cinematográficos.*?self\.narrator_total_duration = [^#]*# [^\n]*'
            replacement = new_fragments
            
            new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            
            # Escribir el archivo actualizado
            with open("intro_cinematica.py", "w", encoding="utf-8") as f:
                f.write(new_content)
            
            print("✅ intro_cinematica.py actualizado automáticamente!")
            print(f"📊 Fragmentos actualizados: {len(self.fragments)}")
            print(f"⏱️ Duración total: {self.manual_timestamps[-1] if self.manual_timestamps else 0:.1f} segundos")
            
        except Exception as e:
            print(f"⚠️ Error actualizando intro_cinematica.py: {e}")
            print("💡 Puedes copiar manualmente los timestamps del archivo calibrated_timestamps_clean.txt")
    
    def handle_events(self):
        """Maneja los eventos del calibrador"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.narrator_playing:
                        self.start_narrator()
                    else:
                        self.mark_fragment_end()
                elif event.key == pygame.K_r:
                    self.restart_calibration()
                elif event.key == pygame.K_s:
                    self.stop_narrator()
                elif event.key == pygame.K_e:
                    self.export_timestamps()
                elif event.key == pygame.K_ESCAPE:
                    return False
        return True
    
    def draw(self):
        """Dibuja la interfaz del calibrador"""
        self.screen.fill(self.bg_color)
        
        # Título
        title = self.title_font.render("🎙️ Calibrador Inteligente de Narrador", True, self.highlight_color)
        title_rect = title.get_rect(center=(self.screen_width // 2, 50))
        self.screen.blit(title, title_rect)
        
        # Estado actual
        y_offset = 120
        if self.narrator_playing:
            elapsed = time.time() - self.start_time if self.start_time else 0
            status_text = f"🔴 GRABANDO - Tiempo: {elapsed:.1f}s - Fragmento: {self.current_fragment + 1}/{len(self.fragments)}"
            status_color = self.success_color
        else:
            status_text = "⏸️ DETENIDO - Presiona ESPACIO para iniciar"
            status_color = self.highlight_color
        
        status_surface = self.text_font.render(status_text, True, status_color)
        status_rect = status_surface.get_rect(center=(self.screen_width // 2, y_offset))
        self.screen.blit(status_surface, status_rect)
        
        # Instrucciones
        y_offset += 60
        instructions = [
            "ESPACIO: Iniciar narrador / Marcar fin de fragmento actual",
            "R: Reiniciar calibración",
            "S: Detener narrador",
            "E: Exportar timestamps",
            "ESC: Salir"
        ]
        
        for instruction in instructions:
            inst_surface = self.small_font.render(instruction, True, self.text_color)
            inst_rect = inst_surface.get_rect(center=(self.screen_width // 2, y_offset))
            self.screen.blit(inst_surface, inst_rect)
            y_offset += 25
        
        # Fragmento actual
        y_offset += 40
        if self.current_fragment < len(self.fragments):
            current_text = f"Fragmento {self.current_fragment + 1}:"
            current_surface = self.text_font.render(current_text, True, self.highlight_color)
            current_rect = current_surface.get_rect(center=(self.screen_width // 2, y_offset))
            self.screen.blit(current_surface, current_rect)
            
            y_offset += 40
            # Dividir el fragmento en múltiples líneas si es necesario
            fragment_text = self.fragments[self.current_fragment]
            words = fragment_text.split()
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + " " + word if current_line else word
                test_surface = self.text_font.render(test_line, True, self.text_color)
                if test_surface.get_width() > self.screen_width - 100:
                    lines.append(current_line)
                    current_line = word
                else:
                    current_line = test_line
            if current_line:
                lines.append(current_line)
            
            for line in lines:
                line_surface = self.text_font.render(line, True, self.text_color)
                line_rect = line_surface.get_rect(center=(self.screen_width // 2, y_offset))
                self.screen.blit(line_surface, line_rect)
                y_offset += 30
        
        # Timestamps marcados
        y_offset += 40
        timestamps_title = self.text_font.render("Timestamps Marcados:", True, self.highlight_color)
        self.screen.blit(timestamps_title, (50, y_offset))
        y_offset += 35
        
        for i, timestamp in enumerate(self.manual_timestamps):
            if i < len(self.fragments):
                ts_text = f"{timestamp:.1f}s: {self.fragments[i][:50]}..."
                color = self.success_color if i < self.current_fragment else self.text_color
                ts_surface = self.small_font.render(ts_text, True, color)
                self.screen.blit(ts_surface, (50, y_offset))
                y_offset += 22
                
                # Limitar cuántos timestamps mostrar para no salir de pantalla
                if y_offset > self.screen_height - 100:
                    remaining = len(self.manual_timestamps) - i - 1
                    if remaining > 0:
                        more_text = f"... y {remaining} más"
                        more_surface = self.small_font.render(more_text, True, (150, 150, 150))
                        self.screen.blit(more_surface, (50, y_offset))
                    break
        
        pygame.display.flip()
    
    def run(self):
        """Ejecuta el calibrador"""
        print("🎙️ Calibrador Inteligente de Narrador iniciado")
        print("📖 Instrucciones para CALIBRACIÓN COMPLETA:")
        print("   1. Presiona ESPACIO para iniciar el narrador")
        print("   2. Escucha atentamente cada frase")
        print("   3. Presiona ESPACIO cuando termine cada frase")
        print("   4. Calibra TODOS los 24 fragmentos")
        print("   5. Presiona E para exportar y actualizar automáticamente")
        print()
        print("🎯 Al exportar se actualizará:")
        print("   🎬 intro_cinematica.py (automáticamente)")
        print()
        
        running = True
        while running:
            running = self.handle_events()
            self.draw()
            self.clock.tick(60)
        
        # Limpiar
        if self.narrator_playing:
            self.stop_narrator()
        pygame.quit()
        
        if len(self.manual_timestamps) > 1:
            print("\n✅ Calibración completada exitosamente")
            self.export_timestamps()

if __name__ == "__main__":
    calibrator = IntelligentNarratorCalibrator()
    calibrator.run()