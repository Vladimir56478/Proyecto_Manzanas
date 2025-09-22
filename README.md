# 🍎 **PROYECTO MANZANAS** 🕹️# 🍎 Proyecto Tierra de las Manzanas

*Juego 2D épico en Python con Pygame - Versión Final Optimizada*

## 🎮 **Descripción del Juego**

Un emocionante juego de acción 2D donde Juan y Adán luchan contra gusanos en un épico enfrentamiento. Con animaciones fluidas, sistema de combate dinámico, intro cinematográfica inmersiva y **sistema de narrador unificado**.Juego de acción 2D donde controlas a **Adán** y **Juan** en combate contra gusanos enemigos usando animaciones GIF cargadas directamente desde GitHub Issues.



---## 🗂️ **ESQUEMA DEL PROYECTO**



## 🌟 **CARACTERÍSTICAS PRINCIPALES**```

📁 Proyecto-tierra-de-las-manzanas/

### 🎬 **Intro Cinematográfica Completa**├── 🎮 nivel 1 escenario.py          # Archivo principal del juego

- **Selección de personaje:** Juan vs Adán├── 🎬 intro_cinematica.py           # Intro cinematográfica y selección

- **🎙️ Narrador unificado** con sincronización perfecta├── 📊 loading_screen.py             # Pantalla de carga con progreso

- **🎵 Audio optimizado** (un solo archivo MP3 de 90 segundos)├── � audio_manager.py              # Sistema de gestión de audio

- **⏱️ 24 fragmentos calibrados** con timestamps precisos├── �👤 adan_character_animation.py   # Personaje Adán + animaciones

- **Transiciones automáticas** entre historia y menú├── 👤 juan_character_animation.py   # Personaje Juan + animaciones  

├── ⚔️ adan_attacks.py              # Sistema de ataques de Adán

### ⚔️ **Sistema de Combate Avanzado**├── ⚔️ juan_attacks.py              # Sistema de ataques de Juan

- **Combate en tiempo real** con ataques direccionales├── 🐛 worm_enemy.py                # Enemigos gusano con IA

- **Sistema de combos** para Juan (3 niveles)├── 🧠 character_ai.py              # Inteligencia artificial

- **Ataques especiales** únicos por personaje├── 🎵 sounds/                      # Directorio de archivos de audio

- **Efectos visuales** impactantes└── 📖 README.md                    # Este archivo

```

### 🤖 **IA de Enemigos Inteligente**

- **Gusanos con comportamiento** de persecución## 📅 **LÍNEA DE TIEMPO DEL DESARROLLO**

- **Spawn automático** balanceado

- **Estados dinámicos:** idle, persiguiendo, atacando### **🕐 FASE 1: Estructura Base (Completada ✅)**

- ✅ Creación de personajes básicos (Adán y Juan)

### 🎵 **Sistema de Audio Profesional**- ✅ Sistema de movimiento con teclas WASD/Flechas

- **AudioManager** unificado sin playlists- ✅ Carga de animaciones GIF desde GitHub Issues

- **Un solo archivo de narrador** optimizado- ✅ Renderizado básico con pygame

- **Música de fondo** integrada

### **🕑 FASE 2: Sistema de Combate (Completada ✅)**  

---- ✅ Implementación de ataques direccionales

- ✅ GIFs de ataque específicos por dirección

## ⚙️ **INSTALACIÓN**- ✅ Tecla ESPACIO para ataques básicos

- ✅ Tecla X para ataques especiales

### **Requisitos del sistema:**- ✅ Sistema de daño y cooldowns

```bash

Python 3.8+### **🕒 FASE 3: Enemigos y IA (Completada ✅)**

pygame- ✅ Gusanos enemigos con animaciones

requests (para descarga de GIFs desde GitHub)- ✅ IA básica de persecución y ataque

```- ✅ Sistema de spawn automático

- ✅ Detección de colisiones optimizada

### **Instalar dependencias:**

```bash### **🕓 FASE 4: Optimizaciones (Completada ✅)**

pip install pygame requests- ✅ Corrección de direcciones invertidas de Juan

```- ✅ Eliminación de fondos blancos en GIFs

- ✅ Sistema de cámara que sigue al personaje

### **📁 Estructura Final del Proyecto (14 archivos esenciales):**- ✅ Interfaz de usuario mejorada

```

📁 Proyecto_Manzanas/### **🕔 FASE 5: Sistema de Juego (Completada ✅)**

