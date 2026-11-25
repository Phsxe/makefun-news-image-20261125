#!/usr/bin/env python3
"""Render the make.fun news-image-20261125 entry: a 1024x1024 newspaper front page.

25 stories, 6 regions, 3 headline cards, 8 short cards, 14 ALSO items,
a UTC wire line, a numbers bar, a region count bar and a DATE CHECK box.

Everything is drawn from scratch in this session. Glyph bitmaps are NOT
stored as data: they are generated at runtime from the system DejaVu fonts
(/usr/share/fonts/truetype/dejavu/), rendered with PIL and thresholded to
1-bit, exactly as the approved image was built. Text is placed glyph by
glyph at measured pen positions (the per-glyph x offsets in TEXT below),
because PIL's fractional advances do not land on the same integer pixels.

Deterministic: no network, no randomness, no timestamps. Running this
script twice produces byte-identical output.

Usage: python3 main.py   (writes out/entry.png next to this file)
"""

import hashlib
import os
import struct
import zlib

import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- palette
BG = (246, 241, 229)     # paper
INK = (32, 33, 31)       # body text / borders
GRAY = (120, 118, 110)   # secondary text / rules
RED = (178, 44, 34)      # accent / card 1
DBLUE = (28, 48, 92)     # masthead / card 1 top
TEAL = (56, 103, 122)    # card 3 top / water
GOLD = (176, 124, 10)    # card r2c3 top / flames
GREEN = (32, 89, 71)     # card r1c3 top / container
MBLUE = (46, 74, 122)    # card r1c4 top / container
ORANGE = (198, 96, 32)   # card r2c1 top / rocket nose / flame
RUST = (162, 72, 54)     # card r1c2 top
GBLUE = (90, 90, 110)    # card r2c4 top / sky

W = H = 1024

REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# ---------------------------------------------------------------- canvas
arr = np.full((H, W, 3), BG, dtype=np.uint8)


def rect(x0, y0, x1, y1, color):
    """Fill an inclusive rectangle."""
    arr[y0:y1 + 1, x0:x1 + 1] = color


def disc(cx, cy, r, color):
    """Fill a true geometric disc: pixels whose centres satisfy dx^2+dy^2<=r^2.

    PIL's ellipse rasterises differently (it is fatter at the poles), so
    circles are drawn with this distance test instead.
    """
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                arr[y, x] = color


def paste_bitmap(rows, x0, y0, mapping):
    """Paste a small ASCII bitmap; each char maps to a colour in mapping."""
    for dy, row in enumerate(rows):
        for dx, ch in enumerate(row):
            if ch in mapping:
                arr[y0 + dy, x0 + dx] = mapping[ch]


# ------------------------------------------------- glyphs, made at runtime
_fontcache = {}
_glyphcache = {}


def font(path, size):
    key = (path, size)
    if key not in _fontcache:
        _fontcache[key] = ImageFont.truetype(path, size)
    return _fontcache[key]


def glyph(f, size, ch):
    """Render one glyph with PIL and threshold to 1-bit.

    Returns (bitmap, ox, oy): the tight 1-bit bitmap plus the offset of its
    top-left ink pixel relative to the draw origin. The bitmap is generated
    fresh from the system font file every run; nothing is stored.
    """
    key = (id(f), size, ch)
    if key in _glyphcache:
        return _glyphcache[key]
    cs = max(100, size * 3 + 20)
    c = cs // 2
    img = Image.new("L", (cs, cs), 0)
    dd = ImageDraw.Draw(img)
    dd.text((c, c), ch, font=f, fill=255)
    a = np.array(img) >= 128
    ys, xs = np.where(a)
    if len(xs) == 0:
        _glyphcache[key] = None
        return None
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    out = (a[y0:y1 + 1, x0:x1 + 1], x0 - c, y0 - c)
    _glyphcache[key] = out
    return out


def paste_text(text, f, size, color, y0, pens):
    """Paste one line of text glyph by glyph at the measured pen positions.

    pens[i] is the draw x for text[i]; None means a space (skip).
    """
    for i, ch in enumerate(text):
        if ch == " ":
            continue
        pen = pens[i]
        if pen is None:
            continue
        g = glyph(f, size, ch)
        if g is None:
            continue
        tmpl, ox, oy = g
        h, w = tmpl.shape
        px, py = pen + ox, y0 + oy
        if px < 0 or py < 0 or px + w > W or py + h > H:
            continue
        region = arr[py:py + h, px:px + w]
        region[tmpl] = color


