import json
import os
import random
import bottle
import math

from api import ping_response, start_response, move_response, end_response
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

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

    closeFood=getNearestFood(converted_data)
    pathableBoard = setBoardValues(converted_data)


    """
    TODO: Using the data from the endpoint request object, your
            snake AI must choose a direction to move in.
    """

    print(json.dumps(data))

    
    directions = navigate(converted_data,pathableBoard,closeFood)
    direction = random.choice(directions)

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
    board = setEdge(jData)
    
    # pertaining to our own body
    me = jData["you"]["id"]

    for z in jData["you"]["body"]:
        if (z == jData["you"]["body"][0]):
            x = z['x']
            y = z['y']
            board[y][x] = 1
        else:
            x = z['x']
            y = z['y']
            board[y][x] = -1
    # other snakes
    for z in jData["board"]["snakes"]:
        name = z["id"]

        for a in z["body"]:
            if (name != me):
                if (a == z["body"][0]):
                    x = a['x']
                    y = a['y']
                    board[y][x] = -1
                else:
                    x = a['x']
                    y = a['y']
                    board[y][x] = -1
    return board

def setEdge(dataDump):
    board_width = dataDump["board"]["width"]
    board_height = dataDump["board"]["height"]
    board = [[0 for x in range(board_width)] for y in range(board_height)] 
    for x in range(board_width):
        for y in range(board_height):
            if(y == dataDump["board"]["height"] - 1):
                board[y][x] = 2
            elif(y == 0):
                board[y][x] = 2
            elif (x == dataDump["board"]["width"] - 1):
                board[y][x] = 2
            elif(x == 0):
                board[y][x] = 2
            else:
                board[y][x] = 1
    return board


def getNearestFood(datadump):
    """
    Returns a x,y coordinates of the closest pathable food (as a crow flys)
    Args:
        datadump (json): converted python representation of current game snapshot
    Returns:
        Index of the food closest to head of snake. 
    """
    food_array = []
    distance_array = []
    snake_x = datadump["you"]["body"][0]['x']
    snake_y = datadump["you"]["body"][0]['y']
    for z in datadump["board"]["food"]:
        x = z['x']
        y = z['y']
        food_array.append([x, y])

    for i in food_array:
        move_distance = (abs((snake_x) - i[0])) + (abs((snake_y) - i[1]))
        distance_array.append(move_distance)

    index_of_smallest = distance_array.index(min(distance_array))
    print(food_array[index_of_smallest])
    return food_array[index_of_smallest]
  

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
    return cardinal(converted_data, path)

def cardinal(converted_data, path):
    """
    Translates first move on path to cardinal direction.
    Args:
        converted_data (json): python readable json
        path (list): path from a*
    Return:
        direction (single item list): cardinal direction as string 
    """
    
    #same logic but perhaps clearer this way? I'll leave it up to code review which one we choose. 
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


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=os.getenv('DEBUG', True)
    )
