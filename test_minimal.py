#!/usr/bin/env python3

import pygame
from worm_enemy import WormSpawner

def test_minimal():
    """Test mínimo para verificar WormSpawner"""
    pygame.init()
    
    print("🔍 Test: Inicializando pygame...")
    screen = pygame.display.set_mode((800, 600))
    
    print("🔍 Test: Creando WormSpawner...")
    worm_spawner = WormSpawner(max_worms=15)
    print("✅ Test: WormSpawner creado exitosamente")
    
    print("🔍 Test: Probando métodos...")
    worms = worm_spawner.get_worms()
    print(f"✅ Test: get_worms() devuelve: {len(worms)} gusanos")
    
    pygame.quit()
    print("✅ Test completado exitosamente")

if __name__ == "__main__":
    test_minimal()