# ------------------------------------------------------------- PNG writing
def save_png(path):
    """Write the canvas as a PNG with filter 0 on every row, zlib level 9.

    That is the exact encoding of the approved image: no per-row filter
    selection, maximum compression. It makes the output byte-identical.
    """
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += arr[y].tobytes()
    idat = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        out = struct.pack(">I", len(data)) + typ + data
        out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", idat)
        + chunk(b"IEND", b"")
    )
    with open(path, "wb") as fh:
        fh.write(png)
    return png
TEXT = [
    # also12_num
    ('12', 'B', 20, RED, 668, [18,33]),
    # also12_src
    ('TOI', 'R', 14, GRAY, 672, [483,491,501]),
    # also12_title
    ('India condemns Riyadh tower attack', 'R', 20, INK, 668, [55,61,74,87,93,None,111,122,134,147,160,172,191,204,None,220,234,241,252,264,277,None,297,304,317,332,344,None,358,371,379,386,398,409]),
    # also13_num
    ('13', 'B', 20, RED, 698, [18,33]),
    # also13_src
    ('BBC', 'R', 14, GRAY, 702, [475,485,496]),
    # also13_title
    ('Lamarre-Condon guilty of murder', 'R', 20, INK, 698, [55,66,78,97,109,117,125,138,144,158,170,183,196,208,None,227,240,253,259,266,274,None,291,304,None,316,335,348,356,369,381]),
    # also14_num
    ('14', 'B', 20, RED, 728, [18,34]),
    # also14_src
    ('REUTERS', 'R', 14, GRAY, 732, [439,449,458,470,477,486,497]),
    # also14_title
    ('Australia sorry to LGBTQ veterans', 'R', 20, INK, 728, [56,69,82,93,100,108,120,126,132,None,150,160,172,180,189,None,207,214,None,232,243,259,275,285,None,308,319,332,339,351,359,371,384]),
    # also15_num
    ('15', 'B', 20, RED, 758, [18,33]),
    # also15_src
    ('REUTERS', 'R', 14, GRAY, 762, [439,449,458,470,477,486,497]),
    # also15_title
    ('Oil falls: Brent $90.97, WTI $81.58', 'R', 20, INK, 758, [55,71,77,None,90,96,108,114,120,129,None,143,157,165,177,191,None,204,217,230,242,249,262,275,None,288,309,319,None,331,344,356,369,376,389]),
    # also16_num
    ('16', 'B', 20, RED, 788, [18,33]),
    # also16_src
    ('REUTERS', 'R', 14, GRAY, 792, [439,449,458,470,477,486,497]),
    # also16_title
    ('Gold $3,544.54 ahead of US PCE', 'R', 20, INK, 788, [55,71,83,89,None,108,121,134,140,154,167,178,185,199,None,217,229,242,254,266,None,285,298,None,310,325,None,344,356,370]),
    # also17_num
    ('17', 'B', 20, RED, 818, [18,33]),
    # also17_src
    ('REUTERS', 'R', 14, GRAY, 822, [439,449,458,470,477,486,497]),
    # also17_title
    ('US shelves Russia business deals: FT', 'R', 20, INK, 818, [55,70,None,89,99,112,124,131,142,154,None,170,184,197,207,217,223,None,241,254,267,277,283,296,308,318,None,334,347,359,371,377,386,None,400,414]),
    # also18_num
    ('18', 'B', 20, RED, 848, [18,33]),
    # also18_src
    ('POLLAR', 'R', 14, GRAY, 852, [450,459,469,477,486,495]),
    # also18_title
    ('EU debates 1.582tn budget plan', 'R', 20, INK, 848, [55,68,None,89,102,114,127,140,147,159,None,174,187,194,207,220,234,241,None,260,273,286,299,312,325,None,338,351,357,369]),
    # also19_num
    ('19', 'B', 20, RED, 668, [516,531]),
    # also19_src
    ('REUTERS', 'R', 14, GRAY, 672, [937,947,956,968,975,984,995]),
    # also19_title
    ('Indonesia gold-mine rescue goes on', 'R', 20, INK, 668, [553,559,572,585,597,610,622,632,638,None,656,669,681,687,701,707,726,732,745,None,763,771,783,793,804,817,None,835,848,860,872,None,888,900]),
    # also20_num
    ('20', 'B', 20, RED, 698, [517,532]),
    # also20_src
    ('REUTERS', 'R', 14, GRAY, 702, [937,947,956,968,975,984,995]),
    # also20_title
    ('Citi UK risk chief stands down', 'R', 20, INK, 698, [553,567,574,581,None,593,608,None,627,635,641,651,None,669,680,693,699,712,None,724,735,742,754,767,780,None,796,809,822,837]),
    # also21_num
    ('21', 'B', 20, RED, 728, [517,530]),
    # also21_src
    ('REUTERS', 'R', 14, GRAY, 732, [937,947,956,968,975,984,995]),
    # also21_title
    ('Nikkei to rise in 2027, below record', 'R', 20, INK, 728, [553,568,574,586,598,610,None,623,630,None,648,656,662,672,None,690,696,None,715,728,741,754,767,None,779,792,804,810,823,None,844,852,864,875,887,895]),
    # also22_num
    ('22', 'B', 20, RED, 758, [517,531]),
    # also22_src
    ('YONHAP', 'R', 14, GRAY, 762, [945,954,964,974,986,995]),
    # also22_title
    ('Korea births +12.2% in September', 'R', 20, INK, 758, [553,566,578,586,598,None,616,629,635,644,651,664,None,679,696,710,722,729,742,None,767,773,None,792,805,817,831,838,850,869,882,894]),
    # also23_num
    ('23', 'B', 20, RED, 788, [517,531]),
    # also23_src
    ('HOYOVERSE', 'R', 14, GRAY, 792, [914,926,937,946,957,966,975,986,994]),
    # also23_title
    ('Honkai: Nexus Anima beta opens', 'R', 20, INK, 788, [553,568,580,593,605,617,622,None,636,651,664,675,688,None,705,718,731,737,756,None,774,787,800,807,None,825,837,850,862,875]),
    # also24_num
    ('24', 'B', 20, RED, 818, [517,532]),
    # also24_src
    ('PRNEWSWIRE', 'R', 14, GRAY, 822, [906,914,924,934,944,958,967,980,984,994]),
    # also24_title
    ('GoVeda launches AI IP agent', 'R', 20, INK, 818, [553,569,582,595,607,620,None,638,644,656,669,682,693,706,718,None,735,748,None,760,766,None,784,796,809,821,835]),
    # also25_num
    ('25', 'B', 20, RED, 848, [517,531]),
    # also25_src
    ('USCG', 'R', 14, GRAY, 852, [963,974,983,993]),
    # also25_title
    ('Horn Island: all 6 dead, search ends', 'R', 20, INK, 848, [553,568,580,588,None,607,613,623,629,641,654,666,None,680,692,698,None,710,None,729,742,754,766,779,None,791,801,813,825,833,844,None,863,875,888,901]),
    # also_head
    ('14 MORE STORIES | 25 TOTAL | 6 REGIONS', 'B', 20, INK, 636, [18,34,None,54,74,91,106,None,127,142,155,172,187,194,208,None,228,None,243,257,None,279,292,310,324,338,None,357,None,372,None,393,408,422,438,445,462,479]),
    # dc1
    ('DATE CHECK: EVERY STORY IS 25 NOV 2026', 'B', 20, INK, 940, [33,51,66,79,None,100,115,132,146,161,176,None,192,207,221,235,252,None,271,286,299,316,333,None,352,359,None,380,394,None,415,432,450,None,471,486,499,513]),
    # dc2
    ('LOCAL DATE WHERE IT HAPPENED; UTC FOR GLOBAL', 'B', 20, INK, 962, [33,46,63,79,93,None,113,131,146,159,None,181,202,219,233,248,None,269,277,None,297,315,329,344,359,373,390,404,421,None,436,453,466,None,488,502,519,None,541,557,570,587,603,617]),
    # dc3
    ('SEOUL DEAL + EDOCHIE DEATH: 25 NOV LOCAL, 24 NOV UTC. HORN ISLAND: CRASH 24 NOV, USCG CONFIRMED 6 DEAD 25 NOV.', 'R', 14, GRAY, 988, [34,42,52,62,72,None,84,95,105,114,None,126,None,142,151,163,174,183,194,198,None,211,222,232,243,250,261,None,270,279,None,292,303,314,None,327,336,347,357,366,374,None,382,392,None,404,415,426,None,439,451,459,468,None,476,488,498,508,None,522,527,535,544,553,563,574,None,584,593,604,614,622,None,637,647,None,659,670,681,690,None,698,709,718,728,None,743,753,763,773,781,785,795,807,816,None,831,None,844,855,865,874,None,889,898,None,911,922,933,942]),
    # hc1_body1
    ('Shenzhou-24 docks 03:56', 'R', 20, INK, 322, [29,42,55,67,81,90,103,115,129,135,149,None,167,180,192,203,215,None,231,244,256,264,277]),
    # hc1_body2
    ('UTC; first Pakistani in space.', 'R', 20, INK, 345, [29,46,56,70,None,84,90,96,104,115,None,128,140,152,164,170,181,188,200,213,None,225,231,None,250,260,273,285,296,307]),
    # hc1_src
    ('JIUQUAN | REUTERS', 'R', 14, GRAY, 371, [31,33,37,48,58,69,78,None,96,None,109,119,128,140,147,156,167]),
    # hc1_title1
    ('TIANGONG', 'B', 34, INK, 239, [30,50,66,89,119,147,174,204]),
    # hc1_title2
    ('FIRST GUEST', 'B', 34, INK, 277, [27,50,63,90,116,None,150,176,204,228,254]),
    # hc2_body1
    ('Fires at two Rosneft plants in', 'R', 20, INK, 322, [357,369,375,383,395,None,411,424,None,438,446,461,None,479,493,505,515,528,541,548,None,561,574,580,592,606,613,None,629,635]),
    # hc2_body2
    ('Samara region.', 'R', 20, INK, 345, [357,370,382,401,413,421,None,439,447,459,472,478,490,502]),
    # hc2_src
    ('SAMARA | KYIV IND.', 'R', 14, GRAY, 371, [358,367,376,389,398,409,None,426,None,439,449,457,462,None,475,479,489,500]),
    # hc2_title1
    ('UKRAINE HITS', 'B', 34, INK, 239, [355,383,409,438,461,474,502,None,537,565,581,602]),
    # hc2_title2
    ('REFINERIES', 'B', 34, INK, 277, [355,381,404,427,440,468,491,517,530,554]),
    # hc3_body1
    ('Coalition hits port; 4', 'R', 20, INK, 322, [719,733,745,757,763,770,777,783,795,None,814,827,834,841,None,857,870,882,891,898,None,912]),
    # hc3_body2
    ('drones intercepted.', 'R', 20, INK, 345, [719,732,740,752,765,777,None,793,799,813,820,832,840,851,863,877,884,896,908]),
    # hc3_src
    ('HODEIDAH | REUTERS', 'R', 14, GRAY, 371, [719,731,741,752,761,765,777,786,None,805,None,818,828,837,849,856,865,876]),
    # hc3_title1
    ('STRIKES HIT', 'B', 34, INK, 239, [718,744,764,790,803,829,853,None,888,916,932]),
    # hc3_title2
    ('HODEIDAH', 'B', 34, INK, 277, [717,747,774,802,825,838,869,892]),
    # label1
    ('AUSTRALIA CPI - OCT, Y/Y', 'R', 14, INK, 158, [94,103,114,124,131,142,151,159,164,None,178,187,195,None,204,None,213,224,235,242,None,251,260,265]),
    # label2
    ('KOSPI - TARIFF ROUT', 'R', 14, INK, 158, [438,448,459,467,475,None,484,None,494,502,511,521,525,533,None,545,556,566,578]),
    # label3
    ('BRENT CRUDE - DOWN 0.5%', 'R', 14, INK, 158, [739,749,759,768,780,None,792,801,811,821,832,None,846,None,854,866,877,890,None,905,913,917,927]),
    # masthead
    ('WEDNESDAY, 25 NOV 2026', 'B', 60, DBLUE, 15, [54,116,157,207,257,299,341,396,443,482,None,525,567,None,629,681,735,None,798,842,882,925]),
    # num1
    ('+4.9%', 'B', 28, RED, 127, [132,156,174,186,206]),
    # num2
    ('-5.3%', 'B', 28, RED, 127, [467,478,497,509,529]),
    # num3
    ('$90.97', 'B', 28, RED, 127, [785,805,824,842,854,873]),
    # r1c1_body1
    ('Fastest in 3 years;', 'R', 20, INK, 443, [27,39,51,62,69,81,92,None,105,111,None,130,None,150,161,173,185,193,203]),
    # r1c1_body2
    ('RBA hike on table.', 'R', 20, INK, 463, [27,41,56,None,75,88,94,106,None,124,136,None,156,163,175,188,194,205]),
    # r1c1_src
    ('CANBERRA | ABS', 'R', 14, GRAY, 489, [44,54,63,73,83,92,102,113,None,130,None,144,153,164]),
    # r1c1_title1
    ('AUSTRALIA CPI', 'B', 20, INK, 400, [28,42,58,73,86,102,116,129,137,None,158,173,188]),
    # r1c1_title2
    ('+4.9% IN OCT', 'B', 20, INK, 421, [26,45,57,66,81,None,107,114,None,138,155,171]),
    # r1c2_body1
    ('MSCI Asia ex-Japan', 'R', 20, INK, 443, [275,292,305,319,None,332,345,355,361,None,379,392,404,413,416,428,441,453]),
    # r1c2_body2
    ('-2.3%; Nikkei -2.9%.', 'R', 20, INK, 463, [276,282,294,301,314,333,None,346,361,367,379,391,403,None,416,422,434,441,454,472]),
    # r1c2_src
    ('TOKYO | REUTERS', 'R', 14, GRAY, 489, [293,301,311,321,330,None,348,None,361,371,380,392,399,408,419]),
    # r1c2_title1
    ('ASIA STOCKS', 'B', 20, INK, 400, [276,290,304,312,None,333,348,361,378,393,409]),
    # r1c2_title2
    ('TUMBLE -5.3%', 'B', 20, INK, 421, [276,289,305,325,340,353,None,374,382,395,404,419]),
    # r1c3_body1
    ('Metro unions agree', 'R', 20, INK, 443, [523,540,553,560,568,None,586,599,612,618,630,643,None,659,671,684,692,704]),
    # r1c3_body2
    ('+3.5% pay; 500 jobs.', 'R', 20, INK, 463, [522,540,552,559,572,None,597,610,623,634,None,647,660,673,None,694,698,710,723,732]),
    # r1c3_src
    ('SEOUL | KOREA HERALD', 'R', 14, GRAY, 489, [540,548,558,568,578,None,594,None,607,617,627,637,647,None,660,671,680,691,700,708]),
    # r1c3_title1
    ('SEOUL STRIKE', 'B', 20, INK, 400, [523,537,551,568,584,None,604,619,632,647,654,670]),
    # r1c3_title2
    ('CALLED OFF', 'B', 20, INK, 421, [523,539,553,566,579,593,None,617,634,648]),
    # r1c4_body1
    ('Australia is lead', 'R', 20, INK, 443, [772,785,798,809,816,824,836,842,848,None,866,872,None,888,894,906,918]),
    # r1c4_body2
    ('partner; A$740m.', 'R', 20, INK, 463, [771,784,796,805,812,825,837,845,None,859,872,885,899,911,924,942]),
    # r1c4_src
    ('CANBERRA | PM OFFICE', 'R', 14, GRAY, 489, [788,798,807,817,827,836,846,857,None,874,None,887,895,None,912,922,930,938,943,952]),
    # r1c4_title1
    ('SOLOMONS PACT', 'B', 20, INK, 400, [771,785,802,815,832,852,869,886,None,907,923,937,953]),
    # r1c4_title2
    ('SIGNED', 'B', 20, INK, 421, [771,785,792,808,825,839]),
    # r2c1_body1
    ('Threatens Jeddah, all', 'R', 20, INK, 563, [29,39,52,60,72,85,92,104,117,None,136,139,151,164,177,189,202,None,214,226,232]),
    # r2c1_body2
    ('Red Sea ports.', 'R', 20, INK, 583, [27,41,53,None,72,85,97,None,115,128,140,149,156,165]),
    # r2c1_src
    ('SANAA | REUTERS', 'R', 14, GRAY, 609, [44,53,62,73,83,None,100,None,113,123,132,144,151,160,171]),
    # r2c1_title1
    ('HOUTHI THREAT', 'B', 20, INK, 520, [27,44,61,78,91,108,None,123,136,153,168,183,198]),
    # r2c1_title2
    ('TO JEDDAH', 'B', 20, INK, 541, [28,41,None,68,72,86,103,121,135]),
    # r2c2_body1
    ('Floods to 3 ft; waves', 'R', 20, INK, 563, [275,287,293,305,317,330,None,347,354,None,372,None,392,399,406,None,420,435,448,459,471]),
    # r2c2_body2
    ('to 30 ft.', 'R', 20, INK, 583, [276,283,None,301,314,None,334,341,347]),
    # r2c2_src
    ('CALIFORNIA | NWS', 'R', 14, GRAY, 609, [292,302,311,319,323,332,342,352,362,367,None,384,None,397,408,422]),
    # r2c2_title1
    ('CALIFORNIA', 'B', 20, INK, 520, [275,291,305,318,325,339,356,371,388,396]),
    # r2c2_title2
    ('KING TIDES', 'B', 20, INK, 541, [275,291,298,315,None,339,352,359,376,390]),
    # r2c3_body1
    ('Nollywood icon dies', 'R', 20, INK, 563, [523,538,550,556,563,575,590,602,614,None,633,639,650,662,None,681,694,700,712]),
    # r2c3_body2
    ('aged 79.', 'R', 20, INK, 583, [523,535,548,560,None,579,592,604]),
    # r2c3_src
    ('ENUGU | CHANNELS TV', 'R', 14, GRAY, 609, [539,548,558,569,579,None,597,None,611,620,632,641,651,661,670,679,None,693,701]),
    # r2c3_title1
    ('PETE EDOCHIE', 'B', 20, INK, 520, [523,538,553,566,None,587,601,618,635,650,667,674]),
    # r2c3_title2
    ('DIES AT 79', 'B', 20, INK, 541, [523,540,547,561,None,583,598,None,618,632]),
    # r2c4_body1
    ('Fastest since 1990;', 'R', 20, INK, 563, [771,783,795,806,813,825,836,None,849,859,865,878,889,None,906,920,933,946,959]),
    # r2c4_body2
    ('BOJ hike case grows.', 'R', 20, INK, 583, [771,785,804,None,813,826,832,844,None,862,873,885,895,None,913,926,934,947,962,971]),
    # r2c4_src
    ('TOKYO | REUTERS', 'R', 14, GRAY, 609, [789,797,807,817,826,None,844,None,857,867,876,888,895,904,915]),
    # r2c4_title1
    ('JAPAN SERVICES', 'B', 20, INK, 520, [774,779,793,809,823,None,847,861,875,891,905,912,927,941]),
    # r2c4_title2
    ('PPI +4.2%', 'B', 20, INK, 541, [771,786,801,None,814,833,845,854,869]),
    # region
    ('ASIA-PACIFIC 13 | EUROPE 4 | MIDDLE EAST 3 | AMERICAS 2 | AFRICA 1 | MARKETS 2', 'R', 14, INK, 900, [197,207,215,220,230,234,243,253,262,266,274,279,None,292,301,None,318,None,331,340,350,361,371,379,None,393,None,409,None,422,434,438,449,460,468,None,481,491,501,511,None,522,None,539,None,553,562,574,583,593,598,608,618,None,630,None,647,None,661,670,678,688,693,703,None,716,None,733,None,746,759,768,778,787,798,806,None,818]),
    # wire
    ('WIRE TIMES UTC | 00:18 SHENZHOU LAUNCH | 00:30 AUS CPI +4.9% | 02:12 SAMARA FIRES | 03:56 SHENZHOU DOCKS', 'R', 14, INK, 106, [20,33,37,47,None,62,69,73,85,95,None,107,119,127,None,148,None,166,175,183,188,198,None,211,219,230,239,250,259,271,281,None,295,304,313,323,334,343,None,366,None,384,393,401,406,416,None,429,438,449,None,462,471,479,None,487,500,508,513,522,None,546,None,564,572,581,586,595,None,609,618,627,640,649,660,None,673,681,685,695,705,None,725,None,743,751,760,765,774,None,788,796,807,816,827,836,848,858,None,872,884,895,904,914]),
]


