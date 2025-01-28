"""Classes for .tgx images and their file header."""

import os
import pathlib
import struct
from dataclasses import dataclass

from PIL import Image

from .color_converter import gm1_byte_array_to_img


@dataclass
class TGXImageHeader:
    """Class for a .tgx file header."""

    width: int
    height: int
    offset_x: int
    offset_y: int
    image_part: int
    sub_parts: int
    tile_offset: int
    direction: int
    horizontal_offset_of_image: int
    building_width: int
    animated_color: int

    @staticmethod
    def from_bytes(byte_array: bytes) -> "TGXImageHeader":
        """Instantiate class from byte array.

        Args:
            byte_array (bytes): tgx file header bytes.

        Returns:
            TGXImageHeader: instantiated class object.
        """
        fields = struct.unpack("<4H2BHB3B", byte_array[:16])
        return TGXImageHeader(
            width=fields[0],
            height=fields[1],
            offset_x=fields[2],
            offset_y=fields[3],
            image_part=fields[4],
            sub_parts=fields[5],
            tile_offset=fields[6],
            direction=fields[7],
            horizontal_offset_of_image=fields[8],
            building_width=fields[9],
            animated_color=fields[10],
        )

    def to_bytes(self) -> bytes:
        """Convert instance into tgx header byte array.

        Returns:
            bytes: tgx header byte array
        """
        return struct.pack(
            "<4H2BHB3B",
            self.width,
            self.height,
            self.offset_x,
            self.offset_y,
            self.image_part,
            self.sub_parts,
            self.tile_offset,
            self.direction,
            self.horizontal_offset_of_image,
            self.building_width,
            self.animated_color,
        )


class TGXImage:
    """Class representing a .tgx image file."""

    def __init__(self) -> None:
        """Initialize class."""
        self.tgx_header: TGXImageHeader  # For TGX as a subimage in GM1 file
        self.offset_in_byte_array = 0
        self.size_in_byte_array = 0
        self.tgx_width: int = 0
        self.tgx_height: int = 0
        self.img_byte_array: bytes = bytes([])
        self.bitmap: Image.Image = Image.Image()


def decode_tgx_data(array: bytes) -> Image.Image:
    """Decode a .tgx file into a PIL image.

    Args:
        array (bytes): .tgx file bytes

    Returns:
        Image.Image: PIL image
    """
    tgx_image = TGXImage()

    # Extract width and height (first 8 bytes)
    tgx_image.tgx_width = struct.unpack("<I", array[:4])[0]
    tgx_image.tgx_height = struct.unpack("<I", array[4:8])[0]

    # Extract image data (everything after the first 8 bytes)
    tgx_image.img_byte_array = array[8:]

    # Decode the byte array into an image (using placeholder function)
    tgx_image.bitmap = gm1_byte_array_to_img(
        bytearray(tgx_image.img_byte_array), tgx_image.tgx_width, tgx_image.tgx_height
    )
    return tgx_image.bitmap


def decode_tgx(file_path: str | os.PathLike) -> Image.Image:
    """Decode a .tgx file from a file path into a PIL image.

    Args:
        array (str | os.PathLike): .tgx file patg

    Returns:
        Image.Image: PIL image
    """
    file_path = pathlib.Path(file_path)
    image = decode_tgx_data(file_path.read_bytes())
    return image


def decode_tgx_to_file(in_path: str | os.PathLike, out_path: str | os.PathLike) -> None:
    """Decode a tgx file into an image at 'out_path.suffix'.

    Args:
        in_path (str | os.PathLike): .tgx file to decode
        out_path (str | os.PathLike): path to save the file to
    """
    in_path = pathlib.Path(in_path)
    out_path = pathlib.Path(out_path)
    image = decode_tgx_data(in_path.read_bytes())
    image.save(out_path.with_suffix(".png"))
