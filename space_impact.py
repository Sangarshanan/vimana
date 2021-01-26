"""
Space Impact.

For Nostalgia ...

░▄░▀▄░░░▄▀░▄░
░█▄███████▄█░
░███▄███▄███░
░▀█████████▀░
░░▄▀░░░░░▀▄░░


The Coordinate System
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
BLACK = (0, 0, 0)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        # Read the Image and get the rectangular area out of the surface
        self.surf = pygame.transform.rotate(pygame.image.load("images/player.png"), 270)
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

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self).__init__()
        self.surf = pygame.image.load("images/enemy_ship.png")
        self.rect = self.surf.get_rect(
            center=(screen_width, random.randint(2, screen_height - 2))
        )
        self.speed = random.randint(1, 2)

    def update(self, **kwargs):
        # Keep moving right
        self.rect.move_ip(-self.speed, 0)
        # If it crosses the border disappear
        if self.rect.right < 0:
            self.kill()

# class Enemy(pygame.sprite.Sprite):
#     def __init__(self):
#         super(Enemy, self).__init__()
#         self.surf = pygame.image.load("images/enemy_ship.png")
#         self.rect = self.surf.get_rect(
#             center=(screen_width, random.randint(2, screen_height - 2))
#         )
#         self.speed = random.randint(1, 2)

#     def update(self, **kwargs):
#         # Keep moving right
#         self.rect.move_ip(-self.speed, 0)
#         # If it crosses the border disappear
#         if self.rect.right < 0:
#             self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self).__init__()
        self.surf = pygame.image.load("images/enemy_ship.png")
        self.rect = self.surf.get_rect(
            center=(screen_width, random.randint(2, screen_height - 2))
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


class SpaceImpact(object):
    def __init__(self):
        """Initialize."""
        pygame.init()
        pygame.display.set_caption("🛸 Space Impact 🛸")

    def _init_game(self):
        self.background = pygame.image.load("images/background.jpeg")

        self.player = Player()
        self.player_x, self.player_y = self.player.surf.get_size()

        self.NEWENEMY = pygame.USEREVENT + 1
        pygame.time.set_timer(self.NEWENEMY, 1000)

        self.enemy_group = pygame.sprite.Group()
        self.bullet_group = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)

        self.font = pygame.font.Font(None, 50)

        self.reload_time = 0.1  # Seconds it takes to reload after a shot
        self.next_shot_time = 0  # Can we fire yet ? current_time + reload_time

        self.enemy_explosion_images = []
        enemy_explosion_anim_path = "images/explosions/enemy/"
        _, _, img_paths = next(os.walk(enemy_explosion_anim_path))
        for img_path in sorted(img_paths):
            img = pygame.image.load(os.path.join(enemy_explosion_anim_path, img_path))
            img_ts = pygame.transform.scale(img, (100, 100))
            self.enemy_explosion_images.append(img_ts)

        self.initial_score = 0

        self.game_loop = True
        self.game_over = False

    def _game_over(self):
        self.player.kill()
        text = self.font.render("Game Over", True, WHITE)
        text_rect = text.get_rect(
            center=(
                screen.get_width() / 2,
                screen.get_height() / 2,
            )
        )
        screen.blit(text, text_rect)

    def _score(self, increment=0):
        self.initial_score += increment
        text = self.font.render(f"Score: {self.initial_score}", False, WHITE)
        text_rect = text.get_rect(center=(screen.get_width() - 100, 50))
        screen.blit(text, text_rect)

    def main(self):
        """Game loop."""
        self._init_game()

        while self.game_loop:
            current_time = int(time.time())

            for event in pygame.event.get():
                if event.type == loc.QUIT:
                    self.game_loop = False
                if event.type == self.NEWENEMY:
                    new_enemy = Enemy()
                    self.enemy_group.add(new_enemy)
                    self.all_sprites.add(new_enemy)

                # React to Keypresses
                if event.type == pygame.KEYDOWN:

                    # Shoot Bullets
                    if (
                        event.key == pygame.K_SPACE
                        and current_time > self.next_shot_time
                    ):
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
            else:

                if pygame.sprite.spritecollideany(self.player, self.enemy_group):
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
                    entity.update(pressed_keys=pressed_keys)
                    screen.blit(entity.surf, entity.rect)

            pygame.display.flip()


if __name__ == "__main__":
    game = SpaceImpact()
    game.main()
