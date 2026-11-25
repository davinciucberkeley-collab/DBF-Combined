#!/bin/bash
# T-101 D-254 (AM-057): derived roll / gust criterion check. All runs: T1 trim (pack at the aft slot end, CG 23.49 mm; AIRSPEED_CRUISE 18) and
# RLL2SRV_RMAX 45 (roll-rate demand cap = the derived cruise roll requirement, MIL-F-8785C Class I Level 1 Category B, about 45 deg/s).
# Gust = ONE 3 m/s 1-cos increment (RFS mean <= 5, gust <= 8 m/s), 1.08 s, in the worst direction for the elevon: vertical 1.62 + side 2.52 m/s (|v| = 3.0).
# RQ1 plain transition (pitch use); RQ2 gust + roll doublet at the pitch peak (transition window); RQ3 the same events in steady cruise (c3g_pre 6 s).
cd /c/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined/redesign/qp/A/sitl
export SCR=C:/Users/dillo/tools/ardupilot-sitl A_MOTOR=x2216
PY=$SCR/venv/Scripts/python.exe
LOG=../mechanism/out/T101_data/sitl_batch_RQ.log; : > $LOG
BASE="inst=2 speedup=8 case=trans mass=1.881 wind=0 hold=25 r=1.33 fw_hold=1.0 P:TECS_SPDWEIGHT=0.5 cg=23.49 P:AIRSPEED_CRUISE=18 P:RLL2SRV_RMAX=45"
G="c3g=1 gv_vert=1.62 gv_side=2.52 gv_dur=1.08 c3g_stick=0.75"
run() { tag=$1; shift; s=$(date +%s); $PY run_fwd.py $tag $BASE "$@" > runs/$tag.out 2>&1; echo "$tag exit $? wall $(( $(date +%s)-s )) s" >> $LOG; $PY fwd_sum.py $tag >> $LOG 2>&1; }
run T101RQ1_T074 cruise_s=8
run T101RQ2_T074 cruise_s=8 $G
run T101RQ3_T074 cruise_s=16 $G c3g_pre=6
echo ALLDONE >> $LOG
