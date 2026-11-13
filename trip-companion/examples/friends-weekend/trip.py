"""EXAMPLE TRIP, the smallest useful one. Everything here is invented.

Three friends, a long weekend, one flight and one stay known so far. Romance off, no secrets, no documents,
no transfers, no phrases, no money converter: the page simply leaves those parts out.
Build with:  python3 ../../templates/build.py trip.py
"""

TRIP = dict(
    title="Lisbon",
    theme="lagoon",
    romance=False,                      # friends: stars instead of hearts, plain wording, notes between everyone
    tz="Europe/Lisbon",
    home_tz="Europe/Dublin",
    home="DUB",
)

TRAVELLERS = ["Ana", "Ben", "Chloe"]

PLACES = {
    "DUB": dict(name="Dublin", lat=53.4264, lon=-6.2499, tz="Europe/Dublin"),
    "LIS": dict(name="Lisbon", lat=38.7742, lon=-9.1342),
}

FLIGHTS = {
    "EX201": dict(airline="Example Air", num="EX 201", frm="DUB", to="LIS", date="2027-09-17", dep="06:50", arr="09:40", ref="GHI789"),
}

STAYS = {
    "flat": dict(name="The Tile House flat", short="Lisbon", place="Lisbon · Alfama", check_in="2027-09-17", check_out="2027-09-20",
                 cin="from 15:00", cout="by 10:00", ref="DEMO-0100", phone="+351 21 000 0000"),
}

CHAPTERS = [
    dict(id="lisbon", name="Lisbon", place="Alfama and the river", scene=dict(type="city", sticker="tram", outline="bridge"), days=[
        dict(date="2027-09-17", title="Arrive", items=[
            ("flight", "EX201"),
            ("stay", "flat"),
            ("idea", "Custard tarts first, everything else after."),
        ]),
        dict(date="2027-09-18", title="Hills and trams", items=[
            ("idea", "Ride the old tram up the hill and walk back down."),
            ("pick", "The viewpoint at sunset.", "Miradouro da Senhora do Monte Lisbon", "Sunset viewpoint", "Chloe"),
        ]),
        dict(date="2027-09-19", title="The river", items=[
            ("idea", "Out along the river to the tower and the monastery."),
        ]),
        dict(date="2027-09-20", title="Home", items=[
            ("note", "The flight home is not booked yet."),
        ]),
    ]),
]

TODOS = [
    dict(id="flight-home", text="Book the flight home", sub="Mon 20 Sep, any time after lunch."),
]