# ------------------------------------------------------- illustration art
# Small bitmaps for the three headline illustrations, transcribed from the
# approved image pixel by pixel. '#' is ink, 'O' orange, 'R' red.

# Card 2: flame (21x15), pasted twice; ink "shoulders" above each flame.
FLAME = [
    "..........O..........",
    ".........OO..........",
    "........OOOO.........",
    ".......OOOOOO........",
    ".......OOOOOO........",
    "......OOOOOOOO.......",
    ".....OOOOOROOOO......",
    ".....OOOORROOOOO.....",
    "....OOOORRRROOOO.....",
    "...OOOOORRRROOOOO....",
    "..OOOOORRRRRROOOOO...",
    "..OOOORRRRRRRROOOO...",
    ".OOOOORRRRRRRROOOOO..",
    "OOOOORRRRRRRRRROOOOO.",
    "OOOOORRRRRRRRRRROOOOO",
]
INKBARS = [
    "...######....######....",
    "...#####......#####....",
    "...#####......#####....",
    "...####........####....",
    "...###..........###....",
    "...###...........##....",
    "...##............##....",
    "...#..............#....",
]

# Card 1: rocket nose cone (13 rows, origin 288,194) and gold flames.
NOSE = [
    "......#......",
    ".....##.......",
    ".....###......",
    "....####......",
    "....#####.....",
    "...######.....",
    "...#######....",
    "..########....",
    "..#########...",
    ".##########...",
    ".###########..",
    "############..",
    "#..........##.",
]
FLAME_L = [
    "....#####.",
    "...#####..",
    "...####...",
    "..####....",
    "..###.....",
    ".###......",
    ".##.......",
    "##........",
    "#.........",
]
FLAME_R = [
    "#####.....",
    ".####.....",
    "..####....",
    "...###....",
    "....###...",
    ".....##...",
    "......##..",
    ".......#..",
    "........#.",
]

