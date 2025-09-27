#!/usr/bin/env python3
"""
🔄 MIGRADOR A ASSETS LOCALES - La Tierra de las Manzanas
Reemplaza automáticamente URLs de GitHub por rutas locales en todos los archivos Python.
Convierte requests.get() a Image.open() directo para eliminar lag.

Autor: GitHub Copilot  
Fecha: 27 de septiembre de 2025
"""

import os
import re
import json
import shutil
from pathlib import Path
from datetime import datetime

class LocalAssetMigrator:
    def __init__(self, mapping_file="asset_mapping.json"):
        self.mapping_file = mapping_file
        self.asset_mapping = {}
        self.backup_folder = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.files_modified = 0
        self.urls_replaced = 0
        
        # Archivos a migrar
        self.target_files = [
            "juan_character_animation.py",
            "juan_attacks.py",
            "adan_character_animation.py", 
            "adan_attacks.py",
            "chaman_character_animation.py",
            "chaman_attacks.py",
            "worm_enemy.py",
            "nivel 1 escenario.py", 
            "nivel_2.py",
            "items_system.py"
        ]
    
    def load_asset_mapping(self):
        """Carga el mapeo de assets desde el archivo JSON"""
        if not os.path.exists(self.mapping_file):
            print(f"❌ Archivo de mapeo no encontrado: {self.mapping_file}")
            print("   Ejecuta primero 'python download_assets.py'")
            return False
        
        try:
            with open(self.mapping_file, 'r', encoding='utf-8') as f:
                self.asset_mapping = json.load(f)
            
            total_mappings = sum(len(mappings) for mappings in self.asset_mapping.values())
            print(f"✅ Mapeo cargado: {total_mappings} assets para migrar")
            return True
            
        except Exception as e:
            print(f"❌ Error cargando mapeo: {e}")
            return False
    
    def create_backup(self):
        """Crea backup de todos los archivos originales"""
        print(f"\n💾 Creando backup en: {self.backup_folder}/")
        
        os.makedirs(self.backup_folder, exist_ok=True)
        
        backed_up = 0
        for filename in self.target_files:
            if os.path.exists(filename):
                try:
                    shutil.copy2(filename, os.path.join(self.backup_folder, filename))
                    backed_up += 1
                    print(f"   ✅ {filename}")
                except Exception as e:
                    print(f"   ❌ Error backing up {filename}: {e}")
        
        print(f"📁 {backed_up} archivos respaldados")
        return backed_up > 0
    
    def detect_loading_pattern(self, content, url):
        """Detecta qué patrón de carga usa cada archivo"""
        
        # Buscar contexto alrededor de la URL
        url_line_start = content.find(url)
        if url_line_start == -1:
            return 'unknown'
        
        # Obtener contexto más amplio (800 caracteres antes y después)
        context_start = max(0, url_line_start - 800)
        context_end = min(len(content), url_line_start + 800)
        context = content[context_start:context_end]
        
        # Detectar patrones específicos - orden importa
        if 'BytesIO(response.content)' in context:
            if 'gif_data' in context or 'while True:' in context:
                return 'gif_loading'
            elif 'pil_image' in context or 'Image.open' in context:
                return 'image_loading'
        
        if 'pygame.image.load' in context or 'background_image' in context:
            return 'background_loading'
            
        # Detectar por contenido del archivo
        if any(x in content for x in ['character_animation', 'attacks', 'worm']):
            return 'gif_loading'
        elif any(x in content for x in ['escenario', 'nivel', 'background']):
            return 'background_loading'
        else:
            return 'image_loading'
    
    def generate_replacement_code(self, url, local_path, pattern, context):
        """Genera código de reemplazo específico para cada patrón"""
        
        if pattern == 'gif_loading':
            return f'''
            # Carga local de GIF - {context}
            gif_path = "{local_path}"
            frames = []
            if os.path.exists(gif_path):
                try:
                    with Image.open(gif_path) as gif:
                        while True:
                            frame = gif.copy()
                            if frame.mode != 'RGBA':
                                frame = frame.convert('RGBA')
                            frame_surface = pygame.image.fromstring(
                                frame.tobytes(), frame.size, 'RGBA'
                            )
                            frames.append(frame_surface)
                            gif.seek(len(frames))
                except EOFError:
                    pass  # Fin del GIF
                except Exception as e:
                    print(f"⚠️ Error cargando {{gif_path}}: {{e}}")
                    frames = []
            else:
                print(f"⚠️ Asset no encontrado: {{gif_path}}")
                frames = []'''
        
        elif pattern == 'background_loading':
            return f'''
            # Carga local de fondo - {context}
            background_path = "{local_path}"
            if os.path.exists(background_path):
                try:
                    background_image = pygame.image.load(background_path)
                    original_width, original_height = background_image.get_size()
                except Exception as e:
                    print(f"⚠️ Error cargando {{background_path}}: {{e}}")
                    background_image = None
            else:
                print(f"⚠️ Asset no encontrado: {{background_path}}")
                background_image = None'''
        
        elif pattern == 'image_loading':
            return f'''
            # Carga local de imagen - {context}  
            image_path = "{local_path}"
            if os.path.exists(image_path):
                try:
                    pil_image = Image.open(image_path)
                    if pil_image.mode != 'RGBA':
                        pil_image = pil_image.convert('RGBA')
                except Exception as e:
                    print(f"⚠️ Error cargando {{image_path}}: {{e}}")
                    pil_image = None
            else:
                print(f"⚠️ Asset no encontrado: {{image_path}}")
                pil_image = None'''
        
        else:
            # Patrón genérico
            return f'''
            # Carga local - {context}
            asset_path = "{local_path}"
            if os.path.exists(asset_path):
                # TODO: Implementar carga específica
                pass
            else:
                print(f"⚠️ Asset no encontrado: {{asset_path}}")'''
    
    def migrate_file(self, filename):
        """Migra un archivo individual"""
        if filename not in self.asset_mapping:
            print(f"⚠️ {filename}: No hay assets para migrar")
            return False
        
        if not os.path.exists(filename):
            print(f"❌ {filename}: Archivo no encontrado")
            return False
        
        print(f"\n🔄 Migrando {filename}...")
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            modifications = 0
            
            # Migrar cada URL en este archivo
            for url, local_path in self.asset_mapping[filename].items():
                if url in content:
                    print(f"   🔗 Reemplazando: {url.split('/')[-1][:12]}...")
                    
                    # Detectar patrón de carga
                    pattern = self.detect_loading_pattern(content, url)
                    
                    # Buscar y reemplazar el bloque de código completo
                    content = self._replace_download_block(content, url, local_path, pattern)
                    modifications += 1
            
            # Agregar imports necesarios
            content = self._ensure_imports(content)
            
            if modifications > 0:
                # Escribir archivo modificado
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"   ✅ {modifications} URLs migradas en {filename}")
                self.files_modified += 1
                self.urls_replaced += modifications
                return True
            else:
                print(f"   ℹ️ {filename}: No requiere cambios")
                return False
                
        except Exception as e:
            print(f"   ❌ Error migrando {filename}: {e}")
            return False
    
    def _replace_download_block(self, content, url, local_path, pattern):
        """Reemplaza el bloque completo de descarga con carga local"""
        
        # Enfoque más simple y efectivo: reemplazar por URL directa
        escaped_url = re.escape(url)
        
        # Buscar y reemplazar bloques completos de descarga
        patterns = [
            # Patrón para GIFs con while True:
            rf'response = requests\.get\([^)]*{escaped_url}[^)]*\).*?while True:.*?gif\.seek\(len\(frames\)\)',
            # Patrón para imágenes con pil_image
            rf'response = requests\.get\([^)]*{escaped_url}[^)]*\).*?pil_image = Image\.open\(BytesIO\(response\.content\)\)',
            # Patrón para backgrounds con pygame.image.load
            rf'response = requests\.get\([^)]*{escaped_url}[^)]*\).*?pygame\.image\.load\(BytesIO\(response\.content\)\)'
        ]
        
        context = self._extract_variable_name(content, url)
        replacement_code = self.generate_replacement_code(url, local_path, pattern, context)
        
        # Intentar cada patrón
        for pattern_regex in patterns:
            if re.search(pattern_regex, content, re.DOTALL):
                content = re.sub(pattern_regex, replacement_code, content, flags=re.DOTALL)
                break
        else:
            # Si no se encuentra un patrón complejo, reemplazar solo la URL
            content = content.replace(f'"{url}"', f'"{local_path}"')
            content = content.replace(f"'{url}'", f"'{local_path}'")
        
        return content
    
    def _extract_variable_name(self, content, url):
        """Extrae el nombre/contexto de la variable que contiene la URL"""
        lines = content.split('\n')
        for line in lines:
            if url in line:
                # Buscar patrones como "up": "url" o variable_url = "url"  
                key_match = re.search(r'"(\w+)":\s*"' + re.escape(url), line)
                if key_match:
                    return key_match.group(1)
                
                var_match = re.search(r'(\w+)\s*=.*"' + re.escape(url), line)
                if var_match:
                    return var_match.group(1)
                
                break
        return "asset"
    
    def _ensure_imports(self, content):
        """Asegura que los imports necesarios estén presentes"""
        imports_needed = []
        
        if 'Image.open(' in content and 'from PIL import Image' not in content:
            imports_needed.append('from PIL import Image')
        
        if 'os.path.exists(' in content and 'import os' not in content:
            imports_needed.append('import os')
        
        if imports_needed:
            # Encontrar lugar para insertar imports
            lines = content.split('\n')
            import_section_end = 0
            
            for i, line in enumerate(lines):
                if line.strip().startswith(('import ', 'from ')) or line.strip().startswith('#'):
                    import_section_end = i + 1
                elif line.strip() and not line.strip().startswith('#'):
                    break
            
            # Insertar imports
            for import_stmt in imports_needed:
                if import_stmt not in content:
                    lines.insert(import_section_end, import_stmt)
                    import_section_end += 1
            
            content = '\n'.join(lines)
        
        return content
    
    def migrate_all_files(self):
        """Migra todos los archivos"""
        if not self.asset_mapping:
            print("❌ No hay mapeo de assets cargado")
            return False
        
        print(f"\n🚀 Iniciando migración de {len(self.target_files)} archivos...")
        print("=" * 60)
        
        # Crear backup primero
        if not self.create_backup():
            print("❌ No se pudo crear backup. Abortando migración.")
            return False
        
        # Migrar archivos
        for filename in self.target_files:
            self.migrate_file(filename)
        
        # Reporte final
        print("\n" + "=" * 60)
        print("📊 REPORTE DE MIGRACIÓN")
        print("=" * 60)
        print(f"✅ Archivos modificados: {self.files_modified}")
        print(f"🔗 URLs reemplazadas: {self.urls_replaced}")
        print(f"💾 Backup guardado en: {self.backup_folder}/")
        
        if self.files_modified > 0:
            print("\n🎉 ¡Migración completada exitosamente!")
            print("🎮 Tu juego ahora usa assets locales - ¡Adiós al lag!")
            print("\n💡 NEXT STEPS:")
            print("   1. Prueba tu juego: python 'nivel 1 escenario.py'")
            print("   2. Si hay problemas, restaura desde backup")
            print("   3. ¡Disfruta del juego súper fluido!")
        else:
            print("\n⚠️ No se realizaron cambios")
        
        return self.files_modified > 0
    
    def verify_assets_exist(self):
        """Verifica que todos los assets locales existan"""
        print("\n🔍 Verificando assets locales...")
        
        missing_assets = []
        total_assets = 0
        
        for filename, mappings in self.asset_mapping.items():
            for url, local_path in mappings.items():
                total_assets += 1
                if not os.path.exists(local_path):
                    missing_assets.append({
                        'file': filename,
                        'path': local_path,
                        'url': url
                    })
        
        if missing_assets:
            print(f"❌ {len(missing_assets)} assets faltantes de {total_assets}:")
            for asset in missing_assets[:5]:  # Mostrar solo primeros 5
                print(f"   - {asset['path']} (de {asset['file']})")
            
            if len(missing_assets) > 5:
                print(f"   ... y {len(missing_assets) - 5} más")
            
            print("\n💡 Ejecuta 'python download_assets.py' para descargar assets faltantes")
            return False
        else:
            print(f"✅ Todos los assets locales están presentes ({total_assets})")
            return True

def main():
    """Función principal"""
    print("🔄 MIGRADOR A ASSETS LOCALES - La Tierra de las Manzanas")
    print("=" * 60)
    print("Eliminando lag... Migrando a carga local súper rápida")
    print("=" * 60)
    
    migrator = LocalAssetMigrator()
    
    # Paso 1: Cargar mapeo
    if not migrator.load_asset_mapping():
        return
    
    # Paso 2: Verificar assets locales
    if not migrator.verify_assets_exist():
        print("⚠️ Algunos assets faltan. Considera ejecutar download_assets.py primero")
        response = input("¿Continuar con la migración? (y/n): ")
        if response.lower() != 'y':
            print("Migración cancelada")
            return
    
    # Paso 3: Migrar archivos
    success = migrator.migrate_all_files()
    
    if success:
        print(f"\n🎯 ¡MISIÓN CUMPLIDA!")
        print("Tu juego ahora carga assets localmente = ¡CERO LAG!")

if __name__ == "__main__":
    main()