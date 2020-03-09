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
    # debug display boards
    # parse_board.display(dima_board, pathable_board)
    # debug board object boards
    board_object.print_int_board()
    board_object.print_dima_board()

    # switch from modifying board state to interpreting it in pathing
    pathable_board_obj = board_object.get_path_board()

    # direction = cardinal(converted_data,
    #                      get_min_path_to_food(converted_data,
    #                                           pathable_board_obj))
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


def get_min_path_to_food(converted_data, path_board):
    """
    Checks for lightest path to food.
    Args:
        converted_data (dict): converted python representation of current game
                                snapshot
        path_board (array.py): integer representation of board
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
        if shortest_path == "Unassigned" and (len(new_path) != 0):
            shortest_path = new_path
        elif shortest_path != "Unassigned":
            # Line below too long. Broken into 3 pieces for clarity
            if (sum_path_weight(new_path, path_board) <
                    sum_path_weight(shortest_path, path_board)
                    and (len(new_path) != 0)):
                shortest_path = new_path
# --------------------------------------------------------------------------------------------
        sum_path_weight(new_path, path_board) # fairly sure this can be removed in a last pass
    return shortest_path


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
    print("***************************************")
    print(len(possible_futures))
    print("***************************************")
    return possible_futures


def target_selection(converted_data, board):
    '''
    Can eventually be call list for logic to deal with oh shit situations.
    Returns a path to cloest food or tail given possible_futures.
    Args:
        converted_data (dict): python readable json
        board(board object): representation of board
    Returns:
        path(list): path to target
    '''
    possible_futures = heads_up(converted_data, board)
    possible_futures = chasing_tail(possible_futures, converted_data, board)
    i = 0
    for tile_lists in possible_futures:
        print("**the view from here**" + str(i))
        tests.print_look_from_object(tile_lists, converted_data, board)
        i = i + 1
    food_tiles = board.get_food_tiles()
    options = []
    for future in possible_futures:
        for food in food_tiles:
            if food not in future[0]:
                del food
            else:
                target = [food.get_x(), food.get_y()]
                path = navigate(converted_data, board.get_path_board(), target)
                temp = [sum_path_weight(path, board.get_path_board()), path]
                options.append(temp)

    if len(options) == 0:
        tail = board.get_tile_at(converted_data["you"]["body"][-1]['x'],
                                 converted_data["you"]["body"][-1]['y'])
        return navigate(converted_data, board.get_path_board(), tail)
    else:
        shortest_path = "Unassigned"
        # option[0] is lenght of path found in option[1]
        for option in options:
            if shortest_path == "Unassigned" and (option[0] != 0): # might be able to remove this later
                shortest_path = option[1]
                # tests.print()
            elif shortest_path != "Unassigned":
                # Line below too long. Broken into 3 pieces for clarity
                if (option[0]) < len(shortest_path) and (option[0] != 0):
                    shortest_path = option[1]
    return shortest_path


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
