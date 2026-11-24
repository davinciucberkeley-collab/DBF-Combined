# QP-1 sizing, candidate A: scaled quad tailsitter (2026-11-14)

Reproduce: `python -I redesign/qp/sizing_A/sizing_a.py` (stdlib, prints markdown, writes nothing). Only `redesign/qp/sizing_A/` and this file were written; no git.
Labels: `V` vendor page read today; `U` snippet or aggregator, page not read; `EST` estimate (named constant in the script); `—` unknown.
Basis: RESTUDY A (0.90 x 0.245 m wing, 2 fins, 4 fixed motors in an X, 4S, 2 packs); mission from A2 s2.1 (3.0 min hover-mode incl. 40 s go-around, 3.5 min cruise, 20 % reserve); K09-L lessons from B3, E1, C4, C5, A3 (closure round 2026-11-14), each re-computed at this scale, not copied.

## Verdict

A closes on mass, thrust, current, pack, landing and cost. Three tailsitter risks are **marginal, none fails once one design change is taken**: cant must go from K09-L's 10 deg to 14 deg for hover yaw; the pack must sit in the motor cage ahead of the leading edge for static margin; and the cruise prop is pitch-limited. Two numbers rest on the maker's thrust table, whose rpm column is internally inconsistent (below), so the first bench test is not optional.

| Risk | Rating | Number |
|---|---|---|
| Hover yaw, 5 m/s, wingtip 20 deg off | **MARGINAL** | ratio 1.57 at 14 deg cant (limit 1.5, thin); **1.25 FAIL at K09-L's 10 deg** |
| Transition entry window | **PASS** (low-fidelity model) | 1.33-1.73 W, +-13 % (K09-L +-2.5 %) |
| Fin-tip landing / tip-over | **PASS** | 33.2 deg static (limit 30); parked wind-tip 6.8 m/s; 1.85 restoring/overturning at 5 m/s |
| Rotor-excited fin vibration | **MARGINAL** | f1 219 Hz ideal; separation 43 % / 22 % / 7 % at root fixity 1.0 / 0.85 / 0.75 (need 20 %) |
| Wind sensitivity at lower mass | **MARGINAL** | lean 29 deg at 5 m/s (K09-L 22), 47 deg at 7 m/s; thrust 53-68 % of sagged max |

## 1. Mass and box

| Item | g | Source |
|---|---|---|
| Wing (foam, CF spar, 2 elevons) | 220 | EST |
| 2 fins 0.36 x 0.12 m, foot pads | 36 | EST |
| 4 x T-Motor MN2212 V2.0 KV780 with cables | 260 | V: 65 g each, store.tmotor.com/goods-388-MN2212-V20.html, 2026-11-14 |
| 4 x T9545 props | 32 | EST |
| 4 x 45 A ESC | 40 | EST (RESTUDY) |
| 1 x CNHL 4S 2000 mAh 100C | 232 | U: 232 g listed (RaceDayQuads, WREKD, search 2026-11-14) |
| FC, GPS, RX, airspeed, wiring | 110 | EST (RESTUDY) |
| 2 servos + linkage | 30 | EST (RESTUDY) |
| Motor mounts / X cage | 120 | EST (RESTUDY) |
| Hardware, tape, paint | 35 | EST |
| Base 1,115 g; +10 % contingency | **1,226 g** | RESTUDY A 1,228 g |

Box (cruise attitude, 1.25 x 0.55 x 0.45 m): props on 0.90 x 0.50 x 0.39 m, slack 0.35 / 0.05 / 0.07 m, **PASS**; props off 0.90 x 0.39 x 0.36 m. The 0.05 m slack is the 9.5 in props on a 0.26 m motor grid (tip clearance 0.019 m, design choice).

## 2. Wing

