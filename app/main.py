import json
import os
import bottle
import parse_board
import board
import tests

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

    dima_board = parse_board.board_to_array(converted_data)
    pathable_board = parse_board.int_board(converted_data)
    board_object = board.Board(converted_data, pathable_board, dima_board)

    # Json data is printed for debug help
    print(json.dumps(data))

    # debug board object boards
    board_object.print_int_board()
    board_object.print_dima_board()

    direction = cardinal(converted_data, target_selection(converted_data,
                                                          board_object))

    response = {"move": direction, "shout": board_object.food_string()}
    return response


@bottle.post('/end')
def end():
    data = bottle.request.json

    """
    TODO: If your snake AI was stateful,
        clean up any stateful objects here.
    """
    print(json.dumps(data))

    return end_response()


def sum_path_weight(path, path_board):
    """
    Receives path, returns cost of the nodes of the path.
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
        if path_board[step[1]][step[0]] <= 0:
            return
        weight = weight + path_board[step[1]][step[0]]
    return weight


def navigate(converted_data, path_board, target):
    """
    This method generates A* path to navigate to the target
    Args:
        target (list): [x,y] format
        converted_data (dict): parsed json data dump
        path_board (array): integer representation of current board
    Returns:
        path(list): path to target
    """
    matrix = path_board
    grid = Grid(matrix=matrix)

    start_tile = grid.node(converted_data["you"]["body"][0]['x'],
                           converted_data["you"]["body"][0]['y'])
    end_tile = grid.node(target[0], target[1])

    finder = AStarFinder()
    path, runs = finder.find_path(start_tile, end_tile, grid)
    return path


def cardinal(converted_data, path):
    """
    Translates first move on path to cardinal direction.

    Args:
        converted_data (dict): python readable json
        path (list): path from a*
    Return:
        direction (str): cardinal direction as string
    """
    # if x values are same check y values for direction
    if converted_data["you"]["body"][0]['x'] == path[1][0]:
        if (converted_data["you"]["body"][0]['y']) < (path[1][1]):
            direction = 'down'
        else:
            direction = 'up'
    # x values are different check them for direction
    else:
        if (converted_data["you"]["body"][0]['x']) < (path[1][0]):
            direction = 'right'
        else:
            direction = 'left'
    return direction


def heads_up(converted_data, board):
    '''
    Creates list of look_from_here objects based on targets pathable
    neighbours that are not our head
    Args:
        converted_data (dict): python readable json
        board(board object): representation of board
    Returns:
        possible_futures(list): collection of objects returned from
        look_from_here
    '''
    head = board.get_tile_at(converted_data["you"]["body"][0]['x'],
                             converted_data["you"]["body"][0]['y'])
    neighbours = board.find_neighbours(head)

    # remove head and unpathable neighbours from our list stack
    for i in xrange(len(neighbours) - 1, -1, -1):
        if ((neighbours[i].get_cost() < 1 or
             neighbours[i].get_cost() == 10)):
            del neighbours[i]

    possible_futures = []
    for neighbour in neighbours:
        possible_futures.append(board.look_from_here(neighbour,
                                                     converted_data))
    return possible_futures


def target_selection(converted_data, board):
    '''
    Can eventually be call list for logic to deal with oh shit situations.
    Returns a path to closest food or tail given possible_futures.
    Args:
        converted_data (dict): python readable json
        board(board object): representation of board
    Variables: (explination of some variables that might not be clear)
        possible_futures (list): [[][],] collection of tile_lists
        tile_list (list):[][] collection of pathable tiles,
                              collection of walls around them
        options (list):[][] collection of weights of paths and paths to food
        weigth_path (list):[][] same as options

    Returns:
        path(list): path to target
    '''
    possible_futures = heads_up(converted_data, board)
    possible_futures = chasing_tail(possible_futures, converted_data, board)
    options = buffet(possible_futures, converted_data, board)

    shortest_path = "Unassigned"

    if len(options) > 0:
        shortest_path = shortest_option(options)
    # No safe food so path to tail
    if (shortest_path == "Unassigned"):
        return path_to_tail(converted_data, board)

    return shortest_path[1]


def buffet(possible_futures, converted_data, board):
    '''
    Returns a list of all routes to food from tiles adjcent to our head
    and their weights
    Args:
        possible_futures (list): [[][],] collection of tile_lists
        tile_list (list):[][] collection of pathable tiles,
                              collection of walls around them
    Returns:
        options (list):[][] collection of weights of paths and paths to food
    '''
    food_tiles = board.get_food_tiles()
    options = []
    nacho(converted_data, board)
    for future in possible_futures:
        for food in food_tiles:
            if food in future[0]:
                target = [food.get_x(), food.get_y()]
                path = navigate(converted_data, board.get_path_board(), target)
                weight = [sum_path_weight(path, board.get_path_board()), path]
                options.append(weight)
    return options


def nacho(converted_data, board):
    my_size = len(converted_data["you"]["body"])
    my_id = converted_data["you"]["id"]
    big_snakes_heads = []

    for snake in converted_data["board"]["snakes"]:
        if (snake["id"] != my_id) and (len(snake["body"]) >= my_size):
            x = snake["body"][0]["x"]
            y = snake["body"][0]["y"]
            big_snakes_heads.append(board.get_tile_at(x, y))
            print("head at x:" + str(x) + ", y:" + str(y))
    # if big snakes_heads > 0
    neighbours_plate = []
    for head in big_snakes_heads:
        adjacents = board.find_neighbours(head)
        for tile in adjacents:
            neighbours_plate.append(tile) # add all the parts of a list I believe there is a better function for this in the API
    print("neighbours_plate after adjacents 1")
    print(len(neighbours_plate))
    for tile in neighbours_plate:
        adjacents = board.find_neighbours(tile)
        for once_removed in adjacents:
            if once_removed not in neighbours_plate:
                neighbours_plate.append(once_removed)
    print("neighbours_plate after adjacents 2")
    print(len(neighbours_plate))
    tests.print_other_plates(neighbours_plate, converted_data, board)


def shortest_option(options):
    '''
    Takes in list of paired weights and paths returns shortest.
    Args:
        options(list):[[weight][path],]
    Returns:
        shortest(list):[][]
        or
        shortest(string): "Unassigned" if something went wrong
    '''
    shortest = "Unassigned"
    # option[0] is weight of path found in option[1]
    # sifting for the shortest path to food
    for option in options:
        if shortest == "Unassigned":
            shortest = option
        elif shortest != "Unassigned":
            if (option[0] < shortest[0]) and (option[0] != 0):
                shortest = option
    return shortest


def path_to_tail(converted_data, board):
    '''
    Returns A* path to tail including tomfoolery around tail weight.
    NEEDS better fix to not eat tail if there is another safe option.
        Args:
        converted_data (dict): python readable json
        board(board object): representation of board
    Returns:
        path(list): path to tail
    '''
    x = converted_data["you"]["body"][-1]['x']
    y = converted_data["you"]["body"][-1]['y']

    print("No food. Must eat tail!")

    # save tile value
    tail_tile_value = board.get_tile_at(x, y).get_cost()
    board.get_tile_at(x, y).set_cost(111)  # tail must be pathable for A*
    path_to_tail = navigate(converted_data, board.get_path_board(), [x, y])
    # replace tale value
    board.get_tile_at(x, y).set_cost(tail_tile_value)

    return path_to_tail


def chasing_tail(possible_futures, converted_data, board):
    '''
    Prunes possible_futures without out tail in them.
    Args:
        possible_futures(list): collection of objects returned from
            look_from_here
        converted_data (dict): python readable json
        board(board object): representation of board
    Returns:
        path(list): path to target
    '''
    tail = board.get_tile_at(converted_data["you"]["body"][-1]['x'],
                             converted_data["you"]["body"][-1]['y'])
    for i in xrange(len(possible_futures) - 1, -1, -1):
        possible = possible_futures[i][0]
        walls = possible_futures[i][1]
        if (tail not in possible) and (tail not in walls):
            del possible_futures[i]
            continue
    print(len(possible_futures))
    return possible_futures


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '127.0.0.1'),
        port=os.getenv('PORT', '8080'),
        debug=os.getenv('DEBUG', True)
    )
