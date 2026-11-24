"""Plain-English layer for the concept A proof chain (presentation only; no number, limit or pass / fail rule lives here).

Read by render_readable_a.py, which joins it to out/graph.json and writes out/READABLE.md and out/readable.js (the Explorer's
Guide pages). Nothing in this file is read by build_graph.py, so the strict build cannot be affected by it.

Per claim (EXPLAIN[claim id]):
  g        group id (GROUPS)
  why      one plain sentence: what is being checked and why it matters to the aircraft
  formula  the formula in words and symbols
  sym      {symbol: meaning in words}; units come from the inputs table
  steps    [(name, python expression, unit, label)] evaluated in order over the calculation's inputs and outputs
           (the renderer substitutes the real values, shows the arithmetic and compares the last step with the stored value)
  ms       (stress, allowable, unit, load text) for margin-of-safety claims: MS = allowable / stress - 1, numbers copied
           from the cited structures file (not part of the strict chain; the renderer flags any disagreement)
  via      for a stored result (not recomputed here): the analysis that produced it and how to redo it
  real     how a student would check it in the real world
  limit_why  why the limit is what it is
  tab      {input symbol: (column names, row labels or None)} so a list input is shown as a table
Every number is read from the graph at render time, so an edit to a parameter can never leave this text stale.
"""

# ------------------------------------------------------------------ groups (reading order)
GROUPS = [
    ("mass", "Mass", "Will the aircraft weigh what we say it weighs? Every other number (thrust margin, stall speed, loads) is scaled by this one."),
    ("cg", "Balance: centre of gravity and static margin", "Does the aircraft balance in the right place, and will it fly straight (stay pitch-stable) in cruise?"),
    ("hover", "Hover thrust, motors and ESC", "Can four motors lift it with margin, and do the motors and speed controllers stay inside their current ratings?"),
    ("struct", "Structures and loads", "Do the tubes, joints, printed parts and foam survive the loads we expect, with the safety factor on top?"),
    ("cost", "Cost", "Does everything we buy fit inside the $2,000 limit, with room for prices that turn out higher?"),
    ("mission", "Mission, energy and range", "Does the battery last long enough for the mission, and does the aircraft stay inside the flying field?"),
    ("flight", "Flying qualities: stall, yaw, wind, control", "Can it be steered and held steady in hover, in wind, and in fast flight?"),
    ("aeroelastic", "Flutter, divergence and gusts", "Can the wing and elevons shake themselves apart at speed? Is there a safe gap to our top speed?"),
    ("vib", "Vibration", "Do the structure's natural frequencies stay away from the motor frequencies, and does the flight computer feel acceptable vibration?"),
    ("pack", "Packaging and the 3-D model", "Does it fit in a car, and does the CAD model assemble with no parts colliding?"),
    ("sched", "Schedule", "Is the build finished and flown by 30 April 2027?"),
]

# ------------------------------------------------------------------ how to read
INTRO = [
    "This is a checking list for the aircraft. Each card below is one claim: a number the design depends on, written so you can redo it yourself with a calculator.",
    "A claim is a number plus a limit. For example, 'the predicted mass is 1.466 kg and must be at most 1.467 kg'. Every card answers the same six questions, in the same order.",
]
HOWTO = [
    ("What is being checked", "One sentence: what the number is and why the aircraft needs it to be inside a limit."),
    ("The formula", "The rule that turns inputs into the result, with every symbol explained in words and units."),
    ("The inputs", "Each input with its value, unit and where it came from, named as a document, not an id. Inputs marked ESTIMATE have not been measured or confirmed yet. Inputs marked ASSUMPTION are a deliberate guess the team has written down."),
    ("The arithmetic", "The inputs put into the formula, step by step. Redo it on a calculator; you should get the same answer to the digits shown."),
    ("The result and the margin", "The result next to its limit, and how much room is left. A positive margin is a pass. A margin of +5 % means the result has 5 % to spare."),
    ("How to check it in real life", "The test or measurement that would confirm it on a real aircraft. Tests marked 'planned' have not been run: nothing is built yet."),
]
STATUS_WORDS = [
    ("UNVERIFIED", "The arithmetic works and the limit is met, but at least one input is an unconfirmed estimate or an upstream claim is itself unverified. Treat as 'probably fine, not proven'."),
    ("CHECKED", "The arithmetic works, the limit is met, and every input is traced to a repo file or vendor source that was compared on the date shown. Still no physical test."),
    ("VERIFIED", "A physical test has been run and passed. No claim has this status yet: nothing is built."),
    ("PROPOSED", "A value with a written basis but no calculation yet."),
]
NUMBER_RULES = [
    "Results are shown to 5 significant figures and inputs as stored (up to 6), so a calculator should land on the last digit shown give or take 1.",
    "'Stored, not recomputed' means the number comes from a report written by a bigger analysis (finite-element run, simulation, CAD collision check). The card names that report and how to rerun it; this chain does not redo it.",
    "Margins use the project's rule: for a limit that is not zero the margin is the fraction of the limit left over; for a limit of zero (margin of safety, overlap counts) it is the signed distance to zero in the claim's own unit.",
]

GLOSSARY = [
    # (term, meaning, section)
    ("Concept A", "The aircraft being built: a scaled quad tailsitter. About 1.47 kg, 0.90 m wing, four motors in an X, sits on its fin tips, takes off like a quadcopter, pitches 90 degrees and flies like a plane, then pitches back to land.", "Aircraft"),
    ("Tailsitter", "An aircraft that takes off and lands standing on its tail. Here the whole aircraft tips forward to change between hover and wing-borne flight.", "Aircraft"),
    ("Hover mode / cruise mode", "Hover: nose up, the motors hold it up like a quadcopter. Cruise: nose forward, the wing makes the lift, as in an ordinary plane.", "Aircraft"),
    ("Transition", "The few seconds in which the aircraft pitches between hover and cruise. Thrust and control are tight here.", "Aircraft"),
    ("Cage / hub / arms / bridge", "The printed and tube structure that holds the four motors. Arms are the carbon tubes to the motors, the hub joins them, the bridge tube carries the hub load into the wing spar.", "Aircraft"),
    ("Elevon", "A wing flap that works as both elevator (pitch) and aileron (roll). Two of them, one per wing half.", "Aircraft"),
    ("LE / chord", "LE is the wing's leading edge. Chord is the front-to-back width of the wing (245 mm here); positions are measured aft of the LE.", "Aircraft"),
    ("CG", "Centre of gravity: the point where the aircraft balances. Measured in mm aft of the leading edge. Too far aft makes it unstable; too far forward makes it hard to pitch.", "Balance"),
    ("NP", "Neutral point: the position of the CG at which the aircraft is exactly neutrally stable in pitch. The CG must sit ahead of it.", "Balance"),
    ("SM / static margin", "Static margin = (NP - CG) / chord, as a percent. It measures how far ahead of the neutral point the CG sits. At least 5 % chord is required.", "Balance"),
    ("T/W", "Thrust-to-weight ratio: total thrust of the four motors divided by the aircraft's weight. Above 1 it can lift off; the team requires 2.0 with a fresh pack and 1.6 with a worn one.", "Propulsion"),
    ("Fresh / sag", "Fresh pack: fully charged, 16.8 V for four cells. Sag: the pack nearly empty (20 % left) with its voltage dropping under load (14.92 V at rest in the model); thrust is lower.", "Propulsion"),
    ("Spin cap / duty", "Duty is the fraction of full throttle. The flight software never commands more than 0.90, so one motor can never draw the current of full throttle.", "Propulsion"),
    ("Derate", "A knock-down multiplier (0.93) applied to the published propeller thrust table because real thrust is usually lower than a vendor table.", "Propulsion"),
    ("Cant", "The sideways tilt of each motor's thrust line (17 degrees) that gives yaw authority.", "Propulsion"),
    ("ESC", "Electronic speed controller: the box that drives a motor from the battery. One per motor. Rated in amps.", "Propulsion"),
    ("4S, mAh, Wh", "4S: four lithium cells in series (14.8 V nominal, 16.8 V full). mAh or Ah: charge capacity. Wh: energy (Ah x volts).", "Propulsion"),
    ("MN2212, KV780, APC 9x4.5MR", "The motor (T-Motor MN2212, 780 rpm per volt) and the propeller (APC, 9 in diameter, 4.5 in pitch) used on all four positions.", "Propulsion"),
    ("Gate / mass gate", "A limit a design number must pass before the team may order or fly. The mass gate is 1.47 kg: the as-built aircraft must weigh at most that.", "Process"),
    ("EST / ESTIMATE", "A number the team estimated rather than measured or took from a vendor page. EST inputs are the reason many claims are UNVERIFIED.", "Process"),
    ("UNVERIFIED / CHECKED / VERIFIED / PROPOSED", "The status words. See the status list at the top of this page.", "Process"),
    ("Assumption (ASM-)", "A guess the team has written down on purpose, with the reasoning, so it can be replaced by a measurement later.", "Process"),
    ("Margin", "How much room a result has to its limit, as a percent of the limit. Positive passes. Negative fails.", "Process"),
    ("MS (margin of safety)", "For structures: MS = allowable stress / design stress - 1. MS = 0 means the part is exactly at its allowable under the design load; MS = +0.5 means it can take 1.5 times that load. It is >= 0 to pass.", "Structures"),
    ("Utilisation", "Design stress divided by allowable stress. Utilisation = 1 / (1 + MS). Utilisation 0.5 means the part uses half of what it can carry.", "Structures"),
    ("Factor of safety", "A multiplier on the expected load so that the part still has margin if the load is bigger than predicted. Here the design load is 1.5 x limit load x 1.15 (= 1.725) for carbon and metal parts and 2.156 for printed and bonded parts.", "Structures"),
    ("Limit load / ultimate load", "Limit load: the largest load expected in service. Ultimate: limit x the factor of safety; the part must carry ultimate without breaking.", "Structures"),
    ("Allowable", "The stress a material or joint is allowed to carry. Many allowables here are EST until a coupon (a small test piece) is broken on a test stand.", "Structures"),
    ("Prop strike", "The propeller hitting the ground or an object. The team treats a 30 N strike on one prop as a design load case (a damage case, factor 1.0).", "Structures"),
    ("CFRP, PETG, XPS", "Carbon-fibre tube; PETG printed plastic (the printed parts); XPS the pink extruded foam of the wing core (FOAMULAR 150).", "Structures"),
    ("MPa, kPa", "Units of stress. 1 MPa = 1 N per square millimetre; 1 kPa = 1/1000 of that.", "Structures"),
    ("Fatigue", "Failure from many repeated small loads rather than one big one. Checked against the propeller's once-per-turn shake over the flight life.", "Structures"),
    ("n, g-load, VD", "n is load factor (3.4 means 3.4 times weight). VD is the design dive speed, 24 m/s: the fastest speed the structure is designed for.", "Flight"),
    ("Vs, CLmax", "Vs is stall speed (the lowest speed the wing can still fly). It depends on CLmax, the wing's peak lift coefficient, which is an assumption (0.75) until a flight measures it.", "Flight"),
    ("Flutter / divergence / reversal", "Three aeroelastic failures. Flutter: the wing or control surface oscillates and grows. Divergence: the wing twists more as it gets more lift until it breaks. Reversal: the elevon works backwards. The team requires all of them to be at least 1.2 x VD = 28.8 m/s.", "Flight"),
    ("Yaw authority", "The twisting force about the vertical axis the motors can produce for steering in hover (N m). Needs at least 0.35 N m.", "Flight"),
    ("SITL", "Software-in-the-loop: the real autopilot software flying a simulated aircraft on a computer. Simulation results are marked CHECKED at best, never VERIFIED.", "Flight"),
    ("BATT_LOW", "The autopilot's low-battery trigger. After it fires the aircraft must land with the energy left.", "Mission"),
    ("FE / FEA", "Finite-element analysis: a computer model that splits a part into small pieces to find its stress. The FEA files are separate from this chain; the chain stores their results.", "Structures"),
    ("Rotor band, 1P, 2P", "The vibration frequencies produced by the spinning propellers: 1P once per turn, 2P twice. Structures must stay 20 % away from them.", "Vibration"),
    ("Gain margin", "How much the control loop's gain could be multiplied before the loop goes unstable. At least 2 is required.", "Vibration"),
    ("BOM", "Bill of materials: the list of everything bought, with price. BOM-A.csv has 38 lines.", "Cost"),
    ("G7", "The cost gate: total at most $1,800 and at least $100 left under $2,000 even if the unverified prices run 30 % higher.", "Cost"),
    ("D-xxx (D-206, D-182 ...)", "Design decision numbers from the team log (redesign/params/CHANGE-LOG.md). 'D-206' is decision 206. A number in a card's source name tells you which decision changed the design.", "Ids"),
    ("QP-n, FIXES, FIXES2", "QP-1 to QP-5 are the design review rounds (boards). FIXES and FIXES2 are the fix lists the boards produced.", "Ids"),
    ("A-P3, A-U1, A-D2 ...", "Requirement ids in REQUIREMENTS-A.md. U = user constraint, P = performance, D = design target. Each claim lists the requirement it verifies.", "Ids"),
    ("CL-A-..., CALC-A-..., P:..., ASM-A-..., SRC-A-..., T-A-...", "Ids used by the proof chain. CL = claim, CALC = the calculation behind it, P = a parameter (input number), ASM = assumption, SRC = source document, T = planned test. The Guide shows the readable name; the id is for searching.", "Ids"),
    ("Part ids (WNG, FIN, CGE, PRP, PWR, GER, MEC, AVN, HWC)", "Prefixes of parts in the CAD model: WNG wing, FIN fins and ribs, CGE cage (hub, arms, tray), PRP propulsion (motors, props), PWR battery and power, GER landing gear (foot shoes), MEC mechanics (servos, linkages), AVN avionics, HWC hardware (screws, nuts).", "Ids"),
    ("M1 ... M12", "Planned measurements in the team's test plan (for example M1 thrust stand, M5 CG on a knife edge). The 'How to check' text names the test.", "Process"),
]

