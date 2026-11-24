#!/bin/bash
cd "$(dirname "$0")"
PY="$SCR/venv/Scripts/python"
run() { tag=$1; shift; timeout 420 "$PY" run_case.py "$tag" "$@" > "runs/$tag.out" 2>&1; echo "$tag done $(date +%T)"; }
run t20_5 wind=5 from=70 hold=40
run t20_7 wind=7 from=70 hold=40
run d7c16 wind=7 from=45 cant=16 hold=40
run b5pos wind=5 from=0 hold=40 P:Q_P_NE_VEL_I=1.5 P:Q_P_NE_POS_P=1.0
echo ALL DONE2
