"""B2-R4: trimmed stall with the CG height (D-62) and the B1 / B2 / B3 CLmax and NP reconciliation (CR-B1-23).

Run from the repo root after avl_wing.py and xfoil_wing.py (reads out/avl_results.json, out/xfoil_results.json):
    python -I redesign/team/B2/sim/stall_zcg.py          # ~3-6 min (about 35 AVL runs, 6 in parallel)
then python -I redesign/team/B2/sim/sim_claims.py and python -I redesign/proofs/build_graph.py.

Why: B2-R3 read the trimmed CLmax from a static-margin table built with the moment reference ON the chord plane
(z = 0) and mapped each CG to that table through B3's NP. Since D-62 the CG sits 18.5 mm above the chord plane. With
a raised CG the forward tilt of the lift vector at high alpha adds a nose-up moment that grows with CL, so the
effective NP is a function of CL and a single SM no longer describes the stall trim. This script puts the real
(x, z) of the CG into AVL as the moment reference (Xref, Zref) and runs the critical-section method directly.

Model (unchanged from avl_wing.py): AVL 3.52, wing + 0.21 m half-fins, props off, no pod; elevon eta from XFOIL;
trim to AVL Cm = cm_t (viscous section-cm correction); XFOIL section clmax vs elevon deflection (B2 envelope: lower
of the stall and cruise Re, non-increasing towards up-elevon). Props and pod enter as a CL-independent NP shift
(B3: CL-B3-V-XNP-AERO - CL-B3-V-XNP = 2.91 mm forward), so the AVL reference is x_cg + dprop (same as B3's
stall_v). The AVL ST output at each trimmed CL gives the effective NP at that CL.

Cases
  grid   x_cg in {0.0446, 0.0466, 0.0490, 0.0514, 0.0536} m  x  z_cg in {0, 0.010, 0.0185, 0.025} m (B2 method)
  recon  CR-B1-23 waterfall at the A3 predicted CG (0.0536, z 0.018), one change per step from B1's set-up to B2's:
         W0 B1 set-up (no props/pod shift, cm_t = 0, B1's raw stall-Re clmax per flap)
         W1 B2's raw stall-Re XFOIL clmax per flap (no envelope)
         W2 B2 envelope (min over Re, monotone)
         W3 + viscous cm trim correction (cm_t)
         W4 + props/pod NP shift (= grid point x 0.0536, z 0.018)
  np     effective NP vs CL at z 0 / 0.0185 (props off) for the 0.0708 vs 0.0738 question
Writes sim/out/stall_zcg.json and sim/params.zcg.json (P:b2sim.zcg.*).
"""
from __future__ import annotations

import concurrent.futures as cf
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
B2 = HERE.parent
REDESIGN = B2.parents[1]
ARGS = sys.argv[1:]
sys.argv = [sys.argv[0]]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


AW = load("avl_wing", B2 / "avl_wing.py")
A = json.loads((B2 / "out" / "avl_results.json").read_text())
FOIL = "s5010"
F = A["foils"][FOIL]
OUT = AW.OUT
CLS = [0.40, 0.47, 0.55, 0.65, 0.70, 0.74, 0.76, 0.78, 0.80, 0.82, 0.84, 0.86, 0.88, 0.90, 0.93, 0.96]
X_GRID = [0.0446, 0.0466, 0.0490, 0.0514, 0.0536]
Z_GRID = [0.0, 0.010, 0.0185, 0.025]


def claims_of(rel):
    d = json.loads((REDESIGN / rel).read_text(encoding="utf-8"))
    return {n["id"]: n for n in d.get("nodes", [])}


B3V = claims_of("team/B3/claims.verify.json")
DPROP = B3V["CL-B3-V-XNP-AERO"]["value"] - B3V["CL-B3-V-XNP"]["value"]       # props + pod NP term (B3), > 0
B1_TABLE = sorted((float(k), v) for k, v in json.loads(
    (REDESIGN / "team" / "B1" / "sim" / "vlm_xfoil_results.json").read_text())["clmax_trimmed"][
    "clmax_2d_stall_by_flap"].items())
B1_X, B1_Z = 0.05359047710729024, 0.018     # B1 vlm_xfoil.py: CL-A3-CG-X-PRED at its run, ZCG 0.018


