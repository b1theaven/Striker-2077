import pygame
from OpenGL.GL import *

s_width, s_height = 800, 600

class PlayerBullet:
    def __init__(self, img_path, x, y, scale=(20, 20)):
        self.width, self.height = scale
        self.texture = self.load_texture(img_path)
        self.position = [x, y]
        self.speed = 5
        self.active = True

    def load_texture(self, img_path):
        image = pygame.image.load(img_path).convert_alpha()
        image = pygame.transform.scale(image, (self.width, self.height))
        image = pygame.transform.rotate(image, 180)
        width, height = image.get_size()
        image_data = pygame.image.tostring(image, "RGBA", True)

        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
        return texture

    def update(self):
        if self.active:
            self.position[1] -= self.speed
            if self.position[1] < 0:
                self.active = False
        
    def draw(self):
        if self.active:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture)
            glColor4f(1, 1, 1, 1)

            x, y = self.position
            width, height = self.width, self.height
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0); glVertex2f(x, y)
            glTexCoord2f(1, 0); glVertex2f(x + width, y)
            glTexCoord2f(1, 1); glVertex2f(x + width, y + height)
            glTexCoord2f(0, 1); glVertex2f(x, y + height)
            glEnd()

            glDisable(GL_TEXTURE_2D)

class EnemyBullet:
    def __init__(self, img_path, x, y, scale=(20, 20)):
        self.image = pygame.image.load(img_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, scale)
        self.width, self.height = scale
        self.position = [x, y]
        self.active = True
        self.texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        texture_data = pygame.image.tostring(self.image, "RGBA", True)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    def update(self):
        self.position[1] += 3
        if self.position[1] > s_height:
            self.active = False

    def draw(self):
        if not self.active:
            return

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0)
        glVertex2f(self.position[0], self.position[1])
        glTexCoord2f(1, 0)
        glVertex2f(self.position[0] + self.width, self.position[1])
        glTexCoord2f(1, 1)
        glVertex2f(self.position[0] + self.width, self.position[1] + self.height)
        glTexCoord2f(0, 1)
        glVertex2f(self.position[0], self.position[1] + self.height)
        glEnd()
        glDisable(GL_TEXTURE_2D)