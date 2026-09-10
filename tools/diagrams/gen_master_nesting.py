#!/usr/bin/env python3
"""Generate Advanced/master-nesting.svg — nested (chained) master controls.

Verified against 4.3.3 TTemplateControl::injectContent() + initRecursive():
  - Each template control's own <com:TContent> tags are injected into its master's
    matching <com:TContentPlaceHolder>s (a Content fills a Placeholder).
  - A master is itself a template control: its Contents fill its own master's
    placeholders, and its template also contains placeholders (which may be embedded
    inside those very contents) for the more derived control to fill.
  - If a content's id matches no placeholder in the immediate master and that master has
    its own MasterClass, the content is forwarded up the chain to the next master.

Layout, base (left) to most-derived (right):
    Base Master Control   <-fills-   Child Master Control   <-fills-   Template Control (TPage)
The Child's Content "body" fills Base's "body" placeholder AND embeds the "sidebar"/"main"
placeholders the Page fills. The Page's Content "footer" has no placeholder in the Child,
so it is forwarded up to Base's "footer" placeholder. Scope: 4.3.3 only.

Usage:
    python3 tools/diagrams/gen_master_nesting.py

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

FONT = "Verdana, 'Segoe UI', -apple-system, sans-serif"
PAGE_FRAME, PAGE_STROKE = "#fdf7ec", "#b9992e"
CHILD_FRAME, CHILD_STROKE = "#eef7ea", "#5a8f45"
BASE_FRAME, BASE_STROKE = "#eaf2fb", "#4a78a8"
MASTER = "#7a4fb5"
ID = {"head": "#2f8f6f", "body": "#3f6fa0", "sidebar": "#a8548a", "main": "#b8862a", "footer": "#c05a3a"}
TIPGAP = 1.0                 # keep the arrow tip a hair off the target box (no penetration)

def rrect(o, x, y, w, h, fill, stroke, sw=1.2, rx=7, dash=None, shadow=False):
    da = f' stroke-dasharray="{dash}"' if dash else ''
    sh = ' filter="url(#ds)"' if shadow else ''
    o.append(f'  <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{da}{sh}/>')

def ctext(o, x, y, s, fs=10.5, fill="#1a1a1a", weight=None, italic=False, anchor="start"):
    fw = f' font-weight="{weight}"' if weight else ''
    it = ' font-style="italic"' if italic else ''
    o.append(f'  <text x="{x:.1f}" y="{y:.1f}" font-size="{fs}"{fw}{it} fill="{fill}" text-anchor="{anchor}" dominant-baseline="central">{esc(s)}</text>')

def content_box(o, x, y, w, h, cid):
    rrect(o, x, y, w, h, "#ffffff", ID[cid], sw=1.3, rx=6)
    ctext(o, x + w/2, y + h/2, f'Content  ID="{cid}"', fs=9.2, fill=ID[cid], weight=600, anchor="middle")

def placeholder_box(o, x, y, w, h, cid):
    rrect(o, x, y, w, h, "#ffffff", ID[cid], sw=1.2, rx=6, dash="5 3")
    ctext(o, x + w/2, y + h/2, f'Placeholder  ID="{cid}"', fs=8.8, fill=ID[cid], weight=600, anchor="middle")

def base_ph(o, x, w, y, h, cid, center=None):
    rrect(o, x, y, w, h, "#ffffff", ID[cid], sw=1.2, rx=6, dash="5 3")
    c = center if center is not None else y + h/2
    ctext(o, x + w/2, c - 6, "Placeholder", fs=8.6, fill=ID[cid], weight=700, anchor="middle")
    ctext(o, x + w/2, c + 6, f'ID="{cid}"', fs=9.2, fill=ID[cid], weight=700, anchor="middle")

def harrow(o, x1, x2_edge, y, color, sw=2.1):
    # stop the tip TIPGAP short of the target edge so the arrowhead never penetrates it
    endpoint = x2_edge + TIPGAP if x2_edge < x1 else x2_edge - TIPGAP
    o.append(f'  <line x1="{x1:.1f}" y1="{y:.1f}" x2="{endpoint:.1f}" y2="{y:.1f}" stroke="{color}" stroke-width="{sw}" marker-end="url(#fill)"/>')

W, H = 592, 418
o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}">']
o.append('''  <defs>
    <filter id="ds" x="-25%" y="-30%" width="150%" height="170%">
      <feDropShadow dx="0.7" dy="1.0" stdDeviation="0.8" flood-color="#000" flood-opacity="0.22"/>
    </filter>
    <marker id="fill" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7.5" markerHeight="7.5" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/>
    </marker>
  </defs>''')
o.append(f'  <rect x="0" y="0" width="{W}" height="{H}" fill="#fff"/>')

FTOP = 14
FBOT = 305                   # +5: extra margin below "(base — no master)" grows the frames
FH = FBOT - FTOP

# ---- column frames: Base (left), Child (middle), Page (right) ----
bfx, bfw = 12, 104
cfx, cfw = 160, 216
pfx, pfw = 420, 160
rrect(o, bfx, FTOP, bfw, FH, BASE_FRAME, BASE_STROKE, sw=1.4, rx=9, shadow=True)
ctext(o, bfx + bfw/2, FTOP + 14, "Base Master", fs=10, weight=700, fill=BASE_STROKE, anchor="middle")
ctext(o, bfx + bfw/2, FTOP + 26, "Control", fs=10, weight=700, fill=BASE_STROKE, anchor="middle")
ctext(o, bfx + bfw/2, FTOP + 38, "(base — no master)", fs=7.8, fill="#5a6b7a", italic=True, anchor="middle")
rrect(o, cfx, FTOP, cfw, FH, CHILD_FRAME, CHILD_STROKE, sw=1.4, rx=9, shadow=True)
ctext(o, cfx + cfw/2, FTOP + 15, "Child Master Control", fs=10.5, weight=700, fill=CHILD_STROKE, anchor="middle")
ctext(o, cfx + cfw/2, FTOP + 29, "MasterClass = Base Master Control", fs=8.0, fill="#4f6b45", italic=True, anchor="middle")
rrect(o, pfx, FTOP, pfw, FH, PAGE_FRAME, PAGE_STROKE, sw=1.4, rx=9, shadow=True)
ctext(o, pfx + pfw/2, FTOP + 14, "Template Control", fs=10, weight=700, fill=PAGE_STROKE, anchor="middle")
ctext(o, pfx + pfw/2, FTOP + 26, "(TPage)", fs=10, weight=700, fill=PAGE_STROKE, anchor="middle")
ctext(o, pfx + pfw/2, FTOP + 38, "MasterClass = Child Master Control", fs=7.6, fill="#8a7326", italic=True, anchor="middle")

# ---- row geometry (generous, even gaps) ----
# SHIFT moves everything below the title band down by 3px. Every row uses an ABSOLUTE
# anchor (already including SHIFT), so a nested box and its contents each shift once.
SHIFT = 5
BOX_H = 38
HEAD_C = 81 + SHIFT
HEAD_Y = HEAD_C - BOX_H/2
BODY_TOP = 112 + SHIFT
BODY_LABEL_Y = BODY_TOP + 13              # blue arrow aligns here
SIDE_C = 155 + SHIFT
MAIN_C = 205 + SHIFT
BODY_BOT = MAIN_C + BOX_H/2 + 12
BODY_H = BODY_BOT - BODY_TOP
FOOT_C = 267 + SHIFT
FOOT_Y = FOOT_C - BOX_H/2

# ---- Base placeholders (left): head, body, footer ----
bpx, bpw = bfx + 9, bfw - 18
base_ph(o, bpx, bpw, HEAD_Y, BOX_H, "head")
base_ph(o, bpx, bpw, BODY_TOP, BODY_H, "body", center=BODY_TOP + 16)   # top-aligned label
base_ph(o, bpx, bpw, FOOT_Y, BOX_H, "footer")

# ---- Child contents (middle); Content head matches Content body width ----
cb_x, cb_w = cfx + 10, cfw - 20
ch_x, ch_w = cb_x, cb_w
content_box(o, ch_x, HEAD_Y, ch_w, BOX_H, "head")
rrect(o, cb_x, BODY_TOP, cb_w, BODY_H, "#ffffff", ID["body"], sw=1.4, rx=7)
ctext(o, cb_x + cb_w/2, BODY_LABEL_Y, 'Content  ID="body"', fs=9.2, fill=ID["body"], weight=600, anchor="middle")
# embedded placeholders with EQUAL left/right margins inside the body box
emb_m = 12
emb_x, emb_w = cb_x + emb_m, cb_w - 2 * emb_m
placeholder_box(o, emb_x, SIDE_C - BOX_H/2, emb_w, BOX_H, "sidebar")
placeholder_box(o, emb_x, MAIN_C - BOX_H/2, emb_w, BOX_H, "main")

# ---- Page contents (right) ----
pc_x, pc_w = pfx + 12, pfw - 24
content_box(o, pc_x, SIDE_C - BOX_H/2, pc_w, BOX_H, "sidebar")
content_box(o, pc_x, MAIN_C - BOX_H/2, pc_w, BOX_H, "main")
content_box(o, pc_x, FOOT_Y, pc_w, BOX_H, "footer")

# ---- fill arrows (Content fills Placeholder; all point left toward the master) ----
harrow(o, ch_x, bpx + bpw, HEAD_C, ID["head"])                 # Child head -> Base head
harrow(o, cb_x, bpx + bpw, BODY_LABEL_Y, ID["body"])           # Child body -> Base body (aligned to label)
harrow(o, pc_x, emb_x + emb_w, SIDE_C, ID["sidebar"])          # Page sidebar -> Child sidebar
harrow(o, pc_x, emb_x + emb_w, MAIN_C, ID["main"])             # Page main -> Child main
harrow(o, pc_x, bpx + bpw, FOOT_C, ID["footer"])               # Page footer -> Base footer (forwarded)
ctext(o, cfx + cfw/2, FOOT_C - 13, "forwarded through Child", fs=7.8, fill=ID["footer"], italic=True, anchor="middle")

# ---- MasterClass arrows between frames (top band) ----
harrow(o, pfx, cfx + cfw, FTOP + 16, MASTER, sw=2.3)           # Page -> Child
harrow(o, cfx, bfx + bfw, FTOP + 16, MASTER, sw=2.3)           # Child -> Base

# ---- Legend, enclosed in its own padded box (bottom-left) ----
# Equal padding all sides; the three items are equidistant; each swatch is vertically
# centred on its text; the MasterClass arrow points left (as it does in the diagram).
lgx, lgy = 12, FBOT + 14
pad = 12
SWH = 13                       # swatch height
ITEMSP = 19                    # equal spacing between item centres
_items = ["MasterClass — declared master", "Placeholder — TContentPlaceHolder", "Content — TContent"]
lgw = int(2 * pad + 38 + max(text_px(s, 8.3) for s in _items) + 8)   # tight to the widest item text
title_y = lgy + pad + 4
i1 = title_y + 19
i2 = i1 + ITEMSP
i3 = i2 + ITEMSP
lgh = (i3 + SWH/2 + pad) - lgy
rrect(o, lgx, lgy, lgw, lgh, "#fafafa", "#c8c8c8", sw=1.0, rx=6)
ctext(o, lgx + pad, title_y, "Legend", fs=9, weight=700, fill="#444")
sx = lgx + pad                 # swatch left edge
tx = lgx + pad + 38            # text left edge
# item 1: MasterClass arrow, pointing left, centred on i1
o.append(f'  <line x1="{sx+28:.1f}" y1="{i1:.1f}" x2="{sx:.1f}" y2="{i1:.1f}" stroke="{MASTER}" stroke-width="2.3" marker-end="url(#fill)"/>')
ctext(o, tx, i1, "MasterClass — declared master", fs=8.3, fill="#555")
# item 2: Placeholder swatch (dashed), centred on i2
rrect(o, sx, i2 - SWH/2, 28, SWH, "#ffffff", "#7a7a7a", sw=1.1, rx=4, dash="4 2")
ctext(o, tx, i2, "Placeholder — TContentPlaceHolder", fs=8.3, fill="#555")
# item 3: Content swatch (solid), centred on i3
rrect(o, sx, i3 - SWH/2, 28, SWH, "#ffffff", "#7a7a7a", sw=1.3, rx=4)
ctext(o, tx, i3, "Content — TContent", fs=8.3, fill="#555")

# ---- caption: centred between the legend's right edge and the SVG's right edge ----
cap_cx = (lgx + lgw + W) / 2
cap_cy = lgy + lgh/2
ctext(o, cap_cx, cap_cy - 7, "Contents fill the master's matching Placeholders.", fs=8.4, fill="#888", italic=True, anchor="middle")
ctext(o, cap_cx, cap_cy + 8, "No match in the immediate master → forwarded up the chain.", fs=8.4, fill="#888", italic=True, anchor="middle")

o.append('</svg>')
path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "quickstart", "protected", "pages", "Advanced", "master-nesting.svg"))
with open(path, "w") as f:
    f.write("\n".join(o))
print(f"wrote {path}  {W}x{H}")
