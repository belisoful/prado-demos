#!/usr/bin/env python3
"""Generate the two Advanced/MasterContent diagrams (replace mastercontent.gif + pcrelation.gif).

  - Advanced/mastercontent.svg : each TContent is inserted into the TContentPlaceHolder
    with the matching ID (the decorator step). Content blocks and placeholders are
    color-coded by ID so the ID matching reads at a glance.
  - Advanced/pcrelation.svg : the resulting parent-child tree. The template control keeps
    only the master control as its child; the master control keeps its own static content
    ("other stuff") with the placeholders replaced by the matched contents.

Faithful to the legacy GIFs, redrawn crisp and color-coded. Scope: 4.3.3 only.

Usage:
    python3 tools/diagrams/gen_mastercontent.py

Requires: Python 3 standard library only.
"""
import html
import os

def esc(s): return html.escape(s, quote=True)

VW = {
    32:352.0, 33:394.0, 34:459.0, 35:818.0, 36:636.0, 37:1076.0, 38:727.0, 39:269.0, 40:454.0, 41:454.0, 42:636.0, 43:818.0,
    44:364.0, 45:454.0, 46:364.0, 47:454.0, 48:636.0, 49:636.0, 50:636.0, 51:636.0, 52:636.0, 53:636.0, 54:636.0, 55:636.0,
    56:636.0, 57:636.0, 58:454.0, 59:454.0, 60:818.0, 61:818.0, 62:818.0, 63:545.0, 64:1000.0, 65:684.0, 66:686.0, 67:698.0,
    68:771.0, 69:632.0, 70:575.0, 71:775.0, 72:751.0, 73:421.0, 74:455.0, 75:693.0, 76:557.0, 77:843.0, 78:748.0, 79:787.0,
    80:603.0, 81:787.0, 82:695.0, 83:684.0, 84:616.0, 85:732.0, 86:684.0, 87:989.0, 88:685.0, 89:615.0, 90:685.0, 91:454.0,
    92:454.0, 93:454.0, 94:818.0, 95:636.0, 96:636.0, 97:601.0, 98:623.0, 99:521.0, 100:623.0, 101:596.0, 102:352.0, 103:623.0,
    104:633.0, 105:274.0, 106:344.0, 107:592.0, 108:274.0, 109:973.0, 110:633.0, 111:607.0, 112:623.0, 113:623.0, 114:427.0, 115:521.0,
    116:394.0, 117:633.0, 118:592.0, 119:818.0, 120:592.0, 121:592.0, 122:525.0, 123:635.0, 124:454.0, 125:635.0, 126:818.0,
}
def text_px(s, fs):
    return sum(VW.get(ord(c), 636.0) for c in s) / 1000.0 * fs

STROKE = "#2f2f2f"
ID_FILL = {"A": "#f6e3b0", "B": "#d8ecd0", "C": "#f0d9e6"}
ID_STROKE = {"A": "#c09a3a", "B": "#5a8f45", "C": "#a8548a"}
CONTAINER_L = "#eef1f5"
CONTAINER_R = "#e7eef8"
NEUTRAL_FILL = "#efefef"
NEUTRAL_STROKE = "#9a9a9a"
FONT = "Verdana, 'Segoe UI', -apple-system, sans-serif"

def svg_open(W, H):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}">',
            f'''  <defs>
    <filter id="ds" x="-25%" y="-30%" width="150%" height="170%">
      <feDropShadow dx="0.7" dy="1.0" stdDeviation="0.8" flood-color="#000" flood-opacity="0.22"/>
    </filter>
    <marker id="arrow" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7.5" markerHeight="7.5" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/>
    </marker>
  </defs>''',
            f'  <rect x="0" y="0" width="{W}" height="{H}" fill="#fff"/>']

def rrect(o, x, y, w, h, fill, stroke, sw=1.2, rx=6, dash=None, shadow=True):
    da = f' stroke-dasharray="{dash}"' if dash else ''
    sh = ' filter="url(#ds)"' if shadow else ''
    o.append(f'  <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{da}{sh}/>')

def ctext(o, x, y, s, fs=10.5, fill="#1a1a1a", weight=None, italic=False, anchor="middle"):
    fw = f' font-weight="{weight}"' if weight else ''
    it = ' font-style="italic"' if italic else ''
    o.append(f'  <text x="{x:.1f}" y="{y:.1f}" font-size="{fs}"{fw}{it} fill="{fill}" text-anchor="{anchor}" dominant-baseline="central">{esc(s)}</text>')

def write(o, fname):
    o.append('</svg>')
    path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "quickstart", "protected", "pages", "Advanced", fname))
    with open(path, "w") as f:
        f.write("\n".join(o))
    print(f"wrote {path}")

