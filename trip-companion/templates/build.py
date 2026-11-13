#!/usr/bin/env python3
"""Builds a trip companion page: one self-contained HTML file.

    python3 build.py path/to/trip.py                 -> path/to/dist/index.html
    python3 build.py trip.py --theme night           try another look without editing the trip file
    python3 build.py trip.py --out some/dir          write index.html (and seed.json) somewhere else
    python3 build.py trip.py --offline               never download map data; draw plain route maps
    python3 build.py trip.py --local-gsap DIR        local testing only: load GSAP from copies in DIR, not the CDN,
                                                     and add the viewport tag the published page gets from its wrapper
    python3 build.py --themes                        list the themes

Everything about the trip lives in the trip file (see references/data-schema.md and examples/). The page itself
is template.html, drawings are art.py and scenes.py, route maps geo.py, looks themes/*.css.
Tickets and vouchers: put PDFs or JPG/PNG files in a docs/ folder next to the trip file; page 1 of each PDF is
rendered with pdftoppm and embedded. Also writes SECRETS.md next to the trip file: private, for the builder only.

Python 3.9+ standard library only. pdftoppm (poppler-utils) is needed only when there are PDFs.
"""
import base64, datetime as dt, hashlib, importlib.util, json, pathlib, re, shutil, subprocess, sys
from urllib.parse import quote_plus

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True
import art, geo, scenes  # noqa: E402

WD = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MO = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
HEART = "M12 21 C-6 9 3 -3 12 6 C21 -3 30 9 12 21Z"
SPARK = "M12 1 C13 8 16 11 23 12 C16 13 13 16 12 23 C11 16 8 13 1 12 C8 11 11 8 12 1Z"
STICKER_DEFAULTS = dict(hero="sun", wallet="plane", lists="suitcase", notes="hibiscus", handy="camera", footer="hibiscus")
warnings, open_items = [], []


class TripError(Exception):
    pass


def need(cond, msg):
    if not cond:
        raise TripError(msg)


def warn(msg):
    warnings.append(msg)


# ---------------------------------------------------------------- small helpers
def maps_url(q):
    return "https://www.google.com/maps/search/?api=1&query=" + quote_plus(q)


def day(s, what):
    try:
        return dt.date.fromisoformat(s)
    except Exception:
        raise TripError(f"{what}: {s!r} is not a full ISO date like 2027-06-05")


def label(iso):                                             # "2027-06-05" -> "Sat 5 Jun"
    d = dt.date.fromisoformat(iso)
    return f"{WD[d.weekday()]} {d.day} {MO[d.month - 1]}"


def offset_hours(tz, when):
    """UTC offset of a zone at a local wall time. tz is an IANA name ("Europe/Athens") or a number of hours."""
    if isinstance(tz, (int, float)):
        return float(tz)
    try:
        from zoneinfo import ZoneInfo
        return when.replace(tzinfo=ZoneInfo(tz)).utcoffset().total_seconds() / 3600
    except Exception as e:
        raise TripError(f"Time zone {tz!r} could not be loaded ({e}). Use a number of hours ahead of UTC instead, e.g. tz=3 "
                        f"(check it is right for the trip dates, daylight saving included).")


def utc(day_iso, hhmm, tz):                                 # local wall time -> UTC ISO string
    need(re.fullmatch(r"\d\d:\d\d", hhmm or ""), f"Time {hhmm!r} on {day_iso} must look like 08:10")
    t = dt.datetime.fromisoformat(f"{day_iso}T{hhmm}:00")
    return (t - dt.timedelta(hours=offset_hours(tz, t))).strftime("%Y-%m-%dT%H:%M:%SZ")


