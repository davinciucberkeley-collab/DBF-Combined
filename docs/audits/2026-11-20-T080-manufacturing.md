# T-080 manufacturing re-plan, concept A O4b, with the equipment actually available (2026-11-20)

Task T-080 (R-OPT-01, R-OPT-02, R-CAD-04). Reviewer/decision agent: opus. I wrote none of the records used here. **This file is the only repo file I wrote.** No CAD, FEA, SITL, landing simulation, CHANGE-LOG, requirement, ledger, BOM, MASS-GATE or T-076c file was run or edited. Status: **decision record, not VERIFIED COMPLETE.** The conductor logs it (CHANGE-LOG, engineering-decisions trade tables, BOM lines) and opens the implementation tasks.

Hand calculations: two scratch scripts in the session scratchpad (`.../scratchpad/t080/calc/t080_hand.py`, `t080_mass.py`, run with `python -I`, exit 0); every formula is restated below so the numbers can be rebuilt without them. Two web reads (curl, saved in `.../scratchpad/t080/dl/`, text extracted with `pdftotext` / a regex strip): the Markforged composites datasheet and the Wikipedia 6061 page (s1). Failed reads (stated, not used): asm.matweb.com (no connection), matweb.com, makeitfrom.com, onlinemetals.com (403), static.markforged.com Onyx TDS (403), two Stratasys material PDFs (HTTP 500). The Stratasys 380mc/450mc product page loaded but its material list could not be separated from the site navigation, so **the Fortus 380mc material list and every Fortus allowable are "—"**.

Limits not relaxed: RF >= 1.0; KF 1.725 (CFRP / metal) and KP 2.156 (printed / bonded) (`structures/structures_a.py` l.11-12); the hard 1.2 m/s landing cases; judge at max(DAF from D-1, 1.5) (hub escalation s2.4); A-P9 30 deg, A-P10, A-P4. AM-011: mass may exceed the gate in initial design, but every mass-dependent check is still run. AM-013: total including the crash reserve <= $2,000. EST = estimate; "—" = unknown.

Inputs read: `docs/reference/jacobs-equipment.md`; root `CLAUDE.md`; `redesign/params/CHANGE-LOG.md` D-215 to D-220; `docs/audits/2026-11-20-hub-escalation.md` (all); `docs/audits/2026-11-19-T068-decision.md` (all); `docs/audits/2026-11-19-T070-decision.md` (all, s4 in detail); `redesign/qp/A/mechanism/out/T067_mass_audit.md`, `T071b_centre_nodes.md`, `T073_o4_checks.md` (s headline-step 6, findings), `T076_o4b_analysis.md` (s0-s6, b.0-b.3), `T079_cost_closure.md` (totals); `docs/engineering-decisions.md` (ladder, trade-table format); `docs/task-ledger.md` rows T-064 to T-080; `redesign/qp/A/BOM-A.csv`; `structures/structures_a.py` l.10-22, `structures/fea_arm.py` l.88-100, `structures/fea_hub.py` header and `GEO` (l.12-14, l.42-43).

## 0. Answers in one place

| Part (ID) | Process and machine | Material, orientation | Allowable basis | Δmass vs T-067 adopted g (EST) | What it does to the failing rows |
|---|---|---|---|---|---|
| Hub CGE-001 | **Machined: team-lab Kent knee mill (squaring, the three bores, cross-pin holes, first prototype) + Jacobs Tormach 440 (contour, lightening pockets, strut sockets) for the flight hub.** Knee-mill-only build is the fallback (prismatic shape, heavier) | 6061-T6 bar; galvanic barrier: one wrap of the 48 g/m2 glass cloth already on the O4b list in every CF-in-Al bond | 6061-T6 min yield 240 / min UTS 290 MPa, E 68-69 GPa, 2.70 g/cm3 (s1, secondary source; MMPDS/supplier cert to confirm before H-A1 is judged) | **+13.2** (+10.2 to +16.2): 27 g lightened (escalation 24-30) + 2 g octagonal sleeves (DFM, F-5) against 15.82 | Closes the hub net-section row (PETG 0.71, hand) and the C6/V1 FEA stop rows (0.94 / 0.91) by hand at any DAF <= 3: required yield >= 68 MPa, 240 available (RF about 3.5 EST, H-A1 to confirm). Bond torsion (0.90 at DAF 2) closed by a 3 mm cross-pin drilled on the knee mill (D-202 practice) |
| Centre node / bridge saddle CGE-006 | **Markforged X7, Onyx with continuous CF rings** (in-layer around the bridge socket, spar ring and ear edges); CF plate N2 waterjet; 4 x 3 mm CF pins | Onyx + CF, **printed z-up (layers in the wing x-y plane)**: the governing in-plane moment Mz bends the node in-layer | Onyx and CF from the Markforged sheet (s1) scaled to EST design values; **conditional on coupons C-2 (CF knockdown) and C-3 (bond to Onyx)**. Fallback: machined 6061 node (Tormach), +10 to +15 g more | **+15.0** (+12 to +18) against 9.67 (that is the T-071b C6 node, +13.9 g solid PETG, printed in Onyx instead: -0.8 g on that) | **New finding (F-1): the node rows were sized on My only, like the hub.** Mz at the saddle is 15.3-19.7 N m. A PETG z-up node net section gives RF 1.62 / 1.08 / 0.81 (RB / x1.5 / x2), interlayer-oriented 0.77 RB. CF in-layer is what lifts it at DAF >= 1.5. T-071b saddle body shear 0.87 and ear bond 0.93 (x1.5) must be re-derived with all six components |
| Fin rib saddle FIN-005 | **Clamshell (D-215): two CF plates cut on the OMAX waterjet** + printed PETG cradle (2 mm walls, 4 mm pin boss) + 3 x 3 mm CF pins | CF plate **0.5 mm** (not 1.0: in-plane RF scales with t; 1.0 mm gave 15.9, so 0.5 mm gives about 8 EST); cradle printed so the pin bosses' bearing is in-layer | ACP Composites PDS Dec 2014 (repo, T-071b A.4) x 0.70 EST | **-5.0** (-7.8 to -0.8) against 28.78 | Replaces P11 / P12 (0.34 / 0.28 printed; 0.90 / 0.66 largest printed in-layer) with plates; cradle pins 1.66 / 2.94 (T-076); bond rows to coupon C-4 |
| Fin root block FIN-003 | **Plain FDM PETG, printed flat z-up (D-215 rule), enlarged, 3 x 3 mm pins in a 4 mm boss.** X7 Onyx + CF is the named mass-recovery variant after coupons C-2 / C-3 | PETG z-up, orientation on the drawing | PETG 20 in-layer / 9.5 interlayer EST (`structures_a.py` l.16; no coupon) | **+12.2** (+9.2 to +17.2) against 37.80 (T-070 "T" row, not new here) | P6 / P8 0.50 / 0.51 → 1.58 / 1.72 only with the in-layer rule (T-071b B.2); pins 0.30 → 1.43 / 2.53 (T-076). X7 variant: -4 to -8 g pair EST, not adopted until C-2 / C-3 pass |
| Foot shoe GER-001 + pad cup | **Plain FDM PETG**, plate printed flat (P2 junction in-layer) | PETG; UHMW face; EVA pad | PETG EST; EVA "—" | **+7.0** (+5 to +9) against 18.20 (T-068 D3, not new here) | P2 0.96 → 2.03 (in-layer). **CUP EVA rows 0.01 / 0.14 / 0.15 are a data/model gap: no machine closes them;** coupon C-6 (T-076 s5). Onyx (tougher nylon) is the swap if the drop rig cracks a PETG shoe |
| Motor cups CGE-003 | **Plain FDM PETG** (R3fix), plate on the bed | PETG; thermal hold point H-1 | PETG EST | **-11.2** against 38.04 | R3 as specified -0.71 MS → R3fix 1.37 (T-073 / T-076). Switch to Onyx (HDT 145 °C, s1) only if H-1 shows the motor base is too hot for PETG (PETG HDT "—") |
| Strut clamps CGE-007 | **Plain FDM PETG** (R4), printed flat: socket and ring axes in the layer plane | PETG; fillets r 2.0 mm | PETG EST | **-5.6** against 13.16 | R4 junction 0.86 → 1.48 (r 2.0, Kt EST); socket wall 0.67 standing → 1.41 in-layer (T-076): **orientation is load-bearing** |
| Pack tray CGE-008 | **Plain FDM PETG** (R1''), walls raised for the 37 mm pack (D-219), notch for the hub collar | PETG | PETG EST | **-8.7** against 25.80 | R1 0.25 / 0.24 → R1'' 1.48 / 1.23, bond 1.75 (T-076). A CF floor plate saves about 2.6 g only, adds a bond line: not taken |
| Avionics bosses (AVN-001 removed) | **Plain FDM PETG** (8 bosses + GPS / RX pads) | PETG | PETG EST; foam-limited stiffness | **-14.9** against 17.91 | R2 rows pass (2.76 / 4.27, T-073); GPS / RX pads still to be drawn |
| Bay cover AVN-008 | **Vacu-former** (makerspace), 0.5 mm PETG sheet over a printed PLA buck (free Prusa); 0.3 mm only if a formed sample passes a press test | PETG sheet | no structural row | **-1.6** (-4.5 at 0.3 mm) against 9.59 | none failing |
| Spar plugs WNG-003/4/5, horn MEC-004, keeper MEC-008 | **Plain FDM PETG**, unchanged (horn printed flat, D-212 rev 3) | PETG | PETG EST | 0 | Horn stall bearing stays on the bench stall test (row K bushing as fallback, engineering-decisions) |
| **Sum, the parts above** | | | | **+0.5 (-17.8 to +20.6)** on a 223.9 g T-067 basis | Most of the change was already decided (T-068 / T-070 / T-073 / D-220); T-080's own process choices (Al hub octagonal, Onyx node, 0.5 mm plates, thermoformed cover) are about **+5 g** against the D-219 PETG plan |

