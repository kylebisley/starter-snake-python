# DEPRECATED
# I'd like to move this code to another file in our repo and keep it for reference. 
# def getNearestFood(datadump):
#     """
#     Returns x,y coordinates of the closest pathable food (as a crow flys)
#     Args:
#         datadump (json): converted python representation of current game snapshot
#     Returns:
#         Index of the food closest to head of snake. 
#     """
#     food_array = []
#     distance_array = []
#     snake_x = datadump["you"]["body"][0]['x']
#     snake_y = datadump["you"]["body"][0]['y']
#     for z in datadump["board"]["food"]:
#         x = z['x']
#         y = z['y']
#         food_array.append([x, y])

#     for i in food_array:
#         move_distance = (abs((snake_x) - i[0])) + (abs((snake_y) - i[1]))
#         distance_array.append(move_distance)

#     index_of_smallest = distance_array.index(min(distance_array))
#     print(food_array[index_of_smallest])
#     return food_array[index_of_smallest]


# def get_min_path_to_food(converted_data, pathBoard):
#     """
#     Checks for shortest path to food. 
#     Args:
#         converted_data (json): converted python representation of current game snapshot
#         pathBoard (int array): integer representation of board
#     Returns:
#         shortestPath (path): shortest path to food 
#         OR 
#         shortestPath (string): "Unassigned" when it can't path to food
#     """
#     shortestPath = "Unassigned"
#     for food in converted_data["board"]["food"]:
#         x = food['x']
#         y = food['y']
#         newPath = navigate(converted_data, pathBoard, [x, y])
#         if (shortestPath == "Unassigned" and (len(newPath) != 0)):
#             shortestPath = newPath
#         if (len(newPath) < len(shortestPath) and (len(newPath) != 0)):
#             shortestPath = newPath
        
#         sum_path_weight(newPath, pathBoard)
#     return shortestPath
#
#   def printBoard(converted_board, integer_board):
#    for x in integer_board:
#       for y in x:
#          print(str(y) + " "),
#     print()
#     for x in converted_board:
#        for y in x:
#           print(str(y) + " "),
#      print()
#
#
#


# def get_min_path_to_food(converted_data, path_board):
#     """
#     Checks for lightest path to food.
#     Args:
#         converted_data (dict): converted python representation of current game
#                                 snapshot
#         path_board (array.py): integer representation of board
#     Returns:
#         shortest_path (list): shortest path to food
#         OR
#         shortest_path (str): "Unassigned" when it can't path to food
#     """
#     shortest_path = "Unassigned"
#     for food in converted_data["board"]["food"]:
#         x = food['x']
#         y = food['y']
#         new_path = navigate(converted_data, path_board, [x, y])
#         if shortest_path == "Unassigned" and (len(new_path) != 0):
#             shortest_path = new_path
#         elif shortest_path != "Unassigned":
#             # Line below too long. Broken into 3 pieces for clarity
#             if (sum_path_weight(new_path, path_board) <
#                     sum_path_weight(shortest_path, path_board)
#                     and (len(new_path) != 0)):
#                 shortest_path = new_path
# # --------------------------------------------------------------------------------------------
#         sum_path_weight(new_path, path_board) # fairly sure this can be removed in a last pass
#     return shortest_path
