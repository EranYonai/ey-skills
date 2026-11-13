# Scenes, stickers and maps

Everything drawn on the page is inline SVG written by hand in Python: no image files, no icon fonts. Motion is
GSAP with ScrollTrigger (scroll-scrubbed scenes and maps) plus the Web Animations API (taps, confetti). The fun
is in motion and small reactions. **No games**: no bingo, dares, spinners, scores or streaks.

## Scenes

Each chapter opens on a 400 x 300 illustrated scene. As it scrolls through the screen its layers drift at
different speeds, a line draws itself, and a traveller moves along it. Choose the type with the travellers, per
chapter:

```python
scene="beach"                                              # short form
scene=dict(type="city", sticker="tram", outline="bridge", caption="Sunset about 20:35")
```

| type | what it shows | what moves on scroll | options |
|---|---|---|---|
| `flight` | night sky over the curve of the earth, a dashed arc between two airport codes | the arc draws, the plane flies it | `frm`, `to` (labels at each end) |
| `island` | sea, an island with palms, a small boat, a mascot sticker on the sand | waves slide, the boat crosses, the mascot pops up | `mascot` (sticker, default `pineapple`), `extra` (small second sticker), `caption` |
| `beach` | sun over the sea, birds, a sticker on the sand | the sun sets, dusk falls, stars come out | `sticker` (default `coconut`), `caption` |
| `palms` | two palms and a hammock | the hammock swings, flowers fall | `falling` (sticker, default `hibiscus`), `caption` |
| `mountain` | ranges, mist, a winding road, a scooter | the sun rises, the road draws, the scooter rides it with turning wheels | `snow=True` for snowy peaks, `caption` |
| `hills` | rolling green country, a railway, a little train | the sun rises, the train crosses | `sticker` (optional), `caption` |
| `city` | a skyline at dusk and a gold line-drawn landmark | the skyline rises, windows light up at random, the landmark draws, a plane passes | `outline` (`spire`, `tower`, `dome`, `columns`, `bridge`), `sticker` (default `temple`), `caption` |
| `lanterns` | full moon over water, rising lanterns, floating candles | the moon rises, lanterns drift up | used for a single evening; also the moon secret's night |

Every type also takes `label`, the description read by screen readers.

- An unknown type falls back to `hills` and the build prints a warning.
- A single day can carry its own small scene: `dict(date=..., scene="lanterns", scene_caption="Moon over the bay")`.
- Scenes take their sky, sea and line colours from the theme (`@scene` in the theme file), so they match any look.
- With `romance=False` the couple-only details (elements with class `rom`, such as a heart on the plane's tail)
  are removed.
- Under "reduce motion" the scenes are still and complete; nothing depends on animation to be readable.

Which secrets a scene can host: `hold` needs a traveller to press (`flight`, `island`, `mountain`, `hills`);
`mascot` needs a sticker (`island`, `beach`, `city`, or `hills` with `sticker`).

## Stickers

Flat, friendly drawings with thick shapes and a face where it fits. Every sticker wiggles and throws hearts or
stars when tapped; the sun spins.

`sun, pineapple, coconut, hibiscus, palm, plane, temple, sunglasses, suitcase, camera, tram, cactus, peak`

Places on the page (`TRIP["stickers"]`): `hero` (top panel on Today), `wallet`, `lists`, `notes`, `handy`
(view headings), `footer`. Scenes take stickers through their options.

## Route maps

One small map per flight and per transfer whose two places have `lat`/`lon`. Real coastlines, the destination
country tinted, home tinted differently, a dashed arc for a flight and a solid line for a boat or land leg, and a
plane, boat or car that travels the route as the map scrolls by. Stops are hearts with romance on, pins otherwise.

- Coastline data is Natural Earth through the `world-atlas` package, downloaded once from `registry.npmjs.org`
  into `.cache/world-atlas` beside the trip file. No trip data is sent; the request only fetches the package.
- Offline, or with `--offline`, maps still build: plain sea, the route, the two stops and their names.
- The map picks its own scale and detail from the distance. Routes across the 180 degree meridian use the plain form.
- `python3 templates/geo.py --fetch <dir>` downloads the data ahead of time.

## Drawing a new scene

When no type fits the destination, add one in `templates/scenes.py` instead of forcing a wrong one.

1. Write `def name(o, c)` returning `svg(body, label=...)`. `o` is the options dict, `c` carries the palette
   (`c.deep, c.dark, c.mid, c.gold, c.gold2, c.ivory`), `c.uid` (unique id suffix for gradients) and `c.st(name)`
   (a sticker, already stripped for romance). Register it in `TYPES`.
2. Canvas is `0 0 400 300`. Draw wider than the frame (from about -20 to 430) because layers move sideways.
3. Use the classes the scroll script already animates, and it moves without new JavaScript:

   | class | effect |
   |---|---|
   | `p-far`, `p-mid`, `p-near` | parallax layers, slow to fast |
   | `wv1`, `wv2`, `wv3` | waves sliding sideways (make them with `wave()`) |
   | `draw` on a path with `pathLength="1"` | the line draws itself |
   | `actor` with `data-path=".cls"` | follows that path, turning with it (`data-tilt` scales the turn) |
   | `actor-x` with `data-from`, `data-to`, `data-y` | slides horizontally |
   | `pop` | pops up with a bounce; the first one is the mascot for the `mascot` secret |
   | `tap` | wiggles and bursts when tapped; `tap holdable` marks the traveller for the `hold` secret |
   | `rom` on a self-closing element | removed when romance is off |

   Type-specific motion (a setting sun, lighting windows) is keyed on the scene type in `initMotion()` in
   `template.html`; add a short block there only if the generic classes are not enough.
4. Helpers: `nest()` places a sticker, `centred()` centres one on an actor, `wave()`, `stars()`, `grad()`, `cap()`.
5. Style: flat fills, two or three depth layers, gold line accents from `c.gold`, no outlines, no text except the
   caption. Keep one scene under about 8 KB.
6. Build the example with the new type and scroll it slowly at phone width: nothing may leave a gap at the
   frame's edge at either end of the scroll.

## Drawing a new sticker

Add a constant in `templates/art.py` (`<svg class="sticker" viewBox="0 0 W H" aria-hidden="true">`) and its name
to `NAMES`. Match the others: about 120 to 170 units wide, rounded shapes, the shared ink colour for faces, a
white highlight, one or two flat shadows. Give couple-only parts the class `rom`. Original drawings only: no
logos, characters or anything traced.
