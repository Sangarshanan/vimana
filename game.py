"""
Vimana: A Space Shooter.

For Nostalgia ...

░▄░▀▄░░░▄▀░▄░
░█▄███████▄█░
░███▄███▄███░
░▀█████████▀░
░░▄▀░░░░░▀▄░░


The Coordinate System
Top left corner of the screen is (0,0)
Bottom right is (width, height)
     0
     ^
     |
     |
0 <-----> Width
     |
     |
   height
"""

import os
import time
import pygame
import random
import pygame.locals as loc

screen_width = 1500
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))

WHITE = (255, 255, 255)
BLACK = (0,0,0)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        # Read the Image and get the rectangular area out of the surface
        self.surf = pygame.transform.scale(
            pygame.image.load("images/player.png"), (100, 50)
        )
        self.rect = self.surf.get_rect()
        self.speed = 2

    def update(self, **kwargs):
        # Move the Rectangular area In-Place
        pressed_keys = kwargs["pressed_keys"]
        if pressed_keys[loc.K_UP] and self.rect.top >= 0:
            self.rect.move_ip(0, -self.speed)
        if pressed_keys[loc.K_DOWN] and self.rect.bottom <= screen_height:
            self.rect.move_ip(0, self.speed)
        if pressed_keys[loc.K_LEFT] and self.rect.left > 0:
            self.rect.move_ip(-self.speed, 0)
        if pressed_keys[loc.K_RIGHT] and self.rect.right < screen_width:
            self.rect.move_ip(self.speed, 0)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Bullet, self).__init__()
        self.surf = pygame.transform.rotate(
            pygame.image.load("images/lasers/laser_red.png"), 270
        )
        self.rect = self.surf.get_rect(topleft=(x, y))
        self.speed = 7

    def update(self, **kwargs):
        self.rect.move_ip(self.speed, 0)
        # If it crosses the border disappear
        if self.rect.left < 0:
            self.kill()


class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(EnemyBullet, self).__init__()
        self.surf = pygame.transform.rotate(
            pygame.image.load("images/lasers/laser_green.png"), 90
        )
        self.rect = self.surf.get_rect(topleft=(x, y))
        self.speed = 4

    def update(self, **kwargs):
        self.rect.move_ip(-self.speed, 0)
        # If it crosses the border disappear
        if self.rect.left < 0:
            self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self).__init__()
        self.surf = pygame.image.load("images/enemy_ship.png")
        self.rect = self.surf.get_rect(
            center=(screen_width, random.randint(50, screen_height - 50))
        )
        self.speed = random.randint(1, 2)

    def update(self, **kwargs):
        # Keep moving right
        self.rect.move_ip(-self.speed, 0)
        # If it crosses the border disappear
        if self.rect.right < 0:
            self.kill()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, images):
        super(Explosion, self).__init__()
        self.images = images
        self.surf = self.images[0]
        self.rect = self.surf.get_rect()
        self.rect.center = center
        self.frame = 0
        self.updated_at = pygame.time.get_ticks()
        self.fps = 70

    def update(self, **kwargs):
        now = pygame.time.get_ticks()
        if now - self.updated_at > self.fps:
            self.updated_at = now
            self.frame += 1
            if self.frame == len(self.images):
                self.kill()
            else:
                center = self.rect.center
                self.surf = self.images[self.frame]
                self.rect = self.surf.get_rect()
                self.rect.center = center