**Bottom line.** The new equipment matters for exactly three failure groups: the hub (aluminium, both mills), the fin saddle (waterjet CF plates) and the centre node (X7 continuous CF, or aluminium). Everything else is closed by geometry and a stated print orientation in plain PETG, and the X7 / Fortus would only add cost and an unknown bond allowable there. Rows that no process closes stay on coupons: pad-cup EVA, bond integrity, CF-to-Al and CF-to-Onyx bonds, printed in-layer / interlayer allowables.

## 1. Sources read today and the allowables derived from them

| Material | Value (as read) | Source (URL, date) | Design value used here | Status |
|---|---|---|---|---|
| Onyx (Markforged composite base) | tensile modulus 2.4 GPa; tensile stress at yield 40 MPa, at break 37 MPa; strain at break 25 %; flexural strength 71 MPa, flexural modulus 3.0 GPa (D7901); HDT 145 °C (D648 B); density 1.2 g/cm3 | Markforged "Material Datasheet: Composites", REV 5.0 - 08/01/2021, https://static.markforged.com/downloads/composites-data-sheet.pdf, read 2026-11-20 (PDF text layer; I re-aligned the table columns, cross-checked by the sheet's own text "Onyx Flexural Strength: 71 MPa") | in-layer 20 MPa and bearing 20 MPa EST (= the PETG basis, because Onyx's 37 MPa break stress matches the 36.5 MPa base behind the PETG values, `structures_a.py` l.16); interlayer 0.26 x 37 = **9.6 MPa EST** | EST until coupon C-1; plastic test plaques "printed with full infill"; moisture state not stated ("—") |
| Continuous carbon fibre (in Onyx) | tensile strength 800 MPa, tensile modulus 60 GPa, strain 1.5 %; flexural 540 MPa / 51 GPa; compressive 420 MPa / 62 GPa (the sheet prints "MPa" for the compressive modulus; read as GPa); density printed as 1.2 g/cm3 | same sheet | on the **fibre area only**: tension 800 x 0.5 = **400 MPa EST**, compression 420 x 0.5 = **210 MPa EST** (the 0.5 knockdown is mine: walls, turns, fibre start/stop and Onyx between rings), then KP 2.156 as a printed part | EST until coupon C-2 |
| | **Interlayer limitation, quoted:** "Continuous Fibers are laid down on the inside of parts ... laid down in-layer, replacing FFF infill." Test plaques are "fiber reinforced unidirectionally (0° Plies)", "fully filled with unidirectional fiber and printed without walls." The sheet also says the data "should not be used to establish design, quality control, or specification limits". | | **Fibre adds nothing across layers.** Every interlayer row of an X7 part is an Onyx-only row (9.6 MPa EST). So the print orientation must put the governing stress in the layer plane, exactly as for PETG. | |
| 6061-T6 aluminium | T6: UTS at least 290 MPa, yield at least 240 MPa ("more typical" 310 / 276); E 68-69 GPa; nu 0.33; density 2.70 g/cm3; fatigue limit 97 MPa at 5 x 10^8 reversed cycles (RR Moore) | https://en.wikipedia.org/wiki/6061_aluminium_alloy, read 2026-11-20 (secondary source; the page cites the standards) | **yield 240 MPa (the minimum, not the typical value)**: von Mises x KF 1.725 <= 240. Bearing yield "—" | secondary source: the conductor must replace it with the supplier mill certificate or an MMPDS / ASM value before H-A1 is judged (escalation s3.2) |
| CF plate (bought, cured) | Xt 600 / Xc 570 MPa, S 90 MPa, E 70 GPa, density 1.6 g/cm3 (std CF fabric, Vf 50 %, 0/90) | ACP Composites PDS Dec 2014, already cited in T-071b A.4 (read 2026-11-19) | x 0.70 EST (T-071b) | not re-read today |
| PETG (Prusament) | density 1.27 g/cm3 | T-067 s3 (search-reported) | 20 MPa in-layer / bearing, 9.5 MPa interlayer, E 2.1 GPa, all EST (`structures_a.py` l.16, `fea_arm.py` l.93-95) | no coupon; HDT "—" (not read) |
| Epoxy bonds | 2.0 MPa shear EST on CF / PETG (`structures_a.py` l.17) | — | CF to 6061 and CF to Onyx: **"—"** | coupons C-3, C-5 |
| Fortus 380mc materials | "—" (product page did not separate the list; two Stratasys datasheets returned HTTP 500) | — | not used | not selected for any structural part (s3) |

