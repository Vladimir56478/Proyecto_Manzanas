# 🍎 La Tierra de las Manzanas

## 🎮 Juego de Aventuras en Python/Pygame - OPTIMIZADO v2.0

Un emocionante juego de aventuras donde Juan y Adán luchan contra gusanos enemigos en un mundo mágico. **Completamente refactorizado y optimizado** con arquitectura modular y eliminación de código duplicado.

### ✨ Características Principales

- **🎯 Dos Niveles Completos**: Nivel 1 (Gusanos) y Nivel 2 (Chamán Malvado)
- **👥 Dos Personajes**: Juan (ágil) y Adán (fuerte)
- **🤖 IA Avanzada**: Compañero inteligente que ayuda en combate
- **💾 Progreso Persistente**: Tu avance se guarda automáticamente
- **🛠️ Editor de Niveles**: Crea bloques de colisión personalizados
- **⚡ Carga Ultra Rápida**: Assets locales para cero lag

### 🚀 Cómo Jugar

1. **Ejecutar el juego:**
   ```bash
   python "nivel 1 escenario.py"
   ```

2. **Controles:**
   - `WASD` - Movimiento
   - `Espacio` - Ataque básico
   - `X` - Ataque especial
   - `TAB` - Cambiar personaje
   - `F1` - Modo editor (oculto pero funcional)

3. **Objetivo:**
   - Derrota 25 gusanos para desbloquear automáticamente el Nivel 2

### 📁 Estructura del Proyecto

```
📦 Proyecto_Manzanas/
├── 🎮 Archivos Principales del Juego
│   ├── nivel 1 escenario.py        # Juego principal
│   ├── nivel_2.py                  # Segundo nivel
│   ├── intro_cinematica.py         # Cinemática de inicio
│   └── loading_screen.py           # Pantalla de carga
│
├── 👥 Sistema de Personajes
│   ├── juan_character_animation.py # Animaciones de Juan
│   ├── juan_attacks.py            # Ataques de Juan
│   ├── adan_character_animation.py # Animaciones de Adán
│   ├── adan_attacks.py            # Ataques de Adán
│   ├── chaman_character_animation.py # Animaciones del Chamán
│   └── chaman_attacks.py          # Ataques del Chamán
│
├── 🤖 Sistemas del Juego
│   ├── character_ai.py             # Inteligencia artificial
│   ├── worm_enemy.py              # Enemigos gusano
│   ├── audio_manager.py           # Gestión de audio
│   ├── items_system.py            # Sistema de objetos
│   └── game_data_manager.py       # Persistencia de datos
│
├── 🎨 Assets Locales
│   ├── assets/                    # Todos los recursos gráficos
│   └── sounds/                    # Archivos de audio
│
├── 💾 Datos del Juego
│   └── save_data/                 # Progreso y configuración
│
├── 📚 Documentación
│   └── docs/                      # Manuales y reportes
│
├── 🔧 Scripts de Utilidad
│   └── scripts/                   # Herramientas de desarrollo
│
└── 📦 Backups
    └── backup/                    # Copias de seguridad
```

### 🎯 Características Técnicas

- **Lenguaje:** Python 3.13+
- **Framework:** Pygame 2.6+
- **Dependencias:** PIL/Pillow para manejo de imágenes
- **Persistencia:** JSON para datos del juego
- **Rendimiento:** Carga local ultra-rápida

### 🏆 Sistema de Progresión

- Contador de gusanos derrotados (sesión + histórico)
- Progresión automática entre niveles
- Sistema de mejoras para personajes
- Persistencia completa del progreso

### 🛠️ Para Desarrolladores

El proyecto incluye herramientas de migración y utilidades en `scripts/` para:
- Descarga automática de assets
- Migración de código
- Corrección de carga local
- Reportes de desarrollo

---

**¡Disfruta el juego!** 🎮✨
