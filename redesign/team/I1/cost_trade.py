"""I1 cost trade (2026-11-14): reprices BOM.csv levers with the BOM's own model.
Run: python -I team/I1/cost_trade.py   (reads BOM.csv; writes nothing)
Model: pessimistic line = qty_total x unit_usd_pessimistic x 1.1025; shipments = distinct
(vendor, EARLY/DEC) groups of non-LOCAL lines x 10.71; + 5 FAA + 7 tax-measure + 0.07 rounding.
Flight-ready set excludes lines gated X10, X12, X13. Reproduces bom_summary 2,979.84.
"""
import csv, re, copy, os
T = 1.1025; SH = 10.71
rows = [x for x in csv.DictReader(open(os.path.join(os.path.dirname(__file__), 'BOM.csv'), encoding='utf-8')) if x['line'] != 'TOTAL']
def f(v):
    try: return float(v)
    except: return None
base = []
for x in rows:
    u, q = f(x['unit_usd_pessimistic']), f(x['qty_total'])
    if u is None: continue
    if any(g in ('X10', 'X12', 'X13') for g in re.findall(r'X\d+', x['order'])): continue
    k = None if x['order'].startswith('LOCAL') else (x['vendor'].split('/')[0].strip(), 'DEC' if x['order'].startswith('DEC') else 'EARLY')
    base.append(dict(line=x['line'], pe=round(q * u * T, 2), k=k))
def total(L):
    ks = {x['k'] for x in L if x['k'] and x['pe'] > 0}
    return round(sum(x['pe'] for x in L) + len(ks) * SH + 12.07, 2), len(ks)
def apply(L, ops):
    L = copy.deepcopy(L)
    for op in ops:
        if op[0] == 'rm': L = [x for x in L if x['line'] not in op[1]]
        elif op[0] == 'set':
            for x in L:
                if x['line'] == op[1]:
                    x['pe'] = round(op[2] * T, 2)
                    if len(op) > 3: x['k'] = op[3]
    return L
RDQ = ('RaceDayQuads', 'EARLY'); AMZ = ('Amazon', 'EARLY'); RM = ('ReadyMadeRC', 'EARLY')
def run(L, ops):
    for op in ops:
        if op[0] == 'amzdec':
            L = copy.deepcopy(L)
            for x in L:
                if x['k'] == ('Amazon', 'DEC'): x['k'] = AMZ
        else: L = apply(L, [op])
    return L
lev = {
'J1 Jacobs pliers+Allen wrenches (K05,K07)':(1,[('rm',['K05','K07'])]),
'T1 lever-arm torque, no K01':(2,[('rm',['K01'])]),
'T2 phone inclinometer, no K04':(1,[('rm',['K04'])]),
'T3 DIY prop balancer, no K06':(2,[('rm',['K06'])]),
'T4 no TPU spool K08':(3,[('rm',['K08'])]),
'H1 hot wire from pack (G11 -> wire, Zoro 100 ft upper bound)':(2,[('set','G11',22.15)]),
'S1 no 5th motor':(2,[('set','B01',4*39.99)]),
'S2 no 2nd ESC 4-pack B08':(3,[('rm',['B08'])]),
'S3 props 8 total, adapters 8 total':(1,[('set','B03',8*4.98),('set','B05',8*0.5)]),
'S4 no W03 spare 22x20 tube':(2,[('rm',['W03'])]),
'S5 RW tube 36 in':(3,[('set','W10',118.97)]),
'S6 caps 9 not 13':(2,[('set','F07',9*3.03)]),
'P1 one Gens Ace pack':(3,[('set','P01',131.99)]),
'P2 two CNHL LiHV 6000 (69.99)':(3,[('set','P01',2*69.99,('chinahobbyline','EARLY'))]),
'P3 one CNHL LiHV 6000':(4,[('set','P01',69.99,('chinahobbyline','EARLY'))]),
'X1 plain Pocket ELRS 64.99 in B01 shipment':(1,[('set','R01',64.99,RM)]),
'A1 defer airspeed sensor':(3,[('rm',['A04'])]),
'A2 no anemometer (phone)':(2,[('rm',['G14'])]),
'D1 plug: oak dowel $6.78 not D08':(3,[('set','D08',6.78,None)]),
'D2 plug: eBay US 19 mm $28.56':(2,[('set','D08',28.56,('eBay US','EARLY'))]),
'F1 fin tube INFINITubeV 36 in 76.99 (C4 gate)':(5,[('set','W10',76.99)]),
'C1 XT60H into RDQ cart':(1,[('set','H06',9.0,RDQ)]),
'C2 packing tape for PTFE (no W11)':(2,[('rm',['W11'])]),
'C3 M6 nut into Amazon cart':(1,[('set','B06',9.59,AMZ)]),
'C4 PETG+ASA into Amazon cart (same price EST)':(1,[('set','W05',20.99,AMZ),('set','W08',24.99,AMZ)]),
'C5 Amazon DEC lines into the Nov cart':(1,[('amzdec',)]),
}

lev['X2 no C07 silica / C08 microballoons (X14)']=(3,[('rm',['C07','C08'])])
lev['X3 no T07 tote (team stock)']=(1,[('rm',['T07'])])
lev['K9 blades 2 x 5-pack Walmart 3.78']=(1,[('set','K09',7.56)])
lev['E6 one LiPo bag']=(1,[('set','G02',9.99)])
lev['E2 one 16 AWG reel']=(1,[('set','F03',14.0)])
lev['E11 hot-wire bow from Jacobs scrap, no H05']=(1,[('rm',['H05'])])
lev['E1 SpeedyBee F405 Wing 47.99']=(3,[('set','A01',47.99)])
lev['E4 no T05 mat, T06 foam']=(2,[('rm',['T05','T06'])])
t0 = total(base)[0]
print('base', total(base))
for n, (r, ops) in lev.items():
    t = total(run(base, ops)); print(f"{n:64s} risk {r}  saves {t0 - t[0]:8.2f}")
REC = ['J1','T2','X1','S3','C1','C3','C4','C5','K9','E6','E2','T1','A2','S1','S4','H1','E11','C2','T3','P3','A1','T4','S2','S6','S5','D1','X2','X3','E4']
L = copy.deepcopy(base)
for p in REC:
    n = [k for k in lev if k.startswith(p + ' ')][0]
    L = run(L, lev[n][1]); print(f"cum {n[:58]:58s} {total(L)[0]:9.2f}")
print('recommended set spend', total(L), '+ 130 crash =', round(total(L)[0] + 130, 2))
