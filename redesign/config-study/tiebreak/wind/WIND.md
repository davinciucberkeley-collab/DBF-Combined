# Wind at the test site (Richmond Field Station), February–April

Written 2026-11-09 for the K09 vs K01 tie-break (README §4.3, open question 9). All numbers below come from
`wind_stats.py` run on the raw files in `data/` with `python -I wind_stats.py data`. The full output is in
`wind_stats_output.txt`. Hours are local (Pacific, DST applied). "Mean" is the hourly mean of the station's 2-minute
average wind. "Gust" is the highest gust reported in that hour.

## 1. Answer

**With a 5 m/s mean / 8 m/s gust limit, March–April gives about 5 to 6 usable flight mornings per week**
(07:00–10:00 all inside the limit). The nearest station, Richmond RCMC1, gives 5.7 per week. Oakland airport
(KOAK), the conservative bound, gives 5.0. In the worst year since 2022 the figure was 5.0 at RCMC1 and 4.6 at KOAK.
On weekdays only, that is about **4 mornings out of 5**. Measured wind does **not** rule out a 5 m/s flight-card
limit, so README §4.3's flip condition ("RFS morning wind > 5 m/s on most days") is **not met**.
Afternoons are a different matter. At KOAK only 27 % of hours from 13:00 to 17:00 in March–April are ≤ 5 m/s, so
plan K09 as a morning aircraft. These counts leave out rain (see §5).

## 2. Tables (2022–2025, all hours with data)

### 2a. Hourly wind by month and time of day

Columns: mean wind; % of hours with mean ≤ 5 m/s; % with mean ≤ 8 m/s; median / 90th-percentile hourly gust;
% of hours inside the flight-card limit (mean ≤ 5 **and** gust ≤ 8).

**RCMC1 Richmond (NOS 9414863), about 7 km west of RFS, anemometer 7.2 m, on the harbor shore**

| Month | Window | Mean m/s | ≤ 5 m/s | ≤ 8 m/s | Gust med / P90 m/s | Inside 5/8 limit |
|---|---|---|---|---|---|---|
| Feb | 07–10 | 3.0 | 89 % | 98 % | 4.9 / 9.1 | 85 % |
| Feb | 10–13 | 3.2 | 86 % | 95 % | 4.8 / 9.4 | 81 % |
| Feb | 13–17 | 3.4 | 79 % | 95 % | 4.6 / 12.1 | 75 % |
| Mar | 07–10 | 2.8 | 89 % | 98 % | 4.4 / 9.5 | 84 % |
| Mar | 10–13 | 3.2 | 85 % | 97 % | 5.0 / 9.9 | 79 % |
| Mar | 13–17 | 3.4 | 83 % | 98 % | 5.8 / 10.6 | 76 % |
| Apr | 07–10 | 2.3 | 95 % | 99 % | 3.9 / 7.6 | 92 % |
| Apr | 10–13 | 2.8 | 95 % | 98 % | 4.7 / 7.4 | 92 % |
| Apr | 13–17 | 3.2 | 90 % | 99 % | 5.4 / 9.0 | 84 % |

**KOAK Oakland airport ASOS, about 18 km SSE of RFS, 10 m mast in open exposure (conservative bound)**

| Month | Window | Mean m/s | ≤ 5 m/s | ≤ 8 m/s | Gust med / P90 m/s* | Inside 5/8 limit |
|---|---|---|---|---|---|---|
| Feb | 07–10 | 3.0 | 79 % | 95 % | 2.6 / 7.7 | 79 % |
| Feb | 10–13 | 4.2 | 69 % | 91 % | 3.1 / 12.9 | 68 % |
| Feb | 13–17 | 5.0 | 59 % | 85 % | 4.1 / 14.4 | 59 % |
| Mar | 07–10 | 3.4 | 78 % | 95 % | 3.1 / 7.2 | 78 % |
| Mar | 10–13 | 4.5 | 67 % | 90 % | 3.6 / 13.4 | 67 % |
| Mar | 13–17 | 6.1 | 33 % | 81 % | 6.2 / 15.4 | 33 % |
| Apr | 07–10 | 3.0 | 81 % | 98 % | 2.6 / 6.7 | 81 % |
| Apr | 10–13 | 4.3 | 70 % | 94 % | 3.6 / 7.2 | 70 % |
| Apr | 13–17 | 6.6 | 20 % | 82 % | 6.2 / 14.4 | 20 % |

