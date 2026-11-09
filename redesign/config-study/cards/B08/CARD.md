# B08 — Buy an ArduPilot-ready tilt-tri PNP (T1-S primary; Altus VTOL alt; Manta demoted)

Status: PROPOSED (concept sizing, 2026-11-09). Numbers: `sizing.py` → `sizing.json`, `cost.csv`. Mission: REQUIREMENTS §3 M-A
(hover 2 min + cruise ≥ 5/10 min, 20 % reserve). Same floor and method as the other cards. `ESTIMATE` = guess, `UNVERIFIED` = unchecked.

**Research changed the order.** The HEEWING T1's flight controller is an official ArduPilot board (`HEEWING-F405v2`,
ardupilot.org/plane/docs/common-heewingf405.html), and a community ArduPilot 4.7.1 parameter file exists
(discuss.ardupilot.org/t/145545). That settles B01's open question. The Manta's US price and stock are still unconfirmed,
its GPS has no compass, and FIMI's parameter files are only on social media (forum t/104248). So the **T1-S is the primary**,
the **ZOHD Altus VTOL** (980 mm, $299.99 in stock at ReadyMadeRC, team supplies the FC, no maker parameters found) is the
larger alternative, and the **Manta** stays as a backup only.

<svg viewBox="0 0 700 330" width="700" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif" font-size="10">
<rect width="700" height="330" fill="white"/>
<text x="10" y="14" font-weight="bold">T1-S, scale 0.4 px/mm. Overall span, length and height are from the listing; planform shape is schematic (ESTIMATE)</text>
<!-- TOP VIEW: span 730 mm = 292 px, length 645 mm = 258 px, centre x=166 -->
<text x="130" y="32">TOP</text>
<rect x="156" y="40" width="20" height="160" rx="8" fill="#ddd" stroke="#333"/>
<line x1="166" y1="200" x2="166" y2="285" stroke="#333" stroke-width="3"/>
<polygon points="20,95 312,95 306,161 26,161" fill="#cfe3f7" stroke="#333"/>
<polygon points="166,272 124,292 128,298 166,284 204,298 208,292" fill="#cfe3f7" stroke="#333"/>
<circle cx="102" cy="78" r="30" fill="none" stroke="#c33" stroke-dasharray="3,2"/>
<circle cx="230" cy="78" r="30" fill="none" stroke="#c33" stroke-dasharray="3,2"/>
<rect x="98" y="72" width="8" height="40" fill="#555"/><rect x="226" y="72" width="8" height="40" fill="#555"/>
<circle cx="166" cy="250" r="30" fill="none" stroke="#c33" stroke-dasharray="3,2"/>
<text x="64" y="44">tilt motor + servo</text><text x="196" y="44">tilt motor + servo</text>
<text x="200" y="250">fixed rear lift motor</text>
<line x1="20" y1="312" x2="312" y2="312" stroke="#333"/><text x="130" y="324">730 mm span</text>
<line x1="330" y1="40" x2="330" y2="298" stroke="#333"/><text x="334" y="175" transform="rotate(90 334 175)">645 mm</text>
<text x="40" y="132">wing halves detach at the fuselage</text>
<!-- SIDE VIEW: length 258 px, height 140 mm = 56 px -->
<text x="380" y="32">SIDE (cruise: front motors tilted forward)</text>
<rect x="380" y="70" width="80" height="22" rx="10" fill="#ddd" stroke="#333"/>
<line x1="460" y1="80" x2="638" y2="80" stroke="#333" stroke-width="3"/>
<rect x="420" y="62" width="66" height="6" fill="#cfe3f7" stroke="#333"/>
<line x1="372" y1="50" x2="372" y2="86" stroke="#c33" stroke-width="2"/>
<rect x="374" y="62" width="14" height="8" fill="#555"/>
<polygon points="612,80 638,56 644,58 630,80" fill="#cfe3f7" stroke="#333"/>
<rect x="602" y="74" width="8" height="10" fill="#555"/><line x1="576" y1="72" x2="636" y2="72" stroke="#c33" stroke-width="2"/>
<line x1="380" y1="110" x2="638" y2="110" stroke="#333"/><text x="490" y="122">645 mm</text>
<line x1="652" y1="50" x2="652" y2="106" stroke="#333"/><text x="656" y="82">140</text>
<!-- FRONT VIEW: span 292 px, height 56 px, centre x=520 -->
<text x="380" y="160">FRONT (hover: front motors vertical)</text>
<rect x="374" y="222" width="292" height="6" fill="#cfe3f7" stroke="#333"/>
<rect x="510" y="214" width="20" height="30" rx="8" fill="#ddd" stroke="#333"/>
<rect x="452" y="200" width="8" height="22" fill="#555"/><rect x="580" y="200" width="8" height="22" fill="#555"/>
<line x1="426" y1="198" x2="486" y2="198" stroke="#c33" stroke-width="2"/><line x1="554" y1="198" x2="614" y2="198" stroke="#c33" stroke-width="2"/>
<line x1="374" y1="262" x2="666" y2="262" stroke="#333"/><text x="490" y="274">730 mm</text>
<text x="380" y="300">Props 6 in (152 mm) ESTIMATE, drawn as dashed discs. Rotors: 2 tilting front + 1 fixed rear.</text>
</svg>

## Key numbers (sizing.py, first-order; ρ 1.20, FM 0.55, η 0.75 hover / 0.50 cruise, L/D 6 calibrated on the Altus maker's 70 km/h @ 5 A)

