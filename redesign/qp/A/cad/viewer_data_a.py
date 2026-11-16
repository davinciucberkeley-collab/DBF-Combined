"""viewer_data_a.py - viewer data for concept A (reuses redesign/viewer/build_data.py unchanged for K09-L).
    python -I redesign/qp/A/cad/viewer_data_a.py --glb DIR_WITH_assembly.glb --interfaces merged_interfaces.json --out redesign/site/data
Merged interfaces: python -I redesign/interfaces/merge_check.py --root redesign/qp/A/cad/model --out SOME_DIR
Mass budget: qp/A/cad/model/mass_budget.json. Claims: qp/A/proofs/out/graph.json (build it first:
python -I redesign/qp/A/proofs/run_all.py); a claim's `parts` ids (CAD part ids) become the part panel's "Claims about this part". No cost/vendor: BOM-A.csv ids (P01, W01 ...) are
purchase lines, not CAD part ids (WNG-001 ...), so there is no mapping; the inspector shows no cost for A."""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
RED = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(RED, 'viewer'))
import build_data  # noqa: E402
import subprocess  # noqa: E402
subprocess.run([sys.executable, '-I', os.path.join(HERE, 'parts_links_a.py')], check=True)   # CAD part -> BOM line / build clip (Vendor / file)

sys.argv[1:1] = ['--budget', os.path.join(HERE, 'model', 'mass_budget.json'), '--proofs', os.path.join(os.path.dirname(HERE), 'proofs', 'out', 'graph.json'),
                 '--csv', os.path.join(HERE, 'out', 'parts-a.csv'), '--no-spec', '--dataset', 'concept-a']
sys.exit(build_data.main())
