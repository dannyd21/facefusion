#!/usr/bin/env python3
"""
make_icon.py — Generates a FaceFusion.icns from a programmatic PNG.

Creates a simple mask-like icon using Pillow. Replace with your own
artwork by dropping a 1024x1024 PNG at resources/icon.png before running.
"""

import os
import struct
import subprocess
import zlib
from pathlib import Path

RESOURCES = Path(__file__).parent / 'resources'
RESOURCES.mkdir(exist_ok=True)

PNG_PATH  = RESOURCES / 'icon.png'
ICNS_PATH = RESOURCES / 'FaceFusion.icns'


# ---------------------------------------------------------------------------
# Generate a simple programmatic PNG if none exists
# ---------------------------------------------------------------------------

def make_png(path: Path, size: int = 1024) -> None:
    """Draw a minimal FaceFusion-style icon using only stdlib + Pillow."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        raise SystemExit("Pillow is required: pip install Pillow")

    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background circle
    pad = size // 16
    draw.ellipse([pad, pad, size - pad, size - pad], fill='#e53935')

    # Stylised face silhouette (simple white shapes)
    cx, cy = size // 2, size // 2
    r = size // 3

    # Head outline
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill='white')

    # Dark face cut-out
    ri = int(r * 0.82)
    draw.ellipse([cx - ri, cy - ri, cx + ri, cy + ri], fill='#e53935')

    # Eyes
    ew = size // 14
    eh = size // 10
    ex_off = size // 9
    ey_off = size // 18
    for sign in (-1, 1):
        draw.ellipse(
            [cx + sign * ex_off - ew, cy - ey_off - eh,
             cx + sign * ex_off + ew, cy - ey_off + eh],
            fill='white'
        )

    # Smile arc
    sm = size // 8
    draw.arc([cx - sm, cy, cx + sm, cy + sm * 2], start=10, end=170,
             fill='white', width=size // 28)

    img.save(str(path), 'PNG')
    print(f'  Generated icon PNG: {path}')


# ---------------------------------------------------------------------------
# Convert PNG → ICNS using macOS iconutil (or a fallback pure-Python method)
# ---------------------------------------------------------------------------

ICNS_SIZES = [16, 32, 64, 128, 256, 512, 1024]
ICNS_TAGS  = {
    16:   b'icp4',
    32:   b'icp5',
    64:   b'icp6',
    128:  b'ic07',
    256:  b'ic08',
    512:  b'ic09',
    1024: b'ic10',
}


def make_icns_iconutil(png: Path, icns: Path) -> bool:
    """Use macOS iconutil (best quality). Returns False if unavailable."""
    import shutil
    if not shutil.which('iconutil'):
        return False
    try:
        from PIL import Image
    except ImportError:
        return False

    iconset = png.parent / 'FaceFusion.iconset'
    iconset.mkdir(exist_ok=True)

    img = Image.open(str(png)).convert('RGBA')
    for s in ICNS_SIZES:
        resized = img.resize((s, s), Image.LANCZOS)
        resized.save(str(iconset / f'icon_{s}x{s}.png'))
        if s <= 512:
            resized2 = img.resize((s * 2, s * 2), Image.LANCZOS)
            resized2.save(str(iconset / f'icon_{s}x{s}@2x.png'))

    result = subprocess.run(
        ['iconutil', '-c', 'icns', str(iconset), '-o', str(icns)],
        capture_output=True
    )
    # Cleanup
    import shutil; shutil.rmtree(str(iconset), ignore_errors=True)
    return result.returncode == 0


def make_icns_pure(png: Path, icns: Path) -> None:
    """Pure-Python ICNS writer (fallback when iconutil is unavailable)."""
    try:
        from PIL import Image
        import io
    except ImportError:
        raise SystemExit("Pillow is required: pip install Pillow")

    import io

    img = Image.open(str(png)).convert('RGBA')
    icon_data = b''

    for s, tag in ICNS_TAGS.items():
        resized = img.resize((s, s), Image.LANCZOS)
        buf = io.BytesIO()
        resized.save(buf, format='PNG')
        data = buf.getvalue()
        entry_len = 8 + len(data)
        icon_data += tag + struct.pack('>I', entry_len) + data

    total_len = 8 + len(icon_data)
    with open(str(icns), 'wb') as f:
        f.write(b'icns')
        f.write(struct.pack('>I', total_len))
        f.write(icon_data)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    if not PNG_PATH.exists():
        make_png(PNG_PATH)

    if not make_icns_iconutil(PNG_PATH, ICNS_PATH):
        print('  iconutil not available, using pure-Python fallback…')
        make_icns_pure(PNG_PATH, ICNS_PATH)

    print(f'  [OK] ICNS written to {ICNS_PATH}')
