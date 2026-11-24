"""Rebuild the whole concept A proof chain.

    python -I redesign/qp/A/proofs/run_all.py

Order: params-A.json -> the four claims scripts -> build_graph.py --strict into redesign/qp/A/proofs/out/.
Requirements in REQUIREMENTS-A.md with no numeric or pass / fail basis are NOT nodes (a requirement with no claim fails the
strict build): A-D1 (configuration), A-D4 (pack mass at the weigh-in), A-D5 / A-D6 (reserve rule, one-BOM rule), A-D7 (test
order), A-D9 (>= 10 h SITL), A-D10 (transport drop, box mass: no box mass in the A files), A-D12 (wind measured), A-P8a (heading
rule, a procedure), A-P12, A-P14 (airspeed error `-`), A-P15 (Cn_beta `-`, not computed), A-P17 / A-P18 / A-P19 (notch, thermal and
BEC limits, arm and kill: no value yet; BEC against servo stall current `-`), A-P20 (declared not survivable), A-P21 / A-P22 /
A-P23, A-P25 (settings). A-P8's 8 m/s survive-and-land gust and A-D11's graph gate (this build's own result) are not claims either.
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REDESIGN = HERE.parents[2]
steps = ["gen_params_a.py", "claims_a0_base.py", "claims_a1_flight.py", "claims_a2_struct.py", "claims_a3_program.py"]
for s in steps:
    print(">>", s)
    r = subprocess.run([sys.executable, "-I", str(HERE / s)])
    if r.returncode:
        sys.exit(r.returncode)
r = subprocess.run([sys.executable, "-I", str(REDESIGN / "proofs" / "build_graph.py"), "--root", str(REDESIGN / "qp" / "A"),
                    "--out", str(HERE / "out"), "--dataset", "concept-a", "--strict"])
if r.returncode:
    sys.exit(r.returncode)
print(">> render_readable_a.py (plain-English cards: out/READABLE.md, out/readable.js; presentation only)")
sys.exit(subprocess.run([sys.executable, "-I", str(HERE / "render_readable_a.py")]).returncode)
