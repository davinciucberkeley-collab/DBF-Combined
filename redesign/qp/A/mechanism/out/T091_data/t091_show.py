import sys, json
R = json.load(open(sys.argv[1])); node = sys.argv[2] if len(sys.argv) > 2 else 's+0.000'
names = []; [names.append(r['name']) for r in R if r['name'] not in names]
print('%-58s | f27 kd/nom/hi | gov(100) kd/nom/hi | GM(x1.0) kd/nom/hi | GM(x0.8) | GM(x1.2) | D185 | lim pole Hz | dI | forced win/sweep (hi,0.5%%)' % 'candidate')
for n in names:
    rows = {r['kind']: r for r in R if r['name'] == n and r['group'][0] == 'nominal'}
    if not rows: continue
    def f27(r):
        c = [(f, g) for f, g in r['flex'][node] if 20 < f < 36]; return max(c, key=lambda x: abs(x[1])) if c else (float('nan'), 0)
    def gov(r):
        c = [f for f, cx, cy in r['strong'] if 80 <= f <= 125]; return c[0] if c else float('nan')
    ks = ('kd', 'nom', 'hi')
    gm = lambda s: '/'.join('%.2f' % rows[k]['gm'][node][s] for k in ks)
    fo = ''
    if 'forced' in rows['hi']: z = rows['hi']['forced'][node]['0.005']; fo = '%.1f/%.0f' % (z['window'], z['sweep'])
    print('%-58s | %s | %s | %s | %s | %s | %s | %s | %+.4f | %s' % (n[:58], '/'.join('%.1f(%.2f)' % f27(rows[k]) for k in ks), '/'.join('%.1f' % gov(rows[k]) for k in ks), gm('1.0'), gm('0.8'), gm('1.2'),
          ''.join('F' if rows[k]['d185_fail'] else 'p' for k in ks), '/'.join('%.1f' % (rows[k]['lim'][node][1] or 0) for k in ks), rows['nom']['dI'], fo))
