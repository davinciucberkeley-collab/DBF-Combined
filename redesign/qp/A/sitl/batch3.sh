#!/bin/bash
# QP-2 WIND round: levers at 5 m/s, 4 parallel SITL instances. usage: SCR=<scratch> bash batch3.sh
cd "$(dirname "$0")"
PY="$SCR/venv/Scripts/python"
run() { i=$1; tag=$2; shift; shift; timeout 600 "$PY" run_case.py "$tag" inst=$i hold=40 "$@" > "runs/$tag.out" 2>&1; echo "$tag done $(date +%T)"; }
( run 0 w_a45 wind=5 from=45 arm=1.2; run 0 w_a70 wind=5 from=70 arm=1.2; run 0 w_a0 wind=5 from=0 arm=1.2; run 0 w_h80 wind=5 from=80 ) &
( run 1 w_c45 wind=5 from=45 cant=16; run 1 w_c70 wind=5 from=70 cant=16; run 1 w_h60 wind=5 from=60; run 1 w_h110 wind=5 from=110 ) &
( run 2 w_s45 wind=5 from=45 wing_s=0.75; run 2 w_s70 wind=5 from=70 wing_s=0.75; run 2 w_s0 wind=5 from=0 wing_s=0.75; run 2 w_wv45 wind=5 from=45 P:Q_WVANE_ENABLE=1 ) &
( run 3 w_p45 wind=5 from=45 P:Q_M_SPIN_MAX=0.95; run 3 w_p70 wind=5 from=70 P:Q_M_SPIN_MAX=0.95; run 3 w_f45 wind=5 from=45 fin_s=0.7; run 3 w_f70 wind=5 from=70 fin_s=0.7 ) &
wait; echo ALL DONE3
