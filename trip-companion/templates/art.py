"""Hand-drawn SVG stickers for the trip companion page.

Fixed colours on purpose: they are illustrations with a white sticker edge, so they read on every theme.
Each sticker is one <svg class="sticker" viewBox="0 0 W H">. Anything that only belongs on a couple's trip
(little hearts) carries class="rom" on a single self-closing element; build.py drops those when romance is off.

Add a sticker: write another UPPERCASE constant in the same style (see references/scenes-and-art.md) and
list its lowercase name in NAMES.
"""
import re

SKIN = "#F2C29B"; SKIN2 = "#E6A97F"; INK = "#2A2A3A"; BLUSH = "#F49AA8"
HEART = "M0,6 C-11,-2 -7,-11 0,-5 C7,-11 11,-2 0,6Z"

def heart(x, y, s=1, c="#E8577E", cls="rom"):
    return f'<path class="{cls}" transform="translate({x},{y}) scale({s})" d="{HEART}" fill="{c}"/>'

SHADES = ('<g fill="{c}"><path d="M-22,-4 h18 q2,0 2,2 q-1,10 -10,10 q-10,0 -10,-10 q0,-2 2,-2Z"/>'
          '<path d="M4,-4 h18 q2,0 2,2 q-1,10 -10,10 q-10,0 -10,-10 q0,-2 2,-2Z"/>'
          '<rect x="-4" y="-3" width="8" height="2.6" rx="1.3"/></g>'
          '<path d="M-17,-1 l5,0" stroke="#fff" stroke-width="2" stroke-linecap="round" opacity=".7"/>'
          '<path d="M9,-1 l5,0" stroke="#fff" stroke-width="2" stroke-linecap="round" opacity=".7"/>')

def shades(x, y, s=1, c=INK):
    return f'<g transform="translate({x},{y}) scale({s})">{SHADES.format(c=c)}</g>'

STICK = 'stroke="#fff" stroke-width="7" stroke-linejoin="round" paint-order="stroke"'

PINEAPPLE = f'''<svg class="sticker" viewBox="0 0 120 170" aria-hidden="true">
<g {STICK}>
 <g fill="#3E9B5B"><path d="M60,62 C50,40 38,30 30,26 C44,28 54,36 60,50 C64,30 70,14 78,6 C74,24 72,40 68,58Z"/>
 <path d="M60,60 C66,42 80,30 94,28 C82,38 72,50 66,64Z"/><path d="M58,62 C48,52 36,48 24,50 C36,54 46,60 54,68Z"/></g>
 <ellipse cx="60" cy="112" rx="38" ry="50" fill="#F6B73C"/>
</g>
<g stroke="#D98B1C" stroke-width="2.5" fill="none" opacity=".75">
 <path d="M30,84 L84,150 M24,108 L66,160 M40,66 L94,132 M60,62 L98,108"/>
 <path d="M90,84 L36,150 M96,108 L54,160 M80,66 L26,132 M60,62 L22,108"/></g>
{shades(60, 104, 1.05)}
<path d="M50,124 q10,9 20,0" stroke="{INK}" stroke-width="3" fill="none" stroke-linecap="round"/>
<circle cx="38" cy="120" r="5" fill="{BLUSH}" opacity=".8"/><circle cx="82" cy="120" r="5" fill="{BLUSH}" opacity=".8"/>
</svg>'''

SUN = f'''<svg class="sticker spin" viewBox="0 0 150 150" aria-hidden="true">
<g class="rays" {STICK} fill="#F7A93B">{"".join(f'<path transform="rotate({a} 75 75)" d="M71,8 L79,8 L75,26Z" stroke-width="5"/>' for a in range(0, 360, 30))}</g>
<circle cx="75" cy="75" r="40" fill="#FFCB47" {STICK}/>
{shades(75, 70, 1.25)}
<path d="M62,90 q13,12 26,0" stroke="{INK}" stroke-width="3.2" fill="none" stroke-linecap="round"/>
<circle cx="52" cy="88" r="6" fill="{BLUSH}" opacity=".8"/><circle cx="98" cy="88" r="6" fill="{BLUSH}" opacity=".8"/>
</svg>'''

