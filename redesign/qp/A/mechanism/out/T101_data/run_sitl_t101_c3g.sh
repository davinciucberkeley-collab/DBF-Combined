#!/bin/bash
# T-101 step 4 (D-251 / reserve unit U-B): C3G = T101C3_T074 (no Lua, T-074 case, chord 0.25, fw_hold 1.0, TECS_SPDWEIGHT 0.5) plus, from the AR-017 pitch peak
# (1.14 s after the CRUISE command): vertical 1-cos gust 3 m/s (1.08 s), side 1-cos gust 3 m/s (1.08 s), roll doublet (stick +-0.75 of ROLL_LIMIT_DEG, 1.5 s each).
# one instance (inst 2, as T101C3_T074); usage: run_sitl_t101_c3g.sh
cd /c/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined/redesign/qp/A/sitl
export SCR=C:/Users/dillo/tools/ardupilot-sitl A_MOTOR=x2216
PY=$SCR/venv/Scripts/python.exe
LOG=../mechanism/out/T101_data/sitl_batch_C3G.log; : > $LOG
tag=T101C3G_T074
s=$(date +%s)
$PY run_fwd.py $tag inst=2 speedup=8 case=trans mass=1.881 wind=0 hold=25 cruise_s=8 r=1.33 fw_hold=1.0 P:TECS_SPDWEIGHT=0.5 c3g=1 gv_vert=3 gv_side=3 gv_dur=1.08 c3g_stick=0.75 > runs/$tag.out 2>&1
echo "$tag exit $? wall $(( $(date +%s)-s )) s" >> $LOG
$PY fwd_sum.py $tag >> $LOG 2>&1
echo ALLDONE >> $LOG
