"""T-077 p4 step 1b: judge the pocketed hub (step4_<tag>.json) against the G1 baseline (T076d step4_g1ms11.json) with the D-223 rule:
demand = max( max(DAF_q, 1.5) x RB , D-1 direct / r_m ), DAF_q 1.97 (tubes, bond, hub), r_m 0.84.  RF = allowable / (KF x value) (scale 1.0 in the json) -> RB row RF/1.97, D-1 row RF x 0.84.
CATEGORY: FEA post-processing.   python -I t077p4_judge.py <tag>"""
import json, sys, os
H = os.path.dirname(os.path.abspath(__file__)); tag = sys.argv[1]
new = json.load(open(os.path.join(H, 'step4_%s.json' % tag))); old = json.load(open(os.path.join(H, '..', 'T076d_data', 'step4_g1ms11.json')))
KF, KP = 1.725, 2.156; AL = dict(axial=350.0, hoop=40.0, tau_st=30.0); SY = 240.0; DAF, RM = 1.97, 0.84
def rows(j):
    out = {}
    for z in ('0.02', '0.05', '0.10'):
        for kind in ('RB', 'D1'):
            r = j['rows']['%s z%s' % (kind, z)]; f = (lambda rf: rf / DAF) if kind == 'RB' else (lambda rf: rf * RM)
            for t in 'AB':
                for nm, al in (('axial', AL['axial']), ('hoop', AL['hoop']), ('tau_st', AL['tau_st'])):
                    out[('tube %s %s' % (t, nm), kind, z)] = f(al / (KF * r['tubes'][t][nm + '|judged']['value']))
            out[('bond full', kind, z)] = f(r['bond']['full']['rf_KP'])
            out[('bond T076c def', kind, z)] = f(r['bond']['T076c']['rf_KP'])
            out[('hub von Mises', kind, z)] = f(r['hub']['rf'])
    return out
a, b = rows(old), rows(new)
names = sorted({k[0] for k in a})
print('D-223 rows (RB / 1.97 and D-1 x 0.84), minimum over pad zeta; baseline G1 (T076d) -> pocketed %s' % tag)
print('%-16s %-4s %9s %9s %7s' % ('row', 'set', 'baseline', 'pocketed', 'ratio'))
flag = []
for n in names:
    for kind in ('RB', 'D1'):
        va = min(v for k, v in a.items() if k[0] == n and k[1] == kind); vb = min(v for k, v in b.items() if k[0] == n and k[1] == kind)
        print('%-16s %-4s %9.3f %9.3f %7.3f' % (n, kind, va, vb, vb / va))
        if va >= 1.0 and vb < 1.0: flag.append((n, kind, va, vb))
print('rows that PASSED (>= 1.0) at baseline and FAIL now:', flag if flag else 'none')
hub = min(v for k, v in b.items() if k[0] == 'hub von Mises'); print('hub von Mises minimum RF %.3f (baseline %.3f); hub mass %.2f g Al (baseline %.2f g)' % (hub, min(v for k, v in a.items() if k[0] == 'hub von Mises'), new['hub_g_Al'], old['hub_g_Al']))
