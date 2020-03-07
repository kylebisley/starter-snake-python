import tile
import board as b
# import re

SNAKE = -1
WALL_SPACE = 50
OPEN_SPACE = 25
SMALLER_SNAKE_FUTURE_HEAD = 15
OUR_HEAD = 10
LARGER_SNAKE_FUTURE_HEAD = 99
TESTER = 11


def int_board(converted_data):
    """
    Call list of functions that modify and build the path_board
    Args: 
        converted_data (dict): Converted json

    Returns: 
        A* friendly version of the game-board
    """
    # make path_board
    path_board = set_edge(converted_data)

    # pass by reference modify it
    set_snake_values(converted_data, path_board)
    bully_pathing(converted_data, path_board)
    coward_pathing(converted_data, path_board)

    remove_tails(converted_data, path_board)

    return path_board


def remove_tails(converted_data, path_board):
    """
    """
    print("converted_data['turn']")
    print(converted_data['turn'])
    if converted_data["turn"] == 0:
        print("escape")
        return
    food = converted_data["you"]["shout"].split("/")
    food = [str(x) for x in food]
    food.pop()
    print("food")
    print(food)
    print("len(food)")
    print(len(food))
    growers = []
    if len(food) > 0:
        for location in food:
            xy = location.split(",")
            x = int(xy[0])
            y = int(xy[1])
            print("food was at " + str(x) + ", " + str(y))
            print("value of tile")
            print(int(path_board[y][x]))
            if (path_board[y][x] <= 0) or (path_board[y][x] != 10):
                snake_id = snake_id_from_tile(x, y, converted_data)
                print("snake_id in remove tails")
                print(snake_id)
                growers.append(snake_id)
                print("a snake just ate")
                print("growers")
                print(growers)
    remove_hungry_tails(path_board, growers, converted_data)


def remove_hungry_tails(path_board, growers, converted_data):
    print("removing hungry tails")
    print("growers size")
    print(len(growers))
    print("growers")
    print(growers)
    for snake in converted_data["board"]["snakes"]:
        print("snake['id']")
        print(snake["id"])
        if snake["id"] not in growers:
            print(snake["id"] + 'not in growers')
            print("path_board[snake['body'][-1]['y']][snake['body'][-1]['x']]")
            print(path_board[snake["body"][-1]["y"]][snake["body"][-1]["x"]])
            path_board[snake["body"][-1]["y"]][snake["body"][-1]["x"]] = TESTER
            print(path_board[snake["body"][-1]["y"]][snake["body"][-1]["x"]])


def snake_id_from_tile(x, y, converted_data):
    for snake in converted_data["board"]["snakes"]:
        if x == snake["body"][0]["x"] and y == snake["body"][0]["y"]:
            print("food eatten at " + str(x) + ", " + str(y))
            return snake["id"]

            # return tail
            # return {"x": snake["body"][-1]["x"], "y": snake["body"][-1]["y"]}
            # get snake id from json
            # set tail of snake[id] to 25


def set_snake_values(converted_data, board):
    """
    Replaces values on pathable board that correspond with snake locations
    with values for snake bodies
    Args:
        converted_data (dict): Converted JSON data
        board (list): integer representation of the board

    Returns:
        A_Star friendly version of the game-board.

    """

    # pertaining to our own body
    me = converted_data["you"]["id"]

    for segment in converted_data["you"]["body"]:
        if segment == converted_data["you"]["body"][0]:
            x = segment['x']
            y = segment['y']
            board[y][x] = OUR_HEAD
        else:
            x = segment['x']
            y = segment['y']
            board[y][x] = SNAKE

    # other snakes
    for snake in converted_data["board"]["snakes"]:
        name = snake["id"]
        for segment in snake["body"]:
            if name != me:
                if segment == snake["body"][0]:
                    x = segment['x']
                    y = segment['y']
                    board[y][x] = SNAKE
                else:
                    x = segment['x']
                    y = segment['y']
                    board[y][x] = SNAKE


def set_edge(data_dump):
    """
    Creates path-able board and sets edge of game-map to the value 'WALL_SPACE'
    Args:
        data_dump (dict): Converted JSON data

    Returns:
        Game board with the edges initialised to '10'
    """
    board_width = data_dump["board"]["width"]
    board_height = data_dump["board"]["height"]
    board = [[1 for x in range(board_width)] for y in range(board_height)]
    for x in range(board_width):
        for y in range(board_height):
            # Bottom of board
            if y == data_dump["board"]["height"] - 1:
                board[y][x] = WALL_SPACE
            # Top of Board
            elif y == 0:
                board[y][x] = WALL_SPACE
            # Right side of board
            elif x == data_dump["board"]["width"] - 1:
                board[y][x] = WALL_SPACE
            # Left side of board
            elif x == 0:
                board[y][x] = WALL_SPACE
            # Anything Else
            else:
                board[y][x] = OPEN_SPACE
    return board


