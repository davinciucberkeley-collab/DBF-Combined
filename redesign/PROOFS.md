# Proof chains (claims map)

Every number in the redesign is meant to be traceable: **requirement ← claim ← calculation ← parameters ← sources**.
The graph has **4,244 nodes and 13,815 links**, built by `python -I redesign/proofs/build_graph.py`, which
re-runs every calculation and flags any stored number that no longer matches (drift).

**Explore it:** the **Proofs ↗** link in the K09-L Explorer (double-click `00 - OPEN THE K09-L EXPLORER (double-click me).bat`,
or the artifact link), or open `proofs/viewer/index.html`. Search any id, click a node to see its equation, inputs,
outputs and sources, and walk the chain up to the requirement and down to the sources. Filter by status to see
everything still UNVERIFIED.

**Read it as text:** [`proofs/out/CHAIN.md`](proofs/out/CHAIN.md) (large; one section per requirement).

## What the graph contains

| Node type | VERIFIED | CHECKED | PROPOSED | UNVERIFIED | Total |
|---|---|---|---|---|---|
| requirement | 0 | 1 | 1 | 57 | 59 |
| claim | 0 | 84 | 37 | 1563 | 1684 |
| calculation | 0 | 418 | 0 | 0 | 418 |
| parameter | 0 | 64 | 630 | 366 | 1060 |
| source | 0 | 73 | 0 | 98 | 171 |
| assumption | 0 | 0 | 283 | 246 | 529 |
| test | 0 | 0 | 141 | 0 | 141 |
| part | 0 | 0 | 0 | 149 | 149 |

VERIFIED needs a physical test, and nothing has been built yet, so nothing is VERIFIED. CHECKED means re-run and
compared to an independent calculation or simulation. 90 claims currently show a negative margin (FAILS flag; 2026-11-11 after D-85: 87 after D-80…D-84, plus `CL-F2-MASS`, `CL-F2-I2C-LEN` and `R-HARNESS-INSTALL` from the routed harness), and
14 requirements inherit one; see `STATUS.md` for which ones matter.

## Honest state (2026-11-11, after the harness re-route and the D5-R6 landing parts list)

**The build is clean: 0 drift, 0 errors** (`OK: every stored number re-computes`; two warnings for transport part ids
TRN-102 / TRN-105 not in any `interfaces.json`). Every calculation re-runs to its stored outputs, so all 418
calculations are CHECKED. The rebuild takes about 4.5 min when the C4 FEA cache is warm.

What it took (from 547 build errors: 536 drifted values and 11 script errors):

- every drifted script re-run to a fixed point (the mass chain F2 harness 119.8 g → A3 → A1 → loads, performance,
  thermal, structures), including the C4 fin FEA (`team/C4/sim_fin.py`, cold run about 40 min (2 345 s) with the four parts
  in parallel: `sim/run_part.py stress|modes`, `sim/run_trial.py 0|1`);
- `team/D5/sim/fea_shoe_d5.py`: the leg-to-floor fillet was meshed as an exact arc, which left 8 tangled quads at its
  cusps; SU2 did not converge (6 609 MPa garbage) and the script stored it anyway. The fillet is now 6 chords labelled
  by surface, and a run that does not converge is refused. Shoe FEA re-run: +y 30.5 MPa, +z 38.8 MPa;
- `fusion/skeleton/make_skeleton.py` re-run (the skeleton still carried the D-48 allocations, so A5's cross-check stopped);
- `team/D5/make_interfaces.py` run on D5-R6 (lead decision), so the landing parts list and A3 now carry the real
  69.9 g (A3 retired its +5 g sleeve adder automatically);
- `team/D2/pod_claims.py` cited a requirement that does not exist (`R-TRANSPORT-FIT` → `R-TRANSPORT`).

Real design results the re-runs exposed (claims left failing, no allocation changed):

| Claim | Value vs limit | Margin |
|---|---|---|
| `CL-D5-MASS-TOTAL` / `CL-A3-ALLOC-WORST` landing mass (D5-R6 shoe: 1.2 mm walls, 2.8 mm rim, 25 mm engagement) | 69.9 g vs 48 g allocation | −46 % |
| `CL-A3-CG-X-PRED-RANGE` predicted CG x, 550 g pack at nominal | 52.6 mm vs range 46.6–51.4 mm (1.2 mm aft of the limit) | −51 % (range use 1.51) |
| `CL-A3-CG-X-STATIONS` worst CG x range use over the 546 / 551 / 590 g packs | 1.028 vs 1 | −3 % |
| `CL-A3-GATE-MARGIN-590` gate margin with the 590 g pack (was −9 %) | 67 g vs 100 g | −33 % |
| `CL-A1-PACK-ACCEPT` / `CL-E2-PACK-ACCEPT-KG` heaviest pack the 100 g overrun still covers | 536 g vs 556 g | −4 % |
| `CL-E2-PACK-MASS` 550 g pack carried in the budget vs that acceptance line | 550 g vs 536 g | −3 % |
| `CL-D3-TIP-STEP-MISMATCH` / `CL-D3-TIP-SQUARE` D3 fin tip vs the D5-R6 step | 13 mm vs 0.5 mm; ratio 0.78 vs 1 | fails |
| `CL-C4-SIM-SEP` fin station-mode separation from 1P/2P | 0.181 vs 0.20 | −9 % |
| `CL-C4-SIM-FACE-DRAWN` fin face hot-spot at the drawn D5 shoe, ultimate | 10.3 MPa vs 10 MPa | −3 % |

The mass gate itself still holds: basic 2 374 g, predicted 2 493 g against 2 600 g, gate margin 107 g against the
100 g first-build overrun (+7 %, was +31 %). The harness (120 g basic) stays inside its 123 g allocation.
