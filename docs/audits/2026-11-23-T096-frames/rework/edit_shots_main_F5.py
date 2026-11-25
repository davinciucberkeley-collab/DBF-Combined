import json, copy
F = r'C:\Users\dillo\Downloads\Berkeley\Fall\Capstone\DBF-Combined\redesign\showcase\concept-a\film\shots-main.json'
d = json.load(open(F, encoding='utf-8'))
S = {s['id']: s for s in d['scenes']}


def shot(sc, i):
    return next(x for x in S[sc]['shots'] if x['id'] == i)


# S2
shot('S2', '2.2')['title_delay'] = 1.5
s23 = shot('S2', '2.3')
s23['sub'] = s23['sub'].replace('PETG hub', 'Machined 6061-T6 hub (D-220)').replace('(CGE-001, CGE-002, CGE-003)', '(CGE-001 to CGE-003)')
# S4
RUN = 'T097_Z5'
NOTE = 'Run of T-097 (AR-015), 1.881 kg EST, X2216, CG 22.049 mm; SITL with the a_plant.py plant (EST aero).'
S['S4']['title'] = 'Simulation playback: executed ArduPilot SITL run T097_Z5 (1.881 kg EST)'
for sh in S['S4']['shots']:
    sh['tag'] = 'SIMULATED: ArduPilot SITL run T097_Z5, 1.881 kg EST, a_plant.py plant model (EST aero)'
    sh['sitl']['run'] = RUN
    sh['sitl']['note'] = NOTE
shot('S4', '4.4')['sub'] = shot('S4', '4.4')['sub'].replace('about 89 m', 'about 92 m')
shot('S4', '4.5')['sub'] = 'Touch-down on the fin pads at the end of the run. The foam pad stroke is checked separately (AR-016, closing card).'
# S5
S['S5']['title'] = 'Structures: machined 6061-T6 hub status, arm and motor cup FEA'
modes = copy.deepcopy(s23['modes'])
s51 = {'id': '5.1', 'dur': 6.0,
       'tag': 'SIMULATED: FEA T-076c run H-A1, aluminium hub (analysis only, not VERIFIED)',
       'los': False, 'wires': False, 'modes': modes,
       'title': 'Hub: machined 6061-T6 (D-220)',
       'sub': 'The hub passes in the aluminium-hub FEA. The printed PETG hub map of 2026-11-17 is an earlier design (record) and is not shown.',
       'readout': {'title': 'HUB STATUS, 6061-T6 (D-220)', 'legend': False,
                   'src': 'qp/A/mechanism/out/T076c_hub_al.md s0; CHANGE-LOG.md D-220, D-226; Explorer #structures (analysis only, EST)',
                   'rows': [
                       {'label': 'Hub, aluminium FEA H-A1', 'fmt': 'passes', 'vals': []},
                       {'label': 'Mesh (tet10 elements)', 'fmt': '427,333', 'vals': []},
                       {'label': 'Allowables, factors', 'fmt': 'not relaxed', 'vals': []},
                       {'label': 'H-A2 and the d209 map', 'fmt': 'not re-run', 'vals': []},
                       {'label': 'Status', 'fmt': 'not VERIFIED', 'vals': []}]},
       'cam': [{'t': 0, 'target': [-0.08, 0, 0], 'az': -38, 'el': 26, 'dist': 0.5},
               {'t': 6.0, 'target': [-0.08, 0, 0], 'az': 12, 'el': 24, 'dist': 0.46}]}
s52 = {'id': '5.2', 'dur': 6.0,
       'tag': 'SIMULATED: FEA T-076c run H-A1, landing demand (analysis only, not VERIFIED)',
       'los': False, 'wires': False, 'modes': copy.deepcopy(modes),
       'title': 'Open rows: arm tube and bond',
       'sub': 'The carbon arm-tube shear and the arm-tube / sleeve bond fail for the landing demand. They also fail with a PETG hub, so the hub material is not the cause.',
       'readout': {'title': 'OPEN ROWS, H-A1 (landing demand)', 'legend': False,
                   'src': 'qp/A/mechanism/out/T076c_hub_al.md s0; CHANGE-LOG.md D-220, D-226; load basis 1.64 kg, older than the 1.881 kg EST',
                   'rows': [
                       {'label': 'CF arm-tube shear', 'fmt': 'FAIL, open', 'vals': []},
                       {'label': 'Arm-tube / sleeve bond', 'fmt': 'FAIL, open', 'vals': []},
                       {'label': 'Same rows, PETG hub (control)', 'fmt': 'also FAIL', 'vals': []},
                       {'label': 'Routed to', 'fmt': 'D-226, TP-4, TP-5', 'vals': []},
                       {'label': 'Load basis (T-076c)', 'fmt': '1.64 kg', 'vals': []}]},
       'cam': [{'t': 6.0, 'target': [-0.12, 0.05, 0], 'az': 62, 'el': 22, 'dist': 0.4}]}
