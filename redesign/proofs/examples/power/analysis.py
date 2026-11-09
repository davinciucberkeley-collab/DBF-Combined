"""Example analysis (demo aircraft): mass roll-up, hover thrust-to-weight, connector currents.

Run:  python -I redesign/proofs/examples/power/analysis.py   -> claims.json beside this file
It shows the pattern every analysis script follows: declare calculations with @kit.calc, state claims with
kit.claim, call kit.write() under __main__. build_graph.py later imports this file and calls each function
again with the current params to confirm the stored numbers.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))       # redesign/proofs (python -I adds no paths)
import proofkit as pk  # noqa: E402

kit = pk.Kit(__file__, params=["../params.json"])

MOTORS = ["EX-PWR-001", "EX-PWR-002", "EX-PWR-003", "EX-PWR-004"]

kit.assumption("ASM-EX-INTERP", "Linear interpolation", "Current between two rows of the maker's thrust table "
               "varies linearly with thrust", basis="rows are 250 gf apart; the curve is smooth and convex, so linear "
               "interpolation slightly over-estimates current (conservative)")


@kit.calc("CALC-EX-MTOW", title="Mass roll-up", equation="m = sum of item masses (motors, props, ESCs x n)",
          inputs={"fus": "P:mass.fuselage_box_kg", "wing": "P:mass.wing_panels_kg", "spar": "P:mass.spar_kg",
                  "booms": "P:mass.booms_kg", "motor": "P:mass.lift_motor_kg", "prop": "P:mass.prop_kg",
                  "esc": "P:mass.esc_kg", "batt": "P:mass.battery_kg", "avn": "P:mass.avionics_kg",
                  "wires": "P:mass.wiring_kg", "servos": "P:mass.servos_kg", "n": "P:propulsion.n_lift"},
          units={"fus": "kg", "batt": "kg", "motor": "kg"}, output="m_kg")
def mtow(fus, wing, spar, booms, motor, prop, esc, batt, avn, wires, servos, n):
    return fus + wing + spar + booms + n * (motor + prop + esc) + batt + avn + wires + servos


@kit.calc("CALC-EX-HOVER-TW", title="Hover thrust-to-weight", equation="T/W = n * T_max / m  (T_max = last table row)",
          inputs={"n": "P:propulsion.n_lift", "table": "P:propulsion.thrust_table", "m_kg": "CL-EX-MTOW"},
          units={"m_kg": "kg"}, output="tw")
def hover_tw(n, table, m_kg):
    t_max_kg = max(row[1] for row in table) / 1000.0
    return n * t_max_kg / m_kg


def interp_current(table, thrust_gf):
    """Motor current at a thrust, linear between the bracketing rows of [A, gf] (ASM-EX-INTERP)."""
    rows = sorted(table, key=lambda r: r[1])
    for (a0, t0), (a1, t1) in zip(rows, rows[1:]):
        if t0 <= thrust_gf <= t1:
            return a0 + (a1 - a0) * (thrust_gf - t0) / (t1 - t0)
    raise ValueError(f"{thrust_gf:.0f} gf is outside the table")


@kit.calc("CALC-EX-HOVER-I", title="Hover pack current", assumes=["ASM-EX-INTERP"],
          equation="I_pack = n * I_motor(m * 1000 / n gf)",
          inputs={"n": "P:propulsion.n_lift", "table": "P:propulsion.thrust_table", "m_kg": "CL-EX-MTOW"},
          units={"m_kg": "kg"})
def hover_current(n, table, m_kg):
    per_motor_gf = m_kg * 1000.0 / n
    i_motor = interp_current(table, per_motor_gf)
    return {"per_motor_gf": per_motor_gf, "i_motor_a": i_motor, "i_pack_a": n * i_motor}


@kit.calc("CALC-EX-DISCONNECT", title="Main disconnect current", equation="I_req = k * I_pack,hover",
          inputs={"k": "P:requirements.disconnect_factor", "i_pack": "CL-EX-HOVER-I"}, output="i_req_a")
def disconnect_required(k, i_pack):
    return k * i_pack


@kit.calc("CALC-EX-ESC-CONN", title="ESC connector current", equation="I_req = k * I_motor,max (last table row)",
          inputs={"k": "P:requirements.disconnect_factor", "table": "P:propulsion.thrust_table"}, output="i_req_a")
def esc_connector_required(k, table):
    return k * max(row[0] for row in table)


# ---- claims: what the numbers above mean, against which limit, for which requirement ----
kit.claim("CL-EX-MTOW", "Take-off mass", calc="CALC-EX-MTOW", output="m_kg", unit="kg",
          limit=("<=", "P:requirements.mtow_max_kg"), verifies=["R-EX-MASS"], parts=["EX-FUS-001", "EX-PWR-010"],
          how="Weigh the assembled aircraft with battery on a 10 kg scale (T-EX-WEIGH).")
kit.claim("CL-EX-HOVER-TW", "Hover thrust-to-weight", calc="CALC-EX-HOVER-TW", output="tw", unit="-",
          limit=(">=", "P:requirements.hover_tw_min"), verifies=["R-EX-HOVER"], parts=MOTORS,
          how="Thrust stand: one motor + 17x5.8 prop at 22.2 V, full throttle, >= 3.13 kgf (T-EX-THRUST).")
kit.claim("CL-EX-HOVER-I", "Hover pack current", calc="CALC-EX-HOVER-I", output="i_pack_a", unit="A",
          parts=["EX-PWR-010", "EX-HRN-003"],
          how="Log battery current (power module) in a 30 s hover; compare with this value.")
kit.claim("CL-EX-DISCONNECT", "Main disconnect rating", calc="CALC-EX-DISCONNECT", output="i_req_a", unit="A",
          limit=("<=", "P:harness.main_disconnect_a"), verifies=["R-EX-DISCONNECT"], parts=["EX-HRN-001"],
          how="Open the Amass AS150U datasheet and confirm the continuous rating.")
kit.claim("CL-EX-ESC-CONN", "ESC connector rating", calc="CALC-EX-ESC-CONN", output="i_req_a", unit="A",
          limit=("<=", "P:harness.esc_connector_a"), verifies=["R-EX-DISCONNECT"], parts=["EX-HRN-002"],
          how="Compare the connector datasheet rating with 1.25 x the maker's maximum motor current.")

kit.test("T-EX-WEIGH", "Weigh the assembled aircraft", verifies=["CL-EX-MTOW"], state="run", result="pass",
         measured="5.07 kg", date="2026-11-09", procedure="Battery in, props on, kitchen scale (10 kg, 1 g).",
         note="ILLUSTRATIVE: the demo aircraft does not exist; this shows how a run test makes a claim VERIFIED.")
kit.test("T-EX-THRUST", "Static thrust, one lift unit", verifies=["CL-EX-HOVER-TW"], state="planned",
         procedure="Thrust stand, 22.2 V bench supply, 0-100 % throttle in 10 % steps, log A and gf.")

if __name__ == "__main__":
    kit.write()