def dur(a, b):
    m = int((dt.datetime.fromisoformat(b[:-1]) - dt.datetime.fromisoformat(a[:-1])).total_seconds() // 60)
    return (f"{m // 60}h {m % 60:02d}m" if m >= 60 else f"{m}m") if m > 0 else ""


def scramble(text, key):
    """Hides text from a casual look at the page source. Obfuscation, not encryption. Mirrors scramble() in template.html."""
    k = key.encode()
    return base64.b64encode(bytes(b ^ k[i % len(k)] ^ 0x5A for i, b in enumerate(text.encode()))).decode()[::-1]


def hid(prefix, *parts):                                    # stable id from the words, never from the position
    return prefix + hashlib.md5("|".join(parts).encode()).hexdigest()[:8]


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "trip"


def join_names(names):
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " & " + names[-1]


def load_trip(path):
    spec = importlib.util.spec_from_file_location("trip_data", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    known = {"TRIP", "TRAVELLERS", "PLACES", "FLIGHTS", "STAYS", "TRANSFERS", "CHAPTERS", "TODOS", "PACKING", "CONTACTS", "TAXI",
             "PHRASES", "PHRASES_NOTE", "FX", "TIPS", "LETTERS", "SECRETS", "SEED_PATCHES"}
    for name in dir(mod):
        if name.isupper() and name not in known:
            warn(f"{name} in the trip file is not something the build reads (typo?)")
    need(hasattr(mod, "TRIP") and hasattr(mod, "CHAPTERS") and hasattr(mod, "TRAVELLERS"), "The trip file needs at least TRIP, TRAVELLERS and CHAPTERS")
    return mod


def theme_info(name):
    p = HERE / "themes" / f"{name}.css"
    need(p.exists(), f"Unknown theme {name!r}. Have: " + ", ".join(sorted(x.stem for x in (HERE / 'themes').glob('*.css'))))
    css = p.read_text()
    meta = dict(re.findall(r"@(\w+):\s*(.+?)\s*(?:\n|\*/)", css))
    pal = dict(kv.split("=") for kv in meta.get("scene", "").split()) if meta.get("scene") else {}
    return dict(name=meta.get("name", name), fonts=meta.get("fonts", ""), mood=meta.get("mood", ""), palette=pal, css=css,
                confetti=meta.get("confetti", "").split())


# ---------------------------------------------------------------- the data the page reads
def build_data(T, theme, docs):
    trip = dict(T.TRIP)
    people = list(T.TRAVELLERS)
    need(people and all(isinstance(p, str) and p for p in people), "TRAVELLERS must be a list of first names")
    romance = bool(trip.get("romance", False))
    if romance and len(people) != 2:
        warn("romance is on but there are not exactly two travellers; the couple wording assumes two")
    need(trip.get("tz") is not None, 'TRIP needs tz: the destination time zone, e.g. tz="Europe/Athens" or tz=3')
    tz, home_tz = trip["tz"], trip.get("home_tz", trip["tz"])
    places = getattr(T, "PLACES", {})
    g = lambda name, default: getattr(T, name, default)

    def place(key, what):
        need(key in places, f"{what}: place {key!r} is not in PLACES")
        return places[key]

    def doc(name, what):
        if not name:
            return None
        stem = re.sub(r"\.(pdf|jpe?g|png)$", "", name, flags=re.I)
        if stem not in docs:
            warn(f"{what}: document {name!r} is not in the docs folder; its button is left out")
            return None
        return stem

    def missing(what, d, fields):
        for f in fields:
            if not d.get(f):
                open_items.append(f"{what}: no {f}")

    # ---- days and chapters first: everything else hangs off the calendar
    chapters, days, n, seen = [], [], 0, set()
    wish = {}
    flights_src, stays_src, moves_src = g("FLIGHTS", {}), g("STAYS", {}), g("TRANSFERS", {})
    for ci, ch in enumerate(T.CHAPTERS):
        cid = ch.get("id") or slug(ch["name"])
        need(cid not in seen, f"Two chapters share the id {cid!r}"); seen.add(cid)
        need(ch.get("days"), f"Chapter {ch['name']!r} has no days")
        c = dict(id=cid, name=ch["name"], place=ch.get("place", ""), wx=ch.get("weather", ""), days=[], col=ci % 6,
                 food=[dict(n=a, d=b, map=maps_url(q)) for a, b, q in ch.get("food", [])])
        for d in ch["days"]:
            iso = day(d["date"], f"Chapter {ch['name']}").isoformat()
            need(not days or iso > days[-1]["iso"], f"Day {iso} is out of order or repeated")
            need(not days or (dt.date.fromisoformat(iso) - dt.date.fromisoformat(days[-1]["iso"])).days == 1,
                 f"There is no day entry between {days[-1]['iso'] if days else ''} and {iso}; every date of the trip needs one (it can be empty)")
            n += 1
            out = []
            for it in d.get("items", []):
                k = it[0]
                if k == "flight":
                    need(it[1] in flights_src, f"{iso}: flight {it[1]!r} is not in FLIGHTS"); out.append(dict(k=k, id=it[1]))
                elif k in ("stay", "hotel"):
                    need(it[1] in stays_src, f"{iso}: stay {it[1]!r} is not in STAYS"); out.append(dict(k="hotel", id=it[1]))
                elif k in ("transfer", "boat"):
                    need(it[1] in moves_src, f"{iso}: transfer {it[1]!r} is not in TRANSFERS"); out.append(dict(k="boat", id=it[1]))
                elif k == "step":
                    need(len(it) == 3, f"{iso}: a step is (\"step\", \"HH:MM\", text)"); out.append(dict(k=k, t=it[1], x=it[2]))
                elif k == "todo":
                    out.append(dict(k=k, x=it[1], url=it[2] if len(it) > 2 else "", link=it[3] if len(it) > 3 else ""))
                elif k == "pick":                           # ("pick", text, map search, short name, whose)
                    need(len(it) >= 4, f"{iso}: a pick is (\"pick\", text, map search, short name[, whose])")
                    by = it[4] if len(it) > 4 else ""
                    need(not by or by in people, f"{iso}: pick by {by!r}, who is not in TRAVELLERS")
                    out.append(dict(k=k, x=it[1], map=maps_url(it[2]), by=by))
                    wish[hid("w", it[3])] = dict(name=it[3], note=it[1], map=maps_url(it[2]), day=iso, by=by, pick=True, done=False, o=len(wish))
                elif k in ("idea", "note"):
                    out.append(dict(k=k, x=it[1]))
                else:
                    raise TripError(f"{iso}: unknown item kind {k!r}")
            dd = dt.date.fromisoformat(iso)
            rec = dict(iso=iso, label=label(iso), wd=WD[dd.weekday()], dd=dd.day, mon=MO[dd.month - 1], title=d.get("title", ""), n=n, ch=cid, items=out)
            if d.get("scene"):
                rec["scene"] = dict(id=f"day-{iso}", kind=d["scene"], caption=d.get("scene_caption", ""))
            days.append(rec); c["days"].append(iso)
        a, b = c["days"][0], c["days"][-1]
        c["span"] = label(a) if a == b else f"{label(a).split(' ', 1)[1]} to {label(b).split(' ', 1)[1]}"
        sc = ch.get("scene", scenes.FALLBACK)
        c["_scene"] = dict(type=sc) if isinstance(sc, str) else dict(sc)
        chapters.append(c)
    first, last = days[0]["iso"], days[-1]["iso"]
    day_ch = {d["iso"]: d["ch"] for d in days}

    # ---- flights
    flights, zones = {}, []
    for key, f in flights_src.items():
        a, b = place(f["frm"], f"Flight {key}"), place(f["to"], f"Flight {key}")
        d0 = day(f["date"], f"Flight {key}").isoformat()
        d1 = day(f.get("arr_date", d0), f"Flight {key}").isoformat()
        dep, arr = utc(d0, f["dep"], a.get("tz", tz)), utc(d1, f["arr"], b.get("tz", tz))
        need(arr > dep, f"Flight {key} lands before it takes off; check dates, times and the places' time zones")
        diff = (dt.date.fromisoformat(d1) - dt.date.fromisoformat(d0)).days
        pax = []
        for p in f.get("pax", [dict(who=w) for w in people]):
            need(p["who"] in people, f"Flight {key}: passenger {p['who']!r} is not in TRAVELLERS")
            pax.append(dict(who=p["who"], tkt=p.get("ticket", ""), seat=p.get("seat", ""), doc=doc(p.get("doc"), f"Flight {key}")))
        flights[key] = dict(key=key, airline=f.get("airline", ""), num=f.get("num", key), frm=a.get("code", f["frm"]), to=b.get("code", f["to"]),
                            frm_city=a["name"], to_city=b["name"], frm_ap=f.get("frm_ap", a["name"]), to_ap=f.get("to_ap", b["name"]),
                            dep=f["dep"], arr=f["arr"], arr_note=(f"{diff:+d} day" + ("s" if abs(diff) > 1 else "")) if diff else "",
                            dur=f.get("dur") or dur(dep, arr), date=label(d0), iso=d0, arrIso=d1, ref=f.get("ref", ""), bag=f.get("bag", ""),
                            depUtc=dep, arrUtc=arr, pax=pax)
        missing(f"Flight {key}", f, ["ref"])
        zones.append((dep, b.get("tz", tz)))

    # ---- stays
    taxi = [dict(en=t[0], local=t[1], sub=t[2] if len(t) > 2 else "", ph=t[3] if len(t) > 3 else "") for t in g("TAXI", [])]
    hotels = {}
    for key, h in stays_src.items():
        i, o = day(h["check_in"], f"Stay {key}"), day(h["check_out"], f"Stay {key}")
        need(o > i, f"Stay {key}: check-out is not after check-in")
        m = re.search(r"(\d\d:\d\d)", h.get("cin", ""))
        hotels[key] = dict(key=key, name=h["name"], short=h.get("short", h["name"]), place=h.get("place", ""), addr=h.get("addr", ""), phone=h.get("phone", ""),
                           room=h.get("room", ""), board=h.get("board", ""), nights=(o - i).days, inn=label(i.isoformat()), out=label(o.isoformat()),
                           inIso=i.isoformat(), outIso=o.isoformat(), cin=h.get("cin", ""), cout=h.get("cout", ""), ref=h.get("ref", ""),
                           doc=doc(h.get("doc"), f"Stay {key}"), note=h.get("note", ""), map=maps_url(h.get("map") or h["name"] + " " + h.get("place", "")),
                           cinUtc=utc(i.isoformat(), m.group(1) if m else "15:00", h.get("tz", tz)), cinExact=bool(m),
                           taxi=next((ti for ti, t in enumerate(taxi) if t["ph"] and t["ph"] == h.get("phone")), None))
        missing(f"Stay {h['name']}", h, ["ref", "phone"])

    # ---- transfers: boats, trains, buses, cars
    boats = {}
    VERB = dict(boat="Boat", ferry="Ferry", train="Train", bus="Bus", car="Car", walk="Walk")
    for key, b in moves_src.items():
        d0 = day(b["date"], f"Transfer {key}").isoformat()
        pa, pb = places.get(b["frm"]), places.get(b["to"])
        dep, arr = utc(d0, b["dep"], (pa or {}).get("tz", tz)), utc(d0, b["arr"], (pb or {}).get("tz", tz))
        kind = b.get("kind", "boat")
        boats[key] = dict(key=key, kind=kind, verb=b.get("verb") or VERB.get(kind, "Transfer"), operator=b.get("operator", ""), service=b.get("service", ""),
                          frm=(pa or {}).get("name", b["frm"]), to=(pb or {}).get("name", b["to"]), frm_ap=b.get("frm_ap", ""), to_ap=b.get("to_ap", ""),
                          date=label(d0), iso=d0, dep=b["dep"], arr=b["arr"], dur=b.get("dur") or dur(dep, arr), ref=b.get("ref", ""), note=b.get("note", ""),
                          doc=doc(b.get("doc"), f"Transfer {key}"), depUtc=dep, arrUtc=arr, _a=pa, _b=pb)
        missing(f"Transfer {key}", b, ["ref"])
        if pb and pb.get("tz") is not None:
            zones.append((dep, pb["tz"]))

    # ---- nights, drawn to scale on Today
    nights = []
    d = dt.date.fromisoformat(first)
    while d.isoformat() < last:
        iso = d.isoformat()
        h = next((x for x in hotels.values() if x["inIso"] <= iso < x["outIso"]), None)
        ch = day_ch.get(iso, chapters[0]["id"])
        lab = h["short"] if h else "On the way"
        if nights and nights[-1]["label"] == lab:
            nights[-1]["n"] += 1
        else:
            nights.append(dict(ch=ch, label=lab, n=1, col=next(c["col"] for c in chapters if c["id"] == ch), away=not h))
        d += dt.timedelta(days=1)

    # ---- letters: written before the trip, sealed until their day
    letters = []
    for i, L in enumerate(g("LETTERS", [])):
        frm, to = L.get("frm") or trip["title"], L.get("to", "all")
        need(to == "all" or to in people, f"Letter {i + 1}: to {to!r} is not a traveller or \"all\"")
        on = day(L["on"], f"Letter {i + 1}").isoformat()
        letters.append(dict(id=f"L{i}-{on}", **{"from": frm}, to=to, on=on, title=L.get("title", ""), body=scramble(L["text"], frm.lower() + on)))

    # ---- what the shared lists start with. Ids come from the words, so seeding twice is harmless.
    seeds = dict(todos={}, packing={}, wishlist=wish)
    alerts = []
    for i, t in enumerate(g("TODOS", [])):
        tid = t.get("id") or hid("t", t["text"])
        row = dict(text=t["text"], sub=t.get("sub", ""), done=False, o=i)
        if t.get("url"):
            row.update(url=t["url"], link=t.get("link") or re.sub(r"^https?://", "", t["url"]).rstrip("/"))
        seeds["todos"][tid] = row
        if t.get("opens"):
            alerts.append(dict(id=tid, opens=day(t["opens"], "Todo").isoformat(), until=day(t.get("until", last), "Todo").isoformat(), title=t.get("now_title", t["text"]),
                               body=t.get("now_body", t.get("sub", "")), url=t.get("url", ""), link=row.get("link", ""), done=t.get("done_label", "Done")))
    o = 0
    for grp, items in g("PACKING", []):
        for text in items:
            seeds["packing"][hid("p", grp, text)] = dict(text=text, g=grp, done=False, o=o); o += 1

    # ---- phrases, money
    phrases = [dict(en=p[0], local=p[1], ro=p[2] if len(p) > 2 else "") for p in g("PHRASES", [])]
    fx = None
    if g("FX", None):
        F = T.FX
        need(F.get("rate"), "FX needs a rate")
        steps = F.get("steps") or ([1, 2, 5, 10, 20, 50, 100, 200, 500] if F["rate"] > 0.2 else [10, 20, 50, 100, 200, 500, 1000, 2000, 5000])
        fx = dict(rate=F["rate"], asof=F.get("asof", ""), fn=F["from_name"], fs=F.get("from_symbol", ""), tn=F["to_name"], ts=F.get("to_symbol", ""),
                  rule=F.get("rule", ""), steps=steps, start=F.get("start", steps[4]))

    # ---- secrets: which are on, and whether the page has what each one needs
    heading = trip.get("heading") or join_names(people)
    S = {k: dict(v) for k, v in g("SECRETS", {}).items()}
    for k in S:
        need(k in SECRET_DEFAULTS, f"SECRETS: unknown secret {k!r}. Known: " + ", ".join(SECRET_DEFAULTS))
    on = lambda k: bool(S.get(k, {}).get("on"))
    eggs, cfg, sheet = {}, {}, []
    by_id = {c["id"]: c for c in chapters}

    def text_of(k):
        dflt = SECRET_DEFAULTS[k][0 if romance else 1]
        return S[k].get("title", dflt[0]), S[k].get("text", dflt[1])

    def scene_target(k, marker, what):
        cid = S[k].get("chapter")
        cands = [c for c in chapters if marker(c)]
        if cid:
            need(cid in by_id, f"SECRETS.{k}: chapter {cid!r} does not exist")
            if not marker(by_id[cid]):
                warn(f"SECRETS.{k}: the scene of chapter {cid!r} has no {what}; this secret is off"); return None
            return by_id[cid]
        if not cands:
            warn(f"SECRETS.{k}: no chapter scene has a {what}; this secret is off")
        return cands[0] if cands else None

    for c in chapters:                                      # draw the scenes now: secrets need to know what is in them
        sc = c.pop("_scene")
        c["_svg"], c["kind"] = scenes.make(sc.pop("type", scenes.FALLBACK), c["id"], sc, theme["palette"], romance)
        if c["kind"] != T.CHAPTERS[chapters.index(c)].get("scene", c["kind"]) and isinstance(T.CHAPTERS[chapters.index(c)].get("scene"), str):
            warn(f"Chapter {c['name']}: no scene type {T.CHAPTERS[chapters.index(c)]['scene']!r}; using {c['kind']!r}")
    if on("amp"):
        if "&" in heading:
            eggs["amp"] = text_of("amp"); sheet.append(("amp", "Tap the \"&\" in the names 7 times within 4 seconds", "Today, top panel"))
        else:
            warn("SECRETS.amp: the heading has no \"&\" to tap; this secret is off")
    if on("hold"):
        c = scene_target("hold", lambda c: "holdable" in c["_svg"], "traveller to press (plane, boat, scooter or train)")
        if c:
            c["_svg"] = c["_svg"].replace('class="tap holdable"', 'class="tap hold-egg" data-egg="hold"', 1)
            eggs["hold"] = text_of("hold"); cfg["holdToast"] = S["hold"].get("toast", "Vroom!")
            what = dict(flight="plane", island="boat", mountain="scooter", hills="train").get(c["kind"], "traveller")
            sheet.append(("hold", f"Press and hold the {what} for about a second", f"Journey, {c['name']} scene"))
    if on("mascot"):
        c = scene_target("mascot", lambda c: 'class="pop' in c["_svg"], "sticker")
        if c:
            c["_svg"] = c["_svg"].replace('class="pop', 'class="egg-mascot pop', 1)
            eggs["mascot"] = text_of("mascot")
            sheet.append(("mascot", "Tap the big sticker in the scene 3 times quickly", f"Journey, {c['name']} scene"))
    if on("moon"):
        need(S["moon"].get("date"), "SECRETS.moon needs a date")
        md = day(S["moon"]["date"], "SECRETS.moon").isoformat()
        if not first <= md <= last:
            warn(f"SECRETS.moon: {md} is outside the trip; it will still work, but nobody may be looking that day")
        eggs["moon"] = text_of("moon"); cfg.update(moonDate=md, wish=S["moon"].get("wish", "Make a wish."), moonLabel=S["moon"].get("label", "The full moon"))
        sheet.append(("moon", f"Only on {label(md)} ({md}, destination calendar): the sticker in the top panel becomes a glowing moon. Tap it for the lantern night, then the letter", "Today, top panel"))
    if on("code"):
        if fx and S["code"].get("value"):
            eggs["code"] = text_of("code"); cfg["code"] = scramble(str(S["code"]["value"]), "code")
            sheet.append(("code", f"Type {S['code']['value']} into the money converter", "Handy, money"))
        else:
            warn("SECRETS.code needs FX (the converter) and a value; this secret is off")
    if on("phrase"):
        want = S["phrase"].get("phrase")
        idx = next((i for i, p in enumerate(phrases) if p["en"] == want), len(phrases) - 1 if phrases and not want else None)
        if idx is None:
            warn("SECRETS.phrase: that phrase is not in PHRASES; this secret is off")
        else:
            phrases[idx]["egg"] = 1; eggs["phrase"] = ("", "")
            sheet.append(("phrase", f"Open the phrase card \"{phrases[idx]['en']}\" full screen: it rains (counts quietly, no letter)", "Handy, phrases"))
    if on("flower"):
        eggs["flower"] = text_of("flower"); sheet.append(("flower", "Press and hold the sticker in the footer for about a second", "Bottom of any view"))

    # ---- the rest
    after = [[str(len(days)), "days"], [str(len(flights)), "flights" if len(flights) != 1 else "flight"],
             [str(len(hotels)), "stays" if len(hotels) != 1 else "stay"]] + [list(map(str, k)) for k in trip.get("keeps", [])]
    if trip.get("occasion"):
        after.append(["1", trip["occasion"]])
    f0 = min(flights.values(), key=lambda f: f["depUtc"]) if flights else None
    takeoff = f0["depUtc"] if f0 else utc(first, "00:00", home_tz)
    noon = dt.datetime.fromisoformat(first + "T12:00:00")
    off = offset_hours(tz, noon)
    zones = sorted(zones, key=lambda z: z[0])
    st = dict(STICKER_DEFAULTS, **trip.get("stickers", {}))
    for k, v in st.items():
        need(v in art.NAMES, f"TRIP.stickers.{k}: no sticker called {v!r}. Have: " + ", ".join(art.NAMES))
    f, l = dt.date.fromisoformat(first), dt.date.fromisoformat(last)
    data = dict(
        key=trip.get("storage_key") or slug(trip["title"] + "-" + first), title=trip["title"], heading=heading, people=people, romance=romance,
        eyebrow=f"{trip['title']} · {f.day:02d}.{f.month:02d} to {l.day:02d}.{l.month:02d}.{l.year}", footer=trip.get("footer", "Made for a trip worth remembering."),
        stickers=st, tz=tz, tzHome=home_tz, zones=[dict(t=z[0], tz=z[1]) for z in zones],
        lockOff=f"{'+' if off >= 0 else '-'}{int(abs(off)):02d}:{int(round(abs(off) % 1 * 60)):02d}",
        flights=flights, hotels=hotels, boats=boats, chapters=chapters, days=days, nights=nights, keeps=after,
        contacts=[dict(a=a, b=b) for a, b in g("CONTACTS", [])], taxi=taxi, phrases=phrases, phrasesNote=g("PHRASES_NOTE", ""),
        lang=trip.get("local_lang", ""), packing=[dict(g=a, items=b) for a, b in g("PACKING", [])],
        shopGroups=trip.get("shopping_groups", ["Clothes", "Gifts", "Food to try", "Other"]),
        fx=fx, tips=g("TIPS", []), letters=letters, seeds=seeds, seedPatches=g("SEED_PATCHES", []), alerts=alerts,
        eggs={k: [scramble(v[0], "egg" + k), scramble(v[1], "egg" + k)] for k, v in eggs.items()}, eggCfg=cfg,
        takeoffUtc=takeoff, first=dict(label=f0["date"], dep=f0["dep"], frm=f0["frm_ap"]) if f0 else None,
        confetti=(["#E8577E", "#F49AA8", "#E3B95A", "#C99A3A"] if romance else theme["confetti"] or ["#E3B95A", "#5CC4B8", "#E8577E", "#7FB2E8", "#F6B73C"]),
    )
    for v in data["seedPatches"]:
        need(isinstance(v.get("v"), int) and v["v"] >= 2, "SEED_PATCHES: each patch needs v=2, 3, ... in order")
    return data, sheet, eggs


# title, text per secret: (couple wording, neutral wording). The trip file can replace either.
SECRET_DEFAULTS = dict(
    amp=(("Better together", "The smallest character on the page, and the one doing all the work."),
         ("The whole gang", "The smallest character on the page, and the one keeping this group in one piece.")),
    hold=(("Road trip rules", "Driver picks the road. Passenger picks the music and every stop for a view."),
          ("Road trip rules", "Driver picks the road. Everyone else votes on the music.")),
    mascot=(("Spotted", "Official holiday business: do nothing at all until at least four o'clock."),
            ("Spotted", "Official holiday business: do nothing at all until at least four o'clock.")),
    moon=(("Look up", "Phones away for ten minutes. The sky is doing the work tonight."),
          ("Look up", "Phones away for ten minutes. The sky is doing the work tonight.")),
    code=(("You remembered", "That number means something. Tonight is on the house."),
          ("You remembered", "That number means something. Next round is on whoever typed it.")),
    phrase=(("", ""), ("", "")),
    flower=(("The small print", "Somebody built this page for you, one evening at a time."),
            ("The small print", "Somebody built this page for this trip, one evening at a time.")),
)


def secrets_md(trip, data, sheet, eggs, builder_note):
    n = len(sheet)
    rows = "\n".join(f"| {i + 1} | {eggs[k][0] or '(no letter)'} | {how} | {where} |" for i, (k, how, where) in enumerate(sheet))
    letters = "\n".join(f"- From {L['from']} to {'everyone' if L['to'] == 'all' else L['to']}, opens {label(L['on'])} ({L['on']})"
                        + (f": \"{L['title']}\"" if L["title"] else "") for L in data["letters"]) or "- none"
    mark = "hearts" if data["romance"] else "stars"
    return f"""# Secrets in the {trip['title']} page

PRIVATE. For whoever asked for the page. Do not publish this file, and do not paste it into a shared chat.
None of this is written anywhere a traveller can read on the page itself.
{builder_note}
{f'The footer shows {n} small {mark} that fill in as secrets are found (shared between phones). Finding one opens a small letter and says "Secret found, n of {n}".' if n else 'No hidden secrets are switched on.'}

| # | Secret | How to trigger | Where |
|---|--------|----------------|-------|
{rows}

Sealed letters written into the page (visible as sealed envelopes in Notes, not counted above):

{letters}

Small touches that are not secrets: every sticker wiggles and throws {mark} when tapped, the sun spins,
ticking a list item pops, copying a booking number sparkles, packing the last item makes it rain,
and a sealed note cracks its wax seal the first time it is opened.

Testing: open the built file locally with ?date=YYYY-MM-DD added to the address to pretend it is that day
(for example ?date={data['eggCfg'].get('moonDate', data['days'][0]['iso'])}). This does not work inside the published page, where only the real date counts.

The words of secrets and sealed letters are scrambled in the page source so they do not show up in a casual
look. That is obfuscation, not encryption: someone determined can read them.
"""


# ---------------------------------------------------------------- documents, maps, page
def load_docs(folder, cache):
    """Every PDF/JPG/PNG in docs/ -> {stem: data URI}. PDFs: page 1 at 130 dpi through pdftoppm."""
    out = {}
    if not folder.is_dir():
        return out
    for p in sorted(folder.iterdir()):
        ext = p.suffix.lower()
        if ext == ".pdf":
            cache.mkdir(parents=True, exist_ok=True)
            jpg = cache / (p.stem + ".jpg")
            if not jpg.exists() or jpg.stat().st_mtime < p.stat().st_mtime:
                if not shutil.which("pdftoppm"):
                    warn(f"pdftoppm is not installed, so {p.name} was skipped. Install poppler-utils, or save page 1 as a JPG in docs/")
                    continue
                subprocess.run(["pdftoppm", "-r", "130", "-jpeg", "-f", "1", "-l", "1", "-singlefile", str(p), str(jpg.with_suffix(""))], check=True)
            out[p.stem] = "data:image/jpeg;base64," + base64.b64encode(jpg.read_bytes()).decode()
        elif ext in (".jpg", ".jpeg", ".png"):
            out[p.stem] = f"data:image/{'png' if ext == '.png' else 'jpeg'};base64," + base64.b64encode(p.read_bytes()).decode()
    return out


def draw_maps(T, data, world):
    places, home, out = getattr(T, "PLACES", {}), T.TRIP.get("home"), {}
    pt = lambda p: (p["lon"], p["lat"], p["name"])
    for key, f in getattr(T, "FLIGHTS", {}).items():
        a, b = places[f["frm"]], places[f["to"]]
        if all("lat" in p and "lon" in p for p in (a, b)):
            out[key] = geo.route_map(key, pt(a), pt(b), "flight", world, "a" if f["frm"] == home else "b" if f["to"] == home else None, data["romance"])
        else:
            warn(f"Flight {key}: a place has no lat/lon, so there is no map for it")
    for key, b in data["boats"].items():
        pa, pb = b.pop("_a"), b.pop("_b")
        if pa and pb and all("lat" in p and "lon" in p for p in (pa, pb)):
            kind = "boat" if b["kind"] in ("boat", "ferry") else "land"
            out[key] = geo.route_map(key, pt(pa), pt(pb), kind, world, None, data["romance"], note=b["dur"])
    return out


def build(trip_path, theme_name=None, out_dir=None, offline=False, local_gsap=None):
    trip_path = pathlib.Path(trip_path).resolve()
    T = load_trip(trip_path)
    base = trip_path.parent
    cache = base / ".cache"
    theme = theme_info(theme_name or T.TRIP.get("theme", "silk"))
    docs = load_docs(base / "docs", cache / "docs")
    data, sheet, eggs = build_data(T, theme, docs)
    world = None if offline else geo.fetch(cache / "world-atlas")
    maps = draw_maps(T, data, world)
    romance = data["romance"]

    templates = ""
    for c in data["chapters"]:
        templates += f'<template id="scene-{c["id"]}">{c.pop("_svg")}</template>'
    for d in data["days"]:
        if d.get("scene"):
            svg, kind = scenes.make(d["scene"]["kind"], d["scene"]["id"], {}, theme["palette"], romance)
            d["scene"]["kind"] = kind
            templates += f'<template id="scene-{d["scene"]["id"]}">{svg}</template>'
    if "moon" in data["eggs"]:
        templates += f'<template id="scene-night">{scenes.make("lanterns", "night", {}, theme["palette"], romance)[0]}</template>'
    templates += "".join(f'<template id="map-{k}">{v}</template>' for k, v in maps.items())
    for name in sorted(set(data["stickers"].values())):
        s = art.get(name, romance)
        templates += f'<template id="st-{name}">{s.replace(chr(34) + "sticker", chr(34) + "sticker tap", 1)}</template>'

    used = {p["doc"] for f in data["flights"].values() for p in f["pax"]} | {h["doc"] for h in data["hotels"].values()} | {b["doc"] for b in data["boats"].values()}
    imgs = {k: v for k, v in docs.items() if k in used}
    for k in sorted(set(docs) - used):
        warn(f"docs/{k} is not referenced by any flight, stay or transfer, so it is not embedded")

    fonts = theme["fonts"]
    if T.TRIP.get("local_font"):
        fonts += "&family=" + T.TRIP["local_font"].replace(" ", "+") + ":wght@400;600"
    tpl = (HERE / "template.html").read_text()
    local_css = f':root {{ --local: "{T.TRIP["local_font"]}", var(--body); }}\n' if T.TRIP.get("local_font") else ""
    out = (tpl.replace("{{TITLE}}", scenes.esc(data["heading"] + " · " + data["title"]))
              .replace("{{FONTS}}", f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{fonts}&display=swap">' if fonts else "")
              .replace("{{THEME_CSS}}", f"/* ===== theme: {theme['name']} ===== */\n" + theme["css"] + local_css)
              .replace("{{SYMBOL}}", HEART if romance else SPARK)
              .replace("{{SHARED_DEFS}}", scenes.shared_defs(theme["palette"]))
              .replace("{{TEMPLATES}}", templates)
              .replace("{{IMGDATA}}", json.dumps(imgs))
              .replace("{{DATA}}", json.dumps(data, ensure_ascii=False).replace("</", "<\\/")))
    dist = pathlib.Path(out_dir).resolve() if out_dir else base / "dist"
    dist.mkdir(parents=True, exist_ok=True)
    if local_gsap:
        (dist / "vendor").mkdir(exist_ok=True)
        for f in ("gsap.min.js", "ScrollTrigger.min.js"):
            shutil.copy(pathlib.Path(local_gsap) / f, dist / "vendor" / f)
        out = re.sub(r"https://cdn\.jsdelivr\.net/npm/gsap@[\d.]+/dist/", "vendor/", out)
        # the published page gets its viewport from the Artifact wrapper; a bare local file needs its own to lay out at phone width
        out = '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n' + out
    need("{{" not in re.sub(r"<script type=\"application/json\".*?</script>", "", out, flags=re.S), "A template placeholder was left unfilled")
    (dist / "index.html").write_text(out)
    (dist / "seed.json").write_text(json.dumps(data["seeds"], ensure_ascii=False, indent=1))
    who = T.TRIP.get("builder")
    (base / "SECRETS.md").write_text(secrets_md(T.TRIP, data, sheet, eggs, f"Private list for {who}.\n" if who else ""))

    print(f"{dist / 'index.html'}  {len(out.encode()) // 1024} KB; {len(data['days'])} days, {len(data['chapters'])} chapters, "
          f"{len(maps)} maps{'' if world else ' (plain)'}, {len(imgs)} documents, {len(sheet)} secrets, theme {theme['name']}, romance {'on' if romance else 'off'}")
    if local_gsap:
        print("  LOCAL TEST BUILD: GSAP is loaded from dist/vendor/. Rebuild without --local-gsap before publishing.")
    for w in warnings:
        print("  warning:", w)
    if open_items:
        print("  open items (unknown, shown on the page as \"to confirm\"; ask, never guess):")
        for o in open_items:
            print("   -", o)
    print(f"  private: {base / 'SECRETS.md'}")
    return dist / "index.html"


def main(argv):
    if "--themes" in argv:
        for p in sorted((HERE / "themes").glob("*.css")):
            t = theme_info(p.stem)
            print(f"{p.stem:10} {t['name']:16} {t['mood']}")
        return 0
    args, opts, i = [], {}, 0
    while i < len(argv):
        if argv[i] in ("--theme", "--out", "--local-gsap"):
            need(i + 1 < len(argv), f"{argv[i]} needs a value"); opts[argv[i]] = argv[i + 1]; i += 2
        elif argv[i] == "--offline":
            opts["--offline"] = True; i += 1
        else:
            args.append(argv[i]); i += 1
    if len(args) != 1:
        print(__doc__); return 2
    build(args[0], opts.get("--theme"), opts.get("--out"), bool(opts.get("--offline")), opts.get("--local-gsap"))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except TripError as e:
        print("Trip file problem:", e, file=sys.stderr)
        sys.exit(1)