sh5 = S['S5']['shots']
assert [x['id'] for x in sh5] == ['5.1', '5.2', '5.3']
sh5[0] = s51
sh5[1] = s52
# S6 card
card = shot('S6', '6.2')['card']
L = card['lines']
mass_of = {"b": {"param": "mass/basic_cad_kg"}, "g": {"param": "mass/growth_factor"}, "o": {"param": "mass/overrun_frac"}, "m": {"param": "req/mass_gate_kg"}}
L[0] = {'label': 'Design record', 'vals': {}, 'text': 'CHANGE-LOG D-246, 2026-11-23 (untagged working tree)', 'cite': 'CHANGE-LOG D-246'}
L[1] = {'label': 'Mass, predicted vs gate',
        'vals': {'bk': {'param': 'mass/basic_cad_kg'}, 'p': {'calc': 'b*g+o*m', 'of': mass_of}, 'm': {'param': 'req/mass_gate_kg'},
                 'over': {'calc': '((b*g+o*m)-m)*1000', 'of': mass_of}},
        'text': 'predicted {p:.3f} kg EST (CAD {bk:.3f} kg) vs {m:.2f} kg gate: over the gate by {over:.1f} g',
        'cite': 'params-A.json mass/*, req/mass_gate_kg (D-208); README.md'}
i_land = next(i for i, l in enumerate(L) if l['label'].startswith('Landing'))


def sw(k):
    return {'sum': RUN, 'path': k}


def st(i):
    return {'t098': 'plateau_sweep_rib25x23/37.5N', 'idx': i}


L[i_land] = {'label': 'Landing (SITL, 1.881 kg)',
             'vals': {'s': sw(['landing', 'sink_ms']), 'l': sw(['landing', 'lean_deg_at_touch']), 'ms': sw(['mass']),
                      'tip': {'calc': "'yes' if t else 'no'", 'of': {'t': sw(['landing', 'tipped_over'])}}},
             'text': 'run T097_Z5 ({ms:.3f} kg EST): sink {s:.2f} m/s, lean {l:.1f} deg, tipped over: {tip}',
             'cite': 'T097_data sum.json (AR-015)'}
L.insert(i_land + 1, {'label': 'Landing foam (AR-016)', 'vals': {'st': st(0), 'n': st(1), 't': st(2)},
                      'text': 'stroke {st:.1f} of 20 mm, {n:.2f} g of 12 g, tilt {t:.1f} deg (worst of 10); only for foam 37.5-39.0 N, zeta 0.02-0.05 (D-243); TP-3 open',
                      'cite': 'T098_results.json (AR-016), D-243'})
i_hub = next(i for i, l in enumerate(L) if l['label'].startswith('Hub FEA'))
L[i_hub] = {'label': 'Hub (machined 6061-T6)', 'vals': {},
            'text': 'FEA H-A1: hub passes; CF arm-tube shear and tube / sleeve bond FAIL, open (D-226, TP-4, TP-5)',
            'cite': 'T076c_hub_al.md s0, D-220'}
L.append({'label': 'Elevon pitch use (open)', 'vals': {'u': {'param': 'sim/pitch_use_15_worst'}, 'lim': {'param': 'req/pitch_use_max'}},
          'text': '{u:.2f} vs {lim:.2f} limit (15 deg basis): FAIL, open (D-245)', 'cite': 'params-A.json sim/pitch_use_15_worst'})
json.dump(d, open(F, 'w', encoding='utf-8', newline=''), indent=1)