| | **T1-S (primary)** | Altus VTOL (alt) | Manta (backup) |
|---|---|---|---|
| Span × length | 0.73 × 0.645 m (listing) | 0.98 × 0.77 m (listing) | 0.70 × 0.445 m (listing) |
| TOW, built up / listed | **0.69 kg** / 0.60–0.75 | 1.18 / 1.10–1.30 | 0.59 / 0.50 |
| Wing loading / stall / transition (1.3 Vs) | 5.8 kg/m² / 9.7 / 12.6 m/s | 6.2 / 10.1 / 13.1 | 5.0 / 9.0 / 11.7 |
| Disk loading / hover power / current | 125 N/m² / 119 W / **8.0 A** (4S) | 304 / 315 W / 21 A | 105 / 92 W / 8.5 A (3S) |
| Hover T/W (motor thrust `ESTIMATE`) | **2.4** (1.75 with +0.25 kg growth) | 2.2 (1.8) | 2.0 (1.4, fails 1.6) |
| Cruise power / current | 32 W / 2.1 A at 14 m/s | 65 W / 4.4 A at 17 m/s | 25 W / 2.3 A at 13 m/s |
| Pack / usable | 4S 1500 LiPo / 17.8 Wh | 4S 3000 LiPo / 35.5 Wh | 3S 21700 Li-ion / 43 Wh |
| Cruise after 2 min hover / hover only | **24 min** / 9 min | 20 / 7 min | 95 (optimistic; one reviewer measured ≈ 30 min) / 28 |
| Gust lift at 8 m/s ÷ weight (hover) | 0.20 | 0.19 | 0.24 |
| Total spend (cost.csv, tax + ship) | **$1,388.75** → reserve **$611** | $1,373.87 → $626 | not priceable (US stock UNVERIFIED) |
| Packed | 1 tote ≈ 0.66 × 0.40 × 0.16 m, ≈ 2 kg with 4 packs | 1 box ≈ 0.80 × 0.45 × 0.22 m | 0.50 × 0.36 × 0.12 m |

All three meet G6 (≥ 5 min cruise, objective 10 min) with a large margin. **None can take the 0.25 kg growth allowance
inside its listed maximum take-off weight**, so this airframe cannot grow into mission M-B or M-C. The cost is higher
than the screening's $950–1,100 because this card uses the same floor as the scratch concepts: ground kit, airspeed sensor,
Remote ID, a full spare motor and servo set, and a modification budget.

## Transport and assembly
One person, one tote, about 2 kg. In the field: slide the wing halves on and plug them in, fit a pack, power on, do the
pre-arm checks. **About 3 min, 1 person, no tools** `ESTIMATE`. The T1-S is also sold with a foam case. Fully assembled
it is 0.73 × 0.65 × 0.14 m, so it even fits on a back seat without taking it apart.

## How it is built
Nothing structural is made. **Assembly** 4 h (glue/clip the tail, fit the RX, airspeed, compass). **Firmware** 10 h
(V2 bootloader, Plane 4.7, load the community parameters, calibrations). **Failsafe/arming bench** 8 h (D8–D10, props off).
**SITL + simulator** 10 h per pilot (D15). **Measured modification** 40–60 h: for example a printed wing-tip extension
or skids, flown A/B with logged current. **Total about 80–100 team-hours; first hover in build week 1–2** `ESTIMATE`.
Processes: hand assembly, FDM printing for the modification, soldering. Lead time: US stock, 3–7 days.

## Controls
ArduPilot Plane QuadPlane tilt-rotor: `Q_ENABLE 1`, `Q_FRAME_CLASS 7` (tri), `Q_TILT_ENABLE 1`, `Q_TILT_TYPE 2`
(vectored yaw: differential tilt gives yaw), taken from the community 4.7 parameters (`UNVERIFIED` until the file is opened).
Modes: QHOVER/QLOITER → FBWA → CRUISE/AUTO → QRTL/QLAND. `ARSPD_USE 1` with the added sensor, `AIRSPEED_MIN` ≈ 13 m/s,
`Q_ASSIST_SPEED` ≈ 10 m/s, D10 failsafes, and a geofence on the RFS sub-field.

## Top 3 risks
1. **Wind.** At 0.7 kg and 5.8 kg/m², an 8 m/s gust produces lift equal to about 20 % of weight on a level hover wing,
   and the transition speed of 12.6 m/s is only 1.6 × the D11 gust. Mitigation: morning flights and a 5 m/s limit on
   the flight card. The Altus is no better per kilogram.
2. **Thin capstone content.** The team gets an aircraft but designs almost nothing, and the airframe has no growth margin.
   The measured modification and the test campaign have to carry the engineering story; the team lead should decide if
   that is enough. Another option is B06: fly this aircraft as the mule while a scratch-built main aircraft is made.
   The radio, charger and ground kit are shared, but the $611 left is about what a class-S scratch airframe plus its
   propulsion costs on top of that shared floor (`ESTIMATE` from cost_model.py), so B06 leaves almost no crash reserve.
3. **Logging and firmware version.** The V1 HEEWING board has no logging (fails the campus D7 requirement) and needs a
   bootloader fix. Check for V2 on arrival; the fallback is a $67 CoreWing F405 or a $100 H743-WING. The 9 g tilt servos
   are the known single-point failure, and spares are in the BOM.

## First prototype test (build week 1)
Bench, props off: arming, kill within 1 s, RC-loss → QLAND, battery failsafe. Put one station on the thrust stand to
replace the 550 g/motor `ESTIMATE` (pass: T/W ≥ 1.6). Then, on a calm RFS morning, 60 s of QHOVER at 1–2 m with logging.
**Pass:** hover current within ±25 % of 8.0 A, attitude error < 5°, log downloaded.
