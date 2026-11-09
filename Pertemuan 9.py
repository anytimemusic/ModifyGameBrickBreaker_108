# ==============================================================================
# Tugas Pemrograman GUI - Implementasi OOP pada Game Brick Breaker
# Nama Repository : ModifyGameBrickBreaker_108
# NIM             : ...108
# ==============================================================================

import pygame
import random
import math
import sys
import os

# Inisialisasi Pygame & Font
pygame.init()
pygame.font.init()

# ==============================================================================
# KONFIGURASI LAYAR & WARNA
# ==============================================================================
WIDTH, HEIGHT = 640, 560
FPS = 60

# Palette Warna Retro/Arcade Modern
BG_COLOR       = (15, 17, 26)
BG_GRID        = (24, 27, 40)
WHITE          = (255, 255, 255)
GRAY           = (140, 145, 160)
DARK_GRAY      = (45, 50, 65)

COLOR_RED      = (255, 75, 92)      # Armored / Bomb / Heart
COLOR_ORANGE   = (255, 155, 60)     # Fireball / Powerup
COLOR_YELLOW   = (255, 214, 75)     # Level / Gold
COLOR_GREEN    = (75, 235, 120)     # Normal / Wide Paddle
COLOR_CYAN     = (60, 215, 255)     # Slow-Mo / Shield
COLOR_PURPLE   = (195, 90, 255)     # Alien / Multi-Ball
COLOR_BOMB     = (255, 45, 85)      # Ledakan Bom

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Super Brick Breaker - OOP GUI Implementation [NIM 108]")
clock = pygame.time.Clock()


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def collisionChecker(rectA, rectB):
    """Fungsi helper OOP untuk mendeteksi collision antara dua objek ber-Rect."""
    return pygame.Rect.colliderect(rectA, rectB)


# ==============================================================================
# CLASS SOUND MANAGER (Audio & BGM)
# ==============================================================================
class SoundManager:
    """Class untuk mengelola seluruh audio, SFX, dan musik latar (BGM)."""
    def __init__(self):
        self.enabled = False
        self.muted = False
        self.sounds = {}
        self.bgm = None
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.mixer.set_num_channels(16)
            self.enabled = True

            base_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
            s_dir = os.path.join(base_dir, 'sounds')
            if not os.path.exists(s_dir):
                s_dir = os.path.join(os.getcwd(), 'sounds')

            mapping = {
                'paddle': 'paddle.wav', 'block': 'block_hit.wav', 'break': 'block_break.wav',
                'bomb': 'bomb.wav', 'powerup': 'powerup.wav', 'laser': 'laser.wav',
                'alien_hit': 'alien_hit.wav', 'alien_die': 'alien_die.wav',
                'lose': 'lose_life.wav', 'win': 'win.wav', 'bgm': 'bgm.wav'
            }
            for k, f in mapping.items():
                p = os.path.join(s_dir, f)
                if os.path.exists(p):
                    self.sounds[k] = pygame.mixer.Sound(p)

            if 'bgm' in self.sounds:
                self.bgm = self.sounds['bgm']
                self.bgm.set_volume(0.25)
                self.bgm.play(loops=-1)
        except Exception:
            self.enabled = False

    def play(self, key):
        if self.enabled and not self.muted and key in self.sounds:
            try:
                self.sounds[key].play()
            except Exception:
                pass

    def toggleMute(self):
        self.muted = not self.muted
        if self.bgm:
            self.bgm.set_volume(0.0 if self.muted else 0.25)
        return self.muted


# ==============================================================================
# CLASS VISUAL EFFECTS (Partikel & Teks Mengambang)
# ==============================================================================
class Particle:
    """Class efek partikel serpihan pecahan balok dan ledakan."""
    def __init__(self, x, y, color):
        self.x = float(x)
        self.y = float(y)
        ang = random.uniform(0, 2 * math.pi)
        spd = random.uniform(1.5, 4.5)
        self.vx = math.cos(ang) * spd
        self.vy = math.sin(ang) * spd
        self.color = color
        self.size = random.uniform(2.5, 4.5)
        self.life = random.randint(18, 30)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.08  # gravitasi
        self.life -= 1
        self.size = max(0.5, self.size * 0.94)
        return self.life > 0

    def display(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), int(self.size))