def raw_stall_table():
    """B2 XFOIL clmax per flap at the stall Re only, no envelope (the way B1 builds its table)."""
    rows = []
    for d in (-15.0, -10.0, -5.0, 0.0, 5.0, 10.0):
        _, s = AW.polar(FOIL, AW.RE_STALL, d)
        if s and s.get("n", 0) >= 20 and s["clmax"] > 0.5:
            rows.append((d, s["clmax"]))
    return rows


def case_xz(tag, xref, zref, cm_t, cls=CLS):
    """AVL trim sweep with the moment reference at (xref, 0, zref); ST at each trimmed CL for the effective NP."""
    f = OUT / f"{tag}.avl"
    AW.write_avl(f, FOIL, F["eta"])
    txt = f.read_text().splitlines()
    txt[4] = f"{xref:.5f} 0.0 {zref:.5f}"
    f.write_text("\n".join(txt) + "\n")
    for old in OUT.glob(f"{tag}_*.txt"):
        old.unlink()
    cmds = "OPER\n"
    for c in cls:
        cmds += (f"A C {c}\nD1 PM {cm_t:.5f}\nX\nFT\n{tag}_ft_cl{c:.2f}.txt\nFS\n{tag}_fs_cl{c:.2f}.txt\n"
                 f"ST\n{tag}_st_cl{c:.2f}.txt\n")
    cmds += "\nQUIT\n"
    log = AW.run_avl(f, cmds)
    (OUT / f"{tag}.log").write_text(log[-20000:])
    res = {"trim": {}}
    for c in cls:
        ft = (OUT / f"{tag}_ft_cl{c:.2f}.txt").read_text()
        st = (OUT / f"{tag}_st_cl{c:.2f}.txt").read_text()
        d = {k: AW.grab(ft, k) for k in ("Alpha", "CLtot", "CDtot", "Cmtot")}
        m = AW.re.search(r"elevator\s*=\s*([-+0-9.Ee]+)", ft)
        d["elevator"] = float(m.group(1)) if m else None
        d["Xnp"] = AW.grab(st, "Xnp")
        d["CLa"] = AW.grab(st, "CLa")
        d["strips"] = AW.parse_fs_text(OUT / f"{tag}_fs_cl{c:.2f}.txt")
        res["trim"][f"{c:.2f}"] = d
    return res


def stall_point(res, table):
    cs = AW.critical_section(res, FOIL, table)
    if cs["CLmax_trim"] is None:
        raise RuntimeError("no strip reached clmax inside the CL list: extend CLS")
    cl = cs["CLmax_trim"]
    ks = sorted(res["trim"], key=float)
    cls = np.array([res["trim"][k]["CLtot"] for k in ks])
    xnp = np.array([res["trim"][k]["Xnp"] for k in ks])
    return {"CLmax_trim": cl, "elevator_deg": cs["elevator_deg"], "alpha_deg": cs["alpha_deg"],
            "y_first": cs["y_first_stall"], "xnp_aero_at_clmax": float(np.interp(cl, cls, xnp)),
            "xnp_aero_vs_cl": [[float(a), float(b)] for a, b in zip(cls, xnp)]}


def run_grid_point(xz):
    x, z = xz
    tag = f"r4_x{x*1e4:.0f}_z{z*1e4:.0f}"
    r = case_xz(tag, x + DPROP, z, F["cm_t"])
    return x, z, stall_point(r, F["clmax_vs_flap"])


def run_recon(step):
    raw = raw_stall_table()
    spec = {"W0": (B1_X, B1_Z, 0.0, B1_TABLE),
            "W1": (B1_X, B1_Z, 0.0, raw),
            "W2": (B1_X, B1_Z, 0.0, F["clmax_vs_flap"]),
            "W3": (B1_X, B1_Z, F["cm_t"], F["clmax_vs_flap"]),
            "W4": (B1_X + DPROP, B1_Z, F["cm_t"], F["clmax_vs_flap"])}[step]
    xr, zr, cmt, tab = spec
    r = case_xz(f"r4_recon_{step}", xr, zr, cmt)
    sp = stall_point(r, [tuple(t) for t in tab])
    sp.update({"xref": xr, "zref": zr, "cm_t": cmt, "table": [list(t) for t in tab]})
    return step, sp


