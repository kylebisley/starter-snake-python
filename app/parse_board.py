import tile

SNAKE = -1
WALL_SPACE = 50
OPEN_SPACE = 25
SMALLER_SNAKE_FUTURE_HEAD = 15
OUR_HEAD = 10
LARGER_SNAKE_FUTURE_HEAD = 99


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

    return path_board


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

# TODO: change this to use passed in board object, can't use as is since Tile
# constructor changed
# def whatDoYourSnakeEyesSee(pathBoard, xPos, yPos):
#     """
#     This method finds the tiles it is possible to path to from any tiles
#     coordinates, and the tiles that form walls around/in this area,
#     then creates lists of this information.
#     Args:
#         pathBoard (array): integer representation of current board
#         xPos(int): the x coordinate of the tile we want to search from
#         yPos(int): the y coordinate of the tile we want to search from
#     OBJECT_ORIENTED_TODO: pass in a board object and tile object instead
#     Returns:
#         an list of two lists, the first contains all the Tile objects it is
#         possible and viable to path to, the second contains all Tile objects
#         that form the walls. Can compare these lists to lists of all food,
#         for example, to get just food we can path too.
#     OBJECT_ORIENTED_TODO: return board objects instead eventually maybe
#     """
#     board_width = len(pathBoard[0])
#     board_height = len(pathBoard)
#     allBoardTiles = [[None for x in range(board_width)] for y in range(board_height)] 

#     startTile = tile.Tile(xPos, yPos, pathBoard[yPos][xPos])
#     startTile.visit()
#     #head = converted_data["you"]["body"][0]
#     newViableTiles = [startTile]
#     pathableTiles = []
#     blockingTiles = []


#     for x in pathBoard:
#         for y in x:
#             allBoardTiles[y][x] += tile.Tile(x, y, pathBoard[y][x])

#     while (len(newViableTiles) > 0):
#         #deal with the next tile we are examining
#         checkNext = newViableTiles.pop()
#         yHere = checkNext.getCoord[0]
#         xHere = checkNext.getCoord[1]

#         if (checkNext.getCost() < 1):
#             blockingTiles.append(checkNext)
#             continue #go to next iteration if it's a wall, we don't care about it after this step
#         else:
#             pathableTiles.append(checkNext)

#         #at this point, look in each cardinal direction, and if the tile there exists, and has not been visited, append to newViableTiles
#         if((yHere > 0) and not allBoardTiles[yHere - 1][xHere].getVisited()):
#             newViableTiles.append(allBoardTiles[yHere - 1][xHere])
#             allBoardTiles[yHere - 1][xHere].visit()
#         if((yHere < board_height - 1) and not allBoardTiles[yHere + 1][xHere].getVisited()):
#             newViableTiles.append(allBoardTiles[yHere + 1][xHere])
#             allBoardTiles[yHere + 1][xHere].visit()
#
#         if((xHere > 0) and not allBoardTiles[yHere][xHere - 1].getVisited()):
#             newViableTiles.append(allBoardTiles[yHere][xHere - 1])
#             allBoardTiles[yHere][xHere - 1].visit()
#         if((xHere < board_width - 1) and not allBoardTiles[yHere][xHere + 1].getVisited()):
#             newViableTiles.append(allBoardTiles[yHere][xHere + 1])
#             allBoardTiles[yHere][xHere + 1].visit()

#     return [pathableTiles, blockingTiles]


def turnedAround(walls_around, converted_data):
    tail = converted_data["you"]["body"][len(converted_data["you"]["body"])-1]
    index_counter = 1
    for z in walls_around:
        if z is tail:
            return tail
    else:
        while tail != walls_around[len(walls_around)-1]:
            tail = converted_data["you"]["body"][len(
                converted_data["you"]["body"]) - index_counter]
            index_counter -= 1
        return tail
