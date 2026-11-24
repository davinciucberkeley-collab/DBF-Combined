# Stream W notes (stopped 2026-11-14 at the coordinator's request)

Stream W (wing, R-STRUCT-MARGIN), stopped mid-investigation. **No repo file was edited, no solver was run and no
background job was started.** No scratch scripts were written. No web lookups were made, so there are no prices or
sources with URLs yet. Paths are relative to `redesign/`. `EST` = estimate, "—" = unknown.

## 1. What the existing results already say

### Level 3 exists but was never merged
S1 (`review/CDR-2026-11-13/fixes/S1.md` §5) left the level-3 local job running. Its output,
`team/C2/fea/out/d68_local_d68_L3.json`, was written 2026-11-13 17:49: 356 703 nodes, 0.75 mm, wall 9 107 s, and the
L4 case alone took 3 744 s. `out/d68_submodel.json` (15:14) and `fea/params.json` still hold the level-2 values. The
claims will read level 3 once the integrator or the new owner runs this chain:
`python -I redesign/team/C2/fea/wing_fea_d68.py --phase merge`, then `fea_report.py`, then `fea_claims.py`.

### Peaks per level
Source: the `d68_local_*.json` files. Pocket/foam zone, governing case `block/L4-CORNER-SIDE-Y/MC-C`. All values are
at limit load (× 1.5 gives ultimate), in kPa.

| Model | h (mm) | s1 element | s1 1 mm avg (n elems) | s3 element | s3 avg | tau element | tau avg |
|---|---|---|---|---|---|---|---|
| d68 L1 | 1.6 | 208.1 | 166.2 (6) | −135.0 | −119.4 | 88.1 | 75.2 |
| d68 L2 | 1.1 | 221.1 | 189.4 (8) | −160.7 | −128.9 | 94.0 | 84.2 |
| d68 L3 | 0.75 | 259.4 | 167.5 (27) | −188.0 | −127.7 | 108.6 | 80.9 |
| d68g L2 (grooves + open seams) | 1.1 | 224.1 | 192.3 | −180.1 | −145.8 | 94.5 | 83.1 |
| as drawn L2 | 1.1 | 195.4 | 165.5 | −167.9 | −132.5 | 93.0 | 73.0 |
| d68 L2, tube G 4.31 GPa | 1.1 | 182.9 | 156.2 | −120.5 | −96.8 | 76.8 | 67.6 |

What the levels show:
- At level 3 (0.75 mm), the 1 mm-averaged corner values at ultimate would be **s1 251 / s3 192 / tau 121 kPa**
  (= 1.5 × L3 avg), against allowables of 150 / 120 / 100 kPa. These replace the level-2 claim values of
  284 / 193 / 126 kPa. All three still fail.
- **The model has not converged and, as built, cannot converge.**
  - The element peaks rise with every refinement (208 → 221 → 259 kPa). That is a singularity at a stiff/soft
    re-entrant corner: PETG 1.1 GPa or bead 1.5 GPa against XPS 10 MPa.
  - The 1 mm average does not settle either (166 → 189 → 168 kPa), because only 6–27 elements fall inside the
    sphere.
  - A converged claim needs either a design whose governing foam stress is not at a bimaterial re-entrant corner,
    or elements well below 1 mm. At level 3 one local solve already takes about 1–2.5 h, so finer meshes are
    impractical.
- The "distributed" introduction (fin-root fillet carries the station load, a sensitivity case not used by the claims)
  is far worse: L3 L4 avg 274.5 / −303.4 kPa limit at the outboard-aft corner (x 0.096, y 0.336–0.341).

### Where the peaks are
| Peak | Location (m) | Where that is |
|---|---|---|
| s1 | (0.0296, 0.2989, −0.0069) | front-inboard block corner, at the toe of the 3 mm bead, just under the lower skin (zl(0.03) = −0.00705) |
| s3 | (0.0958, 0.2989, −0.0083) | aft-inboard corner, lower surface |

Both peaks are at the surface, on the inboard pocket face.

