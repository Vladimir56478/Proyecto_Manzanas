#!/usr/bin/env python3
"""
🎮 ELIMINADOR DE LAG TOTAL - La Tierra de las Manzanas
Script maestro que ejecuta automáticamente todo el proceso de migración:
GitHub Assets → Assets Locales = ¡JUEGO SÚPER FLUIDO!

Autor: GitHub Copilot
Fecha: 27 de septiembre de 2025
"""

import os
import sys
import time
import subprocess
from pathlib import Path

def print_banner():
    """Imprime banner genial"""
    banner = """
🎮═══════════════════════════════════════════════════════════════🎮
    ⚡ ELIMINADOR DE LAG TOTAL - La Tierra de las Manzanas ⚡
🎮═══════════════════════════════════════════════════════════════🎮

    🎯 OBJETIVO: GitHub Assets → Assets Locales = ¡CERO LAG!
    
    📋 PROCESO AUTOMÁTICO:
    1. 🔍 Escanear archivos Python para encontrar URLs de GitHub
    2. 📁 Crear estructura de carpetas organizadas  
    3. ⬇️  Descargar TODOS los assets (GIFs, PNGs, etc.)
    4. 🔄 Migrar código: requests.get() → Image.open() directo
    5. 💾 Crear backup de archivos originales
    6. ✅ Verificar que todo funcione correctamente
    
    🚀 RESULTADO: ¡Juego súper fluido sin lag por descargas!
    
═══════════════════════════════════════════════════════════════════
"""
    print(banner)

def check_dependencies():
    """Verifica que todas las dependencias estén instaladas"""
    print("🔍 Verificando dependencias...")
    
    required_modules = [
        'requests',
        'PIL',  # Pillow
        'pygame'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError:
            missing_modules.append(module)
            print(f"   ❌ {module}")
    
    if missing_modules:
        print(f"\n❌ Faltan dependencias: {', '.join(missing_modules)}")
        print("💡 Instálalas con:")
        
        for module in missing_modules:
            if module == 'PIL':
                print("   pip install Pillow")
            else:
                print(f"   pip install {module}")
        
        return False
    
    print("✅ Todas las dependencias están disponibles\n")
    return True

def check_python_files():
    """Verifica que los archivos Python del juego existan"""
    print("🔍 Verificando archivos del juego...")
    
    required_files = [
        "juan_character_animation.py",
        "juan_attacks.py",
        "adan_character_animation.py",
        "adan_attacks.py", 
        "nivel 1 escenario.py"
    ]
    
    optional_files = [
        "chaman_character_animation.py",
        "chaman_attacks.py",
        "worm_enemy.py",
        "nivel_2.py",
        "items_system.py"
    ]
    
    missing_required = []
    found_optional = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            missing_required.append(file)
            print(f"   ❌ {file}")
    
    for file in optional_files:
        if os.path.exists(file):
            found_optional.append(file)
            print(f"   ✅ {file}")
        else:
            print(f"   ⚪ {file} (opcional)")
    
    if missing_required:
        print(f"\n❌ Archivos requeridos faltantes: {missing_required}")
        return False
    
    total_files = len(required_files) + len(found_optional)
    print(f"✅ {total_files} archivos del juego encontrados\n")
    return True

def run_step(step_name, script_name, description):
    """Ejecuta un paso del proceso"""
    print(f"\n{'='*60}")
    print(f"🚀 {step_name}")  
    print(f"{'='*60}")
    print(f"📋 {description}")
    print()
    
    if not os.path.exists(script_name):
        print(f"❌ Script no encontrado: {script_name}")
        return False
    
    try:
        # Ejecutar el script
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, 
                              text=True, 
                              encoding='utf-8')
        
        # Mostrar output
        if result.stdout:
            print(result.stdout)
        
        if result.stderr and result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            return False
        
        if result.returncode == 0:
            print(f"✅ {step_name} completado exitosamente")
            return True
        else:
            print(f"❌ {step_name} falló (código {result.returncode})")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando {script_name}: {e}")
        return False

