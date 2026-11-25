#!/bin/bash
# T-083 gates run 3: clamp socket slot 1.0 -> 1.5 mm clear (assembly run 2: B1 0.095 mm). Run-2 outputs of the re-run gates kept in gates/run2/.
A=C:/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined/redesign/qp/A
D=$A/mechanism/out/T083_data/gates
mkdir -p $D/run2
for g in build_a collide_pose21 assembly drawings build_guide; do [ -f $D/gate_$g.txt ] && mv $D/gate_$g.txt $D/run2/; done
run() { n=$1; shift; s=$(date +%s); "$@" > $D/gate_$n.txt 2>&1; e=$?; echo "$n exit $e $(( $(date +%s)-s )) s (run 3)" >> $D/gates_summary.txt; }
cd $A/cad && run build_a python -I build_a.py
cd $A/cad && export A_ELEV_POSE=21 && run collide_pose21 python -I collide_a.py
unset A_ELEV_POSE
cd $A/cad && run assembly python -I a_assembly.py
cd $A/drawings && run drawings python -B make_drawings_a.py
cd $A && run build_guide python -I make_build_guide_a.py
echo GATES_DONE_R3 >> $D/gates_summary.txt
