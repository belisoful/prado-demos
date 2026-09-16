#!/usr/bin/env python3
"""Generate Advanced/error-handling.svg — PRADO exception hierarchy + error-template
selection with its language fallback.

Verified against 4.3.3 framework/Exceptions:
  - TException extends \\Exception.
  - TSystemException extends TException; its subclasses (framework-usage errors) include
    TConfigurationException, TInvalidDataValueException, TInvalidDataTypeException,
    TInvalidOperationException, TPhpErrorException, TIOException, TDbException,
    TNotSupportedException, THttpException.
  - TApplicationException extends TException (a separate branch, client-application errors).
  - THttpException uses StatusCode-specific templates: error<code>-<lang>.html falls back
    to error<code>.html; every other exception uses exception-<lang>.html falling back to
    exception.html. Templates resolve under ErrorTemplatePath (default
    framework/Exceptions/templates).

Note: the page text listed two classes that do not exist in 4.3.3
(TInvalidDataFormatException, TSecurityException) and mis-cased TDbException; this diagram
shows the verified set. Scope: 4.3.3 only. Python 3 stdlib only.

Usage: python3 tools/diagrams/gen_error_diagram.py
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
STRUCT = ("#eef1f5", "#7a8a9a")   # TException / TSystemException / TApplicationException
SUB    = ("#dbe9f6", "#4a78a8")   # ordinary subclasses / exception-template chain
HTTP   = ("#f6e6c8", "#b8862a")   # THttpException / error<code> template chain
LINE = "#9aa0a6"; ARROW = "#4a4a4a"

o = []
def rrect(x, y, w, h, fill, stroke, rx=6, sw=1.1):
    o.append(f'  <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
def txt(x, y, s, fs=9.6, fill="#1a1a1a", weight=None, anchor="start", italic=False, family=None):
    fw = f' font-weight="{weight}"' if weight else ''
    it = ' font-style="italic"' if italic else ''
    fm = f' font-family="{family}"' if family else ''
    o.append(f'  <text x="{x:.1f}" y="{y:.1f}" font-size="{fs}"{fw}{it}{fm} fill="{fill}" text-anchor="{anchor}" dominant-baseline="central">{esc(s)}</text>')
def arrow(pts, color=ARROW):
    d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    o.append(f'  <polyline points="{d}" fill="none" stroke="{color}" stroke-width="1.3" marker-end="url(#arrow)"/>')

# ---- exception hierarchy (indented tree) ----
LEFT, TOP, ROW_H, INDENT, BOX_H, FS = 16, 49, 28, 20, 22, 9.4
# (class, depth, kind)
NODES = [
    ("TException", 0, "struct"),
    ("TSystemException", 1, "struct"),
    ("TConfigurationException", 2, "sub"),
    ("TInvalidDataValueException", 2, "sub"),
    ("TInvalidDataTypeException", 2, "sub"),
    ("TInvalidOperationException", 2, "sub"),
    ("TPhpErrorException", 2, "sub"),
    ("TIOException", 2, "sub"),
    ("TDbException", 2, "sub"),
    ("TNotSupportedException", 2, "sub"),
    ("THttpException", 2, "http"),
    ("TApplicationException", 1, "struct"),
]
rows = []
for i, (cls, depth, kind) in enumerate(NODES):
    w = text_px(cls, FS) + 16   # uniform 8px padding on both sides (node text is not bold)
    x = LEFT + depth*INDENT
    y = TOP + i*ROW_H
    rows.append(dict(cls=cls, depth=depth, kind=kind, x=x, y=y, w=w, mid=y+BOX_H/2, cx=x+10))
TREE_R = round(max(r["x"]+r["w"] for r in rows))

PX = TREE_R + 34
W = 622
TREE_BOT = TOP + (len(NODES)-1)*ROW_H + BOX_H
LG_P = 10
LGH = 2*LG_P + 44        # title + 2 rows (two-column legend)
LGY = TREE_BOT - LGH            # colour legend bottom-aligned with the tree
H = round(max(TREE_BOT, LGY+LGH) + 6)

svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}">']
svg.append('''  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="''' + ARROW + '''"/>
    </marker>
  </defs>''')
svg.append(f'  <rect x="0" y="0" width="{W}" height="{H}" fill="#fff"/>')
o = svg

# tree title (centred over the tree, underlined)
tc = (LEFT + TREE_R)/2
txt(tc, 24, "Exception hierarchy", fs=12, weight=700, fill="#333", anchor="middle")
_tw = text_px("Exception hierarchy", 12)
o.append(f'  <line x1="{tc-_tw/2:.1f}" y1="33" x2="{tc+_tw/2:.1f}" y2="33" stroke="#333" stroke-width="1.1"/>')

# tree connectors
stack = {}
for r in rows:
    stack[r["depth"]] = r
    if r["depth"] > 0:
        pr = stack[r["depth"]-1]
        o.append(f'  <line x1="{pr["cx"]:.1f}" y1="{pr["mid"]+BOX_H/2:.1f}" x2="{pr["cx"]:.1f}" y2="{r["mid"]:.1f}" stroke="{LINE}" stroke-width="1"/>')
        o.append(f'  <line x1="{pr["cx"]:.1f}" y1="{r["mid"]:.1f}" x2="{r["x"]:.1f}" y2="{r["mid"]:.1f}" stroke="{LINE}" stroke-width="1"/>')
# tree nodes
for r in rows:
    fill, stroke = {"struct": STRUCT, "sub": SUB, "http": HTTP}[r["kind"]]
    rrect(r["x"], r["y"], r["w"], BOX_H, fill, stroke, sw=(1.4 if r["kind"] != "sub" else 1.1))
    txt(r["x"]+8, r["mid"], r["cls"], fs=FS)   # uniform weight -> exact, even padding

# ---- template selection panel (right) ----
cxp = (PX + W - 16)/2
txt(cxp, 24, "Selecting the error template", fs=12, weight=700, fill="#333", anchor="middle")
_tw2 = text_px("Selecting the error template", 12)
o.append(f'  <line x1="{cxp-_tw2/2:.1f}" y1="33" x2="{cxp+_tw2/2:.1f}" y2="33" stroke="#333" stroke-width="1.1"/>')

def box(cx, cy, w, h, lines, fill, stroke, fs=9, family=None, weight=None):
    rrect(cx-w/2, cy-h/2, w, h, fill, stroke, sw=1.2)
    y0 = cy - (len(lines)-1)*6.5
    for i, ln in enumerate(lines):
        txt(cx, y0+i*13, ln, fs=fs, family=family, weight=weight, anchor="middle")
def diamond(cx, cy, w, h, lines, fill, stroke):
    o.append(f'  <path d="M{cx:.1f},{cy-h/2:.1f} L{cx+w/2:.1f},{cy:.1f} L{cx:.1f},{cy+h/2:.1f} L{cx-w/2:.1f},{cy:.1f} Z" fill="{fill}" stroke="{stroke}" stroke-width="1.2"/>')
    y0 = cy - (len(lines)-1)*6.5
    for i, ln in enumerate(lines):
        txt(cx, y0+i*13, ln, fs=9, anchor="middle")

col_l, col_r = cxp-86, cxp+86
# proc box top aligned with the tree's first box (TOP), roomier arrow gaps below
proc_y, dia_y, t1_y, t2_y = TOP+15, 123, 190, 248
box(cxp, proc_y, 250, 30, ["TErrorHandler picks a template"], STRUCT[0], STRUCT[1], fs=9.4, weight=700)
diamond(cxp, dia_y, 150, 52, ["THttpException?"], "#f3ead6", "#b8862a")
# yes -> error chain (left, amber); no -> exception chain (right, blue)
arrow([(cxp, proc_y+15), (cxp, dia_y-26)])
arrow([(cxp-75, dia_y), (col_l, dia_y), (col_l, t1_y-15)])
arrow([(cxp+75, dia_y), (col_r, dia_y), (col_r, t1_y-15)])
txt(cxp-75, dia_y-9, "yes", fs=8.4, fill="#555", italic=True, anchor="middle")
txt(cxp+75, dia_y-9, "no", fs=8.4, fill="#555", italic=True, anchor="middle")
box(col_l, t1_y, 156, 28, ["error<code>-<lang>.html"], HTTP[0], HTTP[1], family=MONO, fs=8.6)
box(col_l, t2_y, 156, 28, ["error<code>.html"], HTTP[0], HTTP[1], family=MONO, fs=8.6)
box(col_r, t1_y, 156, 28, ["exception-<lang>.html"], SUB[0], SUB[1], family=MONO, fs=8.6)
box(col_r, t2_y, 156, 28, ["exception.html"], SUB[0], SUB[1], family=MONO, fs=8.6)
arrow([(col_l, t1_y+14), (col_l, t2_y-14)])
arrow([(col_r, t1_y+14), (col_r, t2_y-14)])
txt(col_l+8, (t1_y+t2_y)/2, "if missing", fs=7.8, fill="#777", italic=True, anchor="start")
txt(col_r+8, (t1_y+t2_y)/2, "if missing", fs=7.8, fill="#777", italic=True, anchor="start")
# note (extra gap above the legend)
ny = LGY - 30
txt(cxp, ny, "The client's preferred language is tried first, then the version with no language.", fs=8.4, fill="#666", italic=True, anchor="middle")
txt(cxp, ny+13, "Templates resolve under ErrorTemplatePath (default framework/Exceptions/templates).", fs=8.4, fill="#666", italic=True, anchor="middle")
# colour legend, two columns, centred under the flow, bottom-aligned with the tree
_col1 = [(STRUCT, "base classes"), (HTTP, "THttpException & templates")]
_col2 = [(SUB, "exceptions & templates")]
_c1w = max(text_px(t, 8.6) for _, t in _col1)
_c2w = max(text_px(t, 8.6) for _, t in _col2)
COLGAP = 18
lgw = 2*LG_P + 22 + _c1w + COLGAP + 22 + _c2w
lbx = cxp - lgw/2
rrect(lbx, LGY, lgw, LGH, "#fbfbf9", "#c4c4c4", rx=7, sw=1)
txt(lbx+lgw/2, LGY+LG_P+5, "Legend", fs=9, weight=700, fill="#444", anchor="middle")
_r0 = LGY+LG_P+21
_c1x, _c2x = lbx+LG_P, lbx+LG_P+22+_c1w+COLGAP
def _legitem(x, y, col, label):
    rrect(x, y-6, 15, 12, col[0], col[1], rx=3, sw=1)
    txt(x+22, y, label, fs=8.6, fill="#555")
for _i, (col, label) in enumerate(_col1):
    _legitem(_c1x, _r0+_i*17, col, label)
for _i, (col, label) in enumerate(_col2):
    _legitem(_c2x, _r0+_i*17, col, label)

o.append('</svg>')
path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "quickstart", "protected", "pages", "Advanced", "error-handling.svg"))
with open(path, "w") as f:
    f.write("\n".join(o))
print(f"wrote {path}  {W}x{H}")
