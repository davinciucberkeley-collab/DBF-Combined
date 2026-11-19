#!/bin/bash
# T-074 check 3 step 2: C3-equivalent SITL transition runs (sitl/run_fwd.py, case=trans, same procedure as the S_ series of SITL-FLIGHT.md s2).
# Scheduled cap modelled as a constant Q_M_SPIN_MAX = cap(V_rest) for the V_rest of the run (14.92 V sag state: cap = 1.000); no Lua in the loop.
# usage: SCR=C:/Users/dillo/tools/ardupilot-sitl bash run_c3.sh   (reads jobs from run_c3_jobs.txt: "<tag> <extra args>", 3 in parallel by instance number)
cd /c/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined/redesign/qp/A/sitl
export SCR=${SCR:-C:/Users/dillo/tools/ardupilot-sitl}
JOBS=$(cd .. && pwd)/mechanism/out/T074_data/run_c3_jobs.txt
LOG=$(cd .. && pwd)/mechanism/out/T074_data/run_c3.log
NP=${NP:-3}; i=0
while read -r tag rest; do
  [ -z "$tag" ] && continue
  inst=$((i % NP)); i=$((i+1))
  ( s=$(date +%s); timeout 1200 $SCR/venv/Scripts/python.exe run_fwd.py $tag inst=$inst $rest > runs/$tag.out 2>&1; echo "$tag exit $? wall $(( $(date +%s)-s )) s :: $rest" >> $LOG ) &
  if [ $((i % NP)) -eq 0 ]; then wait; fi
done < $JOBS
wait; echo ALLDONE >> $LOG
