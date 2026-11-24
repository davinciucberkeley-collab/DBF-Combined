# Mission definition, concept A (scaled quad tailsitter), 2026-11-14 (updated D-183 / D-184; QP-4 fold-in of BOARD QP-3, 2026-11-15)

One definition for every A report (BOARD C6). Reproduce: `python -I mission_gate_a.py`. Labels: `EST` estimate, `V` vendor page, `—` unknown. Updated for D-183 (APC 9x4.5MR props x0.93 derate, Tattu 2300 pack kept, 0.90 spin cap) and D-184 (arm x1.2, cant 16 deg, wind rule; `review/QP-2/D183.md`, `D184.md`, `WIND.md`). Basis: method of `review/CLOSURE-ROUND-2026-11-14/A2.md` s2.1 (flight-test programme: H2 gate 1i, flight card 4b), re-done with A's stall and power. The 3.5 min / 17 m/s mission of K09-L, B's 15 m/s / 3.6 min and the 16 m/s of the first A draft are replaced by this one.

> **T-084..T-087 status note (2026-11-22, D-233..D-236; review round 3 fix M-D).** Current concept A O4b state (EST; `mechanism/out/T084_report.md` s0, s3, `T086_report.md`, `T087_report.md`, `T085_report.md`): basic 1,633.0 g as drawn, tallied predicted **1.8796 kg**, CG 23.13 mm tallied, SM 7.17 %, transition window +11.88 %, T/W 2.632 fresh / 2.111 sag, cruise 234 s (limit 204.6 s), 1.3 Vs 17.56 m/s against the 17.0 m/s cruise (A-P6 FAIL carried on CLmax 0.75 EST, TP-11 pass line 0.81). Tip-over (A-P9, edge toward the CG, FIN_H 0.1937 m): **31.00 deg** minimum, target 30.5 (D-233). BOM **$1,939.17, margin +$60.83** (D-234, D-235). D-185 (a): carried FAIL on the upgraded model (governing mode 94.6-108.7 Hz, cx 0.74-0.85, cy 1.12-1.35); the T-A-TAP test (TP-10b) decides it after the build, D-236. The hover and cruise energy lines of s4 were not re-derived for 1.8796 kg: "—" (re-run `mission_gate_a.py --o4b`). The T-083c note below is the earlier (T-083b) state: its mass, CG, window, T/W and cruise numbers are superseded by this note.

> **T-083c status note (2026-11-22, D-227, D-228, D-229).** This file is the 2026-11-14/15 record at 1.396 kg, MN2212 and a Tattu 2300 pack; its numbers are NOT current. Current concept A O4b state (EST, `T083b_report.md` s0, s4.1): X2216 V3 short-shaft 880KV on APC 9x4.5MR, 2,800 mAh 4S pack, `Q_M_SPIN_MAX` 1.0, `Q_M_BAT_CURR_MAX` 72 A (T083_report s2.4); tallied 1,634.5 g basic, predicted 1.873 kg, CG 22.26 mm, SM 7.52 %, window +12.05 %, T/W 2.641 fresh / 2.118 sag, cruise 236 s (limit 204.6 s), 1.3 Vs 17.53 m/s against the 17.0 m/s cruise (A-P6, gated by a measured stall CLmax >= 0.81, D-228). The s1 speeds (CLmax 0.75 EST) and the s4 energy budget below were not re-derived by T-083c; re-run `mission_gate_a.py --o4b` for current values.


## 1. Speeds re-derived

SIZING-A's stall (Vs 11.0 m/s, 1.3 Vs 14.3) was computed at 1.226 kg, before the board's re-roll. Vs = sqrt(2 m g / (rho S CLmax)), S 0.22 m^2, CLmax 0.75 `EST`, rho 1.20:

| Mass | Vs | 1.3 Vs |
|---|---|---|
| 1.226 kg (SIZING-A) | 11.02 | 14.3 |
| 1.396 kg (predicted incl. growth and overrun, MASS-GATE; was 1.381) | 11.76 | 15.29 |
| 1.50 kg (gate) | 12.19 | 15.85 |

