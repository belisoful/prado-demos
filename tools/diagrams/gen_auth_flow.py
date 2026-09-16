#!/usr/bin/env python3
"""Generate Advanced/auth-flow.svg — PRADO authentication + authorization request flow.

Verified against 4.3.3:
  - TAuthManager restores the user from the session on Authentication (else guest); on
    Authorization it evaluates the page's rules and redirects to LoginPage on failure.
  - TAuthorizationRuleCollection::isUserAllowed walks rules in order, returns the first
    non-zero decision; none applies -> authorized (default allow).
  - TAuthorizationRule::isUserAllowed returns allow(+1)/deny(-1) iff verb AND ip AND user
    AND role all match (each dimension matches all when unset), else 0.

Decision flowchart with the rule loop. Scope: 4.3.3 only. Python 3 stdlib only.
Usage: python3 tools/diagrams/gen_auth_flow.py
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
STROKE = "#2f2f2f"
PROC = ("#dbe9f6", "#4a78a8")
DEC  = ("#f6e6c8", "#b8862a")
TERM = ("#eef1f5", "#7a8a9a")
OK   = ("#dcecd6", "#5a8f45")
NO   = ("#f3d3d3", "#c05a3a")
LINE = "#4a4a4a"
LH = 12.6

o = []
def rrect(x, y, w, h, fill, stroke, rx=7, sw=1.2, shadow=True):
    sh = ' filter="url(#ds)"' if shadow else ''
    o.append(f'  <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{sh}/>')
def lines_at(cx, cy, lines, fs=9.6, fill="#1a1a1a", weight=None):
    fw = f' font-weight="{weight}"' if weight else ''
    y0 = cy - (len(lines)-1)*LH/2
    for i, ln in enumerate(lines):
        o.append(f'  <text x="{cx:.1f}" y="{y0+i*LH:.1f}" font-size="{fs}"{fw} fill="{fill}" text-anchor="middle" dominant-baseline="central">{esc(ln)}</text>')
def node(kind, cx, cy, w, h, lines, fill, stroke, fs=9.6, weight=None):
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

W, H = 540, 572
CX = 196
BW = 322                    # both blue boxes share the smaller width
n_start = (CX, 26, 140, 28)
n_authn = (CX, 82, BW, 42)
n_authz = (CX, 152, BW, 46)
n_more  = (CX, 226, 120, 54)
n_appl  = (CX, 318, 130, 60)
n_act   = (CX, 410, 132, 56)
ok_c    = (190, 496, 248, 40)         # AUTHORIZED: right edge kept at 314; left edge extended ~12px left
den_c   = (404, 410, 211, 38)         # DENIED, directly off rule action? (wider so the text isn't cramped)
DOWN_X  = 104                         # more? -> AUTHORIZED vertical (equidistant: AUTH-left 78 <-26-> 104 <-26-> steps-left 130)
RG      = 344                         # loop-back gutter (moved right, clear of the "yes" spine label)

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

def top(n): return (n[0], n[1]-n[3]/2)
def bot(n): return (n[0], n[1]+n[3]/2)
def lft(n): return (n[0]-n[2]/2, n[1])
def rgt(n): return (n[0]+n[2]/2, n[1])

# spine
arrow([bot(n_start), top(n_authn)])
arrow([bot(n_authn), top(n_authz)])
arrow([bot(n_authz), top(n_more)])
arrow([bot(n_more), top(n_appl)])
arrow([bot(n_appl), top(n_act)])
arrow([bot(n_act), (CX, ok_c[1]-ok_c[3]/2)])   # allow: straight down the spine
# more? no -> AUTHORIZED (enters from ABOVE at DOWN_X)
arrow([lft(n_more), (DOWN_X, n_more[1]), (DOWN_X, ok_c[1]-ok_c[3]/2)])
# applies? no -> loop back to more? (right gutter)
arrow([rgt(n_appl), (RG, n_appl[1]), (RG, n_more[1]), rgt(n_more)])
# action? deny -> DENIED (directly to the right)
arrow([rgt(n_act), lft(den_c)])

# decision labels, each at its diamond's exit
lbl(CX+11, bot(n_more)[1]+9, "yes", "start")
lbl(CX+11, bot(n_appl)[1]+9, "yes", "start")
lbl(CX+11, bot(n_act)[1]+9, "allow", "start")
lbl((lft(n_more)[0]+DOWN_X)/2, n_more[1]-8, "no")
lbl(rgt(n_appl)[0]+8, n_appl[1]-8, "no · next rule", "start")
lbl((rgt(n_act)[0]+lft(den_c)[0])/2, n_act[1]-9, "deny")

# nodes
node("term", *n_start, ["Page request"], TERM[0], TERM[1], weight=700)
node("proc", *n_authn, ["Authentication — TAuthManager restores the", "user from the session (otherwise a guest)"], PROC[0], PROC[1])
node("proc", *n_authz, ["Authorization — gather the page's rules,", "bottom-up: current folder, then parent folders"], PROC[0], PROC[1])
node("diamond", *n_more, ["more", "rules?"], DEC[0], DEC[1])
node("diamond", *n_appl, ["rule", "applies?"], DEC[0], DEC[1])
node("diamond", *n_act, ["rule", "action?"], DEC[0], DEC[1])
node("term", *ok_c, ["AUTHORIZED — run the page"], OK[0], OK[1], weight=700)
node("term", *den_c, ["DENIED — redirect to LoginPage"], NO[0], NO[1], weight=700)

# caption
cap = 544
o.append(f'  <text x="{W/2:.1f}" y="{cap:.1f}" font-size="8.8" fill="#666" text-anchor="middle" font-style="italic">A rule applies when  verb ∧ ip ∧ user ∧ role  all match (each unset dimension matches all), for a page the rule lists.</text>')
o.append(f'  <text x="{W/2:.1f}" y="{cap+14:.1f}" font-size="8.8" fill="#666" text-anchor="middle" font-style="italic">The first applicable rule decides; if none applies, the user is authorized.</text>')

o.append('</svg>')
path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "quickstart", "protected", "pages", "Advanced", "auth-flow.svg"))
with open(path, "w") as f:
    f.write("\n".join(o))
print(f"wrote {path}  {W}x{H}")
