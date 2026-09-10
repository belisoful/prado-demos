#!/usr/bin/env python3
"""Generate quickstart/protected/pages/Fundamentals/page-lifecycle.svg.

The PRADO page lifecycle as a self-contained SVG, replacing the legacy Visio/GIF
statechart (lifecycles.gif) and enriching it while staying faithful to the original:

  - The step sequence is taken verbatim from TPage::run() and its three request paths
    (4.3.3): processNormalRequest(), processPostBackRequest(), processCallbackRequest().
  - onPreRunPage is added at the top: the TPageService event (since 4.2.0) raised just
    before the page runs, where modules attach handlers to reach each page and request.
  - Steps that run only for postback/callback requests are grouped in red dashed boxes,
    as in the original statechart. A normal (first/GET) request skips those boxes.
  - The two steps that differ between postback and callback (the event step and the
    render step) carry both names, with the difference explained in the note.
  - Green nodes are lifecycle events raised on every control in the hierarchy.
  - Every note box is sized to its own text with equal padding on all sides, using an
    embedded Verdana advance-width table (so line wrapping and box sizing are exact,
    with no runtime font dependency). The legend is two columns, centered above.

Usage:
    python3 tools/diagrams/gen_page_lifecycle.py    # writes the SVG in place

Validate by rendering to pixels; refresh the Performance-mode published copy with a cp
overwrite of quickstart/assets/<hash>/page-lifecycle.svg. Scope: 4.3.3 only.
Requires: Python 3 standard library only.
"""
import html
import os

def esc(s): return html.escape(s, quote=True)

# Verdana advance widths per 1000 em (ASCII 32..126), measured from Verdana.ttf.
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

LEFT = 20                  # left margin (doubled)
NODE_W = 218               # ~8% wider so the two dual-label nodes fit
NODE_H = 26
RBOX_PAD = 16              # red box left/right margin around the bubbles
BOT_PAD = {"A": 15, "B": 25}   # per-box bottom margin
ARROW_ROOM = 14            # top arrow room below the label, above the first bubble
RTOP = RBOX_PAD + ARROW_ROOM   # red box top extent above the first bubble (30)
BOX_EDGE_GAP = {"A": 19, "B": 21}   # per-box gap from the previous node's bottom to the box top line
END_GAP = 16               # dot-center to node-edge distance, top and bottom (mirrored)
END_R = 6.5                # end-ball outer radius
TOP_R = 6                  # start-ball radius
CX = LEFT + RBOX_PAD + NODE_W / 2     # red box left edge lands at x = LEFT
# Note left edge sits RBOX_PAD from the red box's right edge, matching the RBOX_PAD gap
# between the step's right edge and the red box's right edge (symmetric spacing).
NOTE_X = CX + NODE_W / 2 + 2 * RBOX_PAD
NAME_FS = 9.6
DESC_FS = 9.8
LINE_H = 12.6
PAD = 8                    # uniform inner padding of note boxes, all sides
TARGET_COL = 372           # target text-column width (px) for wrapping long notes
GAP = 16                   # vertical distance between steps

HOOK_FILL, HOOK_STROKE = "#f4e2b0", "#a9862f"
HIER_FILL = "#c6e6c6"
PATH_FILL = "#f3d3d3"   # inner postback bubbles: more reddish than the red box
PAGE_FILL = "#ffffff"
STROKE = "#2f2f2f"
REDBOX = "#8f2a2a"
REDFILL = "#fbeeee"

def wrap_px(text, col=TARGET_COL, fs=DESC_FS):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if cur and text_px(trial, fs) > col:
            lines.append(cur); cur = w
        else:
            cur = trial
    if cur: lines.append(cur)
    return lines