# ------------------------------------------------------------------ shared symbol wording
S_MASSG = {"gate": "the mass gate: the heaviest the finished aircraft may be", "over": "build overrun: extra mass allowed for glue, wire and things not drawn, as a fraction of the gate",
           "gf": "growth factor: multiplier on the CAD mass for parts that are heavier in real life than drawn", "basic": "total mass of every part as drawn in the CAD model"}
S_PROP = {"m": "aircraft mass used", "g": "gravitational acceleration", "kv": "motor speed constant (rpm per volt)", "rm_ohm": "motor winding resistance",
          "i0_a": "motor no-load current", "rp_ohm": "battery pack internal resistance", "derate": "knock-down on the published thrust table",
          "cant_deg": "tilt of each thrust line", "download": "fraction of thrust left after the propeller wash hits the wing", "hot_sag": "extra knock-down on thrust for a hot, nearly empty pack",
          "spin_cap": "highest throttle the software allows (duty)", "v_fresh": "full pack voltage", "v_sag_rest": "worn pack voltage at rest", "apc_table": "vendor static thrust and power at each rpm",
          "lo": "lowest entry thrust the transition needs, in multiples of weight", "hi_frac": "highest entry thrust allowed, as a fraction of the sagged thrust", "duty": "throttle of the one motor"}
PROP_TAB = {"apc_table": (["rpm", "static thrust (N)", "shaft power (W)"], None)}
TW_FORMULA = ("T/W = (4 x T x cos(cant) x derate x hot) / (m x g)  where T is the thrust of one APC 9x4.5MR propeller at the rpm that the "
              "MN2212 motor reaches on the duty-capped bus voltage. Entry window = (0.80 x T/W_sag - 1.33) / (0.80 x T/W_sag + 1.33).")
TW_METHOD = ["The motor speed is found by balancing motor torque against propeller torque (prop_a.py, bisection over the vendor table above); "
             "that iteration is not hand-friendly, so this card shows the last step by calculator and gives the command to rerun the whole model:",
             "python -I redesign/qp/A/prop_a.py   (prints the same thrusts in gf)"]
TW_REAL = ("Thrust stand test T-A-BENCH-THRUST: one MN2212 with one APC 9x4.5MR on a 16.8 V and a 14.9 V supply, throttle to 0.90, read the load cell. "
           "Pass: fresh at least 780 gf and sag at least 624 gf per motor.")
MS_SYM = {"stress": "design stress in the part under the design load (load x factor of safety)", "allow": "allowable stress: what the material or joint may carry",
          "MS": "margin of safety"}

# ------------------------------------------------------------------ the claims
E = {}


def C(cid, g, why, **kw):
    E[cid] = dict(g=g, why=why, **kw)


# ---- mass
C("CL-A-MASS-PRED", "mass",
  "Adds up what the aircraft will really weigh (CAD mass plus growth plus build overrun) and checks it is under the 1.467 kg design target, so the thrust, stall and energy numbers all use a mass we can defend.",
  formula="m = basic x gf + over x gate", sym={**S_MASSG, "m": "predicted take-off mass"},
  steps=[("m", "basic*gf + over*gate", "kg", "predicted take-off mass")],
  limit_why="1.467 kg is the design target (D-207). It sits 3 g under the 1.47 kg mass gate so that a small overrun is noticed before the gate is hit.",
  real="Weigh-in test T-A-WEIGH: weigh the foam block, printed parts, epoxy joint and servo as they are built, then the whole aircraft with battery. As-built mass must be at most 1.47 kg. Use a kitchen scale good to 1 g.")
C("CL-A-MASS-ITEM", "mass",
  "A second, independent way to predict the mass: each item gets its own growth allowance based on how mature it is (weighed vendor part = 0 %, drawn printed part = 20 %). If the two methods disagree, one of them is wrong.",
  formula="m = (sum over items of mass_i x (1 + growth_i) + over x gate x 1000) / 1000", sym={"items": "table of item mass (g) and growth fraction", "over": S_MASSG["over"], "gate": S_MASSG["gate"]},
  steps=[("sum_g", "sum(r[0]*(1+r[1]) for r in items)", "g", "sum of item mass x (1 + growth)"), ("m", "(sum_g + over*gate*1000)/1000", "kg", "predicted mass")],
  tab={"items": (["item mass (g)", "growth fraction"], ["wing", "fins + feet", "motors", "props", "adapters + spinner nuts", "ESC", "pack", "strap", "avionics + harness", "servos", "cage", "hardware"])},
  limit_why="Same 1.467 kg design target as the first method.",
  real="Same weigh-in as the first mass claim (T-A-WEIGH). Weighing each item separately also tells you which row of the table is off.")
C("CL-A-MASS-GATE-ROOM", "mass",
  "Checks the same predicted mass against the hard gate: if the finished aircraft weighs more than 1.47 kg the team may not fly it without a further review.",
  formula="m = basic x gf + over x gate  (same as the mass prediction), compared with the gate", sym={**S_MASSG, "m": "predicted take-off mass"},
  steps=[("m", "basic*gf + over*gate", "kg", "predicted take-off mass")], limit_why="1.47 kg is the mass gate (D-190): above it the transition window and hover margin are no longer proven.",
  real="Weigh-in (T-A-WEIGH). The margin to 1.47 kg is the room the team has for anything added later.")
