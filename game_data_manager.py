#!/usr/bin/env python3
"""
GAME DATA MANAGER - La Tierra de las Manzanas
Sistema de persistencia de datos del juego incluyendo:
- Contador de gusanos derrotados  
- Bloques de colisión colocados en editor mode
- Progreso del juego y estadísticas
"""

import json
import os
import pygame
from typing import Dict, List, Tuple, Any

class GameDataManager:
    """Maneja la persistencia de datos del juego"""
    
    def __init__(self, data_dir: str = "save_data"):
        """Inicializa el manager de datos del juego"""
        self.data_dir = data_dir
        self.game_data_file = os.path.join(data_dir, "game_progress.json")
        self.collision_data_file = os.path.join(data_dir, "collision_blocks.json")
        
        # Crear directorio si no existe
        os.makedirs(data_dir, exist_ok=True)
        
        # Datos por defecto
        self.default_game_data = {
            "total_worms_defeated": 0,
            "current_level": 1,
            "session_stats": {
                "games_played": 0,
                "total_playtime_minutes": 0,
                "best_worm_streak": 0
            },
            "achievements": {
                "first_victory": False,
                "level_2_unlocked": False,
                "master_editor": False
            }
        }
        
        self.default_collision_data = {
            "blocks": [],
            "last_modified": None,
            "total_blocks_placed": 0
        }
    
    def load_game_data(self) -> Dict[str, Any]:
        """Carga los datos del juego desde archivo"""
        try:
            if os.path.exists(self.game_data_file):
                with open(self.game_data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"📊 Datos cargados: {data['total_worms_defeated']} gusanos totales derrotados")
                return data
            else:
                print("📋 Creando nuevo archivo de datos del juego...")
                return self.default_game_data.copy()
        except Exception as e:
            print(f"⚠️ Error cargando datos del juego: {e}")
            return self.default_game_data.copy()
    
    def save_game_data(self, data: Dict[str, Any]) -> bool:
        """Guarda los datos del juego"""
        try:
            with open(self.game_data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Error guardando datos del juego: {e}")
            return False
    
    def load_collision_data(self) -> Dict[str, Any]:
        """Carga los datos de bloques de colisión"""
        try:
            if os.path.exists(self.collision_data_file):
                with open(self.collision_data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"🧱 Bloques de colisión cargados: {len(data.get('blocks', []))} bloques")
                return data
            else:
                print("📋 Creando nuevo archivo de bloques de colisión...")
                return self.default_collision_data.copy()
        except Exception as e:
            print(f"⚠️ Error cargando bloques de colisión: {e}")
            return self.default_collision_data.copy()
    
    def save_collision_data(self, blocks: List[Tuple[int, int]], silent: bool = False) -> bool:
        """Guarda los bloques de colisión"""
        try:
            data = {
                "blocks": [{"x": x, "y": y} for x, y in blocks],
                "last_modified": pygame.time.get_ticks(),
                "total_blocks_placed": len(blocks)
            }
            
            with open(self.collision_data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            if not silent:
                print(f"💾 Bloques guardados: {len(blocks)} bloques de colisión")
            return True
        except Exception as e:
            print(f"❌ Error guardando bloques: {e}")
            return False
    
    def update_worm_count(self, new_count: int, session_defeated: int = 0) -> bool:
        """Actualiza el contador total de gusanos derrotados"""
        try:
            data = self.load_game_data()
            
            # Actualizar contador total
            data["total_worms_defeated"] = new_count
            
            # Actualizar estadísticas de sesión
            if session_defeated > data["session_stats"]["best_worm_streak"]:
                data["session_stats"]["best_worm_streak"] = session_defeated
            
            # Achievements
            if new_count >= 25 and not data["achievements"]["level_2_unlocked"]:
                data["achievements"]["level_2_unlocked"] = True
                print("🏆 ¡Achievement desbloqueado: Nivel 2!")
            
            if new_count >= 100 and not data["achievements"]["first_victory"]:
                data["achievements"]["first_victory"] = True
                print("🏆 ¡Achievement desbloqueado: Primera Victoria!")
            
            return self.save_game_data(data)
        except Exception as e:
            print(f"❌ Error actualizando contador de gusanos: {e}")
            return False
    
    def get_total_worms_defeated(self) -> int:
        """Obtiene el total de gusanos derrotados"""
        data = self.load_game_data()
        return data.get("total_worms_defeated", 0)
    
    def reset_game_data(self) -> bool:
        """Resetea todos los datos del juego (para debugging)"""
        try:
            return self.save_game_data(self.default_game_data.copy())
        except Exception as e:
            print(f"❌ Error reseteando datos: {e}")
            return False
    
    def get_collision_blocks_as_rects(self, block_size: int = 32) -> List[pygame.Rect]:
        """Obtiene los bloques de colisión como rectángulos de pygame"""
        data = self.load_collision_data()
        blocks = []
        
        for block_data in data.get("blocks", []):
            rect = pygame.Rect(block_data["x"], block_data["y"], block_size, block_size)
            blocks.append(rect)
        
        return blocks
    
    def get_stats_summary(self) -> Dict[str, Any]:
        """Obtiene resumen de estadísticas para mostrar en UI"""
        data = self.load_game_data()
        collision_data = self.load_collision_data()
        
        return {
            "total_worms": data.get("total_worms_defeated", 0),
            "current_level": data.get("current_level", 1),
            "best_streak": data["session_stats"]["best_worm_streak"],
            "total_blocks": len(collision_data.get("blocks", [])),
            "achievements_unlocked": sum(1 for v in data["achievements"].values() if v),
            "level_2_unlocked": data["achievements"]["level_2_unlocked"]
        }

# Instancia global para fácil acceso
game_data = GameDataManager()

def get_game_data_manager() -> GameDataManager:
    """Obtiene la instancia global del manager de datos"""
    return game_data