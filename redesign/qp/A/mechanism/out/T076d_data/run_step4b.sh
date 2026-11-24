#!/bin/bash
# T-076d step 4 convergence pair: MS 1.4 (coarse) against the MS 1.1 run (MS 0.9 does not fit: see step4.time)
cd "$(dirname "$0")"
s=$(date +%s); python -I t076d_step4_tubes.py --tag g1ms14 --geom G1 --p MS=1.4 > step4_g1ms14_stdout.txt 2> step4_g1ms14.err; echo "g1ms14 exit $? wall $(( $(date +%s)-s )) s" >> step4.time