COCONUT = f'''<svg class="sticker" viewBox="0 0 140 150" aria-hidden="true">
<g {STICK}>
 <path d="M84,20 L100,94" stroke="#E8577E" stroke-width="6" stroke-linecap="round"/>
 <path d="M40,30 Q70,6 100,30 Z" fill="#7FD1C7"/><path d="M70,24 L74,70" stroke="#8A5A3B" stroke-width="3"/>
 <circle cx="70" cy="100" r="42" fill="#8A5A3B"/>
 <ellipse cx="70" cy="74" rx="34" ry="11" fill="#FFF6E5"/>
</g>
<path d="M84,20 L96,76" stroke="#E8577E" stroke-width="5" stroke-linecap="round"/>
<path d="M40,30 Q70,6 100,30 Z" fill="#7FD1C7"/><path d="M55,27 Q70,14 85,27" stroke="#fff" stroke-width="2" fill="none" opacity=".6"/>
<path d="M50,110 q-6,-12 2,-22" stroke="#A9744F" stroke-width="3" fill="none" stroke-linecap="round"/>
<circle cx="112" cy="70" r="9" fill="#F6B73C"/><path d="M106,70 h12" stroke="#fff" stroke-width="2"/>
</svg>'''

HIBISCUS = f'''<svg class="sticker" viewBox="0 0 120 120" aria-hidden="true">
<g {STICK} fill="#E8577E">{"".join(f'<ellipse transform="rotate({a} 60 60)" cx="60" cy="32" rx="20" ry="26"/>' for a in range(0, 360, 72))}</g>
{"".join(f'<ellipse transform="rotate({a} 60 60)" cx="60" cy="32" rx="20" ry="26" fill="#E8577E"/>' for a in range(0, 360, 72))}
<circle cx="60" cy="60" r="12" fill="#B7305C"/>
<path d="M60,60 L84,36" stroke="#F6B73C" stroke-width="3" stroke-linecap="round"/>
<circle cx="86" cy="34" r="4" fill="#F6B73C"/><circle cx="80" cy="30" r="3" fill="#F6B73C"/><circle cx="90" cy="40" r="3" fill="#F6B73C"/>
</svg>'''

SUNGLASSES = f'''<svg class="sticker" viewBox="0 0 140 70" aria-hidden="true">
<g {STICK}><path d="M14,22 h44 q4,0 4,4 q-2,26 -24,26 q-22,0 -24,-26 q0,-4 4,-4Z M82,22 h44 q4,0 4,4 q-2,26 -24,26 q-22,0 -24,-26 q0,-4 4,-4Z" fill="#E8577E"/>
<rect x="56" y="24" width="28" height="7" rx="3.5" fill="#E8577E"/></g>
<path d="M22,30 q10,-2 16,0" stroke="#fff" stroke-width="3" stroke-linecap="round" opacity=".6"/>
<path d="M90,30 q10,-2 16,0" stroke="#fff" stroke-width="3" stroke-linecap="round" opacity=".6"/>
</svg>'''

PALM = f'''<svg class="sticker sway" viewBox="0 0 140 180" aria-hidden="true">
<g {STICK}>
 <path d="M70,176 C74,140 66,100 76,60" stroke="#A9744F" stroke-width="12" fill="none" stroke-linecap="round"/>
 <g fill="#3E9B5B"><path d="M76,58 C60,36 34,34 14,46 C36,42 56,48 76,62Z"/><path d="M76,58 C92,34 118,34 134,48 C112,42 94,48 76,62Z"/>
 <path d="M76,58 C70,30 52,14 34,10 C52,22 64,38 74,60Z"/><path d="M76,58 C84,30 102,16 120,14 C104,24 90,40 78,60Z"/>
 <path d="M76,58 C56,60 40,76 34,92 C48,78 62,70 78,64Z"/><path d="M76,58 C96,62 110,78 116,94 C102,80 90,72 74,64Z"/></g>
</g>
<circle cx="70" cy="66" r="7" fill="#8A5A3B"/><circle cx="82" cy="68" r="7" fill="#8A5A3B"/>
</svg>'''

