import json
import os
import bottle
import parseBoard
import tile

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

    color = "#ff5050"
    head = "shades"
    tail = "bolt"
    return start_response(color, head, tail)


@bottle.post('/move')
def move():
    data = bottle.request.json
    # Converts data to be parsable
    converted_data = json.loads(json.dumps(data))

    board = parseBoard.boardToArray(converted_data)
    pathable_board = parseBoard.int_board(converted_data)

    # Json data is printed for debug help
    print(json.dumps(data))
    # debug display boards
    parseBoard.display(board, pathable_board)

    directions = cardinal(converted_data,
                          getMinPathToFood(converted_data, pathable_board))
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


def getMinPathToFood(converted_data, path_board):
    """
    Checks for lightest path to food.
    Args:
        converted_data (dict): converted python representation of current game

                                snapshot
        path_board (list): integer representation of board
    Returns:
        shortest_path (list): shortest path to food
        OR
        shortest_path (str): "Unassigned" when it can't path to food
    """
    shortest_path = "Unassigned"
    for food in converted_data["board"]["food"]:
        x = food['x']
        y = food['y']
        new_path = navigate(converted_data, path_board, [x, y])
        if (shortest_path == "Unassigned" and (len(new_path) != 0)):
            shortest_path = new_path
        elif (shortest_path != "Unassigned"):
            # Line below too long. Broken into 3 pieces for clarity
            if (sumPathWeight(new_path, path_board) <
                    sumPathWeight(shortest_path, path_board)
                    and (len(new_path) != 0)):
                shortest_path = new_path

        sumPathWeight(new_path, path_board)
    return shortest_path


def sumPathWeight(path, path_board):
    """
    Recieves path, returns cost of the nodes of the path.
    Args:
        path (list): A* path
        path_board (list): int representation of board
    Returns:
        sum (int): sum of weights of tiles on path
    """
    if path == "Unassigned":
        return
    weight = 0
    for step in path:
        if (path_board[step[1]][step[0]] <= 0):
            return
        weight = weight + path_board[step[1]][step[0]]
    return weight


def navigate(converted_data, path_board, food):
    """
    This method generates the cardinal direction to navigate to the first
    element of path.
    Args:
        food (list): food locations in (x,y) format
        converted_data (dict): parsed json data dump
        path_board (array): integer representation of current board
    Returns:
        output of cardinal function
    """
    matrix = path_board
    grid = Grid(matrix=matrix)

    start = grid.node(converted_data["you"]["body"][0]['x'],
                      converted_data["you"]["body"][0]['y'])
    end = grid.node(food[0], food[1])

    finder = AStarFinder()
    path, runs = finder.find_path(start, end, grid)
    return path


def cardinal(converted_data, path):
    """
    Translates first move on path to cardinal direction.

    Args:
        converted_data (dict): python readable json
        path (list): path from a*
    Return:
        direction (single item list): cardinal direction as string
    """
    # if x values are same check y values for direction
    if (converted_data["you"]["body"][0]['x'] == path[1][0]):
        if ((converted_data["you"]["body"][0]['y']) < (path[1][1])):
            direction = ['down']
        else:
            direction = ['up']
    # x values are different check them for direction
    else:
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
        host=os.getenv('IP', '127.0.0.1'),
        port=os.getenv('PORT', '8080'),
        debug=os.getenv('DEBUG', True)
    )
