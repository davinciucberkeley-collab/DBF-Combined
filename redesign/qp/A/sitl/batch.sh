#!/bin/bash
# Sequential A hover cases. usage: SCR=<scratch> bash batch.sh
cd "$(dirname "$0")"
PY="$SCR/venv/Scripts/python"
run() { tag=$1; shift; timeout 420 "$PY" run_case.py "$tag" "$@" > "runs/$tag.out" 2>&1; echo "$tag done $(date +%T)"; }
mkdir -p runs
run w0 wind=0 hold=40
run b3 wind=3 from=0 hold=40
run b7 wind=7 from=0 hold=40
run e3 wind=3 from=90 hold=40
run e5 wind=5 from=90 hold=40
run e7 wind=7 from=90 hold=40
run d3 wind=3 from=45 hold=40
run d5 wind=5 from=45 hold=40
run d7 wind=7 from=45 hold=40
run gb wind=5 gust=2 from=0 hold=45 gust_at=20
run ge wind=5 gust=2 from=90 hold=45 gust_at=20
run tb wind=5 turb=1.0 from=0 hold=45
run m137b wind=5 from=0 mass=1.37 hold=40
run m137e wind=5 from=90 mass=1.37 hold=40
echo ALL DONE
