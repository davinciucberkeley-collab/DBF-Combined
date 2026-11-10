"""D1 wing designer (revision D1-R1, params A1-R3): claims other roles build on (wing mass and CG for A3, elevon area
as built for B3, spar cover and bond area for C2, cut sizes for D2 / D3 / D6 / F2, hinge clearance for D6).

Run:  python -I redesign/team/D1/wing_data.py     (CAD masses -> subsystems/wing/interfaces.json, parts.csv)
      python -I redesign/team/D1/wing_claims.py   then  python -I redesign/proofs/build_graph.py
Wing-local numbers and CAD read-outs enter the graph as ASM-D1-* assumptions written when this script runs, so each
calculation stays a pure function of node ids (the D2 pattern). The read-outs are produced by the same functions as
the Fusion module (subsystems/wing/fusion/wing.py#layout, team/D1/wing_data.py#readouts).
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

kit = pk.Kit(__file__, params=["../../params/params.json"])
P = "P:"
WING = REDESIGN / "subsystems" / "wing"
_L = json.loads((WING / "params.json").read_text(encoding="utf-8"))
_IF = json.loads((WING / "interfaces.json").read_text(encoding="utf-8"))
SRC = ["SRC-K09-CARD", "SRC-S5010"]


def _lv(*keys):
    d = _L
    for k in keys:
        d = d[k]
    return d["value"]


def _readouts():
    import wing_data as wd
    ctx, Pp, g, mod = wd.build_wing()
    r = wd.readouts(ctx, Pp, g, mod)
    return r, g


def _prop_gap():
    """Lower bound of the gap from the real wing surfaces (core WNG-001, tape WNG-003) to the upper prop keep-outs
    KO-PROP-UR/UL (canted cylinders, R = D/2 + requirements.prop_clearance_min_m). Every body's section polygon is
    sampled densely (21 points per edge x 41 stations across the body span); per point max(|a| - half, rad - R) is a
    lower bound of its distance to the finite cylinder, so the minimum is a lower bound of the surface gap. check.py's
    per-body bounding box over-reports here (CR-E1-45, CR-D1-11)."""
    import build_all
    from backends.stub_backend import StubBackend
    root, lst = build_all.roots(False, None, False)
    ctx, _, _ = build_all.build(StubBackend(), root, lst)
    best = None
    for ko in [k for k in ctx.keepouts if k.name.startswith("KO-PROP-U")]:
        n = [float(v) for v in ko.axis]
        ln = math.sqrt(sum(v * v for v in n))
        n = [v / ln for v in n]
        for pid in ("WNG-001", "WNG-003"):
            c = ctx.components[pid]
            for sh in c.shapes:
                pts = [c.to_world(p) for p in sh.points()]
                ys = sorted(set(round(p[1], 6) for p in pts))
                if len(ys) != 2:
                    continue
                prof = [p for p in pts if abs(p[1] - ys[0]) < 1e-6]
                for i in range(len(prof)):
                    p, q = prof[i], prof[(i + 1) % len(prof)]
                    for t in range(21):
                        for k in range(41):
                            w = (p[0] + (q[0] - p[0]) * t / 20, ys[0] + (ys[1] - ys[0]) * k / 40, p[2] + (q[2] - p[2]) * t / 20)
                            d = [w[j] - ko.center[j] for j in range(3)]
                            a = sum(d[j] * n[j] for j in range(3))
                            rad = math.sqrt(max(0.0, sum(x * x for x in d) - a * a))
                            gap = max(abs(a) - ko.half, rad - ko.r)
                            if best is None or gap < best:
                                best = gap
    return best


_R, _G = _readouts()
_PROP_GAP = _prop_gap()
_PARTS = [(p["id"], p["mass_g"], p["cg_xyz_m"]) for p in _IF["parts"]]

# ---------------------------------------------------------------- assumptions (wing-local numbers and CAD read-outs)
kit.assumption("ASM-D1-PART-MASSES", "Wing part masses (CAD estimate)",
               "Declared mass of every wing instance node in subsystems/wing/interfaces.json: " + ", ".join(i for i, _m, _c in _PARTS),
               basis="team/D1/wing_data.py: XPS volume x 30 kg/m3, tape arc length x 0.065 kg/m2, spar 0.102 kg/m, C2 plug and slot-fill masses",
               value=[m for _i, m, _c in _PARTS], unit="g", status="UNVERIFIED", cites=SRC + ["SRC-XPS-F250", "SRC-CF-TUBE"])
kit.assumption("ASM-D1-PART-CGX", "Wing part CG x (CAD)", "CG x of every wing instance node, same order as ASM-D1-PART-MASSES",
               basis="subsystems/wing/interfaces.json cg_xyz_m (CAD volume centroids, tape by area)", value=[c[0] for _i, _m, c in _PARTS],
               unit="m", cites=SRC)
kit.assumption("ASM-D1-ELEVON-GAP", "Elevon end gap", "Gap at each end of each panel to the core cut-out (hot-wire kerf)",
               basis="subsystems/wing/params.json elevon.end_gap_m", value=_lv("elevon", "end_gap_m"), unit="m", cites=SRC)
kit.assumption("ASM-D1-GEOM-CAD", "Wing CAD read-outs",
               "[min foam over the closed spar bore, wall from the aft ESC groove to the spar slot, deepest groove / local thickness, "
               "foam over the servo pocket ceiling, lower-bevel clearance to the core at full down, at full up] (m, -)",
               basis="subsystems/wing/fusion/wing.py#layout() via team/D1/wing_data.py#readouts (S5010, params, fins / pod / harness params)",
               value=[round(_R["cover_min"], 6), round(_R["groove_wall"], 6), round(_R["groove_depth_frac"], 5),
                      round(_R["pocket_roof_foam"], 6), round(_R["hinge_clear"][max(_R["hinge_clear"])], 6),
                      round(_R["hinge_clear"][min(_R["hinge_clear"])], 6)], unit="m", cites=SRC)
kit.assumption("ASM-D1-TUBE-COVER", "Foam + skin over D6's torque-tube groove", "Upper skin height minus the groove ceiling at the groove walls",
               basis="team/D1/wing_data.py#readouts (mechanisms params mec.tube)", value=round(_R["tube_groove_cover"], 6), unit="m", cites=SRC)
kit.assumption("ASM-D1-POCKET-AREA", "Servo pocket bond surface", "Floor + four walls of one servo pocket (bare foam the D6 frame bonds to)",
               basis="team/D1/wing_data.py#readouts from subsystems/wing/params.json servo_pocket", value=round(_R["pocket_bond_mm2"], 1),
               unit="mm2", cites=SRC)
kit.assumption("ASM-D1-SPAR-BOND", "Spar bore bond area", "Bore surface in contact with the slot fill over both half-spans (open windows and pockets excluded)",
               basis="team/D1/wing_data.py#readouts", value=round(_R["spar_bond_mm2"], 0), unit="mm2", cites=SRC)
kit.assumption("ASM-D1-RECESS", "Pod recess cut", "Recess front x (upper skin = pod base), aft x, max depth, foam left under the floor at the aft end",
               basis="subsystems/wing/fusion/wing.py#layout() (CR-D2-04)", value=[round(_R["recess_x"][0], 5), round(_R["recess_x"][1], 5),
                                                                                 round(_R["recess_depth_max"], 5), round(_R["recess_foam_under"], 5)],
               unit="m", cites=SRC)


kit.assumption("ASM-D1-PROP-GAP", "Wing surface outside the upper prop keep-outs (CAD)",
               "Lower bound of the gap from the core and tape surfaces to KO-PROP-UR/UL (keep-out radius already includes "
               "requirements.prop_clearance_min_m)",
               basis="team/D1/wing_claims.py#_prop_gap: all modules stub-built, wing section polygons sampled densely against the "
                     "canted keep-out cylinders registered by subsystems/propulsion/fusion/propulsion.py",
               value=round(_PROP_GAP, 5), unit="m", cites=SRC)


# ---------------------------------------------------------------- calculations
@kit.calc("CALC-D1-PROP-GAP", equation="gap = min over sampled wing surface points of max(|a| - half, rad - R) to each KO-PROP-U*",
          inputs={"g": "ASM-D1-PROP-GAP"})
def prop_gap(g):
    return {"gap": g}


@kit.calc("CALC-D1-MASS", equation="wing mass = sum of the CAD part masses; CG x = sum(m x) / sum(m)",
          inputs={"m": "ASM-D1-PART-MASSES", "x": "ASM-D1-PART-CGX"})
def mass(m, x):
    M = sum(m)
    return {"mass_g": M, "cg_x": sum(a * b for a, b in zip(m, x)) / M}


@kit.calc("CALC-D1-ELEVON", equation="frac = 2 sum(span_i - 2 gap) x chord_frac x c / (b c)",
          inputs={"yi": P + "wing.elevon.inboard_y_m", "yo": P + "wing.elevon.outboard_y_m", "cf": P + "wing.elevon.chord_frac",
                  "b": P + "wing.span_m", "gap": "ASM-D1-ELEVON-GAP"})
def elevon(yi, yo, cf, b, gap):
    span = 2 * ((yi[1] - yi[0] - 2 * gap) + (yo[1] - yo[0] - 2 * gap))
    return {"frac": span * cf / b, "span_m": span}


@kit.calc("CALC-D1-CAD", equation="read-outs of wing.py#layout(): spar cover, groove wall, groove depth fraction, pocket floor, hinge clearances",
          inputs={"g": "ASM-D1-GEOM-CAD"})
def cad(g):
    return {"cover": g[0], "groove_wall": g[1], "groove_frac": g[2], "pocket_floor": g[3], "clr_down": g[4], "clr_up": g[5]}


@kit.calc("CALC-D1-AREAS", equation="pass-through of the CAD bond surfaces", inputs={"pocket": "ASM-D1-POCKET-AREA", "spar": "ASM-D1-SPAR-BOND"})
def areas(pocket, spar):
    return {"pocket_mm2": pocket, "spar_mm2": spar}


@kit.calc("CALC-D1-TUBE-COVER", equation="cover = z_upper(groove walls) - groove ceiling", inputs={"c": "ASM-D1-TUBE-COVER"})
def tube_cover(c):
    return {"cover": c}


@kit.calc("CALC-D1-RECESS", equation="read-outs of the pod recess", inputs={"r": "ASM-D1-RECESS"})
def recess(r):
    return {"x0": r[0], "x1": r[1], "depth": r[2], "under": r[3]}


# ---------------------------------------------------------------- claims
CORE = ["WNG-001"]
ALL = [i for i, _m, _c in _PARTS]
kit.claim("CL-D1-WING-MASS", "Wing subsystem mass (CAD estimate)", calc="CALC-D1-MASS", output="mass_g", unit="g",
          limit=("<=", P + "mass.allocation_g.wing"), verifies=["R-MASS-ALLOC"], parts=ALL,
          how="T-D1-WEIGH: weigh the cut core, the tube, the plugs, the tape used and the finished wing on a 1 g scale.")
kit.claim("CL-D1-WING-CG-X", "Wing subsystem CG x (CAD estimate)", calc="CALC-D1-MASS", output="cg_x", unit="m", parts=ALL,
          how="Balance the finished bare wing (no pod, fins) on two knife edges along the span; read x from the LE.")
kit.claim("CL-D1-ELEVON-FRAC", "Elevon area fraction as built (end gaps off)", calc="CALC-D1-ELEVON", output="frac", unit="-",
          limit=(">=", 0.15), verifies=["R-ELEVON-AREA"], parts=["WNG-011-L", "WNG-011-R", "WNG-012-L", "WNG-012-R"],
          how="Measure the four cut panels (span x chord) and divide by 1.15 x 0.32 m.")
kit.claim("CL-D1-SPAR-COVER", "Minimum foam over the spar bore (S5010 at x 0.080, z +0.0066)", calc="CALC-D1-CAD", output="cover",
          unit="m", limit=(">=", "ASM-A5-MIN-COVER"), parts=CORE + ["WNG-002"],
          how="Cut a 20 mm slice off a test core with the slot: calipers from the bore to each skin.")
kit.claim("CL-D1-GROOVE-WALL", "Foam wall from the aft ESC-lead groove to the spar slot", calc="CALC-D1-CAD", output="groove_wall",
          unit="m", limit=(">=", 0.003), parts=CORE, how="Calipers on the first core before skinning (F2 CR-F2-04 asks 3 mm).")
kit.claim("CL-D1-GROOVE-DEPTH-FRAC", "Deepest groove / local section thickness between x 0.06 and 0.10", calc="CALC-D1-CAD",
          output="groove_frac", unit="-", limit=("<=", 0.5), parts=CORE, how="C2 CR-C2-01 rule; depth gauge on the cut grooves.")
kit.claim("CL-D1-POCKET-ROOF", "Foam over the servo-pocket ceiling (pocket open below)", calc="CALC-D1-CAD", output="pocket_floor", unit="m",
          limit=(">=", 0.003), parts=CORE, how="Depth gauge in the cut pocket; ceiling-to-upper-skin by subtraction from the local thickness.")
kit.claim("CL-D1-POCKET-BOND", "Servo pocket bare-foam surface for the D6 frame", calc="CALC-D1-AREAS", output="pocket_mm2", unit="mm2",
          limit=(">=", "CL-C6-LINK-BOND-AREA-MIN"), parts=CORE + ["MEC-008-L", "MEC-008-R"],
          how="D6 shows the frame's bonded area; the pocket offers this much bare foam.")
kit.claim("CL-D1-SPAR-BOND-AREA", "Spar-to-core bond area", calc="CALC-D1-AREAS", output="spar_mm2", unit="mm2", parts=CORE + ["WNG-002"],
          how="Input to C2's slot-bond shear (CL-C2-SPAR-BOND-TAU); visual check of the fill along the slot before the cap goes on.")
kit.claim("CL-D1-HINGE-CLEAR-DOWN", "Elevon lower bevel clear of the core at full down", calc="CALC-D1-CAD", output="clr_down", unit="m",
          limit=(">=", 0.0005), parts=["WNG-011-R", "WNG-012-R", "WNG-001"],
          how="T-D1-THROW: hinge taped, panel to +25 deg on a protractor: a 0.5 mm feeler passes at the lower edge.")
kit.claim("CL-D1-HINGE-CLEAR-UP", "Elevon lower bevel clear of the core at full up", calc="CALC-D1-CAD", output="clr_up", unit="m",
          limit=(">=", 0.0005), parts=["WNG-011-R", "WNG-012-R", "WNG-001"], how="T-D1-THROW at -25 deg.")
kit.claim("CL-D1-TUBE-GROOVE-COVER", "Foam over the elevon torque-tube groove", calc="CALC-D1-TUBE-COVER", output="cover", unit="m",
          limit=(">=", 0.001), parts=["WNG-011-R", "WNG-012-R"], how="Calipers on a panel offcut with the groove routed; no crack on the upper face.")
kit.claim("CL-D1-RECESS-X1", "Pod recess aft end (4 mm of foam ahead of the spar)", calc="CALC-D1-RECESS", output="x1", unit="m",
          parts=CORE + ["POD-001"], how="Steel rule from the LE on the cut recess (CR-D2-04: 0.065).")
kit.claim("CL-D1-RECESS-UNDER", "Foam under the pod recess floor at its aft end", calc="CALC-D1-RECESS", output="under", unit="m",
          limit=(">=", 0.010), parts=CORE + ["POD-001"], how="Depth gauge in the recess; subtract from the local thickness.")
kit.claim("CL-D1-PROP-SURF-GAP", "Wing surface outside the upper prop keep-outs (real surface, not bounding box)", calc="CALC-D1-PROP-GAP",
          output="gap", unit="m", limit=(">=", 0.0), parts=CORE + ["WNG-003", "PRP-001-UR", "PRP-001-UL"],
          how="On the first assembled wing: rule from each upper prop tip, turned by hand, to the upper skin near the LE "
              "at |y| 0.30-0.34; must exceed requirements.prop_clearance_min_m plus this gap.")

kit.test("T-D1-WEIGH", "Weigh every wing part", verifies=["CL-D1-WING-MASS", "CL-D1-WING-CG-X"],
         procedure="1 g scale: core after cutting and pocketing, spar, 4 plugs, tape roll before / after skinning, each elevon, finished wing; "
                   "knife-edge balance of the bare wing for CG x")
kit.test("T-D1-FIT", "First-core fit checks", verifies=["CL-D1-SPAR-COVER", "CL-D1-GROOVE-WALL", "CL-D1-GROOVE-DEPTH-FRAC",
                                                       "CL-D1-POCKET-ROOF", "CL-D1-TUBE-GROOVE-COVER", "CL-D1-RECESS-X1", "CL-D1-RECESS-UNDER", "CL-D1-ELEVON-FRAC"],
         procedure="Spar slides in the slot with 0.1-0.3 mm per side; both blocks drop into their pockets; anchor saddles seat on the spar; "
                   "pod shell sits flat in the recess; grooves and pocket gauged against BUILD.md step checks")
kit.test("T-D1-THROW", "Elevon throw and clearance", verifies=["CL-D1-HINGE-CLEAR-DOWN", "CL-D1-HINGE-CLEAR-UP"],
         procedure="Hinge taped, each panel moved by hand to +/-25 deg on a protractor; no contact with the core; feeler 0.5 mm")

if __name__ == "__main__":
    kit.write()