PLANE = f'''<svg class="sticker" viewBox="0 0 170 110" aria-hidden="true">
<path d="M8,84 q20,-10 40,-4 q20,6 40,-4" stroke="#fff" stroke-width="10" fill="none" stroke-linecap="round" opacity=".9"/>
<path d="M8,84 q20,-10 40,-4 q20,6 40,-4" stroke="#BFE3DF" stroke-width="4" fill="none" stroke-linecap="round" stroke-dasharray="2 9"/>
<g {STICK}>
 <path d="M70,44 L100,14 L114,14 L102,46Z" fill="#7FB2E8"/>
 <path d="M30,56 Q30,40 60,40 L140,40 Q160,40 160,52 Q160,62 140,62 L46,62 Q30,62 30,56Z" fill="#FFFFFF"/>
 <path d="M34,52 L22,26 L36,26 L52,44Z" fill="#E8577E"/>
 <path d="M84,56 L104,86 L118,86 L108,56Z" fill="#7FB2E8"/>
</g>
<path d="M30,56 Q30,40 60,40 L140,40 Q160,40 160,52 Q160,62 140,62 L46,62 Q30,62 30,56Z" fill="#FFFFFF" stroke="#C8D6DF" stroke-width="2"/>
{"".join(f'<circle cx="{x}" cy="49" r="3.4" fill="#7FB2E8"/>' for x in range(64, 140, 12))}
<path d="M148,44 q8,2 10,8 l-10,0Z" fill="#7FB2E8"/>
{heart(26, 22, .9)}
</svg>'''

TEMPLE = f'''<svg class="sticker" viewBox="0 0 140 160" aria-hidden="true">
<g {STICK}>
 <path d="M70,6 L74,40 L66,40Z" fill="#F6B73C"/>
 <path d="M70,34 C56,60 48,74 40,84 L100,84 C92,74 84,60 70,34Z" fill="#F6B73C"/>
 <rect x="34" y="84" width="72" height="12" rx="3" fill="#E8577E"/>
 <rect x="26" y="96" width="88" height="44" rx="4" fill="#FFF3E3"/>
 <rect x="18" y="140" width="104" height="12" rx="3" fill="#E8577E"/>
</g>
<path d="M70,34 C56,60 48,74 40,84 L100,84 C92,74 84,60 70,34Z" fill="#F6B73C"/>
<path d="M58,64 h24 M52,74 h36" stroke="#D98B1C" stroke-width="3" stroke-linecap="round"/>
<path d="M60,140 v-24 q10,-12 20,0 v24Z" fill="#B7305C"/>
<circle cx="42" cy="114" r="5" fill="#7FD1C7"/><circle cx="98" cy="114" r="5" fill="#7FD1C7"/>
</svg>'''