# Card 3: two dock cranes (ink). Crane 1: origin (766,196), 20 rows.
# Crane 2: origin (900,196), 32 rows; its pillar runs down to y227.
CRANE1 = [
    ".....................####.................................",
    "..................###.#####...............................",
    "................##....###..###............................",
    ".............###......###.....##..........................",
    "..........###.........###.......###.......................",
    ".......###............###..........###....................",
    ".....##...............###.............###.................",
    "..###.................###................###..............",
    "......................###...................###...........",
    "......................###......................##.........",
    "......................###........................###......",
    "......................###...........................###...",
    "......................###...........................##.##.",
    "......................###...........................##....",
    "......................###...........................##....",
    "......................###...........................##....",
    "......................###...........................##....",
    "......................###...........................##....",
    "......................###...........................##....",
    "......................###...........................##....",
]
CRANE2 = [
    "........................####.................................",
    ".....................###.#####...............................",
    "...................##....###..###............................",
    "................###......###.....##..........................",
    ".............###.........###.......###.......................",
    "..........###............###..........###....................",
    "........##...............###.............###.................",
    ".....###.................###................###..............",
    "...##....................###...................###...........",
    ".........................###......................##.........",
    ".........................###........................###......",
    ".........................###...........................###...",
    ".........................###...........................##.##.",
    ".........................###...........................##....",
    ".........................###...........................##....",
    ".........................###...........................##....",
    ".........................###...........................##....",
    ".........................###...........................##....",
    ".........................###...........................##....",
    ".........................###...........................##....",
    ".........................###...........................##....",
    ".........................###...........................##....",
    ".........................###.................................",
    ".........................###.................................",
    ".........................###.................................",
    ".........................###.................................",
    ".........................###.................................",
    ".........................###.................................",
    ".........................###.................................",
    ".........................###.................................",
    ".........................###.................................",
    ".........................###.................................",
]


