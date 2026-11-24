# T-085 paused 2026-11-22 (Dillon: "Reach a good place to pause for later resumption")

The T-085 implementer was stopped before it wrote `T085_report.md`. Nothing here is reviewed; treat every number as
preliminary.

- Uncommitted edits to `structures/fe_a.py` (+100 lines: pack-on-tray, hub-joint springs, keywords) and
  `TEST-PLAN-O4B.md` (+17 lines: T-A-TAP method) are saved in `t085_partial.patch` and were reverted in the working
  tree. Resume with `git apply redesign/qp/A/mechanism/out/T085_data/t085_partial.patch` from the repo root.
  `fe_a_post_t085.py` / `TEST-PLAN-O4B_post_t085.md` are the same edits as whole files.
- Preliminary result (`modes_t085.txt` s4): with the cell credited, the pack on a compliant tray and the hub-joint
  springs (`t085_hubflex.py`, al6061), D-185 (a) FAILs at all three corners: strong modes about 99-107 Hz
  (cage bounce, cy 1.2-1.3) and 249-272 Hz. Design sketches C1 (softer bridge in z) and C2 (pack carried by the wing
  centre node) do not clear the band either.
- Check before trusting it: strain energy shows "pad 62-65 %" in the in-band modes; confirm what the "pad" element is
  (pack foam pad?) and that its stiffness is sourced, not invented. If it is an EST spring, bound it (as T-084 did for
  the cell) before judging D-185.
- Still to do for T-085: finish/verify the model, write `T085_report.md` with a proposed D-236, decide the design route
  (D-233 option C trade study) if the FAIL holds, then review.