C("CL-A-MASS-USER", "mass",
  "Checks the mass against the project's hard cap of 25 kg for a four-person-portable aircraft. This is a sanity check: the aircraft is about 17 times under it.",
  formula="m = basic x gf + over x gate, compared with 25 kg", sym={**S_MASSG, "m": "predicted take-off mass"},
  steps=[("m", "basic*gf + over*gate", "kg", "predicted take-off mass")], limit_why="25 kg (55 lb) is the user's portability cap in CLAUDE.md.", real="Any scale. The aircraft fits a bathroom scale.")
C("CL-A-CUTS-REQUIRED", "mass",
  "The mass target only works if estimated weight cuts (lighter foam, lighter printed parts) are really achieved. This finds how many grams of those cuts must be real, out of the 41.6 g the team is counting on.",
  formula="X = cuts - (target - m) / gf x 1000", sym={"cuts": "grams of weight cuts the plan assumes (all estimates)", "target": "design target mass", "m": "predicted mass", "gf": S_MASSG["gf"], "X": "grams of cuts that must be real"},
  steps=[("x_g", "cuts - (target - m)/gf*1000", "g", "cuts that must be real")],
  limit_why="X may not exceed the cuts available: if it did, even all the cuts would not reach the target.",
  real="Weigh the foam block, the printed parts and the epoxy joint (T-A-WEIGH): at least 27.2 g of the 41.6 g must be real.")
C("CL-A-STRUCT-MASS", "mass",
  "Adds the structure groups (wing, fins, feet, hardware, cage) and checks the total against the 494 g ceiling set by the design board, so the structure does not eat the payload budget.",
  formula="structure = wing + fins + feet + hardware + cage", sym={"g": "list of group masses in grams: wing, fins, feet, hardware, cage"},
  steps=[("g_total", "sum(g)", "g", "structure mass")], tab={"g": (["mass (g)"], ["wing", "fins", "feet", "hardware", "cage"])},
  limit_why="494 g is the structure ceiling from the QP-4 board.", real="Weigh each assembly as built (T-A-WEIGH) and add them.")

# ---- balance
C("CL-A-CG", "cg",
  "The aircraft must balance at least 19 mm aft of the wing leading edge or it will be nose-heavy and the elevons cannot pitch it over in transition.",
  via="the CAD model: every part's mass and centroid (sitl/cad_mass.json); CG = sum(mass x position) / sum(mass)", formula="CG = sum(m_i x x_i) / sum(m_i)  over every part",
  sym={"v": "CG position aft of the leading edge"}, limit_why="19 mm is the forward end of the design CG band 19 to 26 mm (D-195).",
  real="CG breadboard (T-A-CG-BREADBOARD): balance the built aircraft on a knife edge under the wing and measure the distance from the leading edge.")
C("CL-A-CG-HI", "cg", "The same CG must not be further aft than 26 mm, or the aircraft is too close to unstable in pitch.",
  via="the CAD mass file (same value as the previous card)", formula="CG as above, compared with the aft limit", sym={"v": "CG position aft of the leading edge"},
  limit_why="26 mm is the aft end of the design band (hard aft limit 28.5 mm).", real="Knife-edge balance (T-A-CG-BREADBOARD).")
C("CL-A-CG-TRIM-AFT", "cg", "The battery can slide in the tray to correct the CG after the first weigh-in. This checks that, at the aft end of that slide, the CG is still inside the hard aft limit.",
  formula="CG_aft = CG + m_pack x trim / m_basic", sym={"cg": "CG from CAD", "pack": "battery mass", "trim": "pack slide aft of the CAD position", "basic": "CAD mass", "trim_fwd": "pack slide forward of the CAD position"},
  steps=[("shift", "pack*trim/(basic*1000)", "mm", "CG shift per trim"), ("aft_mm", "cg + shift", "mm", "CG with the pack at the aft end")],
  limit_why="28.5 mm is the hard aft CG limit: beyond it the static margin falls to the minimum.", real="Move the real pack in the tray slots (T-A-CG-BREADBOARD) and measure the CG at each end.")
C("CL-A-CG-TRIM-FWD", "cg", "The same slide at the forward end must keep the CG at least 19 mm aft of the leading edge.",
  formula="CG_fwd = CG - m_pack x trim_fwd / m_basic", sym={"cg": "CG from CAD", "pack": "battery mass", "trim": "pack slide aft (not used in this step)", "trim_fwd": "pack slide forward of the CAD position", "basic": "CAD mass"},
  steps=[("fwd", "pack*trim_fwd/(basic*1000)", "mm", "CG shift forward"), ("fwd_mm", "cg - fwd", "mm", "CG with the pack at the forward end")],
  limit_why="19 mm is the forward end of the design band.", real="Same as the aft end (T-A-CG-BREADBOARD).")
C("CL-A-SM", "cg", "Static margin is the aircraft's built-in pitch stability. Below 5 % of the chord it gets twitchy and the autopilot has less margin.",
  formula="SM = (NP - CG) / chord x 100", sym={"np": "neutral point: how far aft of the leading edge the aircraft is neutrally stable (assumed)", "cg": "CG from CAD", "c": "wing chord"},
  steps=[("sm_pct", "(np - cg)/c*100", "% chord", "static margin")], limit_why="At least 5 % chord is the requirement A-P4.",
  real="Measure NP and CG on the built aircraft (T-A-CG-BREADBOARD); the neutral point input is an assumption until then.")
C("CL-A-CG-LATERAL", "cg", "The CG must not be more than 5 mm off the centreline sideways, or the aircraft rolls to one side in hover.",
  via="the CAD mass file (cg_y)", formula="cg_y = sum(m_i x y_i) / sum(m_i)", sym={"v": "sideways CG offset"}, limit_why="5 mm is requirement A-P4.",
  real="Hang the built aircraft from its centre and check it hangs level (T-A-CG-BREADBOARD).")

# ---- hover thrust
for cid, key, what, lim_why in [
    ("CL-A-TW-FRESH-GATE", "fresh_cap", "With a full battery and the mass at the 1.47 kg gate, can the four motors lift at least 2.0 times the aircraft's weight at the 0.90 throttle cap?", "2.0 is the requirement A-P2 for a fresh pack."),
    ("CL-A-TW-SAG-GATE", "sag_cap", "With a nearly empty battery (voltage sagging) at the gate mass, can the motors still lift at least 1.6 times the weight? This is the worst state for hover and landing.", "1.6 is the requirement A-P2 for the worst pack state."),
    ("CL-A-TW-FRESH-PRED", "fresh_cap", "The same fresh-pack thrust-to-weight check at the predicted mass instead of the gate mass.", "2.0 is the requirement A-P2."),
    ("CL-A-TW-SAG-PRED", "sag_cap", "The same sagged-pack check at the predicted mass.", "1.6 is the requirement A-P2.")]:
    sag = key == "sag_cap"
    C(cid, "hover", what, formula=TW_FORMULA, sym={**S_PROP, "T/W": "thrust-to-weight ratio"}, tab=PROP_TAB, method=TW_METHOD,
      steps=([("tw", "sag_cap_gf/(m*1000)", "-", "T/W = total sagged thrust (gf) / weight (gf)")] if sag and cid.endswith("GATE") else None),
      limit_why=lim_why, real=TW_REAL)
C("CL-A-WINDOW-PRED", "hover",
  "At the start of the transition from hover to cruise the aircraft needs a minimum entry thrust and has a maximum it can safely reach. The window between them must be at least 5 % wide on each side; this is the predicted-mass case.",
  formula="window = (0.80 x TW_sag - 1.33) / (0.80 x TW_sag + 1.33) x 100", sym={**S_PROP, "window": "half-width of the usable entry-thrust window"},
  tab=PROP_TAB, method=TW_METHOD, steps=[("w", "(hi_frac*sag_cap - lo)/(hi_frac*sag_cap + lo)*100", "%", "window")],
  limit_why="At least 5 % (requirement A-P3): below it the pilot or autopilot cannot reliably time the pitch-over.",
  real="C3 time-domain pitch-over run at the as-weighed mass (T-A-C3-PITCHOVER), and the thrust stand (T-A-BENCH-THRUST).")
C("CL-A-WINDOW-GATE", "hover", "The same entry window at the 1.47 kg gate mass.",
  formula="window = (0.80 x TW_sag - 1.33) / (0.80 x TW_sag + 1.33) x 100", sym={**S_PROP, "window": "half-width of the usable entry-thrust window"},
  tab=PROP_TAB, method=TW_METHOD, steps=[("w", "(hi_frac*sag_cap - lo)/(hi_frac*sag_cap + lo)*100", "%", "window")],
  limit_why="At least 5 % (requirement A-P3).", real="C3 pitch-over run at the as-weighed mass (T-A-C3-PITCHOVER).")
C("CL-A-WINDOW-MASS", "hover", "The heaviest the aircraft can be while the entry window stays at 5 %. It shows how much extra mass the design can absorb.",
  formula="m_max = sagged thrust x 0.80 / (1.33 x (1 + w) / (1 - w))", sym={**S_PROP, "w": "required window half-width (percent)"}, tab=PROP_TAB, method=TW_METHOD,
  limit_why="Must be at least the predicted mass; the gap is the spare mass.", real="Weigh the real aircraft (T-A-WEIGH) and compare with this number.")
C("CL-A-MOTOR-I", "hover", "A single motor can be asked for 0.90 throttle while the other three hold hover. This checks that its winding current stays under the motor's 13 A rating so it does not overheat.",
  formula="I = phase current of one motor at duty 0.90 (prop_a.py one_motor), three motors at hover, 1.50 kg, fresh pack",
  sym={**S_PROP, "i_a": "winding current of the loaded motor"}, tab=PROP_TAB, method=TW_METHOD, limit_why="13 A is the motor winding rating used for requirement A-P16.",
  real="Motor bench test T-A-BENCH-MOTOR: run one motor at duty 0.90 for 180 s with a current meter; phase current at most 13 A and can temperature at most 80 C.")
