import json,sys
for ln in open('results.jsonl'):
    r=json.loads(ln); t=r['tag']
    if not t.startswith(('w_','w4_')) or not r['summary']: continue
    s=r['summary']; print(t, ' '.join(r['args']), '| lean %.1f/%.1f umax %.3f floor %.2fs yawerr %.1f/%.1f pos %.2f/%.2f diff %.2f'%(s['lean_max'],s['lean_mean'],s['u_max'],s['t_floor_s'],s['yaw_err_max'],s['yaw_err_rms'],s['pos_err_max'],s['pos_err_last20_mean'],s['diag_spread_max']))
