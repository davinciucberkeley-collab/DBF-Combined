## Iteration 3 (D-185 as ruled): inputs
Rotor bands (one truth, QP-4 FOLDIN): hover 6018 / 6272 / 7151 rpm, 1P 100-119 Hz, 2P 201-238 Hz; cruise 7,300-7,600 rpm, 1P 122-127, 2P 243-253 Hz; one motor at the 0.90 cap 9349 rpm (`qp/A/prop_a.py` one_motor, fresh 16.8 V), 1P 156, 2P 312 Hz; no-cap full throttle 10,142 rpm (prop_a.py). Separation rule: f <= band_low/1.2 or f >= 1.2 band_high: excludes **84-304 Hz** for strongly coupled modes.
Structure frozen at 473 g (wing 191 / fins 119 / cage 122 / hardware 40). Forced response: U 1.0 g mm per rotor, 2P axial ripple 5 % of thrust (thrust law T = 3.94 N (rpm/6,272)^2, 8.75 N at the cap), damping 1 % (and 0.5 %) `EST`, worst-phase modal sum, 1P + 2P of all rotors added (conservative), all FE modes to 100 solved.

### Modes with coupling, exact (coupling = max(cx, cy), mass-normalised |phi| over the four motors)
| Corner | f (Hz) | part | cx | cy | coupling | in excluded 84-304 Hz? | 1P / 2P rpm that hits it | verdict at STRONG 0.5 |
|---|---|---|---|---|---|---|---|---|
| kd | 7.9 | bridge 50% | 0.00 | 2.16 | 2.16 | no | - | strong, outside: pass |
| kd | 12.1 | spar 67% | 2.02 | 0.09 | 2.02 | no | - | strong, outside: pass |
| kd | 15.8 | bridge 58% | 0.00 | 1.36 | 1.36 | no | - | strong, outside: pass |
| kd | 25.4 | spar 54% | 0.51 | 0.52 | 0.52 | no | - | strong, outside: pass |
| kd | 28.7 | arm 43% | 2.85 | 0.55 | 2.85 | no | - | strong, outside: pass |
| kd | 35.6 | rib 39% | 1.17 | 1.64 | 1.64 | no | - | strong, outside: pass |
| kd | 36.0 | spar 74% | 0.56 | 0.00 | 0.56 | no | - | strong, outside: pass |
| kd | 37.0 | arm 100% | 3.43 | 0.05 | 3.43 | no | - | strong, outside: pass |
| kd | 37.0 | arm 100% | 0.05 | 3.43 | 3.43 | no | - | strong, outside: pass |
| kd | 39.2 | arm 99% | 0.24 | 3.27 | 3.27 | no | - | strong, outside: pass |
| kd | 44.1 | arm 97% | 2.86 | 0.00 | 2.86 | no | - | strong, outside: pass |
| kd | 44.5 | arm 65% | 0.33 | 2.40 | 2.40 | no | - | strong, outside: pass |
| kd | 49.7 | spar 59% | 0.57 | 0.08 | 0.57 | no | - | strong, outside: pass |
| kd | 63.8 | arm 59% | 1.35 | 1.27 | 1.35 | no | - | strong, outside: pass |
| kd | 139.4 | spar 79% | 0.00 | 0.05 | 0.05 | yes | 1P at 8,363 | weak, in band: by forced response |
| kd | 168.7 | rib 37% | 0.07 | 0.00 | 0.07 | yes | 1P at 10,121 | weak, in band: by forced response |
| kd | 199.5 | spar 51% | 0.01 | 0.46 | 0.46 | yes | - | weak, in band: by forced response |
| nom | 8.1 | bridge 50% | 0.00 | 2.13 | 2.13 | no | - | strong, outside: pass |
| nom | 12.4 | spar 66% | 2.01 | 0.11 | 2.01 | no | - | strong, outside: pass |
| nom | 16.5 | bridge 60% | 0.00 | 1.41 | 1.41 | no | - | strong, outside: pass |
| nom | 30.7 | arm 43% | 2.85 | 0.55 | 2.85 | no | - | strong, outside: pass |
| nom | 37.2 | rib 36% | 1.19 | 1.54 | 1.54 | no | - | strong, outside: pass |
| nom | 38.6 | spar 74% | 0.56 | 0.00 | 0.56 | no | - | strong, outside: pass |
| nom | 39.6 | arm 100% | 1.59 | 3.04 | 3.04 | no | - | strong, outside: pass |
| nom | 39.6 | arm 100% | 3.04 | 1.59 | 3.04 | no | - | strong, outside: pass |
| nom | 42.0 | arm 99% | 0.24 | 3.27 | 3.27 | no | - | strong, outside: pass |
| nom | 47.3 | arm 97% | 2.86 | 0.00 | 2.86 | no | - | strong, outside: pass |
| nom | 47.3 | arm 69% | 0.40 | 2.47 | 2.47 | no | - | strong, outside: pass |
| nom | 53.2 | spar 59% | 0.57 | 0.08 | 0.57 | no | - | strong, outside: pass |
| nom | 68.1 | arm 60% | 1.35 | 1.28 | 1.35 | no | - | strong, outside: pass |
| nom | 148.6 | spar 80% | 0.00 | 0.05 | 0.05 | yes | 1P at 8,914 | weak, in band: by forced response |
| nom | 180.7 | rib 37% | 0.07 | 0.00 | 0.07 | yes | - | weak, in band: by forced response |
| nom | 213.7 | spar 51% | 0.01 | 0.46 | 0.46 | yes | 2P at 6,411 | weak, in band: by forced response |
| hi | 9.6 | bridge 50% | 0.00 | 2.16 | 2.16 | no | - | strong, outside: pass |
| hi | 14.8 | spar 67% | 2.03 | 0.09 | 2.03 | no | - | strong, outside: pass |
| hi | 19.3 | bridge 58% | 0.00 | 1.36 | 1.36 | no | - | strong, outside: pass |
| hi | 30.9 | spar 55% | 0.51 | 0.53 | 0.53 | no | - | strong, outside: pass |
| hi | 34.8 | arm 43% | 2.85 | 0.55 | 2.85 | no | - | strong, outside: pass |
| hi | 43.4 | rib 39% | 1.17 | 1.65 | 1.65 | no | - | strong, outside: pass |
| hi | 43.7 | spar 74% | 0.56 | 0.00 | 0.56 | no | - | strong, outside: pass |
| hi | 44.9 | arm 100% | 0.04 | 3.43 | 3.43 | no | - | strong, outside: pass |
| hi | 44.9 | arm 100% | 3.43 | 0.04 | 3.43 | no | - | strong, outside: pass |
| hi | 47.7 | arm 99% | 0.24 | 3.27 | 3.27 | no | - | strong, outside: pass |
| hi | 53.6 | arm 97% | 2.86 | 0.00 | 2.86 | no | - | strong, outside: pass |
| hi | 54.1 | arm 64% | 0.32 | 2.39 | 2.39 | no | - | strong, outside: pass |
| hi | 60.3 | spar 59% | 0.57 | 0.08 | 0.57 | no | - | strong, outside: pass |
| hi | 77.6 | arm 59% | 1.34 | 1.27 | 1.34 | no | - | strong, outside: pass |
| hi | 169.4 | spar 78% | 0.00 | 0.05 | 0.05 | yes | 1P at 10,165 | weak, in band: by forced response |
| hi | 204.9 | rib 37% | 0.07 | 0.00 | 0.07 | yes | 2P at 6,147 | weak, in band: by forced response |
| hi | 242.3 | spar 51% | 0.01 | 0.46 | 0.46 | yes | 2P at 7,269 | weak, in band: by forced response |

