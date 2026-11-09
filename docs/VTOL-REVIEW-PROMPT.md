Build an engineering design review for our student hybrid lift + cruise VTOL
in the same house style as our earlier gripper review. The style is
specified in docs/reference/REVIEW-STYLE.md — read it first and match its
format, layout, components and tone exactly. Do not reuse any gripper
content or numbers. Adapt sections wherever the VTOL needs something
different; the map below is my starting point, not a constraint.

PROJECT CONTEXT
- University student project. First build priority: a hybrid lift + cruise
  VTOL, i.e. vertical lift rotors for takeoff/landing plus a pusher prop and
  fixed wing for cruise, with lift rotors stopped in cruise.
- Reference configurations: docs/reference/lift-cruise-reference.png shows
  BETA Alia (4 lift rotors, pusher, high-aspect wing) and a generic
  "Lift Plus Cruise" layout (8 lift rotors on booms, pusher, conventional
  tail). Treat these as the concept starting points.
- Hard constraints: $2,000 total physical budget (all hardware, spares,
  batteries, test equipment, shipping, tax); built and flight-tested by the
  end of April 2027.
- Size: a real, flyable aircraft, but portable: a team of 4 must be able to
  move it routinely. Working target: 8–15 kg MTOW, 2–3 m span, hard cap
  under 25 kg (55 lb). It must break down so the largest piece fits in a
  standard car, and two people must be able to carry it assembled. Treat
  the exact MTOW as a design output: size it from the budget and mission,
  then show me where it lands in the range and why.
- Stage: concept. There is little or no CAD, no requirements doc, and no
  sizing scripts yet. Repo contents: <list any folders/files, or "none">.
- Scope: the real, physical aircraft only. Ignore any browser flight-sim
  code you find; it was a design toy, not a source for numbers, geometry
  or control logic.

STEP 1 — Design basis and section map (stop and wait for my OK)
a) Draft numbered requirements (R1…Rn) from the constraints above plus
   reasonable student-UAV assumptions: MTOW within the stated size limits,
   mission (hover → transition → cruise → transition → land), endurance,
   cruise speed, payload if any, hover thrust-to-weight margin, motor-out
   tolerance, cost cap, schedule, portability, and legal compliance. Mark
   each as Given (from me) or Assumed, and list the assumptions I most need
   to confirm.
b) Confirm this section map against what exists:
   1. Overview: baseline concept in one paragraph, open decisions,
      workstream status, requirement status chips, budget and schedule KPIs.
   2. 3D model: if no CAD exists, build a simple parametric layout from the
      sizing numbers (fuselage, wing, booms, rotor discs, pusher), clearly
      labeled "concept geometry", with a parts and mass table and the
      breakdown/transport split.
   3. Concepts: 4-lift (Alia-style) vs 8-lift vs any other credible
      layouts; morphological chart; Pugh matrix with a stated datum.
   4. Mass & power (replaces Mass & torque): weight build-up, hover power
      (momentum theory with a figure of merit), cruise power from L/D,
      battery sizing, endurance; live back-calculation chain plus
      sensitivity sliders.
   5. Propulsion (replaces Actuators): lift motors, pusher motor, props,
      ESCs, battery: a trade table with real part numbers and prices.
   6. Structures (replaces Finger FEA): wing spar and boom hand calcs,
      landing loads, joints for breakdown, material choice
      (foam/carbon/print).
   7. Budget & BOM (replaces Gears): itemized BOM against $2,000 with
      contingency, spares, a second battery, a crash-repair reserve, and
      the items that are cost risks. Show the cost of the 4-lift and
      8-lift layouts side by side at the chosen MTOW; if either can't fit
      under $2,000 with a spare battery and a crash reserve, say so in a
      red decision card.
   8. Testing & failure (replaces Dyno & fatigue): thrust-stand test plan,
      mission duty cycle, battery/ESC thermal, motor-out behavior, hard
      landing, weakest-link ranking.
   9. CG & stability (replaces Tolerances): CG envelope, lift-rotor thrust
      centroid vs CG in hover, static margin in cruise.
   10. Controls: flight controller choice (e.g. ArduPilot QuadPlane vs PX4
       VTOL; verify current support), flight-mode state diagram, transition
       table with airspeed and altitude thresholds, wiring and pins.
   11. Schedule & compliance (replaces Camera): milestones Oct 2026 → end
       of April 2027 with design freeze, order-by dates against shipping
       lead times, hover test, transition test; FAA/registration and
       campus flight rules (verify current rules).
   Add, drop or merge sections where that makes the review better; tell me
   why.

STEP 2 — Build the single self-contained HTML page per the spec.
- Every number cites its source: a repo file, a formula shown in the calc
  chain, or a URL with the date checked. Prices and specs must be looked up,
  not recalled.
- Estimates are labeled as estimates; unknowns get "—", never invented
  values.
- Every technical section ends with a numbered "What the team must measure"
  box (M1, M2…): what to measure, a cheap method a student team can use,
  and the threshold at which the design fails a named requirement.
- Any open decision that threatens the budget or the April deadline
  gets a red decision card.

STEP 3 — Verify.
- Re-check every cited number against its source.
- Re-run each formula in the calc chain independently and confirm it
  matches.
- Confirm the BOM sums to the stated total and stays under $2,000.
- Open the page at desktop and phone widths, in light and dark mode.
- Report anything you couldn't match to the spec.
