#!/bin/bash
# T-101 SITL reruns: identical T097 setup (1.883 kg EST (chord 0.30, T-101 U4), X2216, same cases / Lua / battery monitor) except the candidate change in $EXTRA.
# usage: run_sitl_t101.sh <candidate tag, e.g. C1> "<extra run_fwd args>"   4 instances in parallel
CAND=$1; EXTRA=$2
cd /c/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined/redesign/qp/A/sitl
export SCR=C:/Users/dillo/tools/ardupilot-sitl A_MOTOR=x2216
PY=$SCR/venv/Scripts/python.exe
LOG=../mechanism/out/T101_data/chord/sitl_batch_$CAND.log; : > $LOG
LUA="P:SCR_ENABLE=1 P:BATT_MONITOR=4 P:BATT_VOLT_MULT=10.1 P:BATT_AMP_PERVLT=17 P:SIM_BATT_VOLTAGE=14.92 P:BATT_ARM_VOLT=0 P:Q_M_BAT_VOLT_MAX=0 P:Q_M_BAT_VOLT_MIN=0"
for t in T101${CAND}_Z5_lua T101${CAND}_T074_lua; do mkdir -p runs/$t/scripts; cp lua/spin_cap.lua runs/$t/scripts/; done
j(){ tag=$1; inst=$2; shift 2; ( s=$(date +%s); $PY run_fwd.py $tag inst=$inst speedup=8 "$@" > runs/$tag.out 2>&1; echo "$tag exit $? wall $(( $(date +%s)-s )) s" >> $LOG ) & }
j T101${CAND}_Z5 0 case=trans mass=1.883 wind=0 from=0 chain=1 hold=30 cruise_s=15 P:THR_MAX=80 P:Q_WVANE_ENABLE=0 $EXTRA
j T101${CAND}_Z5_lua 1 case=trans mass=1.883 wind=0 from=0 chain=1 hold=30 cruise_s=15 P:THR_MAX=80 P:Q_WVANE_ENABLE=0 $LUA $EXTRA
j T101${CAND}_T074 2 case=trans mass=1.883 wind=0 hold=25 cruise_s=8 r=1.33 $EXTRA
j T101${CAND}_T074_lua 3 case=trans mass=1.883 wind=0 hold=25 cruise_s=8 r=1.33 $LUA $EXTRA
wait; echo ALLDONE >> $LOG
