#!/bin/bash
# T-076c step 4, H-A1: aluminium hub, C6 envelope, bore floor X_BR0 15.0, collar to x 45 (bonded L 30), tube end released 0.5 mm (BR_GAP).  Expected 35-60 min (mesh ~8, solve ~8, judge + evaluate ~20-40).
cd "$(dirname "$0")"
export LAND_MASS_KG=1.64
s=$(date +%s); python -I t076c_ha.py --tag t076cha1 --p S_END=60 SLV_W=1.5 MS=1.1 FIL=2.0 BR_CH=0.8 COL_E=21 X_BR0=15.0 X_HUB1=45 BR_GAP=0.5 > ha1_stdout.txt 2> ha1.err; echo "ha1 exit $? wall $(( $(date +%s)-s )) s" > ha1.time
