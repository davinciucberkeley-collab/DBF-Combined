#!/bin/bash
# T-083 gates run 2, after two fixes found by run 1 (raceway window +0.4 mm aft; clamp socket slot 1.0 mm clear; B0j strut axis for the 15 mm shift).
# Run-1 outputs of the re-run gates are kept in gates/run1/.
A=C:/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined/redesign/qp/A
D=$A/mechanism/out/T083_data/gates
mkdir -p $D/run1
for g in build_a collide_pose21 collide_linkage assembly wire_inventory cad_mass drawings build_guide parts_links; do [ -f $D/gate_$g.txt ] && mv $D/gate_$g.txt $D/run1/; done
cp $D/gates_summary.txt $D/run1/gates_summary_run1.txt
run() { n=$1; shift; s=$(date +%s); "$@" > $D/gate_$n.txt 2>&1; e=$?; echo "$n exit $e $(( $(date +%s)-s )) s (run 2)" >> $D/gates_summary.txt; }
cd $A/cad && run build_a python -I build_a.py
cd $A/cad && run wire_inventory python -I wire_inventory.py
cd $A/sitl && run cad_mass python -I cad_mass.py
cd $A/cad && export A_ELEV_POSE=21 && run collide_pose21 python -I collide_a.py
unset A_ELEV_POSE
cd $A/cad && run collide_linkage python -I collide_a.py --linkage-poses
cd $A/cad && run assembly python -I a_assembly.py
cd $A/drawings && run drawings python -B make_drawings_a.py
cd $A && run build_guide python -I make_build_guide_a.py
cd $A/cad && run parts_links python -I parts_links_a.py
echo GATES_DONE_R2 >> $D/gates_summary.txt
