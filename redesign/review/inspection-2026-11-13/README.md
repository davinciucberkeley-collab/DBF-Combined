# Inspection pictures 2026-11-13: wire terminations (D-89)

These close-ups were rendered from the D-89 CAD, through `blender/blender_backend.py`, in Blender 4.5.14 Workbench. Each part has its own
colour, and each wire has a stronger colour. The pod shell, hatch, pack and straps are hidden so the ends show. The team flagged
this area in the D-88 Explorer, where the FC's leads ended on the bare box. Each lead now ends on a drawn termination,
and the CAD gate checks this by name (`collision/README.md`, "On a termination").

| Picture | What it shows |
|---|---|
| `T1_fc_aft.png` | FC aft strip. Each output conductor is soldered in its own hole, rises off the board and enters its JR contact on the tray. The GPS cable leaves the GH-6 plug and rises through the I²C splice sleeve. |
| `T2_fc_fore_rx_plug.png` | FC fore edge. The RX cable leaves the GH-4 (SERIAL6) plug square and runs down in front of the end stop. |
| `T3_rx_pads.png` | RP3. The 4-core cable ends in its breakout sleeve and the four conductors lie on the four solder pads. The airspeed lead (top) enters the GH-4 plug on the sensor's aft face. |
| `T5_gps_plug.png` | GPS mast. The cable enters the GH-6 plug on the module's aft-upper end face, along the 45° pad. |
| `T6_pdb_link_pads.png` | Power board. The battery and output jumpers lie on their four pad joints. The board-link ribbon enters its plug on the top header. |
| `T7_fc_under_link.png` | Under the FC (seen from below). The board-link ribbon ends in the 2 × 5 header plug between the gel cubes. |

Connector sizes come from the JST GH catalogue. Board layouts are EST until the boards arrive (`params/CHANGE-LOG.md` D-89).
