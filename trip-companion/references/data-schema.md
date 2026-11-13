# The trip file

One Python file holds every fact of the trip. `build.py` imports it, checks it, and writes the page. Start from
`examples/greece/trip.py` (everything switched on) or `examples/friends-weekend/trip.py` (almost nothing).

Only `TRIP`, `TRAVELLERS` and `CHAPTERS` are required. Leave out any other block and that part of the page is
simply not shown. An unknown upper-case name is reported as a probable typo. Errors stop the build with a
sentence saying what to fix.

**Conventions**

- Dates are full ISO strings: `"2027-06-05"`. Times are `"HH:MM"`, local wall-clock time where they happen.
- An unknown value is an empty string `""`, never a guess. A missing `ref` shows on the page as "To confirm" and
  is printed by the build under "open items".
- Keys (`"EX101"`, `"plaka"`) are yours to choose; they link bookings to days.

## TRIP

| key | required | meaning |
|---|---|---|
| `title` | yes | The trip in the travellers' words: `"Greece"`. |
| `tz` | yes | Destination time zone: an IANA name (`"Europe/Athens"`) or a UTC offset in hours (`3`, `5.5`). It decides what "today" is during the trip and the calendar that sealed letters and the moon open on. |
| `home_tz` | no | Time zone used for "today" before the first departure. Defaults to `tz`. |
| `romance` | no | `True` for a couple who want the couple layer; default `False`. See below. |
| `theme` | no | One of the eight in `references/themes.md`. Default `"silk"`. |
| `home` | no | The `PLACES` key of home, so maps tint the home country differently. |
| `occasion` | no | `"honeymoon"`, `"anniversary"`... Shown in the after-trip summary. |
| `builder` | no | Who asked for the page; named at the top of `SECRETS.md`. |
| `heading` | no | The big name line. Default: the travellers joined ("Alex & Sam", "Ana, Ben & Chloe"). |
| `footer` | no | One line at the very bottom. |
| `stickers` | no | Which sticker sits where: keys `hero, wallet, lists, notes, handy, footer`; values from the sticker list in `references/scenes-and-art.md`. |
| `keeps` | no | Extra numbers for the after-trip summary: `[(2, "islands"), (3, "ferries")]`. Days, flights and stays are counted for you. |
| `shopping_groups` | no | Group names for the shopping list. |
| `local_lang` | no | Language code of the local script (`"el"`, `"ja"`, `"ar"`), set on taxi cards and phrases. |
| `local_font` | no | A Google Fonts family for the local script when the theme fonts do not cover it, e.g. `"Noto Sans JP"`. |
| `storage_key` | no | Name of this trip in the phone's own storage. Default: title plus first day. Do not change it after launch. |

### romance

`romance=True` switches on the couple layer: hearts as the page's little symbol (confetti, counters, map stops),
a tappable "&" between the two names, "between the two of us" wording in Notes, and couple wording in the
default secret texts. It expects exactly two travellers (the build warns otherwise).

`romance=False` (the default) is for families, friends and solo travellers, any number of people: a four-point
sparkle replaces every heart, map stops are pins, confetti takes the theme's colours, the couple-only details are
removed from the drawings, Notes are written to a chosen traveller or to everyone, and the default secret texts
are neutral. Every feature still works. Ask the travellers; do not infer it from two names.

## TRAVELLERS

`["Alex", "Sam"]`. First names or nicknames exactly as they should appear. One or more. These are the names on
the "who are you on this phone?" sheet, on passes, on picks and on notes.

## PLACES

Airports, ports, stations and towns that flights and transfers run between.

```python
PLACES = {"LHR": dict(name="London", lat=51.47, lon=-0.4543, tz="Europe/London"),
          "ATH": dict(name="Athens", lat=37.9364, lon=23.9445)}
```

`name` is required. `lat`/`lon` draw the route map (without them there is no map for that leg). `tz` is needed
only where it differs from `TRIP["tz"]`; it makes departure countdowns and durations right, and the page's clock
switches zone at each departure. `code` overrides the big three-letter code shown on a pass (default: the key).

## FLIGHTS

```python
"EX101": dict(airline="Example Air", num="EX 101", frm="LHR", to="ATH", date="2027-06-05", dep="08:10", arr="13:55",
              frm_ap="Heathrow, Terminal 2", to_ap="Athens International", ref="ABC123", bag="23 kg checked",
              pax=[dict(who="Alex", ticket="000 0000000001", seat="14A", doc="alex-ticket.pdf")])
```

Required: `frm`, `to` (PLACES keys), `date`, `dep`, `arr`. Add `arr_date` when it lands on another day. `dur` is
worked out from the two time zones unless given. `pax` defaults to every traveller with no ticket or seat.

## STAYS

```python
"plaka": dict(name="Olive Tree House", short="Athens", place="Athens · Plaka", addr="...", phone="...", room="...",
              board="Breakfast included", check_in="2027-06-05", check_out="2027-06-07", cin="from 15:00", cout="by 11:00",
              ref="DEMO-0001", doc="stay-olive-tree-house.png", note="...", map="optional map search", tz="optional")
```

