def process_attack(current_player, grid_y, grid_x, p1board, p2board, p1_attempts, p2_attempts, 
                   p1_ships, p2_ships, ship_status_p1, ship_status_p2, p1, p2, gridsize=10):
    """
    Process an attack and return the new current player and winner (if any).
    Returns: (new_current_player, winner)
    """
    from ship import update_ship_status_on_hit
    from board import check_win
    
    winner = None
    
    if current_player == "p1":
        if p2_attempts[grid_y][grid_x] == 0:
            if p2board[grid_y][grid_x] == 1:
                # register hit
                p2board[grid_y][grid_x] = 0
                p2_attempts[grid_y][grid_x] = 2
                # update ship records for p2
                update_ship_status_on_hit(p2_ships, ship_status_p2, (grid_y, grid_x))
                # keep turn on hit (optional)
            else:
                p2_attempts[grid_y][grid_x] = 3
                current_player = "p2"
    else:
        if p1_attempts[grid_y][grid_x] == 0:
            if p1board[grid_y][grid_x] == 1:
                p1board[grid_y][grid_x] = 0
                p1_attempts[grid_y][grid_x] = 2
                update_ship_status_on_hit(p1_ships, ship_status_p1, (grid_y, grid_x))
            else:
                p1_attempts[grid_y][grid_x] = 3
                current_player = "p1"
    
    if check_win(p1board):
        winner = p2
    elif check_win(p2board):
        winner = p1
    
    return current_player, winner


