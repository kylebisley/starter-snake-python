class Tile():
    """
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