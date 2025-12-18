# Ultra-polished Single-file Pygame Hangman
# Word list updated for 4th-grade vocabulary only

import pygame
import random
import string
import sys
import time

# ---------------------- CONFIG ----------------------
WIDTH, HEIGHT = 900, 600
FPS = 60
SCALE = 1.0
BG_COLOR = (15, 15, 15)
WHITE = (240, 240, 240)
GRAY = (120, 120, 120)
RED = (200, 60, 60)
GREEN = (80, 200, 120)
BLUE = (80, 160, 255)
YELLOW = (220, 200, 120)
GOLD = (255, 215, 0)

DIFFICULTIES = {'EASY':8,'NORMAL':6,'HARD':4}
DEFAULT_DIFFICULTY = 'NORMAL'
TIMED_LIMIT = 90
ANIMATION_SPEED = 0.3

# ---------------------- WORD LIST ----------------------
WORDLIST = (
    'apple','ball','cat','dog','elephant','fish','goat','hat','ice','jungle','kite','lion','monkey','nest','orange',
    'pig','queen','rabbit','sun','tree','umbrella','vase','wolf','xylophone','yak','zebra','book','chair','desk','pen',
    'pencil','school','teacher','friend','family','home','house','garden','river','mountain','beach','car','bike','train',
    'airplane','ship','boat','door','window','flower','grass','leaf','rock','sand','star','moon','cloud','rain','snow',
    'bird','cow','sheep','horse','duck','chicken','frog','snake','tiger','bear','fox','owl','bee','ant','spider','bat',
    'balloon','cake','cookie','milk','bread','water','juice','soup','egg','cheese','butter','honey','salt','sugar','rice',
    'pasta','fruit','vegetable','meat','fish','bread','icecream','chocolate','toy','game','music','song','dance','play',
    'run','jump','swim','read','write','draw','paint','sing','listen','watch','talk','laugh','cry','sleep','dream'
)

# ---------------------- INIT ----------------------
pygame.init()
screen = pygame.display.set_mode((int(WIDTH*SCALE),int(HEIGHT*SCALE)))
pygame.display.set_caption('Hangman – Ultra Edition')
clock = pygame.time.Clock()
FONT_LG = pygame.font.SysFont('consolas',int(48*SCALE)) or pygame.font.Font(None,int(48*SCALE))
FONT_MD = pygame.font.SysFont('consolas',int(28*SCALE)) or pygame.font.Font(None,int(28*SCALE))
FONT_SM = pygame.font.SysFont('consolas',int(20*SCALE)) or pygame.font.Font(None,int(20*SCALE))

# ---------------------- STATS ----------------------
stats = {'wins':0,'losses':0}

# ---------------------- GAME STATE ----------------------

def new_game(difficulty):
    word = random.choice(WORDLIST).lower()
    return {'word': word,'word_set': set(word),'guessed': set(),'wrong': 0,'max_wrong': DIFFICULTIES[difficulty],'status': 'playing','shake': 0.0,'difficulty': difficulty,'start_time': time.time(),'timed': TIMED_LIMIT>0,'fade': 0.0}

game = new_game(DEFAULT_DIFFICULTY)

