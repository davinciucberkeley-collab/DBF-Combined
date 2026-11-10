# E1 Propulsion — summary

Status: performance `UNVERIFIED` (catalogue data; the thrust stand has not run) · stations `MODELLED` (Fusion
module; `check.py` propulsion `ok`; 4 prop keep-out ERRORs, all on the motor tube) · prop clearance **`FAIL`** (21.0 mm
vs 25 mm; fix proposed, A1/D3 to decide). Revision 7, 2026-11-10. Detail: [`PROPULSION.md`](PROPULSION.md). Model and claims:
`propulsion.py` → `claims.json` (64 claims); clearance probe `prop_clearance.py` → `prop_clearance.json`.
Subsystem: [`subsystems/propulsion/SPEC.md`](../../subsystems/propulsion/SPEC.md). Requests:
[`CHANGE-REQUESTS.md`](CHANGE-REQUESTS.md) (rev 7: CR-E1-48 to -50; rev 6: CR-E1-44 to -47).

## Decision

| Item | Choice | Price | Status |
|---|---|---|---|
| Motor | SunnySky X3108S KV900 (5, 1 spare) | $24.99 | `UNVERIFIED` (R, I0 agree across 2 listings) |
| ESC | LANRC BLHeli_S 45 A, Bluejay, carried stripped of power leads (8, 4 spare); fallback Tekko32 F4 45A AM32 | $7.50 / $22.50 | `UNVERIFIED` / `CHECKED` |
| Prop | APC 11×5.5MR/MRP (8) + 11×4.5MR/MRP (4, stand A/B) | $3.83 | `CHECKED` (D-05) |
| Prop adapter | Bolt-on M6×1, 2 RH + 2 LH (Small Parts CNC set), M3×4 under D-58; M3×5 if the bell allows | $23.95 / set | `CHECKED`, out of stock |
| Current limit | `Q_M_BAT_CURR_MAX` 100 A | — | `PROPOSED` |
| Mount stand-off (to A1, CR-D3-26) | `face_ahead_m` 0.0025 → **0.0075 m** | — | `PROPOSED` (CR-E1-44, -48) |
| Prop keep-out `KO-PROP-<st>` | swept envelope +10 / −6 mm + 25 mm; exempt list = own motor, adapter, prop only | — | `MODELLED` (rev 7) |

## Key numbers (2.6 kg gate, 11×5.5MR, cruise 16 m/s)

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Hover thrust per motor (download 1.06, cant 7°) / pack current | 6.81 / 27.3 | N / A | `CL-E1-HOVER-T`, `CL-E1-HOVER-I-55` | `UNVERIFIED` |
| T/W fresh pack with the limiter / worst pack state (limits 2.0 / 1.6) | 2.47 / 2.12 | — | `CL-E1-ILIM-TW-FRESH`, `CL-E1-TW-WORST` | `UNVERIFIED` |
| Per-motor current with the limiter / unlimited burst at 16.8 V | 24.75 / 51.6 | A | `CL-E1-ILIM-I`, `CL-E1-IMAX-168-55` | `UNVERIFIED` |
| Pack current with the limiter (A2 lists it under `R-ESC-CURRENT`) | 100 | A | `CL-E1-IPACK-LIM` | `UNVERIFIED` |
| Cruise propulsion power (16 m/s) / limit | 234 / 240 | W | `CL-E1-CRUISE-P-55` | `UNVERIFIED` |
| Motor out in hover: T/W left | 1.07 | — | `CL-E1-MOTOROUT-TW` | `UNVERIFIED` |
| Propulsion mass vs allocation (D-48) | 462.0 / 462 | g | `CL-E1-MASS-PRP` | `UNVERIFIED` (weigh) |
| Prop plane to collar ÷ 0.14 D / ESC strap-slot ratio | 1.01 / 1.05 | — | `CL-E1-CAD-PROP-GAP`, `CL-E1-ESC-SLOT` | `MODELLED` (rev 5 FAILs closed) |
| **Blade swept volume to CF motor tube (sense −1)** | **21.1** | mm | `CL-E1-TIP-GAP-TUBE` | **`FAIL`** (limit 25) |
| `face_ahead_m` needed / proposed → tube gap | 0.0065 / 0.0075 → 26.1 | m / mm | `CL-E1-FACE-AHEAD-FOR-CLR`, `-TIP-GAP-AT-75` | `PROPOSED` |
| Keep-out reach fwd / aft of hub mid-plane / half-length | 35 / 31 / 33 | mm | `CL-E1-KO-FWD`, `-KO-AFT`, `-KO-HALF` | `MODELLED` |
| `check.py` keep-out ERRORs at `face_ahead` 0.0025 / 0.0060 / 0.0065 / 0.0075 | 4 / 4 / 0 / 0 | — | `prop_clearance.json` (in-memory trials) | `CHECKED` |
| Adapter screws: bell thread needed for D-58 / free depth for M3×5 | 2.5 / 4.0 | mm | `CL-E1-ADAPTER-THREAD-D58`, `-M3X5-DEPTH` | `UNVERIFIED` (measure) |
| ESC envelope for B4: proud of the pad / frontal | 7.5 / 172.5 | mm / mm² | `CL-E1-ESC-PROUD`, `-FRONTAL` | `UNVERIFIED` |

