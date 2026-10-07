#!/usr/bin/env python3
"""Convert a transparent head cutout into an animated ASCII SVG.

Run without arguments to regenerate from the included character grid:
  python scripts/make_portrait.py
To use a different transparent PNG (optional Pillow dependency):
  python scripts/make_portrait.py --photo /path/to/head-cutout.png
The photograph is never embedded in the SVG or copied into the repository.
"""
import argparse
from html import escape
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRID = ROOT / 'data/portrait.json'

def photo_to_grid(path):
    from PIL import Image, ImageOps
    image = Image.open(path).convert('RGBA')
    bbox = image.getchannel('A').point(lambda a: 255 if a > 100 else 0).getbbox()
    if bbox is None:
        raise ValueError('The photo is fully transparent')
    # Sample the supplied pixels into characters; keep the original photo untouched.
    image = image.crop(bbox)
    width, height = image.size
    rows = 76
    columns = round(rows * (width / height) / 0.55)
    image = image.resize((columns, rows), Image.Resampling.LANCZOS)
    gray = ImageOps.autocontrast(image.convert('L'), cutoff=1)
    alpha = image.getchannel('A')
    ramp = ' .:-=+*oO0#%@'
    lines = []
    for y in range(rows):
        line = ''
        for x in range(columns):
            coverage = alpha.getpixel((x,y)) / 255
            # Bright areas receive denser light glyphs. Transparent pixels stay blank.
            intensity = (gray.getpixel((x,y)) / 255) ** 0.65
            intensity = max(0, min(1, (intensity - 0.11) / 0.73))
            index = round(intensity * (len(ramp)-1))
            line += ramp[index] if coverage > .40 else ' '
        lines.append(line)
    return {'name':'Geetha Bonthu', 'columns':columns, 'rows':rows,
            'source':'Character grid sampled from the supplied portrait after background isolation.',
            'lines':lines}

def render_svg(data):
    columns, rows = data['columns'], data['rows']
    line_height = 455 / rows
    glyph_width = line_height * .55
    font_size = glyph_width / .60
    draw_width = columns * glyph_width
    left = (440 - draw_width)/2
    top = 51
    duration = 2.9
    parts = [
      '<svg xmlns="http://www.w3.org/2000/svg" width="440" height="540" viewBox="0 0 440 540" role="img" aria-labelledby="portrait-title portrait-desc">',
      f'<title id="portrait-title">{escape(data["name"])} — animated ASCII portrait</title>',
      '<desc id="portrait-desc">A monochrome portrait made from individual text characters, revealed from top to bottom. Animation plays once and remains visible. A complete portrait is shown when reduced motion is enabled.</desc>',
      '<style>text{font-family:"Courier New",Courier,monospace}.ascii-line{white-space:pre;font-variant-ligatures:none;font-weight:700;font-family:"Courier New",Courier,monospace;opacity:1;animation:portrait-print .12s linear both;animation-delay:var(--delay)}@keyframes portrait-print{from{opacity:0}to{opacity:1}}.scan{opacity:0;animation:portrait-scan 2.9s linear .15s both}@keyframes portrait-scan{0%{opacity:.65;transform:translateY(0)}98%{opacity:.65}100%{opacity:0;transform:translateY(455px)}}@media(prefers-reduced-motion:reduce){.ascii-line,.scan{animation:none}.scan{display:none}}</style>',
      '<rect x=".5" y=".5" width="439" height="539" rx="7" fill="#0d1117" stroke="#21262d"/>',
      '<path d="M1 31H439M1 512H439" stroke="#21262d"/>',
      '<circle cx="13" cy="16" r="3" fill="#ef6a60"/><circle cx="25" cy="16" r="3" fill="#e5c052"/><circle cx="37" cy="16" r="3" fill="#53bd68"/>',
      '<text x="220" y="19" text-anchor="middle" font-size="7.5" fill="#84919f">geetha@github:~ $ ./portrait.sh</text>',
      '<g fill="#eef3f8" xml:space="preserve">',
    ]
    for row, line in enumerate(data['lines']):
        y = top + row*line_height
        delay = .15 + (row/(rows-1))*duration
        parts.append(f'<text class="ascii-line" x="{left:.3f}" y="{y:.3f}" font-size="{font_size:.4f}" style="--delay:{delay:.3f}s">{escape(line)}</text>')
    parts.extend(['</g>',f'<rect class="scan" x="{left:.3f}" y="{top+1}" width="{draw_width:.3f}" height=".6" fill="#7ee787"/>',
      '<text x="12" y="530" font-size="7.5" fill="#8996a5">ascii://geetha  ·  photo → characters</text>',
      '<rect x="417" y="522" width="6" height="9" fill="#39d353"/>','</svg>'])
    return '\n'.join(parts)+'\n'

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--photo',type=Path)
    args=parser.parse_args()
    if args.photo:
        data=photo_to_grid(args.photo)
        GRID.write_text(json.dumps(data,indent=2)+'\n')
    else:
        data=json.loads(GRID.read_text())
    output=ROOT/'assets/portrait.svg'
    output.write_text(render_svg(data),encoding='utf-8')
    print(f'Generated {output.name}: {data["columns"]} columns × {data["rows"]} rows')

if __name__=='__main__':
    main()
