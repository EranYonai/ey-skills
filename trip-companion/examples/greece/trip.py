"""EXAMPLE TRIP. Everything here is invented: the travellers, the airline, the hotels, every number.

A couple's anniversary trip (romance on) with flights, ferries, four stays, every secret and a sealed letter.
Copy this file as the starting point for a real trip, then replace every value with facts from the travellers.

Facts only: never invent bookings, times or reference numbers. What is not known yet stays empty ("") and
goes into TODOS as an open item. Build with:  python3 ../../templates/build.py trip.py
"""

TRIP = dict(
    title="Greece",                     # the destination, as the travellers would say it
    occasion="anniversary",             # optional: shown as "1 anniversary" in the after-trip summary
    theme="silk",                       # see references/themes.md; python3 build.py --themes
    romance=True,                       # the couple layer: hearts, the "&", love-letter wording. False for friends and family
    tz="Europe/Athens",                 # destination clock: "today" during the trip, and the calendar sealed things open on
    home_tz="Europe/London",            # the clock used for "today" until the first departure
    home="LHR",                         # the PLACES key of home, so maps tint the home country differently
    builder="Alex",                     # who asked for the page and gets SECRETS.md (optional)
    footer="Made for ten years of us.",
    local_lang="el",                    # language code of the local script on taxi cards and phrases
    stickers=dict(hero="sun", wallet="plane", lists="suitcase", notes="hibiscus", handy="camera", footer="hibiscus"),
    keeps=[(2, "islands"), (3, "ferries")],   # extra numbers for the after-trip summary
    shopping_groups=["Gifts", "Food to bring home", "For the flat", "Other"],
)

TRAVELLERS = ["Alex", "Sam"]

# Airports, ports and towns that flights and transfers run between. lat/lon draw the route maps.
# tz is only needed where it differs from TRIP["tz"].
PLACES = {
    "LHR": dict(name="London", lat=51.4700, lon=-0.4543, tz="Europe/London"),
    "ATH": dict(name="Athens", lat=37.9364, lon=23.9445),
    "JTR": dict(name="Santorini", lat=36.3992, lon=25.4793),
    "PIR": dict(name="Piraeus", lat=37.9420, lon=23.6400),
    "NAX": dict(name="Naxos", lat=37.1070, lon=25.3740),
    "SAN": dict(name="Santorini", lat=36.3860, lon=25.4210),
}

FLIGHTS = {
    "EX101": dict(airline="Example Air", num="EX 101", frm="LHR", to="ATH", frm_ap="Heathrow, Terminal 2", to_ap="Athens International",
                  date="2027-06-05", dep="08:10", arr="13:55", ref="ABC123", bag="23 kg checked + cabin bag",
                  pax=[dict(who="Alex", ticket="000 0000000001", seat="14A"), dict(who="Sam", ticket="000 0000000002", seat="14B")]),
    "EX440": dict(airline="Example Air", num="EX 440", frm="JTR", to="ATH", frm_ap="Santorini Airport", to_ap="Athens International",
                  date="2027-06-12", dep="18:30", arr="19:20", ref="DEF456", bag="23 kg checked + cabin bag",
                  pax=[dict(who="Alex", ticket="000 0000000003"), dict(who="Sam", ticket="000 0000000004")]),
    "EX102": dict(airline="Example Air", num="EX 102", frm="ATH", to="LHR", frm_ap="Athens International", to_ap="Heathrow, Terminal 2",
                  date="2027-06-13", dep="15:05", arr="17:00", ref="ABC123", bag="23 kg checked + cabin bag",
                  pax=[dict(who="Alex", ticket="000 0000000001", seat="15C"), dict(who="Sam", ticket="000 0000000002", seat="15D")]),
}

