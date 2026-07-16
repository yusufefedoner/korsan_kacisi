import pygame
import time
import json
import os
import random

pygame.init()

WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Korsan Kacisi: Gokyuzu Adalari")

clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 36)
big_font = pygame.font.Font(None, 80)

LEADERBOARD_FILE = "leaderboard.json"

# --- GÖRSEL VARLIKLAR ---
if not os.path.exists("assets"):
    os.makedirs("assets")

def load_image(name, size):
    path = os.path.join("assets", name)
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    return None

# WebP veya PNG fark etmeksizin calisması icin esnek yukleme yapısı
player_right_img = load_image("player.webp", (40, 40)) or load_image("player.png", (40, 40))
# Eğer sağa bakan görsel yüklendiyse, onun yatayda tersini alarak sola bakan görseli otomatik oluşturur
if player_right_img:
    player_left_img = pygame.transform.flip(player_right_img, True, False)
else:
    player_left_img = None
enemy_img = load_image("enemy.webp", (40, 40)) or load_image("enemy.png", (40, 40))
boss_img = load_image("enemy.webp", (80, 80)) or load_image("enemy.png", (80, 80))
bg_img = load_image("background.webp", (WIDTH, HEIGHT)) or load_image("background.png", (WIDTH, HEIGHT))
coin_img = load_image("coin.webp", (25, 25)) or load_image("coin.png", (25, 25))

# --- OZEL EFEKT SISTEMLERI ---
rain_drops = [{"x": random.randint(0, WIDTH), "y": random.randint(-HEIGHT, HEIGHT), "speed": random.randint(8, 15), "length": random.randint(10, 20)} for _ in range(80)]
explosion_particles = []

def create_explosion(x, y):
    for _ in range(20):
        explosion_particles.append({
            "x": x, "y": y,
            "vx": random.uniform(-4, 4), "vy": random.uniform(-6, 2),
            "radius": random.randint(4, 8),
            "color": random.choice([(255, 69, 0), (255, 140, 0), (100, 100, 100)]),
            "lifetime": random.randint(20, 40)
        })

def update_and_draw_effects():
    for drop in rain_drops:
        drop["y"] += drop["speed"]
        drop["x"] += 1
        if drop["y"] > HEIGHT:
            drop["y"] = random.randint(-50, -10)
            drop["x"] = random.randint(0, WIDTH)
        pygame.draw.line(screen, (130, 140, 160), (drop["x"], drop["y"]), (drop["x"] + 1, drop["y"] + drop["length"]), 1)

    for p in explosion_particles[:]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["vy"] += 0.1
        p["lifetime"] -= 1
        if p["lifetime"] <= 0: explosion_particles.remove(p)
        else: pygame.draw.circle(screen, p["color"], (int(p["x"]), int(p["y"])), p["radius"])

# --- SKOR VE SEVIYE SISTEMI ---
def save_score(score):
    try:
        with open(LEADERBOARD_FILE, "r") as f: scores = json.load(f)
    except: scores = []
    scores.append(score); scores.sort(); scores = scores[:10]
    with open(LEADERBOARD_FILE, "w") as f: json.dump(scores, f)

def load_scores():
    try:
        with open(LEADERBOARD_FILE, "r") as f: return json.load(f)
    except: return []

def get_background_color(level):
    colors = {1:(30,40,60), 2:(40,50,80), 3:(50,60,100), 10:(20,10,10)}
    return colors.get(level, (30, 40, 60))

