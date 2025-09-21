import pygame
import os
import random

class AudioManager:
    """Gestor de audio para el juego Tierra de las Manzanas"""
    
    def __init__(self):
        # Inicializar mixer de pygame
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
        pygame.mixer.init()
        
        # Volúmenes
        self.music_volume = 0.7
        self.sfx_volume = 0.8
        
        # Diccionarios para almacenar sonidos
        self.music_tracks = {}
        self.sound_effects = {}
        
        # Estado actual
        self.current_music = None
        self.music_playing = False
        
        # Cargar todos los archivos de audio
        self.load_all_audio()
        
        print("🎵 AudioManager inicializado")
    
    def load_all_audio(self):
        """Carga todos los archivos de audio desde las carpetas"""
        base_path = os.path.dirname(os.path.abspath(__file__))
        sounds_path = os.path.join(base_path, "sounds")
        
        # Cargar música
        music_path = os.path.join(sounds_path, "music")
        if os.path.exists(music_path):
            self.load_music_files(music_path)
        
        # Cargar efectos de sonido
        sfx_path = os.path.join(sounds_path, "sfx")
        if os.path.exists(sfx_path):
            self.load_sfx_files(sfx_path)
    
    def load_music_files(self, music_path):
        """Carga archivos de música"""
        try:
            for filename in os.listdir(music_path):
                if filename.endswith(('.wav', '.ogg', '.mp3')):
                    name = os.path.splitext(filename)[0]
                    filepath = os.path.join(music_path, filename)
                    self.music_tracks[name] = filepath
                    print(f"🎼 Música cargada: {name}")
        except Exception as e:
            print(f"⚠️ Error cargando música: {e}")
    
    def load_sfx_files(self, sfx_path):
        """Carga archivos de efectos de sonido"""
        try:
            for filename in os.listdir(sfx_path):
                if filename.endswith(('.wav', '.ogg', '.mp3')):
                    name = os.path.splitext(filename)[0]
                    filepath = os.path.join(sfx_path, filename)
                    try:
                        sound = pygame.mixer.Sound(filepath)
                        sound.set_volume(self.sfx_volume)
                        self.sound_effects[name] = sound
                        print(f"🔊 Efecto cargado: {name}")
                    except Exception as e:
                        print(f"⚠️ Error cargando {name}: {e}")
        except Exception as e:
            print(f"⚠️ Error cargando efectos: {e}")
    
    def play_music(self, track_name, loop=-1, fade_in=0):
        """Reproduce una pista de música"""
        if track_name in self.music_tracks:
            try:
                if self.music_playing:
                    pygame.mixer.music.stop()
                
                pygame.mixer.music.load(self.music_tracks[track_name])
                pygame.mixer.music.set_volume(self.music_volume)
                
                if fade_in > 0:
                    pygame.mixer.music.play(loop, fade_ms=fade_in)
                else:
                    pygame.mixer.music.play(loop)
                
                self.current_music = track_name
                self.music_playing = True
                print(f"🎵 Reproduciendo: {track_name}")
                
            except Exception as e:
                print(f"⚠️ Error reproduciendo música {track_name}: {e}")
        else:
            print(f"⚠️ Música no encontrada: {track_name}")
    
    def play_sfx(self, sound_name):
        """Reproduce un efecto de sonido"""
        if sound_name in self.sound_effects:
            try:
                self.sound_effects[sound_name].play()
            except Exception as e:
                print(f"⚠️ Error reproduciendo efecto {sound_name}: {e}")
        else:
            print(f"⚠️ Efecto no encontrado: {sound_name}")
    
    def stop_music(self, fade_out=0):
        """Detiene la música actual"""
        if self.music_playing:
            if fade_out > 0:
                pygame.mixer.music.fadeout(fade_out)
            else:
                pygame.mixer.music.stop()
            self.music_playing = False
            self.current_music = None
            print("🔇 Música detenida")
    
    def pause_music(self):
        """Pausa la música"""
        if self.music_playing:
            pygame.mixer.music.pause()
            print("⏸️ Música pausada")
    
    def resume_music(self):
        """Reanuda la música"""
        if self.music_playing:
            pygame.mixer.music.unpause()
            print("▶️ Música reanudada")
    
    def set_music_volume(self, volume):
        """Ajusta el volumen de la música (0.0 - 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
        print(f"🎵 Volumen música: {int(self.music_volume * 100)}%")
    
    def set_sfx_volume(self, volume):
        """Ajusta el volumen de efectos (0.0 - 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sound_effects.values():
            sound.set_volume(self.sfx_volume)
        print(f"🔊 Volumen efectos: {int(self.sfx_volume * 100)}%")
    
    def get_available_music(self):
        """Retorna lista de música disponible"""
        return list(self.music_tracks.keys())
    
    def get_available_sfx(self):
        """Retorna lista de efectos disponibles"""
        return list(self.sound_effects.keys())
    
    def is_music_playing(self):
        """Verifica si hay música reproduciéndose"""
        return pygame.mixer.music.get_busy()
    
    def cleanup(self):
        """Limpia recursos de audio"""
        pygame.mixer.music.stop()
        for sound in self.sound_effects.values():
            sound.stop()
        print("🧹 AudioManager limpiado")

# Instancia global del AudioManager
audio_manager = None

def get_audio_manager():
    """Obtiene la instancia global del AudioManager"""
    global audio_manager
    if audio_manager is None:
        audio_manager = AudioManager()
    return audio_manager