#!/bin/sh
# C5-R6: shoe FEA on the D-65 stack (sleeve end wall 2.0 mm, rim 3.0 mm, inside fillet R 1.0 mm, 25 mm engagement),
# 3 levels x 2 cases, then merge -> sim/out/fea_shoe_v_engage25_rim_t3_w2_rin1.json. Run from the repo root.
# D5 has not yet published the D-65 numbers in team/D5/claims.json (CALC-D5-SIDE inputs); until it does, the variant
# overrides D5's w / rim_t / engage inputs. When D5 publishes them, run sim/run_fea.sh instead (no variant).
L=redesign/team/C5/sim
V="w=0.002,rim_t=0.003,r_in=0.001,engage=0.025"
for h in 0.4 0.32 0.2667; do for c in +y +z; do
  C5_FEA_VARIANT="$V" python -I $L/fea_shoe.py --one $h $c > $L/runs/log_d65_${h}_${c}.txt 2>&1 &
done; done
wait
C5_FEA_VARIANT="$V" python -I $L/fea_shoe.py --collect
