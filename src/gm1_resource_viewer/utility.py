"""Various utility functions."""


def get_diamond_width(num_parts: int) -> int:
    """Calculate the diamond width based on the number of parts."""
    width = 0
    actual_parts = 0
    corner = 1

    while True:
        if num_parts - actual_parts - corner == 0:
            width = corner - corner // 2
            break
        elif num_parts - actual_parts - corner < 0:
            # Error condition
            break
        actual_parts += corner
        corner += 2

    return width
