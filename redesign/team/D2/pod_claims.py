"""D2 pod designer: claims other roles build on (pack bay, trim travel, pack and pod retention, carry point,
pod-to-wing bond first cut, recess for D1, pitot boom, pod mass).

Run:  python -I redesign/team/D2/pod_data.py   (CAD masses -> interfaces.json)
      python -I redesign/team/D2/pod_claims.py  then  python -I redesign/proofs/build_graph.py
Pod-only design numbers come from subsystems/pod/params.json and the CAD roll-up (team/D2/pod_data.py); they enter
the graph as ASM-D2-* assumptions written when this script runs, so the calculations stay pure functions of node
ids. The geometry formulas are the same as subsystems/pod/fusion/pod.py#layout().
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REDESIGN = HERE.parents[1]
sys.path.insert(0, str(REDESIGN / "proofs"))
sys.path.insert(0, str(REDESIGN / "fusion"))
sys.path.insert(0, str(HERE))
import proofkit as pk  # noqa: E402
import k09kit as k9    # noqa: E402

kit = pk.Kit(__file__, params=["../../params/params.json"])
P = "P:"
POD = REDESIGN / "subsystems" / "pod"
_L = json.loads((POD / "params.json").read_text(encoding="utf-8"))
_lv = lambda k: _L[k]["value"]
_IF = json.loads((POD / "interfaces.json").read_text(encoding="utf-8"))
_MASSES = {p["id"]: p["mass_g"] for p in _IF["parts"]}
SRC_POD = ["SRC-K09-CARD"]

# ---------------------------------------------------------------- assumptions (pod-local numbers, D2 choices)
kit.assumption("ASM-D2-POD-WIDTH", "Pod outside width", "Pod outside width that holds the 52 mm bay and two 37 mm side channels",
               basis="subsystems/pod/params.json#width_m; params.json pod.size_m[1] = 0.10 until A1 decides CR-D2-01",
               value=_lv("width_m"), unit="m", cites=SRC_POD)
kit.assumption("ASM-D2-BAY-W", "Pack bay width between the guides", "Inside width of the bay", basis="E2 CR-E2-02 minimum, D2 uses it exactly",
               value=_lv("bay_min_m")[1], unit="m", cites=SRC_POD)
kit.assumption("ASM-D2-FLOOR-STACK", "Tray floor + anti-slip pad under the pack", "Height from the foam-board floor top to the pack underside",
               basis="subsystems/pod/params.json tray_floor_t_m + pad_t_m", value=_lv("tray_floor_t_m") + _lv("pad_t_m"), unit="m", cites=SRC_POD)
kit.assumption("ASM-D2-SLOT-WALL", "Foam between the pod recess and the spar slot", "Recess ends this far ahead of the spar-slot front face",
               basis="subsystems/pod/params.json slot_wall_m; D1 confirms on the first core (CR-D2-04)", value=_lv("slot_wall_m"), unit="m", cites=SRC_POD)
kit.assumption("ASM-D2-STOP-T", "Aft stop wall thickness", "Printed wall at the recess end, the pack's aft stop",
               basis="subsystems/pod/params.json stop_wall_t_m", value=_lv("stop_wall_t_m"), unit="m", cites=SRC_POD)
kit.assumption("ASM-D2-TRIM-NEED", "Aft trim travel needed", "Pack travel aft of the forward stop that re-trims a 680 g pack to the 0.044 m target",
               basis="A3 MASS-CG.md: 680 g pack at the nominal station gives CG 0.040 m; 0.26 mm CG per mm of pack: "
                     "(0.0447 - 0.040) / 0.26 = 18 mm", value=0.018, unit="m", status="UNVERIFIED", cites=SRC_POD)
kit.assumption("ASM-D2-STRAP-CAP", "Installed strap loop capacity", "Breaking load of one 20 mm hook-and-loop battery strap loop as installed (two legs)",
               basis="ESTIMATE for rubber-backed RC battery straps; T-D2-STRAP-PULL pulls one loop to 2 x 85 N", value=100.0, unit="N",
               status="UNVERIFIED", cites=SRC_POD)
kit.assumption("ASM-D2-N-STRAPS", "Pack straps", "Straps holding the pack in z and y", basis="D2 design", value=2, unit="-", cites=SRC_POD)
kit.assumption("ASM-D2-TIE-CAP", "Spar tie capacity", "Rated tensile strength of one 7.6 mm heavy-duty nylon cable tie (50 lb class)",
               basis="catalogue class value 50 lbf = 222 N; T-D2-HANDLE-PULL proof-loads the handle", value=222.0, unit="N",
               status="UNVERIFIED", cites=SRC_POD)
kit.assumption("ASM-D2-N-TIES", "Spar ties", "One tie per handle foot", basis="D2 design", value=2, unit="-", cites=SRC_POD)
kit.assumption("ASM-D2-ULT", "Ultimate factor", "Ultimate = 1.5 x limit for handling loads", basis="C1 LOADS.md convention (limit x 1.5)",
               value=1.5, unit="-", cites=SRC_POD)
kit.assumption("ASM-D2-POD-M-ULT", "Pod-to-wing moment, ultimate", "Pitching moment at the pod bond in the L1 landing, ultimate",
               basis="team/C1/LOADS.md joint table row 'Pod -> wing (C3)': 2.0 N m limit, 3.0 N m ultimate", value=3.0, unit="N m", cites=SRC_POD)
kit.assumption("ASM-D2-XPS-ALLOW", "XPS bond allowable (tension)", "Allowable tensile stress at an epoxy-to-XPS F-250 bond line, foam failure",
               basis="ESTIMATE, conservative for 25 psi XPS (compressive 172 kPa); C3 confirms with T-D2-BOND-PULL", value=100000.0,
               unit="Pa", status="UNVERIFIED", cites=SRC_POD)
kit.assumption("ASM-D2-PART-MASSES", "Pod part masses from the CAD", "Declared masses of POD-001 ... POD-008 (g), body volumes x densities",
               basis="team/D2/pod_data.py from subsystems/pod/fusion/pod.py; foam board areal mass and PETG fill are estimates; weigh (T-D2-WEIGH)",
               value=[_MASSES[k] for k in sorted(_MASSES)], unit="g", status="UNVERIFIED", cites=SRC_POD)
kit.assumption("ASM-D2-PITOT-Y", "Pitot boom lateral station", "Boom on the left side-channel centre, beside the pack",
               basis="subsystems/pod/params.json pitot_y_m; CR-D2-03 asks F3/B4/A1 to move the tip from y 0", value=_lv("pitot_y_m"), unit="m", cites=SRC_POD)
kit.assumption("ASM-D2-SOCKET", "Pitot socket length inside / collar outside", "Socket depth behind the nose wall and collar ahead of it",
               basis="subsystems/pod/params.json socket_m", value=[_lv("socket_m")[2], _lv("socket_m")[3]], unit="m", cites=SRC_POD)


def _section(coords):
    return [tuple(p) for p in coords]


# ---------------------------------------------------------------- calculations
@kit.calc("CALC-D2-BAY", equation="bay L = (spar x - r - slot wall - stop t) - (pod LE + board t); H = (base + H - t) - (base + t + floor stack); "
          "pack centroid fwd = pod LE + t + L_pack/2; travel = bay L - L_pack",
          inputs={"x_le": P + "pod.x_le_m", "size": P + "pod.size_m", "z_base": P + "pod.z_base_m", "t": P + "fins.board_t_m",
                  "xs": P + "wing.spar.x_m", "od": P + "wing.spar.od_m", "wall": "ASM-D2-SLOT-WALL", "stop": "ASM-D2-STOP-T",
                  "stack": "ASM-D2-FLOOR-STACK", "bw": "ASM-D2-BAY-W", "pack": P + "battery.size_m"})
def bay(x_le, size, z_base, t, xs, od, wall, stop, stack, bw, pack):
    xn = x_le + t
    x_stop = xs - od / 2 - wall - stop
    bay_l = x_stop - xn
    zh = z_base + size[2] - t
    zp = z_base + t + stack
    c_fwd = xn + pack[0] / 2
    return {"bay_l": bay_l, "bay_w": bw, "bay_h": zh - zp, "pack_x_fwd": c_fwd,
            "pack_ahead_of_centre": (x_le + size[0] / 2) - c_fwd, "travel": bay_l - pack[0], "pack_z": zp + pack[2] / 2,
            "x_stop": x_stop}


@kit.calc("CALC-D2-RECESS", equation="x0: upper surface z(x) = pod base; depth = z(x_end) - base, x_end = spar x - r - wall; "
          "foam under = base - lower surface z(x_end)",
          inputs={"sec": "ASM-A5-SECTION", "c": P + "wing.chord_m", "z_base": P + "pod.z_base_m", "xs": P + "wing.spar.x_m",
                  "od": P + "wing.spar.od_m", "wall": "ASM-D2-SLOT-WALL"})
def recess(sec, c, z_base, xs, od, wall):
    co = _section(sec)
    zu = lambda x: k9.surface_z(co, c, x / c, "upper")
    lo, hi = 0.0, xs
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if zu(mid) < z_base else (lo, mid)
    x1 = xs - od / 2 - wall
    return {"x0": (lo + hi) / 2, "x1": x1, "depth": zu(x1) - z_base,
            "foam_under": z_base - k9.surface_z(co, c, x1 / c, "lower")}


@kit.calc("CALC-D2-STRAPS", equation="capacity = n straps x installed loop capacity", inputs={"n": "ASM-D2-N-STRAPS", "cap": "ASM-D2-STRAP-CAP"})
def straps(n, cap):
    return {"capacity_n": n * cap}


@kit.calc("CALC-D2-POD-CRASH", equation="F = (pod + avionics + power - nominal pack + heaviest pack listing) x n_crash x g",
          inputs={"pod": P + "mass.allocation_g.pod", "avn": P + "mass.allocation_g.avionics", "pwr": P + "mass.allocation_g.power",
                  "pack_nom": P + "battery.mass_kg", "pack_rng": "ASM-A3-PACK-RANGE", "n": "CL-C1-CRASH-N", "g": P + "env.g_ms2"})
def pod_crash(pod, avn, pwr, pack_nom, pack_rng, n, g):
    m_g = pod + avn + pwr - pack_nom * 1000 + max(pack_rng)
    return {"mass_g": m_g, "force_n": m_g / 1000 * n * g}


@kit.calc("CALC-D2-TIES", equation="capacity = n ties x tie rating", inputs={"n": "ASM-D2-N-TIES", "cap": "ASM-D2-TIE-CAP"})
def ties(n, cap):
    return {"capacity_n": n * cap}


@kit.calc("CALC-D2-HANDLE", equation="F_ult = gate mass x g x handling factor x ultimate factor",
          inputs={"m": P + "requirements.mtow_gate_kg", "g": P + "env.g_ms2", "nh": "ASM-C1-HANDLING-N", "u": "ASM-D2-ULT"})
def handle(m, g, nh, u):
    return {"force_ult_n": m * g * nh * u}


@kit.calc("CALC-D2-BOND", equation="sigma = F/A + M / (b L^2 / 6); A = b L, b = pod width, L = pod TE - recess start",
          inputs={"F": "CL-C1-POD-F-ULT", "M": "ASM-D2-POD-M-ULT", "b": "ASM-D2-POD-WIDTH", "x_le": P + "pod.x_le_m",
                  "size": P + "pod.size_m", "x0": "CL-D2-RECESS-X0"})
def bond(F, M, b, x_le, size, x0):
    L = x_le + size[0] - x0
    return {"stress_pa": F / (b * L) + M / (b * L * L / 6.0), "length_m": L, "area_m2": b * L}


@kit.calc("CALC-D2-PITOT", equation="boom length = socket inner end - tip x; exposed = pod LE - collar - tip x",
          inputs={"tip": P + "avionics.pitot_tip_xyz_m", "x_le": P + "pod.x_le_m", "t": P + "fins.board_t_m", "sock": "ASM-D2-SOCKET"})
def pitot(tip, x_le, t, sock):
    inner = x_le + t + sock[0]
    return {"boom_len": inner - tip[0], "exposed": (x_le - sock[1]) - tip[0], "socket_depth": inner - (x_le - sock[1])}


@kit.calc("CALC-D2-MASS", equation="pod mass = sum of the CAD part masses", inputs={"parts": "ASM-D2-PART-MASSES"})
def mass(parts):
    return {"mass_g": sum(parts)}


# ---------------------------------------------------------------- claims
PODP = ["POD-001", "POD-002"]
kit.claim("CL-D2-BAY-L", "Pack bay inside length (nose wall to aft stop)", calc="CALC-D2-BAY", output="bay_l", unit="m",
          limit=(">=", 0.160), verifies=["R-BATT-HANDLING"], parts=PODP, cites=SRC_POD,
          how="Measure nose wall to aft stop inside the built pod; drop the real pack in with the spacers out.",
          note="E2 CR-E2-02 minimum 0.160 m")
kit.claim("CL-D2-BAY-W", "Pack bay inside width (between the guides)", calc="CALC-D2-BAY", output="bay_w", unit="m",
          limit=(">=", 0.052), verifies=["R-BATT-HANDLING"], parts=PODP, how="Calipers between the guides.")
kit.claim("CL-D2-BAY-H", "Pack bay inside height (pad top to hatch underside)", calc="CALC-D2-BAY", output="bay_h", unit="m",
          limit=(">=", 0.053), verifies=["R-BATT-HANDLING"], parts=PODP + ["POD-003"],
          how="Close the hatch over the strapped pack with the balance lead parked: no bulge.")
kit.claim("CL-D2-PACK-X-FWD", "Pack centroid at the forward stop (nominal station)", calc="CALC-D2-BAY", output="pack_x_fwd", unit="m",
          parts=PODP, how="Mark the pack centre; measure from the wing LE with the pack against the nose wall.",
          note="D-17 asks for 29 mm ahead of the pod centre (-0.034 m); the nose wall allows 25 mm (CR-D2-02, CR-A3-11 option a)")
kit.claim("CL-D2-PACK-AHEAD", "Pack centroid ahead of the pod centre at the forward stop", calc="CALC-D2-BAY", output="pack_ahead_of_centre",
          unit="m", parts=PODP, how="As CL-D2-PACK-X-FWD.")
kit.claim("CL-D2-PACK-TRAVEL", "Pack aft trim travel (forward stop to aft stop)", calc="CALC-D2-BAY", output="travel", unit="m",
          limit=(">=", "ASM-D2-TRIM-NEED"), verifies=["R-CG-RANGE"], parts=PODP + ["POD-008"],
          how="Slide the real pack from the nose wall to the aft stop; record the travel; balance at both ends (T-A3-CG-BALANCE).")
kit.claim("CL-D2-PACK-Z", "Pack centroid height", calc="CALC-D2-BAY", output="pack_z", unit="m", parts=PODP,
          how="Measure pad top above the chord line + half the pack height.")
kit.claim("CL-D2-RECESS-X0", "Pod recess start (upper surface at the pod base)", calc="CALC-D2-RECESS", output="x0", unit="m",
          parts=["POD-001"], how="Template on the hot-wired core; the recess floor meets the skin here.")
kit.claim("CL-D2-RECESS-DEPTH", "Pod recess depth at its aft end (D1 cuts)", calc="CALC-D2-RECESS", output="depth", unit="m",
          parts=["POD-001"], how="Depth gauge at the recess aft end before bonding.")
kit.claim("CL-D2-RECESS-FOAM", "Foam left under the recess at its aft end", calc="CALC-D2-RECESS", output="foam_under", unit="m",
          limit=(">=", 0.015), parts=["POD-001"], how="Calipers through the core at the recess end.",
          note="15 mm keeps the root section stiffer than the outboard core at the tubes (~27 mm thick)")
kit.claim("CL-D2-STRAP-CAP", "Pack strap capacity (2 straps)", calc="CALC-D2-STRAPS", output="capacity_n", unit="N",
          limit=(">=", "CL-C1-PACK-CRASH-LOAD"), verifies=["R-PACK-RETENTION"], parts=["POD-004", "POD-002"],
          how="T-D2-STRAP-PULL: one installed loop pulled to 2 x 85 N without slip or tear.")
kit.claim("CL-D2-POD-CRASH-F", "Pod group crash load (pod, heaviest pack, avionics, power), ultimate", calc="CALC-D2-POD-CRASH",
          output="force_n", unit="N", parts=["POD-001", "POD-007"], how="Recompute from weighed masses.")
kit.claim("CL-D2-TIE-CAP", "Spar ties: pod retention capacity", calc="CALC-D2-TIES", output="capacity_n", unit="N",
          limit=(">=", "CL-D2-POD-CRASH-F"), verifies=["R-PACK-RETENTION"], parts=["POD-007"],
          how="T-D2-HANDLE-PULL: 120 N on the handle grip for 10 s, no tie slip, no foot lift.")
kit.claim("CL-D2-HANDLE-F-ULT", "Carry handle load, lifting at 2 g, ultimate", calc="CALC-D2-HANDLE", output="force_ult_n", unit="N",
          parts=["POD-007"], how="Covered by T-D2-HANDLE-PULL (120 N > this).")
kit.claim("CL-D2-BOND-STRESS", "Pod-to-wing bond stress, L1 ultimate, first cut (C3 sizes)", calc="CALC-D2-BOND", output="stress_pa",
          unit="Pa", limit=("<=", "ASM-D2-XPS-ALLOW"), verifies=["R-STRUCT-MARGIN"], parts=["POD-001"],
          how="T-D2-BOND-PULL: 50 x 50 mm coupon of the same epoxy on F-250 pulled to foam failure; C3 replaces this first cut.")
kit.claim("CL-D2-PITOT-BOOM-L", "Pitot boom length (socket inner end to tip)", calc="CALC-D2-PITOT", output="boom_len", unit="m",
          verifies=["R-AIRSPEED"], parts=["POD-006"], how="F3 cuts the boom to this length; check the tip at x -0.185 m with the boom seated.")
kit.claim("CL-D2-PITOT-SOCKET", "Pitot socket depth", calc="CALC-D2-PITOT", output="socket_depth", unit="m", parts=["POD-006"],
          how="Depth gauge in the bore.")
kit.claim("CL-D2-MASS", "Pod subsystem mass (CAD estimate)", calc="CALC-D2-MASS", output="mass_g", unit="g",
          limit=("<=", P + "mass.allocation_g.pod"), verifies=["R-MASS-ALLOC"], parts=sorted(_MASSES),
          how="T-D2-WEIGH: weigh every pod part before bonding; update interfaces.json.")

# ---------------------------------------------------------------- tests (planned)
kit.test("T-D2-WEIGH", "Weigh every pod part before assembly", verifies=["CL-D2-MASS"],
         procedure="0.1 g scale; each printed part and board piece; record in subsystems/pod/parts.csv")
kit.test("T-D2-FIT", "Real pack fit", verifies=["CL-D2-BAY-L", "CL-D2-BAY-W", "CL-D2-BAY-H", "CL-D2-PACK-TRAVEL"],
         procedure="Both packs: in through the hatch, strapped at both trim ends, XT60 and balance lead reachable, hatch closes")
kit.test("T-D2-STRAP-PULL", "Strap loop pull test", verifies=["CL-D2-STRAP-CAP"],
         procedure="Spring scale, one installed loop on a tray offcut, 170 N for 10 s; no slip, no tear at the slot")
kit.test("T-D2-HANDLE-PULL", "Handle proof load on the built wing", verifies=["CL-D2-TIE-CAP"],
         procedure="Wing supported at the spar ends; 12 kg on the grip for 10 s; feet stay on the spar, ties do not slip")
kit.test("T-D2-BOND-PULL", "Epoxy-on-XPS pull-off coupon", verifies=["CL-D2-BOND-STRESS"],
         procedure="Two 50 x 50 mm PETG pads bonded to F-250 offcut with the build epoxy, 24 h cure, pull to failure; foam must fail")

if __name__ == "__main__":
    kit.write()