# ---------------------------------------------------------------- mastercontent.svg
def build_mastercontent():
    W, H = 470, 300
    o = svg_open(W, H)
    # containers
    lx, lw = 14, 150
    rx, rw = 258, 198
    cy_top, ch = 44, 236
    rrect(o, lx, cy_top, lw, ch, CONTAINER_L, "#8a8a8a", sw=1.1, rx=10)
    rrect(o, rx, cy_top, rw, ch, CONTAINER_R, "#8a8a8a", sw=1.1, rx=10)
    ctext(o, lx + lw/2, 30, "Template Control", fs=11.5, weight=700)
    ctext(o, rx + rw/2, 30, "Master Control", fs=11.5, weight=700)

    # left content blocks, right placeholders sharing one y per row (fully horizontal arrows)
    cw, chh = 116, 46
    cxl = lx + (lw - cw) / 2
    pw, phh = 128, 42
    cxr = rx + (rw - pw) / 2
    ids = ["A", "B", "C"]
    ys = [90, 162, 234]                       # shared content+placeholder centre y
    # "other stuff" static lines, centred in each gap (above / between / below placeholders)
    tops = [y - phh/2 for y in ys]
    bots = [y + phh/2 for y in ys]
    mids = [(cy_top + tops[0]) / 2]
    mids += [(bots[i] + tops[i+1]) / 2 for i in range(len(ys) - 1)]
    mids += [(bots[-1] + (cy_top + ch)) / 2]
    for my in mids:
        ctext(o, rx + rw/2, my, "other stuff", fs=9.2, fill="#8a8a8a", italic=True)
    # arrows first (behind blocks), horizontal
    for cid, y in zip(ids, ys):
        o.append(f'  <line x1="{cxl+cw:.1f}" y1="{y:.1f}" x2="{cxr-3:.1f}" y2="{y:.1f}" stroke="{ID_STROKE[cid]}" stroke-width="2.1" marker-end="url(#arrow)"/>')
    for cid, y in zip(ids, ys):
        rrect(o, cxl, y - chh/2, cw, chh, ID_FILL[cid], ID_STROKE[cid], sw=1.2)
        ctext(o, cxl + cw/2, y, f"Content {cid}", fs=10.5, weight=600)
        rrect(o, cxr, y - phh/2, pw, phh, "#ffffff", ID_STROKE[cid], sw=1.2, dash="5 3")
        ctext(o, cxr + pw/2, y, f"Placeholder {cid}", fs=10.5, weight=600, fill=ID_STROKE[cid])
    ctext(o, W/2, H - 10, "each TContent is inserted into the TContentPlaceHolder with the matching ID", fs=9.0, fill="#666", italic=True)
    write(o, "mastercontent.svg")

# ---------------------------------------------------------------- pcrelation.svg
def build_pcrelation():
    # tree: Template Control -> Master Control -> [ …, Content A, Content B, …, Content C ]
    kids = [("…", None), ("Content A", "A"), ("Content B", "B"), ("…", None), ("Content C", "C")]
    KW = {None: 58, "A": 90, "B": 90, "C": 90}
    KH = 46
    GAP = 20
    total = sum(KW[k[1]] for k in kids) + GAP * (len(kids) - 1)
    W = int(total + 40)
    H = 250
    o = svg_open(W, H)
    cx = W / 2
    # root + master
    nw, nh = 128, 40
    root_cy, mast_cy = 30, 108
    bus_y = 158
    kid_cy = 200
    rrect(o, cx - nw/2, root_cy - nh/2, nw, nh, "#e7eef8", "#5a7fa8", sw=1.3)
    ctext(o, cx, root_cy, "Template Control", fs=11, weight=700)
    rrect(o, cx - nw/2, mast_cy - nh/2, nw, nh, "#e7eef8", "#5a7fa8", sw=1.3)
    ctext(o, cx, mast_cy, "Master Control", fs=11, weight=700)
    o.append(f'  <line x1="{cx:.1f}" y1="{root_cy+nh/2:.1f}" x2="{cx:.1f}" y2="{mast_cy-nh/2:.1f}" stroke="{STROKE}" stroke-width="1.3"/>')
    # bus from master down
    o.append(f'  <line x1="{cx:.1f}" y1="{mast_cy+nh/2:.1f}" x2="{cx:.1f}" y2="{bus_y:.1f}" stroke="{STROKE}" stroke-width="1.3"/>')
    # child x centers
    x = (W - total) / 2
    centers = []
    for lab, cid in kids:
        w = KW[cid]
        centers.append((x + w/2, w, lab, cid))
        x += w + GAP
    o.append(f'  <line x1="{centers[0][0]:.1f}" y1="{bus_y:.1f}" x2="{centers[-1][0]:.1f}" y2="{bus_y:.1f}" stroke="{STROKE}" stroke-width="1.3"/>')
    for xc, w, lab, cid in centers:
        o.append(f'  <line x1="{xc:.1f}" y1="{bus_y:.1f}" x2="{xc:.1f}" y2="{kid_cy-KH/2:.1f}" stroke="{STROKE}" stroke-width="1.3"/>')
        if cid is None:
            rrect(o, xc - w/2, kid_cy - KH/2, w, KH, NEUTRAL_FILL, NEUTRAL_STROKE, sw=1.1)
            ctext(o, xc, kid_cy - 8, "other", fs=8.6, fill="#777")
            ctext(o, xc, kid_cy + 6, "stuff", fs=8.6, fill="#777")
        else:
            rrect(o, xc - w/2, kid_cy - KH/2, w, KH, ID_FILL[cid], ID_STROKE[cid], sw=1.2)
            ctext(o, xc, kid_cy, lab, fs=10.5, weight=600)
    ctext(o, W/2, H - 12, "the placeholders are replaced by the matched contents; other master content is kept", fs=9.0, fill="#666", italic=True)
    write(o, "pcrelation.svg")

build_mastercontent()
build_pcrelation()