# (name, category, note, group)   category: hook|hier|page|path ; group: None|"A"|"B"
STEPS = [
    ("onPreRunPage", "hook",
     "TPageService raises this just before the page runs, after the page is created and its initial properties are set. A module attaches a handler here to reach the page and its request as each page is created and processed. A critical extension point. (since 4.2.0)", None),
    ("onPreInit", "page",
     "Page construction has initialized the page properties from the page configuration. The page hierarchy is not available yet. Usage: set personalized themes (Theme, StyleSheetTheme).", None),
    ("onInit", "hier",
     "initRecursive() creates the child controls and establishes the page hierarchy. onInit is raised on every control. Usage: create dynamic controls.", None),
    ("onInitComplete", "page",
     "The page hierarchy is ready. Usage: create dynamic controls.", None),
    ("loadPageState", "path",
     "Restore the view state and the control state of the page hierarchy.", "A"),
    ("processPostData", "path",
     "Controls load their post data. loadPostData() is invoked for controls that implement IPostBackDataHandler.", "A"),
    ("onPreLoad", "page",
     "The post data is loaded and the page state is restored. Usage: create dynamic controls.", None),
    ("onLoad", "hier",
     "loadRecursive() runs the main request handling. onLoad is raised on every control. Usage: perform work that needs the post data and the restored state.", None),
    ("processPostData", "path",
     "Dynamically created controls load their post data. loadPostData() is invoked for controls that implement IPostBackDataHandler.", "B"),
    ("raiseChangedEvents", "path",
     "Controls raise their data-changed events. raisePostDataChangedEvent() is invoked for controls that implement IPostBackDataHandler and whose data changed due to the postback.", "B"),
    ("raisePostBackEvent / processCallbackEvent", "path",
     "The control responsible for the request raises its event. A postback raises the postback event (raisePostBackEvent, such as a button click, on a control that implements IPostBackEventHandler). A callback runs the callback event through the control's adapter instead (processCallbackEvent).", "B"),
    ("onLoadComplete", "page",
     "The post data is completely processed.", None),
    ("onPreRender", "hier",
     "preRenderRecursive() does the final preparation for rendering. onPreRender is raised on every control. Usage: register postback controls and validation controls.", None),
    ("onPreRenderComplete", "page",
     "Preparation for rendering is complete.", None),
    ("onSaveState", "hier",
     "savePageState() saves the view state and the control state of the page hierarchy.", None),
    ("onSaveStateComplete", "page",
     "The page state is saved.", None),
    ("renderControl / renderCallbackResponse", "hier",
     "The page hierarchy is rendered. renderControl() is invoked recursively on the controls. A callback renders only a partial response instead (renderCallbackResponse).", None),
    ("onUnload", "hier",
     "Unload the page and its hierarchy. onUnload is raised on every control. Usage: disconnect the database connection.", None),
]

FILL = {"hook": HOOK_FILL, "hier": PAGE_FILL, "page": HIER_FILL, "path": PATH_FILL}
NST = {"hook": HOOK_STROKE}

# All note boxes share one width so their right edges align. Text wraps at the same
# 8px right padding as the other sides. The box's right edge sits LEFT px from the
# canvas right edge, mirroring the left margin of the diagram elements.
NOTE_BOX_W = TARGET_COL + 2 * PAD
wrapped = [wrap_px(nt) for (_, _, nt, _) in STEPS]
def box_h(lines):
    return (len(lines) - 1) * LINE_H + DESC_FS + 2 * PAD + 5   # minimal height + padding
boxw = [NOTE_BOX_W] * len(STEPS)
boxh = [box_h(w) for w in wrapped]
W = int(NOTE_X + NOTE_BOX_W + LEFT)

# --- legend (2 columns, centered above) ---
LGW = 350
LGX = (W - LGW) / 2
LGY = 12
LG_TITLE = LGY + 17
LG_R1 = LGY + 38
LG_R2 = LG_R1 + 17
LG_SUB = LG_R2 + 19
LGH = (LG_SUB - LGY) + 12
LG_BOTTOM = LGY + LGH

# --- node geometry (below legend) ---
# Entering or leaving a red-box group adds RBOX_PAD so the box's top/bottom margins
# clear the neighbouring steps and their arrowheads.
grp = [s[3] for s in STEPS]
TOP_DOT = LG_BOTTOM + 26
# Steps stay put; the black dot (and the line's start point) is nudged up 6px, which
# just lengthens the connecting line.
FIRST_CY = TOP_DOT + END_GAP + NODE_H / 2
DOT_CY = TOP_DOT - 11
cy = []
prev_bottom = FIRST_CY - NODE_H / 2
prev_cy = FIRST_CY
for i in range(len(STEPS)):
    half = max(NODE_H, boxh[i]) / 2
    if i == 0:
        c = FIRST_CY
    elif grp[i] is not None and grp[i] != grp[i-1]:
        # entering a red box: its top line sits BOX_EDGE_GAP below the previous node.
        # (leaving a box just uses the normal gap, which lands the box bottom the same
        # small distance from the next node and gives a normal note-to-note gap.)
        c = max(prev_cy + BOX_EDGE_GAP[grp[i]] + NODE_H + RTOP, prev_bottom + GAP + half)
    else:
        c = prev_bottom + GAP + half
    cy.append(c)
    prev_cy = c
    prev_bottom = c + half
