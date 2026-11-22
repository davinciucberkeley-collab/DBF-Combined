"""T-084 probe (FEA-lite, beam FE fe_a.py): identify the D-185 spar mode, its shape and what drives its motor coupling cy.
python -I t084_modes_probe.py   (imports structures_a's FE inputs without running structures_a: re-builds FEKW the same way)"""
import os, sys, math, json, io, contextlib
HERE = os.path.dirname(os.path.abspath(__file__)); QPA = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
S = os.path.join(QPA, 'structures'); sys.path.insert(0, S); sys.path.insert(0, os.path.join(QPA, 'cad')); sys.dont_write_bytecode = True
import numpy as np, fe_a
with contextlib.redirect_stdout(io.StringIO()):
    import a_model as m
def mg(*pre, ex=()): return sum(p["mass_g"] for pid, p in m.PARTS.items() if pid.startswith(pre) and not pid.startswith(ex))
def fekw(**over):
    FEIN = dict(wing_g=mg("WNG")+mg("CGE-007"), avionics_g=mg("AVN", "HWC-001", "HWC-003", "PRP-003", "HRN-001", "HRN-002", "HRD"),
        centre_extra_g=mg("CGE-006", "MEC", "HWC-002"), pack_g=mg("PWR")+mg("CGE-008"), hub_extra_g=mg("CGE-001", "CGE-009", "CGE-010", "HRN-003", "HRN-004"),
        motor_g=(mg("PRP-001-UR")+mg("PRP-002-UR")+mg("PRP-004-UR")+mg("PRP-005-UR")+mg("PRP-006-UR")+mg("CGE-003-UR")),
        foot_pad_m=(mg("GER-001-UR")+mg("GER-002-UR"))/1000.0, root_g=(mg("FIN-003-R")+mg("FIN-005-R")+mg("FIN-009-R")+mg("FIN-006-R")+mg("FIN-010-R")))
    kw = dict(spar_tube=(m.SPAR_OD, m.SPAR_ID), arm_tube=(0.012, 0.010), rib_tube=(m.RIB_OD, m.RIB_ID), bridge_cfg="single+V", bridge_tube=(m.BR_OD, m.BR_ID), vtube=(m.STRUT_OD, m.STRUT_ID),
              bridge_yv=m.STRUT_E[1], fin_strip=None, fin_tube=(m.FIN_OD, m.FIN_ID, 3e-3, 0.055), x_fin=m.XFIN_T, x_hub=m.HUB[0], h_fin=m.FIN_H, **FEIN)   # T-084: fin tip at the CAD FIN_H (structures_a passes it too)
    kw.update(over); return kw
BAND = (94.0, 321.0)
def strong(kind, **over):
    F, info = fe_a.build(kind, **fekw(**over)); res = F.solve(130); out = []
    for (f, e, v, cx, cy) in res:
        if (cx >= 0.5 or cy >= 0.5) and BAND[0] <= f <= BAND[1]: out.append((f, cx, cy, e))
    return F, res, out
def near(res, f0):
    return min(res, key=lambda r: abs(r[0]-f0))
if __name__ == '__main__':
    print('FEIN', {k: round(v, 2) for k, v in fekw().items() if k.endswith('_g') or k == 'foot_pad_m'})
    for kind in ('kd', 'nom', 'hi'):
        F, res, out = strong(kind)
        print(f'\n## {kind}: strong in band:', [(round(f, 1), round(cx, 3), round(cy, 3)) for f, cx, cy, e in out])
        for f, e, v, cx, cy in res:
            if 150 < f < 300:
                top = sorted(e.items(), key=lambda kv: -kv[1])[:4]
                print(f'  {f:7.1f} Hz cx {cx:.3f} cy {cy:.3f}  ' + ', '.join(f'{g} {100*x:.0f}%' for g, x in top))
    # mode shape of the nom spar mode
    F, res, out = strong('nom'); f0 = out[0][0] if out else 218.0
    f, e, v, cx, cy = near(res, f0); idx = F._idx
    print(f'\n## nom mode {f:.1f} Hz shape (translations, mass-normalised):')
    for nm in ['s-0.450', 's-0.380', 's-0.285', 's-0.228', 's-0.150', 's+0.000', 's+0.150', 's+0.228', 's+0.285', 's+0.380', 's+0.450', 'hub', 'm+1+1', 'm+1-1', 'm-1+1', 'm-1-1', 'f+1r', 'f+1+1', 'f+1-1', 'f-1r']:
        i = idx[nm]; print(f'  {nm:8s} ux {v[6*i]:+.3f} uy {v[6*i+1]:+.3f} uz {v[6*i+2]:+.3f}  rx {v[6*i+3]:+.2f} ry {v[6*i+4]:+.2f} rz {v[6*i+5]:+.2f}')