C("CL-A-ESC-I", "hover", "ESCs and connectors must handle more than the worst current, with a 25 % cushion. This finds the current they must be rated for.",
  formula="I_required = 1.25 x peak current of one motor with no throttle cap (full duty, three motors at hover, 1.50 kg, fresh pack)",
  sym={**S_PROP, "factor": "safety factor on current", "i_a": "current the ESC channel and connector must carry"}, tab=PROP_TAB, method=TW_METHOD,
  limit_why="35 A is the rating of the chosen ESC channel (requirement A-P16).", real="Read the rating on the ESC and connector data sheets and compare; confirm with the motor bench test (T-A-BENCH-MOTOR).")

# ---- structures (margin of safety)
def ms(cid, why, ms_, **kw):
    C(cid, "struct", why, ms=ms_, **kw)


MS_REAL = "Break a small test piece (coupon) on a test stand and use the measured strength instead of the estimated allowable; or load the built part with weights to the design load and check nothing yields."
ms("CL-A-MS-SPAR", "The carbon spar is the beam that carries the lift of the whole wing to the fuselage. This checks it does not break at the highest expected load (3.4 g).", (93.9, 350.0, "MPa", "root bending moment 4.78 N m (unrelieved), 3.4 g limit x 1.725"), real=MS_REAL + " For the spar a three-point bend test of an off-cut tube is the cheapest check.")
ms("CL-A-MS-BOND", "The rib saddle is the glued clamp that holds the fin rib on the spar. It is the thinnest bond in the airframe, so it is the first place a glue joint would fail.", (1.5, 2.0, "MPa", "rib saddle on the 12 mm spar, couple 9.4 N m / 12 mm = 783 N"), real="Pull-test a glued sleeve on a spare tube (coupon) to find the real glue shear strength; the 2.0 MPa allowable is an estimate.")
ms("CL-A-MS-ARM", "If a propeller strikes the ground the motor arm takes a sideways bend. This checks the arm tube survives a 30 N strike at its root.", (144.9, 350.0, "MPa", "7.4 N m root bending, 30 N strike"), real=MS_REAL + " Drop-test an arm at its root-to-motor lever; the 30 N strike force is an estimate.")
ms("CL-A-MS-ARM-SOCKET", "The arm tube is glued into a printed socket in the hub. A prop strike tries to twist the arm out of it; this checks the glue bond.", (1.4, 2.0, "MPa", "strike couple 7.4 N m over a 25 mm socket = 296 N"), real="Pull and twist test a bonded socket coupon (see the assumption on printed hub walls).")
ms("CL-A-MS-CUP-HEADPULL", "Each motor is held on a printed cup by four screws. In normal flight at the highest throttle, this checks the screw heads do not pull through the plastic.", (1.26, 20.0, "MPa", "8.8 N thrust and propeller shake, 5.5 N per screw"), real="Pull a screw through a printed PETG coupon with a spring scale; the 20 MPa bearing allowable is an estimate.")
ms("CL-A-MS-CUP-STRIKE", "Same screws, now in a 30 N sideways prop strike. The strike levers the motor off its cup; this checks the screw heads hold.", (7.84, 20.0, "MPa", "strike 30 N at 35 mm above the base, 33.8 N per screw"), real="As above, load the cup sideways.")
ms("CL-A-MS-CUP-PLATE", "The printed cup plate bends where it overhangs the arm sleeve during a strike; this checks the plate does not snap there.", (6.4, 9.5, "MPa", "plate cantilever past the sleeve end, strike"),
   note="The stored value 0.49 comes from the param note (6.4 vs 9.5 MPa). The current arm_cup_checks.md table prints 6.92 MPa (MS +0.37) for the same row after a later edit, so the stored number is slightly out of date, in the optimistic direction. Reported, not changed.", real=MS_REAL)
ms("CL-A-MS-CUP-HOLE", "If a prop blade jams, the motor torque loads the screw holes in the cup. This checks the plastic around the holes is not crushed.", (14.37, 20.0, "MPa", "2.4 N m blade-stop torque on two screws"), real="Torque test a printed cup coupon.")
ms("CL-A-MS-CUP-BOND", "The cup is glued to the arm tube. This checks that glue under a strike torque plus motor torque.", (0.69, 2.0, "MPa", "1.41 N m strike torsion + 2.4 N m torque couple over 25 mm"), real="Pull and twist a bonded cup coupon.")
ms("CL-A-MS-ARM-BLADE", "A worse version of the prop-strike case: the force acts at the blade, 80 mm further out, so the arm root bends more.", (192.07, 350.0, "MPa", "strike force 30 N x 0.326 m = 9.8 N m"), real=MS_REAL)
ms("CL-A-MS-FATIGUE-HUBWALL", "Every spin-up pushes the arm sockets in the hub. This checks the printed wall survives 2000 spin-ups without cracking from repeated loading.", (4.6, 10.0, "MPa", "0 to cap thrust cycles, 2000 cycles, 87 N couple on a 6 mm patch"), real="Cycle a printed socket coupon 2000 times with a thrust-sized load.")
ms("CL-A-MS-FATIGUE-ARM", "The propeller shakes the arm once per turn, millions of times. This checks the carbon tube survives those cycles.", (8.58, 140.0, "MPa", "bending amplitude 0.75 N m at 4.1e6 cycles"), real="Fatigue allowable 140 MPa is 0.40 x 350 MPa (estimated); a tap test and IMU vibration log in the first tethered hover (T-A-TETHER-VIBE) show the real shake.")
ms("CL-A-MS-RIB", "The fin rib sits under the fin foot. If the aircraft rests on one foot (tilted on landing) the rib twists; this checks it.", (18.8, 30.0, "MPa", "one foot 15 N x 0.18 m = 2.7 N m"), real=MS_REAL)
ms("CL-A-MS-FIN", "The aircraft stands on its fin tubes. This checks the fin tube against bending when landing or standing on one foot.", (78.8, 350.0, "MPa", "foot load 42 N x 0.18 m = 7.6 N m"), real="Stand a built fin on a scale and press on it with the landing weight.")
ms("CL-A-MS-PACK-CRASH", "In a hard landing at 12 g the battery (270 g) is the heaviest loose item. This checks the bridge tube and tray hold it so it cannot fly into the electronics.", (90.3, 350.0, "MPa", "bridge under pack + hub at 12 g, 4.6 N m"), real="Drop test the built bridge and pack from a height giving 12 g on a foam pad.")


def tau(cid, why, **kw):
    C(cid, "struct", why, formula="tau = k x M x (OD / 2) / J,  J = pi / 32 x (OD^4 - ID^4)",
      sym={"od": "outer diameter of the bridge tube", "idd": "inner diameter", "m": "roll moment the tube must carry", "k": "factor on the load (1.725 carbon design factor, or 1.0 for a damage case)", "tau": "shear stress in the tube wall"},
      steps=[("j", "3.141592653589793/32*(od**4 - idd**4)", "mm^4", "J, torsion constant of the tube"), ("tau_mpa", "k*m*1000*(od/2)/j", "MPa", "shear stress in the tube")], **kw)


tau("CL-A-BRIDGE-TORSION-F2", "If one motor goes to full power (an ESC cap failure) the hub tries to roll about the bridge tube. This checks the 16 x 14 carbon bridge tube does not fail in twist with the carbon design factor.",
    limit_why="30 MPa is the estimated carbon shear allowable (no coupon test yet).", via_note="Roll moment 4.37 N m is from the hub FEA load set (bridge_torsion_d206.md).", real="Twist a spare 16 x 14 tube on a lever arm with a known weight; the 30 MPa allowable is an estimate.")
tau("CL-A-BRIDGE-TORSION-S2", "The same tube in a worse load: a 30 N prop strike in the disc plane. This is a damage case, so the factor is 1.0.",
    limit_why="30 MPa estimated carbon shear allowable.", via_note="Roll moment 7.93 N m is from the hub FEA load set.", real="Same twist test.")
C("CL-A-LANDING-STROKE", "struct", "On landing, the fin-tip feet crush and absorb the touchdown. This checks that the crush stays within the 20 mm available. It passes (17.2 mm) only inside the accepted foam region (AR-016, D-243); the foam is unmeasured (TP-3).", via="landing_a.py (energy absorbed by the foot shoe at 1.2 m/s descent)", formula="stroke = kinetic energy at touchdown / crush force of the foot",
  sym={"v": "crush stroke of the foot"}, limit_why="20 mm is the stroke the foot design allows (A-P13).", real="Drop the built aircraft from the height that gives 1.2 m/s onto a hard floor and measure the foot crush.")
C("CL-A-TIPOVER", "struct", "Standing on its fin tips, the aircraft must not tip over if the ground slopes or a gust leans it. This is the tilt at which it starts to tip.", via="geometry in SIZING-A s4: feet 0.36 m apart, CG 0.275 m above the ground", formula="tip-over angle = arctan( half the foot spacing / CG height )",
  sym={"v": "static tip-over angle"}, limit_why="At least 30 degrees (requirement A-P9).", real="Tilt the built aircraft on a board until it tips, read the board angle on a phone.")