S 0.22 m2, b 0.90 m, AR 3.68, wing loading 54.7 N/m2. CLmax 0.75 (EST; K09-L's B3 Vs 12.01 m/s implies about 0.85, RESTUDY used 0.70) gives **Vs 11.0 m/s, 1.3 Vs 14.3 m/s**. At 15 m/s: CL 0.405, Re 2.45e5, CD0 0.0356 (wing 0.0151 from Cf, fins 0.0058, motors and struts 0.0146, all EST), CDi 0.0177 (e 0.8), **L/D 7.6**, drag 1.58 N. RESTUDY assumed L/D 8.

## 3. Motors, props, ESCs

Part: T-Motor MN2212 V2.0 KV780, T-MOTOR 9545B prop, 14.8 V. **Published rows (V, store.tmotor.com, 2026-11-14):** 50 % 293 g / 2.1 A / 31.1 W; 65 % 476 g / 4.0 A; 75 % 605 g / 5.6 A; 85 % 742 g / 7.4 A; 100 % 918 g / 10.3 A / 152.4 W. Rating 13 A max continuous, 180 s; 200 W; 173 mohm; no burst rating (—). The page also claims 1.8 kg max thrust, which its own tables do not support, and calls the motor "MN4112" in places; I used only the table rows.

Table quality: the 100 % row lists 7,350 rpm, which implies a static CT of 0.148, above the 0.10-0.11 expected of a 9x4.5 prop. So either the rpm column or the thrust is off. A momentum cross-check on the power column gives FM x eta = 0.48, consistent with K09-L's 0.45, so I trust thrust and power and not rpm. `T9545` vs `9545B` naming is unresolved in vendor listings (U).

| Check | Result | Limit |
|---|---|---|
| Hover thrust/motor (14 deg cant, 3 % download) | 326 g, 36.1 W each, 159 W total with x1.10 | — |
| T/W fresh (table at 14.8 V, no credit for 16.8 V) | **2.82** | >= 2.0 PASS |
| T/W sag (3.6 V/cell, pack R 30 mohm EST, 13.2 V, hot x0.97) | **2.16** | >= 1.6 PASS |
| Hover current | 2.4 A/motor, 10.7 A pack | 13 A PASS |
| Full-duty motor current, fresh 16.8 V (EST, I ~ V^2) | 13.3 A | 13 A / 180 s: **+2 %, over** |
| One-motor transient (one saturated, three at hover) | 13.3 A uncapped; **10.8 A with `Q_M_SPIN_MAX` 0.90** | 13 A PASS with cap |
| Peak pack current | 41 A | 200 A (100C x 2 Ah) PASS |

K09-L lesson re-checked (E1 s1, spin cap): the motor has no burst rating, so I do not pass the 2 % overshoot on an I2t argument. The cap fixes it, and at 0.90 duty fresh thrust is still about 2.3 T/W. ESC 45 A (U, RESTUDY) is 3x the motor current. **Cant for yaw: 14 deg** (cos = 0.970, included above); see s4.

## 4. Tailsitter specifics

**Hover yaw (K09-L B3 model: wingtip into 5 m/s, 20 deg off, plate Cd 2.05, arm 0.25 b, authority at 30 % differential).** Wind force 0.79 N, moment 0.178 N m. Authority 0.279 N m (cant 0.201 + rotor reaction 0.078; Q 65 N mm per motor at 4,248 rpm EST, arm 0.230 m). **Ratio 1.57** at 14 deg. Sweep: 6 deg 0.93, 8 deg 1.09, **10 deg 1.25**, 12 deg 1.41, 15 deg 1.65; without cant 0.44. So K09-L's 10 deg fails here by 17 %: the lighter airframe has less thrust times arm against a wing that scales more slowly. Yaw acceleration 7.8 rad/s2 (I_x 0.036 kg m2 EST; need >= 2.0). No elevon-in-slipstream credit taken (K09-L took none). **MARGINAL**: 4 % over the limit on EST arm and Cd; K09-L's own margin was 1-2 %. Cost of 14 deg is 1.5 % thrust. `T-B3-HOVER-YAW-WTIP`-style hanging test confirms.

**Transition entry window.** A point-mass pitch-over (flat-plate wing, 12 deg/s to 70 deg, thrust held constant: B3's entry law) finds altitude-neutral entry from 0.97 W (0.85 W with a 4 m/s pre-climb). It has no pitch-moment or elevon-use limit, which is what bound K09-L (1.283-1.328 W), so I use K09-L's low edge, 1.33 W, scaled unchanged. High edge 0.80 x T/W sag = **1.73 W**. Window 1.33-1.73 W, +-13 %, against K09-L's 1.328-1.397 W (+-2.5 %): the thrust margin (T/W 2.16 sag vs 1.75) buys the width. **PASS**, with these cautions: the sim handover is 26-32 m/s because it has no speed limit, so entry must be paired with the pitch-rate / airspeed limits; B3's 4.17 m/s pre-climb is not needed here. `—`: elevon pitch authority at the post-stall moment peak; it needs a B3-style time-domain run, which I did not do.

**Fin-tip landing / tip-over.** Feet at the fin aft edge, 0.36 m apart; CG 25 mm aft of the LE, 0.275 m above the feet. Static tip angle **33.2 deg** (K09-L 30.0-30.4, limit 30). Parked broadside to the wind, tip at 6.8 m/s steady; restoring/overturning **1.85 at 5 m/s** (K09-L analogue 1.59). Sliding-foot energy bound on touchdown drift 1.03 m/s (upper bound). 1.2 m/s hard landing on 6 mm foot crush (EST) is 12 g, 147 N total; structure and cartridge life not analysed (C5's 3-D sim and life count have no analogue here yet). **PASS**; it rests on the fin height of 0.36 m, which is the stance width.

**Rotor-excited fin vibration.** Fin half as a cantilever (0.18 m, 0.12 m chord, 0.2 mm CFRP skins on 5 mm foam, EST laminate): EI 16.2 N m2, 101 g/m, f1 219 Hz ideal. Hover 1P/2P: 71/142 Hz fresh, 76/153 Hz sagged (+8 % rpm, EST). Worst separation: 43 % at fixity 1.0, 22 % at 0.85, **7 % at 0.75 FAIL**. K09-L's C4 found the root mount, not the fin, set stiffness. **MARGINAL**: a tap test of the built fin decides. Escape: stiffen to push f1 above 200 Hz at fixity 0.75 (EST), or drop below 1P (not credible for a fin this size).

**Wind sensitivity at the lower mass.** Disk loading 66 N/m2 (K09-L 104), wing loading 54.7 (K09-L 73.9). Hovering broadside (plate Cd 2.0): 5 m/s drag 6.6 N, **lean 29 deg** (K09-L 22), thrust 1.14 W = 53 % of sagged max; 7 m/s (5 + 2 gust) 47 deg, 68 %; 8 m/s 55 deg, 80 %. Thrust holds, but the lean needs `Q_ANGLE_MAX` raised from its default 30 to about 45, and a 7 m/s gust pushes beyond that. **MARGINAL**; the lighter aircraft leans further for the same wind. Mitigation: hover wing-edge-on into the wind where heading allows.

## 5. Pack and mission energy

| Cruise model | Cruise W | Total Wh | Need (/0.80 /0.90) | Pack | Reserve left |
|---|---|---|---|---|---|
| 9545, EST prop model (eta_p 0.26 x 0.76) | 122 | 16.7 | 23.2 | 29.6 Wh | 37 % PASS |
| 9x6, EST (eta_p 0.37) | 84 | 14.4 | 20.1 | 29.6 | 46 % |
| RESTUDY eta 0.50 | 48 | 12.3 | 17.1 | 29.6 | 54 % |

Hover 7.95 Wh (159 W x 180 s), two transitions 1.32 Wh (10 s each, EST), 31 m climb 0.26 Wh. **4S 2000 mAh, 232 g, 29.6 Wh, two packs.** Hover 5.4 C, peak 21 C of 100 C. Even the worst case leaves 37 % reserve, so a 1500 mAh pack (about 25 % lighter) would also close; no priced or weighed 1500 mAh pack was found, so not selected.

**Open prop issue:** the 9545's pitch speed at 7,011 rpm is 13.4 m/s, below the 15 m/s cruise, so it works near zero thrust with eta_p about 0.26 (EST model: CT = CT0 (1-(J/J0)^2), CP = CP0 (1-0.65 J/J0); no in-flight data for any prop here). RESTUDY's 48 W cruise is not credible with this prop; 122 W is the planning number. A higher pitch prop helps cruise, but then the published hover table no longer applies.

## 6. CG and static margin

CG with the pack in the motor cage (centre 20 mm ahead of the LE): **24.6 mm aft of the LE (10.1 % c)**. NP 44.0 mm inviscid (wing AC at 0.25 c, four props destabilising as lifting surfaces ahead of the LE: normal-force slope 0.6 each, K09-L B4 value, Ribner k = 1, EST), 40.7 mm with a viscous shift of -3.3 mm (K09-L's free-transition -4 mm scaled by chord). **SM 6.6 %** (limit 5 %). Aft limit 28.5 mm, forward limit (SM 15 %, EST) 4.0 mm. Pack at the LE: SM 4.9 % (marginal fail); pack 20 mm aft of the LE: 3.2 %. Pack at +40 mm (centre of the wing): 1.5 % FAIL. **The pack location is a hard design constraint** and the tape-on turbulator lesson (K09-L D-163, -1 mm tripped) is not taken here; tripping would restore 3 mm. The aft margin is 3.9 mm of CG.

## 7. Cost against RESTUDY's $1,461

The script reproduces RESTUDY A with its own lines: spend $1,331.18, crash reserve $129.45, total $1,460.63. Re-priced with the chosen parts:

| Change | RESTUDY | Here |
|---|---|---|
| Motors x5 | $30.00 EST each | $46.90 each (V, T-Motor store, 2026-11-14) |
| Props | 12 x $3.50 | 6 pairs x $10.42 (U, rcdrone.top snippet, sold out in the listing) |
| Packs x2 | $38.00 | $40.49 (U, pessimistic of $24.99-40.49) |
| ESC, foam, CF, PETG, hardware, floor | as RESTUDY | as RESTUDY (U / EST) |

Spend $1,452.45 + crash reserve $132.20 = **$1,584.65** (+$124 over RESTUDY), margin **$415** to $2,000. With the candidate lines +30 % (floor unchanged): $1,781, margin $219. The T-Motor price is the largest single item (+$84.5 for 5 motors) and is the only vendor-page price among the changes.

## Open risks

1. Table rpm column inconsistent; thrust stands but must be checked on a bench stand (E1's T-E1-STAND analogue) before motors are bought in bulk.
2. 14 deg cant is a new mount design; yaw ratio is 1.57 on EST arm/Cd.
3. Cruise prop pitch; 122 W planning cruise, and a trade against hover thrust.
4. Pack location, forward of the LE in the cage, sets SM; it is a 20 mm effect on 6.6 %.
5. Fin f1 depends on root stiffness; tap test.
6. 5-7 m/s hover needs 29-47 deg lean; set `Q_ANGLE_MAX` accordingly.
7. Not done: time-domain pitch-over with elevon limit, 3-D landing, mount stiffness, fin structure at 12 g, ESC/Bluejay checks, SITL.
