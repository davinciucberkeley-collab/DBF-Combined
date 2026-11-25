#!/bin/bash
# T-076 row 1: C6 hub (T-071b H3) FEA, then the base-hub control with the same loads.  Sequential (direct solve ~15-25 GB each).
cd "$(dirname "$0")"
COMMON="--level 0 --land land164/demand_series.npz --p S_END=60 SLV_W=1.5 MS=1.1 FIL=2.0 BR_CH=0.8"
s=$(date +%s); python -I fea_hub_c6.py --tag t076c6 $COMMON COL_E=12 X_BR0=13.5 X_HUB1=36 > fea_c6_stdout.txt 2> fea_c6.err; echo "c6 exit $? wall $(( $(date +%s)-s )) s" > fea_c6.time
s=$(date +%s); python -I fea_hub_c6.py --tag t076base $COMMON > fea_base_stdout.txt 2> fea_base.err; echo "base exit $? wall $(( $(date +%s)-s )) s" > fea_base.time
