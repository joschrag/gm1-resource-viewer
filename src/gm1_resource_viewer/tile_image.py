"""Class to represent tile images from gm1 files."""

import numpy as np
from PIL import Image

from .color_converter import decode_argb1555


class TilesImage:
    """Class representing a tile image from a gm1 file."""

    PUFFER = 500

    def __init__(self, width: int, height: int):
        """Init the tile image.

        Args:
            width (int): tile image width
            height (int): tile image height
        """
        self.width = width
        self.height = height
        self.minus_height = float("inf")
        self.colors = np.zeros((height, width, 4), dtype=np.uint32)
        self.bitmap = Image.Image()

    def dispose(self):
        """Dispose of resources."""
        self.bitmap = Image.Image()

    def add_diamond_to_img(self, img_file_as_bytearray, x_offset, y_offset):
        """Add the Diamond Tile Img to the bigger Img."""
        array = [2, 6, 10, 14, 18, 22, 26, 30, 30, 26, 22, 18, 14, 10, 6, 2]

        byte_pos = 0

        for y in range(16):
            for x in range(array[y]):
                pos_x = x_offset + x + 15 - array[y] // 2
                pos_y = y_offset + y
                pos = (pos_y, pos_x)

                color_value = int.from_bytes(img_file_as_bytearray[byte_pos : byte_pos + 2], "little")
                self.colors[pos] = decode_argb1555(color_value)
                byte_pos += 2

    def add_img_tile_on_top_to_img(self, img_file_as_bytearray, offset_x, offset_y):
        """Add normal IMG to the bigger IMG."""
        x = 0
        y = 0
        byte_pos = 512

        while byte_pos < len(img_file_as_bytearray):
            token = img_file_as_bytearray[byte_pos]
            tokentype = token >> 5
            length = (token & 31) + 1
            byte_pos += 1

            if tokentype == 0:  # Stream-of-pixels
                for _ in range(length):
                    pixel_color = int.from_bytes(img_file_as_bytearray[byte_pos : byte_pos + 2], "little")
                    byte_pos += 2

                    self.colors[offset_y + y, offset_x + x, :] = decode_argb1555(pixel_color)
                    x += 1

            elif tokentype == 4:  # Newline
                y += 1
                x = 0

            elif tokentype == 2:  # Repeating pixels
                pixel_color = int.from_bytes(img_file_as_bytearray[byte_pos : byte_pos + 2], "little")
                byte_pos += 2
                color = decode_argb1555(pixel_color)

                for _ in range(length):
                    self.colors[offset_y + y, offset_x + x, :] = color
                    x += 1

            elif tokentype == 1:  # Transparent-Pixel-String
                x += length

    def create_image_from_list(self):
        """Creates the new big IMG as Bitmap."""
        self.dispose()

        if self.minus_height == float("inf"):
            self.minus_height = self.PUFFER

        self.height -= self.minus_height

        cropped_colors = self.colors[self.minus_height :]

        self.bitmap = Image.fromarray(cropped_colors.astype("uint8"), "RGBA")
