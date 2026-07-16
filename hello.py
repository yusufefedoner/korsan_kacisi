import pygame
import random
import math

# Başlangıç
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Korsan Macerası")
clock = pygame.time.Clock()

# Renkler
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
GOLD = (255, 215, 0)
BROWN = (140, 80, 40)
BLUE = (50, 100, 200)
GREEN = (50, 180, 80)
SKY_BLUE = (135, 206, 235)
SEA_BLUE = (20, 60, 120)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)

# Fontlar
font = pygame.font.SysFont("Arial", 28)
big_font = pygame.font.SysFont("Arial", 48)
small_font = pygame.font.SysFont("Arial", 18)

class Gem:
    def __init__(self, x, y, is_player=False):
        self.x = x
        self.y = y
        self.is_player = is_player
        self.size = 40
        self.angle = 0
        self.speed = 0
        self.hp = 100
        self.max_hp = 100
        self.coins = 0
        self.cannon_cooldown = 0
        self.reload_time = 30
        self.direction = pygame.math.Vector2(0, -1)

    def draw(self, screen):
        # Gemi gövdesi
        points = [
            (self.x, self.y - self.size),
            (self.x - self.size * 0.8, self.y + self.size * 0.3),
            (self.x - self.size * 0.4, self.y + self.size * 0.1),
            (self.x, self.y + self.size * 0.5),
            (self.x + self.size * 0.4, self.y + self.size * 0.1),
            (self.x + self.size * 0.8, self.y + self.size * 0.3),
        ]
        rotated = []
        for px, py in points:
            dx = px - self.x
            dy = py - self.y
            new_x = dx * math.cos(self.angle) - dy * math.sin(self.angle) + self.x
            new_y = dx * math.sin(self.angle) + dy * math.cos(self.angle) + self.y
            rotated.append((new_x, new_y))
        
        color = GOLD if self.is_player else BROWN
        pygame.draw.polygon(screen, color, rotated)
        
        # Direk
        top = (self.x + math.sin(self.angle) * self.size * 0.3,
               self.y - math.cos(self.angle) * self.size * 1.2)
        base = (self.x - math.sin(self.angle) * self.size * 0.3,
                self.y + math.cos(self.angle) * self.size * 0.3)
        pygame.draw.line(screen, BLACK, top, base, 3)

        # Korsan bayrağı
        flag_color = RED if self.is_player else BLACK
        flag_pos = (top[0] + math.cos(self.angle) * 10 - math.sin(self.angle) * 8,
                    top[1] + math.sin(self.angle) * 10 + math.cos(self.angle) * 8)
        pygame.draw.circle(screen, flag_color, (int(flag_pos[0]), int(flag_pos[1])), 8)
        
        # Can barı
        bar_width = 50
        bar_height = 6
        bar_x = self.x - bar_width // 2
        bar_y = self.y - self.size - 20
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
        green_width = bar_width * (self.hp / self.max_hp)
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, green_width, bar_height))

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.x = max(50, min(WIDTH - 50, self.x))
        self.y = max(50, min(HEIGHT - 50, self.y))

    def rotate(self, angle_change):
        self.angle += angle_change
        self.direction = pygame.math.Vector2(
            -math.sin(self.angle),
            -math.cos(self.angle)
        )

    def shoot(self):
        if self.cannon_cooldown <= 0:
            self.cannon_cooldown = self.reload_time
            return Gülle(self.x, self.y, self.direction, self.is_player)
        return None

    def update(self):
        if self.cannon_cooldown > 0:
            self.cannon_cooldown -= 1


class Gülle:
    def __init__(self, x, y, direction, is_player):
        self.x = x
        self.y = y
        self.direction = direction.normalize()
        self.speed = 8
        self.radius = 6
        self.is_player = is_player
        self.active = True

    def move(self):
        self.x += self.direction.x * self.speed
        self.y += self.direction.y * self.speed
        if self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT:
            self.active = False

    def draw(self, screen):
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, GRAY, (int(self.x), int(self.y)), self.radius - 2)


