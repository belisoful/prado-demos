#!/usr/bin/env python3
"""Generate Fundamentals/controls-tree.svg — control tree, naming containers, and the
composition of ID / UniqueID / ClientID.

Verified against 4.3.3 TControl:
  - A control's naming container is the nearest ancestor implementing INamingContainer.
  - ID_SEPARATOR = '$', CLIENT_ID_SEPARATOR = '_'.
  - UniqueID = namingContainer.UniqueID + '$' + ID (a control directly under the page is
    just its own ID); ClientID = strtr(UniqueID, '$', '_').
  - findControl(idPath) converts '.' to '$' and walks the naming containers.

The example mirrors the page's own findControl("Repeater1.Item1.Button1"): a repeater whose
two items each hold a Button1/Label1 with the same IDs, differentiated by the item naming
container. Scope: 4.3.3 only. Python 3 stdlib only.

Usage: python3 tools/diagrams/gen_controls_tree.py
"""
import html, os

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
def text_px(s, fs): return sum(VW.get(ord(c), 636.0) for c in s)/1000.0*fs

FONT = "Verdana, 'Segoe UI', -apple-system, sans-serif"
CTRL = ("#dbe9f6", "#4a78a8")     # ordinary control
NC   = ("#e7ddf2", "#7a4fb5")     # naming container
HI   = "#c0512e"                  # highlighted target path
LINE = "#9aa0a6"
LEFT, TOP = 16, 52
ROW_H, INDENT, BOX_H = 33, 22, 23   # a moderate increase over the original 27
FS = 9.6

# (class, id, is_naming_container, highlighted, depth)
NODES = [
    ("TPage",          None,       True,  True,  0),
    ("TForm",          None,       False, False, 1),
    ("TRepeater",      "Repeater1", True, True,  2),
    ("TRepeaterItem",  "Item0",    True,  False, 3),
    ("TButton",        "Button1",  False, False, 4),
    ("TLabel",         "Label1",   False, False, 4),
    ("TRepeaterItem",  "Item1",    True,  True,  3),
    ("TButton",        "Button1",  False, True,  4),
    ("TLabel",         "Label1",   False, False, 4),
]

o = []
def rrect(x, y, w, h, fill, stroke, rx=6, sw=1.1, dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ''
    o.append(f'  <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{da}/>')
def txt(x, y, s, fs=FS, fill="#1a1a1a", weight=None, anchor="start", italic=False, family=None):
    fw = f' font-weight="{weight}"' if weight else ''
    it = ' font-style="italic"' if italic else ''
    fm = f' font-family="{family}"' if family else ''
    o.append(f'  <text x="{x:.1f}" y="{y:.1f}" font-size="{fs}"{fw}{it}{fm} fill="{fill}" text-anchor="{anchor}" dominant-baseline="central">{esc(s)}</text>')

# layout tree rows
rows = []
for i, (cls, cid, nc, hi, depth) in enumerate(NODES):
    idpart = "" if cid is None else f' ID="{cid}"'
    w = text_px(cls, FS)*1.06 + text_px(idpart, FS) + 18   # 1.06: class is rendered bold
    x = LEFT + depth*INDENT
    y = TOP + i*ROW_H
    rows.append(dict(cls=cls, idpart=idpart, cid=cid, nc=nc, hi=hi, depth=depth, x=x, y=y, w=w, mid=y+BOX_H/2, cx=x+11))

TREE_R = round(max(r["x"]+r["w"] for r in rows))
# legend box (below the tree), equal padding all sides
LGY = TOP + len(rows)*ROW_H + 14
LG_P = 12
LG_H = 2*LG_P + 63.5      # top pad + title + items block (see legend drawing) + bottom pad
# panel geometry
PX = TREE_R + 40
PW = 300
W = PX + PW + 16
H = round(max(LGY + LG_H + 12, 314))

svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}">']
svg.append(f'  <rect x="0" y="0" width="{W}" height="{H}" fill="#fff"/>')
o = svg

# --- title, centred over the tree column, larger + underlined ---
tc = (LEFT + TREE_R) / 2
txt(tc, 24, "Control Tree", fs=13, weight=700, fill="#333", anchor="middle")
_tw = text_px("Control Tree", 13)
o.append(f'  <line x1="{tc-_tw/2:.1f}" y1="33" x2="{tc+_tw/2:.1f}" y2="33" stroke="#333" stroke-width="1.1"/>')

# --- tree connectors (parent rail to children) ---
# build parent index by depth stack
stack = {}
for idx, r in enumerate(rows):
    stack[r["depth"]] = idx
    if r["depth"] > 0:
        p = stack[r["depth"]-1]
        pr = rows[p]
        col = HI if (r["hi"] and pr["hi"]) else LINE
        sw = 1.6 if col == HI else 1.0
        o.append(f'  <line x1="{pr["cx"]:.1f}" y1="{r["mid"]:.1f}" x2="{r["x"]:.1f}" y2="{r["mid"]:.1f}" stroke="{col}" stroke-width="{sw}"/>')
        o.append(f'  <line x1="{pr["cx"]:.1f}" y1="{pr["mid"]+BOX_H/2:.1f}" x2="{pr["cx"]:.1f}" y2="{r["mid"]:.1f}" stroke="{col}" stroke-width="{sw}"/>')

