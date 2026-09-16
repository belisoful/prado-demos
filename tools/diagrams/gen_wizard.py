#!/usr/bin/env python3
"""Generate Controls/wizard.svg — the region layout of a TWizard.

Replaces the legacy wizard.gif. Faithful to it: the side bar runs down the left, and the
header, step content, and navigation stack on the right, which is the default table
layout TWizard renders. Each region is annotated with the style property that customizes
it (from the page's customization section). Scope: 4.3.3 only.

Usage:
    python3 tools/diagrams/gen_wizard.py

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
def region(o, x, y, w, h, label, prop, fill, stroke):
    o.append(f'  <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="1.3"/>')
    cx, cy = x + w/2, y + h/2
    o.append(f'  <text x="{cx:.1f}" y="{cy-6:.1f}" font-size="12" font-weight="700" fill="#1a1a1a" text-anchor="middle" dominant-baseline="central">{esc(label)}</text>')
    o.append(f'  <text x="{cx:.1f}" y="{cy+9:.1f}" font-size="8.6" fill="#666" font-style="italic" text-anchor="middle" dominant-baseline="central">{esc(prop)}</text>')

# Margins between the dashed "Wizard" box and the regions: 6px sides/bottom, 8px top.
G_SIDE, G_TOP = 6, 8
SVGM = 6                      # margin from the SVG edge to the dashed box
GAP = 6                      # gap between regions
SB_W = 96                    # side bar width
RW = 224                     # right column width
HDR_H, NAV_H, BODY_H = 46, 46, 128
RX, RY = SVGM + G_SIDE, SVGM + 2 + G_TOP     # region block top-left (extra 2 up top for the label)
block_w = SB_W + GAP + RW
block_h = HDR_H + GAP + BODY_H + GAP + NAV_H
right_x = RX + SB_W + GAP
right_w = RW
dbx, dby = RX - G_SIDE, RY - G_TOP           # dashed box top-left
dbw, dbh = block_w + 2 * G_SIDE, block_h + G_TOP + G_SIDE
W = dbx + dbw + SVGM
H = dby + dbh + SVGM

o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}">']
o.append('''  <defs>
    <filter id="ds" x="-25%" y="-30%" width="150%" height="170%">
      <feDropShadow dx="0.6" dy="0.9" stdDeviation="0.7" flood-color="#000" flood-opacity="0.18"/>
    </filter>
  </defs>''')
o.append(f'  <rect x="0" y="0" width="{W}" height="{H}" fill="#fff"/>')
# outer wizard boundary (dashed), labelled "Wizard" on its top edge
o.append(f'  <rect x="{dbx:.1f}" y="{dby:.1f}" width="{dbw:.1f}" height="{dbh:.1f}" rx="9" fill="none" stroke="#b7b7b7" stroke-width="1.2" stroke-dasharray="4 3"/>')
lbl = "Wizard"; lw = text_px(lbl, 11) + 12
o.append(f'  <rect x="{dbx+8:.1f}" y="{dby-6.5:.1f}" width="{lw:.1f}" height="13" fill="#fff"/>')
o.append(f'  <text x="{dbx+8+lw/2:.1f}" y="{dby:.1f}" font-size="11" font-weight="700" fill="#666" text-anchor="middle" dominant-baseline="central">{esc(lbl)}</text>')

# side bar (full height, left)
region(o, RX, RY, SB_W, block_h, "Side Bar", "SideBarStyle", "#dbe9f6", "#4a78a8")
# header (top-right)
region(o, right_x, RY, right_w, HDR_H, "Header", "HeaderStyle", "#f6e6c8", "#b8862a")
# step content (middle-right)
region(o, right_x, RY + HDR_H + GAP, right_w, BODY_H, "Step Content", "StepStyle", "#eef4fb", "#6b8fb0")
# navigation (bottom-right)
region(o, right_x, RY + HDR_H + GAP + BODY_H + GAP, right_w, NAV_H, "Navigation", "NavigationStyle", "#dcecd6", "#5a8f45")

o.append('</svg>')
path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "quickstart", "protected", "pages", "Controls", "wizard.svg"))
with open(path, "w") as f:
    f.write("\n".join(o))
print(f"wrote {path}  {W}x{H}")
