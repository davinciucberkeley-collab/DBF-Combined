# Configuration study after T-077 part 8, concept A O4b (AM-017, 2026-11-21)

Study for the conductor (opus). I wrote none of T-077 (parts 1-8), D-213..D-226, T-080..T-082 or the audits I cite. Repo files written by me: **this file and `docs/audits/2026-11-21-config-study-data/`** (scratch scripts and their outputs, copied for reproducibility). No CAD, ledger, CHANGE-LOG, TEST-PLAN, BOM, params or requirement file was edited. Status: **study record, not VERIFIED COMPLETE.**

Approval: AM-017 ("Yes, run study"). Hard constraints unchanged (CLAUDE.md): $2,000 total including the crash reserve (AM-013), flight-tested by end of April 2027, one car trunk (2018 Nissan Altima, floor about 40 x 37 in EST per the brief, height unmeasured), 3-D gates, Claude-designed and student-built, CAD fidelity, enclosed wiring.
Limits held, none relaxed: A-P3 window >= +5 % with the 3 % download at derate 0.93; A-P2 T/W fresh >= 2.0, sag >= 1.6; A-P4 CG 19.3..26.0 mm and SM >= 5 %; A-P6 1.3 Vs <= cruise; A-P9 tip-over >= 30 deg; A-P5 12 g; landing rows RF >= 1.0 at max(DAF, 1.5) (D-223: x2.23 wing / bridge, x1.97 tubes), KF 1.725, KP 2.156; mission cruise need 204.6 s.
Labels: V = vendor page read today (URL, 2026-11-21); EST = estimate; "—" = unknown. Categories: illustrative (the repo `prop_a.py` thrust model, EST), rigid-body dynamics (`landing_a.simulate` with the T-077 p6 d'Alembert split, unchanged), geometry arithmetic (mass, CG), hand calculation. No FEA, CFD or SITL was run.

Runs (all `python -I`, exit 0; scripts import the repo modules unchanged and change constants only in memory; scripts and outputs in `docs/audits/2026-11-21-config-study-data/`):
- `cs_bom.py` imports `T077p8_data/bom_p8.py` and edits its rows in memory. Line 1 reproduces **$2,150.75 / -$150.75** (re-run of `bom_p8.py` itself: same).
- `cs_prop.py`, `cs_prop2.py`, `cs_prop3.py`, `cs_prop4.py` import `redesign/qp/A/prop_a.py`. Row 1 reproduces P8.4: **window +1.07 %, T/W fresh 1.894 / 1.837, sag 1.698 at 1.833 kg**.
- Script tags: "1e" in `cs_bom.py` / `cs_prop4.py` = option 1-ii; `cs_prop5.py` = option 3 alone and option 2; `cs_extra.py` = the 1-ii coupon row and the option 3 BOM variants.
- `cs_land.py`, `cs_land_m.py` import `T077p6_data/t077p6_demand.py` (pad Fp 30 N / 24 mm, 1.705 kg, CG 23.91 mm, 23 cases x zeta 0.02 / 0.10 x mu 0.40 / 0.30). The baseline reproduces D-226 s1.1: **half-wing My 8.72 N m (D-226: 8.76)**; hub My at the spar-axis point (0.060, 0, 0) is **12.20 N m against D-226's 12.83** (-5 %; D-226's exact moment point is not in the repo, so I use only ratios of my own runs).

## 0. Answer in one place

**Recommendation: concept A with bigger motors, option 1-ii: SunnySky X2216 880KV motors on the same APC 9x4.5MR props, keeping the 1.2 m/s touchdown case and the D-226 wing torsion cell; restore the 14x12 rib by the planned torsion coupon; close the CG with the cage-forward rung.** It is the only option that passes the transition window and both T/W checks with margin at the part-8 mass, and it lowers the BOM (about $1,850-1,986 against $2,000, crash reserve by its definition). Reason: the window is power-limited, not mass-limited. The MN2212 is held to 12.1 A (13 A rating); the X2216 (320 W continuous, page) runs the same 9 in prop about 10 % faster at sag, so the same airframe gets about 20 % more thrust for +28 g and $28 less per motor.

| # | Option, in one plain sentence | Pred. mass kg | Window % (limit +5) / T/W fresh (dl) / sag | CG mm (19.3..26) / SM % | Landing approach | BOM total $ (reserve by definition) | Verdict |
|---|---|---|---|---|---|---|---|
| p8 | Today: the drawn tailsitter with the wing torsion cell | 1.833 | **+1.07** / 1.837 / 1.698 | **30.17 / 4.30** | D-226 cell, 1.2 m/s | **2,150.75** | fails window, T/W, CG, budget |
| 1-i | Bigger motors (T-Motor MN3110) and 10 in props | 2.063 (EST) | +14.8 / 2.76 / 2.24 (EST) | 19.35 / 8.7 | D-226 cell, grown | about 2,278 | reject: budget, A-P6, 10 in vibration band (D-217) |
| **1-ii** | **Same props, stronger motors (SunnySky X2216 880KV)** | **1.864** | **+9.96 / 2.289 / 2.030** | 27.93 / 5.21; **25.5 / 6.2 with the rib coupon; about 21 / 8 with cage forward** | D-226 cell, 1.2 m/s, plateau 30 -> 33 N (s1.4) | **1,985.76; 1,850.32 if the coupon restores 14x12** | **recommend** |
| 2 | Landing on four legs or a skid frame hung from the motor hub instead of the fin tips | 1.966 (EST) | -2.4 (MN2212) | **45.4 / -1.9** (unstable) | legs carry the feet; the wing still couples the fin inertia (0.53x) | about 2,106 | reject: CG aft, mass |
| 3 | Land slower by rule (0.8 m/s design case) on a softer 20 N pad | 1.785 | +2.39 (MN2212) / 1.884 / 1.744 | 27.13 / 5.54 | cell rows x0.75 demand; 2-ply skin, 16x14 or 14x12 rib | 2,071 (16x14) | not now: alone it fails the window; a 1.2 m/s landing then bottoms the pad (48 g) |
| 1-ii + 3 | Both | 1.817 | +11.25 / 2.347 / 2.084 | 24.86 / 6.47 | as 3 | 1,850-1,911 | later lever only, after a two-stage pad and TP-3 |
| 4 | Concept B: a small conventional quadplane (wing, tail, two booms, 4 lift motors + pusher) re-priced | 2.05 / 2.30 / 2.54 (as sized / x1.3 / x1.6 structure) | T/W fresh 2.17 / 1.94 / 1.75 | SM 12 % EST | gear on booms or fuselage | **2,291.70** | reject: budget, T/W headroom 2 %, trunk length, restart |

