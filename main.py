import pygame
import random
from shipnew import SHIP_TYPES_LIST, SHIP_SIZES, update_ship_status_on_hit, reset_ship_status, create_ship_record
from boardnew import can_place, place_ship, auto_place_with_records, check_win
from gamemanager import process_attack
import filemanager  # uses battleship.txt saving

pygame.init()
screen = pygame.display.set_mode((1000, 800))
pygame.display.set_caption("BATTLESHIP")
clock = pygame.time.Clock()

# Fonts
font1 = pygame.font.Font(None, 50)
font2 = pygame.font.Font(None, 30)

# Input UI
input_box = pygame.Rect(350, 350, 300, 60)
active = False
text = ""
p1 = ""
p2 = ""
current = "p1"

# Background
bg1 = pygame.Surface((1000, 800))
bg1.fill((20, 50, 80))

# Ship image placeholder
ship_image = pygame.Surface((35, 35), pygame.SRCALPHA)
pygame.draw.circle(ship_image, (180, 180, 180), (17, 17), 15)

# Buttons
manual_button = pygame.Rect(300, 300, 400, 80)
automatic_button = pygame.Rect(300, 420, 400, 80)
resume_button = pygame.Rect(300, 540, 400, 60)
restart_button = pygame.Rect(720, 50, 200, 40)

# Game state
game_state = "input"
current_turn_player = ""

# NEW delay-related variables
attack_result = ""
result_timer = 0
placement_timer = 0

# last_attacker records who made the most recent attack (needed to draw show_result correctly)
last_attacker = None

# Board positions & grids
gridsize = 10
player_board_pos = (50, 200)
enemy_board_pos = (450, 200)
ship_status_pos = (820, 200)

# Boards
p1board = [[0]*gridsize for _ in range(gridsize)]
p2board = [[0]*gridsize for _ in range(gridsize)]
p1_attempts = [[0]*gridsize for _ in range(gridsize)]
p2_attempts = [[0]*gridsize for _ in range(gridsize)]

current_player = "p1"
winner = None

# Colors
WHITE = (255,255,255)
GRAY = (150,150,150)
RED = (220,50,50)
BLUE = (50,120,220)

# Manual placement
ship_index = 0
ship_dir = "H"

# Ship records
p1_ships = []
p2_ships = []
ship_status_p1 = {name: False for name,_ in SHIP_TYPES_LIST}
ship_status_p2 = {name: False for name,_ in SHIP_TYPES_LIST}

has_saved = filemanager.has_save()


# ====================================================
# SAVE / LOAD
# ====================================================
def make_save_dict():
    return {
        "game_state": game_state,
        "p1": p1,
        "p2": p2,
        "current_player": current_player,
        "winner": winner,
        "p1board": p1board,
        "p2board": p2board,
        "p1_attempts": p1_attempts,
        "p2_attempts": p2_attempts,
        "p1_ships": p1_ships,
        "p2_ships": p2_ships,
        "ship_status_p1": ship_status_p1,
        "ship_status_p2": ship_status_p2,
        "ship_index": ship_index,
        "ship_dir": ship_dir,
        "current_turn_player": current_turn_player,
        "attack_result": attack_result,
        "last_attacker": last_attacker
    }

def load_state_dict(state):
    global game_state, p1, p2, current_player, winner
    global p1board, p2board, p1_attempts, p2_attempts
    global p1_ships, p2_ships, ship_status_p1, ship_status_p2
    global ship_index, ship_dir, current_turn_player, attack_result, last_attacker

    if not state:
        return

    game_state = state.get("game_state", "menu")
    p1 = state.get("p1", "")
    p2 = state.get("p2", "")
    current_player = state.get("current_player", "p1")
    winner = state.get("winner", None)
    p1board = state.get("p1board", [[0]*gridsize for _ in range(gridsize)])
    p2board = state.get("p2board", [[0]*gridsize for _ in range(gridsize)])
    p1_attempts = state.get("p1_attempts", [[0]*gridsize for _ in range(gridsize)])
    p2_attempts = state.get("p2_attempts", [[0]*gridsize for _ in range(gridsize)])
    p1_ships = state.get("p1_ships", [])
    p2_ships = state.get("p2_ships", [])
    ship_status_p1 = state.get("ship_status_p1", {name: False for name,_ in SHIP_TYPES_LIST})
    ship_status_p2 = state.get("ship_status_p2", {name: False for name,_ in SHIP_TYPES_LIST})
    ship_index = state.get("ship_index", 0)
    ship_dir = state.get("ship_dir", "H")
    current_turn_player = state.get("current_turn_player", "")
    attack_result = state.get("attack_result", "")
    last_attacker = state.get("last_attacker", None)


