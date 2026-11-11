# Proof chains (claims map)

Every number in the redesign is meant to be traceable: **requirement ← claim ← calculation ← parameters ← sources**.
The graph has **4,204 nodes and 13,696 links**, built by `python -I redesign/proofs/build_graph.py`, which
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
| claim | 0 | 81 | 37 | 1564 | 1682 |
| calculation | 0 | 387 | 0 | 31 | 418 |
| parameter | 0 | 64 | 628 | 366 | 1058 |
| source | 0 | 73 | 0 | 98 | 171 |
| assumption | 0 | 0 | 283 | 245 | 528 |
| test | 0 | 0 | 141 | 0 | 141 |
| part | 0 | 0 | 0 | 147 | 147 |

VERIFIED needs a physical test, and nothing has been built yet, so nothing is VERIFIED. CHECKED means re-run and
compared to an independent calculation or simulation. 87 claims currently show a negative margin (FAILS flag);
see `STATUS.md` for which ones matter.

## Honest state (2026-11-11)

The last design rounds changed upstream numbers (CG range, CLmax, prop data), and those changes ripple down the
chain. After re-running the affected scripts, **158 stored values still differ slightly** from a fresh
re-run. They need these scripts re-run (some are long simulations):

| Script | Out-of-date values |
|---|---|
| `redesign/team/C4/sim_fin.py` | 61 |
| `redesign/team/E3/thermal.py` | 45 |
| `redesign/team/A5/cad_claims.py` | 14 |
| `redesign/team/C4/fin_structures.py` | 14 |
| `redesign/team/H1/ground_tests.py` | 11 |
| `redesign/team/D3/fins_calcs.py` | 10 |
| `redesign/team/C2/c2_claims.py` | 2 |
| `redesign/team/F1/power.py` | 1 |

To bring the whole chain current: run each script above (`python -I <script>`), then rebuild the graph. Known script
issues: `team/D5/feet_calc.py` fails on a missing FEA result (re-run `team/D5/sim/` first), `team/A5/cad_claims.py`
and `team/C4/sim_fin.py` take several minutes (the latter re-runs FEA).
