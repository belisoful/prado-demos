#!/usr/bin/env python3
"""Generate Controls/validation-flow.svg — the PRADO validation lifecycle.

From Controls/Validation.page (4.3.3):
  - A postback control whose CausesValidation is true triggers validation.
  - Only the validators in the trigger's ValidationGroup take part.
  - If EnableClientScript is true and the browser runs JavaScript, the selected validators
    run in the browser first; a failure blocks the submit (no round-trip). If not, the
    request is submitted straight to the server.
  - Validation is ALWAYS performed on the server; it sets Page.IsValid, which the event
    handler checks before doing its work.
  - TValidationSummary collects the failed validators' messages (by group).

Client / server phase bands; the client-side condition is a real decision. Scope: 4.3.3.
Usage: python3 tools/diagrams/gen_validation_flow.py
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
PROC = ("#dbe9f6", "#4a78a8")
DEC  = ("#f6e6c8", "#b8862a")
TERM = ("#eef1f5", "#7a8a9a")
OK   = ("#dcecd6", "#5a8f45")
FAIL = ("#f3ddd0", "#c0663a")
CLIENT_BAND = ("#f4f7fb", "#9fb6cf")
SERVER_BAND = ("#f3f6ee", "#a7bd8f")
LINE = "#4a4a4a"; LH = 12.6
BW = 252     # shared width of every blue process box

o = []
def rrect(x, y, w, h, fill, stroke, rx=7, sw=1.2, dash=None, shadow=True):
    da = f' stroke-dasharray="{dash}"' if dash else ''
    sh = ' filter="url(#ds)"' if shadow else ''
    o.append(f'  <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{da}{sh}/>')
def lines_at(cx, cy, lines, fs=9.4, fill="#1a1a1a", weight=None):
    fw = f' font-weight="{weight}"' if weight else ''
    y0 = cy - (len(lines)-1)*LH/2
    for i, ln in enumerate(lines):
        o.append(f'  <text x="{cx:.1f}" y="{y0+i*LH:.1f}" font-size="{fs}"{fw} fill="{fill}" text-anchor="middle" dominant-baseline="central">{esc(ln)}</text>')
def node(kind, cx, cy, w, h, lines, fill, stroke, fs=9.4, weight=None):
    if kind == "diamond":
        o.append(f'  <path d="M{cx:.1f},{cy-h/2:.1f} L{cx+w/2:.1f},{cy:.1f} L{cx:.1f},{cy+h/2:.1f} L{cx-w/2:.1f},{cy:.1f} Z" fill="{fill}" stroke="{stroke}" stroke-width="1.2" filter="url(#ds)"/>')
    else:
        rrect(cx-w/2, cy-h/2, w, h, fill, stroke, rx=(h/2 if kind == "term" else 7))
    lines_at(cx, cy, lines, fs=fs, weight=weight)
def arrow(pts):
    d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    o.append(f'  <polyline points="{d}" fill="none" stroke="{LINE}" stroke-width="1.4" marker-end="url(#arrow)"/>')
def lbl(x, y, s, anchor="middle"):
    o.append(f'  <text x="{x:.1f}" y="{y:.1f}" font-size="8.6" fill="#555" text-anchor="{anchor}" dominant-baseline="central" font-style="italic">{esc(s)}</text>')

W, H = 624, 642
CX = 196
RX = 430
BYP = 36     # bypass gutter x (left of the bands)
n_start = (CX, 34, 268, 44)
n_group = (CX, 108, BW, 42)
n_csdec = (CX, 186, 212, 58)
n_crun  = (CX, 274, BW, 34)
n_cdec  = (CX, 343, 120, 52)
n_srun  = (CX, 452, BW, 34)
n_sdec  = (CX, 521, 130, 52)
ok_c    = (CX, 610, 240, 40)
blk_c   = (RX, 343, 252, 46)
skip_c  = (RX, 521, 252, 46)

svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}">']
svg.append('''  <defs>
    <filter id="ds" x="-25%" y="-30%" width="150%" height="170%">
      <feDropShadow dx="0.7" dy="1.0" stdDeviation="0.8" flood-color="#000" flood-opacity="0.2"/>
    </filter>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="''' + LINE + '''"/>
    </marker>
  </defs>''')
svg.append(f'  <rect x="0" y="0" width="{W}" height="{H}" fill="#fff"/>')
o = svg

def band(y, h, fill, stroke, label, lblcol):
    rrect(56, y, 514, h, fill, stroke, rx=10, sw=1.1, dash="6 4", shadow=False)
    o.append(f'  <text x="68" y="{y+14:.1f}" font-size="9.4" font-weight="700" fill="{lblcol}" dominant-baseline="central">{esc(label)}</text>')
band(232, 156, CLIENT_BAND[0], CLIENT_BAND[1], "Client side", "#3f668c")
band(410, 156, SERVER_BAND[0], SERVER_BAND[1], "Server side", "#4d7238")

def top(n): return (n[0], n[1]-n[3]/2)
def bot(n): return (n[0], n[1]+n[3]/2)
def lft(n): return (n[0]-n[2]/2, n[1])
def rgt(n): return (n[0]+n[2]/2, n[1])

# spine
arrow([bot(n_start), top(n_group)])
arrow([bot(n_group), top(n_csdec)])
arrow([bot(n_csdec), top(n_crun)])
arrow([bot(n_crun), top(n_cdec)])
arrow([bot(n_cdec), top(n_srun)])
arrow([bot(n_srun), top(n_sdec)])
arrow([bot(n_sdec), top(ok_c)])
# client-off bypass: csdec "no" runs down the left gutter into the server run box
arrow([lft(n_csdec), (BYP, n_csdec[1]), (BYP, n_srun[1]), lft(n_srun)])
# failures to the right
arrow([rgt(n_cdec), lft(blk_c)])
arrow([rgt(n_sdec), lft(skip_c)])

# labels at exits
lbl(CX+11, bot(n_csdec)[1]+5, "yes", "start")          # off the diamond, above the Client side box
lbl(CX+11, bot(n_cdec)[1]+5, "yes · submit", "start")  # inside the Client side box, under "all valid?"
lbl(CX+11, bot(n_sdec)[1]+5, "yes", "start")           # inside the Server side box
lbl((lft(n_csdec)[0]+BYP)/2, n_csdec[1]-10, "no")       # all three "no" labels: uniform 10px above the line
lbl(BYP+7, n_csdec[1]+14, "client script off", "start")  # near the no exit, a little lower
lbl((rgt(n_cdec)[0]+lft(blk_c)[0])/2-3, n_cdec[1]-10, "no")
lbl((rgt(n_sdec)[0]+lft(skip_c)[0])/2-3, n_sdec[1]-10, "no")

# nodes
node("term", *n_start, ["A postback control is clicked", "(CausesValidation = true)"], TERM[0], TERM[1], weight=700)
node("proc", *n_group, ["The validators in the trigger's", "ValidationGroup are selected"], PROC[0], PROC[1])
node("diamond", *n_csdec, ["EnableClientScript", "and JavaScript?"], DEC[0], DEC[1])
node("proc", *n_crun, ["Validators run in the browser"], PROC[0], PROC[1])
node("diamond", *n_cdec, ["all", "valid?"], DEC[0], DEC[1])
node("proc", *n_srun, ["Validators run on the server → Page.IsValid"], PROC[0], PROC[1])
node("diamond", *n_sdec, ["Page.IsValid?"], DEC[0], DEC[1])
node("term", *ok_c, ["the event handler runs its work"], OK[0], OK[1], weight=700)
node("term", *blk_c, ["submit blocked — no round-trip;", "messages + TValidationSummary show"], FAIL[0], FAIL[1])
node("term", *skip_c, ["the handler skips its work;", "messages + TValidationSummary show"], FAIL[0], FAIL[1])

o.append('</svg>')
path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "quickstart", "protected", "pages", "Controls", "validation-flow.svg"))
with open(path, "w") as f:
    f.write("\n".join(o))
print(f"wrote {path}  {W}x{H}")