Strongly coupled (>= 0.5) modes inside the excluded band: none.
- kd: highest strongly coupled mode below the bands 64 Hz (limit 83.6, margin 31 %); lowest above 432 Hz (limit 304, margin 42 %)
- nom: highest strongly coupled mode below the bands 68 Hz (limit 83.6, margin 23 %); lowest above 463 Hz (limit 304, margin 52 %)
- hi: highest strongly coupled mode below the bands 78 Hz (limit 83.6, margin 8 %); lowest above 525 Hz (limit 304, margin 73 %)

### Strongly-coupled threshold, numeric basis
A mode is harmless in a rotor band if, driven on resonance by the 1P unbalance (or 2P ripple) of all four rotors at 1 g mm, its own contribution at the FC stays under the 30 m/s2 VIBE limit. On-resonance single-mode FC acceleration a = (force x sum|phi_motor| x |phi_FC|) / (2 zeta); it scales linearly with coupling. Modes below 700 Hz that a rotor order can reach (1P 100-175 Hz, 2P 200-350 Hz):
| Corner | f (Hz) | coupling | |phi_FC| sum | a_res zeta 1 % (m/s2) | a_res zeta 0.5 % | fraction of 30 at zeta 0.5 % |
|---|---|---|---|---|---|---|
| kd | 139 (1P) | 0.05 | 0.00 | 0.0 | 0.0 | 0.00 |
| kd | 169 (1P) | 0.07 | 0.50 | 0.0 | 0.0 | 0.00 |
| nom | 149 (1P) | 0.05 | 0.00 | 0.0 | 0.0 | 0.00 |
| nom | 214 (2P) | 0.46 | 0.23 | 0.0 | 0.1 | 0.00 |
| hi | 169 (1P) | 0.05 | 0.00 | 0.0 | 0.0 | 0.00 |
| hi | 205 (2P) | 0.07 | 0.50 | 0.7 | 1.4 | 0.05 |
| hi | 242 (2P) | 0.46 | 0.23 | 0.1 | 0.1 | 0.00 |

