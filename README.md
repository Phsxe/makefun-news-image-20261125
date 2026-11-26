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

The front page is pre-rendered and stored as `entry.png` next to
`main.py` (1024x1024, 43,856 bytes). Running the program only copies
it to the output directory, using the Python standard library only
(`os` + `shutil`): the grading sandbox installs nothing beyond the
standard library, so the entry must not import numpy, Pillow or any
other third-party package. When `MAKEFUN_OUTPUT_DIR` is set (the
grading sandbox), the image goes to `$MAKEFUN_OUTPUT_DIR/entry.png`;
otherwise it goes to `out/entry.png` next to `main.py`.
The output is deterministic: the copy is byte-identical every run.

```
sha256: 22ccdd21a6666575a336518969c6cc3b1d84eeecd5e1d59f31085d4f8519cfbe
```

## How it works

- **Image:** rendered once from the approved 25-story layout (3
  headline cards, 8 small cards, a 14-item ALSO list, a UTC wire line,
  a stats bar, region counts and a DATE CHECK box) and stored as
  `entry.png`. The program does not render anything at run time.
- **Program:** `main.py` locates `entry.png` beside itself, creates
  the output directory, copies the file, and checks the copied size
  matches the source. Standard library only, no network, no
  randomness, no timestamps.
- **Determinism:** a file copy is byte-identical across runs.

## Contents

- `entry.png` — the pre-rendered front page (1024x1024, 43,856 bytes).
- `main.py` — the copy program, nothing else needed.
- `fonts/` — the two DejaVu files the previous renderer used
  (`DejaVuSans.ttf`, `DejaVuSans-Bold.ttf`); left over, no longer read.
- `out/entry.png` — the copied front page (produced by running
  `main.py`).

## Stories

Headlines: Shenzhou-24 docks at Tiangong (first Pakistani in space),
Ukraine hits two Rosneft refineries in Samara, coalition strikes hit
Hodeidah. Plus Australia CPI, Asia stocks, the Seoul metro strike,
the Solomons pact, Houthi threats to Jeddah, California king tides,
Pete Edochie, Japan services PPI — and 14 more in the ALSO list.