STAYS = {
    "plaka": dict(name="Olive Tree House", short="Athens", place="Athens · Plaka", addr="1 Example Street, Plaka, Athens 105 58",
                  phone="+30 21 0000 0001", room="Double room with balcony", board="Breakfast included",
                  check_in="2027-06-05", check_out="2027-06-07", cin="from 15:00", cout="by 11:00", ref="DEMO-0001",
                  doc="stay-olive-tree-house.png", note="Sample voucher only. Reception is open until midnight."),
    "naxos": dict(name="Blue Door Suites", short="Naxos", place="Naxos · Old Town", addr="2 Example Lane, Chora, Naxos 843 00",
                  phone="+30 22 8500 0002", room="Sea-view suite", board="Breakfast included",
                  check_in="2027-06-07", check_out="2027-06-10", cin="from 14:00", cout="by 11:00", ref="DEMO-0002",
                  note="They meet the ferry with a sign if you send the arrival time the day before."),
    "caldera": dict(name="Caldera View Rooms", short="Santorini", place="Santorini · Firostefani", addr="3 Example Steps, Firostefani, Santorini 847 00",
                    phone="+30 22 8600 0003", room="Cave room with terrace", board="Room only",
                    check_in="2027-06-10", check_out="2027-06-12", cin="afternoon", cout="by 11:00", ref="DEMO-0003",
                    note="Lots of steps and no lift. A porter carries the bags from the road."),
    "airport": dict(name="Runway Rest Hotel", short="Airport", place="Athens · by the airport", addr="4 Example Avenue, Spata 190 04",
                    phone="+30 21 0000 0004", room="Standard double", board="Room only",
                    check_in="2027-06-12", check_out="2027-06-13", cin="from 14:00", cout="by 12:00", ref="",
                    note="Free shuttle from arrivals every 30 minutes."),
}

# Boats, trains, buses, booked cars. kind: boat | ferry | train | bus | car.
TRANSFERS = {
    "FERRY1": dict(kind="ferry", operator="Example Ferries", service="Fast ferry", frm="PIR", to="NAX", frm_ap="Piraeus, gate E7", to_ap="Naxos port",
                   date="2027-06-07", dep="07:25", arr="12:40", ref="FERRY-0001",
                   note="Be at the gate 45 minutes early. Seats are numbered, on the upper deck. If the wind is strong the ferry can run late."),
    "FERRY2": dict(kind="ferry", operator="Example Ferries", service="Fast ferry", frm="NAX", to="SAN", frm_ap="Naxos port", to_ap="Athinios port",
                   date="2027-06-10", dep="13:10", arr="15:15", ref="FERRY-0002",
                   note="The road up from Athinios is slow when a ferry lands. The hotel transfer waits at the bottom."),
}

