# news-image-20261125

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/Phsxe/makefun-news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/Phsxe/makefun-news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

A one-page newspaper front page for **Wednesday, 25 November 2026**,
rendered as a 1024x1024 one-bit-thresholded image. It covers 25 news
items across 6 regions, with a UTC wire line, a stats bar, 3 headline
cards, 8 small cards, a 14-item ALSO list, region counts and a
DATE CHECK box.

## Run

```sh
python3 main.py
```

This writes `out.png` (1024x1024, 43,856 bytes) and prints its SHA-256.
The output is deterministic: run it twice and the hash is identical.

```
sha256: 22ccdd21a6666575a336518969c6cc3b1d84eeecd5e1d59f31085d4f8519cfbe
```

## How it works

- **Text:** rendered at runtime from the DejaVu fonts installed on the
  machine (`DejaVuSans` and `DejaVuSans-Bold`), one glyph at a time.
  Each glyph mask is thresholded at 128 and pasted so the ink lands
  exactly where the approved layout puts it. No font bitmaps are
  stored in the source.
- **Illustrations:** the satellite and rocket, the two factory
  chimneys with smoke, and the port with two cranes are drawn from
  rectangles, pixel-centre polygons and circles. A pixel is filled
  exactly when its centre lies inside the shape.
- **PNG:** encoded by hand — filter 0 on every scanline, zlib level 9
  — so the bytes are stable across runs.
- **Determinism:** no network, no randomness, no timestamps.

## Contents

- `main.py` — the whole generator, nothing else needed.
- `out.png` — the rendered front page (produced by running `main.py`).

## Stories

Headlines: Shenzhou-24 docks at Tiangong (first Pakistani in space),
Ukraine hits two Rosneft refineries in Samara, coalition strikes hit
Hodeidah. Plus Australia CPI, Asia stocks, the Seoul metro strike,
the Solomons pact, Houthi threats to Jeddah, California king tides,
Pete Edochie, Japan services PPI — and 14 more in the ALSO list.
