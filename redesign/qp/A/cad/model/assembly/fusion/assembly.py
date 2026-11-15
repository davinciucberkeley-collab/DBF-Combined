import os, sys
CAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if CAD not in sys.path:
    sys.path.insert(0, CAD)
import a_model


def build(ctx):
    a_model.build_assembly(ctx)