def main():
    pts = [(x, z) for x in X_GRID for z in Z_GRID]
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        grid = list(ex.map(run_grid_point, pts))
        recon = dict(ex.map(run_recon, ["W0", "W1", "W2", "W3", "W4"]))
    tab = [[[None] * len(Z_GRID) for _ in X_GRID] for _ in range(3)]
    for x, z, sp in grid:
        i, j = X_GRID.index(x), Z_GRID.index(z)
        tab[0][i][j], tab[1][i][j], tab[2][i][j] = sp["CLmax_trim"], sp["elevator_deg"], sp["xnp_aero_at_clmax"]
        print(f"  x {x:.4f} z {z:.4f}: CLmax {sp['CLmax_trim']:.4f}  elevon {sp['elevator_deg']:+.2f}  "
              f"alpha {sp['alpha_deg']:.2f}  first y {sp['y_first']}  Xnp_aero@CLmax {sp['xnp_aero_at_clmax']:.5f}")
    for k, sp in recon.items():
        print(f"  {k}: CLmax {sp['CLmax_trim']:.4f}  elevon {sp['elevator_deg']:+.2f}  first y {sp['y_first']}")
    # effective NP (props off) vs CL, z 0 and z 0.0185, at the target x: from the grid runs
    npcl = {f"z{z:g}": next(sp for x, zz, sp in grid if x == 0.0490 and zz == z)["xnp_aero_vs_cl"] for z in (0.0, 0.0185)}
    res = {"_note": "team/B2/sim/stall_zcg.py output (B2-R4)", "dprop_m": DPROP, "x_grid": X_GRID, "z_grid": Z_GRID,
           "clmax": tab[0], "elevon": tab[1], "xnp_aero_at_clmax": tab[2],
           "grid": [{"x": x, "z": z, **{k: v for k, v in sp.items() if k != "xnp_aero_vs_cl"}} for x, z, sp in grid],
           "recon": {k: {kk: vv for kk, vv in v.items() if kk != "xnp_aero_vs_cl"} for k, v in recon.items()},
           "b1_table": B1_TABLE, "raw_stall_table": raw_stall_table(), "b2_envelope": F["clmax_vs_flap"],
           "xnp_aero_vs_cl": npcl, "xnp_props_off_z0_a0": F["Xnp_m"]}
    (HERE / "out" / "stall_zcg.json").write_text(json.dumps(res, indent=1))
    write_params(res)


def write_params(res):
    def e(v, unit, note):
        return {"value": v, "unit": unit, "source": "SRC-B2-AVL", "status": "MODELLED", "note": note}
    npc = {k: np.array(v) for k, v in res["xnp_aero_vs_cl"].items()}
    xnp_at = lambda k, cl: float(np.interp(cl, npc[k][:, 0], npc[k][:, 1]))   # noqa: E731
    p = {"_note": "Written by team/B2/sim/stall_zcg.py (B2-R4): AVL critical-section stall with the CG height as "
                  "the moment reference (D-62). Do not edit by hand.",
         "b2sim": {"zcg": {
             "x_grid_m": e(res["x_grid"], "m", "CG x (real aircraft); AVL Xref = x + dprop_m (props + pod NP term)"),
             "z_grid_m": e(res["z_grid"], "m", "CG height above the chord plane (AVL Zref)"),
             "clmax_grid": e(res["clmax"], "-", "trimmed CLmax [x index][z index], critical section, B2 envelope, "
                                                "cm_t trim, lattice 12x1"),
             "elevon_grid": e(res["elevon"], "deg", "elevon at the trimmed CLmax [x][z]"),
             "dprop_m": e(res["dprop_m"], "m", "props + pod NP term used: CL-B3-V-XNP-AERO - CL-B3-V-XNP at the run"),
             "recon_clmax": e({k: v["CLmax_trim"] for k, v in res["recon"].items()}, "-",
                              "CR-B1-23 waterfall at x 0.0536 z 0.018: W0 B1 set-up, W1 B2 raw stall-Re table, "
                              "W2 B2 envelope, W3 + cm_t, W4 + props/pod shift"),
             "recon_elevon": e({k: v["elevator_deg"] for k, v in res["recon"].items()}, "deg", "same steps"),
             "xnp_aero_z0185_cruise": e(xnp_at("z0.0185", 0.414), "m",
                                        "props-off effective NP at CL 0.414 (B1 cruise), CG z 0.0185, Xref 0.0490+dprop"),
             "xnp_aero_z0_cruise": e(xnp_at("z0", 0.414), "m", "same, CG on the chord plane"),
         }}}
    (HERE / "params.zcg.json").write_text(json.dumps(p, indent=1))
    print("sim/params.zcg.json written")


if __name__ == "__main__":
    if "--params" in ARGS:
        write_params(json.loads((HERE / "out" / "stall_zcg.json").read_text()))
    else:
        main()