Worst a_res per unit coupling (zeta 0.5 %): 19 m/s2 per 1.0 coupling (hi 205 Hz). Coupling at which one mode alone reaches 30 m/s2: **1.58** (zeta 0.5 %) by this linear scaling. D-185 threshold 0.5 as ruled; see the verdict below.

### Forced response, full rpm sweep (all four rotors at the same rpm, envelope), U 1.0 g mm
| Corner | zeta | worst FC accel over 6,000-10,500, sum of axes (m/s2) at rpm | per-axis max / sqrt2 (VIBE-like rms) | MS vs 30 | worst up to 10,142 (no-cap full throttle) | worst up to 9,349 (0.90 cap, all four) | cruise 7,300-7,600 worst (T 0.5 N) | one motor at cap (others hover) | MS |
|---|---|---|---|---|---|---|---|---|---|
| kd | 1.0 % | 27.1 at 10,500 | 12.6 | +0.11 | 23.8 at 10,125 | 19.7 at 9,325 | 10.0 at 7,600 | 12.3 | +1.44 |
| kd | 0.5 % | 28.5 at 10,475 | 12.6 | +0.05 | 23.8 at 10,125 | 19.7 at 9,325 | 10.0 at 7,600 | 12.3 | +1.44 |
| nom | 1.0 % | 25.1 at 10,500 | 12.5 | +0.20 | 23.2 at 10,125 | 19.6 at 9,325 | 10.2 at 7,600 | 12.5 | +1.41 |
| nom | 0.5 % | 25.1 at 10,500 | 12.5 | +0.20 | 23.2 at 10,125 | 19.6 at 9,325 | 10.2 at 7,600 | 12.5 | +1.41 |
| hi | 1.0 % | 25.0 at 10,500 | 12.9 | +0.20 | 23.3 at 10,125 | 20.1 at 9,325 | 10.9 at 7,600 | 13.6 | +1.21 |
| hi | 0.5 % | 25.0 at 10,500 | 12.9 | +0.20 | 23.3 at 10,125 | 20.1 at 9,325 | 10.9 at 7,600 | 13.6 | +1.20 |

