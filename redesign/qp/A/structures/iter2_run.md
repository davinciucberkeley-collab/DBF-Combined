### Mass vs allocation (g)
| Group | Iter 2 | Iter 1 | MASS-GATE |
|---|---|---|---|
| Wing | 191 | 209 | 220 |
| Fins | 119 | 121 | 70 |
| Cage | 122 | 122 | 135 |
| Hardware | 40 | 40 | 35 |
| **Total** | **473** | 492 | 460 |
|   Wing: XPS core | 95.3 | | |
|   Wing: spar 12x10 x 0.90 m | 49.8 | | |
|   Wing: tape skin | 24.2 | | |
|   Wing: 4 PETG plugs + 2 elevon blocks | 14.0 | | |
|   Wing: epoxy EST | 8.0 | | |
|   Fins: 2 fin spar tubes 16x14 x 0.36 m (aft edge, foot on the end) | 54.3 | | |
|   Fins: XPS fairing 3 mm (both) | 7.8 | | |
|   Fins: tape skins 55 g/m2 | 9.5 | | |
|   Fins: 4 foot shoes (PETG 2 + EVA 0.5) | 10.0 | | |
|   Fins: 2 root blocks (PETG) | 8.0 | | |
|   Fins: 2 rib tubes 14x12 x 0.227 m | 29.7 | | |
|   Cage: 4 arms 12x10 x 0.245 m | 54.2 | | |
|   Cage: PETG hub | 16.0 | | |
|   Cage: bridge 12x10 x 0.16 m | 8.8 | | |
|   Cage: 2 struts 6x4.5 x 0.33 m | 13.1 | | |
|   Cage: 3 saddles (PETG; rib saddles 60 mm wide) | 8.0 | | |
|   Cage: 4 motor cups (PETG) | 16.0 | | |
|   Cage: socket epoxy EST | 6.0 | | |
|   Hardware: screws, nuts, fillets, paint EST | 40.0 | | |

### Rotor bands and rpm source
Hover 6,018 / 6,272 / 7,151 rpm (1.381 kg / 1.50 kg / 8 m/s lean at 1.3 W): `qp/A/prop_a.py` hover() at derate 0.93, lean scaled by sqrt(1.3). 1P 100-119 Hz, 2P 201-238 Hz. Cruise 7,300-7,600 rpm (QP-3 BOARD s1 item 2: `sitl/fu_level.py` with the APC V > 0 data; the 8,900-10,500 EST band is withdrawn): 1P 122-127, 2P 243-253 Hz. Rule: f <= band_low/1.2 or f >= 1.2 x band_high for all four. That excludes **84-304 Hz** for strongly coupled modes (coupling >= 0.5, D-185).

