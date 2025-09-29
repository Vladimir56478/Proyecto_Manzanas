# 🍎 La Tierra de las Manzanas

## 🎮 Juego de Aventuras en Python/Pygame - VERSIÓN FINAL v3.0

Un emocionante juego de aventuras donde Juan y Adán luchan contra gusanos enemigos y el Chamán Malvado en un mundo mágico. **Completamente optimizado** con todas las características finales implementadas.

### ✨ Características Principales

- **🎯 Dos Niveles Completos**: Nivel 1 (Gusanos) y Nivel 2 (Chamán Malvado)
- **👥 Dos Personajes**: Juan (ágil) y Adán (fuerte)
- **🤖 IA Avanzada**: Compañero inteligente con sistema de revival
- **⏸️ Sistema de Pausa**: Pausa completa con navegación de menú
- **💾 Progreso Persistente**: Tu avance se guarda automáticamente
- **� Sistema de Revival**: Revive a tu aliado caído
- **🎮 Pantalla de Carga**: Experiencia inmersiva entre niveles
- **⚡ Rendimiento Optimizado**: Assets locales para máximo rendimiento

### 🚀 Cómo Jugar

1. **Ejecutar el juego:**
   ```bash
   python "nivel 1 escenario.py"
   ```

2. **Controles:**
   - `WASD` - Movimiento
   - `Espacio` - Ataque básico
   - `TAB` - Cambiar personaje
   - `P` - Pausar juego
   - `E` - Revivir aliado (cuando está cerca y derrotado)
   - `M` - Menú principal (desde pausa)

3. **Objetivo:**
   - **Nivel 1:** Derrota 25 gusanos para desbloquear el Nivel 2
   - **Nivel 2:** Derrota al Chamán Malvado y sus secuaces

### 📁 Estructura del Proyecto

```
📦 Proyecto_Manzanas/
├── 🎮 Archivos Principales del Juego
│   ├── nivel 1 escenario.py        # Juego principal - Nivel de exploración
│   ├── nivel_2.py                  # Nivel de combate final
│   ├── intro_cinematica.py         # Cinemática de inicio
│   └── loading_screen.py           # Pantalla de carga entre niveles
│
├── 👥 Sistema de Personajes
│   ├── juan_character_animation.py # Personaje Juan + animaciones
│   ├── juan_attacks.py            # Sistema de ataques de Juan
│   ├── adan_character_animation.py # Personaje Adán + animaciones
│   ├── adan_attacks.py            # Sistema de ataques de Adán
│   ├── chaman_character_animation.py # Chamán Malvado + animaciones
│   ├── chaman_attacks.py          # Sistema de ataques del Chamán
│   ├── chaman_malvado.py          # Lógica del jefe final
│   └── character_base.py          # Clase base para todos los personajes
│
├── 🤖 Sistemas del Juego
│   ├── character_ai.py             # Inteligencia artificial
│   ├── worm_enemy.py              # Enemigos gusano
│   ├── audio_manager.py           # Gestión de audio
│   ├── items_system.py            # Sistema de objetos
│   ├── game_data_manager.py       # Persistencia de datos
│   ├── sound_generator.py         # Generación de efectos de sonido
│   ├── utils.py                   # Utilidades comunes
│   └── config.py                  # Configuración global
│
├── 🎨 Assets Locales
│   ├── assets/                    # Todos los recursos gráficos
│   │   ├── backgrounds/              # Fondos y escenarios
│   │   ├── characters/               # Sprites y animaciones
│   │   ├── enemies/                  # Sprites de enemigos
│   │   └── items/                    # Objetos coleccionables
│   └── sounds/                    # Archivos de audio
│       ├── music/                    # Música de fondo
│       └── sfx/                      # Efectos de sonido
│
├── 💾 Datos del Juego
│   ├── save_data/                 # Progreso y configuración
│   ├── collision_data.txt         # Datos de colisión Nivel 1
│   └── collision_data_nivel2.txt  # Datos de colisión Nivel 2
│
└── 📚 Documentación
    ├── docs/                      # Manuales y reportes
    ├── README.md                  # Este archivo
    ├── ERRORES.md                 # Documentación de errores conocidos
    └── ERRORES_CRITICOS.md        # Errores críticos y soluciones
```

### 🎯 Características Técnicas

- **Lenguaje:** Python 3.13+
- **Framework:** Pygame 2.6+
- **Dependencias:** PIL/Pillow para manejo de imágenes
- **Persistencia:** JSON para datos del juego
- **Rendimiento:** Carga local ultra-rápida
- **Compatibilidad:** Windows (PowerShell), Linux, macOS

### 🏆 Sistema de Progresión

- Contador de gusanos derrotados (sesión + histórico)
- Progresión automática entre niveles con pantalla de carga
- Sistema de mejoras para personajes
- Persistencia completa del progreso
- Sistema de revival para compañeros caídos

### 🆕 Nueva Funcionalidad v3.0

- **⏸️ Sistema de Pausa Completo**: Pausa con `P` en ambos niveles
- **🔄 Sistema de Revival Mejorado**: Revive aliados con barra de progreso
- **🎮 Pantalla de Carga**: Transición inmersiva al Nivel 2
- **🔍 IA Optimizada**: Comportamiento idéntico en ambos niveles
- **✨ Código Limpio**: Eliminación de ataques especiales innecesarios

### 🛠️ Para Desarrolladores

**Dependencias:**
```bash
pip install pygame pillow
```

**Estructura de Código:**
- Arquitectura modular con separación clara de responsabilidades
- Sistema de IA reutilizable entre personajes
- Gestión centralizada de assets y configuración
- Sistema de colisiones optimizado

**Debugging:**
- Consulta `ERRORES.md` para errores conocidos
- Revisa `ERRORES_CRITICOS.md` para problemas graves
- Los logs del juego se muestran en consola

---

**¡Disfruta el juego!** 🎮✨

*Proyecto desarrollado como juego completo de aventuras con Python y Pygame.*
