# T-083 propulsion at basic 1669.8 g -> predicted 1.9129 kg (CG 24.41 mm, SM 6.65 %)
Motor X2216 V3 880KV: Kv 880.0, Rm 0.089, I0 0.5; one-motor line 24.93 A EST; derate 0.93; cant 17.0
| Item | Value | Limit | Verdict |
|---|---|---|---|
| A-P3 window, 3 % download, derate 0.93 | +11.02 % | >= +5.0 % | PASS |
| A-P2 T/W fresh, no download / with download | 2.695 / 2.614 | >= 2.0 | PASS |
| A-P2 T/W sag (3.73 V/cell, hot 0.97), with download | 2.074 | >= 1.6 | PASS |
| Lua spin cap cap(V): fresh 16.8 V / sag 14.92 V | 1.000 / 1.000 | <= 1.0 (1.0 = not binding) | PASS |
| One motor saturated + three hovering, fresh, at the cap (A-P16 analogue) | 20.08 A | <= 24.93 A EST line (450 W / 16.8 V x 12.1/13) | PASS |
| All four at the cap, fresh: rpm / A per motor / bus V | 11415 / 18.32 / 14.60 | rpm <= 11667 (APC MR limit); ESC 35 A / channel; motor 32 A / 30 s | PASS |
| All four at the cap, sag: rpm / A per motor / bus V | 10343 / 15.15 / 13.10 | same | PASS |
| Pack current, all four at the cap (fresh / sag) | 73.3 / 60.6 A | RDQ 2800 100C = 280 A | PASS |
| Connector rating needed (A-P16: 1.25 x peak) | 91.6 A | XT90 (90 A, secondary sources); XT60 is 60 A momentary (secondary sources) | info |
| Hover, derate 0.93: gf / rpm / A per motor / motor V / pack W / pack A | 516 / 7106 / 7.51 / 8.74 / 295 / 19.9 | - | PASS |
| Hover throttle, approx. motor V / fresh bus V and / sag bus V | 0.520 / 0.586 | A-P2 <= 0.625 | PASS |
| Cruise before BATT_LOW, 2.8 Ah (CALC-A-ENDURANCE form) | 223 s | >= 204.6 s | PASS |
| A-P6 1.3 Vs at the predicted mass (CLmax 0.75 EST, S 0.22, rho 1.225) | Vs 13.63, 1.3 Vs 17.71 m/s | <= 17.0 m/s | FAIL |
| A-P6 mass ceiling at CLmax 0.75 / CLmax needed at 1.913 kg | 1.7617 kg (basic 1535 g) / 0.814 | - | info |
| Mass ceilings at derate 0.93: window 5 % / T/W fresh 2.0 dl / T/W sag 1.6 dl | 2.159 / 2.500 / 2.480 kg predicted | - | info |
| Bench derate lines at 1.913 kg (thrust real / APC at equal rpm that just meets): A-P3 / A-P2 fresh dl / A-P2 sag dl | 0.824 / 0.712 / 0.717 | bench TP-1 | info |
| Sensitivity derate 0.88: window / T/W fresh dl / sag dl / cruise s | +8.28 % / 2.473 / 1.963 / 200 | - | info |
| Sensitivity derate 0.85: window / T/W fresh dl / sag dl / cruise s | +6.56 % / 2.389 / 1.896 / 185 | - | info |
| Sensitivity derate 0.8: window / T/W fresh dl / sag dl / cruise s | +3.53 % / 2.249 / 1.784 / 157 | - | info |
| Sensitivity one-motor line 17.7 A: cap fresh / window / T/W fresh dl | 0.896 / +11.02 % / 2.219 | - | info |
| Sensitivity one-motor line 15.0 A: cap fresh / window / T/W fresh dl | 0.809 / +4.92 % / 1.895 | - | info |
| Sensitivity one-motor line 12.1 A: cap fresh / window / T/W fresh dl | 0.711 / -5.40 % / 1.540 | - | info |

Maker cross-check (SunnySky X2216 V3 880KV table, 'APC9045' at 14.8 V, sunnyskyusa.com read 2026-11-21; the APC variant is not stated): APC 9x4.5MR model rows at the maker's rpm
| maker rpm | maker A | maker gf | model gf at that rpm | maker / model thrust | model A at that rpm |
|---|---|---|---|---|---|
| 5836 | 2.7 | 300 | 374 | 0.803 | 5.31 |
| 7450 | 4.9 | 500 | 611 | 0.818 | 8.24 |
| 8600 | 7.8 | 700 | 816 | 0.858 | 10.71 |
| 9696 | 11.2 | 900 | 1040 | 0.866 | 13.40 |
| 10117 | 13.05 | 1000 | 1132 | 0.883 | 14.48 |
| 10972 | 16.3 | 1180 | 1334 | 0.884 | 16.88 |
Model at 14.8 V motor terminal, full duty: 11555 rpm, 18.76 A, 1486 gf (maker: 10,972 rpm, 16.3 A, 1,180 gf)
