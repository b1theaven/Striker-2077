import random
from modules.player import Player
from modules.bullet import EnemyBullet

s_width, s_height = 800, 600

class Enemy(Player):
    def __init__(self, img_path, game, scale=(50, 50)):
        super().__init__(img_path, game, scale)
        self.scale = scale
        self.texture = self.load_texture(img_path)
        self.width, self.height = scale
        self.position = [random.randint(50, s_width - 50), random.randint(-500, 0)]
        self.shoot_interval = random.randint(100, 200)
        self.shoot_timer = 0

    def update(self, game):
        self.position[1] += 1
        if self.position[1] > s_height:
            self.reset_position()

        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_interval:
            self.shoot(game)
            self.shoot_timer = 0
    
    def reset_position(self):
        self.position = [random.randint(0, s_width - self.width), random.randint(-100, -50)]
        self.active = True

    def shoot(self, game):
        bullet_scale = (20, 20)
        bullet_width = bullet_scale[0]
        bullet_height = bullet_scale[1]
        bullet_x = self.position[0] + self.width // 2 - (bullet_width // 2)
        bullet_y = self.position[1] + self.height   
        enemy_bullet = EnemyBullet("assets/images/peluru-musuh.png", bullet_x, bullet_y, scale = bullet_scale)
        game.enemy_bullets.append(enemy_bullet)

    def draw(self):
        super().draw()

