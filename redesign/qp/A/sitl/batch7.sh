#!/bin/bash
# QP-2 WIND round 5: wing side area 0.85 with arm 1.2 + cant 16, turbulence. usage: SCR=<scratch> bash batch7.sh
cd "$(dirname "$0")"
PY="$SCR/venv/Scripts/python"
run() { i=$1; tag=$2; shift; shift; timeout 600 "$PY" run_case.py "$tag" inst=$i hold=45 "$@" > "runs/$tag.out" 2>&1; echo "$tag done $(date +%T)"; }
run 0 w_m70t wind=5 from=70 turb=1.0 wing_s=0.85 arm=1.2 cant=16 &
run 1 w_m70t2 wind=5 from=70 turb=1.0 seed=2 wing_s=0.85 arm=1.2 cant=16 &
run 2 w_m90t wind=5 from=90 turb=1.0 wing_s=0.85 arm=1.2 cant=16 &
run 3 w_sac70t2 wind=5 from=70 turb=1.0 seed=2 wing_s=0.75 arm=1.2 cant=16 &
wait; echo ALL DONE7
