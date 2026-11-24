"""Concept A schedule model (I2).  Reproduce: python -I schedule_a.py  (stdlib; prints markdown; writes nothing)
Every input is an EST except the cited ones.  Flight programme = H2 gates F01-F06 (team/H2/FLIGHT-TEST-PLAN.md s6 mornings: 2,5,4,3,5,3 = 22).
A morning is flown with p = P_FLY (DECISION.md l.175: 72-81 % of mornings booked 7 d ahead are flyable; low end used; RFS wind not yet
measured, WIND-RFS.md 0 of 3).  Booked mornings per week is the team's choice; RECESS (22-26 Mar) books +1."""
from datetime import date, timedelta as td
DEADLINE = date(2027, 4, 30)
GATES = [("F01 tethered hover", 2), ("F02 free hover + landing practice", 5), ("F03 fixed-wing tune", 4),
         ("F04 first transition + back-transition", 3), ("F05 round trips + landing practice", 5), ("F06 full missions", 3)]
REPAIR_DAYS, REDO = 11, 3          # crash loop after F04: 11 d (K09-L CR1 10.5 d rounded up, I2-R2) then F04 repeated (3 mornings)
RECESS = (date(2027, 3, 22), date(2027, 3, 26))
# --- AM-037 (2026-11-23, T-103, D-248 or later): no fabrication before Jacobs reopens; orders from 1-4 Dec -------------------------
REOPEN = date(2027, 1, 19)         # spring instruction begins Tue 19 Jan 2027 (Registrar UCB_AcademicCalendar_2026-27_a11y.pdf, read 2026-11-23); Jacobs
                                   # spring reopening date itself is NOT published (jacobsinstitute.berkeley.edu/making-at-jacobs/ read 2026-11-23): assumed = 19 Jan
HOLIDAY = date(2027, 2, 15)        # Presidents' Day (Registrar); no Jacobs / lab work assumed
HOURS = dict(bench="TP-1/TP-2 stand build + prints + solder + campaign: 12 h EST (no source; was inside 'B0')",
             precut=8.5, b1=30.0, b2=14.5, checks=12.0)   # 8.5 / 30 / 14.5 / 12 h: SCHEDULE-A Basis (K09-L 82 h x 0.65 = 53 h, EST)
BENCH_H = 12.0
RATE = 21.0                        # team hours per week in spring (20-22 h/wk EST, SCHEDULE-A Basis)
MAIN_LEAD = 7                      # d, RMRC / Amazon 5-7 d (K09-L ORDER-PLAN), EST; Zoro / Carbonwebshop "-"
def f01_start(rate=RATE, scale=1.0, main_after_bench=False):
    """first tethered-hover Monday-or-later date. Hours are worked in sequence from REOPEN (team-hour limited);
    if main_after_bench the build (B1-B3) cannot start before bench decision + MAIN_LEAD."""
    bench_h = (BENCH_H + HOURS["precut"]) * scale
    build_h = (HOURS["b1"] + HOURS["b2"] + HOURS["checks"]) * scale
    t_bench = REOPEN + td(days=round(7 * bench_h / rate))
    if main_after_bench:
        gng = REOPEN + td(days=10)                 # decision Fri 29 Jan 2027 (bench stand, print, solder, 2 test days)
        start = max(t_bench, gng + td(days=MAIN_LEAD))
        d = start + td(days=round(7 * build_h / rate))
    else:
        d = REOPEN + td(days=round(7 * (bench_h + build_h) / rate))
    if d <= HOLIDAY <= d + td(days=1): d = HOLIDAY + td(days=1)
    return d
def rate(d, booked, p):
    wk_end = d + td(days=6)
    b = booked + (1 if RECESS[0] <= d <= RECESS[1] else 0)
    return b * p
