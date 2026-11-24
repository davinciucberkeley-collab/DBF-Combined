"""One-off patch applied to structures/fe_a.py for T-085 (kept for the record; the patched file is the deliverable)."""
import sys
p = sys.argv[1]
s = open(p).read()
s = s.replace("hub_extra_g=20.0, wing_cell=None, h_fin=None):", "hub_extra_g=20.0, wing_cell=None, h_fin=None, hub_se=None, pack_cfg=None):")
old = """    elif bridge_cfg == 'single+V':
        F.beam("hub", "s+0.000", E*A_b, E*I_b, E*I_b, G*2*I_b, RHO_CF*A_b, (0, 0, 1), "bridge", nseg=3)
"""
new = """    elif bridge_cfg == 'single+V':
        if hub_se is None:
            F.beam("hub", "s+0.000", E*A_b, E*I_b, E*I_b, G*2*I_b, RHO_CF*A_b, (0, 0, 1), "bridge", nseg=3)
        else:   # T-085: the bridge starts at the superelement's fixed-bore node 'bb' (hub FEA models the block and 40 mm of bridge); hub -> bb is inside the superelement
            pb = hub_se["pts_mm"]["bb"]; XH0 = X_HUB if x_hub is None else x_hub
            F.node("bb", (XH0+pb[0]*1e-3, pb[1]*1e-3, pb[2]*1e-3))
            F.beam("bb", "s+0.000", E*A_b, E*I_b, E*I_b, G*2*I_b, RHO_CF*A_b, (0, 0, 1), "bridge", nseg=3)
            F.lump("bb", 0.5*RHO_CF*A_b*pb[0]*1e-3); F.lump("hub", 0.5*RHO_CF*A_b*pb[0]*1e-3)     # the bridge length hub -> bb as lumps
"""
assert old in s; s = s.replace(old, new)
old = """    F.lump("hub", pack_g*1e-3+hub_extra_g*1e-3)              # pack + hub print 20 g
"""
new = """    if pack_cfg is None:
        F.lump("hub", pack_g*1e-3+hub_extra_g*1e-3)              # pack + hub print 20 g
    else:                                                          # T-085: pack on the drawn tray (see add_pack); hub_extra_g stays on the hub node
        F.lump("hub", hub_extra_g*1e-3); add_pack(F, XH_ if x_hub is not None else X_M, kind, pack_g, pack_cfg)
"""
assert old in s; s = s.replace(old, new)
old = """            F.beam("hub", nm, E*A_a, E*I_a, E*I_a, G*2*I_a, RHO_CF*A_a, (1, 0, 0), "arm", nseg=5)
            F.lump(nm, motor_g*1e-3)
"""
new = """            if hub_se is None:
                F.beam("hub", nm, E*A_a, E*I_a, E*I_a, G*2*I_a, RHO_CF*A_a, (1, 0, 0), "arm", nseg=5)
            else:   # T-085: the arm starts at the stub end of the hub FEA (s = S_END along the tube); the stub (tube, sleeve, block) is in the superelement
                st = {(1, 1): "UR", (-1, -1): "LL", (1, -1): "LR", (-1, 1): "UL"}[(sy, sz)]; pe = hub_se["pts_mm"][st]; XH0 = X_HUB if x_hub is None else x_hub
                F.node("h_"+st, (XH0+pe[0]*1e-3, pe[1]*1e-3, pe[2]*1e-3))
                F.beam("h_"+st, nm, E*A_a, E*I_a, E*I_a, G*2*I_a, RHO_CF*A_a, (1, 0, 0), "arm", nseg=5)
                F.lump("h_"+st, RHO_CF*A_a*hub_se["s_end_mm"]*1e-3)                # the stub tube mass (hub centre -> stub end) as a lump
            F.lump(nm, motor_g*1e-3)
"""
assert old in s; s = s.replace(old, new)
old = """    # --- fins: rib (PETG box)"""
new = """    if hub_se is not None:
        F.superelement(["h_UR", "h_LL", "h_LR", "h_UL", "hub", "bb"], hub_se["K"], "hubjoint")
    # --- fins: rib (PETG box)"""
assert old in s; s = s.replace(old, new, 1)
helpers = open(sys.argv[2]).read()
s = s.replace("def build(kind=", helpers + "\n\ndef build(kind=", 1)
open(p, 'w').write(s)
