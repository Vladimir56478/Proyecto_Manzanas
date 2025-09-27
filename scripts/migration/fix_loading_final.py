#!/usr/bin/env python3
"""
CORRECTOR ESPECIALIZADO PARA CARGA LOCAL
Corrige específicamente las funciones que aún usan requests
"""

import os
import re

def fix_specific_loading_functions():
    """Corrige funciones específicas que usan requests.get()"""
    
    # Mapeo de patrones de remplazo específicos por archivo
    replacements = {
        'juan_attacks.py': {
            'pattern': r'response = requests\.get\(url\)\s*gif_data = BytesIO\(response\.content\)\s*gif = Image\.open\(gif_data\)',
            'replacement': '# Cargar desde archivo local\n                gif = Image.open(url)'
        },
        'adan_character_animation.py': {
            'pattern': r'response = requests\.get\(url\)\s*gif_data = BytesIO\(response\.content\)\s*gif = Image\.open\(gif_data\)',
            'replacement': '# Cargar desde archivo local\n                gif = Image.open(url)'
        },
        'adan_attacks.py': {
            'pattern': r'response = requests\.get\(url\)\s*gif_data = BytesIO\(response\.content\)\s*gif = Image\.open\(gif_data\)',
            'replacement': '# Cargar desde archivo local\n                gif = Image.open(url)'
        },
        'chaman_character_animation.py': {
            'pattern': r'response = requests\.get\(url.*?\n.*?gif = Image\.open\(.*?\)',
            'replacement': '# Cargar desde archivo local\n                gif = Image.open(url)'
        },
        'chaman_attacks.py': {
            'pattern': r'response = requests\.get\(url.*?\n.*?gif = Image\.open\(.*?\)',
            'replacement': '# Cargar desde archivo local\n                gif = Image.open(url)'
        },
        'worm_enemy.py': {
            'pattern': r'response = requests\.get\(self\.worm_gif_url.*?\n.*?gif = Image\.open\(.*?\)',
            'replacement': '# Cargar desde archivo local\n            gif = Image.open(self.worm_gif_url)'
        }
    }
    
    print("🔧 CORRECTOR ESPECIALIZADO PARA CARGA LOCAL")
    print("===========================================")
    
    for filename, fix_info in replacements.items():
        if not os.path.exists(filename):
            print(f"⚠️ Archivo no encontrado: {filename}")
            continue
            
        print(f"\n🔄 Corrigiendo {filename}...")
        
        # Leer archivo
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Aplicar el patrón de reemplazo
        content = re.sub(
            fix_info['pattern'], 
            fix_info['replacement'], 
            content, 
            flags=re.DOTALL | re.MULTILINE
        )
        
        # También remover las líneas que contengan 'from io import BytesIO'
        content = re.sub(r'from io import BytesIO\n?', '', content)
        
        # Guardar si hay cambios
        if content != original_content:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ {filename} corregido exitosamente")
        else:
            print(f"  ℹ️ {filename} no requirió cambios")
    
    print("\n🎉 ¡Corrección especializada completada!")
    print("🎮 El juego ahora debería cargar todos los assets localmente")

if __name__ == "__main__":
    fix_specific_loading_functions()