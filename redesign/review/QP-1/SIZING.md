# QP-1 sizing: small quadplane (concept B, D-181), 2026-11-14

Reproduce: `python -I redesign/qp/sizing/sizing.py` (stdlib, prints everything below). Labels: `PUB` maker-published
(URL, read 2026-11-14), `U` price from a snippet or reseller, `EST` estimate, `-` unknown. Nothing outside `redesign/qp/` and this
file was edited; no git.

## Baseline

| Item | Value |
|---|---|
| MTOW | 2.06 kg (EST; 10 % contingency included) |
| Wing | span 1.20 m, chord 0.25 m, S 0.30 m2, AR 4.8, 6.9 kg/m2, Clark Y-like 12 % |
| Stall / 1.3 Vs / cruise | 10.1 / 13.1 / 17 m/s (CLmax 1.1 EST); L/D 5.8 at 17 m/s (best 7.3 at 12 m/s) |
| Lift | 4 x T-Motor MN3110 KV700 + APC 12x4.5MR, 4S; hover 4.2 A per motor (55 % throttle), 291 W pack |
| T/W | fresh 2.21 (limit 2.0), at sag 1.82 (limit 1.6); motor 13.0 A vs 21 A rating |
| Pusher | T-Motor MN2212 V2.0 KV780 + 9x6; cruise 131 W (8.9 A of 13 A); climb 0.5 m/s at 10.3 A, 1.4 m/s at 13 A |
| Pack | 2 x 4S 3000 mAh (44.4 Wh, 356 g); mission 25.0 Wh, need 34.7 Wh, margin 1.28x |
| Mission | cruise 204.5 s = 3.41 min (3.5 min requirement), hover-mode 180 s, transitions 2 x 12 s (EST) |
| Static margin | 12 % chord (EST), CG at 28 % chord, V_H 0.41, V_V 0.057 |
| Cost | about $1,806 against $2,000, margin about $194 (RESTUDY B: $1,625) |

## Sections 1-9: script output

Full tables (mass by subsystem, drag build-up, thrust and sag, CG, energy, cost, box) are printed by the script; the numbers
above are copied from it. Basis and sources for each input are in the script (`SRC`, per-row comments).

### Sources (all read 2026-11-14)
- MN3110 KV700, 14.8 V, 12x4 CF: 100 % = 1,290 g, 14.0 A, 207 W; 21 A continuous, 99 g with cables, $61.90: https://store.tmotor.com/goods.php?id=334 (PUB)
- MN2212 V2.0 KV780, 14.8 V, 9545B: 918 g static, 10.3 A, 152 W; 13 A continuous, 65 g, $46.90: https://store.tmotor.com/goods.php?id=388 (PUB)
- 4S 3000 mAh 70C pack $36.99 (XT90) chinahobbyline.com snippet (U); 356 g from RESTUDY-2026-11-14.md B
- APC 12x4.5MR $4.49 getfpv.com snippet (U)

### Mission basis (A2.md section 2.1, adapted)
Speed 17 m/s and the 300 m racetrack at 30 deg bank are unchanged (turn radius 51.0 m, lap 54.2 s; cruise 15 s settle + 2 laps +
go-around lap + half-lap = 204.5 s). The 3.0 min hover-mode total (25 + 35 + 50 + 30 + 40 s) is kept: VTOL climb, descent, landing
and go-around do not change for a quadplane, and the 35 s hold is retained as a conservative placeholder. New for the quadplane:
forward transition 12 s (lift motors at 60 % hover power + pusher full) and back transition 12 s, both EST. Stall in the turn
10.9 m/s, far below 17 m/s.

### Box and span limit
A rigid airframe of 1.16 m length and a 1.20 m wing does not fit 1.25 x 0.55 x 0.45 m at any yaw angle (script check). The
airframe alone (booms, pod, tail; props off) is 1.16 x 0.53 x about 0.25 m and fits. **Baseline therefore needs a two-panel plug-in
wing, which deviates from strict one-piece**: this is a conflict to be decided (DECISIONS.md), not something chosen silently.
Span limit with removable panels: each panel at most the box length (1.25 m); the structural limit is the spar joiner and mass, so
1.20 m is kept from RESTUDY B (1.40 m) for the box. A strictly one-piece quadplane in this box would need a body of at most about 0.55 m.

## Open risks
1. One-piece rule versus the detachable wing (above).
2. Lift thrust uses the T-Motor CF 12x4 table with a 0.95 EST derate for APC props; T/W at sag 1.82 has room (limit 1.6 fails below derate about 0.83). Bench test replaces it. Fallback T-Motor 12x4 CF pair $38.90 (ligpower snippet, U).
3. L/D 5.8 is driven by four stopped props (CdA 0.0048, EST); the cruise and climb margins depend on it. Pusher climb 0.5 m/s at the published 10.3 A; the 9x6 prop and overall efficiency 0.45 are EST (no maker table for that prop).
4. Pack sag resistance 0.045 ohm and OCV at 20 % SoC are EST; the energy margin 1.28x rests on EST power; a 4S 2200 mAh pack (0.94x) is not enough.
5. CG: pack in the nose bay at -0.25 m with 60 mm slide gives SM 8-16 %; V_H is at the low end of typical (0.41); tail and wing AC placement are EST. Pod 0.93 m long.
6. Cost: MN3110 listed at $61.90 (maker store) to $90.90 (reseller, sold out); T-Motor shipping and import not priced (-). Margin about $194 stays above the $100 rule, but about $145 of resellers' spread would cut it to about $34, under the rule.
7. Rear lift discs overlap the wing trailing edge by 13 mm (hover download, EST), and the pusher plane is 30 mm behind the rear discs.
