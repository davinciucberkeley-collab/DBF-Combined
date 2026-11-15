"""E1 design round 2026-11-14: prop_clearance.py's dense-surface probe at trial motor cants (in memory only).

Run:  python -I redesign/team/E1/probe_cant_1114.py  -> probe_cant_1114.json beside this file + printed table
Patches propulsion.stations.cant_deg (build_all.load_params) and fin_detail.mount.face_ahead_m (k09kit.local) in
memory; D3's canted plate and E1's station both follow the patched cant. Writes no params, no shared file.
"""
import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import prop_clearance as pc  # noqa: E402

ba, k9 = pc.build_all, pc.k9
_orig_lp = ba.load_params
TRIALS = [(7.0, 0.0075), (8.5, 0.0075), (10.0, 0.0075), (8.5, 0.0110), (10.0, 0.0130), (10.0, 0.0150)]
if "--b3" in sys.argv:                       # B3's decision (B3.md): 9 deg, face_ahead 12 mm
    TRIALS = [(9.0, 0.0120), (9.0, 0.0075)]


def run(cant, ahead):
    def lp():
        d = copy.deepcopy(_orig_lp())
        d["propulsion"]["stations"]["cant_deg"]["value"] = cant
        return d
    ba.load_params = lp
    try:
        ctx = pc.build(ahead)
    finally:
        ba.load_params = _orig_lp
    root, _ = ba.roots(False, None, False)
    g = pc.merge_check.check(pc.merge_check.load(root))
    flight = lambda pid: (g.parts.get(pid) or {}).get("flight", True)
    kos = [k for k in ctx.keepouts if k.name == "KO-PROP-UR"]
    rows = {}
    for ko in kos:
        nrm = [float(v) for v in ko.axis]
        L = sum(v * v for v in nrm) ** 0.5
        nrm = [v / L for v in nrm]
        R = ko.r - pc.CLR
        hub = tuple(ko.center[i] + (pc.FWD - pc.AFT) / 2 * nrm[i] for i in range(3))
        for pid, c in ctx.components.items():
            if not flight(pid) or not c.shapes or pid.startswith("PRP-"):
                continue
            for sh in c.shapes:
                pts, _ = pc.samples(c, sh)
                a = min(pc.gap(q, hub, nrm, R, pc.FWD, pc.AFT) for q in pts)
                key = pid + " / " + (sh.name or sh.kind)
                if a < 0.045 and (key not in rows or a < rows[key]):
                    rows[key] = round(a, 4)
    return dict(sorted(rows.items(), key=lambda kv: kv[1])[:12])


if __name__ == "__main__":
    out = {}
    for cant, ahead in TRIALS:
        r = run(cant, ahead)
        out[f"cant {cant} / face_ahead {ahead}"] = r
        print(f"cant {cant:5.1f}  face_ahead {ahead*1000:5.1f} mm:",
              "; ".join(f"{k} {v*1000:.1f}" for k, v in list(r.items())[:6]))
    (HERE / ("probe_cant_1114_b3.json" if "--b3" in sys.argv else "probe_cant_1114.json")).write_text(json.dumps(out, indent=1), encoding="utf-8")