# --- tree nodes ---
for r in rows:
    fill, stroke = (NC if r["nc"] else CTRL)
    rrect(r["x"], r["y"], r["w"], BOX_H, fill, stroke, sw=1.1)
    if r["hi"]:
        rrect(r["x"]-1.5, r["y"]-1.5, r["w"]+3, BOX_H+3, "none", HI, rx=7, sw=2.0)
    _lab = f'<tspan font-weight="700">{esc(r["cls"])}</tspan>'
    if r["idpart"]:
        _lab += f'<tspan fill="#555">{esc(r["idpart"])}</tspan>'
    o.append(f'  <text x="{r["x"]+9:.1f}" y="{r["mid"]:.1f}" font-size="{FS}" fill="#1a1a1a" text-anchor="start" dominant-baseline="central">{_lab}</text>')

# --- legend, in a titled box, equal padding all sides ---
_items = ["naming container (INamingContainer)", "ordinary control", "the highlighted target path"]
lgw = 2*LG_P + 15 + 7 + max(text_px(t, 8.6) for t in _items)   # pad + swatch + gap + text + pad
rrect(LEFT, LGY, lgw, LG_H, "#fbfbf9", "#c4c4c4", rx=7, sw=1)
sx, tx = LEFT+LG_P, LEFT+LG_P+22
txt(sx, LGY+LG_P+5, "Legend", fs=9.5, weight=700, fill="#444")
i0 = LGY+LG_P+23
r1, r2, r3 = i0, i0+17, i0+34
rrect(sx, r1-6.5, 15, 13, NC[0], NC[1]);   txt(tx, r1, _items[0], fs=8.6, fill="#555")
rrect(sx, r2-6.5, 15, 13, CTRL[0], CTRL[1]); txt(tx, r2, _items[1], fs=8.6, fill="#555")
o.append(f'  <rect x="{sx:.1f}" y="{r3-6.5:.1f}" width="15" height="13" rx="4" fill="none" stroke="{HI}" stroke-width="2"/>')
txt(tx, r3, _items[2], fs=8.6, fill="#555")

# --- identifier panel ---
rrect(PX, 40, PW, 156, "#fbfbf9", "#c4c4c4", rx=8, sw=1)
txt(PX+14, 58, "Identifiers of the highlighted", fs=10, weight=700, fill="#333")
txt(PX+14, 72, "TButton  (Item1 → Button1)", fs=10, weight=700, fill="#333")
MONO = "'DejaVu Sans Mono', 'SFMono-Regular', Menlo, Consolas, monospace"
def kv(y, k, v, vfill="#1a1a1a"):
    txt(PX+14, y, k, fs=9, fill="#555", weight=700)
    txt(PX+92, y, v, fs=9.2, fill=vfill, family=MONO)
kv(96,  "ID", "Button1")
kv(114, "UniqueID", "Repeater1 $ Item1 $ Button1", HI)
kv(132, "ClientID", "Repeater1 _ Item1 _ Button1", "#2f6f4f")
o.append(f'  <line x1="{PX+14:.1f}" y1="148" x2="{PX+PW-14:.1f}" y2="148" stroke="#ddd" stroke-width="1"/>')
txt(PX+14, 162, "UniqueID joins the naming-container IDs", fs=8.5, fill="#666", italic=True)
txt(PX+14, 174, "with $ ; ClientID replaces $ with _ .", fs=8.5, fill="#666", italic=True)
txt(PX+14, 186, "Treat the format as internal.", fs=8.5, fill="#666", italic=True)

# --- findControl panel ---
FY = 210
rrect(PX, FY, PW, 92, "#f4f7fb", "#9fb6cf", rx=8, sw=1)
txt(PX+14, FY+16, "findControl(\"Repeater1.Item1.Button1\")", fs=9, weight=700, fill="#2f5a86", family=MONO)
txt(PX+14, FY+34, "dots become $ ; the search walks the", fs=8.8, fill="#555")
txt(PX+14, FY+46, "naming containers, step by step:", fs=8.8, fill="#555")
txt(PX+14, FY+64, "Page ▸ Repeater1 ▸ Item1 ▸ Button1", fs=9.2, weight=700, fill=HI, family=MONO)
txt(PX+14, FY+82, "null if nothing matches; error if two", fs=8.6, fill="#777", italic=True)

o.append('</svg>')
path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "quickstart", "protected", "pages", "Fundamentals", "controls-tree.svg"))
with open(path, "w") as f:
    f.write("\n".join(o))
print(f"wrote {path}  {W}x{H}")
