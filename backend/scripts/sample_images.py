"""
Sample images: draws abstract placeholder pictures (gradients, rings,
stripes, horizons, suns, grids) as PNG files for the demo entries.

Only used by seed_demo_entries.py. Each painter takes a pair of x, y grids
(0 to 1 across the picture) and returns the picture's colors.
"""

import struct
import zlib
from collections.abc import Callable

import numpy as np

Color = tuple[int, int, int]
Painter = Callable[[np.ndarray, np.ndarray], np.ndarray]


def write_png(path: str, width: int, height: int, paint: Painter) -> None:
    """Save a PNG painted by paint(x, y), with a faint grain so gradients don't band."""
    y, x = np.mgrid[0:height, 0:width].astype(np.float32)
    pixels = paint(x / width, y / height)
    grain = np.random.default_rng(width * 7919 + height).normal(0, 2.2, pixels.shape[:2])[..., None]
    pixels = np.clip(pixels + grain, 0, 255).astype(np.uint8)

    rows = b"".join(b"\x00" + row.tobytes() for row in pixels)  # each row: "no filter" byte, then pixels

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    with open(path, "wb") as file:
        file.write(b"\x89PNG\r\n\x1a\n")
        file.write(chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(rows, 6)) + chunk(b"IEND", b""))


def _mix(a: Color, b: Color, t: np.ndarray) -> np.ndarray:
    t = np.clip(t, 0, 1)[..., None]
    return np.array(a, np.float32) * (1 - t) + np.array(b, np.float32) * t


def _pick(a: Color, b: Color, choose_a: np.ndarray) -> np.ndarray:
    return np.where(choose_a[..., None], np.array(a, np.float32), np.array(b, np.float32))


def gradient(top: Color, bottom: Color) -> Painter:
    return lambda x, y: _mix(top, bottom, y)


def diagonal(start: Color, end: Color) -> Painter:
    return lambda x, y: _mix(start, end, (x + y) / 2)


def three_stop(top: Color, middle: Color, bottom: Color) -> Painter:
    return lambda x, y: np.where((y < 0.5)[..., None], _mix(top, middle, y * 2), _mix(middle, bottom, y * 2 - 1))


def blob(center: Color, edge: Color, cx: float = 0.45, cy: float = 0.55) -> Painter:
    return lambda x, y: _mix(center, edge, np.hypot(x - cx, y - cy) * 2.2)


def rings(ink: Color, paper: Color, count: int = 9) -> Painter:
    return lambda x, y: _pick(ink, paper, (np.hypot(x - 0.5, y - 0.5) * count * 2).astype(int) % 2 == 0)


def stripes(a: Color, b: Color, count: int = 14, slant: float = 0.4) -> Painter:
    return lambda x, y: _pick(a, b, ((x + y * slant) * count).astype(int) % 2 == 0)


def checker(a: Color, b: Color, count: int = 8) -> Painter:
    return lambda x, y: _pick(a, b, ((x * count).astype(int) + (y * count).astype(int)) % 2 == 0)


def horizon(sky_top: Color, sky_low: Color, ground_top: Color, ground_low: Color, line: float = 0.6) -> Painter:
    """A sky over land or sea, like a landscape photo."""
    return lambda x, y: np.where(
        (y < line)[..., None], _mix(sky_top, sky_low, y / line), _mix(ground_top, ground_low, (y - line) / (1 - line))
    )


def sun(sky_top: Color, sky_low: Color, disc: Color, cx: float = 0.5, cy: float = 0.55, size: float = 0.16) -> Painter:
    """A soft disc low in a gradient sky."""

    def paint(x: np.ndarray, y: np.ndarray) -> np.ndarray:
        sky = _mix(sky_top, sky_low, y)
        glow = np.clip(1 - (np.hypot(x - cx, y - cy) - size) * 30, 0, 1)
        return _mix((0, 0, 0), disc, np.ones_like(x)) * glow[..., None] + sky * (1 - glow[..., None])

    return paint
