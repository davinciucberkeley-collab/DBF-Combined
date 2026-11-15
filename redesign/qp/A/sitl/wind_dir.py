"""QP-2 WIND: how steady is the RCMC1 wind direction in the 07-10 window when the mean is <= 5 m/s? (stdlib; run python -I wind_dir.py)
Over each 30 min block (5 consecutive 6-min records) the circular range of WDIR, for records with 2-min mean 2-5 m/s, Jan-Apr 2022-2025 (same data as wind_limits.py).
Below 2 m/s direction is unreliable and no heading rule is needed (wind lean < 5 deg in the plant). Edge-on window half-widths tested: 10, 15, 20 deg."""
import datetime as dt, os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "config-study", "tiebreak", "wind", "data")
def nth_sun(y, m, n):
    d = dt.date(y, m, 1); d += dt.timedelta(days=(6 - d.weekday()) % 7); return d + dt.timedelta(weeks=n - 1)
def loc(t):
    s = dt.datetime.combine(nth_sun(t.year, 3, 2), dt.time(10)); e = dt.datetime.combine(nth_sun(t.year, 11, 1), dt.time(9))
    return t + dt.timedelta(hours=-7 if s <= t < e else -8)
rec = []
for y in (2022, 2023, 2024, 2025):
    for ln in open(os.path.join(D, "rcmc1_%d.txt" % y)):
        if ln.startswith("#"): continue
        p = ln.split()
        if len(p) < 8: continue
        t = loc(dt.datetime(*[int(x) for x in p[:5]]))
        if t.month > 4 or not 7 <= t.hour < 10: continue
        rec.append((t, float(p[5]), float(p[6])))
rec.sort()
def crange(a):
    best = 360.0
    for s in a:
        r = max((x - s) % 360 for x in a); best = min(best, r)
    return best
blocks = []
for i in range(0, len(rec) - 4):
    w = rec[i:i + 5]
    if (w[-1][0] - w[0][0]) != dt.timedelta(minutes=24): continue
    if any(x[1] > 360 or x[2] > 90 or not 2.0 <= x[2] <= 5.0 for x in w): continue
    blocks.append(crange([x[1] for x in w]))
n = len(blocks); print("30 min blocks, mean 2-5 m/s, 07-10, Jan-Apr 2022-25: n =", n)
for hw in (10, 15, 20): print("direction range <= %d deg (a fixed heading stays inside +-%d): %.0f %%" % (2 * hw, hw, 100.0 * sum(1 for b in blocks if b <= 2 * hw) / n))
