import random
from OpenGL.GL import *

s_width, s_height = 800, 600

class Background:
    def __init__(self, x, y):
        self.size = (x, y)
        self.position = [random.randint(0, s_width), random.randint(0, s_height)]

    def update(self):
        self.position[1] += 1
        self.position[0] += 1

        if self.position[1] > s_height:
            self.position[1] = random.randrange(-10, 0)
            self.position[0] = random.randrange(-400, s_width)

    def draw(self):
        glColor3f(1, 1, 1)
        glBegin(GL_QUADS)
        x, y = self.position
        size_x, size_y = self.size
        glVertex2f(x, y)
        glVertex2f(x + size_x, y)
        glVertex2f(x + size_x, y + size_y)
        glVertex2f(x, y + size_y)
        glEnd()