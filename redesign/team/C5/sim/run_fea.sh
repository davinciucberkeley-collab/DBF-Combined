#!/bin/sh
# C5 shoe FEA: 3 levels x 2 cases in parallel (3 SU2 threads each), then merge. Run from the repo root.
for h in 0.4 0.32 0.2667; do for c in +y +z; do
  python -I redesign/team/C5/sim/fea_shoe.py --one $h $c > redesign/team/C5/sim/runs/log_${h}_${c}.txt 2>&1 &
done; done
wait
python -I redesign/team/C5/sim/fea_shoe.py --collect