\*ASOS reports a gust only when the wind is gusty. When no gust was reported, the hour's mean is used, so the
median gust is close to the mean.

**Cross-checks, March–April combined**

| Station | 07–10 ≤ 5 m/s | 10–13 ≤ 5 m/s | 13–17 ≤ 5 m/s | 13–17 mean m/s |
|---|---|---|---|---|
| RCMC1 Richmond | 92 % | 90 % | 86 % | 3.3 |
| AAMC1 Alameda (NOS 9414750, anemometer 6.9 m) | 89 % | 87 % | 67 % | 4.4 |
| KOAK Oakland | 80 % | 69 % | 27 % | 6.4 |
| KSFO San Francisco (gap-wind site, upper bound) | 73 % | 52 % | 16 % | 7.7 |

### 2b. Usable mornings, March–April (244 days, 2022–2025)

Mornings per week = fraction of days × 7. The "B" column is the strict definition used in the answer.

| Station | A: 07–10 every hour mean ≤ 5 | **B: 07–10 every hour mean ≤ 5 and gust ≤ 8** | C: at least 1 hour in 07–10 inside limit | D: 2 consecutive hours in 07–11 inside limit | B, worst / best year |
|---|---|---|---|---|---|
| RCMC1 Richmond | 6.2 /wk (89 %) | **5.7 /wk (81 %)** | 6.5 /wk (93 %) | 6.3 /wk (90 %) | 5.0 (2023) / 6.2 (2022) |
| AAMC1 Alameda | 5.9 (84 %) | **5.7 (82 %)** | 6.4 (92 %) | 6.2 (89 %) | 5.4 (2023–24) / 6.4 (2022) |
| KOAK Oakland | 5.1 (73 %) | **5.0 (72 %)** | 6.0 (86 %) | 5.6 (80 %) | 4.6 (2023) / 5.6 (2022) |
| KSFO | 4.3 (61 %) | **4.3 (61 %)** | 5.7 (82 %) | 4.9 (70 %) | 4.1 / 4.4 |

March is worse than April at every station. At RCMC1 March is 5.4/wk and April 6.0/wk; at KOAK March is 4.8 and
April 5.3. With an 8 m/s mean / 12 m/s gust limit (K01-like tolerance), every Bay-shore station gives 6.4 to
6.8 mornings per week.

## 3. What this means for RFS (interpretation; `ESTIMATE`)

- **Nobody has measured wind at RFS itself**, and no public station sits on the site. RFS lies between RCMC1
  (sheltered harbor shore, calmest) and KOAK (open airport, 10 m mast, windier). The two bracket a reasonable
  range: **5.0 to 5.7 usable mornings per week**, roughly 20 to 23 over a four-week month.
- RCMC1's afternoons are calm compared with Alameda and Oakland (86 % vs 27–67 % of hours ≤ 5 m/s). A likely reason
  is that the Potrero/Miller-Knox ridge shelters it from the westerly sea breeze (`UNVERIFIED`; wind direction was
  not analyzed). Do not count on RFS afternoons being that calm. Use KOAK's afternoon figures for planning.
- **Height correction.** Station winds are measured at 7–10 m. A drone hovering at 2–5 m over grass sees about 15–25 %
  less mean wind. By the log law with z0 = 0.03 m, the ratio is ln(3/0.03)/ln(10/0.03) = 0.79. Gusts are relatively
  larger near the ground and near buildings or trees. The table is slightly conservative for mean wind and
  roughly neutral for gusts.
