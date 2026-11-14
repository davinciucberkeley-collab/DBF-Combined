# H3 RFS wind measurement (`R-WIND-MEASURE`)

Revision H3-R1, 2026-11-13. Status `PROPOSED`; no measurement taken. Owner H3 (with B1). Requirement: RFS morning wind is measured with a handheld anemometer on >= 3 mornings at 2 m height against the RCMC1 real-time reading;
the ratio RFS/RCMC1 is < 1.4 (else the K01 reversal in `CONFIGURATION.md` applies) and the flight-card limit is rescaled to the measured ratio (`team/A2/REQUIREMENTS.md`, `requirements.wind_ratio_max` 1.4).
Why it matters: the whole 5 m/s card rests on the RCMC1 station, which is not the flying site (`STATUS.md`; `config-study/tiebreak/DECISION.md` unknown 4: nobody has measured RFS).

## Equipment

| Item | Note | BOM |
|---|---|---|
| Handheld anemometer | the tie-break budgeted $20-30 from the hardware line (`DECISION.md`); **no anemometer line exists in `team/I1/BOM.csv`** | `CR-H3-02` (I1): add it or borrow one from a team member |
| Pole or tripod to hold it at 2 m | any | - |
| Watch, phone with the RCMC1 real-time page | free | - |
| Log | table below, or `templates/wind_log.csv` | - |

## Procedure (per morning, 07:00-10:00, no precipitation)

1. Stand in the sub-field where the aircraft will fly (yellow sub-fields 1-4, `env.site`), clear of buildings and trees as far as the site allows. Hold the anemometer at 2 m, facing into the wind.
2. Take a 60 s average reading every 10 min for the whole window and note the maximum gust in each minute. Note the direction.
3. At the same minute open the RCMC1 real-time reading and note its mean and gust values.
4. Compute the ratio RFS/RCMC1 per reading, then the mean ratio for the morning.
5. Repeat on **at least three mornings**, preferably including a windy one (calm mornings give an unreliable ratio).
6. Flights: record the anemometer reading in the flight row before each sortie (`../H2/templates/flight_log.csv`).

## Decision rule

| Result | Action |
|---|---|
| Mean ratio over >= 3 mornings < 1.4 | `R-WIND-MEASURE` passes; the 5 m/s card stands; limit = 5 m/s measured on site |
| Ratio r >= 1.4 | A1 applies the K01 reversal condition (`CONFIGURATION.md`: RFS wind >= 1.4 x RCMC1); report to A1 the same day |
| Ratio between | rescale the card: the RCMC1 go / no-go number is the card limit divided by the ratio (e.g. ratio 1.2 gives 5 / 1.2 = 4.2 m/s at RCMC1) |

## Log

| Date | Time | RFS mean m/s (2 m) | RFS max gust m/s | Direction | RCMC1 mean m/s | RCMC1 gust m/s | Ratio | Notes |
|---|---|---|---|---|---|---|---|---|
| - | - | - | - | - | - | - | - | - |

Result: mornings measured **0 of 3**; mean ratio **-**.