for cid, why in [
    ("CL-A-FOAM-SPAR-BOND", "The foam core is glued to the spar. In flight the lift load passes through that glue; this checks the foam shear around the spar."),
    ("CL-A-FOAM-FIN-SLOT", "The fin is plugged into a slot in the foam wing. This checks the foam bearing under the fin's side load."),
    ("CL-A-FOAM-TRAY", "In a crash the battery tray presses on the foam slot floor. This worst case assumes only a quarter of the floor carries it."),
    ("CL-A-FOAM-SERVO", "If a servo is driven against its stop it pulls on its foam pocket. This checks the foam shear with epoxy on all four walls."),
    ("CL-A-FOAM-CAP-PEEL", "A stop reaction can peel a lens cap off the tape skin of the wing. This checks the foam under it in tension.")]:
    E[cid] = dict(g="struct", why=why, ms={"CL-A-FOAM-SPAR-BOND": (58.0, 86.0, "kPa", "bond zone |y| <= 0.20 m"), "CL-A-FOAM-FIN-SLOT": (57.0, 103.0, "kPa", "2 x 20 N side load on 65 x 23 mm"),
                  "CL-A-FOAM-TRAY": (76.0, 103.0, "kPa", "12 g crash, quarter of the slot floor"), "CL-A-FOAM-SERVO": (50.0, 86.0, "kPa", "servo stall 0.427 N m, 4 walls"),
                  "CL-A-FOAM-CAP-PEEL": (94.0, 129.0, "kPa", "30 N stop reaction on 698 mm2")}[cid],
                  real="Cut a small block of the real foam (FOAMULAR 150) and load it in compression, shear and tension with weights or on a test stand; the shear and tension allowables are estimates.")

# ---- cost
COSTSYM = {"rows": "BOM lines: id, group, vendor, quantity, unit price (USD), unverified flag", "tax": "sales tax on goods", "faa": "FAA registration fee", "ship": "shipping per vendor", "bump": "price uplift for unverified lines (30 %)",
           "tubes": "BOM ids counted in the crash reserve", "budget": "the budget cap"}
COSTSTEP = [("goods", "sum(r[3]*r[4] for r in rows)", "USD", "goods = sum of quantity x unit price over every BOM line"), ("goods_tax", "goods*(1+tax)", "USD", "goods with tax")]
C("CL-A-COST-TOTAL", "cost", "Adds up everything we must buy (parts, tax, shipping, FAA registration and a reserve for crash damage) and checks it is under $1,800, leaving a $200 cushion under the $2,000 cap.",
  formula="total = goods x (1 + tax) + shipping + FAA + crash reserve", sym=COSTSYM, tab={"rows": (["BOM id", "group", "vendor", "qty", "unit price (USD)", "unverified?"], None)},
  steps=COSTSTEP + [("total", "goods_tax + shipping_usd + faa + reserve_usd", "USD", "total")], limit_why="$1,800 is gate G7: the $2,000 cap minus a $200 buffer.",
  real="Compare each BOM line with the live vendor page on the day of ordering (BOM-A.csv has the date checked). Add the real shipping at checkout.")
C("CL-A-COST-MARGIN30", "cost", "If every unverified price turns out 30 % higher, how much of the $2,000 is still left? At least $100 must remain.",
  formula="margin = budget - total with +30 % on unverified lines", sym=COSTSYM, tab={"rows": (["BOM id", "group", "vendor", "qty", "unit price (USD)", "unverified?"], None)},
  steps=[("margin_30", "budget - total_30_usd", "USD", "margin")], limit_why="At least $100 left under $2,000 (gate G7).",
  real="Re-check each line flagged unverified before ordering; the margin shrinks $1 per $1 of price rise (plus tax).")
C("CL-A-COST-BUDGET", "cost", "The total with every unverified line 30 % higher must still be under the $2,000 hard budget.",
  formula="total_30 = goods with unverified lines x 1.30, then tax, shipping, FAA and reserve as above", sym=COSTSYM, tab={"rows": (["BOM id", "group", "vendor", "qty", "unit price (USD)", "unverified?"], None)},
  steps=[("unv", "sum(r[3]*r[4] for r in rows if r[5])", "USD", "goods on the unverified lines"), ("extra", "unv*bump*(1+tax)", "USD", "uplift of those lines at +30 %, with tax (the crash reserve also rises a little)"), ("t30", "total_30_usd", "USD", "total with the uplift (the BOM calculation's own output)")], limit_why="$2,000 is the user's hard total (CLAUDE.md).",
  real="Run python -I redesign/qp/A/bom_a.py (reads BOM-A.csv) and compare the totals.")

# ---- mission
C("CL-A-CRUISE-NEED", "mission", "How long must the aircraft cruise to fly the required racetrack laps, including a go-around and run-in? This is the time the battery must support.",
  formula="R = V^2 / (g x tan(bank));  lap time = (2 x L_ref + 2 x pi x R) / V;  need = settle + (laps + go-around + run-in) x lap time",
  sym={"v": "cruise speed", "g": "gravity", "bank": "bank angle in turns", "leg": "straight leg length", "settle": "time to settle in cruise", "laps": "required laps", "ga": "go-around laps", "runin": "run-in laps"},
  steps=[("radius", "v**2/(g*math.tan(math.radians(bank)))", "m", "turn radius"), ("lap_s", "(2*leg + 2*math.pi*radius)/v", "s", "time for one lap"), ("need", "settle + (laps + ga + runin)*lap_s", "s", "cruise time needed")],
  limit_why="At most 210 s (3.5 min, requirement A-D2).", real="Fly the racetrack on a tethered or open-field test and time the cruise portion on the flight log.")
C("CL-A-CRUISE-RADIUS", "mission", "The turn radius at cruise speed and 30 degrees of bank. It sets the size of the racetrack and so the fence distance.", formula="R = V^2 / (g x tan(bank))",
  sym={"v": "cruise speed", "g": "gravity", "bank": "bank angle in turns"}, steps=[("radius", "v**2/(g*math.tan(math.radians(bank)))", "m", "turn radius")], real="Log GPS during a coordinated turn.")
C("CL-A-CRUISE-AVAIL", "mission", "How long can the battery actually power cruise, after hover, transition and climb take their share? Must exceed the time the mission needs.",
  formula="t = (E_usable - E_hover - E_transition - E_climb) / P_cruise x 3600", sym={"pack_ah": "pack capacity", "pack_v": "pack nominal voltage", "floor_frac": "usable fraction of capacity (down to the BATT_LOW floor)", "reserve_frac": "fraction kept as reserve", "hover_s": "hover time", "trans_wh_ref": "transition energy at reference mass", "climb_wh_ref": "climb energy at reference mass", "cruise_w_ref": "cruise power at reference mass", "ref_mass_kg": "reference mass for those three", "trans_exp": "how transition energy grows with mass", "cruise_exp": "how cruise power grows with mass", "m": "predicted mass"},
  steps=[("usable", "pack_ah*pack_v*floor_frac*reserve_frac", "Wh", "usable battery energy"), ("hover_wh", "hover_w*hover_s/3600", "Wh", "energy for hover (hover power from the prop model)"), ("trans", "trans_wh_ref*(m/ref_mass_kg)**trans_exp", "Wh", "transition energy"), ("climb", "climb_wh_ref*(m/ref_mass_kg)", "Wh", "climb energy"), ("cruise_w2", "cruise_w_ref*(m/ref_mass_kg)**cruise_exp", "W", "cruise power"), ("cruise_s", "(usable - hover_wh - trans - climb)/cruise_w2*3600", "s", "cruise time available")],
  limit_why="At least the time the mission needs (previous claim).", real="Fly a full mission profile on a bench or tether with a power meter (watt-hours used) and compare with the model.")
C("CL-A-FENCE", "mission", "After the battery warning fires in cruise the aircraft keeps travelling for a while before it lands. This checks it stays inside the 240 m flying fence in any direction.",
  formula="bound = leg / 2 + R + run-out", sym={"leg": "racetrack leg length", "r": "turn radius", "runout": "distance travelled after the warning"}, steps=[("bound_m", "leg/2 + r + runout", "m", "worst-case distance from the field centre")],
  limit_why="240 m is the fence radius (requirement A-P24).", real="Set the geofence at 240 m in the autopilot and simulate a BATT_LOW trigger at each point of the racetrack.")

# ---- flight
C("CL-A-STALL", "flight", "The slowest speed at which the wing still lifts the aircraft. Cruise must be at least 1.3 times this, or a small gust drops the wing.",
  formula="Vs = sqrt(2 x m x g / (rho x S x CLmax));  claim = 1.3 x Vs", sym={"m": "gate mass", "g": "gravity", "rho": "air density", "s": "wing area", "cl": "wing's peak lift coefficient (an assumption)", "k": "safety ratio of cruise to stall"},
  steps=[("vs", "(2*m*g/(rho*s*cl))**0.5", "m/s", "stall speed"), ("k_vs", "k*vs", "m/s", "1.3 x stall speed")], limit_why="At most the 17 m/s cruise speed (requirement A-P6).",
  real="First-cruise test (T-A-FIRST-CRUISE): slow the aircraft until it stalls at altitude and read airspeed; the measured stall replaces the CLmax assumption.")
C("CL-A-STALL-PRED", "flight", "The same stall check at the predicted take-off mass (1.881 kg estimate) instead of the 1.47 kg gate. Cruise (17 m/s) must be at least 1.3 times the stall speed; at this mass it is not (17.74 m/s), so it FAILS until a measured stall shows the wing lifts better than the 0.75 estimate (TP-11).",
  formula="Vs = sqrt(2 x m x g / (rho x S x CLmax));  claim = 1.3 x Vs", sym={"m": "predicted mass", "g": "gravity", "rho": "air density 1.20", "s": "wing area", "cl": "wing's peak lift coefficient (an assumption)", "k": "safety ratio of cruise to stall"},
  steps=[("vs", "(2*m*g/(rho*s*cl))**0.5", "m/s", "stall speed"), ("k_vs", "k*vs", "m/s", "1.3 x stall speed")], limit_why="At most the 17 m/s cruise speed (requirement A-P6).",
  real="First-cruise test (T-A-FIRST-CRUISE, TP-11): measure the stall at the as-weighed mass; the pass line is CLmax 0.81 or more.")
