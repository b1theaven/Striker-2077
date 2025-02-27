import pygame
from OpenGL.GL import *
from OpenGL.GL import GL_BLEND, GL_ONE_MINUS_SRC_ALPHA, GL_LINEAR

from modules.explosion import Explosion

s_width, s_height = 800, 600

class Player:
    def __init__(self, img_path, game, scale=(75, 75)):
        self.scale = scale
        self.texture = self.load_texture(img_path)
        self.width, self.height = scale
        self.position = [s_width // 2, s_height // 2]
        self.alive = True
        self.count_to_live = 0
        self.invulnerable = False
        self.invulnerable_timer = 0 
        self.activate_bullet = True
        self.alpha_duration = 0
        self.game = game

    def load_texture(self, img_path):
        image = pygame.image.load(img_path).convert_alpha()
        image = pygame.transform.scale(image, self.scale)
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
        if not self.alive:
            self.position[1] = s_height + 200
            current_time = pygame.time.get_ticks()
            if current_time - self.invulnerable_timer > 3000:
                self.alive = True
                self.invulnerable = False
                self.invulnerable_timer = pygame.time.get_ticks()
            return

        if self.invulnerable:
            current_time = pygame.time.get_ticks()
            if (current_time // 200) % 2 == 0:
                self.draw()
        else:
            self.draw()

        if self.alive:
            self.alpha_duration += 1
            if self.alpha_duration > 170:
                self.alpha_duration = 0
            mouse = pygame.mouse.get_pos()
            self.position[0] = mouse[0] - self.scale[0] // 2
            self.position[1] = mouse[1] - self.scale[1] // 2
        else:
            self.alpha_duration = 0
            self.position[1] = s_height + 200
            self.count_to_live += 1
            if self.count_to_live > 100:
                self.alive = True
                self.count_to_live = 0
                self.activate_bullet = True

    def draw(self):
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glColor4f(1, 1, 1, 1)

        x, y = self.position
        width, height = self.scale
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(x, y)
        glTexCoord2f(1, 0); glVertex2f(x + width, y)
        glTexCoord2f(1, 1); glVertex2f(x + width, y + height)
        glTexCoord2f(0, 1); glVertex2f(x, y + height)
        glEnd()

        glDisable(GL_TEXTURE_2D)

    def shoot(self):
        if self.activate_bullet:
            pass
    
    def is_hit(self, bullet_position):
        bullet_x, bullet_y = bullet_position
        if (
            self.position[0] < bullet_x < self.position[0] + self.width
            and self.position[1] < bullet_y < self.position[1] + self.height
        ):
            return True
        return False

    def dead(self):
        self.alive = False
        self.invulnerable = True
        self.invulnerable_timer = pygame.time.get_ticks()
        self.activate_bullet = False
        explosion = Explosion(self.position[0], self.position[1])
        self.game.add_explosion(explosion.position[0], explosion.position[1])

        pygame.mixer.Sound.play(self.game.explosion_sound)