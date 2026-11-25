### Pairs over 0.05 mm per angle (mesh, all parts in)

| delta deg | zj=mid | zj=lo | zj=hi |
|---|---|---|---|
| -21 | 0 (deepest 0.000) | 0 (deepest 0.024) | 0 (deepest 0.011) |
| -20 | 0 (deepest 0.000) | 0 (deepest 0.016) | 0 (deepest 0.000) |
| -18 | 0 (deepest 0.000) | 0 (deepest 0.012) | 0 (deepest 0.000) |
| -15 | 0 (deepest 0.000) | 0 (deepest 0.000) | 0 (deepest 0.000) |
| -12 | 0 (deepest 0.000) | 0 (deepest 0.000) | 0 (deepest 0.000) |
| -9 | 0 (deepest 0.000) | 0 (deepest 0.000) | 0 (deepest 0.000) |
| -6 | 0 (deepest 0.000) | 0 (deepest 0.000) | 0 (deepest 0.000) |
| -3 | 0 (deepest 0.000) | 0 (deepest 0.000) | 0 (deepest 0.000) |
| +0 | 0 (deepest 0.000) | 0 (deepest 0.000) | 0 (deepest 0.000) |
| +3 | 0 (deepest 0.000) | 0 (deepest 0.000) | 0 (deepest 0.000) |
| +6 | 0 (deepest 0.000) | 0 (deepest 0.000) | 0 (deepest 0.000) |
| +9 | 0 (deepest 0.000) | 0 (deepest 0.000) | 0 (deepest 0.000) |
| +12 | 0 (deepest 0.000) | 0 (deepest 0.000) | 0 (deepest 0.000) |
| +15 | 0 (deepest 0.000) | 0 (deepest 0.000) | 0 (deepest 0.000) |
| +18 | 0 (deepest 0.000) | 0 (deepest 0.012) | 0 (deepest 0.000) |
| +20 | 0 (deepest 0.000) | 0 (deepest 0.018) | 0 (deepest 0.000) |
| +21 | 0 (deepest 0.000) | 0 (deepest 0.019) | 0 (deepest 0.012) |

### Minimum mesh clearance per part pair, zj=mid (mm; negative = penetration depth from the hit list; only pairs under 2 mm)

| Part pair | mesh min mm | at delta | same group (constant) | declared contact |
|---|---|---|---|---|
| HWC-002 / MEC-001 | 0.000 | -21 | no | - |
| HWC-002 / MEC-008 | 0.000 | -21 | yes | arm screw through the keeper hole |
| MEC-001 / MEC-002 | 0.000 | -21 | no | arm bottom sits on the servo case top (ARM_Z0 = SV_Z1) |
| MEC-002 / MEC-003 | 0.000 | -21 | no | Z-bend leg in the 1.3 mm arm hole (leg 1.2 mm dia, end 0.25 mm inside the arm underside); at zj=lo the rod rests on the arm top (rod bottom tangent, by design) |
| MEC-002 / MEC-008 | 0.000 | -21 | yes | keeper clamped on the arm top by the arm screw (same group: constant) |
| MEC-003 / MEC-005 | 0.000 | -21 | yes | clevis pin through the cheek holes (ctx.seat: cheeks are cut to the pin; seated joint) |
| MEC-004 / MEC-005 | 0.020 | +21 | no | clevis pin in the 1.1 mm horn hole (same elevon group: relative pose constant) |
| HWC-002 / MEC-002 | 0.062 | -21 | yes | arm screw through the arm hub bore |
| MEC-003 / MEC-004 | 0.075 | +21 | no | - |
| MEC-003 / MEC-008 | 0.150 | -18 | no | keeper bridge over the Z-bend: top stop of the leg freedom, rod top bears on it at zj=hi (by design, D-212 rev 3) |
| MEC-001 / MEC-003 | 0.242 | -21 | no | - |
| MEC-001 / MEC-008 | 2.000 | -21 | no | - |

### Mesh vs analytic (AR-003), like for like at body level, zj=mid, side R, chosen angles (mm)

