#!/usr/bin/env python3
"""Convert an image file to sixel and write it to stdout.

Usage: img2sixel.py IMAGE [-w WIDTH] [-c COLORS] [--bg #RRGGBB]

Requires Pillow; everything else is standard library.
"""

import argparse
import sys

from PIL import Image


def parse_color(s):
    s = s.lstrip("#")
    if len(s) != 6:
        raise argparse.ArgumentTypeError("background must be #RRGGBB")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def load_image(path, width, colors, bg, pad_multiple=None):
    """Load and quantize an image for sixel output; alpha is flattened onto
    bg. pad_multiple=(w, h) pads the canvas with bg up to the next multiple,
    so a graphic explicitly paints every pixel of every terminal cell it
    touches (terminals fill unpainted graphic area with their own default
    background)."""
    img = Image.open(path)
    img.load()

    # Flatten transparency onto the background color.
    if img.mode in ("RGBA", "LA", "PA") or (
        img.mode == "P" and "transparency" in img.info
    ):
        img = img.convert("RGBA")
        base = Image.new("RGBA", img.size, bg + (255,))
        base.alpha_composite(img)
        img = base.convert("RGB")
    elif img.mode != "RGB":
        img = img.convert("RGB")

    if width and img.width > width:
        height = max(1, round(img.height * width / img.width))
        img = img.resize((width, height), Image.LANCZOS)

    if pad_multiple:
        pw = -(-img.width // pad_multiple[0]) * pad_multiple[0]
        ph = -(-img.height // pad_multiple[1]) * pad_multiple[1]
        if (pw, ph) != img.size:
            canvas = Image.new("RGB", (pw, ph), bg)
            canvas.paste(img, (0, 0))
            img = canvas

    # Palette mode: sixel colors are palette registers.
    return img.quantize(colors=colors, dither=Image.Dither.FLOYDSTEINBERG)


def rle(mask):
    """Run-length encode one band line of sixel values (0..63)."""
    parts = []
    end = len(mask)
    while end and mask[end - 1] == 0:  # trailing blanks are implicit
        end -= 1
    i = 0
    while i < end:
        value = mask[i]
        j = i
        while j < end and mask[j] == value:
            j += 1
        run = j - i
        ch = chr(63 + value)
        parts.append(f"!{run}{ch}" if run > 3 else ch * run)
        i = j
    return "".join(parts)


def to_sixel(img):
    w, h = img.size
    pixels = img.tobytes()
    palette = img.getpalette()
    ncolors = len(palette) // 3

    out = ["\x1bPq", f'"1;1;{w};{h}']

    # Define color registers (sixel wants RGB as 0-100 percentages).
    for i in range(ncolors):
        r, g, b = palette[3 * i:3 * i + 3]
        out.append(f"#{i};2;{r * 100 // 255};{g * 100 // 255};{b * 100 // 255}")

    # Emit the image in bands of 6 rows.
    for y in range(0, h, 6):
        rows = [pixels[(y + dy) * w:(y + dy + 1) * w]
                for dy in range(min(6, h - y))]

        masks = {}  # color index -> per-column sixel bitmask
        for dy, row in enumerate(rows):
            bit = 1 << dy
            for x, color in enumerate(row):
                mask = masks.get(color)
                if mask is None:
                    mask = masks[color] = bytearray(w)
                mask[x] |= bit

        band = []
        for color, mask in sorted(masks.items()):
            band.append(f"#{color}{rle(mask)}")
        out.append("$".join(band))
        out.append("-")

    out.append("\x1b\\")
    return "".join(out)


def main():
    ap = argparse.ArgumentParser(description="Output an image file as sixel.")
    ap.add_argument("image", help="path to the image file")
    ap.add_argument("-w", "--width", type=int, default=800,
                    help="max output width in pixels (default 800, 0 = no resize)")
    ap.add_argument("-c", "--colors", type=int, default=256,
                    help="palette size, 2-256 (default 256)")
    ap.add_argument("--bg", type=parse_color, default=(0, 0, 0),
                    help="background for transparent images, e.g. #ffffff")
    args = ap.parse_args()

    if not 2 <= args.colors <= 256:
        ap.error("--colors must be between 2 and 256")

    try:
        img = load_image(args.image, args.width, args.colors, args.bg)
    except OSError as e:
        sys.exit(f"error: {e}")

    sys.stdout.write(to_sixel(img))
    sys.stdout.flush()


if __name__ == "__main__":
    main()
