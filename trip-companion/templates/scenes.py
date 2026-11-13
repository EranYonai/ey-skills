"""Scroll scenes for the journey: one illustrated SVG per chapter, picked by a scene type in the trip data.

Every scene is drawn in a composed resting state, so it reads as a finished picture when scripts or motion are
off. The page's script (template.html, "scroll motion") moves the pieces as the scene scrolls through the screen,
using the class names below. Shared hooks, understood for every scene:

    p-far / p-mid / p-near   parallax layers          wv1 / wv2 / wv3   wave bands that slide sideways
    draw                     a path that draws itself (needs pathLength="1")
    actor + data-path        a group that travels along a path in the same svg (data-at = resting position 0..1)
    actor-x + data-from/to/y a group that slides horizontally
    pop                      a sticker that pops in; the first one in a scene can carry the "mascot" secret
    holdable                 the thing a long press can turn into the "hold" secret
    glint                    short horizontal light strokes on water

Scene-specific moves (a setting sun, falling flowers, windows lighting up) are keyed on data-kind in the template.
Most colours are fixed: scenes are illustrations. Only the dark sky tones and the gold line work follow the theme,
through the palette build.py passes in (see themes/*.css, "@scene").

Add a scene type: write a function (o, c) -> svg string, register it in TYPES, and if it needs its own moves add
a block for its kind in the template's initMotion(). See references/scenes-and-art.md.
"""
import random, re
import art as ST

PALETTE = dict(deep="#0A261F", dark="#123B30", mid="#1E5A47", gold="#E3B95A", gold2="#C99A3A", ivory="#F8F3E8")
SAND = "#EBD9A9"


class Ctx:
    """What a scene function gets besides its options: palette, romance flag, and a unique id suffix."""
    def __init__(self, uid, palette=None, romance=True):
        self.uid, self.romance = uid, romance
        self.p = dict(PALETTE, **(palette or {}))

    def __getattr__(self, k):
        return self.p[k]

    def st(self, name):
        return ST.get(name, self.romance)


def _parts(sticker):
    vb = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', sticker)
    return float(vb.group(1)), float(vb.group(2)), sticker[sticker.index(">") + 1: sticker.rindex("</svg>")]


def nest(sticker, x, y, w, cls="", flip=False, tap=True):
    """Place a sticker drawing inside a scene, w wide, with its top-left at x,y."""
    vw, vh, inner = _parts(sticker)
    s = w / vw
    t = f"translate({x + w if flip else x},{y}) scale({-s if flip else s},{s})"
    # outer group: moved by the scroll script; middle group: wiggles when tapped; inner group: placement
    return f'<g class="{cls}"><g class="{"tap" if tap else ""}"><g transform="{t}">{inner}</g></g></g>'


def centred(sticker, w, cls="", hold=False):
    """A sticker centred on 0,0 so the script can move it with one translate."""
    vw, vh, inner = _parts(sticker)
    s = w / vw
    return (f'<g class="mv {cls}"><g class="tap{" holdable" if hold else ""}">'
            f'<g transform="scale({s}) translate({-vw / 2},{-vh / 2})">{inner}</g></g></g>')


def wave(y, amp, wl, fill, cls, width=900, depth=120, opacity=1):
    d = f"M-250,{y}"
    x = -250
    up = True
    while x < width:
        d += f" q{wl / 2},{-amp if up else amp} {wl},0"
        x += wl
        up = not up
    d += f" V{y + depth} H-250Z"
    return f'<path class="{cls}" d="{d}" fill="{fill}" opacity="{opacity}"/>'


def stars(n, seed, gold, w=400, h=150, cls="stars"):
    r = random.Random(seed)
    out = []
    for i in range(n):
        x, y, rad = r.uniform(6, w - 6), r.uniform(6, h), r.choice([.7, .9, 1.1, 1.5])
        out.append(f'<circle class="star s{i % 3}" cx="{x:.1f}" cy="{y:.1f}" r="{rad}" fill="{gold}"/>')
    return f'<g class="{cls}">{"".join(out)}</g>'


def svg(body, h=300, label=""):
    return (f'<svg class="scene-svg" viewBox="0 0 400 {h}" preserveAspectRatio="xMidYMax slice" role="img" '
            f'aria-label="{esc(label)}">{body}</svg>')


