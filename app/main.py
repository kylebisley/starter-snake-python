import json
import os
import bottle

from api import ping_response, start_response, move_response, end_response
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

SNAKE = -1
WALL_SPACE = 50
OPEN_SPACE = 25
SMALLER_SNAKE_FUTURE_HEAD = 15
OUR_HEAD = 10
LARGER_SNAKE_FUTURE_HEAD = 50


@bottle.route('/')
def index():
    return '''
    Battlesnake documentation can be found at
        <a href="https://docs.battlesnake.com">https://docs.battlesnake.com</a>.
    '''


@bottle.route('/static/<path:path>')
def static(path):
    """
    Given a path, return the static file located relative
    to the static folder.

    This can be used to return the snake head URL in an API response.
    """
    return bottle.static_file(path, root='static/')


@bottle.post('/ping')
def ping():
    """
    A keep-alive endpoint used to prevent cloud application platforms,
    such as Heroku, from sleeping the application instance.
    """
    return ping_response()


@bottle.post('/start')
def start():
    data = bottle.request.json

    """
    TODO: If you intend to have a stateful snake AI,
            initialize your snake state here using the
            request's data if necessary.
    """
    print(json.dumps(data))

    color = "#ff5050"
    head = "shades"
    tail = "bolt"
    return start_response(color, head, tail)


@bottle.post('/move')
def move():
    data = bottle.request.json
    # Converts data to be parsable
    converted_data = json.loads(json.dumps(data))

    board = boardToArray(converted_data)

    # closeFood = getNearestFood(converted_data)
    pathable_board = setBoardValues(converted_data)

    # Json data is printed for debug help
    print(json.dumps(data))
    printBoard(board, pathable_board)
    directions = cardinal(converted_data, getMinPathToFood(converted_data, pathable_board))

    direction = directions[0]

    return move_response(direction)


@bottle.post('/end')
def end():
    data = bottle.request.json

    """
    TODO: If your snake AI was stateful,
        clean up any stateful objects here.
    """
    print(json.dumps(data))

    return end_response()


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


def setBoardValues(jData):
    """
    Converts converted JSON data from the battlesnake engine, to an a_star friendly gameboard.
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
            board[y][x] = OUR_HEAD
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
    board = bullyPathing(jData, board)
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


def getMinPathToFood(converted_data, pathBoard):
    """
    Checks for lightest path to food.
    Args:
        converted_data (json): converted python representation of current game snapshot
        pathBoard (int array): integer representation of board
    Returns:
        shortestPath (path): shortest path to food
        OR
        shortestPath (string): "Unassigned" when it can't path to food
    """
    shortestPath = "Unassigned"
    for food in converted_data["board"]["food"]:
        x = food['x']
        y = food['y']
        newPath = navigate(converted_data, pathBoard, [x, y])
        if (shortestPath == "Unassigned" and (len(newPath) != 0)):
            shortestPath = newPath
        elif (shortestPath != "Unassigned"):
            if (sumPathWeight(newPath, pathBoard) < sumPathWeight(shortestPath, pathBoard) and (len(newPath) != 0)):
                shortestPath = newPath

        sumPathWeight(newPath, pathBoard)
    return shortestPath


def sumPathWeight(path, pathBoard):
    """
    Recieves path, returns cost of the nodes of the path.
    Args:
        path (list): A* path
        pathBoard (list): int representation of board
    Returns:
        sum (int): sum of weights of tiles on path
    """
    if path == "Unassigned":
        return
    weight = 0
    for step in path:
        if (pathBoard[step[1]][step[0]] <= 0):
            return
        weight = weight + pathBoard[step[1]][step[0]]
    return weight


def navigate(converted_data, pathBoard, food):
    """
    This method generates the cardinal direction to navigate to the first element of path.
    Args:
        food (list): food locations in (x,y) format
        converted_data (json): parsed json data dump
        pathBoard (array): integer representation of current board
    Returns:
        output of cardinal function
    """
    matrix = pathBoard
    grid = Grid(matrix=matrix)

    start = grid.node(converted_data["you"]["body"][0]['x'], converted_data["you"]["body"][0]['y'])
    end = grid.node(food[0], food[1])

    finder = AStarFinder()
    path, runs = finder.find_path(start, end, grid)
    return path


def cardinal(converted_data, path):
    """
    Translates first move on path to cardinal direction.

    Args:
        converted_data (json): python readable json
        path (list): path from a*
    Return:
        direction (single item list): cardinal direction as string
    """

    if (converted_data["you"]["body"][0]['x'] == path[1][0]):  # if x values are same check y values for direction
        if ((converted_data["you"]["body"][0]['y']) < (path[1][1])):
            direction = ['down']
        else:
            direction = ['up']
    else:  # x values are different check them for direction
        if((converted_data["you"]["body"][0]['x']) < (path[1][0])):
            direction = ['right']
        else:
            direction = ['left']
    return direction


def bullyPathing(converted_data, pathBoard):
    """
    Finds Snakes that are smaller than us and assigns the area around their head with the Smaller_Snake_Future_Head

    May need logical update for snake bodies but it should be fine

    Args:
        converted_data (json): python readable json
        path (list): path from a*

    Return:
        updated board (list) with potentially new values around smaller snakes heads
    """
    me = converted_data["you"]["id"]
    board = pathBoard
    # other snakes heads will be assigned xy
    for z in converted_data["board"]["snakes"]:
        name = z["id"]
        for a in z["body"]:
            if ((str(name) != str(me)) and (len(z["body"]) < len(converted_data["you"]["body"]))):
                if (a == z["body"][0]):
                    x = a['x']
                    y = a['y']
                    if(x < converted_data['board']['width']-1 and x >=0):
                        if(pathBoard[y][x+1] != -1):
                            board[y][x+1] = SMALLER_SNAKE_FUTURE_HEAD
                        if(pathBoard[y][x-1] != -1):
                            board[y][x-1] = SMALLER_SNAKE_FUTURE_HEAD
                    if(y < converted_data['board']['height']-1 and y >=0):
                        if(pathBoard[y+1][x] != -1):
                            board[y+1][x] = SMALLER_SNAKE_FUTURE_HEAD
                            print("lower than head 15")
                        if(pathBoard[y-1][x] != -1):
                            board[y-1][x] = SMALLER_SNAKE_FUTURE_HEAD

    return board


def printBoard(converted_board, integer_board):
    for x in integer_board:
        for y in x:
            print(str(y) + " "),
        print()
    for x in converted_board:
        for y in x:
            print(str(y) + " "),
        print()


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '127.0.0.1'),
        port=os.getenv('PORT', '8080'),
        debug=os.getenv('DEBUG', True)
    )
