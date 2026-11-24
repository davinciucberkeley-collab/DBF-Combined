# T-101 D-253: inviscid Hess-Smith Cm_c/4 at alpha 0 for the scout airfoils. Run from the repo root: python -I redesign/qp/A/mechanism/out/T101_data/reflex_panel.py redesign/qp/A docs/audits/2026-11-24-T101-reflex-coords
import sys, os, glob, numpy as np
sys.path.insert(0, sys.argv[1]); import aero_s5010 as P
for f in sorted(glob.glob(os.path.join(sys.argv[2], "*.dat"))):
    pts=[]
    for l in open(f).read().splitlines()[1:]:
        try:
            a=list(map(float,l.split()))
            if len(a)==2 and abs(a[0])<=1.01: pts.append(a)
        except ValueError: pass
    xy=np.array(pts)
    if len(xy)<20: print(os.path.basename(f),"skip"); continue
    try:
        r0=P.panel(xy[::-1],0.0); r1=P.panel(xy,0.0)
        r = r0 if r0[0]>r1[0] else r1
        print(f"{os.path.basename(f):18s} n {len(xy)} cl0 {r[0]:.3f} cm_c/4 {r[1]:+.4f}")
    except Exception as e: print(os.path.basename(f),"err",e)
