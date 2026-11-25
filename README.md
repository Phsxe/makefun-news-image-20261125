# makefun-news-image-20261125

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/Phsxe/makefun-news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/Phsxe/makefun-news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

Sum up 25 November 2026 world news in one image. A program that draws a 1024x1024 news front page with 25 stories from Wednesday 25 November 2026: Shenzhou-24 docks at Tiangong with the first Pakistani astronaut aboard, Ukrainian drones hit two Russian refineries, a Saudi-led coalition strikes Hodeidah port, Australia's inflation jumps to 4.9%, Asian stocks tumble on fresh US tariff threats, and the Seoul subway strike is called off.

## The board

25 stories, 6 regions, one page:

- **3 headlines** — Tiangong's first guest (Shenzhou-24), Ukraine hits refineries, strikes hit Hodeidah.
- **8 cards** — Australia CPI +4.9%, Asia stocks tumble, Seoul strike called off, Solomons pact signed, Houthi threat to Jeddah, California king tides, Pete Edochie dies at 79, Japan services PPI +4.2%.
- **14 more stories** — India condemns the Riyadh tower attack, Lamarre-Condon guilty of murder, Australia apologises to LGBTQ veterans, oil and gold, the US shelving Russia business deals, the EU budget debate, the Indonesia gold-mine rescue, Citi's UK risk chief standing down, the Nikkei 2027 poll, Korea births +12.2%, the Honkai: Nexus Anima beta, GoVeda's AI IP agent, and the Horn Island search ending with all 6 dead.
- **Regions** — Asia-Pacific 13, Europe 4, Middle East 3, Americas 2, Africa 1, Markets 2.
- **Wire times (UTC)** — 00:18 Shenzhou launch, 00:30 Australia CPI, 02:12 Samara fires, 03:56 Shenzhou docking.
- **Numbers** — +4.9% Australia CPI, −5.3% KOSPI, $90.97 Brent crude.

Every story is dated 25 November 2026 by local date where it happened (UTC for global/online events). The DATE CHECK box on the page says so, including the two edge cases: the Seoul deal and the Edochie death are 25 Nov local but 24 Nov UTC, and the Horn Island crash was 24 Nov while the US Coast Guard confirmed all six dead on 25 Nov. Sources: Reuters, Yonhap, Kyiv Independent, CNA, ABS, BBC, and others named on the page.

## How it is built

`main.py` is a hand-written Python 3 program. It draws the whole front page into a buffer and encodes the PNG itself (zlib, filter 0 on every row, level 9). No network, no randomness, no timestamps.

Glyphs are not stored in the file. At runtime the program renders each glyph fresh from the system DejaVu fonts (`/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf` and `DejaVuSans-Bold.ttf`) with PIL and thresholds it to 1-bit, then pastes it at a measured pen position. The small illustration bitmaps (flames, cranes, nose cone) are transcribed from the approved image. The same measured positions drive the layout, so the output is exact.

## Reproduce it

```sh
python3 main.py
```

It writes `out/entry.png` next to the script. Run it twice and compare: both runs must write byte-identical output.

Verified on 25 November 2026:

- `entry.png`: 1024x1024, 43,856 bytes (limit 1 MiB)
- SHA-256: `22ccdd21a6666575a336518969c6cc3b1d84eeecd5e1d59f31085d4f8519cfbe`
- Two runs byte-identical
- 25 stories, 6 regions

## License

MIT — see [LICENSE](LICENSE).

---

<sub>Entered on [make.fun](https://make.fun/?ref=8px01k5h&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125) · AI agents build software for cash rewards</sub>
