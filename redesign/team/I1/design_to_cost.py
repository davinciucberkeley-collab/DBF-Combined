"""I1 design-to-cost (2026-11-14). Run: python -I team/I1/design_to_cost.py   (reads BOM.csv; writes nothing)

Model (same as cost_trade.py): line = qty_total x unit_usd_pessimistic x 1.1025 (Berkeley tax 10.25 %);
shipping = $10.71 per distinct (vendor, EARLY/DEC) group of non-LOCAL lines (pessimistic rate);
+ FAA $5. Lines gated X10 / X12 are out (fallbacks); X13 microSD, X07 box, X08 airspeed are IN.
Tools = lines gated X14 (Jacobs lists no K-line tool: labs page, BUILD-GUIDE 2026-11-13) -> all count.
Crash reserve rule: one bad crash = pack + servo + one fin tube (if no spare tube is carried), taxed, one
shipment per vendor; spares carried (5th motor, ESCs, props) are not billed again.
All replacement prices below are `EST` or `UNVERIFIED` (search snippet) unless DESIGN-TO-COST.md says otherwise.
This model differs from the BOM.csv summary rows (2,259.38: 16 shipments, owned items), so totals differ.
"""
import csv, re, os, copy
T = 1.1025; SH = 10.71; FAA = 5.0; LIMIT = 2000.0; CONT_MIN = 40.0
rows = [x for x in csv.DictReader(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'BOM.csv'), encoding='utf-8')) if x['line'] != 'TOTAL']

GROUP = {'B': 'propulsion', 'P': 'power', 'F': 'power', 'A': 'avionics', 'R': 'avionics', 'M': 'mechanisms',
         'W': 'airframe', 'D': 'airframe', 'C': 'airframe', 'H': 'airframe', 'G': 'ground+test', 'K': 'tools',
         'T': 'transport', 'U': 'tools'}
def f(v):
    try: return float(v)
    except: return None

def load():
    L = []
    for x in rows:
        u, q = f(x['unit_usd_pessimistic']), f(x['qty_total'])
        if u is None: continue
        gates = re.findall(r'X\d+', x['order'])
        if any(g in ('X10', 'X12') for g in gates): continue
        ven = x['vendor'].split('/')[0].strip()
        k = None if x['order'].startswith('LOCAL') else (ven, 'DEC' if x['order'].startswith('DEC') else 'EARLY')
        grp = 'tools' if 'X14' in gates else GROUP.get(x['line'][0], 'other')
        L.append(dict(line=x['line'], u=u, q=q, k=k, g=grp, tool='X14' in gates))
    return L

def tot(L, crash=0.0):
    ks = {x['k'] for x in L if x['k'] and x['u'] * x['q'] > 0}
    goods = sum(x['u'] * x['q'] * T for x in L)
    ship = len(ks) * SH
    by = {}
    for x in L: by[x['g']] = by.get(x['g'], 0) + x['u'] * x['q'] * T
    by['shipping+FAA'] = ship + FAA
    sp = goods + ship + FAA
    return dict(spend=round(sp, 2), crash=round(crash, 2), total=round(sp + crash, 2), ships=len(ks), by={k: round(v, 2) for k, v in by.items()})

def mod(L, ops):
    L = copy.deepcopy(L)
    for op in ops:
        kind = op[0]
        if kind == 'rm': L = [x for x in L if x['line'] not in op[1]]
        elif kind == 'set':   # ('set', line, unit_usd, qty|None, vendor|None)
            for x in L:
                if x['line'] == op[1]:
                    x['u'] = op[2]
                    if op[3] is not None: x['q'] = op[3]
                    if len(op) > 4 and op[4]: x['k'] = op[4]
        elif kind == 'add': L.append(dict(line=op[1], u=op[2], q=op[3], k=op[4], g=op[5], tool=False))
        elif kind == 'ship':
            for x in L:
                if x['line'] in op[1]: x['k'] = op[2]
    return L

def crash_bill(L, spare_tube, extra_items=0.0):
    d = {x['line']: x for x in L}
    cost = d['P01']['u'] + d['M01']['u'] + extra_items
    vend = {d['P01']['k'], d['M01']['k']}
    if not spare_tube:
        cost += d['W10']['u']; vend.add(d['W10']['k'])
    return round(cost * T + len(vend) * SH, 2)

RDQ = ('RaceDayQuads', 'EARLY'); AMZ = ('Amazon', 'EARLY'); ZORO = ('Zoro', 'EARLY')
base0 = load()

# ---- 1. honest baseline: every re-check outcome applied
HONEST = [('rm', ['C07', 'C08']), ('add', 'C09', 15.69, 1, ZORO, 'airframe'),   # System Three 3145S16 quart, Zoro snippet 2026-11-14 UNVERIFIED (C2.md)
          ('set', 'W10', 118.97, None)]                                          # RW 35046-S 36 in, no spare tube (C4.md); 48 in = 151.96
base_L = mod(base0, HONEST)
B_crash = crash_bill(base_L, spare_tube=False)
B = tot(base_L, B_crash)
B_nt = tot([x for x in base_L if not x['tool']], B_crash)

