"""T-085 s6: D-233 option C levers on the credible model (hub al6061, pad nom / tray 24 from t085_bounds), nominal and lower-bound wing cell.  Not applied to the CAD.
Coupling is reported two ways: A = fe_a.py as defined (T-066 / T-084; its cy sum also picks up the interior nodes of the +y motors' brace beams, a precedence quirk
'a or b and c'), B = motor-mass nodes only (the 4 nodes carrying the motor lumps).  The D-185 rule is judged on A (not redefined); B is a diagnostic.
python -I t085_levers.py > levers_t085.txt"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.dont_write_bytecode = True
import numpy as np
import t085_bounds as B
T = B.T; BAND = T.BAND
MOT = ('m+1+1', 'm+1-1', 'm-1+1', 'm-1-1')
def coup(F, v):
    i = F._idx; cx = math.sqrt(sum(v[6*i[m]]**2 for m in MOT)); cy = math.sqrt(sum(v[6*i[m]+1]**2+v[6*i[m]+2]**2 for m in MOT)); return cx, cy
def run(kind, cell, pack, **ov):
    F, res = T.solve(kind, cell, 'al6061', pack, **ov); rows = []
    for (f, e, v, cx, cy) in res:
        cxb, cyb = coup(F, v)
        if 60 <= f <= 400 and (max(cx, cy) >= 0.5 or max(cxb, cyb) >= 0.5): rows.append((f, cx, cy, cxb, cyb, e))
    return F, res, rows
def fmt(rows):
    return '; '.join(f"{f:.1f}{'*' if BAND[0] <= f <= BAND[1] else ''} A {cx:.2f}/{cy:.2f} B {cxb:.2f}/{cyb:.2f}" for f, cx, cy, cxb, cyb, e in rows) or 'none'
def verdict(rows): return 'FAIL' if any(BAND[0] <= f <= BAND[1] and max(cx, cy) >= 0.5 for f, cx, cy, cxb, cyb, e in rows) else 'PASS'
def verdictB(rows): return 'FAIL' if any(BAND[0] <= f <= BAND[1] and max(cxb, cyb) >= 0.5 for f, cx, cy, cxb, cyb, e in rows) else 'PASS'
if __name__ == '__main__':
    from t084_modes_probe import fekw
    mg = fekw()['motor_g']; print('motor + prop + cup mass (UR, CAD parts) %.1f g' % mg)
    T.PACKS['base'] = B.CASES[[k for k in B.CASES if k.startswith('pad nom (50A') and 'K' not in k][0]]
    # pack isolator: pad modulus scaled so that the pad-on-pack bounce frequency (z, whole pad, unenhanced) f = sqrt(k/m)/2pi is 40 / 60 Hz: k = m (2 pi f)^2 = E A / t -> E = k t / A
    mp = (T.PACKS['base'] and 0.2957-0.0133); tt = 1.0e-3
    def pk_iso(f_hz, t=1.0e-3):
        k = mp*(2*math.pi*f_hz)**2; E = k*t/3.0e-3; return dict(T.PACKS['base'], pad_E=E, pad_t=t, z_mult=1.0, w=0.024)
    for f_ in (40, 60): T.PACKS['iso%d' % f_] = pk_iso(f_)
    MM = lambda f_, mf=0.85: (mf*mg*1e-3*(2*math.pi*f_)**2,)*3 + (mf,)
    OPT = [('as drawn (pad nom)', 'base', {}),
           ('C1 bridge z-bending x0.5', 'base', dict(bridge_f=(0.5, 1, 1))), ('C1 bridge z-bending x0.25', 'base', dict(bridge_f=(0.25, 1, 1))),
           ('C2 pack carried by wing centre node', 'base spar', {}),
           ('C3 pack on a soft mount, bounce 60 Hz (EST pad E %.3f MPa, 1 mm)' % (T.PACKS['iso60']['pad_E']/1e6), 'iso60', {}),
           ('C3 pack on a soft mount, bounce 40 Hz (EST pad E %.3f MPa, 1 mm)' % (T.PACKS['iso40']['pad_E']/1e6), 'iso40', {}),
           ('C5 arms 10x8 (was 12x10)', 'base', dict(arm_tube=(0.010, 0.008))),
           ('C4 motor + prop on a soft mount, 60 Hz', 'base', dict(motor_mount=MM(60))), ('C4 motor + prop on a soft mount, 45 Hz', 'base', dict(motor_mount=MM(45))), ('C4 motor + prop on a soft mount, 30 Hz', 'base', dict(motor_mount=MM(30)))]
    T.PACKS['base spar'] = dict(T.PACKS['base'], anchor='s+0.000')
    print('| option | cell | corner | strong modes 60-400 Hz (* = in band; A = fe_a metric, B = motor nodes only) | D-185 (a) on A | on B |'); print('|---|---|---|---|---|---|')
    for lab, pk, ov in OPT:
        for cell in ('nominal', 'lower'):
            for kind in T.KINDS:
                F, res, rows = run(kind, cell, pk, **ov); print(f'| {lab} | {cell} | {kind} | {fmt(rows)} | {verdict(rows)} | {verdictB(rows)} |', flush=True)
