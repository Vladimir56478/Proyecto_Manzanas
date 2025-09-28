import pygame
import numpy as np
import math
import random

class SoundGenerator:
    """Generador de sonidos procedurales para el juego"""
    
    def __init__(self):
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        self.sample_rate = 22050
        self.sounds = {}
        self.generate_all_sounds()
    
    def generate_sine_wave(self, frequency, duration, volume=0.5, fade_out=True):
        """Genera una onda sinusoidal básica"""
        frames = int(duration * self.sample_rate)
        arr = np.zeros((frames, 2))
        
        for i in range(frames):
            time = float(i) / self.sample_rate
            wave = volume * math.sin(2 * math.pi * frequency * time)
            
            # Fade out para evitar clicks
            if fade_out and i > frames * 0.8:
                fade_factor = 1.0 - (i - frames * 0.8) / (frames * 0.2)
                wave *= fade_factor
            
            arr[i][0] = wave  # Canal izquierdo
            arr[i][1] = wave  # Canal derecho
        
        return (arr * 32767).astype(np.int16)
    
    def generate_noise(self, duration, volume=0.3, filter_freq=None):
        """Genera ruido blanco/filtrado"""
        frames = int(duration * self.sample_rate)
        arr = np.zeros((frames, 2))
        
        for i in range(frames):
            noise = (random.random() - 0.5) * 2 * volume
            arr[i][0] = noise
            arr[i][1] = noise
        
        return (arr * 32767).astype(np.int16)
    
    def generate_complex_tone(self, base_freq, harmonics, duration, volume=0.4):
        """Genera tono complejo con armónicos"""
        frames = int(duration * self.sample_rate)
        arr = np.zeros((frames, 2))
        
        for i in range(frames):
            time = float(i) / self.sample_rate
            wave = 0
            
            # Frecuencia base
            wave += volume * math.sin(2 * math.pi * base_freq * time)
            
            # Agregar armónicos
            for harmonic, harm_vol in harmonics:
                wave += (volume * harm_vol) * math.sin(2 * math.pi * base_freq * harmonic * time)
            
            # Envelope (fade in/out)
            envelope = 1.0
            if i < frames * 0.1:  # Fade in
                envelope = i / (frames * 0.1)
            elif i > frames * 0.7:  # Fade out
                envelope = 1.0 - (i - frames * 0.7) / (frames * 0.3)
            
            wave *= envelope
            arr[i][0] = wave
            arr[i][1] = wave
        
        return (arr * 32767).astype(np.int16)
    
    def generate_sweep(self, start_freq, end_freq, duration, volume=0.5):
        """Genera un sweep de frecuencia"""
        frames = int(duration * self.sample_rate)
        arr = np.zeros((frames, 2))
        
        for i in range(frames):
            time = float(i) / self.sample_rate
            progress = i / frames
            current_freq = start_freq + (end_freq - start_freq) * progress
            
            wave = volume * math.sin(2 * math.pi * current_freq * time)
            
            # Envelope
            envelope = math.sin(math.pi * progress)
            wave *= envelope
            
            arr[i][0] = wave
            arr[i][1] = wave
        
        return (arr * 32767).astype(np.int16)
    
    def generate_all_sounds(self):
        """Genera todos los sonidos del juego"""
        print("🎵 Generando sonidos procedurales...")
        
        try:
            # === SONIDOS DE COMBATE ===
            
            # Ataque básico - sonido de slash
            self.sounds['attack_basic'] = self.generate_sweep(200, 100, 0.2, 0.6)
            
            # Ataque especial - sonido más dramático
            self.sounds['attack_special'] = self.generate_complex_tone(
                150, [(2, 0.5), (3, 0.3), (4, 0.2)], 0.4, 0.7
            )
            
            # Combo de Juan - serie de sonidos rápidos
            combo_sound = np.concatenate([
                self.generate_sine_wave(300, 0.1, 0.4),
                self.generate_sine_wave(400, 0.1, 0.4),
                self.generate_sine_wave(500, 0.15, 0.5)
            ])
            self.sounds['combo_attack'] = combo_sound
            
            # Proyectil de Adán
            self.sounds['projectile_shoot'] = self.generate_sweep(400, 200, 0.3, 0.5)
            self.sounds['projectile_hit'] = self.generate_complex_tone(
                180, [(2, 0.4), (3, 0.2)], 0.2, 0.6
            )
            
            # === SONIDOS DE DAÑO Y MUERTE ===
            
            # Daño recibido
            self.sounds['damage_taken'] = self.generate_complex_tone(
                120, [(1.5, 0.6), (0.7, 0.4)], 0.3, 0.5
            )
            
            # Muerte de gusano
            self.sounds['enemy_death'] = self.generate_sweep(300, 80, 0.5, 0.4)
            
            # Muerte del jugador
            self.sounds['player_death'] = self.generate_complex_tone(
                100, [(0.5, 0.8), (0.3, 0.6)], 1.0, 0.6
            )
            
            # === SONIDOS DE INTERACCIÓN ===
            
            # Recoger item (manzana/poción)
            self.sounds['collect_item'] = self.generate_complex_tone(
                440, [(2, 0.4), (3, 0.2), (4, 0.1)], 0.3, 0.5
            )
            
            # Activar escudo
            self.sounds['shield_activate'] = self.generate_sweep(200, 600, 0.4, 0.4)
            
            # Revivir personaje
            self.sounds['revive'] = self.generate_complex_tone(
                220, [(2, 0.3), (3, 0.2), (5, 0.1)], 0.8, 0.5
            )
            
            # === SONIDOS DE INTERFAZ ===
            
            # Cambio de personaje
            self.sounds['character_switch'] = self.generate_sine_wave(523, 0.2, 0.4)
            
            # Menú de mejoras
            self.sounds['upgrade_menu'] = self.generate_complex_tone(
                330, [(2, 0.3), (3, 0.2)], 0.4, 0.4
            )
            
            # Selección de mejora
            self.sounds['upgrade_select'] = self.generate_sweep(440, 660, 0.3, 0.5)
            
            # === SONIDOS AMBIENTALES ===
            
            # Pasos (opcional)
            self.sounds['footstep'] = self.generate_noise(0.1, 0.2)
            
            # Spawn de enemigo
            self.sounds['enemy_spawn'] = self.generate_sweep(150, 250, 0.4, 0.3)
            
            # === SONIDOS DE VICTORIA/DERROTA ===
            
            # Victoria
            victory_sound = np.concatenate([
                self.generate_sine_wave(523, 0.3, 0.5),  # C
                self.generate_sine_wave(659, 0.3, 0.5),  # E
                self.generate_sine_wave(784, 0.6, 0.6)   # G
            ])
            self.sounds['victory'] = victory_sound
            
            # Game Over - Sonido melancólico pero no aterrador
            game_over_sound = np.concatenate([
                self.generate_sine_wave(330, 0.4, 0.4),  # E suave
                self.generate_sine_wave(294, 0.4, 0.4),  # D 
                self.generate_sine_wave(261, 0.8, 0.5)   # C prolongado
            ])
            self.sounds['game_over'] = game_over_sound
            
        except Exception as e:
            print(f"⚠️ Error generando sonidos: {e}")
            print("🔇 Continuando sin sonidos procedurales")
            self.sounds = {}
        
        print(f"✅ {len(self.sounds)} sonidos generados exitosamente")
    
    def play_sound(self, sound_name, volume=1.0):
        """Reproduce un sonido"""
        if sound_name in self.sounds:
            try:
                sound_array = self.sounds[sound_name]
                sound = pygame.sndarray.make_sound(sound_array)
                sound.set_volume(volume)
                sound.play()
            except Exception as e:
                print(f"⚠️ Error reproduciendo sonido {sound_name}: {e}")
        else:
            print(f"⚠️ Sonido no encontrado: {sound_name}")
    
    def get_sound(self, sound_name):
        """Obtiene un objeto Sound para control avanzado"""
        if sound_name in self.sounds:
            try:
                sound_array = self.sounds[sound_name]
                return pygame.sndarray.make_sound(sound_array)
            except Exception as e:
                print(f"⚠️ Error creando objeto Sound {sound_name}: {e}")
                return None
        return None


# Instancia global del generador de sonidos
_sound_generator = None

def get_sound_generator():
    """Obtiene la instancia global del generador de sonidos"""
    global _sound_generator
    if _sound_generator is None:
        _sound_generator = SoundGenerator()
    return _sound_generator

def play_sound(sound_name, volume=1.0):
    """Función de conveniencia para reproducir sonidos"""
    try:
        generator = get_sound_generator()
        generator.play_sound(sound_name, volume)
    except Exception as e:
        print(f"⚠️ Error en play_sound: {e}")