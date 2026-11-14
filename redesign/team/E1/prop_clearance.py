"""E1 prop clearance probe (rev 7, CR-D3-26): true blade-to-structure gaps on the assembled stub CAD.

Run:  python -I redesign/team/E1/prop_clearance.py      -> prop_clearance.json beside this file + a printed table

Why: KO-PROP-<st> is (rev 7) the swept envelope 10 mm forward / 6 mm aft of the hub mid-plane (ASM-E1-BLADE-ENV)
plus 25 mm on every face; check.py pre-filters by box, tests the convex hull and reports the distance to the swept
volume (A5, CR-A5-22). This probe is the independent cross-check: it samples the body surfaces densely (revolve:
circles along the axis; prism: profile vertices and edge midpoints along the extrusion; anything else: the box
faces, conservative), measures the distance to the swept volume (radius D/2, E1 envelope; and the old symmetric
10 mm, ASM-E1-BLADE-HALF, for comparison), and counts hits by check.py's rule for trial values of
fin_detail.mount.face_ahead_m (fins params patched in memory only), so A1 sees geometry and tool side by side.
Python 3 stdlib; reads only. Cross-check of CL-E1-TIP-GAP-TUBE (analytic, propulsion.py).
"""
import copy
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FUSION = HERE.parents[1] / "fusion"
sys.path.insert(0, str(FUSION))
import build_all            # noqa: E402
import k09kit as k9         # noqa: E402
import merge_check          # noqa: E402
from backends.stub_backend import StubBackend  # noqa: E402

FWD, AFT, SYM = 0.010, 0.006, 0.010          # ASM-E1-BLADE-ENV, ASM-E1-BLADE-HALF
TRIALS = (0.0025, 0.0060, 0.0065, 0.0075, 0.010)
CLR = 0.025


def samples(c, sh, n=60):
    pts = [c.to_world(p) for p in sh.points()]
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    out = list(pts)
    if sh.kind == "revolve" and isinstance(sh.axis, str):
        k = "XYZ".index(sh.axis)
        o = [i for i in range(3) if i != k]
        r = (hi[o[0]] - lo[o[0]]) / 2
        cc = [(hi[i] + lo[i]) / 2 for i in range(3)]
        for a in range(n + 1):
            for j in range(48):
                q = [0.0, 0.0, 0.0]
                q[k] = lo[k] + (hi[k] - lo[k]) * a / n
                q[o[0]] = cc[o[0]] + r * math.cos(2 * math.pi * j / 48)
                q[o[1]] = cc[o[1]] + r * math.sin(2 * math.pi * j / 48)
                out.append(tuple(q))
    elif sh.kind == "prism" and isinstance(sh.axis, str):
        k = "XYZ".index(sh.axis)
        base = [p for p in pts if abs(p[k] - pts[0][k]) < 1e-9] or pts
        base = base + [tuple((base[i][j] + base[(i + 1) % len(base)][j]) / 2 for j in range(3))
                       for i in range(len(base))]
        for a in range(n + 1):
            for p in base:
                q = list(p)
                q[k] = lo[k] + (hi[k] - lo[k]) * a / n
                out.append(tuple(q))
    else:
        for a in range(n + 1):
            for b in range(n + 1):
                for k in range(3):
                    o = [i for i in range(3) if i != k]
                    for v in (lo[k], hi[k]):
                        q = [0.0, 0.0, 0.0]
                        q[k] = v
                        q[o[0]] = lo[o[0]] + (hi[o[0]] - lo[o[0]]) * a / n
                        q[o[1]] = lo[o[1]] + (hi[o[1]] - lo[o[1]]) * b / n
                        out.append(tuple(q))
    return out, (tuple(lo), tuple(hi))


def gap(p, c, n, r, fwd, aft):
    d = [p[i] - c[i] for i in range(3)]
    t = sum(d[i] * n[i] for i in range(3))                 # + aft (KO axis = shaft x', thrust toward -x')
    rr = math.sqrt(max(0.0, sum(v * v for v in d) - t * t))
    dt = max(0.0, -fwd - t, t - aft)
    return dt if rr <= r else math.hypot(dt, rr - r)


def build(face_ahead):
    orig = k9.local

    def local(name, *a, **kw):
        d = orig(name, *a, **kw)
        if name == "fins":
            d = copy.deepcopy(d)
            d["fin_detail"]["mount"]["face_ahead_m"]["value"] = face_ahead
        return d
    k9.local = local
    try:
        root, lst = build_all.roots(False, None, False)
        ctx, _, _ = build_all.build(StubBackend(), root, lst, log=lambda *a: None)
    finally:
        k9.local = orig
    return ctx


def main():
    root, _ = build_all.roots(False, None, False)
    g = merge_check.check(merge_check.load(root))
    flight = lambda pid: (g.parts.get(pid) or {}).get("flight", True)
    out = {"envelope_m": {"fwd": FWD, "aft": AFT, "sym": SYM}, "clearance_m": CLR, "trials": {}}
    for fa in TRIALS:
        ctx = build(fa)
        kos = [k for k in ctx.keepouts if k.name.startswith("KO-PROP")]
        bodies = []
        for pid, c in ctx.components.items():
            if not flight(pid) or not c.shapes or pid.startswith("PRP-"):
                continue
            for sh in c.shapes:
                pts, box = samples(c, sh)
                hull = [c.to_world(q) for q in sh.hull_points()]
                bodies.append((pid, sh.name or sh.kind, pts, box, hull))
        rows, hits = {}, set()
        for ko in kos:
            n = [float(v) for v in ko.axis]
            L = math.sqrt(sum(v * v for v in n))
            n = [v / L for v in n]
            R = ko.r - CLR
            hub = tuple(ko.center[i] + (FWD - AFT) / 2 * n[i] for i in range(3))   # KO is centred on the envelope
            for pid, nm, pts, box, hull in bodies:
                if pid in ko.exempt:
                    continue
                if ko.hits(box) and ko.hull_hits(hull):            # check.py rule (CR-A5-22 + distance, rev 7)
                    d = ko.core_distance(hull)
                    if d is None or d < CLR - 1e-6:
                        hits.add((ko.name, pid))
                if ko.name != "KO-PROP-UR":
                    continue                      # the four stations are exact mirrors
                a = min(gap(p, hub, n, R, FWD, AFT) for p in pts)
                s = min(gap(p, hub, n, R, SYM, SYM) for p in pts)
                key = pid + " / " + nm
                if s < 0.040 and (key not in rows or a < rows[key]["e1_m"]):
                    rows[key] = {"e1_m": round(a, 4), "sym_m": round(s, 4)}
        worst = min(rows.items(), key=lambda kv: kv[1]["e1_m"]) if rows else (None, None)
        out["trials"]["%.4f" % fa] = {"box_hits": len(hits), "box_hit_parts": sorted({p for _, p in hits}),
                                      "min_gap": {"body": worst[0], **(worst[1] or {})},
                                      "bodies_within_40mm": dict(sorted(rows.items(), key=lambda kv: kv[1]["e1_m"]))}
        print("face_ahead %.4f  min gap %s  E1 env %.1f mm  sym %.1f mm  | check.py hits %d %s" % (
            fa, worst[0], worst[1]["e1_m"] * 1000, worst[1]["sym_m"] * 1000, len(hits),
            sorted({p for _, p in hits})))
    (HERE / "prop_clearance.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("wrote", (HERE / "prop_clearance.json").relative_to(HERE.parents[2]).as_posix())


if __name__ == "__main__":
    main()
