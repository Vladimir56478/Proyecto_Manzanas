# 📜 Historial de Desarrollo - Proyecto Manzanas

## 🎮 Resumen del Proyecto
Juego de aventuras con dos personajes (Juan y Adán) que combaten enemigos en múltiples niveles.

### ✅ Funcionalidades Completadas
- **Sistema dual de personajes**: Juan (veloz, menos vida) y Adán (fuerte, más vida)
- **Controles invertidos para Juan**: Implementado como característica especial
- **Sistema de IA avanzado**: Control automático del personaje inactivo
- **Ataques direccionales**: Sistema de combate preciso
- **Sistema de revivir**: Los personajes pueden revivirse entre sí
- **Coleccionables**: Manzanas (mejoras) y pociones (escudo)
- **Múltiples niveles**: Nivel 1 (gusanos) y Nivel 2 (chamán)
- **Editor de colisiones**: Modo F1 para crear obstáculos personalizados

### 🛠️ Problemas Solucionados
- **Duplicación de archivos**: Eliminados archivos duplicados
- **IA de ataques**: Corregido sistema de doble-inversión para Juan
- **Controles invertidos**: Implementado sistema dual manual/IA
- **Indicadores visuales**: Eliminados indicadores de "IA" del juego
- **Sistema de colisiones**: Integrado editor personalizable

### 🎯 Estado Actual
- ✅ Nivel 1: Funcional y completo
- ✅ Nivel 2: Funcional y completo  
- ✅ Sistema de personajes: Balanceado y operativo
- ✅ IA: Funcionando correctamente para ambos personajes
- ✅ Controles: Juan (invertido) y Adán (normal) funcionando

### 🔧 Archivos Principales
- `nivel 1 escenario.py`: Nivel principal con 15 gusanos
- `nivel_2.py`: Segundo nivel con chamán malvado
- `juan_attacks.py` / `adan_attacks.py`: Sistemas de combate
- `character_ai.py`: Inteligencia artificial
- `intro_cinematica.py`: Pantalla de selección de personaje

### 📝 Notas de Desarrollo
- Juan usa controles invertidos como característica especial
- La IA maneja ambos personajes con precisión
- Sistema de mejoras mediante manzanas rojas
- Escudos temporales con pociones azules
- Editor de obstáculos integrado (F1)

---
*Desarrollo completado y estabilizado*