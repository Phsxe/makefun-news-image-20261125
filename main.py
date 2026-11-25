#!/usr/bin/env python3
"""news-image-20261125 -- front page for 25 Nov 2026.

Renders a 1024x1024 one-bit-thresholded front page: 25 news items,
6 regions, 3 headline cards, 8 small cards, 14 ALSO items, a UTC wire
line, a stats bar, region counts and a DATE CHECK box. All text is
rendered at runtime from the DejaVu fonts (thresholded at 128); the
PNG is encoded by hand (filter 0 per row, zlib level 9) so the output
is byte stable. No network, no randomness, no timestamps.
"""
import hashlib
import struct
import zlib

import numpy as np
from PIL import ImageFont

W = 1024
H = 1024

BG = (246, 241, 229)
INK = (32, 33, 31)
NAVY = (28, 48, 92)
GRAY = (120, 118, 110)
SLATE = (90, 90, 110)
RED = (178, 44, 34)
TEAL = (56, 103, 122)
OCHRE = (176, 124, 10)
GREEN = (32, 89, 71)
BLUE = (46, 74, 122)
ORANGE = (198, 96, 32)
BRICK = (162, 72, 54)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
F60B = ImageFont.truetype(FONT_DIR + "DejaVuSans-Bold.ttf", 60)
F34B = ImageFont.truetype(FONT_DIR + "DejaVuSans-Bold.ttf", 34)
F28B = ImageFont.truetype(FONT_DIR + "DejaVuSans-Bold.ttf", 28)
F20B = ImageFont.truetype(FONT_DIR + "DejaVuSans-Bold.ttf", 20)
F20 = ImageFont.truetype(FONT_DIR + "DejaVuSans.ttf", 20)
F14 = ImageFont.truetype(FONT_DIR + "DejaVuSans.ttf", 14)

img = np.zeros((H, W, 3), dtype=np.uint8)
img[:, :] = BG


def rect(x0, y0, x1, y1, color):
    img[y0:y1 + 1, x0:x1 + 1] = color


def text(x0, y0, s, font, color):
    """Draw text, one glyph at a time. Each glyph is rendered with
    font.getmask2, thresholded at 128, and pasted so the ink bbox
    lands at cursor + (ink_left - raw_left). Advance is
    round(font.getlength(ch)). Space advances only."""
    x = x0
    for ch in s:
        adv = round(font.getlength(ch))
        if ch == " ":
            x += adv
            continue
        mask, off = font.getmask2(ch)
        m = np.array(mask, dtype=np.uint8).reshape(mask.size[1], mask.size[0])
        rb = mask.getbbox()
        ink = m >= 128
        ys, xs = np.where(ink)
        ix0, iy0 = int(xs.min()), int(ys.min())
        sub = ink[iy0:, ix0:]
        px0 = x + (ix0 - rb[0])
        py0 = y0 + off[1] + iy0
        hh, ww = sub.shape
        region = img[py0:py0 + hh, px0:px0 + ww]
        region[sub] = color
        x += adv


def bar(x, y0, color, h=14):
    img[y0:y0 + h, x] = color


