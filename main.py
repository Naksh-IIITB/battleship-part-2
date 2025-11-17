import pygame
import random
from shipnew import SHIP_TYPES_LIST, SHIP_SIZES, update_ship_status_on_hit, reset_ship_status, create_ship_record
from boardnew import can_place, place_ship, auto_place_with_records, check_win
from gamemanager import process_attack

pygame.init()
screen = pygame.display.set_mode((1000,800))
pygame.display.set_caption('BATTLESHIP')
clock = pygame.time.Clock()

# Fonts
font1 = pygame.font.Font(None,50)
font2 = pygame.font.Font(None,30)

# Input box setup
input_box = pygame.Rect(350,350,300,60)
active = False
text = ""
p1 = ""
p2 = ""
current = "p1"

# Background and buttons - using fallback colors if images not found
try:
    bg1 = pygame.image.load(r"C:\Users\srika\OneDrive\Desktop\random.jpg").convert()
    bg1 = pygame.transform.scale(bg1,(1000,800))
except Exception:
    bg1 = pygame.Surface((1000,800))
    bg1.fill((20,50,80))

# Load ship image - create fallback if not found
try:
    ship_image = pygame.image.load(r"C:\Users\srika\OneDrive\Desktop\ship.jpg").convert_alpha()
    ship_image = pygame.transform.scale(ship_image,(35,35))
except Exception:
    ship_image = pygame.Surface((35,35), pygame.SRCALPHA)
    pygame.draw.circle(ship_image, (200,200,200), (17,17), 15)

manual_button = pygame.Rect(300,300,400,80)
automatic_button = pygame.Rect(300,420,400,80)

# Game variables
game_state = "input"
gridsize = 10
board_topleft = (300,200)
ships_placed = 0

# Boards
p1board = [[0]*gridsize for i in range(gridsize)]
p2board = [[0]*gridsize for i in range(gridsize)]
p1_attempts = [[0]*gridsize for i in range(gridsize)]
p2_attempts = [[0]*gridsize for i in range(gridsize)]

current_player = "p1"
winner = None

# Colors
WHITE = (255,255,255)
GRAY  = (150,150,150)
RED   = (220,50,50)
BLUE  = (50,120,220)
BG_COL = (20,50,80)

# Ship placement tracking
ship_index = 0
ship_dir = "H"

# Per-player ship records
p1_ships = []
p2_ships = []

# Per-player ship-status dicts
ship_status_p1 = {name: False for name, _ in SHIP_TYPES_LIST}
ship_status_p2 = {name: False for name, _ in SHIP_TYPES_LIST}

# ---------------------------
# Drawing helpers
# ---------------------------
def drawboard(board, top_left):
    for r in range(gridsize):
        for c in range(gridsize):
            rect = pygame.Rect(top_left[0]+c*35, top_left[1]+r*35, 35,35)
            pygame.draw.rect(screen, WHITE, rect, 2)
            if board[r][c] == 1:
                screen.blit(ship_image, rect.topleft)

def draw_attempts(attempts, top_left):
    for r in range(gridsize):
        for c in range(gridsize):
            rect = pygame.Rect(top_left[0]+c*35, top_left[1]+r*35, 35,35)
            if attempts[r][c] == 2:  # hit
                pygame.draw.rect(screen, RED, rect)
            elif attempts[r][c] == 3:  # miss
                pygame.draw.rect(screen, BLUE, rect)
            pygame.draw.rect(screen, GRAY, rect, 1)

def draw_ship_status_for_opponent(opponent_ship_status, topleft=(700,200)):
    """Draw ship list for opponent."""
    x, y = topleft
    title = font1.render("SHIPS", True, (255,255,0))
    screen.blit(title, (x, y))
    y += 60
    for name, size in SHIP_TYPES_LIST:
        color = RED if opponent_ship_status.get(name, False) else WHITE
        txt = font2.render(f"{size} - {name}", True, color)
        screen.blit(txt, (x, y))
        y += 40

