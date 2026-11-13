# Sharing between phones

The page is one HTML file, but the travellers' ticks, list items, ideas, sealed notes and found secrets are
shared live between their phones. This uses two Artifact runtime capabilities, with the phone's own storage as a
fallback so the page always works.

## Publishing with the capabilities

Publish `dist/index.html` with:

```json
{"db": {}, "user": {}}
```

- `db`: a small shared database that belongs to the Artifact. The page reads and writes it through
  `window.claude.use("db")`.
- `user`: lets the page remember which traveller this viewer is (`window.claude.use("user")`), so nobody has to
  answer "who are you on this phone?" twice.

If your environment has guidance for Artifact capabilities, load it before publishing; the exact way to declare
capabilities belongs to the publishing tool, not to this skill. Do not change the page's storage code to fit a
tool: it is written against the documented `db` and `user` interfaces and degrades on its own.

## Everyone needs edit access

A viewer with view-only access can read the shared lists but cannot write to them. The page then shows "This
phone can look but not change the shared lists. Ask whoever shared the page to give you edit access." and keeps
that phone's changes on that phone only.

So: **the person who owns the Artifact shares it with every traveller with edit access.** Tell them this in the
handover message, and ask each traveller to tick one packing item as a test: it should appear on the other phones
within a few seconds. The line under the Lists heading says which mode a phone is in:

| line | meaning |
|---|---|
| "Shared live between your phones" | connected and syncing |
| "Saved on this phone" | no shared database here (local file, preview, or capability not granted); everything still works, on this phone only |
| "Can't reach the shared lists yet. Showing what this phone last saw." | slow or no connection; it keeps trying |
| "The shared lists stopped answering. Changes stay on this phone for now." | the connection dropped |

## What is stored

Collections in the Artifact database (one document per row):

| collection | rows |
|---|---|
| `todos` | things to sort: `{text, sub, done, o, url?, link?}` |
| `packing` | `{text, g (group), done, o}` |
| `wishlist` | places: `{name, note, map, day, by, pick, done, o}` |
| `shopping` | `{text, g, done, o}` |
| `ideas` | ideas added to a day: `{day, text, by, ts}` |
| `notes` | sealed notes: `{from, to, on, body (scrambled), opened, ts, o}` |
| `found` | found secrets: `{ts, by}` keyed by secret id |
| `meta/seed` | which starting lists have been written, and the seed version |
| `data/users/<id>/profile` | `{who}`: which traveller this account is |

The phone's own storage holds a copy of all of it under keys starting `tc.<storage_key>.`, plus "who am I" and
which built-in letters this phone has already opened. Storage can be empty or blocked (private windows,
previews); every access is wrapped and the page renders without it.

Booking data (flights, stays, references, documents) is **not** in the database. It is in the page file itself,
so it is visible to exactly the people the Artifact is shared with.

## Starting lists and seeding

`TODOS`, `PACKING` and the day `pick`s are the starting content. The first phone that connects writes them to
the database once and records that in `meta/seed`. Row ids are made from the words (or the `id` you gave a
to-do), so writing them twice is harmless. From then on the lists belong to the travellers: they tick, add and
delete, and **rebuilding the page does not overwrite their lists.**

That is the point, but it means editing `TODOS` or `PACKING` in the trip file after launch changes nothing on
phones that already seeded. To change starting rows after launch, add a seed patch:

```python
SEED_PATCHES = [
    dict(v=2,
         set={"todos": {"ferry-seats": dict(text="Choose ferry seats", sub="Opens a week before.", done=False, o=20)}},
         remove={"todos": ["scooter"], "packing": ["p-1a2b3c4d"]}),
]
```

- `v` starts at 2 and goes up by one per patch. Each phone and the shared database apply a patch once.
- `set` adds a row only if no row with that id exists, so it never overwrites a tick.
- `remove` deletes rows by id. Ids are in `dist/seed.json` (written by every build).
- Also make the same change in `TODOS`/`PACKING`, so a phone opening the page for the first time gets the right
  starting lists.
- Never renumber or delete an old patch.

Things that are not lists (times, bookings, chapter text, secrets, themes) are in the page file: edit the trip
file, rebuild, republish to the same Artifact, and every phone sees them on next load.

## Who are you on this phone?

Notes need to know which traveller is holding the phone. The first time, a sheet lists every traveller; the
choice is kept on the phone and, when the `user` capability is granted, in that account's profile document. A
solo trip skips the question. "Switch" in Notes changes it (useful on a shared tablet).

## Comments

Artifact comments work on the published page like on any Artifact. They are the natural way for travellers to
ask for changes ("the ferry moved to 08:10"): treat a comment as a request, change the trip file, rebuild and
republish. Comments are visible to everyone the page is shared with, so never answer one with a secret.

## Troubleshooting

| symptom | likely cause |
|---|---|
| One phone's ticks never reach the others | that traveller has view-only access; reshare with edit access |
| "Saved on this phone" on the published page | the Artifact was published without the `db` capability; republish with it |
| A deleted starting row came back | the build's ids changed because the words changed; remove the old id with a seed patch |
| Lists are empty on a fresh phone | first load had no connection before seeding; reload once online |
| Asked "who are you" again | storage was cleared and the `user` capability is not granted |
