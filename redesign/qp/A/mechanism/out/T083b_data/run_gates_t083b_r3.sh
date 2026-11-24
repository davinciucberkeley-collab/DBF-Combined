#!/bin/bash
# T-083b run 3: collide pose 21 and the linkage poses again, ALONE (in run 2 a leftover run-1 a_assembly.py shared cad/out/_job.json with them), then proofs after assembly.json exists.
A=C:/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined/redesign/qp/A
D=$A/mechanism/out/T083b_data/gates
run() { n=$1; shift; s=$(date +%s); "$@" > $D/gate_$n.txt 2>&1; e=$?; echo "$n exit $e $(( $(date +%s)-s )) s (run 3)" >> $D/gates_summary.txt; }
cd $A && run proofs python -I proofs/run_all.py
cd $A/cad && export A_ELEV_POSE=21 && run collide_pose21 python -I collide_a.py
unset A_ELEV_POSE
cd $A/cad && run collide_linkage python -I collide_a.py --linkage-poses
echo GATES_R3_DONE >> $D/gates_summary.txt
