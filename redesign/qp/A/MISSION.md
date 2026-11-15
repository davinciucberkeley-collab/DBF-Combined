# Mission definition, concept A (scaled quad tailsitter), 2026-11-14 (updated D-183 / D-184)

One definition for every A report (BOARD C6). Reproduce: `python -I mission_gate_a.py`. Labels: `EST` estimate, `V` vendor page, `—` unknown. Updated for D-183 (APC 9x4.5MR props x0.93 derate, Tattu 2300 pack kept, 0.90 spin cap) and D-184 (arm x1.2, cant 16 deg, wind rule; `review/QP-2/D183.md`, `D184.md`, `WIND.md`). Basis: method of `review/CLOSURE-ROUND-2026-11-14/A2.md` s2.1 (flight-test programme: H2 gate 1i, flight card 4b), re-done with A's stall and power. The 3.5 min / 17 m/s mission of K09-L, B's 15 m/s / 3.6 min and the 16 m/s of the first A draft are replaced by this one.

## 1. Speeds re-derived

SIZING-A's stall (Vs 11.0 m/s, 1.3 Vs 14.3) was computed at 1.226 kg, before the board's re-roll. Vs = sqrt(2 m g / (rho S CLmax)), S 0.22 m^2, CLmax 0.75 `EST`, rho 1.20:

| Mass | Vs | 1.3 Vs |
|---|---|---|
| 1.226 kg (SIZING-A) | 11.02 | 14.3 |
| 1.381 kg (predicted incl. growth and overrun, MASS-GATE) | 11.70 | 15.21 |
| 1.50 kg (gate) | 12.19 | 15.85 |

**Cruise 17 m/s** (IAS), set so that the gate-mass 1.3 Vs (15.85) is still 7.3 % under cruise and the predicted-mass (1.381 kg, 1.3 Vs 15.21) margin is 11.8 %. At 15-16 m/s the gate-mass margin is 5 % and 1 %; they are rejected. 17 m/s is also K09-L's value, so the same flight card (fence 250 m / 110 m) carries. CLmax is `EST`: measured stall replaces it before `Q_TAILSIT`/airspeed limits are frozen. The APC 9x4.5MR has the same 4.5 in pitch as the 9545 (pitch speed 13.4 m/s at 7,000 rpm, SIZING-A s5), so at 17 m/s it is windmilling-limited: cruise power is `EST` and untested, and C7 (higher pitch prop) may lower it.

Cruise power, 1.37 kg: CL 0.352, L/D 7.19, drag 1.87 N, aero 31.8 W, electric **161 W** (162 W at 1.381 kg) at eta_p 0.26 x 0.76 `EST` (SIZING-A used 122 W at 15 m/s). Hover-to-cruise handover speed: `—` until the time-domain pitch-over (C3).

## 2. Cruise racetrack (same segments as A2)

| Segment | Basis | s |
|---|---|---|
| Settle to trimmed 17 m/s after the transition | A2 `EST` | 15.0 |
| 2 laps | H2 gate 1i precedent | 108.3 |
| 1 go-around lap | flight card 4b | 54.2 |
| Run-in into the wind, <= 1/2 lap | flight card 4b | 27.1 |
| **Total** | | **204.6 s = 3.41 min, requirement 3.5 min** |

Bank 30 deg: R = V^2 / (g tan 30) = 289 / (9.807 x 0.5774) = **51.0 m**; leg 300 m; lap 2 x 300 + 2 pi R = 920.7 m = 54.2 s; far point 150 + 51.0 = **201 m** inside the 250 m fence and 500 m VLOS; the transition climb (about 31 m from 50 m, `EST`) ends near 81 m under the 110 m ceiling. These match K09-L's 3.41 min because the speed is the same.

**QP-3 follow-up 4 (SITL-FLIGHT.md): leg 200 m, not 300 m.** A cruise BATT_LOW (loiter to 50 m, back-transition, QLAND) moves the aircraft up to 49 m outward / 94 m in any direction from the trigger point (SITL, 1.50 kg, `WP_LOITER_RAD` 40, `Q_TAILSIT_RAT_VT` 24). With the 300 m leg (far point 201 m) that is 250-295 m against the 250 m fence; with a 200 m leg (lap 2 x 200 + 2 pi 51 = 720 m = 42 s, far point 151 m) it is 200 m outward-heading and 245 m for the conservative any-direction bound. Total cruise time (204.6 s) is unchanged: fly more, shorter laps. `EST`.

