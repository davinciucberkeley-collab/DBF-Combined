#!/bin/bash
cd "$(dirname "$0")"
python -I t077p5_step4.py --tag f4m05nofms14 --geom G1 --p MS=1.4 RC_R=9.25 RC_X0=15.5 SH_R=4.0 MO_R=0.5 MO_FMS=0 > step4_f4m05nofms14_stdout.txt 2> step4_f4m05nofms14.err
python -I t077p5_step4.py --tag f4only14 --geom G1 --p MS=1.4 RC_R=9.25 RC_X0=15.5 SH_R=4.0 MO_R=0 > step4_f4only14_stdout.txt 2> step4_f4only14.err
echo DIAG_DONE > diag_done.txt
