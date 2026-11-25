#!/bin/bash
# T-076b step 3, batch 2 (3 SITL instances in parallel, ~130 s): isolate the pitch use 0.61-0.63 (T074 0.44).
cd /c/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined/redesign/qp/A/sitl
export SCR=C:/Users/dillo/tools/ardupilot-sitl
PY=$SCR/venv/Scripts/python.exe
DATA=../mechanism/out/T076_data
( s=$(date +%s); $PY run_fwd.py T076b_r4_mon_c0_v0 inst=0 case=trans mass=1.64 wind=0 hold=25 cruise_s=8 r=1.33 P:Q_M_SPIN_MAX=1.0 P:BATT_MONITOR=4 P:BATT_VOLT_MULT=10.1 P:BATT_AMP_PERVLT=17 P:SIM_BATT_VOLTAGE=14.92 P:BATT_ARM_VOLT=0 P:Q_M_BAT_VOLT_MAX=0 P:Q_M_BAT_VOLT_MIN=0 P:Q_M_BAT_CURR_MAX=0 > runs/T076b_r4_mon_c0_v0.out 2>&1; echo "r4 exit $? wall $(( $(date +%s)-s )) s" >> $DATA/s4b_batch2.log ) &
( s=$(date +%s); $PY run_fwd.py T076b_r5_mon_c41_v0_rep inst=1 case=trans mass=1.64 wind=0 hold=25 cruise_s=8 r=1.33 P:Q_M_SPIN_MAX=1.0 P:BATT_MONITOR=4 P:BATT_VOLT_MULT=10.1 P:BATT_AMP_PERVLT=17 P:SIM_BATT_VOLTAGE=14.92 P:BATT_ARM_VOLT=0 P:Q_M_BAT_VOLT_MAX=0 P:Q_M_BAT_VOLT_MIN=0 > runs/T076b_r5_mon_c41_v0_rep.out 2>&1; echo "r5 exit $? wall $(( $(date +%s)-s )) s" >> $DATA/s4b_batch2.log ) &
( s=$(date +%s); $PY run_fwd.py T076b_r6_mon_c41_v0_lowV inst=2 case=trans mass=1.64 wind=0 hold=25 cruise_s=8 r=1.33 P:Q_M_SPIN_MAX=1.0 P:BATT_MONITOR=4 P:BATT_VOLT_MULT=10.1 P:BATT_AMP_PERVLT=17 P:SIM_BATT_VOLTAGE=16.2 P:BATT_ARM_VOLT=0 P:Q_M_BAT_VOLT_MAX=0 P:Q_M_BAT_VOLT_MIN=0 > runs/T076b_r6_mon_c41_v0_lowV.out 2>&1; echo "r6 exit $? wall $(( $(date +%s)-s )) s" >> $DATA/s4b_batch2.log ) &
wait
echo ALLDONE >> $DATA/s4b_batch2.log
