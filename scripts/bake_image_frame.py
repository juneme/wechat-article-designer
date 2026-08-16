#!/usr/bin/env python3
"""Bake a soft rounded WeChat-style frame into an image.

Use only when the image itself must carry the white frame, rounded corners, and
shadow. For WeChat articles where the user will manually insert photos, prefer
an HTML frame placeholder instead.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1200)
    parser.add_argument("--outer-pad-x", type=int, default=64)
    parser.add_argument("--outer-pad-top", type=int, default=44)
    parser.add_argument("--outer-pad-bottom", type=int, default=50)
    parser.add_argument("--inner-pad", type=int, default=14)
    parser.add_argument("--frame-radius", type=int, default=42)
    parser.add_argument("--photo-radius", type=int, default=34)
    # Brand-customizable colors. Defaults match the skill's default fallbacks.
    parser.add_argument("--canvas-bg", type=str, default="#f7faf8",
                        help="Outer canvas background (page color around the frame).")
    parser.add_argument("--frame-border", type=str, default="#daeae2",
                        help="Border color of the white frame around the photo.")
    return parser.parse_args()


def rounded_image(img: Image.Image, radius: int) -> Image.Image:
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([0, 0, img.width, img.height], radius=radius, fill=255)
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.paste(img.convert("RGBA"), (0, 0), mask=mask)
    return out


def parse_hex_color(value: str) -> tuple[int, int, int, int]:
    """Convert '#rrggbb' or '#rrggbbaa' into an RGBA tuple."""
    raw = value.lstrip("#")
    if len(raw) == 6:
        r, g, b = int(raw[0:2], 16), int(raw[2:4], 16), int(raw[4:6], 16)
        return r, g, b, 255
    if len(raw) == 8:
        r, g, b, a = int(raw[0:2], 16), int(raw[2:4], 16), int(raw[4:6], 16), int(raw[6:8], 16)
        return r, g, b, a
    raise ValueError(f"Invalid color '{value}'. Use '#rrggbb' or '#rrggbbaa'.")


def main() -> None:
    args = parse_args()
    src = Image.open(args.input).convert("RGB")

    photo_w = args.width - args.outer_pad_x * 2 - args.inner_pad * 2
    photo_h = round(photo_w * src.height / src.width)
    src = src.resize((photo_w, photo_h), Image.LANCZOS)

    frame_w = photo_w + args.inner_pad * 2
    frame_h = photo_h + args.inner_pad * 2
    canvas_h = args.outer_pad_top + frame_h + args.outer_pad_bottom
    canvas_bg = parse_hex_color(args.canvas_bg)
    border_color = parse_hex_color(args.frame_border)
    canvas = Image.new("RGBA", (args.width, canvas_h), canvas_bg)

    fx = args.outer_pad_x
    fy = args.outer_pad_top

    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle(
        [fx, fy + 16, fx + frame_w, fy + frame_h + 16],
        radius=args.frame_radius,
        fill=(42, 83, 66, 36),
    )
    canvas.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(34)))

    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(
        [fx, fy, fx + frame_w, fy + frame_h],
        radius=args.frame_radius,
        fill=(255, 255, 255, 255),
        outline=border_color,
        width=2,
    )

    canvas.alpha_composite(
        rounded_image(src, args.photo_radius),
        (fx + args.inner_pad, fy + args.inner_pad),
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(args.out, quality=95, optimize=True)


if __name__ == "__main__":
    main()
