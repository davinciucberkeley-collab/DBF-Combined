# I1 Procurement / BOM: K09-L

> **R4, 2026-11-13 (supersedes the numbers below):** committed spend $1,631.07 baseline / $1,716.28 pessimistic, reserve $368.93 / $283.72 (short of $309 by $25.28), all-in pessimistic reserve +$20.45. See `ORDER-PLAN.md` and `bom_summary.json`; the figures in the table below are from I1-R1.

Revision I1-R1, 2026-11-09. Status `PROPOSED`: every price is `UNVERIFIED` until the order-day re-read (`T-I1-LISTINGS`).
Files: [`BOM.csv`](BOM.csv) (one line per purchase) · [`ORDER-PLAN.md`](ORDER-PLAN.md) · `build_bom.py` → `claims.json`, `bom_summary.json` · [`CHANGE-REQUESTS.md`](CHANGE-REQUESTS.md).
Re-run: `python -I redesign/team/I1/build_bom.py` then `python -I redesign/proofs/build_graph.py` (my claims re-run without drift; the build still fails on B1/B3 drift that is not mine).

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Spend at order, baseline | 1 569.03 | USD | `CL-I1-SPEND-BASE` | `UNVERIFIED` |
| Spend at order, pessimistic | 1 680.35 | USD | `CL-I1-SPEND-PESS` | `UNVERIFIED` |
| Reserve, baseline (planned >= 150) | 430.97 | USD | `CL-I1-RESERVE-BASE` | `UNVERIFIED` |
| Reserve, pessimistic (>= 309, +3 %) | **319.65** | USD | `CL-I1-RESERVE-PESS` | `UNVERIFIED` |
| Early order ~20 Nov (incl. tax, shipping `EST`) | 996.88 | USD | `BOM.csv` `EARLY` | `PROPOSED` |
| December order 15 Dec | 396.31 | USD | `BOM.csv` `DEC` | `PROPOSED` |
| Store pick-up (XPS, box, jig, ammo can) | 170.84 | USD | `BOM.csv` `LOCAL` | `PROPOSED` |
| Tie-break bridge difference | -0.01 | USD | `CL-I1-BRIDGE-DELTA` | rounding only |
| Tax rate | 10.25 | % | `params.json#requirements.tax_rate` | Measure V (+0.5 %) leading, date unknown |

Bridge from the tie-break's $1 678.58 pessimistic spend: servos +$9.98 (ES3005HV ×2 replace the $30 allowance), tubes -$4.32 (1 Aloft + 2 at overseas price replace 3 overseas), Small Parts adapters +$23.95, M3×8 screws +$2.00, second ESC pack -$30.00; sum +$1.61 × 1.1025 = +$1.77 → $1 680.35.

## Action items from the 20 Nov order brief

| Item | Result |
|---|---|
| Electronics in the early order | `ORDER-PLAN.md` early table: motors, ESC pack, props, FC, GPS, RX, TX, cells, charger, test gear, $996.88 |
| Two Ovonic 4S 6500 packs, no 4000 fallback, no packs 3–4 | one two-pack `P01` $79.25; packs 3–4 are gated line X04 (D-12). Listing title reads "XT60 to TRA plug": confirm XT60 |
| One US-stock 22×20×1000 tube (Aloft, CR-J1-07) | `W03` $24.00 in the early order; the December tubes follow C4's bend test (Aloft or overseas) |
| 8 × 11×5.5MR/MRP + 4 × 11×4.5MR/MRP (CR-E1-12) | `B03` 8, `B04` 4, $3.83 each, `CHK` on the APC page |
| Optional 11×5.5E pair (CR-B4-11) | not ordered: gated line X03, $18.39 |
| Re-check LANRC 45 A listing | **not confirmed**: Amazon 503, search finds no US LANRC 4-pack. Open it before 20 Nov; fallback Tekko32 +$60 |
| Re-check SunnySky page | page 429; search of the vendor page shows KV900 $24.99, 60 in stock; price carried as `CHK` by snippet only |
| Reserve >= $309 pessimistic | **met at $319.65 only by deferring the second ESC pack (X01, $33.08)**; with it, $286.57 |

## What the team must know

- The pessimistic margin is $10.65. Any new line above that fails the gate; the sanctioned lever is deferring the airspeed sensor (+$66.14, DECISION section 5.1).
- Not itemised by any owner: the $124.01 wiring/hardware kit is one lump (`CR-I1-01`). Servo `M01` is a placeholder for D6.
- Prices from `cost.csv` dated 2026-10-01 … 2026-11-01 are carried, not re-read (`CARRY`/`EST` in `BOM.csv`).
- Subsystem `parts.csv` exists only for propulsion; wing, fins, pod, landing, power, avionics, harness, mechanisms, transport have none yet, so those lines come from `cost.csv` and the tie-break (`CR-I1-01`).

## How to verify

| Check | How |
|---|---|
| Totals | `python -I redesign/team/I1/build_bom.py` asserts the bottom-up pessimistic spend equals the tie-break bridge within $0.02 |
| Prices | on 20 Nov and 15 Dec open each listing in `ORDER-PLAN.md`, log in `listing_log.csv`, re-run |
| Arrival | weigh packs, motors, ESCs, tube; confirm connector (`T-I1-ARRIVAL`) |
