#!/usr/bin/env python3
"""Generate quickstart/protected/pages/Advanced/cron-flow.svg.

A compact run-cycle flow for TCronModule (scoped to 4.2.0+): the operating system's
cron runs `prado-cli cron` every minute (the required external driver); TCronModule then
checks each job's schedule and, for a job that is due, runs the task as its user and logs
the run, otherwise it skips the job.

Usage:
    python3 tools/diagrams/gen_cron_flow.py     # writes the SVG in place

Validate by rendering to pixels (see local/quickstart-doc-update-plan-4.3.3.md 4a) and,
because the quickstart runs Mode="Performance", refresh the published copy with a cp
overwrite of quickstart/assets/<hash>/cron-flow.svg.
Requires: Python 3 standard library only.
"""
import html
import os

def esc(s): return html.escape(s, quote=True)

FS = 9.5
CHW = 5.9
NH = 26
CX = 150
OS_FILL, OS_STROKE = "#eef0f2", "#7a8290"     # external (operating system)
STEP_FILL, STEP_STROKE = "#ffffff", "#2f2f2f"  # PRADO step
DEC_FILL, DEC_STROKE = "#fff3e0", "#c79a3a"    # decision
CONN = "#2f2f2f"
NOTE = "#555"

def w_of(label):
    return max(len(label) * CHW + 26, 62)

out = []

def box(cx, cy, label, fill, stroke, dashed=False, note=None, bold=True):
    w = w_of(label)
    da = ' stroke-dasharray="4 3"' if dashed else ''
    out.append(f'  <rect x="{cx-w/2:.1f}" y="{cy-NH/2:.1f}" width="{w:.1f}" height="{NH}" rx="7" ry="7" '
               f'fill="{fill}" stroke="{stroke}" stroke-width="1.15"{da} filter="url(#ds)"/>')
    fw = ' font-weight="600"' if bold else ''
    out.append(f'  <text x="{cx:.1f}" y="{cy:.1f}" font-size="{FS}" fill="#1a1a1a"{fw} text-anchor="middle" '
               f'dominant-baseline="central">{esc(label)}</text>')
    if note:
        out.append(f'  <text x="{cx+w/2+9:.1f}" y="{cy:.1f}" font-size="8.6" fill="{NOTE}" '
                   f'dominant-baseline="central">{esc(note)}</text>')
    return w

def diamond(cx, cy, label):
    tw = len(label) * CHW
    hw = max(tw / 2 + 20, 52)
    hh = 22
    pts = f'{cx},{cy-hh} {cx+hw:.1f},{cy} {cx},{cy+hh} {cx-hw:.1f},{cy}'
    out.append(f'  <polygon points="{pts}" fill="{DEC_FILL}" stroke="{DEC_STROKE}" stroke-width="1.15" filter="url(#ds)"/>')
    out.append(f'  <text x="{cx:.1f}" y="{cy:.1f}" font-size="{FS}" fill="#7a1f1f" text-anchor="middle" '
               f'dominant-baseline="central">{esc(label)}</text>')
    return hw, hh

def varrow(cy1, cy2, cx=CX):
    out.append(f'  <line x1="{cx}" y1="{cy1:.1f}" x2="{cx}" y2="{cy2:.1f}" stroke="{CONN}" stroke-width="1.3" marker-end="url(#arrow)"/>')

# ---- positions ----
OS_CY, CLI_CY, MOD_CY = 44, 104, 162
DEC_CY = 230
RUN_CY, LOG_CY = 306, 364
SKIP_CX = CX + 150

# ---- canvas ----
W = SKIP_CX + w_of("skip") / 2 + 150
H = LOG_CY + NH / 2 + 18

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

# spine arrows
varrow(OS_CY + NH/2, CLI_CY - NH/2)
varrow(CLI_CY + NH/2, MOD_CY - NH/2)
varrow(MOD_CY + NH/2, DEC_CY - 22)
varrow(DEC_CY + 22, RUN_CY - NH/2)
varrow(RUN_CY + NH/2, LOG_CY - NH/2)

# nodes
box(CX, OS_CY, "system cron", OS_FILL, OS_STROKE, dashed=True, note="your OS, every minute")
box(CX, CLI_CY, "prado-cli cron", STEP_FILL, STEP_STROKE)
box(CX, MOD_CY, "TCronModule", STEP_FILL, STEP_STROKE, note="for each job")
hw, hh = diamond(CX, DEC_CY, "schedule due?")
box(CX, RUN_CY, "run the task", STEP_FILL, STEP_STROKE, note="as its user")
box(CX, LOG_CY, "log the run", STEP_FILL, STEP_STROKE)

# Yes label on the down branch
out.append(f'  <text x="{CX+6:.1f}" y="{(DEC_CY+22+RUN_CY-NH/2)/2:.1f}" font-size="8.8" fill="#2f2f2f">Yes</text>')
# No branch: diamond right -> skip
skip_left = SKIP_CX - w_of("skip") / 2
out.append(f'  <line x1="{CX+hw:.1f}" y1="{DEC_CY}" x2="{skip_left:.1f}" y2="{DEC_CY}" stroke="{CONN}" stroke-width="1.3" marker-end="url(#arrow)"/>')
out.append(f'  <text x="{(CX+hw+skip_left)/2:.1f}" y="{DEC_CY-5:.1f}" font-size="8.8" fill="#2f2f2f" text-anchor="middle">No</text>')
box(SKIP_CX, DEC_CY, "skip", STEP_FILL, STEP_STROKE)

out.append('</svg>')

_out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "quickstart", "protected", "pages", "Advanced", "cron-flow.svg"))
with open(_out, "w") as f:
    f.write("\n".join(out))
print(f"wrote {_out}  {W:.0f}x{H:.0f}")