# ====================================================
# DRAW HELPERS
# ====================================================
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
            if attempts[r][c] == 2:
                pygame.draw.rect(screen, RED, rect)
            elif attempts[r][c] == 3:
                pygame.draw.rect(screen, BLUE, rect)
            pygame.draw.rect(screen, GRAY, rect, 1)

def draw_full_board(board, attempts, top_left):
    for r in range(gridsize):
        for c in range(gridsize):
            rect = pygame.Rect(top_left[0]+c*35, top_left[1]+r*35, 35,35)
            pygame.draw.rect(screen, (40,40,40), rect)

            if board[r][c] == 1:
                screen.blit(ship_image, rect.topleft)

            if attempts[r][c] == 2:
                pygame.draw.rect(screen, RED, rect)
            elif attempts[r][c] == 3:
                pygame.draw.rect(screen, BLUE, rect)

            pygame.draw.rect(screen, WHITE, rect, 1)

def draw_ship_status_for_opponent(status, tl):
    x, y = tl
    screen.blit(font1.render("SHIPS", True, (255,255,0)), (x,y))
    y += 60
    for name, size in SHIP_TYPES_LIST:
        color = RED if status.get(name, False) else WHITE
        screen.blit(font2.render(f"{size} - {name}", True, color), (x,y))
        y += 40


