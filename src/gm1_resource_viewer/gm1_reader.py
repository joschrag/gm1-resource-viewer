"""This module contains the main class for reading gm1 files."""

import logging
import os
import pathlib
import struct
from dataclasses import dataclass
from enum import Enum

import numpy as np
from PIL import Image

from .color_converter import gm1_byte_array_to_img
from .palette import Palette
from .tgx_image import TGXImage, TGXImageHeader
from .tile_image import TilesImage
from .utility import get_diamond_width

logger = logging.getLogger(__name__)


class GM1_Datatype(Enum):
    """GM1 data type enum."""

    Interface = 1
    Animations = 2
    TilesObject = 3
    Font = 4
    No_Compression = 5
    TGX_Const_Size = 6
    No_Compression1 = 7


@dataclass
class GM1FileHeader:
    """Class representing a gm1 file header."""

    unknown_field1: int
    unknown_field2: int
    unknown_field3: int
    number_of_pictures_in_file: int
    unknown_field5: int
    data_type: GM1_Datatype
    unknown_field7: int
    unknown_field8: int
    unknown_field9: int
    unknown_field10: int
    unknown_field11: int
    unknown_field12: int
    width: int
    height: int
    unknown_field15: int
    unknown_field16: int
    unknown_field17: int
    unknown_field18: int
    origin_x: int
    origin_y: int
    data_size: int
    unknown_field22: int
    header_size = 88

    @staticmethod
    def from_bytes(byte_array: bytes) -> "GM1FileHeader":
        """Instantiate class instance from byte array.

        Args:
            byte_array (bytes): gm1 file header bytes.

        Returns:
            GM1FileHeader: class instance
        """
        fields = struct.unpack("<22I", byte_array[:88])
        return GM1FileHeader(
            unknown_field1=fields[0],
            unknown_field2=fields[1],
            unknown_field3=fields[2],
            number_of_pictures_in_file=fields[3],
            unknown_field5=fields[4],
            data_type=GM1_Datatype(fields[5]),
            unknown_field7=fields[6],
            unknown_field8=fields[7],
            unknown_field9=fields[8],
            unknown_field10=fields[9],
            unknown_field11=fields[10],
            unknown_field12=fields[11],
            width=fields[12],
            height=fields[13],
            unknown_field15=fields[14],
            unknown_field16=fields[15],
            unknown_field17=fields[16],
            unknown_field18=fields[17],
            origin_x=fields[18],
            origin_y=fields[19],
            data_size=fields[20],
            unknown_field22=fields[21],
        )

    def to_bytes(self) -> bytes:
        """Convert class instance into gm1 header byte array.

        Returns:
            bytes: gm1 header byte array
        """
        return struct.pack(
            "<22I",
            self.unknown_field1,
            self.unknown_field2,
            self.unknown_field3,
            self.number_of_pictures_in_file,
            self.unknown_field5,
            self.data_type.value,
            self.unknown_field7,
            self.unknown_field8,
            self.unknown_field9,
            self.unknown_field10,
            self.unknown_field11,
            self.unknown_field12,
            self.width,
            self.height,
            self.unknown_field15,
            self.unknown_field16,
            self.unknown_field17,
            self.unknown_field18,
            self.origin_x,
            self.origin_y,
            self.data_size,
            self.unknown_field22,
        )

    @staticmethod
    def from_file(filepath: pathlib.Path) -> "GM1FileHeader":
        """Create class instance directly from file path.

        Args:
            filepath (pathlib.Path): path to .gm1 file

        Returns:
            GM1FileHeader: class instance
        """
        with open(filepath, "rb") as file:
            byte_array = file.read(88)
        return GM1FileHeader.from_bytes(byte_array)


