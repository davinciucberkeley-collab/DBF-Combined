import json
R=json.load(open(''+__import__('sys').argv[1]+''))
for nd in ('s+0.000','s+0.075','s+0.150','s+0.285'):
    mn={}; fw={}; fs={}
    for r in R:
        g=r['nodes'][nd]['gm']
        for ax in g:
            for sc,v in g[ax].items(): mn[(ax,sc)]=min(mn.get((ax,sc),99),v)
        for z,v in r['nodes'][nd]['forced'].items():
            fw[z]=max(fw.get(z,0),v['window']); fs[z]=max(fs.get(z,0),v['sweep'])
    print(nd,{f'{a}|{s}':round(v,2) for (a,s),v in sorted(mn.items())}); print('   forced window',{z:round(v,1) for z,v in fw.items()},'sweep',{z:round(v,1) for z,v in fs.items()})
