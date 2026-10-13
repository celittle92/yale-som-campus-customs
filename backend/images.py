"""Normalise product photography onto one background.

The supplied photos are inconsistent: some garments sit on black, some on white. Side by
side in a grid that reads as a mistake, and it pulls the eye away from the product.

This flood-fills the background from the image's corners and replaces it with white, so
every product sits on the same surface. It is deliberately conservative:

- it only runs when the four corners agree on a colour, which is what a studio
  background looks like;
- it fills from the corners outward, so a garment in the middle of the frame is never
  touched, however dark it is;
- the colour distance threshold is well below the gap between black and Yale navy, so a
  navy hoodie on black keeps its navy;
- if anything is unclear, the original is served unchanged.

**The supplied images are never modified.** Results are written to a cache directory and
the originals are only ever read.
"""
from __future__ import annotations

import logging
from pathlib import Path

from PIL import Image, ImageDraw

logger = logging.getLogger("campus_customs.images")

CACHE_DIR = Path(__file__).resolve().parent.parent / ".image-cache"

# Corners must agree within this distance for us to believe it is a studio background.
CORNER_AGREEMENT = 40

# How far the fill spreads. Calibrated rather than guessed: on the navy-hoodie-on-black
# shot, tolerances from 10 to 55 all leave the same 51% of the frame as garment, and 70
# drops it to 47.6% — the fill escaping through a dark shadow and eating the sleeve. 30
# sits in the middle of the stable band with margin on both sides.
FILL_TOLERANCE = 30
# A deliberately timid second pass, used to detect that the main one leaked.
SAFE_TOLERANCE = 12
# If the two passes disagree by more than this many percentage points of coverage, the
# main fill escaped into the garment and the timid result is used instead.
LEAK_TOLERANCE_PP = 2.5
# Backgrounds already this close to white are left alone.
ALREADY_WHITE = 26

WHITE = (255, 255, 255)


def _distance(a: tuple[int, ...], b: tuple[int, ...]) -> float:
    return sum((int(x) - int(y)) ** 2 for x, y in zip(a[:3], b[:3])) ** 0.5


def _background_colour(image: Image.Image) -> tuple[int, int, int] | None:
    """The studio background, if the four corners agree on one."""
    w, h = image.size
    corners = [
        image.getpixel((1, 1)),
        image.getpixel((w - 2, 1)),
        image.getpixel((1, h - 2)),
        image.getpixel((w - 2, h - 2)),
    ]
    first = corners[0]
    if any(_distance(first, c) > CORNER_AGREEMENT for c in corners[1:]):
        return None  # a photo that bleeds to the edge; leave it alone
    return tuple(int(v) for v in first[:3])  # type: ignore[return-value]


def _filled(image: Image.Image, tolerance: int) -> Image.Image:
    """A copy with the background flooded to white from all four corners."""
    out = image.copy()
    w, h = out.size
    for corner in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        ImageDraw.floodfill(out, corner, WHITE, thresh=tolerance)
    return out


def _coverage(image: Image.Image) -> float:
    """Percentage of the frame that is not near-white, i.e. still garment."""
    w, h = image.size
    px = image.load()
    step = max(1, min(w, h) // 150)
    xs, ys = range(0, w, step), range(0, h, step)
    dark = sum(1 for x in xs for y in ys if sum(px[x, y]) / 3 < 235)
    return 100 * dark / (len(xs) * len(ys))


def normalise(source: Path, product_id: str) -> Path:
    """Return a white-background version of `source`, generating it once and caching.

    Falls back to the original path on any problem — a product photo must always load,
    even if tidying it fails.
    """
    cached = CACHE_DIR / f"{product_id}.jpg"
    if cached.is_file() and cached.stat().st_mtime >= source.stat().st_mtime:
        return cached

    try:
        with Image.open(source) as opened:
            image = opened.convert("RGB")

        background = _background_colour(image)
        if background is None:
            return source
        if _distance(background, WHITE) <= ALREADY_WHITE:
            return source  # already on white; nothing to gain

        normal = _filled(image, FILL_TOLERANCE)
        timid = _filled(image, SAFE_TOLERANCE)

        # A flood fill can escape through a dark shadow and eat part of a dark garment.
        # Running a second, timid pass makes that detectable: if the two disagree about
        # how much of the frame survived, the generous one leaked.
        if _coverage(timid) - _coverage(normal) > LEAK_TOLERANCE_PP:
            logger.info("fill leaked on %s; using the conservative pass", product_id)
            normal = timid

        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        normal.save(cached, "JPEG", quality=90, optimize=True)
        return cached
    except Exception:  # noqa: BLE001 - a tidier image is never worth a broken page
        logger.warning("could not normalise %s; serving the original", product_id)
        return source
