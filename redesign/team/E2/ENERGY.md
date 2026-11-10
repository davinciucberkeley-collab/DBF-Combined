# Energy: flight pack, mission budget, charging and handling (K09-L)

Owner: E2 (battery / energy engineer). Revision E2-R3, 2026-11-09, against params D-32 to D-38. Status:
`PROPOSED`. Every number below is computed by `redesign/team/E2/energy_claims.py` (claims in `team/E2/claims.json`).
To re-check, run `python -I redesign/team/E2/energy_claims.py` and then `python -I redesign/proofs/build_graph.py`.
All 35 E2 claims are `UNVERIFIED` or `PROPOSED`: no pack has been weighed, capacity-tested or IR-tested yet.

**What changed in R3** (CR-A1-31, CR-F1-03/-04, CR-A2-17, CR-E3-10, D-35).

| Change | Effect |
|---|---|
| Cruise power is B1 rev 2 (11x5.5MR, 16 m/s, pod +3 %): `CL-B1-CRUISE-P` 227.8 W, `-P-PESS` 300.6 W as stored today | base 9.6 → 12.8 min, pessimistic 5.1 → 6.9 min (at the old 3 mΩ) |
| Lead and harness resistance from F1: `P:electrical.r_ext_mohm` 6.5 (was E2's 3 mΩ assumption) | −0.1 min base and pessimistic; pack R 30.5 mΩ cold, 22.5 mΩ warm |
| Capacity fraction read from `P:requirements.pack_capacity_min_frac` (0.92, same value) | none (A2 retires `ASM-A2-PACK-CAPACITY-FRAC`) |
| Voltage sag: E2 adopts E1's station model under the 100 A limiter (D-35); E2's (V/14.8)² claims retired | one worst-state T/W claim, `CL-E1-TW-WORST`; E2 checks it with a bracket |
| Phase currents and durations emitted as claims (CR-F1-04) | F1's `ASM-F1-PROFILE` can link to live values |
| Indicative 11x5.5MR sensitivity (`CALC-E2-PROP55-SENS`, `-55` claims) retired | B1 rev 2 is on the 11x5.5MR, so the ratio would count the prop change twice |

The params carry 13.7 / 7.3 min: the build's re-run of E2's calcs on B1's earlier 216.9 / 283.4 W. B1 has since
re-run for the 0.14 m pod (227.8 / 300.6 W), and F1's 6.5 mΩ costs another 0.1 min. **The published values are
12.7 / 6.8 min.**

**Verdict.** Keep the **Ovonic 4S 6500 mAh LiPo**, one per sortie, 2 sorties per test day (D-12). The pessimistic
mission now gives **6.8 min** of cruise (+36 %), and `BATT_LOW` triggers after **6.4 min** (+28 %), so the R2 `FAILS`
is closed. The first pack is not weighed yet: the order arrives ~20 Nov.

## 1. Pack selection

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Chemistry, cells | LiPo, 4S (KV900 motors fix 4S) | — | `params.json#battery.cells_s` | `PROPOSED` |
| Capacity, energy | 6.5, 96.2 | Ah, Wh | `params.json#battery` | `UNVERIFIED` |
| Mass carried in the budget | 0.55 (listings 0.522–0.551; one listing 0.680); accept ≤ 0.68 | kg | `CL-E2-PACK-MASS` | `PROPOSED` (not weighed) |
| Envelope, hard case | 0.139 × 0.047 × 0.049 (alt. SKU 0.157 × 0.048 × 0.043) | m | `SRC-E2-OVONIC-LISTINGS`, `params.json#battery.size_m` | `UNVERIFIED` |
| Connectors | ships XT60 (confirm at order, CR-I1-06); re-terminated to **AS150U** main (F1, D-32); JST-XH 5-pin balance | — | `SRC-E2-OVONIC-LISTINGS`, F1 `POWER.md` | `UNVERIFIED` |
| Pack lead gauge | ≥ 10 AWG required (12 AWG rises 28 °C at 30 A); confirm before ordering (CR-F1-14) | — | `CL-F1-PACKLEAD-RISE` | `UNVERIFIED` |
| Peak draw (100 A limiter) | 100 A = 15.4 C | A | `CL-E2-C-PEAK` (≤ 25 C) | `UNVERIFIED` |
| Real continuous rating needed | ≥ 25 C, IR ≤ 5 mΩ/cell (the "130C" label is not physical) | — | `ASM-E2-R-CELL` | `UNVERIFIED` |

**Trade** (`CALC-E2-PACK-TRADE`). Each candidate replaces the 0.55 kg pack in the sized mass (2.594 kg). The
pessimistic case adds the same growth up to the gate.

| Candidate | Ah | kg | Aircraft kg | Cruise base, min | Cruise pess., min | Cont. A | Result |
|---|---|---|---|---|---|---|---|
| Admiral 4S 4000 | 4.0 | 0.386 | 2.430 | 6.0 | 2.4 | 120 | fails 5 min pess. |
| 4S 5000 hard case `EST` | 5.0 | 0.46 | 2.504 | 8.7 | 4.2 | 150 | fails 5 min pess. |
| **Ovonic 4S 6500** | **6.5** | **0.55** | **2.594** | **12.7** | **6.8** | 195 | **passes** |
| 4S 8000 hard case `EST` | 8.0 | 0.70 | 2.744 | 15.8 | 8.8 | 240 | fails 2.6 kg gate |
| Li-ion 4S2P 21700 9 Ah `EST` | 9.0 | 0.62 | 2.664 | 19.3 | 11.2 | 90 | fails gate and 100 A peak |

The 6500 is still the only candidate inside the gate that passes. The sized mass is now 2.594 kg (D-38), 6 g under
the gate, so a heavier pack cannot be absorbed.

## 2. Energy budget per mission phase

The model is a Thevenin pack (Voc 4 × 3.70 V, R = 4 × 4.0 mΩ + 6.5 mΩ of leads and harness from
`P:electrical.r_ext_mohm`), with current solved from bus power. Hover power comes from the maker table plus the
download factor and the ESC loss. Climb uses momentum theory. Cruise is B1's power × 1.05 circuit factor. The
reserve is 20 % of nameplate (1.30 Ah) and is never planned into. **Base**: sized mass 2.594 kg, new pack, calm,
25 °C. **Pessimistic**: 2.6 kg, 92 % capacity, R × 1.5 at 10 °C, hover × 1.10 for 5 m/s wind, B1 pessimistic cruise
(CD0 × 1.3, e 0.80, η_prop 0.40), 20 s transitions.

| Phase | Time base / pess, s | Power base / pess, W | Current base / pess, A | Charge base / pess, mAh | Pessimistic claims (A, s) |
|---|---|---|---|---|---|
| Ground, armed checks | 180 / 180 | 6 / 6 | 0.4 / 0.4 | 20 / 20 | — |
| Climb 0–50 m at 2 m/s | 25 / 25 | 442 / 487 | 31.4 / 35.5 | 218 / 247 | `CL-E2-I-CLIMB-PESS`, `CL-E2-T-CLIMB-PESS` |
| Hover (mission) | 120 / 120 | 379 / 418 | 26.7 / 30.1 | 891 / 1 004 | `CL-E2-HOVER-I-GATE`, `CL-E2-T-HOVER-PESS` |
| Transition forward | 10 / 20 | 531 / 585 | 38.1 / 43.5 | 106 / 241 | `CL-E2-I-TRANS-FWD-PESS`, `CL-E2-T-TRANS-FWD-PESS` |
| Back-transition | 10 / 20 | 493 / 544 | 35.2 / 40.0 | 98 / 222 | `CL-E2-I-TRANS-BACK-PESS`, `CL-E2-T-TRANS-BACK-PESS` |
| Descent 50–0 m at 1 m/s | 50 / 50 | 379 / 418 | 26.7 / 30.1 | 371 / 418 | `CL-E2-I-DESCENT-PESS`, `CL-E2-T-DESCENT-PESS` |
| **Cruise at 16 m/s to the 20 % line** | **760 / 407** | 239 / 316 | 16.6 / 22.4 | 3 497 / 2 526 | `CL-E2-CRUISE-I-PESS`, `CL-E2-T-CRUISE-PESS` |
| Reserve (untouched) | — | — | — | 1 300 / 1 300 | — |

Highest phase current: 43.5 A in the pessimistic forward transition (`CL-E2-I-MAX-PHASE-PESS`, ≤ 100 A limiter).

| Result | Base | Pess. | Limit | Claim | Status |
|---|---|---|---|---|---|
| Cruise after 2 min hover, min | **12.7** | **6.8** | ≥ 5 | `CL-E2-CRUISE-MIN-BASE`, `-PESS` | `UNVERIFIED` (+153 % / +36 %) |
| Cruise before `BATT_LOW` triggers, min | — | 6.4 | ≥ 5 | `CL-E2-CRUISE-TO-LOW-PESS` | `UNVERIFIED` (+28 %) |
| Hover-only sortie to 20 %, min | 11.6 | 9.3 | ≥ 2 | `CL-E2-HOVER-ONLY-MIN-PESS` | `UNVERIFIED` |
| Flight time of the mission, min | 16.3 | 10.7 | — | `CALC-E2-BUDGET-*` | `UNVERIFIED` |

**Cross-check and the remaining risk.** E2's own drag model (K09 CD0 0.0593, η_prop 0.47 / 0.35) gives 249 W base
and 405 W pessimistic, against 239 / 316 W from B1 rev 2 with circuits. The base cases agree within 4 %. The
pessimistic cases differ by 28 %, because B1 rev 2 has a lower CD0 (0.0452 build-up) and the 11x5.5MR's better
η_prop. If E2's pessimistic power were right, cruise would be about 5.2 min and `BATT_LOW` would trigger at about
4.7 min. B1 owns the drag build-up and E2 carries it. The logged cruise current on the first fixed-wing tune flight
(`T-E2-MISSION-LOG`) settles it, before any full-mission sortie.

## 3. Voltage sag and thrust (D-35 resolved)

**Decision.** E2 adopts E1's model. There is one worst-state T/W claim, `CL-E1-TW-WORST`, computed by `CALC-E1-WORST`
from E1's station model and E2's pack inputs (`ASM-E2-OCV-20`, `-R-CELL`, `-COLD-R` and the line resistance). E2's
`CL-E2-SAG-F-WORST` (0.76) and `CL-E2-TW-SAG-WORST` (1.89) are retired. A1 sets `propulsion.voltage_sag` from
`CL-E1-SAG-FACTOR`.

**Why.** The 100 A pack-current limiter binds in every pack state (`CALC-E2-SAG`). Without it, the four motors at full
duty would draw 164 A fresh, 124 A at 20 %, and still 109 A at 20 % with a cold pack (`CL-E2-LIMITER-BINDS-WORST`,
+9 %). So the pack current at full throttle is 100 A in every state, and only the bus voltage changes. The power into
the motors then scales with V, and static thrust lies between two bounds: thrust ∝ V, where all of the lost power
comes out of thrust, and thrust ∝ V^(2/3) for an ideal rotor (P ∝ T^1.5). E2's old rule, (V/14.8)², is the law for an
*unlimited* motor at full duty. Applying it to `thrust_max_per_motor_kg`, which is already the limited thrust,
counted the sag twice.

| Pack state, 100 A | Pack R, mΩ | Bus V | V/cell loaded | Unlimited A | Status |
|---|---|---|---|---|---|
| Full (4.20 V/cell), 25 °C | 22.5 | 14.55 | 3.64 | 164 | `UNVERIFIED` |
| 20 % line (3.73 V/cell), 25 °C | 22.5 | 12.67 | 3.17 | 124 | `UNVERIFIED` |
| **20 % line, 10 °C pack** | 30.5 | **11.87** (`CL-E2-V-BUS-WORST`) | 2.97 (0.76 V/cell sag, `CL-E2-SAG-V-WORST`) | 109 | `UNVERIFIED` |

| Thrust factor, worst / fresh | Value | Basis |
|---|---|---|
| Lower bound, thrust ∝ V | 0.816 | V ratio 11.87 / 14.55 |
| **E1 station model** (`CL-E1-SAG-FACTOR`, stored at 3 mΩ) | **0.854** (0.851 at 6.5 mΩ) | motor and ESC losses, winding at 80 °C |
| Upper bound, ideal rotor ∝ V^(2/3) | 0.873 | — |
| Old E2 rule (V/14.8)², retired | 0.643 | double-counts the sag |

E1's factor lies inside the bracket with a 0.019 margin (`CL-E2-SAG-BRACKET` ≥ 0; effective exponent 0.78).
**Worst-state T/W.** E1 stores 2.18 (3 mΩ, cant 3°). E2 ran E1's current `worst()` on the current params (6.5 mΩ,
cant 7°) and got **2.12** (fresh thrust 1 634 gf, worst 1 390 gf, f 0.851), ≥ 1.6 (+33 %). Even the lower bound
applied to E1's fresh thrust gives 4 × 1.634 × 0.816 × cos 7° / 2.6 = 2.04. E1's working script already reads
`P:electrical.r_ext_mohm`; its stored claims predate that, so E1 re-runs and publishes 2.12 / 0.851 (CR-E2-17).
A1 then sets `voltage_sag` 0.76 → **0.851** (CR-E2-18).