### Modes with motor coupling >= 0.3, plus the fin and every mode in the excluded band with coupling >= 0.1 (coupling = mass-normalised |phi| summed at the four motors; arm modes 2.7-3.4)
| Corner | f (Hz) | part | coupling | vs bands |
|---|---|---|---|---|
| kd | 8 | bridge 50% | 2.2 | pass |
| kd | 12 | spar 67% | 2.0 | pass |
| kd | 16 | bridge 58% | 1.4 | pass |
| kd | 25 | spar 54% | 0.5 | pass |
| kd | 29 | arm 43% | 2.8 | pass |
| kd | 36 | rib 39% | 1.6 | pass |
| kd | 36 | spar 74% | 0.6 | pass |
| kd | 37 | arm 100% | 3.4 | pass |
| kd | 37 | arm 100% | 3.4 | pass |
| kd | 39 | arm 99% | 3.3 | pass |
| kd | 44 | arm 97% | 2.9 | pass |
| kd | 44 | arm 65% | 2.4 | pass |
| kd | 50 | spar 59% | 0.6 | pass |
| kd | 64 | arm 59% | 1.3 | pass |
| kd | 199 | spar 51% | 0.5 | in band, coupling 0.5 |
| kd | 432 | fin 61% | 0.6 | pass |
| kd | 450 | fin 87% | 0.0 | pass |
| kd | 544 | fin 93% | 0.0 | pass |
| kd | 551 | fin 91% | 0.3 | pass |
| nom | 8 | bridge 50% | 2.1 | pass |
| nom | 12 | spar 66% | 2.0 | pass |
| nom | 16 | bridge 60% | 1.4 | pass |
| nom | 26 | rib 48% | 0.5 | pass |
| nom | 31 | arm 43% | 2.8 | pass |
| nom | 37 | rib 36% | 1.5 | pass |
| nom | 39 | spar 74% | 0.6 | pass |
| nom | 40 | arm 100% | 3.0 | pass |
| nom | 40 | arm 100% | 3.0 | pass |
| nom | 42 | arm 99% | 3.3 | pass |
| nom | 47 | arm 97% | 2.9 | pass |
| nom | 47 | arm 69% | 2.5 | pass |
| nom | 53 | spar 59% | 0.6 | pass |
| nom | 68 | arm 60% | 1.4 | pass |
| nom | 214 | spar 51% | 0.5 | in band, coupling 0.5 |
| nom | 463 | fin 60% | 0.6 | pass |
| nom | 482 | fin 87% | 0.0 | pass |
| nom | 582 | fin 93% | 0.0 | pass |
| nom | 590 | fin 91% | 0.3 | pass |
| hi | 10 | bridge 50% | 2.2 | pass |
| hi | 15 | spar 67% | 2.0 | pass |
| hi | 19 | bridge 58% | 1.4 | pass |
| hi | 31 | spar 55% | 0.5 | pass |
| hi | 35 | arm 43% | 2.8 | pass |
| hi | 43 | rib 39% | 1.7 | pass |
| hi | 44 | spar 74% | 0.6 | pass |
| hi | 45 | arm 100% | 3.4 | pass |
| hi | 45 | arm 100% | 3.4 | pass |
| hi | 48 | arm 99% | 3.3 | pass |
| hi | 54 | arm 97% | 2.9 | pass |
| hi | 54 | arm 64% | 2.4 | pass |
| hi | 60 | spar 59% | 0.6 | pass |
| hi | 78 | arm 59% | 1.3 | pass |
| hi | 242 | spar 51% | 0.5 | in band, coupling 0.5 |
| hi | 525 | fin 61% | 0.6 | pass |
| hi | 546 | fin 87% | 0.0 | pass |
| hi | 660 | fin 93% | 0.0 | pass |
| hi | 669 | fin 91% | 0.3 | pass |

Smallest margin among strongly coupled modes (>= 0.5): see the lowest-frequency rows; the highest strongly coupled mode below the bands and the lowest above them per corner:
- kd: highest coupled mode below the bands 64 Hz (limit 83.6, margin 31 %); lowest above 432 Hz (limit 304)
- nom: highest coupled mode below the bands 68 Hz (limit 83.6, margin 23 %); lowest above 463 Hz (limit 304)
- hi: highest coupled mode below the bands 78 Hz (limit 83.6, margin 8 %); lowest above 525 Hz (limit 304)

### Forced response, no balancing credit (U 1.0 g mm per rotor EST; ISO G16 prop alone 0.27; 2P ripple 5 % of thrust EST; damping 1 % EST); worst over the D-185 sweep 6,000-10,500 rpm in 250 rpm steps plus the hover and cruise (7,300 / 7,450 / 7,600) points, all three corners; FC acceleration vs 30 m/s2
- kd: 18.4 m/s2, MS +0.63
- nom: 17.9 m/s2, MS +0.67
- hi: 18.0 m/s2, MS +0.66

Static cage rotation vs the spar centre (kd): pure pitch moment 2.44 N m: 0.58 deg (iteration 1: 2.0 deg); yaw/roll about the thrust axis, 0.35 N m: 0.29 deg

Static cage rotation vs the spar centre (nom): pure pitch moment 2.44 N m: 0.50 deg (iteration 1: 2.0 deg); yaw/roll about the thrust axis, 0.35 N m: 0.26 deg