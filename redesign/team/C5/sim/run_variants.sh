#!/bin/sh
# C5 shoe design-fix study (coarse level h 0.4 mm, both load cases), for CR-C5-18. Run from the repo root.
L=redesign/team/C5/sim
for v in "w=0.0016,rim_t=0.0024" "w=0.002,rim_t=0.003,r_in=0.001" "w=0.002,rim_t=0.003,r_in=0.001,engage=0.025"; do
  for c in +y +z; do
    tag=$(echo "$v" | tr ',=.' '__p')
    C5_FEA_VARIANT="$v" python -I $L/fea_shoe.py --one 0.4 $c > $L/runs/log_var_${tag}_${c}.txt 2>&1 &
  done
done
wait