## Rev 7: KO-PROP blocker (8 ERRORs on FIN-002/004/006)

| Item | Done | Status |
|---|---|---|
| Exempt the mount chain, or use an annulus with a hub inner radius | **Not done.** The tube's nearest point is r 143.8 mm, 4 mm outboard of the 139.7 mm tip, 26.8 mm aft: a tip gap. An exemption would hide 21 mm against 25 mm, and an annulus would not remove it | rejected, with evidence |
| Keep-out on E1's real envelope | `k9.prop_keepout(fwd=0.010, aft=0.006)` (A5's API); the symmetric ±10 mm is retired from the CAD | `MODELLED` |
| Effect | `check.py` keep-out ERRORs **8 → 4**. The bore boss (25.4 mm) and the plug (26.3 mm) clear; the motor tube (21.0 mm) remains on the 4 stations | `CHECKED` |
| Close-out | A1 / D3 set `face_ahead_m` ≥ 0.0065 (E1: 0.0075) → 0 keep-out ERRORs (CR-E1-48) | `PROPOSED` |

## Rev 6 actions

| Item | Done | Status |
|---|---|---|
| CR-A1-48 re-run | `propulsion.py`, `make_propulsion.py` on the R4 fins; CAD centroids regenerated on the reversed cant (motor 0.0156 / 0.321 / 0.1885 UR); `PRP-002` 7.6 g | `CHECKED` |
| CR-A5-21 | `k9.prop_keepout(..., rotate=rot, blade_half=0.010)` kept as A1 set it; true gaps measured beside it (probe) | `MODELLED` |
| CR-A4-43 / D-58 | M3×4 at 2.5 mm under D-58 (C6 lists it); condition `CL-E1-ADAPTER-THREAD-D58` in `T-E1-MOTOR-RM`; M3×5 if thread ≥ 3.0 mm and free depth ≥ 4.0 mm | `PROPOSED` (measure) |
| CR-D3-22, lead reach | base Ø ≥ 28 mm, 16 × 19 mm, hole ≥ 4.0 mm, leads vs 0.121 m in `T-E1-MOTOR-RM` | `PROPOSED` (motors mid-December) |
| Acknowledgements | 36 acknowledged, 0 pending (`E-HRN-13…20`, `-24…27`, `-34…37`, `E-TRN-17…20`, `E-FIN-61…68`, `-81…88`) | `CHECKED` |
| CR-B4-20 ESC envelope / `CL-E1-IPACK-LIM` to A2 | published / listed by A2 | closed |
| `ASM-E1-PACK` | kept: B4's `props.py` still reads it (CR-E1-46) | open |
| New: prop clearance after D-52 (CR-D3-26) | analytic calc + CAD probe; E1 proposes 0.0075 to A1 (CR-E1-44); surface test to A5 (CR-E1-45) | `FAIL` until A1 decides |

Checks (rev 7, 2026-11-10): `fusion/check.py` propulsion `ok`; FAIL overall on **4 KO-PROP ERRORs**, motor tube
FIN-002-L/R at 21.0 mm (was 16 box hits in rev 6, 8 after A5's hull test). WARN `mass` 462 g at zero margin
(floating point). `merge_check.py`: 0 propulsion errors. `build_graph.py`: no `CALC-E1` drift, no E1 errors (other
roles' drift remains). `plots.py` not re-run (local matplotlib lacks `packaging`); its figures do not depend on
anything changed in rev 6.

## Verify

`python -I redesign/team/E1/propulsion.py` → `python -I redesign/subsystems/propulsion/make_propulsion.py` →
`python -I redesign/team/E1/prop_clearance.py` (about 75 s) → `python -I redesign/fusion/check.py` →
`python -I redesign/proofs/build_graph.py`; hardware `T-E1-MOTOR-RM` (masses, base Ø and pattern, hole depth, bell
thread and free depth, lead length, ESC height, R, I0, 25 mm gauge at the tube), `T-E1-STAND`, `T-C6-PROPNUT`.
