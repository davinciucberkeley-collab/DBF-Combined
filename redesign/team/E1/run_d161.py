"""E1: run propulsion.py with the D-161 params values applied in memory, before A1 writes them to params.json.

Run:  python -I redesign/team/E1/run_d161.py      -> same outputs as propulsion.py (team/E1/claims.json + report)

D-161 (closure round 2026-11-14): APC 11x5.5E / 11x5.5EP, Q_M_BAT_CURR_MAX 73.2 A. Every key below is a request to
A1 in review/CLOSURE-ROUND-2026-11-14/E1.md section D-161. Once A1 has applied them, plain propulsion.py gives the same
claims and this file can be deleted. It edits nothing on disk except what propulsion.py itself writes.
"""
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "proofs"))
import proofkit as pk  # noqa: E402

D161 = {"P:fin_detail.mount.face_ahead_m": 0.014}   # D-164: 14.0 mm, applied by A1 but not yet in D3's subsystems/fins/params.json
# (D-161's 73.2 A is in params.json since A1 applied D-161; no longer patched here)

_load = pk.load_params


def _patched(path):
    out = _load(path)
    for k, v in D161.items():
        if k in out:
            out[k] = {**out[k], "value": v, "note": f"pending in params (E1 (E1 run_d161.py): {v}"}
    return out


pk.load_params = _patched
if __name__ == "__main__":
    sys.argv = [str(HERE / "propulsion.py")] + sys.argv[1:]
    runpy.run_path(str(HERE / "propulsion.py"), run_name="__main__")
