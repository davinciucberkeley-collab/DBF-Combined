"""D2 pack station table (D2-R5, D-47): for each weighed pack mass, the spacer stack (2 mm steps, colour-coded), the
centroid it gives, the crush block B cut length and the block minimum scaled from C5's 550 g length. H3 copies the
rows onto the pack labels and the flight card. The R4 what-if for CR-D2-16 (nose extension) is closed by D-47.

    python -I redesign/team/D2/pod_station_options.py            # A1's three stations (pod params pack_x_per_pack_m)
    python -I redesign/team/D2/pod_station_options.py 612 -0.019 # any other weighed pack: mass g, target centroid m

Rebuilds the pod layout on the stub backend from the current params; writes nothing.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REDESIGN = HERE.parents[1]
sys.path.insert(0, str(HERE))
import pod_data as pdm                              # noqa: E402

COLOUR = {2: 'white', 4: 'yellow', 6: 'green', 8: 'blue'}


def stack(mm, sizes=(8, 8, 6, 4, 2)):
    """Fewest spacers from the set that make mm (greedy works for 2/4/6/8/8)."""
    out, left = [], mm
    for s in sizes:
        if s <= left:
            out.append(s)
            left -= s
    return out if left == 0 else None


def block_l_c5():
    d = json.loads((REDESIGN / 'team' / 'C5' / 'claims.json').read_text(encoding='utf-8'))
    nodes = d.get('nodes', d)
    for n in (nodes if isinstance(nodes, list) else nodes.values()):
        if isinstance(n, dict) and n.get('id') == 'CL-C5-BLOCK-L':
            return n['value']
    raise KeyError('CL-C5-BLOCK-L')


def main(argv):
    _ctx, P, L, G, _src = pdm.build_pod()
    lp = G['pack'][0]
    m_nom = P['battery']['mass_kg']['value'] * 1000
    lb = block_l_c5()
    rows = {k: v['target'] for k, v in G['stations'].items()}
    if len(argv) == 2:
        rows = {argv[0]: float(argv[1])}
    print('forward stop %.4f m, aft stop %.4f m, pack %.0f mm, CL-C5-BLOCK-L %.1f mm at %.0f g' % (
        G['x_fs'], G['x_as'], lp * 1e3, lb * 1e3, m_nom))
    print('| Pack g | Target x m | Spacer mm | Stack (colours) | Centroid x m | Block B mm | Block min mm | OK |')
    print('|---|---|---|---|---|---|---|---|')
    for m, xt in sorted(rows.items(), key=lambda kv: float(kv[0])):
        sp = max(0, round((G['x_as'] - (xt + lp / 2)) * 1000 / 2) * 2)
        x = G['x_as'] - sp / 1000 - lp / 2
        blk = (x - lp / 2 - G['sp_t']) - G['x_fs']
        bmin = lb * float(m) / m_nom
        st = stack(sp)
        print('| %s | %.4f | %d | %s | %.4f | %.1f | %.1f | %s |' % (
            m, xt, sp, ' + '.join('%d %s' % (s, COLOUR[s]) for s in st) if st else 'none', x, blk * 1e3, bmin * 1e3,
            'yes' if blk >= bmin - 1e-6 else 'NO: block short'))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
