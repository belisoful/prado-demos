#!/usr/bin/env python3
"""Generate quickstart/protected/pages/Fundamentals/applifecycles.svg.

The PRADO TApplication lifecycle activity diagram, scoped to 4.3.3, as a self-contained
SVG: Application construction, the initApplication stage containing the onConfiguration
and onInitComplete events, the ordered request-step events onBeginRequest..flushOutput,
onEndRequest, and the exception decision (TExitException? -> Yes: onEndRequest /
No: onError -> onEndRequest).

Usage:
    python3 tools/diagrams/gen_applifecycles.py     # writes the SVG in place

After regenerating, validate by rendering to pixels and, because the quickstart runs
Mode="Performance" (the asset manager does not re-check timestamps), refresh the
published copy with a cp overwrite of quickstart/assets/<hash>/applifecycles.svg.
See local/quickstart-doc-update-plan-4.3.3.md 4a for the render/validate recipe.

Scope: keep to features present in 4.3.3; do not add 4.4.0-only nodes or labels.
Requires: Python 3 standard library only.
"""
import html
import os

def esc(s): return html.escape(s, quote=True)

CX = 210
NODE_W = 150
NOTE_X = 300
NOTE_W = 320          # ~67% wider than before
LINE_H = 12.6
NAME_FS = 9.5
DESC_FS = 10
GAP = 21              # ~50% more vertical spacing
WRAP = 58             # chars per note line (fits the wider NOTE_W)
W = 632

STAGE_FILL = "#d4e3f4"      # less neutral (soft blue)
EVENT_FILL = "#ffffff"
ERR_FILL = "#f7d1d1"        # red background at 75% of the prior saturation
ERR_STROKE = "#b23b3b"
ERR_TXT = "#7a1f1f"
RED = "#b23b3b"

def wrap(text, mx=WRAP):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > mx:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur: lines.append(cur)
    return lines

def nheight(text):
    return len(wrap(text)) * LINE_H + 11

def note(out, conn_cy, text, box_cy=None):
    if box_cy is None:
        box_cy = conn_cy
    lines = wrap(text)
    n = len(lines)
    nh = n * LINE_H + 11
    top = box_cy - nh / 2
    fold = 10
    right = NOTE_X + NOTE_W
    # connector: node edge (conn_cy) to note box (box_cy) — diagonal when they differ
    out.append(f'  <line x1="{CX + NODE_W/2:.1f}" y1="{conn_cy:.1f}" x2="{NOTE_X}" y2="{box_cy:.1f}" stroke="#8a8a8a" stroke-width="0.9" stroke-dasharray="2.5 2"/>')
    out.append(f'  <path d="M{NOTE_X},{top:.1f} H{right-fold} L{right},{top+fold:.1f} V{top+nh:.1f} H{NOTE_X} Z" fill="#fffdf3" stroke="#9a9a8f" stroke-width="0.9" filter="url(#ds)"/>')
    out.append(f'  <path d="M{right-fold},{top:.1f} V{top+fold:.1f} H{right}" fill="none" stroke="#9a9a8f" stroke-width="0.9"/>')
    y0 = box_cy - (n - 1) * LINE_H / 2
    for j, ln in enumerate(lines):
        out.append(f'  <text x="{NOTE_X+8}" y="{y0 + j*LINE_H:.1f}" font-size="{DESC_FS}" fill="#333" dominant-baseline="central">{esc(ln)}</text>')
    return nh

CONSTR_TXT = "Register the application singleton. Set the base, runtime, and configuration paths."
ONCONF_TXT = "The configuration is fully applied and the modules are loaded. No service has started. Register additional services here."
ONINIT_TXT = "The requested service is loaded and initialized. The request is about to begin."
ONEND_TXT = "The request is processed. Modules do end-of-request work such as logging."

def stadium(out, cx, cy, w, h, name, fill, fs=NAME_FS, sw=1.15, stroke="#2f2f2f", txt="#1a1a1a", bold=False):
    out.append(f'  <rect x="{cx-w/2:.1f}" y="{cy-h/2:.1f}" width="{w}" height="{h}" rx="{h/2:.1f}" ry="{h/2:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" filter="url(#ds)"/>')
    fw = ' font-weight="600"' if bold else ''
    out.append(f'  <text x="{cx}" y="{cy:.1f}" font-size="{fs}" fill="{txt}"{fw} text-anchor="middle" dominant-baseline="central">{esc(name)}</text>')