def create_level(lv):
    return [

        [pygame.Rect(50,350,200,20), pygame.Rect(400,280,200,20), pygame.Rect(750,220,200,20)],
        [pygame.Rect(50,450,150,20), pygame.Rect(280,350,200,20), pygame.Rect(500,250,200,20), pygame.Rect(750,180,200,20)],
        [pygame.Rect(50,250,120,20), pygame.Rect(250,380,150,20), pygame.Rect(500,450,150,20), pygame.Rect(750,320,200,20)],
        [pygame.Rect(50,400,150,20), pygame.Rect(260,320,250,20), pygame.Rect(480,240,200,20), pygame.Rect(700,280,150,20), pygame.Rect(880,350,120,20)],
        [pygame.Rect(50,320,150,20), pygame.Rect(300,420,150,20), pygame.Rect(550,300,150,20), pygame.Rect(780,200,150,20)],
        [pygame.Rect(50,200,150,20), pygame.Rect(250,300,150,20), pygame.Rect(500,400,150,20), pygame.Rect(750,300,200,20)],
        [pygame.Rect(50,450,120,20), pygame.Rect(250,350,150,20), pygame.Rect(450,250,150,20), pygame.Rect(650,220,150,20), pygame.Rect(820,300,150,20)],
        [pygame.Rect(50,300,180,20), pygame.Rect(180,380,200,20), pygame.Rect(450,420,200,20), pygame.Rect(620,320,200,20), pygame.Rect(800,220,180,20)],
        [pygame.Rect(50,400,100,20), pygame.Rect(200,320,160,20), pygame.Rect(400,250,150,20), pygame.Rect(650,320,140,20), pygame.Rect(850,400,120,20)],
        [pygame.Rect(50,350,200,20), pygame.Rect(400,260,200,20), pygame.Rect(750,200,200,10)],
    ][lv - 1]

def create_enemy(lv, platforms):
    if lv == 10:
        return [{"rect": pygame.Rect(750, 120, 80, 80), "start_x": 750, "end_x": 900, "speed": 5}]
    
    enemies_list = []
    for p in platforms[1:-1]:
        enemies_list.append({
            "rect": pygame.Rect(p.centerx - 20, p.top - 40, 40, 40),
            "start_x": p.left,
            "end_x": p.right - 40,
            "speed": random.choice([2, -2])
        })
    return enemies_list

def create_coins(lv, platforms):
    coins = []
    for p in platforms:
        coins.append(pygame.Rect(p.centerx - 12, p.top - 40, 25, 25))
    return coins

# --- ANA MENU ---
timed_mode = False
while True:
    screen.fill((20, 20, 40))
    title = big_font.render("KORSAN KACISI", True, (255,215,0))
    normal = font.render("1 - Normal Mod", True, (255,255,255))
    timed = font.render("2 - Sureli Mod", True, (255,255,255))
    board = font.render("3 - Liderlik Tablosu", True, (255,255,255))

    screen.blit(title, (240,120))
    screen.blit(normal, (380,260))
    screen.blit(timed, (380,320))
    screen.blit(board, (380,380))
    pygame.display.flip()
    
    choice_made = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1: choice_made = True
            elif event.key == pygame.K_2: timed_mode = True; choice_made = True
            elif event.key == pygame.K_3:
                showing = True
                while showing:
                    screen.fill((15, 15, 25))
                    txt = big_font.render("LIDERLIK", True, (255,215,0))
                    screen.blit(txt, (350,50))
                    scores = load_scores()
                    if len(scores) == 0: screen.blit(font.render("Kayit yok.", True, (255,255,255)), (440,200))
                    for i, score in enumerate(scores): screen.blit(font.render(f"{i+1}. {score:.2f} sn", True, (255,255,255)), (410,170 + i * 40))
                    screen.blit(font.render("Geri donmek icin ESC", True, (150,150,150)), (360,520))
                    pygame.display.flip()
                    for e in pygame.event.get():
                        if e.type == pygame.QUIT: pygame.quit(); quit()
                        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE: showing = False
    if choice_made: break

# --- OYUN BASLANGIC AYARLARI ---
level = 1
platforms = create_level(level) # Hatalı olan satır düzeltildi (level=1 yerine sadece level yazıldı)
player = pygame.Rect(platforms[0].left + 20, platforms[0].top - 45, 40, 40)
player_direction = "right"

y_vel = 0
gravity = 0.6
on_ground = False

hp = 100000
max_level = 10
score_coins = 0

enemies = create_enemy(level, platforms)
coins = create_coins(level, platforms)

start_time = time.time()
time_limit = 60
running = True
victory = False