| Analytic pair (solids) | CAD bodies compared | analytic min | at delta | mesh min | at delta | max abs(mesh - analytic) over angles | note |
|---|---|---|---|---|---|---|---|
| arm / servo case | MEC-002 servo arm / MEC-001 servo case | 0.000 | -21 | 0.000 | -21 | 0.000 |  |
| clevis cheek -1 / horn blade | MEC-003 clevis cheek / MEC-004 horn | 0.066 | +21 | 0.075 | +21 | 0.008 |  |
| clevis cheek +1 / horn blade | MEC-003 clevis cheek / MEC-004 horn | 0.077 | +21 | 0.075 | +21 | 0.002 |  |
| arm / rod | MEC-002 servo arm / MEC-003 pushrod | 0.113 | -21 | 0.122 | +21 | 0.016 |  |
| keeper bridge / rod | MEC-008 keeper bridge / MEC-003 pushrod | 0.147 | -12 | 0.150 | -18 | 0.003 |  |
| rod Z-bend pin / servo case | MEC-003 rod Z-bend leg / MEC-001 servo case | 0.250 | -21 | 0.242 | -21 | 0.008 |  |
| keeper spacer / rod | MEC-008 keeper spacer / MEC-003 pushrod | 0.698 | -21 | 0.701 | -21 | 0.003 |  |
| keeper bridge / rod Z-bend pin | MEC-008 keeper bridge / MEC-003 rod Z-bend leg | 0.750 | -21 | 0.742 | -21 | 0.008 |  |
| clevis sleeve / horn blade | MEC-003 clevis sleeve / MEC-004 horn | 1.287 | +21 | 1.286 | +21 | 0.000 |  |
| keeper spacer / rod Z-bend pin | MEC-008 keeper spacer / MEC-003 rod Z-bend leg | 1.397 | -21 | 1.399 | +15 | 0.007 |  |
| rod / servo case | MEC-003 pushrod / MEC-001 servo case | 1.891 | -21 | 1.894 | -21 | 0.003 |  |
| keeper spacer / servo case | MEC-008 keeper spacer / MEC-001 servo case | 2.000 | -21 | 2.000 | -21 | 0.000 |  |
| arm / servo boot | MEC-002 servo arm / MEC-001 servo lead strain-relief boot | 2.952 | -21 | > 3 (none within cap) | - | - | |
| clevis sleeve / clevis pin | MEC-003 clevis sleeve / MEC-005 clevis pin | 2.974 | -21 | 3.000 | -21 | 0.026 | analytic hull bound |

### Minimum mesh clearance per part pair, zj=lo (mm; negative = penetration depth from the hit list; only pairs under 2 mm)

| Part pair | mesh min mm | at delta | same group (constant) | declared contact |
|---|---|---|---|---|
| MEC-002 / MEC-003 | -0.024 | -21 | no | Z-bend leg in the 1.3 mm arm hole (leg 1.2 mm dia, end 0.25 mm inside the arm underside); at zj=lo the rod rests on the arm top (rod bottom tangent, by design) |
| HWC-002 / MEC-001 | 0.000 | -21 | no | - |
| HWC-002 / MEC-008 | 0.000 | -21 | yes | arm screw through the keeper hole |
| MEC-001 / MEC-002 | 0.000 | -21 | no | arm bottom sits on the servo case top (ARM_Z0 = SV_Z1) |
| MEC-002 / MEC-008 | 0.000 | -21 | yes | keeper clamped on the arm top by the arm screw (same group: constant) |
| MEC-003 / MEC-005 | 0.000 | -21 | yes | clevis pin through the cheek holes (ctx.seat: cheeks are cut to the pin; seated joint) |
| MEC-004 / MEC-005 | 0.020 | +21 | no | clevis pin in the 1.1 mm horn hole (same elevon group: relative pose constant) |
| HWC-002 / MEC-002 | 0.062 | -21 | yes | arm screw through the arm hub bore |
| MEC-003 / MEC-004 | 0.075 | +21 | no | - |
| MEC-001 / MEC-003 | 0.094 | -21 | no | - |
| MEC-003 / MEC-008 | 0.294 | +0 | no | keeper bridge over the Z-bend: top stop of the leg freedom, rod top bears on it at zj=hi (by design, D-212 rev 3) |
| MEC-001 / MEC-008 | 2.000 | -21 | no | - |

