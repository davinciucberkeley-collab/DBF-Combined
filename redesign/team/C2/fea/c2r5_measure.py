"""C2-R5: read the pocket-zone field dumps of c2r5_corner.py with several stress measures.

Measures (foam elements only, pocket zone = within 30 mm of the block footprint in plan view):
  peak     element-centroid peak (singular at the bimaterial corner: grows with refinement)
  avg1     volume average over a 1 mm sphere round the peak element (the D-68 claim measure, AVG_R)
  vm(r)    critical-distance volume method used for the claim: the foam-only volume average over a ball of
           radius r, maximised over the ball centre (the 3000 highest foam elements are tried as centres). r = L/2,
           L = (1/pi) (K_Ic / sigma_0)^2 (Taylor, TCD). For a corner field sigma ~ rho^-s, the ball average of radius
           R equals the point value at rho = R (3 / (3 - s))^(-1/s): 0.70 R for s = 0.30, 0.72 R for s = 0.255, so
           vm(L/2) is the point-method stress at about 0.35 L, i.e. more conservative than the PM (0.5 L) and the
           line method (about 0.6 L for these exponents). Same-material averaging as the D-68 1 mm measure.
Ultimate = 1.5 x limit (SF of the claims). Allowables 150 / 120 / 100 kPa (wing_struct.M, unchanged).

Run: python -I redesign/team/C2/fea/c2r5_measure.py [--dir D] [--zone block|servo] [tags ...]
     -> prints and writes D/measures.json (D default out/c2r5). Zone "block" (default): ball centres and peaks within
     30 mm of the block footprint (as in wave 1). Zone "servo": within 15 mm of the lower-skin servo-pocket opening
     (subsystems/wing/params.json servo_pocket; needs a run made with c2r5_corner.py --dump-servo); key "<tag>@servo".
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "out" / "c2r5"
SF = 1.5
ALLOW = {"s1": 150e3, "s3": 120e3, "tau": 100e3}
COL = {"s1": 5, "s3": 6, "tau": 7}
FOAM = 0
# TCD length: K_Ic 0.0547 MPa m^0.5 (XPS, KEM 776:160); sigma_0 = 517 kPa (75 psi C203 flexural minimum, FOAMULAR 250)
K_IC = 0.0547e6
SIG0 = 517e3
L_TCD = (K_IC / SIG0) ** 2 / math.pi
D_LIST = [0.0010, round(L_TCD / 2, 5), 0.0025]


def v_all(R, k):
    return -R[:, COL[k]] if k == "s3" else R[:, COL[k]]


def vm_ball(R, v, foam, r, n_cent=3000, cmask=None):
    from scipy.spatial import cKDTree
    F = np.where(foam)[0]
    tree = cKDTree(R[F, :3])
    vol = R[F, 3]
    vf = v[F]
    vc = vf if cmask is None else np.where(cmask[F], vf, -np.inf)
    order = np.argsort(-vc)[:min(n_cent, int(np.isfinite(vc).sum()))]
    best, at = -np.inf, None
    for i in order:
        nb = tree.query_ball_point(R[F[i], :3], r)
        a_ = float(np.sum(vf[nb] * vol[nb]) / np.sum(vol[nb]))
        if a_ > best:
            best, at = a_, R[F[i], :3].round(4).tolist()
    return best, at


BLK_X, BLK_Y, BEAD = (0.02785, 0.09715), (0.30185, 0.33815), 0.003
_SP = json.loads((HERE.parents[2] / "subsystems" / "wing" / "params.json").read_text("utf-8"))


def _find(d, key):
    if isinstance(d, dict):
        if key in d:
            return d[key]
        for v in d.values():
            r = _find(v, key)
            if r is not None:
                return r
    return None


_sp = _find(_SP, "servo_pocket")
SP_X, SP_Y = tuple(_sp["x_m"]["value"]), tuple(_sp["y_m"]["value"])
ZONES = {"block": (BLK_X, BLK_Y, 0.030), "servo": (SP_X, SP_Y, 0.015)}
DIR = OUT


def in_zone(R, zone):
    (x0, x1), (y0, y1), m = ZONES[zone]
    dx = np.maximum(np.maximum(x0 - R[:, 0], R[:, 0] - x1), 0)
    dy = np.maximum(np.maximum(y0 - R[:, 1], R[:, 1] - y1), 0)
    return np.hypot(dx, dy) <= m


def skin_as_foam(R, tag):
    """The skin layer (mat 4 / 6) is modelled inside the outline, so it replaces the outer t_model of foam. Where
    foam lies under it (outside the block footprint + bead), its foam part is recovered from the common strain:
    sigma_foam = sigma_layer x E_foam / E_layer. The layer elements are then measured as foam."""
    j = DIR / (tag.rsplit("_", 1)[0] + ".json")
    if not j.exists():
        return R, np.zeros(len(R), bool)
    E = json.loads(j.read_text())["E"]
    R = R.copy()
    out = (R[:, 0] < BLK_X[0] - BEAD) | (R[:, 0] > BLK_X[1] + BEAD) | (R[:, 1] < BLK_Y[0] - BEAD) | (R[:, 1] > BLK_Y[1] + BEAD)
    conv = np.zeros(len(R), bool)
    for mid in (4, 6):
        if mid < len(E) and not isinstance(E[mid], str):
            sel = (R[:, 4] == mid) & out
            R[sel, 5:9] *= E[0] / E[mid]
            conv |= sel
    return R, conv


def measures(npz, zone="block"):
    d = np.load(npz)
    R, dist = d["R"], d["dist"]
    R_raw = R
    R, conv = skin_as_foam(R, Path(npz).stem.replace("_L4-CORNER-SIDE-Y", "").replace("_G2-HANG-MOTOR", "")
                           + "_x")
    foam = (R[:, 4] == FOAM) | conv
    zm = in_zone(R, zone)
    F, dF = R[foam & zm], dist[foam & zm]
    out = {}
    for k, c in COL.items():
        v = -F[:, c] if k == "s3" else F[:, c]
        i = int(np.argmax(v))
        near = np.linalg.norm(F[:, :3] - F[i, :3], axis=1) <= 0.001
        avg = float(np.sum(v[near] * F[near, 3]) / np.sum(F[near, 3]))
        row = {"peak": float(v[i]), "peak_at": F[i, :3].round(4).tolist(), "peak_dist_mm": float(dF[i] * 1e3),
               "avg1": avg}
        for dd in D_LIST:
            val, at = vm_ball(R, v_all(R, k), foam, dd, cmask=zm)
            row[f"vm_{dd * 1e3:.2f}"] = val
            row[f"vm_{dd * 1e3:.2f}_at"] = at
        out[k] = row
    # other materials: max principal / min principal in each
    other = {}
    for mid, name in ((2, "petg"), (3, "bead"), (4, "glass"), (5, "collar"), (6, "doubler")):
        S = R_raw[R_raw[:, 4] == mid]
        if len(S):
            other[name] = {"s1": float(S[:, 5].max()), "s3": float(S[:, 6].min()), "tau": float(S[:, 7].max()),
                           "s1_at": S[int(np.argmax(S[:, 5])), :3].round(4).tolist()}
    return out, other, float(d["h"])


def main():
    global DIR
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", type=Path, default=OUT)
    ap.add_argument("--zone", default="block", choices=list(ZONES))
    ap.add_argument("tags", nargs="*")
    a = ap.parse_args()
    DIR = a.dir
    tags = a.tags or sorted({p.stem for p in DIR.glob("*.npz")})
    res = {}
    print(f"L_TCD = {L_TCD * 1e3:.2f} mm, point-method distance L/2 = {L_TCD / 2 * 1e3:.2f} mm")
    for t in tags:
        p = DIR / f"{t}.npz"
        if not p.exists():
            continue
        m, other, h = measures(p, a.zone)
        t = t if a.zone == "block" else f"{t}@{a.zone}"
        res[t] = {"h_m": h, "zone": a.zone, "foam": m, "other": other}
        print(f"\n{t} (h {h * 1e3:.2f} mm), ULTIMATE kPa (allow s1 150 / s3 120 / tau 100)")
        hdr = ["peak", "avg1"] + [f"vm_{dd * 1e3:.2f}" for dd in D_LIST]
        print("      " + " ".join(f"{x:>9s}" for x in hdr))
        for k in ("s1", "s3", "tau"):
            print(f"  {k:4s}" + " ".join(f"{SF * m[k][x] / 1e3:9.1f}" for x in hdr)
                  + f"   peak at {m[k]['peak_at']} d {m[k]['peak_dist_mm']:.2f} mm; vm L/2 centre {m[k][f'vm_{L_TCD / 2 * 1e3:.2f}_at']}")
        for n, o in other.items():
            print(f"  {n}: s1 {SF * o['s1'] / 1e6:.2f} s3 {SF * o['s3'] / 1e6:.2f} tau {SF * o['tau'] / 1e6:.2f} MPa ult "
                  f"(s1 at {o['s1_at']})")
    prev = {}
    jp = DIR / "measures.json"
    if jp.exists():
        prev = json.loads(jp.read_text())
    prev.update(res)
    prev["_meta"] = {"L_tcd_m": L_TCD, "K_Ic": K_IC, "sigma0": SIG0, "SF": SF, "allow": ALLOW}
    jp.write_text(json.dumps(prev, indent=1))


if __name__ == "__main__":
    main()