# Two riders on a scooter, facing right. Scenes use only the <g class="ride"> part.
SCOOTER = f'''<svg class="moto" viewBox="0 0 340 230" role="img" aria-label="Two people riding a scooter">
<g class="hills"><path d="M0,190 L60,110 L110,160 L170,80 L240,150 L290,104 L340,150 L340,230 L0,230Z" fill="#9CCFA8" opacity=".55"/>
<path d="M0,200 L80,150 L150,190 L230,140 L340,196 L340,230 L0,230Z" fill="#6DB383" opacity=".55"/></g>
<path d="M0,206 Q170,196 340,206" stroke="#C9B79C" stroke-width="10" fill="none" stroke-linecap="round" opacity=".7"/>
<g class="ride">
 <g stroke="#9AA9B0" stroke-width="4" stroke-linecap="round" opacity=".8"><path d="M14,150 h30"/><path d="M4,166 h34"/><path d="M20,182 h24"/></g>
 <g class="hearts">{heart(70, 56, 1.1)}{heart(50, 80, .8, "#F49AA8")}{heart(86, 30, .7, "#F49AA8")}</g>
 <!-- wheels -->
 <g class="wheel"><circle cx="96" cy="180" r="24" fill="{INK}"/><circle cx="96" cy="180" r="10" fill="#D7DEE2"/><path d="M96,170 v20 M86,180 h20" stroke="#9AA9B0" stroke-width="2"/></g>
 <g class="wheel w2"><circle cx="252" cy="180" r="24" fill="{INK}"/><circle cx="252" cy="180" r="10" fill="#D7DEE2"/><path d="M252,170 v20 M242,180 h20" stroke="#9AA9B0" stroke-width="2"/></g>
 <!-- scooter -->
 <path d="M62,168 C62,138 86,128 120,128 L190,128 C204,128 212,140 214,152 L222,168Z" fill="#5CC4B8"/>
 <rect x="122" y="152" width="96" height="12" rx="6" fill="#3FA79B"/>
 <path d="M214,164 C214,128 222,108 236,98 L246,102 C240,124 240,148 252,166Z" fill="#5CC4B8"/>
 <path d="M240,100 L252,180" stroke="#3FA79B" stroke-width="5"/>
 <circle cx="250" cy="108" r="8" fill="#FFE07A" stroke="#fff" stroke-width="3"/>
 <path d="M226,92 L246,88" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>
 <path d="M100,128 C100,114 116,112 142,112 L184,112 C194,112 196,128 186,128Z" fill="#7A4E3A"/>
 <path d="M66,150 q-10,-2 -12,8" stroke="#E8577E" stroke-width="7" stroke-linecap="round" fill="none"/>
 <!-- passenger -->
 <path d="M150,116 L170,128 L162,156" stroke="#2F6FA8" stroke-width="12" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
 <path d="M160,158 h10" stroke="#fff" stroke-width="8" stroke-linecap="round"/>
 <path d="M134,60 C108,62 92,72 84,86 C100,78 112,78 124,80Z" fill="#5A3A2A"/>
 <path d="M130,70 C128,96 132,112 140,118 L164,118 C166,100 164,82 156,68 Q144,62 130,70Z" fill="#F49AA8"/>
 <circle cx="148" cy="50" r="15" fill="{SKIN}"/>
 <path d="M132,44 C132,24 164,22 166,40 L166,44 L132,44Z" fill="#E8577E"/>
 <path d="M132,44 h34" stroke="#B7305C" stroke-width="3"/><path d="M134,44 c-3,6 -2,12 2,16" stroke="#5A3A2A" stroke-width="4" fill="none" stroke-linecap="round"/>
 <path d="M153,50 q3,-2 6,0" stroke="{INK}" stroke-width="1.8" fill="none" stroke-linecap="round"/><circle cx="160" cy="56" r="3.2" fill="{BLUSH}" opacity=".8"/>
 <path d="M153,58 q3,2.5 6,0" stroke="{INK}" stroke-width="1.6" fill="none" stroke-linecap="round"/>
 <!-- driver -->
 <path d="M188,114 L212,124 L208,154" stroke="#2A4D5C" stroke-width="13" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
 <path d="M206,156 h12" stroke="#fff" stroke-width="8" stroke-linecap="round"/>
 <path d="M172,62 C168,88 172,108 180,118 L204,118 C208,98 206,80 198,64 Q186,56 172,62Z" fill="#F6B73C"/>
 <circle cx="182" cy="84" r="2.6" fill="#E8577E"/><circle cx="194" cy="98" r="2.6" fill="#E8577E"/><circle cx="184" cy="106" r="2.6" fill="#E8577E"/>
 <path d="M196,72 L230,90" stroke="{SKIN2}" stroke-width="8" stroke-linecap="round"/>
 <path d="M158,78 C168,86 180,90 194,84" stroke="{SKIN}" stroke-width="7" stroke-linecap="round" fill="none"/>
 <circle cx="192" cy="42" r="16" fill="{SKIN}"/>
 <path d="M174,36 C174,14 210,12 210,32 L210,36 L174,36Z" fill="#2F6FA8"/>
 <path d="M192,40 h18 q2,0 2,2 q-1,7 -9,7 q-9,0 -11,-7Z" fill="{INK}"/><path d="M196,43 h5" stroke="#fff" stroke-width="1.6" opacity=".7"/>
 <path d="M174,36 h36" stroke="#1F4F7A" stroke-width="3"/><circle cx="203" cy="52" r="3.2" fill="{BLUSH}" opacity=".8"/>
 <path d="M197,55 q5,3 9,0" stroke="{INK}" stroke-width="1.8" fill="none" stroke-linecap="round"/>
 <path d="M180,38 c-4,4 -3,10 2,13" stroke="#5A3A2A" stroke-width="3" fill="none" stroke-linecap="round"/>
</g>
</svg>'''


