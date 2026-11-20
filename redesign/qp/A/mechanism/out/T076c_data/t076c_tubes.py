"""T-076c step 4 diagnostic (after the H-A1 stop): CF arm-tube and bond rows for the 301 landing combos on the H-A1 geometry, partitions A (whole wrench through the arms) and B (arm group through the stubs, hub+pack group on the hub aft face),
hub material aluminium and a PETG control (same mesh, E 2.1 GPa).  CATEGORY: FEA.  python -I t076c_tubes.py  (~40-60 min).  Rows: tube axial 350 / hoop 40 / shear 30 MPa EST x KF, bond mean shear x KP vs 2.0 MPa EST (fea_arm.ALLOW)."""
import os, sys, json, time, inspect
D = os.path.dirname(os.path.abspath(__file__)); T76 = os.path.abspath(os.path.join(D, '..', 'T076_data'))
sys.path.insert(0, T76); sys.path.insert(0, D); sys.dont_write_bytecode = True
os.environ['LAND_MASS_KG'] = '1.64'
import numpy as np
import fea_hub_c6 as H
import t076b_run as TB
src = inspect.getsource(H.evaluate).replace('reshape(24,', 'reshape(S.shape[0],').replace('def evaluate(', 'def evaluate_n(')
exec(src, H.__dict__)
for kv in 'S_END=60 SLV_W=1.5 MS=1.1 FIL=2.0 BR_CH=0.8 COL_E=21 X_BR0=15.0 X_HUB1=45 BR_GAP=0.5'.split(): k, v = kv.split('='); H.GEO[k] = float(v)
CA, CB, labs = TB.combos_cached(); AL = H.FA.ALLOW; KF, KP = H.FA.KF, H.FA.KP
out = {}; t0 = time.time()
for mat, (E, nu) in (('Al', (69000.0, 0.33)), ('PETG', (2100.0, 0.35))):
    H.FA.E_PETG, H.FA.NU_PETG = E, nu
    res = H.run(0, 't076cha1'); res24 = dict(res); res24['S'] = res['S'][:24]
    for part, rr, CC in (('A', res24, CA), ('B', res, CB)):
        _c = H.coeffs; H.coeffs = lambda c: c
        try: ev = H.evaluate_n(rr, list(CC))
        finally: H.coeffs = _c
        row = {}
        for t in ('A', 'B'):
            e = ev['tube_' + t]; row['tube ' + t] = dict(axial=AL['cf_axial'] / (KF * e['axial']), hoop=AL['cf_hoop'] / (KF * e['hoop']), shear=AL['cf_shear'] / (KF * e['shear']), axial_MPa=e['axial'], shear_MPa=e['shear'], axial_at_s=e['axial_at_s'], shear_at_s=e['shear_at_s'])
        row['bond mean shear'] = dict(MPa=ev['bond']['shear_mean_worst_arm'], RF=AL['bond'] / (KP * ev['bond']['shear_mean_worst_arm']), peak_MPa=ev['bond']['shear'], p99_MPa=ev['bond']['shear_p99'])
        out['%s|%s' % (mat, part)] = row
        print('%s partition %s (scale 1.0; RF at 1.5 = RF/1.5): %s  [%.0f s]' % (mat, part, json.dumps(row, default=float), time.time() - t0), flush=True)
json.dump(out, open(os.path.join(D, 'tubes_diag.json'), 'w'), indent=1, default=float)
print('done %.0f s' % (time.time() - t0))