# ---------------------- UI ----------------------
KEYS = list(string.ascii_uppercase)
KEY_SIZE = int(36*SCALE)
KEY_MARGIN = int(6*SCALE)
KEY_COLS = 7
KEY_START = (WIDTH - KEY_SIZE*KEY_COLS - KEY_MARGIN*(KEY_COLS-1) - 20, 150)  # Right-hand side
key_rects = {}
for i, k in enumerate(KEYS):
    x = KEY_START[0] + (i % KEY_COLS) * (KEY_SIZE + KEY_MARGIN)
    y = KEY_START[1] + (i // KEY_COLS) * (KEY_SIZE + KEY_MARGIN)
    key_rects[k] = pygame.Rect(x, y, KEY_SIZE, KEY_SIZE)

DIFF_BTNS = {}
for i, d in enumerate(DIFFICULTIES):
    DIFF_BTNS[d] = pygame.Rect(int(30*SCALE + i*120*SCALE), int(20*SCALE), int(110*SCALE), int(36*SCALE))

# ---------------------- DRAW HELPERS ----------------------

def glow_text(surface, text, font, color, pos):
    glow = font.render(text, True, (0,0,0))
    for dx in (-2,2):
        for dy in (-2,2): surface.blit(glow, (pos[0]+dx, pos[1]+dy))
    surface.blit(font.render(text, True, color), pos)

def draw_gallows():
    # Lengthened hangman pole
    pygame.draw.line(world, WHITE, (150,400), (350,400), 4)  # base
    pygame.draw.line(world, WHITE, (250,400), (250,100), 4)  # longer vertical pole
    pygame.draw.line(world, WHITE, (250,100), (420,100), 4)  # top beam
    pygame.draw.line(world, WHITE, (420,100), (420,160), 4)  # rope

def draw_hangman(stage):
    parts = [
        lambda: pygame.draw.circle(world, WHITE, (420,200), 35, 3),
        lambda: pygame.draw.line(world, WHITE, (420,235),(420,330), 3),
        lambda: pygame.draw.line(world, WHITE, (420,260),(380,300), 3),
        lambda: pygame.draw.line(world, WHITE, (420,260),(460,300), 3),
        lambda: pygame.draw.line(world, WHITE, (420,330),(390,390), 3),
        lambda: pygame.draw.line(world, WHITE, (420,330),(450,390), 3)
    ]
    stage_index = min(max(0, stage), len(parts))
    for i in range(stage_index):
        parts[i]()

def draw_word():
    txt = ' '.join(c if c in game['guessed'] else '_' for c in game['word'])
    surf = FONT_LG.render(txt, True, WHITE)
    rect = surf.get_rect(center=(WIDTH//2 - 50, 480))  # moved lower for more space below base
    world.blit(surf, rect)

def draw_keyboard():
    for letter, rect in key_rects.items():
        l = letter.lower()
        color = GREEN if l in game['guessed'] and l in game['word_set'] else RED if l in game['guessed'] else BLUE
        pygame.draw.rect(world, color, rect, border_radius=6)
        t = FONT_SM.render(letter, True, WHITE)
        world.blit(t, t.get_rect(center=rect.center))

def draw_status():
    if game['status'] == 'won': msg, col = 'YOU WON! Press R', GOLD
    elif game['status'] == 'lost': msg, col = f'YOU LOST! Word: {game["word"]} Press R', RED
    else: msg, col = 'Type or click letters', GRAY
    glow_text(world, msg, FONT_MD, col, (WIDTH//2 - 220, 60))

def draw_difficulty():
    for d, r in DIFF_BTNS.items():
        col = GREEN if d == game['difficulty'] else GRAY
        pygame.draw.rect(world, col, r, 2, border_radius=6)
        t = FONT_SM.render(d, True, col)
        world.blit(t, t.get_rect(center=r.center))

def draw_stats():
    s = f"Wins: {stats['wins']} Losses: {stats['losses']}"
    t = FONT_SM.render(s, True, YELLOW)
    world.blit(t, (WIDTH-260, 20))

def draw_timer():
    if not game['timed']: return
    elapsed = int(time.time() - game['start_time'])
    remaining = max(0, TIMED_LIMIT - elapsed)
    t = FONT_SM.render(f'Time: {remaining}', True, YELLOW)
    world.blit(t, (WIDTH-140, 50))
    if remaining == 0 and game['status'] == 'playing': game['status'] = 'lost'; stats['losses'] += 1

# ---------------------- LOGIC ----------------------

def handle_guess(letter):
    letter = letter.lower()
    if game['status'] != 'playing' or letter in game['guessed']: return
    game['guessed'].add(letter)
    if letter not in game['word_set']:
        game['wrong'] += 1
        game['shake'] = 12.0
        if game['wrong'] >= game['max_wrong']: game['status'] = 'lost'; stats['losses'] += 1
    elif game['word_set'].issubset(game['guessed']): game['status'] = 'won'; stats['wins'] += 1

# ---------------------- MAIN LOOP ----------------------
world = pygame.Surface((WIDTH, HEIGHT))
running = True
fade_speed = 0.05

while running:
    clock.tick(FPS)
    for e in pygame.event.get():
        if e.type == pygame.QUIT: running = False
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE: running = False
            if e.key == pygame.K_r: game = new_game(game['difficulty'])
            if pygame.K_a <= e.key <= pygame.K_z: handle_guess(chr(e.key))
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for d, r in DIFF_BTNS.items():
                if r.collidepoint(e.pos): game = new_game(d)
            for k, r in key_rects.items():
                if r.collidepoint(e.pos): handle_guess(k.lower())

    offset = int(game['shake'])
    game['shake'] *= 0.85

    world.fill(BG_COLOR)
    draw_difficulty()
    draw_stats()
    draw_timer()
    draw_gallows()
    draw_hangman(game['wrong'])
    draw_word()
    draw_keyboard()
    draw_status()

    screen.fill(BG_COLOR)
    screen.blit(world, (random.randint(-offset, offset), random.randint(-offset, offset)))
    pygame.display.flip()

pygame.quit()
sys.exit()