class Vimana(object):
    def __init__(self):
        """Initialize."""
        pygame.init()
        pygame.display.set_caption("🛸 Vimana 🛸")

    def _init_game(self):
        self.background = pygame.image.load("images/background.jpeg")

        self.player = Player()
        self.player_x, self.player_y = self.player.surf.get_size()

        self.NEWENEMY = pygame.USEREVENT + 1
        self.ENEMYSHOOT = pygame.USEREVENT + 2
        pygame.time.set_timer(self.NEWENEMY, 1000)
        pygame.time.set_timer(self.ENEMYSHOOT, 500)

        self.enemy_list = []
        self.enemy_group = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.bullet_group = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)

        self.font_100 = pygame.font.Font('fonts/samarkan.ttf', 100)
        self.font_50 = pygame.font.Font(None, 50)
        self.font_30 = pygame.font.Font(None, 30)
        self.font_40 = pygame.font.Font(None, 40)

        self.reload_time = 0.5  # Seconds it takes to reload after a shot
        self.next_shot_time = 0  # Can we fire yet ? current_time + reload_time

        self.enemy_explosion_images = []
        enemy_explosion_anim_path = "images/explosions/enemy/"
        _, _, img_paths = next(os.walk(enemy_explosion_anim_path))
        for img_path in sorted(img_paths):
            img = pygame.image.load(os.path.join(enemy_explosion_anim_path, img_path))
            img_ts = pygame.transform.scale(img, (100, 100))
            self.enemy_explosion_images.append(img_ts)

        self.player_shoot_sound = pygame.mixer.Sound('sounds/laser_player.ogg')
        self.enemy_shoot_sound = pygame.mixer.Sound('sounds/laser_enemy.ogg')

        self.initial_score = 0

        self.home_screen = True
        self.game_loop = True
        self.game_over = False

    def _game_over(self):
        self.player.kill()
        text_go = self.font_50.render("Game Over", True, WHITE)
        text_restart = self.font_30.render("Press R to restart", True, WHITE)
        text_go_rect = text_go.get_rect(
            center=(screen.get_width() / 2, screen.get_height() / 2,)
        )
        screen.blit(text_go, text_go_rect)
        text_restart_rect = text_restart.get_rect(
            center=(screen.get_width() / 2, screen.get_height() / 2 + 50,)
        )
        screen.blit(text_restart, text_restart_rect)

    def _home_screen(self):
        self.home_background = pygame.transform.scale(
            pygame.image.load("images/galaxy.jpeg"), (screen_width, screen_height)
        )
        screen.blit(self.home_background, (0, 0))

        text = self.font_100.render("Vimana", False, WHITE)
        text_rect = text.get_rect(
            center=(screen.get_width() / 2, screen.get_height() / 3,)
        )
        screen.blit(text, text_rect)

        text_sub = self.font_30.render("-----A Space Shooter---->", True, WHITE)
        text_sub_rect = text_sub.get_rect(
            center=(screen.get_width() / 2, screen.get_height() / 3 + 50,)
        )
        screen.blit(text_sub, text_sub_rect)

        text_start = self.font_40.render("Press Enter to Start", True, WHITE)
        text_start_rect = text_start.get_rect(
            center=(screen.get_width() / 2, screen.get_height() / 2,)
        )
        screen.blit(text_start, text_start_rect)

        text_bottom = self.font_30.render("Made Ironically by Sangarshanan", True, WHITE)
        text_bottom_rect = text_bottom.get_rect(
            center=(screen.get_width() / 2+20, screen_height-50,)
        )
        screen.blit(text_bottom, text_bottom_rect)


    def _score(self, increment=0):
        self.initial_score += increment
        text = self.font_50.render(f"Score: {self.initial_score}", False, WHITE)
        text_rect = text.get_rect(center=(screen.get_width() - 100, 50))
        screen.blit(text, text_rect)

    def main(self):
        """Game loop."""
        self._init_game()
        pygame.mixer.music.load('sounds/homescreen.ogg')
        pygame.mixer.music.play(-1)

        while self.game_loop:
            if self.home_screen:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            self.home_screen = False
                self._home_screen()
            else:
                current_time = time.time()

                for event in pygame.event.get():
                    if event.type == loc.QUIT:
                        pygame.mixer.music.stop()
                        self.game_loop = False

                    # Enemy Spawns
                    if event.type == self.NEWENEMY:
                        new_enemy = Enemy()
                        self.enemy_group.add(new_enemy)
                        self.enemy_list.append(new_enemy)
                        self.all_sprites.add(new_enemy)

                    # Enemy Shoots
                    if event.type == self.ENEMYSHOOT and self.enemy_group:
                        random_enemy = random.choice(self.enemy_list)
                        # Enemy is alive and has not crossed half the screen
                        if (
                            random_enemy.alive()
                            and random_enemy.rect.right > screen_width / 2
                        ):
                            self.enemy_shoot_sound.play()
                            enemy_bullet = EnemyBullet(
                                random_enemy.rect.x - 30, random_enemy.rect.y + 30
                            )
                            self.enemy_bullets.add(enemy_bullet)
                            self.all_sprites.add(enemy_bullet)
                    # React to Keypresses
                    if event.type == pygame.KEYDOWN:

                        # Shoot Bullets
                        if (
                            event.key == pygame.K_SPACE
                            and current_time > self.next_shot_time
                        ):
                            self.player_shoot_sound.play()
                            self.next_shot_time = current_time + self.reload_time
                            bullet = Bullet(
                                self.player.rect.x + self.player_x,
                                self.player.rect.y + self.player_y / 2,
                            )
                            self.bullet_group.add(bullet)
                            self.all_sprites.add(bullet)

                        # Restart
                        if event.key == pygame.K_r:
                            self.game_over = False
                            self._init_game()
                            self.main()

                screen.blit(self.background, (0, 0))
                pressed_keys = pygame.key.get_pressed()

                self._score()
                if self.game_over:
                    self._game_over()

                if pygame.sprite.spritecollideany(
                    self.player, self.enemy_group
                ) or pygame.sprite.spritecollideany(self.player, self.enemy_bullets):
                    self.player.kill()
                    self.game_over = True
                for enemy in pygame.sprite.groupcollide(
                    self.enemy_group, self.bullet_group, True, True
                ).keys():
                    explosion = Explosion(
                        enemy.rect.center, self.enemy_explosion_images
                    )
                    self.all_sprites.add(explosion)
                    self._score(increment=1)
                    enemy.kill()

                for entity in self.all_sprites:
                    entity.update(pressed_keys=pressed_keys, player=self.player)
                    screen.blit(entity.surf, entity.rect)

            pygame.display.flip()


if __name__ == "__main__":
    game = Vimana()
    game.main()
