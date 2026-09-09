#!/usr/bin/env python3
"""Generate quickstart/protected/pages/Configurations/parameters-routeback.svg.

Shows the TDbParameterModule capture / route-back (4.2.0): a change to the application
parameters is captured (at TPageService::onPreRunPage) and written to the database table.
The database write is not written back into the application parameters, so a change does
not loop between the two. The one-time load of parameters from the database into the
application happens on init, before the capture is attached (noted in the caption).

Usage:
    python3 tools/diagrams/gen_parameters_routeback.py     # writes the SVG in place

Validate by rendering to pixels (see local/quickstart-doc-update-plan-4.3.3.md 4a) and,
because the quickstart runs Mode="Performance", refresh the published copy with a cp
overwrite of quickstart/assets/<hash>/parameters-routeback.svg.
Requires: Python 3 standard library only.
"""
import html
import os

def esc(s): return html.escape(s, quote=True)

FS = 10
CHW = 6.0
NH = 34
APP_FILL, APP_STROKE = "#d4e3f4", "#3f6fa0"
DB_FILL, DB_STROKE = "#eef4fb", "#3f6fa0"
BLACK = "#2f2f2f"
RED = "#b23b3b"
NOTE = "#555"

def w_of(label):
    return max(len(label) * CHW + 30, 90)

APP_CX, DB_CX, CY = 120, 430, 92
out = []

def box(cx, cy, label, fill, stroke):
    w = w_of(label)
    out.append(f'  <rect x="{cx-w/2:.1f}" y="{cy-NH/2:.1f}" width="{w:.1f}" height="{NH}" rx="8" ry="8" '
               f'fill="{fill}" stroke="{stroke}" stroke-width="1.2" filter="url(#ds)"/>')
    out.append(f'  <text x="{cx:.1f}" y="{cy:.1f}" font-size="{FS}" fill="#1a1a1a" font-weight="600" '
               f'text-anchor="middle" dominant-baseline="central">{esc(label)}</text>')
    return w

appw = w_of("application Parameters")
dbw = w_of("database table")
app_r = APP_CX + appw/2
db_l = DB_CX - dbw/2

W = DB_CX + dbw/2 + 20
H = 200

out.insert(0, f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H}" width="{W:.0f}" height="{H}" '
              f'font-family="Verdana, \'Segoe UI\', -apple-system, sans-serif">')
out.append(f'''  <defs>
    <filter id="ds" x="-20%" y="-30%" width="140%" height="170%">
      <feDropShadow dx="0.6" dy="0.9" stdDeviation="0.7" flood-color="#000" flood-opacity="0.20"/>
    </filter>
    <marker id="arrow" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="{BLACK}"/>
    </marker>
    <marker id="arrowr" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="{RED}"/>
    </marker>
  </defs>''')
out.append(f'  <rect x="0" y="0" width="{W:.0f}" height="{H}" fill="#fff"/>')

# capture arrow: application Parameters -> database (top)
ytop = CY - 10
out.append(f'  <line x1="{app_r:.1f}" y1="{ytop}" x2="{db_l-2:.1f}" y2="{ytop}" stroke="{BLACK}" stroke-width="1.4" marker-end="url(#arrow)"/>')
out.append(f'  <text x="{(app_r+db_l)/2:.1f}" y="{ytop-8:.1f}" font-size="9" fill="{BLACK}" text-anchor="middle">a change is captured and written</text>')
out.append(f'  <text x="{(app_r+db_l)/2:.1f}" y="{ytop-20:.1f}" font-size="8.6" fill="{NOTE}" text-anchor="middle">(at TPageService::onPreRunPage)</text>')

# return arrow (prevented): database -> application Parameters (bottom), dashed red, crossed out
ybot = CY + 10
midx = (app_r + db_l) / 2
out.append(f'  <line x1="{db_l:.1f}" y1="{ybot}" x2="{app_r+2:.1f}" y2="{ybot}" stroke="{RED}" stroke-width="1.3" stroke-dasharray="4 3" marker-end="url(#arrowr)"/>')
# X mark across the return arrow
out.append(f'  <g stroke="{RED}" stroke-width="2">')
out.append(f'    <line x1="{midx-7:.1f}" y1="{ybot-7:.1f}" x2="{midx+7:.1f}" y2="{ybot+7:.1f}"/>')
out.append(f'    <line x1="{midx-7:.1f}" y1="{ybot+7:.1f}" x2="{midx+7:.1f}" y2="{ybot-7:.1f}"/>')
out.append(f'  </g>')
out.append(f'  <text x="{midx:.1f}" y="{ybot+20:.1f}" font-size="9" fill="{RED}" text-anchor="middle">not written back &#8212; no loop</text>')

box(APP_CX, CY, "application Parameters", APP_FILL, APP_STROKE)
box(DB_CX, CY, "database table", DB_FILL, DB_STROKE)

# caption
out.append(f'  <text x="{W/2:.1f}" y="172" font-size="8.8" fill="{NOTE}" text-anchor="middle">On start the module loads the parameters from the database into the application,</text>')
out.append(f'  <text x="{W/2:.1f}" y="184" font-size="8.8" fill="{NOTE}" text-anchor="middle">before the capture is attached.</text>')

out.append('</svg>')

_out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "quickstart", "protected", "pages", "Configurations", "parameters-routeback.svg"))
with open(_out, "w") as f:
    f.write("\n".join(out))
print(f"wrote {_out}  {W:.0f}x{H}")
