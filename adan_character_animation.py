import pygame
import os
from character_base import CharacterBase

class AdanCharacter(CharacterBase):
    def __init__(self, x, y):
        super().__init__(x, y, "Adan", "assets/characters/adan/animations")
        self.max_health = 125
        self.health = self.max_health
        self.damage = 28
        print(f"Adan creado en ({x}, {y})")
    
    def take_damage(self, damage):
        reduced_damage = int(damage * 0.8)
        return super().take_damage(reduced_damage)
