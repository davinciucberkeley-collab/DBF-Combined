# QP-4 structures re-run (C1 / C2 / C4 / C6), concept A, 2026-11-15

D-185 as ruled, structure frozen at 473 g. Full detail: `qp/A/structures/iter3_run.md` and the section "Iteration 3 (D-185 as ruled)" at the end of `review/QP-3/STRUCTURES.md`. Scripts `iter3_run.py`, `iter3_gmwindow.py` (`python -I`). `EST` estimate, `CALC` computed. No git.

| Line | Result | Rating |
|---|---|---|
| Strongly coupled (>= 0.5; basis: one mode alone reaches the 30 m/s2 limit at coupling 1.6, so 0.5 = 32 % of it) in the 84-304 Hz band | none; spar modes in band are 0.46, response < 1.5 m/s2; nearest below 78 Hz vs 83.6 | PASS |
| Forced response 6,000-10,500 rpm, U 1.0 g mm, FC sum of axes | 19.6-20.1 at the 9,349 cap; 25-27 only at 10,500 (unreachable); cruise 10-11; one motor at cap 12-14 | PASS (MARGINAL at 10,500) |
| Hard-mounted FC, VIBE <= 30 | per-axis rms-equivalent 12.5-12.9 | PASS |
| Control band, GM >= 2 (A.param gains) | min 2.06 (yaw); 29-35 Hz arm modes GM 2.5+; pitch 12 Hz mode 2.8-3.6 | PASS |
| Same with cage modes +-20 % | 1.64 | MARGINAL: tap window pitch mode 12-16 Hz, roll 21-43 Hz, else re-tune |
| C1 at VD 24 | gust n 3.01 < 3.4; spar MS +2.73 (+2.2 at the 3.96 g stall pull) | PASS |
| D-187 elevon horn / lead / rod | hinge 0.146 N m vs servo 0.17-0.24; rod 12 N vs 339 N; lead 0.36 N (n 3.4), 1.26 N (12 g); horn 5 MPa vs 9.5 | PASS (servo margin +0.17) |
| Mass | 473 + 21 = 494 g | FAIL vs freeze; board waiver needed |

Actions: (1) board waiver for +21 g or offset (lighter elevons -4 g, 7.1 g balance at 45 mm -7 g); (2) tap-test the built cage against the 12-16 Hz window before the first tether; (3) measure elevon K and free play (FLUTTER step 5).