yawsym = {"cant_term_ref_nm": "yaw authority from cant at the reference cant angle", "arm_factor": "factor for the longer arm design", "cant_deg": "actual cant", "cant_ref_deg": "reference cant", "q_model_nmm": "rotor reaction torque from the model", "q_gain": "arm-factor scaling on Q"}
for cid, why, lw in [("CL-A-YAW-MODEL", "In hover the aircraft steers in yaw by slightly speeding two motors and slowing two. This checks it can make at least 0.35 N m of twist.", "0.35 N m is the pass level (requirement A-P7)."),
                     ("CL-A-YAW-R2", "The same yaw authority against the lower R2 floor: below 0.30 N m the design must be changed.", "0.30 N m is the R2 fail level.")]:
    C(cid, "flight", why, formula="authority = cant_term x arm_factor x sin(cant) / sin(cant_ref) + q_gain x Q", sym=yawsym,
      steps=[("n_m", "cant_term_ref_nm*arm_factor*math.sin(math.radians(cant_deg))/math.sin(math.radians(cant_ref_deg)) + q_gain*q_model_nmm/1000", "N m", "yaw authority")], limit_why=lw,
      real="Hanging yaw test (T-A-BENCH-YAW): the built aircraft on a pivot, apply +-0.10 throttle and measure the twisting force on a scale.")
C("CL-A-YAW-Q", "flight", "The reaction torque of a spinning propeller is half of the yaw authority. This checks the modelled torque value on its own.", via="D184.md model of the rotor reaction", formula="Q = motor shaft torque at +-0.10 throttle",
  sym={"v": "rotor reaction torque"}, limit_why="At least 55 N mm (bench analysis).", real="Measure shaft torque on the thrust stand with a torque cell.")
C("CL-A-WIND-LEAN", "flight", "In a 5 m/s wind the aircraft leans into it in hover. If it leans more than 40 degrees, the thrust that holds it up falls short.", via="a SITL run (ArduPlane 4.7.3, QP-2 SITL.md)", formula="lean angle = angle the aircraft tilts to hold position in wind",
  sym={"v": "maximum belly-on hover lean"}, limit_why="At most 40 degrees (45 degrees is the autopilot's own limit, with margin).", real="Tethered hover in light wind (T-A-WIND-HEADING): log the pitch angle.")
C("CL-A-WIND-OUTPUT", "flight", "In turbulence, motors briefly go near full output. This checks no motor stays above 85 % for more than half a second.", via="SITL turbulence runs N4_*", formula="longest time a motor is at or above 0.85 output",
  sym={"v": "longest time at or above 0.85"}, limit_why="At most 0.5 s.", real="Log motor outputs during a tethered hover in gusty wind (T-A-WIND-HEADING).")
C("CL-A-WIND-CAP", "flight", "The same turbulence runs must never hit the 0.90 throttle cap, because that is where the autopilot loses control authority.", via="the same SITL runs", formula="total time at the 0.90 cap",
  sym={"v": "time at the cap"}, limit_why="Zero seconds.", real="Same tethered hover log.")
for cid, why, via, sym in [("CL-A-ROLL-141", "Can the aircraft roll fast enough in cruise (at least about 45 degrees per second, the derived requirement of D-254) to steer through a gust? This SITL run uses the 1.455 kg target mass.", "SITL run R5_rt65", {"v": "peak roll rate"}),
                           ("CL-A-ROLL-GATE", "The same roll rate at the 1.47 kg gate mass.", "SITL run R5_rt65g", {"v": "peak roll rate"})]:
    C(cid, "flight", why, via=via, formula="peak roll rate from a full-stick roll command in the simulator", sym=sym, limit_why="At least 44.8 degrees per second: a 60 degree bank change in 1.7 s (MIL-F-8785C Class I Level 1 Category B, A-P11 as re-derived in D-254; the old 90 was never derived).", real="First cruise test (T-A-FIRST-CRUISE): full-aileron roll and read the gyro.")
C("CL-A-PITCH-USE", "flight", "During the pitch-over transition the elevons deflect part of their travel. This checks the use stays under 60 % of a 15 degree basis (9 degrees), leaving travel for roll and gusts. With the D-255 configuration (battery at the aft end of its slot, cruise 18 m/s, roll-rate cap 45 deg/s) the worst of the four transition cases is 0.59, just under the 0.60 line (one simulator run each; runs scatter by 0.01 to 0.03, so first-flight logs decide it). Before: 0.651 with C3 controls alone, 0.69 to 0.79 before them. The roll and gust reserve now fits too: cruise reversal plus the worst gust 16.7 degrees, transition plus gust 13.4 degrees, against the 20 degree stop. Decision D-245 keeps this line.",
  via="SITL transition runs (AR-015 baseline, AR-017 C3)", formula="use = elevon pitch deflection / 15 degree basis (read from the simulation summary)", sym={"v": "elevon pitch use on the 15 degree basis"},
  limit_why="At most 0.60 (SITL-FLIGHT.md line 25; D-245 supersedes the QP-4 board 20 degree basis).", real="Log elevon commands during the first transition.")
C("CL-A-SERVO-FACTOR", "flight", "The elevon servo must be strong enough to hold the elevon against the airflow at top speed with a safety factor of 1.5 on top. This is the 25 C case.",
  formula="factor = servo torque / (load factor x (hinge moment + preload + damper at slew))", sym={"stall_72_nm": "servo stall torque at 7.2 V", "hinge_vd_nm": "aerodynamic hinge moment at VD", "preload_nm": "hinge friction preload", "damper_slew_nm": "damper drag while moving", "load_factor": "safety factor on load", "damper_slew_cold_nm": "damper drag when cold", "arm_mm": "servo arm length", "horn_mm": "elevon horn length"},
  steps=[("factor_25c", "stall_72_nm/(load_factor*(hinge_vd_nm + preload_nm + damper_slew_nm))", "-", "torque factor")], limit_why="At least 1.5 (requirement A-P11).", real="Servo rail voltage test (T-A-SERVO-RAIL) and the elevon coupon E1 (T-A-ELEVON-E1): measure real servo torque and hinge moment.")
C("CL-A-SERVO-COLD", "flight", "The same servo check on a cold day (0 C), when the damper fluid is thicker and drags more, with the real horn-to-arm ratio.",
  formula="factor = servo torque / (load factor x (hinge + preload + cold damper)) x horn / arm", sym={"stall_72_nm": "servo stall torque", "hinge_vd_nm": "hinge moment at VD", "preload_nm": "preload", "damper_slew_cold_nm": "damper drag when cold", "load_factor": "safety factor", "arm_mm": "servo arm length", "horn_mm": "elevon horn length"},
  steps=[("f", "stall_72_nm/(load_factor*(hinge_vd_nm + preload_nm + damper_slew_cold_nm))*horn_mm/arm_mm", "-", "torque factor at 0 C")], limit_why="At least 1.5.", real="Elevon coupon E1 with the damper in a freezer (T-A-ELEVON-E1).")
C("CL-A-SERVO-RATIO", "flight", "A looser reading of the same requirement: servo stall torque compared with the hinge moment alone.", formula="ratio = servo torque / hinge moment", sym={"stall_72_nm": "servo stall torque", "hinge_vd_nm": "hinge moment at VD"},
  steps=[("r", "stall_72_nm/hinge_vd_nm", "-", "ratio")], limit_why="At least 1.5 (A-P11 wording).", real="As the previous two.")

# ---- aeroelastic
C("CL-A-FLUTTER-LINE", "aeroelastic", "The speed every flutter, divergence and reversal result must beat: 1.2 times the design dive speed.", formula="line = factor x VD", sym={"k": "safety factor 1.2", "vd": "design dive speed"},
  steps=[("v_ms", "k*vd", "m/s", "flutter line")], real="Flight envelope: never exceed VD (24 m/s); an airspeed alarm at VD.")
for cid, why, via, t in [
    ("CL-A-FLUTTER-ELEVON-NOM", "Elevon flutter is the shaking of the control surface on its hinge. At 25 C this is the lowest speed at which it begins, with the hinge damper fitted.", "structures/fixes2_cdamp.md", "nominal 25 C"),
    ("CL-A-FLUTTER-ELEVON-HOT", "The same, hot (50 C), when the damper fluid is thinner.", "fixes2_cdamp.md", "hot 50 C"),
    ("CL-A-FLUTTER-ELEVON-COLD", "The same, cold (0 C).", "fixes2_cdamp.md", "cold 0 C")]:
    C(cid, "aeroelastic", why, via="the p-method flutter analysis in " + via + " (a table over wing stiffness corners kd / nominal / hi), lowest onset speed", formula="onset = lowest speed over the three corners", sym={"x": "onset speed in each corner (kd, nominal, hi)"},
      steps=[("v_ms", "min(x)", "m/s", "lowest onset")], limit_why="At least 1.2 x VD = 28.8 m/s.", real="Elevon coupon E1 (T-A-ELEVON-E1): measure hinge stiffness, free play and damper; ground vibration test on the built wing.")
C("CL-A-FLUTTER-HALF", "aeroelastic", "What if the damper leaks and is half empty? This shows how much the safety falls (no limit set).", via="fixes2_cdamp.md half-fill case", formula="lowest onset speed with half the damper fluid", sym={"v": "onset speed"},
  real="Preflight fill check of the damper every flight; O-ring seals.")
C("CL-A-FLUTTER-WING", "aeroelastic", "Wing bending-torsion flutter: the wing twisting and bending together at speed. Lowest case is with the fins removed.", via="Ritz + strip Theodorsen model in FIXES s1.3", formula="lowest of the base and fins-off cases over the three stiffness corners",
  sym={"base": "base-case speeds per corner", "nofin": "fins-off speeds per corner"}, steps=[("v_ms", "min(min(base), min(nofin))", "m/s", "lowest speed")], limit_why="At least 28.8 m/s.", real="Ground vibration test of the built wing to confirm bending and torsion frequencies.")
