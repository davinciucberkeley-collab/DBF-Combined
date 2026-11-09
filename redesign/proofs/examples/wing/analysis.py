"""Example analysis (demo aircraft): stall speed and wing-spar root stress.

Run after power/analysis.py (it reads CL-EX-MTOW from power/claims.json):
    python -I redesign/proofs/examples/wing/analysis.py
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))       # redesign/proofs
import proofkit as pk  # noqa: E402

kit = pk.Kit(__file__, params=["../params.json"])

kit.assumption("ASM-EX-CLMAX", "Aircraft CLmax 1.1", "Whole-aircraft maximum lift coefficient, no flaps",
               value=1.1, unit="-", status="UNVERIFIED",
               basis="typical of a rectangular wing with a 12 % low-Re section; replace with the aero analysis")
kit.assumption("ASM-EX-UNIFORM-LIFT", "Uniform spanwise lift", "Lift is spread evenly along the span",
               basis="puts each half's resultant at b/4 = 0.25 b, outboard of the elliptic 0.21 b, so the root "
                     "moment is over-estimated (conservative)")


@kit.calc("CALC-EX-STALL", title="Stall speed", equation="Vs = sqrt(2 m g / (rho b c CLmax))",
          inputs={"m": "CL-EX-MTOW", "g": "P:env.g_ms2", "rho": "P:env.rho_kgm3", "b": "P:wing.span_m",
                  "c": "P:wing.chord_m", "cl_max": "ASM-EX-CLMAX"},
          units={"m": "kg", "rho": "kg/m3", "b": "m", "c": "m"})
def stall_speed(m, g, rho, b, c, cl_max):
    s = b * c
    return {"S_m2": s, "Vs_ms": math.sqrt(2 * m * g / (rho * s * cl_max))}


@kit.calc("CALC-EX-SPAR", title="Spar root stress", assumes=["ASM-EX-UNIFORM-LIFT"],
          equation="M = n m g / 2 * b / 4;  I = pi/64 (D^4 - d^4);  sigma = SF * M (D/2) / I",
          inputs={"m": "CL-EX-MTOW", "g": "P:env.g_ms2", "n": "P:requirements.load_factor", "b": "P:wing.span_m",
                  "od": "P:wing.spar_od_mm", "wall": "P:wing.spar_wall_mm", "sf": "P:requirements.safety_factor"},
          units={"m": "kg", "b": "m", "od": "mm", "wall": "mm"})
def spar_stress(m, g, n, b, od, wall, sf):
    moment_nmm = n * m * g / 2 * (b / 4) * 1000.0           # half the lift, acting at b/4 (N*mm)
    i_mm4 = math.pi / 64 * (od ** 4 - (od - 2 * wall) ** 4)
    sigma = moment_nmm * (od / 2) / i_mm4                    # N/mm2 = MPa
    return {"M_root_Nm": moment_nmm / 1000.0, "I_mm4": i_mm4, "sigma_MPa": sigma, "sigma_design_MPa": sf * sigma}


kit.claim("CL-EX-STALL", "Stall speed at MTOW", calc="CALC-EX-STALL", output="Vs_ms", unit="m/s",
          limit=("<=", "P:requirements.stall_max_ms"), verifies=["R-EX-STALL"],
          parts=["EX-WNG-001", "EX-WNG-002", "EX-WNG-004"],
          how="Replace ASM-EX-CLMAX with the aero analysis CLmax; flight: slow-flight stall at MTOW with airspeed logging.")
kit.claim("CL-EX-SPAR", "Spar design stress", calc="CALC-EX-SPAR", output="sigma_design_MPa", unit="MPa",
          limit=("<=", "P:wing.spar_yield_mpa"), verifies=["R-EX-SPAR"], parts=["EX-WNG-003"],
          how="Wingtip load test: support at the root, hang n*m*g/2 spread over each half, check no permanent set.")

if __name__ == "__main__":
    kit.write()
