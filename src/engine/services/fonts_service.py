
import pygame

class FontsService:
    def __init__(self):
        self._fonts = {}

    def get(self, path: str, size: int) -> pygame.font.Font:
        
        font_key = f"{path}_{size}"
        if font_key not in self._fonts:
            try:
                self._fonts[font_key] = pygame.font.Font(path, size)
            except pygame.error as e:
                print(f"Error loading font {path}: {e}")
                
                self._fonts[font_key] = pygame.font.SysFont("arial", size)
        return self._fonts[font_key]