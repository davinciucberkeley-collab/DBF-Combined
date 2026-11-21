#!/bin/bash
A=C:/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined/redesign/qp/A
D=$A/mechanism/out/T077p4_data/gates
cd $A/cad
s=$(date +%s); python -I a_assembly.py > $D/gate_assembly.txt 2>&1; e=$?
echo "assembly(rerun after strut direction fix) exit $e $(( $(date +%s)-s )) s" >> $D/gates_summary.txt
echo ASSEMBLY_RERUN_DONE >> $D/gates_summary.txt