Print orientation rule for every printed load-path part (PETG or Onyx): the drawing states the build direction, and every row is judged with the allowable that matches it (in-layer or interlayer), as the escalation's corrected rule requires (s2.4 there).

## 2. What I recomputed (did not trust the reports)

| # | Check | Recomputation | Result |
|---|---|---|---|
| V1 | Escalation V5 bridge bending at the hub mouth | Z = pi/64 (16^4 - 14^4) / 8 = 166 mm3; 17.51e3 / 166 x 1.725 = 182 MPa vs 350 EST | RF **1.92**, reproduced (escalation 1.93) |
| V2 | **Moment at the saddle forward end** (not done by the escalation) | Same governing combo (F = (-53.7, -28.9, 2.1) N, Mz 17.51 N m, escalation V1). Moving the reference aft by dx: ΔMz = Fy dx. dx 0.054-0.075 m (bore mouth of the Al hub at about hub x 45 mm, or of C6 at x 36, to the saddle forward end at body x 0.030, T-071b A.1) | **Mz 19.1-19.7 N m if the terms add, 15.3-15.9 if they subtract.** I did not resolve the sign (it needs the vector form M' = M + (P - P') x F in the code's frame): D-1 must report both ends. |
| V3 | Bridge 16x14 at the saddle mouth | 19.68e3 / 166 x 1.725 = 204 MPa vs 350 EST; x1.5 306; x2 408 | **RF 1.72 / 1.14 / 0.86** (RB / x1.5 / x2). If the terms add, the bridge stop threshold is **DAF >= 1.72, not 1.93** (F-2). |
| V4 | Centre-node net section under Mz (T-071b checked only My and the skin torque) | Section across the saddle body at the bridge socket: 33 mm in y (ears to y +-16.5, T-071b A.6) x 20 mm in z, less the 16 mm socket: I = 20 x 33^3 / 12 - pi x 16^4 / 64 = 56,678 mm4, Z = I / 16.5 = 3,435 mm3; sigma = 19.68e3 / 3,435 x KP | **PETG / Onyx in-layer (20 MPa EST): RF 1.62 / 1.08 / 0.81; interlayer (9.5): 0.77 / 0.51 / 0.38.** Solid, no spar hole, no pin holes, no stress concentration: an **upper bound**. A printed node passes RB only with the z-up orientation and fails at DAF 2. |
| V5 | Can X7 fibre carry the hub-class moment? (to decide where X7 is worth it) | Fibre couple at the +-y faces of a 20 mm block, lever 16 mm: F = Mz x KP x DAF / 0.016 | 3,540 N per side at DAF 1.5, 7,080 N at DAF 3, i.e. **8.8 / 17.7 mm2 of fibre per side at 400 MPa EST**. That is plausible in a 20 mm tall part, but the bore bearing (Onyx 20 MPa, same as PETG: L >= 32.6 mm at x1.5, escalation V3) and the crossing arm holes stay. So X7 is a fallback for the hub, not the choice. |
| V6 | Al hub mass | escalation: 19.7 cm3 solid x 2.70 g/cm3 (density now cited, s1) = 53.2 g; lightened 24-30 g EST | reproduced; +2 g EST for octagonal sleeves (s7.1) |
| V7 | Hub stock envelope (for the purchase) | `fea_hub.py` GEO: sleeves over s +-24 mm (L_SLV) on 12 mm tubes at phi 34.4 deg, radius 6 + 2 + 1 (tube, sleeve, doubler) = 9 mm; block x -15.5 to the collar mouth at about +45 | y half-extent 24 cos 34.4 + 9 = 28.8 mm, z half-extent 24 sin 34.4 + 9 = 22.6 mm, x about 61 mm: **envelope about 61 x 58 x 46 mm EST**, so a 2.5 x 2.5 x 2 in (63.5 x 63.5 x 50.8 mm) block per hub, two blocks (one prototype / scrap). The CAD (T-077) fixes the real size. |
| V8 | CF plate mass for FIN-005 | 50 x 75 x t x 1.6 g/cm3 | 3.0 g (0.5 mm), 6.0 g (1.0 mm) per plate, before windows |
| V9 | Onyx for PETG at equal geometry | 1.2 / 1.27 = 0.945 | -5.5 % mass at equal allowables (EST). A real but small lever; it brings the bond unknown (F-3), so not taken across the board |
| V10 | Budget headroom | T-079 addendum: O4b total about $1,890-1,905 (EST) with the RDQ 2,800 pack at $54.99, reserve unchanged | **about $95-110 left** for every purchase in s10 |

## 3. Trade tables (spec 6.2 format; RF by hand or quoted from the record; "RB" rigid-body demand)

### 3.1 Hub CGE-001 (D-220 already chose aluminium; this table settles the machine)