def draw_frame():
    """Rules, card borders, chips and the DATE CHECK box."""
    # horizontal rules
    rect(20, 94, 1003, 95, DBLUE)
    rect(20, 130, 1003, 130, GRAY)
    rect(20, 178, 1003, 179, DBLUE)
    rect(20, 664, 1003, 665, RED)
    rect(20, 890, 1003, 890, GRAY)
    rect(20, 936, 1003, 936, INK)
    # numbers bar dividers
    rect(348, 136, 348, 171, GRAY)
    rect(676, 136, 676, 171, GRAY)
    # headline cards: 1px ink top rule, then 4px colour band
    for x0, x1, c in [(20, 337, DBLUE), (348, 699, RED), (710, 1003, TEAL)]:
        rect(x0, 180, x1, 180, INK)
        rect(x0 + 1, 181, x1 - 1, 184, c)
        rect(x0, 389, x1, 389, INK)
        rect(x0, 180, x0, 389, INK)
        rect(x1, 180, x1, 389, INK)
    # short cards, row 1: 1px ink top rule, then 3px colour band
    for x0, x1, c in [(20, 259, RED), (268, 507, RUST),
                      (516, 755, GREEN), (764, 1003, MBLUE)]:
        rect(x0, 396, x1, 396, INK)
        rect(x0 + 1, 397, x1 - 1, 399, c)
        rect(x0, 509, x1, 509, INK)
        rect(x0, 396, x0, 509, INK)
        rect(x1, 396, x1, 509, INK)
        rect(x0 + 8, 491, x0 + 17, 500, c)
    # short cards, row 2
    for x0, x1, c in [(20, 259, ORANGE), (268, 507, TEAL),
                      (516, 755, GOLD), (764, 1003, GBLUE)]:
        rect(x0, 516, x1, 516, INK)
        rect(x0 + 1, 517, x1 - 1, 519, c)
        rect(x0, 629, x1, 629, INK)
        rect(x0, 516, x0, 629, INK)
        rect(x1, 516, x1, 629, INK)
        rect(x0 + 8, 611, x0 + 17, 620, c)
    # DATE CHECK box: side + bottom ink borders, red bar on the left
    rect(20, 937, 20, 1003, INK)
    rect(1003, 937, 1003, 1003, INK)
    rect(20, 1003, 1003, 1003, INK)
    rect(21, 937, 23, 1002, RED)