# ---- content ----
STEPS = [
    ("onBeginRequest", "The application starts to process the user request."),
    ("onLoadState", "Load the application state from persistent storage under the runtime directory."),
    ("onLoadStateComplete", "The application state is restored."),
    ("onAuthentication", "Determine the request user's identity. The user becomes a guest or a registered user."),
    ("onAuthenticationComplete", "User authentication is complete."),
    ("onAuthorization", "Determine whether the user may access the requested resource."),
    ("onAuthorizationComplete", "Authorization is complete."),
    ("onPreRunService", "Prepare to run the requested service."),
    ("runService", "The requested service runs and produces the response."),
    ("onSaveState", "Save the application state to persistent storage under the runtime directory."),
    ("onSaveStateComplete", "The application state is stored."),
    ("onPreFlushOutput", "Prepare to flush the buffered output."),
    ("flushOutput", "Flush the buffered output to the client."),
]

# ---- geometry ----
START_CY = 70.0      # leave a top band for the Legend box
cur = 90.0
CONSTR_H = 26; constr_cy = cur + CONSTR_H/2; cur += CONSTR_H + GAP
HEAD_H = 20; SUBH = 22; SUB_GAP = 16; PAD_B = 9
cont_top = cur
cont_h = HEAD_H + 4 + 2*SUBH + SUB_GAP + PAD_B
head_cy = cont_top + HEAD_H/2 + 1
sub1_cy = cont_top + HEAD_H + 4 + SUBH/2
sub2_cy = sub1_cy + SUBH + SUB_GAP
cur = cont_top + cont_h + GAP
EVH = 24
step_cy = []
for _ in STEPS:
    step_cy.append(cur + EVH/2); cur += EVH + GAP
EXC_GAP = 60            # room before onEndRequest for the exception decision (left)
cur += EXC_GAP
end_node_cy = cur + EVH/2; cur += EVH + GAP
END_CY = cur + 10
# exception-decision geometry (left gutter); onError aligned with onEndRequest
DIA_CX = 58; DIA_HW = 48; DIA_HH = 20
DIA_CY = end_node_cy - 54
ERR_CX = 58; ERR_W = 88; ERR_H = 24
err_cy = end_node_cy
EX = DIA_CX
H = END_CY + 24

# minimum vertical gap between any two immediately-adjacent request-step notes
_seq_h = [nheight(d) for (_, d) in STEPS] + [nheight(ONEND_TXT)]
MIN_GAP = min((EVH + GAP) - (_seq_h[i]/2 + _seq_h[i+1]/2) for i in range(len(_seq_h) - 1))
# reposition the two initApplication inner notes: onConfiguration up under the
# construction note (with room to spare), onInitComplete below it at MIN_GAP
_constr_bot = constr_cy + nheight(CONSTR_TXT) / 2
_onconf_h = nheight(ONCONF_TXT); _oninit_h = nheight(ONINIT_TXT)
ONCONF_CY = _constr_bot + (MIN_GAP + 6) + _onconf_h / 2
ONINIT_CY = ONCONF_CY + _onconf_h / 2 + MIN_GAP + _oninit_h / 2

# ---- draw ----
out = []
out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H:.0f}" width="{W}" height="{H:.0f}" font-family="Verdana, \'Segoe UI\', -apple-system, sans-serif">')
out.append(f'''  <defs>
    <filter id="ds" x="-25%" y="-30%" width="150%" height="170%">
      <feDropShadow dx="0.7" dy="1.0" stdDeviation="0.8" flood-color="#000" flood-opacity="0.22"/>
    </filter>
    <marker id="arrow" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#2f2f2f"/>
    </marker>
    <marker id="arrowr" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="{RED}"/>
    </marker>
  </defs>''')
out.append(f'  <rect x="0" y="0" width="{W}" height="{H:.0f}" fill="#fff"/>')

