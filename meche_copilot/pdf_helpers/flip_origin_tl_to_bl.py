# from origin at tl to origin at bottom left
def flip_origin_tl_to_bl(tl_x, tl_y, br_x, br_y, height):
    # Convert the top-left y-coordinate
    new_tl_y = height - tl_y

    # Convert the bottom-right y-coordinate
    new_br_y = height - br_y

    return tl_x, new_tl_y, br_x, new_br_y