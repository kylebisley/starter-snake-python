from tile import Tile
import tests


class Board:
    '''
    The Board object is responsible for generating and tracking all tiles.

    It is a 2d rectangular list, where the coordinates of the tile correspond
    to it's location, on creation it populates the board with tiles whose cost
    and character representation is passed in to the constructor.
    It is also responsible for allowing access to individual tiles, and
    any methods that return a subselection of the board
    Not responsible for logic or pathing.

    Attributes:
        _board_width  = width of the board object
        _board_height = height of the board object
        _the_board    = internal storage of Tiles
        food_tiles    = a list of tiles that are food

    Object Methods:
        find_neighbours(self, tile): takes in a tile, and outputs a list of
                                    all tiles that are adjacent to it
        get_path_board(self): generates a board representation of just
                                integer vals of tiles
        look_from_here(self, tile, j_data): finds all tiles it is possible
                                            to path to from a tile
    '''
    def __init__(self, j_data, path_board, char_board):
        self._board_width = j_data["board"]["width"]
        self._board_height = j_data["board"]["height"]
        self._the_board = []
        self.food_tiles = []
        self.nachos = []

        # this loop creates a new row, then creates the tile objects
        # belonging to that row and adds them to the list of food tiles if
        # they are food. At the end of the iteration adds that row to the board
        for y in range(self._board_height):

            new_row = []
            for x in range(self._board_width):

                # decide whether a tile is food
                is_food = False
                if char_board[y][x] == 'F':
                    is_food = True

                # build the tile
                new_tile = Tile(x,
                                y,
                                path_board[y][x],
                                is_food,
                                char_board[y][x])
                new_row.append(new_tile)

                if new_tile.get_food():
                    self.food_tiles.append(new_tile)

            self._the_board.append(new_row)
        self.nachos = self.nacho(j_data)

    # Getters and setters
    def get_tile_at(self, x, y):
        return self._the_board[y][x]

    def get_board_width(self):
        return self._board_width

    def get_board_height(self):
        return self._board_height

    def get_food_tiles(self):
        return self.food_tiles

    # string methods
    def food_string(self):
        """
        String representation of food locations
        Returns: (str) x,y/x,y
        """
        food_list = ""
        for food in self.food_tiles:
            food_list = (food_list +
                         str(food.get_x()) + "," +
                         str(food.get_y()) +
                         "/")
        return food_list

    def print_int_board(self):
        '''
        prints integer representation of the board, same as pathing values
        '''
        print "Integer Board, Width:", str(self.get_board_height()), "Height:", str(self.get_board_width())
        for y in range(self.get_board_height()):
            for x in range(self.get_board_width()):
                print str(self.get_tile_at(x, y).get_cost()) + " ",
            print ""
        print ""

    def print_dima_board(self):
        '''
        prints character representation of all tiles on board
        '''
        print "Dima board:"
        for y in range(self.get_board_height()):
            for x in range(self.get_board_width()):
                print str(self.get_tile_at(x, y).get_char()) + " ",
            print ""
        print ""

    def dab(self):
        raise NotImplementedError

    # Other methods

    # takes in a tile, and outputs a list of all tiles that are adjacent to it
    def find_neighbours(self, tile):
        '''
        finds the tiles adjacent to a given tile, safely avoids tiles that would be at a bad index

        Args:
            tile, (Tile): a tile object
        Return:
            a list of tile objects
        '''
        neighbours = []

        # look down
        if(tile.get_y() > 0):
            neighbours.append(self.get_tile_at(tile.get_x(), tile.get_y() - 1))

        # look up
        if(tile.get_y() < self.get_board_height() - 1):
            neighbours.append(self.get_tile_at(tile.get_x(), tile.get_y() + 1))

        # look left
        if(tile.get_x() > 0):
            neighbours.append(self.get_tile_at(tile.get_x() - 1, tile.get_y()))

        # look right
        if(tile.get_x() < self.get_board_width() - 1):
            neighbours.append(self.get_tile_at(tile.get_x() + 1, tile.get_y()))

        return neighbours

    def get_path_board(self):
        '''
        generates a board that is just the integer values of the costs on the board, same as what's generated
        by our int_board method
        '''
        path_board = []

        for y in range(self.get_board_height()):
            row = []

            for x in range(self.get_board_width()):
                row.append(self.get_tile_at(x, y).get_cost())

            path_board.append(row)

        return path_board

    def look_from_here(self, the_tile, j_data):
        '''
        finds all tiles reachable on the board from a passed in tile, and the walls
        surrounding them, treats our head as a wall unless we call it on our head
        Args:
            the_tile (tile): the tile object we want to search from
            j_data (dict): the converted json data initially given to us
        Returns:
            a list of two 1d lists, the first is all the tiles that are possible
            to path to from the passed in tile, the second is a list of tiles
            that form a wall around the pathable area
        '''
        tile_is_head = True
        head_cost = the_tile.get_cost()
        head = j_data["you"]["body"][0]
        # if we path from anywhere other than our head temporarily change cost
        if not ((the_tile.get_x() == head["x"]) and (the_tile.get_y() == head["y"])):
            tile_is_head = False
            self.get_tile_at(head["x"], head["y"]).set_cost(-1)

        new_viable_tiles = [the_tile]
        blocking_tiles = []
        pathable_tiles = []

        # this loop keeps finding tiles next to the ones we already know about
        # and if they are new and not walls will search from those new tiles
        while (len(new_viable_tiles) > 0):
            # deal with the next tile we are examining
            check_next = new_viable_tiles.pop()

            if (check_next.get_cost() < 1):
                blocking_tiles.append(check_next)
                continue  # go to next iteration if it's a wall
            else:
                pathable_tiles.append(check_next)

            neighbours = self.find_neighbours(check_next)

            for i in neighbours:
                if (not i.get_visited()):
                    new_viable_tiles.append(i)
                    i.set_visited(True)

        # Cleanup:
        # reset visited bool on entire board so that later calls can use it
        for x in range(self.get_board_width()):
            for y in range(self.get_board_height()):
                self.get_tile_at(x, y).set_visited(False)

        # reset our head's cost if we changed it
        if not tile_is_head:
            self.get_tile_at(head["x"], head["y"]).set_cost(head_cost)

        return [pathable_tiles, blocking_tiles]

    def nacho(self, converted_data):
        my_size = len(converted_data["you"]["body"])
        my_id = converted_data["you"]["id"]
        big_snakes_heads = []

        for snake in converted_data["board"]["snakes"]:
            if (snake["id"] != my_id) and (len(snake["body"]) >= my_size):
                print("len(snake['body']")
                print(len(snake["body"]))
                print("my_size")
                print(my_size)
                x = snake["body"][0]["x"]
                y = snake["body"][0]["y"]
                big_snakes_heads.append(self.get_tile_at(x, y))
                print("head at x:" + str(x) + ", y:" + str(y))
        print("number of bigger snakes")
        print(len(big_snakes_heads))
        # if big snakes_heads > 0
        neighbours_plate = []
        for head in big_snakes_heads:
            adjacents = self.find_neighbours(head)
            for tile in adjacents:
                neighbours_plate.append(tile)  # add all the parts of a list I believe there is a better function for this in the API
        print("neighbours_plate after adjacents 1")
        print(len(neighbours_plate))
        # can't change neighbours_plate in the loop. Must use a copy or of neighbours_plate
        tile_twice_removed = []
        tile_twice_removed.extend(neighbours_plate)
        for target in neighbours_plate:
            adjacents = self.find_neighbours(target)
            x = target.get_x()
            y = target.get_y()
            print("target check")
            print("adjacents type")
            print(type(adjacents))
            for once_removed in adjacents:
                # print("once_removed_type")
                # print(type(once_removed))
                # if once_removed not in neighbours_plate:
                tile_twice_removed.append(once_removed)
        print("neighbours_plate after adjacents 2")
        print(len(neighbours_plate))
        print("************************************************")
        # tests.print_other_plates(neighbours_plate, converted_data)

        look_board_width = converted_data["board"]["width"]
        look_board_height = converted_data["board"]["height"]
        look_board = [["-" for x in range(look_board_width)] for y in range(look_board_height)]

        for tile in neighbours_plate:
            x = tile.get_x()
            y = tile.get_y()
            look_board[y][x] = 'P'

        print "nachos"
        for x in look_board:
            for y in x:
                print str(y) + " ",
            print ""
        print ""
        return neighbours_plate
