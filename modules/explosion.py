import pygame
from OpenGL.GL import *

class Explosion:
    def __init__(self, x, y):
        self.textures = []
        for i in range(1, 6):
            img = pygame.image.load(f'assets/images/exp{i}.png').convert_alpha()
            img = pygame.transform.scale(img, (120, 120))
            texture = self._load_texture(img)
            self.textures.append(texture)
        self.index = 0
        self.position = [x, y]
        self.scale = 75
        self.count_delay = 0

    def _load_texture(self, img):
        texture_data = pygame.image.tostring(img, "RGBA", True)
        width, height = img.get_size()
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
        return texture_id

    def update(self):
        self.count_delay += 1
        if self.count_delay >= 12:
            if self.index < len(self.textures) - 1:
                self.index += 1
        if self.index >= len(self.textures) - 1 and self.count_delay >= 12:
            return False
        return True

    def draw(self):
        if self.index < len(self.textures):
            texture = self.textures[self.index]
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, texture)
            glColor3f(1, 1, 1)
            x, y = self.position
            size = self.scale
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0); glVertex2f(x, y)
            glTexCoord2f(1, 0); glVertex2f(x + size, y)
            glTexCoord2f(1, 1); glVertex2f(x + size, y + size)
            glTexCoord2f(0, 1); glVertex2f(x, y + size)
            glEnd()
            glDisable(GL_TEXTURE_2D)