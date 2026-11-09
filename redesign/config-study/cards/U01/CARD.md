# U01 — Wing-assisted quad on a bought carbon frame (conditional on a one-day test)

Status: PROPOSED; numbers CHECKED by `sizing.py` (calc only, nothing VERIFIED). Mission: REQUIREMENTS §3 M-A.
Base: Holybro X500 V2 frame (500 mm) + four class-S stations from `cost_model.py` + 1.2 m foam wing at +25°.
U09 (free-pivot wing) is the same airframe with the saddle replaced by a free spar bearing (+$30, +0.05 kg `ESTIMATE`).
It has no autopilot mode, so it is a test variant only. The research `FINDINGS.md` files did not exist when this card
was written, so the evidence cited here comes from the audit log and web search on 2026-11-09.

<svg viewBox="0 0 880 290" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif" font-size="11">
<rect width="880" height="290" fill="#fff"/>
<text x="10" y="16" font-weight="bold">Top (hover attitude)</text>
<text x="350" y="16" font-weight="bold">Front</text>
<text x="690" y="16" font-weight="bold">Side (nose right)</text>
<!-- TOP: scale 0.25 px/mm, centre (165,140), FWD up -->
<g stroke="#333" fill="none">
<rect x="15" y="115" width="300" height="50" fill="#cfe3f7"/>
<line x1="121" y1="96" x2="209" y2="184"/><line x1="209" y1="96" x2="121" y2="184"/>
<rect x="147" y="122" width="36" height="36" fill="#ddd"/>
<circle cx="121" cy="96" r="35" stroke-dasharray="3 2"/><circle cx="209" cy="96" r="35" stroke-dasharray="3 2"/>
<circle cx="121" cy="184" r="35" stroke-dasharray="3 2"/><circle cx="209" cy="184" r="35" stroke-dasharray="3 2"/>
<line x1="165" y1="40" x2="165" y2="25"/><polyline points="160,31 165,24 170,31"/>
</g>
<text x="172" y="34">FWD</text>
<text x="20" y="110">wing 1200 × 220 (2 × 600 halves)</text>
<text x="70" y="240">props 11 in (279), 500 mm wheelbase</text>
<!-- FRONT: centre x 515, ground y 250 -->
<g stroke="#333" fill="none">
<line x1="345" y1="250" x2="685" y2="250" stroke="#999"/>
<line x1="485" y1="250" x2="485" y2="196"/><line x1="545" y1="250" x2="545" y2="196"/>
<line x1="475" y1="250" x2="495" y2="250" stroke-width="3"/><line x1="535" y1="250" x2="555" y2="250" stroke-width="3"/>
<rect x="497" y="189" width="36" height="7" fill="#ddd"/>
<rect x="503" y="198" width="24" height="16" fill="#f4c27a"/>
<line x1="471" y1="191" x2="559" y2="191"/>
<line x1="436" y1="187" x2="506" y2="187" stroke-dasharray="3 2"/><line x1="524" y1="187" x2="594" y2="187" stroke-dasharray="3 2"/>
<line x1="508" y1="189" x2="508" y2="172"/><line x1="522" y1="189" x2="522" y2="172"/>
<rect x="365" y="149" width="300" height="23" fill="#cfe3f7"/>
</g>
<text x="600" y="215">pack</text>
<text x="370" y="143">wing TE 70 above rotor plane</text>
<text x="420" y="270">gear 215 high</text>
<!-- SIDE: centre x 760, ground 250, nose right -->
<g stroke="#333" fill="none">
<line x1="680" y1="250" x2="860" y2="250" stroke="#999"/>
<line x1="745" y1="250" x2="745" y2="196"/><line x1="775" y1="250" x2="775" y2="196"/>
<rect x="742" y="189" width="36" height="7" fill="#ddd"/>
<rect x="745" y="198" width="30" height="16" fill="#f4c27a"/>
<line x1="716" y1="191" x2="804" y2="191"/>
<line x1="681" y1="187" x2="751" y2="187" stroke-dasharray="3 2"/><line x1="769" y1="187" x2="839" y2="187" stroke-dasharray="3 2"/>
<line x1="755" y1="189" x2="752" y2="172"/><line x1="767" y1="189" x2="770" y2="170"/>
<line x1="735" y1="172" x2="785" y2="149" stroke-width="5" stroke="#5b8fc7"/>
</g>
<text x="790" y="150">+25° incidence</text>
<!-- scale bar 500 mm = 125 px -->
<line x1="15" y1="275" x2="140" y2="275" stroke="#000" stroke-width="2"/>
<text x="145" y="279">500 mm (all views to the same scale, 0.25 px/mm)</text>
</svg>

