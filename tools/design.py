"""Shared design tokens + helpers. Change the palette/typography here; everything else rebuilds from it."""
import os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_SRC = os.path.join(ROOT, "fonts")
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_OUT = os.path.join(HERE, "fonts", "static")
PKG = os.path.join(ROOT, "pkg")
ASSETS = os.path.join(PKG, "assets")

# ---- palette -------------------------------------------------------------
BLACK, NEAR, GRAPHITE, GRAPHITE2 = "#050506", "#0b0b0d", "#17181b", "#26282d"
CRIMSON, SCARLET, DEEP = "#b3121f", "#e5253a", "#5a0a12"
WHITE, MUTED = "#f4f4f5", "#8a8d93"

def hex2rgb(h): h = h.lstrip("#"); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

# ---- typography ----------------------------------------------------------
FONTS = {  # name: (file, axes)
    "display":  ("Syne[wght].ttf", {"wght": 800}),
    "heading":  ("CormorantGaramond-Italic[wght].ttf", {"wght": 600}),
    "mono":     ("JetBrainsMono[wght].ttf", {"wght": 500}),
    "monobold": ("JetBrainsMono[wght].ttf", {"wght": 700}),
    "sans":     ("Manrope[wght].ttf", {"wght": 600}),
    "sansreg":  ("Manrope[wght].ttf", {"wght": 500}),
}
def font_path(name):
    out = os.path.join(FONT_OUT, name + ".ttf")
    if not os.path.exists(out):
        os.makedirs(FONT_OUT, exist_ok=True)
        from fontTools.varLib import instancer  # build-time only
        f, axes = FONTS[name]
        instancer.instantiateVariableFont(TTFont(os.path.join(FONT_SRC, f)), axes).save(out)
    return out

_cache = {}
def tt(name):
    if name not in _cache: _cache[name] = TTFont(font_path(name))
    return _cache[name]

def text_width(name, text, size, tracking=0):
    f = tt(name); s = size / f["head"].unitsPerEm; cm = f.getBestCmap(); hm = f["hmtx"]
    return sum(hm[cm.get(ord(c), ".notdef")][0] * s + tracking for c in text) - (tracking if text else 0)

def text_path(name, text, size, x=0, y=0, tracking=0, anchor="start"):
    """Return SVG path data for text (outlined, so SVGs never depend on installed fonts)."""
    f = tt(name); upm = f["head"].unitsPerEm; s = size / upm
    gs = f.getGlyphSet(); cm = f.getBestCmap(); hm = f["hmtx"]
    w = text_width(name, text, size, tracking)
    cur = x - (w if anchor == "end" else w / 2 if anchor == "middle" else 0)
    d = []
    for c in text:
        gn = cm.get(ord(c), ".notdef")
        pen = SVGPathPen(gs, ntos=lambda v: ("%.2f" % v).rstrip("0").rstrip("."))
        gs[gn].draw(TransformPen(pen, (s, 0, 0, -s, cur, y)))
        d.append(pen.getCommands())
        cur += hm[gn][0] * s + tracking
    return " ".join(x for x in d if x), w

def save(path, content, mode="w"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, mode) as fh: fh.write(content)
