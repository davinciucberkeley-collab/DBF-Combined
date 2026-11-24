"""C4 closure round: mount mass / CG and rocking-stiffness estimate with both cheeks thickened outward by dt (EST).
Scratch only. python -I cl_mount.py  -> prints the table and writes out/cl_mount.json.

Added slab per cheek = free cheek length x cheek depth h x dt, ASA 1.07 g/cm3 (subsystems/fins/params.json
materials.asa_gcc), solid (100 % perimeters in the cheeks, ASM-C4-ASA-E text). Cheek x span: plate back face x_back
over l_out (outboard) / l (inboard); z span: tube_len/2 - ear_h/2 to z_st + plate_hz (the _mount_k depth h). y: the slab
sits outside the present outer face (outboard + , inboard -). Added to ASM-C4-MOUNT-CAD [kg, dx, dy, dz] from the
motor station (0.045, y, 0.19).
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import fin_structures_d3 as d3  # noqa: E402

kit = d3.kit
RHO_ASA = 1070.0
# D-164 (10 deg / face_ahead 14.0 mm) overrides, set by cl_opts.py / cl_d3.py: MK_IN keys and the base mount tuple.
# 10 / 14: x_face 0.0198 - 0.002 = 0.0178 (face_ahead +2 mm), cheek length 21.5 + 2 = 23.5 mm (C4.md wave 1 section 1.5:
# cheeks lengthen with face_ahead), base mount +0.26 g and CG 1.6 mm further forward (C4.md wave 1: 10/14 vs 9/12 =
# +0.85 - 0.59 g, 5.1 - 3.5 mm, scaled from the R4 -> R5 CAD step, EST)
OVR = {}
BASE_MOUNT = None
D164 = {"x_face": 0.0178, "cl": 0.0235, "cant": 10.0}
D164_MOUNT = [0.01167 + 0.00026, -0.0105 - 0.0016, 0.0005, -0.0106]


def _kw():
    k = {k: kit.value(r) for k, r in d3.MK_IN.items() if k != "k_nom"}
    k.update(OVR)
    return k


def slab(dt):
    k = _kw()
    x_back = k["x_face"] + k["plate_t"] / math.cos(math.radians(k["cant"]))
    r = d3._mount_k(**k)
    h, l_out, l_in = r["cheek_h_m"], r["cl_out_m"], k["cl"]
    z0 = k["tube_len"] / 2 - k["ear_h"] / 2
    zc = z0 + h / 2 - k["z_st"]
    m_o, m_i = l_out * h * dt * RHO_ASA, l_in * h * dt * RHO_ASA
    parts = [(m_o, x_back + l_out / 2 - k["tube_x"], k["cy"] + k["ct"] + dt / 2, zc),
             (m_i, x_back + l_in / 2 - k["tube_x"], -(k["cy_in"] + k["ct_in"] + dt / 2), zc)]
    return parts


def mount_tuple(dt):
    m0, dx0, dy0, dz0 = BASE_MOUNT or kit.value("ASM-C4-MOUNT-CAD")
    parts = [(m0, dx0, dy0, dz0)] + slab(dt)
    M = sum(p[0] for p in parts)
    return [M] + [sum(p[0] * p[i] for p in parts) / M for i in (1, 2, 3)]


def add_collar_ext(mt, dg):
    """Mount collar lengthened by dg toward the wing: ring r_i = od/2 + bond gap, wall collar_wall_m, solid ASA."""
    k = _kw()
    ri = k["od"] / 2 + k["gap"]
    m = math.pi * ((ri + k["wall"]) ** 2 - ri ** 2) * dg * RHO_ASA
    dz = (k["tube_len"] / 2 - k["grip"] - dg / 2) - k["z_st"]
    M = mt[0] + m
    return [M, mt[1] * mt[0] / M, mt[2] * mt[0] / M, (mt[3] * mt[0] + m * dz) / M]


def k_est(dt, E=None, grip=None):
    k = _kw()
    k.update({"ct": k["ct"] + dt, "ct_in": k["ct_in"] + dt})
    if grip is not None:
        k["grip"] = grip
    if E is not None:
        k["E"] = E
    return d3._mount_k(**k)["k_est"]


if __name__ == "__main__":
    rows = []
    for dt in (0.0, 0.0005, 0.0010, 0.0015):
        mt = mount_tuple(dt)
        row = {"dt_mm": dt * 1e3, "k_est_2p0": k_est(dt), "k_est_1p8": k_est(dt, 1.8e9), "mount": mt,
               "dm_g_each": (mt[0] - kit.value("ASM-C4-MOUNT-CAD")[0]) * 1e3}
        row["dm_g_aircraft"] = 4 * row["dm_g_each"]
        rows.append(row)
        print(f"dt {dt*1e3:.1f} mm  k_est {row['k_est_2p0']:6.0f} (E 2.0) {row['k_est_1p8']:6.0f} (E 1.8)  mount "
              f"{mt[0]*1e3:.2f} g dx {mt[1]*1e3:+.2f} dy {mt[2]*1e3:+.2f} dz {mt[3]*1e3:+.2f} mm  +{row['dm_g_each']:.2f} g "
              f"each, +{row['dm_g_aircraft']:.2f} g aircraft")
    (HERE / "out").mkdir(exist_ok=True)
    (HERE / "out" / "cl_mount.json").write_text(json.dumps(rows, indent=1))
