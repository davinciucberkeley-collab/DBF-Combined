#!/bin/bash
# QP-2 WIND round 2: lever combinations and margin cases, 4 parallel instances. usage: SCR=<scratch> bash batch4.sh
cd "$(dirname "$0")"
PY="$SCR/venv/Scripts/python"
run() { i=$1; tag=$2; shift; shift; timeout 600 "$PY" run_case.py "$tag" inst=$i hold=40 "$@" > "runs/$tag.out" 2>&1; echo "$tag done $(date +%T)"; }
( run 0 w_ac70 wind=5 from=70 arm=1.2 cant=16; run 0 w_ac60 wind=5 from=60 arm=1.2 cant=16; run 0 w_ac45 wind=5 from=45 arm=1.2 cant=16; run 0 w_s60 wind=5 from=60 wing_s=0.75 ) &
( run 1 w_sac70 wind=5 from=70 wing_s=0.75 arm=1.2 cant=16; run 1 w_sac60 wind=5 from=60 wing_s=0.75 arm=1.2 cant=16; run 1 w_sac45 wind=5 from=45 wing_s=0.75 arm=1.2 cant=16; run 1 w_sac0 wind=5 from=0 wing_s=0.75 arm=1.2 cant=16 ) &
( run 2 w_sc60 wind=5 from=60 wing_s=0.75 cant=16; run 2 w_sc45 wind=5 from=45 wing_s=0.75 cant=16; run 2 w_sa60 wind=5 from=60 wing_s=0.75 arm=1.2; run 2 w_sa45 wind=5 from=45 wing_s=0.75 arm=1.2 ) &
( run 3 w_sac60t wind=5 from=60 turb=1.0 wing_s=0.75 arm=1.2 cant=16 hold=45; run 3 w_sac60g wind=5 from=60 gust=2 gust_at=20 wing_s=0.75 arm=1.2 cant=16 hold=45; run 3 w_sac60m wind=5 from=60 mass=1.37 wing_s=0.75 arm=1.2 cant=16; run 3 w_sac45w6 wind=6 from=45 wing_s=0.75 arm=1.2 cant=16 ) &
wait; echo ALL DONE4