### Mesh vs analytic (AR-003), like for like at body level, zj=lo, side R, chosen angles (mm)

| Analytic pair (solids) | CAD bodies compared | analytic min | at delta | mesh min | at delta | max abs(mesh - analytic) over angles | note |
|---|---|---|---|---|---|---|---|
| arm / rod | MEC-002 servo arm / MEC-003 pushrod | -0.028 | -21 | 0.000 | -20 | 0.031 | analytic hull bound |
| arm / servo case | MEC-002 servo arm / MEC-001 servo case | 0.000 | -21 | 0.000 | -21 | 0.000 |  |
| clevis cheek -1 / horn blade | MEC-003 clevis cheek / MEC-004 horn | 0.066 | +21 | 0.075 | +21 | 0.008 |  |
| clevis cheek +1 / horn blade | MEC-003 clevis cheek / MEC-004 horn | 0.077 | +21 | 0.075 | +21 | 0.002 |  |
| rod Z-bend pin / servo case | MEC-003 rod Z-bend leg / MEC-001 servo case | 0.100 | -21 | 0.094 | -21 | 0.006 |  |
| keeper bridge / rod | MEC-008 keeper bridge / MEC-003 pushrod | 0.292 | +0 | 0.294 | +0 | 0.004 |  |
| keeper spacer / rod | MEC-008 keeper spacer / MEC-003 pushrod | 0.698 | -21 | 0.701 | -21 | 0.003 |  |
| keeper bridge / rod Z-bend pin | MEC-008 keeper bridge / MEC-003 rod Z-bend leg | 0.900 | -21 | 0.894 | -21 | 0.006 |  |
| clevis sleeve / horn blade | MEC-003 clevis sleeve / MEC-004 horn | 1.287 | +21 | 1.287 | +21 | 0.000 |  |
| keeper spacer / rod Z-bend pin | MEC-008 keeper spacer / MEC-003 rod Z-bend leg | 1.397 | -21 | 1.400 | +15 | 0.007 |  |
| rod / servo case | MEC-003 pushrod / MEC-001 servo case | 1.804 | -21 | 1.807 | -21 | 0.006 |  |
| keeper spacer / servo case | MEC-008 keeper spacer / MEC-001 servo case | 2.000 | -21 | 2.000 | -21 | 0.000 |  |
| arm / servo boot | MEC-002 servo arm / MEC-001 servo lead strain-relief boot | 2.951 | -21 | > 3 (none within cap) | - | - | |
| clevis sleeve / clevis pin | MEC-003 clevis sleeve / MEC-005 clevis pin | 2.974 | -21 | 3.000 | -21 | 0.026 | analytic hull bound |

### Minimum mesh clearance per part pair, zj=hi (mm; negative = penetration depth from the hit list; only pairs under 2 mm)

| Part pair | mesh min mm | at delta | same group (constant) | declared contact |
|---|---|---|---|---|
| MEC-002 / MEC-003 | -0.012 | +21 | no | Z-bend leg in the 1.3 mm arm hole (leg 1.2 mm dia, end 0.25 mm inside the arm underside); at zj=lo the rod rests on the arm top (rod bottom tangent, by design) |
| HWC-002 / MEC-001 | 0.000 | -21 | no | - |
| HWC-002 / MEC-008 | 0.000 | -21 | yes | arm screw through the keeper hole |
| MEC-001 / MEC-002 | 0.000 | -21 | no | arm bottom sits on the servo case top (ARM_Z0 = SV_Z1) |
| MEC-002 / MEC-008 | 0.000 | -21 | yes | keeper clamped on the arm top by the arm screw (same group: constant) |
| MEC-003 / MEC-005 | 0.000 | -21 | yes | clevis pin through the cheek holes (ctx.seat: cheeks are cut to the pin; seated joint) |
| MEC-003 / MEC-008 | 0.000 | -15 | no | keeper bridge over the Z-bend: top stop of the leg freedom, rod top bears on it at zj=hi (by design, D-212 rev 3) |
| MEC-004 / MEC-005 | 0.019 | +21 | no | clevis pin in the 1.1 mm horn hole (same elevon group: relative pose constant) |
| HWC-002 / MEC-002 | 0.062 | -21 | yes | arm screw through the arm hub bore |
| MEC-003 / MEC-004 | 0.075 | +21 | no | - |
| MEC-001 / MEC-003 | 0.390 | -21 | no | - |
| MEC-001 / MEC-008 | 2.000 | -21 | no | - |

