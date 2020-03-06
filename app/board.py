import tile as t
from parse_board import board_to_array


class Board:

    # TODO: add functionality to ignore tails if their snake isn't growing this turn
    def __init__(self, j_data, path_board):
        self._board_width = len(j_data["board"]["width"])
        self._board_height = len(j_data["board"]["height"])
        self._the_board = [[None for x in range(self._board_width)] for y in range(self._board_height)]
        self.food_tiles = []
        
        char_board = board_to_array(j_data)

        for y in range(len(path_board)):
            for x in range(len(path_board[0])):

                is_food = False
                if char_board[y][x] == 'F':
                    is_food = True

                new_tile = t.Tile(x, y, path_board[y][x], is_food, char_board[y][x])
                self._the_board[y][x].append(new_tile)
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

    # TODO: finish print methods
    def print_int_board(self):
        raise NotImplementedError

    def print_dima_board(self):
        raise NotImplementedError

    def dab(self):
        raise NotImplementedError