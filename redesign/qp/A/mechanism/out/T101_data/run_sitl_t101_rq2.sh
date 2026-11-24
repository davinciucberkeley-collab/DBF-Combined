#!/bin/bash
# T-101 D-254 follow-up: doublet sized to the derived criterion. RQ2/RQ3 used stick 0.75 (+-33.75 deg bank reversal, 67.5 deg change, overshoot to 44-50 deg),
# beyond the criterion. RQ4 = steady cruise, worst-direction 3 m/s gust + bank reversal +-30 deg (stick 0.667: 60 deg change, Category B);
# RQ5 = pitch peak (transition window), same gust + reversal +-15 deg (stick 0.333: 30 deg change, Category C). Same base as run_sitl_t101_rq.sh.
cd /c/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined/redesign/qp/A/sitl
export SCR=C:/Users/dillo/tools/ardupilot-sitl A_MOTOR=x2216
PY=$SCR/venv/Scripts/python.exe
LOG=../mechanism/out/T101_data/sitl_batch_RQ2.log; : > $LOG
BASE="inst=2 speedup=8 case=trans mass=1.881 wind=0 hold=25 r=1.33 fw_hold=1.0 P:TECS_SPDWEIGHT=0.5 cg=23.49 P:AIRSPEED_CRUISE=18 P:RLL2SRV_RMAX=45"
G="c3g=1 gv_vert=1.62 gv_side=2.52 gv_dur=1.08"
run() { tag=$1; shift; s=$(date +%s); $PY run_fwd.py $tag $BASE "$@" > runs/$tag.out 2>&1; echo "$tag exit $? wall $(( $(date +%s)-s )) s" >> $LOG; $PY fwd_sum.py $tag >> $LOG 2>&1; }
run T101RQ4_T074 cruise_s=16 $G c3g_pre=6 c3g_stick=0.667
run T101RQ5_T074 cruise_s=8 $G c3g_stick=0.333
echo ALLDONE >> $LOG
