SHIP_TYPES_LIST=[("Carrier",5),("Battleship",4),("Cruiser",3),("Submarine",3),("Destroyer",2)]
SHIP_SIZES=[5,4,3,3,2]
def create_ship_record(name,cells):
    return {"name":name,"cells":cells,"hits":0}

def update_ship_status_on_hit(opponent_ships,ship_status_dict,hit_coord):
    for ship in opponent_ships:
        if hit_coord in ship["cells"]:
            ship["hits"]+=1
            if ship["hits"]==len(ship["cells"]):
                ship_status_dict[ship["name"]]=True
            return
def reset_ship_status(ship_status_dict):
    for k in ship_status_dict:
        ship_status_dict[k]=False   