"""E2 battery / energy engineer: pack selection, energy budget per mission phase, voltage sag, charging and
test-day pack count for the K09-L quad tailsitter.

Run:  python -I redesign/team/E2/energy_claims.py        -> claims.json beside this file
Then: python -I redesign/proofs/build_graph.py           -> confirms nothing drifted

Method (one paragraph). The budget is kept in amp-hours, because that is what the flight controller's current
sensor counts (BATT_CAPACITY / BATT_LOW_MAH). For each phase the bus power P (W) is converted to pack current
with a Thevenin pack model, I = (Voc - sqrt(Voc^2 - 4 R P)) / (2 R), so voltage sag costs capacity. Hover power
comes from the maker's thrust table (linear through zero below the first row, as the K09 review did), with the
fin/tube download factor and the ESC loss; climb uses momentum theory; cruise uses the K09 drag build-up with
the review's corrected propulsive efficiencies. The 20 % reserve is 20 % of nameplate and is never planned
into. Two cases: BASE (sized mass, new pack, calm, warm) and PESSIMISTIC (2.6 kg gate, 92 % capacity, wind and
control margin on hover, CD0 x 1.3, eta_prop 0.35, longer transitions, cold pack). Every input is a node id.
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "proofs"))          # redesign/proofs (python -I adds no paths)
import proofkit as pk  # noqa: E402

kit = pk.Kit(__file__, params=["../../params/params.json"])
P = "P:"

# ---------------------------------------------------------------- sources
kit.source("SRC-E2-OVONIC-LISTINGS", "Ovonic 4S 6500 hard-case listings (mass, size)", kind="web",
           url="https://us.ovonicshop.com/products/ovonic-50c-14-8v-6500mah-4s1p-hardcase-14-deans-lipo-battery",
           where="search results 2026-11-09 (pages rate-limited, not opened): Ovonic 50C 6500 4S hard case 522 g, "
                 "139 x 47 x 49 mm (us.ovonicshop.com); Ovonic 120C 6500 4S 551 g, 135 x 46 x 49 mm (ampow.com); "
                 "130C 6500 4S 545 g, 138 x 47 x 47.5 mm (rccaraction.com, Muchmore); 130C 2-pack 680 g, "
                 "157 x 48 x 43 mm, XT60 + JST-XH (rcdrone.top)",
           note="none of these is the exact 130C XT60 SKU the BOM buys; weigh and measure the first pack (T-E2-WEIGH)",
           status="UNVERIFIED")
kit.source("SRC-E2-OVONIC-120C-EC5", "Ovonic 14.8V 120C 4S 6500 mAh hard-case LiPo, EC5, 2-pack (named SKU, D-58)",
           kind="web", url="https://www.ampow.com/products/2-pack-ovonic-4s-6500mah-120c-lipo-hardcase-ec5-1-8-rc-car",
           checked="2026-11-10",
           where="mass and size re-confirmed from the listing's search snippet 2026-11-14 (551 g +/- 5 g per piece, "
                 "135 x 46 x 49 mm, EC5; page itself HTTP 429 that day, price not re-read). Product page read 2026-11-10: 6500 mAh, 120C, net weight 551 g (+/-5 g) per piece, 135 x 46 x 49 mm "
                 "(+/-3 mm), EC5 plug, JST-XHR-5P balance, 2 packs, in stock, EUR 98.69 shown (EU storefront; "
                 "another snippet EUR 113.30). Lead gauge not stated on the page: the EC5 contact takes 8-10 AWG, so "
                 "10 AWG is inferred, not read",
           note="checked = mass, size, plug and balance lead compared with the page; the lead gauge and the US price "
                "are confirmed by I1 at order (photo or seller answer) and by E2 on arrival (T-E2-WEIGH step 3a)")
kit.source("SRC-E2-TATTU-6750", "Tattu 4S 6750 mAh 25C LiPo, XT90 (fallback SKU)", kind="web",
           url="https://www.gensace.de/tattu-6750mah-14-8v-25c-4s1p-lipo-battery-with-xt90.html",
           where="search results 2026-11-10 (page not opened): net weight 605 g (+/-10 g), wire gauge 10#, XT90, "
                 "about 138 x 42 x 44 mm; NextFPV USD 74 sale / 83 list per pack, stock 'contact us'; Grepow 620 g",
           status="UNVERIFIED")
kit.source("SRC-E2-PACK-SEARCH-1114", "4S 6000-6500 mAh pack listings searched for a lighter named pack (E2 closure)",
           kind="web", url="https://www.ampow.com/products/ovonic-50c-14-8v-6500mah-4s1p-hardcase-14-deans-lipo-battery",
           checked="2026-11-14",
           where="web search 2026-11-14 (ampow / ovonicshop pages returned HTTP 429, rcdrone.top HTTP 403: snippets "
                 "only). Ovonic 50C 6500 4S hard case Deans: 522 g (dev. 20 g), 139 x 47 x 49 mm, lead gauge not "
                 "stated (rcdrone.top/products/ovonic-6500mah-4s-lipo-battery). Muchmore 4S 6500 130C XT90: 545 g, "
                 "10 AWG, 138 x 47 x 47.5 mm (rccaraction.com/?p=331350). Ovonic 4S 6200 130C EC5: 548 / 590 g, 12 AWG "
                 "(us.ovonicshop.com). ProTek 4S 6500 120C HV: 547 / 578 g. Powerhobby 4S 6500 100C: 19.8 oz = 561 g. "
                 "LiperiAir 6200 4S: 586 g. DXF 4S 6500 100C: 575 g. Ovonic 120C 6500 EC5 2-pack: 551 g +/- 5 g, "
                 "135 x 46 x 49 mm (ampow.com snippet, same as SRC-E2-OVONIC-120C-EC5)",
           note="no listed 4S pack of >= 6.1 Ah (the capacity the 3.5 min cruise to BATT_LOW needs, CALC-E2-PACK-TRADE) "
                "with 10 AWG leads was found under 551 g; prices not re-read (pages rate-limited)",
           status="UNVERIFIED")
kit.source("SRC-E2-PACK-SEARCH-D163", "4S 5.8-6.2 Ah packs under 551 g (E2 D-163 search)", kind="web",
           url="https://buddyrc.com/products/gens-ace-redline-6000mah-15-2v-130c-4s1p-hard-case-hv-lipo-battery",
           checked="2026-11-14",
           where="web search 2026-11-14 (vendor pages HTTP 429, snippets only). Gens Ace Redline 6000 mAh 15.2 V 130C "
                 "4S1P hard case HV (GEA60004S13D5): 447 g / 448 g (+/-10), 139 x 47 x 37 mm, 5.0 mm bullet tubes, "
                 "wire gauge 'No', USD 127.99 (buddyrc.com, discountrcparts.com), 131.99 (horizonhobby.com, liquidrc.com, "
                 "back-order). CNHL LiHV 6000 15.2 V 4S 120C hard case EC5: approx. 479 g, 138 x 47 x 37 mm, 10 AWG, "
                 "USD 69.99 (chinahobbyline.com/products/cnhl-lihv-6000mah-15-2v-4s-120c-hv-hard-case-lipo-battery-with-ec5-plug). "
                 "Rejected: Ovonic 50C 6000 Deans 531-532 g (510 +/- 20), 12 AWG, USD 53.99; Zeee 6000 60C soft ~573 g; "
                 "SMC HCL-HP 6000 574 g; HRB 6000 50C 397 g (same listing also says 549 g, case not named: not credible); "
                 "no Tattu 4S 5500-6000 listing found",
           status="UNVERIFIED")
kit.source("SRC-E2-PACK-SEARCH-D173", "Lightest 4S pack of >= 5.7 Ah (E2 D-173 search)", kind="web",
           url="https://horizonhobby.com/product/15.2v-6000mah-4s-130c-shorty-hardcase-lihv-battery-5mm-tubes/GEA60004S13S.html",
           checked="2026-11-14",
           where="web search 2026-11-14 (snippets). Gens Ace Redline 6000 mAh 15.2 V 130C 4S2P shorty hard case HV "
                 "(GEA60004S13S): 410 g +/- 10, 98 x 47 x 46 mm (+/-5; LiquidRC 97.8 x 46.8 x 46.8), 5.0 mm bullet "
                 "tubes; USD 131.99 horizonhobby.com, 131.99 liquidrc.com (back-order), 127.99 discountrcparts.com "
                 "(2 in stock), 129.99 adrenalinercracing.com (sold out); EUR 119.99 gensace.de. No 4S LiPo (4.20 V) "
                 "pack of >= 5.7 Ah under ~470 g with 10 AWG leads was found: Turnigy Graphene 6000 611 g, nano-tech "
                 "6000 623 g, Admiral Pro 6000 4S mass not listed (USD 84), ProTek 6000 HV shorty 425 +/- 10 g "
                 "(archived listing), Lumenier NAV 6000 4S 21700 Li-ion (out of stock, mass not listed)",
           status="UNVERIFIED")
kit.source("SRC-E2-HTRC-C150", "HTRC C150 150 W AC/DC balance charger", kind="web",
           url="https://www.amazon.com/dp/B0H4QLJYHY",
           where="config-study/cards/K09/cost.csv ground line ($56.99, 2026-11-01); 150 W AC rating from the BOM line",
           note="maximum charge current and IR-measurement function not confirmed: read the manual on arrival",
           status="UNVERIFIED")
kit.source("SRC-E2-FAA-PACKSAFE", "FAA PackSafe: lithium batteries", kind="web",
           url="https://www.faa.gov/hazmat/packsafe/lithium-batteries",
           where="spare lithium-ion/polymer batteries <= 100 Wh: carry-on only, no airline approval needed",
           status="UNVERIFIED")
kit.source("SRC-E2-ARDUPILOT-BATT", "ArduPilot battery failsafe parameters", kind="web",
           url="https://ardupilot.org/plane/docs/apms-failsafe-function.html",
           where="BATT_LOW_MAH / BATT_CRT_MAH / BATT_LOW_VOLT / BATT_CRT_VOLT / BATT_FS_VOLTSRC; capacity counter "
                 "assumes a full pack at boot", status="UNVERIFIED")

# ---------------------------------------------------------------- assumptions
A = kit.assumption
A("ASM-E2-ESC-EFF", "ESC efficiency 0.95", "Bus power = motor input power / 0.95",
  basis="K09 sizing.py ESC_EFF; the maker table is probably measured at the supply already, so this is conservative "
        "(REVIEW section 3)", value=0.95, unit="-", status="UNVERIFIED", cites=["SRC-K09-CARD", "SRC-K09-REVIEW"])
A("ASM-E2-AVIONICS-W", "Avionics + servos 6 W", "FC, GPS, RX, airspeed, UBEC loss and two micro servos draw 6 W",
  basis="K09 card 5 W had no servos; +1 W for two micro servos holding trim. F1/F3 replace with the bench current",
  value=6.0, unit="W", status="UNVERIFIED", cites=["SRC-K09-CARD"])
A("ASM-E2-OCV-AVG", "Average open-circuit voltage 3.80 V/cell (LiHV nameplate, D-174)", "Mean OCV between 100 % and 20 % state of charge",
  basis="LiPo OCV curve averages ~3.80 V over 100-20 %; 3.70 V nameplate is used (conservative ~3 %). Rule: the "
        "pack's nameplate cell voltage. For an LiHV pack (4.35 V/cell full) the nameplate is 3.80 V (15.2 V / 4) and "
        "the pack trade uses it per candidate (E2 D-168). D-174: battery.v_nom is 15.2 (Gens Ace Shorty, LiHV), "
        "so the budget chains carry 3.80 V/cell (E2 final re-run 2026-11-14)",
  value=3.80, unit="V", cites=["SRC-OVONIC-4S6500", "SRC-E2-PACK-SEARCH-D173"])
A("ASM-E2-OCV-20", "OCV at 20 % charge 3.73 V/cell", "Resting voltage at the 20 % reserve line",
  basis="typical LiPo rest curve (3.73-3.75 V at 20 %); measured on the first discharge test (T-E2-CAPACITY)",
  value=3.73, unit="V", status="UNVERIFIED")
A("ASM-E2-R-CELL", "Cell-group resistance 3.8 mOhm at 25 degC = the IR acceptance line (D-174)",
  "DC internal resistance per series cell group (2 parallel cells, 4S2P) of the Gens Ace Shorty; the pack is "
  "accepted only at or under this value, so every chain runs on the acceptance line",
  basis="E2 final re-run 2026-11-14: hover heat and cold sag close at 3.8 mOhm per cell group (hot landing 50 degC "
        "line, CL-E2-PACK-T-END). params battery.pack carries the same line. hobby packs measure 2.5-5 mOhm/cell "
        "new; C labels (130C) are not physical. Measure with a load step (T-E2-IR)", value=0.0038, unit="ohm", status="UNVERIFIED")
# ASM-E2-R-EXT (the 6.5 mOhm mirror of P:electrical.r_ext_mohm) is retired in E2-R5: no calculation of any role reads
# it any more (CR-E2-17 closed); every calc reads P:electrical.r_ext_mohm (6.7 mOhm, D-67, CL-F1-R-EXT) directly.
A("ASM-E2-COLD-R", "Cold-pack resistance factor 1.5", "Cell resistance at 10 degC = 1.5 x the 25 degC value",
  basis="LiPo IR roughly doubles from 25 to 0 degC; 10 degC is the bottom of params env.ambient_design_c "
        "(March-April 07:00 at RFS). Keeping packs in the car cabin removes most of it", value=1.5, unit="-",
  status="UNVERIFIED")
A("ASM-E2-HOVER-MARGIN", "Hover wind/control factor 1.10 (pessimistic)",
  "Hover power in 5 m/s wind with station-keeping activity = 1.10 x calm hover power",
  basis="16 deg lean at 5 m/s needs T/cos = 1.04 W; P ~ T^1.5 gives +6 %; +4 % for attitude-control activity. "
        "Replace with the twin's logged hover current", value=1.10, unit="-", status="UNVERIFIED",
  cites=["SRC-K09-REVIEW"])
A("ASM-E2-PROFILE", "Mission profile timings",
  "Ground 180 s at avionics power; climb and descent between 0 and 50 m AGL at 2.0 / 1.0 m/s; forward and back "
  "transitions 10 s at 1.4 / 1.3 x hover power (pessimistic 20 s each); hover hold at 50 m before the transition = "
  "requirements.hover_time_min x 60 - climb - descent - landing hover 30 s - requirements.goaround_hover_s (D-160: "
  "3.0 min total hover-mode time = 180 - 25 - 50 - 30 - 40 = 35 s hold); the landing hover and the go-around are "
  "spent after the cruise and sit in the BATT_LOW landing need (CALC-E2-FAILSAFE); cruise to the reserve line",
  basis="R-TEST-ORDER transition at >= 50 m AGL; ArduPilot Q_PILOT_SPD_UP default 2.5 m/s, land 1 m/s; tailsitter "
        "pitch-over is a few seconds at high throttle (J1 evidence); doubled for the pessimistic case. Hover split per "
        "review/CLOSURE-ROUND-2026-11-14/A2.md s2.1 (D-160); landing hover 30 s includes the last 6 m at 0.3 m/s "
        "(Q_LAND_FINAL_ALT 6). Was a fixed 120 s hold with no go-around (E2 closure 2026-11-14)",
  value={"ground_s": 180, "alt_m": 50, "climb_ms": 2.0, "descent_ms": 1.0, "landing_hover_s": 30,
         "trans_s": [10, 20], "trans_fwd_factor": 1.4, "trans_back_factor": 1.3}, unit="-", status="PROPOSED")
A("ASM-E2-CRUISE-AERO", "Cruise mass scaling, circuit factor and independent cross-check model",
  "The cruise power LEVEL is B1's as-designed simulation (CL-B1V-CRUISE-P-GATE at the 2.6 kg gate; "
  "CL-B1V-CRUISE-P-PESS at A3's predicted mass CL-A3-MASS-PREDICTED; level flight, avionics included). This "
  "E2 drag model (CD0 0.0593, x1.3 pessimistic, e from params, eta_prop 0.47 / 0.35, eta_motor 0.72, trim 1.05) "
  "only scales B1's power from B1's reference mass to the budget mass (the pessimistic value up to the gate), and "
  "is reported as a cross-check. The turning (circuit) factor 1.05 multiplies B1's level-flight power",
  basis="K09 sizing.json CD0 build-up; REVIEW section 4 corrected efficiencies; circuits inside one RFS sub-field "
        "spend about half the time in 30 deg banks (induced drag x1.33). CR-E2-08: B1 owns cruise power; E2 "
        "follows B1's claims through the proof chain (re-run this script after every B1 re-run)",
  value={"cd0": 0.0593, "cd0_pess": 1.3, "eta_prop": [0.47, 0.35], "eta_motor": 0.72, "trim": 1.05,
         "circuit": 1.05}, unit="-", status="UNVERIFIED", cites=["SRC-K09-CARD", "SRC-K09-REVIEW"])
A("ASM-E2-PACK-CANDIDATES", "4S pack candidates [name, Ah, listed kg, mass tolerance kg, continuous A, lead AWG, "
  "nameplate V/cell]",
  "Row 0 is the named flight pack (D-174: Gens Ace Shorty; was the Ovonic of D-64); the others are real listed 4S packs, for the trade only",
  basis="Listed masses: SRC-E2-OVONIC-120C-EC5, SRC-E2-TATTU-6750, SRC-E2-PACK-SEARCH-1114. Continuous A = realistic "
        "cell limit (~30C for 120-130C labels, 25C for the Tattu), not the label C. Tolerance as listed; Muchmore 10 g "
        "EST (not stated). Ovonic 50C lead gauge not stated: 12 AWG assumed (EST, Deans plug). E2 closure 2026-11-14 "
        "removed the rejected options: Li-ion 4S2P 9 Ah (rejected D-154), Ovonic 130C XT60 680 g 12 AWG (not bought, "
        "D-64), Admiral 4S 4000 (no 4000 fallback, D-12), and the unnamed 5000 / 8000 EST classes (no listing). "
        "D-163 rows (E2 2026-11-14, SRC-E2-PACK-SEARCH-D163): Gens Ace 448 g +/- 10 listed + 4 g EST for two 0.10 m "
        "10 AWG pigtails with 5 mm bullets (the pack has bullet tubes, no leads); CNHL approx. 479 g, tolerance not "
        "stated (10 g EST). Both are LiHV (4.35 V/cell full): the 6.0 Ah is rated at the HV charge. Continuous 180 A "
        "= 30C EST. D-168 (E2 2026-11-14): CNHL LiHV 6000 re-read on chinahobbyline.com.au: 479 +/- 5 g, "
        "138 x 47 x 37 mm, 12 AWG (12#), EC5, out of stock -> fails the 10 AWG rule; CNHL Lightning 6700 4S LiHV EC5 "
        "about 530 g, 10 AWG, 149 x 51 x 35 mm (chinahobbyline.com, ja page), tolerance not stated (10 g EST). Last "
        "column = the pack's nameplate cell voltage, used as its average OCV by the ASM-E2-OCV-AVG rule (3.70 LiPo, "
        "3.80 LiHV: 15.2 V / 4 on the listings)",
  value=[["Gens Ace Redline 4S 6000 130C HV Shorty (GEA60004S13S), 5 mm tubes + own 10 AWG pigtails (named, D-173/D-174)",
          6.0, 0.414, 0.010, 180.0, 10, 3.80],
         ["Ovonic 4S 6500 120C hard case EC5 (superseded D-64 pack)", 6.5, 0.551, 0.005, 195.0, 10, 3.70],
         ["Tattu 4S 6750 25C XT90 (params fallback)", 6.75, 0.605, 0.010, 168.75, 10, 3.70],
         ["Muchmore 4S 6500 130C XT90", 6.5, 0.545, 0.010, 195.0, 10, 3.70],
         ["Ovonic 4S 6500 50C hard case Deans", 6.5, 0.522, 0.020, 195.0, 12, 3.70],
         ["Gens Ace Redline 4S 6000 130C HV hard case, 5 mm tubes + own 10 AWG pigtails (D-163 candidate)", 6.0,
          0.452, 0.010, 180.0, 10, 3.80],
         ["CNHL LiHV 4S 6000 120C hard case EC5 (D-163 candidate; 12 AWG per D-168 re-read)", 6.0, 0.479, 0.005,
          180.0, 12, 3.80],
         ["CNHL Lightning 4S 6700 LiHV EC5", 6.7, 0.530, 0.010, 201.0, 10, 3.80],
         ["CNHL Racing 4S 6000 130C LiHV Shorty hard case, 5 mm sockets + own 10 AWG pigtails (D-180 cost re-check; "
          "415.5 g listed + 4 g pigtails)", 6.0, 0.4195, 0.010, 180.0, 10, 3.80],
         ],
  unit="-", status="UNVERIFIED",
  cites=["SRC-E2-OVONIC-120C-EC5", "SRC-E2-TATTU-6750", "SRC-E2-PACK-SEARCH-1114", "SRC-E2-PACK-SEARCH-D163",
         "SRC-E2-PACK-SEARCH-D173"])
A("ASM-E2-PACK-SKU", "Named flight-pack SKU (D-174): Gens Ace Redline 4S 6000 HV Shorty, listed data",
  "Gens Ace Redline 4S 6000 mAh 15.2 V 130C HV Shorty hard case, 4S2P (GEA60004S13S): 0.410 kg listed +/- 0.010 + "
  "0.004 kg EST for two 0.10 m 10 AWG pigtails with 5 mm bullets = 0.414 kg (params battery.mass_kg), "
  "98 x 47 x 46 mm +/- 3 mm (params battery.size_m), own 10 AWG pigtails to the AS150U, JST-XH balance lead; "
  "LiHV, charge 4.35 V/cell; IR acceptance <= 3.8 mOhm per cell group",
  basis="E2.md D-173 pack section (search snippets 2026-11-14, UNVERIFIED); params battery.pack, battery.mass_kg, "
        "battery.size_m (A1 D-174). Weight, size and lead gauge are confirmed on arrival (T-E2-WEIGH). The 130C "
        "label is not a physical continuous rating; the real limit is the cell IR (ASM-E2-R-CELL, T-E2-IR). "
        "Superseded: Ovonic 4S 6500 120C EC5 551 +/- 5 g, 135 x 46 x 49 mm (D-64)",
  value={"mass_kg": 0.414, "mass_tol_kg": 0.010, "size_m": [0.098, 0.047, 0.046], "size_tol_m": 0.003,
         "lead_awg": 10}, unit="-", status="UNVERIFIED", cites=["SRC-E2-PACK-SEARCH-D173"])
A("ASM-E2-PACK-LIMITS", "Pack acceptance limits other than mass (D-15, CR-F1-14)",
  "Body fits the D2 bay 0.160 x 0.052 x 0.053 m (D-15); discharge leads 10 AWG or heavier (AWG number <= 10, "
  "CR-F1-14, CL-F1-PACKLEAD12-RISE). The mass line is not set here: it is A3's CL-A3-PACK-ACCEPT (D-154; "
  "A1's CL-A1-PACK-ACCEPT carries the same number), read live",
  basis="params/CHANGE-LOG.md D-15, D-64; F1 pack-lead rise rule electrical.pack_lead_rise_max_c 20 K "
        "(12 AWG 28.4 K). The D-58 601 g line is retired (D-64)",
  value={"bay_m": [0.160, 0.052, 0.053], "awg_max": 10}, unit="-", status="PROPOSED")
A("ASM-E2-TESTDAY", "Test-day window and turnaround",
  "Flying window 180 min (07:00-10:00 flight card); 20 min on the ground between sorties (log check, feet and "
  "prop inspection, pack swap, re-brief); one fully charged pack per sortie; no charging at the field",
  basis="R-SITE flight card; CONFIGURATION.md morning-only; RFS mains power not confirmed, and P21 forbids car "
        "charging", value={"window_min": 180, "turnaround_min": 20}, unit="-", status="PROPOSED")
kit.source("SRC-E2-B2-TURB", "B2 closure report: lower-surface turbulator power cost (D-168)", kind="repo",
           url="review/CLOSURE-ROUND-2026-11-14/B2.md",
           where="B2C-3: dcd_wing +0.0040 (EST, upper bound) -> +0.26 N, +14.0 W electrical at 17 m/s and 2.64 kg "
                 "(+5.3 % of 263 W); params wing.turbulator (D-168) carries the geometry but no power key")
A("ASM-E2-TURB-W", "Turbulator cruise power adder 14.0 W (D-168)",
  "The lower-surface zigzag trip (wing.turbulator) adds 14.0 W electrical at 17 m/s on top of E1's untripped cruise "
  "point CL-E1-CRUISE-P-55-V17",
  basis="B2.md B2C-3 (XFOIL, upper bound). Added to the E1-based chains (CALC-E2-BUDGET-V17, -240, -PACK-TRADE) and "
        "scaled with them into the pessimistic case. Remove once E1 / B1 carry the trip in their own cruise power",
  value=14.0, unit="W", status="UNVERIFIED", cites=["SRC-E2-B2-TURB"])
A("ASM-E2-CHARGE", "Charge profile", "CC at min(1C, charger W / 16.8 V) to ~85 % state of charge, then CV for 20 min",
  basis="standard LiPo CC-CV; 1C is the maker's normal charge rate for hobby packs", value={"cc_end_soc": 0.85,
  "cv_min": 20, "c_max": 1.0}, unit="-", status="PROPOSED")


# ---------------------------------------------------------------- helpers (pure)
def pack_current(p_w, voc, r):
    """Pack current for bus power p_w with a Thevenin source (voc, r)."""
    disc = voc * voc - 4 * r * p_w
    if disc < 0:
        raise ValueError("power beyond the pack's maximum transfer")
    return (voc - math.sqrt(disc)) / (2 * r)


def table_power(table, thrust_g):
    """Motor input W per motor; linear through zero below the first row (conservative, REVIEW section 3)."""
    rows = sorted(table)
    if thrust_g <= rows[0][0]:
        return rows[0][1] * thrust_g / rows[0][0]
    for (g0, w0), (g1, w1) in zip(rows, rows[1:]):
        if thrust_g <= g1:
            return w0 + (w1 - w0) * (thrust_g - g0) / (g1 - g0)
    return rows[-1][1]


def hover_bus_w(m_kg, n, table, download, esc, avn):
    return n * table_power(table, m_kg * 1000 * download / n) / esc + avn


def climb_factor(m_kg, g, rho, n, D, vc):
    """P_climb / P_hover from momentum theory: vc/(2 vh) + sqrt((vc/(2 vh))^2 + 1)."""
    vh = math.sqrt(m_kg * g / n / (2 * rho * math.pi * D * D / 4))
    x = vc / (2 * vh)
    return x + math.sqrt(x * x + 1)


def cruise_bus_w(m_kg, g, rho, S, b, e, V, cd0, eta_p, eta_m, trim, circuit, avn):
    W = m_kg * g
    cl = 2 * W / (rho * V * V * S)
    cd = cd0 + cl * cl / (math.pi * b * b / S * e)
    D = 0.5 * rho * V * V * S * cd
    return D * V * trim * circuit / (eta_p * eta_m) + avn


def hover_hold_s(prof, t_hover_min, goaround_s):
    """D-160: hover_time_min is the TOTAL hover-mode time; the hold before the transition is what is left after
    climb, descent, landing hover and the go-around (the last two sit in the BATT_LOW landing need)."""
    alt = prof["alt_m"]
    hold = t_hover_min * 60 - alt / prof["climb_ms"] - alt / prof["descent_ms"] - prof["landing_hover_s"] - goaround_s
    if hold < 0:
        raise ValueError(f"hover_time_min {t_hover_min} min leaves a negative hold ({hold:.0f} s)")
    return hold


PHASE_KEYS = {"ground, armed checks": "ground", "climb 0-50 m": "climb", "hover (mission)": "hover",
              "transition forward": "trans_fwd", "back-transition": "trans_back", "descent 50-0 m": "descent",
              "cruise": "cruise"}


def budget(m_kg, pess, *, n, table, download, esc, avn, g, rho, D, S, b, e, V, cells, ah, ocv, r_cell, r_ext,
           cold, hmargin, prof, aero, cap_frac, reserve, pc_b, pc_p, m_ref, m_ref_p, t_hover, goaround, p_hov,
           p_scale=1.0):
    """Phase table [name, s, W, A, Ah] and the cruise time to the reserve line. r_ext in mOhm (params unit)."""
    k = 1 if pess else 0
    r_ext = r_ext / 1000.0
    r = cells * r_cell * (cold if pess else 1.0) + r_ext
    voc = cells * ocv
    # E2 D-173: E1 owns hover power (performance.hover_power_w at the gate, like B1 owns cruise). The maker table
    # (still the X3108S / 11x4.7 rows) only scales it with mass; cal = E1 hover W / table hover W at the gate
    cal = p_hov / hover_bus_w(m_ref, n, table, download, esc, avn)
    ph = hover_bus_w(m_kg, n, table, download, esc, avn) * cal * (hmargin if pess else 1.0)
    alt = prof["alt_m"]
    hold = hover_hold_s(prof, t_hover, goaround)
    phases = [
        ("ground, armed checks", prof["ground_s"], avn),
        ("climb 0-50 m", alt / prof["climb_ms"], ph * climb_factor(m_kg, g, rho, n, D, prof["climb_ms"])),
        ("hover (mission)", hold, ph),
        ("transition forward", prof["trans_s"][k], ph * prof["trans_fwd_factor"]),
        ("back-transition", prof["trans_s"][k], ph * prof["trans_back_factor"]),
        ("descent 50-0 m", alt / prof["descent_ms"], ph),
    ]
    rows, ah_fixed = [], 0.0
    for name, t, p in phases:
        i = pack_current(p, voc, r)
        rows.append([name, t, p, i, i * t / 3600])
        ah_fixed += i * t / 3600
    cd0 = aero["cd0"] * (aero["cd0_pess"] if pess else 1.0)

    def e2_model(mm):                               # level flight, no circuit factor (B1's basis)
        return cruise_bus_w(mm, g, rho, S, b, e, V, cd0, aero["eta_prop"][k], aero["eta_motor"], aero["trim"],
                            1.0, avn)
    # B1's level-flight power at its reference mass (base: gate; pessimistic: A3 predicted), scaled to this mass by
    # the E2 drag model of the same case, x circuit factor
    ref = m_ref_p if pess else m_ref
    pc = (pc_p if pess else pc_b) * p_scale * aero["circuit"] * e2_model(m_kg) / e2_model(ref)
    pc_e2 = e2_model(m_kg) * aero["circuit"]
    ic = pack_current(pc, voc, r)
    ah_avail = ah * (cap_frac if pess else 1.0) - ah * reserve      # reserve = 20 % of nameplate, never planned in
    ah_cruise = ah_avail - ah_fixed
    rows.append(["cruise", ah_cruise / ic * 3600, pc, ic, ah_cruise])
    ih = pack_current(ph, voc, r)
    out = {"phases": rows, "cruise_min": ah_cruise / ic * 60, "hover_cal": cal, "ah_fixed": ah_fixed, "ah_avail": ah_avail,
           "cruise_w_b1_level": (pc_p if pess else pc_b) * p_scale, "mass_scale": e2_model(m_kg) / e2_model(ref),
           "hover_w": ph, "hover_a": ih, "cruise_w": pc, "cruise_a": ic, "cruise_w_e2_model": pc_e2,
           "hover_only_min": (ah_avail - rows[0][4]) / ih * 60,
           "flight_min": (sum(x[1] for x in rows) - prof["ground_s"]) / 60, "r_pack": r}
    for name, t, _, i, _ in rows:                   # flat per-phase outputs, so each can be a claim (CR-F1-04)
        out[f"i_{PHASE_KEYS[name]}_a"] = i
        out[f"t_{PHASE_KEYS[name]}_s"] = t
    out["i_max_phase_a"] = max(x[3] for x in rows)
    return out


COMMON = {"n": P + "propulsion.n_motors", "table": P + "propulsion.thrust_table_g_w",
          "download": P + "propulsion.download_factor", "esc": "ASM-E2-ESC-EFF", "avn": "ASM-E2-AVIONICS-W",
          "g": P + "env.g_ms2", "rho": P + "env.rho_kgm3", "D": P + "propulsion.prop_diameter_m",
          "S": "CL-A1-WING-AREA", "b": P + "wing.span_m", "e": P + "wing.oswald_e", "V": P + "performance.cruise_ms",
          "cells": P + "battery.cells_s", "ah": P + "battery.capacity_ah", "ocv": "ASM-E2-OCV-AVG",
          "r_cell": "ASM-E2-R-CELL", "r_ext": P + "electrical.r_ext_mohm", "cold": "ASM-E2-COLD-R",
          "hmargin": "ASM-E2-HOVER-MARGIN", "prof": "ASM-E2-PROFILE", "aero": "ASM-E2-CRUISE-AERO",
          "cap_frac": P + "requirements.pack_capacity_min_frac", "reserve": P + "requirements.energy_reserve_frac",
          "pc_b": "CL-B1V-CRUISE-P-GATE", "pc_p": "CL-B1V-CRUISE-P-PESS", "m_ref": P + "requirements.mtow_gate_kg",
          "m_ref_p": "CL-A3-MASS-PREDICTED", "t_hover": P + "requirements.hover_time_min",
          "goaround": P + "requirements.goaround_hover_s", "p_hov": P + "performance.hover_power_w"}
CU = {"g": "m/s2", "rho": "kg/m3", "D": "m", "S": "m2", "b": "m", "V": "m/s", "ah": "Ah", "ocv": "V",
      "r_cell": "ohm", "r_ext": "mOhm", "pc_b": "W", "pc_p": "W", "m_ref": "kg", "m_ref_p": "kg",
      "t_hover": "min", "goaround": "s", "p_hov": "W"}
ASSUMES = ["ASM-E2-ESC-EFF", "ASM-E2-AVIONICS-W", "ASM-E2-OCV-AVG", "ASM-E2-R-CELL",
           "ASM-E2-PROFILE", "ASM-E2-CRUISE-AERO"]


# ---------------------------------------------------------------- calculations
@kit.calc("CALC-E2-BUDGET-BASE", title="Energy budget per phase, base case (sized mass)", assumes=ASSUMES,
          equation="I = (Voc - sqrt(Voc^2 - 4 R P)) / (2 R) per phase ; Ah = I t ; "
                   "P_cruise = P_B1(gate) x circuit x P_E2(m) / P_E2(gate) ; "
                   "t_cruise = (C - 0.2 C - sum Ah_fixed) / I_cruise",
          inputs={"m": "CL-A1-MASS-SIZED", "p17": "CL-E1-CRUISE-P-55-V17", "turb": "ASM-E2-TURB-W", **COMMON},
          units={"m": "kg", "p17": "W", "turb": "W", **CU})
def budget_base(m, p17, turb, **kw):
    # E2 final re-run 2026-11-14: B1's level power (CL-B1V-CRUISE-P-GATE) is still the pre-D-173 propeller; the
    # cruise level is E1's X2814 / 11x8E point + avionics + turbulator, carried as in CALC-E2-BUDGET-V17
    r = budget(m, False, p_scale=(p17 + kw["avn"] + turb) / kw["pc_b"], **kw)
    return {k: v for k, v in r.items()}


@kit.calc("CALC-E2-BUDGET-PESS", title="Energy budget per phase, pessimistic (2.6 kg gate)",
          assumes=ASSUMES + ["ASM-E2-COLD-R", "ASM-E2-HOVER-MARGIN"],
          equation="as base (cruise level x k, k = (E1 17 m/s point + avionics + turbulator) / B1 gate, D-174), with m = gate, C x 0.92, R x 1.5 (10 degC), P_hover x 1.10, P_cruise = B1 as-designed "
                   "pessimistic (CL-B1V-CRUISE-P-PESS at A3 predicted mass) x P_E2,pess(gate) / P_E2,pess(m_pred) "
                   "x circuit, 20 s transitions",
          inputs={"m": P + "requirements.mtow_gate_kg", "p17": "CL-E1-CRUISE-P-55-V17", "turb": "ASM-E2-TURB-W",
                  **COMMON}, units={"m": "kg", "p17": "W", "turb": "W", **CU})
def budget_pess(m, p17, turb, **kw):
    return budget(m, True, p_scale=(p17 + kw["avn"] + turb) / kw["pc_b"], **kw)


@kit.calc("CALC-E2-SAG", title="Bus voltage at the 100 A limiter vs pack state; bracket on the thrust factor",
          equation="V_bus = Voc - R I_lim (limiter binds when I_unlim(V) = n I_148 (V/14.8)^2 > I_lim) ; "
                   "thrust factor worst/fresh bracketed by (V_w/V_f) (thrust prop. to power) and (V_w/V_f)^(2/3) "
                   "(ideal rotor at fixed current) ; old rule (V/V_tab)^2 kept for the record (unlimited motor) ; "
                   "bracket margin = min(f_E1 - lower, upper - f_E1)",
          inputs={"cells": P + "battery.cells_s", "i_lim": P + "performance.full_throttle_current_a",
                  "i148": "CL-E1-IMAX-148-55", "n": P + "propulsion.n_motors", "ocv20": "ASM-E2-OCV-20",
                  "r_cell": "ASM-E2-R-CELL", "r_ext": P + "electrical.r_ext_mohm", "cold": "ASM-E2-COLD-R",
                  "ah": P + "battery.capacity_ah", "f_e1": "CL-E1-SAG-FACTOR"},
          units={"i_lim": "A", "i148": "A", "ocv20": "V", "r_cell": "ohm", "r_ext": "mOhm", "ah": "Ah"},
          assumes=["ASM-E2-OCV-20", "ASM-E2-R-CELL", "ASM-E2-COLD-R"])
def sag(cells, i_lim, i148, n, ocv20, r_cell, r_ext, cold, ah, f_e1):
    r_ext = r_ext / 1000.0
    cases = {"full_warm": (cells * 4.35, cells * r_cell + r_ext),
             "res20_warm": (cells * ocv20, cells * r_cell + r_ext),
             "res20_cold": (cells * ocv20, cells * r_cell * cold + r_ext)}
    out = {}
    for k, (voc, r) in cases.items():
        v = voc - r * i_lim
        out[f"v_{k}"] = v
        out[f"r_{k}_ohm"] = r
        out[f"i_unlim_{k}"] = n * i148 * (v / 14.8) ** 2      # four motors at full duty; prop load I ~ V^2
        out[f"limiter_binds_{k}"] = 1.0 if out[f"i_unlim_{k}"] > i_lim else 0.0
    ratio = out["v_res20_cold"] / out["v_full_warm"]
    out["f_lower_thrust_prop_v"] = ratio
    out["f_upper_ideal_rotor"] = ratio ** (2.0 / 3.0)
    out["f_old_v2_rule"] = (out["v_res20_cold"] / 14.8) ** 2   # D-06 / E2-R2 rule: double-counts under the limiter
    out["f_e1"] = f_e1
    out["e1_bracket_margin"] = min(f_e1 - ratio, ratio ** (2.0 / 3.0) - f_e1)
    out["e1_exponent"] = math.log(f_e1) / math.log(ratio)
    out["c_peak"] = i_lim / ah
    out["sag_v_per_cell_worst"] = (cells * ocv20 - out["v_res20_cold"]) / cells
    out["v_cell_worst_loaded"] = out["v_res20_cold"] / cells
    return out


A("ASM-E2-LIHV-VOLT", "F4 LiHV voltage backups [BATT_LOW_VOLT, BATT_CRT_VOLT, BATT_ARM_VOLT] V (F4 D-174)",
  "14.4 / 14.0 / 17.0 V = 3.60 / 3.50 / 4.25 V per cell, sag-compensated (BATT_FS_VOLTSRC 1); full charge 4.35 V/cell",
  basis="review/CLOSURE-ROUND-2026-11-14/F4.md section D-174 table (F4 EST, asked E2 to confirm: CR-F4-59). The 20 % OCV "
        "is ASM-E2-OCV-20; a LiHV cell rests at or above the LiPo value at the same charge, so using 3.73 V is the "
        "conservative end for the LOW / CRT backups",
  value=[14.4, 14.0, 17.0], unit="V", status="UNVERIFIED", cites=["SRC-E2-ARDUPILOT-BATT"])


@kit.calc("CALC-E2-LIHV-BACKUP", title="F4 voltage backups against the mAh failsafes (they must fire later) and the arming line "
          "against full charge",
          equation="margin_low = OCV_20 - V_low / cells (the voltage backup sits below the resting voltage at the 20 % "
                   "reserve, so the mAh trigger fires first) ; margin_crt = V_low / cells - V_crt / cells ; "
                   "margin_arm = V_full_cell - V_arm / cells (a fresh 4.35 V/cell pack passes the arming check)",
          inputs={"v": "ASM-E2-LIHV-VOLT", "cells": P + "battery.cells_s", "ocv20": "ASM-E2-OCV-20"},
          units={"ocv20": "V"}, assumes=["ASM-E2-LIHV-VOLT", "ASM-E2-OCV-20"])
def lihv_backup(v, cells, ocv20):
    low, crt, arm = v
    return {"low_cell_v": low / cells, "crt_cell_v": crt / cells, "arm_cell_v": arm / cells,
            "margin_low_v": ocv20 - low / cells, "margin_crt_v": (low - crt) / cells, "margin_arm_v": 4.35 - arm / cells}


@kit.calc("CALC-E2-HEAT", title="Pack self-heating over the pessimistic mission, cold and hot mornings",
          equation="Q = sum(I^2 R t) over phases ; dT = Q / (m c) (adiabatic, c = 1000 J/kg K) ; "
                   "T_end = T_amb + dT ; cold: 10 degC, R x 1.5 ; hot: 30 degC, R x 1.0",
          inputs={"b": "CL-E2-BUDGET-PESS-TABLE", "r_cell": "ASM-E2-R-CELL", "cells": P + "battery.cells_s",
                  "cold": "ASM-E2-COLD-R", "m": P + "battery.mass_kg", "amb": P + "env.ambient_design_c"},
          units={"r_cell": "ohm", "m": "kg", "amb": "degC"}, assumes=["ASM-E2-R-CELL", "ASM-E2-COLD-R"])
def heat(b, r_cell, cells, cold, m, amb):
    out = {}
    for case, t_amb, f in (("cold", amb[0], cold), ("hot", amb[1], 1.0)):
        r = cells * r_cell * f                     # cell resistance only (leads heat the harness, not the pack)
        q = sum(row[3] ** 2 * r * row[1] for row in b)
        out[f"dT_{case}_k"] = q / (m * 1000.0)
        out[f"t_end_{case}_c"] = t_amb + q / (m * 1000.0)
        out[f"p_hover_{case}_w"] = b[2][3] ** 2 * r
    out["t_end_max_c"] = max(out["t_end_cold_c"], out["t_end_hot_c"])
    return out


@kit.calc("CALC-E2-PACK-TRADE", title="Pack trade: candidates against the pack acceptance line, R-MISSION as flown "
          "(cruise at 17 m/s to BATT_LOW) and current",
          equation="P_cruise = performance.cruise_power_w + ASM-E2-TURB-W (D-173) ; "
                   "pass = (m_listed + tol <= CL-A3-PACK-ACCEPT) AND t_to_low(17 m/s, pessimistic, gate mass, this pack's "
                   "Ah and BATT_LOW) >= cruise_time_min AND land_left >= BATT_CRT AND I_cont >= I_limiter AND AWG <= 10 ; "
                   "BATT_LOW and t_to_low as CALC-E2-FAILSAFE / -BUDGET-V17 ; named_pass_ah = Ah of row 0 if it passes "
                   "else 0",
          inputs={"cands": "ASM-E2-PACK-CANDIDATES", "accept_g": "CL-A3-PACK-ACCEPT", "m_p": P + "requirements.mtow_gate_kg",
                  "t_req": P + "requirements.cruise_time_min", "i_full": P + "performance.full_throttle_current_a",
                  "p_par": P + "performance.cruise_power_w", "lim": "ASM-E2-PACK-LIMITS", "turb": "ASM-E2-TURB-W",
                  **{k: v for k, v in COMMON.items() if k != "ah"}},
          units={"accept_g": "g", "m_p": "kg", "t_req": "min", "i_full": "A", "p_par": "W", "turb": "W",
                 **{k: v for k, v in CU.items() if k != "ah"}},
          assumes=["ASM-E2-PACK-CANDIDATES", "ASM-E2-PACK-LIMITS", "ASM-E2-COLD-R", "ASM-E2-HOVER-MARGIN"] + ASSUMES)
def pack_trade(cands, accept_g, m_p, t_req, i_full, p_par, lim, turb, **kw):
    """E2 closure 2026-11-14: was 'largest candidate passing the A1 sized mass and the 20 % line' (the sized mass
    2.64 kg is above the 2.6 kg gate, so nothing could pass). Now each pack is judged as flown: the pessimistic
    aircraft is at the gate whatever the pack weighs, the pack itself must pass the acceptance line of record."""
    k = (p_par + turb) / kw["pc_b"]       # E2 D-173: params cruise power of record (avionics incl.) + turbulator
    rows, best = [], None
    for name, ah, kg, tol, icont, awg, v_nom_cell in cands:
        kc = dict(kw, ocv=v_nom_cell)      # ASM-E2-OCV-AVG rule: the pack's own nameplate cell voltage (LiHV 3.80)
        pess = budget(m_p, True, ah=ah, p_scale=k, **kc)
        fs = failsafe_rows(pess["phases"], ah, kw["reserve"], kw["cap_frac"], kw["prof"]["landing_hover_s"],
                           kw["goaround"])
        crit = {"mass": kg + tol <= accept_g / 1000 + 1e-9, "mission": fs["cruise_to_low_min"] >= t_req,
                "landing": fs["land_left_mah"] >= fs["crt_mah"], "current": icont >= i_full,
                "lead": awg <= lim["awg_max"]}
        ok = all(crit.values())
        rows.append([name, ah, round((kg + tol) * 1000, 1), fs["low_mah"], round(fs["cruise_to_low_min"], 2),
                     round(fs["land_left_mah"]), icont, awg, ",".join(c for c, v in crit.items() if not v) or "PASS"])
        if ok and (best is None or ah > best[1]):
            best = rows[-1]
    return {"table": rows, "named_pass_ah": cands[0][1] if rows[0][-1] == "PASS" else 0.0,
            "named_fails_on": rows[0][-1], "accept_g": accept_g,
            "named_accept_needed_g": (cands[0][2] + cands[0][3]) * 1000,
            "largest_passing_ah": best[1] if best else 0.0, "largest_passing": best[0] if best else "none"}


FAILSAFE_EQ = ("CRT_MAH = reserve C ; LOW_MAH = CRT + Ah(back-transition + descent + 60 s return cruise + 30 s "
               "landing hover + goaround_hover_s go-around at hover current, D-160), pessimistic currents, rounded up "
               "to 100 mAh ; the FC counts mAh used against "
               "BATT_CAPACITY = the pack's measured capacity (D-154; pessimistic pack = cap_frac x C), so BATT_LOW "
               "fires after (cap_frac C - LOW_MAH) used ; t_to_low = (cap_frac C - LOW_MAH - Ah before cruise) / "
               "I_cruise ; charge at touchdown after a QRTL from the far point = LOW_MAH - need")


@kit.calc("CALC-E2-FAILSAFE", title="Battery failsafe thresholds for the flight controller",
          equation=FAILSAFE_EQ,
          inputs={"b": "CL-E2-BUDGET-PESS-TABLE", "ah": P + "battery.capacity_ah",
                  "reserve": P + "requirements.energy_reserve_frac",
                  "cap_frac": P + "requirements.pack_capacity_min_frac", "prof": "ASM-E2-PROFILE",
                  "goaround": P + "requirements.goaround_hover_s"}, units={"ah": "Ah", "goaround": "s"},
          assumes=["ASM-E2-PROFILE"])
def failsafe(b, ah, reserve, cap_frac, prof, goaround):
    return failsafe_rows(b, ah, reserve, cap_frac, prof["landing_hover_s"], goaround)


def failsafe_rows(b, ah, reserve, cap_frac, land_hover_s, goaround_s):
    """D-154: the counter base is the pack's real capacity (BATT_CAPACITY = measured T-E2-CAPACITY), not the
    6 500 mAh nameplate. Counting from nameplate on a 92 % pack spent the reserve (12.3 % at touchdown)."""
    rows = {r[0]: r for r in b}
    need = rows["back-transition"][4] + rows["descent 50-0 m"][4] + rows["cruise"][3] * 60 / 3600 \
        + rows["hover (mission)"][3] * (land_hover_s + goaround_s) / 3600     # D-160: go-around protected
    crt = math.ceil(ah * reserve * 10 - 1e-9) * 100     # -1e-9: 6.0 x 0.2 x 10 = 12.000000000000002 rounded to 1300 (E2 D-168)
    # E2 D-163 (2026-11-14): LOW is built on the ROUNDED CRT, so LOW - need >= CRT always holds. Rounding the reserve
    # and the sum separately let CRT round up past LOW - need (6.0 / 6.1 Ah packs landed 70 mAh under CRT)
    low = math.ceil((crt / 1000 + need) * 10 - 1e-9) * 100
    before = sum(rows[k][4] for k in ("ground, armed checks", "climb 0-50 m", "hover (mission)", "transition forward"))
    counter = ah * cap_frac                                            # BATT_CAPACITY = measured capacity, Ah
    to_low = (counter - low / 1000 - before) / rows["cruise"][3] * 60
    left = low / 1000 - need                                           # true Ah at touchdown after far-point QRTL
    return {"crt_mah": crt, "low_mah": low, "land_need_mah": need * 1000, "cruise_to_low_min": to_low,
            "goaround_mah": rows["hover (mission)"][3] * goaround_s / 3.6,
            "counter_mah": counter * 1000, "land_left_mah": left * 1000}


@kit.calc("CALC-E2-TESTDAY", title="Sorties per test day and charge time",
          equation="sorties_window = floor(window / (t_flight + t_turn)) ; sorties = min(packs, window) (D-12: 2) ; "
                   "window used = sorties t_flight + (sorties - 1) t_turn ; "
                   "t_charge = (0.85 - 0.20) C / I_cc + t_cv ; I_cc = min(1C, P_chg / 16.8 V)",
          inputs={"b": "CL-E2-BUDGET-BASE-TABLE", "td": "ASM-E2-TESTDAY", "n_packs": P + "battery.n_packs",
                  "ah": P + "battery.capacity_ah", "cells": P + "battery.cells_s", "chg": "ASM-E2-CHARGE",
                  "p_chg": "ASM-E2-CHARGER-W", "reserve": P + "requirements.energy_reserve_frac"},
          units={"ah": "Ah", "p_chg": "W"}, assumes=["ASM-E2-TESTDAY", "ASM-E2-CHARGE"])
def testday(b, td, n_packs, ah, cells, chg, p_chg, reserve):
    t_flight = sum(r[1] for r in b) / 60
    window = math.floor(td["window_min"] / (t_flight + td["turnaround_min"]))
    i_cc = min(chg["c_max"] * ah, p_chg / (cells * 4.2))
    t_chg = (chg["cc_end_soc"] - reserve) * ah / i_cc * 60 + chg["cv_min"]
    planned = min(n_packs, window)
    return {"t_sortie_min": t_flight, "sorties_window": window, "sorties_current_packs": planned,
            "window_used_min": planned * t_flight + (planned - 1) * td["turnaround_min"],
            "packs_to_fill_window": window, "charge_min_per_pack": t_chg,
            "charge_h_current_packs": n_packs * t_chg / 60, "charge_h_4_packs": 4 * t_chg / 60,
            "i_cc_a": i_cc}


A("ASM-E2-CHARGER-W", "Charger output 150 W", "HTRC C150 delivers 150 W into one pack on AC",
  basis="BOM line 'HTRC C150 charger 150 W AC'; output vs input rating to confirm from the manual",
  value=150.0, unit="W", status="UNVERIFIED", cites=["SRC-E2-HTRC-C150"])


@kit.calc("CALC-E2-SKU-CHECK", title="Named pack SKU against the pack pass line of record (CL-A3-PACK-ACCEPT, D-154), the bay and the lead rule",
          equation="accept = CL-A3-PACK-ACCEPT / 1000 (PACK_ACCEPT_KG, read live) ; m_worst = m_listed + tol ; "
                   "mass margin = accept - m_worst ; bay clearance = min_i(bay_i - (size_i + tol)) (pack length along "
                   "the bay) ; lead AWG number <= awg_max",
          inputs={"sku": "ASM-E2-PACK-SKU", "lim": "ASM-E2-PACK-LIMITS", "accept_g": "CL-A3-PACK-ACCEPT"},
          units={"accept_g": "g"}, assumes=["ASM-E2-PACK-SKU", "ASM-E2-PACK-LIMITS"])
def sku_check(sku, lim, accept_g):
    accept = accept_g / 1000.0
    worst = sku["mass_kg"] + sku["mass_tol_kg"]
    clear = [b - (s + sku["size_tol_m"]) for b, s in zip(lim["bay_m"], sku["size_m"])]
    return {"accept_kg": accept, "mass_worst_kg": worst, "mass_margin_kg": accept - worst,
            "bay_clear_min_m": min(clear),
            "bay_clear_m": clear, "lead_awg": sku["lead_awg"], "awg_max": lim["awg_max"]}


@kit.calc("CALC-E2-BUDGET-240", title="Budget sensitivity at the params cruise power (performance.cruise_power_w: 293 W at 17 m/s since D-145; 253 W D-97, 240 W D-49)",
          assumes=ASSUMES + ["ASM-E2-COLD-R", "ASM-E2-HOVER-MARGIN"],
          equation="as CALC-E2-BUDGET-BASE / -PESS with B1's level cruise power x k, k = P_params / P_B1 "
                   "(base: params cruise power / B1V level power at the gate; pessimistic: B1V pessimistic x the same "
                   "k) ; BATT_LOW count as CALC-E2-FAILSAFE (counter = measured capacity, D-154)",
          inputs={"m_b": "CL-A1-MASS-SIZED", "m_p": P + "requirements.mtow_gate_kg",
                  "p_par": P + "performance.cruise_power_w", "turb": "ASM-E2-TURB-W", **COMMON},
          units={"m_b": "kg", "m_p": "kg", "p_par": "W", "turb": "W", **CU})
def budget_240(m_b, m_p, p_par, turb, **kw):
    k = (p_par + turb) / kw["pc_b"]
    base = budget(m_b, False, p_scale=k, **kw)
    pess = budget(m_p, True, p_scale=k, **kw)
    fs = failsafe_rows(pess["phases"], kw["ah"], kw["reserve"], kw["cap_frac"], kw["prof"]["landing_hover_s"],
                       kw["goaround"])
    return {"k": k, "cruise_min_base": base["cruise_min"], "cruise_min_pess": pess["cruise_min"],
            "cruise_w_base": base["cruise_w"], "cruise_w_pess": pess["cruise_w"], "cruise_a_pess": pess["cruise_a"],
            "low_mah": fs["low_mah"], "cruise_to_low_min": fs["cruise_to_low_min"]}


@kit.calc("CALC-E2-BUDGET-V17", title="Budget at 17 m/s on E1's cruise point (performance.cruise_ms 17, D-145)",
          assumes=ASSUMES + ["ASM-E2-COLD-R", "ASM-E2-HOVER-MARGIN", "ASM-E1-V-FALLBACK"],
          equation="as CALC-E2-BUDGET-240 with the params cruise power replaced by E1's 17 m/s point: "
                   "k = (P_E1(17 m/s) + P_avionics) / P_B1(17 m/s, gate) ; base = B1 level power x k ; pessimistic = "
                   "B1 pessimistic power (17 m/s, B1-W2) x the same k (EST: E1's / B1's base ratio applied to "
                   "the pessimistic power) ; BATT_LOW count as CALC-E2-FAILSAFE with the 17 m/s cruise current, counter = measured "
                   "capacity (D-154)",
          inputs={"m_b": "CL-A1-MASS-SIZED", "m_p": P + "requirements.mtow_gate_kg",
                  "p17": "CL-E1-CRUISE-P-55-V17", "turb": "ASM-E2-TURB-W", **COMMON},
          units={"m_b": "kg", "m_p": "kg", "p17": "W", "turb": "W", **CU})
def budget_v17(m_b, m_p, p17, turb, **kw):
    k = (p17 + kw["avn"] + turb) / kw["pc_b"]
    base = budget(m_b, False, p_scale=k, **kw)
    pess = budget(m_p, True, p_scale=k, **kw)
    fs = failsafe_rows(pess["phases"], kw["ah"], kw["reserve"], kw["cap_frac"], kw["prof"]["landing_hover_s"],
                       kw["goaround"])
    return {"k": k, "p_carried_w": p17 + kw["avn"] + turb, "cruise_min_base": base["cruise_min"],
            "cruise_min_pess": pess["cruise_min"], "cruise_w_base": base["cruise_w"],
            "cruise_w_pess": pess["cruise_w"], "cruise_a_pess": pess["cruise_a"],
            "low_mah": fs["low_mah"], "cruise_to_low_min": fs["cruise_to_low_min"],
            "counter_mah": fs["counter_mah"], "land_left_mah": fs["land_left_mah"]}


# ---------------------------------------------------------------- claims
def table_out(calc, title):
    return dict(calc=calc, output="phases", unit="-", how=f"{title}: compare each row with the DataFlash log "
                "(BAT.Curr, BAT.CurrTot) of a full mission; rows within +/-15 %.")


kit.claim("CL-E2-BUDGET-BASE-TABLE", "Phase table, base [phase, s, W, A, Ah]",
          **table_out("CALC-E2-BUDGET-BASE", "Base phase table"))
kit.claim("CL-E2-BUDGET-PESS-TABLE", "Phase table, pessimistic [phase, s, W, A, Ah]",
          **table_out("CALC-E2-BUDGET-PESS", "Pessimistic phase table"))
kit.claim("CL-E2-CRUISE-MIN-BASE", "Cruise after the hover hold to the 20 % line, base", calc="CALC-E2-BUDGET-BASE",
          output="cruise_min", unit="min", limit=(">=", P + "requirements.cruise_time_min"), verifies=["R-MISSION"],
          how="Full-mission flight (R-TEST-ORDER gate 9): land when BAT.CurrTot reaches 80 % of 6 500 mAh; logged "
              "cruise time >= this value.")
kit.claim("CL-E2-CRUISE-MIN-PESS", "Cruise after the hover hold to the 20 % line, pessimistic",
          calc="CALC-E2-BUDGET-PESS", output="cruise_min", unit="min",
          limit=(">=", P + "requirements.cruise_time_min"), verifies=["R-MISSION"],
          how="Same flight; also re-run this script with the twin's logged hover and cruise currents in place of the "
              "model (ASM-E2-HOVER-MARGIN, ASM-E2-CRUISE-AERO).")
kit.claim("CL-E2-HOVER-ONLY-MIN-PESS", "Hover-only sortie to the 20 % line, pessimistic",
          calc="CALC-E2-BUDGET-PESS", output="hover_only_min", unit="min",
          limit=(">=", P + "requirements.hover_time_min"),
          how="Tethered hover (R-TEST-ORDER gate 3): log BAT.CurrTot vs time; minutes to 5 200 mAh >= this value.")
kit.claim("CL-E2-HOVER-I-GATE", "Hover pack current at the gate, 5 m/s wind", calc="CALC-E2-BUDGET-PESS",
          output="hover_a", unit="A",
          how="Tethered hover at gate mass (ballast) with the 150 A watt meter; F1 sizes wires and the disconnect on it.")
kit.claim("CL-E2-CRUISE-I-PESS", "Cruise pack current, pessimistic", calc="CALC-E2-BUDGET-PESS",
          output="cruise_a", unit="A", how="Fixed-wing tune flights: mean BAT.Curr in level cruise at "
                                            "AIRSPEED_CRUISE (performance.cruise_ms).")
PHASE_CLAIMS = [("ground", "Ground, armed checks"), ("climb", "Climb 0-50 m at 2 m/s"),
                ("trans_fwd", "Forward transition"), ("trans_back", "Back-transition"),
                ("descent", "Descent 50-0 m at 1 m/s")]
for key, label in PHASE_CLAIMS:
    tag = key.upper().replace("_", "-")
    kit.claim(f"CL-E2-I-{tag}-PESS", f"{label}: pack current, pessimistic (gate, 10 degC)",
              calc="CALC-E2-BUDGET-PESS", output=f"i_{key}_a", unit="A",
              how="DataFlash BAT.Curr mean over the phase on the full-mission log (T-E2-MISSION-LOG), within +/-15 %; "
                  "F1 reads this claim for harness heating (CALC-F1-PROFILE, CL-F1-PROFILE).")
    kit.claim(f"CL-E2-T-{tag}-PESS", f"{label}: duration, pessimistic", calc="CALC-E2-BUDGET-PESS",
              output=f"t_{key}_s", unit="s", how="Phase duration on the full-mission log (MODE and QTUN messages).")
kit.claim("CL-E2-T-HOVER-PESS", "Hover hold at 50 m before the transition: duration (D-160 split)", calc="CALC-E2-BUDGET-PESS", output="t_hover_s", unit="s",
          how="Phase duration on the full-mission log.")
kit.claim("CL-E2-T-CRUISE-PESS", "Cruise to the 20 % line: duration, pessimistic", calc="CALC-E2-BUDGET-PESS",
          output="t_cruise_s", unit="s", how="As CL-E2-CRUISE-MIN-PESS x 60.")
kit.claim("CL-E2-I-MAX-PHASE-PESS", "Highest mission-phase pack current, pessimistic", calc="CALC-E2-BUDGET-PESS",
          output="i_max_phase_a", unit="A", limit=("<=", P + "performance.full_throttle_current_a"),
          how="Largest phase-mean BAT.Curr on the full-mission log; stays under the pack-current limiter "
              "(Q_M_BAT_CURR_MAX).")
kit.claim("CL-E2-C-PEAK", "Peak discharge rate, all motors full", calc="CALC-E2-SAG", output="c_peak", unit="1/h",
          limit=("<=", 25.0),
          how="Limiter performance.full_throttle_current_a (Q_M_BAT_CURR_MAX, 70 A since D-148) / C; any hobby 6500 "
              "pack with IR <= 5 mOhm/cell carries it (T-E2-IR). Limit 25C = realistic continuous rating of a "
              "hard-case pack labelled 100C+.")
kit.claim("CL-E2-SAG-BRACKET", "E1's worst/fresh thrust factor lies inside E2's physical bracket (D-35)",
          calc="CALC-E2-SAG", output="e1_bracket_margin", unit="-", limit=(">=", 0.0),
          note="D-35 resolved: E2 adopts E1's station model (CL-E1-SAG-FACTOR, CL-E1-TW-WORST) as the one worst-state "
               "claim. The limiter binds in every pack state, so the pack current is fixed at the limiter and thrust "
               "follows power (lower bound, thrust ~ V) or the ideal rotor (upper, ~ V^(2/3)); E1 lies between. "
               "Retires CL-E2-SAG-F-WORST and CL-E2-TW-SAG-WORST (the (V/14.8)^2 rule counted the sag twice)",
          how="T-E1-STAND fresh and worst-state runs: measured thrust ratio between the measured bus-voltage ratio "
              "and its 2/3 power.")
kit.claim("CL-E2-LIMITER-BINDS-WORST", "Unlimited pack current at 20 % charge, 10 degC (limiter still binds)",
          calc="CALC-E2-SAG", output="i_unlim_res20_cold", unit="A",
          limit=(">=", P + "performance.full_throttle_current_a"),
          how="Same stand run with Q_M_BAT_CURR_MAX disabled for one 1 s punch (props on the stand only): pack "
              "current at full duty above the limiter. If it is not, the V^2 rule applies below the limiter and D-35 "
              "re-opens.")
kit.claim("CL-E2-V-BUS-WORST", "Bus voltage at the pack-current limiter, 20 % charge, 10 degC pack", calc="CALC-E2-SAG",
          output="v_res20_cold", unit="V",
          how="Logged BAT.Volt during a full-throttle punch on the cold-pack stand run (T-E2-IR); F4 sets "
              "BATT_FS_VOLTSRC 1 (sag-compensated) and Q_M_BAT_VOLT_MIN below it.")
kit.claim("CL-E2-SAG-V-WORST", "Cell sag at the pack-current limiter, 20 % charge, 10 degC", calc="CALC-E2-SAG",
          output="sag_v_per_cell_worst", unit="V",
          how="Load-step IR test (T-E2-IR) scaled to the limiter current; F4 uses it for BATT_FS_VOLTSRC 1 and Q_M_BAT_VOLT_MIN.")
kit.claim("CL-E2-PACK-T-END", "Pack temperature at landing, worst morning (adiabatic)", calc="CALC-E2-HEAT",
          output="t_end_max_c", unit="degC", limit=("<=", 50.0), verifies=["R-THERMAL"],
          how="IR thermometer on the pack face at landing; E3 adds the pod's heat path. 50 degC leaves 10 K to the "
              "usual 60 degC LiPo discharge limit.")
kit.claim("CL-E2-PACK-HEAT-HOVER", "Pack internal heat in hover, cold pack", calc="CALC-E2-HEAT",
          output="p_hover_cold_w", unit="W", how="E3 input; check by I^2 R from the measured IR and hover current.")
kit.claim("CL-E2-PACK-LARGEST", "Named flight pack passes the pack trade (acceptance line, cruise to BATT_LOW at "
          "17 m/s >= requirement, landing >= BATT_CRT, current, lead)", calc="CALC-E2-PACK-TRADE",
          output="named_pass_ah", unit="Ah", limit=(">=", P + "battery.capacity_ah"), verifies=["R-MISSION", "R-PACK-MASS"],
          parts=["PWR-001"],
          note="E2 closure 2026-11-14: re-defined. Was 'largest candidate passing A1 sized mass and the 20 % line', "
               "which no pack could pass because CL-A1-MASS-SIZED 2.64 kg sits above the 2.6 kg gate. The id is kept "
               "for the graph links. Value = the named pack's Ah if it passes all five criteria, else 0",
          how="Re-run after A3's mass_rollup.py and with the weighed pack mass (T-E2-WEIGH) and the measured capacity "
              "(T-E2-CAPACITY); the named pack stands while it passes.")
kit.claim("CL-E2-BATT-CRT-MAH", "BATT_CRT_MAH (critical: QLAND)", calc="CALC-E2-FAILSAFE", output="crt_mah",
          unit="mAh", verifies=["R-FAILSAFES"],
          how="SITL and bench (props off): set BATT_CAPACITY to the measured capacity (D-154), inject current, "
              "confirm QLAND at this count.")
kit.claim("CL-E2-BATT-LOW-MAH", "BATT_LOW_MAH (low: QRTL)", calc="CALC-E2-FAILSAFE", output="low_mah", unit="mAh",
          verifies=["R-FAILSAFES"], how="Same bench test: QRTL at this count; landing then ends above BATT_CRT_MAH.")
TO_LOW_NOTE = ("What this measures: R-MISSION as flown. Minutes of cruise, after ground, climb, the hover hold and the "
               "forward transition, before the flight controller's mAh counter reaches BATT_LOW_MAH and commands "
               "QRTL, on the pessimistic pack (92 % of nameplate, cold, gate mass). The counter counts against "
               "BATT_CAPACITY = the pack's measured capacity (D-154), and BATT_LOW_MAH holds the energy to come back "
               "and land, one 40 s hover go-around (D-160) and the 20 % reserve. It is stricter than CL-E2-CRUISE-MIN-PESS*, which cruises to the "
               "20 % line and keeps nothing for the return. Before D-154 the counter base was 6 500 mAh, which "
               "spent the reserve on a 92 % pack")
kit.claim("CL-E2-CRUISE-TO-LOW-PESS", "Cruise before BATT_LOW (QRTL) fires, pessimistic pack, counter = measured "
          "capacity, at B1's cruise point", calc="CALC-E2-FAILSAFE", output="cruise_to_low_min", unit="min",
          limit=(">=", P + "requirements.cruise_time_min"), verifies=["R-MISSION"], note=TO_LOW_NOTE,
          how="SITL with the logged currents and BATT_CAPACITY = measured: QRTL must not trigger before "
              "requirements.cruise_time_min (3.5 min, D-160) of cruise.")
kit.claim("CL-E2-SORTIES-WINDOW", "Full-mission sorties the 3 h window allows", calc="CALC-E2-TESTDAY",
          output="sorties_window", unit="-", how="Count logged sorties on the first full test day; I2 plans on it.")
kit.claim("CL-E2-SORTIES-PACKS", "Sorties per day with the packs on order", calc="CALC-E2-TESTDAY",
          output="sorties_current_packs", unit="-", how="= min(packs owned, window); one full pack per sortie.")
kit.claim("CL-E2-CHARGE-MIN", "Charge time per pack from the 20 % line", calc="CALC-E2-TESTDAY",
          output="charge_min_per_pack", unit="min", how="Time the first charge on the HTRC C150 (T-E2-CAPACITY).")
kit.claim("CL-E2-CHARGE-H-4", "Attended charge time for 4 packs, one port", calc="CALC-E2-TESTDAY",
          output="charge_h_4_packs", unit="h", limit=("<=", 5.0),
          how="Sum of logged charge times after a test day; must fit one attended afternoon (<= 5 h).")
kit.claim("CL-E2-WINDOW-USED", "Window minutes used by the planned sorties (2 packs, D-12)", calc="CALC-E2-TESTDAY",
          output="window_used_min", unit="min", limit=("<=", 180.0),
          how="Log take-off and landing times on the first test day; I2 plans the day on it.")
kit.claim("CL-E2-PACK-ACCEPT-KG", "Pack pass line PACK_ACCEPT_KG (= CL-A3-PACK-ACCEPT, read live; D-154)",
          calc="CALC-E2-SKU-CHECK", output="accept_kg", unit="kg", parts=["PWR-001"],
          note="Information (E2 closure 2026-11-14): the limit >= 0.556 kg was removed because it was the same test as "
               "CL-E2-SKU-MASS-MARGIN (accept - (551 + 5 g) >= 0), counted twice; that claim and CL-E2-PACK-LARGEST "
               "keep it. D-154: the pack pass line of record is A3's CL-A3-PACK-ACCEPT (carried pack + CL-A3-GATE-MARGIN - "
               "build overrun), read live, never typed in: 564.4 g on 2026-11-14, so <= 564 g that day (the 558 g "
               "of D-132 is retired). A3 may move it (D-155 package), so it is re-read on the weigh day. Limit = the "
               "SKU's listed maximum 0.556 kg: below it the named pack itself would fail acceptance",
          how="Re-run this script after A3's mass_rollup.py, on the weigh day; T-E2-WEIGH passes a pack at or under "
              "this value rounded down to the gram.")
kit.claim("CL-E2-SKU-MASS-MARGIN", "Named pack (listed mass + tolerance) under the D-64 acceptance line",
          calc="CALC-E2-SKU-CHECK", output="mass_margin_kg", unit="kg", limit=(">=", 0.0), verifies=["R-PACK-MASS"],
          parts=["PWR-001"],
          how="T-E2-WEIGH: every pack <= CL-E2-PACK-ACCEPT-KG on a 1 g scale, leads included (pack_log.csv).")
kit.claim("CL-E2-SKU-BAY-CLEAR", "Named pack body (listed + 3 mm) inside the D2 bay, tightest axis",
          calc="CALC-E2-SKU-CHECK", output="bay_clear_min_m", unit="m", limit=(">=", 0.0), parts=["PWR-001"],
          how="T-E2-WEIGH step 3: calipers L x W x H against the bay 160 x 52 x 53 mm; lead exit routed per D2.")
kit.claim("CL-E2-SKU-LEAD-AWG", "Named pack discharge-lead gauge (AWG number)", calc="CALC-E2-SKU-CHECK",
          output="lead_awg", unit="-", limit=("<=", 10.0), parts=["PWR-001"],
          note="10 AWG inferred from the EC5 plug (the page does not state it); I1 confirms at order, E2 on arrival",
          how="T-E2-WEIGH step 3a: read the print on the lead insulation, or strip 5 mm of the cut-off end at "
              "re-termination and measure the bundle (10 AWG ~2.6 mm, 12 AWG ~2.1 mm).")
kit.claim("CL-E2-CRUISE-MIN-BASE-240", "Cruise after the hover hold, base, at the params' cruise power (sensitivity)",
          calc="CALC-E2-BUDGET-240", output="cruise_min_base", unit="min",
          limit=(">=", P + "requirements.cruise_time_min"),
          how="As CL-E2-CRUISE-MIN-BASE; the first tune flight's logged cruise current decides between B1 and E1.")
kit.claim("CL-E2-CRUISE-MIN-PESS-240", "Cruise after the hover hold, pessimistic, at the params' cruise power (sensitivity)",
          calc="CALC-E2-BUDGET-240", output="cruise_min_pess", unit="min",
          limit=(">=", P + "requirements.cruise_time_min"), how="As CL-E2-CRUISE-MIN-PESS.")
kit.claim("CL-E2-CRUISE-TO-LOW-PESS-240", "Cruise before BATT_LOW (QRTL) fires, pessimistic pack, counter = measured capacity, at the params' cruise power (sensitivity)",
          calc="CALC-E2-BUDGET-240", output="cruise_to_low_min", unit="min",
          limit=(">=", P + "requirements.cruise_time_min"), note=TO_LOW_NOTE,
          how="SITL with the logged currents, as CL-E2-CRUISE-TO-LOW-PESS.")


kit.claim("CL-E2-LIHV-BACKUP-LOW", "BATT_LOW_VOLT (14.4 V, 3.60 V/cell) sits below the resting voltage at the 20 % reserve",
          calc="CALC-E2-LIHV-BACKUP", output="margin_low_v", unit="V", limit=(">=", 0.0), verifies=["R-FAILSAFES"],
          note="E2 final re-run 2026-11-14 (answers CR-F4-59): the mAh triggers (BATT_LOW_MAH 3 000, BATT_CRT_MAH 1 200) fire "
               "first; the voltage values are backups. Confirmed on paper only; the discharge curve (T-E2-CAPACITY) decides",
          how="T-E2-CAPACITY logs resting and loaded voltage at 100 / 50 / 20 %; F4 corrects the backups if the "
              "20 % rest is under 3.70 V/cell.")
kit.claim("CL-E2-LIHV-BACKUP-CRT", "BATT_CRT_VOLT (14.0 V) is below BATT_LOW_VOLT (14.4 V)", calc="CALC-E2-LIHV-BACKUP",
          output="margin_crt_v", unit="V", limit=(">=", 0.0), verifies=["R-FAILSAFES"],
          how="Same discharge log.")
kit.claim("CL-E2-LIHV-ARM-MARGIN", "BATT_ARM_VOLT (17.0 V, 4.25 V/cell) is under a full 4.35 V/cell charge",
          calc="CALC-E2-LIHV-BACKUP", output="margin_arm_v", unit="V", limit=(">=", 0.05), verifies=["R-FAILSAFES"],
          note="A pack charged to 4.35 V/cell and rested reads about 4.30-4.33 V/cell (EST); the line is 0.10 V/cell below",
          how="First charge on the HTRC C150 in LiHV mode: read the resting pack voltage; if the charger caps at 4.20 "
              "V/cell the pack reads 16.8 V and will not arm (F4 lowers the line).")


# ---------------------------------------------------------------- measured packs (T-E2-WEIGH)
def read_pack_log(path):
    """Rows of pack_log.csv with a mass entered; empty until the ~20 Nov order arrives."""
    import csv
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if (r.get("mass_g") or "").strip()]


PACK_LOG = HERE / "pack_log.csv"
WEIGHED = read_pack_log(PACK_LOG)
# D-154: the pass line is A3's CL-A3-PACK-ACCEPT (g), read live; never a hard-coded number (558 g D-132, 0.601 D-58)
PACK_ACCEPT_KG = kit.value("CL-A3-PACK-ACCEPT") / 1000.0
if WEIGHED:
    m_meas = max(float(r["mass_g"]) for r in WEIGHED) / 1000.0
    kit.claim("CL-E2-PACK-MASS", "Flight pack mass, heaviest weighed pack", value=m_meas, unit="kg",
              limit=("<=", "CL-E2-PACK-ACCEPT-KG"), verifies=["R-PACK-MASS"], cites=["SRC-E2-OVONIC-LISTINGS"],
              how="Weighed on arrival (T-E2-WEIGH, pack_log.csv). A3 replaces the 550 g line with this value; "
                  "A1 may then set checked on SRC-OVONIC-4S6500.")
    kit.test("T-E2-WEIGH", "Weigh and measure every pack on arrival", verifies=["CL-E2-PACK-MASS", "CL-E2-SKU-MASS-MARGIN", "CL-E2-SKU-BAY-CLEAR", "CL-E2-SKU-LEAD-AWG"], state="run",
             result="pass" if m_meas <= PACK_ACCEPT_KG else "fail", measured=m_meas,
             date=max(r.get("received", "") for r in WEIGHED), evidence="redesign/team/E2/pack_log.csv",
             procedure="1 g scale, calipers L x W x H incl. lead exit; one row per pack in pack_log.csv.")
else:
    kit.claim("CL-E2-PACK-MASS", "Flight pack mass carried in the budget (not yet weighed)", value=0.414, unit="kg",
              limit=("<=", "CL-E2-PACK-ACCEPT-KG"), verifies=["R-PACK-MASS"], status="UNVERIFIED",
              cites=["SRC-E2-PACK-SEARCH-D173"],
              note="named SKU (D-174): Gens Ace Redline 4S 6000 HV Shorty, listed 410 +/- 10 g + 4 g EST pigtails = "
                   "0.414 kg (params battery.mass_kg) stays the carried value until weighed",
              how="Weigh each pack on arrival on a 1 g scale (T-E2-WEIGH) and enter it in pack_log.csv, then re-run. "
                  f"Pass: every pack <= CL-E2-PACK-ACCEPT-KG (= CL-A3-PACK-ACCEPT, {PACK_ACCEPT_KG * 1000:.1f} g "
                  "when this script last ran; re-read on the weigh day); a pack above "
                  "0.424 kg (the listed maximum) is reported to A3 so the 550 g line is replaced; a pack above the "
                  "acceptance line is returned (D-64; the Tattu fallback is not pre-approved).")
    kit.test("T-E2-WEIGH", "Weigh and measure every pack on arrival", verifies=["CL-E2-PACK-MASS", "CL-E2-SKU-MASS-MARGIN", "CL-E2-SKU-BAY-CLEAR", "CL-E2-SKU-LEAD-AWG"], state="planned",
             procedure="1 g scale; calipers L x W x H incl. lead exit; one row per pack (E2-P1, E2-P2) in "
                       "redesign/team/E2/pack_log.csv, then re-run this script and build_graph.py.")
kit.test("T-E2-CAPACITY", "Discharge capacity test at 1C", verifies=["CL-E2-CRUISE-MIN-PESS", "CL-E2-CHARGE-MIN"],
         state="planned", procedure="Charger discharge mode is limited in power: discharge through the thrust stand "
         "at ~6.0 A to 3.5 V/cell under load, log mAh with the watt meter; pass >= 5.52 Ah (0.92 x 6.0 Ah; D-174 pack). "
         "Also log resting voltage at 100 / 50 / 20 % (LiHV backups, CL-E2-LIHV-BACKUP-*).")
kit.test("T-E2-IR", "Pack resistance by load step", verifies=["CL-E2-SAG-BRACKET", "CL-E2-V-BUS-WORST", "CL-E2-SAG-V-WORST", "CL-E2-C-PEAK"],
         state="planned", procedure="Thrust stand, one motor: rest voltage, then 20 A step; R = dV / dI after 2 s; "
         "repeat at 10 degC (pack 1 h in a fridge, bagged). Pass <= 3.8 mOhm per cell group (4S2P) at 25 degC "
         "(D-174 acceptance line; the hot-landing 50 degC line, CL-E2-PACK-T-END, holds only up to it).")
kit.test("T-E2-MISSION-LOG", "Full-mission current log", verifies=["CL-E2-CRUISE-MIN-BASE", "CL-E2-HOVER-I-GATE",
         "CL-E2-CRUISE-I-PESS", "CL-E2-PACK-T-END", "CL-E2-I-CLIMB-PESS", "CL-E2-I-TRANS-FWD-PESS",
         "CL-E2-I-TRANS-BACK-PESS", "CL-E2-I-DESCENT-PESS", "CL-E2-I-MAX-PHASE-PESS"], state="planned",
         procedure="DataFlash BAT messages; IR thermometer on pack before/after; compare row by row with the phase table.")

# ---- CDR-05 / CDR-AE-09 (2026-11-13): the 17 m/s fallback of D-96 (c), which decision B6 makes the planning case
V17_NOTE = ("17 m/s is AIRSPEED_MIN = AIRSPEED_CRUISE (D-122), and performance.cruise_ms is 17 since D-145. "
            "Cruise power = E1's 17 m/s point (CL-E1-CRUISE-P-55-V17) + 6 W avionics, carried through the same "
            "chain as the params-power case; the pessimistic case scales B1's pessimistic power by the same factor "
            "(EST). BATT_LOW counts against BATT_CAPACITY = the measured capacity (D-154)")
kit.claim("CL-E2-CRUISE-MIN-BASE-V17", "Cruise after the hover hold to the 20 % line, base, at 17 m/s",
          calc="CALC-E2-BUDGET-V17", output="cruise_min_base", unit="min",
          limit=(">=", P + "requirements.cruise_time_min"), note=V17_NOTE, how="As CL-E2-CRUISE-MIN-BASE at 17 m/s.")
kit.claim("CL-E2-CRUISE-MIN-PESS-V17", "Cruise after the hover hold to the 20 % line (no return energy kept), pessimistic, at 17 m/s",
          calc="CALC-E2-BUDGET-V17", output="cruise_min_pess", unit="min",
          limit=(">=", P + "requirements.cruise_time_min"), note=V17_NOTE,
          how="As CL-E2-CRUISE-MIN-PESS at 17 m/s (T-E2-MISSION-LOG decides).")
kit.claim("CL-E2-CRUISE-TO-LOW-PESS-V17", "R-MISSION as flown: cruise at 17 m/s before BATT_LOW (QRTL) fires, "
          "pessimistic pack, counter = measured capacity", calc="CALC-E2-BUDGET-V17", output="cruise_to_low_min",
          unit="min", limit=(">=", P + "requirements.cruise_time_min"), verifies=["R-MISSION"],
          note=TO_LOW_NOTE + ". " + V17_NOTE + ". Passes on the 6.5 Ah LiPo since D-160 (3.5 min cruise; 35 s hold + 40 s go-around "
               "inside BATT_LOW 3 100 mAh; E2 closure 2026-11-14)",
          how="SITL with the logged currents at AIRSPEED_CRUISE 17 and BATT_CAPACITY = measured: QRTL must not "
              "trigger before 3.5 min of cruise; first logged cruise current (T-E2-MISSION-LOG).")
kit.claim("CL-E2-LAND-LEFT-PESS-V17", "True charge at touchdown after a BATT_LOW QRTL from the far point, 17 m/s, "
          "pessimistic", calc="CALC-E2-BUDGET-V17", output="land_left_mah", unit="mAh",
          limit=(">=", "CL-E2-BATT-CRT-MAH"), verifies=["R-MISSION", "R-FAILSAFES"], note=V17_NOTE,
          how="Guard on the counter base (D-154): with BATT_CAPACITY = measured capacity the landing ends with at "
              "least the 20 % reserve. Check on the full-mission log: BAT.CurrTot at touchdown <= measured "
              "capacity - BATT_CRT_MAH.")
kit.claim("CL-E2-BATT-LOW-MAH-V17", "BATT_LOW_MAH needed with the 17 m/s cruise current (60 s return leg)",
          calc="CALC-E2-BUDGET-V17", output="low_mah", unit="mAh", note=V17_NOTE,
          how="F4 sets BATT_LOW_MAH to this value at AIRSPEED_CRUISE 17 (E2 closure 2026-11-14, D-160: 3 100 for the 6.5 Ah pack; was 2 700), with "
              "BATT_CAPACITY = the lowest measured T-E2-CAPACITY of the packs flown.")
kit.claim("CL-E2-CRUISE-W-PESS-V17", "Cruise bus power, pessimistic, at the 17 m/s fallback", calc="CALC-E2-BUDGET-V17",
          output="cruise_w_pess", unit="W", note=V17_NOTE, how="Logged pack power in 17 m/s legs (T-E2-MISSION-LOG).")


if __name__ == "__main__":
    kit.write()
    for cid in ("CALC-E2-BUDGET-BASE", "CALC-E2-BUDGET-PESS"):
        o = kit.nodes[cid]["outputs"]
        print(f"\n{cid}: R_pack {o['r_pack']*1000:.1f} mOhm, hover {o['hover_w']:.0f} W / {o['hover_a']:.1f} A, "
              f"cruise {o['cruise_w']:.0f} W / {o['cruise_a']:.1f} A, avail {o['ah_avail']:.2f} Ah")
        for name, t, p, i, ah in o["phases"]:
            print(f"  {name:<22} {t:7.0f} s {p:6.0f} W {i:6.1f} A {ah*1000:6.0f} mAh")
        print(f"  cruise {o['cruise_min']:.1f} min, hover-only {o['hover_only_min']:.1f} min, flight {o['flight_min']:.1f} min")
    print("\nSAG", {k: round(v, 3) for k, v in kit.nodes["CALC-E2-SAG"]["outputs"].items()})
    print("HEAT", {k: round(v, 2) for k, v in kit.nodes["CALC-E2-HEAT"]["outputs"].items()})
    for r in kit.nodes["CALC-E2-PACK-TRADE"]["outputs"]["table"]:
        print("TRADE", r)
    print("FAILSAFE", kit.nodes["CALC-E2-FAILSAFE"]["outputs"])
    print("TESTDAY", {k: round(v, 2) for k, v in kit.nodes["CALC-E2-TESTDAY"]["outputs"].items()})
    for cid in ("CALC-E2-BUDGET-BASE", "CALC-E2-BUDGET-PESS"):
        print(cid, "E2 cross-check cruise W", round(kit.nodes[cid]["outputs"]["cruise_w_e2_model"], 1))
    print("SKU", kit.nodes["CALC-E2-SKU-CHECK"]["outputs"])
    print("AT PARAMS CRUISE W", {k: round(v, 3) for k, v in kit.nodes["CALC-E2-BUDGET-240"]["outputs"].items()})
    print("AT 17 M/S FALLBACK", {k: round(v, 3) for k, v in kit.nodes["CALC-E2-BUDGET-V17"]["outputs"].items()})
    print("PACK LOG", f"{len(WEIGHED)} weighed pack(s)" if WEIGHED else "no pack weighed yet (order ~20 Nov)")
