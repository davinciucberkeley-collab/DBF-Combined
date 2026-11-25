#!/bin/bash
# T-101 AM-059 step 1: roll overshoot tuning in the RQ4 cruise case (T1 trim, RLL2SRV_RMAX 45, worst 3 m/s gust, +-30 deg bank reversal),
# legs 2.0 s (so the 60 deg change can be timed against Category B 1.7 s). Variants of RLL2SRV_TCONST (ArduPlane default 0.5) and RLL_RATE_FF.
cd /c/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined/redesign/qp/A/sitl
export SCR=C:/Users/dillo/tools/ardupilot-sitl A_MOTOR=x2216
PY=$SCR/venv/Scripts/python.exe
LOG=../mechanism/out/T101_data/sitl_batch_TUNE.log; : > $LOG
BASE="inst=2 speedup=8 case=trans mass=1.881 wind=0 hold=25 r=1.33 fw_hold=1.0 P:TECS_SPDWEIGHT=0.5 cg=23.49 P:AIRSPEED_CRUISE=18 P:RLL2SRV_RMAX=45 cruise_s=18 c3g=1 gv_vert=1.62 gv_side=2.52 gv_dur=1.08 c3g_pre=6 c3g_stick=0.667 c3g_leg=2.0"
run() { tag=$1; shift; s=$(date +%s); $PY run_fwd.py $tag $BASE "$@" > runs/$tag.out 2>&1; echo "$tag exit $? wall $(( $(date +%s)-s )) s" >> $LOG; $PY fwd_sum.py $tag >> $LOG 2>&1; }
run T101TU05_T074
run T101TU07_T074 P:RLL2SRV_TCONST=0.7
run T101TU09_T074 P:RLL2SRV_TCONST=0.9
run T101TU07F_T074 P:RLL2SRV_TCONST=0.7 P:RLL_RATE_FF=0.25
echo ALLDONE >> $LOG
