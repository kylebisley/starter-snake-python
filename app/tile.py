class Tile():
    """
    Attributes:
        x (integer): the x coordinate, should line up with our other methods
        y (integer): the y coordinate etc
        visited (bool): whether or not a tile has been visited, useful for some algorithms
        cost: the cost for a-star to travers a tile, can be used to determine if a tile is pathable

    Object Methods:
        getCoord(): int list, returns a list of the x position, then the y position
        getX(): int, returns the x coordinate of the tile
        getY(): int, returns the y coordinate of the tile
        visit(): void, sets visited to true
        getVisited(): bool, returns current state of visited
        getCost(): int, returns cost attribute of the tile
    """

    def __init__(self, xCoord, yCoord, pathCost, is_food, debug_char):
        self._x = xCoord
        self._y = yCoord
        self.cost = pathCost
        self._is_food = is_food
        self._debug_char = debug_char
        self.visited = False


    #Getters and setters
    
    def get_x(self):
        return self._x

    def get_y(self):
        return self._y

    def set_visited(self, visit):
        self.visited = visit

    def get_visited(self):
        return self.visited
    
    def get_cost(self):
        return self.cost
    

    '''
    doesn't change "walls" and won't make a pathable tile unpathable
    '''
    def modify_cost(self, change_by):
        if self.getCost() < 1:
            return
        if self.getCost() + change_by < 1:
            self.cost = 1
            return
        self.cost += change_by

    def get_food(self):
        return self._is_food

    def get_char(self):
        return self._debug_char
