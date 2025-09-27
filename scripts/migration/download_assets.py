#!/usr/bin/env python3
"""
🎮 DESCARGADOR DE ASSETS - La Tierra de las Manzanas
Extrae y descarga automáticamente TODOS los assets de GitHub a carpetas locales organizadas.
Elimina lag por descargas en tiempo real.

Autor: GitHub Copilot
Fecha: 27 de septiembre de 2025
"""

import os
import re
import requests
from urllib.parse import urlparse
from pathlib import Path
import time
from io import BytesIO
from PIL import Image

class AssetDownloader:
    def __init__(self, base_path="assets"):
        self.base_path = Path(base_path)
        self.urls_found = {}
        self.download_count = 0
        self.total_urls = 0
        
        # Estructura de carpetas organizada
        self.folder_structure = {
            "juan_character_animation.py": "characters/juan/animations",
            "juan_attacks.py": "characters/juan/attacks", 
            "adan_character_animation.py": "characters/adan/animations",
            "adan_attacks.py": "characters/adan/attacks",
            "chaman_character_animation.py": "characters/chaman/animations", 
            "chaman_attacks.py": "characters/chaman/attacks",
            "worm_enemy.py": "enemies/worm",
            "nivel 1 escenario.py": "backgrounds",
            "nivel_2.py": "backgrounds", 
            "items_system.py": "items"
        }
    
    def extract_urls_from_files(self):
        """Extrae todas las URLs de GitHub de los archivos Python"""
        print("🔍 Escaneando archivos Python para encontrar URLs de GitHub...")
        
        python_files = [
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
        
        url_pattern = r'https://github\.com/user-attachments/assets/[a-f0-9\-]+'
        
        for filename in python_files:
            if not os.path.exists(filename):
                print(f"⚠️  {filename} no encontrado, saltando...")
                continue
                
            self.urls_found[filename] = []
            
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                urls = re.findall(url_pattern, content)
                
                for url in urls:
                    # Extraer contexto (qué representa esta URL)
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if url in line:
                            context_info = self._extract_context(lines, i, filename)
                            self.urls_found[filename].append({
                                'url': url,
                                'context': context_info,
                                'line': i + 1
                            })
                            break
                
                if self.urls_found[filename]:
                    print(f"✅ {filename}: {len(self.urls_found[filename])} URLs encontradas")
                else:
                    print(f"❌ {filename}: No se encontraron URLs")
                    
            except Exception as e:
                print(f"❌ Error leyendo {filename}: {e}")
        
        # Contar total de URLs
        self.total_urls = sum(len(urls) for urls in self.urls_found.values())
        print(f"\n📊 Total de assets encontrados: {self.total_urls}")
    
    def _extract_context(self, lines, line_index, filename):
        """Extrae contexto sobre qué representa cada URL"""
        current_line = lines[line_index].strip()
        
        # Buscar clave de diccionario (ej: "up": "url")
        key_match = re.search(r'"(\w+)":\s*"https', current_line)
        if key_match:
            return key_match.group(1)
        
        # Buscar variable (ej: self.worm_gif_url = "url")
        var_match = re.search(r'(\w+_url)\s*=', current_line)
        if var_match:
            return var_match.group(1).replace('_url', '').replace('_', ' ')
        
        # Contexto de personajes específicos
        if 'juan' in filename.lower():
            return 'juan_animation'
        elif 'adan' in filename.lower():  
            return 'adan_animation'
        elif 'chaman' in filename.lower():
            return 'chaman_animation'
        elif 'worm' in filename.lower():
            return 'worm_animation'
        elif 'item' in filename.lower():
            return 'item_sprite'
        elif 'escenario' in filename or 'nivel' in filename:
            return 'background'
        
        return f"asset_{line_index}"
    
    def create_folder_structure(self):
        """Crea la estructura de carpetas organizada"""
        print("\n📁 Creando estructura de carpetas...")
        
        folders_to_create = [
            "characters/juan/animations",
            "characters/juan/attacks",
            "characters/adan/animations", 
            "characters/adan/attacks",
            "characters/chaman/animations",
            "characters/chaman/attacks",
            "enemies/worm",
            "backgrounds", 
            "items"
        ]
        
        for folder in folders_to_create:
            folder_path = self.base_path / folder
            folder_path.mkdir(parents=True, exist_ok=True)
            print(f"📂 {folder_path}")
    
    def download_asset(self, url, filepath, context=""):
        """Descarga un asset individual con manejo de errores"""
        try:
            print(f"⬇️  Descargando {context}: {filepath.name}")
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Determinar extensión basada en content-type
            content_type = response.headers.get('content-type', '')
            if 'image/gif' in content_type or url.endswith('.gif'):
                extension = '.gif'
            elif 'image/png' in content_type or url.endswith('.png'):
                extension = '.png'  
            elif 'image/jpeg' in content_type or url.endswith('.jpg'):
                extension = '.jpg'
            else:
                # Detectar por contenido
                try:
                    img_data = BytesIO(response.content)
                    with Image.open(img_data) as img:
                        extension = f'.{img.format.lower()}'
                except:
                    extension = '.png'  # Por defecto
            
            # Asegurar que el archivo tenga la extensión correcta
            if not filepath.suffix:
                filepath = filepath.with_suffix(extension)
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            self.download_count += 1
            file_size = len(response.content) / 1024  # KB
            print(f"✅ {filepath.name} ({file_size:.1f} KB) - {self.download_count}/{self.total_urls}")
            
            return True
            
        except requests.exceptions.Timeout:
            print(f"⚠️  Timeout descargando {filepath.name}")
            return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Error descargando {filepath.name}: {e}")
            return False
        except Exception as e:
            print(f"❌ Error inesperado con {filepath.name}: {e}")
            return False
    
    def download_all_assets(self):
        """Descarga todos los assets encontrados"""
        if self.total_urls == 0:
            print("❌ No se encontraron assets para descargar")
            return
        
        print(f"\n🚀 Iniciando descarga de {self.total_urls} assets...")
        print("=" * 60)
        
        start_time = time.time()
        failed_downloads = []
        
        for filename, urls_data in self.urls_found.items():
            if not urls_data:
                continue
                
            print(f"\n📁 Procesando {filename}...")
            
            # Determinar carpeta de destino
            target_folder = self.folder_structure.get(filename, "misc")
            base_folder = self.base_path / target_folder
            
            for url_info in urls_data:
                url = url_info['url']
                context = url_info['context']
                
                # Generar nombre de archivo descriptivo
                if context and context != "asset_0":
                    filename_base = f"{context}"
                else:
                    # Usar parte del hash de GitHub como identificador
                    url_hash = url.split('/')[-1][:8]
                    filename_base = f"asset_{url_hash}"
                
                filepath = base_folder / filename_base
                
                if not self.download_asset(url, filepath, context):
                    failed_downloads.append({
                        'url': url,
                        'file': filename,
                        'context': context
                    })
                
                # Pequeña pausa para evitar sobrecargar GitHub
                time.sleep(0.1)
        
        end_time = time.time()
        download_time = end_time - start_time
        
        # Reporte final
        print("\n" + "=" * 60)
        print("📊 REPORTE DE DESCARGA")
        print("=" * 60)
        print(f"✅ Assets descargados exitosamente: {self.download_count}/{self.total_urls}")
        print(f"⏱️  Tiempo total: {download_time:.2f} segundos")
        
        if failed_downloads:
            print(f"\n❌ Fallos en descarga ({len(failed_downloads)}):")
            for fail in failed_downloads:
                print(f"   - {fail['context']} de {fail['file']}")
        
        success_rate = (self.download_count / self.total_urls) * 100
        print(f"📈 Tasa de éxito: {success_rate:.1f}%")
        
        if success_rate >= 95:
            print("\n🎉 ¡Descarga completada exitosamente!")
            print(f"📂 Assets guardados en: {self.base_path.absolute()}")
        else:
            print("\n⚠️  Algunas descargas fallaron, considera volver a ejecutar")
    
    def generate_asset_mapping(self):
        """Genera un archivo de mapeo para el script de migración"""
        mapping = {}
        
        for filename, urls_data in self.urls_found.items():
            mapping[filename] = {}
            target_folder = self.folder_structure.get(filename, "misc")
            
            for url_info in urls_data:
                url = url_info['url']
                context = url_info['context']
                
                if context and context != "asset_0":
                    filename_base = f"{context}"
                else:
                    url_hash = url.split('/')[-1][:8]
                    filename_base = f"asset_{url_hash}"
                
                local_path = f"assets/{target_folder}/{filename_base}"
                mapping[filename][url] = local_path
        
        # Guardar mapeo
        import json
        with open('asset_mapping.json', 'w', encoding='utf-8') as f:
            json.dump(mapping, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Mapeo guardado en: asset_mapping.json")

def main():
    """Función principal"""
    print("🎮 DESCARGADOR DE ASSETS - La Tierra de las Manzanas")
    print("=" * 60)
    print("Eliminando lag por descargas... Convirtiendo a assets locales")
    print("=" * 60)
    
    downloader = AssetDownloader()
    
    # Paso 1: Extraer URLs
    downloader.extract_urls_from_files()
    
    if downloader.total_urls == 0:
        print("❌ No se encontraron assets para descargar. Verifique los archivos Python.")
        return
    
    # Paso 2: Crear estructura de carpetas
    downloader.create_folder_structure()
    
    # Paso 3: Descargar assets
    downloader.download_all_assets()
    
    # Paso 4: Generar mapeo para migración
    downloader.generate_asset_mapping()
    
    print(f"\n🎯 SIGUIENTE PASO:")
    print("   Ejecuta 'python migrate_to_local.py' para migrar el código")

if __name__ == "__main__":
    main()