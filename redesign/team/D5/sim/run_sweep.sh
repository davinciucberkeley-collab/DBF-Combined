#!/bin/sh
# D5-R6 shoe FEA sweep (coarse h 0.4 mm, both cases) + the C5 cross-check. Run from the repo root.
L=redesign/team/D5/sim
for v in "ws=0.0008,rim_t=0.0032" "ws=0.001,rim_t=0.003" "ws=0.0012,rim_t=0.0028" "ws=0.0014,rim_t=0.0026"; do
  for c in +y +z; do
    tag=$(echo "$v" | tr ',=.' '__p')
    D5_FEA_VARIANT="$v" python -I $L/fea_shoe_d5.py --one 0.4 $c > $L/runs/log_${tag}_${c}.txt 2>&1 &
  done
done
wait