def poly(points, color):
    """Fill a polygon; a pixel is filled iff its centre is inside."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x0 = max(int(min(xs)), 0)
    x1 = min(int(max(xs)) + 1, W - 1)
    y0 = max(int(min(ys)), 0)
    y1 = min(int(max(ys)) + 1, H - 1)
    yy, xx = np.mgrid[y0:y1 + 1, x0:x1 + 1]
    cx = xx + 0.5
    cy = yy + 0.5
    inside = np.zeros(cx.shape, dtype=bool)
    n = len(points)
    j = n - 1
    for i in range(n):
        xi, yi = points[i]
        xj, yj = points[j]
        if yi == yj:
            j = i
            continue
        cond = ((yi > cy) != (yj > cy)) & (cx < (xj - xi) * (cy - yi) / (yj - yi) + xi)
        inside ^= cond
        j = i
    region = img[y0:y1 + 1, x0:x1 + 1]
    region[inside] = color


def circle(cx, cy, r, color):
    """Fill a circle; a pixel is filled iff its centre is inside."""
    x0 = max(int(cx - r), 0)
    x1 = min(int(cx + r) + 1, W - 1)
    y0 = max(int(cy - r), 0)
    y1 = min(int(cy + r) + 1, H - 1)
    yy, xx = np.mgrid[y0:y1 + 1, x0:x1 + 1]
    d2 = (xx + 0.5 - cx) ** 2 + (yy + 0.5 - cy) ** 2
    inside = d2 <= r * r
    region = img[y0:y1 + 1, x0:x1 + 1]
    region[inside] = color




# ---- page rules ----
rect(20, 94, 1003, 95, NAVY)
rect(20, 130, 1003, 130, GRAY)
rect(20, 178, 1003, 179, NAVY)
rect(20, 664, 1003, 665, RED)
rect(20, 890, 1003, 890, GRAY)

# ---- title ----
text(55, 15, "WEDNESDAY, 25 NOV 2026", F60B, NAVY)

# ---- wire line ----
text(20, 106, "WIRE TIMES UTC", F14, INK)
text(166, 106, "00:18 SHENZHOU LAUNCH", F14, INK)
text(384, 106, "00:30 AUS CPI +4.9%", F14, INK)
text(564, 106, "02:12 SAMARA FIRES", F14, INK)
text(743, 106, "03:56 SHENZHOU DOCKS", F14, INK)
for bx in (150, 368, 548, 727):
    bar(bx, 108, INK)

# ---- stats ----
text(134, 127, "+4.9%", F28B, RED)
text(468, 127, "-5.3%", F28B, RED)
text(787, 127, "$90.97", F28B, RED)
text(94, 158, "AUSTRALIA CPI - OCT, Y/Y", F14, INK)
text(439, 158, "KOSPI - TARIFF ROUT", F14, INK)
text(740, 158, "BRENT CRUDE - DOWN 0.5%", F14, INK)
rect(348, 136, 348, 171, GRAY)
rect(676, 136, 676, 171, GRAY)

# ---- headline cards ----
HEAD = [
    # (x0, x1, top-rule color, title1, title2, deck1, deck2, src1, barx, src2)
    (20, 337, NAVY, "TIANGONG", "FIRST GUEST",
     "Shenzhou-24 docks 03:56", "UTC; first Pakistani in space.",
     "JIUQUAN", 98, "REUTERS"),
    (348, 699, RED, "UKRAINE HITS", "REFINERIES",
     "Fires at two Rosneft plants in", "Samara region.",
     "SAMARA", 428, "KYIV IND."),
    (710, 1003, TEAL, "STRIKES HIT", "HODEIDAH",
     "Coalition hits port; 4", "drones intercepted.",
     "HODEIDAH", 807, "REUTERS"),
]
for (cx0, cx1, topc, t1, t2, d1, d2, s1, barx, s2) in HEAD:
    rect(cx0, 180, cx1, 180, INK)
    rect(cx0 + 1, 181, cx1 - 1, 184, topc)
    rect(cx0, 180, cx0, 389, INK)
    rect(cx1, 180, cx1, 389, INK)
    rect(cx0, 389, cx1, 389, INK)
    text(cx0 + 10, 239, t1, F34B, INK)
    text(cx0 + 10, 277, t2, F34B, INK)
    text(cx0 + 10, 322, d1, F20, INK)
    text(cx0 + 10, 345, d2, F20, INK)
    text(cx0 + 10, 371, s1, F14, GRAY)
    bar(barx, 373, GRAY)
    text(barx + 12, 371, s2, F14, GRAY)

# ---- small cards ----
SMALL = [
    # (cx, top-rule color, title1, title2, deck1, deck2, src1, barx, src2)
    (20, RED, "AUSTRALIA CPI", "+4.9% IN OCT",
     "Fastest in 3 years;", "RBA hike on table.", "CANBERRA", 132, "ABS"),
    (268, BRICK, "ASIA STOCKS", "TUMBLE -5.3%",
     "MSCI Asia ex-Japan", "-2.3%; Nikkei -2.9%.", "TOKYO", 350, "REUTERS"),
    (516, GREEN, "SEOUL STRIKE", "CALLED OFF",
     "Metro unions agree", "+3.5% pay; 500 jobs.", "SEOUL", 596, "KOREA HERALD"),
    (764, BLUE, "SOLOMONS PACT", "SIGNED",
     "Australia is lead", "partner; A$740m.", "CANBERRA", 876, "PM OFFICE"),
    (20, ORANGE, "HOUTHI THREAT", "TO JEDDAH",
     "Threatens Jeddah, all", "Red Sea ports.", "SANAA", 102, "REUTERS"),
    (268, TEAL, "CALIFORNIA", "KING TIDES",
     "Floods to 3 ft; waves", "to 30 ft.", "CALIFORNIA", 386, "NWS"),
    (516, OCHRE, "PETE EDOCHIE", "DIES AT 79",
     "Nollywood icon dies", "aged 79.", "ENUGU", 599, "CHANNELS TV"),
    (764, SLATE, "JAPAN SERVICES", "PPI +4.2%",
     "Fastest since 1990;", "BOJ hike case grows.", "TOKYO", 846, "REUTERS"),
]
for i, (cx, topc, t1, t2, d1, d2, s1, barx, s2) in enumerate(SMALL):
    y0 = 396 if i < 4 else 516
    y1 = 509 if i < 4 else 629
    rect(cx, y0, cx + 239, y0, INK)
    rect(cx, y1, cx + 239, y1, INK)
    rect(cx, y0, cx, y1, INK)
    rect(cx + 239, y0, cx + 239, y1, INK)
    rect(cx + 1, y0 + 1, cx + 238, y0 + 3, topc)
    text(cx + 8, y0 + 4, t1, F20B, INK)
    text(cx + 8, y0 + 25, t2, F20B, INK)
    text(cx + 8, y0 + 47, d1, F20, INK)
    text(cx + 8, y0 + 67, d2, F20, INK)
    rect(cx + 8, y0 + 95, cx + 17, y0 + 104, topc)
    text(cx + 24, y0 + 93, s1, F14, GRAY)
    bar(barx, y0 + 95, GRAY)
    text(barx + 12, y0 + 93, s2, F14, GRAY)

# ---- MORE line ----
text(20, 636, "14 MORE STORIES | 25 TOTAL | 6 REGIONS", F20B, INK)

# ---- ALSO list ----
ALSO_L = [
    ("12", "India condemns Riyadh tower attack", "TOI", 482),
    ("13", "Lamarre-Condon guilty of murder", "BBC", 476),
    ("14", "Australia sorry to LGBTQ veterans", "REUTERS", 440),
    ("15", "Oil falls: Brent $90.97, WTI $81.58", "REUTERS", 440),
    ("16", "Gold $3,544.54 ahead of US PCE", "REUTERS", 440),
    ("17", "US shelves Russia business deals: FT", "REUTERS", 440),
    ("18", "EU debates 1.582tn budget plan", "POLLAR", 451),
]
ALSO_R = [
    ("19", "Indonesia gold-mine rescue goes on", "REUTERS", 938),
    ("20", "Citi UK risk chief stands down", "REUTERS", 938),
    ("21", "Nikkei to rise in 2027, below record", "REUTERS", 938),
    ("22", "Korea births +12.2% in September", "YONHAP", 945),
    ("23", "Honkai: Nexus Anima beta opens", "HOYOVERSE", 915),
    ("24", "GoVeda launches AI IP agent", "PRNEWSWIRE", 907),
    ("25", "Horn Island: all 6 dead, search ends", "USCG", 964),
]
for r, (num, txt, src, sx) in enumerate(ALSO_L):
    y = 668 + r * 30
    text(20, y, num, F20B, RED)
    text(56, y, txt, F20, INK)
    text(sx, y + 4, src, F14, GRAY)
for r, (num, txt, src, sx) in enumerate(ALSO_R):
    y = 668 + r * 30
    text(518, y, num, F20B, RED)
    text(554, y, txt, F20, INK)
    text(sx, y + 4, src, F14, GRAY)

# ---- region counts ----
text(197, 900, "ASIA-PACIFIC 13", F14, INK)
text(332, 900, "EUROPE 4", F14, INK)
text(423, 900, "MIDDLE EAST 3", F14, INK)
text(553, 900, "AMERICAS 2", F14, INK)
text(661, 900, "AFRICA 1", F14, INK)
text(747, 900, "MARKETS 2", F14, INK)
for bx in (320, 411, 541, 649, 735):
    bar(bx, 902, INK)

# ---- DATE CHECK box ----
rect(20, 936, 1003, 936, INK)
rect(20, 1003, 1003, 1003, INK)
rect(20, 936, 20, 1003, INK)
rect(1003, 936, 1003, 1003, INK)
rect(21, 937, 23, 1002, RED)
text(34, 940, "DATE CHECK: EVERY STORY IS 25 NOV 2026", F20B, INK)
text(34, 962, "LOCAL DATE WHERE IT HAPPENED; UTC FOR GLOBAL", F20B, INK)
text(34, 988, "SEOUL DEAL + EDOCHIE DEATH: 25 NOV LOCAL, 24 NOV UTC. HORN ISLAND: CRASH 24 NOV, USCG CONFIRMED 6 DEAD 25 NOV.", F14, GRAY)

# ---- illustration card 1: satellite + rocket ----
rect(30, 190, 327, 239, NAVY)
for (sx, sy) in ((82, 195), (214, 195), (38, 196), (170, 196), (302, 196),
                 (126, 197), (258, 197), (192, 202), (280, 202), (104, 204),
                 (236, 204), (148, 205), (60, 206)):
    rect(sx, sy, sx + 1, sy + 1, BG)
rect(133, 216, 170, 223, BG)
rect(187, 216, 224, 223, BG)
rect(171, 210, 186, 229, OCHRE)
circle(179.5, 220.5, 5, RED)
poly([(294, 193.5), (287.5, 206.75), (301, 206.75)], ORANGE)
rect(289, 206, 298, 223, BG)
poly([(288.8, 224), (294.5, 223.8), (284.5, 233.5)], OCHRE)
poly([(294.5, 223.6), (299.5, 223.6), (304, 233)], OCHRE)

# ---- illustration card 2: chimneys + smoke ----
rect(358, 190, 689, 233, SLATE)
rect(358, 234, 689, 239, INK)
for dx in (0, 166):
    rect(427 + dx, 212, 454 + dx, 233, GRAY)
    rect(423 + dx, 206, 458 + dx, 211, INK)
    rect(433 + dx, 194, 448 + dx, 201, INK)
    poly([(441 + dx, 191.8), (430.2 + dx, 207), (452 + dx, 207)], ORANGE)
    poly([(441 + dx, 197.7), (435.2 + dx, 207), (447 + dx, 207)], RED)
circle(524.5, 200.5, 7, BG)
circle(536.5, 196.5, 5, BG)

# ---- illustration card 3: port + cranes ----
rect(720, 228, 993, 239, TEAL)
rect(788, 196, 790, 227, INK)
rect(925, 196, 927, 227, INK)
# crane arms, one horizontal run per row (measured from the approved image)
DIAG1L = [(196, 787, 787), (197, 784, 786), (198, 782, 783), (199, 779, 781),
          (200, 776, 778), (201, 773, 775), (202, 771, 772), (203, 768, 770)]
DIAG1R = [(197, 791, 792), (198, 793, 795), (199, 796, 797), (200, 798, 800),
          (201, 801, 803), (202, 804, 806), (203, 807, 809), (204, 810, 812),
          (205, 813, 814), (206, 815, 817), (207, 818, 820), (208, 821, 822)]
DIAG2L = [(196, 924, 924), (197, 921, 923), (198, 919, 920), (199, 916, 918),
          (200, 913, 915), (201, 910, 912), (202, 908, 909), (203, 905, 907),
          (204, 903, 904)]
DIAG2R = [(197, 928, 929), (198, 930, 932), (199, 933, 934), (200, 935, 937),
          (201, 938, 940), (202, 941, 943), (203, 944, 946), (204, 947, 949),
          (205, 950, 951), (206, 952, 954), (207, 955, 957), (208, 958, 959)]
for (y, x0, x1) in DIAG1L + DIAG1R + DIAG2L + DIAG2R:
    rect(x0, y, x1, y, INK)
rect(818, 208, 819, 215, INK)
rect(955, 208, 956, 217, INK)
rect(748, 204, 787, 215, OCHRE)
rect(728, 216, 767, 227, RED)
rect(772, 216, 811, 227, GREEN)
rect(816, 216, 855, 227, BLUE)
rect(814, 218, 815, 223, RED)
rect(951, 218, 958, 223, RED)


def encode_png(rgb):
    h, w, _ = rgb.shape
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw += rgb[y].tobytes()
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        c += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        return c

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    return png


if __name__ == "__main__":
    data = encode_png(img)
    with open("out.png", "wb") as f:
        f.write(data)
    print("sha256:", hashlib.sha256(data).hexdigest())
    print("bytes:", len(data))
