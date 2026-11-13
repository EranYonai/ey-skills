---
name: trip-companion
description: Build a phone-first trip companion page for any trip (honeymoon, family holiday, friends' weekend, solo journey) and publish it as a single-file HTML Artifact. Interviews the travellers for everything, lets them pick one of eight looks, then builds a page with a today view, a scroll-animated journey, a ticket wallet, shared lists and sealed notes that sync between phones, handy cards, and hidden surprises. Use when someone asks for a trip page, itinerary page, travel companion, honeymoon page or "a page for our trip".
---

# Trip companion

One HTML page that lives on the travellers' phones for the whole trip. It holds every booking, shows what is
happening today, and is nice to scroll. It is built from a trip data file by a small Python build; you never
hand-write the page.

What the travellers get, on a bottom bar of six views:

| view | what it does |
|---|---|
| **Today** | Countdown before the trip; during it, today's plan, the next flight or check-in with a live countdown, tonight's stay. Any day can be peeked at. Afterwards, a keepsake summary. |
| **Journey** | The whole trip as one long scroll. Each chapter opens on an illustrated scene that moves as it scrolls through the screen; planes and boats travel along route maps. |
| **Wallet** | Every flight, transfer and stay as a card. Booking numbers copy on tap; tickets and vouchers open inside the page and pinch to zoom. |
| **Lists** | To-dos, packing, places wishlist, shopping. Shared live between the travellers' phones. |
| **Notes** | Sealed notes: write to another traveller, pick the day it opens. Letters can also be written into the page before the trip. |
| **Handy** | Taxi cards in the local script to show a driver, phrases, a money converter, contacts, tips. |

Three things make it loved. Protect them in every change you make:

1. **Secrets.** Hidden surprises (tap, long-press, a date-locked moon, a code typed in the converter) and sealed
   letters. The build writes a private `SECRETS.md` for whoever asked for the page. See `references/secrets.md`.
2. **Animation.** Scroll-scrubbed scenes per chapter, travellers moving along maps, stickers that react to taps.
   The fun is in beautiful motion and small reactions. **Do not add games**: no bingo, dares, spinners, scores
   or streaks. See `references/scenes-and-art.md`.
3. **Togetherness.** Ticks, lists, ideas and sealed notes sync between phones through the Artifact `db` and
   `user` capabilities, with a fallback to the phone's own storage. See `references/collaboration.md`.

A **romance** setting switches the couple layer on or off. On (a couple): hearts, a tappable "&" between the two
names, love-letter wording. Off (family, friends, solo, any number of travellers): sparkles instead of hearts,
plain wording, notes between everyone. Ask; never assume.

## Folder

```
SKILL.md                 this file
references/              read on demand (table below)
templates/               build.py, template.html, art.py, scenes.py, geo.py, themes/*.css  (do not edit per trip)
examples/greece/         a full invented couple's trip: copy trip.py as the starting point
examples/friends-weekend/ the smallest useful trip: three friends, romance off, almost everything left out
previews/                one picture per theme and a few of the page, to show the travellers
```

## Workflow

1. **Interview.** Follow `references/interview.md`: short rounds, accept anything they paste or upload. Collect
   secrets and letters from the person who asked for the page, privately if the other travellers are in the chat.
2. **Pick the look.** Show the theme pictures (`references/themes.md`, `previews/`). Set `theme` and `romance`.
3. **Write the trip file.** Make a working folder for this trip outside the skill folder. Copy
   `examples/greece/trip.py` into it and replace everything, following `references/data-schema.md`. Put ticket
   and voucher PDFs or photos in a `docs/` folder beside it.
   **Facts only. Never invent a booking, time, address, phone or reference number.** What is unknown stays empty
   and becomes a to-do; the page shows "To confirm".
4. **Build.** `python3 <skill>/templates/build.py <trip folder>/trip.py` writes `dist/index.html` (one
   self-contained file) and a private `SECRETS.md` beside the trip file. Python 3.9+ standard library only;
   `pdftoppm` only if there are PDFs. Read every warning and the "open items" list it prints, and go back to the
   travellers with the open items.
5. **Test at phone width** before anyone sees it: `references/publishing.md` has the checklist (every view,
   scroll the journey, each secret, `?date=` for date-locked things, zero console errors).
6. **Publish** `dist/index.html` as an Artifact with capabilities `{"db": {}, "user": {}}`. Load the
   artifact-capabilities guidance first if your environment has it. Publish only `index.html`; never `SECRETS.md`,
   `seed.json` or the trip file.
7. **Share with edit access.** Every traveller must open the page with edit access, or their phone can read the
   shared lists but not change them. Tell the person who asked how to share it that way.
8. **Hand over the secrets.** Give `SECRETS.md` only to the person who asked for the page, never in a chat the
   other travellers read. Mention that Artifact comments work on the page too, for asking you for changes.
9. **Later changes.** Edit the trip file, rebuild, republish to the same Artifact. Changing the starting lists
   after phones have opened the page needs a seed patch: `references/collaboration.md`.

## Rules

- The trip file is the only place trip facts live. `templates/` contains no trip facts and is not edited per trip.
- Treat bookings, names, letters and secrets as private. Do not put them in commit messages, shared chats, URLs or
  requests to outside services. Keep the trip folder out of any public repository.
- Sealed notes and secret texts are scrambled in the page, which is obfuscation, not encryption. Say so plainly if
  asked; never promise privacy the page cannot give.
- Do not add tracking, analytics, or scripts from anywhere but the pinned GSAP CDN files the template already loads.
- New destination, nothing in the library fits? Draw a new scene or sticker in the same style
  (`references/scenes-and-art.md`) rather than shipping a mismatched one.

## References

| file | read when |
|---|---|
| `references/interview.md` | before talking to the travellers |
| `references/data-schema.md` | writing or changing a trip file |
| `references/themes.md` | choosing, showing or adding a theme |
| `references/secrets.md` | planning surprises, sealed letters, and handing over `SECRETS.md` |
| `references/collaboration.md` | publishing, sharing, sync problems, changing lists after launch |
| `references/scenes-and-art.md` | picking chapter scenes, drawing new scenes or stickers, route maps |
| `references/publishing.md` | building, testing, publishing, troubleshooting |
