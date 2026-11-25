"""T-084 (FEA-lite, beam FE fe_a.py with wing_cell): modes vs rotor bands with the D-226 wing torsion cell credited in the spar beam (cell_props.json), nominal and lower-bound cell,
three corners; every strongly coupled mode (cx or cy >= 0.5) and its band status (94-321 Hz, T-066 rule, unchanged); plus the T-066 spar-only model for comparison.
python -I t084_modes_cell.py > modes_cell.txt"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.dont_write_bytecode = True
from t084_modes_probe import fe_a, fekw, BAND
CP = json.load(open(os.path.join(HERE, 'cell_props.json')))
def zones(tag):
    z = CP[tag]; k = list(z)
    return dict(zones=[(0.0751,) + tuple(z[k[0]][q] for q in ('EA', 'EI_flap', 'EI_in', 'GJ')), (0.40,) + tuple(z[k[1]][q] for q in ('EA', 'EI_flap', 'EI_in', 'GJ')),
                       (0.46,) + tuple(z[k[2]][q] for q in ('EA', 'EI_flap', 'EI_in', 'GJ'))])
CELLS = {'spar only (T-066 model)': None, 'cell nominal': zones('nominal'), 'cell lower bound': zones('lower (foam E,G x0.5, skin x0.7, no strip)')}
def table(cell, over=None):
    rows = {}
    for kind in ('kd', 'nom', 'hi'):
        F, info = fe_a.build(kind, **fekw(wing_cell=cell, **(over or {}))); res = F.solve(130)
        rows[kind] = res
    return rows
def summarize(rows):
    out = {}
    for kind, res in rows.items():
        st = [(f, cx, cy) for (f, e, v, cx, cy) in res if (cx >= 0.5 or cy >= 0.5) and f < 800]
        inb = [s for s in st if BAND[0] <= s[0] <= BAND[1]]
        lo = max([s[0] for s in st if s[0] < BAND[0]] or [0]); hi = min([s[0] for s in st if s[0] > BAND[1]] or [float('nan')])
        cmax = max([(max(cx, cy), f) for (f, e, v, cx, cy) in res if BAND[0] <= f <= BAND[1]] or [(0, 0)])
        out[kind] = dict(inband=inb, below=lo, above=hi, cmax_in_band=cmax)
    return out
if __name__ == '__main__':
    for name, cell in CELLS.items():
        rows = table(cell); s = summarize(rows)
        print(f"\n## {name}")
        for kind in ('kd', 'nom', 'hi'):
            d = s[kind]
            print(f"  {kind}: strong in band: {[(round(f,1), round(cx,2), round(cy,2)) for f, cx, cy in d['inband']] or 'none'};  highest strong below {d['below']:.1f} Hz (margin {100*(BAND[0]/d['below']-1):.0f} %), lowest strong above {d['above']:.1f} Hz (margin {100*(d['above']/BAND[1]-1):.0f} %);  max coupling of any in-band mode {d['cmax_in_band'][0]:.3f} at {d['cmax_in_band'][1]:.0f} Hz")
        res = rows['nom']
        print("  nom modes 60-600 Hz (f, cx, cy, top groups):")
        for (f, e, v, cx, cy) in res:
            if 60 < f < 600:
                top = sorted(e.items(), key=lambda kv: -kv[1])[:3]
                print(f"    {f:7.1f}  cx {cx:.3f} cy {cy:.3f}  " + ", ".join(f"{g} {100*x:.0f}%" for g, x in top))
