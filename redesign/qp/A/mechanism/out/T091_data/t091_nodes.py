"""T-091 FC relocation: base airframe (no structural change), IMU at spar centre / s+0.075 / s+0.150 ...: 3-axis GM and forced response, all 24 groups x kd / nom / hi.  python -I t091_nodes.py <out.json> node1,node2"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import t091_lib as L, t091_cands as C
def do(task):
    group, kind, nodes, cn = task
    F, res = L.solve(kind, *group, (C.CANDS[cn] if cn else None), nmodes=400); out = dict(group=list(group), kind=kind, nodes={})
    for nd in nodes:
        g = L.gm_axes_node(F, kind, nd)
        out['nodes'][nd] = dict(gm={ax: {str(k): v for k, v in g[ax].items()} for ax in g}, forced={str(z): v for z, v in L.forced(F, res, nd).items()})
    return out
if __name__ == '__main__':
    nodes = sys.argv[2].split(','); cn = sys.argv[3] if len(sys.argv) > 3 else None; tasks = [(g, k, nodes, cn) for g in L.GROUPS for k in L.KINDS]; t0 = time.time()
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(18) as ex: res = list(ex.map(do, tasks, chunksize=2))
    json.dump(res, open(sys.argv[1], 'w'), default=str); print('done %.0f s' % (time.time()-t0))