# Each chapter gets a scroll scene. Each day: date, title, items.
# Item kinds: ("step", "HH:MM", text)  ("flight", key)  ("stay", key)  ("transfer", key)  ("idea", text)  ("note", text)
#             ("todo", text[, url, link text])  ("pick", text, map search, short name[, whose pick])
CHAPTERS = [
    dict(id="go", name="Wheels up", place="London to Athens", scene=dict(type="flight", frm="LHR", to="ATH"),
         weather="Athens · 20 to 30°C · dry · sunset about 20:45", days=[
        dict(date="2027-06-05", title="Off we go", items=[
            ("step", "05:40", "At Heathrow Terminal 2. Bags dropped, coffee in hand."),
            ("flight", "EX101"),
            ("note", "Clocks go forward 2 hours on landing."),
            ("step", "15:00", "Metro line 3 from the airport to Syntagma, about 40 minutes, then a short walk."),
            ("stay", "plaka"),
            ("idea", "Dinner on a roof with the Acropolis lit up."),
        ]),
    ]),
    dict(id="athens", name="Athens", place="Plaka and the hill", scene=dict(type="city", sticker="camera", outline="columns"),
         weather="20 to 30°C · dry and bright · sunset about 20:45",
         food=[("A roof terrace in Plaka", "Any of the small rooftops facing the hill. Go at dusk.", "rooftop restaurant Plaka Athens"),
               ("The central market", "Olives, cheese and a counter lunch among the stalls.", "Varvakios Central Market Athens")],
         days=[
        dict(date="2027-06-06", title="The old city", items=[
            ("idea", "Up the hill early, before the heat and the tour groups."),
            ("pick", "Lunch from the stalls at the central market.", "Varvakios Central Market Athens", "Central market", "Sam"),
            ("idea", "The open-air cinema in the evening, if a film is on."),
            ("todo", "Send the ferry arrival time to the hotel in Naxos."),
        ]),
    ]),
    dict(id="naxos", name="Naxos", place="Old Town and the beaches", scene=dict(type="island", caption="07:25 from Piraeus · 5 h 15 min"),
         weather="19 to 27°C · breezy · sea 21°C · sunset about 20:35",
         food=[("The harbour front", "Grilled fish at the tables by the water.", "Naxos Chora harbour restaurants"),
               ("A beach taverna at Plaka beach", "Feet in the sand, long lunch.", "Plaka beach Naxos taverna")],
         days=[
        dict(date="2027-06-07", title="To the island", items=[
            ("step", "06:15", "Taxi to Piraeus, about 25 minutes at that hour."),
            ("transfer", "FERRY1"),
            ("stay", "naxos"),
            ("idea", "Walk out to the marble gate on the islet for sunset."),
        ]),
        dict(date="2027-06-08", title="Beach day", scene="lanterns", scene_caption="Moon over the bay", items=[
            ("idea", "Bus or scooter south to the long sandy beaches."),
            ("pick", "Sunset drinks on the rocks by the marble gate.", "Portara Naxos", "The marble gate at sunset", "Alex"),
            ("note", "Lanterns on the beach after dark."),
        ]),
    ]),
    dict(id="hills", name="The hill villages", place="Inland Naxos", scene=dict(type="mountain", caption="Marble villages"),
         weather="A few degrees cooler than the coast · bring a layer for the ride back", days=[
        dict(date="2027-06-09", title="Up the hills", items=[
            ("step", "09:30", "Pick up the scooter in town. Bring both driving licences."),
            ("idea", "The marble villages, one coffee in each square."),
            ("idea", "The old olive press and the big unfinished statue lying in its quarry."),
            ("note", "Fill the tank before leaving town. There are few pumps inland."),
        ]),
    ]),
    dict(id="santorini", name="Santorini", place="Firostefani, on the rim", scene=dict(type="beach", caption="Sunset about 20:35"),
         weather="20 to 27°C · windy on the rim · sunset about 20:35",
         food=[("Dinner on the rim", "Book a terrace table a week ahead and ask for the edge.", "caldera view restaurant Firostefani"),
               ("A bakery in Fira", "Breakfast pies to eat on the terrace.", "bakery Fira Santorini")],
         days=[
        dict(date="2027-06-10", title="The rim", items=[
            ("step", "12:15", "Check out and walk down to the port."),
            ("transfer", "FERRY2"),
            ("stay", "caldera"),
            ("idea", "Do nothing until the sun goes down."),
        ]),
        dict(date="2027-06-11", title="The anniversary", items=[
            ("idea", "Walk the rim path north in the morning, about three hours with stops."),
            ("pick", "The anniversary dinner, on the rim at sunset.", "caldera view restaurant Firostefani", "Anniversary dinner", "Alex"),
        ]),
    ]),
    dict(id="home", name="Homeward", place="Santorini to London", scene=dict(type="flight", frm="ATH", to="LHR"),
         weather="Athens · 20 to 30°C · London · 12 to 20°C", days=[
        dict(date="2027-06-12", title="Back to the mainland", items=[
            ("step", "11:00", "Check out. One more swim before the taxi."),
            ("step", "16:30", "Transfer to the airport, about 20 minutes."),
            ("flight", "EX440"),
            ("stay", "airport"),
        ]),
        dict(date="2027-06-13", title="Home", items=[
            ("step", "12:30", "Shuttle to the terminal."),
            ("flight", "EX102"),
            ("note", "Home by early evening."),
        ]),
    ]),
]

# Things still to sort before the trip. With opens/until a todo also shows as a "Do this now" card on Today.
TODOS = [
    dict(id="airport-hotel", text="Airport hotel reservation number", sub="Runway Rest Hotel has not sent a confirmation yet. Chase it."),
    dict(id="checkin", text="Check in online for the first flight", sub="Opens 24 hours before departure.", url="https://example.com/checkin",
         opens="2027-06-04", until="2027-06-05", now_title="Online check-in is open", now_body="Check in for EX 101 and save both boarding passes to your phones.", done_label="Both done"),
    dict(id="scooter", text="Book the scooter in Naxos", sub="For Wed 9 Jun. Ask the hotel which rental they trust."),
]

PACKING = [
    ("Documents", ["Passports", "Driving licences, both", "Travel insurance details", "Cards and a little cash"]),
    ("Islands", ["Swimsuits", "Sunscreen", "Hats and sunglasses", "Sandals", "Light layer for the ferry deck"]),
    ("Tech", ["Plug adapter", "Power bank", "Chargers and cables"]),
]

