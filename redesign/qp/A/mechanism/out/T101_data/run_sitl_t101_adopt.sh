#!/bin/bash
# T-101 AM-059: the candidate adopted configuration A1 = C3 controls + T1 trim (CG 23.49 mm, AIRSPEED_CRUISE 18, AIRSPEED_MAX 20) + RLL2SRV_RMAX 45 + RLL2SRV_TCONST 0.9
# (tuning batch sitl_batch_TUNE.log: 0.9 kept the 60 deg change at 1.50 s <= 1.7 s and the elevon at 17.4 deg; FF 0.25 too slow, 2.21 s).
# Part 1: the four C3 transition cases (pitch use claim = worst of four), via run_sitl_t101.sh. Part 2: RQ4 (cruise, 1.5 s legs) and RQ5 (transition window) re-run with A1.
cd /c/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined/redesign/qp/A/sitl
A1="fw_hold=1.0 P:TECS_SPDWEIGHT=0.5 cg=23.49 P:AIRSPEED_CRUISE=18 P:AIRSPEED_MAX=20 P:RLL2SRV_RMAX=45 P:RLL2SRV_TCONST=0.9"
bash ../mechanism/out/T101_data/run_sitl_t101.sh A1 "$A1"
export SCR=C:/Users/dillo/tools/ardupilot-sitl A_MOTOR=x2216
PY=$SCR/venv/Scripts/python.exe
LOG=../mechanism/out/T101_data/sitl_batch_A1R.log; : > $LOG
G="c3g=1 gv_vert=1.62 gv_side=2.52 gv_dur=1.08"
run() { tag=$1; shift; s=$(date +%s); $PY run_fwd.py $tag inst=2 speedup=8 case=trans mass=1.881 wind=0 hold=25 r=1.33 $A1 "$@" > runs/$tag.out 2>&1; echo "$tag exit $? wall $(( $(date +%s)-s )) s" >> $LOG; $PY fwd_sum.py $tag >> $LOG 2>&1; }
run T101A1RQ4_T074 cruise_s=16 $G c3g_pre=6 c3g_stick=0.667
run T101A1RQ5_T074 cruise_s=8 $G c3g_stick=0.333
echo ALLDONE >> $LOG