## 3. Hover-mode time: 3.0 min total (incl. go-around)

| Segment | Basis | s |
|---|---|---|
| Climb 0-50 m at 2 m/s | A2 | 25 |
| Hold at 50 m, QLOITER / attitude check | A2 `EST` | 35 |
| Descent 50-0 m at 1 m/s | A2 | 50 |
| Landing hover (last 6 m at 0.3 m/s) | A2 | 30 |
| One go-around (to >= 10 m, reposition upwind, one retry) | flight card 4b | 40 |
| **Total** | | **180 s = 3.0 min** |

The go-around is inside the energy budget of s4, not the reserve. Wind (D-184, WIND.md): <= 5 m/s mean, gust <= 8 m/s; hover with the wing edge into the wind within +-10 deg by pilot yaw (+-20 deg for steady and gust only), belly-on only to 3 m/s, `Q_WVANE_ENABLE` 0; lean about 29 deg at 5 m/s belly-on (SIZING-A s4). Yaw authority >= 0.35 N m must be confirmed on the bench; if the hanging test gives < 0.30 N m the 5 m/s card is reopened.

## 4. Reserve and energy (Tattu 2300 mAh 4S, 34.0 Wh nameplate, V; D-183b: the pack stays, the CNHL 3000 is dropped)

Reserve 20 % of nameplate and worn-pack floor 0.90 (A2). Usable = 34.0 x 0.90 x 0.80 = **24.5 Wh**. Hover power from `prop_a.py` (APC 9x4.5MR PER3 static data x0.93 derate, cant 16 deg, 3 % download, ESC 0.98, x1.10 control margin); transitions and climb scaled from SIZING-A (1.56 and 0.29 Wh at 1.37 kg, as m^1.5 and m `EST`); cruise 161 W x (m/1.37)^0.58 `EST`. Reproduce: `python -I mission_gate_a.py`.

| Mass | Hover W | Hover Wh (180 s incl 40 s go-around) | Transitions | Climb | Cruise W / Wh (204.6 s) | **Total Wh** | Pack margin = usable / total | Max cruise before BATT_LOW |
|---|---|---|---|---|---|---|---|---|
| 1.381 kg (predicted + overrun) | 193 | 9.67 | 1.58 | 0.29 | 162 / 9.19 | **20.7** | **1.18** | **4.81 min** (289 s) |
| 1.44 kg (target) | 206 | 10.29 | 1.68 | 0.30 | 166 / 9.42 | 21.7 | 1.13 | 4.43 min |
| 1.50 kg (gate) | 218 | 10.92 | 1.79 | 0.32 | 170 / 9.64 | **22.7** | **1.08** | **4.06 min** (244 s) |

**BATT_LOW budget:** hover 180 s (which already holds the 40 s go-around), both transitions and the climb are taken first; what is left of the 24.5 Wh is cruise. At the predicted mass that is 4.81 min against 3.41 min needed (3.5 min requirement): a 3rd lap (54 s) fits with 1.6 laps spare; at the gate mass it is 4.06 min, 0.65 min over the need. `A.param`: `BATT_CAPACITY` 2300, `BATT_LOW_MAH` 650 (= 2300 - 0.72 x 2300 = 644), `BATT_CRT_MAH` 345. The margin is thinner than the board's "1.3x" at the gate (1.08); it holds at the predicted mass (1.18). A measured cruise power above about 200 W at the gate mass breaks it. Hover pack current at the gate: 218 W / 14.8 V = **14.8 A** (3.7 A per motor pack side; 5.4 A phase per motor with the 0.93 derate, rating 13 A). Cheapest levers if it breaks: cut the hold from 35 s to 15 s (-0.5 Wh) or fly 2 laps with no go-around lap in the budget; neither is applied.

## 5. Flight-test basis

Gate order from A2/H2 carried: bench, thrust stand, hanging yaw test, tethered hover, free hover in <= 5 m/s, transition at >= 50 m (after the C3 time-domain run), 2 laps, back-transition, 20 landings, full mission. `—`: tailsitter transition altitude loss, so 50 m is kept.
