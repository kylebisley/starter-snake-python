class Tile:
    """
    Attributes:
        _x (integer): the x coordinate, should line up with our other methods
        _y (integer): the y coordinate etc
        visited (boolean): whether or not a tile has been visited, useful for some algorithms
        cost: the cost for a-star to travers a tile, can be used to determine if a tile is pathable

    Object Methods:
        get_coord(): int list, returns a list of the x position, then the y position
        get_x(): int, returns the x coordinate of the tile
        get_y(): int, returns the y coordinate of the tile
        visit(): void, sets visited to true
        get_visited(): boolean, returns current state of visited
        get_cost(): int, returns cost attribute of the tile
    """

    def __init__(self, x_coord, y_coord, path_cost, is_food, debug_char):
        self._x = x_coord
        self._y = y_coord
        self.cost = path_cost
        self._is_food = is_food
        self._debug_char = debug_char
        self.visited = False

    # Getters and setters
    
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

    #be careful with this one, make sure to set it back after you're done
    def set_cost(self, new_cost):
        self.cost = new_cost

    # doesn't change "walls" and won't make a pathable tile un-pathable

    def modify_cost(self, change_by):
        if self.get_cost() < 1:
            return
        if self.get_cost() + change_by < 1:
            self.cost = 1
            return
        self.cost += change_by

    def get_food(self):
        return self._is_food

    def get_char(self):
        return self._debug_char