## 2. Geometry and model facts gathered
| Item | Value | Source |
|---|---|---|
| Block footprint | x 0.02785–0.09715, y 0.30185–0.33815, full depth | `team/C2/fea/wing_fea.py` `d1_geometry()` (from `team/D1/wing_data.py`) |
| Spar | axis x 0.080, z 0.0066, r 11 / 10 mm | same |
| Brace anchor | y 0.2335–0.2505 | same |
| Servo pocket (open below) | y 0.2527–0.2879, x 0.1722–0.2075 | same |
| Elevon spans | (0.07, 0.30) and (0.34, 0.56) | same |
| Hinge | x 0.2496 | same |
| Section | upper z 0.0170 / lower z −0.0070 at x 0.03; upper z 0.0226 / lower z −0.0086 at x 0.08 | `ws.XA`, `ws.ZU`, `ws.ZL` |
| Foam and tube properties | XPS E 10 MPa, G 4 MPa; tube E_lo 70 GPa, G_lo 3 GPa | `wing_struct.M` |
| PETG block | E 1.1 GPa (2.0 GPa × 0.55 fill) | `wing_fea.materials` |
| Allowables | 150 / 120 / 100 kPa (tension / compression / shear) | `wing_struct.M` |
| Load introduction | block intro: station loads as tractions on the skin faces over the block only | `wing_fea.tractions` |
| Foam torque share | FEA/beam tip-twist ratio L4 = 0.833, so the foam carries about 17 % of the torque far from the block (EST) | `team/C2/fea/params.json` `fea_beam_twist_ratio_L4` |
| Global cut planes | the pickled global solves have planes only at 0.27, 0.28, 0.36, 0.37 m | `wing_fea_d68.py`; any wider local model needs a new global solve (about 200–900 s) |
| Existing doubler | 60 mm tape band wrapped round the LE from upper x 0.12 to lower x 0.12 over each block pocket; tape skin not in the FEA | `subsystems/wing/params.json` `skin.block_doubler_x_m` |
| Block size and edge radius | come from the fins params (`fin_detail.block.edge_r_m`) | owned by stream F, so a longer block or a larger radius is a request to F |

## 3. Options weighed (none run yet)
| Option | Reading so far |
|---|---|
| Larger corner radius | S1 found R 3 + bead 14 % worse than the sharp pocket at L2, so the stress is not a corner-radius effect. Unlikely to help. Needs F to change the block. |
| Bigger microballoon bead | The bead is itself a stiff inclusion: it moves the peak to its toe. Unlikely to help. |
| Moving or stopping the lead grooves | Worth only 1.5 % on tension (`d68g_over_d68_s1` 1.015). Does not close the fail. |
| Longer block | Does not change the foam's torque share, which is set by the GJ ratio. Needs F. Not promising alone. |
| Denser foam frame round the block (e.g. PVC foam) | Weakens the modulus step at the XPS edge, but a corner remains. Price not looked up. |
| **Preferred candidate: glass block doubler band** | Replace or underlay the 60 mm tape band with 2 plies of woven E-glass in epoxy (one ply 0/90, one ±45, about 0.2 mm, quasi-isotropic E about 14 GPa EST). Wrap it round the LE from upper x 0.12 to lower x 0.12, so the band has no front edge, and run it the block span ± 20–25 mm. It bridges the surface strain step at the inboard and outboard pocket faces, where both peaks sit. Shear-lag length sqrt(E t h / G_f) ≈ 87 mm EST, so load passes into the foam gently. Mass about 0.025 m² per station × 0.2 kg/m² per ply × 2 plies ≈ 10 g per side, about 20 g total EST, less the tape it replaces. Prices and laminate properties still to be looked up and cited. |

## 4. Plan for the next owner
1. Merge level 3 and re-emit the claims first: the s1 claim drops from 284 to 251 kPa and still fails.
2. Write a variant driver in `team/C2/fea/` that imports `wing_fea_d68`, with the band built in:
   - the band as a 0.5 mm offset layer (gmsh `extra_lines` along the inward outline normal over the band arc, plus a
     closing segment at x 0.12);
   - E_eq = 14 GPa × 0.2 / 0.5 = 5.6 GPa, so the layer has the laminate's membrane stiffness;
   - local cuts at 0.255 / 0.385, so the band ends sit ≥ 25 mm from the cuts, and a new global solve on those
     planes;
   - fine span layers at the band ends;
   - run L4 block only at L1 to screen, then L1 / L2 / L3 for the GCI;
   - report the foam under the band ends and corners, the glass stress, and the cut-plane check.
3. If the band passes, D1 draws it and updates the part data and mass. It replaces part of WNG-003's tape band.

## 5. Files
- Reverted: none (nothing edited).
- Written: this file only.
