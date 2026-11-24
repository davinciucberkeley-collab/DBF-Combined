#!/bin/bash
# T-076 row 1 (second pass): landing demand with the A (all through arms) and B (arm group through the stub ends, hub+pack group through the hub aft face) load partitions.
# Standard flight / strike cases for C6 were run in the first pass (fea_c6_stdout.txt); the base-hub standard cases are the committed D-209 file.  Sequential.
cd "$(dirname "$0")"
export LAND_MASS_KG=1.64
COMMON="--level 0 --skip-std --p S_END=60 SLV_W=1.5 MS=1.1 FIL=2.0 BR_CH=0.8"
s=$(date +%s); python -I fea_hub_c6.py --tag t076c6b $COMMON COL_E=12 X_BR0=13.5 X_HUB1=36 > fea_c6b_stdout.txt 2> fea_c6b.err; echo "c6b exit $? wall $(( $(date +%s)-s )) s" > fea_c6b.time
s=$(date +%s); python -I fea_hub_c6.py --tag t076baseb $COMMON > fea_baseb_stdout.txt 2> fea_baseb.err; echo "baseb exit $? wall $(( $(date +%s)-s )) s" > fea_baseb.time