def esc(s):
    return str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def cap(text, x=14, y=291, anchor="start"):
    return f'<text class="sc-cap" x="{x}" y="{y}" text-anchor="{anchor}">{esc(text).upper()}</text>' if text else ""


def grad(gid, stops):
    return (f'<linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
            + "".join(f'<stop offset="{o}" stop-color="{col}"/>' for o, col in stops) + "</linearGradient>")


# ------------------------------------------------------------------ flight: a night flight between two labels
def flight(o, c):
    a, b = esc(o.get("frm", "")), esc(o.get("to", ""))
    return svg(f'''
<defs>{grad("g-" + c.uid, [(0, c.deep), (1, c.mid)])}</defs>
<rect width="400" height="300" fill="url(#g-{c.uid})"/>
{stars(34, 7, c.gold, h=190, cls="stars p-far")}
<g class="p-mid" fill="{c.ivory}" opacity=".09"><ellipse cx="80" cy="150" rx="70" ry="12"/><ellipse cx="300" cy="118" rx="90" ry="14"/><ellipse cx="210" cy="182" rx="56" ry="9"/></g>
<circle cx="200" cy="720" r="480" fill="{c.deep}" stroke="{c.gold2}" stroke-opacity=".55" stroke-width="1.2"/>
<circle cx="200" cy="728" r="480" fill="none" stroke="{c.gold2}" stroke-opacity=".22" stroke-width="1"/>
<path d="M46,250 Q200,96 354,246" fill="none" stroke="{c.gold2}" stroke-width="1.6" stroke-dasharray="1 7" stroke-linecap="round" opacity=".5"/>
<path class="draw route" d="M46,250 Q200,96 354,246" fill="none" stroke="{c.gold}" stroke-width="2.2" stroke-linecap="round" pathLength="1"/>
<circle cx="46" cy="250" r="4.5" fill="{c.gold}"/><text class="sc-cap" x="46" y="272" text-anchor="middle">{a}</text>
<circle cx="354" cy="246" r="4.5" fill="{c.gold}"/><text class="sc-cap" x="354" y="268" text-anchor="middle">{b}</text>
<g class="actor" data-path=".route" data-at=".5">{centred(c.st("plane"), 84, hold=True)}</g>
<g class="p-near" fill="{c.ivory}" opacity=".13"><ellipse cx="330" cy="292" rx="110" ry="16"/><ellipse cx="60" cy="296" rx="90" ry="14"/></g>
''', label=o.get("label") or f"A plane flying by night from {a} to {b}")


# ------------------------------------------------------------------ island: a boat crossing to an island
def boat(c):
    flag = (f'<path class="rom" transform="translate(-33,-24) scale(.7)" d="{ST.HEART}" fill="#E8577E"/>' if c.romance
            else '<path d="M-40,-28 l13,4 l-13,5Z" fill="#E8577E"/>')
    return f'''<g class="bob">
 <path d="M-46,0 h78 l16,-10 l-10,18 q-3,6 -12,6 h-58 q-10,0 -14,-14Z" fill="{c.ivory}" stroke="#fff" stroke-width="2"/>
 <path d="M-40,6 h70" stroke="{c.gold2}" stroke-width="3" stroke-linecap="round"/>
 <path d="M-22,-24 h40 v4 h-40Z" fill="{c.gold}"/><path d="M-18,-20 v20 M14,-20 v20" stroke="{c.gold2}" stroke-width="2"/>
 <circle cx="-8" cy="-7" r="5.5" fill="#F2C29B"/><path d="M-14,-8 q6,-9 12,0Z" fill="#E8577E"/>
 <circle cx="4" cy="-8" r="6" fill="#F2C29B"/><path d="M-2.5,-9 q6.5,-9 13,0Z" fill="#2F6FA8"/>
 <path d="M-40,-2 v-26" stroke="{c.gold2}" stroke-width="2"/>{flag}
 <g class="wake" stroke="{c.ivory}" stroke-width="2.4" stroke-linecap="round" opacity=".7"><path d="M-54,12 h-16"/><path d="M-60,18 h-22"/><path d="M-52,6 h-10"/></g>
 <rect x="-60" y="-34" width="116" height="56" fill="transparent"/>
</g>'''