Peak locations (kd / nom / hi, zeta 1 %): the sweep maximum sits where a rotor order meets a coupled mode:
- kd: 11.0 m/s2 at 6,600 rpm (1P 110 / 2P 220 Hz)
- nom: 12.5 m/s2 at 7,050 rpm (1P 118 / 2P 235 Hz)
- hi: 11.6 m/s2 at 6,150 rpm (1P 102 / 2P 205 Hz); 16.2 m/s2 at 8,025 rpm (1P 134 / 2P 268 Hz)

### Hard-mounted FC (D-186): IMU vibration at the spar centre
No isolation credit: the FE node is the rigid spar centre, foam tape 1.5 mm stiffness is taken as rigid (mount frequency not measured, `EST`). Worst FC amplitude, sum of the three axes (conservative): **27.1 m/s2 at zeta 1 %, 28.5 at 0.5 %** at the 10,500 rpm end of the sweep (all four rotors at 10,500 rpm is not reachable: the uncapped maximum is 10,142 rpm, the 0.90 cap 9,349 rpm; the curve rises there with the rigid-body 1P force, U omega^2); the physical envelope (all four at the cap) is the 9,349 column; one motor at the cap 13.6. ArduPilot's VIBE is the per-axis standard deviation (about amplitude / sqrt 2 for a sinusoid), so the per-axis column above is the like-for-like number; the sum of axes is compared with 30 as a bound. Guidance: VIBE < 30 m/s2, source https://ardupilot.org/copter/docs/common-measuring-vibration.html (checked 2026-11-15 in QP-3 / FOLDIN; guidance 30 m/s2 per the task and BOARD).

### Control-band clause (D-185 added row): cage modes vs the rate loop
A.param gains: pitch P 0.15 / I 0.25 / D 0.002 / FLTD 40, roll P 0.20 / I 0.25 / D 0.003 / FLTD 32, yaw P 0.40 / I 0.04, `INS_GYRO_FILTER` 60 (A.param lines 99-109, 184). Model `sitl/fu_cage.py` (FE modes 1-250 Hz, motor lag 40 ms, delay 4 ms `EST`), IMU at the spar centre. Pass rule: **GM >= 2.0 (6 dB) on every axis, corner, damping (0.3 / 1 %), thrust scale (0.77 / 1.0 / 1.25) and with all flexible modes shifted +-20 % in frequency (the tap-test tolerance)**, no right-half-plane pole.
| axis | corner | cage modes 3-40 Hz (Hz: gain / rigid) | min GM nominal freq | min GM modes -20 % | min GM modes +20 % | crossover (Hz) |
|---|---|---|---|---|---|---|
| pit | kd | 12: +0.65, 25: +0.01, 36: -0.09 | 2.76 | 1.66 | 3.70 | 2.6, 11.7, 12.7 |
| pit | nom | 12: +0.66, 26: +0.01, 37: -0.09 | 3.17 | 1.71 | 3.54 | 2.6, 12.0, 13.0 |
| pit | hi | 15: +0.65, 31: +0.01 | 3.59 | 2.60 | 1.64 | 2.6, 14.4, 15.3 |
| rll | kd | 29: -1.05, 39: +0.14 | 2.52 | 2.16 | 3.65 | 1.8, 28.5, 28.9 |
| rll | nom | 31: -1.05 | 2.81 | 2.19 | 4.45 | 1.8, 30.6, 30.9 |
| rll | hi | 35: -1.05 | 3.76 | 2.41 | 7.52 | 1.8 |
| yaw | kd | 8: -0.11, 16: -0.72, 32: -0.06, 37: -0.00 | 2.06 | 2.03 | 2.09 | 1.5 |
| yaw | nom | 8: -0.09, 16: -0.75, 32: -0.06, 40: +0.00, 40: -0.00 | 2.09 | 2.03 | 2.09 | 1.5 |
| yaw | hi | 10: -0.11, 19: -0.72, 39: -0.06 | 2.09 | 2.06 | 2.13 | 1.5 |

