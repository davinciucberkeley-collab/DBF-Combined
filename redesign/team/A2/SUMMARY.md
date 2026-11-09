# A2 systems engineer — requirements and verification matrix for K09-L

Status: `PROPOSED` requirement set, 2026-11-09. One inventory (`requirements.json`) drives the proof-chain nodes, the
requirement document and the matrix: `python -I redesign/team/A2/build_requirements.py` (rebuilds the proof graph, < 2 s).

## What was produced

| File | What | Status |
|---|---|---|
| `team/A2/REQUIREMENTS.md` | 57 requirements in 8 groups, each with P-line, value, unit, source, owner, method (A/I/T/D); P1–P25 map; A2's limits; differences from the proposed set | `PROPOSED` |
| `team/A2/VERIFICATION-MATRIX.md` | requirement → owner → support → method → evidence files (present on disk?) → claims → margin → status, plus a by-owner table | live from `proofs/out/graph.json` |
| `team/A2/claims.json` | 39 new `R-…` requirement nodes + 39 `ASM-A2-…` limit nodes (`PROPOSED`); A1's 18 ids reused, none duplicated | builds `OK` |
| `team/A2/requirements.json` | the inventory (edit this, not the Markdown) | — |
| `team/A2/build_requirements.py` | validator + generator; exit 1 on a duplicate id, an unmapped P-line, an `R-…` id in the graph with no row | runs |
| `team/A2/CHANGE-REQUESTS.md` | 11 requests (A1 ×3, A3, A4, J1, B1/B2, F1, C1, H1–H3, J2) | open |

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Requirements (shared / new) | 57 (18 / 39) | — | `requirements.json` | `CHECKED` (validator) |
| P1–P25 lines mapped | 25 / 25 | — | `REQUIREMENTS.md` P-map | `CHECKED` |
| Requirements with ≥ 1 claim | 13 | — | `VERIFICATION-MATRIX.md` | — |
| Status today | 5 `CHECKED` · 1 `PROPOSED` · 51 `UNVERIFIED` · 0 `VERIFIED` | — | `proofs/out/graph.json` | — |
| Requirements failing | 4: `R-TRANSITION` −0.3 %, `R-MASS-GATE` −18 %, `R-STATIC-MARGIN` −126 % (CG range claims), `R-DISCONNECT` −50 % (XT60 burst) | — | matrix header | `FAIL` |
| Limits added by A2 | 39 (`ASM-A2-…`: n +3.0/−1.5, FoS 1.5, sink 1.5 m/s, 12 g, SITL 10 h, transition ≥ 50 m, …) | — | `REQUIREMENTS.md` last table | `PROPOSED` → CR-A2-01 |

## What changed against REQUIREMENTS-PROPOSED.md

- Structures had no requirements: added `R-LOADS`, `R-STRUCT-MARGIN`, `R-FIN-TUBE-JOINT`, `R-VIBRATION`, `R-PACK-RETENTION`, `R-LANDING-IMPACT`.
- Control had no pass/fail numbers: added `R-HOVER-AUTHORITY`, `R-CRUISE-AUTHORITY`, `R-DIRECTIONAL`, `R-SERVO-TORQUE`, `R-AIRSPEED`, `R-COMPASS`, `R-RC-LINK`.
- P13 "30 A per motor" is the 14.8 V table; `R-ESC-CURRENT` tests ≤ 36 A at 14.8 V and ≤ 45 A at 16.8 V on the stand.
- P8 gust case: the 36° lean at 8 m/s is within 1° of the 37° tip-over angle, so `R-GUST-LEAN` asks for attitude-limit and thrust headroom only; an upright landing in 8 m/s is not required.
- P6 fin height 0.40 m vs `params.json` 0.38 m; P14 "≥ 3 packs" vs the decided 2: the set follows `params.json` (CR-A2-02).

## Open issues

1. 44 of 57 requirements have no claim yet; the by-owner table in the matrix lists each role's open ids.
2. Four requirements fail on today's claims (table above); owners B1/B2, A3, B3, F1 (CR-A2-04, -07, -08).
3. A3's CG-range, A5's layout-CG and J1's vibration/yaw claims verify the wrong or no requirement until they point at the new ids (CR-A2-04, -06).
4. The 39 limits are A2's `PROPOSED` numbers until A1 adopts them into `params.json` and the owning roles re-derive them.
5. SITL cannot run on the design machine: `R-PILOT` and the SITL half of `R-FAILSAFES` stay `UNVERIFIED` until the team runs them.