# Legend box (top, aligned with the note column)
LGW = NOTE_W; LGX = NOTE_X; LGY = 10; LGH = 58
out.append(f'  <rect x="{LGX}" y="{LGY}" width="{LGW}" height="{LGH}" rx="6" fill="#fbfbf7" stroke="#8a8a8a" stroke-width="1" filter="url(#ds)"/>')
out.append(f'  <text x="{LGX+11}" y="{LGY+14:.0f}" font-size="10.5" font-weight="600" fill="#333">Legend</text>')
out.append(f'  <g font-size="9.2" fill="#333">')
_c1 = LGX + 13; _c2 = LGX + 168; _r1 = LGY + 31; _r2 = LGY + 48
# row 1: stage | exception path
out.append(f'    <rect x="{_c1}" y="{_r1-5}" width="17" height="10" rx="5" fill="{STAGE_FILL}" stroke="#2f2f2f" stroke-width="0.9"/>')
out.append(f'    <text x="{_c1+24}" y="{_r1:.0f}" dominant-baseline="central">stage</text>')
out.append(f'    <line x1="{_c2}" y1="{_r1:.0f}" x2="{_c2+17}" y2="{_r1:.0f}" stroke="{RED}" stroke-width="1.3" marker-end="url(#arrowr)"/>')
out.append(f'    <text x="{_c2+24}" y="{_r1:.0f}" fill="{RED}" dominant-baseline="central">exception path</text>')
# row 2: event | onError
out.append(f'    <rect x="{_c1}" y="{_r2-5}" width="17" height="10" rx="5" fill="#fff" stroke="#2f2f2f" stroke-width="0.9"/>')
out.append(f'    <text x="{_c1+24}" y="{_r2:.0f}" dominant-baseline="central">event</text>')
out.append(f'    <rect x="{_c2}" y="{_r2-5}" width="17" height="10" rx="5" fill="{ERR_FILL}" stroke="{ERR_STROKE}" stroke-width="0.9"/>')
out.append(f'    <text x="{_c2+24}" y="{_r2:.0f}" dominant-baseline="central">onError</text>')
out.append(f'  </g>')

def sarrow(y1, y2, x=CX):
    out.append(f'  <line x1="{x}" y1="{y1:.1f}" x2="{x}" y2="{y2:.1f}" stroke="#2f2f2f" stroke-width="1.3" marker-end="url(#arrow)"/>')

out.append(f'  <circle cx="{CX}" cy="{START_CY}" r="8" fill="#222"/>')
sarrow(START_CY + 8, constr_cy - CONSTR_H/2)
sarrow(constr_cy + CONSTR_H/2, cont_top)
sarrow(cont_top + cont_h, step_cy[0] - EVH/2)
for i in range(len(step_cy) - 1):
    sarrow(step_cy[i] + EVH/2, step_cy[i+1] - EVH/2)
sarrow(step_cy[-1] + EVH/2, end_node_cy - EVH/2)
sarrow(end_node_cy + EVH/2, END_CY - 8.5)
out.append(f'  <circle cx="{CX}" cy="{END_CY:.1f}" r="8.5" fill="none" stroke="#222" stroke-width="1.6"/>')
out.append(f'  <circle cx="{CX}" cy="{END_CY:.1f}" r="4.3" fill="#222"/>')

