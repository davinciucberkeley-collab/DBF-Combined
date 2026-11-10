"""D2 what-if for CR-D2-16: how far the pod nose must move forward so the pack can fly at the forward stations B3,
A3 and C5 published (CR-B3-18, CR-A3-15, CL-C5-PACK-X-B3*) and still keep C5's crush block B ahead of it.

    python -I redesign/team/D2/pod_station_options.py

Rebuilds the pod CAD (subsystems/pod/fusion/pod.py) on the stub backend with pod.x_le_m moved forward by each
extension (pod.size_m length grows by the same amount; the aft end, the spar handle and the aft stop stay), and
reports per pack mass: the most forward centroid that keeps block B, the spacer needed at each published station,
and the pod mass. Block B length scales with pack mass (crush energy ~ m at a fixed crush stress and section):
L_B(m) = CL-C5-BLOCK-L x m / 550 g (UNVERIFIED: C5 to confirm). Writes nothing; numbers go into CHANGE-REQUESTS.md.
"""
import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REDESIGN = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REDESIGN / 'fusion'))
import fusionkit as fk                              # noqa: E402
import k09kit as k9                                 # noqa: E402
from backends.stub_backend import StubBackend      # noqa: E402
import pod_data as pdm                              # noqa: E402


def claim(team, cid):
    d = json.loads((REDESIGN / 'team' / team / 'claims.json').read_text(encoding='utf-8'))
    nodes = d.get('nodes', d) if isinstance(d, dict) else d
    for n in (nodes if isinstance(nodes, list) else nodes.values()):
        if isinstance(n, dict) and n.get('id') == cid:
            return n['value']
    raise KeyError(cid)


def build(ext):
    P = copy.deepcopy(k9.load_params())
    P['pod']['x_le_m']['value'] -= ext
    P['pod']['size_m']['value'][0] += ext
    parts = {p[0]: {'name': p[1], 'material': p[2], 'mass_g': 1.0, 'status': 'MODELLED'} for p in pdm.PARTS}
    ctx = fk.Context(StubBackend(), parts=parts, params=P)
    ctx.begin_module('pod', str(pdm.POD))
    k9.build_datums(ctx)
    mod = pdm.load_module()
    mod.build(ctx)
    coords, _ = k9.section(ctx)
    G = mod.layout(ctx.value, ctx.local, coords)
    M = pdm.masses(ctx, P, pdm.local())
    return G, sum(v[0] for v in M.values())


def main():
    LB = claim('C5', 'CL-C5-BLOCK-L')
    L = pdm.local()
    t_sp = L['spreader_t_m']['value']
    sp_sum = sum(L['spacer_set_m']['value'])
    stations = {   # pack mass g -> published centroid stations (m)
        503: {'B3 CR-B3-18': -0.015, 'C5 CL-C5-PACK-X-B3-LIGHT': claim('C5', 'CL-C5-PACK-X-B3-LIGHT')},
        550: {'B3 CR-B3-18': -0.012, 'A3 CL-A3-PACK-X-REQ': claim('A3', 'CL-A3-PACK-X-REQ'),
              'C5 CL-C5-PACK-X-B3': claim('C5', 'CL-C5-PACK-X-B3'), 'params (D-24)': -0.001},
        680: {'B3 CR-B3-18': 0.000, 'C5 CL-C5-PACK-X-B3-HEAVY': claim('C5', 'CL-C5-PACK-X-B3-HEAVY')},
    }
    print('CL-C5-BLOCK-L %.1f mm at 550 g; spreader %.1f mm; spacer set %.0f mm' % (LB * 1e3, t_sp * 1e3, sp_sum * 1e3))
    print('| Nose ext mm | x_le m | x_fs m | pod g | pack g | L_B mm | fwd-min centroid m | station | x m | block mm | spacer mm | fits |')
    for ext in (0.0, 0.009, 0.012, 0.015):
        G, mass = build(ext)
        for m, st in stations.items():
            lb = LB * m / 550.0
            x_min = G['x_fs'] + t_sp + lb + G['pack'][0] / 2
            for who, x in st.items():
                block = (x - G['pack'][0] / 2 - t_sp) - G['x_fs']
                spacer = G['x_as'] - (x + G['pack'][0] / 2)
                ok = block >= lb - 1e-6 and -1e-6 <= spacer <= sp_sum + 1e-6
                print('| %4.0f | %.3f | %.4f | %.1f | %d | %.1f | %.4f | %s | %.4f | %.1f | %.1f | %s |' % (
                    ext * 1e3, G['x0'], G['x_fs'], mass, m, lb * 1e3, x_min, who, x, block * 1e3, spacer * 1e3,
                    'yes' if ok else 'NO'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