def island(o, c):
    mascot, extra = o.get("mascot", "pineapple"), o.get("extra", "hibiscus")
    return svg(f'''
<defs>{grad("g-" + c.uid, [(0, "#124F4A"), (.62, "#3BA596"), (.66, "#8FD1C0")])}</defs>
<rect width="400" height="300" fill="url(#g-{c.uid})"/>
<g class="p-far"><circle cx="322" cy="92" r="70" fill="url(#g-glow)"/><circle cx="322" cy="92" r="22" fill="#F3D27C"/></g>
<g class="p-mid"><path d="M196,200 Q226,150 262,168 Q292,120 334,150 Q368,128 420,172 L420,204 L196,204Z" fill="#0F4A40"/>
 <g stroke="#0F4A40" stroke-width="3" fill="none" stroke-linecap="round"><path d="M300,140 q2,-16 -2,-26 M298,114 q-12,-6 -20,2 M298,114 q10,-10 20,-4 M298,114 q-2,-12 -12,-14"/><path d="M356,142 q2,-14 0,-22 M356,120 q-10,-6 -18,0 M356,120 q10,-8 18,-2"/></g></g>
<rect y="198" width="400" height="102" fill="#1D6E68"/>
{wave(202, 5, 46, "#27877C", "wv wv1")}
{wave(226, 6, 60, "#1D6E68", "wv wv2")}
<g class="actor-x boat" data-from="-70" data-to="238" data-y="236" transform="translate(120,236)"><g class="tap holdable">{boat(c)}</g></g>
{wave(252, 7, 74, "#145249", "wv wv3")}
<path d="M270,300 Q300,258 352,262 Q392,262 420,278 L420,300Z" fill="{SAND}"/>
{nest(c.st(mascot), 318, 176, 62, cls="pop") if mascot else ""}
{nest(c.st(extra), 286, 262, 30, cls="pop pop2") if extra else ""}
{cap(o.get("caption"))}
''', label=o.get("label") or "A small boat crossing the sea to an island")


# ------------------------------------------------------------------ lanterns: a full-moon night (inset scene and the moon secret)
def _float(x, y, s, i, c):
    return f'''<g transform="translate({x},{y}) scale({s})"><g class="floater k{i}"><g class="bob">
 <ellipse cx="0" cy="5" rx="17" ry="5" fill="#2D6A3E"/>
 <path d="M-15,4 q3,-13 9,-2Z M15,4 q-3,-13 -9,-2Z M-7,3 q7,-19 14,0Z" fill="#F4B6C6" stroke="#fff" stroke-width="1"/>
 <path d="M0,-6 v-7" stroke="{c.ivory}" stroke-width="2.2" stroke-linecap="round"/>
 <path class="flame" d="M0,-24 q5,7 0,12 q-5,-5 0,-12Z" fill="#FFD36B"/>
 <ellipse cx="0" cy="12" rx="12" ry="2" fill="{c.gold}" opacity=".35"/></g></g></g>'''


def _lantern(x, y, s, i):
    return f'''<g transform="translate({x},{y}) scale({s})"><g class="lantern l{i}">
 <ellipse cx="0" cy="0" rx="20" ry="24" fill="url(#g-glow)"/>
 <path d="M-8,-12 q8,-6 16,0 l-2,20 q-6,3 -12,0Z" fill="#F7C25C" stroke="#FCE7B0" stroke-width="1"/>
 <path class="flame" d="M0,8 q3,4 0,7 q-3,-3 0,-7Z" fill="#FFF2C4"/></g></g>'''


