# Secrets and sealed letters

The part people remember. Secrets are small hidden surprises: do the right thing in the right place and a letter
opens. They are planned with **one person only** (whoever asked for the page) and never mentioned where the other
travellers can read. Nothing on the page says where they are; the footer only shows a row of small empty hearts
(stars with romance off) that fill as secrets are found.

## The seven secrets

Switch each on in `SECRETS` in the trip file. All are off unless listed with `on=True`.

| id | how it is found | where | needs | options |
|---|---|---|---|---|
| `amp` | Tap the "&" in the names 7 times within 4 seconds | Today, top panel | two or more travellers (the heading must contain "&") | `title`, `text` |
| `hold` | Press and hold the traveller in a scene (plane, boat, scooter or train) for about a second; it honks first | Journey, one chapter scene | a `flight`, `island`, `mountain` or `hills` scene | `chapter` (which one; default the first that fits), `toast` ("Beep beep!"), `title`, `text` |
| `mascot` | Tap the big sticker in a scene 3 times quickly | Journey, one chapter scene | a scene with a sticker (`island`, `beach`, `city`, `hills` with a sticker) | `chapter`, `title`, `text` |
| `moon` | Only on one date: the sticker in the top panel becomes a glowing moon. Tap it: a night of rising lanterns, then the letter | Today, top panel | a `date` | `date`, `label` ("The full moon"), `wish` ("Make a wish."), `title`, `text` |
| `code` | Type a meaningful number into the money converter | Handy, money | `FX` | `value` (digits, e.g. a date as `"1106"`), `title`, `text` |
| `phrase` | Open one phrase card full screen: it rains hearts or stars. Counts quietly, no letter | Handy, phrases | `PHRASES` | `phrase` (the English text of the card; default the last one) |
| `flower` | Press and hold the sticker in the footer for about a second | bottom of any view | nothing | `title`, `text` |

```python
SECRETS = dict(
    amp=dict(on=True, title="Alex and Sam", text="..."),
    hold=dict(on=True, chapter="hills", toast="Vroom!"),
    moon=dict(on=True, date="2027-06-08", label="The moon", wish="Look up."),
    code=dict(on=True, value="1106", title="Ten years", text="..."),
)
```

- `title` and `text` are the letter that opens. Leave them out and a built-in text is used: couple wording with
  `romance=True`, neutral wording otherwise. Personal words are much better than the defaults; ask for them.
- If the page lacks what a secret needs (no "&", no converter, no fitting scene) the build switches that secret
  off and prints a warning. It never fails silently on the page.
- Found secrets are shared: when one traveller finds one, the counter fills on the other phones too. A secret
  can be opened again; the second time it says "A secret, again".
- The moon uses the destination calendar (`TRIP["tz"]`), like every date-locked thing. Pick a date that means
  something: a real full moon, a birthday, the anniversary. Check the fact (a full moon date) before you promise it.

## Sealed letters

Two kinds, both shown in **Notes** as an envelope with a wax seal that only opens on its day.

1. **Written into the page before the trip** (`LETTERS`). From one traveller to another, to everyone, or "from
   the trip" itself when `frm` is left out.

   ```python
   LETTERS = [dict(frm="Alex", to="Sam", on="2027-06-11", title="For tonight", text="..."),
              dict(to="all", on="2027-06-12", title="Before you pack", text="...")]
   ```

   Take the words exactly as the writer gives them. A letter from Alex to Sam is visible in the trip file and in
   the page source in scrambled form, so collect it privately and do not show the trip file to Sam.
2. **Written on the phone during the trip.** Any traveller writes a note in Notes, picks who it is for and the
   day it opens. It syncs to the other phone as a sealed envelope.

Today shows "1 sealed note is waiting for you" with the date the next one opens, and a card on the day itself.

## What is and is not private

Secret texts, the converter code and letter bodies are scrambled in the page source and in the shared store, so
a casual look (or "view source") does not spoil them. **This is obfuscation, not encryption.** Someone who wants
to can decode them, and anyone who can open the Artifact, even view-only, can read its data. The page says so in the Notes
view ("Hidden, not locked"). Do not put anything in a letter that would be harmful if read early, and say this
plainly to the person planning the surprises.

## SECRETS.md

Every build writes `SECRETS.md` beside the trip file: a table of each secret that is on, how to trigger it and
where, the list of sealed letters with their dates, and how to test date-locked things. It is for the person who
asked for the page.

- Give it to that person only, in a private thread. Never publish it, never attach it to the Artifact, never
  paste it into a chat the other travellers read.
- If the builder is also a traveller who wants to be surprised by some of it (for example letters written by the
  other person), agree with both who sees what before sending it.
- Regenerate it after any change to secrets; it is always rebuilt from the trip file.

## Testing

Open the locally built page (`--local-gsap`, see `references/publishing.md`) and trigger every secret exactly as
`SECRETS.md` describes. Then:

- `index.html?date=2027-06-08` pretends it is that day (destination calendar, noon): check the moon, each
  letter's opening day, and the day before it. The override only works on a local file, not in the published page.
- The counter in the footer must reach "n of n" and the last letter must say that was all of them.
- Build once with a secret switched off and confirm its trigger does nothing and the counter is one shorter.

## Do not turn secrets into games

No scores, streaks, dares, bingo, spinners or leaderboards. A secret is found once, by accident or by love, and
gives a few warm words. That is the whole design.