C("CL-A-DIVERGENCE", "aeroelastic", "Torsional divergence: above this speed the lift twists the wing more and more until it breaks.", via="Ritz / Bredt torsion-stiffness model, FLUTTER.md", formula="divergence speed from wing torsion stiffness and the aerodynamic centre offset",
  sym={"v": "divergence speed"}, limit_why="At least 28.8 m/s.", real="Measure wing torsion stiffness on the built wing (twist under a known torque).")
C("CL-A-REVERSAL", "aeroelastic", "Control reversal: above this speed the elevon flexes the wing the wrong way and works backwards.", via="FIXES s1.3, 3-D lift basis", formula="reversal speed from wing torsion stiffness and elevon effectiveness",
  sym={"x": "speed per case"}, steps=[("v_ms", "min(x)", "m/s", "lowest reversal speed")], limit_why="At least 28.8 m/s.", real="First flight envelope expansion: step up speed with elevon pulses.")
C("CL-A-GUST-N", "aeroelastic", "A 4 m/s gust at the dive speed multiplies the load on the wing. This checks the multiplier stays under the 3.4 g limit.", via="structures_run.md s2 C1 load table", formula="n = 1 + (gust lift change) / weight", sym={"v": "gust load factor"},
  limit_why="At most 3.4 g.", real="Accelerometer log in the first fast passes.")

# ---- vibration
C("CL-A-VIB-LOW-LIMIT", "vib", "Structure modes below the rotor bands must be below this frequency, so they stay 20 % clear of the lowest spin frequency.", formula="limit = low 1P edge (rpm / 60) / 1.2", sym={"rpm": "lowest hover rpm", "sep": "required 20 % separation"},
  steps=[("f_hz", "rpm/60/sep", "Hz", "upper edge of the allowed low zone")], real="Tap test on the built cage (T-A-TAP).")
C("CL-A-VIB-HIGH-LIMIT", "vib", "Modes above the rotor bands must be above this frequency.", formula="limit = high 2P edge x 1.2", sym={"f": "highest cruise 2P frequency", "sep": "required 20 % separation"},
  steps=[("f_hz", "f*sep", "Hz", "lower edge of the allowed high zone")], real="Tap test (T-A-TAP).")
C("CL-A-VIB-LOW", "vib", "The highest strongly coupled mode below the rotor bands must be under the allowed low limit.", via="the finite-element run in structures_run.md s4 (three stiffness corners)", formula="highest mode over the corners",
  sym={"x": "mode frequency per corner"}, steps=[("f_hz", "max(x)", "Hz", "highest mode")], limit_why="At most the low limit (previous card).", real="Tap test: strike the built cage and read the frequency from a phone app (T-A-TAP).")
C("CL-A-VIB-HIGH", "vib", "The lowest strongly coupled mode above the rotor bands must be over the allowed high limit.", via="structures_run.md s4", formula="lowest mode over the corners", sym={"x": "mode frequency per corner"},
  steps=[("f_hz", "min(x)", "Hz", "lowest mode")], limit_why="At least the high limit.", real="Tap test (T-A-TAP).")
C("CL-A-VIB-IN-BAND", "vib", "No strongly coupled structure mode may sit inside the rotor bands (D-185 (a)). This counts the stiffness corners that have one.", via="structures_run.md s4 and T085_report.md s3.1", formula="count of corners with a strong mode in the band", sym={"v": "corners with a mode in the band"},
  limit_why="None allowed (D-185 (a)); not relaxed.", real="Tap test with pack and motors installed (T-A-TAP, TP-10b).")
C("CL-A-VIB-FC", "vib", "The flight computer must not feel more than 30 m/s2 of vibration or its sensors degrade.", via="forced-response sweep of the T-085 upgraded model (T089_report.md s3; spar-only values in structures_run.md s4)", formula="worst acceleration over the sweep cases", sym={"x": "acceleration per case"},
  steps=[("a_ms2", "max(x)", "m/s^2", "worst vibration")], limit_why="At most 30 m/s2 (requirement A-P10 (d)).", real="Read IMU VIBE in the first tethered hover (T-A-TETHER-VIBE).")
C("CL-A-VIB-GM", "vib", "The control loop needs at least a factor of 2 of gain margin before the structure's flex modes could make it unstable.", via="fu_cage.py rebuilt for the X2216 / T-085 model, T089_report.md s2 (T-089)", formula="smallest gain margin over axes and corners", sym={"x": "gain margin per axis and corner"},
  steps=[("gm", "min(x)", "-", "smallest gain margin")], limit_why="At least 2.", real="Increase the rate gain in tethered hover until oscillation starts and compare.")
C("CL-A-VIB-GM-SHIFT", "vib", "The same gain margin if the real flex modes are 20 % off the model, which is the expected tolerance.", via="fu_cage.py rebuilt for the X2216 / T-085 model, T089_report.md s2 (T-089)", formula="smallest gain margin with modes shifted -20 % and +20 %", sym={"lo": "margins with modes -20 %", "hi": "margins with modes +20 %"},
  steps=[("gm", "min(min(lo), min(hi))", "-", "smallest gain margin")], limit_why="At least 2.", real="Tap test then repeat the margin calculation with measured frequencies.")

# ---- packaging
C("CL-A-BOX-FIT", "pack", "The packed aircraft must fit in a car trunk. The test is the biggest ratio of packed size to the 1.2 x 0.5 x 0.4 m box limit.", formula="ratio = max over the three sorted dimensions of packed / limit", sym={"box": "packed dimensions", "lim": "box limit"},
  steps=[("ratio", "max(a/b for a, b in zip(sorted(box, reverse=True), sorted(lim, reverse=True)))", "-", "worst ratio")], limit_why="At most 1.0 (fits).", real="Measure the real trunk and the packed aircraft with props on (the trunk size is not measured yet).")
for cid, why, via in [("CL-A-COLL-COUNT", "The CAD model must not have two parts overlapping. This counts overlaps deeper than the 0.05 mm tolerance across the control-surface poses.", "the collision check collide_a.py (Blender), stored reports"),
                      ("CL-A-COLL-DEPTH", "The deepest overlap of any two parts, at any pose. A designed contact (horn on its stop) is allowed to touch.", "collide_a.py stored reports"),
                      ("CL-A-WIRE-ENDS", "Every wire in the CAD must end seated in a part; an open end would be an unconnected wire in the real build.", "collide_a.py wire check"),
                      ("CL-A-WIRE-FOLDS", "No wire in the model may fold sharply (a kink the real wire could not make).", "collide_a.py kink check"),
                      ("CL-A-ASSY-STEPS", "The build sequence has numbered steps; each must be possible without parts colliding on the way in.", "a_assembly.py stored output"),
                      ("CL-A-ASSY-PARTS", "Every part in the model must appear in some build step so nothing is left out of the instructions.", "a_assembly.py stored output")]:
    C(cid, "pack", why, via=via, formula="count taken from the stored report", sym={"v": "count or depth reported"}, real="Do a dry fit of the real parts in build order; try inserting every part before gluing.")

# ---- schedule
SSYM = {"gates": "days per gate F01 to F06 (booked mornings)", "start": "planned F01 start", "deadline": "last day", "repair": "days for a crash repair loop", "redo": "mornings to redo F04", "recess": "spring recess start and end", "booked": "booked mornings a week",
        "p": "fraction of booked mornings that are flyable (estimate)", "p_sens": "pessimistic flyable fraction", "req_f01": "latest safe F01 start"}
for cid, why, out in [("CL-A-SCHED-SLACK", "How many days of spare time are there between finishing the last test gate and 30 April 2027 on the baseline plan?", "slack_days"),
                      ("CL-A-SCHED-F01", "How much later could the first tethered hover start and still end by 30 April?", "f01_slack_days"),
                      ("CL-A-SCHED-F01-DATE", "Days from the planned first-hover start to the 18 February trigger that marks the latest safe date.", "f01_to_req_days"),
                      ("CL-A-SCHED-SENS", "The same slack if only 60 % of booked mornings are flyable instead of 72 % (a sensitivity, not the plan).", "slack_sens_days")]:
    C(cid, "sched", why, formula="Gates F01 to F06 take (days per gate) at booked x p mornings a week, with one crash loop after F04. slack = deadline - end of F06.", sym=SSYM,
      method=["The schedule is a day-by-day simulation (schedule_a.py logic) that a calculator cannot redo; run python -I redesign/qp/A/schedule_a.py to reproduce it."],
      real="Compare the real gate dates against the plan every week; re-plan when the main order slips past 28 December.")

