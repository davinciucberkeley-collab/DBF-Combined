"""One SU2 solver trial of CALC-C4-SIM-CODES into the cache: python -I run_trial.py <index into SU2_TRIALS>"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sim_fin as S  # noqa: E402

kit = S.kit
kw = {a: kit.value(r) for a, r in kit.nodes["CALC-C4-SIM-CODES"]["inputs"].items()}
g, k = S._split(kw)
S.THREADS = 4
print(S.su2_trial(g, k, *S.SU2_TRIALS[int(sys.argv[1])]), flush=True)
