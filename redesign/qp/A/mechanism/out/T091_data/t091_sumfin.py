import json, sys
R=json.load(open(sys.argv[1])); names=[]; [names.append(r['name']) for r in R if r['name'] not in names]
base_m=None
for n in names:
    rs=[r for r in R if r['name']==n]; mn={}; fw={}; fs={}; d185=0
    for r in rs:
        for ax in ('pit','rll','yaw'):
            for sc,v in r['gm'][ax].items(): mn[(ax,sc)]=min(mn.get((ax,sc),99),v)
        for z,v in r['forced'].items(): fw[z]=max(fw.get(z,0),v['window']); fs[z]=max(fs.get(z,0),v['sweep'])
        d185+=r['d185_fail']
    m=sum(r['mass_fe'] for r in rs)/len(rs)
    if base_m is None: base_m=m
    print(n); print('  GM min over 72:', ' '.join(f'{a}{s}={v:.2f}' for (a,s),v in sorted(mn.items())))
    print('  forced window', {z:round(v,1) for z,v in fw.items()}, 'sweep', {z:round(v,1) for z,v in fs.items()}, 'D185 FAIL %d/72'%d185, 'dm_FE %.1f g'%((m-base_m)*1000))