# ------------------------------------------------------------------ typeset equations (LaTeX; shown with KaTeX in the Explorer, as $$ blocks in READABLE.md)
# Only the formula is typeset here; the plain-text `formula` above stays as the fallback.
TEX = {
    "CL-A-MASS-PRED": r"m = m_{\mathrm{basic}}\,g_f + f_{\mathrm{over}}\,m_{\mathrm{gate}}",
    "CL-A-MASS-GATE-ROOM": r"m = m_{\mathrm{basic}}\,g_f + f_{\mathrm{over}}\,m_{\mathrm{gate}}",
    "CL-A-MASS-USER": r"m = m_{\mathrm{basic}}\,g_f + f_{\mathrm{over}}\,m_{\mathrm{gate}}",
    "CL-A-MASS-ITEM": r"m = \frac{\sum_i m_i\,(1+\gamma_i) + f_{\mathrm{over}}\,m_{\mathrm{gate}}\cdot 1000}{1000}",
    "CL-A-CUTS-REQUIRED": r"X = X_{\mathrm{cuts}} - \frac{m_{\mathrm{target}} - m}{g_f}\cdot 1000",
    "CL-A-STRUCT-MASS": r"m_{\mathrm{struct}} = m_{\mathrm{wing}} + m_{\mathrm{fins}} + m_{\mathrm{feet}} + m_{\mathrm{hw}} + m_{\mathrm{cage}}",
    "CL-A-CG": r"x_{CG} = \frac{\sum_i m_i\,x_i}{\sum_i m_i}",
    "CL-A-CG-HI": r"x_{CG} = \frac{\sum_i m_i\,x_i}{\sum_i m_i}",
    "CL-A-CG-LATERAL": r"y_{CG} = \frac{\sum_i m_i\,y_i}{\sum_i m_i}",
    "CL-A-CG-TRIM-AFT": r"x_{CG,\mathrm{aft}} = x_{CG} + \frac{m_{\mathrm{pack}}\,\Delta x_{\mathrm{aft}}}{m_{\mathrm{basic}}}",
    "CL-A-CG-TRIM-FWD": r"x_{CG,\mathrm{fwd}} = x_{CG} - \frac{m_{\mathrm{pack}}\,\Delta x_{\mathrm{fwd}}}{m_{\mathrm{basic}}}",
    "CL-A-SM": r"\mathrm{SM} = \frac{x_{NP} - x_{CG}}{c}\times 100\ \%",
    "CL-A-TW-FRESH-GATE": r"\frac{T}{W} = \frac{4\,T_1\cos\theta\;k_{\mathrm{derate}}\,k_{\mathrm{hot}}}{m\,g}",
    "CL-A-TW-SAG-GATE": r"\frac{T}{W} = \frac{4\,T_1\cos\theta\;k_{\mathrm{derate}}\,k_{\mathrm{hot}}}{m\,g}",
    "CL-A-TW-FRESH-PRED": r"\frac{T}{W} = \frac{4\,T_1\cos\theta\;k_{\mathrm{derate}}\,k_{\mathrm{hot}}}{m\,g}",
    "CL-A-TW-SAG-PRED": r"\frac{T}{W} = \frac{4\,T_1\cos\theta\;k_{\mathrm{derate}}\,k_{\mathrm{hot}}}{m\,g}",
    "CL-A-WINDOW-PRED": r"w = \frac{0.80\,(T/W)_{\mathrm{sag}} - 1.33}{0.80\,(T/W)_{\mathrm{sag}} + 1.33}\times 100\ \%",
    "CL-A-WINDOW-GATE": r"w = \frac{0.80\,(T/W)_{\mathrm{sag}} - 1.33}{0.80\,(T/W)_{\mathrm{sag}} + 1.33}\times 100\ \%",
    "CL-A-ESC-I": r"I_{\mathrm{req}} = 1.25\; I_{\mathrm{peak}}",
    "CL-A-BRIDGE-TORSION-F2": r"\tau = \frac{k\,M\,(d_o/2)}{J},\qquad J = \frac{\pi}{32}\left(d_o^{4} - d_i^{4}\right)",
    "CL-A-BRIDGE-TORSION-S2": r"\tau = \frac{k\,M\,(d_o/2)}{J},\qquad J = \frac{\pi}{32}\left(d_o^{4} - d_i^{4}\right)",
    "CL-A-COST-TOTAL": r"C = G\,(1+t) + S + F + R",
    "CL-A-COST-MARGIN30": r"\text{margin} = B - C_{+30\%}",
    "CL-A-CRUISE-NEED": r"R=\frac{V^{2}}{g\tan\phi},\quad t_{\mathrm{lap}}=\frac{2L+2\pi R}{V},\quad t_{\mathrm{need}} = t_{\mathrm{settle}} + (n_{\mathrm{laps}}+n_{\mathrm{ga}}+n_{\mathrm{run}})\,t_{\mathrm{lap}}",
    "CL-A-CRUISE-RADIUS": r"R = \frac{V^{2}}{g\tan\phi}",
    "CL-A-CRUISE-AVAIL": r"t_{\mathrm{cruise}} = \frac{E_{\mathrm{usable}} - E_{\mathrm{hover}} - E_{\mathrm{trans}} - E_{\mathrm{climb}}}{P_{\mathrm{cruise}}}\times 3600",
    "CL-A-FENCE": r"d = \frac{L}{2} + R + d_{\mathrm{run}}",
    "CL-A-STALL-PRED": r"V_s = \sqrt{\frac{2\,m\,g}{\rho\,S\,C_{L\max}}},\qquad \text{claim} = 1.3\,V_s",
    "CL-A-STALL": r"V_s = \sqrt{\frac{2\,m\,g}{\rho\,S\,C_{L\max}}},\qquad \text{claim} = 1.3\,V_s",
    "CL-A-YAW-MODEL": r"N = N_{\mathrm{ref}}\,k_{\mathrm{arm}}\,\frac{\sin\theta}{\sin\theta_{\mathrm{ref}}} + k_Q\,Q",
    "CL-A-YAW-R2": r"N = N_{\mathrm{ref}}\,k_{\mathrm{arm}}\,\frac{\sin\theta}{\sin\theta_{\mathrm{ref}}} + k_Q\,Q",
    "CL-A-SERVO-FACTOR": r"F = \frac{M_{\mathrm{servo}}}{k\,\left(M_{\mathrm{hinge}} + M_{\mathrm{preload}} + M_{\mathrm{damper}}\right)}",
    "CL-A-SERVO-COLD": r"F = \frac{M_{\mathrm{servo}}}{k\,\left(M_{\mathrm{hinge}} + M_{\mathrm{preload}} + M_{\mathrm{damper,cold}}\right)}\cdot\frac{\ell_{\mathrm{horn}}}{\ell_{\mathrm{arm}}}",
    "CL-A-SERVO-RATIO": r"r = \frac{M_{\mathrm{servo}}}{M_{\mathrm{hinge}}}",
    "CL-A-FLUTTER-LINE": r"V_{\mathrm{line}} = 1.2\,V_D",
    "CL-A-VIB-LOW-LIMIT": r"f_{\mathrm{low}} = \frac{n_{\min}/60}{1.2}",
    "CL-A-VIB-HIGH-LIMIT": r"f_{\mathrm{high}} = 1.2\, f_{2P,\max}",
    "CL-A-BOX-FIT": r"\rho = \max_i \frac{a_i}{b_i}",
}
_MS_TEX = r"\mathrm{MS} = \frac{\sigma_{\mathrm{allow}}}{\sigma_{\mathrm{design}}} - 1"
for _k, _v in E.items():
    if "ms" in _v:
        TEX.setdefault(_k, _MS_TEX)

# ------------------------------------------------------------------ requirements in plain words (shown in the Requirements and Overview tabs)
REQ_PLAIN = {
    "A-U1": "Everything we buy, including tax, shipping, battery, radio and a crash-repair reserve, must stay under $2,000. The team's own gate is stricter: $1,800 total, and still $100 to spare if the prices we have not confirmed turn out 30 % higher.",
    "A-U2": "The aircraft must be built and flown by 30 April 2027. The schedule is a plan of test gates; this checks the plan leaves spare days.",
    "A-U3": "The packed aircraft has to fit in a normal car trunk so four students can move it. The trunk has not been measured yet, so a standard box size stands in for it.",
    "A-U4": "The 3-D model must be physically possible: no two parts overlapping, no loose wire ends, and every assembly step can be carried out.",
    "A-U5": "A hard cap from the project brief: under 25 kg. The aircraft is about 1.5 kg, so this is a sanity check.",
    "A-D2": "The battery must power the whole mission: 3 minutes of hover plus about 3.4 minutes of cruise, with a 20 % reserve.",
    "A-P1": "The finished aircraft may weigh at most 1.47 kg (the mass gate), and with that mass the motors must still lift 2.0 times the weight with a fresh battery.",
    "A-D3": "The mass we predict from the CAD, with growth and overrun allowances, must be at most 1.467 kg, with the structure itself at most 494 g.",
    "A-P2": "Hover needs spare thrust: at least 2.0 times the weight with a full battery, and at least 1.6 times with a nearly empty one.",
    "A-P3": "Switching from hover to forward flight needs the thrust to land inside a window; the window must be at least 5 % wide on each side so timing errors do not cause a drop.",
    "A-P4": "The centre of gravity must sit in a band 19 to 26 mm behind the wing's front edge, keep at least 5 % of the chord stability margin, and stay within 5 mm of the centreline.",
    "A-P5": "In a 12 g crash the battery must stay in its tray and not fly into the electronics.",
    "A-P6": "Cruise speed must be at least 1.3 times the stall speed, so a gust cannot stall the wing.",
    "A-P7": "In hover the aircraft must be able to twist about its vertical axis with at least 0.35 N m, otherwise it cannot hold its heading.",
    "A-P8": "The aircraft must handle wind: lean no more than 40 degrees in 5 m/s wind, and no motor may sit near full throttle for more than half a second in 4 m/s turbulence.",
    "A-P9": "Standing on its fin tips, the aircraft must not tip over until the ground is tilted at least 30 degrees.",
    "A-P10": "The structure's shaking frequencies must stay 20 % away from the propeller frequencies, the flight computer must feel at most 30 m/s² of vibration, and the control loop needs a gain margin of at least 2.",
    "A-P11": "In forward flight the aircraft must roll at least 90 degrees per second, use at most 60 % of the elevon travel in transition, and the elevon servos must be 1.5 times stronger than the load.",
    "A-P13": "The structure must survive 1.5 times the highest expected loads (3.4 g, a 30 N propeller strike, a 12 g crash), and the wing and control surfaces must not flutter below 28.8 m/s.",
    "A-P16": "Each motor must stay under 13 A, and the speed controllers and connectors must be rated 25 % above the worst current.",
    "A-P24": "After a low-battery warning in cruise, the aircraft must still be inside the 240 m flying fence wherever it is on the racetrack.",
    "A-D8": "The first tethered hover must start by 18 February 2027, the latest date that still finishes everything by 30 April.",
}
