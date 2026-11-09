# Research findings: flight-control

> Recovered summary (2026-11-09). The research agent could not write its full report; this is its returned summary. Sources were cited in the agent text but are not preserved here: treat claims as UNVERIFIED unless a card cites them.

I didn't write FINDINGS.md: the harness blocked the file write and told me to return the findings as text. The folder research/flight-control/ now exists but is empty.

Ranking by controls risk, lowest first (my own scores, from ArduPilot/PX4 docs and forum reports):
1. Lift+cruise. PX4 docs call it the easiest to control, and it is ArduPilot's default sim frame.
2. Tilt-tricopter. Its tilt servos and motor alignment are flight-critical.
3. Quad tailsitter. Both autopilots' docs warn about hover in wind.
4. Quad tiltrotor.
5. Dual vectored tailsitter.
6. Dual non-vectored tailsitter. PX4 says it is much harder to tune.
7. Tilt-wing. Its transition is research-grade.

Hardware: buy an H7 flight controller (Matek H743-WING V3 about $125, or Pixhawk 6C Mini about $177), not an F405 (1MB flash, no Lua). Add an airspeed sensor (about $47-75) and a GPS (about $48). The core avionics come to about $220-272.

Use ArduPilot Plane.

The sources, comparison tables and 10 implications are ready to return as text if the workflow allows it.
