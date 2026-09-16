#!/usr/bin/env python3
"""Generate Advanced/themes.svg — theme directory + property-value precedence.

Verified against 4.3.3:
  - A theme is a directory of .skin files, CSS and JavaScript. A CSS file named
    name.<media>.css applies to that media only (e.g. app.print.css -> print).
  - A skin applies to a control when the control type AND SkinID both match; an empty
    SkinID matches controls whose SkinID is unset/empty (Themes.page).
  - Application order (TTemplate::instantiateIn + TControl):
      1. StyleSheetTheme skin  (applyStyleSheetSkin, before the template) -> INITIAL values
      2. the control's template markup                                    -> overrides #1
      3. Theme skin            (applyControlSkin, after the template)      -> OVERWRITES
    So for a property the precedence is  Theme > template markup > StyleSheetTheme.

Scope: 4.3.3 only. Python 3 stdlib only.
Usage: python3 tools/diagrams/gen_themes.py
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
MONO = "'DejaVu Sans Mono', 'SFMono-Regular', Menlo, Consolas, monospace"
DIR  = ("#f6ecd0", "#b89a4a")
SKIN = ("#f6e6c8", "#b8862a")
CSS  = ("#dbe9f6", "#4a78a8")
JS   = ("#dcecd6", "#5a8f45")
THEME_L = ("#dcecd6", "#5a8f45")   # Theme skin (wins)
TPL_L   = ("#dbe9f6", "#4a78a8")   # template markup
SS_L    = ("#f6e6c8", "#b8862a")   # StyleSheetTheme skin
LINE = "#9aa0a6"; ARROW = "#4a4a4a"

o = []
def rrect(x, y, w, h, fill, stroke, rx=6, sw=1.1, shadow=True):
    sh = ' filter="url(#ds)"' if shadow else ''
    o.append(f'  <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{sh}/>')
def txt(x, y, s, fs=9.4, fill="#1a1a1a", weight=None, anchor="start", italic=False, family=None):
    fw = f' font-weight="{weight}"' if weight else ''
    it = ' font-style="italic"' if italic else ''
    fm = f' font-family="{family}"' if family else ''
    o.append(f'  <text x="{x:.1f}" y="{y:.1f}" font-size="{fs}"{fw}{it}{fm} fill="{fill}" text-anchor="{anchor}" dominant-baseline="central">{esc(s)}</text>')
def title(cx, y, s):
    txt(cx, y, s, fs=12, weight=700, fill="#333", anchor="middle")
    tw = text_px(s, 12)*1.07   # bold width, so the underline spans the whole title
    o.append(f'  <line x1="{cx-tw/2:.1f}" y1="{y+9:.1f}" x2="{cx+tw/2:.1f}" y2="{y+9:.1f}" stroke="#333" stroke-width="1.1"/>')

W, H = 664, 308
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}">']
svg.append('''  <defs>
    <filter id="ds" x="-25%" y="-30%" width="150%" height="170%">
      <feDropShadow dx="0.6" dy="0.9" stdDeviation="0.7" flood-color="#000" flood-opacity="0.18"/>
    </filter>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7.5" markerHeight="7.5" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="''' + ARROW + '''"/>
    </marker>
  </defs>''')
svg.append(f'  <rect x="0" y="0" width="{W}" height="{H}" fill="#fff"/>')
o = svg

# ================= left: theme directory =================
LEFT, TOP, ROW_H, BOX_H, INDENT, FS = 16, 55, 28, 23, 20, 9.2
NODES = [
    ("themes/", DIR, 0, None),
    ("MyTheme/", DIR, 1, "the Theme (= directory name)"),
    ("Button.skin", SKIN, 2, "control skins"),
    ("Label.skin", SKIN, 2, "control skins"),
    ("app.css", CSS, 2, "CSS · all media"),
    ("app.print.css", CSS, 2, "CSS · print only"),
    ("app.js", JS, 2, "JavaScript"),
]
rows = []
for i, (name, col, depth, note) in enumerate(NODES):
    w = (text_px(name, FS)*1.06 if col is DIR else len(name)*FS*0.6) + 16   # DIR bold; files monospace
    x = LEFT + depth*INDENT
    y = TOP + i*ROW_H
    rows.append(dict(name=name, col=col, depth=depth, note=note, x=x, y=y, w=w, mid=y+BOX_H/2, cx=x+10))
fmax = max(r["w"] for r in rows if r["depth"] == 2)   # equal width for the items inside MyTheme/
for r in rows:
    if r["depth"] == 2:
        r["w"] = fmax
title(152, 30, "A theme directory")
# connectors
stack = {}
for r in rows:
    stack[r["depth"]] = r
    if r["depth"] > 0:
        pr = stack[r["depth"]-1]
        o.append(f'  <line x1="{pr["cx"]:.1f}" y1="{pr["mid"]+BOX_H/2:.1f}" x2="{pr["cx"]:.1f}" y2="{r["mid"]:.1f}" stroke="{LINE}" stroke-width="1"/>')
        o.append(f'  <line x1="{pr["cx"]:.1f}" y1="{r["mid"]:.1f}" x2="{r["x"]:.1f}" y2="{r["mid"]:.1f}" stroke="{LINE}" stroke-width="1"/>')
for r in rows:
    rrect(r["x"], r["y"], r["w"], BOX_H, r["col"][0], r["col"][1], sw=1.1)
    txt(r["x"]+8, r["mid"], r["name"], fs=FS, weight=(700 if r["col"] is DIR else None), family=(None if r["col"] is DIR else MONO))
    if r["note"]:
        txt(r["x"]+r["w"]+10, r["mid"], r["note"], fs=7.8, fill="#777", italic=True)   # close to its item

# ================= right: property-value precedence =================
RCX = 496
title(RCX, 30, "Property-value precedence")
def layer(cy, w, h, name, sub, col, tag=None):
    rrect(RCX-w/2, cy-h/2, w, h, col[0], col[1], rx=7, sw=1.3)
    txt(RCX, cy-6, name, fs=10, weight=700, anchor="middle")
    txt(RCX, cy+8, sub, fs=8.0, fill="#555", anchor="middle", italic=True)
    if tag:
        txt(RCX+w/2-8, cy-h/2+9, tag, fs=8.2, fill=col[1], weight=700, anchor="end")
LW = 300
layer(78, LW, 46, "Theme skin", "overwrites · applied after the template", THEME_L, tag="highest priority")
layer(150, LW, 38, "Template markup", "the control tag's own values", TPL_L, tag="medium priority")
layer(222, LW, 46, "StyleSheetTheme skin", "initial value · applied before the template", SS_L, tag="lowest priority")
# upward "overrides" arrows between layers
def up(y1, y2, label):
    o.append(f'  <line x1="{RCX:.1f}" y1="{y1:.1f}" x2="{RCX:.1f}" y2="{y2:.1f}" stroke="{ARROW}" stroke-width="1.3" marker-end="url(#arrow)"/>')
    txt(RCX+13, (y1+y2)/2, label, fs=7.8, fill="#666", italic=True, anchor="start")
up(150-19, 78+23, "overrides")
up(222-23, 150+19, "overrides")
# caption
txt(RCX, 262, "For a property, the highest layer that sets it wins.", fs=8.4, fill="#666", italic=True, anchor="middle")
txt(RCX, 275, "A skin matches when the control type and SkinID both match", fs=8.4, fill="#666", italic=True, anchor="middle")
txt(RCX, 287, "(an empty SkinID matches controls with no SkinID).", fs=8.4, fill="#666", italic=True, anchor="middle")

# note: the file names are illustrative, not prescribed
note = [
    "The file names are the developer's own choice, not fixed names.",
    "A control gets a skin from a matching tag inside a skin file",
    "(e.g. <com:TButton SkinID=\"Blue\"/>), not from the file name.",
    "For CSS, only the .<media> infix (as in app.print.css) is meaningful.",
]
for i, ln in enumerate(note):
    txt(20, 256 + i*12, ln, fs=7.8, fill="#777", italic=True)

o.append('</svg>')
path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "quickstart", "protected", "pages", "Advanced", "themes.svg"))
with open(path, "w") as f:
    f.write("\n".join(o))
print(f"wrote {path}  {W}x{H}")
