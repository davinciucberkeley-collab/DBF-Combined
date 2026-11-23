import sys; sys.path.insert(0, '.')
import t091_lib as L
for kind in L.KINDS:
    F, res = L.solve(kind, 'nominal', 'al6061', L.PAD_NOM)
    print('##', kind)
    for f, cx, cy, top in L.modes_table(F, res, 130):
        print('  %7.2f Hz cx %.2f cy %.2f  %s' % (f, cx, cy, top))
    print('mass FE', sum(F.mass.values()))