**Cruise 17 m/s** (IAS), set so that the gate-mass 1.3 Vs (15.85) is still 7.3 % under cruise and the predicted-mass (1.396 kg, 1.3 Vs 15.29) margin is 11.2 %. At 15-16 m/s the gate-mass margin is 5 % and 1 %; they are rejected. 17 m/s is also K09-L's value, so the same flight card (fence 250 m / 110 m) carries. CLmax is `EST`: measured stall replaces it before `Q_TAILSIT`/airspeed limits are frozen. The APC 9x4.5MR has the same 4.5 in pitch as the 9545 (pitch speed 13.4 m/s at 7,000 rpm, SIZING-A s5), so at 17 m/s it is windmilling-limited. **Cruise rpm 7,300-7,600** (`sitl/fu_level.py` with the APC V > 0 data, duty 0.60-0.70; QP-3 BOARD s1 item 2; the 8,900-10,500 rpm figure in STRUCTURES iter. 2 is withdrawn), J = 17 / (125 x 0.2286) = 0.595 against zero thrust at J 0.64, so cruise power and `THR_MAX` rest on the APC model where a small Ct error is a large thrust error. Cruise power is `EST`; the board measures duty and rpm on the first cruise (M8, audio FFT; above 0.65 duty fresh fails the `THR_MAX` 68 basis; C7 is re-stated that way). The model's electric power may be 10-15 % under this file's 161 W: treat 200 W as the energy break point (s4).

Cruise power, 1.37 kg: CL 0.352, L/D 7.19, drag 1.87 N, aero 31.8 W, electric **161 W** (162 W at 1.396 kg) at eta_p 0.26 x 0.76 `EST` (SIZING-A used 122 W at 15 m/s). Hover-to-cruise handover speed: `—` until the time-domain pitch-over (C3).

## 2. Cruise racetrack (same segments as A2)

| Segment | Basis | s |
|---|---|---|
| Settle to trimmed 17 m/s after the transition | A2 `EST` | 15.0 |
| 2 laps | H2 gate 1i precedent | 108.3 |
| 1 go-around lap | flight card 4b | 54.2 |
| Run-in into the wind, <= 1/2 lap | flight card 4b | 27.1 |
| **Total** | | **204.6 s = 3.41 min, requirement 3.5 min** |

Bank 30 deg: R = V^2 / (g tan 30) = 289 / (9.807 x 0.5774) = **51.0 m**. **Leg 150 m** (BOARD QP-3 s3, was 300 m / 200 m): lap 2 x 150 + 2 pi R = 620.7 m = **36.5 s**; racetrack far point 75 + 51 = **126 m**; the 204.6 s requirement above is unchanged (it is set on the 300 m reference lap, 54.2 s): fly 5.2 laps of 36.5 s after the 15 s settle. The transition climb (about 31 m from 50 m, `EST`) ends near 81 m under the 110 m ceiling.

**Fence (QP-3 SITL-FLIGHT follow-up 4, BOARD s1 item 7 and s3).** A cruise BATT_LOW (loiter to 50 m, back-transition, QLAND) moves the aircraft up to 49 m outward / 94 m in any direction from the trigger point (SITL, 1.50 kg, `WP_LOITER_RAD` 40, `Q_TAILSIT_RAT_VT` 24). Any-direction bound = L/2 + 51 + 94 against the fence 250 m less `FENCE_MARGIN` 10 m = **240 m** (not 250): L <= 190 m; with L = 150 m it is **220 m, 20 m margin** `CALC`. The 245 m of the 200 m leg was a fail. Open: SITL check that a fence breach during QLAND does not command RTL (a forward transition in a Q mode) before F04.

## 3. Hover-mode time: 3.0 min total (incl. go-around)

| Segment | Basis | s |
|---|---|---|
| Climb 0-50 m at 2 m/s | A2 | 25 |
| Hold at 50 m, QLOITER / attitude check | A2 `EST` | 35 |
| Descent 50-0 m at 1 m/s | A2 | 50 |
| Landing hover (last 6 m at 0.3 m/s) | A2 | 30 |
| One go-around (to >= 10 m, reposition upwind, one retry) | flight card 4b | 40 |
| **Total** | | **180 s = 3.0 min** |

