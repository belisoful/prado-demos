#!/usr/bin/env python3
"""Generate Fundamentals/objectdiagram.svg — the static object diagram of a page request.

Replaces the legacy objectdiagram.gif, faithful to its structure. The Application owns the
core modules (Request, Response, Session, Error Handler, Asset Manager), its Parameters,
and any Custom Modules. It hands the request to the Page Service, which uses the Theme
Manager and Template Manager to build the Page. The Page is a composition of Controls
(one Parent, many Children). All collaborators verified present in 4.3.3
(TAssetManager, TThemeManager, TTemplateManager, TPageService). Object names are
underlined, following the UML instance convention. Scope: 4.3.3 only.

Usage:
    python3 tools/diagrams/gen_objectdiagram.py

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
STROKE = "#2f2f2f"
CORE = ("#dbe9f6", "#4a78a8")     # Application / Page Service / Page
MODU = ("#e7ddf2", "#7a4fb5")     # core modules
NEUT = ("#eef1f5", "#7a8a9a")     # Parameter / Custom Module
MGR  = ("#d6ecec", "#2f8f8f")     # Theme / Template Manager
CTRL = ("#dcecd6", "#5a8f45")     # Control
LINE = "#6a6a6a"

o = []
def box(x, y, w, h, label, fill, stroke, fs=9.6):
    o.append(f'  <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="4" fill="{fill}" stroke="{stroke}" stroke-width="1.2"/>')
    cx, cy = x + w/2, y + h/2
    o.append(f'  <text x="{cx:.1f}" y="{cy:.1f}" font-size="{fs}" font-weight="600" fill="#1a1a1a" text-anchor="middle" dominant-baseline="central">{esc(label)}</text>')
    tw = text_px(label, fs)
    o.append(f'  <line x1="{cx-tw/2:.1f}" y1="{cy+7:.1f}" x2="{cx+tw/2:.1f}" y2="{cy+7:.1f}" stroke="#1a1a1a" stroke-width="0.7"/>')
    return (x, y, w, h, cx, cy)

def line(x1, y1, x2, y2):
    o.append(f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{LINE}" stroke-width="1.2"/>')

def mult(x, y, s):
    o.append(f'  <text x="{x:.1f}" y="{y:.1f}" font-size="8.6" fill="#444" text-anchor="middle" dominant-baseline="central">{esc(s)}</text>')

def role(x, y, s):
    o.append(f'  <text x="{x:.1f}" y="{y:.1f}" font-size="8.2" fill="#666" font-style="italic" text-anchor="start" dominant-baseline="central">{esc(s)}</text>')

def diamond(x, y, d):
    # filled composition diamond with its near vertex at the whole's box edge (x, y); d=+1 down, -1 up
    o.append(f'  <path d="M{x:.1f},{y:.1f} l5,{6*d:.0f} l-5,{6*d:.0f} l-5,{-6*d:.0f} z" fill="{STROKE}" stroke="{STROKE}" stroke-width="1"/>')

W, H = 514, 212
# --- geometry ---
MB_X, MB_W, MB_H = 12, 98, 26
mod_ys = [16, 48, 80, 112, 144]
mods = ["Request", "Response", "Session", "Error Handler", "Asset Manager"]
APP_X, MID_W = 142, 108
APP_Y, APP_H = 74, 40
APP_CY = APP_Y + APP_H/2
PS_X = 288
PG_X, PG_W = 418, 66
TOP_Y, SM_H = 16, 26
BOT_Y = APP_Y + APP_H + (APP_Y - (TOP_Y + SM_H))   # symmetric top/bottom gap → consistent connectors

o.insert(0, f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}">')
o.append(f'  <rect x="0" y="0" width="{W}" height="{H}" fill="#fff"/>')
# "Services" package container around the Page Service (drawn behind everything else)
sc_x, sc_y, sc_w, sc_h = PS_X - 10, APP_Y - 20, MID_W + 20, APP_H + 30   # taller top: more room under "Services"
o.append(f'  <rect x="{sc_x:.1f}" y="{sc_y:.1f}" width="{sc_w:.1f}" height="{sc_h:.1f}" rx="7" fill="#f4f6f9" stroke="#8a97a8" stroke-width="1.1"/>')
o.append(f'  <text x="{sc_x+7:.1f}" y="{sc_y+9:.1f}" font-size="8.8" font-weight="700" fill="#5a6b7a" dominant-baseline="central">Services</text>')

# core modules (left), fanning into Application's left-centre
appL = (APP_X, APP_CY)
for lbl, yy in zip(mods, mod_ys):
    b = box(MB_X, yy, MB_W, MB_H, lbl, MODU[0], MODU[1])
    line(MB_X + MB_W, yy + MB_H/2, appL[0], appL[1])
# Application
box(APP_X, APP_Y, MID_W, APP_H, "Application", CORE[0], CORE[1], fs=10.2)
# Parameter (top) and Custom Module (bottom), stacked on Application's column
pcx = APP_X + MID_W/2
LG = 6   # every connector label sits this far from its adjacent box
box(APP_X, TOP_Y, MID_W, SM_H, "Parameter", NEUT[0], NEUT[1])
line(pcx, TOP_Y + SM_H, pcx, APP_Y)
diamond(pcx, APP_Y, -1)                      # Application composes its Parameters
mult(pcx - 11, TOP_Y + SM_H + LG, "*"); mult(pcx - 11, APP_Y - LG, "1")
box(APP_X, BOT_Y, MID_W, SM_H, "Custom Module", NEUT[0], NEUT[1])
line(pcx, APP_Y + APP_H, pcx, BOT_Y)
diamond(pcx, APP_Y + APP_H, +1)              # Application composes its Custom Modules
mult(pcx - 11, APP_Y + APP_H + LG, "1"); mult(pcx - 11, BOT_Y - LG, "*")
# Application -> Page Service
line(APP_X + MID_W, APP_CY, PS_X, APP_CY)
# Page Service
box(PS_X, APP_Y, MID_W, APP_H, "Page Service", CORE[0], CORE[1], fs=10.2)
pscx = PS_X + MID_W/2
# Theme Manager (top) / Template Manager (bottom) -> Page Service
box(PS_X, TOP_Y, MID_W, SM_H, "Theme Manager", MGR[0], MGR[1])
line(pscx, TOP_Y + SM_H, pscx, APP_Y)
box(PS_X, BOT_Y, MID_W, SM_H, "Template Manager", MGR[0], MGR[1])
line(pscx, APP_Y + APP_H, pscx, BOT_Y)
# Page Service -> Page
line(PS_X + MID_W, APP_CY, PG_X, APP_CY)
# Page
box(PG_X, APP_Y, PG_W, APP_H, "Page", CORE[0], CORE[1], fs=10.2)
pgcx = PG_X + PG_W/2
# Page composition -> Control (filled diamond at the Page end)
box(PG_X, BOT_Y, PG_W, SM_H, "Control", CTRL[0], CTRL[1])
line(pgcx, APP_Y + APP_H, pgcx, BOT_Y)
dy = APP_Y + APP_H
diamond(pgcx, dy, +1)                        # Page composes its Controls
role(pgcx + 8, dy + LG, "Parent 1")          # same distance from Page ...
role(pgcx + 8, BOT_Y - LG, "Child *")        # ... as Child is from Control

o.append('</svg>')
path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "quickstart", "protected", "pages", "Fundamentals", "objectdiagram.svg"))
with open(path, "w") as f:
    f.write("\n".join(o))
print(f"wrote {path}  {W}x{H}")