def bully_pathing(converted_data, path_board):
    """
    Finds Snakes that are smaller than us and assigns the area around their
    head with the SMALLER_SNAKE_FUTURE_HEAD

    May need logical update for snake bodies but it should be fine

    Args:
        path_board (list): Path from A*
        converted_data (dict): python readable version of json
    Return:
        updated board (list) with potentially new values around smaller snakes
        heads
    """
    snake_id = converted_data["you"]["id"]
    # other snakes heads will be assigned xy
    for snake in converted_data["board"]["snakes"]:
        name = snake["id"]
        for segment in snake["body"]:
            if ((str(name) != str(snake_id))
                    and (len(snake["body"]) < len(converted_data["you"]["body"]))):

                if segment == snake["body"][0]:
                    x = segment['x']
                    y = segment['y']
                    if converted_data['board']['width'] > x > 0:
                        if path_board[y][x + 1] != -1:
                            path_board[y][x+1] = SMALLER_SNAKE_FUTURE_HEAD
                        if path_board[y][x - 1] != -1:
                            path_board[y][x-1] = SMALLER_SNAKE_FUTURE_HEAD
                    if converted_data['board']['width'] > y > 0:
                        if -1 != path_board[y + 1][x]:
                            path_board[y+1][x] = SMALLER_SNAKE_FUTURE_HEAD
                        if path_board[y - 1][x] != -1:
                            path_board[y-1][x] = SMALLER_SNAKE_FUTURE_HEAD


def coward_pathing(converted_data, path_board):
    """
    Finds Snakes that are LARGER than us and assigns
    the area around their head with the LARGER_Snake_Future_Head

    May need logical update for snake bodies but it should be fine

    Args:
        converted_data (dict): python readable version of json
        path_board (list): path from a*

    Return:
        updated board (list) with potentially new values
        around LARGER snakes heads
    """
    me = converted_data["you"]["id"]
    # other snakes heads will be assigned xy
    for snake in converted_data["board"]["snakes"]:
        name = snake["id"]
        for segment in snake["body"]:
            if ((str(name) != str(me)) and
                    (len(snake["body"]) >= len(converted_data["you"]["body"]))):
                if segment == snake["body"][0]:
                    x = segment['x']
                    y = segment['y']
                    if converted_data['board']['width']-1 > x >= 0:
                        if path_board[y][x + 1] != -1:
                            path_board[y][x+1] = LARGER_SNAKE_FUTURE_HEAD
                        if path_board[y][x - 1] != -1:
                            path_board[y][x-1] = LARGER_SNAKE_FUTURE_HEAD
                    if converted_data['board']['height']-1 > y >= 0:
                        if path_board[y + 1][x] != -1:
                            path_board[y+1][x] = LARGER_SNAKE_FUTURE_HEAD
                        if path_board[y - 1][x] != -1:
                            path_board[y-1][x] = LARGER_SNAKE_FUTURE_HEAD


def board_to_array(data_dump):
    """
    Converts converted JSON data from battle-snake engine to a list
    Args:
        data_dump (dict): Converted JSON data

    Returns:
        2D list of game board.
    """
    board_width = data_dump["board"]["width"]
    board_height = data_dump["board"]["height"]
    board = [[0 for x in range(board_width)] for y in range(board_height)]
    # label spaces as food
    for z in data_dump["board"]["food"]:
        x = z['x']
        y = z['y']
        board[y][x] = 'F'
    # finding your body
    me = data_dump["you"]["id"]
    for z in data_dump["you"]["body"]:
        if z == data_dump["you"]["body"][0]:
            x = z['x']
            y = z['y']
            board[y][x] = 'H'
        else:
            x = z['x']
            y = z['y']
            board[y][x] = 'S'
    # to find other snakes
    for z in data_dump["board"]["snakes"]:
        name = z["id"]
        for a in z["body"]:
            if name != me:
                if a == z["body"][0]:
                    x = a['x']
                    y = a['y']
                    board[y][x] = 'E'
                else:
                    x = a['x']
                    y = a['y']
                    board[y][x] = 'S'
    return board


def display(converted_board, integer_board):
    for x in integer_board:
        for y in x:
            print(str(y) + " "),
        print()
    print()
    for x in converted_board:
        for y in x:
            print(str(y) + " "),
        print()


# def look_from_here(the_board, the_tile, j_data):
#     '''
#     finds all tiles reachable on a board from a given tile, and the walls surrounding them, treats our head as
#     a wall
#     Args:
#         the_board (board): a board object
#         the_tile (tile): the tile object we want to search from
#         j_data (dict): the converted json data initially given to us
#     Returns:
#         a list of two 1d lists, the first is all the tiles that are possible to path to from the passed in tile,
#         the second is a list of tiles that form a wall around the pathable area
#     '''
#     tile_is_head = True
#     head_cost = the_tile.get_cost()
#     head = j_data["you"]["body"][0]
#     if not ((the_tile.get_x() == head["x"]) and (the_tile.get_y() == head["y"])):
#         tile_is_head = False
#         the_board.get_tile_at(head["x"], head["y"]).set_cost(-1)

#     new_viable_tiles = [the_tile]
#     blocking_tiles = []
#     pathable_tiles = []
    
#     while (len(new_viable_tiles) > 0):
#         #deal with the next tile we are examining
#         check_next = new_viable_tiles.pop()

#         if (check_next.getCost() < 1):
#             blocking_tiles.append(check_next)
#             continue  # go to next iteration if it's a wall, we don't care about it after this step
#         else:
#             pathable_tiles.append(check_next)

#         neighbours = the_board.find_neighbours(check_next)

#         for t in neighbours:
#             if (not t.get_visited()):
#                 new_viable_tiles.append(t)
#                 t.set_visited(True)
        
#     for x in range(the_board.get_width()):
#         for y in range(the_board.get_height()):
#             the_board.get_tile_at(x, y).set_visited(False)

#     if not tile_is_head:
#         the_board.get_tile_at(head["x"], head["y"]).set_cost(head_cost)
    
#     return [pathable_tiles, blocking_tiles]
