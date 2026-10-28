# -*- coding: utf-8 -*-
"""chart-skill shared setup: CJK font, palette, save helper, graphviz lookup.

Import this first and every figure gets a working CJK font and the same palette.
"""
import os
import shutil

import matplotlib

matplotlib.use("Agg")                 # headless backend, must precede pyplot
import matplotlib.pyplot as plt
from matplotlib import font_manager

# ---------------------------------------------------------------- CJK font ---
WINDIR = os.environ.get("WINDIR", "")
PROGRAMFILES = os.environ.get("ProgramFiles", "")

_CANDIDATES = [
    # (display name, [font file paths], [family names matplotlib may know])
    ("Microsoft YaHei", [os.path.join(WINDIR, "Fonts", "msyh.ttc"),
                         os.path.join(WINDIR, "Fonts", "msyh.ttf")],
     ["Microsoft YaHei"]),
    ("PingFang SC", ["/System/Library/Fonts/PingFang.ttc",
                     "/System/Library/Fonts/Supplemental/PingFang.ttc"],
     ["PingFang SC"]),
    ("Noto Sans CJK SC", ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                          "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
                          "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc"],
     ["Noto Sans CJK SC", "Noto Sans SC"]),
    ("Source Han Sans SC", ["/usr/share/fonts/opentype/adobe-source-han-sans/SourceHanSansSC-Regular.otf"],
     ["Source Han Sans SC"]),
    ("WenQuanYi Micro Hei", ["/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"],
     ["WenQuanYi Micro Hei"]),
    ("SimHei", [os.path.join(WINDIR, "Fonts", "simhei.ttf")], ["SimHei"]),
]


def find_cjk_font():
    """Return (family name, found). Never raises."""
    installed = {f.name for f in font_manager.fontManager.ttflist}
    for display, paths, families in _CANDIDATES:
        if any(os.path.exists(p) for p in paths):
            return display, True
        for fam in families:
            if fam in installed:
                return fam, True
    return "DejaVu Sans", False


FONT_NAME, HAS_CJK_FONT = find_cjk_font()
plt.rcParams["font.sans-serif"] = [FONT_NAME, "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False      # keep minus signs from becoming boxes
plt.rcParams["figure.facecolor"] = "white"
plt.rcParams["savefig.facecolor"] = "white"

if not HAS_CJK_FONT:
    import sys
    sys.stderr.write(
        "vizlib: no CJK font found, Chinese text will render as boxes.\n"
        "        Install one: apt install fonts-noto-cjk  |  brew install font-noto-sans-cjk-sc\n"
    )

# --------------------------------------------------------------- graphviz ---
_GV_DIRS = [
    os.path.join(PROGRAMFILES, "Graphviz", "bin") if PROGRAMFILES else "",
    os.path.join(PROGRAMFILES + " (x86)", "Graphviz", "bin") if PROGRAMFILES else "",
    "/opt/homebrew/bin",
    "/usr/local/bin",
    "/usr/bin",
]


def ensure_graphviz():
    """Make sure the dot binary is reachable. Returns True when it is."""
    if shutil.which("dot"):
        return True
    exe = "dot.exe" if os.name == "nt" else "dot"
    for d in _GV_DIRS:
        if os.path.exists(os.path.join(d, exe)):
            os.environ["PATH"] = os.environ.get("PATH", "") + os.pathsep + d
            return True
    return False


HAS_GRAPHVIZ = ensure_graphviz()

# ---------------------------------------------------------------- palette ---
INK    = "#0F172A"
MUTED  = "#64748B"
LINE   = "#E2E8F0"
BLUE   = "#2563EB"
GREEN  = "#059669"
ORANGE = "#D97706"
PURPLE = "#7C3AED"
CYAN   = "#0891B2"
PINK   = "#DB2777"
SLATE  = "#94A3B8"
PALETTE = [BLUE, GREEN, ORANGE, PURPLE, CYAN, PINK, SLATE]


def color(i):
    """Palette colour i, cycling instead of running out after 7 series."""
    return PALETTE[i % len(PALETTE)]


def colors(n):
    """n colours, cycling when n > len(PALETTE)."""
    return [color(i) for i in range(n)]


# ------------------------------------------------------------------ output ---
def save(fig, out, dpi=150):
    """Write the figure: create parent dirs, white background, tight bbox."""
    out = os.path.abspath(out)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    fig.savefig(out, dpi=dpi, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print(out)
    return out


def bare(ax):
    """Drop top/right spines and tone down ticks."""
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(colors=MUTED, labelsize=9)
    return ax
