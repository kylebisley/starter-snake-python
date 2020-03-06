import tile

SNAKE = -1
WALL_SPACE = 10
OPEN_SPACE = 5
SMALLER_SNAKE_FUTURE_HEAD = 3
ourHead = 1


def setBoardValues(jData):
    """
    Converts converted JSON data from the battlesnake engine, to an a_star
    friendly gameboard.
    Args:
        jData (list): Converted JSON data

    Returns:
        A_Star friendly version of the gameboard.

    """
    board = setEdge(jData)

    # pertaining to our own body
    me = jData["you"]["id"]

    for z in jData["you"]["body"]:
        if (z == jData["you"]["body"][0]):
            x = z['x']
            y = z['y']
            board[y][x] = ourHead
        else:
            x = z['x']
            y = z['y']
            board[y][x] = SNAKE

    # other snakes
    for z in jData["board"]["snakes"]:
        name = z["id"]
        for a in z["body"]:
            if (name != me):
                if (a == z["body"][0]):
                    x = a['x']
                    y = a['y']
                    board[y][x] = SNAKE
                else:
                    x = a['x']
                    y = a['y']
                    board[y][x] = SNAKE
    return board


def setEdge(dataDump):
    """
    Sets edge of gamemap to the value '10'
    Args:
        dataDump (list): Converted JSON data

    Returns:
        Gameboard with the edges initialised to '10'
    """
    board_width = dataDump["board"]["width"]
    board_height = dataDump["board"]["height"]
    board = [[1 for x in range(board_width)] for y in range(board_height)]
    for x in range(board_width):
        for y in range(board_height):
            # Bottom of board
            if(y == dataDump["board"]["height"] - 1):
                board[y][x] = WALL_SPACE
            # Top of Board
            elif(y == 0):
                board[y][x] = WALL_SPACE
            # Right side of board
            elif (x == dataDump["board"]["width"] - 1):
                board[y][x] = WALL_SPACE
            # Left side of board
            elif(x == 0):
                board[y][x] = WALL_SPACE
            # Anything Else
            else:
                board[y][x] = OPEN_SPACE
    return board


def bullyPathing(converted_data, pathBoard):
    """
    Finds Snakes that are smaller than us and assigns the area around their
    head with the Smaller_Snake_Future_Head

    May need logical update for snake bodies but it should be fine

    Args:
        converted_data (json): python readable json
        path (list): path from a*
    Return:
        updated board (list) with potentially new values around smaller snakes
        heads
    """
    snake_id = converted_data["you"]["id"]
    board = pathBoard
    # other snakes heads will be assigned xy
    for z in converted_data["board"]["snakes"]:
        name = z["id"]
        for a in z["body"]:
            if ((str(name) != str(snake_id)) and (len(z["body"]) < len(converted_data["you"]["body"]))):

                if (a == z["body"][0]):
                    x = a['x']
                    y = a['y']
                    if(x < converted_data['board']['width'] and x > 0):
                        if(pathBoard[y][x+1] != -1):
                            board[y][x+1] = 3
                        if(pathBoard[y][x-1] != -1):
                            board[y][x-1] = 3
                    if(y < converted_data['board']['width'] and y > 0):
                        if(pathBoard[y+1][x] != -1):
                            board[y+1][x] = 3
                        if(pathBoard[y-1][x] != -1):
                            board[y-1][x] = 3
    return board


def boardToArray(dataDump):
    """
    Converts converted JSON data from battlesnake engine to a list
    Args:
        dataDump (list): Converted JSON data

    Returns:
        2D list of game board.
    """
    board_width = dataDump["board"]["width"]
    board_height = dataDump["board"]["height"]
    board = [[0 for x in range(board_width)] for y in range(board_height)]
    # label spaces as food
    for z in dataDump["board"]["food"]:
        x = z['x']
        y = z['y']
        board[y][x] = 'F'
    # finding your body
    me = dataDump["you"]["id"]
    for z in dataDump["you"]["body"]:

        if (z == dataDump["you"]["body"][0]):
            x = z['x']
            y = z['y']
            board[y][x] = 'H'
        else:
            x = z['x']
            y = z['y']
            board[y][x] = 'S'
    # to find other snakes
    for z in dataDump["board"]["snakes"]:
        name = z["id"]
        for a in z["body"]:
            if (name != me):
                if (a == z["body"][0]):
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
    for x in converted_board:
        for y in x:
            print(str(y) + " "),
        print()

def whatDoYourSnakeEyesSee(pathBoard, xPos, yPos):
    """
    This method finds the tiles it is possible to path to from any tiles coordinates, and the tiles that form walls around/in this area,
    Then creates lists for this information.
    Args:
        pathBoard (array): integer representation of current board 
        xPos(int): the x coordinate of the tile we want to search from
        yPos(int): the y coordinate of the tile we want to search from
    OBJECT_ORIENTED_TODO: pass in a board object and tile object instead
    Returns:
        an list of two lists, the first contains all the Tile objects it is possible and viable to path to, the second 
        contains all Tile objects that form the walls. Can compare these lists to lists of all food, for example, to get
        just food we can path too.
    OBJECT_ORIENTED_TODO: return board objects instead eventually maybe
    """
    board_width = len(pathBoard[0])
    board_height = len(pathBoard)
    allBoardTiles = [[None for x in range(board_width)] for y in range(board_height)] 

    startTile = tile.Tile(xPos, yPos, pathBoard[yPos][xPos])
    startTile.visit()
    #head = converted_data["you"]["body"][0]
    newViableTiles = [startTile]
    pathableTiles = []
    blockingTiles = []


    for x in pathBoard:
        for y in x:
            allBoardTiles[y][x] += tile.Tile(x, y, pathBoard[y][x])

    while (len(newViableTiles) > 0):
        #deal with the next tile we are examining
        checkNext = newViableTiles.pop()
        yHere = checkNext.getCoord[0]
        xHere = checkNext.getCoord[1]

        if (checkNext.getCost() < 1):
            blockingTiles.append(checkNext)
            continue #go to next iteration if it's a wall, we don't care about it after this step
        else:
            pathableTiles.append(checkNext)
        
        #at this point, look in each cardinal direction, and if the tile there exists, and has not been visited, append to newViableTiles
        if((yHere > 0) and not allBoardTiles[yHere - 1][xHere].getVisited()):
            newViableTiles.append(allBoardTiles[yHere - 1][xHere])
            allBoardTiles[yHere - 1][xHere].visit()
        if((yHere < board_height - 1) and not allBoardTiles[yHere + 1][xHere].getVisited()):
            newViableTiles.append(allBoardTiles[yHere + 1][xHere])
            allBoardTiles[yHere + 1][xHere].visit()

        if((xHere > 0) and not allBoardTiles[yHere][xHere - 1].getVisited()):
            newViableTiles.append(allBoardTiles[yHere][xHere - 1])
            allBoardTiles[yHere][xHere - 1].visit()
        if((xHere < board_width - 1) and not allBoardTiles[yHere][xHere + 1].getVisited()):
            newViableTiles.append(allBoardTiles[yHere][xHere + 1])
            allBoardTiles[yHere][xHere + 1].visit()

    return [pathableTiles, blockingTiles]
