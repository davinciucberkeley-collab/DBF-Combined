"""build_a.py - concept A CAD: generate interfaces (2 passes), stub-build, then run check.py on model/.
    python -I redesign/qp/A/cad/build_a.py            # generate + check
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REDESIGN = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REDESIGN, 'fusion'))
sys.path.insert(0, os.path.join(REDESIGN, 'interfaces'))
import gen_interfaces as gi   # noqa: E402
import build_all              # noqa: E402
from backends.stub_backend import StubBackend  # noqa: E402

MODEL = os.path.join(HERE, 'model')


def centroids():
    ctx, _, results = build_all.build(StubBackend(), MODEL, os.path.join(MODEL, 'modules.txt'), log=lambda *a: None)
    bad = [r for r in results if not r[2]]
    for r in bad:
        print('MODULE FAILED', r[0], r[4])
    cg = {}
    for pid, c in ctx.components.items():
        if c.shapes:
            v = c.volume_centroid()[1]
            if v:
                cg[pid] = [round(x, 4) for x in v]
    return cg


if __name__ == '__main__':
    gi.write()
    cg = centroids()
    gi.write(cg)
    r = subprocess.run([sys.executable, '-I', os.path.join(REDESIGN, 'fusion', 'check.py'), '--root', MODEL])
    sys.exit(r.returncode)