| Option | Δmass g (vs T-067 15.82) | Margin | Works? | Reliability | Manufacture | Assembly | Aero | Constraints | Source |
|---|---|---|---|---|---|---|---|---|---|
| PETG C6 / V1 / V2 (printed) | +5.6 to +8.5 | net section 0.71; FEA 0.94 / 0.91 | **no** | — | free Prusa (PETG allowed? "—") | as now | none | — | escalation V3-V4; T-076 |
| X7 Onyx + CF hub (rung 4) | about +4 to +8 (EST, C6 envelope, longer collar) | fibre net section OK by V5 at DAF <= 3 if 9-18 mm2 per side fits; **bore bearing stays Onyx (L >= 32.6 mm at x1.5)**; the arm tubes cross the layers at 34.4 deg | not shown | interlayer and bond-to-Onyx unknown (F-3) | X7 access and charge "—" | as now | none | coupons C-1 to C-3 | s1, V5 |
| 6061 hub, knee mill only (Kent, team lab) | +16 to +20 (prismatic, fewer pockets; EST) | yield 240 vs >= 68 MPa needed at DAF 3: about 3.5 | yes by hand | no orientation or interlayer issue | squaring, bores with the tilting head or an angle vise at +-34.4 deg, straight pockets only; no booking | as Tormach | none | heavier | escalation s3.2; s1 |
| **6061 hub, knee mill (bores, datums, pins) + Tormach 440 (contour, pockets, strut sockets) (CHOSEN)** | **+10.2 to +16.2** | as above | **yes by hand; H-A1 / H-A2 to confirm** | bores reamed on the knee mill; contour from the bore datums on the Tormach | 4-5 setups (square, bore A at +34.4, bore B at -34.4, bridge bore, contour top / bottom); Tormach training and booking "—" | bonded tubes with a glass-scrim barrier, cross-pin; grommets at the phase-lead exits | none | stock and tooling purchases (s10); CG forward (s6) | escalation s3.2; V6-V7 |
| 6061 hub, Tormach only | same | same | yes | angled bores need an angle fixture on a 3-axis machine (no 4th axis listed) | more fixture work | same | none | — | jacobs-equipment.md |

Why both machines: the knee mill is in the team lab (no booking) and has a tilting head (jacobs-equipment.md), which is the simplest way to put the two 12 mm bores at +-34.4 deg and ream them to the bond fit. The Tormach is a CNC with conversational cycles, which is what makes the lightening pockets and the sleeve outline repeatable. If Tormach access is not confirmed by the T-077 freeze, the hub is drawn as the knee-mill shape (upper mass end).

### 3.2 Centre node CGE-006 (bridge saddle, wing-end node of the skin)

| Option | Δmass g (vs T-067 9.67) | Margin (hand, EST) | Works? | Reliability | Manufacture | Assembly | Aero | Constraints | Source |
|---|---|---|---|---|---|---|---|---|---|
| T-071b C6 node in PETG z-up (one-piece saddle with ears, CF plate N2, 4 pins) | +13.9 solid | My rows: body shear 1.30 / 0.87, ear bond 1.39 / 0.93 (RB / x1.5); **Mz net section 1.62 / 1.08 / 0.81 (V4)** | **no** at x1.5 / DAF 2 | interlayer 0.77 if mis-oriented | free / own printer | slot and plate as T-071b | none | — | T-071b A.2, A.4; V4 |
| **X7 Onyx + CF rings, z-up, same envelope, N2 plate waterjet, 4 x 3 mm pins (CHOSEN, conditional)** | **+12 to +18** | Mz section: fibre at +-y faces carries the in-plane bending; the Onyx-only rows are those of the PETG option (bearing 20, interlayer 9.6 EST) | **expected yes; must be shown** by the six-component rows (s11 step 1) and coupons C-2 / C-3 | **bonded socket on Onyx (nylon) has no allowable (F-3)**: pins carry torsion | X7 job; fibre layout in Eiger kept as a record | as T-071b | none | X7 charge "—" | s1; V4-V5 |
| 6061 node, Tormach (fallback) | about +22 to +33 EST (printed portion x 2.70 / 1.27 after pocketing) | yield 240 / KF: large | yes | no orientation issue; CF-Al barrier | 3-4 setups | same | none | heavier; CG aft side of the CG (s6) | s1 |
| Second waterjet CF clamshell around the bridge-spar crossing (as FIN-005) | about +8 to +12 EST | plates carry Mz in-plane well (1 mm plate pair: Z about 530 mm3, RF > 5 EST), but the bridge has to load the plates through the 1 mm tube wall in pin bearing (about 290 N per wall per pin at 30 mm spacing, CF bearing "—") | not shown | many bonded / pinned joints in a 24 mm deep slot that already removes the bottom skin (T-071b A.5) | waterjet + cradle | hard | none | — | hand estimate |

### 3.3 Fin rib saddle FIN-005

| Option | Δmass g (pair, vs 28.78) | Margin | Works? | Reliability | Manufacture | Assembly | Aero | Constraints | Source |
|---|---|---|---|---|---|---|---|---|---|
| Largest printed saddle, in-layer | about +10 vs solid | P12 0.89, P11 about 0.8 | **no** | — | — | — | — | wing depth 23.9 mm | T-068 V4 |
| Clamshell, 1.0 mm CF plates (T-071b sized) | about +1 | plate 15.9 / 16.2; bond 2.70; cradle pins 1.66 / 2.94 | yes | plates far over-sized | waterjet | as D-215 | none | — | T-071b B.2; T-076 |
| **Clamshell, 0.5 mm CF plates, waterjet (CHOSEN)** | **-5.0** (-7.8 to -0.8) | plate about 8 EST (in-plane stress linear in t: 15.9 at 1.0, 23.8 at 1.5 mm, T-071b); bond and pins as above | **yes at EST** | thin plate: pierce delamination risk on the waterjet (lead-in outside the part, backing sheet; practice "—"); plate thickness measured on receipt | OMAX waterjet (wet cut: no CF dust) | as D-215 | none | one 0.5 mm sheet also gives the N2 node plates | T-071b; V8 |
| Clamshell, 1.5 mm lite-ply (laser) | about -4 | lite-ply shear allowable "—" (T-071b C3) | not shown | moisture | laser cutter | same | none | — | T-071b A.2 |
| X7 Onyx + CF saddle (printed, in the 23.9 mm depth) | about -2 | in-layer fibre helps P12, but P11 wall / interlayer rows stay Onyx (9.6) | not shown | bond unknown | X7 | same | none | — | s1 |

### 3.4 Fin root block FIN-003

| Option | Δmass g (pair, vs 37.80) | Margin | Works? | Reliability | Manufacture | Assembly | Aero | Constraints | Source |
|---|---|---|---|---|---|---|---|---|---|
| As drawn, PETG | 0 | P6 0.50, P8 0.51 | no | — | — | — | — | — | T064r |
| **Enlarged, PETG z-up, 3 x 3 mm pins in a 4 mm boss (CHOSEN)** | **+12.2** (+9.2 to +17.2) | P6 1.58, P8 1.72 (in-layer rule); pins 1.43 / 2.53 at 1.64 kg | **yes at EST** | interlayer share (torsion) at 9.5 EST; coupon `ASM-A-PETG-JOINT-ILAY` | plain FDM; build direction on the drawing | as D-215 | FIN-006 blister grows (frontal area "—") | — | T-071b B.2; T-076 s2 |
| X7 Onyx + CF, z-up, slimmer walls (mass-recovery variant) | about +4 to +8 EST | in-layer rows rise with fibre; interlayer rows equal to PETG | not shown | bond to Onyx "—" (F-3) | X7 | same | smaller blister | coupons C-1 to C-3 | s1 |
| Clamshell root block | about -25 vs solid | 18 mm couple: about 1.15 kN hole bearing | likely no | — | — | — | — | — | T-068 s6 |

