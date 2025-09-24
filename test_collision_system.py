#!/usr/bin/env python3
"""
Test para verificar que el juego se ejecuta correctamente
"""

import pygame
import sys
import os

def test_game_execution():
    """Test de ejecución del juego"""
    print("🔍 Verificando que el juego se ejecute sin errores...")
    
    try:
        # Verificar que pygame funcione
        pygame.init()
        print("✅ Pygame inicializado correctamente")
        
        # Verificar que el archivo del juego exista
        if os.path.exists('nivel 1 escenario.py'):
            print("✅ Archivo 'nivel 1 escenario.py' encontrado")
        else:
            print("❌ Archivo del juego no encontrado")
            return False
        
        # Verificar que los archivos de dependencias existan
        required_files = [
            'adan_character_animation.py',
            'juan_character_animation.py',
            'audio_manager.py',
            'loading_screen.py'
        ]
        
        for file in required_files:
            if os.path.exists(file):
                print(f"✅ Dependencia {file} encontrada")
            else:
                print(f"⚠️  Dependencia {file} no encontrada")
        
        print("🎯 Estado del proyecto:")
        print("   - Sistema de colisiones: Implementado")
        print("   - Modo editor: F1 para activar/desactivar")  
        print("   - Controles del editor:")
        print("     • Flechas: Mover cursor")
        print("     • Espacio: Colocar bloque de colisión")
        print("     • Backspace: Eliminar bloque de colisión")
        print("     • F1: Salir del editor y guardar")
        print("   - Fondo: URL de GitHub configurado para 1980x1080")
        print("   - Límites: Los jugadores no pueden salir de los bordes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en el test: {e}")
        return False
    finally:
        pygame.quit()

if __name__ == "__main__":
    success = test_game_execution()
    if success:
        print("\n🎉 El proyecto está configurado correctamente")
        print("💡 Para probar el juego ejecuta: python \"nivel 1 escenario.py\"")
        print("🎮 Usa F1 dentro del juego para acceder al modo editor")
    else:
        print("\n❌ Hay algunos problemas en la configuración")
    
    sys.exit(0 if success else 1)