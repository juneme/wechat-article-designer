#!/usr/bin/env python3
"""Generate a deterministic soft-App WeChat recruitment cover at 2.35:1."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE_WIDTH = 1175
BASE_HEIGHT = 500


def parse_hex(value: str) -> tuple[int, int, int]:
    raw = value.strip().lstrip("#")
    if len(raw) != 6:
        raise argparse.ArgumentTypeError(f"Invalid color '{value}'; use #RRGGBB.")
    try:
        return tuple(int(raw[index : index + 2], 16) for index in (0, 2, 4))
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid color '{value}'; use #RRGGBB."
        ) from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a 2.35:1 WeChat recruitment cover with exact supplied text."
    )
    parser.add_argument("--out", type=Path, required=True, help="Output PNG path.")
    parser.add_argument("--width", type=int, default=BASE_WIDTH)
    parser.add_argument("--height", type=int, default=BASE_HEIGHT)
    parser.add_argument("--brand", default="品牌招聘")
    parser.add_argument("--eyebrow", default="RECRUITMENT")
    parser.add_argument("--headline", default="期待新的同行者")
    parser.add_argument("--tagline", default="多元岗位开放 · 招聘通道开启")
    parser.add_argument("--position-count", default="05")
    parser.add_argument("--positions-label", default="OPEN POSITIONS")
    parser.add_argument("--footer", default="")
    parser.add_argument("--font-regular", type=Path)
    parser.add_argument("--font-bold", type=Path)
    parser.add_argument("--background", type=parse_hex, default=parse_hex("#F5F6FC"))
    parser.add_argument("--surface", type=parse_hex, default=parse_hex("#FFFFFF"))
    parser.add_argument("--ink", type=parse_hex, default=parse_hex("#172153"))
    parser.add_argument("--muted", type=parse_hex, default=parse_hex("#70789A"))
    parser.add_argument("--primary", type=parse_hex, default=parse_hex("#7C73E8"))
    parser.add_argument("--primary-soft", type=parse_hex, default=parse_hex("#EEEAFE"))
    parser.add_argument("--mint", type=parse_hex, default=parse_hex("#DDF6EC"))
    parser.add_argument("--border", type=parse_hex, default=parse_hex("#DDE1EF"))
    args = parser.parse_args()
    if args.width <= 0 or args.height <= 0:
        parser.error("--width and --height must be positive integers.")
    if args.width * 20 != args.height * 47:
        parser.error(
            "Canvas must be exactly 2.35:1 (width:height = 47:20), e.g. 1175x500."
        )
    if args.out.suffix.lower() != ".png":
        parser.error("--out must use a .png extension.")
    return args


def font_candidates(bold: bool) -> list[Path]:
    windows = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
    if bold:
        return [
            windows / "msyhbd.ttc",
            windows / "simhei.ttf",
            Path("/System/Library/Fonts/PingFang.ttc"),
            Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"),
            Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        ]
    return [
        windows / "msyh.ttc",
        windows / "simsun.ttc",
        Path("/System/Library/Fonts/PingFang.ttc"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
    ]


def resolve_font(explicit: Path | None, bold: bool) -> Path:
    if explicit:
        if not explicit.is_file():
            raise FileNotFoundError(f"Font not found: {explicit}")
        return explicit
    for candidate in font_candidates(bold):
        if candidate.is_file():
            return candidate
    kind = "bold" if bold else "regular"
    raise FileNotFoundError(
        f"No CJK {kind} font found. Pass --font-{kind} with a .ttf or .ttc file."
    )


def text_width(
    draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont
) -> int:
    left, _, right, _ = draw.textbbox((0, 0), text or " ", font=font)
    return right - left


def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        if paragraph == "":
            lines.append("")
            continue
        current = ""
        for character in paragraph:
            candidate = current + character
            if current and text_width(draw, candidate, font) > max_width:
                lines.append(current)
                current = character
            else:
                current = candidate
        lines.append(current)
    return lines


def fit_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font_path: Path,
    start_size: int,
    min_size: int,
    max_width: int,
    max_height: int,
    max_lines: int,
    spacing: int,
) -> tuple[ImageFont.FreeTypeFont, list[str], int]:
    for size in range(start_size, min_size - 1, -1):
        font = ImageFont.truetype(str(font_path), size=size)
        lines = wrap_text(draw, text, font, max_width)
        bbox = draw.textbbox((0, 0), "国Ag", font=font)
        line_height = bbox[3] - bbox[1]
        total_height = line_height * len(lines) + spacing * max(0, len(lines) - 1)
        if len(lines) <= max_lines and total_height <= max_height:
            return font, lines, line_height
    raise ValueError(
        f"Text does not fit without truncation: {text!r}. Shorten the text or use a larger canvas."
    )


def draw_lines(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    lines: list[str],
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int],
    line_height: int,
    spacing: int,
) -> None:
    x, y = xy
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill, anchor="la")
        y += line_height + spacing


def scaled(value: int, width: int) -> int:
    return max(1, round(value * width / BASE_WIDTH))


def main() -> None:
    args = parse_args()
    regular_path = resolve_font(args.font_regular, bold=False)
    bold_path = resolve_font(args.font_bold, bold=True)
    width, height = args.width, args.height

    def s(value: int) -> int:
        return scaled(value, width)

    canvas = Image.new("RGB", (width, height), args.background)
    draw = ImageDraw.Draw(canvas)

    margin = s(20)
    gap = s(16)
    left_right = s(770)
    left_box = (margin, margin, left_right, height - margin)
    right_box = (left_right + gap, margin, width - margin, height - margin)
    draw.rounded_rectangle(
        left_box, radius=s(30), fill=args.primary_soft, outline=args.border, width=s(1)
    )
    draw.rounded_rectangle(
        right_box, radius=s(30), fill=args.surface, outline=args.border, width=s(1)
    )

    content_x = s(56)
    badge_y = s(48)
    eyebrow_font, _, _ = fit_text(
        draw, args.eyebrow, bold_path, s(18), s(12), s(220), s(24), 1, s(2)
    )
    badge_w = text_width(draw, args.eyebrow, eyebrow_font) + s(28)
    draw.rounded_rectangle(
        (content_x, badge_y, content_x + badge_w, badge_y + s(36)),
        radius=s(18),
        fill=args.mint,
    )
    draw.text(
        (content_x + badge_w // 2, badge_y + s(18)),
        args.eyebrow,
        font=eyebrow_font,
        fill=args.ink,
        anchor="mm",
    )

    brand_font, brand_lines, brand_height = fit_text(
        draw, args.brand, bold_path, s(24), s(15), s(630), s(34), 1, s(2)
    )
    draw_lines(
        draw,
        (content_x, s(118)),
        brand_lines,
        brand_font,
        args.muted,
        brand_height,
        s(2),
    )

    headline_font, headline_lines, headline_height = fit_text(
        draw, args.headline, bold_path, s(70), s(38), s(650), s(150), 2, s(8)
    )
    draw_lines(
        draw,
        (content_x, s(164)),
        headline_lines,
        headline_font,
        args.ink,
        headline_height,
        s(8),
    )

    tagline_font, tagline_lines, tagline_height = fit_text(
        draw, args.tagline, regular_path, s(24), s(15), s(650), s(62), 2, s(6)
    )
    draw_lines(
        draw,
        (content_x, s(340)),
        tagline_lines,
        tagline_font,
        args.muted,
        tagline_height,
        s(6),
    )

    footer_y = s(422)
    draw.rounded_rectangle(
        (s(42), footer_y, s(748), s(460)),
        radius=s(19),
        fill=args.primary,
    )
    footer_text = args.footer or args.brand
    footer_font, _, _ = fit_text(
        draw, footer_text, bold_path, s(18), s(12), s(650), s(24), 1, s(2)
    )
    draw.text(
        (content_x, footer_y + s(19)),
        footer_text,
        font=footer_font,
        fill=args.surface,
        anchor="lm",
    )

    right_center = (right_box[0] + right_box[2]) // 2
    label_font, _, _ = fit_text(
        draw, args.positions_label, bold_path, s(16), s(11), s(280), s(22), 1, s(2)
    )
    draw.text(
        (right_center, s(92)),
        args.positions_label,
        font=label_font,
        fill=args.muted,
        anchor="mm",
    )

    count_font, _, _ = fit_text(
        draw, args.position_count, bold_path, s(124), s(54), s(280), s(132), 1, s(2)
    )
    draw.text(
        (right_center, s(220)),
        args.position_count,
        font=count_font,
        fill=args.ink,
        anchor="mm",
    )
    draw.rounded_rectangle(
        (right_center - s(58), s(300), right_center + s(58), s(314)),
        radius=s(7),
        fill=args.primary,
    )
    draw.ellipse(
        (right_center - s(86), s(353), right_center - s(66), s(373)),
        fill=args.mint,
    )
    draw.ellipse(
        (right_center - s(10), s(353), right_center + s(10), s(373)),
        fill=args.primary_soft,
    )
    draw.ellipse(
        (right_center + s(66), s(353), right_center + s(86), s(373)),
        fill=args.primary,
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(args.out, format="PNG", optimize=True)
    print(f"Wrote {args.out} ({width}x{height}, 2.35:1)")


if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, ValueError) as exc:
        raise SystemExit(f"error: {exc}") from None