class FloatingText:
    """Class teks skor dan notifikasi power-up yang melayang ke atas."""
    def __init__(self, x, y, text, color, font):
        self.x = float(x)
        self.y = float(y)
        self.text = text
        self.color = color
        self.font = font
        self.life = 40
        self.maxLife = 40

    def update(self):
        self.y -= 0.8
        self.life -= 1
        return self.life > 0

    def display(self, surf):
        alpha = int(255 * (self.life / self.maxLife))
        s = self.font.render(self.text, True, self.color)
        s.set_alpha(alpha)
        surf.blit(s, (int(self.x - s.get_width() // 2), int(self.y)))


# ==============================================================================
# CLASS ALIEN ENEMY & LASER (Musuh Segitiga Terbalik ▼)
# ==============================================================================
class AlienLaser:
    """Class proyektil laser yang ditembakkan oleh musuh Alien ke arah pemain."""
    def __init__(self, posx, posy):
        self.posx = float(posx)
        self.posy = float(posy)
        self.speed = 3.8
        self.laserRect = pygame.Rect(int(self.posx - 2), int(self.posy), 4, 12)

    def update(self):
        self.posy += self.speed
        self.laserRect = pygame.Rect(int(self.posx - 2), int(self.posy), 4, 12)
        return self.posy < HEIGHT + 20

    def display(self, surf):
        pygame.draw.rect(surf, (255, 60, 90), self.laserRect, border_radius=2)
        pygame.draw.rect(surf, (255, 230, 240), (self.laserRect.x + 1, self.laserRect.y + 1, 2, self.laserRect.height - 2))

    def getRect(self):
        return self.laserRect


class Alien:
    """Class Musuh Alien Pesawat berbentuk segitiga menghadap ke bawah ▼."""
    def __init__(self, posx=WIDTH//2, posy=48, hp=3):
        self.posx = float(posx)
        self.posy = float(posy)
        self.baseY = float(posy)
        self.width = 38
        self.height = 24
        self.speed = 2.2
        self.health = hp
        self.maxHealth = hp
        self.flashTimer = 0
        self.shootCooldown = random.randint(80, 140)
        self.bobAngle = 0.0
        self.alive = True
        self.respawnTimer = 0

    def getRect(self):
        return pygame.Rect(int(self.posx - self.width // 2), int(self.posy), self.width, self.height)

    def update(self, listOfLasers, sfx):
        if not self.alive:
            self.respawnTimer -= 1
            if self.respawnTimer <= 0:
                self.alive = True
                self.health = self.maxHealth
                self.posx = random.randint(100, WIDTH - 100)
                self.shootCooldown = 90
            return

        # Animasi melayang (bobbing) & patroli horizontal
        self.bobAngle += 0.05
        self.posy = self.baseY + math.sin(self.bobAngle) * 4.0
        self.posx += self.speed

        if self.posx - self.width // 2 <= 20 or self.posx + self.width // 2 >= WIDTH - 20:
            self.speed *= -1

        if self.flashTimer > 0:
            self.flashTimer -= 1

        # Menembakkan laser ke arah paddle
        self.shootCooldown -= 1
        if self.shootCooldown <= 0:
            self.shootCooldown = random.randint(90, 160)
            listOfLasers.append(AlienLaser(self.posx, self.posy + self.height))
            sfx.play('laser')

    def hit(self, damage=1):
        self.health -= damage
        self.flashTimer = 6
        if self.health <= 0:
            self.alive = False
            self.respawnTimer = 60 * 15  # Respawn dalam 15 detik
            return True
        return False

    def display(self, surf):
        if not self.alive:
            return

        # Koordinat segitiga menghadap ke bawah ▼
        p_bottom    = (int(self.posx), int(self.posy + self.height))
        p_top_left  = (int(self.posx - self.width // 2), int(self.posy))
        p_top_right = (int(self.posx + self.width // 2), int(self.posy))

        body_color   = WHITE if self.flashTimer > 0 else (175, 40, 240)
        border_color = WHITE if self.flashTimer > 0 else (255, 120, 255)

        # Gambar badan pesawat segitiga terbalik
        pygame.draw.polygon(surf, body_color, [p_top_left, p_top_right, p_bottom])
        pygame.draw.polygon(surf, border_color, [p_top_left, p_top_right, p_bottom], 2)

        # Cockpit mata alien di tengah
        eye_y = int(self.posy + 7)
        pygame.draw.circle(surf, (255, 45, 85), (int(self.posx), eye_y), 4)
        pygame.draw.circle(surf, (255, 230, 230), (int(self.posx - 1), eye_y - 1), 1)

        # Moncong laser
        pygame.draw.line(surf, (60, 215, 255), (p_top_left[0] - 4, p_top_left[1] + 3), p_top_left, 2)
        pygame.draw.line(surf, (60, 215, 255), (p_top_right[0] + 4, p_top_right[1] + 3), p_top_right, 2)

        # Health bar alien
        bar_w = 30
        bar_x = int(self.posx - bar_w // 2)
        bar_y = int(self.posy - 7)
        pygame.draw.rect(surf, (40, 45, 60), (bar_x, bar_y, bar_w, 3))
        fill_w = int(bar_w * max(0, self.health / self.maxHealth))
        pygame.draw.rect(surf, (255, 75, 92), (bar_x, bar_y, fill_w, 3))


# ==============================================================================
# CLASS POWER-UP (Kapsul Item Jatuh)
# ==============================================================================
class PowerUp:
    """Class untuk item power-up yang jatuh saat balok hancur."""
    TYPES = {
        'WIDE':  ((75, 235, 120), 'W', 'EXPAND PADDLE!'),
        'MULTI': ((195, 90, 255), 'M', 'MULTI-BALL!'),
        'LIFE':  ((255, 75, 92),  '+', '+1 EXTRA LIFE!'),
        'SLOW':  ((60, 215, 255), 'S', 'SLOW MOTION!'),
        'FIRE':  ((255, 140, 50), 'F', 'FIREBALL PIERCE!')
    }

    def __init__(self, posx, posy, p_type=None):
        self.posx = float(posx)
        self.posy = float(posy)
        self.width = 24
        self.height = 14
        self.type = p_type or random.choices(
            ['WIDE', 'MULTI', 'LIFE', 'SLOW', 'FIRE'],
            weights=[30, 25, 15, 20, 10]
        )[0]
        self.color, self.label, self.name = self.TYPES[self.type]
        self.speed = 2.4
        self.rect = pygame.Rect(int(self.posx - self.width // 2), int(self.posy - self.height // 2), self.width, self.height)

    def update(self):
        self.posy += self.speed
        self.rect = pygame.Rect(int(self.posx - self.width // 2), int(self.posy - self.height // 2), self.width, self.height)
        return self.posy < HEIGHT + 20

    def display(self, surf, font):
        pygame.draw.rect(surf, self.color, self.rect, border_radius=6)
        pygame.draw.rect(surf, WHITE, self.rect, width=1, border_radius=6)
        txt = font.render(self.label, True, (15, 17, 26))
        surf.blit(txt, (self.rect.centerx - txt.get_width() // 2, self.rect.centery - txt.get_height() // 2))

    def getRect(self):
        return self.rect


# ==============================================================================
# CLASS BLOCK (BRICK)
# ==============================================================================
class Block:
    """Class Balok Penghalang (Normal, Lapis Baja, Bom, Emas)."""
    def __init__(self, posx, posy, width, height, color, block_type='normal'):
        self.posx = posx
        self.posy = posy
        self.width = width
        self.height = height
        self.color = color
        self.block_type = block_type
        self.maxHealth = 2 if block_type == 'armored' else 1
        self.health = self.maxHealth
        self.points = 150 if block_type == 'gold' else (50 if block_type == 'armored' else 25)
        self.blockRect = pygame.Rect(self.posx, self.posy, self.width, self.height)

    def hit(self):
        self.health -= 1
        return self.health <= 0

    def display(self, surf, font):
        col = (min(255, self.color[0] + 70), min(255, self.color[1] + 70), min(255, self.color[2] + 70)) if (self.block_type == 'armored' and self.health == 1) else self.color
        pygame.draw.rect(surf, col, self.blockRect, border_radius=3)
        pygame.draw.line(surf, WHITE, (self.blockRect.left + 2, self.blockRect.top + 1), (self.blockRect.right - 2, self.blockRect.top + 1), 1)

        cx, cy = self.blockRect.centerx, self.blockRect.centery
        if self.block_type == 'bomb':
            pygame.draw.circle(surf, (20, 20, 25), (cx, cy + 1), 5)
            pygame.draw.circle(surf, (255, 220, 0), (cx + 3, cy - 3), 2)
        elif self.block_type == 'armored':
            pygame.draw.rect(surf, WHITE, (cx - 5, cy - 1, 10, 2))
            pygame.draw.rect(surf, WHITE, (cx - 1, cy - 5, 2, 10))
        elif self.block_type == 'gold':
            t = font.render("$", True, (40, 30, 0))
            surf.blit(t, (cx - t.get_width() // 2, cy - t.get_height() // 2))

    def getRect(self):
        return self.blockRect

    def getHealth(self):
        return self.health


# ==============================================================================
# CLASS STRIKER (PADDLE)
# ==============================================================================
class Striker:
    """Class Paddle yang dikendalikan oleh pemain."""
    def __init__(self, posx, posy, width=96, height=14, speed=8.5, color=WHITE):
        self.posx = float(posx)
        self.posy = float(posy)
        self.baseWidth = width
        self.width = float(width)
        self.targetWidth = float(width)
        self.height = height
        self.speed = speed
        self.color = color

        # Power-Up Timers
        self.wideTimer = 0
        self.fireTimer = 0
        self.invulnerableTimer = 0

    def getRect(self):
        return pygame.Rect(int(self.posx), int(self.posy), int(self.width), self.height)

    def update(self, xFac):
        self.posx += xFac * self.speed
        if self.posx < 10:
            self.posx = 10
        elif self.posx + self.width > WIDTH - 10:
            self.posx = WIDTH - 10 - self.width

        # Update durasi powerup
        if self.wideTimer > 0:
            self.wideTimer -= 1
            self.targetWidth = self.baseWidth * 1.5
        else:
            self.targetWidth = self.baseWidth

        if self.fireTimer > 0:
            self.fireTimer -= 1

        if self.invulnerableTimer > 0:
            self.invulnerableTimer -= 1

        # Smooth resize paddle
        self.width += (self.targetWidth - self.width) * 0.15

    def display(self, surf):
        # Efek kedip saat kebal setelah terkena tembakan
        if self.invulnerableTimer > 0 and (self.invulnerableTimer // 4) % 2 == 0:
            return

        r = self.getRect()
        if self.fireTimer > 0:
            col = (255, 140, 50)
        elif self.wideTimer > 0:
            col = (75, 235, 120)
        else:
            col = self.color

        pygame.draw.rect(surf, col, r, border_radius=6)
        pygame.draw.rect(surf, WHITE, (r.x + 4, r.y + 2, r.width - 8, 3), border_radius=2)

        if self.invulnerableTimer > 0:
            pygame.draw.arc(surf, (60, 215, 255), (r.x - 4, r.y - 6, r.width + 8, 16), 0, math.pi, 2)

        if self.wideTimer > 0:
            pygame.draw.rect(surf, (75, 235, 120), (r.x, r.bottom + 2, int(r.width * (self.wideTimer / 600)), 2))
        elif self.fireTimer > 0:
            pygame.draw.rect(surf, (255, 140, 50), (r.x, r.bottom + 2, int(r.width * (self.fireTimer / 360)), 2))


# ==============================================================================
# CLASS BALL
# ==============================================================================
class Ball:
    """Class Bola dengan fisika pantulan dinamis dan ekor komet."""
    def __init__(self, posx, posy, radius=6, speed=6.0, color=WHITE):
        self.posx = float(posx)
        self.posy = float(posy)
        self.radius = radius
        self.baseSpeed = speed
        self.speed = speed
        self.color = color
        self.xFac = 0.0
        self.yFac = 0.0
        self.stuck = True
        self.stuckOffset = 0.0
        self.trail = []
        self.isFireball = False

    def launch(self):
        self.stuck = False
        angle = random.uniform(-math.pi / 4, math.pi / 4)
        self.xFac = self.speed * math.sin(angle)
        self.yFac = -self.speed * math.cos(angle)

    def getRect(self):
        return pygame.Rect(int(self.posx - self.radius), int(self.posy - self.radius), self.radius * 2, self.radius * 2)

    def update(self, striker, slowMotion=False):
        currentSpeed = self.baseSpeed * 0.65 if slowMotion else self.baseSpeed

        if self.stuck:
            self.posx = striker.posx + striker.width / 2 + self.stuckOffset
            self.posy = striker.posy - self.radius - 2
            self.trail.clear()
            return 'ok'

        self.trail.append((self.posx, self.posy))
        if len(self.trail) > 7:
            self.trail.pop(0)

        mag = math.hypot(self.xFac, self.yFac)
        if mag > 0:
            self.xFac = (self.xFac / mag) * currentSpeed
            self.yFac = (self.yFac / mag) * currentSpeed

        self.posx += self.xFac
        self.posy += self.yFac

        # Pantulan dinding kiri / kanan
        if self.posx - self.radius <= 10:
            self.posx = 10 + self.radius
            self.xFac = abs(self.xFac)
        elif self.posx + self.radius >= WIDTH - 10:
            self.posx = WIDTH - 10 - self.radius
            self.xFac = -abs(self.xFac)

        # Pantulan dinding atas
        if self.posy - self.radius <= 35:
            self.posy = 35 + self.radius
            self.yFac = abs(self.yFac)

        return 'dead' if self.posy - self.radius > HEIGHT else 'ok'

    def bounceStriker(self, striker):
        # Arah pantulan dihitung dinamis berdasarkan titik benturan di paddle
        rel = max(-0.95, min(0.95, (self.posx - (striker.posx + striker.width / 2)) / (striker.width / 2)))
        angle = rel * math.radians(65)
        speed = math.hypot(self.xFac, self.yFac)
        self.xFac = speed * math.sin(angle)
        self.yFac = -abs(speed * math.cos(angle))
        self.posy = striker.posy - self.radius - 1

    def hit(self):
        self.yFac *= -1

    def display(self, surf):
        trailCol = (255, 120, 50) if self.isFireball else (100, 200, 255)
        for i, (tx, ty) in enumerate(self.trail):
            r = max(1, int(self.radius * ((i + 1) / (len(self.trail) + 1)) * 0.8))
            pygame.draw.circle(surf, trailCol, (int(tx), int(ty)), r)

        bCol = (255, 180, 70) if self.isFireball else self.color
        pygame.draw.circle(surf, bCol, (int(self.posx), int(self.posy)), self.radius)
        pygame.draw.circle(surf, WHITE, (int(self.posx - 2), int(self.posy - 2)), max(1, self.radius // 3))


# ==============================================================================
# PROCEDURAL LEVEL GENERATOR
# ==============================================================================
def populateBlocks(level=1):
    """Menghasilkan penempatan balok secara acak dan simetris di setiap level."""
    blocks = []
    bw, bh = 56, 18
    gx, gy = 6, 6
    cols, rows = 10, 6
    colors = [COLOR_RED, COLOR_ORANGE, COLOR_YELLOW, COLOR_GREEN, COLOR_CYAN, COLOR_PURPLE]
    spawnProb = min(0.90, 0.70 + (level * 0.05))
    grid = [[None for _ in range(cols)] for _ in range(rows)]

    for r in range(rows):
        for c in range(cols // 2):
            if random.random() < spawnProb:
                roll = random.random()
                b_type = 'armored' if roll < 0.12 + (level * 0.02) else ('bomb' if roll < 0.22 else ('gold' if roll < 0.28 else 'normal'))
                item = (b_type, colors[r % len(colors)])
                grid[r][c] = grid[r][cols - 1 - c] = item

    for r in range(rows):
        for c in range(cols):
            if grid[r][c]:
                bt, col = grid[r][c]
                blocks.append(Block(22 + c * (bw + gx), 75 + r * (bh + gy), bw, bh, col, bt))

    return populateBlocks(level) if len(blocks) < 20 else blocks


# ==============================================================================
# MAIN GAME MANAGER
# ==============================================================================
def main():
    f_hud, f_bold   = pygame.font.Font('freesansbold.ttf', 16), pygame.font.Font('freesansbold.ttf', 20)
    f_title, f_small = pygame.font.Font('freesansbold.ttf', 38), pygame.font.Font('freesansbold.ttf', 12)

    sfx = SoundManager()
    score = 0
    highScore = 0
    lives = 3
    level = 1
    combo = 0
    slowTimer = 0

    striker = Striker(WIDTH // 2 - 48, HEIGHT - 45)
    balls = [Ball(striker.posx + striker.width // 2, striker.posy - 10)]
    blocks = populateBlocks(level)
    alien = Alien(WIDTH // 2, 48, 3 + level)
    listOfLasers, particles, texts, powerups = [], [], [], []

    strikerXFac = 0
    state = 'PLAYING'
    running = True

    while running:
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_m:
                    sfx.toggleMute()
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    strikerXFac = -1
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    strikerXFac = 1
                elif event.key == pygame.K_SPACE:
                    if state == 'PLAYING':
                        for b in balls:
                            if b.stuck:
                                b.launch()
                                sfx.play('paddle')
                    else:
                        if state == 'GAME_OVER':
                            score, lives, level = 0, 3, 1
                        else:
                            level += 1
                        striker = Striker(WIDTH // 2 - 48, HEIGHT - 45)
                        balls = [Ball(striker.posx + striker.width // 2, striker.posy - 10)]
                        blocks = populateBlocks(level)
                        alien = Alien(WIDTH // 2, 48, 3 + level)
                        listOfLasers.clear(); particles.clear(); texts.clear(); powerups.clear()
                        combo = slowTimer = 0
                        state = 'PLAYING'

            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d):
                    strikerXFac = 0

        # Game Logic Updates
        if state == 'PLAYING':
            striker.update(strikerXFac)
            if slowTimer > 0:
                slowTimer -= 1

            # Update Alien & Laser
            alien.update(listOfLasers, sfx)
            for laser in listOfLasers[:]:
                if not laser.update():
                    listOfLasers.remove(laser)
                    continue
                if collisionChecker(striker.getRect(), laser.getRect()):
                    listOfLasers.remove(laser)
                    if striker.invulnerableTimer > 0:
                        for _ in range(5):
                            particles.append(Particle(laser.laserRect.centerx, laser.laserRect.centery, COLOR_CYAN))
                    else:
                        sfx.play('lose')
                        striker.invulnerableTimer = 90
                        if striker.wideTimer > 0:
                            striker.wideTimer = 0
                            texts.append(FloatingText(striker.posx + striker.width//2, striker.posy - 15, "SHIELD BROKEN!", COLOR_CYAN, f_bold))
                        else:
                            lives -= 1
                            texts.append(FloatingText(striker.posx + striker.width//2, striker.posy - 15, "-1 LIFE!", COLOR_RED, f_bold))
                            if lives <= 0:
                                state = 'GAME_OVER'
                                if score > highScore: highScore = score

            # Update Power-Ups
            for p in powerups[:]:
                if not p.update():
                    powerups.remove(p)
                    continue
                if collisionChecker(striker.getRect(), p.getRect()):
                    sfx.play('powerup')
                    score += 50
                    texts.append(FloatingText(striker.posx + striker.width//2, striker.posy - 15, p.name, p.color, f_bold))
                    if p.type == 'WIDE': striker.wideTimer = 600
                    elif p.type == 'MULTI':
                        new_b = []
                        for b in balls:
                            if not b.stuck:
                                for off in (-0.4, 0.4):
                                    nb = Ball(b.posx, b.posy, b.speed); nb.stuck = False
                                    spd = math.hypot(b.xFac, b.yFac); a = math.atan2(b.xFac, -b.yFac)
                                    nb.xFac, nb.yFac = spd * math.sin(a + off), -spd * math.cos(a + off)
                                    new_b.append(nb)
                        balls.extend(new_b)
                    elif p.type == 'LIFE': lives = min(5, lives + 1)
                    elif p.type == 'SLOW': slowTimer = 480
                    elif p.type == 'FIRE': striker.fireTimer = 360
                    powerups.remove(p)

            # Update Balls & Collisions
            for b in balls[:]:
                b.isFireball = (striker.fireTimer > 0)
                if b.update(striker, slowTimer > 0) == 'dead':
                    balls.remove(b)
                    continue
                if b.stuck:
                    continue

                # Collision Ball & Striker
                if b.yFac > 0 and collisionChecker(striker.getRect(), b.getRect()):
                    b.bounceStriker(striker)
                    sfx.play('paddle')
                    combo = 0

                # Collision Ball & Alien
                if alien.alive and collisionChecker(alien.getRect(), b.getRect()):
                    if not b.isFireball:
                        b.yFac *= -1
                    if alien.hit(2 if b.isFireball else 1):
                        sfx.play('bomb')
                        score += 300
                        texts.append(FloatingText(alien.posx, alien.posy - 10, "ALIEN DOWN! +300", COLOR_PURPLE, f_bold))
                        for _ in range(25):
                            particles.append(Particle(alien.posx, alien.posy + 10, COLOR_PURPLE))
                        powerups.append(PowerUp(alien.posx, alien.posy + 10, random.choice(['FIRE', 'MULTI', 'WIDE'])))
                    else:
                        sfx.play('alien_hit')
                        for _ in range(6):
                            particles.append(Particle(b.posx, b.posy, (255, 120, 255)))

                # Collision Ball & Blocks
                b_r = b.getRect()
                for blk in blocks[:]:
                    if collisionChecker(blk.getRect(), b_r):
                        if not b.isFireball:
                            ox = min(b_r.right - blk.blockRect.left, blk.blockRect.right - b_r.left)
                            oy = min(b_r.bottom - blk.blockRect.top, blk.blockRect.bottom - b_r.top)
                            if ox < oy: b.xFac *= -1
                            else: b.yFac *= -1

                        if blk.hit():
                            sfx.play('break')
                            blocks.remove(blk)
                            combo += 1
                            pts = blk.points * (1 + (combo - 1) // 3)
                            score += pts
                            texts.append(FloatingText(blk.blockRect.centerx, blk.blockRect.centery, f"+{pts}", blk.color, f_hud))
                            for _ in range(12):
                                particles.append(Particle(blk.blockRect.centerx, blk.blockRect.centery, blk.color))

                            if blk.block_type == 'gold' or random.random() < 0.22:
                                powerups.append(PowerUp(blk.blockRect.centerx, blk.blockRect.centery, random.choice(['WIDE', 'MULTI', 'FIRE']) if blk.block_type == 'gold' else None))

                            if blk.block_type == 'bomb':
                                sfx.play('bomb')
                                for _ in range(30):
                                    particles.append(Particle(blk.blockRect.centerx, blk.blockRect.centery, COLOR_BOMB))
                                for oth in blocks[:]:
                                    if math.hypot(oth.blockRect.centerx - blk.blockRect.centerx, oth.blockRect.centery - blk.blockRect.centery) < 80:
                                        if oth.hit():
                                            blocks.remove(oth)
                                            score += oth.points
                                            for _ in range(8):
                                                particles.append(Particle(oth.blockRect.centerx, oth.blockRect.centery, oth.color))
                        else:
                            sfx.play('block')
                            for _ in range(4):
                                particles.append(Particle(b.posx, b.posy, WHITE))

                        if not b.isFireball:
                            break

            # Cek jika semua bola hilang
            if len(balls) == 0:
                lives -= 1
                sfx.play('lose')
                combo = 0
                if lives <= 0:
                    state = 'GAME_OVER'
                    if score > highScore: highScore = score
                else:
                    balls = [Ball(striker.posx + striker.width // 2, striker.posy - 10)]

            # Cek jika semua blok hancur (Menang)
            if len(blocks) == 0:
                sfx.play('win')
                state = 'LEVEL_CLEARED'
                score += 500 * level
                if score > highScore: highScore = score

        particles = [p for p in particles if p.update()]
        texts = [t for t in texts if t.update()]

        # Rendering
        screen.fill(BG_COLOR)
        for gx in range(0, WIDTH, 32): pygame.draw.line(screen, BG_GRID, (gx, 35), (gx, HEIGHT), 1)
        for gy in range(35, HEIGHT, 32): pygame.draw.line(screen, BG_GRID, (0, gy), (WIDTH, gy), 1)

        for blk in blocks: blk.display(screen, f_small)
        alien.display(screen)
        for l in listOfLasers: l.display(screen)
        for p in powerups: p.display(screen, f_bold)
        striker.display(screen)
        for b in balls: b.display(screen)
        for p in particles: p.display(screen)
        for t in texts: t.display(screen)

        # Top HUD Bar
        pygame.draw.rect(screen, (22, 25, 38), (0, 0, WIDTH, 35))
        pygame.draw.line(screen, (45, 50, 75), (0, 35), (WIDTH, 35), 2)
        screen.blit(f_hud.render(f"SCORE: {score:05d}", True, WHITE), (15, 9))
        screen.blit(f_small.render("[M] Muted" if sfx.muted else "[M] Sound ON", True, (120, 130, 160)), (15, 38))
        lvl_t = f_hud.render(f"LEVEL {level}", True, COLOR_YELLOW)
        screen.blit(lvl_t, (WIDTH // 2 - lvl_t.get_width() // 2, 9))
        if combo > 1:
            cmb_t = f_small.render(f"COMBO x{combo}!", True, COLOR_ORANGE)
            screen.blit(cmb_t, (WIDTH // 2 - cmb_t.get_width() // 2, 38))
        for i in range(lives):
            pygame.draw.circle(screen, COLOR_RED, (WIDTH - 20 - i * 18, 17), 6)
            pygame.draw.circle(screen, (255, 150, 150), (WIDTH - 20 - i * 18 - 2, 15), 2)

        if state == 'PLAYING' and any(b.stuck for b in balls):
            p_msg = f_hud.render("TEKAN [SPACE] UNTUK MELUNCURKAN BOLA", True, (255, 215, 0))
            screen.blit(p_msg, (WIDTH // 2 - p_msg.get_width() // 2, HEIGHT - 80))

        # Game Over / Win Screens
        if state in ('GAME_OVER', 'LEVEL_CLEARED'):
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((10, 12, 18, 210))
            screen.blit(ov, (0, 0))
            c_tit = COLOR_RED if state == 'GAME_OVER' else COLOR_GREEN
            t1 = f_title.render("GAME OVER" if state == 'GAME_OVER' else "LEVEL CLEARED!", True, c_tit)
            t2 = f_bold.render(f"FINAL SCORE: {score}" if state == 'GAME_OVER' else f"BONUS POIN: +{500 * level}!", True, WHITE if state == 'GAME_OVER' else COLOR_YELLOW)
            t3 = f_hud.render("TEKAN [SPACE] MAIN LAGI  |  [ESC] KELUAR" if state == 'GAME_OVER' else "TEKAN [SPACE] LANJUT KE LEVEL BERIKUTNYA", True, COLOR_YELLOW if state == 'GAME_OVER' else WHITE)
            for txt_surf, y_off in [(t1, -70), (t2, -15), (t3, 45)]:
                screen.blit(txt_surf, (WIDTH // 2 - txt_surf.get_width() // 2, HEIGHT // 2 + y_off))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