# ---------------------------
# Main Game Loop
# ---------------------------
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # allow rotation
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                ship_dir = "V" if ship_dir == "H" else "H"

        # INPUT STATE
        if game_state == "input":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = True
                else:
                    active = False
            if event.type == pygame.KEYDOWN:
                if current == "done" and event.key == pygame.K_SPACE:
                    game_state = "menu"
                elif active:
                    if event.key == pygame.K_RETURN:
                        if text.strip() != "":
                            if current == "p1":
                                p1 = text.strip()
                                text = ""
                                current = "p2"
                            elif current == "p2":
                                p2 = text.strip()
                                text = ""
                                current = "done"
                                active = False
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        if len(text) < 20:
                            text += event.unicode

        # MENU STATE
        elif game_state == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if manual_button.collidepoint(event.pos):
                    game_state = "setup_manual_p1"
                    current_player = "p1"
                    ships_placed = 0
                    ship_index = 0
                    ship_dir = "H"
                    # clear any previous ship records
                    p1_ships = []
                    p2_ships = []
                    reset_ship_status(ship_status_p1)
                    reset_ship_status(ship_status_p2)
                    # clear boards
                    p1board = [[0]*gridsize for _ in range(gridsize)]
                    p2board = [[0]*gridsize for _ in range(gridsize)]
                    p1_attempts = [[0]*gridsize for _ in range(gridsize)]
                    p2_attempts = [[0]*gridsize for _ in range(gridsize)]
                elif automatic_button.collidepoint(event.pos):
                    # reset boards & records
                    p1board = [[0]*gridsize for _ in range(gridsize)]
                    p2board = [[0]*gridsize for _ in range(gridsize)]
                    p1_attempts = [[0]*gridsize for _ in range(gridsize)]
                    p2_attempts = [[0]*gridsize for _ in range(gridsize)]
                    p1_ships = []
                    p2_ships = []
                    reset_ship_status(ship_status_p1)
                    reset_ship_status(ship_status_p2)
                    # auto place with records
                    auto_place_with_records(p1board, p1_ships, gridsize)
                    auto_place_with_records(p2board, p2_ships, gridsize)
                    game_state = "ready"

        # MANUAL P1
        elif game_state == "setup_manual_p1":
            if event.type == pygame.MOUSEBUTTONDOWN:
                x,y = event.pos
                grid_x = (x-board_topleft[0])//35
                grid_y = (y-board_topleft[1])//35
                if 0 <= grid_x < gridsize and 0 <= grid_y < gridsize:
                    if ship_index < len(SHIP_SIZES):
                        size = SHIP_SIZES[ship_index]
                        if can_place(p1board, grid_y, grid_x, size, ship_dir, gridsize):
                            cells = place_ship(p1board, grid_y, grid_x, size, ship_dir)
                            name = SHIP_TYPES_LIST[ship_index][0]
                            p1_ships.append(create_ship_record(name, cells))
                            ship_index += 1
                            ships_placed = ship_index
                    if ships_placed >= len(SHIP_SIZES):
                        game_state = "setup_manual_p2"
                        ships_placed = 0
                        ship_index = 0
                        ship_dir = "H"

        # MANUAL P2
        elif game_state == "setup_manual_p2":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x,y = event.pos
                grid_x = (x-board_topleft[0])//35
                grid_y = (y-board_topleft[1])//35
                if 0 <= grid_x < gridsize and 0 <= grid_y < gridsize:
                    if ship_index < len(SHIP_SIZES):
                        size = SHIP_SIZES[ship_index]
                        if can_place(p2board, grid_y, grid_x, size, ship_dir, gridsize):
                            cells = place_ship(p2board, grid_y, grid_x, size, ship_dir)
                            name = SHIP_TYPES_LIST[ship_index][0]
                            p2_ships.append(create_ship_record(name, cells))
                            ship_index += 1
                            ships_placed = ship_index
                    if ships_placed >= len(SHIP_SIZES):
                        game_state = "ready"
                        ships_placed = 0
                        ship_index = 0
                        ship_dir = "H"

        # READY STATE
        elif game_state == "ready":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_state = "battle"

        # BATTLE STATE
        elif game_state == "battle":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                grid_x = (x - board_topleft[0]) // 35
                grid_y = (y - board_topleft[1]) // 35
                if 0 <= grid_x < gridsize and 0 <= grid_y < gridsize:
                    current_player, winner = process_attack(
                        current_player, grid_y, grid_x, p1board, p2board, 
                        p1_attempts, p2_attempts, p1_ships, p2_ships, 
                        ship_status_p1, ship_status_p2, p1, p2, gridsize
                    )
                    if winner is not None:
                        game_state = "gameover"

        # GAME OVER STATE
        elif game_state == "gameover":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

    # ---------------- DRAWING ----------------
    screen.blit(bg1,(0,0))

    if game_state == "input":
        if current == "p1":
            label = font1.render("Enter p1:", True, WHITE)
        elif current == "p2":
            label = font1.render("Enter p2:", True, WHITE)
        else:
            label = font1.render(f"Welcome {p1} & {p2}!", True, WHITE)
            sub = font2.render("Press SPACE to start the game!", True, (255,200,0))
            screen.blit(label,(200,300))
            screen.blit(sub,(250,380))
            pygame.display.flip()
            clock.tick(60)
            continue
        screen.blit(label,(250,200))
        pygame.draw.rect(screen,(200,0,0),input_box,5)
        txt_surface = font1.render(text,True,WHITE)
        screen.blit(txt_surface,(input_box.x+10,input_box.y+10))

    elif game_state == "menu":
        title = font1.render("Choose set up mode",True,WHITE)
        screen.blit(title,(250,250))
        pygame.draw.rect(screen,(30,120,200),manual_button)
        pygame.draw.rect(screen,(30,120,200),automatic_button)
        screen.blit(font2.render("set board manually",True,WHITE),
                    (manual_button.x+50,manual_button.y+35))
        screen.blit(font2.render("automatically set up",True,WHITE),
                    (automatic_button.x+35,automatic_button.y+45))

    elif game_state == "setup_manual_p1":
        screen.blit(font2.render(f"{p1} place ships ({ships_placed}/{len(SHIP_SIZES)})",
                                 True,WHITE),(300,100))
        screen.blit(font2.render("Click on grid to place ships (press R to rotate)",True,GRAY),
                    (330,140))
        if ship_index < len(SHIP_SIZES):
            screen.blit(font2.render(f"Placing size: {SHIP_SIZES[ship_index]} | Dir: {ship_dir}",
                                     True,WHITE),(300,180))
        drawboard(p1board, board_topleft)

    elif game_state == "setup_manual_p2":
        screen.blit(font2.render(f"{p2} place ships ({ships_placed}/{len(SHIP_SIZES)})",
                                 True,WHITE),(300,100))
        screen.blit(font2.render("Click on grid to place ships (press R to rotate)",True,GRAY),
                    (330,140))
        if ship_index < len(SHIP_SIZES):
            screen.blit(font2.render(f"Placing size: {SHIP_SIZES[ship_index]} | Dir: {ship_dir}",
                                     True,WHITE),(300,180))
        drawboard(p2board, board_topleft)

    elif game_state == "ready":
        screen.blit(font1.render("Both players ready!",True,(0,200,0)),(280,300))
        screen.blit(font2.render("Press SPACE to start battle!",True,WHITE),(320,370))

    elif game_state == "battle":
        screen.blit(font1.render(f"{p1 if current_player=='p1' else p2}'s turn",
                                 True,(255,220,0)),(300,130))
        screen.blit(font2.render("Click on grid to attack!",True,WHITE),(320,170))

        # Draw attempts and ship-status panel for the opponent
        if current_player == "p1":
            draw_attempts(p2_attempts, board_topleft)
            draw_ship_status_for_opponent(ship_status_p2)
        else:
            draw_attempts(p1_attempts, board_topleft)
            draw_ship_status_for_opponent(ship_status_p1)

    elif game_state == "gameover":
        screen.blit(font1.render(f"{winner} wins!",True,(0,200,0)),(330,300))
        screen.blit(font2.render("Press ESC to quit",True,WHITE),(380,360))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()