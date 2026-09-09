#!/usr/bin/env python3
"""Generate quickstart/protected/pages/Advanced/cron-runtime.svg.

The TDbCronManager runtime-task pattern (@since 4.3.3): a web request adds a runtime
task with addTask($task, true). The task is persisted in the database cron table and
queued for onEndRequest. If the request completes, the task runs at onEndRequest (for
example, sending a queued email right after the response). If it does not complete, the
next system cron runs the persisted task as a backup.

Usage:
    python3 tools/diagrams/gen_cron_runtime.py     # writes the SVG in place

Validate by rendering to pixels (see local/quickstart-doc-update-plan-4.3.3.md 4a) and,
because the quickstart runs Mode="Performance", refresh the published copy with a cp
overwrite of quickstart/assets/<hash>/cron-runtime.svg.
Requires: Python 3 standard library only.
"""
import html
import os

def esc(s): return html.escape(s, quote=True)

FS = 9.5
CHW = 5.9
NH = 26
CX = 176
STEP_FILL, STEP_STROKE = "#ffffff", "#2f2f2f"
DB_FILL, DB_STROKE = "#eef4fb", "#3f6fa0"
DEC_FILL, DEC_STROKE = "#fff3e0", "#c79a3a"
CONN = "#2f2f2f"
NOTE = "#555"

def w_of(label):
    return max(len(label) * CHW + 26, 62)

out = []

def box(cx, cy, label, fill, stroke, note=None):
    w = w_of(label)
    out.append(f'  <rect x="{cx-w/2:.1f}" y="{cy-NH/2:.1f}" width="{w:.1f}" height="{NH}" rx="7" ry="7" '
               f'fill="{fill}" stroke="{stroke}" stroke-width="1.15" filter="url(#ds)"/>')
    out.append(f'  <text x="{cx:.1f}" y="{cy:.1f}" font-size="{FS}" fill="#1a1a1a" font-weight="600" text-anchor="middle" '
               f'dominant-baseline="central">{esc(label)}</text>')
    if note:
        out.append(f'  <text x="{cx+w/2+9:.1f}" y="{cy:.1f}" font-size="8.6" fill="{NOTE}" '
                   f'dominant-baseline="central">{esc(note)}</text>')
    return w

def diamond(cx, cy, label):
    hw = max(len(label) * CHW / 2 + 20, 52)
    hh = 22
    out.append(f'  <polygon points="{cx},{cy-hh} {cx+hw:.1f},{cy} {cx},{cy+hh} {cx-hw:.1f},{cy}" '
               f'fill="{DEC_FILL}" stroke="{DEC_STROKE}" stroke-width="1.15" filter="url(#ds)"/>')
    out.append(f'  <text x="{cx:.1f}" y="{cy:.1f}" font-size="{FS}" fill="#7a1f1f" text-anchor="middle" '
               f'dominant-baseline="central">{esc(label)}</text>')
    return hw, hh

def varrow(cy1, cy2, cx=CX):
    out.append(f'  <line x1="{cx}" y1="{cy1:.1f}" x2="{cx}" y2="{cy2:.1f}" stroke="{CONN}" stroke-width="1.3" marker-end="url(#arrow)"/>')

ADD_CY, DB_CY, DEC_CY, YES_CY = 44, 112, 186, 268
NO_CX = CX + 168

W = NO_CX + w_of("run at the next cron") / 2 + 96
H = YES_CY + NH / 2 + 18

out.insert(0, f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" width="{W:.0f}" height="{H:.0f}" '
              f'font-family="Verdana, \'Segoe UI\', -apple-system, sans-serif">')
out.append('''  <defs>
    <filter id="ds" x="-25%" y="-30%" width="150%" height="170%">
      <feDropShadow dx="0.6" dy="0.9" stdDeviation="0.7" flood-color="#000" flood-opacity="0.20"/>
    </filter>
    <marker id="arrow" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#2f2f2f"/>
    </marker>
  </defs>''')
out.append(f'  <rect x="0" y="0" width="{W:.0f}" height="{H:.0f}" fill="#fff"/>')

varrow(ADD_CY + NH/2, DB_CY - NH/2)
varrow(DB_CY + NH/2, DEC_CY - 22)
varrow(DEC_CY + 22, YES_CY - NH/2)

box(CX, ADD_CY, "add a runtime task", STEP_FILL, STEP_STROKE, note="a web request: addTask($task, true)")
box(CX, DB_CY, "persist in the cron table", DB_FILL, DB_STROKE)
hw, hh = diamond(CX, DEC_CY, "request completes?")
box(CX, YES_CY, "run at onEndRequest", STEP_FILL, STEP_STROKE, note="sends the email now")

out.append(f'  <text x="{CX+6:.1f}" y="{(DEC_CY+22+YES_CY-NH/2)/2:.1f}" font-size="8.8" fill="#2f2f2f">Yes</text>')
no_left = NO_CX - w_of("run at the next cron") / 2
out.append(f'  <line x1="{CX+hw:.1f}" y1="{DEC_CY}" x2="{no_left:.1f}" y2="{DEC_CY}" stroke="{CONN}" stroke-width="1.3" marker-end="url(#arrow)"/>')
out.append(f'  <text x="{(CX+hw+no_left)/2:.1f}" y="{DEC_CY-5:.1f}" font-size="8.8" fill="#2f2f2f" text-anchor="middle">No</text>')
box(NO_CX, DEC_CY, "run at the next cron", STEP_FILL, STEP_STROKE, note="the backup")

out.append('</svg>')

_out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "quickstart", "protected", "pages", "Advanced", "cron-runtime.svg"))
with open(_out, "w") as f:
    f.write("\n".join(out))
print(f"wrote {_out}  {W:.0f}x{H:.0f}")
