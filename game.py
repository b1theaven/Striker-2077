import pygame, sys, random
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

from modules.background import Background
from modules.particle import Particle
from modules.player import Player
from modules.enemy import Enemy, Bos
from modules.bullet import PlayerBullet, EnemyBullet
from modules.explosion import Explosion

s_width, s_height = 800, 600
lives = 3

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_mode((s_width, s_height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("STRIKER 2077")
        gluOrtho2D(0, s_width, s_height, 0)
        pygame.mouse.set_visible(False)
        
        self.paused = False
        self.shoot_sound = pygame.mixer.Sound('assets/audios/laser.wav')
        self.explosion_sound = pygame.mixer.Sound('assets/audios/low_expl.wav')
        self.background_objects = []
        self.particles =[]
        self.player = None
        self.enemies = []
        self.bos = None
        self.bosbullet_group = []
        self.player_bullets = []
        self.bos_bullets = []
        self.enemy_bullets= []
        self.explosions = []
        self.score = 0
        self.count_hit = 0
        self.count_hit2 = 0
        self.lives = 3
        self.life_icon, self.life_icon_scale = self.load_life_icon("assets/images/pesawat.png", (20, 20))
        self.create_background()
        self.create_particles()
        self.create_player()
        self.create_enemy()
        self.create_bos()

    def create_background(self):
        for _ in range(30):
            size = random.randint(1, 5)
            bg = Background(size, size)
            self.background_objects.append(bg)
    
    def create_particles(self):
        for _ in range(60):
            size_x = 1
            size_y = random.randint(1, 7)
            particle = Particle(size_x, size_y)
            self.particles.append(particle)

    def load_life_icon(self, img_path, scale):
        image = pygame.image.load(img_path).convert_alpha()
        image = pygame.transform.scale(image, scale)
        width, height = image.get_size()
        image_data = pygame.image.tostring(image, "RGBA", True)
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
        return texture, (width, height)
    
    def draw_lives(self):
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.life_icon)
        icon_width, icon_height = self.life_icon_scale
        for i in range(self.lives):
            x = 10 + i * (icon_width + 5)
            y = 10
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0); glVertex2f(x, y)
            glTexCoord2f(1, 0); glVertex2f(x + icon_width, y)
            glTexCoord2f(1, 1); glVertex2f(x + icon_width, y + icon_height)
            glTexCoord2f(0, 1); glVertex2f(x, y + icon_height)
            glEnd()
        glDisable(GL_TEXTURE_2D)
    
    def draw_score(self):
        pygame.font.init()
        score_font = pygame.font.Font(None, 20)
        score_text = f"Score: {self.score}"
        score_surface = score_font.render(score_text, True, (255, 255, 255))
        score_data = pygame.image.tostring(score_surface, "RGBA", True)
        score_width, score_height = score_surface.get_size()
        x = s_width - score_width - 10
        y = 30

        glRasterPos2i(x, y)
        glDrawPixels(score_width, score_height, GL_RGBA, GL_UNSIGNED_BYTE, score_data)

    def create_player(self):
        self.player = Player("assets/images/pesawat.png", self)
    
    def create_enemy(self):
        self.enemies = []
        for _ in range(5):
            enemy = Enemy("assets/images/pesawat-musuh.png", self)
            self.enemies.append(enemy)

    def create_bos(self):
        self.bos = Bos("assets/images/bos.png", self)

    def player_crash_with_enemy(self):
        if not self.player.alive or self.player.invulnerable:
            return

        for enemy in self.enemies:
            if (
                self.player.position[0] < enemy.position[0] + enemy.width
                and self.player.position[0] + self.player.width > enemy.position[0]
                and self.player.position[1] < enemy.position[1] + enemy.height
                and self.player.position[1] + self.player.height > enemy.position[1]
            ):
                self.add_explosion(self.player.position[0] + self.player.width // 2, 
                                self.player.position[1] + self.player.height // 2)
                self.lives -= 1
                self.score += 1
                self.player.dead()
                self.add_explosion(enemy.position[0] + enemy.width // 2, 
                                enemy.position[1] + enemy.height // 2)
                enemy.reset_position()

                pygame.mixer.Sound.play(self.explosion_sound)
                break
    
    def player_crash_with_bos(self):
        if not self.player.alive or self.player.invulnerable:
            return

        if self.bos:
            if (
                self.player.position[0] < self.bos.position[0] + self.bos.width and
                self.player.position[0] + self.player.width > self.bos.position[0] and
                self.player.position[1] < self.bos.position[1] + self.bos.height and
                self.player.position[1] + self.player.height > self.bos.position[1]
            ):
                self.add_explosion(self.player.position[0] + self.player.width // 2,
                                self.player.position[1] + self.player.height // 2)
                self.lives -= 1
                self.player.dead()

                pygame.mixer.Sound.play(self.explosion_sound)
    
    def player_shoot(self):
        if self.player.alive:
            bullet_x = self.player.position[0] + self.player.width // 2 - 5
            bullet_y = self.player.position[1]
            bullet = PlayerBullet("assets/images/peluru-player.png", bullet_x, bullet_y, scale=(25, 25))
            self.player_bullets.append(bullet)
            self.shoot_sound.play()
    
    def enemy_shoot(self, enemy):
        bullet = EnemyBullet("assets/images/peluru-player.png", enemy.position[0], enemy.position[1])
        self.enemy_bullets.append(bullet)

    def update_bullets(self):
        for bullet in self.player_bullets:
            bullet.update()
            if not bullet.active:
                self.player_bullets.remove(bullet)

    def draw_bullets(self):
        for bullet in self.player_bullets:
            bullet.update()
            bullet.draw()
        for bullet in self.enemy_bullets:
            bullet.update()
            bullet.draw()
        for bullet in self.bos_bullets:
            bullet.update()
            bullet.draw()

    def playerbullet_hits_enemy(self):
        for enemy in self.enemies:
            for bullet in self.player_bullets:
                if bullet.active and enemy.alive:
                    if (
                        enemy.position[0] - enemy.width / 2 < bullet.position[0] < enemy.position[0] + enemy.width / 2 and
                        enemy.position[1] - enemy.height / 2 < bullet.position[1] < enemy.position[1] + enemy.height / 2
                    ):
                        bullet.active = False
                        self.count_hit += 1
                        if self.count_hit == 3:
                            self.score += 1
                            explosion = Explosion(enemy.position[0] + (enemy.width // 2), enemy.position[1] + (enemy.height // 2))
                            self.add_explosion(explosion.position[0], explosion.position[1])
                            enemy.reset_position()
                            self.count_hit = 0
                            self.explosion_sound.play()

    def add_explosion(self, x, y):
        explosion = Explosion(x, y)
        self.explosions.append(explosion)

    def update_explosions(self):
        for explosion in self.explosions[:]:
            if not explosion.update():
                self.explosions.remove(explosion)

    def draw_explosions(self):
        for explosion in self.explosions:
            explosion.draw()

    def playerbullet_hits_bos(self):
        if not self.bos or not self.bos.active:
            return

        for bullet in self.player_bullets:
            if (
                self.bos.position[0] - self.bos.width / 2 < bullet.position[0] < self.bos.position[0] + self.bos.width / 2
                and self.bos.position[1] - self.bos.height / 2 < bullet.position[1] < self.bos.position[1] + self.bos.height / 2
            ):
                bullet.active = False
                self.count_hit2 += 1

                if self.count_hit2 == 30:
                    self.score += 20

                    for _ in range(5):
                        offset_x = random.randint(-50, 50)
                        offset_y = random.randint(-50, 50)
                        explosion = Explosion(
                            self.bos.position[0] + self.bos.width // 2 + offset_x,
                            self.bos.position[1] + self.bos.height // 2 + offset_y
                        )
                        self.add_explosion(explosion.position[0], explosion.position[1])

                    self.bos.reset_position()
                    self.count_hit2 = 0
                    self.explosion_sound.play()
    
    def enemybullet_hits_player(self):
        if not self.player.alive or self.player.invulnerable:
            return
        
        for bullet in self.enemy_bullets:
            if self.player.is_hit(bullet.position):
                self.enemy_bullets.remove(bullet)
                self.lives -= 1
                self.player.dead()

    def bosbullet_hits_player(self):
        if not self.player.alive or self.player.invulnerable:
            return
        
        for bullet in self.bos_bullets:
            if self.player.is_hit(bullet.position):
                self.bos_bullets.remove(bullet)
                self.lives -= 1
                self.player.dead()

    def show_pause_screen(self):
        pygame.font.init()
        font = pygame.font.Font(None, 60)
        text_surface = font.render("PAUSED", True, (255, 255, 255))
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        text_width, text_height = text_surface.get_size()

        glRasterPos2i((s_width - text_width) // 2, s_height // 2)
        glDrawPixels(text_width, text_height, GL_RGBA, GL_UNSIGNED_BYTE, text_data)

    def game_over_screen(self):
        print("Game Over!")
        pygame.mixer.music.stop()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        pygame.font.init()
        title_font = pygame.font.Font(None, 80)
        instr_font = pygame.font.Font(None, 30)
        score_font = pygame.font.Font(None, 40)
        title_surface = title_font.render("GAME OVER", True, (255, 0, 0))
        title_data = pygame.image.tostring(title_surface, "RGBA", True)
        title_width, title_height = title_surface.get_size()
        instr_surface = instr_font.render("ESC untuk keluar, Enter untuk coba lagi", True, (255, 0, 0))
        instr_data = pygame.image.tostring(instr_surface, "RGBA", True)
        instr_width, instr_height = instr_surface.get_size()
        score_text = f"Skor Akhir: {self.score}"
        score_surface = score_font.render(score_text, True, (255, 255, 0))
        score_data = pygame.image.tostring(score_surface, "RGBA", True)
        score_width, score_height = score_surface.get_size()
 
        title_x = (s_width - title_width) // 2
        title_y = s_height // 2 - title_height
        instr_x = (s_width - instr_width) // 2
        instr_y = s_height // 2 + 20
        score_x = (s_width - score_width) // 2
        score_y = title_y - score_height - 50
        game_over_voice = pygame.mixer.Sound('assets/audios/game_over.wav')
        game_over_voice.play()
        clock = pygame.time.Clock()
        elapsed = 0

        while elapsed < 1500:
            dt = clock.tick(60)
            elapsed += dt
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glRasterPos2i(score_x, score_y)
            glDrawPixels(score_width, score_height, GL_RGBA, GL_UNSIGNED_BYTE, score_data)
            glRasterPos2i(title_x, title_y)
            glDrawPixels(title_width, title_height, GL_RGBA, GL_UNSIGNED_BYTE, title_data)
            glRasterPos2i(instr_x, instr_y)
            glDrawPixels(instr_width, instr_height, GL_RGBA, GL_UNSIGNED_BYTE, instr_data)
            pygame.display.flip()

        pygame.mixer.music.load('assets/audios/illusoryrealm.mp3')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == K_RETURN or event.key == K_KP_ENTER:
                        waiting = False

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glRasterPos2i(score_x, score_y)
            glDrawPixels(score_width, score_height, GL_RGBA, GL_UNSIGNED_BYTE, score_data)
            glRasterPos2i(title_x, title_y)
            glDrawPixels(title_width, title_height, GL_RGBA, GL_UNSIGNED_BYTE, title_data)
            glRasterPos2i(instr_x, instr_y)
            glDrawPixels(instr_width, instr_height, GL_RGBA, GL_UNSIGNED_BYTE, instr_data)
            pygame.display.flip()
            
        pygame.mixer.music.stop()
        self.reset_game_state()

    def reset_game_state(self):
        self.score = 0
        self.lives = 3
        self.count_hit = 0
        self.count_hit2 = 0
        self.player_bullets.clear()
        self.enemy_bullets.clear()
        self.bos_bullets.clear()
        self.explosions.clear()
        self.player.position = [s_width // 2, s_height // 2]
        self.player.alive = True
        self.player.invulnerable = False
        
        for enemy in self.enemies:
            enemy.reset_position()
        
        if self.bos:
            self.bos.reset_position()
        
        pygame.mixer.music.load('assets/audios/epicsong.mp3')
        pygame.mixer.music.play(-1)

    def start_screen(self):
        pygame.mixer.music.load('assets/audios/cyberfunk.mp3')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        go_sound = pygame.mixer.Sound('assets/audios/go.wav')

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        pygame.font.init()
        title_font = pygame.font.Font(None, 80)
        subtitle_font = pygame.font.Font(None, 30)
        title_surface = title_font.render("STRIKER 2077", True, (255, 255, 255))
        title_data = pygame.image.tostring(title_surface, "RGBA", True)
        title_width, title_height = title_surface.get_size()
        subtitle_surface = subtitle_font.render("Tekan spasi untuk memulai!", True, (255, 255, 255))
        subtitle_data = pygame.image.tostring(subtitle_surface, "RGBA", True)
        subtitle_width, subtitle_height = subtitle_surface.get_size()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        go_sound.play()
                        waiting = False

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            glRasterPos2i((s_width - title_width) // 2, s_height // 2 - 50)
            glDrawPixels(title_width, title_height, GL_RGBA, GL_UNSIGNED_BYTE, title_data)
            glRasterPos2i((s_width - subtitle_width) // 2, s_height // 2 + 20)
            glDrawPixels(subtitle_width, subtitle_height, GL_RGBA, GL_UNSIGNED_BYTE, subtitle_data)

            pygame.display.flip()

        pygame.mixer.music.stop()

    def run(self):
        pygame.mixer.music.load('assets/audios/epicsong.mp3')
        pygame.mixer.music.play(-1)
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.player_shoot()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        if not self.paused:
                            self.paused = True
                            self.pause_start_time = pygame.time.get_ticks()
                            pygame.mixer.music.pause()
                        else:
                            self.paused = False
                            pause_duration = pygame.time.get_ticks() - self.pause_start_time
                            self.player.invulnerable_timer += pause_duration
                            pygame.mixer.music.unpause()
                            
            if self.paused:
                self.show_pause_screen()
                pygame.display.flip()
                continue
            
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            for bg in self.background_objects:
                bg.update()
                bg.draw()

            for particle in self.particles:
                particle.update()
                particle.draw()


            for enemy in self.enemies:
                enemy.update(self)
                enemy.draw()

            if self.bos:
                self.bos.update()
                self.bos.draw()

            for bullet in self.bosbullet_group:
                bullet.update()
                bullet.draw()

            self.player.update()
            self.player.draw()
            self.draw_lives()
            self.player_crash_with_enemy()
            self.player_crash_with_bos()
            self.update_bullets()
            self.draw_bullets()
            self.update_explosions()
            self.draw_explosions()
            self.draw_score()
            self.playerbullet_hits_enemy()
            self.playerbullet_hits_bos()
            self.enemybullet_hits_player()
            self.bosbullet_hits_player()

            pygame.display.flip()
            clock.tick(60)

            if self.lives == 0:
                self.game_over_screen()

        pygame.mixer.music.stop()
    

if __name__ == "__main__":
    game = Game()
    game.start_screen()
    game.run()