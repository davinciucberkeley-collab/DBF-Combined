#!/bin/bash
# T-076b step 2: variant V1 = C6 collar (12 mm, 24x24) with the bore floor kept at X_BR0 15.0 (web over tube B 2.5 mm instead of 1.0), bore L 21.0 mm, 0.8 mm tube-end / floor chamfer pair kept.
# Same tool, mesh settings, loads and p99 convention as the T-076 C6 run.  Expected ~30 min (mesh ~8, solve ~7, evaluation ~10; the T-076 C6 run took 55 min under CPU contention, the C6 re-solve here 14 min).
cd "$(dirname "$0")"
export LAND_MASS_KG=1.64
COMMON="S_END=60 SLV_W=1.5 MS=1.1 FIL=2.0 BR_CH=0.8"
s=$(date +%s); python -I t076b_run.py --tag t076bv1 --p $COMMON COL_E=12 X_BR0=15.0 X_HUB1=36 > fea_t076b_v1_stdout.txt 2> fea_t076b_v1.err; echo "v1 exit $? wall $(( $(date +%s)-s )) s" > fea_t076b_v1.time
