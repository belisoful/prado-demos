#!/usr/bin/env python3
"""Generate Configurations/urlmapping.svg — TUrlMapping, both directions.

From Configurations/UrlMapping.page (4.3.3):
  - Recognize: the request PATH_INFO is tested against the ordered pattern list; the FIRST
    pattern whose regex (and Verbs) matches decomposes the URL into the service parameter
    and the named GET parameters.
  - Construct (EnableCustomUrl): constructUrl(serviceParameter, params) delegates to the
    first pattern whose ServiceID/ServiceParameter match AND whose named parameters are all
    present in params; it fills the placeholders to build the friendly URL.

Uses the page's own blog example. Note pattern 2 (archive/{time}) shares the ListPost
service but needs a `time` param, so constructUrl('Posts.ListPost', {cat:2}) skips it and
uses pattern 3. Scope: 4.3.3 only. Python 3 stdlib only.
Usage: python3 tools/diagrams/gen_urlmapping.py
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
IO   = ("#eef1f5", "#7a8a9a")
REC  = "#4a78a8"     # recognize accent (blue)
CON  = "#5a8f45"     # construct accent (green)
REC_HL = ("#dbe9f6", "#4a78a8")
CON_HL = ("#dcecd6", "#5a8f45")
LINE = "#5a5a5a"
PATS = [("post/{id}", "Posts.ViewPost"), ("archive/{time}", "Posts.ListPost"), ("category/{cat}", "Posts.ListPost")]

o = []
def rrect(x, y, w, h, fill, stroke, rx=6, sw=1.1, shadow=True):
    sh = ' filter="url(#ds)"' if shadow else ''
    o.append(f'  <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{sh}/>')
def txt(x, y, s, fs=9.4, fill="#1a1a1a", weight=None, anchor="middle", italic=False, family=None):
    fw = f' font-weight="{weight}"' if weight else ''
    it = ' font-style="italic"' if italic else ''
    fm = f' font-family="{family}"' if family else ''
    o.append(f'  <text x="{x:.1f}" y="{y:.1f}" font-size="{fs}"{fw}{it}{fm} fill="{fill}" text-anchor="{anchor}" dominant-baseline="central">{esc(s)}</text>')
def arrow(x1, y1, x2, y2):
    o.append(f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{LINE}" stroke-width="1.4" marker-end="url(#arrow)"/>')

def iobox(cx, cy, w, lines, fs=8.8):
    h = 20 + len(lines)*12
    rrect(cx-w/2, cy-h/2, w, h, IO[0], IO[1], rx=6)
    y0 = cy - (len(lines)-1)*12/2
    for i, (s, mono) in enumerate(lines):
        txt(cx, y0+i*12, s, fs=fs, family=(MONO if mono else None))
    return h

def patbox(cx, cy, hl, hlcol, hlfill):
    w, rh, h = 214, 19, 86
    bx = cx - w/2
    rrect(bx, cy-h/2, w, h, "#fbfbf9", "#c4c4c4", rx=7)
    txt(cx, cy-h/2+12, "URL patterns · evaluated in order", fs=8.4, weight=700, fill="#555")
    ry0 = cy-h/2+30
    svc_x = bx + 122     # service names left-align at one column (both boxes share it)
    for i, (pat, svc) in enumerate(PATS):
        ry = ry0 + i*rh
        hlq = (i == hl)
        if hlq:
            rrect(bx+6, ry-rh/2+1, w-12, rh-2, hlfill, hlcol, rx=4, sw=1.2, shadow=False)
            txt(bx+13, ry, "✓", fs=9.6, fill=hlcol, weight=700, anchor="start")   # inside the box
        col = hlcol if hlq else "#333"
        txt(bx+26, ry, f"{i+1}", fs=8.4, fill=(hlcol if hlq else "#888"), weight=700, anchor="start")
        txt(bx+40, ry, pat, fs=8.6, family=MONO, fill=col, anchor="start")
        txt(svc_x, ry, f"→ {svc}", fs=8.2, fill=(hlcol if hlq else "#777"), anchor="start")
    return h

W, H = 810, 296
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}">']
svg.append('''  <defs>
    <filter id="ds" x="-25%" y="-30%" width="150%" height="170%">
      <feDropShadow dx="0.6" dy="0.9" stdDeviation="0.7" flood-color="#000" flood-opacity="0.18"/>
    </filter>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="''' + LINE + '''"/>
    </marker>
  </defs>''')
svg.append(f'  <rect x="0" y="0" width="{W}" height="{H}" fill="#fff"/>')
o = svg

IN_X, PAT_X, OUT_X = 100, 397, 710
IOW = 168
def alabel(x, y, s): txt(x, y-8, s, fs=7.6, fill="#555", italic=True)

# --- Recognize (top) ---
txt(16, 20, "Recognize a request  —  incoming URL → parameters", fs=10, weight=700, fill=REC, anchor="start")
ry = 80
iobox(IN_X, ry, IOW, [("request path", False), ("post/123", True)])
patbox(PAT_X, ry, 0, REC_HL[1], REC_HL[0])
iobox(OUT_X, ry, IOW, [("page = Posts.ViewPost", False), ("id = 123", False)])
arrow(IN_X+IOW/2, ry, PAT_X-107, ry);  alabel((IN_X+IOW/2+PAT_X-107)/2, ry, "tested top-down")
arrow(PAT_X+107, ry, OUT_X-IOW/2, ry); alabel((PAT_X+107+OUT_X-IOW/2)/2, ry, "first match → decompose")

# --- Construct (bottom) ---
txt(16, 165, "Construct a URL  —  constructUrl() → friendly URL", fs=10, weight=700, fill=CON, anchor="start")
cy = 225
iobox(IN_X, cy, IOW, [("constructUrl(", False), ("'Posts.ListPost', {cat:2})", True)])
ph = patbox(PAT_X, cy, 2, CON_HL[1], CON_HL[0])
iobox(OUT_X, cy, IOW, [("/index.php/category/2", True)])
arrow(IN_X+IOW/2, cy, PAT_X-107, cy);  alabel((IN_X+IOW/2+PAT_X-107)/2, cy, "by service + params")
arrow(PAT_X+107, cy, OUT_X-IOW/2, cy); alabel((PAT_X+107+OUT_X-IOW/2)/2, cy, "fill placeholders")
txt(PAT_X, cy+ph/2+15, "pattern 2 also maps to Posts.ListPost but needs a time parameter, so it is skipped.", fs=7.6, fill="#8a8a8a", italic=True)

o.append('</svg>')
path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "quickstart", "protected", "pages", "Configurations", "urlmapping.svg"))
with open(path, "w") as f:
    f.write("\n".join(o))
print(f"wrote {path}  {W}x{H}")