# exception path: any step -> "TExitException?" decision -> Yes: onEndRequest / No: onError -> onEndRequest
top_step = step_cy[0]; bot_step = step_cy[-1]
dia_top = DIA_CY - DIA_HH
left_x = CX - NODE_W/2
# rail: bracket over the steps, then down into the decision diamond
out.append(f'  <g stroke="{RED}" stroke-width="1.1" fill="none" stroke-dasharray="3 2.5">')
out.append(f'    <path d="M{left_x:.0f},{top_step:.1f} H{EX}"/>')
out.append(f'    <path d="M{left_x:.0f},{bot_step:.1f} H{EX}"/>')
out.append(f'    <path d="M{EX},{top_step:.1f} V{dia_top-1:.1f}"/>')
out.append(f'  </g>')
out.append(f'  <path d="M{EX},{dia_top-7:.1f} V{dia_top:.1f}" stroke="{RED}" stroke-width="1.2" marker-end="url(#arrowr)" fill="none"/>')
lbl_y = (top_step + bot_step) / 2
out.append(f'  <text transform="translate({EX-9:.1f},{lbl_y:.1f}) rotate(-90)" font-size="9" fill="{RED}" text-anchor="middle">on exception (any step)</text>')
# decision diamond
dpts = f'{DIA_CX},{DIA_CY-DIA_HH:.1f} {DIA_CX+DIA_HW},{DIA_CY:.1f} {DIA_CX},{DIA_CY+DIA_HH:.1f} {DIA_CX-DIA_HW},{DIA_CY:.1f}'
out.append(f'  <polygon points="{dpts}" fill="#fff3e0" stroke="{RED}" stroke-width="1.2" filter="url(#ds)"/>')
out.append(f'  <text x="{DIA_CX}" y="{DIA_CY:.1f}" font-size="8.4" fill="{ERR_TXT}" text-anchor="middle" dominant-baseline="central">TExitException?</text>')
# No branch: diamond bottom -> onError
out.append(f'  <path d="M{DIA_CX},{DIA_CY+DIA_HH:.1f} V{err_cy-ERR_H/2:.1f}" stroke="{RED}" stroke-width="1.2" marker-end="url(#arrowr)" fill="none"/>')
out.append(f'  <text x="{DIA_CX+5:.1f}" y="{(DIA_CY+DIA_HH+err_cy-ERR_H/2)/2:.1f}" font-size="8.6" fill="{RED}">No</text>')
stadium(out, ERR_CX, err_cy, ERR_W, ERR_H, "onError", ERR_FILL, fs=9.5, sw=1.3, stroke=ERR_STROKE, txt=ERR_TXT, bold=True)
# onError -> onEndRequest (horizontal, aligned)
out.append(f'  <path d="M{ERR_CX+ERR_W/2:.1f},{err_cy:.1f} H{left_x:.1f}" fill="none" stroke="{RED}" stroke-width="1.3" marker-end="url(#arrowr)"/>')
# Yes branch: straight line from the diamond's right point to onEndRequest
out.append(f'  <path d="M{DIA_CX+DIA_HW:.1f},{DIA_CY:.1f} L{left_x:.1f},{end_node_cy-6:.1f}" fill="none" stroke="{RED}" stroke-width="1.3" marker-end="url(#arrowr)"/>')
out.append(f'  <text x="{DIA_CX+DIA_HW+14:.1f}" y="{DIA_CY:.1f}" font-size="8.6" fill="{RED}" text-anchor="middle" dominant-baseline="central">Yes</text>')

# construction stage
stadium(out, CX, constr_cy, NODE_W, CONSTR_H, "Application construction", STAGE_FILL)
note(out, constr_cy, CONSTR_TXT)

# initApplication container
out.append(f'  <rect x="{CX-NODE_W/2:.1f}" y="{cont_top:.1f}" width="{NODE_W}" height="{cont_h:.1f}" rx="10" ry="10" fill="{STAGE_FILL}" stroke="#2f2f2f" stroke-width="1.2" filter="url(#ds)"/>')
out.append(f'  <text x="{CX}" y="{head_cy:.1f}" font-size="10" font-weight="600" fill="#1a1a1a" text-anchor="middle" dominant-baseline="central">initApplication</text>')
out.append(f'  <line x1="{CX-NODE_W/2+6:.1f}" y1="{cont_top+HEAD_H:.1f}" x2="{CX+NODE_W/2-6:.1f}" y2="{cont_top+HEAD_H:.1f}" stroke="#a9b7c9" stroke-width="0.8"/>')
SUBW = 120
stadium(out, CX, sub1_cy, SUBW, SUBH, "onConfiguration", "#fff", fs=9)
stadium(out, CX, sub2_cy, SUBW, SUBH, "onInitComplete", "#fff", fs=9)
out.append(f'  <line x1="{CX}" y1="{cont_top+HEAD_H+1:.1f}" x2="{CX}" y2="{sub1_cy-SUBH/2:.1f}" stroke="#5a6472" stroke-width="1" marker-end="url(#arrow)"/>')
out.append(f'  <line x1="{CX}" y1="{sub1_cy+SUBH/2:.1f}" x2="{CX}" y2="{sub2_cy-SUBH/2:.1f}" stroke="#5a6472" stroke-width="1" marker-end="url(#arrow)"/>')
note(out, sub1_cy, ONCONF_TXT, box_cy=ONCONF_CY)
note(out, sub2_cy, ONINIT_TXT, box_cy=ONINIT_CY)

# request steps
for (name, desc), cy in zip(STEPS, step_cy):
    stadium(out, CX, cy, NODE_W, EVH, name, EVENT_FILL)
    note(out, cy, desc)

# onEndRequest
stadium(out, CX, end_node_cy, NODE_W, EVH, "onEndRequest", EVENT_FILL)
note(out, end_node_cy, ONEND_TXT)

out.append('</svg>')
_out_path = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "quickstart", "protected", "pages", "Fundamentals", "applifecycles.svg"))
with open(_out_path, "w") as _f:
    _f.write("\n".join(out))
print(f"wrote {_out_path}  {W}x{H:.0f}")
