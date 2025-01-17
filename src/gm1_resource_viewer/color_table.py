"""Class to represent a colortable."""

import struct
from dataclasses import dataclass, field
from typing import List


@dataclass
class ColorTable:
    """Represents a color table containing 256 2-byte colors."""

    colors: List[int] = field(default_factory=list)

    ByteSize: int = 512  # Each color table is 512 bytes
    ColorCount: int = 256  # A color table contains 256 colors

    @classmethod
    def from_bytes(cls, byte_array: bytes) -> "ColorTable":
        """Initialize a ColorTable from a byte array."""
        if len(byte_array) != cls.ByteSize:
            raise ValueError(f"ColorTable must be exactly {cls.ByteSize} bytes.")
        # Use struct.unpack to efficiently read all 256 2-byte integers
        colors = list(struct.unpack(f"<{cls.ColorCount}H", byte_array))
        return cls(colors)

    @classmethod
    def from_ushort_array(cls, ushort_array: List[int]) -> "ColorTable":
        """Initialize a ColorTable from a list of 256 unsigned shorts."""
        if len(ushort_array) != cls.ColorCount:
            raise ValueError(f"Invalid input length ({len(ushort_array)}). The length must be {cls.ColorCount}.")
        return cls(colors=ushort_array)

    def to_bytes(self) -> bytes:
        """Convert the ColorTable back to a byte array."""
        # Use struct.pack to efficiently write all 256 2-byte integers
        return struct.pack(f"<{self.ColorCount}H", *self.colors)

    def copy(self) -> "ColorTable":
        """Create a copy of this color table."""
        return ColorTable(colors=self.colors.copy())
