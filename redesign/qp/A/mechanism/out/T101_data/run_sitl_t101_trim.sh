#!/bin/bash
# T-101 D-253 (AM-053): cruise-trim cut variants of C3 (T-074 case, no events) and C3G (pitch peak + 3 m/s vertical and side 1-cos gusts + roll doublet).
# T1 = pack at the aft end of its tray slot (CG 22.05 -> 23.49 mm) + AIRSPEED_CRUISE 18; T2 = section Cm0 +0.021 (E 186-class reflex, XFOIL delta +0.013); T3 = Cm0 +0.036 (zero plant trim, E 230-class).
# one instance at a time (inst 2); usage: run_sitl_t101_trim.sh
cd /c/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined/redesign/qp/A/sitl
export SCR=C:/Users/dillo/tools/ardupilot-sitl A_MOTOR=x2216
PY=$SCR/venv/Scripts/python.exe
LOG=../mechanism/out/T101_data/sitl_batch_TRIM.log; : > $LOG
BASE="inst=2 speedup=8 case=trans mass=1.881 wind=0 hold=25 cruise_s=8 r=1.33 fw_hold=1.0 P:TECS_SPDWEIGHT=0.5"
G="c3g=1 gv_vert=3 gv_side=3 gv_dur=1.08 c3g_stick=0.75"
declare -A V=( [T1]="cg=23.49 P:AIRSPEED_CRUISE=18" [T2]="cm0=0.021" [T3]="cm0=0.036" )
for k in T1 T2 T3; do
  for g in "" G; do
    tag=T101${k}${g}_T074; s=$(date +%s)
    extra=""; [ "$g" = G ] && extra="$G"
    $PY run_fwd.py $tag $BASE ${V[$k]} $extra > runs/$tag.out 2>&1
    echo "$tag exit $? wall $(( $(date +%s)-s )) s" >> $LOG
    $PY fwd_sum.py $tag >> $LOG 2>&1
  done
done
echo ALLDONE >> $LOG