def verify_migration_success():
    """Verifica que la migración haya sido exitosa"""
    print(f"\n{'='*60}")
    print("🔍 VERIFICACIÓN FINAL")
    print(f"{'='*60}")
    
    # Verificar que existe la carpeta assets
    if not os.path.exists("assets"):
        print("❌ Carpeta 'assets' no encontrada")
        return False
    
    print("✅ Carpeta 'assets' creada")
    
    # Contar assets descargados
    asset_count = 0
    assets_path = Path("assets")
    
    for asset_file in assets_path.rglob("*"):
        if asset_file.is_file():
            asset_count += 1
    
    print(f"✅ {asset_count} assets descargados")
    
    # Verificar que existe el backup
    backup_folders = [d for d in os.listdir('.') if d.startswith('backup_')]
    if backup_folders:
        print(f"✅ Backup creado: {backup_folders[-1]}")
    else:
        print("⚠️ No se encontró carpeta de backup")
    
    # Verificar que no hay más requests.get() de GitHub en archivos
    github_requests_found = 0
    python_files = [
        "juan_character_animation.py",
        "juan_attacks.py", 
        "adan_character_animation.py",
        "adan_attacks.py",
        "nivel 1 escenario.py"
    ]
    
    for filename in python_files:
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'requests.get(' in content and 'github.com/user-attachments' in content:
                        github_requests_found += 1
            except:
                pass
    
    if github_requests_found == 0:
        print("✅ Migración de código completada - No más requests.get() de GitHub")
    else:
        print(f"⚠️ {github_requests_found} archivos aún contienen requests.get() de GitHub")
    
    print()
    
    # Resultado final
    if asset_count > 0 and github_requests_found == 0:
        print("🎉 ¡MIGRACIÓN EXITOSA!")
        print("🚀 Tu juego ahora usa assets locales - ¡LAG ELIMINADO!")
        return True
    else:
        print("⚠️ Migración incompleta - revisa los errores arriba")
        return False

def show_final_instructions():
    """Muestra instrucciones finales"""
    instructions = """
🎯 ¡PROCESO COMPLETADO!

📁 ESTRUCTURA DE ASSETS CREADA:
   assets/
   ├── characters/
   │   ├── juan/animations/
   │   ├── juan/attacks/
   │   ├── adan/animations/
   │   ├── adan/attacks/
   │   └── chaman/...
   ├── enemies/worm/
   ├── backgrounds/
   └── items/

🎮 PRÓXIMOS PASOS:
   1. Prueba tu juego: python "nivel 1 escenario.py"
   2. ¡Disfruta del rendimiento súper fluido!
   3. Si hay problemas, restaura desde la carpeta backup_*

⚡ BENEFICIOS OBTENIDOS:
   ✅ Eliminado lag por descargas de GitHub
   ✅ Carga instantánea de assets
   ✅ Juego funciona offline
   ✅ Rendimiento máximo

🎉 ¡MISIÓN CUMPLIDA - JUEGO OPTIMIZADO AL MÁXIMO!
"""
    print(instructions)

def main():
    """Función principal que ejecuta todo el proceso"""
    print_banner()
    
    # Verificaciones previas
    if not check_dependencies():
        print("❌ Resuelve las dependencias antes de continuar")
        return
    
    if not check_python_files():
        print("❌ Verifica que todos los archivos del juego estén presentes")
        return
    
    # Confirmación del usuario
    print("🎯 TODO LISTO PARA ELIMINAR EL LAG")
    print("⚠️  Este proceso modificará tus archivos Python")
    print("💾 Se creará un backup automático de todos los archivos")
    print()
    
    response = input("¿Continuar con la migración? (y/n): ")
    if response.lower() != 'y':
        print("❌ Migración cancelada por el usuario")
        return
    
    print("\n🚀 ¡INICIANDO ELIMINACIÓN TOTAL DE LAG!")
    print("⏱️ Esto puede tomar algunos minutos...")
    
    # Paso 1: Descargar assets
    if not run_step(
        "PASO 1: DESCARGA DE ASSETS",
        "download_assets.py", 
        "Escaneando archivos y descargando todos los assets de GitHub..."
    ):
        print("❌ Error en la descarga. Revisa tu conexión a internet.")
        return
    
    time.sleep(1)
    
    # Paso 2: Migrar código
    if not run_step(
        "PASO 2: MIGRACIÓN DE CÓDIGO",
        "migrate_to_local.py",
        "Reemplazando URLs de GitHub por rutas locales..."
    ):
        print("❌ Error en la migración de código.")
        return
    
    time.sleep(1)
    
    # Verificación final
    if verify_migration_success():
        show_final_instructions()
    else:
        print("⚠️ La migración no se completó correctamente")
        print("💾 Tus archivos originales están seguros en la carpeta backup_*")

if __name__ == "__main__":
    main()