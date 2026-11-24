#!/bin/bash
# QP-5 (D-195): re-run of the forward-flight, transition, landing and hover-wind cases at cant 17, D-191 gains, CAD mass/CG/inertia of 2026-11-15, S5010 aero.  usage: SCR=<scratch> bash batch_qp5.sh
cd "$(dirname "$0")"
PY="$SCR/venv/Scripts/python"
SCR="$SCR" NW=4 "$PY" jobq.py jobs_qp5.txt > queue_qp5.log 2>&1
run() { i=$1; tag=$2; shift; shift; timeout 900 "$PY" run_case.py "$tag" inst=$i hold=45 arm=1.2 cant=17 turb=1.0 wind=4 mass=1.455 "$@" > "runs/$tag.out" 2>&1; echo "$tag done $(date +%T)"; }
run 0 R5_h60 from=60 &
run 1 R5_h60s2 from=60 seed=2 &
run 2 R5_h60s3 from=60 seed=3 &
run 3 R5_h70 from=70 &
wait
run 0 R5_h90 from=90 &
run 1 R5_h70s2 from=70 seed=2 &
run 2 R5_h80 from=80 &
wait; echo ALL DONE QP5
