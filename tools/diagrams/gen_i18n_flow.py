#!/usr/bin/env python3
"""Generate Advanced/i18n-flow.svg — culture determination + the translation lookup.

Verified against 4.3.3:
  Culture (I18N/TGlobalization.php, TGlobalizationAutoDetect.php)
    - init(): Charset <- DefaultCharset, Culture <- DefaultCulture when unset (118-125).
    - TGlobalizationAutoDetect::init(): first browser Accept-Language that is a valid ICU
      locale (q-values stripped, "en-US" -> "en_US"), skipped unless in AvailableLanguages
      when that is set; setCulture(); none accepted -> Culture stays (73-89, 124-168).
    - setCulture() normalizes hyphens to underscores (207-214); a page directive
      <%@ Application.Globalization.Culture="zh" %> or code sets it later.
    - getTranslationConfiguration() is null when TranslateDefaultCulture is false and
      Culture == DefaultCulture (235-240) -> localize() returns the text as written.
  Translation (Prado.php localize; I18N/Translation.php; I18N/core/MessageFormat.php;
               MessageSource.php load(); MessageSource_*.php getCatalogueList())
    - no globalization module / no translation config -> strtr(text, params), no marker.
    - Translation::init: MessageSource::factory(type, source) for XLIFF|gettext|PHP|Database;
      setCulture; MessageCache(runtime/i18n) when cache; marker -> setUntranslatedPS;
      autosave -> saveMessages on OnEndRequest.
    - load(): variants most specific first; per variant: cache hit, else loadData + cache save.
      XLIFF/gettext/PHP for en_US: en_US/messages.xml, en/messages.xml, messages.en_US.xml,
      messages.en.xml, messages.xml (XLIFF also tries each as .xlf). Database: messages.en_US,
      messages.en, messages.
    - formatString(): first variant that holds the source string wins; non-empty target ->
      strtr(target, args); empty target -> marker-wrapped text; not found -> append() +
      marker-wrapped text.
Scope: 4.3.3 only. Python 3 stdlib only.
Usage: python3 tools/diagrams/gen_i18n_flow.py
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
ARROW = "#4a4a4a"; INK = "#1a1a1a"
STEP  = ("#dbe9f6", "#3f6f9f")   # culture steps (blue)
PROC  = ("#f6f6f3", "#8a8a8a")   # process (neutral)
DEC   = ("#fff6d8", "#b08a1f")   # decision (amber)
OK    = ("#dcecd6", "#4f8140")   # translated (green)
MARK  = ("#f6e6c8", "#b07f24")   # untranslated / marker (amber)
PLAIN = ("#eef1f5", "#7a8a9a")   # returned as written (grey)

o = []
def rrect(x, y, w, h, col, rx=7, sw=1.2, shadow=True, dash=None):
    sh = ' filter="url(#ds)"' if shadow else ''
    da = f' stroke-dasharray="{dash}"' if dash else ''
    o.append(f'  <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{col[0]}" stroke="{col[1]}" stroke-width="{sw}"{da}{sh}/>')
def txt(x, y, s, fs=9.0, fill=INK, weight=None, anchor="middle", italic=False, family=None):
    fw = f' font-weight="{weight}"' if weight else ''
    it = ' font-style="italic"' if italic else ''
    fm = f' font-family="{family}"' if family else ''
    o.append(f'  <text x="{x:.1f}" y="{y:.1f}" font-size="{fs}"{fw}{it}{fm} fill="{fill}" text-anchor="{anchor}" dominant-baseline="central">{esc(s)}</text>')
def poly(pts, arrow=True, stroke=ARROW, sw=1.3):
    d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    mk = ' marker-end="url(#arrow)"' if arrow else ''
    o.append(f'  <polyline points="{d}" fill="none" stroke="{stroke}" stroke-width="{sw}"{mk}/>')
def title(cx, y, s):
    txt(cx, y, s, fs=12, weight=700, fill="#333")
    tw = text_px(s, 12)*1.07
    o.append(f'  <line x1="{cx-tw/2:.1f}" y1="{y+9:.1f}" x2="{cx+tw/2:.1f}" y2="{y+9:.1f}" stroke="#333" stroke-width="1.1"/>')

LH  = 11.5     # line pitch inside a box, header and sub-lines alike
PAD = 9        # top/bottom padding inside a box
def box_h(nlines): return 2*PAD + 13 + (nlines-1)*LH
def node(cx, top, w, col, name, subs=(), fs=9.6, sub_fs=7.9, mono_subs=False, rx=7):
    """box sized from its lines: PAD, header, then sub-lines at the same pitch, PAD; returns bottom"""
    h = box_h(1+len(subs))
    rrect(cx-w/2, top, w, h, col, rx=rx)
    y = top + PAD + 6.5
    txt(cx, y, name, fs=fs, weight=700)
    for s_ in subs:
        y += LH
        txt(cx, y, s_, fs=sub_fs, fill="#555", italic=not mono_subs, family=(MONO if mono_subs else None))
    return top + h
def node_c(cx, cy, w, col, name, subs=(), **kw):
    return node(cx, cy - box_h(1+len(subs))/2, w, col, name, subs, **kw)
def diamond(cx, top, w, h, s, s2=None):
    cy = top + h/2
    o.append(f'  <polygon points="{cx:.1f},{top:.1f} {cx+w/2:.1f},{cy:.1f} {cx:.1f},{top+h:.1f} {cx-w/2:.1f},{cy:.1f}" fill="{DEC[0]}" stroke="{DEC[1]}" stroke-width="1.2" filter="url(#ds)"/>')
    if s2:
        txt(cx, cy-6, s, fs=8.6, weight=700); txt(cx, cy+6, s2, fs=8.6, weight=700)
    else:
        txt(cx, cy, s, fs=8.8, weight=700)
    return top + h
def lab(x, y, s, anchor="middle", fill="#555"):
    txt(x, y, s, fs=7.6, fill=fill, italic=True, anchor=anchor)

W, H = 904, 540
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}">']
svg.append('''  <defs>
    <filter id="ds" x="-25%" y="-30%" width="150%" height="170%">
      <feDropShadow dx="0.6" dy="0.9" stdDeviation="0.7" flood-color="#000" flood-opacity="0.16"/>
    </filter>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="''' + ARROW + '''"/>
    </marker>
  </defs>''')
svg.append(f'  <rect x="0" y="0" width="{W}" height="{H}" fill="#fff"/>')
o = svg

# ============================ left: which culture ============================
LX = 160; LW = 272; GL = 27          # GL: arrow length between steps
title(LX, 30, "Which culture applies")
y = 56
b = node(LX, y, LW, STEP, "DefaultCulture and DefaultCharset",
         ["module properties; the defaults are en and UTF-8"])
poly([(LX, b), (LX, b+GL)]); lab(LX+6, b+GL/2-2, "then, with TGlobalizationAutoDetect", anchor="start")
b = node(LX, b+GL, LW, STEP, "Browser Accept-Language",
         ["the first valid locale wins, en-US becomes en_US",
          "a language outside AvailableLanguages is skipped",
          "no accepted language leaves the default in place"])
poly([(LX, b), (LX, b+GL)]); lab(LX+6, b+GL/2-2, "then, when a page or code sets it", anchor="start")
b = node(LX, b+GL, LW, STEP, "Page directive or code",
         ['<%@ Application.Globalization.Culture="zh" %>',
          "$this->Application->Globalization->Culture = 'zh'"], mono_subs=True)
poly([(LX, b), (LX, b+GL)])
b = node(LX, b+GL, 150, OK, "Culture", rx=15)
lab(LX, b+16, "each later step replaces the value from the step before it")
# the no-translation gate
gy = b + 69
rrect(LX-LW/2, gy, LW, box_h(3), PLAIN, dash="3,2", shadow=False)
txt(LX, gy+PAD+6.5, "No lookup at all", fs=8.6, weight=700, fill=PLAIN[1])
lab(LX, gy+PAD+6.5+LH, "TranslateDefaultCulture is false and", fill="#555")
lab(LX, gy+PAD+6.5+2*LH, "Culture equals DefaultCulture: text is returned as written", fill="#555")

# ============================ right: which translation ============================
RX = 560; RW = 300; G = 26           # G: arrow length between steps
title(RX+89, 30, "How a string is translated")
y = 51
b = node(RX, y, RW, PLAIN, "Prado::localize()   ·   <com:TTranslate>   ·   <%[ text ]%>", fs=8.8, rx=15)
poly([(RX, b), (RX, b+G)])
# decision: configured?
dw, dh = 190, 46
t = b+G; cy = t+dh/2
b = diamond(RX, t, dw, dh, "a translation source", "is configured?")
lab(RX+6, b+7, "yes", anchor="start")
poly([(RX+dw/2, cy), (RX+150, cy)]); lab(RX+dw/2+6, cy-7, "no", anchor="start")
node_c(RX+240, cy, 176, PLAIN, "Text as written", ["{params} substituted, no marker"], fs=9.2)
poly([(RX, b), (RX, b+G)])
# message source
b = node(RX, b+G, RW, PROC, "MessageSource for the configured type",
         ["XLIFF  ·  gettext  ·  PHP  ·  Database",
          "source is a directory, or a connection id for Database"])
poly([(RX, b), (RX, b+G)])
# variants box: header, caption, column headers, rows, note — all at the LH pitch
VY = b+G
rows = ["en_US/messages.xml", "en/messages.xml", "messages.en_US.xml", "messages.en.xml", "messages.xml"]
VH = box_h(3 + len(rows) + 1)
rrect(RX-RW/2, VY, RW, VH, PROC)
ly = VY + PAD + 6.5
txt(RX, ly, "Load the catalogue, most specific variant first", fs=9.2, weight=700); ly += LH
lab(RX, ly, "for Culture en_US and catalogue messages", fill="#666"); ly += LH
cx1, cx2 = RX-72, RX+82
txt(cx1, ly, "XLIFF, gettext, PHP", fs=7.8, weight=700, fill="#444")
txt(cx2, ly, "Database", fs=7.8, weight=700, fill="#444")
div_top = ly - 6
for i, f in enumerate(rows):
    txt(cx1, ly+(i+1)*LH, f, fs=7.6, family=MONO, fill="#2a2a2a")
for i, f in enumerate(["messages.en_US", "messages.en", "messages"]):
    txt(cx2, ly+(i+1)*LH, f, fs=7.6, family=MONO, fill="#2a2a2a")
ly += (len(rows)+1)*LH
o.append(f'  <line x1="{RX+6:.1f}" y1="{div_top:.1f}" x2="{RX+6:.1f}" y2="{ly-6:.1f}" stroke="#d0d0cc" stroke-width="1"/>')
lab(RX, ly, "cache=true keeps each loaded variant in runtime/i18n", fill="#666")
b = VY + VH
poly([(RX, b), (RX, b+G)])
# decision: found?
dw, dh = 240, 48
t = b+G; cy = t+dh/2
b = diamond(RX, t, dw, dh, "the first variant holding the", "string has a target?")
lab(RX+6, b+7, "yes", anchor="start")
poly([(RX+dw/2, cy), (RX+150, cy)]); lab(RX+dw/2+6, cy-7, "no", anchor="start")
node_c(RX+240, cy, 176, MARK, "@@text@@",
       ["the marker wraps the text", "autosave appends it on OnEndRequest"], fs=9.2)
poly([(RX, b), (RX, b+G)])
b = node(RX, b+G, RW, OK, "Translated target", ["{params} substituted"], fs=9.4)
H = int(b + 16)
o[0] = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}">'
o[2] = f'  <rect x="0" y="0" width="{W}" height="{H}" fill="#fff"/>'

o.append('</svg>')
path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "quickstart", "protected", "pages", "Advanced", "i18n-flow.svg"))
with open(path, "w") as f:
    f.write("\n".join(o))
print(f"wrote {path}  {W}x{H}")