├── 🎬 intro_cinematica.py           # Archivo principal con intro y narrador- ✅ Alternancia entre personajes con TAB

├── 🕹️ nivel 1 escenario.py          # Juego principal- ✅ Barras de vida dinámicas

├── ⚔️ juan_attacks.py               # Ataques de Juan- ✅ Condiciones de victoria/derrota

├── ⚔️ adan_attacks.py               # Ataques de Adán  - ✅ Sistema de reinicio con R

├── 🏃 juan_character_animation.py   # Animaciones Juan

├── 🏃 adan_character_animation.py   # Animaciones Adán### **🕕 FASE 6: Interfaz y Audio (Completada ✅)**

├── 🤖 character_ai.py               # IA de personajes- ✅ Intro cinematográfica con selección de personaje

├── 🐛 worm_enemy.py                 # Enemigos gusanos- ✅ Sistema de audio integrado (AudioManager)

├── 🔊 audio_manager.py              # Sistema de audio unificado- ✅ Música de fondo en la intro

├── 📱 loading_screen.py             # Pantalla de carga- ✅ **Narrador sincronizado con mensajes de texto**

├── 🛠️ narrator_calibrator.py        # Herramienta de calibración- ✅ **Gestión inteligente de audio (música/narrador)**

└── 📁 sounds/                       # Directorio de audio- ✅ **Indicadores visuales del estado del narrador**

    ├── 🎵 music/- ✅ Pantalla de carga con progreso real

    │   ├── Audio narrador del juego intro, COMPLETO.mp3  # ✅ UNIFICADO- ✅ Eliminación de pantallas negras durante la carga

    │   └── Melodia_Interfaz_intro.wav- ✅ Efectos visuales en pantallas de transición

    └── 🔊 sfx/

```## 🎮 **CONTROLES**



### **Ejecutar el juego:**| Tecla | Función |

```bash|-------|---------|

# Iniciar desde la intro cinematográfica (Recomendado)| W/A/S/D o Flechas | Mover personaje |

python "intro_cinematica.py"| ESPACIO | Ataque direccional con GIF |

| X | Ataque especial |

# Iniciar directamente el nivel (Solo para testing)| TAB | Cambiar entre Adán y Juan |

python "nivel 1 escenario.py"| R | Reiniciar (en Game Over/Victoria) |

| ESC | Salir del juego |

# Calibrar timestamps del narrador (Desarrollo)

python "narrator_calibrator.py"### **🎬 Controles de la Intro:**

```| Tecla | Función |

|-------|---------|

---| ESPACIO/ENTER | Saltar intro (detiene narrador) |

| ↑↓ | Navegar menú principal |

## 🎯 **NUEVAS CARACTERÍSTICAS OPTIMIZADAS**| ←→ | Seleccionar personaje |

| ENTER | Confirmar selección |

### **🎙️ Sistema de Narrador Unificado:**| ESC | Volver al menú anterior |

- **🎵 Audio único** - Un solo archivo MP3 de 1.1MB (90 segundos)

- **⏱️ Sincronización perfecta** - 24 fragmentos con timestamps calibrados## 🔧 **INSTALACIÓN Y USO**

- **🔧 Herramienta de calibración** - `narrator_calibrator.py` para ajustes precisos

- **🎯 Control automático:**### **Requisitos:**

  - Se inicia automáticamente con el primer fragmento```bash

  - Se detiene al saltar la intro (ESPACIO/ENTER)pip install pygame pillow requests

  - Se detiene automáticamente al terminar la historia```

  - Restaura la música de fondo al finalizar

- **📝 Control por tiempo transcurrido** - Los mensajes aparecen/desaparecen siguiendo exactamente lo que dice el narrador### **Clonar repositorio:**

- **👁️ Indicador visual animado** con tiempo transcurrido y estado de sincronización```bash

git clone https://github.com/Vladimir56478/Proyecto-tierra-de-las-manzanas.git

### **🛠️ Herramienta de Calibración de Timestamps:**cd Proyecto-tierra-de-las-manzanas

- **Interfaz visual interactiva** con Pygame```

- **Reproducción en tiempo real** del audio del narrador

- **Marcado preciso** de timestamps con tecla ESPACIO### **Ejecutar el juego:**

- **Actualización automática** de `intro_cinematica.py````bash

- **Sin archivos temporales** - Todo integrado en el flujo principal# Opción 1: Iniciar desde la intro cinematográfica (Recomendado)

