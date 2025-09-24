# 🛠️ **MODO EDITOR DE COLISIONES - Instrucciones Completas**

## 🎯 **¿Qué es el Modo Editor?**
El Modo Editor te permite colocar **bloques invisibles de colisión** en cualquier parte del escenario. Estos bloques evitan que los personajes (Juan, Adán y los enemigos) puedan atravesar ciertas áreas, creando obstáculos estratégicos.

---

## 🎮 **Controles del Modo Editor**

### **Activación/Desactivación:**
- **`F1`**: Entrar y salir del modo editor
  - Al **entrar**: Aparece cursor verde y información del editor
  - Al **salir**: Se guardan automáticamente todos los bloques en `collision_data.txt`

### **Navegación del Cursor:**
- **`↑`** (Flecha Arriba): Mover cursor hacia arriba
- **`↓`** (Flecha Abajo): Mover cursor hacia abajo  
- **`←`** (Flecha Izquierda): Mover cursor hacia la izquierda
- **`→`** (Flecha Derecha): Mover cursor hacia la derecha

### **Gestión de Bloques:**
- **`Espacio`**: Colocar un bloque invisible en la posición del cursor
- **`Backspace`**: Eliminar el bloque que esté en la posición del cursor

---

## 📐 **Características Técnicas**

### **Tamaño de los Bloques:**
- Cada bloque es de **32x32 píxeles**
- Los bloques se alinean automáticamente a una **grilla de 32px**
- Son **completamente invisibles** durante el juego normal

### **Movimiento del Cursor:**
- El cursor se mueve de **32 píxeles** en cada dirección
- Se mantiene dentro de los límites del escenario
- Coordenadas se muestran en tiempo real

---

## 🎨 **Indicadores Visuales**

### **En Modo Editor:**
- **Cursor Verde**: Muestra dónde se colocaría el próximo bloque
- **Bloques Rojos Semi-transparentes**: Muestran bloques ya colocados
- **Panel de Información**: Muestra:
  - Posición actual del cursor
  - Número total de bloques colocados
  - Controles disponibles

### **En Modo Juego:**
- Los bloques son **completamente invisibles**
- Solo se notan por la colisión (personajes no pueden atravesarlos)

---

## 💾 **Sistema de Guardado**

### **Guardado Automático:**
- Los bloques se guardan en `collision_data.txt` al presionar **F1** para salir
- **No necesitas hacer nada manualmente**

### **Carga Automática:**
- Al iniciar el juego, se cargan automáticamente los bloques guardados
- Si no existe `collision_data.txt`, el escenario empieza **completamente limpio**

---

## 🔧 **Consejos Estratégicos**

### **Usos Recomendados:**
1. **Crear laberintos** para hacer el combate más táctico
2. **Proteger áreas** donde aparecen ítems importantes
3. **Canalizar enemigos** hacia chokepoints
4. **Crear refugios** para estrategias defensivas
5. **Dividir el campo** de batalla en secciones

### **Estrategias Avanzadas:**
- **Pasillos estrechos**: Fuerza combate 1v1 con gusanos
- **Salas cerradas**: Crea áreas de combate intenso
- **Rutas de escape**: Deja siempre caminos alternativos
- **Emboscadas**: Crea esquinas para sorprender enemigos

---

## ⚠️ **Notas Importantes**

### **Limitaciones:**
- Los bloques afectan a **todos** los personajes (Juan, Adán y enemigos)
- Una vez colocado, un bloque **no se puede mover**, solo eliminar
- Los bloques persisten entre sesiones de juego

### **Recomendaciones:**
- **Prueba tu diseño** antes de salir del editor
- **No bloquees completamente** rutas importantes
- **Deja espacio suficiente** para que los personajes se muevan cómodamente

---

## 🚀 **¡Instrucciones de Uso Rápido!**

1. **Inicia el juego** normalmente
2. **Presiona F1** para activar el modo editor
3. **Usa las flechas** para mover el cursor verde
4. **Presiona Espacio** para colocar bloques donde quieras obstáculos
5. **Presiona Backspace** para eliminar bloques si te equivocas
6. **Presiona F1** para salir y probar tu diseño
7. **¡Disfruta el combate táctico** con tus obstáculos personalizados!

---

## 🎯 **¡Ahora puedes diseñar el campo de batalla perfecto para enfrentar a los 15 gusanos!**