def draw_illustrations():
    """The three headline-card illustration bands (y 190..239)."""
    # ---- card 1: satellite + rocket on deep blue
    rect(30, 190, 327, 239, DBLUE)
    for sx, sy in [(82, 195), (214, 195), (38, 196), (170, 196), (302, 196),
                   (126, 197), (258, 197), (192, 202), (280, 202),
                   (104, 204), (236, 204), (148, 205), (60, 206)]:
        rect(sx, sy, sx + 1, sy + 1, BG)
    rect(171, 210, 186, 229, GOLD)          # satellite body
    disc(179, 220, 5, RED)                  # round window
    rect(133, 216, 170, 223, BG)            # solar panels
    rect(187, 216, 224, 223, BG)
    rect(289, 206, 298, 223, BG)            # rocket body
    paste_bitmap(NOSE, 288, 194, {"#": ORANGE})
    paste_bitmap(FLAME_L, 285, 224, {"#": GOLD})
    paste_bitmap(FLAME_R, 295, 224, {"#": GOLD})
    # ---- card 2: refinery towers, flames and smoke on grey-blue sky
    rect(358, 190, 689, 233, GBLUE)
    rect(427, 212, 454, 233, GRAY)
    rect(593, 212, 620, 233, GRAY)
    rect(423, 206, 458, 211, INK)
    rect(589, 206, 624, 211, INK)
    rect(358, 234, 689, 239, INK)
    disc(524, 200, 7, BG)                   # smoke rings
    disc(536, 196, 5, BG)
    paste_bitmap(INKBARS, 430, 194, {"#": INK})
    paste_bitmap(INKBARS, 596, 194, {"#": INK})
    paste_bitmap(FLAME, 431, 192, {"O": ORANGE, "R": RED})
    paste_bitmap(FLAME, 597, 192, {"O": ORANGE, "R": RED})
    # ---- card 3: dock cranes, containers, water
    paste_bitmap(CRANE1, 766, 196, {"#": INK})
    paste_bitmap(CRANE2, 900, 196, {"#": INK})
    rect(814, 218, 821, 223, RED)           # hook boxes (crane 1 mostly
    rect(951, 218, 958, 223, RED)           # hidden behind the blue box)
    rect(728, 216, 767, 227, RED)           # containers
    rect(748, 204, 787, 215, GOLD)
    rect(772, 216, 811, 227, GREEN)
    rect(816, 216, 855, 227, MBLUE)
    rect(720, 228, 993, 239, TEAL)          # water


def main():
    draw_frame()
    draw_illustrations()
    for text, fkey, size, color, y0, pens in TEXT:
        f = font(BOLD if fkey == "B" else REGULAR, size)
        paste_text(text, f, size, color, y0, pens)
    outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    png = save_png(path)
    print(path)
    print("sha256:", hashlib.sha256(png).hexdigest())


if __name__ == "__main__":
    main()
