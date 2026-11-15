"""Cost of candidate T chosen parts on the RESTUDY-2026-11-14 basis (floor 744.02 includes its own tax, 7 shipments, FAA).
Run: python -I cost_T.py   (prices: see SIZING-T.md section 7; U = unverified snippet, V = vendor page read 2026-11-14)"""
TAX, SHIP = 0.1025, 10.71
FLOOR_TOTAL, FLOOR_GOODS = 744.02, 602.31
CHOSEN = [  # item, qty, unit, vendor, tag
    ("T-Motor AT2317 KV880 (3 + 1 spare)", 4, 39.99, "T-Motor store", "V"),
    ("APC 11x5.5E props (3 + 5 spare; CW-prop fix open)", 8, 4.17, "APC", "V"),
    ("LANRC 45 A ESC 4-pack", 1, 30.00, "Amazon", "U"),
    ("Powerhobby 329TG tilt servo (2 + 1 spare)", 3, 27.95, "WREKD", "U (K06 card 2026-11-09)"),
    ("Tilt pivots 6 mm shaft + bearings + collars", 1, 12.00, "Amazon", "EST"),
    ("Tilt bench-rig extras", 1, 10.00, "Amazon", "EST"),
    ("CNHL Black 4S 2200 mAh 40C packs, priced pessimistically at $25 (listing $17.99)", 2, 25.00, "chinahobbyline", "U"),
    ("XPS 2 in sheet (HD pickup, no shipping)", 1, 59.97, "Home Depot", "U (K06 cost.csv)"),
    ("CF tubes 20x18 / 18x16 (about 2 x 1 m)", 2, 28.32, "Amazon", "U (K06 cost.csv)"),
    ("PETG 4 kg spool", 1, 39.99, "Amazon", "U (K06 cost.csv)"),
    ("Packing tape, foam glue, foam board", 1, 38.97, "Amazon/Dollar Tree", "U (K06 cost.csv)"),
    ("AS150U anti-spark + leads (70 A all-out)", 1, 15.00, "Amazon", "EST"),
]
SHIPMENTS = 5  # T-Motor, APC, WREKD, chinahobbyline, Amazon (HD pickup free)
goods = sum(q * u for _, q, u, *_ in CHOSEN)
tax = goods * TAX
ship = SHIPMENTS * SHIP
chosen = goods + tax + ship
total = FLOOR_TOTAL + chosen
# crash reserve rule: (one flight pack + one servo + one replacement wing/airframe set) x 1.1025 + 2 shipments
airframe_set = 70.0  # EST: foam, spar tube, tape, PETG share
reserve = (25.0 + 27.95 + airframe_set) * 1.1025 + 2 * SHIP
if __name__ == "__main__":
    for n, q, u, v, t in CHOSEN:
        print(f"| {n} | {q} | {u:.2f} | {q * u:.2f} | {v} | {t} |")
    print(f"goods {goods:.2f} tax {tax:.2f} ship {ship:.2f} chosen {chosen:.2f}")
    print(f"floor {FLOOR_TOTAL:.2f} + chosen = {total:.2f}; reserve {reserve:.2f}; all-in {total + reserve:.2f}; margin {2000 - total - reserve:.2f}")
    print(f"chosen +30 %: margin {2000 - total - reserve - 0.3 * chosen:.2f}")
