#!/bin/sh
# C5-R6: independent shoe FEA of D5's R6 stack (subsystems/landing/params.json 15:12: sleeve walls 1.2 mm, rim 2.8 mm,
# lip = rim, inside fillets R 1.0, engagement 25 mm, cartridge 20.9 x 11.0 mm, short snap windows from landing.stack).
# D5 has not yet re-published CALC-D5-SIDE, so the R6 numbers go in as a variant over D5's claims. C5's model meshes the
# legs at the sleeve wall (D5's own model at 0.8 mm). 3 levels x 2 cases, then merge. Run from the repo root.
L=redesign/team/C5/sim
V="ws=0.0012,rim_t=0.0028,lip=0.0028,fy=0.0209,fz=0.011,engage=0.025,r_in=0.001"
for h in 0.4 0.32 0.2667; do for c in +y +z; do
  C5_FEA_VARIANT="$V" python -I $L/fea_shoe.py --one $h $c > $L/runs/log_d5r6_${h}_${c}.txt 2>&1 &
done; done
wait
C5_FEA_VARIANT="$V" python -I $L/fea_shoe.py --collect
