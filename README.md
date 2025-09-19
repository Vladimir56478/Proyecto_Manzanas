# 🍎 Proyecto Tierra de las Manzanas

## 🎮 **Descripción del Juego**
Juego de acción 2D donde controlas a **Adán** y **Juan** en combate contra gusanos enemigos usando animaciones GIF cargadas directamente desde GitHub Issues.

## 🗂️ **ESQUEMA DEL PROYECTO**

```
📁 Proyecto-tierra-de-las-manzanas/
├── 🎮 nivel 1 escenario.py          # Archivo principal del juego
├── 👤 adan_character_animation.py   # Personaje Adán + animaciones
├── 👤 juan_character_animation.py   # Personaje Juan + animaciones  
├── ⚔️ adan_attacks.py              # Sistema de ataques de Adán
├── ⚔️ juan_attacks.py              # Sistema de ataques de Juan
├── 🐛 worm_enemy.py                # Enemigos gusano con IA
└── 📖 README.md                    # Este archivo
```

## 📅 **LÍNEA DE TIEMPO DEL DESARROLLO**

### **🕐 FASE 1: Estructura Base (Completada ✅)**
- ✅ Creación de personajes básicos (Adán y Juan)
- ✅ Sistema de movimiento con teclas WASD/Flechas
- ✅ Carga de animaciones GIF desde GitHub Issues
- ✅ Renderizado básico con pygame

### **🕑 FASE 2: Sistema de Combate (Completada ✅)**  
- ✅ Implementación de ataques direccionales
- ✅ GIFs de ataque específicos por dirección
- ✅ Tecla ESPACIO para ataques básicos
- ✅ Tecla X para ataques especiales
- ✅ Sistema de daño y cooldowns

### **🕒 FASE 3: Enemigos y IA (Completada ✅)**
- ✅ Gusanos enemigos con animaciones
- ✅ IA básica de persecución y ataque
- ✅ Sistema de spawn automático
- ✅ Detección de colisiones optimizada

### **🕓 FASE 4: Optimizaciones (Completada ✅)**
- ✅ Corrección de direcciones invertidas de Juan
- ✅ Eliminación de fondos blancos en GIFs
- ✅ Sistema de cámara que sigue al personaje
- ✅ Interfaz de usuario mejorada

### **🕔 FASE 5: Sistema de Juego (Completada ✅)**
- ✅ Alternancia entre personajes con TAB
- ✅ Barras de vida dinámicas
- ✅ Condiciones de victoria/derrota
- ✅ Sistema de reinicio con R

## 🎮 **CONTROLES**

| Tecla | Función |
|-------|---------|
| W/A/S/D o Flechas | Mover personaje |
| ESPACIO | Ataque direccional con GIF |
| X | Ataque especial |
| TAB | Cambiar entre Adán y Juan |
| R | Reiniciar (en Game Over/Victoria) |
| ESC | Salir del juego |

## 🔧 **INSTALACIÓN Y USO**

### **Requisitos:**
```bash
pip install pygame pillow requests
```

### **Clonar repositorio:**
```bash
git clone https://github.com/Vladimir56478/Proyecto-tierra-de-las-manzanas.git
cd Proyecto-tierra-de-las-manzanas
```

### **Ejecutar el juego:**
```bash
python "nivel 1 escenario.py"
```

## 🎯 **CARACTERÍSTICAS TÉCNICAS**

