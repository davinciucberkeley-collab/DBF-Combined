"""T-076d step 4 mesh-convergence comparison: judged rows of the same geometry (G1) at two mesh sizes (MS 1.4 coarse, MS 1.1 reference).  python -I t076d_step4_conv.py [coarse_tag fine_tag]
Reports, per demand set, the ratio coarse / fine for every judged quantity (tube axial, hoop, tau_s,theta, tau_s,r of tubes A and B, bond 'full' and 'T-076c', hub von Mises) and the maximum |ratio - 1| (the audit s2.4 criterion is < 5 %).  Ratios > 1 mean the finer mesh gives the LOWER stress."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ct, ft = (sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else ('g1ms14', 'g1ms11')
c = json.load(open(os.path.join(HERE, 'step4_%s.json' % ct))); f = json.load(open(os.path.join(HERE, 'step4_%s.json' % ft)))
print('# mesh pair %s (%d elements, %d dof) vs %s (%d elements, %d dof)' % (ct, c['elements'], c['dof'], ft, f['elements'], f['dof']))
print('| set | quantity | coarse | fine | coarse / fine |'); print('|---|---|---|---|---|')
worst = {}; allr = []
for nm in f['rows']:
    if nm not in c['rows']: continue
    qs = []
    for t in 'AB':
        for q in ('axial', 'hoop', 'tau_st', 'tau_sr'):
            qs.append(('tube %s %s (judged)' % (t, q), c['rows'][nm]['tubes'][t][q + '|judged']['value'], f['rows'][nm]['tubes'][t][q + '|judged']['value']))
        qs.append(('tube %s tau_s,r raw max (incl. rings)' % t, c['rows'][nm]['tubes'][t]['tau_sr|raw']['value'], f['rows'][nm]['tubes'][t]['tau_sr|raw']['value']))
    qs.append(('bond mean shear full', c['rows'][nm]['bond']['full']['mean_worst_arm'], f['rows'][nm]['bond']['full']['mean_worst_arm']))
    qs.append(('bond mean shear T-076c def.', c['rows'][nm]['bond']['T076c']['mean_worst_arm'], f['rows'][nm]['bond']['T076c']['mean_worst_arm']))
    qs.append(('hub von Mises max excl', c['rows'][nm]['hub']['max_excl_vm'], f['rows'][nm]['hub']['max_excl_vm']))
    for q, a, b in qs:
        r = a / b; allr.append((nm, q, a, b, r)); worst[q] = max(worst.get(q, 0.0), abs(r - 1))
        if nm in ('RB z0.05', 'D1 z0.05'): print('| %s | %s | %.3f | %.3f | %.3f |' % (nm, q, a, b, r))
print('\nmax |coarse / fine - 1| over all 6 sets, per quantity:')
for q, v in sorted(worst.items(), key=lambda kv: -kv[1]): print('  %-42s %5.1f %%' % (q, 100 * v))
ok = [q for q, v in worst.items() if v < 0.05]; print('\nquantities within 5 %%: %d of %d: %s' % (len(ok), len(worst), ', '.join(ok)))
json.dump(dict(pair=[ct, ft], worst_abs_change=worst, rows=[dict(set=a, q=b, coarse=c_, fine=d_, ratio=e_) for a, b, c_, d_, e_ in allr]), open(os.path.join(HERE, 'step4_convergence.json'), 'w'), indent=1)
