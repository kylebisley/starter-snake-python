# DEPRICATED
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