Dillon decisions needed: **none on hard constraints.** Money: (1) purchase approval to put SunnySky X2216 880KV (5 x $18.99, RMRC, In Stock) in Order 1 in place of the MN2212 (5 x $46.90); (2) the crash-reserve basis: by its definition it falls with the cheaper motor ($342.53 or $287.31 against $373.31); held at the AM-012 value $327.43 the totals are $1,970.66 / $1,890.44 (s7). Both are under $2,000.

## 1. Starting point, recomputed

| Item | Value | Check |
|---|---|---|
| Tallied basic / predicted | 1,598.4 g / 1.833 kg (pred = 1.1174 x basic + 0.032 x 1.47) | P8.4, `t077p8_metrics.py` |
| A-P3 window (download) | +1.07 % (limit +5.0); ceiling at derate 0.93: pred 1.6944 kg = basic 1,474.3 g | `metrics_p8.txt`; `cs_prop` row 1 |
| A-P2 T/W fresh (no dl / dl), sag (dl) | 1.894 / 1.837, 1.698 | same |
| CG / SM | 30.17 mm / 4.30 % (A-P4 band <= 26.0; SM 5 % at 28.45 mm) | P8.4 |
| BOM | $2,150.75 (margin -$150.75) | `bom_p8.py` re-run |
| **A-P6 at the predicted mass (new)** | Vs = sqrt(2 m g / (rho S CLmax)) = sqrt(2 x 1.833 x 9.81 / (1.225 x 0.22 x 0.75)) = 13.34 m/s; **1.3 Vs = 17.34 > 17.0: FAILS**. Proof CL-A-STALL judges it at the 1.47 kg gate (15.69). Mass ceiling: m <= (17/1.3)^2 x 1.225 x 0.22 x 0.75 / (2 x 9.81) = **1.761 kg** | `claims_a1_flight.py` l.284; AM-011 (mass-dependent checks at the predicted mass) |
| **Cruise time (new)** | `params-A.json` mission.pack_ah = **2.3** (stale; O4b pack is 2,800 mAh). With 2.8 Ah the CALC-A-ENDURANCE formula gives **236 s >= 204.6 s** at 1.833 kg; the gate's 141.6 s FAIL is a stale input | `cs_prop` row 1 |

Root of the window failure, from the same model: at p7 (no passing landing path) the tree was already 6.8 g over the window ceiling (P7.4: +4.78 %). **No landing path fits the 9x4.5 / MN2212 / 12.1 A window at derate 0.93**; D-226 only made the gap larger (+117 g). The binding item is power at sag, so the fixes are either more power into the props (option 1) or a much lighter airframe (none found).

### 1.4 Pad stroke at the heavier masses (rigid-body, `cs_land_m.py`, 1.2 m/s, Fp 30 N)
| Mass | Stroke 24 mm pad, zeta 0.02 mu 0.40 | Note |
|---|---|---|
| 1.705 kg (p6 basis) | 21.47 mm, tilt 2.98 deg | reproduces `demand_p6.json` |
| 1.864 kg (option 1-ii), Fp 30 / 24 mm | **24.16 mm: bottoms** in "hard 10 narrow + drift .5" (foot 110.8 N, tilt 3.35 deg > 3.0) | envelope hub My 13.56 N m (x1.11), half-wing 9.26 (x1.06) |
| 1.864 kg, Fp 30, usable stroke 28 mm (`pad_geometry(0.028)`: free foam x1.5, x_foot +6 mm, pad edge held at A-P9 30.5 deg) | 24.45 of 28 mm, **tilt 3.37 deg > 3.0** | hub 13.77 (x1.13), half-wing **11.72 (x1.34)** |
| 1.864 kg, **Fp 33 N** (plateau scaled with mass, 30 x 1.864/1.705 = 32.8), 24 mm | 22.19 mm, tilt **3.09 deg** (> 3.0 by 0.09), n 12.10 g at zeta 0.10 (A-P5 12 g: the same zeta-0.10 exceedance as today's 12.41) | zeta 0.02 sets: hub 11.30, half 7.35 (below today's envelope 12.20 / 8.72); zeta 0.10 sets: hub **14.09 (x1.15)**, half **13.63 (x1.56, one case: "hard 7/7 combo", mu 0.30)** |

This is not specific to option 1-ii: the part-8 tree itself (1.833 kg) is above the mass at which the 24 mm pad was sized (1.705 kg). Whatever is chosen, the landing demand must be re-run at the predicted mass (task 2, s8). Reading: if TP-3 measures zeta at about 0.02, the D-226 cell as drawn holds at 1.864 kg with a 33 N plateau (its rows were judged on the 1.705 kg envelope, which the zeta-0.02 sets stay below). At the zeta-0.10 bound the centre sleeve C1 (1.04) and bridge B1 (1.03) fall to about 0.9 and the fin-side rows by up to 1/1.56, so the cell regrows (EST +15-30 g, CG +1-2 mm at the P8.4 rate of about 0.06 mm/g). The 3.0 deg end-tilt line is missed by 0.09 deg with either pad change: the pad edge or plateau needs a small change (task 2).