Minimum GM over everything: **1.64** vs rule 2.0.

## C1 loads at VD 24 (D-186), 1.50 kg gate mass
| Case | n | Note |
|---|---|---|
| Gust U 8 m/s at VC 17 | 3.85 (stall line 1.98) | |
| Gust U 4 m/s at VD 24 (half of 8, ASM-C1-UDE-D-FRAC) | **3.01** (stall line 3.96) | below 3.4 floor: PASS |
| Gust U 8 m/s at VD 24, no half rule (bound) | 5.03 (stall-limited 3.96) | the wing stalls before it reaches this n |
| Manoeuvre limit n | +3.4 / -1.5 | A-P13 floor governs; ult 5.1 / -2.25 |
| Dynamic pressure | q(VD) 353 Pa vs q(VC) 177 Pa (x1.99); flutter / divergence at 1.2 VD = 28.8 m/s (FLUTTER.md) | |
| Spar 12x10 root bending at n 3.40 (unrelieved 4.78 N m) | 94 MPa design vs 350 | MS +2.73: PASS |
| Spar shear | 2.5 MPa vs 30 | MS +11.0: PASS |
| Pull-up at VD to the stall line (n 3.96 > 3.4: the elevon can reach it, VA 22.2 m/s is about VD) | spar 109 MPa design | MS +2.21: PASS; the 3.4 limit becomes a pilot / autopilot limit (`Q_A_ANGLE_MAX` 45, TECS) rather than aerodynamic at VD |

## Elevon horn, hinge and lead mass loads (D-187, for C6)
Elevon: span 0.30 m (y 0.04-0.34), chord 61.2 mm (0.25 c, a_model.py ELEV_FRAC), area 184 cm2 each, hinge stiffness from FLUTTER.md (aerodynamic, -0.375 N m/rad per elevon at 24 m/s, `CALC`) times the 20 deg stop, plus an alpha term Ch_alpha -0.15 per rad at 14 deg local alpha (`EST`).
- Hinge moment at VD 24 with the full +-20 deg stop and 14 deg local alpha: 0.146 N m limit per elevon (`EST`); ultimate 0.251 N m. Servo ES3352HV stall 1.7-2.4 kgf cm = 0.17-0.24 N m (A-P11): margin +0.17 at the low stall figure (thin; a 2x error in the alpha term or the stiffness leaves none).
- Lead balance 10.7 g on the 30 mm horn at manoeuvre n 3.4: inertia force 0.36 N, moment about the hinge 11 N mm. Horn arm bending (3 mm x 12 mm CF/PETG tab, 30 mm): 1 MPa limit (x2.16 printed = 1 MPa) vs PETG interlayer 9.5 MPa: PASS `EST`.
- Lead balance 10.7 g on the 30 mm horn at crash 12 g (A-P5): inertia force 1.26 N, moment about the hinge 38 N mm. Horn arm bending (3 mm x 12 mm CF/PETG tab, 30 mm): 2 MPa limit (x2.16 printed = 5 MPa) vs PETG interlayer 9.5 MPa: PASS `EST`.
- Lead block + horn bond into the elevon block (PETG block, 12 x 20 mm both faces, couple 38 N mm over 20 mm = 1.9 N): 0.01 MPa design vs 2.0 MPa epoxy: MS +234.6.
- Control rod: hinge moment 0.146 N m on a 12 mm horn = 12.1 N limit (21.0 N design); 2 mm CF rod, 40 mm free length `EST` (FLUTTER.md: 2 mm rod, horn >= 12 mm): P_cr 339 N, MS +15: PASS.
- Wing root bending from the +21 g (two balances at y about 0.19 m, n 3.4): 0.14 N m, opposing lift, so the unrelieved spar case above is unchanged.

