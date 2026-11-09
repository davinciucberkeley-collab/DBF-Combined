"""Wind statistics for the Richmond Field Station (RFS) flight window.

Run:  python -I wind_stats.py data   (stdlib only)

Inputs (in the data folder, downloaded 2026-11-09):
  rcmc1_YYYY.txt / aamc1_YYYY.txt  NDBC historical stdmet, 6-min records, UTC,
      WSPD = 2-min mean wind (m/s), GST = peak gust (m/s), 99.0 = missing.
      RCMC1 = NOS PORTS 9414863 Richmond, CA, 37.923 N 122.410 W, anemometer 7.2 m.
      AAMC1 = NOS PORTS 9414750 Alameda, CA, 37.772 N 122.300 W, anemometer 6.9 m.
  asos_OAK.csv / asos_SFO.csv  Iowa Environmental Mesonet ASOS, local time,
      sknt = 2-min mean wind (kt), gust (kt) only reported when gusty (M otherwise).

Method:
  * Every record is put in a local-time hour bin (US Pacific, DST applied by rule).
  * Hourly mean wind = mean of all WSPD samples in the hour (NDBC: up to 10 samples);
    ASOS: the routine/special reports in that hour (usually 1).
  * Hourly gust = max GST in the hour (NDBC). ASOS: max reported gust, or the
    mean wind if no gust was reported (ASOS only reports gusts >= ~10 kt peaks).
  * Windows: 07-10 = hours starting 07, 08, 09; 10-13 = 10, 11, 12; 13-17 = 13..16.
  * Months Feb, Mar, Apr; years 2022-2025.
  * A "usable morning" (day-level) is evaluated over the 07-10 window, several ways:
      A  every hour 07-10 has mean <= 5 m/s
      B  every hour 07-10 has mean <= 5 m/s AND gust <= 8 m/s
      C  at least one hour in 07-10 has mean <= 5 m/s AND gust <= 8 m/s
      D  at least 2 consecutive hours in 07-11 with mean <= 5 m/s and gust <= 8 m/s
    Days with fewer than 3 valid hours in 07-10 are dropped.
"""
import csv
import datetime as dt
import os
import sys
from collections import defaultdict

KT = 0.514444
MONTHS = {2: "Feb", 3: "Mar", 4: "Apr"}
WINDOWS = [("07-10", range(7, 10)), ("10-13", range(10, 13)), ("13-17", range(13, 17))]


def nth_sunday(year, month, n):
    d = dt.date(year, month, 1)
    d += dt.timedelta(days=(6 - d.weekday()) % 7)
    return d + dt.timedelta(weeks=n - 1)


def utc_to_pacific(t):
    """US rule since 2007: DST from 2nd Sun Mar 02:00 PST (10:00 UTC) to 1st Sun Nov 02:00 PDT (09:00 UTC)."""
    y = t.year
    start = dt.datetime.combine(nth_sunday(y, 3, 2), dt.time(10))
    end = dt.datetime.combine(nth_sunday(y, 11, 1), dt.time(9))
    off = -7 if start <= t < end else -8
    return t + dt.timedelta(hours=off)


def load_ndbc(folder, prefix):
    hours = defaultdict(lambda: [[], []])  # (date, hour) -> [speeds], [gusts]
    for fn in sorted(os.listdir(folder)):
        if not (fn.startswith(prefix + "_") and fn.endswith(".txt")):
            continue
        with open(os.path.join(folder, fn)) as f:
            for line in f:
                if line.startswith("#"):
                    continue
                p = line.split()
                if len(p) < 8:
                    continue
                t = dt.datetime(int(p[0]), int(p[1]), int(p[2]), int(p[3]), int(p[4]))
                lt = utc_to_pacific(t)
                if lt.month not in MONTHS:
                    continue
                key = (lt.date(), lt.hour)
                ws, gs = float(p[6]), float(p[7])
                if ws < 90:
                    hours[key][0].append(ws)
                if gs < 90:
                    hours[key][1].append(gs)
    out = {}
    for k, (w, g) in hours.items():
        if w:
            out[k] = (sum(w) / len(w), max(g) if g else None)
    return out


def load_asos(path):
    hours = defaultdict(lambda: [[], []])
    with open(path) as f:
        for row in csv.DictReader(f):
            if row["sknt"] in ("M", ""):
                continue
            lt = dt.datetime.strptime(row["valid"], "%Y-%m-%d %H:%M")
            if lt.month not in MONTHS:
                continue
            key = (lt.date(), lt.hour)
            w = float(row["sknt"]) * KT
            hours[key][0].append(w)
            g = row["gust"]
            hours[key][1].append(float(g) * KT if g not in ("M", "") else w)
    return {k: (sum(w) / len(w), max(g)) for k, (w, g) in hours.items() if w}


def pct(x, n):
    return 100.0 * x / n if n else float("nan")


