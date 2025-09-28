import pygame
import os
from character_base import CharacterBase

class JuanCharacter(CharacterBase):
    def __init__(self, x, y):
        super().__init__(x, y, "Juan", "assets/characters/juan/animations")
        self.max_health = 100
        self.health = self.max_health
        self.speed = 6
        self.damage = 22
        self.mana = 100
        self.max_mana = 100
        print(f"Juan creado en ({x}, {y})")
    
    def cast_spell(self, spell_cost=20):
        if self.mana >= spell_cost:
            self.mana -= spell_cost
            return True
        return False
