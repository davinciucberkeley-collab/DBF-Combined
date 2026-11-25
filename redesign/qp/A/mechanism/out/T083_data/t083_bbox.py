"""T-083: whole-aircraft CAD bounding box (geometry arithmetic) from the stub build, with the parts that set each extreme.
python -I t083_bbox.py  (prints; writes nothing)"""
import os, sys
CAD = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'cad'))
sys.path.insert(0, CAD)
import build_a  # noqa: E402  (sets the import paths)
import build_all  # noqa: E402
from backends.stub_backend import StubBackend  # noqa: E402
ctx, _, res = build_all.build(StubBackend(), build_a.MODEL, os.path.join(build_a.MODEL, 'modules.txt'), log=lambda *a: None)
lo, hi, who_lo, who_hi = [9] * 3, [-9] * 3, [''] * 3, [''] * 3
for pid, c in ctx.components.items():
    if pid.startswith('KO-') or not c.shapes:
        continue
    b = c.bbox()
    if not b:
        continue
    for i in range(3):
        if b[0][i] < lo[i]: lo[i], who_lo[i] = b[0][i], pid
        if b[1][i] > hi[i]: hi[i], who_hi[i] = b[1][i], pid
for i, ax in enumerate('xyz'):
    print(f"{ax}: {lo[i]*1e3:8.1f} ({who_lo[i]}) .. {hi[i]*1e3:8.1f} ({who_hi[i]}) = {(hi[i]-lo[i])*1e3:.1f} mm")