def lanterns(o, c):
    return svg(f'''
<defs>{grad("g-" + c.uid, [(0, c.deep), (1, c.mid)])}
<radialGradient id="g-mglow-{c.uid}"><stop offset="0" stop-color="#F6E7B8" stop-opacity=".5"/><stop offset="1" stop-color="#F6E7B8" stop-opacity="0"/></radialGradient></defs>
<rect width="400" height="240" fill="url(#g-{c.uid})"/>
{stars(26, 24, c.gold, h=120)}
<g class="moon"><circle cx="300" cy="66" r="80" fill="url(#g-mglow-{c.uid})"/><circle cx="300" cy="66" r="30" fill="#F6E7B8"/>
 <circle cx="290" cy="58" r="6" fill="#E4D29C" opacity=".6"/><circle cx="310" cy="76" r="4" fill="#E4D29C" opacity=".6"/><circle cx="306" cy="52" r="2.5" fill="#E4D29C" opacity=".6"/></g>
<path d="M-10,168 Q60,138 130,160 Q200,132 260,162 Q330,146 410,166 L410,180 L-10,180Z" fill="{c.deep}"/>
<rect y="172" width="400" height="68" fill="{c.dark}"/>
<g class="glint" stroke="#F6E7B8" stroke-linecap="round" opacity=".5"><path d="M280,182 h40" stroke-width="2"/><path d="M288,192 h26" stroke-width="1.6"/><path d="M270,204 h56" stroke-width="1.4"/><path d="M292,216 h20" stroke-width="1.2"/></g>
{"".join(_lantern(x, y, s, i) for i, (x, y, s) in enumerate([(56, 100, 1.2), (128, 50, .85), (190, 112, 1.35), (232, 44, .95), (92, 22, .7), (356, 124, 1.05)]))}
{wave(190, 3, 50, c.mid, "wv wv1", depth=60, opacity=.55)}
{"".join(_float(x, y, s, i, c) for i, (x, y, s) in enumerate([(70, 204, 1), (150, 222, 1.25), (232, 200, .85), (330, 218, 1.1)]))}
{wave(226, 3, 64, c.deep, "wv wv3", depth=30, opacity=.8)}
''', h=240, label=o.get("label") or "Lanterns rising and candles floating on the water under a full moon")


# ------------------------------------------------------------------ beach: the sun goes down into the sea
def beach(o, c):
    st = o.get("sticker", "coconut")
    return svg(f'''
<defs>{grad("g-" + c.uid, [(0, c.dark), (.45, "#2F7A5C"), (.7, "#E3B95A")])}
{grad("g-dusk-" + c.uid, [(0, "#3A1730"), (.5, "#9C2A4E"), (.72, "#E88B5A")])}</defs>
<rect width="400" height="300" fill="url(#g-{c.uid})"/>
<rect class="dusk" width="400" height="300" fill="url(#g-dusk-{c.uid})" opacity=".55"/>
{stars(16, 3, c.gold, h=90, cls="stars dusk-stars")}
<g class="birds p-far" stroke="{c.ivory}" stroke-width="2" fill="none" stroke-linecap="round" opacity=".7"><path d="M120,186 q6,-6 10,0 q4,-6 10,0"/><path d="M152,174 q5,-5 8,0 q3,-5 8,0"/></g>
<g class="sunset" transform="translate(262,186)">{centred(c.st("sun"), 104)}</g>
<rect y="208" width="400" height="92" fill="#145249"/>
<g class="glint" stroke="#E3B95A" stroke-linecap="round" opacity=".75"><path d="M226,218 h72" stroke-width="2.4"/><path d="M240,230 h44" stroke-width="2"/><path d="M216,244 h92" stroke-width="1.8"/><path d="M246,258 h32" stroke-width="1.4"/></g>
{wave(212, 4, 52, "#1B6A62", "wv wv1", opacity=.75)}
{wave(250, 6, 70, "#0F4A40", "wv wv3")}
<path d="M-20,300 Q20,256 86,262 Q140,266 170,300Z" fill="{SAND}"/>
{nest(c.st(st), 26, 198, 76, cls="pop") if st else ""}
{cap(o.get("caption"), 388, 291, "end")}
''', label=o.get("label") or "The sun setting into the sea")


