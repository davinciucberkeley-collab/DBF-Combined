"""T-077 step 1: RDQ 2800 pack (107 x 33 x 46 mm) fit check. Category: interference (axis-aligned bounding boxes of the stub-built CAD, plus arithmetic). Run: python -I fit_check.py"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..'))      # redesign/
sys.path.insert(0, R + '/qp/A/cad'); sys.path.insert(0, R + '/fusion'); sys.path.insert(0, R + '/interfaces')
import build_all, a_model as m
from backends.stub_backend import StubBackend
M = R + '/qp/A/cad/model'
ctx, _, res = build_all.build(StubBackend(), M, M + '/modules.txt', log=lambda *a: None)
bb = {k: c.bbox() for k, c in ctx.components.items() if c.shapes and c.bbox()}
mm = lambda v: [round(x * 1e3, 2) for x in v]
print('pack PWR-001 bbox (mm):', mm(bb['PWR-001'][0]), mm(bb['PWR-001'][1]))
lo = [min(v[0][i] for v in bb.values()) for i in range(3)]; hi = [max(v[1][i] for v in bb.values()) for i in range(3)]
ext = [hi[i] - lo[i] for i in range(3)]
noprop = {k: v for k, v in bb.items() if not k.startswith('PRP-001') and not k.startswith('PRP-002') and not k.startswith('PRP-004') and not k.startswith('PRP-005')}
print('whole-aircraft bbox (mm) lo', mm(lo), 'hi', mm(hi), 'extent', mm(ext))
print('  (before T-077, same script on HEAD: extent 479.4 x 900.0 x 461.3; pack does not set any extreme: x min PRP-005-LL, z extremes PRP-002)')
for i, n in enumerate('xyz'):
    print(' ', n, 'min set by', min(bb, key=lambda k: bb[k][0][i]), 'max set by', max(bb, key=lambda k: bb[k][1][i]))
box = sorted([0.90, 0.50, 0.39], reverse=True); e = sorted(ext, reverse=True)
print('box proxy 0.90 x 0.50 x 0.39 vs aircraft sorted extent:', [round(a, 3) for a in e], 'ratios', [round(a / b, 3) for a, b in zip(e, box)])
# pack at the trim ends: x range and clearance to every other part (bbox overlap in x and y and z, excluding the parts it is meant to touch)
touch = {'CGE-008', 'PWR-002', 'PWR-003', 'HRN-001', 'HRN-002'}
P = ((m.PACK_X[0], -m.PACK_L / 2, m.PACK_Z0), (m.PACK_X[1], m.PACK_L / 2, m.PACK_Z0 + m.PACK_H))   # cell body only (the PWR-001 bbox also holds the XT60 male housing and the JST plug)
for tag, dx in (('trim -6 (fwd)', -m.TRIM_FWD), ('trim 0', 0.0), ('trim +10 (aft)', m.TRIM)):
    plo = (P[0][0] + dx, P[0][1], P[0][2]); phi = (P[1][0] + dx, P[1][1], P[1][2])
    hits = []
    for k, v in bb.items():
        if k == 'PWR-001' or k in touch or k.startswith(('HRN-00', 'E-')) or k.startswith('WNG-001'):
            continue
        ov = [min(phi[i], v[1][i]) - max(plo[i], v[0][i]) for i in range(3)]
        if all(o > 0 for o in ov):
            hits.append((k, mm(ov)))
    print(tag, 'pack x', round(plo[0] * 1e3, 1), round(phi[0] * 1e3, 1), 'z top', round(phi[2] * 1e3, 1), 'bbox overlaps with other parts (excl. tray, strap, pad, wires, core):', hits or 'none')
print('cover AVN-008 bbox x0 (mm):', round(bb['AVN-008'][0][0] * 1e3, 2), ' pack aft face at +trim:', round((P[1][0] + m.TRIM) * 1e3, 2), 'gap', round((bb['AVN-008'][0][0] - (P[1][0] + m.TRIM)) * 1e3, 2), '; PWR-001 bbox incl. connector/plug z top', round(bb['PWR-001'][1][2]*1e3,1))
print('tray inner wall |y| %.1f, pack half length %.1f: gap %.2f mm' % (m.TRAY_YI * 1e3, m.PACK_L / 2 * 1e3, (m.TRAY_YI - m.PACK_L / 2) * 1e3))
print('pack top z %.1f; upper arm tube axis z at pack end |y|=53.5: %.1f (+-6), arm x range %.1f..%.1f vs pack x min %.1f' % ((m.PACK_Z0 + m.PACK_H) * 1e3, 53.5 * m.ZM / m.YM, (m.HUB[0] - 0.0065 - 0.006) * 1e3, (m.HUB[0] + 0.0065 + 0.006) * 1e3, (m.PACK_X[0] - m.TRIM_FWD) * 1e3))
print('strap loop perimeter (inner) %.0f mm; BOM W08 strap length 300 mm' % (m.STRAP_LOOP * 1e3))
# alternative orientation: 46 mm along x (pack lies on its 33 x 107 face... 107 y x 46 x 33 z)
w = 0.046
print('ALT B (46 along x, 33 up): pack x span at trim -6..+10 = %.1f .. %.1f mm; cover starts %.1f mm; core tray slot ends 22.5 mm' % (((-0.010) - w / 2 - m.TRIM_FWD) * 1e3, ((-0.010) + w / 2 + m.TRIM) * 1e3, m.COV_X0 * 1e3))
import numpy as np
z_cov = lambda x: float(np.interp(x, [m.COV_X0, 0.040], [m.zu(m.COV_X0), m.COV_ZH1]))
xa = (-0.010) + w / 2 + m.TRIM
print('   cover roof outer z at the pack aft edge x=%.1f: %.1f mm; pack top z = %.1f mm (9 + 33) -> %s' % (xa * 1e3, z_cov(max(xa, m.COV_X0)) * 1e3, (m.PACK_Z0 + 0.033) * 1e3, 'collides with the cover at full aft trim' if (m.PACK_Z0 + 0.033) > z_cov(max(xa, m.COV_X0)) and xa > m.COV_X0 else 'ok'))