`ASM-E2-R-EXT` is now a 6.5 mΩ mirror of `P:electrical.r_ext_mohm`, kept only so that E3 and H1, which still read it,
re-run on F1's value. The script stops if the two differ. The id retires once they re-point.

**Pack heating** (`CALC-E2-HEAT`, adiabatic, pessimistic currents). A cold morning gives 22 W in hover and +20 K
(10 → 30 °C). A hot morning gives 15 W and +13 K (30 → **43 °C** at landing), against a 50 °C limit
(`CL-E2-PACK-T-END`, margin 13 %). E3 owns the pod heat path and re-runs on these tables (CR-E3-10).

## 4. Flight-controller battery settings (for F4)

| Parameter | Value | Why | Claim |
|---|---|---|---|
| `BATT_CAPACITY` | 6500 mAh (lower it to the measured capacity) | counter base | `T-E2-CAPACITY` |
| `BATT_LOW_MAH` → QRTL | **2600** mAh remaining (was 2700 in R2) | 1 300 mAh reserve + 1 265 mAh to back-transition, descend, 60 s return and 30 s landing hover (pessimistic) | `CL-E2-BATT-LOW-MAH` |
| `BATT_CRT_MAH` → QLAND | 1300 mAh remaining | the 20 % reserve | `CL-E2-BATT-CRT-MAH` |
| `BATT_LOW_VOLT` / `BATT_CRT_VOLT` | 14.0 / 13.6 V (3.50 / 3.40 V/cell) | voltage backup | — |
| `BATT_FS_VOLTSRC` | 1 (sag-compensated) | a 0.76 V/cell sag at full throttle must not trigger the failsafe | `CL-E2-SAG-V-WORST` |
| `BATT_ARM_VOLT` | 16.4 V (4.10 V/cell) | the mAh counter assumes a full pack at boot, so the aircraft refuses to arm on a used pack | — |
| `Q_M_BAT_VOLT_MAX` / `_MIN` | 16.8 / 13.2 V (F4's values) | thrust compensation; it saturates below 13.2 V, which happens only at full throttle on a low, cold pack (11.87 V); E1's T/W already includes that | `CL-E2-V-BUS-WORST` |

Rule: **one fully charged pack per sortie.** A part-used pack is never re-flown on the same day.

## 5. Charging and balancing

| Item | Value | Source | Status |
|---|---|---|---|
| Charger | HTRC C150, 150 W, one port | `SRC-E2-HTRC-C150` | `UNVERIFIED` |
| Charge lead | one AS150U-to-charger lead per charger (CR-F1-04), 12 AWG, balance lead to the JST-XH port | F1 BOM (CR-F1-12) | `PROPOSED` |
| Charge current | 6.5 A (1C; 109 W at 16.8 V, inside 150 W) | `CALC-E2-TESTDAY` | `PROPOSED` |
| Time per pack from the 20 % line | 59 min (CC to 85 %, CV 20 min) | `CL-E2-CHARGE-MIN` | `UNVERIFIED` |
| 2 packs (D-12) / 4 packs back to back | 2.0 / 3.9 h, attended, the afternoon before a flying morning | `CL-E2-CHARGE-H-4` | `UNVERIFIED` |

- Always use balance mode, with the balance lead connected. At full charge the cell spread must be ≤ 0.02 V.
  Quarantine the pack if the spread after a 1 h rest is > 0.05 V, or if any cell is below 3.0 V.
- Charge 4.20 V/cell only on the day before flying. If the pack will not fly within 48 h, return it to storage
  (3.80–3.85 V/cell, charger STORAGE mode).
- Inspect for puffing, dents and lead damage before every charge. Log every charge: pack id, mAh in, cell voltages,
  IR if the charger shows it.

## 6. Storage, transport and damaged packs

| Situation | Rule |
|---|---|
| Storage | 3.80–3.85 V/cell, each pack in a LiPo bag, bags in the ammo can with **its rubber gasket removed** (vents, does not pressurise), room temperature, away from flammables |
| Drive to RFS | Charged packs in bags in the ammo can, in the cabin (warm packs, see §3), never left in a closed car in the sun |
| Field | Ammo can and sand bucket 5 m from the pilot box. Packs come out only to fly. IR thermometer reading at landing |
| Charging | Attended, on a non-flammable surface, extinguisher or sand at hand, never in a car (R-BATT-HANDLING). H3 names the room |
| After a crash | Unplug. If dented, puffed, hot or smelling: into the ammo can or sand outdoors, observe ≥ 30 min, never charge it again |
| Retire a pack | Capacity < 80 % of nameplate, IR > 1.5 × new, puffing > 2 mm, or any crash damage. Discharge to 0 V on a resistive load, then household hazardous-waste drop-off (H3 confirms the site) |
| Shipping | Ovonic US warehouse, ground (UN3480). 96.2 Wh < 100 Wh, so a spare pack may be carried on an airliner in cabin baggage if ever needed (`SRC-E2-FAA-PACKSAFE`) |

Mark the packs `E2-P1` and `E2-P2` on tape, plus the in-service date. One logbook line per charge and per flight.

**Transport box** (CR-D7-07). The packs travel in the LiPo bag beside the transport box, never inside it. The box
with both packs weighs 7.00 kg against a 6 kg limit, and the packs must stay reachable without opening the airframe
box.

**Re-termination XT60 → AS150U** (CR-F1-04, F1 D-32). Done once per pack on arrival, after steps 1–3 of §8 and before
the first charge, by one trained member with a second present:

1. Pack at storage voltage (3.80–3.85 V/cell), on a non-flammable mat, LiPo bag and sand at hand, safety glasses on.
2. Cut and terminate **one lead at a time**, never both cut at once; tape the other lead's end while working.
3. Heat-shrink both solder cups; polarity and the anti-spark side as on F1's drawing; 100 W iron.
4. Check polarity with a meter at the new plug, then every cell on the balance lead (spread unchanged).
5. Record the date in the `pack_log.csv` notes. The cut XT60 goes into the parts bin, not the pack bag.

## 7. Packs needed for a test day (D-12: 2 sorties)

| Item | Value | Claim | Status |
|---|---|---|---|
| Sortie (ground checks + full mission, base) + ground turnaround | 19.3 + 20 min | `CALC-E2-TESTDAY` | `PROPOSED` |
| Sorties the 07:00–10:00 window allows | 4 | `CL-E2-SORTIES-WINDOW` | `UNVERIFIED` |
| **Sorties planned per test day, 2 packs** | **2** | `CL-E2-SORTIES-PACKS` | `UNVERIFIED` |
| Window used by the 2 sorties | 58.5 of 180 min | `CL-E2-WINDOW-USED` | `UNVERIFIED` |
| Charge the afternoon before | 2.0 h attended | `CL-E2-CHARGE-H-4` | `UNVERIFIED` |
| Packs 3–4 | deferred (D-12): bought only if the post-order reserve stays ≥ $396 | CR-E2-05 | `PROPOSED` |

I2 plans every test day at 2 sorties. Use the spare 2 h of the window for ground work (CG balance, thrust checks,
re-briefs), not extra flights: a part-used pack is never re-flown. If packs 3–4 are bought later, the window allows
4 sorties and the charge afternoon becomes 3.9 h.

## 8. Pack acceptance and the first weigh (CR-A3-08)

The ~20 Nov order holds both flight packs. On arrival, before any charge:

| Step | What | Record in `team/E2/pack_log.csv` | Pass |
|---|---|---|---|
| 1 | Arrival cell voltages (storage charge expected) | `cell_v_on_arrival` | every cell 3.75–3.90 V, spread ≤ 0.02 V |
| 2 | Weigh on a 1 g scale, leads included | `mass_g` | ≤ 680 g (A3 growth bound) |
| 3 | Calipers L × W × H and lead exit | `length_mm` … `lead_exit_mm` | fits the D2 bay 160 × 52 × 53 mm |
| 4 | IR load step at 25 °C (`T-E2-IR`) | `ir_mohm_cell_25c` | ≤ 5 mΩ/cell |
| 5 | 1C capacity on the stand (`T-E2-CAPACITY`) | `capacity_mah` | ≥ 6 000 mAh |

Then re-run the script. It reads `pack_log.csv`, carries the heaviest weighed pack in `CL-E2-PACK-MASS` and marks
`T-E2-WEIGH` run. Decision on the mass: ≤ 550 g, nothing changes; 550–680 g, A3 replaces the 550 g line (the
roll-up's predicted mass already covers 680 g); > 680 g, return it and buy another 4S 6000–6500 SKU. Only then does
A1 set `checked` on `SRC-OVONIC-4S6500` (CR-E2-01b stands until the weigh).

## 9. Verification

| Test | What | Verifies |
|---|---|---|
| `T-E2-WEIGH` | 1 g scale and calipers on every pack on arrival, into `pack_log.csv` | `CL-E2-PACK-MASS` (R-PACK-MASS) |
| `T-E2-CAPACITY` | 1C discharge to 3.5 V/cell on the thrust stand with the watt meter; pass ≥ 6.0 Ah | cruise, charge time |
| `T-E2-IR` | 20 A load step at 25 °C and 10 °C; pass ≤ 5 mΩ/cell at 25 °C | bus voltage at 100 A, sag bracket, C-rate (T/W: `T-E1-STAND`) |
| `T-E2-MISSION-LOG` | DataFlash `BAT` against the phase table (±15 %), pack temperature at landing | budget, phase currents and durations, temperature |
| Twin flights (gate 1) | Replace `ASM-E2-HOVER-MARGIN` and B1's cruise claim with the logged hover and cruise currents, then re-run | every endurance claim |
