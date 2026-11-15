"""viewer_data_a.py - viewer data for concept A (reuses redesign/viewer/build_data.py unchanged for K09-L).
    python -I redesign/qp/A/cad/viewer_data_a.py --glb DIR_WITH_assembly.glb --interfaces merged_interfaces.json --out redesign/site/data
Merged interfaces: python -I redesign/interfaces/merge_check.py --root redesign/qp/A/cad/model --out SOME_DIR
Mass budget: qp/A/cad/model/mass_budget.json. No claims graph for A. No cost/vendor: BOM-A.csv ids (P01, W01 ...) are
purchase lines, not CAD part ids (WNG-001 ...), so there is no mapping; the inspector shows no cost for A."""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
RED = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(RED, 'viewer'))
import build_data  # noqa: E402

sys.argv[1:1] = ['--budget', os.path.join(HERE, 'model', 'mass_budget.json'), '--proofs', os.path.join(HERE, 'out', 'none.json'),
                 '--csv', os.path.join(HERE, 'out', 'no-parts.csv'), '--no-spec', '--dataset', 'concept-a']
sys.exit(build_data.main())
