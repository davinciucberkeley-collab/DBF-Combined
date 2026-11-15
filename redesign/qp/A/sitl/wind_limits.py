"""QP-2 WIND: flyable RFS-proxy mornings Jan-Apr vs hover wind limit. stdlib only. Run: python -I wind_limits.py
Data: config-study/tiebreak/wind/data/rcmc1_YYYY.txt (NDBC RCMC1 Richmond, 6-min, UTC, WSPD 2-min mean, GST gust, 99 = missing; 7.2 m anemometer,
read there 2026-11-09), 2022-2025. Same method as wind_stats.py (local hour bins, 07-10 window = hours 7,8,9, days with < 3 valid hours dropped),
months extended to January. Criterion B = every hour 07-10 has mean <= limit AND gust <= gust limit. No height or RFS/RCMC1 ratio is applied (ratio unmeasured, H3 R-WIND-MEASURE)."""
import datetime as dt, os, sys
from collections import defaultdict
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "config-study", "tiebreak", "wind", "data")
def nth_sun(y, m, n):
    d = dt.date(y, m, 1); d += dt.timedelta(days=(6 - d.weekday()) % 7); return d + dt.timedelta(weeks=n - 1)
def loc(t):
    s = dt.datetime.combine(nth_sun(t.year, 3, 2), dt.time(10)); e = dt.datetime.combine(nth_sun(t.year, 11, 1), dt.time(9))
    return t + dt.timedelta(hours=-7 if s <= t < e else -8)
hrs = defaultdict(lambda: [[], []])
for y in (2022, 2023, 2024, 2025):
    for ln in open(os.path.join(D, "rcmc1_%d.txt" % y)):
        if ln.startswith("#"): continue
        p = ln.split()
        if len(p) < 8: continue
        t = loc(dt.datetime(*[int(x) for x in p[:5]]))
        if t.month > 4: continue
        w, g = float(p[6]), float(p[7])
        if w < 90: hrs[(t.date(), t.hour)][0].append(w)
        if g < 90: hrs[(t.date(), t.hour)][1].append(g)
H = {k: (sum(w) / len(w), max(g) if g else None) for k, (w, g) in hrs.items() if w}
days = sorted({d for d, h in H})
def ok(d, lim, glim):
    v = [H[(d, h)] for h in (7, 8, 9) if (d, h) in H]
    if len(v) < 3: return None
    return all(m <= lim and (g is None or g <= glim) for m, g in v)
def rate(months, lim, glim, years=(2022, 2023, 2024, 2025)):
    r = [ok(d, lim, glim) for d in days if d.month in months and d.year in years]
    r = [x for x in r if x is not None]; return sum(r) / len(r), len(r)
cases = [("5 m/s, gust 8", 5.0, 8.0), ("4 m/s, gust 6.4", 4.0, 6.4), ("4 m/s, gust 8", 4.0, 8.0), ("3 m/s, gust 5", 3.0, 5.0)]
out = []
out.append("limit | Jan | Feb | Mar | Apr | Jan-Apr | worst year Jan-Apr | Feb-Apr | Mar-Apr  (fraction of mornings; x7 = per week)")
for n, lim, gl in cases:
    row = [rate((m,), lim, gl)[0] for m in (1, 2, 3, 4)]
    allr = rate((1, 2, 3, 4), lim, gl)[0]; wy = min(rate((1, 2, 3, 4), lim, gl, (y,))[0] for y in (2022, 2023, 2024, 2025))
    out.append("%s | %s | %.2f | %.2f | %.2f | %.2f" % (n, " | ".join("%.2f" % x for x in row), allr, wy, rate((2, 3, 4), lim, gl)[0], rate((3, 4), lim, gl)[0]))
out.append("")
# blocks of H2 FLIGHT-TEST-PLAN section 6 (dates 2027): F01 12-14 Feb, F02 15-22 Feb, F03 23 Feb-3 Mar, F04 4-10 Mar, F05 22 Mar-2 Apr, F06 3-18 Apr
blocks = [("F01", 2, 3, 2), ("F02", 2, 8, 5), ("F03", 2, 9, 4), ("F04", 3, 7, 3), ("F05", 3, 12, 5), ("F06", 4, 16, 3)]
# block month weights for blocks that straddle: F03 = 6 days Feb + 3 Mar, F05 = 10 days Mar + 2 Apr
split = {"F03": ((2, 6), (3, 3)), "F05": ((3, 10), (4, 2))}
out.append("block | days | needed | " + " | ".join("%s: all-yr / worst-yr days" % c[0] for c in cases))
for b, m, nd, need in blocks:
    parts = split.get(b, ((m, nd),))
    cells = []
    for n, lim, gl in cases:
        a = sum(rate((mm,), lim, gl)[0] * dd for mm, dd in parts)
        w = sum(min(rate((mm,), lim, gl, (y,))[0] for y in (2022, 2023, 2024, 2025)) * dd for mm, dd in parts)
        cells.append("%.1f / %.1f" % (a, w))
    out.append("%s | %d | %d | %s" % (b, nd, need, " | ".join(cells)))
print("\n".join(out))
# slip: days a block needs = needed mornings / (usable mornings per day in the block) minus the block's days; summed over F01-F06 (EST; blocks run back to back)
out = ["", "slip (calendar days added to F01-F06 vs the 12 d I2 slack, which already holds CR1): all-year / worst-year-per-month"]
for n, lim, gl in cases:
    tot_a = tot_w = 0.0
    for b, m, nd, need in blocks:
        parts = split.get(b, ((m, nd),))
        a = sum(rate((mm,), lim, gl)[0] * dd for mm, dd in parts); w = sum(min(rate((mm,), lim, gl, (y,))[0] for y in (2022, 2023, 2024, 2025)) * dd for mm, dd in parts)
        tot_a += max(0.0, need * nd / a - nd); tot_w += max(0.0, need * nd / w - nd)
    out.append("%s | %.1f d / %.1f d" % (n, tot_a, tot_w))
print("\n".join(out))
