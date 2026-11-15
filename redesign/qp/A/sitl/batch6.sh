#!/bin/bash
# QP-2 WIND round 4: turbulence at edge-on and at 4 m/s. usage: SCR=<scratch> bash batch6.sh
cd "$(dirname "$0")"
PY="$SCR/venv/Scripts/python"
run() { i=$1; tag=$2; shift; shift; timeout 600 "$PY" run_case.py "$tag" inst=$i hold=45 "$@" > "runs/$tag.out" 2>&1; echo "$tag done $(date +%T)"; }
( run 0 w_h90t wind=5 from=90 turb=1.0; run 0 w_h90t2 wind=5 from=90 turb=1.0 seed=2 ) &
( run 1 w_ac90t wind=5 from=90 turb=1.0 arm=1.2 cant=16; run 1 w_ac80t wind=5 from=80 turb=1.0 arm=1.2 cant=16 ) &
( run 2 w4_h70t wind=4 from=70 turb=1.0; run 2 w4_ac70t wind=4 from=70 turb=1.0 arm=1.2 cant=16 ) &
( run 3 w4_h90t wind=4 from=90 turb=1.0; run 3 w4_ac60t wind=4 from=60 turb=1.0 arm=1.2 cant=16 ) &
wait; echo ALL DONE6