### Mesh vs analytic (AR-003), like for like at body level, zj=hi, side R, chosen angles (mm)

| Analytic pair (solids) | CAD bodies compared | analytic min | at delta | mesh min | at delta | max abs(mesh - analytic) over angles | note |
|---|---|---|---|---|---|---|---|
| keeper bridge / rod | MEC-008 keeper bridge / MEC-003 pushrod | -0.003 | -6 | 0.000 | -15 | 0.003 |  |
| arm / servo case | MEC-002 servo arm / MEC-001 servo case | 0.000 | -21 | 0.000 | -21 | 0.000 |  |
| clevis cheek -1 / horn blade | MEC-003 clevis cheek / MEC-004 horn | 0.066 | +21 | 0.075 | +21 | 0.008 |  |
| clevis cheek +1 / horn blade | MEC-003 clevis cheek / MEC-004 horn | 0.077 | +21 | 0.075 | +21 | 0.002 |  |
| arm / rod | MEC-002 servo arm / MEC-003 pushrod | 0.255 | -21 | 0.259 | -21 | 0.009 |  |
| rod Z-bend pin / servo case | MEC-003 rod Z-bend leg / MEC-001 servo case | 0.400 | -21 | 0.390 | -21 | 0.010 |  |
| keeper bridge / rod Z-bend pin | MEC-008 keeper bridge / MEC-003 rod Z-bend leg | 0.600 | -21 | 0.590 | -21 | 0.010 |  |
| keeper spacer / rod | MEC-008 keeper spacer / MEC-003 pushrod | 0.699 | -21 | 0.702 | -21 | 0.003 |  |
| clevis sleeve / horn blade | MEC-003 clevis sleeve / MEC-004 horn | 1.286 | +21 | 1.286 | +21 | 0.000 |  |
| keeper spacer / rod Z-bend pin | MEC-008 keeper spacer / MEC-003 rod Z-bend leg | 1.397 | -21 | 1.397 | +15 | 0.007 |  |
| rod / servo case | MEC-003 pushrod / MEC-001 servo case | 1.978 | -21 | 1.981 | -21 | 0.003 |  |
| keeper spacer / servo case | MEC-008 keeper spacer / MEC-001 servo case | 2.000 | -21 | 2.000 | -21 | 0.000 |  |
| arm / servo boot | MEC-002 servo arm / MEC-001 servo lead strain-relief boot | 2.952 | -21 | > 3 (none within cap) | - | - | |
| clevis sleeve / clevis pin | MEC-003 clevis sleeve / MEC-005 clevis pin | 2.974 | -21 | 3.000 | -21 | 0.026 | analytic hull bound |

### Per-angle clearance, zj=mid (mm, min of R and L; negative = penetration)

