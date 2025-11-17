import random

def can_place(board,row,column,size,direction,gridsize=10):
    if direction =='H':
        if column +size >gridsize:
            return False
        return all(board[row][column+i]==0 for i in range(size))
    elif direction=='V':
        if row+size>gridsize:
            return false
        return all(board[row+i][column]==0 for i in range(size))

    #all checks if every elemtent in iterable is true
def place_ship (board,row,column,size,direction):
    cells=[]
    if direction =='H':
        for i in range(size):
            board[row][column+i]=1  #putting the ship horizontolly across i columns
            cells.append((row,column+i))  #appending the exact row and column of ship cell to cells list
    else:
        for i in range(size):
            board[row+i][column]=1   #same as above, but vertically
            cells.append((row+i,column))

    return cells
def auto_place_with_records(board,ship_list,gridsize=10):
    from shipnew import SHIP_TYPES_LIST, create_ship_record
    for name,size in SHIP_TYPES_LIST:
        placed=False
        attempt_limit=2000        #it can attempt a max of 2000 times to place a ship
        while not placed and attempt_limit>0:
            attempt_limit-=1
            orientation=random.choice (["H","V"])
            if orientation=="H":
                row=random.randint(0,gridsize-1)
                col=random.randint(0,gridsize-size)
                if can_place(board,row,col,size,"H",gridsize):  #checks if it can place at the random row n colum
                    cells=place_ship(board,row,col,size,"H")    #places ship and returns cells occupied
                    ship_list.append(create_ship_record(name,cells))  
                    placed=True
            else:
                row=random.randint(0,gridsize-size)
                col=random.randint(0,gridsize-1)
                if can_place(board,row,col,size,"V",gridsize):
                    cells=place_ship(board,row,col,size,"V")
                    ship_list.append(create_ship_record(name,cells))
                    placed=True
def check_win(board):
    return not any(1 in row for row in board)  #checking if 1(ship present but not hit) is present in any row
                                               #any checks if at least one element in iterable is true
                                               #not any means all elements are false(no ship present)