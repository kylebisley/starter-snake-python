import tile as t


class Board:

    # TODO: add functionality to ignore tails if their snake isn't growing this turn
    def __init__(self, j_data, path_board, char_board):
        self._board_width = j_data["board"]["width"]
        self._board_height = j_data["board"]["height"]
        self._the_board = [[None for x in range(self._board_width)] for y in range(self._board_height)]
        self.food_tiles = []

        for y in range(len(path_board)):
            for x in range(len(path_board[0])):

                is_food = False
                if char_board[y][x] == 'F':
                    is_food = True

                new_tile = t.Tile(x, y, path_board[y][x], is_food, char_board[y][x])
                self._the_board[y].append(new_tile)
                if new_tile.get_food():
                    self.food_tiles.append(new_tile)

    # Getters and setters
    def get_tile_at(self, x, y):
        return self._the_board[y][x]

    def get_board_width(self):
        return self._board_width

    def get_board_height(self):
        return self._board_height

    def get_food_tiles(self):
        return self.food_tiles

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
        for y in range(self.get_board_height()):
            for x in range(self.get_board_width()):
                print(self.get_tile_at(x, y).get_cost() + " "),
            print()
        print()
        

    def print_dima_board(self):
        '''
        prints character representation of all tiles on board
        '''
        for y in range(self.get_board_height()):
            for x in range(self.get_board_width()):
                print(self.get_tile_at(x, y).get_char() + " "),
            print()
        print()

    def dab(self):
        raise NotImplementedError


    # Other methods

    #takes in a tile, and outputs a list of all tiles that are adjacent to it
    def find_neighbours(self, tile):
        neighbours = []

        # look down
        if((tile.get_y() > 0) and not self.get_tile_at(tile.get_x(), tile.get_y() - 1)):
            neighbours.append(self.get_tile_at(tile.get_x(), tile.get_y() - 1))

        #look up
        if((tile.get_y() < self.get_height() - 1) and not self.get_tile_at(tile.get_x(), tile.get_y() + 1)):
            neighbours.append(self.get_tile_at(tile.get_x(), tile.get_y() + 1))

        #look left
        if((tile.get_x() > 0) and not self.get_tile_at(tile.get_x() - 1, tile.get_y())):
            neighbours.append(self.get_tile_at(tile.get_x() - 1, tile.get_y()))
        
        #look right
        if((tile.get_x() < self.get_width() - 1) and not self.get_tile_at(tile.get_x() + 1,tile.get_y())):
            neighbours.append(self.get_tile_at(tile.get_x() + 1,tile.get_y()))
        
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
