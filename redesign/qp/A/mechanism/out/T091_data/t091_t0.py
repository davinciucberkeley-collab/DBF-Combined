import sys, time; sys.path.insert(0, '.')
import t091_lib as L
t0 = time.time()
for kind in L.KINDS:
    F, res = L.solve(kind, 'nominal', 'al6061', L.PAD_NOM, nmodes=150)
    for nd in ('s+0.000', 'hub'):
        c = L.pit_case(F, kind, nd)
        print(kind, nd, 'I_fe %.4f' % (1/c['inv_I']), 'flex<60:', [(round(a,1), round(b/c['inv_I'],2)) for a,b in c['flex'] if a<120], flush=True)
        g = L.gm_pitch(c, L.I_T0)
        print('   GM', {k:(round(v[0],2),v[1]) for k,v in g.items()}, 'lim pole', L.limiting(c,1.0,0.003,1.25,(1/c['inv_I'])/L.I_T0), '%.0f s'%(time.time()-t0), flush=True)
