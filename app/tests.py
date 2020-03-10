def print_look_from(board_object, converted_data):
    '''
    prints the output of look_from_here starting at our head, "0" means pathable, "X" means unpathable
    and "-" means unreachable, best used with dima board for info like food locations and our head location
    Arguments:
        board_object (Board): the full board object
        converted_data (dict): Converted JSON data
    '''
    head_tile = board_object.get_tile_at(converted_data["you"]["body"][0]["x"],
                                         converted_data["you"]["body"][0]["y"])
    tileLists = board_object.look_from_here(head_tile, converted_data)

    look_board_width = converted_data["board"]["width"]
    look_board_height = converted_data["board"]["height"]
    look_board = [["-" for x in range(look_board_width)] for y in range(look_board_height)]

    for z in tileLists[0]:
        x = z.get_x()
        y = z.get_y()
        look_board[y][x] = '0'
    for z in tileLists[1]:
        x = z.get_x()
        y = z.get_y()
        look_board[y][x] = 'X'

    print "look_from output starting from head:"
    for x in look_board:
        for y in x:
            print str(y) + " ",
        print ""
    print ""


def print_look_from_object(tileLists, converted_data, board_object):
    '''
    prints the output of look_from_here_object
    "0" means pathable, "X" means unpathable
    and "-" means unreachable, best used with dima board for info like food locations and our head location
    Arguments:
        board_object (Board): the full board object
        converted_data (dict): Converted JSON data
    '''
    head_tile = board_object.get_tile_at(converted_data["you"]["body"][0]["x"],
                                         converted_data["you"]["body"][0]["y"])

    look_board_width = converted_data["board"]["width"]
    look_board_height = converted_data["board"]["height"]
    look_board = [["-" for x in range(look_board_width)] for y in range(look_board_height)]
    
    for tile in tileLists[0]:
        x = tile.get_x()
        y = tile.get_y()
        look_board[y][x] = '0'
    for tile in tileLists[1]:
        x = tile.get_x()
        y = tile.get_y()
        look_board[y][x] = 'X'

    print "look_from output"
    for x in look_board:
        for y in x:
            print str(y) + " ",
        print ""
    print ""

    # # Debug for seeing the choices the snake is making. Leaving it in for now
    # # 888888888888888888888888888888888888888888888888888888888888888888
    # i = 0
    # for tile_lists in possible_futures:
    #     print("**the view from here**" + str(i))
    #     tests.print_look_from_object(tile_lists, converted_data, board)
    #     i = i + 1
    # # 888888888888888888888888888888888888888888888888888888888888888888
