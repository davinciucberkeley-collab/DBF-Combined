# Chosen configuration: K09-L quad tailsitter

Decided 2026-11-09 by the orchestrating agent at the team lead's request ("choose the configuration"), after the
configuration study (`config-study/README.md`) and a tie-break (`config-study/tiebreak/DECISION.md`). Status:
**PROPOSED baseline for detailed design**; reversible on the conditions below until the mid-December order.

## What it is
A flat flying wing (~1.15 × 0.30 m, hot-wired XPS core, tape/laminate skin, one carbon spar) with two fins at about
±0.32 m span. Each fin carries a vertical carbon tube with a motor at each end: **four fixed motors in an X**, two
above and two below the wing. It **stands on its four fin tips**, takes off as a quadcopter, **pitches 90° nose-down
onto the same four motors** for cruise, and pitches back up to land. **Two elevons** give roll and pitch in cruise
(ArduPilot Plane, `Q_TAILSIT_ENABLE 1`, motors in tailsitter mixing). An **airspeed sensor** is fitted for gain
scheduling. Class-S propulsion (SunnySky X3108S-class motors, APC 11×4.5MR-class props, 4S LiPo, two flight
packs). Transported in **one piece** in a ~1.25 × 0.55 × 0.45 m box; field set-up ≈ 5 min, one person, no tools.

Starting numbers (all to be re-derived by the design team; sources in `config-study/cards/K09/` and
`config-study/tiebreak/`): sized mass ≈ 2.48 kg, mass gate ≈ 2.6 kg; hover T/W ≈ 2.5; cruise ≈ 15 m/s; stall
≈ 11.2 m/s; transition ≥ 14.6 m/s; ≈ 12–19 min cruise after 2 min hover; spend ≈ $1,679 pessimistic, reserve ≈ $321
(≥ one $309 crash).

## Why this one
- **Only shortlisted concept that passes the budget gate on pessimistic numbers** with a reserve covering one realistic
  crash (lean K01 −$108, K19 −$76 against the same gate).
- **Fastest to build and to repair** (≈ 115 team-hours pessimistic to first hover, week 3–4; crash repair ≈ $20 and
  2–4 days by re-cutting a foam core), which protects the end-of-April deadline.
- **Simplest airframe:** four motor stations, two servos, no tilt mechanism, no field joints, one-piece transport.
- **Wind is workable:** Mar–Apr mornings (07–10) at the nearest bay-shore station are ≤ 5 m/s in ~92 % of hours
  (≈ 5–5.7 usable mornings/week) — `tiebreak/wind/WIND.md`.

## The price (accepted, stated plainly)
- **Highest flight risk of the shortlist.** No logged elevon quad-tailsitter transition in this size class was found;
  estimated P(full transition round trip by end of April) ≈ 0.55–0.65 vs ≈ 0.65–0.70 for the lean quadplane K01.
- **Any motor/ESC failure is fatal** in both modes. **Morning-only flying** with a 5 m/s wind limit on the flight card.
  Landing on fin tips is the recurring damage mode.

## Mandatory de-risking (before the mid-December order)
1. Build and fly a **$40 foam-board twin** (Box Kite guide) on the real motors, FC and pack: hold position within 1 m
   in 5 m/s; then a transition.
2. **Fixed-wing tune first:** hand-launch and tune it as a plain flying wing before any transition attempt.
3. ≥ 10 h **SITL** and a stable ArduPilot Plane tailsitter build confirmed for the chosen flight controller.
4. **Handheld anemometer at RFS** vs the RCMC1 station.
5. Early order (~20 Nov) of transferable electronics and carbon tubes so the twin flies on real hardware.

## Reverse to K01 (lean twin-boom quadplane, `config-study/tiebreak/k01-lean/`) if
- the twin fails the 5 m/s hover test or cannot complete a transition before the December order, or
- K01-lean's pessimistic reserve is verified ≥ $309 (tool loan in writing, board in stock, independent skeptic), or
- RFS wind measures ≥ 1.4 × RCMC1, or the team wants hover motor-out survivability.
Other reversals: a bought PNP accepted as "student-built" → B08; Maker Passes charged to this budget → re-run Gate 1.

## What the design team builds on
- Requirements: `config-study/REQUIREMENTS-PROPOSED.md` (re-derived by A2 for K09-L).
- Inactive roles in `TEAM.md` for this configuration (expected): **C4/D3 booms** (fin tubes replace them, owned by
  the fuselage/fin designers as re-scoped by A1), **D4 tail** (fins only, merged with the wing/fin subsystem), the
  pusher. Landing (C5/D5) becomes the fin-tip feet. The chief engineer (A1) finalises this.
- Previous decisions D1–D15: see `config-study/README.md` §5.2 for what carries over.
