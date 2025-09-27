#!/usr/bin/env python3
"""
CORRECTOR FINAL DE ASSETS LOCALES - La Tierra de las Manzanas
Script para reemplazar completamente requests.get() por carga local en todos los archivos
"""

import os
import re

def fix_character_loading():
    """Corrige todos los archivos de personajes para usar carga local"""
    
    # Mapeo de archivos a corregir
    files_to_fix = [
        'juan_character_animation.py',
        'juan_attacks.py', 
        'adan_character_animation.py',
        'adan_attacks.py',
        'chaman_character_animation.py',
        'chaman_attacks.py',
        'worm_enemy.py'
    ]
    
    print("🔧 CORRECTOR FINAL DE ASSETS LOCALES")
    print("====================================")
    print("Reemplazando requests.get() por carga local...")
    
    for filename in files_to_fix:
        if not os.path.exists(filename):
            print(f"⚠️ Archivo no encontrado: {filename}")
            continue
            
        print(f"\n🔄 Procesando {filename}...")
        
        # Leer archivo
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Reemplazar import requests con import os
        if 'import requests' in content:
            content = content.replace('import requests', 'import os')
            print("  📦 Reemplazado import requests por import os")
        
        # Reemplazar from io import BytesIO (ya no necesario)
        content = re.sub(r'from io import BytesIO\n?', '', content)
        
        # Reemplazar patrones de requests.get() 
        # Patrón: response = requests.get(url, ...)
        def replace_requests_get(match):
            return '''            # Cargar desde archivo local
            pil_image = Image.open(url)'''
        
        content = re.sub(
            r'response = requests\.get\(url[^)]*\)\s*response\.raise_for_status\(\)\s*image_data = BytesIO\(response\.content\)\s*pil_image = Image\.open\(image_data\)',
            replace_requests_get,
            content,
            flags=re.DOTALL
        )
        
        # Patrón más simple para requests.get
        content = re.sub(
            r'response = requests\.get\([^)]+\).*?pil_image = Image\.open\(.*?\)',
            'pil_image = Image.open(url)',
            content,
            flags=re.DOTALL
        )
        
        # Reemplazar mensajes de GitHub por locales
        content = content.replace('Descargando', 'Cargando')
        content = content.replace('desde GitHub', 'desde archivo local')
        content = content.replace('GitHub...', 'archivo local...')
        
        # Guardar si hay cambios
        if content != original_content:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ {filename} actualizado")
        else:
            print(f"  ℹ️ {filename} ya estaba correcto")
    
    print("\n🎉 ¡Corrección completada!")
    print("Todos los archivos ahora cargan assets desde archivos locales")

if __name__ == "__main__":
    fix_character_loading()