# ------------------------------------------------------------------ palms: two palms and a hammock
def palms(o, c):
    f = lambda x, y, w, i: nest(c.st(o.get("falling", "hibiscus")), x, y, w, cls=f"fall f{i}", tap=False)
    hearts = (f'<path class="rom" transform="translate(186,222) scale(1.5)" d="{ST.HEART}" fill="#E8577E" stroke="#fff" stroke-width="1.4"/>'
              f'<path class="rom" transform="translate(212,224) scale(1.5)" d="{ST.HEART}" fill="#F49AA8" stroke="#fff" stroke-width="1.4"/>') if c.romance else ""
    return svg(f'''
<defs>{grad("g-" + c.uid, [(0, c.dark), (.7, "#3F8F5A"), (1, "#8CC79A")])}</defs>
<rect width="400" height="300" fill="url(#g-{c.uid})"/>
<g class="p-far"><circle cx="200" cy="210" r="120" fill="url(#g-glow)"/><circle cx="200" cy="214" r="40" fill="#F3D27C" opacity=".85"/></g>
<rect y="232" width="400" height="68" fill="#1D6E68"/>
{wave(236, 4, 50, "#27877C", "wv wv1")}
<g class="p-mid">{nest(c.st("palm"), 2, 128, 130, cls="swayer")}{nest(c.st("palm"), 268, 132, 126, cls="swayer s2", flip=True)}</g>
<g class="hammock"><path d="M70,204 Q200,276 330,204" fill="none" stroke="{c.ivory}" stroke-width="3" stroke-linecap="round"/>
 <path d="M100,216 Q200,268 300,216 Q200,238 100,216Z" fill="{c.ivory}" opacity=".9"/>
 <path d="M122,222 Q200,252 278,222" fill="none" stroke="{c.gold2}" stroke-width="1.5" stroke-dasharray="3 5"/>{hearts}</g>
{wave(264, 6, 72, "#145249", "wv wv3")}
{f(60, 40, 26, 0)}{f(150, 120, 20, 1)}{f(236, 70, 30, 2)}{f(330, 150, 22, 3)}{f(196, 20, 18, 4)}
{cap(o.get("caption"))}
''', label=o.get("label") or "Two palms and a hammock by the sea")


# ------------------------------------------------------------------ mountain: a winding road and a scooter
ROAD = "M-14,276 C36,272 52,240 104,246 S164,270 212,244 S262,206 312,222 S372,206 416,180"


def mountain(o, c):
    ride = c.st("scooter")
    ride = ride[ride.index('<g class="ride">'): ride.rindex("</g>") + 4]
    snow = o.get("snow")
    far, mid, near = ("#B9C9DA", "#7E98B5", "#3F5873") if snow else ("#5E9C74", "#2D6A3E", "#17432F")
    caps = ('<path d="M150,120 L128,144 L142,140 L150,150 L160,138 L172,144Z M40,150 L26,165 L38,162 L44,170 L54,162Z M262,146 L248,158 L260,156 L266,164 L276,157Z" fill="#fff" opacity=".9"/>'
            if snow else "")
    return svg(f'''
<defs>{grad("g-" + c.uid, [(0, c.dark), (.5, "#5C7FA0" if snow else "#2D6A3E"), (.78, "#E3B95A")])}</defs>
<rect width="400" height="300" fill="url(#g-{c.uid})"/>
<g class="sunrise"><circle cx="286" cy="170" r="84" fill="url(#g-glow)"/><circle cx="286" cy="170" r="24" fill="#F6DB8C"/></g>
<g class="p-far"><path d="M-20,214 L40,150 L86,190 L150,120 L214,186 L262,146 L330,200 L380,160 L430,206 L430,310 L-20,310Z" fill="{far}"/>{caps}</g>
<g class="mist p-mid" fill="{c.ivory}" opacity=".22"><ellipse cx="110" cy="200" rx="120" ry="9"/><ellipse cx="320" cy="212" rx="110" ry="8"/></g>
<path class="p-mid" d="M-20,246 L50,196 L120,236 L200,176 L276,232 L340,198 L430,250 L430,310 L-20,310Z" fill="{mid}"/>
<path class="p-near" d="M-20,300 L-20,262 Q60,230 120,248 Q200,270 260,226 Q330,204 430,170 L430,310Z" fill="{near}"/>
<g class="p-near"><path d="{ROAD}" fill="none" stroke="#D8CBA6" stroke-width="9" stroke-linecap="round" opacity=".35"/>
 <path class="draw road" d="{ROAD}" fill="none" stroke="{c.gold}" stroke-width="2.4" stroke-linecap="round" pathLength="1"/>
 <g class="actor scooter" data-path=".road" data-at=".46" data-tilt=".55"><g class="tap holdable"><g transform="scale(.33) translate(-174,-205)">{ride}</g><rect x="-50" y="-66" width="100" height="70" fill="transparent"/></g></g></g>
{cap(o.get("caption"), 388, 286, "end")}
''', label=o.get("label") or "Two people on a scooter on a winding mountain road")


