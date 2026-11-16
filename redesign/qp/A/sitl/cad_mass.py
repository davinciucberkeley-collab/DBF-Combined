"""cad_mass.py - mass properties of the AS-DRAWN aircraft from the CAD (QP-4 7.2 #2): CG, inertias about the CG, prop plane, elevon hinge inertia.
    python -I redesign/qp/A/sitl/cad_mass.py        -> cad_mass.json (read by a_plant.py)
Method: every part at its CAD volume centroid (declared lumps at their declared CG) as a point mass, plus the own inertia of the long parts
(wing core plate, spar, fin tubes and fairings, arms, bridge, elevons). Body axes of the plant: x forward (= -x_cad), y right, z down (= -z_cad);
the products of inertia (Ixz from the 6.6 mm CG height) are dropped, as in the plant. Masses are the CAD declared masses (basic, no growth).
Labels: EST except where the CAD part table cites a source."""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.join(HERE, "..", "cad")
sys.path.insert(0, CAD)
import build_a as b          # noqa: E402
import a_model as m          # noqa: E402

cg = b.centroids()
items = []
for pid, p in m.PARTS.items():
    c = cg.get(pid) or p.get("cg")
    items.append((pid, p["mass_g"] / 1000.0, c))
M = sum(i[1] for i in items)
X = [sum(i[1] * i[2][k] for i in items) / M for k in range(3)]
I = [0.0, 0.0, 0.0]                      # about the CG, CAD axes (x aft, y right, z up): diagonal terms only
for pid, mass, c in items:
    dx, dy, dz = c[0] - X[0], c[1] - X[1], c[2] - X[2]
    I[0] += mass * (dy * dy + dz * dz); I[1] += mass * (dx * dx + dz * dz); I[2] += mass * (dx * dx + dy * dy)
mass_of = lambda pid: m.PARTS[pid]["mass_g"] / 1000.0
# own inertias
mw = mass_of("WNG-001"); I[0] += mw * m.B ** 2 / 12; I[1] += mw * m.C ** 2 / 12; I[2] += mw * (m.B ** 2 + m.C ** 2) / 12
ms = mass_of("WNG-002"); I[0] += ms * 0.9 ** 2 / 12; I[2] += ms * 0.9 ** 2 / 12
for s in "RL":
    mt = mass_of("FIN-001-" + s); L = 2 * m.FIN_H; I[0] += mt * L * L / 12; I[1] += mt * L * L / 12
    mf = mass_of("FIN-004-" + s); h = 2 * m.FIN_H; cw = m.XFIN_T - m.XH
    I[0] += mf * h * h / 12; I[1] += mf * (cw * cw + h * h) / 12; I[2] += mf * cw * cw / 12
for st in m.ST:
    ma = mass_of("CGE-002-" + st); L = 0.245; uy, uz = m.ST[st][0] * m.YM / m.R_M, m.ST[st][1] * m.ZM / m.R_M
    k = ma * L * L / 12; I[0] += k; I[1] += k * (1 - uy * uy); I[2] += k * (1 - uz * uz)
mb = mass_of("CGE-004"); I[1] += mb * 0.154 ** 2 / 12; I[2] += mb * 0.154 ** 2 / 12
for s in "RL":
    me = mass_of("WNG-006-" + s); ce = m.C - m.XH; span = m.ELEV_Y1 - m.ELEV_Y0
    I[0] += me * span * span / 12; I[1] += me * ce * ce / 12; I[2] += me * (span * span + ce * ce) / 12
# prop plane: hub of the prop (motor frame x -0.0475 from the station along the motor axis)
hub = m.mworld("UR", (-0.0475, 0.0, 0.0))
# elevon hinge inertia (one elevon, about the hinge axis): foam + tape 8.5 g plate (ce wide), balance horn + lead
ce = m.C - m.XH
Ih_elevon = mass_of("WNG-006-R") * ce * ce / 3
lead_kg = 0.0156                            # QP-4 FIXES D-187 v2: lead strip 15.6 g, 20 mm ahead of the hinge; 2 tabs 0.5 g (11 mm), 2 caps 1.0 g sit on the wing, not the elevon
vx, vz = m.BAL_REACH, m.HINGE_Z - (m.HINGE_Z + m.BAL_DZ)
Ih_bal = 0.0005 * 0.011 ** 2 + lead_kg * (vx * vx + vz * vz)
# elevon CG offset from the hinge (+ aft) with and without the balance
xe = 0.35 * ce
mb_ = lead_kg + 0.0005
cg_off_unbal = xe
cg_off_bal = (mass_of("WNG-006-R") * xe - lead_kg * m.BAL_REACH - 0.0005 * 0.011) / (mass_of("WNG-006-R") + mb_)
out = dict(mass_basic_kg=M, cg_x_m=X[0], cg_y_m=X[1], cg_z_m=X[2],
           I_cad_axes_kgm2=dict(Ixx=I[0], Iyy=I[1], Izz=I[2]),
           prop_hub_x_aft_of_LE_m=hub[0], motor_station_y=m.YM, motor_station_z=m.ZM, x_ground_m=m.X_GROUND, fin_y_m=m.YFIN, fin_h_m=m.FIN_H,
           elevon=dict(hinge_inertia_one_elevon_kgm2=Ih_elevon, hinge_inertia_balance_one_kgm2=Ih_bal, hinge_inertia_total_kgm2=Ih_elevon + Ih_bal,
                       cg_aft_of_hinge_unbalanced_m=cg_off_unbal, cg_aft_of_hinge_balanced_m=cg_off_bal, y0=m.ELEV_Y0, y1=m.ELEV_Y1, lim_deg=m.ELEV_LIM,
                       balance_mass_each_g=m.PARTS["WNG-007-R"]["mass_g"]),   # FIXES2: 16.1 g (lead 15.6 + tabs 0.5); caps are WNG-008, damper WNG-009/010,
           pack_x_m=list(m.PACK_X), trim_m=m.TRIM, trim_fwd_m=m.TRIM_FWD)
json.dump(out, open(os.path.join(HERE, "cad_mass.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