class HazineAda:
    def __init__(self):
        self.x = random.randint(100, WIDTH - 100)
        self.y = random.randint(100, HEIGHT - 100)
        self.radius = 25
        self.collected = False

    def draw(self, screen):
        if not self.collected:
            # Ada
            pygame.draw.circle(screen, GREEN, (int(self.x), int(self.y)), self.radius)
            # Hazine işareti
            pygame.draw.circle(screen, GOLD, (int(self.x), int(self.y)), 10)
            pygame.draw.line(screen, RED, (self.x - 6, self.y), (self.x + 6, self.y), 2)
            pygame.draw.line(screen, RED, (self.x, self.y - 6), (self.x, self.y + 6), 2)


class Düşman:
    def __init__(self):
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            self.gem = Gem(random.randint(50, WIDTH - 50), -50)
        elif side == 'bottom':
            self.gem = Gem(random.randint(50, WIDTH - 50), HEIGHT + 50)
        elif side == 'left':
            self.gem = Gem(-50, random.randint(50, HEIGHT - 50))
        else:
            self.gem = Gem(WIDTH + 50, random.randint(50, HEIGHT - 50))
        self.gem.hp = 50
        self.shoot_timer = random.randint(60, 180)
        self.max_shoot_timer = self.shoot_timer

    def update(self, player_x, player_y):
        # Oyuncuya doğru hareket
        dx = player_x - self.gem.x
        dy = player_y - self.gem.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 0:
            self.gem.angle = math.atan2(-dx, dy)
            self.gem.direction = pygame.math.Vector2(
                -math.sin(self.gem.angle),
                -math.cos(self.gem.angle)
            )
            if dist > 200:
                self.gem.x += (dx / dist) * 1.5
                self.gem.y += (dy / dist) * 1.5

        # Ateş etme
        self.shoot_timer -= 1
        if self.shoot_timer <= 0 and dist < 400:
            self.shoot_timer = self.max_shoot_timer
            return self.gem.shoot()
        return None

    def draw(self, screen):
        self.gem.draw(screen)


class GemPatlama:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.particles = []
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 30,
                'color': random.choice([RED, GOLD, YELLOW, ORANGE])
            })

    def update(self):
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            p['vx'] *= 0.95
            p['vy'] *= 0.95
            if p['life'] <= 0:
                self.particles.remove(p)
        return len(self.particles) > 0

    def draw(self, screen):
        for p in self.particles:
            alpha = p['life'] / 30
            pygame.draw.circle(screen, p['color'], 
                             (int(p['x']), int(p['y'])), int(4 * alpha))

ORANGE = (255, 165, 0)