# --- ANA OYUN DONGUSU ---
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and on_ground:
                y_vel = -13

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        player.x -= 5
        player_direction = "left"
    if keys[pygame.K_d]:
        player.x += 5
        player_direction = "right"

    y_vel += gravity
    player.y += y_vel
    on_ground = False

    # Platform Carpismasi
    for p in platforms:
        if player.colliderect(p) and y_vel > 0:
            player.bottom = p.top
            y_vel = 0
            on_ground = True

    # Düşme Kontrolü
    if player.y > HEIGHT:
        create_explosion(player.centerx, HEIGHT - 20)
        hp -= 1
        player.x = platforms[0].left + 20
        player.y = platforms[0].top - 45
        y_vel = 0
        if hp <= 0: running = False

    # Altın Toplama Kontrolü
    for c in coins[:]:
        if player.colliderect(c):
            coins.remove(c)
            score_coins += 1

    # Düşman Hareketi ve Carpismasi
    for e in enemies:
        e["rect"].x += e["speed"]
        if e["rect"].x < e["start_x"] or e["rect"].x > e["end_x"]:
            e["speed"] *= -1

        if player.colliderect(e["rect"]):
            create_explosion(player.centerx, player.centery)
            hp -= 1
            player.x = platforms[0].left + 20
            player.y = platforms[0].top - 45
            y_vel = 0
            if hp <= 0: running = False

    # Ekran Sonu / Seviye Gecisi
    if player.x > WIDTH:
        level += 1
        if level > max_level:
            victory = True
            running = False
        else:
            platforms = create_level(level)
            enemies = create_enemy(level, platforms)
            coins = create_coins(level, platforms)
            player.x = platforms[0].left + 20
            player.y = platforms[0].top - 45
            y_vel = 0

    if timed_mode:
        elapsed = time.time() - start_time
        remaining = int(time_limit - elapsed)
        if remaining <= 0: running = False

    # --- CIZIM BOLUMU ---
    if bg_img: screen.blit(bg_img, (0, 0))
    else: screen.fill(get_background_color(level))

    update_and_draw_effects()

    # Uçan Cubukları Ciz
    for p in platforms:
        pygame.draw.rect(screen, (120, 90, 60), p)

    # Paraları Ciz
    for c in coins:
        if coin_img: screen.blit(coin_img, (c.x, c.y))
        else: pygame.draw.circle(screen, (255, 215, 0), c.center, 10)

    # Düşmanları Ciz
    for e in enemies:
        if level == 10 and boss_img: screen.blit(boss_img, (e["rect"].x, e["rect"].y))
        elif enemy_img: screen.blit(enemy_img, (e["rect"].x, e["rect"].y))
        else: pygame.draw.rect(screen, (200, 30, 30), e["rect"])

    # Oyuncuyu Ciz
    if player_direction == "left" and player_left_img: screen.blit(player_left_img, (player.x, player.y))
    elif player_direction == "right" and player_right_img: screen.blit(player_right_img, (player.x, player.y))
    else: pygame.draw.rect(screen, (255, 220, 0), player)

    # HUD
    info_text = font.render(f"Can: {hp}  Seviye: {level}  Altin: {score_coins}", True, (255, 255, 255))
    screen.blit(info_text, (20, 20))
    if timed_mode:
        screen.blit(font.render(f"Sure: {remaining}", True, (255, 255, 255)), (20, 60))

    pygame.display.flip()

# --- BITIS EKRANI ---
screen.fill((20, 20, 30))
if victory:
    total_time = time.time() - start_time
    save_score(total_time)
    msg = big_font.render("KAZANDIN, KAPTAN!", True, (0, 255, 100))
    score_txt = font.render(f"Sure: {total_time:.2f} saniye | Toplanan Altin: {score_coins}", True, (255, 255, 255))
    screen.blit(msg, (220, 220))
    screen.blit(score_txt, (280, 320))
else:
    msg = big_font.render("GAME OVER!", True, (255, 50, 50))
    screen.blit(msg, (260, 250))

pygame.display.flip()
pygame.time.delay(5000)
pygame.quit()