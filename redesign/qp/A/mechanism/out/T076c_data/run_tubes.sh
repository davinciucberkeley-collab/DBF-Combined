#!/bin/bash
cd "$(dirname "$0")"
s=$(date +%s); python -I t076c_tubes.py > tubes_stdout.txt 2> tubes.err; echo "tubes exit $? wall $(( $(date +%s)-s )) s" > tubes.time
