#!/bin/bash
# T-074 check 3 step 3: F-5 landing re-runs at the predicted mass.  usage: bash run_s3.sh <mass kg> <cg x mm or default> <tag>
cd "$(dirname "$0")/../../../structures"
D=$(cd ../mechanism/out/T074_data && pwd)

M=$1; CG=$2; TAG=$3
export LAND_MASS_KG=$M
[ "$CG" != "default" ] && export LAND_CG_X_MM=$CG
export LAND_OUT_DIR=$D/centre_cache_$TAG; mkdir -p $LAND_OUT_DIR
run() { n=$1; shift; s=$(date +%s); python -I "$@" > $D/s3_${n}_$TAG.txt 2> $D/s3_${n}_$TAG.err; echo "$n: python -I $* exit $? wall $(( $(date +%s)-s )) s" >> $D/s3_$TAG.times; }
rm -f $D/s3_$TAG.times
run centre landing_centre_a.py --recompute
run centre_cached landing_centre_a.py
run side landing_side_a.py
run tip landing_tip_b.py
run nodes landing_nodes_b.py
echo DONE >> $D/s3_$TAG.times
