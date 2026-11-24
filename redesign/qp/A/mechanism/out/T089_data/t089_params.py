"""T-089: reduce t089_gm.json / t089_fvib.json to the lists re-pointed in proofs/gen_params_a.py (sim.gm_nominal, gm_shifted, gm_shifted_up, vib_fc_ms2).
Order of the gm lists = the stored order: pit / rll / yaw x kd, nom, hi (9 values), minimum over the 24 T-085 bound groups, zeta 0.3 / 1 %, thrust scale 0.77 / 1.0 / 1.25.
Primary = 'CAD' inertia variant (loop gain rescaled to the current 1.8796 kg / cad_mass.json inertia); 'FE' = the FE's own (lighter) inertia, reported as the bound.
Category: data reduction only.   python -I t089_params.py -> t089_params.json, stdout"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
gm = json.load(open(os.path.join(HERE, 't089_gm.json'))); fv = json.load(open(os.path.join(HERE, 't089_fvib.json')))
out = {}
for var in ('CAD', 'FE'):
    for sc, name in (('1.0', 'gm_nominal'), ('0.8', 'gm_shifted'), ('1.2', 'gm_shifted_up')):
        row = []; arg = []
        for ax in ('pit', 'rll', 'yaw'):
            for k in ('kd', 'nom', 'hi'):
                best = (1e9, None)
                for g in gm['groups']:
                    for r in g['rows']:
                        if r['ax'] == ax and r['kind'] == k:
                            v = r['gm'][f'{var}|{sc}'][0]
                            if v < best[0]: best = (v, (g['cell'], g['hub'], g['pad'], r['gm'][f'{var}|{sc}'][1]))
                row.append(round(best[0], 2)); arg.append(best[1])
        out[f'{var}|{name}'] = dict(values=row, worst_group=arg)
        print(var, name, row, 'min', min(row))
vib = []
for kind in ('kd', 'nom', 'hi'):
    for z in (0.01, 0.005):
        rr = [r for g in fv['groups'] for r in g['rows'] if r['kind'] == kind and r['zeta'] == z]
        vib.append(round(max(r['worst'] for r in rr), 1))
out['vib_fc_ms2'] = vib; print('vib_fc_ms2 (kd 1%, kd .5%, nom 1%, nom .5%, hi 1%, hi .5%):', vib)
json.dump(out, open(os.path.join(HERE, 't089_params.json'), 'w'), indent=1)