python "intro_cinematica.py"

### **📊 Sistema de Pantalla de Carga:**

- Barra de progreso en tiempo real# Opción 2: Iniciar directamente el nivel (Solo para testing)

- Indicadores de progreso por assetpython "nivel 1 escenario.py"

- Eliminación de pantallas negras```

- Efectos visuales con partículas animadas

- Tips y mensajes informativos durante la carga## 🎯 **NUEVAS CARACTERÍSTICAS**



### **🔊 AudioManager Simplificado:**### **🎬 Sistema de Intro Cinematográfica:**

- Gestión inteligente de memoria sin playlists- Interfaz de selección de personaje (Juan/Adán)

- Soporte para música y efectos de sonido- Música de fondo integrada con AudioManager

- Carga automática desde directorio `sounds/`- Transiciones suaves entre menús

- Control de volumen y reproducción- Detección automática de selección

- Integración completa con el juego

### **📊 Sistema de Pantalla de Carga:**

---- Barra de progreso en tiempo real

- Indicadores de progreso por asset

## 🎯 **CARACTERÍSTICAS TÉCNICAS**- Eliminación de pantallas negras

- Efectos visuales con partículas animadas

### **🎨 Sistema de Animaciones:**- Tips y mensajes informativos durante la carga

- Carga automática de GIFs desde GitHub Issues (#3, #5, #6, #7)

- Eliminación inteligente de fondos blancos pixel por pixel### **🔊 Sistema de Audio Avanzado:**

- Animaciones direccionales fluidas (0.2s de velocidad)- AudioManager con gestión inteligente de memoria

- Transparencia SRCALPHA para mejor calidad visual- Soporte para música y efectos de sonido

- Carga automática desde directorio `sounds/`

### **⚔️ Sistema de Combate:**- Control de volumen y reproducción

- Ataques direccionales basados en movimiento actual- Integración completa con el juego

- Detección de colisión rectangular optimizada

- Efectos visuales únicos por personaje (dorado para Adán, verde para Juan)### **🎙️ Sistema de Narrador Sincronizado:**

- Sistema de combos progresivos para Juan (3 niveles)- **🕰️ Sincronización perfecta** entre audio y texto basada en timestamps reales

- Cooldowns balanceados (300ms Juan, 500ms Adán)- **📝 Control por tiempo transcurrido** - Los mensajes aparecen/desaparecen siguiendo exactamente lo que dice el narrador

- **🎵 Gestión inteligente de audio** (música de fondo ↔ narrador)

### **🤖 Inteligencia Artificial:**- **👁️ Indicador visual animado** con tiempo transcurrido y estado de sincronización

- Gusanos con comportamiento de persecución inteligente- **🎯 Control de reproducción:**

- Estados: idle, persiguiendo, atacando, herido  - Se inicia automáticamente con el primer fragmento

- Spawn automático en 4 áreas predefinidas  - Se detiene al saltar la intro (ESPACIO/ENTER)

- Balanceo dinámico: máximo 5 gusanos simultáneos  - Se detiene automáticamente al terminar la historia

  - Restaura la música de fondo al finalizar

### **🎬 Sistema de Cámara:**- **⏱️ 38 fragmentos sincronizados** en 90 segundos de audio narrativo

- Seguimiento suave del personaje activo- **🔧 Sistema de debug integrado** con timestamps visibles

- Interpolación 0.1 para movimiento fluido

- Desplazamiento centrado en pantalla## 🎯 **CARACTERÍSTICAS TÉCNICAS**



---### **🎨 Sistema de Animaciones:**

- Carga automática de GIFs desde GitHub Issues (#3, #5, #6, #7)

## 🌐 **URLs de Assets (GitHub Issues)**- Eliminación inteligente de fondos blancos pixel por pixel

- Animaciones direccionales fluidas (0.2s de velocidad)

### **Adán - Movimiento (Issue #3):**- Transparencia SRCALPHA para mejor calidad visual

- Arriba: `a8b0cb2f-6b0a-460d-aa3e-40a404e02bae`

- Abajo: `962334b6-0161-499a-b45d-9537cb82f0ee`### **⚔️ Sistema de Combate:**

- Izquierda: `6fd20d0d-0bce-46e5-ad48-909275503607`- Ataques direccionales basados en movimiento actual

- Derecha: `83d3150d-67db-4071-9e46-1f47846f22d0`- Detección de colisión rectangular optimizada

- Efectos visuales únicos por personaje (dorado para Adán, verde para Juan)

### **Adán - Ataques (Issue #5):**- Sistema de combos progresivos para Juan (3 niveles)

- Arriba: `6544be63-1345-4a5a-b4e9-57ec4a18775a`- Cooldowns balanceados (300ms Juan, 500ms Adán)

- Abajo: `cbce589c-03c0-4bc0-a067-1b769b154fbd`

- Izquierda: `1b2a5d84-7ef7-4598-ada0-68f21c785b06`### **🤖 Inteligencia Artificial:**

- Derecha: `b1dcab29-5e9f-46aa-87f2-1690c0986e77`- Gusanos con comportamiento de persecución inteligente

- Estados: idle, persiguiendo, atacando, herido

### **Juan - Movimiento (Issue #1):**- Spawn automático en 4 áreas predefinidas

- Arriba: `9310bb71-1229-4647-b208-b025cced50ec`- Balanceo dinámico: máximo 5 gusanos simultáneos

- Abajo: `507e3015-5213-4134-9564-127d2d0641b7`

- Izquierda: `acf6de12-85b7-41ea-868c-8bb9f227ddbb`### **🎬 Sistema de Cámara:**

- Derecha: `10059991-1a75-4a92-8e6c-7a8e6b7e7da0`- Seguimiento suave del personaje activo

- Interpolación 0.1 para movimiento fluido

### **Juan - Ataques (Issue #6) - INVERTIDAS:**- Desplazamiento centrado en pantalla

- Arriba: `bcd29b68-808b-4840-a6bb-1691c94581b1` (era down)

- Abajo: `dd75fe07-fdbc-44af-b96c-e02d24f1a541` (era up)## 🌐 **URLs de Assets (GitHub Issues)**

- Izquierda: `dd1ed297-05f1-468b-83fb-266d510595f3` (era right)

- Derecha: `e1db84b2-d37d-4bc4-87f8-cce531c51300` (era left)### **Adán - Movimiento (Issue #3):**

- Arriba: `a8b0cb2f-6b0a-460d-aa3e-40a404e02bae`

### **Gusanos - Movimiento (Issue #7):**- Abajo: `962334b6-0161-499a-b45d-9537cb82f0ee`

- URL: Consultar issue #7 para animaciones de enemigos- Izquierda: `6fd20d0d-0bce-46e5-ad48-909275503607`

- Derecha: `83d3150d-67db-4071-9e46-1f47846f22d0`

---

### **Adán - Ataques (Issue #5):**

## 📊 **ESTADÍSTICAS DEL PROYECTO OPTIMIZADO**- Arriba: `6544be63-1345-4a5a-b4e9-57ec4a18775a`

- Abajo: `cbce589c-03c0-4bc0-a067-1b769b154fbd`

- **Líneas de código:** ~1,200+- Izquierda: `1b2a5d84-7ef7-4598-ada0-68f21c785b06`

- **Archivos Python:** 11 archivos esenciales- Derecha: `b1dcab29-5e9f-46aa-87f2-1690c0986e77`

- **Archivos de audio:** 2 (unificado y optimizado)

- **Clases implementadas:** 8### **Juan - Movimiento (Issue #1):**

- **Métodos únicos:** 50+- Arriba: `9310bb71-1229-4647-b208-b025cced50ec`

- **Assets externos:** 20+ GIFs desde GitHub Issues- Abajo: `507e3015-5213-4134-9564-127d2d0641b7`

- **Tamaño total:** ~2MB (incluyendo audio unificado)- Izquierda: `acf6de12-85b7-41ea-868c-8bb9f227ddbb`

- **Tiempo de desarrollo:** Septiembre 2025- Derecha: `10059991-1a75-4a92-8e6c-7a8e6b7e7da0`



---### **Juan - Ataques (Issue #6) - INVERTIDAS:**

- Arriba: `bcd29b68-808b-4840-a6bb-1691c94581b1` (era down)

## 🎲 **MECÁNICAS DE JUEGO**- Abajo: `dd75fe07-fdbc-44af-b96c-e02d24f1a541` (era up)

- Izquierda: `dd1ed297-05f1-468b-83fb-266d510595f3` (era right)

### **🏃‍♂️ Personajes:**- Derecha: `e1db84b2-d37d-4bc4-87f8-cce531c51300` (era left)

- **Adán:** Tank con ataques de área grande, proyectiles ranged

- **Juan:** DPS rápido con sistema de combos, ataques especiales### **Gusanos - Movimiento (Issue #7):**

- URL: Consultar issue #7 para animaciones de enemigos

### **🎯 Objetivos:**

- Derrotar 10 gusanos para ganar## 📊 **ESTADÍSTICAS DEL PROYECTO**

- Mantener ambos personajes vivos

- Usar alternancia estratégica entre personajes- **Líneas de código:** ~1,200+

- **Archivos Python:** 6

### **⚖️ Balanceo:**- **Clases implementadas:** 8

- Vida: 100 HP por personaje- **Métodos únicos:** 50+

- Invulnerabilidad temporal: 1000ms- **Assets externos:** 20+ GIFs

- Daño Adán: 40 (melee), 25 (ranged)- **Tiempo de desarrollo:** Septiembre 2025

- Daño Juan: 15-25 (combo progresivo), 35 (especial)

## 🎲 **MECÁNICAS DE JUEGO**

---

### **🏃‍♂️ Personajes:**

## 🐛 **DEBUGEO Y LOGS**- **Adán:** Tank con ataques de área grande, proyectiles ranged

- **Juan:** DPS rápido con sistema de combos, ataques especiales

El juego incluye logs detallados en consola:

- 📥 Descarga de GIFs desde GitHub### **🎯 Objetivos:**

- 🎬 Reprodución de animaciones frame por frame- Derrotar 10 gusanos para ganar

- ⚔️ Detección de ataques y daños- Mantener ambos personajes vivos

- 🤖 Comportamiento de IA de enemigos- Usar alternancia estratégica entre personajes

- 🎙️ Sincronización de timestamps del narrador

### **⚖️ Balanceo:**

---- Vida: 100 HP por personaje

- Invulnerabilidad temporal: 1000ms

## 🚀 **ROADMAP FUTURO**- Daño Adán: 40 (melee), 25 (ranged)

- Daño Juan: 15-25 (combo progresivo), 35 (especial)

### **Próximas características:**

- [ ] Más tipos de enemigos## 🐛 **DEBUGEO Y LOGS**

- [ ] Sistema de power-ups

- [ ] Múltiples niveles/escenariosEl juego incluye logs detallados en consola:

- [ ] Efectos de sonido adicionales- 📥 Descarga de GIFs desde GitHub

- [ ] Menú principal expandido- 🎬 Reprodución de animaciones frame por frame

- [ ] Sistema de guardado- ⚔️ Detección de ataques y daños

- 🤖 Comportamiento de IA de enemigos

---

## 🚀 **ROADMAP FUTURO**

## 📁 **LIMPIEZA Y OPTIMIZACIÓN**

### **Próximas características:**

### **✅ Archivos eliminados en la optimización:**- [ ] Más tipos de enemigos

- `narrator_playlist.py` - Reemplazado por sistema unificado- [ ] Sistema de power-ups

- `calibrated_timestamps_clean.txt` - Integrado directamente en código- [ ] Múltiples niveles/escenarios

- `__pycache__/` - Archivos temporales de Python- [ ] Efectos de sonido

- `nivel1_escenario.cache` - Cache obsoleto- [ ] Menú principal

- [ ] Sistema de guardado

### **🎯 Resultado:**

- **Proyecto reducido** de múltiples archivos experimentales a **14 archivos esenciales**## 👥 **CONTRIBUCIÓN**

- **Audio unificado** de múltiples archivos a **un solo MP3 optimizado**Este proyecto está en desarrollo activo. Las mejoras y sugerencias son bienvenidas a través de Issues y Pull Requests.

- **Código limpio** sin archivos temporales o experimentales

- **Documentación actualizada** reflejando el estado final## 📄 **LICENCIA**

Proyecto educativo - Uso libre para aprendizaje y desarrollo.

---

---

## 👥 **CONTRIBUCIÓN**

Este proyecto está en desarrollo activo. Las mejoras y sugerencias son bienvenidas a través de Issues y Pull Requests.**Desarrollado con ❤️ usando Python, Pygame y GitHub Issues como CDN de assets**



## 📄 **LICENCIA***Última actualización: Septiembre 2025*
Proyecto educativo - Uso libre para aprendizaje y desarrollo.

---

**🎮 Desarrollado con ❤️ usando Python, Pygame y GitHub Issues como CDN de assets**

*✨ Versión Final Optimizada - Diciembre 2025*