"""D2 pod self-check: run check.py's checks on the pod against stand-ins for the parts it joins that other roles
have not declared yet (wing core WNG-001, spar WNG-002 from D1; flight pack PWR-001 from F1).

    python -I redesign/team/D2/pod_selfcheck.py

Builds a throw-away root in a temp folder: the real subsystems/pod files + a stand-in wing (S5010 core loft and
the 22 mm spar from params.json) + a stand-in pack (params battery.size_m at the nominal station, aft face 0.069), with both
stand-ins acknowledging the pod edges. Runs fusion/check.py's run_checks with the K09-L datums, --strict on the
pod's own items. Proves the pod geometry touches what it bonds/ties/straps to, every pod edge is registered with
the right kind, nothing of the pod floats, and the joint stacks / blocks are complete. It does NOT replace the
real check once D1 and F1 publish their parts (the stand-ins are not their design).
"""
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REDESIGN = HERE.parents[1]
POD = REDESIGN / 'subsystems' / 'pod'
sys.path.insert(0, str(REDESIGN / 'fusion'))
import check  # noqa: E402

WING_PY = '''import k09kit as k9
def build(ctx):
    v = ctx.value
    coords, _ = k9.section(ctx)
    c, b = v('wing.chord_m', 'm'), v('wing.span_m', 'm')
    loop = k9.section_loop(coords, c)
    ctx.part('WNG-001').loft('Y', [(-b / 2, loop), (b / 2, loop)], name='stand-in core')
    k9.spar_y(ctx.part('WNG-002'), v('wing.spar.x_m', 'm'), v('wing.spar.z_m', 'm'), v('wing.spar.length_m', 'm') / 2,
              v('wing.spar.od_m', 'm'), v('wing.spar.id_m', 'm'))
    ctx.contact('E-SC-01', 'stand-in spar bond')
'''

PWR_PY = '''import json, os
def build(ctx):
    L, W, H = ctx.value('battery.size_m', 'm')
    g = json.load(open(os.path.join(os.path.dirname(ctx.dir), 'pod_layout.json')))
    x0 = g['x_pack0']
    ctx.part('PWR-001').box((x0, -W / 2, g['zp']), (x0 + L, W / 2, g['zp'] + H), name='stand-in pack')
'''


def main():
    sys.path.insert(0, str(HERE))
    import pod_data
    _ctx, _P, _L, G, _src = pod_data.build_pod()
    tmp = Path(tempfile.mkdtemp(prefix='pod_selfcheck_'))
    try:
        shutil.copytree(POD, tmp / 'pod', ignore=shutil.ignore_patterns('__pycache__'))
        (tmp / 'pod_layout.json').write_text(json.dumps({'x_pack0': G['pack_fore_nom'], 'zp': G['zp']}), encoding='utf-8')
        for sub, py in (('wing', WING_PY), ('power', PWR_PY)):
            (tmp / sub / 'fusion').mkdir(parents=True)
            (tmp / sub / 'fusion' / (sub + '.py')).write_text(py, encoding='utf-8')
        pod_if = json.loads((POD / 'interfaces.json').read_text(encoding='utf-8'))
        pod_if['acknowledges'] = []          # the stand-ins do not declare the power/avionics/harness edges
        (tmp / 'pod' / 'interfaces.json').write_text(json.dumps(pod_if, indent=1), encoding='utf-8')
        part = lambda pid, sub, name, mat, m, cg: {'id': pid, 'name': name, 'subsystem': sub, 'status': 'MODELLED',
                                                   'mass_g': m, 'material': mat, 'cg_xyz_m': cg, 'make_or_buy': 'make'}
        wing = {'schema': 'dbf-interfaces/1', 'subsystem': 'wing',
                'parts': [part('WNG-001', 'wing', 'stand-in core', 'XPS', 221, [0.134, 0, 0]),
                          part('WNG-002', 'wing', 'stand-in spar', 'CF tube', 102, [0.08, 0, 0.0066])],
                'edges': [{'id': 'E-SC-01', 'part_a': 'WNG-002', 'part_b': 'WNG-001', 'via': 'CT-EPOXY', 'owner': 'wing',
                           'notes': 'stand-in'}],
                'acknowledges': ['E-POD-01', 'E-POD-09']}
        pwr = {'schema': 'dbf-interfaces/1', 'subsystem': 'power',
               'parts': [dict(part('PWR-001', 'power', 'stand-in pack', 'LiPo', 550, [G['pack_c_nom'], 0, G['pack_z_c']]),
                              make_or_buy='buy')],
               'edges': [], 'acknowledges': ['E-POD-05', 'E-POD-12']}
        (tmp / 'wing' / 'interfaces.json').write_text(json.dumps(wing, indent=1), encoding='utf-8')
        (tmp / 'power' / 'interfaces.json').write_text(json.dumps(pwr, indent=1), encoding='utf-8')
        (tmp / 'modules.txt').write_text('wing\npod\npower\n', encoding='utf-8')
        alloc = json.loads((REDESIGN / 'params' / 'mass_budget.json').read_text(encoding='utf-8'))['allocations_g']['pod']
        (tmp / 'mass_budget.json').write_text(json.dumps({'limit_g': 2600, 'allocations_g': {'pod': alloc}}), encoding='utf-8')
        ctx, results, issues = check.run_checks(str(tmp), str(tmp / 'modules.txt'), 0.002, str(tmp / 'mass_budget.json'),
                                                datums=True)
        pod_ids = {c.id for c in ctx.components.values() if c.subsystem == 'pod'}
        mine = [i for i in issues if any(p in str(i[2]) for p in pod_ids | {'E-POD', 'pod'})
                and i[1] not in ('datums',)]
        for sub, f, ok, ms, _ in results:
            print('%-8s %s' % (sub, 'ok' if ok else 'FAIL'))
        pm = sum(c.mass_g for c in ctx.components.values() if c.subsystem == 'pod')
        print('pod: %d parts, %d bodies, %.1f g (allocation %d g)' % (
            len(pod_ids), sum(len(c.shapes) for c in ctx.components.values() if c.subsystem == 'pod'), pm, alloc))
        for sev, code, item, msg in issues:
            print('  %-5s %-16s %-16s %s' % (sev, code, item, msg))
        fail = [i for i in mine]
        print('pod_selfcheck: %s (%d pod issues, strict; %d issues in total incl. stand-ins)' % (
            'PASS' if not fail else 'FAIL', len(fail), len(issues)))
        return 1 if fail else 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    sys.exit(main())
