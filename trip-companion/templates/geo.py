#!/usr/bin/env python3
"""Draws one small route map per flight or transfer as inline SVG.

Coastlines come from Natural Earth via the world-atlas npm package (public domain data, ISC package),
downloaded once from registry.npmjs.org into a cache folder. When that download is not possible the maps
still build: they fall back to a plain sea with the route arc, the two stops and their names.

    python3 geo.py --fetch [cache-dir]     download the world data now (build.py does this on its own)

build.py calls route_map(); nothing here knows about any particular trip.
Limits: routes that cross the antimeridian (180 degrees) use the plain fallback.
"""
import io, json, math, pathlib, sys, tarfile, urllib.request

REGISTRY = "https://registry.npmjs.org/world-atlas/2.0.2"
FILES = ("countries-110m.json", "countries-50m.json", "countries-10m.json")
PLANE = "M-11,0 L4,-2 L9,-9 L12,-9 L9,-2 L14,-1.5 L16,-5 L18,-5 L17,0 L18,5 L16,5 L14,1.5 L9,2 L12,9 L9,9 L4,2 Z"
HEART = "M0,6 C-11,-2 -7,-11 0,-5 C7,-11 11,-2 0,6Z"
PIN = "M0,7 C-9,-3 -6,-10 0,-10 C6,-10 9,-3 0,7Z"
BOAT = "M-15,-3 L11,-3 L18,0 L11,6 L-12,6 Z"
CABIN = "M-9,-3 L-6,-10 L5,-10 L8,-3 Z"
CAR = "M-14,5 V-2 Q-14,-8 -8,-8 H8 Q14,-8 14,-2 V5 Z"


def fetch(cache, timeout=25):
    """Make sure the three country files are in cache. Returns the folder, or None when they cannot be had."""
    cache = pathlib.Path(cache)
    if all((cache / f).exists() for f in FILES):
        return cache
    try:
        meta = json.loads(urllib.request.urlopen(REGISTRY, timeout=timeout).read())
        raw = urllib.request.urlopen(meta["dist"]["tarball"], timeout=timeout * 3).read()
        cache.mkdir(parents=True, exist_ok=True)
        with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as tar:
            for m in tar.getmembers():
                name = pathlib.PurePosixPath(m.name).name
                if name in FILES and m.isfile():
                    (cache / name).write_bytes(tar.extractfile(m).read())
        return cache if all((cache / f).exists() for f in FILES) else None
    except Exception as e:                                  # offline, proxy, registry down: the caller falls back
        print("  maps: world data not available (" + str(e)[:80] + "); drawing plain maps", file=sys.stderr)
        return None


_cache = {}


def load(path):
    """topojson countries -> {name: [polygon -> [ring -> [(lon, lat)]]]}"""
    path = str(path)
    if path in _cache:
        return _cache[path]
    t = json.loads(pathlib.Path(path).read_text())
    sx, sy = t["transform"]["scale"]; tx, ty = t["transform"]["translate"]
    arcs = []
    for a in t["arcs"]:
        x = y = 0; pts = []
        for dx, dy in a:
            x += dx; y += dy
            pts.append((x * sx + tx, y * sy + ty))
        arcs.append(pts)

    def ring(idx):
        pts = []
        for i in idx:
            a = arcs[i] if i >= 0 else arcs[~i][::-1]
            pts.extend(a if not pts else a[1:])
        return pts
    out = {}
    for g in t["objects"]["countries"]["geometries"]:
        polys = [g["arcs"]] if g["type"] == "Polygon" else g["arcs"] if g["type"] == "MultiPolygon" else []
        out.setdefault(g.get("properties", {}).get("name", g.get("id")), []).extend([[ring(r) for r in p] for p in polys])
    _cache[path] = out
    return out


class Proj:
    """Equirectangular, scaled for the middle latitude of the box."""
    def __init__(self, lon0, lon1, lat0, lat1, width):
        self.lon0, self.lat1 = lon0, lat1
        self.k = math.cos(math.radians((lat0 + lat1) / 2))
        self.s = width / ((lon1 - lon0) * self.k)
        self.w = width; self.h = (lat1 - lat0) * self.s
        self.box = (lon0, lon1, lat0, lat1)

    def __call__(self, lon, lat):
        return ((lon - self.lon0) * self.k * self.s, (self.lat1 - lat) * self.s)


