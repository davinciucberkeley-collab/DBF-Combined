# Research findings: components-cost

> Recovered summary (2026-11-09). The research agent could not write its full report; this is its returned summary. Sources were cited in the agent text but are not preserved here: treat claims as UNVERIFIED unless a card cites them.

FINDINGS.md was not written: the harness blocks subagents from writing report files. The cost model is saved as cost_model.py (`python -I cost_model.py`); every total below comes from it.

Totals include 10.25 % Berkeley tax (CDTFA, effective 2026-10-01), shipping, spares and a ground kit. Prices are mostly vendor pages from Oct–Nov 2026.

| Config (class) | Total | Reserve |
|---|---|---|
| 2–2.5 kg, 4S, at most 1.5 m span (quad tailsitter, tilt-tri, tilt-quad, twin tailsitter, quadplane 4+1) | $1,492–1,636 | $364–508 |
| 4–6 kg, 6S, quadplane 4+1 | $2,003 | −$3 |
| 4–6 kg, 6S, octo 8+1 | $2,350 | −$350 |

One bad crash costs about $309. The fixed floor is about $600 ($213 avionics, $265 ground kit, $124 wiring).

Implications:
- Choose layout on buildability, not parts cost.
- Each lift motor costs about $40 (2–2.5 kg) or $68 (4–6 kg).
- ELRS MAVLink telemetry costs $0; airspeed is optional.
- Stay at or under 12 FC outputs.
- Ask about borrowing kit first; nothing is assumed owned.
