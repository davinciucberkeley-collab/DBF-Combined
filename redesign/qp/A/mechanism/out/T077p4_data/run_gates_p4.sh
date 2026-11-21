#!/bin/bash
# T-077 part 4 gates, sequential (Blender gates share cad/out job files). Each line: name, exit, seconds.
A=C:/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined/redesign/qp/A
D=$A/mechanism/out/T077p4_data/gates
mkdir -p $D
cd $A/cad
run() { n=$1; shift; s=$(date +%s); "$@" > $D/gate_$n.txt 2>&1; e=$?; echo "$n exit $e $(( $(date +%s)-s )) s" >> $D/gates_summary.txt; }
: > $D/gates_summary.txt
run build_a python -I build_a.py
export A_ELEV_POSE=21
run collide_pose21 python -I collide_a.py
unset A_ELEV_POSE
run wire_inventory python -I wire_inventory.py
cd $A/sitl && run cad_mass python -I cad_mass.py
cd $A && run mission_gate python -I mission_gate_a.py --o4b
cd $A/cad && run collide_linkage python -I collide_a.py --linkage-poses
cd $A/cad && run assembly python -I a_assembly.py
echo GATES3D_DONE >> $D/gates_summary.txt