class GM1_Reader:
    """Class to read gm1 files."""

    def __init__(self, file_path: pathlib.Path) -> None:
        """Instantiate GM1 Reader class.

        Args:
            file_path (pathlib.Path): path to .gm1 file
        """
        self.gm_header = GM1FileHeader.from_file(file_path)
        self.palette: Palette | None = None
        with open(file_path, "rb") as file:
            content = file.read()
        self.content = content
        self.actual_pos: int = 0
        self.tgx_images: list[TGXImage] = []
        self.tiles_image: list[TilesImage] = []

    def decode_gm1_file(self) -> bool:
        """Decodes a GM1 file from the provided byte array."""
        if GM1_Datatype(self.gm_header.data_type) == GM1_Datatype.Animations:
            palette_byte_array = self.content[
                self.gm_header.header_size : self.gm_header.header_size + Palette.ByteSize
            ]
            self.palette = Palette.from_bytes(palette_byte_array)
        # Process the image data based on the file type
        self.actual_pos = self.gm_header.header_size + Palette.ByteSize
        try:
            if GM1_Datatype(self.gm_header.data_type) in [
                GM1_Datatype.Animations,
                GM1_Datatype.Interface,
                GM1_Datatype.TGX_Const_Size,
                GM1_Datatype.Font,
            ]:
                self.create_images(self.content)
            elif GM1_Datatype(self.gm_header.data_type) in [
                GM1_Datatype.No_Compression,
                GM1_Datatype.No_Compression1,
            ]:
                pass  # self.create_no_compression_images(self.content)
            elif GM1_Datatype(self.gm_header.data_type) == GM1_Datatype.TilesObject:
                self.create_tile_image(self.content)
            else:
                return False
        except Exception as e:
            logger.error(e)
            return False

        return True

    def get_new_gm1_bytes(self) -> bytes:
        """Returns a byte array representing the new GM1 file structure."""
        new_file = bytearray()
        new_file.extend(self.gm_header.to_bytes())

        if self.palette is None:
            new_file.extend(b"\x00" * Palette.ByteSize)
        else:
            new_file.extend(self.palette.to_bytes())

        # Add offsets, sizes, headers, and image data
        for tgx_image in self.tgx_images:
            assert tgx_image.tgx_header is not None
            new_file.extend(struct.pack("<I", tgx_image.offset_in_byte_array))
            new_file.extend(struct.pack("<I", tgx_image.size_in_byte_array))
            new_file.extend(tgx_image.tgx_header.to_bytes())
            new_file.extend(tgx_image.img_byte_array)

        return bytes(new_file)

    def create_img_header(self, array: bytes) -> None:
        """Creates image headers and associates image data with them."""
        # Parse headers
        for i in range(self.gm_header.number_of_pictures_in_file):
            image_header_start = self.actual_pos + (i * 16)
            image_header_bytes = array[image_header_start : image_header_start + 16]
            self.tgx_images[i].tgx_header = TGXImageHeader.from_bytes(image_header_bytes)
            print(self.tgx_images[i].tgx_header.width, self.tgx_images[i].tgx_header.height)

        self.actual_pos += self.gm_header.number_of_pictures_in_file * 16

        # Parse image data
        for tgx_image in self.tgx_images:
            header = tgx_image.tgx_header
            assert header is not None
            arr_start = self.actual_pos + tgx_image.offset_in_byte_array
            img_data = array[arr_start : arr_start + tgx_image.size_in_byte_array]
            tgx_image.img_byte_array = img_data

    def create_images(self, array):
        """Creates images from the provided byte array."""
        self.create_offset_and_size_in_byte_array_list(array)
        self.create_img_header(array)

        for i in range(self.gm_header.number_of_pictures_in_file):
            # Assuming tgx_images is a list of structures that have ImgFileAsBytearray, Header.Width, and Header.Height
            if self.tgx_images[i] is None:
                self.tgx_images[i] = TGXImage()

            self.tgx_images[i].bitmap = gm1_byte_array_to_img(
                bytearray(self.tgx_images[i].img_byte_array),
                self.tgx_images[i].tgx_header.width,
                self.tgx_images[i].tgx_header.height,
                self.palette.color_tables[self.palette.actual_palette] if self.palette else None,
            )

    def create_tile_image(self, byte_array):
        """Create tile images from the provided byte array."""
        self.create_offset_and_size_in_byte_array_list(byte_array)
        self.create_img_header(byte_array)

        offset_x = 0
        offset_y = 0
        width = 0
        counter = -1
        items_per_row = 1
        actual_items_per_row = 0
        safe_offset = 0
        half_reached = False
        parts_before = 0

        for tgx_image in self.tgx_images:
            if tgx_image.tgx_header.image_part == 0:
                width = get_diamond_width(tgx_image.tgx_header.sub_parts)
                parts_before += tgx_image.tgx_header.sub_parts

                new_tile = TilesImage(
                    width * 30 + ((width - 1) * 2),
                    width * 16 + self.tgx_images[parts_before - 1].tgx_header.tile_offset + TilesImage.PUFFER,
                )
                self.tiles_image.append(new_tile)
                counter += 1

                items_per_row = 1
                actual_items_per_row = 0
                offset_y = new_tile.height - 16
                offset_x = (width // 2) * 30 + (width - 1) - (15 if width % 2 == 0 else 0)
                safe_offset = offset_x
                half_reached = False

            if len(tgx_image.img_byte_array) > 512:
                right = 14 if tgx_image.tgx_header.direction == 3 else 0
                self.tiles_image[counter].add_img_tile_on_top_to_img(
                    tgx_image.img_byte_array, offset_x + right, offset_y - tgx_image.tgx_header.tile_offset
                )

                if self.tiles_image[counter].minus_height > offset_y - tgx_image.tgx_header.tile_offset:
                    self.tiles_image[counter].minus_height = offset_y - tgx_image.tgx_header.tile_offset

            self.tiles_image[counter].add_diamond_to_img(tgx_image.img_byte_array, offset_x, offset_y)

            offset_x += 32
            actual_items_per_row += 1

            if actual_items_per_row == items_per_row:
                offset_x = safe_offset
                offset_y -= 8

                if items_per_row < width:
                    if half_reached:
                        items_per_row -= 1
                        offset_x += 16
                    else:
                        items_per_row += 1
                        offset_x -= 16
                else:
                    items_per_row -= 1
                    offset_x += 16
                    half_reached = True

                safe_offset = offset_x
                actual_items_per_row = 0

        for image in self.tiles_image:
            image.create_image_from_list()
        self.tgx_images = []

    def create_offset_and_size_in_byte_array_list(self, byte_array):
        """Creates the offset and size information for each image in the byte array."""
        # Step 1: Read the offsets
        for i in range(self.gm_header.number_of_pictures_in_file):
            image = TGXImage()
            image.offset_in_byte_array = int.from_bytes(
                byte_array[self.actual_pos + i * 4 : self.actual_pos + (i + 1) * 4], byteorder="little"
            )
            self.tgx_images.append(image)

        self.actual_pos += self.gm_header.number_of_pictures_in_file * 4

        # Step 2: Read the sizes
        for i in range(self.gm_header.number_of_pictures_in_file):
            self.tgx_images[i].size_in_byte_array = int.from_bytes(
                byte_array[self.actual_pos + i * 4 : self.actual_pos + (i + 1) * 4], byteorder="little"
            )

        self.actual_pos += self.gm_header.number_of_pictures_in_file * 4

    def create_bigimage(self, max_rows: int = 0, max_cols: int = 0) -> Image.Image:
        """Create an image with a grid of the decoded images.

        Args:
            max_rows (int, optional): maximum number of rows. Defaults to 0.
            max_cols (int, optional): maximum number of columns. Defaults to 0.

        Returns:
            Image.Image: decoded image grid
        """
        num_pics = self.gm_header.number_of_pictures_in_file
        img_list = self.tgx_images + self.tiles_image

        if max_rows > 0:
            max_cols = np.ceil(len(img_list) / max_rows).astype(np.int64)
        elif max_cols > 0:
            max_rows = np.ceil(len(img_list) / max_cols).astype(np.int64)
        else:
            max_rows = max_cols = np.ceil(np.sqrt(num_pics)).astype(np.int64)

        sizes = np.array([img.bitmap.size for img in img_list])
        if sizes.shape[0] < max_rows * max_cols:
            sizes = np.concat([sizes, np.zeros((max_rows * max_cols - sizes.shape[0], 2))])
        sizes = np.reshape(sizes, (max_rows, max_cols, 2))
        y_offset = np.concatenate([np.zeros(1), np.cumsum(np.max(sizes[:, :, 0], 1))]).astype(np.int64)
        x_offset = np.concatenate([np.zeros(1), np.cumsum(np.max(sizes[:, :, 1], 0))]).astype(np.int64)
        new_im = Image.new(
            "RGB",
            (x_offset[-1], y_offset[-1]),
        )
        for y in range(max_rows):
            for x in range(max_cols):
                if y * max_cols + x < num_pics:
                    new_im.paste(img_list[y * max_cols + x].bitmap, (x_offset[x], y_offset[y]))
                else:
                    break
        return new_im

    def show_image(self, max_rows: int = 0, max_cols: int = 0) -> None:
        """Display a decoded .gm1 file as a bigimage.

        Args:
            max_rows (int, optional): maximum number of rows. Defaults to 0.
            max_cols (int, optional): maximum number of columns. Defaults to 0.
        """
        image = self.create_bigimage(max_rows, max_cols)
        image.show()

    def to_file(self, file_path: str | os.PathLike, max_rows: int = 0, max_cols: int = 0) -> None:
        """Save the decoded bigimage to a file.

        Args:
            file_path (str | os.PathLike): filepath to save image to
            max_rows (int, optional): maximum number of rows. Defaults to 0.
            max_cols (int, optional): maximum number of columns. Defaults to 0.
        """
        big_img = self.create_bigimage(max_rows, max_cols)
        big_img.save(file_path)
