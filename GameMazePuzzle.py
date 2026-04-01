import pygame
import sys
import random

class GameObject(pygame.sprite.Sprite):
    def __init__(self, x, y, color, width, height, image_path=None,):
        super().__init__()
        if image_path:
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (width, height))
        else:
            self.image = pygame.Surface([width,height])
            self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

class Player(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, (0, 255, 0), 40, 40, image_path="player.png")
        self.speed = 5
        self.inventory = []
        self.health = 3
        self.start_pos = (x,y)

    def respawn(self):
        self.rect.topleft = self.start_pos

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.x > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.x < 760:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.y > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.y < 560:
            self.rect.y += self.speed

class Enemy(GameObject):
    def __init__(self, x, y, distance):
        super().__init__(x, y, (255, 0, 0), 40, 40)
        self.start_x = x
        self.distance = distance
        self.speed = random.randint(3, 7)
        self.direction = 1

    def update(self):
        self.rect.x += self.speed * self.direction
        if abs(self.rect.x - self.start_x) > self.distance:
            self.direction *= -1

class Item(GameObject):
    def __init__(self, x, y, color):
        super().__init__(x, y, color, 20, 20, image_path="key.png")

class DungeonGame:
    def __init__(self):
        pygame.init()
        self. screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Dungeon Escape")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)

        self.all_sprites = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

        self.player = Player(50,50)
        self.all_sprites.add(self.player)

        for loc in [(200,150), (600, 100), (400, 500)]:
            key = Item(loc[0], loc[1], (255, 255, 0))
            self.all_sprites.add(key)
            self.items.add(key)

        for i in range(8):
            rx = random.randint(100, 600) # Posisi X acak
            ry = random.randint(100, 500) # Posisi Y acak
            dist = random.randint(100, 250) # Jarak patroli acak
            
            e = Enemy(rx, ry, dist)
            self.all_sprites.add(e)
            self.enemies.add(e)

        self.door = GameObject(730, 530, (139, 69, 19), 50, 60, image_path="pintu.png")
        self.all_sprites.add(self.door)

        self.is_running = True
        self.game_over = False

    def run(self):
        while self.is_running:
            self.handle_events()
            if not self.game_over:
                self.update()
            self.draw()
            self.clock.tick(60)
        pygame.quit()

    def reset_game(self):
        self.game_over = False

        self.player.health = 3
        self.player.inventory = []
        self.player.respawn()

        self.all_sprites.empty()
        self.player.inventory = []
        self.player.respawn()

        self.all_sprites.empty()
        self.items.empty()
        self.enemies.empty()

        self.all_sprites.add(self.door)

        self.all_sprites.add(self.player)
        for loc in [(200,150), (600,100), (400, 500)]:
            Key = Item(loc[0], loc[1], (255, 255, 0))
            self.all_sprites.add(Key)
            self.items.add(Key)

        for i in range(8):
            rx = random.randint(100, 600) # Posisi X acak
            ry = random.randint(100, 500) # Posisi Y acak
            dist = random.randint(100, 250) # Jarak patroli acak
            
            e = Enemy(rx, ry, dist)
            self.all_sprites.add(e)
            self.enemies.add(e)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over:
                    self.reset_game()

    def update(self):
        self.all_sprites.update()

        # Cek Tabrakan Kunci
        collected = pygame.sprite.spritecollide(self.player, self.items, True)
        for _ in collected:
            self.player.inventory.append("Key")

        # Cek Tabrakan Musuh
        if pygame.sprite.spritecollide(self.player, self.enemies, False):
            print("Kena Musuh! Game Over.")
            self.player.health -= 1
            print(f"Terkena Musuh! Sisa nyawa : {self.player.health}")

            if self.player.health > 0:
                self.player.respawn()
            else:
                print(" GAME OVER ")
                self.game_over = True

        # Cek Pintu (Menang)
        if self.player.rect.colliderect(self.door.rect):
            if len(self.player.inventory) >= 3:
                print("Berhasil Kabur! Kamu Menang.")
                self.game_over = True

    def draw(self):
        self.screen.fill((30, 30, 30)) # Latar belakang gelap
        self.all_sprites.draw(self.screen)
        
        # Teks Info
        status_text = f"Kunci : {len(self.player.inventory)}/ 3 | Health : {self.player.health} "
        info = self.font.render(status_text, True, (255, 255, 255))
        self.screen.blit(info, (10, 10))

        if self.game_over:
            if self.player.health <= 0:
                msg = "GAME OVER - NYAWA HABIS"
            else:
                msg = "MISSION COMPLETE - BERHASIL KABUR"
            result_text = self.font.render(msg, True, (255, 255, 255))
            self.screen.blit(result_text, (250, 280))

            restart_info = self.font.render("Rekan 'R' untuk Restart", True, (200,200,200))
            self.screen.blit(restart_info, (280, 330))

        pygame.display.flip()

if __name__ == "__main__":
    game = DungeonGame()
    game.run()

