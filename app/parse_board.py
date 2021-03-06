import tile
import board as b

SNAKE = -1
WALL_SPACE = 26
OPEN_SPACE = 15
SMALLER_SNAKE_FUTURE_HEAD = 11
OUR_HEAD = 10
LARGER_SNAKE_FUTURE_HEAD = 99
PATHABLE_TAIL = 12


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

    # after snakes fully deployed update board with projected tail positions
    if (converted_data["turn"] > 2):
        update_tails(converted_data, path_board)
    return path_board


def update_tails(converted_data, path_board):
    """
    Reads shout object for last turns moves and updates board to reflect if
    any snake heads occupy a tile that was previously occupied by food

    Args:
        converted_data (dict): python readable version of json
        path_board (list): int representation of the board for A*

    Returns:
        Nothing

    """
    food = converted_data["you"]["shout"].split("/")
    food = [str(x) for x in food]
    food.pop()  # kludge removes empty last element caused by parsing

    growers = []
    if len(food) > 0:
        for location in food:
            # get x,y with unicode converted
            xy = location.split(",")
            x = int(xy[0])
            y = int(xy[1])

            # if other snake or our head
            if (int(path_board[y][x]) <= 0) or (int(path_board[y][x]) == 10):
                snake_id = snake_id_from_XY(x, y, converted_data)
                snake_id.encode("utf-8")  # fixes unicode issue with parser
                growers.append(snake_id)
    remove_hungry_tails(path_board, growers, converted_data)


def remove_hungry_tails(path_board, growers, converted_data):
    """
    Edits the path_board to reflect if a snake ate this turn or not

    Args:
        converted_data (dict): python readable version of json
        path_board (list): int representation of the board for A*
        growers (list): string list of snake_ids whos tail will not move next
        turn
    Returns:
        Modifys path_board by reference.
    """
    for snake in converted_data["board"]["snakes"]:
        if snake["id"] not in growers:
            x = snake["body"][-1]["x"]
            y = snake["body"][-1]["y"]
            path_board[y][x] = PATHABLE_TAIL


def snake_id_from_XY(x, y, converted_data):
    """
    Returns snake_id from x, y integers.

    Args:
        x (int): x value of tile
        y (int): y value of tile
        converted_data (dict): python readable version of json

    Returns:
        snake["id"](unicode string): snake id
    """
    for snake in converted_data["board"]["snakes"]:
        if (x == snake["body"][0]["x"]) and (y == snake["body"][0]["y"]):
            return snake["id"]


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
                    and (len(snake["body"]) <
                         len(converted_data["you"]["body"]))):

                if segment == snake["body"][0]:
                    x = segment['x']
                    y = segment['y']
                    if (converted_data['board']['width'] - 1) > x > 0:
                        if path_board[y][x + 1] != -1:
                            path_board[y][x+1] = SMALLER_SNAKE_FUTURE_HEAD
                        if path_board[y][x - 1] != -1:
                            path_board[y][x-1] = SMALLER_SNAKE_FUTURE_HEAD
                    if (converted_data['board']['width'] - 1) > y > 0:
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
                    (len(snake["body"]) >=
                        len(converted_data["you"]["body"]))):
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