H = prev_bottom + 46

out = []
out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H:.0f}" width="{W}" height="{H:.0f}" font-family="Verdana, \'Segoe UI\', -apple-system, sans-serif">')
out.append(f'''  <defs>
    <filter id="ds" x="-25%" y="-30%" width="150%" height="170%">
      <feDropShadow dx="0.7" dy="1.0" stdDeviation="0.8" flood-color="#000" flood-opacity="0.22"/>
    </filter>
    <marker id="arrow" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="{STROKE}"/>
    </marker>
  </defs>''')
out.append(f'  <rect x="0" y="0" width="{W}" height="{H:.0f}" fill="#fff"/>')

# legend
out.append(f'  <rect x="{LGX:.1f}" y="{LGY}" width="{LGW}" height="{LGH:.0f}" rx="6" fill="#fbfbf7" stroke="#8a8a8a" stroke-width="1" filter="url(#ds)"/>')
out.append(f'  <text x="{LGX + LGW/2:.1f}" y="{LG_TITLE}" font-size="10.5" font-weight="600" fill="#333" text-anchor="middle">Legend</text>')
col1 = LGX + 20; col2 = LGX + LGW/2 + 8
def leg_item(x, y, lab, fl, sk, dash=False):
    da = ' stroke-dasharray="4 2.5"' if dash else ''
    out.append(f'  <rect x="{x:.1f}" y="{y-5:.1f}" width="17" height="10" rx="5" fill="{fl}" stroke="{sk}" stroke-width="0.9"{da}/>')
    out.append(f'  <text x="{x+23:.1f}" y="{y:.1f}" font-size="8.9" fill="#333" dominant-baseline="central">{esc(lab)}</text>')
leg_item(col1, LG_R1, "onPreRunPage hook", HOOK_FILL, HOOK_STROKE)
leg_item(col2, LG_R1, "raised on all controls", PAGE_FILL, STROKE)
leg_item(col1, LG_R2, "page event", HIER_FILL, STROKE)
leg_item(col2, LG_R2, "postback & callback only", PATH_FILL, REDBOX, dash=True)
out.append(f'  <text x="{LGX + LGW/2:.1f}" y="{LG_SUB:.1f}" font-size="8.6" fill="#666" text-anchor="middle" font-style="italic">A normal (first) request skips the red boxes.</text>')

# red dashed boxes (behind nodes); labels drawn later, over the arrows
def group_span(gid):
    # size to the node column (not the notes), so the box wraps the bubbles
    idx = [i for i, s in enumerate(STEPS) if s[3] == gid]
    top = cy[idx[0]] - NODE_H/2
    bot = cy[idx[-1]] + NODE_H/2
    return top, bot
_redlabels = []
for gid in ("A", "B"):
    top, bot = group_span(gid)
    # top/bottom margins equal the left/right margin (RBOX_PAD) around the nodes
    bx = CX - NODE_W/2 - RBOX_PAD; bw = NODE_W + 2*RBOX_PAD
    by = top - RTOP; bh = (bot - top) + RTOP + BOT_PAD[gid]   # top: arrow room; bottom: per-box
    out.append(f'  <rect x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="9" fill="{REDFILL}" stroke="{REDBOX}" stroke-width="1.3" stroke-dasharray="6 4"/>')
    _redlabels.append((bx + 9, by + 12))