### **🎨 Sistema de Animaciones:**
- Carga automática de GIFs desde GitHub Issues (#3, #5, #6, #7)
- Eliminación inteligente de fondos blancos pixel por pixel
- Animaciones direccionales fluidas (0.2s de velocidad)
- Transparencia SRCALPHA para mejor calidad visual

### **⚔️ Sistema de Combate:**
- Ataques direccionales basados en movimiento actual
- Detección de colisión rectangular optimizada
- Efectos visuales únicos por personaje (dorado para Adán, verde para Juan)
- Sistema de combos progresivos para Juan (3 niveles)
- Cooldowns balanceados (300ms Juan, 500ms Adán)

### **🤖 Inteligencia Artificial:**
- Gusanos con comportamiento de persecución inteligente
- Estados: idle, persiguiendo, atacando, herido
- Spawn automático en 4 áreas predefinidas
- Balanceo dinámico: máximo 5 gusanos simultáneos

### **🎬 Sistema de Cámara:**
- Seguimiento suave del personaje activo
- Interpolación 0.1 para movimiento fluido
- Desplazamiento centrado en pantalla

## 🌐 **URLs de Assets (GitHub Issues)**

### **Adán - Movimiento (Issue #3):**
- Arriba: `a8b0cb2f-6b0a-460d-aa3e-40a404e02bae`
- Abajo: `962334b6-0161-499a-b45d-9537cb82f0ee`
- Izquierda: `6fd20d0d-0bce-46e5-ad48-909275503607`
- Derecha: `83d3150d-67db-4071-9e46-1f47846f22d0`

### **Adán - Ataques (Issue #5):**
- Arriba: `6544be63-1345-4a5a-b4e9-57ec4a18775a`
- Abajo: `cbce589c-03c0-4bc0-a067-1b769b154fbd`
- Izquierda: `1b2a5d84-7ef7-4598-ada0-68f21c785b06`
- Derecha: `b1dcab29-5e9f-46aa-87f2-1690c0986e77`

### **Juan - Movimiento (Issue #1):**
- Arriba: `9310bb71-1229-4647-b208-b025cced50ec`
- Abajo: `507e3015-5213-4134-9564-127d2d0641b7`
- Izquierda: `acf6de12-85b7-41ea-868c-8bb9f227ddbb`
- Derecha: `10059991-1a75-4a92-8e6c-7a8e6b7e7da0`

### **Juan - Ataques (Issue #6) - INVERTIDAS:**
- Arriba: `bcd29b68-808b-4840-a6bb-1691c94581b1` (era down)
- Abajo: `dd75fe07-fdbc-44af-b96c-e02d24f1a541` (era up)
- Izquierda: `dd1ed297-05f1-468b-83fb-266d510595f3` (era right)
- Derecha: `e1db84b2-d37d-4bc4-87f8-cce531c51300` (era left)

### **Gusanos - Movimiento (Issue #7):**
- URL: Consultar issue #7 para animaciones de enemigos

## 📊 **ESTADÍSTICAS DEL PROYECTO**

- **Líneas de código:** ~1,200+
- **Archivos Python:** 6
- **Clases implementadas:** 8
- **Métodos únicos:** 50+
- **Assets externos:** 20+ GIFs
- **Tiempo de desarrollo:** Septiembre 2025

## 🎲 **MECÁNICAS DE JUEGO**

### **🏃‍♂️ Personajes:**
- **Adán:** Tank con ataques de área grande, proyectiles ranged
- **Juan:** DPS rápido con sistema de combos, ataques especiales

### **🎯 Objetivos:**
- Derrotar 10 gusanos para ganar
- Mantener ambos personajes vivos
- Usar alternancia estratégica entre personajes

### **⚖️ Balanceo:**
- Vida: 100 HP por personaje
- Invulnerabilidad temporal: 1000ms
- Daño Adán: 40 (melee), 25 (ranged)
- Daño Juan: 15-25 (combo progresivo), 35 (especial)

## 🐛 **DEBUGEO Y LOGS**

El juego incluye logs detallados en consola:
- 📥 Descarga de GIFs desde GitHub
- 🎬 Reprodución de animaciones frame por frame
- ⚔️ Detección de ataques y daños
- 🤖 Comportamiento de IA de enemigos

## 🚀 **ROADMAP FUTURO**

### **Próximas características:**
- [ ] Más tipos de enemigos
- [ ] Sistema de power-ups
- [ ] Múltiples niveles/escenarios
- [ ] Efectos de sonido
- [ ] Menú principal
- [ ] Sistema de guardado

## 👥 **CONTRIBUCIÓN**
Este proyecto está en desarrollo activo. Las mejoras y sugerencias son bienvenidas a través de Issues y Pull Requests.

## 📄 **LICENCIA**
Proyecto educativo - Uso libre para aprendizaje y desarrollo.

---

**Desarrollado con ❤️ usando Python, Pygame y GitHub Issues como CDN de assets**

*Última actualización: Septiembre 2025*