# ------------------------------------------------------------------ hills: rolling country and a little train (also the fallback)
RAIL = "M-14,262 C60,236 110,262 176,246 S290,214 416,232"
TRAIN = '''<g>
 <path d="M-38,-4 h76" stroke="#2A2A3A" stroke-width="2" stroke-linecap="round"/>
 <rect x="-40" y="-21" width="23" height="16" rx="3.5" fill="#E8577E" stroke="#fff" stroke-width="1.6"/>
 <rect x="-14" y="-21" width="23" height="16" rx="3.5" fill="#F6B73C" stroke="#fff" stroke-width="1.6"/>
 <path d="M12,-5 v-16 h13 q12,2 14,16Z" fill="#5CC4B8" stroke="#fff" stroke-width="1.6"/>
 <g fill="#FFF6E5"><rect x="-36" y="-17" width="6" height="6" rx="1"/><rect x="-27" y="-17" width="6" height="6" rx="1"/><rect x="-10" y="-17" width="6" height="6" rx="1"/><rect x="-1" y="-17" width="6" height="6" rx="1"/><path d="M16,-17 h8 q6,1 8,7 h-16Z"/></g>
 <g fill="#2A2A3A"><circle cx="-34" cy="-3" r="3"/><circle cx="-23" cy="-3" r="3"/><circle cx="-8" cy="-3" r="3"/><circle cx="3" cy="-3" r="3"/><circle cx="18" cy="-3" r="3"/><circle cx="31" cy="-3" r="3"/></g>
 <rect x="-46" y="-40" width="92" height="46" fill="transparent"/>
</g>'''


def _tree(x, y, h, fill):
    return f'<path d="M{x},{y} q{-h * .22},{-h * .55} 0,{-h} q{h * .22},{h * .45} 0,{h}Z" fill="{fill}"/>'


def hills(o, c):
    st = o.get("sticker")
    return svg(f'''
<defs>{grad("g-" + c.uid, [(0, c.dark), (.55, c.mid), (.82, "#E3B95A")])}</defs>
<rect width="400" height="300" fill="url(#g-{c.uid})"/>
<g class="sunrise"><circle cx="112" cy="168" r="90" fill="url(#g-glow)"/><circle cx="112" cy="168" r="26" fill="#F6DB8C"/></g>
<g class="birds p-far" stroke="{c.ivory}" stroke-width="2" fill="none" stroke-linecap="round" opacity=".6"><path d="M250,96 q6,-6 10,0 q4,-6 10,0"/><path d="M286,116 q5,-5 8,0 q3,-5 8,0"/></g>
<path class="p-far" d="M-20,212 Q60,150 150,196 Q230,150 310,190 Q370,168 430,200 L430,310 L-20,310Z" fill="#7FB383"/>
<g class="mist p-mid" fill="{c.ivory}" opacity=".2"><ellipse cx="290" cy="206" rx="120" ry="8"/></g>
<g class="p-mid"><path d="M-20,250 Q70,196 170,232 Q260,190 430,238 L430,310 L-20,310Z" fill="#4E9160"/>
 {_tree(214, 216, 34, "#1F5A3A")}{_tree(228, 214, 26, "#1F5A3A")}{_tree(318, 220, 30, "#1F5A3A")}
 <g transform="translate(262,198)"><rect x="0" y="6" width="22" height="14" fill="#FFF3E3"/><path d="M-3,7 L11,-4 L25,7Z" fill="#E8577E"/><rect x="9" y="12" width="5" height="8" fill="#B7305C"/></g></g>
<path class="p-near" d="M-20,300 L-20,270 Q70,238 170,252 Q290,216 430,236 L430,310Z" fill="#2D6A3E"/>
<g class="p-near"><path d="{RAIL}" fill="none" stroke="#D8CBA6" stroke-width="7" stroke-linecap="round" opacity=".35"/>
 <path d="{RAIL}" fill="none" stroke="{c.gold}" stroke-width="5" stroke-dasharray="1.5 7" opacity=".7"/>
 <path class="draw road2" d="{RAIL}" fill="none" stroke="{c.gold}" stroke-width="1" stroke-linecap="round" pathLength="1" opacity=".8"/>
 <g class="actor train" data-path=".road2" data-at=".5" data-tilt=".8"><g class="tap holdable">{TRAIN}</g></g></g>
{nest(c.st(st), 20, 222, 60, cls="pop") if st else ""}
{cap(o.get("caption"), 388, 290, "end")}
''', label=o.get("label") or "A little train crossing rolling hills")