# ====================================================
# MAIN LOOP
# ====================================================
running = True
while running:
    for event in pygame.event.get():

        # Quit autosave
        if event.type == pygame.QUIT:
            filemanager.save_game(make_save_dict())
            running = False

        # Key inputs
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                ship_dir = "V" if ship_dir == "H" else "H"
            if event.key == pygame.K_s:
                filemanager.save_game(make_save_dict())


        # =================================
        # INPUT NAMES
        # =================================
        if game_state == "input":

            if event.type == pygame.MOUSEBUTTONDOWN:
                active = input_box.collidepoint(event.pos)

            if event.type == pygame.KEYDOWN and active:
                if event.key == pygame.K_RETURN:
                    if current == "p1":
                        p1 = text.strip()
                        text = ""
                        current = "p2"
                    elif current == "p2":
                        p2 = text.strip()
                        text = ""
                        current = "done"
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode

            if current == "done" and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_state = "menu"

        # =================================
        # MENU
        # =================================
        elif game_state == "menu":

            if event.type == pygame.MOUSEBUTTONDOWN:

                if manual_button.collidepoint(event.pos):
                    p1board = [[0]*gridsize for _ in range(gridsize)]
                    p2board = [[0]*gridsize for _ in range(gridsize)]
                    p1_attempts = [[0]*gridsize for _ in range(gridsize)]
                    p2_attempts = [[0]*gridsize for _ in range(gridsize)]
                    p1_ships.clear()
                    p2_ships.clear()
                    reset_ship_status(ship_status_p1)
                    reset_ship_status(ship_status_p2)
                    ship_index = 0
                    ship_dir = "H"
                    game_state = "setup_manual_p1"

                elif automatic_button.collidepoint(event.pos):
                    p1board = [[0]*gridsize for _ in range(gridsize)]
                    p2board = [[0]*gridsize for _ in range(gridsize)]
                    p1_attempts = [[0]*gridsize for _ in range(gridsize)]
                    p2_attempts = [[0]*gridsize for _ in range(gridsize)]
                    p1_ships.clear()
                    p2_ships.clear()
                    reset_ship_status(ship_status_p1)
                    reset_ship_status(ship_status_p2)
                    auto_place_with_records(p1board, p1_ships, gridsize)
                    auto_place_with_records(p2board, p2_ships, gridsize)
                    game_state = "ready"

                elif resume_button.collidepoint(event.pos) and has_saved:
                    data = filemanager.load_game()
                    if data:
                        load_state_dict(data)


        # =================================
        # MANUAL P1
        # =================================
        elif game_state == "setup_manual_p1":

            if event.type == pygame.MOUSEBUTTONDOWN:
                x,y = event.pos
                gx = (x - player_board_pos[0]) // 35
                gy = (y - player_board_pos[1]) // 35

                if 0 <= gx < gridsize and 0 <= gy < gridsize:

                    if ship_index < len(SHIP_SIZES):
                        size = SHIP_SIZES[ship_index]
                        if can_place(p1board, gy, gx, size, ship_dir, gridsize):
                            cells = place_ship(p1board, gy, gx, size, ship_dir)
                            p1_ships.append(create_ship_record(SHIP_TYPES_LIST[ship_index][0], cells))
                            ship_index += 1

                    if ship_index >= len(SHIP_SIZES):
                        # FIRST delay: show final ship on the board
                        placement_timer = pygame.time.get_ticks() + 500
                        game_state = "placement_showboard_p1"


        # =================================
        # MANUAL P2
        # =================================
        elif game_state == "setup_manual_p2":

            if event.type == pygame.MOUSEBUTTONDOWN:
                x,y = event.pos
                gx = (x - player_board_pos[0]) // 35
                gy = (y - player_board_pos[1]) // 35

                if 0 <= gx < gridsize and 0 <= gy < gridsize:

                    if ship_index < len(SHIP_SIZES):
                        size = SHIP_SIZES[ship_index]
                        if can_place(p2board, gy, gx, size, ship_dir, gridsize):
                            cells = place_ship(p2board, gy, gx, size, ship_dir)
                            p2_ships.append(create_ship_record(SHIP_TYPES_LIST[ship_index][0], cells))
                            ship_index += 1

                    if ship_index >= len(SHIP_SIZES):
                        placement_timer = pygame.time.get_ticks() + 500
                        game_state = "placement_showboard_p2"


        # =================================
        # NEW: show final ship on P1 board
        # =================================
        elif game_state == "placement_showboard_p1":
            # After showing board for 0.5s, go to next stage
            if pygame.time.get_ticks() >= placement_timer:
                placement_timer = pygame.time.get_ticks() + 500
                game_state = "placement_done_p1"

        # =================================
        # NEW: show "P1 DONE!"
        # =================================
        elif game_state == "placement_done_p1":
            if pygame.time.get_ticks() >= placement_timer:
                ship_index = 0
                ship_dir = "H"
                game_state = "setup_manual_p2"


        # =================================
        # NEW: show final ship on P2 board
        # =================================
        elif game_state == "placement_showboard_p2":
            if pygame.time.get_ticks() >= placement_timer:
                placement_timer = pygame.time.get_ticks() + 500
                game_state = "placement_done_p2"


        # =================================
        # NEW: show "P2 DONE!"
        # =================================
        elif game_state == "placement_done_p2":
            if pygame.time.get_ticks() >= placement_timer:
                ship_index = 0
                ship_dir = "H"
                game_state = "ready"


        # =================================
        # READY
        # =================================
        elif game_state == "ready":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_state = "battle"


        # =================================
        # BATTLE
        # =================================
        elif game_state == "battle":

            if event.type == pygame.MOUSEBUTTONDOWN:
                x,y = event.pos
                gx = (x - enemy_board_pos[0]) // 35
                gy = (y - enemy_board_pos[1]) // 35

                if 0 <= gx < gridsize and 0 <= gy < gridsize:

                    prev_player = current_player
                    last_attacker = prev_player  # record who attacked

                    current_player, winner = process_attack(
                        current_player, gy, gx,
                        p1board, p2board,
                        p1_attempts, p2_attempts,
                        p1_ships, p2_ships,
                        ship_status_p1, ship_status_p2,
                        p1, p2, gridsize
                    )

                    # FORCED alternating turns (explicit)
                    current_player = "p2" if prev_player == "p1" else "p1"

                    filemanager.save_game(make_save_dict())

                    if winner is not None:
                        game_state = "gameover"

                    else:
                        # detect hit/miss based on prev_player and attempts arrays
                        if prev_player == "p1":
                            was_hit = (p2_attempts[gy][gx] == 2)
                        else:
                            was_hit = (p1_attempts[gy][gx] == 2)

                        attack_result = "HIT!" if was_hit else "MISS!"
                        result_timer = pygame.time.get_ticks() + 500
                        game_state = "show_result"


        # =================================
        # SHOW HIT/MISS
        # =================================
        elif game_state == "show_result":
            if pygame.time.get_ticks() >= result_timer:
                current_turn_player = p1 if current_player == "p1" else p2
                game_state = "switch"


        # =================================
        # COVER SCREEN
        # =================================
        elif game_state == "switch":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_state = "battle"


        # =================================
        # GAME OVER
        # =================================
        elif game_state == "gameover":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False


        # RESTART BUTTON (in all states except placement/show/result)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if restart_button.collidepoint(event.pos):
                game_state = "menu"
                p1_ships.clear()
                p2_ships.clear()
                p1board = [[0]*gridsize for _ in range(gridsize)]
                p2board = [[0]*gridsize for _ in range(gridsize)]
                p1_attempts = [[0]*gridsize for _ in range(gridsize)]
                p2_attempts = [[0]*gridsize for _ in range(gridsize)]
                reset_ship_status(ship_status_p1)
                reset_ship_status(ship_status_p2)


    # ====================================================
    # DRAW SECTION
    # ====================================================
    # default background clear (we'll override in special states)
    screen.blit(bg1, (0,0))


    # INPUT SCREEN
    if game_state == "input":

        if current == "p1":
            screen.blit(font1.render("Enter Player 1:", True, WHITE), (250,200))
        elif current == "p2":
            screen.blit(font1.render("Enter Player 2:", True, WHITE), (250,200))
        else:
            screen.blit(font1.render(f"Welcome {p1} & {p2}!", True, WHITE), (250,300))
            screen.blit(font2.render("Press SPACE to continue", True, (255,200,0)), (300,380))
            pygame.display.flip()
            continue

        pygame.draw.rect(screen, (200,0,0), input_box, 3)
        screen.blit(font1.render(text, True, WHITE), (input_box.x+10, input_box.y+10))


    # MENU
    elif game_state == "menu":
        screen.blit(font1.render("Choose Setup Mode", True, WHITE), (260,200))

        pygame.draw.rect(screen, (30,120,200), manual_button)
        screen.blit(font2.render("Manual Setup", True, WHITE),
                    (manual_button.x+130, manual_button.y+28))

        pygame.draw.rect(screen, (30,120,200), automatic_button)
        screen.blit(font2.render("Automatic Setup", True, WHITE),
                    (automatic_button.x+110, automatic_button.y+28))

        if has_saved:
            pygame.draw.rect(screen, (40,180,100), resume_button)
            screen.blit(font2.render("Resume Saved Game", True, WHITE),
                        (resume_button.x+100, resume_button.y+20))


    # MANUAL P1
    elif game_state == "setup_manual_p1":
        screen.blit(font2.render(f"{p1}: Place Ships (R to rotate)", True, WHITE), (300, 100))
        drawboard(p1board, player_board_pos)

    # MANUAL P2
    elif game_state == "setup_manual_p2":
        screen.blit(font2.render(f"{p2}: Place Ships (R to rotate)", True, WHITE), (300, 100))
        drawboard(p2board, player_board_pos)


    # FINAL SHIP DISPLAY P1
    elif game_state == "placement_showboard_p1":
        # clear and show only P1 board + small message
        screen.blit(bg1, (0,0))
        drawboard(p1board, player_board_pos)
        screen.blit(font2.render("Final ship placed!", True, WHITE), (360,150))


    # P1 DONE MESSAGE (shifted right to x=520)
    elif game_state == "placement_done_p1":
        screen.blit(bg1, (0,0))
        drawboard(p1board, player_board_pos)
        screen.blit(font1.render(f"{p1} DONE!", True, WHITE), (520,350))


    # FINAL SHIP DISPLAY P2
    elif game_state == "placement_showboard_p2":
        screen.blit(bg1, (0,0))
        drawboard(p2board, player_board_pos)
        screen.blit(font2.render("Final ship placed!", True, WHITE), (360,150))


    # P2 DONE MESSAGE (shifted right to x=520)
    elif game_state == "placement_done_p2":
        screen.blit(bg1, (0,0))
        drawboard(p2board, player_board_pos)
        screen.blit(font1.render(f"{p2} DONE!", True, WHITE), (520,350))


    # READY
    elif game_state == "ready":
        screen.blit(font1.render("Both boards ready!", True, (0,200,0)), (260,300))
        screen.blit(font2.render("Press SPACE to start battle", True, WHITE), (300,380))


    # BATTLE
    elif game_state == "battle":
        name = p1 if current_player == "p1" else p2
        screen.blit(font1.render(f"{name}'s Turn", True, (255,220,0)), (330,130))

        # Correct: message directly above the enemy grid
        screen.blit(
            font2.render("Click the enemy grid!", True, WHITE),
            (enemy_board_pos[0], enemy_board_pos[1] - 30)
        )

        if current_player == "p1":
            draw_full_board(p1board, p1_attempts, player_board_pos)
            draw_attempts(p2_attempts, enemy_board_pos)
            draw_ship_status_for_opponent(ship_status_p2, ship_status_pos)
        else:
            draw_full_board(p2board, p2_attempts, player_board_pos)
            draw_attempts(p1_attempts, enemy_board_pos)
            draw_ship_status_for_opponent(ship_status_p1, ship_status_pos)



    # HIT/MISS RESULT: draw the actual boards + colored text
    elif game_state == "show_result":
        screen.blit(bg1, (0,0))

        # Draw correct attacker's view
        if last_attacker == "p1":
            draw_full_board(p1board, p1_attempts, player_board_pos)
            draw_attempts(p2_attempts, enemy_board_pos)
            draw_ship_status_for_opponent(ship_status_p2, ship_status_pos)
        else:
            draw_full_board(p2board, p2_attempts, player_board_pos)
            draw_attempts(p1_attempts, enemy_board_pos)
            draw_ship_status_for_opponent(ship_status_p1, ship_status_pos)

        # HIT/MISS message below the boards
        color = RED if attack_result == "HIT!" else BLUE
        msg = font1.render(attack_result, True, color)
        screen.blit(msg, (430, 580))

        press_msg = font2.render("Press SPACE to continue", True, (255,255,0))
        screen.blit(press_msg, (380, 620))

        # CHECK FOR SPACE SAFELY
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            current_turn_player = p1 if current_player == "p1" else p2
            game_state = "switch"




    # COVER SCREEN
    elif game_state == "switch":
        screen.blit(font1.render(f"{current_turn_player}'s turn!", True, WHITE), (300,320))
        screen.blit(font2.render("Press SPACE to continue", True, (255,255,0)), (320,380))


    # GAME OVER
    elif game_state == "gameover":
        screen.blit(font1.render(f"{winner} WINS!", True, (0,200,0)), (350,330))
        screen.blit(font2.render("Press ESC to quit", True, WHITE), (380,400))


    # RESTART BUTTON (hide during placement/show_result states)
    if game_state not in ("placement_showboard_p1", "placement_done_p1",
                          "placement_showboard_p2", "placement_done_p2",
                          "show_result"):
        pygame.draw.rect(screen, (100,100,100), restart_button)
        screen.blit(font2.render("Restart", True, WHITE),
                    (restart_button.x+55, restart_button.y+10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