Required: `name`, `check_in`, `check_out`. `short` labels the nights strip on Today. If `cin` contains a time, the
check-in countdown uses it. A stay whose `phone` equals the phone of a `TAXI` row gets a "show the driver" button.

## TRANSFERS

Boats, trains, buses and booked cars: `kind` is `boat`, `ferry`, `train`, `bus` or `car` (default `boat`).

```python
"FERRY1": dict(kind="ferry", operator="Example Ferries", service="Fast ferry", frm="PIR", to="NAX", frm_ap="Piraeus, gate E7",
               to_ap="Naxos port", date="2027-06-07", dep="07:25", arr="12:40", ref="FERRY-0001", note="...", doc="ferry.pdf")
```

Required: `frm`, `to`, `date`, `dep`, `arr`. `frm`/`to` are PLACES keys for a map, or plain words for none.
`verb` overrides the word on the card ("Ferry", "Train"...).

## CHAPTERS

The journey, in order. One chapter is usually one place.

```python
dict(id="naxos", name="Naxos", place="Old Town and the beaches",
     scene=dict(type="island", caption="07:25 from Piraeus"),          # or just scene="island"
     weather="19 to 27°C · breezy",                                    # optional, only if known
     food=[("Name", "One line about it", "map search words")],         # optional
     days=[dict(date="2027-06-07", title="To the island", items=[...]),
           dict(date="2027-06-08", title="Beach day", scene="lanterns", scene_caption="Moon over the bay", items=[...])])
```

Days must be in date order across the whole file. A day may carry its own small `scene`. Scene types and their
options are in `references/scenes-and-art.md`.

Day items, in the order they should read:

| item | shows as |
|---|---|
| `("step", "06:15", "Taxi to the port")` | a timed line |
| `("flight", "EX101")` | the boarding pass with its route map |
| `("stay", "plaka")` | the stay card |
| `("transfer", "FERRY1")` | the transfer card with its map |
| `("idea", "text")` | a loose idea |
| `("note", "text")` | a quiet aside |
| `("todo", "text", "https://...", "link words")` | a reminder inside the day (url and link optional) |
| `("pick", "text", "map search", "short name", "Sam")` | "Sam's pick", also added to the shared places wishlist (name optional) |

## Lists and handy things

```python
TODOS = [dict(id="checkin", text="Check in online", sub="Opens 24 hours before.", url="https://example.com/checkin",
              opens="2027-06-04", until="2027-06-05", now_title="Online check-in is open", now_body="...", done_label="Both done")]
PACKING = [("Documents", ["Passports", "Insurance details"]), ("Tech", ["Plug adapter"])]
CONTACTS = [("Example Air", "+44 20 0000 0000")]
TAXI = [("Name in English", "Name in the local script", "smaller second line", "phone of the matching stay")]
PHRASES = [("Hello", "Γεια σας", "ya sas")]            # English, local, how to say it (optional)
PHRASES_NOTE = "Tap any phrase to show it big."
FX = dict(from_name="Euros", from_symbol="€", to_name="Pounds", to_symbol="£", rate=0.85, asof="1 May 2027",
          rule="Quick rule: take off about a seventh.", start=40, steps=[1, 2, 5, 10, 20, 50, 100, 200, 500])
TIPS = ["Paper goes in the bin, not the toilet."]
```

- `TODOS`: only `text` is required. Give each an `id` so it can be patched later. With `opens` (and optionally
  `until`) the to-do also appears as a "do this now" card on Today during that window.
- `FX`: `rate` is how much home money one unit of destination money is. Always give `asof`. Without `FX` there is
  no converter.
- `TODOS`, `PACKING` and the picks are only the *starting* content of the shared lists. See
  `references/collaboration.md` before changing them after the travellers have opened the page.

## LETTERS and SECRETS

```python
LETTERS = [dict(frm="Alex", to="Sam", on="2027-06-11", title="For tonight", text="...")]   # frm optional, to may be "all"
SECRETS = dict(amp=dict(on=True, title="...", text="..."), moon=dict(on=True, date="2027-06-08"), ...)
```

Full catalog, options and default wording: `references/secrets.md`.

## SEED_PATCHES

Changes to the starting lists after launch. Format and rules: `references/collaboration.md`.

## Documents

Put ticket and voucher files in `docs/` beside the trip file: PDF (page 1 is used), JPG or PNG. Refer to them by
file name in `doc=` on a stay, a transfer, or a passenger of a flight. A file nobody refers to is not embedded,
and the build says so. Keep images modest (a phone screenshot is fine); everything is embedded in the one page,
which must stay well under the Artifact size limit.

## What the build writes

| file | what |
|---|---|
| `dist/index.html` | the page: publish this and nothing else |
| `dist/seed.json` | the starting lists with their ids, for reference when writing a seed patch |
| `SECRETS.md` | private how-to-find list for whoever asked for the page |
| `.cache/` | downloaded map data and rendered PDF pages; safe to delete |
