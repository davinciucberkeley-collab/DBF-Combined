#!/bin/bash
# T-083b gates (6061 root fitting FIN-003, cage T083_DX +3 mm), sequential (Blender gates share cad/out job files). Each line: name, exit, seconds.
A=C:/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined/redesign/qp/A
D=$A/mechanism/out/T083b_data/gates
mkdir -p $D
cd $A/cad
run() { n=$1; shift; s=$(date +%s); "$@" > $D/gate_$n.txt 2>&1; e=$?; echo "$n exit $e $(( $(date +%s)-s )) s" >> $D/gates_summary.txt; }
: > $D/gates_summary.txt
run build_a python -I build_a.py
run wire_inventory python -I wire_inventory.py
cd $A/sitl && run cad_mass python -I cad_mass.py
cd $A && run mission_gate python -I mission_gate_a.py --o4b
cd $A && run prop_sched python -I prop_a.py --sched --mass 1.873
cd $A && run proofs python -I proofs/run_all.py
cd $A/mechanism/out/T083_data && run bbox python -I t083_bbox.py
cd $A/cad && export A_ELEV_POSE=21 && run collide_pose21 python -I collide_a.py
unset A_ELEV_POSE
cd $A/cad && run collide_linkage python -I collide_a.py --linkage-poses
cd $A/cad && run assembly python -I a_assembly.py
cd $A/drawings && run drawings python -B make_drawings_a.py
cd $A && run build_guide python -I make_build_guide_a.py
cd $A/cad && run parts_links python -I parts_links_a.py
echo GATES_DONE >> $D/gates_summary.txt
