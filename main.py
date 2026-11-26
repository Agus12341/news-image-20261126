#!/usr/bin/env python3
"""Validate the bundled news image and copy it to /output/entry.png.

The image sums up the world news of Thursday 26 November 2026: a
Long March rocket lifts off at dawn carrying Shenzhou-24 toward the
Tiangong space station, with the flags of China and Pakistan flying
side by side at the launch site, the day China flew the first foreign
astronaut, Pakistan's Muhammad Zeeshan Ali, to its space station.
The date is captioned at the bottom of the picture.

The kit's gate takes a PNG or JPEG of at most 1 MiB and at most 1024
by 1024 pixels, and the program must write the same bytes on every
run, so this program checks the bundled file against those limits
before copying it.
"""

import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")
MAX_BYTES = 1048576
MAX_SIDE = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC = b"\xff\xd8\xff"


def png_size(data: bytes) -> tuple[int, int]:
    """Read the width and height from a PNG's IHDR chunk."""
    return struct.unpack(">II", data[16:24])


def jpeg_size(data: bytes) -> tuple[int, int]:
    """Walk JPEG markers until a start-of-frame marker gives the size."""
    i = 2
    while i < len(data) - 9:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            height, width = struct.unpack(">HH", data[i + 5 : i + 9])
            return width, height
        length = struct.unpack(">H", data[i + 2 : i + 4])[0]
        i += 2 + length
    raise ValueError("no start-of-frame marker found")


def validate(path: str) -> None:
    """Fail loudly unless the file is an image inside the gate limits."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"missing image: {path}")
    data = open(path, "rb").read()
    if len(data) > MAX_BYTES:
        raise ValueError(f"image is {len(data)} bytes, over the {MAX_BYTES} cap")
    if data.startswith(PNG_MAGIC):
        width, height = png_size(data)
    elif data.startswith(JPEG_MAGIC):
        width, height = jpeg_size(data)
    else:
        raise ValueError("image is neither PNG nor JPEG")
    if width > MAX_SIDE or height > MAX_SIDE:
        raise ValueError(f"image is {width}x{height}, over the {MAX_SIDE} pixel cap")


def main() -> int:
    validate(SOURCE)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SOURCE, target)
    # The judge sees exactly the bytes in the output file, so a short
    # or padded copy must fail here rather than score as a bad image.
    if open(target, "rb").read() != open(SOURCE, "rb").read():
        raise ValueError("copied file differs from the bundled image")
    return 0


if __name__ == "__main__":
    sys.exit(main())
