"""Normalise product photography onto one background.

The supplied photos are inconsistent: some garments sit on black, some on white. Side by
side in a grid that reads as a mistake, and it pulls the eye away from the product.

This flood-fills the background from the image's corners and replaces it with white, so
every product sits on the same surface. It is deliberately conservative:

- it only runs when the four corners agree on a colour, which is what a studio
  background looks like;
- it fills from the corners outward, so a garment in the middle of the frame is never
  touched, however dark it is;
- background the corners cannot reach — the wedge between a sleeve and the torso — is
  matched by colour instead, at a much tighter tolerance, because nothing vouches for
  those pixels except their own colour;
- the colour distance threshold is well below the gap between black and Yale navy, so a
  navy hoodie on black keeps its navy;
- if anything is unclear, the original is served unchanged.

**The supplied images are never modified.** Results are written to a cache directory and
the originals are only ever read.
"""
from __future__ import annotations

import logging
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

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

# Background can also be *trapped* inside the frame — the triangle between a sleeve and
# the torso is walled off from every corner, so the flood fill can never reach it and it
# stays black. Those regions are found directly instead, and this is the tolerance used.
#
# It is deliberately much tighter than FILL_TOLERANCE, because there is no corner to
# vouch for these pixels: anything matched here is whitened on colour alone. Calibrated
# on the two cases that disagree. The sleeve gaps on soccer-left-chest-crewneck are
# already 0.98% of the frame at 12 against 1.27% at 30, so a tight threshold keeps
# essentially all of the real gap; the shadow inside basic-hoodie-big-yale's hood stays
# out at 12 (0.12%) and floods in above 20 (0.27% → 1.35% at 25 → 2.02% at 30).
HOLE_TOLERANCE = 12
# No real sleeve gap in this catalogue exceeds 1.2% of the frame. Well past that, the
# assumption has broken down, so the regions are left alone rather than bleached.
HOLE_LIMIT_PCT = 5.0

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


def _mask_percent(mask: Image.Image) -> float:
    """How much of the frame a mask covers."""
    on = sum(mask.histogram()[1:])
    return 100 * on / (mask.size[0] * mask.size[1])


def _enclosed_background(image: Image.Image, background: tuple[int, int, int]) -> Image.Image:
    """Background-coloured regions the corner fill cannot reach.

    The flood fill spreads inward from the four corners, so it only ever finds
    background that is connected to an edge. A garment photographed with its sleeves
    away from its body encloses a wedge of the backdrop, and that wedge stays black —
    which is what made the navy crewnecks look like they had holes cut in them.

    This finds those wedges by colour and then subtracts everything the corner fill
    already handles, leaving exactly what it could not reach.
    """
    solid = Image.new("RGB", image.size, background)
    red, green, blue = ImageChops.difference(image, solid).split()
    # L1 across the channels — the same colour metric Pillow's own floodfill uses, so
    # "within tolerance" means the same thing here as it does for the corner fill.
    distance = ImageChops.add(ImageChops.add(red, green), blue)
    near = distance.point(lambda v: 255 if v <= HOLE_TOLERANCE else 0)

    w, h = near.size
    border = (
        [(x, 0) for x in range(w)]
        + [(x, h - 1) for x in range(w)]
        + [(0, y) for y in range(h)]
        + [(w - 1, y) for y in range(h)]
    )
    for seed in border:
        if near.getpixel(seed) == 255:
            ImageDraw.floodfill(near, seed, 0)

    # An opening — erode, then dilate — drops stray single-pixel specks inside the
    # garment without shrinking a real gap, which is many pixels across.
    return near.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))


def _background_mask(original: Image.Image, filled: Image.Image) -> Image.Image:
    """Exactly which pixels the flood fill changed — i.e. the background.

    Derived by comparing before and after rather than by looking for white, which is the
    distinction that matters: a garment's own white lettering is white too.
    """
    diff = ImageChops.difference(original, filled).convert("L")
    return diff.point(lambda v: 255 if v > 0 else 0).convert("L")


def _clean_fringe(
    image: Image.Image, background: Image.Image, rounds: int = 2
) -> Image.Image:
    """Remove the dark halo the flood fill cannot reach.

    A photo's edge is anti-aliased: where garment meets background the pixels are a
    blend of the two. The fill stops at them, leaving a speckled outline.

    This grows the **background region** inward a pixel at a time, over dark pixels
    only, so it eats the blended edge and stops at the garment.

    Growing from the background mask rather than from "anything white" is the whole
    point. An earlier version grew from white pixels, which meant a garment's own white
    lettering — "YALE CREW" on a navy hoodie — seeded the growth and chewed holes in its
    own logo. Interior white can never seed this version, because it was never part of
    the background.
    """
    white_fill = Image.new("RGB", image.size, WHITE)
    for _ in range(rounds):
        grey = image.convert("L")
        dark = grey.point(lambda v: 255 if v < 120 else 0).convert("L")
        grown = background.filter(ImageFilter.MaxFilter(3))
        fringe = ImageChops.darker(grown, dark)
        image.paste(white_fill, mask=fringe.convert("1"))
        # Anything just cleaned becomes background for the next round.
        background = ImageChops.lighter(background, fringe)
    return image


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

        # Then the background the corner fill could not reach, such as the gap between a
        # sleeve and the torso.
        enclosed = _enclosed_background(image, background)
        share = _mask_percent(enclosed)
        if share > HOLE_LIMIT_PCT:
            logger.info(
                "enclosed regions cover %.1f%% of %s; leaving them alone", share, product_id
            )
        elif share > 0:
            normal.paste(Image.new("RGB", normal.size, WHITE), mask=enclosed.convert("1"))

        # The fringe pass reads the background out of what actually changed, so it now
        # cleans the rims of those gaps too, not just the outline.
        normal = _clean_fringe(normal, _background_mask(image, normal))

        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        normal.save(cached, "JPEG", quality=90, optimize=True)
        return cached
    except Exception:  # noqa: BLE001 - a tidier image is never worth a broken page
        logger.warning("could not normalise %s; serving the original", product_id)
        return source