OUT = 'stroke="#fff" stroke-linecap="round" stroke-linejoin="round" fill="none"'

SUITCASE = f'''<svg class="sticker" viewBox="0 0 130 150" aria-hidden="true">
<path d="M46,36 V22 Q46,12 56,12 H74 Q84,12 84,22 V36" {OUT} stroke-width="16"/>
<path d="M46,36 V22 Q46,12 56,12 H74 Q84,12 84,22 V36" fill="none" stroke="#8A5A3B" stroke-width="7" stroke-linecap="round"/>
<g {STICK}><rect x="16" y="34" width="98" height="100" rx="14" fill="#5CC4B8"/>
 <circle cx="38" cy="138" r="7" fill="{INK}"/><circle cx="92" cy="138" r="7" fill="{INK}"/></g>
<rect x="16" y="34" width="98" height="100" rx="14" fill="#5CC4B8"/>
<path d="M16,64 h98 M16,104 h98" stroke="#3FA79B" stroke-width="7"/>
<rect x="55" y="55" width="20" height="18" rx="4" fill="#F6B73C"/><rect x="55" y="95" width="20" height="18" rx="4" fill="#F6B73C"/>
<circle cx="92" cy="84" r="11" fill="#E8577E" stroke="#fff" stroke-width="2.5"/><path d="M86,84 h12 M92,78 v12" stroke="#fff" stroke-width="2.5" stroke-linecap="round"/>
<path d="M28,46 v14" stroke="#fff" stroke-width="4" stroke-linecap="round" opacity=".5"/>
</svg>'''

CAMERA = f'''<svg class="sticker" viewBox="0 0 150 120" aria-hidden="true">
<g {STICK}><path d="M48,32 l9,-16 h36 l9,16Z" fill="#B7305C"/><rect x="22" y="22" width="18" height="12" rx="3" fill="{INK}"/>
 <rect x="10" y="30" width="130" height="80" rx="14" fill="#E8577E"/></g>
<rect x="10" y="30" width="130" height="80" rx="14" fill="#E8577E"/>
<path d="M10,52 h130" stroke="#B7305C" stroke-width="5"/>
<circle cx="75" cy="72" r="30" fill="#FFF6E5"/><circle cx="75" cy="72" r="22" fill="{INK}"/><circle cx="75" cy="72" r="11" fill="#7FB2E8"/>
<circle cx="68" cy="64" r="4.5" fill="#fff" opacity=".8"/>
<rect x="110" y="38" width="20" height="9" rx="3" fill="#FFE07A"/>
</svg>'''

