"""Class to represent a gm1 palette."""

from dataclasses import dataclass, field
from typing import List

from .color_table import ColorTable


@dataclass
class Palette:
    """Represents a palette containing 10 color tables."""

    color_tables: List[ColorTable] = field(default_factory=list)
    actual_palette: int = 0
    ByteSize: int = 5120  # Palette is 10 color tables * 512 bytes each
    ColorTableCount: int = 10
    pixel_size: int = 10
    width: int = 32
    height: int = 8

    @classmethod
    def from_bytes(cls, byte_array: bytes) -> "Palette":
        """Initialize a Palette from a byte array."""
        color_tables = [
            ColorTable.from_bytes(byte_array[i * ColorTable.ByteSize : (i + 1) * ColorTable.ByteSize])
            for i in range(cls.ColorTableCount)
        ]
        return cls(color_tables=color_tables)

    def to_bytes(self) -> bytes:
        """Convert the Palette back to a byte array."""
        byte_array = bytearray()
        for color_table in self.color_tables:
            byte_array.extend(color_table.to_bytes())
        return bytes(byte_array)

    def validate_actual_palette(self):
        """Ensure the actual palette index is within valid bounds."""
        if not (0 <= self.actual_palette < self.ColorTableCount):
            raise ValueError(f"Actual palette index must be between 0 and {self.ColorTableCount - 1}.")
