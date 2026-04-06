import pygame
import sys
import random
import os

# --- KONSTANTA GAME ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

class GameObject(pygame.sprite.Sprite):
    def __init__(self, x, y, color, width, height, image_path=None):
        super().__init__()
        
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        
        # load gambar jika ada
        if image_path:
            try:
                loaded_image = pygame.image.load(image_path).convert_alpha()
                self.image = pygame.transform.scale(loaded_image, (width, height))
            except Exception as e:
                print(f"Warning: Gambar '{image_path}' tidak ditemukan. Menggunakan warna cadangan.")
                
        self.rect = self.image.get_rect(topleft=(x, y))

class Wall(GameObject):
    def __init__(self, x, y, width, height):
        # Tembok warna abu-abu
        super().__init__(x, y, (128, 128, 128), width, height, image_path=None)

class Player(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, (0, 255, 0), 40, 40, image_path="player.png")
        self.speed = 3
        self.inventory = []
        self.health = 3
        self.start_pos = (x, y)
        self.walls = None

    def respawn(self):
        self.rect.topleft = self.start_pos

    def update(self):
        keys = pygame.key.get_pressed()
        
        old_x = self.rect.x
        old_y = self.rect.y
        
        # Gerakan Horizontal
        if keys[pygame.K_LEFT] and self.rect.x > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.x < (SCREEN_WIDTH - self.rect.width):
            self.rect.x += self.speed
            
        # Cek Tabrakan Horizontal dengan Tembok
        if self.walls:
            if pygame.sprite.spritecollideany(self, self.walls):
                self.rect.x = old_x

        # Gerakan Vertikal
        if keys[pygame.K_UP] and self.rect.y > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.y < (SCREEN_HEIGHT - self.rect.height):
            self.rect.y += self.speed
            
        # Cek Tabrakan Vertikal dengan Tembok
        if self.walls:
            if pygame.sprite.spritecollideany(self, self.walls):
                self.rect.y = old_y

class Enemy(GameObject):
    def __init__(self, x, y, distance):
        super().__init__(x, y, (255, 0, 0), 40, 40, image_path="enemy.png")
        self.start_x = x
        self.distance = distance
        self.speed = random.randint(1, 2) 
        self.direction = 1
        self.walls = None

    def update(self):
        self.rect.x += self.speed * self.direction
        
        # Musuh memantul jika menabrak tembok
        if self.walls:
            if pygame.sprite.spritecollideany(self, self.walls):
                self.rect.x -= self.speed * self.direction # Mundur
                self.direction *= -1 # Balik arah
                self.start_x = self.rect.x # Reset jarak patroli
                return

        if abs(self.rect.x - self.start_x) > self.distance:
            self.direction *= -1

class Item(GameObject):
    def __init__(self, x, y, color):
        super().__init__(x, y, color, 20, 20, image_path="key.png")

class DungeonGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init() # Mengaktifkan sistem audio Pygame
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Dungeon Escape")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)
        
        #SYSTEM AUDIO
        self.sfx_key = self.load_sound("dapat_kunci.mp3")
        self.sfx_hit = self.load_sound("kena_musuh.mp3")
        self.sfx_win = self.load_sound("menang.mp3")

        try:
            # Memuat background musik dan loop selamanya
            pygame.mixer.music.load("musik_tema.mp3")
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1) 
        except Exception:
            print("Warning: File 'musik_tema.mp3' tidak ditemukan, game akan dimainkan tanpa musik BGM.")
        # ----------------------------------------------------

        self.all_sprites = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()

        # Konfigurasi Level
        self.current_level_index = 0
        # --- DAFTAR LEVEL (MAP) ---
         
        # 'W' = Wall (Tembok)
        # 'K' = Key (Kunci)
        # 'E' = Enemy (Musuh)
        # ' ' = Jalan Kosong
        self.levels = [
            [   # --- STAGE 1 ---
                "WWWWWWWWWWWWWWWW",
                "W   W       K  W",
                "W      WWWWWW  W",
                "W   W  W    E  W",
                "WW WW  W  WWWW W",
                "W   E  W   K   W",
                "W  WWWWWWW WW  W",
                "W     E        W",
                "W  W WWWWWWWW  W",
                "W  W   KWWWW   W",
                "W  W       W   W",
                "WWWWWWWWWWWWWWWW"
            ],
            [   # --- STAGE 2 ---
                "WWWWWWWWWWWWWWWW",
                "W  K           W",
                "W WWWWWW  WWWW W",
                "W W    W  W E  W",
                "W W WW W WW WW W",
                "W W W   K   W  W",
                "W W W WWWW  W  W",
                "W E W W     W  W",
                "WWWWW W WWW W  W",
                "W  K  W E W E  W",
                "W         W    W",
                "WWWWWWWWWWWWWWWW"
            ]
        ]

        # Inisialisasi Tembok 
        self.create_walls()

        # Inisialisasi Player
        self.player = Player(50, 50)
        self.player.walls = self.walls
        self.all_sprites.add(self.player)
        self.door = GameObject(650, 500, (139, 69, 19), 50, 50, image_path="pintu.png")
        self.all_sprites.add(self.door)

        # Buat item dan musuh secara dinamis
        self.spawn_entities()

        self.is_running = True
        self.game_over = False
        self.state = "MENU" # Memulai di Menu Utama

    def load_sound(self, file_path):
        # Pengaman jika file suara tidak ada, game tidak akan rusak
        try:
            return pygame.mixer.Sound(file_path)
        except Exception:
            return None

    def play_sound(self, sound_obj):
        if sound_obj:
            sound_obj.play()

    def draw_menu(self):
        self.screen.fill((20, 20, 40))
        
        # Judul Game
        title_font = pygame.font.SysFont("Arial", 64, bold=True)
        title_text = title_font.render("DUNGEON ESCAPE", True, (255, 215, 0))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(title_text, title_rect)
        
        # Instruksi
        instr_text = self.font.render("Tekan SPACE untuk Memulai", True, (255, 255, 255))
        instr_rect = instr_text.get_rect(center=(SCREEN_WIDTH // 2, 400))
        self.screen.blit(instr_text, instr_rect)
        
        # Kredit Kecil
        credit_text = pygame.font.SysFont("Arial", 16).render("Dibuat dengan Python & Pygame", True, (150, 150, 150))
        self.screen.blit(credit_text, (SCREEN_WIDTH - 200, SCREEN_HEIGHT - 30))

    def create_walls(self):
        for wall in self.walls:
            wall.kill()
        TILE_SIZE = 50
        
        peta = self.levels[self.current_level_index]
        # peta teks menjadi tembok
        for row_index, baris in enumerate(peta):
            for col_index, cell in enumerate(baris):
                # Cetak Tembok jika huruf adalah W
                if cell == "W":
                    x = col_index * TILE_SIZE
                    y = row_index * TILE_SIZE
                    w = Wall(x, y, TILE_SIZE, TILE_SIZE)
                    self.all_sprites.add(w)
                    self.walls.add(w)

    def get_valid_pos(self, width, height):
        # Mencari posisi random agar objek tidak spawn ke dalam tembok
        while True:
            rx = random.randint(100, SCREEN_WIDTH - width - 100)
            ry = random.randint(100, SCREEN_HEIGHT - height - 100)
            temp_rect = pygame.Rect(rx, ry, width, height)
            
            overlap = False
            for w in self.walls:
                if temp_rect.colliderect(w.rect):
                    overlap = True
                    break
            
            if not overlap:
                return rx, ry

    def spawn_entities(self):
        # Bersihkan Item & Musuh
        for s in list(self.items) + list(self.enemies): s.kill()
        
        TILE_SIZE = 50
        peta = self.levels[self.current_level_index]
        
        for row_index, baris in enumerate(peta):
            for col_index, cell in enumerate(baris):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE
                
                # Jika ketemu K (Kunci)
                if cell == "K":
                    key = Item(x + 15, y + 15, (255, 255, 0)) # Sedikit offset agar di tengah tile
                    self.all_sprites.add(key)
                    self.items.add(key)
                
                # Jika ketemu E (Musuh)
                elif cell == "E":
                    dist = random.randint(100, 200) # Tetap pakai random patrol distance
                    e = Enemy(x + 5, y + 5, dist)
                    e.walls = self.walls
                    self.all_sprites.add(e)
                    self.enemies.add(e)

    def run(self):
        while self.is_running:
            self.handle_events()
            if self.state == "PLAYING" and not self.game_over:
                self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()

    def reset_game(self):
        self.game_over = False
        self.current_level_index = 0 # Kembali ke Stage 1 saat restart
        self.player.health = 3
        self.player.inventory = []
        self.create_walls() # restart tembok level 1
        self.player.respawn()
        self.spawn_entities()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

            if event.type == pygame.KEYDOWN:
                # Transisi dari Menu ke Game
                if self.state == "MENU":
                    if event.key == pygame.K_SPACE:
                        self.state = "PLAYING"
                
                # Lanjut ke Level Berikutnya
                if self.state == "STAGE_COMPLETE":
                    if event.key == pygame.K_RETURN:
                        self.next_level()
                        self.state = "PLAYING"

                # Restart Game
                if event.key == pygame.K_r and self.game_over:
                    self.reset_game()

    def update(self):
        self.all_sprites.update()

        # 1. Cek Tabrakan Kunci
        collected = pygame.sprite.spritecollide(self.player, self.items, True)
        if collected:
            self.play_sound(self.sfx_key)
            for _ in collected:
                self.player.inventory.append("Key")

        # 2. Cek Tabrakan Musuh
        if pygame.sprite.spritecollide(self.player, self.enemies, False):

            # Flash Merah
            self.screen.fill((255, 0, 0))
            pygame.display.flip()
            pygame.time.delay(50)

            self.play_sound(self.sfx_hit)
            self.player.health -= 1
            print(f"Terkena Musuh! Sisa nyawa : {self.player.health}")

            if self.player.health > 0:
                self.player.respawn()
            else:
                print(" GAME OVER ")
                self.game_over = True
            return

        # 3. Cek Pintu (Menang / Lanjut Level)
        if self.player.rect.colliderect(self.door.rect) and len(self.player.inventory) >= 3:
            self.play_sound(self.sfx_win) # Sound menang langsung saat kena pintu
            if self.current_level_index < len(self.levels) - 1:
                self.state = "STAGE_COMPLETE"
            else:
                self.game_over = True

    def next_level(self):
        if self.current_level_index < len(self.levels) - 1:
            self.current_level_index += 1
            print(f"Lanjut ke Level {self.current_level_index + 1}")
            self.player.inventory = []
            self.player.health = 3 # Reset Nyawa saat pindah stage
            self.create_walls()
            self.player.respawn()
            self.spawn_entities()
        else:
            print("Berhasil Kabur! Kamu Menang Telak.")
            self.game_over = True

    def draw(self):
        if self.state == "MENU":
            self.screen.fill((20, 20, 40))
            title = pygame.font.SysFont("Arial", 50, bold=True).render("DUNGEON ESCAPE PRO", True, (255, 215, 0))
            self.screen.blit(title, (180, 200))
            hint = self.font.render("Press SPACE to Start", True, (255, 255, 255))
            self.screen.blit(hint, (300, 350))
        
        elif self.state == "STAGE_COMPLETE":
            # Overlay transisi stage
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180); overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            msg = f"STAGE {self.current_level_index + 1} COMPLETE!"
            txt = self.font.render(msg, True, (100, 255, 100))
            self.screen.blit(txt, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 - 50))
            
            hint = self.font.render("Press ENTER for Stage 2", True, (255, 255, 255))
            if self.current_level_index == 1: # Jika ada level lebih banyak, sesuaikan teks ini
                hint = self.font.render("Press ENTER to Continue", True, (255, 255, 255))
            self.screen.blit(hint, (SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 + 20))

        else:
            self.screen.fill((30, 30, 30))
            self.all_sprites.draw(self.screen)
            
            # UI Overlay
            ui_bg = pygame.Surface((800, 40)); ui_bg.set_alpha(150); self.screen.blit(ui_bg, (0,0))
            stats = f"STAGE: {self.current_level_index + 1} | KEYS: {len(self.player.inventory)}/3 | HP: {self.player.health}"
            self.screen.blit(self.font.render(stats, True, (255, 255, 255)), (20, 10))

            if self.game_over:
                txt = "WINNER! ESCAPED!" if self.player.health > 0 else "DEFEATED! GAME OVER"
                col = (100, 255, 100) if self.player.health > 0 else (255, 50, 50)
                self.screen.blit(self.font.render(txt, True, col), (300, 280))
                self.screen.blit(self.font.render("Press 'R' to Restart", True, (255, 255, 255)), (320, 320))

        pygame.display.flip()

if __name__ == "__main__":
    game = DungeonGame()
    game.run()