| Key number | Value | Source |
|---|---|---|
| Take-off mass | **2.71 kg** (incl. 0.25 kg growth): frame 0.61, propulsion 0.67, wing 0.34, pack 0.64, avionics/wiring 0.21 | sizing.py, mostly `ESTIMATE` |
| Wing | 1.20 m × 0.22 m, S 0.264 m², AR 5.5, 103 g/dm², +25° to rotor plane | sizing.py |
| Hover | disk loading 112 N/m², **356 W / 24 A**, T/W **2.2** (`ESTIMATE`: no maker thrust table found for X3108S 900KV + 11×4.5) | FM 0.65, η 0.80 |
| Forward flight, 14 m/s (modelled) | pitch 16.5° nose-down, wing carries 49 % of weight, **9.4 A vs 18.0 A for the bare quad** (−48 %) | Glauert + lifting line |
| Same, pessimistic inputs | saving **15 % at 12 m/s, 14 % at 14 m/s**, which fails the screen's ≥ 20 % condition | wing CD0 0.04, full rotor inflow on the wing, FM 0.55 |
| Endurance, 4S 6500 (80 % usable, 77 Wh) | hover 13 min; cruise 33 min; **M-A objective (2 min hover + 10 min cruise) needs 35 Wh: met** | sizing.py |
| Bare quad without wing | 2 min hover + 14.7 min at 14 m/s: **also meets M-A**. The wing buys margin the mission does not need | sizing.py sweep |
| Cost | **$1,523** with tax and shipping; **$477 left for crashes** (≈ 1.7 bad crashes at ~$275) | cost.csv |
| Packed | **one box 0.65 × 0.44 × 0.38 m**, about 4.5 kg; longest piece 0.60 m | sizing.py |

**Transport and assembly.** The frame travels whole with props off. The two wing halves lie flat on top. Each half
has a 0.55 m carbon stub glued in, which plugs into a 14 mm sleeve in the printed saddle and is held by one nylon
thumb-screw. In the field: 4 props, 2 wing halves, 2 thumb-screws, pack strap (the wing has no electrics). One
person, **≈ 5 min, no tools beyond the prop wrench** `ESTIMATE`. This beats C3 easily.

**Build.** Bought frame (6 h). Motors on printed or aluminium adapters (the 16×16 X500 mount versus the X3108 bolt
pattern is `UNVERIFIED`). Solder ESCs/harness and AS150U (12 h). FC, GPS and ArduCopter setup (12 h). Hot-wire 1 in
XPS halves and tape-skin them, two sets (10 h). Design and print the saddle and masts with an adjustable 20/25/30°
incidence (12 h). Foam-board test wing (4 h). **≈ 55–65 h, 2–3 weeks to first hover**. Repairing a crash means
swapping arms or stations and re-cutting a foam half: about 1 day. Processes: FDM, hot-wire, hand tools.

**Controls.** ArduCopter 4.6 QUAD/X. There is no QuadPlane, transition or servo logic. Autotune the bare quad first,
then again with the wing. `ANGLE_MAX` 3500, `LOIT_SPEED`/`WPNAV_SPEED` ≈ 1400 cm/s, battery and RC failsafes →
LAND/RTL, geofence. The wing behaves as a speed-dependent disturbance: the altitude loop must drop throttle by about 50 %
between 6 and 12 m/s. Its pitch moment uses 21 % of the available pitch authority at 14 m/s. ArduCopter has no
weathervane, so the pilot keeps the nose into wind.

**Top 3 risks**
1. **Mission fit.** U01 never transitions. It is a quad that carries a wing. REQUIREMENTS §3 says a wingless
   multirotor does not demonstrate transition, and U01 shows wing-borne lift only partly (≤ 49 % of weight). The
   team must decide whether that counts. The bare quad already meets M-A, so the wing has to justify itself
   with data.
2. **Wing–rotor interference decides the payoff, and no one has measured it.** The modelled saving ranges from 52 % to 15 % at 12 m/s depending on how much
   rotor inflow the wing sees (`K_UPWASH`). There is no documented fixed-wing-on-quad build with logs; the only data
   point is forum hearsay (19 A → 13 A on a tilt-tri, `UNVERIFIED`).
3. **Hover in gusts.** In a 5 → 8 m/s gust the 25° wing changes lift by −5 % to +20 % of weight and drag by up to 3.8 ×
   the bare quad's (2.3 vs 0.6 N). Tail and quartering winds are not modelled. The forum tri-with-wing had "quite a
   problem with wind". In hover the wing also blocks part of the rotor inflow, costing about 3 % of thrust (`ESTIMATE`).

**First prototype test (the screen's condition, done honestly).** The team owns no quad, so the "< $20 one-day test"
first needs the base quad bought (≈ $1,050 pre-tax, ≈ $1,280 with tax and shipping, of this BOM). About 70 % of that (FC, radio, packs, charger, ground kit, wiring: $738 of $1,050)
transfers to any concept, and the quad doubles as the D15 trainer. Day 1: fly the bare quad and log current in
straight passes at 8, 10, 12, 14 and 16 m/s, flying both directions (GPS speed). Then tape on a foam-board wing at 20°,
25° and 30° and repeat. Same day, try U09 on a free spar if the fixed wing weathercocks. **Pass: ≥ 20 % less current at
12 m/s (averaged over both directions) and hover attitude excursions ≤ 10° in ≥ 5 m/s wind.** If it fails, U01
drops out and the quad stays on as the team's trainer and test bed.