## 2. Option 1: bigger motors or props

**Plain sentence: keep the airframe and put more thrust on it, either with bigger props or with motors that can take more power.**

Model (illustrative, EST; `prop_a.py` unchanged): APC 9x4.5MR static rows T(n), P(n) (PER3 file read 2026-11-14; apcprop.com refused all requests today, Cloudflare block); motor V_m = n/Kv + I R_m, I = Q(n)/K_t + I0, K_t = 60/(2 pi Kv); pack V_b = V_rest - 4 I R_p (R_p 30 mOhm EST); T/W = 4 T hot derate cos 17 deg / (m g); window = 100 (0.8 TW_sag x 0.97 - 1.33)/(0.8 TW_sag x 0.97 + 1.33); one-motor current line = rating x 12.1/13 (the A-P16 margin, carried); fresh cap by `cap_sched` (the O4b Lua schedule).

### 2.1 Candidates computed

| Variant | Motor data (page, read 2026-11-21) | Result | Verdict |
|---|---|---|---|
| 1-a MN2212 KV920 on 9x4.5 | Rm 142 mOhm, 15 A / 180 s, 65 g (store.tmotor.com/goods.php?id=388) | window +1.50 % at 1.833 kg (fresh cap 0.775, line 13.96 A); fresh T/W 1.824 | reject: the 15 A rating moves only about 5 % more power into the same disc |
| 1-b MN3110 KV780 / KV700 on 9x4.5 | KV780: Rm 71 mOhm, 26 A, 100 g; KV700: Rm 92 mOhm, 21 A, 99 g; $61.90 (goods.php?id=334) | at 2.045 / 2.041 kg: window +2.52 / -5.57 % | reject: +140 g for little more rpm at sag |
| 1-c (= 1-i) MN3110 KV780 + 10 in prop | T-Motor table KV780 14.8 V tops out at 11x3.7 (1,260 g, 14.9 A); KV700 12x4 1,290 g, 14 A. No 11 in prop is sold on the T-Motor store; P12x4 pair $38.90, 14.5 g (V) | 10 in by static similarity of the 9x4.5MR rows (T x (10/9)^4, P x (10/9)^5; a P/D 0.5 prop, EST): window **+14.8 %**, T/W fresh 2.845 / sag 2.239 at 2.063 kg; 20.5 A per motor; cruise 209 s; **1.3 Vs 18.40** | reject: A-P6 fails by 1.4 m/s; D-217 found the 10 in hover band on the 71-89 Hz cage / wing-torsion mode (54.8 vs 30 m/s2); BOM about $2,278 |
| 1-c' MN3110 KV700 + P12x4 | P12x4 pitch speed at the 100 % row 7,600 rpm: 0.1016 m x 7,600 / 60 = **12.9 m/s < 17 m/s cruise** | cannot hold cruise on these props; a 12 in prop with >= 6 in pitch has no readable data today | reject |
| **1-ii SunnySky X2216 880KV long shaft on the same APC 9x4.5MR** | **$18.99 In Stock, 72 g, Rm 117 mOhm, I0 0.5 A/10 V, max continuous 320 W, 2-4S, ESC 30 A, stator 22 x 16 mm, rotor 27.5 mm, shaft 3.175 mm** (https://www.readymaderc.com/products/details/85810-sunnysky-x2216-brushless-motors-long-shaft-version-880kv) | below | **recommend** |

Sanity check of the model on D-217: the same scaling gives MN2212 + 10 in at 12.1 A a window of -3.7 % (D-217 had +0.8 % at most with the real 10x4.5MR file). Similarity scaling overstates the 10 in power, so the 1-c numbers are optimistic on thrust per amp; this does not change the 1-c verdict.

### 2.2 Option 1-ii in numbers (`cs_prop4.py`; current line 320 W / 16.8 V x 12.1/13 = 17.7 A, EST because the page gives power, not current)

| State | basic g | pred kg | CG mm | SM % | window % | T/W fresh (no dl / dl) | T/W sag (dl) | fresh cap | 1 motor A | hover A | cruise s (2.8 Ah) | 1.3 Vs | full throttle fresh / sag |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| p8 + 4 x 7 g | 1,626.4 | 1.864 | 27.93 | 5.21 | **+9.96** | 2.360 / 2.289 | 2.030 | 0.929 | 17.73 | 7.32 | 233 | 17.49 | 10,560 rpm 15.8 A / 10,113 rpm 14.5 A |
| same, derate 0.88 | | | | | +7.22 | 2.233 / 2.166 | 1.921 | | | 7.73 | 209 | | |
| same, current line 15 A | | | | | +6.35 | 2.010 / 1.950 | 1.888 | 0.836 | 15.00 | | 233 | | 9,761 / 13.6 A |
| + rib coupon (14x12, -23.8 g, -2.4 mm x 1,598/1,603) | 1,602.6 | 1.838 | **25.54** | 6.19 | **+10.67** | 2.392 / 2.321 | 2.060 | | | | 241 | 17.36 | |
| + option 3 recovery (-42.8 g, -3.04 mm) | 1,583.6 | 1.817 | 24.86 | 6.47 | +11.25 | 2.419 / 2.347 | 2.084 | 0.928 | 17.73 | 7.16 | 248 | 17.26 | |

- Mass ceilings with X2216 at derate 0.93: **window 5 % at 2.060 kg predicted (basic 1,802 g)**; fresh T/W 2.0 with the download at 2.150 kg (basic 1,882 g). That is about 200 g of basic-mass headroom against -124 g today.
- **Bench derate line (A-P3) falls from 1.006 to about 0.84** (linear between the derate 0.93 and 0.88 rows: slope (9.96 - 7.22)/0.05 = 54.8 points per unit derate; 0.88 - (7.22 - 5)/54.8 = 0.840); A-P2 fresh with download 0.93 x 2.0 / 2.289 = 0.813.
- Why it works (check by hand): at sag the MN2212 runs 9,180 rpm (TEST-PLAN TP-1) and the X2216 10,113 rpm; thrust ratio (10,113 / 9,180)^2 = 1.214; 1.698 x 1.214 x 1.833 / 1.864 = 2.027 (model 2.030). Power ratio 1.214^1.5 = 1.34; sag current 14.5 A against 10.75 A.
- Unchanged: the same prop, so the hover rpm moves only by sqrt(1.864/1.833) = +0.8 % and the A-P10 1P band is unchanged (the reason D-217 rejected 10 in props does not arise). Cruise pitch speed improves (more rpm available).
- New requirements it brings (all EST, to verify): (a) pack current at full throttle 4 x 15.8 = 63 A: `Q_M_BAT_CURR_MAX` 45 -> 65 A, XT90 and 12 AWG battery lead (A-P16 connector >= 1.25 x 63 = 79 A; +8 g EST, $12 EST); (b) the Lua cap table regenerated (cap 0.929 at 16.8 V, 1.0 at sag); (c) **APC 9x4.5MR rpm limit at 10,560 rpm "—"** (apcprop.com unreadable today; must be read before ordering); (d) prop adapter for the 3.175 mm shaft, part "—"; (e) **vendor drawing for CAD fidelity "—"**: the RMRC page gives stator, rotor and shaft only; motor length, mount pattern and lead length must come from SunnySky's drawing or be measured on arrival and the part marked until then; (f) the H743-Wing current-sensor range at 65 A "—"; (g) motor mass with leads: page 72 g (whether leads are included is not stated; +5 g per motor would cost about 0.6 window points).
- Risks: no maker thrust table for this motor on 4S (the model uses Kv, Rm, I0 from the retailer page, as the MN2212 model does); the 320 W rating is the retailer's figure; the line 17.7 A is my EST. The 15 A sensitivity row still passes the window (+6.35 %), but fresh T/W with download falls to 1.950: if the bench shows the motor must be held at 15 A, A-P2 fresh fails by 2.5 %.

## 3. Option 2: landing on legs or a skid

**Plain sentence: give the aircraft four landing legs (or a skid frame) that hang from the motor hub and reach back past the trailing edge, so the fins no longer touch the ground.**

Geometry: the stance is on the tail, so the feet must stay at x_foot 0.3475 m and keep the footprint |y| 0.38, |z| 0.19 m (A-P9: tan-1(0.19 / (0.3475 - 0.030)) = 30.9 deg; a narrower footprint fails 30 deg). Leg from the hub (x -0.081, 0, 0) to a foot: L = sqrt(0.4285^2 + 0.38^2 + 0.19^2) = **0.603 m**.

Load path (rigid-body, `cs_land.py`, same 23 cases; "legs" = the same foot forces applied to the hub group instead of the fin halves):

| Pad / sink | Half-wing My at the spar axis, fins (today) | Same, feet on legs | Ratio |
|---|---|---|---|
| Fp 30, 1.2 m/s, envelope | 8.72 N m | 4.62 N m | **0.53** |
| Fp 20, 0.8 m/s, envelope | 6.56 | 3.57 | 0.54 |

The wing still has to turn the fins with the aircraft (about half the torque remains, because the fins with ribs and root blocks hold 46 % of Iyy, D-226 s1.1). So legs halve the cell torque; they do not remove the cell.

Leg structure (hand): a cantilever leg takes the foot friction as bending, M = mu F L x DAF x KF = 0.40 x 65.7 N x 0.603 m x 2.23 x 1.725 = 61 N m; a 10x8 tube has Z = pi (10^4 - 8^4) / (32 x 10) = 58 mm3, sigma = 1,050 MPa against 350 MPa. So each foot needs a braced frame: 4 legs (2.41 m) + a rectangular tail frame 2 x (0.76 + 0.38) = 2.28 m of 8x6 CF (pi/4 (8^2 - 6^2) mm2 x 1.55 g/cm3 = 34 g/m) = 160 g + 10 joints x 5 g + pads = **about 215 g EST**.
Recovered (EST): rib 25x23 -> 14x12 -23.8; skin 3 -> 2 plies -23.2 (2-ply RF 0.773/0.53 = 1.46); shoes and cups -24.2; root-block enlargement -12.2; lighter fin and centre nodes -13: **-96 g**. Net **+119 g**; the hub then reacts all four feet (hub rows "—").
CG: x_cg' = (1,598.4 x 30.17 + 119 x about 250) / 1,717.4 = **45.4 mm, SM -1.9 %: statically unstable** (the frame sits at x 0.2-0.35 m, 0.2-0.3 m behind the CG). Window at 1.966 kg on MN2212: -2.43 %. Cost: legs and braces $43.12 goods, R15 dropped: **about $2,106** with the legs in the reserve tube set.
Transport: unchanged (the frame is inside the present 0.90 x 0.50 x 0.39 m envelope, EST). The legs and frame sit in the prop wash (download, A-P3) and in cruise drag ("—").
**Verdict: reject.** Moving the feet off the fins moves the landing mass behind the CG, which is the opposite of what A needs.

## 4. Option 3: a re-derived design touchdown speed

**Plain sentence: write down how fast the aircraft really touches down under ArduPilot control, design the pad and wing for that speed with a margin, and prove the pad by a drop test.**

### 4.1 What ArduPilot commands (docs read 2026-11-21)
- QLAND: "descending to Q_LAND_FINAL_ALT at Q_WP_SPD_DN until it reaches Q_LAND_FINAL_ALT, at which point it continues to descend at Q_LAND_FINAL_SPD until landing"; landing is recognised when "the motors are at minimum for 5 seconds and its altitude has not changed more than 0.2m for 4 seconds" (https://ardupilot.org/plane/docs/qland-mode.html).
- Q_LAND_FINAL_SPD "The descent speed for the final stage of landing in m/s", range 0.3 to 2; Q_LAND_FINAL_ALT range 0.5 to 50 m; Q_PILOT_SPD_DN "The maximum vertical velocity the pilot may request in m/s going down", range 0.5 to 5; Q_WP_SPD_DN range 0.10 to 10 m/s (https://ardupilot.org/plane/docs/parameters.html). **`Q_LAND_SPEED` does not appear on the current Plane parameter page** (0 matches): the brief's name is from older firmware; the current names are the four above.
- A.param today: `Q_WP_SPD_DN` 1.2, `Q_PILOT_SPD_DN` 1.0, `Q_LAND_FINAL_SPD` 0.3 (the docs minimum), `Q_LAND_FINAL_ALT` 6 (A.param l.116-119). Manual-throttle QSTABILIZE has no descent limit (T-068 F-8).
- So the commanded touchdown is 0.3 m/s in QLAND and AUTO, up to 1.0 m/s with the stick fully down in QHOVER / QLOITER. The 1.2 m/s case came from K09-L D-65 ("landing_sink_ms >= the pilot descent limit") and equals `Q_WP_SPD_DN`, which only applies above 6 m. The SITL touchdowns in the case set are 0.30-0.32 m/s (`landing_path_a.cases`).

### 4.2 Design case
v_design = v_cmd,max + delta_track + delta_gust = 0.5 (with `Q_PILOT_SPD_DN` lowered to 0.5, the docs minimum) + 0.1 (tracking: 2.5x the SITL overshoot 0.04, EST) + 0.2 (vertical gust, ground effect, EST, no source) = **0.8 m/s**, 60 % above the largest commanded descent and 2.5x the SITL touchdowns. It holds only with a flight-card rule: no landings in QSTABILIZE / QACRO. Energy ratio (0.8 / 1.2)^2 = 0.44. Drop height for TP-3: h = v^2 / 2g = 0.64 / 19.62 = **32.6 mm** (73 mm today).

### 4.3 How the demand scales (rigid-body, `cs_land.py`; 23 cases with every 1.2 m/s case set to v, cases above v capped at v; envelope over zeta 0.02 / 0.10 and mu 0.40 / 0.30)

| v m/s | Fp N | Worst stroke mm (of 24) | n g | tilt deg | Hub My (spar) N m | Half-wing My N m | k (vs 12.20 / 8.72) |
|---|---|---|---|---|---|---|---|
| 1.2 | 30 | 21.46 | 12.41 | 2.99 | 12.20 | 8.72 | 1.00 |
| 0.8 | 20 | 17.41 | 7.56 | 1.87 | 9.17 | 6.56 | **0.75** (0.59 / 0.55 at zeta 0.02 only) |
| 0.8 | 15 | 22.60 | 6.03 | 2.42 | 7.28 | 5.00 | 0.60, stroke reserve 1.4 mm |
| 0.8 | 12 | **24.46 bottoms** | 24.6 | 3.10 | 41.4 | 25.9 | fails |
| 0.6 | 15 | **24.23 bottoms** (hard 16 wide + drift .5 y) | 9.0 | 2.19 | 9.49 | 11.58 | fails |
| 0.5 | 10 | **24.50 bottoms** | 30.9 | 2.70 | 19.4 | 20.6 | fails |
| **1.2 on the 20 N pad** | 20 | **24.76 bottoms** | **48.0** | 3.37 | **96.6** | **50.0** | crash |
| 1.0 on the 20 N pad | 20 | 23.72 | 8.32 | 3.18 (> 3.0) | 9.17 | 6.33 | no bottoming; tilt fails |

Findings: (a) the demand does not fall with v^2. Below about 20 N the plateau is set by the drift and lean cases (0.5 m/s drift, 16 deg lean), which bottom a soft pad at any sink rate; Fp 20 N is the lowest robust plateau. (b) At Fp 20 / 0.8 m/s every landing row scales by k = 0.75 (bound) and 0.59 if TP-3 measures zeta <= 0.02. (c) **A 1.2 m/s touchdown on the 20 N pad bottoms at 48 g** (rigid stop, k_stop 5e5 N/m, so the peak is an upper bound), four times A-P5's 12 g pack-retention case. A pilot error that today is a design case becomes a crash that can free the pack.

### 4.4 Which wing build k allows (RF scales as 1/k for these linear rows; P8.2 values)
| Row (P8.2 at k = 1) | k = 0.75 | k = 0.59 (TP-3 zeta <= 0.02) |
|---|---|---|
| Skin K1, 3-ply 1.16 | 2-ply 0.773/k = **1.03**; 1-ply 0.51 | 2-ply 1.31; 1-ply 0.66 |
| Rib R1 25x23 1.32 (J/r 870 mm3) | 20x18 (540): 1.09; 16x14 (333): 0.67, passes with a coupon >= 30/0.67 = 45 MPa; 14x12 (248): needs >= 60 MPa | 16x14 needs >= 35 MPa; 14x12 >= 47 MPa |
| Root block P6 drawn 0.37 | 0.49: the T-068 enlarged block is still needed | 0.63: still needed |
| Centre node C1 1.04, bridge B1 1.03, fin node N4a 1.12 | 1.39 / 1.37 / 1.49 | 1.76 / 1.75 / 1.90 |
| TP-4 bond line 4.5 MPa (D-223), hub Mz 12.86 -> 8.17 N m | 2.9-3.4 MPa | lower |
| A-P5 peak n | 7.56 g (12.41 today) | 5.52 g |

Mass (EST): one ply -23.2 g (-1.06 mm CG), rib 25x23 -> 16x14 -19.6 g (-2.0 mm) or 14x12 -23.8 g (-2.4 mm): **-42.8 to -47 g**. On MN2212: 1.785 kg, window +2.39 %, T/W fresh 1.942 / 1.884, CG 27.13 mm (`cs_prop5_out.txt`): **fails A-P3, A-P2 and A-P4 alone.** BOM $2,071.24 with a second 16x14 tube (R15 dropped); $2,010.69 with the 14x12 rib ($10.69 over).
**Verdict: not adopted now.** It cannot close the window on the present motors, and it turns the 1.2 m/s error case into a pad bottoming. It stays a later mass and margin lever on top of 1-ii, only with (i) a two-stage pad (20 N for 24 mm, then a second stage of about 30 N over about 12 mm more, so a 1.2 m/s touchdown reaches today's demand without bottoming; +12 mm pad height, A-P9 re-check, EST), (ii) TP-3 at 32.6 mm and at 73 mm drops, (iii) `Q_PILOT_SPD_DN` 0.5 and the flight-card rule, and (iv) A-P5 re-checked at the second-stage peak.

## 5. Option 4: concept B re-priced

**Plain sentence: build a conventional small quadplane instead (a 1.2 m wing with a tail on two booms, four lift motors for hover and a pusher motor for cruise) that lands flat on short legs.**

Mass with A's lesson (formula): m_B = m_pack + 1.10 x (m_vendor,non-pack + f x S), with S = 750 g (QP-1 structure EST: wing 360, pod 140, booms 130, tail 60, gear 60) and m_vendor,non-pack = 784 g (MN3110 4 x 99 V, P12x4 4 x 14.5 V, 4-in-1 ESC 7.2 V + pusher ESC 33 EST, pusher group 85 EST, avionics + 4 servos 135 EST, harness 70 EST), pack Tattu 3700 361 g (COST.md). A's structural mass went from 452 g (QP-1, with contingency) to about 862 g (1,598 g basic less about 736 g of vendor items, EST), x1.9, much of it tailsitter landing structure. I use f = 1.0 / 1.3 / 1.6:

| f | m_B kg | T/W fresh (4.454 kgf: SIZING 4.55 kgf x 0.93/0.95) | T/W sag (3.681 kgf) | Verdict on A-P2-equivalent (2.0 / 1.6) |
|---|---|---|---|---|
| 1.0 | 2.048 | 2.17 | 1.80 | pass (QP-1 2,062 g reproduced within 1 %) |
| 1.3 | 2.296 | **1.94** | 1.60 | fails fresh |
| 1.6 | 2.543 | 1.75 | 1.45 | fails both |

B's T/W ceiling is 4.454 / 2.0 = **2.23 kg**: 9 % above its as-sized mass, 2-4 % above the board re-roll (2.18 kg, QP-1 BOARD s1). A larger lift motor than MN3110 on 4S has no readable T-Motor 4S table today (MN4110 is a 6S / 16-18 in motor at $86.99).
Landing: level touchdown on four boom feet; boom root bending with a 35 N foot at 0.32 m: M = 35 x 0.32 x 2.23 = 25 N m, sigma = M x KF / Z(16x14: 166 mm3) = 260 MPa, RF 1.35 (hand, EST, borrowed DAF). A nose-first strike puts a pitch torque into the boom-to-wing joint and the wing over |y| 0.25 m: the same kind of path that failed A, shorter; not computed ("—").
Transport: SIZING.md s9 airframe 1.16 x 0.53 m. On a 1.016 x 0.940 m floor (EST): for any angle t, 1.16 cos t + 0.53 sin t <= 1.016 needs t >= about 62 deg, where 1.16 sin t + 0.53 cos t >= 1.27 > 0.94: **does not lie flat** (height unmeasured). Detachable booms or tail add joints ("—" mass).
Cost (`cs_bom.py`, same floor and cost rules; prices read 2026-11-21): 5 MN3110 $61.90, MN2212 pusher $46.90, 3 P12x4 pairs $38.90, 3 APC 9x6E $3.22, Skywalker 30A $14.99, 2 Tattu 3700 $59.99, 5 servos $13.99, 3 x 16x14 and 2 x 12x10 tubes, tail EST $15; tailsitter-only lines removed (25x23 tube, 6061 node bar, flock, cage struts, lead, damper fluid, silicone, hub bar, yaw planform). **Total $2,291.70, margin -$291.70** (reserve by definition $387.16; held at $327.43: $2,231.97).
Schedule: new CAD to fidelity, new gates, QuadPlane SITL, two booms, tail, pod, five motors; Jacobs closed 19 Dec - 18 Jan (SCHEDULE-A); A's 11-day slack does not cover a restart, and first tethered hover before 18 Feb is unlikely (EST).
**Verdict: reject.** Over budget by $292, T/W headroom gone at any realistic growth, and it does not fit the trunk in one piece.

## 6. Side-by-side (EST unless stated)

| Item | 1-ii (recommended) | 1-i | 2 | 3 | 4 (B) |
|---|---|---|---|---|---|
| Predicted mass | 1.864 kg (1.838 with the rib coupon) | 2.063 | 1.966 | 1.785 | 2.05-2.54 |
| A-P3 window / T/W fresh dl / sag dl | +9.96 / 2.289 / 2.030 | +14.8 / 2.76 / 2.24 | -2.43 / 1.719 / 1.584 | +2.39 / 1.884 / 1.744 | n/a (QuadPlane) / 2.17-1.75 / 1.80-1.45 |
| CG / SM | 27.93 / 5.21 (25.54 / 6.19 with coupon; cage forward -4.8 mm, P8.4) | 19.35 / 8.7 | 45.4 / -1.9 | 27.13 / 5.54 | 12 % SM EST |
| A-P6 1.3 Vs (17.0) | 17.49 (17.37) | 18.40 | 17.96 | 17.11 | 13.1 at 2.06 kg (SIZING) |
| Cruise s (need 204.6) | 233 | 209 | 192 | 251 | 1.28x energy (SIZING) |
| Landing | D-226 cell at 1.2 m/s; plateau 33 N; holds as drawn if TP-3 zeta is about 0.02, else regrows +15-30 g (s1.4) | D-226, grown | legs + frame, cell x0.53 | cell x0.75, 1.2 m/s bottoms | gear on booms, joint "—" |
| BOM total (reserve by definition / held $327.43) | 1,985.76 / 1,970.66; with coupon 1,850.32 / 1,890.44 | about 2,278 (= 2,146.13 + (5 x 15.00 + 8 x 3.32 - 9.40 + 12) x 1.1025 + 15 x 1.1025) | about 2,106 | 2,071.24 / 2,050.31 (16x14); 2,010.69 / 2,020.03 (14x12) | 2,291.70 / 2,231.97 |
| Schedule to April 2027 | low: part swap in Order 1 (1-4 Dec), CAD motor + cups, Lua table, gates once | medium-high | high | medium | high |
| Reused from A | all (CAD, gates, SITL, landing method, test plan) | all but cage motor mounts | most; new frame | all | avionics, power, ground test, SITL install, methods |
| Confidence | medium (model on retailer Kv/Rm/I0; bench decides at line 0.84) | low | low | medium-low | low |

## 7. Budget detail (`cs_bom_out.txt`)
| Scenario | Goods | Spend | Reserve | Total | Margin |
|---|---|---|---|---|---|
| p8 as recorded | 1,550.25 | 1,781.99 | 368.76 | 2,150.75 | -150.75 |
| p8 + today's reads (H743-Wing **$129.01**, was $141.44; 14x12 $15.36; strut 8x6 $8.50, was "—") | 1,541.94 | 1,772.83 | 373.31 | 2,146.13 | -146.13 |
| **1-ii, p8 airframe** (+ prop adapters $10 EST, XT90 / 12 AWG $12 EST) | 1,424.39 | 1,643.23 | 342.53 | **1,985.76** | **+14.24** |
| 1-ii + rib 14x12 (coupon) | 1,374.30 | 1,563.01 | 287.31 | **1,850.32** | **+149.68** |
| 1-ii + 3, rib 16x14 | 1,401.76 | 1,593.28 | 317.59 | 1,910.87 | +89.13 |
| 3 alone, rib 16x14 | 1,519.31 | 1,722.88 | 348.36 | 2,071.24 | -71.24 |
| 2 legs (legs in the reserve) | | | | about 2,105.77 | -105.77 |
| 4 concept B | 1,703.51 | 1,904.54 | 387.16 | 2,291.70 | -291.70 |

With U/EST lines +30 % (G7, information only): 1-ii $2,104.34; 1-ii with coupon $1,968.89.

## 8. Recommendation, first three tasks, decisions

**Recommendation: 1-ii (SunnySky X2216 880KV on the APC 9x4.5MR), D-226 kept at 1.2 m/s, rib coupon, cage-forward CG rung. Option 3 is a later lever, not part of this decision.** The window, both T/W checks, cruise time and the budget pass on paper. The CG passes with the coupon (thin, 0.4 mm) or with the cage-forward rung (P8.4). Two open items remain:
- **A-P6.** 17.49 m/s against 17.0 on CLmax 0.75 EST. A-P6 is derived. Its own verification line says the measured stall replaces 0.75; CLmax >= 0.794 passes at 1.864 kg. Alternatively, re-derive cruise to 17.5 m/s: mass ceiling (17.5/17)^2 x 1.761 = 1.866 kg; need 204.6 x 17/17.5 = 198.8 s; available about 233 / (17.5/17)^3 = 214 s, EST; turn radius 54.1 m; fence bound 75 + 54.1 + 94 = 223 m <= 240.
- **The landing demand at the new mass** (s1.4).

First three tasks:
1. **T-propulsion (sonnet implementer, $0):**
   - Add the X2216 constants to `prop_a.py` / `params-A.json` (Kv 880, Rm 0.117, I0 0.5, line 17.7 A). Fix `mission.pack_ah` 2.3 -> 2.8.
   - Judge A-P6 at the predicted mass, not the gate.
   - Regenerate the Lua cap table. Set `Q_M_BAT_CURR_MAX` to 65 A. Change to XT90 / 12 AWG and update the wire inventory.
   - Read the APC 9x4.5MR rpm limit and the SunnySky drawing (length, mount, leads) before Order 1.
   - Re-spec TP-1 / TP-2 for the X2216: pass derate >= 0.84; one motor <= 17.7 A at the cap; current-line check against the 320 W rating; rpm from the audio FFT.
2. **T-landing re-run (sonnet, $0):**
   - Re-run `t077p6_demand.py` at the 1-ii mass and CG with the X2216 masses and the plateau scaled with mass (33 N). s1.4 shows the 24 mm / 30 N pad bottoms and the 28 mm pad tilts 3.37 deg.
   - Re-judge every D-226 row and the root block (`t077p8_path.py`) per zeta. TP-3 decides between "as drawn" (zeta about 0.02) and a regrown cell (zeta-0.10 bound, EST +15-30 g). The rib torsion coupon (SL-4) decides 14x12; its line rises with the demand (79 MPa x the new rib demand ratio).
   - Close the 0.09 deg end-tilt miss (pad edge or plateau). Update TP-3 to the 33 N plateau.
3. **T-CAD and gates (sonnet, after 1 and 2):**
   - Model the X2216 (marked where the drawing lacks a dimension) and its cups.
   - Apply the coupon result and the cage-forward rung if the CG needs it.
   - Run the gates once (build, collide pose 21, linkage poses, assembly, wire inventory, cad_mass, mission gate, prop, proofs, drawings, `python -I tools/ledger_audit.py`).
   - Price the BOM copy.

Decisions for Dillon: purchase approval for the motor swap in Order 1 (money; net saving about $160 on the BOM: $2,146.13 -> $1,985.76), and the crash-reserve basis (held $ value or by definition; both under $2,000). No hard constraint changes. For information: AM-016's failure branch named "bigger props or motors"; this study takes that branch before the bench rather than after it, because the bench line for the present motor (1.006) asks the motor to beat its catalogue.

## 9. Findings

| ID | Severity | Evidence | Required fix |
|---|---|---|---|
| CS-1 | CRITICAL | s1: the window ceiling (basic 1,474 g) is below p7 (1,481 g) on MN2212 / 12.1 A; no landing path fits | Change the propulsion (1-ii) before the 2026-12-15 bench; do not spend further CAD on landing-path mass to save the window |
| CS-2 | MAJOR | s1: CL-A-STALL judged at 1.47 kg; at the predicted 1.833 kg 1.3 Vs = 17.34 > 17.0 | Judge A-P6 at the predicted mass (AM-011); record the resolution (measured CLmax or cruise 17.5 m/s) |
| CS-3 | MAJOR | s1.4: at 1.864 kg the 24 mm / 30 N pad bottoms (24.16 mm, 110.8 N, tilt 3.35 deg); 28 mm tilts 3.37 deg; 33 N tilts 3.09 deg and raises the zeta-0.10 demand (hub x1.15, half-wing x1.56 in one case). The p6 demand was run at 1.705 kg; the p8 tree is 1.833 kg | Re-run the demand at the predicted mass with the plateau scaled to mass; re-judge all landing rows per zeta after TP-3 |
| CS-4 | MAJOR | s4.3: a 20 N pad bottoms at 1.2 m/s (48 g); below 20 N the drift / lean cases bottom at any sink | Option 3 only with a two-stage pad, TP-3 at both drop heights, `Q_PILOT_SPD_DN` 0.5 and the no-manual-landing rule |
| CS-5 | MINOR | s1: `params-A.json` pack_ah 2.3 (O4b pack 2,800 mAh); CL-A-CRUISE-AVAIL 141.6 s is a stale fail (236 s with 2.8 Ah) | Update the parameter; re-run proofs |
| CS-6 | MINOR | s7: H743-Wing now $129.01 (RMRC, In Stock); 8x6 strut tube $8.50 (was "—"); 14x12 $15.36 (was U $15.34) | Update the BOM copy at the next BOM task |
| CS-7 | MINOR | s4.1: `Q_LAND_SPEED` is not a current Plane parameter | Use Q_WP_SPD_DN / Q_LAND_FINAL_ALT / Q_LAND_FINAL_SPD / Q_PILOT_SPD_DN in all records |
| CS-8 | INFO | s2.1: MN2212 KV920 and MN3110 on 9 in give at most +1.5 % window; 10-12 in props bring the D-217 vibration band, a cruise pitch-speed problem (12x4: 12.9 m/s) and A-P6 failures | None |
| CS-9 | INFO | s5: B's T/W ceiling 2.23 kg; airframe 1.16 m does not lie flat on a 40 x 37 in floor | Keep B closed unless A fails the X2216 bench |

## 10. Sources (read 2026-11-21 unless stated)
- ArduPilot Plane parameters: https://ardupilot.org/plane/docs/parameters.html ; QLAND mode: https://ardupilot.org/plane/docs/qland-mode.html
- T-Motor MN3110 (KV470/700/780 data, $61.90): https://store.tmotor.com/goods.php?id=334 ; MN2212 V2.0 (KV780/920 data, $46.90): https://store.tmotor.com/goods.php?id=388 ; P12x4 prop pair $38.90, 14.5 g: https://store.tmotor.com/product/polish-carbon-fiber-12x4-prop.html ; MN4110 $86.99: https://store.tmotor.com/product/mn4110-motor-navigator-type.html
- RMRC (readymaderc.com/products/details/...): SunnySky X2216 880KV `85810-...-880kv` $18.99; X2216 V3 950KV `85634-...` $24.99 (no Rm on page); Kakute H743-Wing `87185-...` $129.01; SpeedyBee BLS 35A `86873-...` $45.66; Tattu 3700 4S 45C `tattu-3700mah-45c-4s1p-lipo-xt60` $59.99; Skywalker 30A V2 `85587-...` $14.99; APC 9x6E $3.22; APC 10x4.5MR $3.32 / MRP $3.16; APC 10x5.5MR / MRP $3.32; CF tubes 16x14 $27.46, 14x12 $15.36, 12x10 $12.26, 10x8 $11.44, 8x6 $8.50, 6x4.5 $4.40 (all In Stock).
- apcprop.com (PER3 files, rpm limits): refused (Cloudflare) on 2026-11-21: "—".
- Repo: T077_cad.md P8; CHANGE-LOG D-182, D-213..D-226; audits 2026-11-20 landing root cause, 2026-11-21 DAF ruling, saddle load path; review/QP-1 BOARD, SIZING, SIZING-A, COST; TEST-PLAN-O4B; SCHEDULE-A; A.param l.116-119; REQUIREMENTS-A A-P1..A-P16; proofs/claims_a1_flight.py.

## 11. Limits
- The thrust numbers are the repo's EST model. The X2216 has no maker thrust table. Its line (17.7 A from 320 W) and its mass with leads are EST. The 10 in rows use similarity scaling, which is optimistic on thrust per amp (s2.1 check).
- Landing results are rigid-body with the D-222 pad law at the p6 mass and CG (except s1.4). The k-scaling of strength rows assumes each row is linear in the demand. The rigid stop makes the bottoming peaks upper bounds.
- Masses of legs, frame, cups, adapters and connectors are EST. B's mass uses a structure-growth factor, not a design.
- Trunk floor 40 x 37 in is the brief's EST; trunk height is unmeasured.
- Prices are retailer pages today; shipping follows the `bom_p8.py` EST rules. The T-Motor variant price for KV920 is assumed equal to the page price (U).
