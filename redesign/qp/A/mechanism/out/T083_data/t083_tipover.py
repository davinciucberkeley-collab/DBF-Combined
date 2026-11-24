"""T-083: static tip-over (A-P9 >= 30 deg) with landing_a.static() at a given CG (env LAND_CG_X_MM), CAD pad geometry. Category: geometry arithmetic.
python -I t083_tipover.py CG_MM [CG_MM ...]"""
import os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.abspath(os.path.join(H, '..', '..', '..', 'structures'))); sys.dont_write_bytecode = True
for cg in sys.argv[1:]:
    os.environ['LAND_CG_X_MM'] = cg
    for k in [k for k in sys.modules if k.startswith('landing')]: del sys.modules[k]
    import landing_a as L
    s = L.static()
    print('CG %s mm:' % cg, {k: round(v, 2) for k, v in s.items() if isinstance(v, float) and (k.startswith('tip') or k in ('h', 'v_tip_parked'))})
