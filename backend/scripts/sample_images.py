"""
Sample images: draws simple abstract placeholder pictures (gradients, rings,
stripes) as PNG files, with no image library needed.

Only used by seed_sample_entries.py to give the sample entries something to show.
"""

import math
import struct
import zlib
from collections.abc import Callable

Color = tuple[int, int, int]
Painter = Callable[[float, float], Color]


def write_png(path: str, width: int, height: int, paint: Painter) -> None:
    """Save a PNG where each pixel's color comes from paint(x, y), with x and y from 0 to 1."""
    rows = bytearray()
    for py in range(height):
        rows.append(0)  # PNG row header: no filter
        for px in range(width):
            rows.extend(paint(px / width, py / height))

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    with open(path, "wb") as file:
        file.write(b"\x89PNG\r\n\x1a\n")
        file.write(chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(bytes(rows))) + chunk(b"IEND", b""))


def _mix(a: Color, b: Color, t: float) -> Color:
    t = min(1.0, max(0.0, t))
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))  # type: ignore[return-value]


def gradient(top: Color, bottom: Color) -> Painter:
    return lambda x, y: _mix(top, bottom, y)


def rings(ink: Color, paper: Color, count: int = 9) -> Painter:
    def paint(x: float, y: float) -> Color:
        distance = math.hypot(x - 0.5, y - 0.5)
        return ink if int(distance * count * 2) % 2 == 0 else paper

    return paint


def stripes(a: Color, b: Color, count: int = 14, slant: float = 0.4) -> Painter:
    return lambda x, y: a if int((x + y * slant) * count) % 2 == 0 else b


def blob(center: Color, edge: Color, cx: float = 0.45, cy: float = 0.55) -> Painter:
    return lambda x, y: _mix(center, edge, math.hypot(x - cx, y - cy) * 2.2)
