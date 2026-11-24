#!/bin/bash
# AM-062 / D-258: A-P8 hover-wind cases for the O4b aircraft. Same seven cases as D-195 (batch_qp5.sh: 4 m/s mean, 1 m/s turbulence, arm 1.2, cant 17, hold 45 s,
# wind from 60-90 deg, seeds 1-3) at 1.881 kg, flying CG 23.49 mm (D-255), X2216 hover thrust model (x2216_hover=1, A_MOTOR=x2216) on the worst pack (vrest 14.92 V,
# derate 0.93, hot 0.97). Plus the belly-on lean case (5 m/s from 0, turbulence 1 m/s) for CL-A-WIND-LEAN.
cd /c/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined/redesign/qp/A/sitl
export SCR=C:/Users/dillo/tools/ardupilot-sitl A_MOTOR=x2216
PY=$SCR/venv/Scripts/python.exe
LOG=../mechanism/out/T101_data/sitl_batch_AP8.log; : > $LOG
run() { i=$1; tag=$2; shift 2; s=$(date +%s); timeout 900 $PY run_case.py $tag inst=$i hold=45 arm=1.2 cant=17 mass=1.881 cg=23.49 x2216_hover=1 vrest=14.92 "$@" > runs/$tag.out 2>&1; echo "$tag exit $? wall $(( $(date +%s)-s )) s" >> $LOG; }
run 0 AP8_h60 turb=1.0 wind=4 from=60 & run 1 AP8_h60s2 turb=1.0 wind=4 from=60 seed=2 & run 2 AP8_h60s3 turb=1.0 wind=4 from=60 seed=3 & run 3 AP8_h70 turb=1.0 wind=4 from=70 &
wait
run 0 AP8_h90 turb=1.0 wind=4 from=90 & run 1 AP8_h70s2 turb=1.0 wind=4 from=70 seed=2 & run 2 AP8_h80 turb=1.0 wind=4 from=80 & run 3 AP8_belly5 turb=1.0 wind=5 from=0 &
wait; echo ALLDONE >> $LOG