def path(polys, P, minarea=0.0, step=0.8):
    lon0, lon1, lat0, lat1 = P.box
    d = []
    for poly in polys:
        r = poly[0]                                         # outer ring only
        xs = [p[0] for p in r]; ys = [p[1] for p in r]
        if max(xs) < lon0 - 2 or min(xs) > lon1 + 2 or max(ys) < lat0 - 2 or min(ys) > lat1 + 2:
            continue
        pts = []; last = None
        for lon, lat in r:
            x, y = P(lon, lat)
            if last and abs(x - last[0]) < step and abs(y - last[1]) < step:
                continue
            pts.append((x, y)); last = (x, y)
        if len(pts) < 3:
            continue
        area = abs(sum(pts[i][0] * pts[i - 1][1] - pts[i - 1][0] * pts[i][1] for i in range(len(pts)))) / 2
        if area < minarea:
            continue
        d.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + "Z")
    return "".join(d)


def inside(lon, lat, ring):
    hit = False
    j = len(ring) - 1
    for i in range(len(ring)):
        (xi, yi), (xj, yj) = ring[i], ring[j]
        if (yi > lat) != (yj > lat) and lon < (xj - xi) * (lat - yi) / (yj - yi) + xi:
            hit = not hit
        j = i
    return hit


def country_at(C, lon, lat):
    for name, polys in C.items():
        if any(inside(lon, lat, p[0]) for p in polys):
            return name
    best, bd = None, 0.6                                    # coastal airports often sit just off a coarse outline
    for name, polys in C.items():
        for p in polys:
            for x, y in p[0]:
                d = math.hypot(x - lon, y - lat)
                if d < bd:
                    best, bd = name, d
    return best


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def route_map(key, a, b, kind="flight", world=None, home=None, hearts=True, width=600, aspect=None, note=""):
    """One leg. a and b are (lon, lat, name). kind: flight | boat | land.
    world: folder with the world-atlas files, or None for the plain fallback.
    home: "a" or "b" when that end is where the travellers live (its country is tinted differently).
    hearts: heart-shaped stop markers (couples) or neutral pins.  note: small italic text, e.g. "40 min".
    """
    (ax, ay, an), (bx, by, bn) = a, b
    if abs(ax - bx) > 180:
        world = None
        if ax < bx: ax += 360
        else: bx += 360
    span = max(abs(ax - bx) * math.cos(math.radians((ay + by) / 2)), abs(ay - by), 0.02)
    pad = max(span * (0.16 if kind == "flight" else 0.4), 0.03)
    aspect = aspect or (2.0 if span > 35 else 1.5 if kind == "flight" else 1.2)
    lon0, lon1 = min(ax, bx) - pad, max(ax, bx) + pad
    lat0, lat1 = max(-85, min(ay, by) - pad), min(85, max(ay, by) + pad)
    k = math.cos(math.radians((lat0 + lat1) / 2))
    wdeg, hdeg = (lon1 - lon0) * k, lat1 - lat0
    if wdeg / hdeg < aspect:
        grow = (hdeg * aspect - wdeg) / k / 2; lon0 -= grow; lon1 += grow
    else:
        grow = (wdeg / aspect - hdeg) / 2; lat0 -= grow; lat1 += grow
    P = Proj(lon0, lon1, lat0, lat1, width)
    w, h = P.w, P.h
    pa, pb = P(ax, ay), P(bx, by)

    land = ""
    if world:
        res = "110m" if span > 35 else "50m" if span > 5 else "10m"
        C = load(pathlib.Path(world) / f"countries-{res}.json")
        ca, cb = country_at(C, a[0], a[1]), country_at(C, b[0], b[1])
        tint = {}
        if cb: tint[cb] = "m-home" if home == "b" else "m-dest"
        if ca and ca not in tint: tint[ca] = "m-home" if home == "a" else "m-dest"
        if home == "a" and ca == cb and ca: tint[ca] = "m-dest"
        fine = dict(minarea=0.4, step=0.5)
        rest = "".join(path(v, P, 1.5, 1.0) for n, v in C.items() if n not in tint)
        land = f'<path class="m-land" d="{rest}"/>' + "".join(f'<path class="{cls}" d="{path(C[n], P, **fine)}"/>' for n, cls in tint.items())
    else:
        grid = "".join(f'<path d="M0,{h * i / 5:.0f} H{w:.0f}"/>' for i in range(1, 5)) + "".join(f'<path d="M{w * i / 6:.0f},0 V{h:.0f}"/>' for i in range(1, 6))
        land = f'<g class="m-grid">{grid}</g>'

    dx, dy = pb[0] - pa[0], pb[1] - pa[1]
    if kind == "flight":
        bend = 0.2
        c1 = ((pa[0] + pb[0]) / 2 - dy * bend, (pa[1] + pb[1]) / 2 + dx * bend)
        c2 = ((pa[0] + pb[0]) / 2 + dy * bend, (pa[1] + pb[1]) / 2 - dx * bend)
        c = c1 if c1[1] < c2[1] else c2                     # always bulge towards the top of the map
        d = f"M{pa[0]:.1f},{pa[1]:.1f}Q{c[0]:.1f},{c[1]:.1f} {pb[0]:.1f},{pb[1]:.1f}"
        mover = (f'<g class="m-plane"><path d="{PLANE}" transform="rotate(180) scale(1.7)"/>'
                 f'<animateMotion dur="7s" repeatCount="indefinite" rotate="auto"><mpath href="#arc-{key}"/></animateMotion></g>')
        line = f'<path class="m-route" id="arc-{key}" d="{d}"/>'
    else:
        bend = 0.28 if kind == "boat" else 0.12
        n = (-dy * bend, dx * bend)
        if n[0] < 0: n = (-n[0], -n[1])                     # bulge to the right, clear of the labels on the left
        k1 = (pa[0] + dx * .25 + n[0], pa[1] + dy * .25 + n[1]); k2 = (pa[0] + dx * .75 + n[0], pa[1] + dy * .75 + n[1])
        d = f"M{pa[0]:.1f},{pa[1]:.1f}C{k1[0]:.1f},{k1[1]:.1f} {k2[0]:.1f},{k2[1]:.1f} {pb[0]:.1f},{pb[1]:.1f}"
        face = "scale(1.6)" if dx >= 0 else "scale(-1.6,1.6)"
        body = (f'<path class="hull" d="{BOAT}"/><path class="cabin" d="{CABIN}"/><path class="wake" d="M-18,2 q-6,-3 -12,0 M-18,6 q-6,-3 -12,0"/>'
                if kind == "boat" else f'<path class="hull" d="{CAR}"/><path class="cabin" d="M-9,-5 h18 v4 h-18Z"/>')
        mover = (f'<g class="m-ship"><g transform="{face}">{body}</g>'
                 f'<animateMotion dur="6s" repeatCount="indefinite" rotate="0"><mpath href="#arc-{key}"/></animateMotion></g>')
        line = f'<path class="m-boat" id="arc-{key}" d="{d}"/>'

    mark = HEART if hearts else PIN

    def stop(pt, name, other):
        side = 1 if pt[0] < w * 0.55 else -1
        if kind != "flight": side = -1 if pt[0] > w * 0.3 else 1
        ddy = 0
        if abs(pt[1] - other[1]) < 30 and abs(pt[0] - other[0]) < 200: ddy = 22 if pt[1] >= other[1] else -22
        ty = min(h - 8, max(22, pt[1] + 7 + ddy))
        return (f'<path class="m-stop" transform="translate({pt[0]:.1f},{pt[1]:.1f}) scale(1.7)" d="{mark}"/>'
                f'<text class="m-lbl" x="{pt[0] + 16 * side:.1f}" y="{ty:.1f}" text-anchor="{"start" if side > 0 else "end"}">{esc(name)}</text>')
    extra = f'<text class="m-hand" x="{min(w - 60, max(pa[0], pb[0]) + 70):.0f}" y="{(pa[1] + pb[1]) / 2:.0f}" text-anchor="middle">{esc(note)}</text>' if note else ""
    what = {"flight": "flight", "boat": "boat"}.get(kind, "route")
    return (f'<svg class="map legmap" viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="Map of the {what} from {esc(an)} to {esc(bn)}">'
            f'<rect class="m-sea" width="{w:.0f}" height="{h:.0f}"/>{land}{line}{mover}{stop(pa, an, pb)}{stop(pb, bn, pa)}{extra}</svg>')


if __name__ == "__main__":
    if "--fetch" in sys.argv:
        rest = [a for a in sys.argv[1:] if a != "--fetch"]
        got = fetch(rest[0] if rest else pathlib.Path(__file__).parent / ".cache" / "world-atlas")
        print("world data:", got or "not available")
    else:
        print(__doc__)
