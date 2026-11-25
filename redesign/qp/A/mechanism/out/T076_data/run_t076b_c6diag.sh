#!/bin/bash
# T-076b step 1: C6 re-solve (cached mesh t076c6b) with the hot-spot location analysis; caches the 301 landing combos for the next run.  Expected ~40 min.
cd "$(dirname "$0")"
export LAND_MASS_KG=1.64
COMMON="S_END=60 SLV_W=1.5 MS=1.1 FIL=2.0 BR_CH=0.8"
s=$(date +%s); python -I t076b_run.py --tag t076c6b --p $COMMON COL_E=12 X_BR0=13.5 X_HUB1=36 > fea_t076b_c6diag_stdout.txt 2> fea_t076b_c6diag.err; echo "c6diag exit $? wall $(( $(date +%s)-s )) s" > fea_t076b_c6diag.time