The go-around is inside the energy budget of s4, not the reserve. Wind (D-184, WIND.md): <= 5 m/s mean, gust <= 8 m/s; hover with the wing edge into the wind within +-10 deg by pilot yaw (+-20 deg for steady and gust only), belly-on only to 3 m/s, `Q_WVANE_ENABLE` 3 / `Q_WVANE_GAIN` 1 / `Q_WVANE_SPD_MAX` 2 (side into the wind = the wing edge; D-186 accepted **conditionally**: works in calm SITL only, so before the first free hover run SITL with WIND.md's 1 m/s turbulence model, heading excursion <= 15 deg, and fly the card QLOITER -> QSTABILIZE -> FBWA within 2 s so the vane never acts before the pitch-over; tether check M9); lean about 29 deg at 5 m/s belly-on (SIZING-A s4). Yaw authority >= 0.35 N m must be confirmed on the bench; if the hanging test gives < 0.30 N m the 5 m/s card is reopened.

## 4. Reserve and energy (record at the Tattu 2300 mAh 4S, 34.0 Wh nameplate, V; superseded by the 2,800 mAh pack, T-083, see the status note at the top; D-183b: the pack stays, the CNHL 3000 is dropped)

Reserve 20 % of nameplate and worn-pack floor 0.90 (A2). Usable = 34.0 x 0.90 x 0.80 = **24.5 Wh**. Hover power from `prop_a.py` (APC 9x4.5MR PER3 static data x0.93 derate, cant 16 deg, 3 % download, ESC 0.98, x1.10 control margin); transitions and climb scaled from SIZING-A (1.56 and 0.29 Wh at 1.37 kg, as m^1.5 and m `EST`); cruise 161 W x (m/1.37)^0.58 `EST`. Reproduce: `python -I mission_gate_a.py`.

| Mass | Hover W | Hover Wh (180 s incl 40 s go-around) | Transitions | Climb | Cruise W / Wh (204.6 s) | **Total Wh** | Pack margin = usable / total | Max cruise before BATT_LOW |
|---|---|---|---|---|---|---|---|---|
| 1.396 kg (predicted + overrun) | 197 | 9.83 | 1.60 | 0.30 | 163 / 9.25 | **21.0** | **1.17** | **4.71 min** (283 s) |
| 1.44 kg (target) | 206 | 10.29 | 1.68 | 0.30 | 166 / 9.42 | 21.7 | 1.13 | 4.43 min |
| 1.50 kg (gate) | 218 | 10.92 | 1.79 | 0.32 | 170 / 9.64 | **22.7** | **1.08** | **4.06 min** (244 s) |

**BATT_LOW budget:** hover 180 s (which already holds the 40 s go-around), both transitions and the climb are taken first; what is left of the 24.5 Wh is cruise. At the predicted mass that is 4.71 min against 3.41 min needed (3.5 min requirement): 2.1 laps of the 150 m leg (36.5 s each) spare; at the gate mass it is 4.06 min, 0.65 min over the need. `A.param`: `BATT_CAPACITY` 2300, `BATT_LOW_MAH` 650 (= 2300 - 0.72 x 2300 = 644), `BATT_CRT_MAH` 345. The margin is thinner than the board's "1.3x" at the gate (1.08); it holds at the predicted mass (1.17). A measured cruise power above about 200 W at the gate mass breaks it. Hover pack current at the gate: 218 W / 14.8 V = **14.8 A** (3.7 A per motor pack side; 5.4 A phase per motor with the 0.93 derate, rating 13 A). Cheapest levers if it breaks: cut the hold from 35 s to 15 s (-0.5 Wh) or fly 2 laps with no go-around lap in the budget; neither is applied.

## 5. Flight-test basis

Gate order from A2/H2 carried: bench, thrust stand, hanging yaw test, tethered hover, free hover in <= 5 m/s, transition at >= 50 m (after the C3 time-domain run), 2 laps, back-transition, 20 landings, full mission. `—`: tailsitter transition altitude loss, so 50 m is kept.

## Update 2026-11-15 (CLAIMS-FIX D-189 / D-190)

Cant 17 deg (was 16) and the weigh-in gate 1.47 kg (was 1.50): `mission_gate_a.py` now prints the 1.47 kg row beside 1.50 kg; the hover and cruise energy lines move by < 1 % (hover 214 W at 1.47 kg, 220 W at 1.50 kg, pack margin 1.10x at the gate, 1.14x at the predicted 1.419 kg; cruise to BATT_LOW 253 s at the gate against the 204.6 s requirement). Numbers above that cite cant 16 or 1.50 kg are the previous run and stay conservative for the gate.
