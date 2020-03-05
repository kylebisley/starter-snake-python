import json
import os
import random
import bottle
import math

from api import ping_response, start_response, move_response, end_response
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

SNAKE = -1
WALL_SPACE = 10
OPEN_SPACE = 5
SMALLER_SNAKE_FUTURE_HEAD = 3
ourHead = 1

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

    color = "#00FF00"

    return start_response(color)


@bottle.post('/move')
def move():
    data = bottle.request.json
    # Converts data to be parsable
    converted_data = json.loads(json.dumps(data))
    game_id = converted_data["game"]["id"]

    board = boardToArray(converted_data)
    for x in board:
        for y in x:
            print(str(y) + " "),
        print()

    #closeFood = getNearestFood(converted_data)
    pathableBoard = setBoardValues(converted_data)
    
    # for x in pathableBoard:
    #     for y in x:
    #         print(str(y) + " "),
    #     print()
    #Json data is printed for debug help
    print(json.dumps(data))
    directions = cardinal(converted_data, getMinPathToFood(converted_data, pathableBoard))

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
    #label spaces as food
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
    Sets edge of gamemap to the value '2'
    Args:
        dataDump (list): Converted JSON data

    Returns:
        Gameboard with the edges initialised to '2'

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
    Checks for shortest path to food. 
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
        else:
            # good place to begin the logic for when we can't path to food
            print("NO FOOD IN IMMEDIATE FUTURE BETTER KILL MYSELF")
            continue
        if (len(newPath) < len(shortestPath) & (len(newPath) != 0)):
            shortestPath = newPath
    return shortestPath

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

    start = grid.node(converted_data["you"]["body"][0]['x'],converted_data["you"]["body"][0]['y'])
    end = grid.node(food[0],food[1]) 

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

    if (converted_data["you"]["body"][0]['x'] == path[1][0]): #if x values are same check y values for direction
        if ((converted_data["you"]["body"][0]['y']) < (path[1][1])):
            direction = ['down']
        else:
            direction = ['up']
    else: #x values are different check them for direction
        if((converted_data["you"]["body"][0]['x']) < (path[1][0])):
            direction = ['right']
        else:
            direction = ['left']
    return direction


class Tile():
    """
    TODO: Add functionality for what kind of tile it is, ie: snakeBody, ourHead, ourBody, food, empty tile
    This class exists so that whatDoYourSnakeEyesSee only needs to look at the associated object of a tile to see if it's been
    visited, instead of searching the entire list of visited tiles every time. Should be usable for other things.

    Attributes:
        x (integer): the x coordinate, should line up with our other methods
        y (integer): the y coordinate etc
        visited (boolean): whether or not a tile has been visited, useful for some algorithms
        cost: the cost for a-star to travers a tile, can be used to determine if a tile is pathable

    Object Methods:
        getCoord(): int list, returns a list of the x position, then the y position
        getX(): int, returns the x coordinate of the tile
        getY(): int, returns the y coordinate of the tile
        visit(): void, sets visited to true
        getVisited(): boolean, returns current state of visited
        getCost(): int, returns cost attribute of the tile
    """
    #isFood = False

    def __init__(self, xCoord, yCoord, pathCost):
        self.x = xCoord
        self.y = yCoord
        self.visited = False
        self.cost = pathCost
    
    def getCoord(self):
        return [self.x, self.y]
    
    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def visit(self):
        self.visited = True

    def getVisited(self):
        return self.visited
    
    def getCost(self):
        return cost


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

    startTile = Tile(xPos, yPos, pathBoard[yPos][xPos]) 
    #head = converted_data["you"]["body"][0]
    newViableTiles = [startTile]
    pathableTiles = []
    blockingTiles = []


    for x in pathBoard:
        for y in x:
            allBoardTiles[y][x] += Tile(x, y, pathBoard[y][x])

    while (len(newViableTiles) > 0):
        #deal with the next tile we are examining
        checkNext = newViableTiles.pop()
        checkNext.visit()
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
        if((yHere < board_height - 1) and not allBoardTiles[yHere + 1][xHere].getVisited()):
            newViableTiles.append(allBoardTiles[yHere + 1][xHere])
        
        if((xHere > 0) and not allBoardTiles[yHere][xHere - 1].getVisited()):
            newViableTiles.append(allBoardTiles[yHere][xHere - 1])
        if((xHere < board_width - 1) and not allBoardTiles[yHere][xHere + 1].getVisited()):
            newViableTiles.append(allBoardTiles[yHere][xHere + 1])

    return [pathableTiles, blockingTiles]

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=os.getenv('DEBUG', True)
    )
