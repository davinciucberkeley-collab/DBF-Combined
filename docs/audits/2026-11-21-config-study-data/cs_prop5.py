"""Option 3 alone and option 2 (legs) on the MN2212 KV780 model (writes cs_prop5_out.txt rows to stdout)."""
import sys
sys.path.insert(0, r'C:/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined/docs/audits/2026-11-21-config-study-data')
import cs_prop as S
for tag, b, cg in (('3 alone (KV780), rib 16x14, 2 plies', 1598.4-42.8, 30.17-3.04), ('3 alone, rib 14x12', 1598.4-47.0, 30.17-1.06-2.4), ('2 legs (KV780) EST', 1598.4+119, 45.4)):
    mp = S.pred(b); m = S.metrics(mp)
    print('| %s | %.1f | %.3f | %.2f | %.2f | %+.2f | %.3f / %.3f | %.3f | %.0f | %.2f |' % (tag, b, mp, cg, 100*(S.NP-cg)/S.C, m['window'], m['tw_fresh'], m['tw_fresh_dl'], m['tw_sag_dl'], m['cruise_s'], m['k13vs']))
