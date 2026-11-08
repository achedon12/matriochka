"""The website's pictures as WebP: lossless for pixel art (textures, icons, interface captures, which must stay
crisp), lossy for screenshots, photos and renders. Used by tools/site.py, tools/site_visuals.py,
tools/portraits.py and tools/site_versions.py.

Without WebP support in Pillow, pictures are saved as before (PNG, or JPEG for photos) and nothing is converted.
"""
import os
import re

try:
    from PIL import Image, features
    HAS_WEBP = features.check("webp")
except ImportError:  # no Pillow: the files already in site/public are kept
    Image = None
    HAS_WEBP = False

QUALITY = 84  # lossy: as good as the JPEGs at quality 80-82 they replace, at about two thirds of the size
# linked from outside the site (the README, the wiki): kept as they are, beside their WebP
KEEP = re.compile(r"^shots/(gui_journal_1|gui_scroll|gui_station_[a-z_]+)\.png$")
PHOTO_EXT = (".jpg", ".jpeg")
PICTURE = re.compile(r"\.(png|jpe?g)$")


def save(im, path, lossless):
    """Saves a picture at `path` (its extension is replaced): .webp when Pillow can, else .png (lossless) or
    .jpg. Returns the name of the file written."""
    base = os.path.splitext(path)[0]
    if HAS_WEBP:
        out = base + ".webp"
        if lossless:
            # the renders are redrawn every run: an unchanged picture is not encoded again (method 6 is slow)
            if os.path.exists(out):
                try:
                    with Image.open(out) as old:
                        if old.size == im.size and old.convert("RGBA").tobytes() == im.convert("RGBA").tobytes():
                            return os.path.basename(out)
                except OSError:
                    pass
            im.save(out, "WEBP", lossless=True, quality=100, method=6, exact=True)
        else:
            if im.mode not in ("RGB", "RGBA"):
                im = im.convert("RGBA" if "A" in im.getbands() else "RGB")
            im.save(out, "WEBP", quality=QUALITY, method=6)
    elif lossless:
        out = base + ".png"
        im.save(out, optimize=True)
    else:
        out = base + ".jpg"
        im.convert("RGB").save(out, quality=82, optimize=True, progressive=True)
    return os.path.basename(out)


def ext(lossless):
    """The extension pictures are written with."""
    return ".webp" if HAS_WEBP else (".png" if lossless else ".jpg")


def convert_dir(public, sub, lossless=None):
    """Turns the PNG and JPEG files left in site/public/<sub> (committed by an earlier run, or copied there) into
    WebP, and removes them unless they are linked from outside the site. lossless=None: PNGs lossless, JPEGs
    lossy. Returns the number of files converted."""
    d = os.path.join(public, sub)
    if not HAS_WEBP or not os.path.isdir(d):
        return 0
    n = 0
    for f in sorted(os.listdir(d)):
        src = os.path.join(d, f)
        if not os.path.isfile(src) or not PICTURE.search(f):
            continue
        dst = os.path.splitext(src)[0] + ".webp"
        if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src):
            im = Image.open(src)
            im.load()
            save(im, dst, lossless if lossless is not None else not f.lower().endswith(PHOTO_EXT))
            n += 1
        if not KEEP.match(f"{sub}/{f}".replace(os.sep, "/")):
            os.remove(src)
    return n


def paths(obj, public):
    """Points every picture path of the site's data ("items/x.png", "shots/y.jpg") at its WebP when the WebP is
    in site/public; a path with no file in either form is left as it is."""
    if isinstance(obj, dict):
        return {k: paths(v, public) for k, v in obj.items()}
    if isinstance(obj, list):
        return [paths(v, public) for v in obj]
    if isinstance(obj, str) and PICTURE.search(obj) and "/" in obj and not obj.startswith(("http", "/")):
        w = PICTURE.sub(".webp", obj)
        if os.path.exists(os.path.join(public, w)):
            return w
    return obj
