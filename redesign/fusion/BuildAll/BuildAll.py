"""Fusion launcher for redesign/fusion/build_all.py.

Add THIS folder (redesign/fusion/BuildAll) in Utilities > Add-Ins > Scripts and Add-Ins, then Run.
It finds the repo from its own location, so no path needs editing. Each run starts a new design document.
Fusion keeps imported modules between runs; they are dropped first so edits to modules are picked up.
"""
import os
import sys
import traceback

FUSION_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))     # redesign/fusion
OURS = ('build_all', 'fusionkit', 'k09kit', 'merge_check', 'backends')


def run(context):
    import adsk.core
    ui = adsk.core.Application.get().userInterface
    try:
        if FUSION_DIR not in sys.path:
            sys.path.insert(0, FUSION_DIR)
        for name in list(sys.modules):
            if name.split('.')[0] in OURS or name.startswith('dbfmod_'):
                del sys.modules[name]
        import build_all
        text = build_all.fusion_main()
        ui.messageBox(text[:3000] + ('\n... (full text in the TEXT COMMANDS window)' if len(text) > 3000 else ''),
                      'DBF build_all')
    except Exception:
        ui.messageBox('build_all failed:\n' + traceback.format_exc(), 'DBF build_all')