TRAM = f'''<svg class="sticker" viewBox="0 0 170 130" aria-hidden="true">
<path d="M85,34 V14 M58,14 H112" {OUT} stroke-width="12"/><path d="M85,34 V14 M58,14 H112" fill="none" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>
<g {STICK}><rect x="12" y="32" width="146" height="74" rx="16" fill="#F6B73C"/>
 <circle cx="46" cy="110" r="10" fill="{INK}"/><circle cx="124" cy="110" r="10" fill="{INK}"/></g>
<rect x="12" y="32" width="146" height="74" rx="16" fill="#F6B73C"/>
<path d="M12,80 h146 v10 q0,16 -16,16 h-114 q-16,0 -16,-16Z" fill="#FFF6E5"/>
{"".join(f'<rect x="{x}" y="44" width="24" height="26" rx="5" fill="#7FD1C7"/>' for x in (24, 56, 90, 122))}
<path d="M28,48 l8,0 M60,48 l8,0 M94,48 l8,0 M126,48 l8,0" stroke="#fff" stroke-width="3" stroke-linecap="round" opacity=".7"/>
<circle cx="146" cy="92" r="5" fill="#FFE07A" stroke="#D98B1C" stroke-width="1.5"/><path d="M22,92 h20" stroke="#E8577E" stroke-width="5" stroke-linecap="round"/>
<circle cx="46" cy="110" r="4" fill="#D7DEE2"/><circle cx="124" cy="110" r="4" fill="#D7DEE2"/>
</svg>'''

CACTUS = f'''<svg class="sticker" viewBox="0 0 120 160" aria-hidden="true">
<path d="M60,150 V34 M60,100 H32 V66 M60,84 H92 V52" {OUT} stroke-width="38"/>
<path d="M60,150 V34 M60,100 H32 V66 M60,84 H92 V52" fill="none" stroke="#3E9B5B" stroke-width="26" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M54,40 v96 M32,72 v20 M92,58 v18" stroke="#2D7A45" stroke-width="2.5" stroke-linecap="round" opacity=".7"/>
{shades(62, 62, .72)}
<path d="M55,76 q7,6 14,0" stroke="{INK}" stroke-width="2.6" fill="none" stroke-linecap="round"/>
<g fill="#E8577E" stroke="#fff" stroke-width="2">{"".join(f'<ellipse transform="rotate({a} 60 20)" cx="60" cy="11" rx="6" ry="9"/>' for a in range(0, 360, 72))}</g><circle cx="60" cy="20" r="4.5" fill="#F6B73C"/>
</svg>'''

PEAK = f'''<svg class="sticker" viewBox="0 0 160 130" aria-hidden="true">
<g {STICK}><path d="M8,120 L66,18 L98,70 L114,50 L152,120Z" fill="#6E8FB3"/></g>
<path d="M8,120 L66,18 L98,70 L114,50 L152,120Z" fill="#6E8FB3"/>
<path d="M66,18 L45,55 L57,49 L66,61 L76,47 L84,53Z" fill="#fff"/><path d="M114,50 L103,66 L112,62 L120,70 L125,64Z" fill="#fff"/>
<path d="M66,18 V4" stroke="{INK}" stroke-width="3" stroke-linecap="round"/><path d="M66,4 l16,5 l-16,6Z" fill="#E8577E"/>
<path d="M30,120 q14,-18 30,-8 q12,-14 30,-4 q14,-10 30,2 q10,-4 20,10Z" fill="#3E9B5B"/>
</svg>'''

NAMES = ["sun", "pineapple", "coconut", "hibiscus", "palm", "plane", "temple", "sunglasses", "suitcase", "camera", "tram", "cactus", "peak"]


def no_romance(svg):
    """Drop the couple-only bits (single self-closing elements with class rom)."""
    return re.sub(r'<[a-z]+ class="rom[^>]*/>', "", svg)


def get(name, romance=True):
    s = globals()[name.upper()]
    return s if romance else no_romance(s)
