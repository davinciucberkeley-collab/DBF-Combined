cd /c/Users/dillo/Downloads/Berkeley/Fall/Capstone/DBF-Combined
L=docs/audits/2026-11-24-T101-revert-logs
A_ELEV_POSE=21 python -I redesign/qp/A/cad/collide_a.py > $L/G1_collide_a.txt 2>&1; echo $? > $L/G1_rc.txt
python -I redesign/qp/A/cad/a_assembly.py > $L/G3_a_assembly.txt 2>&1; echo $? > $L/G3_rc.txt
echo done > $L/_chain_done.txt