### 3.5 Foot shoe GER-001 and pad cup

| Option | Δmass g (4 feet, vs 18.20) | Margin | Works? | Reliability | Manufacture | Assembly | Aero | Constraints | Source |
|---|---|---|---|---|---|---|---|---|---|
| **PETG shoe + cup, plate flat (in-layer), 3 mm CF pin, UHMW face (CHOSEN)** | **+7** (+5 to +9) | P2 2.03 in-layer; cup EVA rows 0.01 / 0.14 / 0.15 (model and data, coupon C-6) | yes for the printed part; the EVA rows are open | drop rig decides | FDM | pin through cup and pad | none | — | T-068 D3; T-071b B.3; T-076 s5 |
| Onyx shoe (X7, no fibre) | -1 (x 0.945) | same rows | same | tougher nylon (Izod 330 J/m notched, sheet; PETG Izod "—") | X7 | same | none | charge "—" | s1 |
| Waterjet G10 / CF rim insert in the cup | small | would stiffen the rim, but the failing quantity is EVA bearing, not the cup | no | — | waterjet | — | — | — | T-076 s5 |

### 3.6 Cage printed parts: motor cups CGE-003, strut clamps CGE-007, pack tray CGE-008

| Option | Δmass g | Margin | Works? | Reliability | Manufacture | Assembly | Aero | Constraints | Source |
|---|---|---|---|---|---|---|---|---|---|
| **Cups R3fix PETG, plate on the bed (sleeve hoop and plate bending in-layer) (CHOSEN)** | **-11.2** | S2 cantilever 1.37; worst row MS +0.33 (tip-over arm) | yes at EST | **H-1 thermal hold point** (motor-base temperature at hover with the B03 K-type probes) | FDM | as now | none | — | T-073; T-076 |
| Cups in Onyx | -1.4 more | same | yes | HDT 145 °C (sheet) | X7 | same | none | charge "—" | s1 |
| **Clamps R4 PETG, printed flat, fillets r 2.0 (CHOSEN)** | **-5.6** | junction 1.48 (Kt EST), wall 1.41 in-layer (0.67 standing) | yes at EST | coupon on Kt | FDM | as now | none | — | T-076 s2 |
| **Tray R1'' PETG, walls raised for 37 mm, collar notch (CHOSEN)** | **-8.7** | tabs 1.48, wall 1.23, bond 1.75 | yes at EST | drop coupon (T-073 R1) | FDM | strap | none | — | T-073; T-076 |
| Tray with a 0.5 mm CF floor (waterjet) | about -11 | floor fine; adds a CF-PETG bond line | not needed | one more bond | waterjet + FDM | — | none | — | V8 scaling |

### 3.7 Avionics bosses, bay cover, small parts

| Option | Δmass g | Margin | Works? | Reliability | Manufacture | Assembly | Aero | Constraints | Source |
|---|---|---|---|---|---|---|---|---|---|
| **8 PETG bosses + GPS / RX pads (CHOSEN)** | **-14.9** (-15.9 to -13.9) | 2.76 / 4.27 (mount frequency), bonds 98 | yes | foam-limited stiffness | FDM | bonded to the glass skin | none | pads still to draw | T-073 R2 |
| **Bay cover vacu-formed 0.5 mm PETG over a PLA buck (CHOSEN)** | **-1.6** (-4.5 if 0.3 mm passes a press test) | no structural row | yes | thickness varies after forming: measure, then set the CAD wall (s9) | vacu-former; buck on the free Prusa (PLA) or ShopBot MDF | trim, seat on the skin | same outer line | sheet purchase (s10) | T-070 s4 |
| Bay cover printed (as drawn) | 0 | — | yes | — | FDM | — | — | — | T-067 |
| **Spar plugs, horn, keeper PETG as drawn (CHOSEN)** | 0 | horn stall bearing on the bench test | yes | — | FDM | — | — | — | D-212 rev 3 |

Fortus 380mc and J55: not used for any part. The Fortus could only replace PETG with another FDM thermoplastic whose interlayer behaviour is no better known (allowables "—"). The J55 is for fit models; free PLA fit prints on the Prusas do the same job at $0, so they are used for the hub / node / clamshell fit checks before metal or X7 parts are made.

## 4. Process plan per machine (what each one makes)

| Machine (where) | Parts | Notes |
|---|---|---|
| Kent knee mill (team lab) | hub: square the block, bore A / B at +-34.4 deg, bridge bore, ream to the bond fit, 3 mm cross-pin holes; prototype hub; Al fallback parts | bond fit = tube OD + scrim + glue line: bore size "—" until the tubes and the scrim are measured (coupon C-5 sets it) |
| Tormach 440 (metal shop) | hub contour, lightening pockets, octagonal sleeve flats, strut sockets; Al node if the fallback is taken | training / booking "—"; CAM in Fusion (EST) |
| OMAX 2626 waterjet (metal shop) | FIN-005 CF plates (4), N2 node plates (2), G10 or CF washers if any | 0.5 mm CF; lead-ins outside the part; DXF from the CAD |
| Markforged X7 (room 332) | CGE-006 node; FIN-003 recovery variant only after coupons; coupons C-1 / C-2 / C-3 | Onyx + CF; Jacobs fibre stock (CF loaded?) and charge "—" |
| Prusa (free PLA) | fit models; thermoform buck; jigs | **whether PETG (R03 spool) may be printed on them is "—" (F-4)** |
| PETG printer ("—") | all PETG parts in s0 | see F-4 |
| ShopBot (makerspace) | XPS wing / fin cores, plate pockets in the core, MDF buck if needed | — |
| Laser cutters | lite-ply centre bulkheads (T-070), glass bias templates, bonding jigs (hub-arm alignment, fin alignment) | no CF on the laser (fumes; Jacobs rule "—") |
| Vacu-former | bay cover AVN-008 | — |
| DIWire | elevon pushrods with Z-bends (D-212) | — |
| Drill press | pin holes in CF tubes and printed parts with drill jigs | CF dust control "—" (T-068) |
| Creaform Go!SCAN | s9 | — |