def oyunu_başlat():
    player = Gem(WIDTH // 2, HEIGHT // 2, is_player=True)
    enemies = []
    cannons = []
    hazineler = [HazineAda() for _ in range(3)]
    patlamalar = []
    score = 0
    dalga = 1
    enemy_spawn_timer = 0
    oyun_devam = True
    game_over = False

    while oyun_devam:
        screen.fill(SEA_BLUE)
        
        # Dalga efekti
        for i in range(0, WIDTH, 20):
            wave_y = HEIGHT // 2 + math.sin(pygame.time.get_ticks() * 0.003 + i * 0.05) * 20
            pygame.draw.line(screen, BLUE, (i, wave_y), (i + 10, wave_y + 5), 1)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                oyun_devam = False

        if not game_over:
            # Kontroller
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                player.rotate(-0.05)
            if keys[pygame.K_RIGHT]:
                player.rotate(0.05)
            if keys[pygame.K_UP]:
                dx = -math.sin(player.angle) * 3
                dy = -math.cos(player.angle) * 3
                player.move(dx, dy)
            if keys[pygame.K_DOWN]:
                dx = math.sin(player.angle) * 2
                dy = math.cos(player.angle) * 2
                player.move(dx, dy)
            if keys[pygame.K_SPACE]:
                gülle = player.shoot()
                if gülle:
                    cannons.append(gülle)

            player.update()

            # Düşman spawn
            enemy_spawn_timer += 1
            if enemy_spawn_timer > max(60, 180 - dalga * 15):
                enemies.append(Düşman())
                enemy_spawn_timer = 0
                if len(enemies) > 5 + dalga:
                    # Fazla düşmanları temizle
                    enemies = enemies[-5 - dalga:]

            # Gülleleri güncelle
            for g in cannons[:]:
                g.move()
                if not g.active:
                    cannons.remove(g)
                else:
                    # Düşman gülleleri oyuncuya çarpıyor
                    if not g.is_player:
                        if math.sqrt((g.x - player.x)**2 + (g.y - player.y)**2) < 30:
                            player.hp -= 10
                            cannons.remove(g)
                            patlamalar.append(GemPatlama(g.x, g.y))
                    # Oyuncu gülleleri düşmanlara çarpıyor
                    else:
                        for d in enemies[:]:
                            if math.sqrt((g.x - d.gem.x)**2 + (g.y - d.gem.y)**2) < 30:
                                d.gem.hp -= 25
                                cannons.remove(g)
                                patlamalar.append(GemPatlama(g.x, g.y))
                                if d.gem.hp <= 0:
                                    enemies.remove(d)
                                    score += 100
                                    player.coins += random.randint(10, 30)
                                    patlamalar.append(GemPatlama(d.gem.x, d.gem.y))
                                break

            # Düşmanları güncelle
            for d in enemies[:]:
                gülle = d.update(player.x, player.y)
                if gülle:
                    cannons.append(gülle)
                # Çarpışma kontrolü
                if math.sqrt((d.gem.x - player.x)**2 + (d.gem.y - player.y)**2) < 50:
                    player.hp -= 15
                    enemies.remove(d)
                    patlamalar.append(GemPatlama(d.gem.x, d.gem.y))

            # Hazine toplama
            for h in hazineler:
                if not h.collected:
                    if math.sqrt((player.x - h.x)**2 + (player.y - h.y)**2) < 40:
                        h.collected = True
                        score += 200
                        player.coins += 50
                        patlamalar.append(GemPatlama(h.x, h.y))

            # Yeni dalga
            if all(h.collected for h in hazineler):
                dalga += 1
                hazineler = [HazineAda() for _ in range(3)]
                player.hp = min(player.max_hp, player.hp + 20)
                # Mesaj
                mesaj = big_font.render(f"DALGA {dalga}!", True, GOLD)
                screen.blit(mesaj, (WIDTH//2 - 100, HEIGHT//2 - 50))

            # Patlamaları güncelle
            for p in patlamalar[:]:
                if not p.update():
                    patlamalar.remove(p)

            # Ölüm kontrolü
            if player.hp <= 0:
                game_over = True

        # Çizim
        # Hazineler
        for h in hazineler:
            h.draw(screen)
        
        # Gemiler
        for d in enemies:
            d.draw(screen)
        
        for g in cannons:
            g.draw(screen)
        
        player.draw(screen)
        
        for p in patlamalar:
            p.draw(screen)

        # UI
        can_text = font.render(f"Can: {int(player.hp)}/{player.max_hp}", True, WHITE)
        screen.blit(can_text, (10, 10))
        
        score_text = font.render(f"Skor: {score}", True, GOLD)
        screen.blit(score_text, (10, 45))
        
        coin_text = font.render(f"Altın: {player.coins}", True, YELLOW)
        screen.blit(coin_text, (10, 80))
        
        dalga_text = small_font.render(f"Dalga: {dalga}", True, WHITE)
        screen.blit(dalga_text, (10, 115))

        if game_over:
            go_text = big_font.render("OYUN BİTTİ!", True, RED)
            screen.blit(go_text, (WIDTH//2 - 130, HEIGHT//2 - 100))
            restart_text = font.render("R'ye basarak yeniden başla", True, WHITE)
            screen.blit(restart_text, (WIDTH//2 - 140, HEIGHT//2 - 30))
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                return True  

        pygame.display.flip()
        clock.tick(60)

    return False


# Ana döngü
çalışıyor = True
while çalışıyor:
    çalışıyor = oyunu_başlat()

pygame.quit()