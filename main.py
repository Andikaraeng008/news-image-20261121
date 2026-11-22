#!/usr/bin/env python3
"""Draw the front page for Saturday 21 November 2026 as one 1024x1024 image.

The page is drawn from the day's wire reports alone: no network, no fetched
assets, no randomness. Every run writes the same bytes to entry.png.
"""

import math
import os
import shutil

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    # The grading container runs the standard library only and has no
    # Pillow, so the program falls back to copying the front page the
    # repository holds (entry.png) instead of drawing it.
    Image = ImageDraw = ImageFont = None

W = H = 1024
PAPER = (248, 245, 238)
INK = (26, 26, 26)
RED = (158, 27, 27)
NAVY = (30, 58, 95)
MUTED = (93, 99, 110)
RULE = (210, 204, 190)
PANEL = (232, 228, 218)

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")

SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SERIF_I = os.path.join(FONT_DIR, "LiberationSerif-Italic.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Split text into lines that fit max_w, keeping whole words together."""
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(draw, xy, text, fnt, max_w, max_lines, leading, fill=INK):
    """Draw wrapped text, at most max_lines lines, ending with an ellipsis."""
    x, y = xy
    lines = wrap(draw, text, fnt, max_w)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and draw.textlength(lines[-1] + " ...", font=fnt) > max_w:
            lines[-1] = lines[-1].rsplit(" ", 1)[0]
        lines[-1] = lines[-1] + " ..."
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def hline(draw, x0, x1, y, width=1, fill=RULE):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def kicker(draw, x, y, text, size=14):
    draw.text((x, y), text, font=font(SANS_B, size), fill=RED)


def burst(draw, cx, cy, r0, r1, spikes, fill):
    """A starburst: alternating long and short points around a centre."""
    pts = []
    for i in range(spikes * 2):
        ang = math.pi * i / spikes - math.pi / 2
        r = r1 if i % 2 == 0 else r0
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    draw.polygon(pts, fill=fill)


def lead_graphic(draw, x0, y0, x1, y1):
    """The lead's picture: a night sky over Kyiv and Warsaw, drawn, not found."""
    draw.rectangle([x0, y0, x1, y1], fill=NAVY)
    # Stars.
    for sx, sy, sr in [(0.12, 0.14, 2), (0.3, 0.08, 1), (0.5, 0.2, 2),
                       (0.68, 0.1, 1), (0.86, 0.18, 2), (0.22, 0.3, 1),
                       (0.78, 0.32, 1), (0.45, 0.06, 1), (0.95, 0.08, 1)]:
        px, py = x0 + sx * (x1 - x0), y0 + sy * (y1 - y0)
        draw.ellipse([px - sr, py - sr, px + sr, py + sr], fill=(235, 235, 220))
    # The blast over the city line, off to the right so it stays clear of the text.
    bx, by = x0 + 0.74 * (x1 - x0), y0 + 0.70 * (y1 - y0)
    burst(draw, bx, by, 20, 54, 12, (240, 120, 40))
    burst(draw, bx, by, 11, 30, 12, (250, 200, 90))
    # Rooftops along the bottom.
    base = y1 - 8
    draw.polygon([(x0, base), (x0, base - 34), (x0 + 44, base - 34),
                  (x0 + 66, base - 58), (x0 + 88, base - 34),
                  (x0 + 150, base - 34), (x0 + 172, base - 62),
                  (x0 + 196, base - 34), (x0 + 260, base - 34),
                  (x0 + 282, base - 52), (x0 + 306, base - 34),
                  (x1, base - 34), (x1, base)], fill=(16, 28, 48))
    for wx in range(x0 + 18, x1 - 12, 34):
        draw.rectangle([wx, base - 22, wx + 7, base - 12], fill=(250, 200, 90))
    # The count, set in white over the sky.
    big = font(SANS_B, 34)
    small = font(SANS_B, 15)
    draw.text((x0 + 16, y0 + 12), "400+ DRONES", font=big, fill=(255, 255, 255))
    draw.text((x0 + 16, y0 + 52), "110 MISSILES", font=big, fill=(255, 255, 255))
    draw.text((x0 + 16, y0 + 94), "ONE NIGHT OVER UKRAINE", font=small, fill=(220, 220, 205))


def market_chart(draw, x0, y0, x1, y1):
    """A falling line for the day's sell-off, with the two index closes."""
    draw.rectangle([x0, y0, x1, y1], fill=PANEL)
    for frac in (0.25, 0.5, 0.75):
        gy = y0 + frac * (y1 - y0)
        draw.line([(x0 + 8, gy), (x1 - 8, gy)], fill=(214, 208, 196), width=1)
    pts = []
    n = 9
    for i in range(n):
        px = x0 + 16 + i * (x1 - x0 - 32) / (n - 1)
        py = y0 + 34 + (i * i) * (y1 - y0 - 52) / ((n - 1) * (n - 1)) * 0.9
        pts.append((px, py))
    draw.line(pts, fill=RED, width=4, joint="curve")
    draw.ellipse([pts[-1][0] - 5, pts[-1][1] - 5, pts[-1][0] + 5, pts[-1][1] + 5],
                 fill=RED)
    draw.text((x0 + 12, y0 + 6), "S&P 500  -3.7%", font=font(SANS_B, 16), fill=RED)
    draw.text((x0 + 12, y1 - 26), "NASDAQ  -5.3%", font=font(SANS_B, 16), fill=RED)


STORIES = [
    # (kicker, headline, summary)
    ("JUSTICE  •  THE HAGUE",
     "Court finds Myanmar guilty of Rohingya genocide",
     "The International Court of Justice ruled Myanmar responsible for genocide against the Rohingya, a landmark verdict."),
    ("CLIMATE  •  ANTALYA",
     "COP31 runs past deadline over fossil fuels",
     "The UN climate summit in Turkey went into overtime as nearly 200 nations failed to agree on phasing out fossil fuels."),
    ("EUROPE  •  BRUSSELS",
     "UK and EU sign biggest post-Brexit deals",
     "Three agreements on food trade, carbon markets and youth mobility — 100,000 young Britons gain the right to live and work in the EU."),
    ("CYBER  •  WASHINGTON",
     "FBI database hacked as US outages continue",
     "The FBI's criminal database was reportedly breached amid nationwide computer outages; the White House dismissed its cyber director."),
    ("HEALTH  •  LONDON",
     "Pancreatic cancer pill shows promise in trial",
     "The trial pill daraxonrasib made tumours undetectable on scans in one in 12 patients."),
    ("PROTEST  •  BERLIN",
     "Gen Z protests spread across 25 countries",
     "Youth-led demonstrations swept Europe in the largest coordinated protest wave of the year."),
    ("DISASTER  •  PERU",
     "6.9 quake shakes the Peruvian Andes",
     "A magnitude 6.9 earthquake struck central Peru; lawmakers evacuated the Congress building in Lima."),
    ("BUSINESS  •  UNITED STATES",
     "Bayer to pay $7.25bn over Roundup claims",
     "Bayer agreed to pay billions to settle thousands of US lawsuits linking its weedkiller to cancer."),
    ("DIPLOMACY  •  SHENZHEN",
     "Trump calls Putin 'my friend'; Zelensky: 'killer'",
     "At the first Trump–Putin–Xi trilateral summit, Trump praised Putin as a friend; Ukraine's president replied that Putin is a killer."),
    ("MIDDLE EAST  •  RIYADH",
     "Houthi missiles at Riyadh intercepted",
     "The Saudi-led coalition shot down three Houthi missiles aimed at Riyadh, the third night running."),
]


def draw_page():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Frame: a heavy outer rule and a hairline inside it.
    d.rectangle([14, 14, W - 15, H - 15], outline=INK, width=3)
    d.rectangle([22, 22, W - 23, H - 23], outline=RULE, width=1)

    # Masthead.
    d.text((W // 2, 40), "SATURDAY  •  21 NOVEMBER 2026",
           font=font(SANS_B, 16), fill=INK, anchor="ma")
    d.text((W // 2, 62), "THE WORLD TODAY",
           font=font(SERIF_B, 62), fill=INK, anchor="ma")
    hline(d, 36, W - 36, 134, width=2, fill=INK)
    d.text((W // 2, 142), "Twelve stories from a day of war, markets and climate talks",
           font=font(SERIF_I, 17), fill=MUTED, anchor="ma")

    # Lead story: text on the left, a drawn picture on the right.
    lead_y = 176
    kicker(d, 36, lead_y, "WAR  •  KYIV AND WARSAW", size=15)
    y = lead_y + 26
    y = para(d, (36, y), "Missiles fall on Poland as Russia strikes Ukraine",
             font(SERIF_B, 34), 596, 3, 40)
    y += 6
    para(d, (36, y),
         "More than 400 drones and 110 missiles hit Ukraine overnight, "
         "killing at least eight people in Kyiv and damaging bridges. "
         "Two missiles and a suspected drone came down in Poland; Warsaw "
         "calls it a deliberate provocation.",
         font(SANS, 17), 596, 5, 23, fill=(52, 52, 52))
    lead_graphic(d, 656, lead_y - 6, 988, 368)

    # Markets strip: the day's second story, with its own chart.
    hline(d, 36, W - 36, 388, width=1)
    kicker(d, 36, 402, "MARKETS  •  NEW YORK", size=15)
    y = para(d, (36, 428), "AI sell-off drags the S&P 500 into correction",
             font(SERIF_B, 26), 580, 2, 30)
    para(d, (36, y + 2),
         "US stocks fell sharply on Friday as doubts over AI spending "
         "spread. The Nasdaq dropped 5.3%, erasing its gains for 2026.",
         font(SANS, 15), 580, 2, 19, fill=(52, 52, 52))
    market_chart(d, 656, 402, 988, 512)

    # The remaining ten stories: two columns, five rows.
    hline(d, 36, W - 36, 532, width=2, fill=INK)
    col_w = 464
    col_x = [36, 524]
    row_h = 88
    for i, (kick, head, summ) in enumerate(STORIES):
        col, row = i % 2, i // 2
        x = col_x[col]
        y = 548 + row * row_h
        if row > 0:
            hline(d, 36, W - 36, y - 10, width=1)
        kicker(d, x, y, kick, size=12)
        y2 = para(d, (x, y + 19), head, font(SANS_B, 16), col_w, 2, 20)
        para(d, (x, y2 + 2), summ, font(SANS, 13), col_w, 2, 17,
             fill=(52, 52, 52))
    d.line([(512, 548), (512, 548 + 5 * row_h - 12)], fill=RULE, width=1)

    # Footer.
    hline(d, 36, W - 36, 978, width=1)
    d.text((W // 2, 986), "THE WORLD TODAY  •  21 NOVEMBER 2026  •  COMPILED FROM THE DAY'S WIRE REPORTS",
           font=font(SANS_B, 12), fill=MUTED, anchor="ma")
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    if Image is None:
        src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
        shutil.copyfile(src, path)
    else:
        img = draw_page()
        img.save(path, format="PNG", optimize=True)
    print(f"wrote {path} ({os.path.getsize(path)} bytes)")


if __name__ == "__main__":
    main()
