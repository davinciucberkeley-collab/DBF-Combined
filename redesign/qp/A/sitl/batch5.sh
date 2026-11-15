#!/bin/bash
# QP-2 WIND round 3: turbulence and gust at the heading window edges, baseline vs arm 1.2 + cant 16. usage: SCR=<scratch> bash batch5.sh
cd "$(dirname "$0")"
PY="$SCR/venv/Scripts/python"
run() { i=$1; tag=$2; shift; shift; timeout 600 "$PY" run_case.py "$tag" inst=$i hold=45 "$@" > "runs/$tag.out" 2>&1; echo "$tag done $(date +%T)"; }
( run 0 w_h80t wind=5 from=80 turb=1.0; run 0 w_h80g wind=5 from=80 gust=2 gust_at=20 ) &
( run 1 w_ac70t wind=5 from=70 turb=1.0 arm=1.2 cant=16; run 1 w_ac70g wind=5 from=70 gust=2 gust_at=20 arm=1.2 cant=16 ) &
( run 2 w_ac60t wind=5 from=60 turb=1.0 arm=1.2 cant=16; run 2 w_ac60g wind=5 from=60 gust=2 gust_at=20 arm=1.2 cant=16 ) &
( run 3 w_h60t wind=5 from=60 turb=1.0; run 3 w_ac70t2 wind=5 from=70 turb=1.0 seed=2 arm=1.2 cant=16 ) &
wait; echo ALL DONE5
