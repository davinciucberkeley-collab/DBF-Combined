"""A2 crash-reserve re-base for the D-180 cost set (2026-11-14). Prints; writes nothing.
Basis = A2 closure 2.4: CDR B3 bad-crash list (pack, ESC, motor, servo, fin tube, core and tape), net of the spares still in
the BOM, pessimistic prices x 1.1025 (10.25 % tax, COST-TRADE section 1) + one shipment 10.71.
Run: python -I redesign/team/A2/crash_rebase_2026-11-14.py"""
TAX, SHIP = 1.1025, 10.71
CASES = {
  # item: (pre-tax $, spared in the BOM?)  source
  "A2 closure 2.4 (stale, 2 Ovonic-class packs, 5th motor, 2nd ESC pack, 48 in tube)":
      {"pack": 65.72, "ESC 4-pack": 0, "motor": 0, "servo": 41.99, "fin tube": 0, "core/tape": 0},
  "D-180 set, CNHL 6000 120C $69.99 (fails E2/A3)":
      {"pack": 69.99, "ESC 4-pack": 30.00, "motor": 39.99, "servo": 41.99, "fin tube": 118.97, "core/tape": 0},
  "D-180 set, CNHL Shorty 130C $99.99 (passes on paper)":
      {"pack": 99.99, "ESC 4-pack": 30.00, "motor": 39.99, "servo": 41.99, "fin tube": 118.97, "core/tape": 0},
  "D-180 set, Gens Ace Shorty $131.99":
      {"pack": 131.99, "ESC 4-pack": 30.00, "motor": 39.99, "servo": 41.99, "fin tube": 118.97, "core/tape": 0},
}
for name, items in CASES.items():
    pre = sum(items.values())
    print(f"{name}: pre-tax {pre:.2f} -> {pre*TAX + SHIP:.2f}")
print("\nsingle-class repair (pre-tax x tax + one shipment):")
for k, v in CASES["D-180 set, CNHL Shorty 130C $99.99 (passes on paper)"].items():
    if v: print(f"   {k:11s} {v*TAX + SHIP:7.2f}")
SET_CNHL6000 = 1847.99                      # COST-TRADE section 3, recommended set before any reserve
shorty = SET_CNHL6000 + (99.99 - 69.99) * TAX
caps = 13 * 3.03 * TAX - 9 * 3.03 * TAX     # F1: 9 caps fail CL-F1-CAP-I-TRANS; 13 stay
print(f"\nset with CNHL Shorty {shorty:.2f}; + caps kept at 13 (+{caps:.2f}) = {shorty+caps:.2f}; headroom to 2,000 = {2000-shorty-caps:.2f}")
for lab, r in (("stale 130", 130.0), ("re-based B3 bill", 99.99*0+ (99.99+30+39.99+41.99+118.97)*TAX+SHIP)):
    print(f"   + reserve {lab} {r:.2f} -> {shorty+caps+r:.2f}  (over by {shorty+caps+r-2000:+.2f})")