- **Gusts set the limit, not the mean.** At RCMC1 the morning gust/mean ratio is about 1.6–2 (median 4.2 vs 2.1 m/s).
  The B criterion loses about 0.5 mornings per week to the 8 m/s gust condition alone (A 6.2 vs B 5.7).

## 4. Method

1. **Data downloaded 2026-11-09:**
   - NDBC historical standard meteorological files for RCMC1 and AAMC1, 2022–2025. These are 6-minute records:
     WSPD is the 2-minute mean and GST the peak gust, in m/s, UTC.
     `https://www.ndbc.noaa.gov/view_text_file.php?filename=rcmc1h2024.txt.gz&dir=data/historical/stdmet/`
     (same pattern for other years and for `aamc1`).
   - Iowa Environmental Mesonet ASOS archive for KOAK and KSFO, 2022-02-01 to 2025-05-01, routine and special
     METARs, local time, sknt/gust in knots.
     `https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?station=OAK&data=sknt&data=gust&data=drct&year1=2022&month1=2&day1=1&year2=2025&month2=5&day2=1&tz=America%2FLos_Angeles&format=onlycomma&report_type=3&report_type=4`
   - A KCCR (Concord) download returned empty and was dropped. Concord is inland and not representative anyway.
2. **Station metadata:** NDBC station pages, retrieved 2026-11-09. RCMC1 is at 37.923 N 122.410 W, site 2.8 m above
   MSL, anemometer 7.2 m above the site, NOAA NOS PORTS (https://www.ndbc.noaa.gov/station_page.php?station=rcmc1).
   AAMC1 is at 37.772 N 122.300 W, anemometer 6.9 m (https://www.ndbc.noaa.gov/station_page.php?station=aamc1).
3. **Processing (`wind_stats.py`, stdlib only):**
   - UTC is converted to Pacific time with the US DST rule.
   - Each local clock hour gets the mean of its WSPD samples and the maximum of its gusts.
   - Windows: 07–10 covers hours starting 07, 08 and 09; 10–13 covers 10–12; 13–17 covers 13–16.
   - Morning criteria A–D are defined in the script header. Days with fewer than 3 valid morning hours are dropped,
     and none were in March–April.
   - Coverage is about 99 % of possible hours, for example 732 of 732 Mar–Apr morning hours at RCMC1.
4. **Sample size:** 4 years is short. Year-to-year spread of the B criterion is ±0.6 mornings per week at RCMC1 and
   ±0.5 at KOAK.

Web climatology checked but not used: WeatherSpark Richmond
(https://weatherspark.com/y/551/Average-Weather-in-Richmond-California-United-States-Year-Round) did not return its
wind section through the fetch tool. Windfinder "Richmond (Tide)" (https://www.windfinder.com/windstatistics/richmond)
showed "No statistical weather data available". The analysis rests on the raw NOAA/IEM data above.

## 5. Not covered and next steps

- **Rain and low cloud are not counted.** Rain days would cut the morning count further: in a typical March the
  Bay Area has about 6–9 days with measurable rain (`UNVERIFIED`; not computed here).
- **Measure RFS directly.** Take a handheld anemometer (about $20–30) on two or three mornings before December. Log
  readings at 2 m and at roughly 5 m, and compare them with RCMC1 real-time data
  (https://www.ndbc.noaa.gov/station_page.php?station=rcmc1) at the same times. That gives an RFS/RCMC1 ratio, so this
  table can be rescaled. The same RCMC1 page works as a go/no-go check on flight mornings.
- Wind direction and the effect of RFS buildings and trees on turbulence were not analyzed.

## Files

- `wind_stats.py`: analysis script (`python -I wind_stats.py data`)
- `wind_stats_output.txt`: full output, including the 8 m/s / 12 m/s limit tables and year-by-year figures
- `data/`: raw downloads (`rcmc1_2022..2025.txt`, `aamc1_2022..2025.txt`, `asos_OAK.csv`, `asos_SFO.csv`)
