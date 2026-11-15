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
    S = date(2027, 2, 8)
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
