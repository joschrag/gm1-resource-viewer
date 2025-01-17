"""Functions to convert between different color formats."""

import numpy as np
from PIL import Image

from .color_table import ColorTable


def decode_argb1555(color: int) -> tuple[int, int, int, int]:
    """Decodes a 16-bit ARGB1555 color into its individual RGBA components.

    Args:
        color (int): A 16-bit integer representing the ARGB1555 color.

    Returns:
        tuple[int, int, int, int]: A tuple containing the RGBA components
        (red, green, blue, alpha), each as an integer in the range 0-255.
    """
    a: int = 255 if ((color >> 15) & 0b1) == 1 else 0  # 1-bit alpha scaled to 8-bit
    r: int = ((color >> 10) & 0b11111) << 3  # 5-bit red scaled to 8-bit
    g: int = ((color >> 5) & 0b11111) << 3  # 5-bit green scaled to 8-bit
    b: int = (color & 0b11111) << 3  # 5-bit blue scaled to 8-bit
    return r, g, b, a


def encode_argb1555(r: int, g: int, b: int, a: int) -> int:
    """Encodes 8-bit RGBA components into a 16-bit ARGB1555 color.

    Args:
        r (int): Red component (0-255).
        g (int): Green component (0-255).
        b (int): Blue component (0-255).
        a (int): Alpha component (0-255).

    Returns:
        int: A 16-bit integer representing the ARGB1555 color.
    """
    alpha_bit: int = (a & 0b1000_0000) >> 7  # Convert 8-bit alpha to 1 bit
    red_bits: int = (r >> 3) & 0b11111  # Scale 8-bit red to 5 bits
    green_bits: int = (g >> 3) & 0b11111  # Scale 8-bit green to 5 bits
    blue_bits: int = (b >> 3) & 0b11111  # Scale 8-bit blue to 5 bits
    return (alpha_bit << 15) | (red_bits << 10) | (green_bits << 5) | blue_bits


def argb1555_to_rgba8888(color: int) -> int:
    """Converts a 16-bit ARGB1555 color to a 32-bit RGBA8888 color.

    Args:
        color (int): A 16-bit integer representing the ARGB1555 color.

    Returns:
        int: A 32-bit integer representing the RGBA8888 color.
    """
    r, g, b, a = decode_argb1555(color)
    return r | (g << 8) | (b << 16) | (a << 24)


def argb1555_to_bgra8888(color: int) -> int:
    """Converts a 16-bit ARGB1555 color to a 32-bit BGRA8888 color.

    Args:
        color (int): A 16-bit integer representing the ARGB1555 color.

    Returns:
        int: A 32-bit integer representing the BGRA8888 color.
    """
    r, g, b, a = decode_argb1555(color)
    return b | (g << 8) | (r << 16) | (a << 24)


def gm1_byte_array_to_img(
    byte_array: bytearray, width: int, height: int, color_table: ColorTable | None = None
) -> Image.Image:
    """Converts a byte array encoded in GM1 format into an image.

    Args:
        byte_array (bytearray): The encoded byte array.
        width (int): The width of the output image.
        height (int): The height of the output image.
        color_table (list[int], optional): A color table (ARGB1555) for index-based colors. Defaults to None.

    Returns:
        Image: A PIL Image object in BGRA8888 format.
    """
    # Create an empty numpy array for pixel data (BGRA format)
    img_data = np.zeros((height, width, 4), dtype=np.uint8)

    # Initialize variables
    pos = 0  # Current position in the image
    new_line_pos = width  # Position for the next line

    byte_pos = 0  # Current position in the byte array

    while byte_pos < len(byte_array):
        token = byte_array[byte_pos]
        token_type = token >> 5
        length = (token & 31) + 1  # Token length + 1 for GM1 format

        byte_pos += 1

        if token_type == 4:  # Newline token
            pos = new_line_pos
            new_line_pos += width
        elif token_type == 1:  # Repeating transparent pixels
            pos += length
        else:
            read_length = 1
            write_length = 1

            if token_type == 0:  # Stream of pixels
                read_length = length
            elif token_type == 2:  # Repeating pixel
                write_length = length

            for _ in range(read_length):
                if color_table is not None:  # Use color table if available
                    color_argb1555 = color_table.colors[byte_array[byte_pos]]
                    byte_pos += 1
                else:  # Otherwise, read directly as ARGB1555
                    color_argb1555 = int.from_bytes(byte_array[byte_pos : byte_pos + 2], byteorder="little")
                    byte_pos += 2

                # Convert ARGB1555 to BGRA8888
                a = 255 if ((color_argb1555 >> 15) & 0b1) == 1 else 0
                r = ((color_argb1555 >> 10) & 0b11111) << 3
                g = ((color_argb1555 >> 5) & 0b11111) << 3
                b = (color_argb1555 & 0b11111) << 3

                color_rgba8888 = (r, g, b, a)

                for _ in range(write_length):  # Write pixel(s)
                    if pos < img_data.size // 4:
                        img_data[pos // width, pos % width] = color_rgba8888
                        pos += 1

    # Create an image from the numpy array
    image = Image.fromarray(img_data, "RGBA")
    return image