| delta | MEC-002 / MEC-003 | MEC-003 / MEC-008 | MEC-003 / MEC-004 | MEC-004 / MEC-005 | MEC-001 / MEC-003 | MEC-001 / MEC-002 | MEC-002 / MEC-008 | HWC-002 / MEC-002 | MEC-003 / MEC-005 |
|---|---|---|---|---|---|---|---|---|---|
| -21 | 0.000 | 0.150 | 0.075 | 0.020 | 0.242 | 0.000 | 0.000 | 0.062 | 0.000 |
| -20 | 0.000 | 0.150 | 0.077 | 0.021 | 0.242 | 0.000 | 0.000 | 0.062 | 0.000 |
| -18 | 0.003 | 0.150 | 0.082 | 0.023 | 0.244 | 0.000 | 0.000 | 0.062 | 0.000 |
| -15 | 0.010 | 0.150 | 0.087 | 0.024 | 0.246 | 0.000 | 0.000 | 0.062 | 0.000 |
| -12 | 0.017 | 0.150 | 0.092 | 0.028 | 0.247 | 0.000 | 0.000 | 0.062 | 0.000 |
| -9 | 0.024 | 0.150 | 0.095 | 0.032 | 0.248 | 0.000 | 0.000 | 0.062 | 0.000 |
| -6 | 0.029 | 0.150 | 0.098 | 0.033 | 0.249 | 0.000 | 0.000 | 0.062 | 0.000 |
| -3 | 0.028 | 0.150 | 0.100 | 0.032 | 0.250 | 0.000 | 0.000 | 0.062 | 0.000 |
| +0 | 0.028 | 0.150 | 0.100 | 0.031 | 0.250 | 0.000 | 0.000 | 0.062 | 0.000 |
| +3 | 0.028 | 0.150 | 0.100 | 0.032 | 0.250 | 0.000 | 0.000 | 0.062 | 0.000 |
| +6 | 0.029 | 0.150 | 0.098 | 0.033 | 0.249 | 0.000 | 0.000 | 0.062 | 0.000 |
| +9 | 0.024 | 0.150 | 0.095 | 0.033 | 0.248 | 0.000 | 0.000 | 0.062 | 0.000 |
| +12 | 0.017 | 0.150 | 0.092 | 0.028 | 0.247 | 0.000 | 0.000 | 0.062 | 0.000 |
| +15 | 0.010 | 0.150 | 0.087 | 0.023 | 0.246 | 0.000 | 0.000 | 0.062 | 0.000 |
| +18 | 0.004 | 0.150 | 0.082 | 0.021 | 0.244 | 0.000 | 0.000 | 0.062 | 0.000 |
| +20 | 0.001 | 0.150 | 0.077 | 0.021 | 0.242 | 0.000 | 0.000 | 0.062 | 0.000 |
| +21 | 0.000 | 0.150 | 0.075 | 0.020 | 0.242 | 0.000 | 0.000 | 0.062 | 0.000 |

### Per-angle clearance, zj=lo (mm, min of R and L; negative = penetration)

| delta | MEC-002 / MEC-003 | MEC-003 / MEC-008 | MEC-003 / MEC-004 | MEC-004 / MEC-005 | MEC-001 / MEC-003 | MEC-001 / MEC-002 | MEC-002 / MEC-008 | HWC-002 / MEC-002 | MEC-003 / MEC-005 |
|---|---|---|---|---|---|---|---|---|---|
| -21 | -0.024 | 0.300 | 0.075 | 0.020 | 0.094 | 0.000 | 0.000 | 0.062 | 0.000 |
| -20 | -0.016 | 0.300 | 0.077 | 0.021 | 0.095 | 0.000 | 0.000 | 0.062 | 0.000 |
| -18 | -0.012 | 0.300 | 0.082 | 0.022 | 0.096 | 0.000 | 0.000 | 0.062 | 0.000 |
| -15 | 0.000 | 0.300 | 0.087 | 0.024 | 0.098 | 0.000 | 0.000 | 0.062 | 0.000 |
| -12 | 0.001 | 0.300 | 0.092 | 0.028 | 0.099 | 0.000 | 0.000 | 0.062 | 0.000 |
| -9 | 0.001 | 0.299 | 0.095 | 0.033 | 0.100 | 0.000 | 0.000 | 0.062 | 0.000 |
| -6 | 0.003 | 0.296 | 0.098 | 0.033 | 0.099 | 0.000 | 0.000 | 0.062 | 0.000 |
| -3 | 0.005 | 0.296 | 0.100 | 0.032 | 0.098 | 0.000 | 0.000 | 0.062 | 0.000 |
| +0 | 0.002 | 0.294 | 0.100 | 0.031 | 0.098 | 0.000 | 0.000 | 0.062 | 0.000 |
| +3 | 0.005 | 0.295 | 0.100 | 0.032 | 0.098 | 0.000 | 0.000 | 0.062 | 0.000 |
| +6 | 0.002 | 0.296 | 0.098 | 0.033 | 0.099 | 0.000 | 0.000 | 0.062 | 0.000 |
| +9 | 0.001 | 0.299 | 0.095 | 0.032 | 0.100 | 0.000 | 0.000 | 0.062 | 0.000 |
| +12 | 0.000 | 0.300 | 0.092 | 0.028 | 0.099 | 0.000 | 0.000 | 0.062 | 0.000 |
| +15 | 0.000 | 0.300 | 0.087 | 0.023 | 0.098 | 0.000 | 0.000 | 0.062 | 0.000 |
| +18 | -0.012 | 0.300 | 0.082 | 0.021 | 0.096 | 0.000 | 0.000 | 0.062 | 0.000 |
| +20 | -0.018 | 0.300 | 0.077 | 0.021 | 0.095 | 0.000 | 0.000 | 0.062 | 0.000 |
| +21 | -0.019 | 0.300 | 0.075 | 0.020 | 0.094 | 0.000 | 0.000 | 0.062 | 0.000 |