def advance(d, need, booked, p):
    """date when `need` more flown mornings are done, starting at date d (Monday-based weekly rate, linear within week)"""
    while need > 0:
        r = rate(d, booked, p)
        if need <= r: return d + td(days=round(7 * need / r))
        need -= r; d += td(days=7)
    return d
def run(start, booked, p, crash):
    d, out = start, []
    for name, n in GATES:
        s = d
        d = advance(d, n, booked, p)
        out.append((name, s, d))
        if crash and name.startswith("F04"):
            out.append(("CR1 crash repair", d, d + td(days=REPAIR_DAYS))); d += td(days=REPAIR_DAYS)
            s = d; d = advance(d, REDO, booked, p); out.append(("F04 redo", s, d))
    return out
def latest_start(booked, p, crash):
    s = date(2027, 2, 8)
    while run(s, booked, p, crash)[-1][2] > DEADLINE: s -= td(days=1)
    while run(s + td(days=1), booked, p, crash)[-1][2] <= DEADLINE: s += td(days=1)
    return s
if __name__ == "__main__":
    S = f01_start()
    print("Pre-AM-037 plan start of F01 was 2027-02-08 (fabrication in December).  AM-037 plan: fabrication from", REOPEN)
    print("F01 start, hours chain (no main-order wait):", f01_start(), "| main order after bench:", f01_start(main_after_bench=True),
          "| 28 h/wk week 1-3 team:", f01_start(rate=28), "| 18 h/wk:", f01_start(rate=18), "| hours x1.23 (66 h scale):", f01_start(scale=66/53))
    print("Plan start of F01 (first tethered hover week):", S)
    print("\n| Booked mornings/wk | p fly | Crash loop | F06 ends | Slack to 30 Apr (d) | Latest-safe F01 start |\n|---|---|---|---|---|---|")
    for booked in (2, 3, 4, 5):
        for p in (0.72, 0.60):
            for crash in (False, True):
                e = run(S, booked, p, crash)[-1][2]
                print(f"| {booked} | {p} | {'yes' if crash else 'no'} | {e:%d %b} | {(DEADLINE-e).days:+d} | {latest_start(booked,p,crash):%d %b} |")
    print("\nBaseline (4 booked, p 0.72, one crash):")
    for n, s, e in run(S, 4, 0.72, True): print(f"- {n}: {s:%d %b} - {e:%d %b}")
    print("\nBaseline (3 booked, p 0.72, one crash):")
    for n, s, e in run(S, 3, 0.72, True): print(f"- {n}: {s:%d %b} - {e:%d %b}")
    print("\nBaseline (4 booked, p 0.72, one crash) with F01 start of the main-order-after-bench option:")
    for n, s_, e in run(f01_start(main_after_bench=True), 4, 0.72, True): print(f"- {n}: {s_:%d %b} - {e:%d %b}")
    print("\nSlack by option / sensitivity (F01 start, 4 booked, p 0.72, one crash unless stated):")
    for lab, st, b, p, c in (("hours chain, baseline", f01_start(), 4, 0.72, True),
                              ("main order after bench", f01_start(main_after_bench=True), 4, 0.72, True),
                              ("p 0.60", f01_start(), 4, 0.60, True), ("3 mornings/wk", f01_start(), 3, 0.72, True),
                              ("5 mornings/wk", f01_start(), 5, 0.72, True), ("5 mornings/wk, p 0.60", f01_start(), 5, 0.60, True),
                              ("no crash", f01_start(), 4, 0.72, False), ("28 h/wk", f01_start(rate=28), 4, 0.72, True),
                              ("hours x1.25", f01_start(scale=1.25), 4, 0.72, True), ("hours x0.8", f01_start(scale=0.8), 4, 0.72, True)):
        e = run(st, b, p, c)[-1][2]
        print(f"| {lab} | F01 {st:%d %b} | F06 {e:%d %b} | {(DEADLINE-e).days:+d} d |")
    print("Latest-safe F01 start (4, 0.72, crash):", latest_start(4, 0.72, True))
