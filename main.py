"""Catalogue photo of an impossible gadget.

Copies the studio photograph ``gadget.png`` (shipped beside this file)
to ``$MAKEFUN_OUTPUT_DIR/entry.png`` (or ``/output/entry.png`` when the
variable is not set).

The photograph: a chrome retro toaster caught mid-use — toast popping
up while a tiny umbrella on an articulated arm shields it from falling
rain, a butter dish beside it as the single accessory. A toaster that
keeps your toast dry in the rain.

Standard library only, no network, no randomness, no timestamps:
running it twice produces a byte-identical ``entry.png``.
"""

import os
import shutil
import struct
import sys
from pathlib import Path

IMAGE_NAME = "gadget.png"
OUTPUT_NAME = "entry.png"
MAX_BYTES = 1_048_576
MAX_DIMENSION = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def png_dimensions(path: Path) -> tuple[int, int]:
    """Read width/height from a PNG's IHDR chunk (stdlib only)."""
    with path.open("rb") as fh:
        header = fh.read(24)
    if len(header) < 24 or header[:8] != PNG_MAGIC:
        raise ValueError("not a PNG file")
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def main() -> int:
    here = Path(__file__).resolve().parent
    source = here / IMAGE_NAME
    if not source.is_file():
        print(f"missing image: {source}", file=sys.stderr)
        return 1

    output_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f"cannot create output dir {output_dir}: {exc}", file=sys.stderr)
        return 1
    destination = output_dir / OUTPUT_NAME

    shutil.copyfile(source, destination)

    # Validate the output the same way the gate does: whole PNG,
    # at most 1 MiB, at most 1024x1024.
    size = destination.stat().st_size
    if size > MAX_BYTES:
        print(f"output too large: {size} bytes", file=sys.stderr)
        return 1
    try:
        width, height = png_dimensions(destination)
    except (OSError, ValueError) as exc:
        print(f"output is not a whole PNG: {exc}", file=sys.stderr)
        return 1
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        print(f"output too large: {width}x{height}", file=sys.stderr)
        return 1

    print(f"wrote {destination} ({size} bytes, {width}x{height} PNG)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
