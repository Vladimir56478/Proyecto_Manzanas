# 🎵 Audio Assets - Tierra de las Manzanas

## Estructura de archivos de audio

### 📁 music/
Archivos de música de fondo (.wav u .ogg)
- `intro_theme.wav` - Música para la intro cinematográfica
- `level1_background.wav` - Música de fondo del nivel 1
- `battle_music.wav` - Música intensa durante combates
- `victory_theme.wav` - Música de victoria
- `game_over.wav` - Música de derrota

### 📁 sfx/
Efectos de sonido (.wav recomendado para menor latencia)
- `attack_juan.wav` - Sonido de ataque de Juan
- `attack_adan.wav` - Sonido de ataque de Adán
- `enemy_hit.wav` - Sonido cuando golpeas a un enemigo
- `character_hurt.wav` - Sonido cuando te lastiman
- `ui_select.wav` - Sonido al seleccionar en menús
- `ui_hover.wav` - Sonido al pasar por encima de botones
- `revival_complete.wav` - Sonido cuando revives a alguien
- `character_switch.wav` - Sonido al cambiar de personaje
- `enemy_spawn.wav` - Sonido cuando aparece un enemigo
- `footsteps.wav` - Sonidos de pasos (opcional)

## 📋 Notas técnicas:
- **Formato recomendado**: WAV para efectos, OGG para música
- **Calidad**: 44.1kHz, 16-bit para compatibilidad
- **Volumen**: Normalizar todos los archivos al mismo nivel
- **Duración música**: Los loops deben ser seamless (sin cortes)

## 🎮 Uso en el código:
Una vez agregues los archivos, el AudioManager los cargará automáticamente y estarán disponibles para usar en el juego.