"""Build tech-carousel.svg: an animated marquee of tech logos.

Fetches each icon from skillicons.dev and embeds it as a base64 data URI,
so the final SVG is fully self-contained and animates on GitHub READMEs
(GitHub blocks externally-linked images inside SVGs, but data URIs work).

Run from the repo root:  python scripts/build_carousel.py
Output: tech-carousel.svg
"""

import base64
import math
import sys
import urllib.request

ROW1 = ["html", "js", "ts", "react", "vue", "tailwind", "flutter", "androidstudio"]
ROW2 = ["nodejs", "python", "mongodb", "mysql", "firebase", "unity", "unreal"]

CARD_W = 800
CARD_H = 136
ICON = 46
GAP = 22
STEP = ICON + GAP
SPEED = 22  # px per second


def fetch_icon(name: str) -> str:
    url = f"https://skillicons.dev/icons?i={name}"
    req = urllib.request.Request(url, headers={"User-Agent": "carousel-builder"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
    if b"<svg" not in data[:500]:
        raise RuntimeError(f"Unexpected response for icon '{name}'")
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:image/svg+xml;base64,{b64}"


def build_row(names: list[str], row_id: str, y: int, reverse: bool) -> str:
    width = len(names) * STEP
    copies = math.ceil((CARD_W + width) / width)  # enough copies to avoid gaps
    duration = round(width / SPEED, 1)

    images = []
    for i, name in enumerate(names):
        uri = fetch_icon(name)
        print(f"  embedded {name}")
        images.append(
            f'      <image x="{i * STEP}" y="0" width="{ICON}" height="{ICON}" '
            f'href="{uri}"/>'
        )

    uses = "\n".join(
        f'      <use href="#{row_id}" x="{width * c}"/>' for c in range(1, copies)
    )
    anim = "scrollR" if reverse else "scrollL"
    return (
        f'    <g transform="translate(0,{y})">\n'
        f'      <g class="{anim}" style="--loop:-{width}px; '
        f'animation-duration:{duration}s">\n'
        f'        <g id="{row_id}">\n' + "\n".join(images) + "\n        </g>\n"
        f"{uses}\n"
        f"      </g>\n"
        f"    </g>"
    )


def main() -> None:
    print("Fetching icons...")
    row1 = build_row(ROW1, "r1", 16, reverse=False)
    row2 = build_row(ROW2, "r2", 76, reverse=True)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{CARD_W}" height="{CARD_H}" viewBox="0 0 {CARD_W} {CARD_H}" role="img" aria-label="Scrolling carousel of languages and tools">
  <style>
    .scrollL {{ animation-name: toLeft; animation-timing-function: linear; animation-iteration-count: infinite; }}
    .scrollR {{ animation-name: toRight; animation-timing-function: linear; animation-iteration-count: infinite; }}
    @keyframes toLeft {{ from {{ transform: translateX(0); }} to {{ transform: translateX(var(--loop)); }} }}
    @keyframes toRight {{ from {{ transform: translateX(var(--loop)); }} to {{ transform: translateX(0); }} }}
  </style>
  <defs>
    <clipPath id="card"><rect x="0" y="0" width="{CARD_W}" height="{CARD_H}" rx="16"/></clipPath>
    <linearGradient id="fadeL" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#0d1117" stop-opacity="1"/>
      <stop offset="1" stop-color="#0d1117" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="fadeR" x1="1" y1="0" x2="0" y2="0">
      <stop offset="0" stop-color="#0d1117" stop-opacity="1"/>
      <stop offset="1" stop-color="#0d1117" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <rect x="0" y="0" width="{CARD_W}" height="{CARD_H}" rx="16" fill="#0d1117" stroke="#21262d" stroke-width="1"/>
  <g clip-path="url(#card)">
{row1}
{row2}
    <rect x="0" y="0" width="56" height="{CARD_H}" fill="url(#fadeL)"/>
    <rect x="{CARD_W - 56}" y="0" width="56" height="{CARD_H}" fill="url(#fadeR)"/>
  </g>
</svg>
"""
    with open("tech-carousel.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("Wrote tech-carousel.svg")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        print(f"Failed: {exc}", file=sys.stderr)
        sys.exit(1)
