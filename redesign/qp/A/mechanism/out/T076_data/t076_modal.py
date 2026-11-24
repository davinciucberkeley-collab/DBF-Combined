"""T-076 row 3 (A-P10): t073_modal.py (unmodified, imported) re-run for the 9x4.5 prop with the glass skin, the T-067 printed masses and the O4b pack, at 1.64 kg.
CATEGORY: FEA-class beam-frame modal analysis + forced response (fe_a.py via t073_modal.py).  All mass placements are EST (mapping below), nothing in structures/ or T073_data/ edited.
Env: T076_MASS=t067 (default: T-067 printed masses + R1''/R3fix/R4/T-068/skin/strut + 275 g pack) | t073 (control: the t073_modal 9 in skin-1 run as committed, no mass change);
     T076_RESID=1 adds the unallocated growth (wiring, fasteners, adhesive) as a uniform wing line mass so the FE total reaches 1.64 kg (EST);  T076_REBASE=1 re-bases the rotor bands at 1.64 kg.
Run: python -I t076_modal.py > out.txt   (cwd anywhere)."""
import os, sys, math
D = os.path.dirname(os.path.abspath(__file__)); T73 = os.path.abspath(os.path.join(D, '..', 'T073_data'))
os.environ.setdefault('T073_PROP', '9'); os.environ.setdefault('T073_SKIN', '1'); os.environ.setdefault('T073_O4', '0')
sys.path.insert(0, T73)
import numpy as np
import t073_modal as M
import fe_a
MODE = os.environ.get('T076_MASS', 't067'); RESID = os.environ.get('T076_RESID', '0') == '1'; REBASE = os.environ.get('T076_REBASE', '0') == '1'
TARGET_KG = 1.64
# ---- T-067 printed-part adoption (T067_mass_audit.md s4, per part, g) mapped to the FE lumps.  Listed values are what the FE already carries (EST: the FE lumps do not itemise parts).
# per motor: cup listed 4.30 -> T-067 9.51 -> R3fix -2.8 (T-073 -11.2 g / 4)  => +2.41 per motor on motor_g
# hub lump (pack + hub print 20 g): pack 270 -> 275 g (O4b 2,800 mAh, `U`); hub print 20 -> CGE-001 15.82; tray 3.8 listed (not in the 20 g) -> R1'' 15.7 g
# spar centre lump (avionics 110 g + 65 g fixed): plate 8.0 listed -> R2 bosses 1.02; bridge saddle CGE-006 listed 2.0 -> 9.67; cover -0.81; cell skin plates are added by t073_modal (5 + 3.7 g)
# spar y = +-0.30 (V-strut nodes): strut clamps 2 x 3.69 (R4 passing variant) vs 1.5 listed each, +1.5 g each strut growth T-070 (EST) -> + (3.69-1.5) + 1.5
# fin root (per side, lump 6 g): root block 3.20 -> 18.90, saddle 1.00 -> 14.39, T-068 clamshell/plates +6 g per side (12.0 g total, T-070 / T-068 s6)
# fin tips (per tip lump 2.5 g): foot shoe listed 1.40 -> 4.55
if MODE == 't067':
    M.CFG.update(pack_g=275.0, avionics_g=110.0 - 8.0 + 1.02 + 9.67 - 2.0 - 0.81, motor_g=65.0 + 11.06 + 5.0 + 4.3 + 2.9 + 2.41, foot_pad_m=(2.5 + (4.55 - 1.40)) * 1e-3)
_orig_build = fe_a.build
def build2(kind='nom', **kw):
    F, info = _orig_build(kind, **kw)
    if MODE == 't067':
        F.lump('hub', (15.82 - 20.0 + 15.7 + 0.0) * 1e-3)                       # hub print and tray (pack handled by pack_g)
        for sy in (1, -1):
            yv = sy * kw.get('bridge_yv', 0.30)
            nm = 's%+.3f' % yv
            if nm in F.n: F.lump(nm, (3.69 - 1.5 + 1.5) * 1e-3)
            F.lump('f%+dr' % sy, ((18.90 - 3.20) + (14.39 - 1.00) + 6.0) * 1e-3)
    return F, info
fe_a.build = build2
def lumped_total(F):
    m = sum(F.mass.values())
    for (a, b, EA, EIy, EIz, GJ, rA, vref, grp) in F.el:
        m += rA * float(np.linalg.norm(np.array(F.n[a]) - np.array(F.n[b])))
    return m
if RESID:
    _bv = M.build_variant
    def bv2(corner):
        F, sp = _bv(corner)
        m0 = lumped_total(F); res = TARGET_KG - m0
        if res > 0:
            ys = sorted(float(n[1:]) for n in F.n if n.startswith('s') and '>' not in n and abs(float(n[1:])) <= 0.45)
            for y in ys: F.lump('s%+.3f' % y, res / len(ys))
        return F, sp
    M.build_variant = bv2
if REBASE:
    sys.path.insert(0, os.path.abspath(os.path.join(D, '..', '..', '..')))
    import prop_a
    lo = prop_a.hover(TARGET_KG, 1.0)[1]; mid = prop_a.hover(TARGET_KG, 0.93)[1]; hi = 7151.0 * mid / 6272.0
    M.HOV = (lo, mid, hi); M.RPM_H_MID = mid
    M.BANDS = [('hover 1P', lo / 60, hi / 60), ('hover 2P', lo / 30, hi / 30), ('cruise 1P', M.CRU[0] / 60, M.CRU[2] / 60), ('cruise 2P', M.CRU[0] / 30, M.CRU[2] / 30)]
    M.LO_LIM = min(b[1] for b in M.BANDS) / 1.2; M.HI_LIM = 1.2 * max(b[2] for b in M.BANDS)
    print('REBASED hover rpm %.0f / %.0f / %.0f (1.64 kg: derate 1.0 / 0.93 / hi edge scaled from 7151 x mid ratio, EST)' % (lo, mid, hi))
# FE mass report (corner nom)
Fn, _ = M.build_variant('nom'); print('FE lumped + beam mass, corner nom: %.1f g (target aircraft %.0f g; the FE has no wiring / fasteners / adhesive / growth unless T076_RESID=1)' % (lumped_total(Fn) * 1e3, TARGET_KG * 1e3))
print('CFG used:', {k: (round(v, 3) if isinstance(v, float) else v) for k, v in M.CFG.items() if k in ('pack_g', 'avionics_g', 'motor_g', 'foot_pad_m')}, 'MODE', MODE, 'RESID', RESID, 'REBASE', REBASE)
lab = 'T-076 %s resid %s rebase %s; skin 1 ply; prop 9 in' % (MODE, RESID, REBASE)
stop = M.table_for(lab)
print('\nSTOP-RULE hits (strong coupling >= 0.5 in the exclusion zone):', stop if stop else 'none')
