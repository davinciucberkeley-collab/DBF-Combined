#!/bin/bash
# T-076d step 4 FE jobs, sequential (the MATLAB chol of one MS 1.1 mesh needs about 19 GB; MS 0.8 would need about 69 GB > 64 GB RAM, so the refinement is MS 0.9)
cd "$(dirname "$0")"
for job in "g0ms11 G0" "g1ms11 G1" "g1ms09 G1 MS=0.9"; do
  set -- $job; tag=$1; geom=$2; shift 2
  s=$(date +%s)
  if [ -n "$1" ]; then python -I t076d_step4_tubes.py --tag $tag --geom $geom --p "$@" > step4_${tag}_stdout.txt 2> step4_${tag}.err; else python -I t076d_step4_tubes.py --tag $tag --geom $geom > step4_${tag}_stdout.txt 2> step4_${tag}.err; fi
  echo "$tag exit $? wall $(( $(date +%s)-s )) s" >> step4.time
done
