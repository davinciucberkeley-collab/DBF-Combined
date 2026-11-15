"""D2 D-170 study: move the pack forward for the CNHL 6000 (139 x 47 x 37 mm, ~479 g, 12 mm foam spacer).

    python -I redesign/team/D2/d170.py            # print today vs the D-170 proposal (writes nothing)
    python -I redesign/team/D2/d170.py --write    # also write team/D2/d170_overlay.json (the staged params edits)

Builds the pod CAD (subsystems/pod/fusion/pod.py through pod_data.build_pod) twice: on today's params, and on today's
params with the D-170 overlay applied in memory (shared keys for A1 + pod-local keys D2 applies once A1 has). Nothing in
params/ or subsystems/ is changed: the local overlay goes to a temp copy of subsystems/pod. Prints the pack station
range on the 2 mm spacer grid, the crush-block length, mass and CG, the hatch sweep, keep-out / seat / USB checks,
antenna and pitot numbers.
"""
import copy
import json
import math
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pod_data as pdm        # noqa: E402
import k09kit as k9           # noqa: E402

NOSE_EXT = 0.020                               # D-170: pod nose forward by 20 mm
SHARED = {                                     # key -> new value (A1 applies)
    'pod.x_le_m': round(-0.147 - NOSE_EXT, 4),
    'pod.size_m': [round(0.242 + NOSE_EXT, 4), 0.14, 0.07],
    'pod.pack_x_nominal_m': -0.056,
    'pod.pack_aft_travel_m': 0.034,            # x_as - L/2 - x_nom = 0.0475 - 0.0695 + 0.056
    'battery.size_m': [0.139, 0.047, 0.037],   # CNHL 6000 body (A3.md D-168, E2)
    'avionics.pitot_tip_xyz_m': [-0.247, -0.046, 0.045],   # tip moves with the nose: boom length unchanged
}
LOCAL = {                                      # pod-local keys D2 applies after A1
    'pack_aft_face_m': [0.0135, 0.0475],       # datum aft face = -0.056 + 0.0695; no-spacer face on the stop
    'spacer_set_m': [0.002, 0.004, 0.006, 0.006, 0.008, 0.008],   # every 2 mm stack 0-34 mm
    'spacer_flown_m': [0.008, 0.008, 0.006, 0.006, 0.004, 0.002], # 34 mm at the -0.056 datum
    'pack_x_per_pack_m': {'469': -0.056, '479': -0.056, '489': -0.056},
    'strap_x_m': [-0.090, 0.003],
    'ant_b_tip_min_x_m': round(-0.157 - NOSE_EXT, 4),
    'pack_spacer_m': [0.012, 0.139, 0.047],
}


def setv(P, key, v):
    d = P
    for k in key.split('.')[:-1]:
        d = d[k]
    leaf = d[key.split('.')[-1]]
    if isinstance(leaf, dict) and 'value' in leaf:
        leaf['value'] = v
    else:
        d[key.split('.')[-1]] = v


def box_hits(ctx, box, skip=()):
    x0, x1, y0, y1, z0, z1 = box
    n = 0
    for pid, c in ctx.components.items():
        if pid in skip:
            continue
        for sh in c.shapes:
            pts = [c.to_world(q) for q in sh.points()]
            lo = [min(q[i] for q in pts) for i in range(3)]
            hi = [max(q[i] for q in pts) for i in range(3)]
            if min(hi[0], x1) - max(lo[0], x0) > 1e-4 and min(hi[1], y1) - max(lo[1], y0) > 1e-4 and min(hi[2], z1) - max(lo[2], z0) > 1e-4:
                n += 1
    return n


