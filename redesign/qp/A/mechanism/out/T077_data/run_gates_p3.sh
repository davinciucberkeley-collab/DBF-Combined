#!/bin/bash
# T-077 part 3 gates, sequential (Blender gates share cad/out job files). Each line: name, exit, seconds.
A=C:/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined/redesign/qp/A
D=$A/mechanism/out/T077_data
cd $A/cad
run() { n=$1; shift; s=$(date +%s); "$@" > $D/p3_gate_$n.txt 2>&1; e=$?; echo "$n exit $e $(( $(date +%s)-s )) s" >> $D/p3_gates_summary.txt; }
: > $D/p3_gates_summary.txt
run build_a python -I build_a.py
export A_ELEV_POSE=21
run collide_pose21 python -I collide_a.py
unset A_ELEV_POSE
run wire_inventory python -I wire_inventory.py
cd $A/sitl && run cad_mass python -I cad_mass.py
cd $A && run mission_gate python -I mission_gate_a.py --o4b
cd $A/cad && run collide_linkage python -I collide_a.py --linkage-poses
cd $A/cad && run assembly python -I a_assembly.py
cd $A/proofs && run proofs_run_all python -I run_all.py
cd $A/drawings && run drawings python -I make_drawings_a.py
echo DONE >> $D/p3_gates_summary.txt
