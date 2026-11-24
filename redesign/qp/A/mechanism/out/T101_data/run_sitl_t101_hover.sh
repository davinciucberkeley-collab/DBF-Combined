#!/bin/bash
# T-101 AM-061: windy hover at the D-255 flying CG 23.49 mm vs the as-drawn 22.049 mm. A-P8 basis: 4 m/s mean, gust to 6.4 m/s, edge-on heading (A-P8a),
# 1.881 kg, cant 17, sagged pack (thrust_scale 0.767 default), hold 45 s. Cases: steady 4 m/s, 4 m/s + 2.4 m/s gust at 20 s, 4 m/s + 1 m/s turbulence.
cd /c/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined/redesign/qp/A/sitl
export SCR=C:/Users/dillo/tools/ardupilot-sitl A_MOTOR=x2216
PY=$SCR/venv/Scripts/python.exe
LOG=../mechanism/out/T101_data/sitl_batch_HOVER.log; : > $LOG
B="mass=1.881 cant=17 from=90 wind=4 hold=45"
r(){ i=$1; tag=$2; shift 2; ( s=$(date +%s); $PY run_case.py $tag inst=$i $B "$@" > runs/$tag.out 2>&1; echo "$tag exit $? wall $(( $(date +%s)-s )) s" >> $LOG ) ; }
( r 0 T101H_st_22 cg=22.049; r 0 T101H_st_23 cg=23.49 ) &
( r 1 T101H_gu_22 cg=22.049 gust=2.4 gust_at=20; r 1 T101H_gu_23 cg=23.49 gust=2.4 gust_at=20 ) &
( r 3 T101H_tu_22 cg=22.049 turb=1.0; r 3 T101H_tu_23 cg=23.49 turb=1.0 ) &
wait; echo ALLDONE >> $LOG