# start dot
out.append(f'  <circle cx="{CX:.1f}" cy="{DOT_CY}" r="{TOP_R}" fill="{STROKE}"/>')
out.append(f'  <line x1="{CX:.1f}" y1="{DOT_CY+TOP_R:.1f}" x2="{CX:.1f}" y2="{cy[0]-NODE_H/2-1:.1f}" stroke="{STROKE}" stroke-width="1.4" marker-end="url(#arrow)"/>')
# connectors
for i in range(len(STEPS)-1):
    out.append(f'  <line x1="{CX:.1f}" y1="{cy[i]+NODE_H/2:.1f}" x2="{CX:.1f}" y2="{cy[i+1]-NODE_H/2-1:.1f}" stroke="{STROKE}" stroke-width="1.4" marker-end="url(#arrow)"/>')
# red-box labels on top of connectors, with a small backing
for lxp, lyp in _redlabels:
    txt = "only for postback & callback requests"
    out.append(f'  <rect x="{lxp-2:.1f}" y="{lyp-8:.1f}" width="{text_px(txt,9)+4:.0f}" height="12" fill="{REDFILL}"/>')
    out.append(f'  <text x="{lxp:.1f}" y="{lyp:.1f}" font-size="9" fill="{REDBOX}" font-style="italic">only for postback &amp; callback requests</text>')

# note card
def note(box_cy, lines, bw, bh):
    n = len(lines); top = box_cy - bh/2; fold = 10; right = NOTE_X + bw
    out.append(f'  <line x1="{CX + NODE_W/2:.1f}" y1="{box_cy:.1f}" x2="{NOTE_X:.1f}" y2="{box_cy:.1f}" stroke="#8a8a8a" stroke-width="0.9" stroke-dasharray="2.5 2"/>')
    out.append(f'  <path d="M{NOTE_X:.1f},{top:.1f} H{right-fold:.1f} L{right:.1f},{top+fold:.1f} V{top+bh:.1f} H{NOTE_X:.1f} Z" fill="#fffdf3" stroke="#9a9a8f" stroke-width="0.9" filter="url(#ds)"/>')
    out.append(f'  <path d="M{right-fold:.1f},{top:.1f} V{top+fold:.1f} H{right:.1f}" fill="none" stroke="#9a9a8f" stroke-width="0.9"/>')
    y0 = box_cy - (n-1)*LINE_H/2
    for j, ln in enumerate(lines):
        out.append(f'  <text x="{NOTE_X+PAD:.1f}" y="{y0 + j*LINE_H:.1f}" font-size="{DESC_FS}" fill="#333" dominant-baseline="central">{esc(ln)}</text>')

# nodes + notes
for i, (name, cat, nt, grp) in enumerate(STEPS):
    c = cy[i]; fill = FILL[cat]; st = NST.get(cat, STROKE)
    sw = 1.5 if cat == "hook" else 1.15
    fs = NAME_FS - 0.4 if " / " in name else NAME_FS
    out.append(f'  <rect x="{CX-NODE_W/2:.1f}" y="{c-NODE_H/2:.1f}" width="{NODE_W}" height="{NODE_H}" rx="{NODE_H/2:.1f}" ry="{NODE_H/2:.1f}" fill="{fill}" stroke="{st}" stroke-width="{sw}" filter="url(#ds)"/>')
    fw = ' font-weight="700"' if cat == "hook" else ''
    out.append(f'  <text x="{CX:.1f}" y="{c:.1f}" font-size="{fs}" fill="#1a1a1a"{fw} text-anchor="middle" dominant-baseline="central">{esc(name)}</text>')
    note(c, wrapped[i], boxw[i], boxh[i])

# end dot
ey = cy[-1] + NODE_H/2 + END_GAP + 5   # end dot nudged 5px lower, connecting line longer
out.append(f'  <line x1="{CX:.1f}" y1="{cy[-1]+NODE_H/2:.1f}" x2="{CX:.1f}" y2="{ey-END_R:.1f}" stroke="{STROKE}" stroke-width="1.4"/>')
out.append(f'  <circle cx="{CX:.1f}" cy="{ey:.1f}" r="{END_R}" fill="none" stroke="{STROKE}" stroke-width="1.6"/>')
out.append(f'  <circle cx="{CX:.1f}" cy="{ey:.1f}" r="3.2" fill="{STROKE}"/>')

out.append('</svg>')

_out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "quickstart", "protected", "pages", "Fundamentals", "page-lifecycle.svg"))
with open(_out, "w") as f:
    f.write("\n".join(out))
print(f"wrote {_out}  {W}x{H:.0f}")