def run(overlay):
    base_load, base_pod = k9.load_params, pdm.POD
    tmp = None
    try:
        if overlay:
            P = k9.load_params()
            for k, v in SHARED.items():
                setv(P, k, v)
            k9.load_params = lambda *a, **kw: copy.deepcopy(P)
            tmp = Path(tempfile.mkdtemp()) / 'pod'
            shutil.copytree(base_pod, tmp, ignore=shutil.ignore_patterns('__pycache__'))
            L = json.loads((tmp / 'params.json').read_text(encoding='utf-8'))
            for k, v in LOCAL.items():
                L[k]['value'] = v
            (tmp / 'params.json').write_text(json.dumps(L, indent=1), encoding='utf-8')
            pdm.POD = tmp
        ctx, P, L, G, _src = pdm.build_pod()
        M = pdm.masses(ctx, P, L)
    finally:
        k9.load_params, pdm.POD = base_load, base_pod
        if tmp:
            shutil.rmtree(tmp.parent, ignore_errors=True)
    pk = G['pack']
    tot = sum(v[0] for v in M.values())
    cg = [sum(M[k][0] * M[k][1][i] for k in M) / tot for i in range(3)]
    LB = 0.031                                                     # A1 D-150 block floor (C5 per-mass length is shorter)
    x_fwd_min = G['x_fs'] + G['sp_t'] + LB + pk[0] / 2
    step = 0.002
    grid_fwd = G['x_as'] - pk[0] / 2 - math.floor(round((G['x_as'] - pk[0] / 2 - x_fwd_min) / step, 6)) * step
    out = {
        'x_le': G['x0'], 'pod_len': G['x1'] - G['x0'], 'x_fs': G['x_fs'], 'x_as': G['x_as'], 'bay': G['bay'],
        'pack': pk, 'datum': G['pack_c_nom'], 'stack_datum': G['spacer_nom'], 'block_datum': G['block_nom'],
        'x_fwd_min_31': x_fwd_min, 'fwd_on_grid': grid_fwd, 'no_spacer': G['x_as'] - pk[0] / 2,
        'spacer_sum': sum(L['spacer_set_m']['value']), 'mass': {k: round(v[0], 2) for k, v in M.items()}, 'total': tot, 'cg': cg,
        'hatch_gap': G['hatch_sweep'][0], 'fc_hatch_gap': G['fc_hatch_gap'],
        'ko_hits': sum(box_hits(ctx, b) for k, b in G['ko_pwr'].items() if k != 'KO-PWR-SIDE-OUT'),
        'xt30u_hits': sum(box_hits(ctx, b) for b in G['xt30u_zone'].values()),
        'ant_a_pack': G['ant_a_pack_clr'], 'ant_b_pack': G['ant_b_pack_clr'], 'ant_b_tip_x': G['ant_b_tip_x'],
        'boom_len': G['boom_len'], 'socket_x': G['socket_x'], 'pack_top': G['zpk'] + pk[2], 'zh': G['zh'],
        'strap_x': G['strap_x'], 'pack_faces': (G['pack_fore_nom'], G['pack_aft_nom']), 'overhang_clr': G['overhang_clr'],
        'hatch_len': G['x_hatch1'] - G['x_lip1'], 'block_top': G['block_top'],
    }
    return out


def fmt(v):
    if isinstance(v, float):
        return '%.4f' % v
    if isinstance(v, (list, tuple)):
        return '[' + ', '.join(fmt(x) for x in v) + ']'
    if isinstance(v, dict):
        return '{' + ', '.join('%s: %s' % (k, fmt(x)) for k, x in v.items()) + '}'
    return str(v)


def main(argv):
    a, b = run(False), run(True)
    print('%-16s %-48s %s' % ('item', 'today', 'D-170'))
    for k in a:
        print('%-16s %-48s %s' % (k, fmt(a[k])[:48], fmt(b[k])))
    print('pod mass delta %.2f g (incl. the 12 mm foam spacer %.2f g)' % (b['total'] - a['total'], b['mass']['POD-004'] - a['mass']['POD-004']))
    if '--write' in argv:
        (HERE / 'd170_overlay.json').write_text(json.dumps(
            {'_note': 'D-170 staged edits (team/D2/d170.py). shared: A1 applies in params/params.json; local: D2 applies in '
                      'subsystems/pod/params.json after A1 (pod.py refuses a mismatched aft face / stop until both are in).',
             'shared': SHARED, 'local': LOCAL}, indent=1) + '\n', encoding='utf-8')
        print('wrote team/D2/d170_overlay.json')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