## 5. Effect on each known failing row (RF < 1 in T-064r / T-071b / T-073 / T-076 / escalation)

| Row (record) | Worst RF | Process decision | Expected after | Evidence still needed |
|---|---|---|---|---|
| Hub net section under Mz (escalation V4) | 0.71 | 6061 hub | about 3.5 by hand at DAF 3 | H-A1 / H-A2 with the cited alloy |
| C6 / V1 hub FEA whole-hub p99 (T-076, T-076b) | 0.94 / 0.91 RB, 0.62 x1.5 | 6061 hub | — | H-A1 |
| Hub bridge-bore bond in torsion (escalation F-11) | 0.90 at DAF 2 | Al hub L >= 30 bond + 3 mm cross-pin (knee mill) | pin carries torsion; bond becomes integrity class | C-5; pin row in H-A1 |
| Bridge 16x14 bending (escalation V5; V3 here) | 0.97 at x2 (mouth); **0.86 at x2 at the saddle (V3)** | not a process item | — | D-1 at both ends; 18x16 tube "—" if DAF >= 1.72 |
| CGE-006 node body shear / ear bond (T-071b) | 0.87 / 0.93 at x1.5 (My only) | X7 Onyx + CF z-up, fallback Al | unknown until the six-component rows | s11 step 1, C-2, C-3 |
| CGE-006 node net section under Mz (V4, new) | 0.81 at x2 (PETG in-layer) | same | — | same |
| P12 / P11 saddle (T064r; T-071b) | 0.28 / 0.34 (best printed 0.66 / 0.90) | CF clamshell, 0.5 mm plates | plate about 8 EST; bond 2.70 | C-4 node coupon |
| Cradle pin bearing (T-071b) | 0.37 | 3 pins, 4 mm boss | 1.66 / 2.94 | CAD |
| P6 / P8 root block (T064r) | 0.50 / 0.51 | PETG z-up enlarged | 1.58 / 1.72 | `ASM-A-PETG-JOINT-ILAY` coupon (C-1 in PETG) |
| Root block / saddle pins (T-071b) | 0.23 / 0.66 | 3 x 3 mm, 4 mm wall | 1.43 / 2.53 | CAD |
| P2 shoe junction | 0.96 | plate printed flat | 2.03 | drawing note |
| CUP EVA rim / pin / wall (T-071b, T-076) | 0.01 / 0.14 / 0.15 | none (data gap) | — | C-6 |
| Bond integrity P3, P7, P10, P13 | 0.26-0.67 | none (coupon class) | — | C-4 |
| R1 tray tab / wall (T-073) | 0.25 / 0.24 | R1'' | 1.48 / 1.23 | drop coupon |
| R3 cup S2 (T-073) | MS -0.71 | R3fix | 1.37 | — |
| R4 junction / standing wall (T-073, T-076) | 0.86 / 0.67 | fillets r 2.0, printed flat | 1.48 / 1.41 | Kt coupon |
| P9a rib (T064r) | 0.86 → 1.03 with mu 0.30 | not a process item | 1.03 (tight) | twist coupon, drag test |
| SITL pitch use 0.59-0.63 vs 0.60 (escalation s4) | — | not a process item; mass-dependent: re-run with the T-080 mass and CG | — | S-1 to S-4 runs (escalation) |

## 6. Mass and the mass-dependent checks (AM-011)

Roll-up (scratch `t080_mass.py`; basis T-067 adopted, s4 of T-067; parts in s0 only, 223.9 g of the 250.2 g printed set): **+0.5 g mid, -17.8 to +20.6 g**. So the 1.64 kg basis of the O4b checks holds within about +-20 g (EST). What does change:
- **CG.** Crude moment sum with EST part stations (hub x -0.069, root blocks about 0.26, shoes about 0.34, motor cups about -0.07, node about 0.05, avionics about 0.08; CG 0.021; x aft): about **+4 g m, i.e. CG about 2.6 mm aft at 1.64 kg (EST)**. Most of it comes from the T-068 root blocks and shoes (already decided), and part is offset by the Al hub (forward). On the T-068 T4 slope (10 mm aft: static margin 7.9 → 3.8 %) that is about -1.1 % static margin (EST). The forward-trim margin (0.5 mm, escalation F-8) moves the other way. **Both CG claims must be re-run from `sitl/cad_mass.py` after the T-077 CAD;** this estimate is not a result.
- **A-P10.** The hub becomes stiffer (E 68-69 GPa against 2.1) and heavier, and the node changes mass. The coupled cage / wing-torsion mode (hi corner 79 Hz against the 88 Hz limit, T-076 s3) moves. Re-run `t076_modal.py` with the hub as an aluminium member and the s0 masses.
- **Landing, tip-over, SITL, mission_gate_a:** re-run at the T-077 CAD mass (minimize-compute: once, at the end).

## 7. Design-for-manufacture rules for the T-077 CAD (CAD fidelity: draw the real shape)

### 7.1 Machined aluminium (hub, any Al fallback part)
1. **Sleeve outlines prismatic (octagonal, flats aligned with the bore setups), not round.** A round 1.0 mm sleeve on an inclined axis needs 3-D contouring from two sides on the Tormach and cannot be cut on the knee mill. Octagon across flats = tube OD + 2 x 1.0 mm minimum wall: +21 % sleeve area against round, about +2 g (V6 basis; EST).
2. Internal corner radii >= the end-mill radius used (tool list "—": draw R 3.0 mm for a 6 mm cutter, EST) and note the tool on the drawing.
3. Minimum wall 1.0 mm at a flat, 1.5 mm around a drilled hole edge (EST); bridge-bore floor web 2.5 mm (escalation s3.2).
4. Bores: 12 mm arm bores and the 16 mm bridge bore drawn at the bond-fit diameter (tube OD + scrim + glue line, value from coupon C-5; "—" now), reamed; end face of the bridge released 0.5 mm (BR_GAP).
5. Phase-lead exits (4.8 mm, s +-18, `fea_hub.py` HOLE_R 2.4) with a 0.5 mm chamfer and a grommet drawn as a part (escalation s3.2 wiring; exposed-wiring rule unchanged).
6. 3 mm cross-pin holes through the collar and the bridge tube, drilled together on the knee mill with the tube bonded (D-202 practice).
7. A 2-D drawing with datums (bore A axis, bridge axis), tolerances and the setup sequence; anodising "—" (not needed for function).

### 7.2 Waterjet plates
DXF from the CAD at the measured stock thickness (nominal until receipt, marked "—"); holes over 3 mm cut, under 3 mm drilled after; edges sanded; no internal corner under the jet radius ("—", read on the OMAX at Jacobs).