CONTACTS = [
    ("Example Air", "+44 20 0000 0000"),
    ("Example Ferries", "+30 21 0000 0009"),
    ("Emergency (all services)", "112"),
]

# Shown big for a driver: (name in English, name in the local script, smaller second line, phone to match a stay)
TAXI = [
    ("Olive Tree House, Plaka", "Πλάκα, Αθήνα", "κοντά στην Ακρόπολη", "+30 21 0000 0001"),
    ("Piraeus port, gate E7", "Λιμάνι Πειραιά, πύλη Ε7", "", ""),
    ("Athens airport", "Αεροδρόμιο Αθηνών", "αναχωρήσεις (departures)", ""),
    ("Naxos port", "Λιμάνι Νάξου", "", ""),
]

PHRASES_NOTE = "Tap any phrase to show it big."
PHRASES = [
    ("Hello", "Γεια σας", "ya sas"),
    ("Thank you", "Ευχαριστώ", "ef-ha-ri-STO"),
    ("Please / You're welcome", "Παρακαλώ", "pa-ra-ka-LO"),
    ("How much is it?", "Πόσο κάνει;", "PO-so KA-ni"),
    ("The bill, please", "Τον λογαριασμό, παρακαλώ", "ton lo-gha-ria-ZMO, pa-ra-ka-LO"),
    ("Water", "Νερό", "ne-RO"),
    ("Delicious!", "Νόστιμο!", "NO-sti-mo"),
    ("Cheers", "Στην υγειά μας", "stin i-YA mas"),
    ("I love you", "Σ' αγαπώ", "sa-gha-PO"),
]

# Destination money to home money. Give the rate and the day it was looked up; never guess one.
FX = dict(from_name="Euros", from_symbol="€", to_name="Pounds", to_symbol="£", rate=0.85, asof="1 May 2027 (example figure)",
          rule="Quick rule: take off about a seventh.", start=40)

TIPS = [
    "Greece is 2 hours ahead of the UK. Currency is the euro.",
    "Ferries can be delayed or cancelled when the wind is up. Keep the day after a crossing loose.",
    "Paper goes in the bin, not the toilet, almost everywhere on the islands.",
    "Many small shops and tavernas close in the afternoon and reopen in the evening.",
]

# Letters written into the page before the trip, sealed until their day (destination calendar).
# frm: a traveller, or leave out for a letter "from the trip". to: a traveller or "all".
LETTERS = [
    dict(to="all", on="2027-06-12", title="Before you pack",
         text="Tomorrow is suitcases and queues, so tonight is still holiday.\n\nWalk the long way to dinner.\n"
              "Order the thing neither of you can pronounce.\nThen write one line each in Notes about the best hour of this week, and seal it for a year."),
]

# Hidden surprises. Each can be switched off (on=False or leave it out); title and text are optional
# (sensible defaults exist). build.py writes the private how-to-find-them list to SECRETS.md.
SECRETS = dict(
    amp=dict(on=True, title="Alex and Sam",
             text="Three letters shorter as an ampersand, and still the best word on this page.\n\nDinner is on whoever tapped."),
    hold=dict(on=True, chapter="hills", toast="Vroom!", title="Road trip rules",
              text="Driver picks the road. Passenger picks the music and every stop for a view.\n\nNo arguing about either."),
    mascot=dict(on=True, chapter="naxos", title="Spotted by the pineapple",
                text="Official island business: you are hereby ordered to do nothing at all until at least four o'clock.\n\nSigned, the management."),
    moon=dict(on=True, date="2027-06-08", label="The moon", wish="Look up.", title="Night swim",
              text="The sea is warmest after dark.\n\nShoes off, phones in the bag, ten minutes in the water. Go."),
    code=dict(on=True, value="1106", title="Ten years",
              text="You typed the date. Good memory.\n\nThat is the anniversary, so tonight the bill does not get converted."),
    phrase=dict(on=True, phrase="I love you"),
    flower=dict(on=True, title="The small print",
                text="Built over a few evenings while one of you was asleep on the sofa.\n\nHappy anniversary, Sam."),
)

# Changes to the starting lists after the page was first opened by the travellers (see references/collaboration.md).
SEED_PATCHES = []