def percentile(vals, q):
    v = sorted(vals)
    if not v:
        return float("nan")
    i = min(len(v) - 1, max(0, int(round(q * (len(v) - 1)))))
    return v[i]


def window_table(data, name):
    lines = [f"\n## {name}: hourly statistics by month and local window",
             "month | window | n hours | mean m/s | median m/s | P90 m/s | <=5 m/s % | <=8 m/s % | "
             "median gust m/s | P90 gust m/s | (<=5 mean & <=8 gust) %"]
    for mset, mname in [((2,), "Feb"), ((3,), "Mar"), ((4,), "Apr"), ((3, 4), "Mar-Apr")]:
        for wname, hrs in WINDOWS:
            sel = [v for (d, h), v in data.items() if d.month in mset and h in hrs]
            w = [s for s, g in sel]
            g = [gg for s, gg in sel if gg is not None]
            ok = sum(1 for s, gg in sel if s <= 5 and (gg is None or gg <= 8))
            n = len(w)
            lines.append(
                f"{mname} | {wname} | {n} | {sum(w)/n:.1f} | {percentile(w,.5):.1f} | {percentile(w,.9):.1f} | "
                f"{pct(sum(1 for s in w if s <= 5), n):.0f} | {pct(sum(1 for s in w if s <= 8), n):.0f} | "
                f"{percentile(g,.5):.1f} | {percentile(g,.9):.1f} | {pct(ok, n):.0f}")
    return lines


def mornings(data, name, limit=5.0, glimit=8.0):
    days = defaultdict(dict)
    for (d, h), v in data.items():
        if 7 <= h <= 10:
            days[d][h] = v
    res = defaultdict(lambda: [0, 0, 0, 0, 0])  # n, A, B, C, D
    for d, hs in days.items():
        core = [hs[h] for h in (7, 8, 9) if h in hs]
        if len(core) < 3 or d.month not in (3, 4):
            continue
        ok = lambda v: v[0] <= limit and (v[1] is None or v[1] <= glimit)
        r = res[d.month]
        r[0] += 1
        r[1] += all(s <= limit for s, g in core)
        r[2] += all(ok(v) for v in core)
        r[3] += any(ok(v) for v in core)
        r[4] += any(h in hs and h + 1 in hs and ok(hs[h]) and ok(hs[h + 1]) for h in (7, 8, 9))
    lines = [f"\n## {name}: usable mornings (Mar-Apr), limit mean <= {limit} m/s, gust <= {glimit} m/s",
             "month | days | A all 07-10 mean<=lim | B all 07-10 mean&gust ok | C any hour 07-10 ok | "
             "D 2 consecutive ok hours 07-11 | A,B,C,D as mornings/week (x7)"]
    tot = [0] * 5
    for m in (3, 4):
        r = res[m]
        tot = [a + b for a, b in zip(tot, r)]
        lines.append(f"{MONTHS[m]} | {r[0]} | " + " | ".join(f"{pct(x, r[0]):.0f}%" for x in r[1:]) +
                     " | " + ", ".join(f"{7*x/r[0]:.1f}" for x in r[1:]))
    lines.append(f"Mar-Apr | {tot[0]} | " + " | ".join(f"{pct(x, tot[0]):.0f}%" for x in tot[1:]) +
                 " | " + ", ".join(f"{7*x/tot[0]:.1f}" for x in tot[1:]))
    # year-to-year spread of criterion B (all 07-10 hours ok), Mar-Apr
    by_year = defaultdict(lambda: [0, 0])
    for d, hs in days.items():
        core = [hs[h] for h in (7, 8, 9) if h in hs]
        if len(core) < 3 or d.month not in (3, 4):
            continue
        by_year[d.year][0] += 1
        by_year[d.year][1] += all(s <= limit and (g is None or g <= glimit) for s, g in core)
    lines.append("criterion B by year (mornings/week): " +
                 ", ".join(f"{y}: {7*b/n:.1f}" for y, (n, b) in sorted(by_year.items())))
    return lines


def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else "data"
    sets = [
        ("RCMC1 Richmond (NOS 9414863), 2022-2025", load_ndbc(folder, "rcmc1")),
        ("AAMC1 Alameda (NOS 9414750), 2022-2025", load_ndbc(folder, "aamc1")),
        ("KOAK Oakland airport ASOS, 2022-2025", load_asos(os.path.join(folder, "asos_OAK.csv"))),
        ("KSFO San Francisco airport ASOS, 2022-2025", load_asos(os.path.join(folder, "asos_SFO.csv"))),
    ]
    out = []
    for name, data in sets:
        out += window_table(data, name)
        out += mornings(data, name, 5.0, 8.0)
        out += mornings(data, name, 8.0, 12.0)
    text = "\n".join(out)
    print(text)
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "wind_stats_output.txt"), "w") as f:
        f.write(text + "\n")


if __name__ == "__main__":
    main()