### 7.3 X7 parts (Onyx + CF)
Build direction on the drawing; fibre rings drawn as a manufacturing note (Eiger file kept as the record, internal, not modelled as geometry). Every bonded interface either pinned or judged as integrity-class until C-3 passes. Minimum wall and fibre feature sizes per the X7 slicer ("—").

### 7.4 FDM PETG parts
Build direction and the in-layer / interlayer judging on every load-path drawing (escalation F-6). Masses from volume x print basis (T-067 s7, `printed_mass.json`), never hard-coded.

### 7.5 Thermoformed cover
Draft >= 3 deg on the buck (EST practice, not sourced); CAD wall = measured mean thickness of the first formed part; trim line drawn.

## 8. Coupons (UNVERIFIED until done)

| ID | What | Specimens / load | Pass line | Gates |
|---|---|---|---|---|
| C-1 | Printed in-layer and interlayer tension, PETG (on the printer actually used) and Onyx (X7) | 5 + 5 per orientation, tensile bars (D638 type IV per the Markforged sheet's own specimen), quasi-static | mean - 3 sigma (or min of 5) >= 20 / 9.5 MPa x the knockdown the analysis assumed | every printed RF; `ASM-A-PETG-JOINT-ILAY` |
| C-2 | X7 CF knockdown: Onyx beam with the planned concentric CF rings, 3-point bend, plus a pin-bearing coupon with a CF ring round a 3 mm hole | 5 each | fibre stress at failure >= 400 MPa tension-side EST x KP margin used | CGE-006, FIN-003 X7 variant |
| C-3 | Epoxy bond of a CF tube into an Onyx socket (and into PETG as control) | 5 + 5 push-out / torsion | mean shear >= 2.0 MPa (the EST used) | any bonded X7 part; F-3 |
| C-4 | Clamshell node (one fin saddle) in Mz, My, Mx to 2.156 x limit; bond integrity | 1-2 nodes | no failure at 2.156 x limit | FIN-005; bond-integrity rows (T-068 s7) |
| C-5 | CF tube into 6061 bore with one glass-scrim wrap; surface prep (abrade + solvent, primer "—") | 5 push-out + 3 torsion | mean shear >= 2.0 MPa; sets the bore fit | hub, Al fallback node |
| C-6 | Pad cup: rim indentation, pin-hole bearing, side load, drop at 1.2 m/s | per T-076 s5 | RF >= 1.0 with measured EVA data | CUP rows |
| H-1 | Motor-base temperature at hover thrust, 5 min, B03 K-type probes | 1 motor on the thrust stand | below the PETG HDT less 10 °C (HDT to be cited) | cups stay PETG, else Onyx |
| existing | RMRC rib twist, pad mu drag test, horn stall bench, tap test (A-P10) | as recorded | as recorded | T-068, D-212, T-076 |

## 9. Go!SCAN plan for bought parts (CAD fidelity)

Scanner specification (accuracy, resolution, smallest feature) was not read ("—"); booking and training "—". Scanning starts after the December order arrives.

| Part (BOM) | Method | Why |
|---|---|---|
| T-Motor MN2212 KV780 (P01) x 1 | scan (matte removable developer spray, positioning targets) + calipers on the base hole pattern and shaft | CAD of the bell, base and wire exit; base pattern drives the cup |
| APC 9x4.5MR / MRP (P02) x 1 each | scan both faces; compare with the vendor geometry where published ("—") | real blades (CAD fidelity rule); thin trailing edge below scanner resolution: calipers on chord / thickness at 3 stations |
| SpeedyBee BLS 35A 4-in-1 ESC (P04), Kakute H743-Wing FC, RP3 RX (V02), M10Q GPS (V04), MS4525 (V05) | calipers + vendor drawing; scan only the GPS and the ESC with components (height map) | small boards: vendor drawing is better than a scan; component height decides the bay cover clearance |
| ES3054HV servo (M01) | scan + calipers on the mounting ears and the spline | linkage and pocket |
| 4S 2,800 mAh pack (O4b; RDQ or GNB) | scan with positioning targets only, **no spray, no heat, pack at storage charge, no pressure** | tray walls (37 mm) and strap; LiPo safety |
| XT60 / connectors, pushrod connectors, pins | calipers / vendor drawing | too small to scan usefully |
| CF tubes, rods, CF plate, Al stock | calipers / micrometer (OD, ID, thickness) | sets bore fits and plate CAD thickness |
| As-built checks: skinned wing section, thermoformed cover, X7 node, machined hub | scan and compare with the CAD (deviation map) | CAD fidelity of made parts: skin thickness, forming thinning, print warp |

Acceptance (EST, not sourced): scan-to-CAD deviation within +-0.3 mm on parts over 20 mm, else update the CAD and mark the changed dimension with its source (scan file name, date). Unknown dimensions stay "—" and the part is flagged, never invented.

## 10. Costs and access that need Dillon (prices read or "—")

Headroom about **$95-110** (V10). None of these is priced today:

| Item | Quantity (EST) | Price | Note |
|---|---|---|---|
| 6061-T6 bar for the hub | 2 blocks about 2.5 x 2.5 x 2 in (V7) | "—" (OnlineMetals page 403 today) | mill certificate needed for the allowable (s1) |
| Reamers / end mills for 12 mm and 16 mm bond fits | 2 reamers (sizes from C-5), end mill "—" | "—" | Jacobs tooling stock "—": ask first |
| CF plate 0.5 mm | one sheet about 150 x 300 mm (4 fin plates 50 x 75 + 2 node plates) | "—" | replaces the T-068 / T-071b "plate stock" line |
| Markforged material charge (Onyx, CF) | node, coupons C-1 to C-3, optional root blocks | "—" (jacobs-equipment.md: material costs "—") | |
| PETG sheet 0.5 mm (and 0.3 mm sample) | one sheet | "—" | T-070 listed it as optional |
| Scanning spray | 1 can | "—" | removable type |
| Glass scrim | from the 48 g/m2 cloth already on the O4b list | $0 marginal | galvanic barrier |
| **Access** | Tormach training and booking; X7 job access and fibre loaded; whether the free Prusas accept PETG; waterjet booking; CF cutting / drilling dust rules | — | F-4 |

## 11. Implementation scope and order (sonnet implementers; stop rules in bold)

Do not touch `structures/fea_hub.py`, `landing_centre_a.py` defaults or the T-076c files of the running hub-FEA task; work in copies.
1. **Six-component demand at both ends of the bridge ($0).** Extend the escalation s3.4 item 1 script: wrench at the hub bore mouth, along the bridge, at the saddle forward end and at the saddle body section, per case, at 1.64 kg, with the vector transfer M' = M + (P - P') x F. Reproduce V2-V4 here within 2 % (sign resolved). Re-derive the T-071b node rows (body shear, ear bond, socket bearing, net section) and the FIN-003 / FIN-005 rows with all components. **Stop and report if any CGE-006 row < 1.0 at RB in the X7 EST allowables; then the node goes to the 6061 fallback.**
2. **D-1** (escalation s3.3), reporting DAF at the hub mouth **and at the saddle mouth**. **Stop if DAF_bridge >= the bridge RF at that end (1.92 at the mouth, 1.72 at the saddle if V2's terms add).**
3. Materials table as a new module (for example `structures/materials_t080.py`; existing allowables untouched): Onyx, CF in Onyx, 6061-T6, CF plate, PETG, each with its source, date and EST flag exactly as s1.
4. Judging code (escalation s3.4 item 3: zone volume-weighted percentiles, corner exclusion, orientation split, von Mises for metal).
5. **H-A1 / H-A2** with the 6061 values and the s7.1 geometry (octagonal sleeves, 2.5 mm floor web, L >= 30 bond, BR_GAP 0.5, cross-pin). **Stop on any row < 1.0 at max(DAF, 1.5).**
6. Node: hand rows for the X7 node with the s1 EST values (fibre area per side from the X7 slicer), plus one FEA if the hand RF < 2 (copy of the hub FEA driver with an orthotropic layered option, or the Al fallback geometry). **Stop if < 1.0.**
7. FIN-005 0.5 mm plate rows (plate in-plane and out-of-plane, plate-cradle bond), FIN-003 PETG z-up rows, all at 1.64 kg with the step-1 demand.
8. Scratch roll-up (`mission_gate_a.py` on a copy) with s6 masses; A-P10 re-run (`t076_modal.py`) with the Al hub stiffness and mass.
9. **T-077 CAD** (after Dillon approves the s10 purchases and the access items): hub as a machined part with a drawing (s7.1); CF plates as DXF parts at stock thickness; node as an X7 part with the build direction; PETG parts with build directions; thermoformed cover; grommets and pins as parts; then `t067_mass_audit.py` on the new shapes and the gates once at the end (build, `collide.py --glb`, `assembly_check.py`, swept insertion, `wire_inventory.py`, `sitl/cad_mass.py`, `mission_gate_a.py`, CG trim and static-margin claims, landing scripts, `proofs/run_all.py`, `python -I tools/ledger_audit.py`).
10. Coupons C-1 to C-6 and H-1 when material is in hand; replace every EST allowable they cover.
11. Records (conductor): CHANGE-LOG D-2xx citing this file; the s3 trade tables into `docs/engineering-decisions.md`; BOM lines (Dillon); claims `ASM-A-ONYX-ALLOW`, `ASM-A-AL6061-ALLOW`, `ASM-A-CF-AL-BOND`, `ASM-A-CF-ONYX-BOND`, `CL-A-CENTRE-NODE-MZ`.

## 12. Findings

| ID | Severity | Evidence | Required fix |
|---|---|---|---|
| F-1 | **MAJOR** | V2, V4: the centre node (CGE-006) rows in T-071b used the span-axis moment and skin torque only, the same error the escalation found for the hub. Mz at the saddle is 15.3-19.7 N m; a PETG z-up node net section is 1.62 / 1.08 / 0.81 (RB / x1.5 / x2), 0.77 at RB if the layers are wrong | Six-component node rows (s11 step 1) before any node CAD; X7 CF z-up node with an Al fallback |
| F-2 | **MAJOR** | V3: bridge 16x14 at the saddle mouth RF 1.72 / 1.14 / 0.86 if the shear lever adds to Mz; the escalation's stop line (1.93) is for the hub end | D-1 reports both ends; stop line = the lower RF; 18x16 tube price and stock "—" |
| F-3 | **MAJOR** | Onyx is a nylon composite base (Markforged sheet: "Onyx is a micro carbon fiber filled nylon"); no bond allowable for epoxy on Onyx exists in the repo or the sheet | No X7 part counts a bond row until C-3 passes; torsion carried by pins |
| F-4 | **MAJOR** | jacobs-equipment.md lists the Prusas as "PLA, free"; about 20 load-path parts are PETG (R03 spool); where PETG is printed is not recorded | Dillon / Jacobs: confirm PETG printing access; otherwise Onyx (X7, charge "—") or a team printer (cost) |
| F-5 | MAJOR (DFM) | Escalation s3.2 specifies 1.0 mm round sleeve walls; round sleeves on +-34.4 deg axes need 3-D contouring (Tormach only) | Octagonal sleeves, 1.0 mm minimum at the flats, +2 g EST (s7.1) |
| F-6 | MINOR | Markforged data are unidirectional plaques "printed without walls" and "should not be used to establish design ... limits" (sheet) | EST knockdown 0.5 now; C-2 replaces it |
| F-7 | MINOR | The sheet prints the CF density as 1.2 g/cm3 and the compressive modulus unit as MPa | Weigh coupon C-2 to get the real part density; read the modulus as GPa |
| F-8 | MINOR | 6061 values are from a secondary source (Wikipedia, minimum T6 values) | Supplier mill certificate or MMPDS / ASM before H-A1 is judged |
| F-9 | MAJOR (money) | V10: about $95-110 of headroom against six unpriced lines (s10) | Price each line before the December order; Dillon approves |
| F-10 | MINOR | s6: the Al hub changes the cage stiffness and mass; A-P10 hi corner is 79 vs 88 Hz | Re-run `t076_modal.py` with the Al hub |
| F-11 | MINOR | s6: CG about 2.6 mm aft (EST, crude), static margin about -1.1 % | CG and static-margin claims from `cad_mass.py` after T-077 |
| F-12 | OBSERVATION | The fin saddle plates were sized at 1.0 mm with RF about 16; 0.5 mm is enough on the same model and shares stock with the node plate | Adopt 0.5 mm; rows re-run in s11 step 7 |

## 13. Limits of this record

Every allowable except the cited 6061 minima and the Markforged typical values is EST, and those two are typical / secondary values turned into EST design values by my knockdowns. The node net section (V4) is a solid upper bound with no spar or pin holes. The sign of the shear-lever term at the saddle (V2) is not resolved. Masses are hand / record estimates; the T-077 voxel audit replaces them. CG and static-margin shifts are crude. The Go!SCAN specification, Jacobs material charges, training and booking rules, the X7 fibre stock, the Fortus material list and all prices are "—". No FEA, SITL, landing simulation or interference check was run.
