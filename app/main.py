import json
import os
import random
import bottle

from api import ping_response, start_response, move_response, end_response


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
    #Converts data to be parsable
    converted_data = json.loads(json.dumps(data))
    game_id = converted_data["game"]["id"]

    board = boardToArray(converted_data)
    for x in board:
        for y in x:
            print(str(y) + " "),
        print()        
    board = setBoardValues(board)
    
    
    print('After setBoardValues')
    for x in board:
        for y in x:
            print(str(y) + " "),
        print()
    """
    TODO: Using the data from the endpoint request object, your
            snake AI must choose a direction to move in.
    """
    print(json.dumps(data))

    directions = ['up', 'down', 'left', 'right']
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
    #finding your body
    me=dataDump["you"]["id"]
    for z in dataDump["you"]["body"]:
        
        if (z==dataDump["you"]["body"][0]):
            x = z['x']
            y = z['y']
            board[y][x] = 'H'
            headPosition=z
        else:
            x = z['x']
            y = z['y']
            board[y][x] = 'S'
    #to find other snakes
    for z in dataDump["board"]["snakes"]:
        name = z["id"]
        for a in z["body"]:
            if (name!=me):
                if (a == z["body"][0]):
                    x = a['x']
                    y = a['y']
                    board[y][x] = 'E'
                else:
                    x = a['x']
                    y = a['y']
                    board[y][x]='S'
    return board

def setBoardValues(board):
    
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == 'S' or board[i][j] == 'E' or board[i][j] == 'H':
                board[i][j] = None
            elif board[i][j] == 'F':
                board[i][j] = 0
            elif board[i][j] == 'E':
                board[i][j] = 0
    return board

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=os.getenv('DEBUG', True)
    )
