"""CDR-19: 3-D gain of each station-mode lever on the governing (lower) quarter, mesh level 2, one lever at a time.
python -I lever_table.py <name>   -> prints the first station mode; names: base brace3 light10 grip13 grip15 tubeEG
Results are collected by lever_collect() in sim_fin.py from the cache (same keys)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sim_fin as S  # noqa: E402

name = sys.argv[1]
r = S.lever_case(name)
st = [f for f, ke, kind in r["modes"] if ke >= 0.10]
print("LEVER", name, round(st[0], 2), flush=True)