# ------------------------------------------------------------------ city: the skyline lights up at dusk
def skyline(seed, base, fill, cls, lo, hi, lit=True):
    r = random.Random(seed)
    x = -10; out = []; win = []
    while x < 410:
        w = r.choice([18, 22, 26, 30, 36]); h = r.uniform(lo, hi)
        out.append(f'<rect x="{x}" y="{base - h:.0f}" width="{w}" height="{h + 60:.0f}"/>')
        if lit:
            for wy in range(int(base - h) + 8, base - 6, 11):
                for wx in range(x + 5, x + w - 5, 8):
                    if r.random() < .38:
                        win.append(f'<rect class="win" x="{wx}" y="{wy}" width="3" height="4"/>')
        x += w + r.choice([0, 2, 5])
    return f'<g class="{cls}"><g fill="{fill}">{"".join(out)}</g><g fill="#F6DB8C">{"".join(win)}</g></g>'


OUTLINES = {
    # gold line drawings that draw themselves on the left of the skyline
    "spire": "M40,300 V246 H50 V214 H58 V184 H63 L68,128 L73,184 H78 V214 H86 V246 H96 V300",
    "tower": "M44,300 L60,214 H56 V204 H62 L67,150 L68,120 L69,150 L74,204 H80 V214 H76 L92,300 M52,258 H84 M57,232 H79",
    "dome": "M34,300 V236 H102 V300 M40,236 Q40,190 68,186 Q96,190 96,236 M68,186 V168 M62,168 H74",
    "columns": "M26,300 V292 H110 V300 M32,292 V236 M46,292 V236 M60,292 V236 M76,292 V236 M90,292 V236 M104,292 V236 M24,236 H112 M24,236 L68,208 L112,236",
    "bridge": "M10,300 V214 M70,300 V214 M130,300 V214 M10,214 Q40,262 70,214 Q100,262 130,214 M0,268 H140",
}


def city(o, c):
    st, outline = o.get("sticker", "temple"), OUTLINES.get(o.get("outline", "tower"))
    return svg(f'''
<defs>{grad("g-" + c.uid, [(0, "#1B1730"), (.5, "#7A2748"), (.8, "#E3A05A")])}</defs>
<rect width="400" height="300" fill="url(#g-{c.uid})"/>
{stars(22, 11, c.gold, h=110, cls="stars p-far")}
{skyline(5, 250, "#3E1B38", "p-far sky1", 40, 110, lit=False)}
{skyline(9, 262, "#22142B", "p-mid sky2", 30, 86)}
{f'<path class="draw" d="{outline}" fill="none" stroke="{c.gold}" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round" pathLength="1"/>' if outline else ""}
{f'<g class="rise">{nest(c.st(st), 252, 138, 110, cls="pop")}</g>' if st else ""}
<rect y="272" width="400" height="28" fill="#1A1226"/>
<g class="glint" stroke="{c.gold}" stroke-linecap="round" opacity=".6"><path d="M150,282 h60" stroke-width="1.6"/><path d="M240,290 h90" stroke-width="1.4"/><path d="M60,292 h40" stroke-width="1.2"/></g>
{wave(276, 3, 56, "#1A1226", "wv wv3", depth=40)}
<g transform="translate(330,70)"><g class="homeplane"><path d="M-14,4 L14,-6 L2,8 L0,2Z" fill="{c.ivory}"/><path d="M-22,10 q-12,6 -26,6" stroke="{c.ivory}" stroke-width="1.4" stroke-dasharray="2 5" fill="none" opacity=".7"/></g></g>
{cap(o.get("caption"))}
''', label=o.get("label") or "A city at dusk with the lights coming on")


TYPES = dict(flight=flight, island=island, beach=beach, palms=palms, mountain=mountain, hills=hills, city=city, lanterns=lanterns)
FALLBACK = "hills"


def make(kind, uid, opts=None, palette=None, romance=True):
    """Returns (svg, kind actually used). Unknown kinds fall back to FALLBACK so a build never fails on a scene."""
    used = kind if kind in TYPES else FALLBACK
    return TYPES[used](opts or {}, Ctx(uid, palette, romance)), used


def shared_defs(palette=None):
    g = dict(PALETTE, **(palette or {}))["gold"]
    return (f'<radialGradient id="g-glow"><stop offset="0" stop-color="{g}" stop-opacity=".55"/>'
            f'<stop offset="1" stop-color="{g}" stop-opacity="0"/></radialGradient>')