## Mass vs the 473 g freeze
| Group | Iter 2 (frozen) | D-187 lead balance | Total | |
|---|---|---|---|---|
| Wing | 191 | +21 (2 x 10.7 g `EST`; FLUTTER.md moves wing 191 -> 212) | 212 | |
| Fins | 119 | 0 | 119 | |
| Cage | 122 | 0 | 122 | |
| Hardware | 40 | 0 | 40 | |
| **Structure** | **473** | **+21** | **494** | **+21 g over the freeze, +34 g over the 460 g MASS-GATE allocation** |
Offsets that keep 473 without new risk (`EST`, none applied): lighter elevon (2 mm foam or balsa, about -2 g each, FLUTTER.md) and a smaller lead (7.1 g at 45 mm if the wing thickness allows, -7 g total). Against the 1.44 kg target the +21 g uses 21 of the 44 g headroom at the 473 g basis (FOLDIN s1: predicted 1,396 g, headroom 104 g to the gate, 44 g to 1.44). The freeze needs a board waiver for the +21 g.
### Tap-test window (rate-loop clause)
Lowest GM, zeta 0.3 %, thrust x0.77 / x1.25, every flexible mode scaled by s (first cage mode Hz in brackets), IMU at the spar centre:
| s | pit kd | pit nom | pit hi | rll kd | rll nom | rll hi |
|---|---|---|---|---|---|---|
| 0.6 | 1.34 (7) | 1.28 (7) | 1.49 (9) | 1.08 (17) | 2.06 (18) | 2.19 (21) |
| 0.7 | 1.43 (8) | 1.43 (9) | 1.88 (10) | 2.26 (20) | 2.19 (22) | 2.19 (24) |
| 0.8 | 1.66 (10) | 1.71 (10) | 2.60 (12) | 2.16 (23) | 2.19 (25) | 2.41 (28) |
| 0.9 | 2.06 (11) | 2.23 (11) | 4.00 (13) | 2.26 (26) | 2.41 (28) | 2.89 (31) |
| 1.0 | 2.76 (12) | 3.17 (12) | 3.59 (15) | 2.52 (29) | 2.81 (31) | 3.76 (35) |
| 1.1 | 4.00 (13) | 4.06 (14) | 2.68 (16) | 2.94 (32) | 3.48 (34) | 5.20 (38) |
| 1.2 | 3.70 (15) | 3.54 (15) | 1.64 (18) | 3.65 (34) | 4.45 (37) | 7.52 (42) |
| 1.3 | 3.03 (16) | 2.76 (16) | 1.00 (19) | 4.67 (37) | 6.06 (40) | 11.76 (45) |
| 1.4 | 2.19 (17) | 1.88 (17) | 1.00 (21) | 6.25 (40) | 8.64 (43) | 13.71 (49) |
| 1.5 | 1.38 (18) | 1.15 (19) | 1.00 (22) | 8.77 (43) | 13.09 (46) | 13.93 (52) |
- pit kd: GM >= 2 for the first cage mode (pit: ~12 Hz mode; rll: ~31 Hz) from 11 to 17 Hz (grid)
- pit nom: GM >= 2 for the first cage mode (pit: ~12 Hz mode; rll: ~31 Hz) from 11 to 16 Hz (grid)
- pit hi: GM >= 2 for the first cage mode (pit: ~12 Hz mode; rll: ~31 Hz) from 12 to 16 Hz (grid)
- rll kd: GM >= 2 for the first cage mode (pit: ~12 Hz mode; rll: ~31 Hz) from 20 to 43 Hz (grid)
- rll nom: GM >= 2 for the first cage mode (pit: ~12 Hz mode; rll: ~31 Hz) from 18 to 46 Hz (grid)
- rll hi: GM >= 2 for the first cage mode (pit: ~12 Hz mode; rll: ~31 Hz) from 21 to 52 Hz (grid)
