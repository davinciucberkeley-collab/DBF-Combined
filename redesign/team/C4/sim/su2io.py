"""SU2 v8.5 linear-elasticity driver for the C4 hex meshes (library only, SI units).

write_mesh: SU2 native mesh, 3-D, hexahedra (VTK 12) and quadrilateral markers (VTK 9).
run: element-wise materials through FEA_FILENAME (column 2 = material index, checked on a two-material cantilever in
sim_fin.py), MARKER_CLAMPED, MARKER_LOAD (traction in Pa times the face area, along a direction), conjugate gradient
with ILU, ASCII restart read back as nodal displacements.
"""
import subprocess
import time
from pathlib import Path

import numpy as np

SU2_CFD = Path("C:/Users/dillo/tools/su2/bin/bin/SU2_CFD.exe")

CFG = """SOLVER= ELASTICITY
GEOMETRIC_CONDITIONS= SMALL_DEFORMATIONS
MATERIAL_MODEL= LINEAR_ELASTIC
ELASTICITY_MODULUS= ({E})
POISSON_RATIO= ({nu})
MATERIAL_DENSITY= ({rho})
MATERIAL_THERMAL_EXPANSION_COEFF= ({alpha})
FEA_FILENAME= props.dat
MARKER_CLAMPED= ( {clamped} )
MARKER_LOAD= ( {loads} )
MESH_FILENAME= mesh.su2
MESH_FORMAT= SU2
LINEAR_SOLVER= {solver}
LINEAR_SOLVER_PREC= ILU
LINEAR_SOLVER_ILU_FILL_IN= {fill}
LINEAR_SOLVER_ERROR= {tol}
LINEAR_SOLVER_ITER= {iters}
LINEAR_SOLVER_RESTART_FREQUENCY= 200
INNER_ITER= 1
OUTPUT_FILES= (RESTART_ASCII)
RESTART_FILENAME= restart.csv
VOLUME_OUTPUT= (COORDINATES, SOLUTION)
SCREEN_OUTPUT= (INNER_ITER, RMS_UTOL, RMS_RTOL, LINSOL_ITER, LINSOL_RESIDUAL)
HISTORY_OUTPUT= (ITER, RMS_RES, LINSOL)
"""


def write_mesh(path, nodes, hexes, markers):
    with open(path, "w") as f:
        f.write("NDIME= 3\nNELEM= %d\n" % len(hexes))
        np.savetxt(f, np.column_stack([np.full(len(hexes), 12), hexes, np.arange(len(hexes))]), fmt="%d")
        f.write("NPOIN= %d\n" % len(nodes))
        np.savetxt(f, np.column_stack([nodes, np.arange(len(nodes))]), fmt="%.10e %.10e %.10e %d")
        f.write("NMARK= %d\n" % len(markers))
        for name, q in markers.items():
            f.write("MARKER_TAG= %s\nMARKER_ELEMS= %d\n" % (name, len(q)))
            np.savetxt(f, np.column_stack([np.full(len(q), 9), q]), fmt="%d")


def run(case_dir, nodes, hexes, mat, mats, markers, clamped, loads, threads=4, tol=1e-12, iters=20000, fill=1,
        keep=False, solver="CONJUGATE_GRADIENT", check=True):
    """mats: [(E, nu)] per material index; loads: [(marker, traction Pa, (dx, dy, dz))].
    Returns (displacement (nn, 3), info dict)."""
    d = Path(case_dir)
    d.mkdir(parents=True, exist_ok=True)
    write_mesh(d / "mesh.su2", nodes, hexes, markers)
    with open(d / "props.dat", "w") as f:
        f.write("% element  material  dv  electric  density\n")
        np.savetxt(f, np.column_stack([np.arange(len(hexes)), mat, np.zeros((len(hexes), 3), int)]), fmt="%d")
    used = set(clamped) | {m for m, _, _ in loads}
    loads = list(loads) + [(m, 0.0, (1.0, 0.0, 0.0)) for m in markers if m not in used]   # SU2 wants every tag
    ld = ", ".join("%s, 1.0, %.12g, %.12g, %.12g, %.12g" % (m, t, v[0], v[1], v[2]) for m, t, v in loads)
    cfg = CFG.format(E=", ".join("%.8g" % e for e, _ in mats), nu=", ".join("%.6g" % n for _, n in mats),
                     rho=", ".join("1000" for _ in mats), alpha=", ".join("0" for _ in mats),
                     clamped=", ".join(clamped), loads=ld, tol=tol, iters=iters, fill=fill,
                     solver=solver)
    (d / "case.cfg").write_text(cfg)
    t0 = time.time()
    p = subprocess.run([str(SU2_CFD), "-t", str(threads), "case.cfg"], cwd=d, capture_output=True, text=True)
    wall = time.time() - t0
    (d / "su2.log").write_text(p.stdout + p.stderr)
    if p.returncode != 0 or not (d / "restart.csv").exists():
        raise RuntimeError("SU2 failed in %s (see su2.log)" % d)
    r = np.genfromtxt(d / "restart.csv", delimiter=",", skip_header=1)
    r = r[np.argsort(r[:, 0])]
    u = r[:, 4:7]
    if np.max(np.abs(r[:, 1:4] - nodes)) > 1e-9:
        raise RuntimeError("SU2 restart point order differs from the mesh in %s" % d)
    info = {"wall_s": round(wall, 1), "n_nodes": int(len(nodes)), "n_hex": int(len(hexes))}
    hist = d / "history.csv"
    if hist.exists():
        lines = [ln for ln in hist.read_text().splitlines() if ln.strip()]
        head = [h.strip().strip('"') for h in lines[0].split(",")]
        last = [x.strip() for x in lines[-1].split(",")]
        info["history"] = dict(zip(head, last))
    if not keep:
        for f in ("mesh.su2", "restart.csv", "props.dat"):
            if (d / f).exists():
                (d / f).unlink()
    return u, info