### Per-angle clearance, zj=hi (mm, min of R and L; negative = penetration)

| delta | MEC-002 / MEC-003 | MEC-003 / MEC-008 | MEC-003 / MEC-004 | MEC-004 / MEC-005 | MEC-001 / MEC-003 | MEC-001 / MEC-002 | MEC-002 / MEC-008 | HWC-002 / MEC-002 | MEC-003 / MEC-005 |
|---|---|---|---|---|---|---|---|---|---|
| -21 | -0.011 | 0.000 | 0.075 | 0.021 | 0.390 | 0.000 | 0.000 | 0.062 | 0.000 |
| -20 | 0.000 | 0.000 | 0.077 | 0.022 | 0.391 | 0.000 | 0.000 | 0.062 | 0.000 |
| -18 | 0.000 | 0.000 | 0.082 | 0.023 | 0.392 | 0.000 | 0.000 | 0.062 | 0.000 |
| -15 | 0.001 | 0.000 | 0.087 | 0.024 | 0.394 | 0.000 | 0.000 | 0.062 | 0.000 |
| -12 | 0.008 | 0.000 | 0.092 | 0.027 | 0.395 | 0.000 | 0.000 | 0.062 | 0.000 |
| -9 | 0.015 | 0.000 | 0.095 | 0.032 | 0.396 | 0.000 | 0.000 | 0.062 | 0.000 |
| -6 | 0.020 | 0.000 | 0.098 | 0.034 | 0.397 | 0.000 | 0.000 | 0.062 | 0.000 |
| -3 | 0.020 | 0.000 | 0.100 | 0.032 | 0.398 | 0.000 | 0.000 | 0.062 | 0.000 |
| +0 | 0.019 | 0.000 | 0.100 | 0.031 | 0.398 | 0.000 | 0.000 | 0.062 | 0.000 |
| +3 | 0.020 | 0.000 | 0.100 | 0.032 | 0.398 | 0.000 | 0.000 | 0.062 | 0.000 |
| +6 | 0.020 | 0.000 | 0.098 | 0.033 | 0.397 | 0.000 | 0.000 | 0.062 | 0.000 |
| +9 | 0.015 | 0.000 | 0.095 | 0.033 | 0.396 | 0.000 | 0.000 | 0.062 | 0.000 |
| +12 | 0.008 | 0.000 | 0.092 | 0.029 | 0.395 | 0.000 | 0.000 | 0.062 | 0.000 |
| +15 | 0.001 | 0.000 | 0.087 | 0.023 | 0.394 | 0.000 | 0.000 | 0.062 | 0.000 |
| +18 | 0.001 | 0.000 | 0.082 | 0.021 | 0.392 | 0.000 | 0.000 | 0.062 | 0.000 |
| +20 | 0.001 | 0.000 | 0.077 | 0.020 | 0.391 | 0.000 | 0.000 | 0.062 | 0.000 |
| +21 | -0.012 | 0.000 | 0.075 | 0.019 | 0.390 | 0.000 | 0.000 | 0.062 | 0.000 |
