"""Functions to convert between images and no_compression gm1 files."""

from typing import List

import numpy as np
from PIL import Image

from .color_converter import decode_argb1555


def get_bitmap(byte_array: bytes, width: int, height: int) -> Image.Image:
    """Converts a byte array to a bitmap image.

    Args:
        byte_array (bytes): image bytes (can be shorter than width*height)
        width (int): image height
        height (int): image width

    Returns:
        Image.Image: converted image from bytes
    """
    data = np.frombuffer(byte_array, dtype=np.uint16)
    rgba_data = np.array([decode_argb1555(pixel) for pixel in data], dtype=np.uint8)

    # Create a blank RGBA image buffer initialized with (0,0,0,255)
    full_data = np.full((height, width, 4), (0, 0, 0, 255), dtype=np.uint8)

    # Copy rgba_data into full_data, ensuring we don't exceed its bounds
    min_length = min(len(rgba_data) // 4, width * height)
    full_data.flat[: min_length * 4] = rgba_data.flat[: min_length * 4]

    return Image.fromarray(full_data, mode="RGBA")


def get_byte_array(data: List[int], width: int, height: int) -> bytes:
    """Converts a list of 16-bit pixel values to a byte array.

    Args:
        data (List[int]): image rgba data
        width (int): image width
        height (int): image height

    Returns:
        bytes: gm1 bytes
    """
    length = width * height
    byte_array = bytearray(length * 2)

    for i in range(length):
        byte_array[i * 2 : i * 2 + 2] = data[i].to_bytes(2, byteorder="little")

    return bytes(byte_array)