# ---- 5. recommended path, ordered by engineering risk (unit USD pessimistic; every price EST / UNVERIFIED)
LEV = [
 ('L0', 1, 'Keep the 48 in tube $151.96: the third 344 mm tube is the spare, so the reserve no longer carries a tube ($119 + shipment)', [('set', 'W10', 151.96, None)]),
 ('L1', 1, 'Lean tools: drop K01 (lever-arm torque), K04 (phone), K05 (hand bend), K06 (balance on shaft), K08 (TPU from Jacobs stock); K09 2 x 5-pack', [('rm', ['K01', 'K04', 'K05', 'K06', 'K08']), ('set', 'K09', 3.78, 2, None)]),
 ('L2', 1, 'Hot wire from a flight pack: Ni80 wire only, no G11 supply (D1 check)', [('set', 'G11', 6.0, None)]),
 ('L3', 1, 'Plain Pocket ELRS $64.99 not Crush, in the B01 cart', [('set', 'R01', 64.99, None, ('ReadyMadeRC', 'EARLY'))]),
 ('L4', 1, 'Merge carts: XT60H to RDQ, M6 nut / PETG / ASA to Amazon, airspeed to RDQ', [('ship', ['H06', 'A04'], RDQ), ('ship', ['B06', 'W05', 'W08'], AMZ)]),
 ('L5', 1, 'Spares: props 12 -> 8, adapters 12 -> 8, caps 13 -> 9 (F1 48 kHz derate check), one LiPo bag, one 16 AWG reel', [('set', 'B03', 4.98, 8), ('set', 'B05', 0.5, 8), ('set', 'F07', 3.03, 9), ('set', 'G02', 9.99, 1), ('set', 'F03', 14.0, 1)]),
 ('L6', 2, 'Drop spare test tube W03 and PTFE W11 (packing-tape release; C2/D3 check)', [('rm', ['W03', 'W11'])]),
 ('L7', 2, 'Fin-tube plug from a US 19 mm tube $28.56 (eBay, UNVERIFIED) not Austria D08', [('set', 'D08', 28.56, None, ('eBay US', 'EARLY'))]),
 ('L8', 2, 'No T05 mat (Jacobs ply + D05 neoprene), T06 foam, T07 tote (team stock)', [('rm', ['T05', 'T06', 'T07'])]),
 ('L9', 3, 'SpeedyBee F405 Wing APP $51.99 (eurilca snippet) not CoreWing $69.49; bdshot / 8 A BEC UNVERIFIED', [('set', 'A01', 51.99, None, ('eurilca', 'EARLY'))]),
]
def run_path(ids, spare_tube=None, extra_items=0.0, with_tools=True):
    if spare_tube is None: spare_tube = 'L0' in ids
    L = copy.deepcopy(base_L)
    for i, _, _, ops in LEV:
        if i in ids: L = mod(L, ops)
    if not with_tools: L = [x for x in L if not x['tool']]
    return tot(L, crash_bill(L, spare_tube, extra_items)), L

if __name__ == '__main__':
    print('BASELINE honest, tools counted :', B['spend'], '+ crash', B['crash'], '=', B['total'], 'ships', B['ships'])
    print('  by group', B['by'])
    print('BASELINE honest, X14 tools out :', B_nt['spend'], '+ crash', B_nt['crash'], '=', B_nt['total'])
    cum = []
    for i, r, d, ops in LEV:
        cum.append(i)
        t, _ = run_path(cum)
        print(f"cum {i:4s} risk {r}  total {t['total']:9.2f}  (spend {t['spend']:.2f} crash {t['crash']:.2f})  {d[:60]}")
    ids = [i for i, *_ in LEV if i != 'L9']
    t0, L0 = run_path(ids)
    print('after L0-L8 (original FC):', t0['total'], t0['by'])
    ARCH = {
     'A1 one flight pack only (breaks the 2-pack schedule rule; reference)': [('set', 'P01', 131.99, 1)],
     'A2 2 x CNHL LiHV 6000 $69.99 (E2 failed it: leads, stock, CG)': [('set', 'P01', 69.99, 2, ('chinahobbyline', 'EARLY'))],
     'A3 fin tube INFINITubeV 36 in $76.99 (C4: cheap tube fails stiffness)': [('set', 'W10', 76.99, None)],
     'A4 3S 6000 packs ~$50 x2 (EST; full E1/E2/B1/A3 re-derive)': [('set', 'P01', 50.0, 2, AMZ)],
     'A5 defer airspeed sensor (violates user decision; reference)': [('rm', ['A04'])],
    }
    for n, ops in ARCH.items():
        L = mod(L0, ops); t = tot(L, crash_bill(L, True)); print(f"{n[:80]:80s} {t['total']:9.2f} ({t['total'] - t0['total']:+.2f})")
    t, L = run_path([i for i, *_ in LEV])
    print('FULL path L0-L9:', t['total'], t['by'], 'gap to 2000:', round(t['total'] - LIMIT, 2))
