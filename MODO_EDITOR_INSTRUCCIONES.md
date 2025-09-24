# 🛠️ MODO EDITOR DE COLISIONES - NIVEL 1

## 📋 **Instrucciones de Uso**

### 🎮 **Activación del Modo Editor**
- **F1** - Activar/Desactivar el modo editor de colisiones
- En modo editor, el juego se pausa y puedes modificar las áreas de colisión

### 🕹️ **Controles del Editor**

| Tecla | Función |
|-------|---------|
| **↑ ↓ ← →** | Mover cursor del editor (se mueve en bloques de 32x32) |
| **ESPACIO** | Agregar bloque de colisión en la posición del cursor |
| **BACKSPACE** | Eliminar bloque de colisión en la posición del cursor |
| **E** | Salir del modo editor (también puedes usar F1) |

### 🎯 **Cómo Usar el Editor**

1. **Entra al modo editor** presionando **F1** durante el juego
2. **Mueve el cursor verde** con las flechas del teclado
3. **Coloca bloques rojos** con **ESPACIO** donde quieras restringir el movimiento
4. **Elimina bloques** con **BACKSPACE** si te equivocas
5. **Sal del editor** con **F1** o **E** - ¡Los cambios se guardan automáticamente!

### 🔴 **Visualización en Editor**
- **Cursor verde** = Posición donde se colocará/eliminará el próximo bloque
- **Bloques rojos semi-transparentes** = Áreas de colisión activas
- **Información en pantalla** = Coordenadas del cursor y número de bloques

### 💾 **Guardado Automático**
- Los bloques de colisión se guardan automáticamente en `collision_data.txt`
- Se cargan automáticamente la próxima vez que inicies el juego
- El archivo contiene las coordenadas de todos los bloques creados

### 🗺️ **Dimensiones del Mundo**
- **Escenario:** 1980x1080 píxeles exactos
- **Bloques:** 32x32 píxeles cada uno
- **Personajes:** 64x64 píxeles (2x2 bloques)

### 💡 **Consejos de Diseño**

1. **Crea caminos** dejando espacios libres para que los personajes puedan moverse
2. **Usa bloques estratégicamente** para crear obstáculos naturales
3. **No bloquees completamente** las áreas de spawn de enemigos
4. **Prueba el movimiento** saliendo del editor y caminando por tu diseño
5. **Crea estructuras** que complementen el escenario visual

### 🎮 **Controles del Juego (Fuera del Editor)**
- **WASD** o **Flechas** - Mover personaje activo
- **TAB** - Cambiar entre Juan y Adán
- **ESPACIO** - Ataque básico
- **X** - Ataque especial
- **E** - Revivir compañero (si está caído)
- **F1** - Modo editor de colisiones

### ⚠️ **Notas Importantes**
- El modo editor **pausa el juego** - los enemigos no se mueven
- Los bloques son **invisibles en el juego normal**, solo se ven en modo editor
- Los bloques **afectan tanto a Juan como a Adán** y a la IA
- Los **enemigos no son afectados** por los bloques de colisión

### 🗃️ **Archivo de Datos**
```
collision_data.txt - Contiene las coordenadas de todos los bloques
Formato: x,y,ancho,alto (uno por línea)
```

¡Ahora puedes crear el diseño de nivel perfecto para tu aventura en la Tierra de las Manzanas! 🍎