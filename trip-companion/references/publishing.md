# Build, test, publish

## Build

```sh
python3 <skill>/templates/build.py <trip folder>/trip.py
```

Needs Python 3.9 or newer, standard library only. `pdftoppm` (poppler-utils) is needed only if `docs/` holds
PDFs; without it, save page 1 of each PDF as a JPG instead. The first build downloads map coastlines from
`registry.npmjs.org` into `.cache/`; if that is blocked, maps are drawn plain and the build still succeeds
(`--offline` skips the attempt).

The build prints one summary line, then:

- **warnings**: something in the trip file could not be used as written (a document not found, a secret that has
  nothing to attach to, an unknown scene type). Fix each or decide it is fine.
- **open items**: facts that are missing (a booking without a reference, a stay without a phone). The page shows
  "To confirm" for them. Take the list back to the travellers. Never fill one in yourself.
- an **error** stops the build and says what to fix (a day out of order, a flight that lands before it leaves).

Outputs: `dist/index.html` (the page), `dist/seed.json`, and the private `SECRETS.md` beside the trip file.
Keep the trip folder out of public repositories; it contains the travellers' bookings.

## Test locally at phone width

The published page loads GSAP from a CDN and gets its viewport tag from the Artifact wrapper. For a local test,
build a copy that carries both:

```sh
# once: fetch GSAP 3.15.0 from the npm registry (the files are not shipped with this skill)
mkdir -p /tmp/gsap && cd /tmp/gsap && npm pack gsap@3.15.0 && tar -xzf gsap-3.15.0.tgz
# -> /tmp/gsap/package/dist/gsap.min.js and ScrollTrigger.min.js

python3 <skill>/templates/build.py trip.py --out /tmp/trip-test --local-gsap /tmp/gsap/package/dist
```

Open `/tmp/trip-test/index.html` in a browser at 390 x 844 (a phone-sized window, or a headless browser with
that viewport; do not rely on desktop width). **Never publish a `--local-gsap` build**: rebuild without the flag.

Checklist. Do all of it; look at screenshots rather than trusting the DOM.

1. **No errors.** Zero uncaught page errors and nothing red in the console on load and through every step below.
2. **Every view** on the bottom bar: Today, Journey, Wallet, Lists, Notes, Handy. No text cut off or overlapping,
   nothing wider than the screen, the bottom bar never covers the last row.
3. **Journey.** Scroll slowly from top to bottom. Each scene moves and never shows a gap at its edges; planes and
   boats travel along their maps; the chapter chips at the top follow and jump.
4. **Wallet.** Each pass and stay shows the right times and names. Tap a booking number: it copies. Open each
   document: it shows the right file and zooms.
5. **Dates.** Add `?date=YYYY-MM-DD` (or `?date=YYYY-MM-DDTHH:MM`) to the local file's address to pretend it is that
   day at the destination:
   - a day before the trip: countdown and "do this now" cards in their window;
   - the first day, a middle day, a travel day: today's plan, "next up" countdown, tonight's stay;
   - the day after the last: the keepsake summary;
   - each sealed letter's day and the day before it; the moon's date.
6. **Secrets.** Trigger each one as `SECRETS.md` says; the footer counter reaches n of n. See
   `references/secrets.md`.
7. **Lists.** Tick, add and delete in each list, reload: everything is still there ("Saved on this phone").
   Write a sealed note to another traveller; switch traveller in Notes and see it sealed.
8. **Romance off?** Look for leftover hearts or couple wording anywhere. There should be none.
9. **Reduced motion.** With "reduce motion" on, the page is still and complete.
10. **Size.** The build prints the size. Expect about 150 KB plus 100 to 160 KB per route map with real
    coastlines (the nine-day example is about 900 KB). Each embedded document adds its size plus a third. Stay
    far below the Artifact limit; shrink photos before embedding.

The `?date=` override only works on a local file (the page ignores it anywhere else); there only the
real date counts.

## Publish

Publish `dist/index.html` as an Artifact:

- capabilities `{"db": {}, "user": {}}` (see `references/collaboration.md`);
- a short title such as "Greece trip", and a generic icon word such as `map` or `plane`;
- only that one file. Never `SECRETS.md`, `seed.json`, the trip file or `docs/`.

The page needs two outside hosts and nothing else: `cdn.jsdelivr.net` (GSAP 3.15.0 and ScrollTrigger, pinned)
and Google Fonts (the theme's fonts). Without GSAP the page still works, without scroll animation; without the
fonts it falls back to system fonts. Do not add other scripts, tracking or analytics.

Artifacts are private until shared. The page contains real bookings: share it with the travellers only, with
edit access for each (so the shared lists work), and tell the owner not to make it public.

After publishing, open the published page once yourself if you can, confirm the Lists heading says "Shared live
between your phones", and tick and untick one item.

## Hand over

To everyone: the link, "add it to your home screen", and one line each on Today, Wallet and Lists. Say that
ticks and notes are shared, and that comments on the page reach you for changes.

To the person who asked, privately: `SECRETS.md`, how to share with edit access, and the open items still to
confirm.

## Later changes

Edit the trip file, rebuild, run the checklist for what changed, and republish **to the same Artifact** so the
link, the shared lists and everyone's ticks stay. Changing starting list rows needs a seed patch
(`references/collaboration.md`). Changing `storage_key`, or publishing as a new Artifact, starts everyone from
empty lists.

## Troubleshooting

| symptom | cause and fix |
|---|---|
| Page lays out desktop-wide in a local test | built without `--local-gsap` (no viewport tag in a bare file) |
| Scenes do not move locally | GSAP did not load: use `--local-gsap`, or allow the CDN |
| Maps are plain boxes with a line | coastline download was blocked; run `geo.py --fetch` where the registry is reachable and copy the three files into `.cache/world-atlas` |
| "Unknown theme" / "no sticker called" | spelling; `build.py --themes`, sticker list in `references/scenes-and-art.md` |
| A document button is missing | file name in `doc=` does not match a file in `docs/` (see the warning) |
| Times are an hour out | a place needs its own `tz`, or `home_tz` is missing |
| Local script shows as boxes | set `TRIP["local_font"]` to a Google font that covers it |
