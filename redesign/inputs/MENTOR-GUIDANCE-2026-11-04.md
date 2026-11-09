# Mentor guidance, weekly check-in 2026-11-04 (design-relevant points)

- **Buildability before simulation.** Figure out whether it can actually be made and assembled before running
  detailed CFD/FEA/flight sims; a design change means rebuilding the sims. "10 agents all in mechanical design."
- **Practicality checks:** no floating or unattached parts; real ends on booms; one pole holding a wheel is suspect;
  remove duplicated parts; decide hollow vs solid wing and spar before deeper analysis.
- **Manufacturing as a design axis:** compare foam, balsa, 3D-printed and machined options; estimate cost; plan and
  animate assembly; check what Jacobs Hall can actually do.
- **Design-space method:** morphological charts; completeness audits ("is this complete? what options are
  missing?") repeated until saturation, tracking which sources add new ideas; then deduplicate and converge.
  Design similarity (embeddings / scoring) to find unexplored regions. Test the outlandish concepts before
  dismissing them.
- **Success criteria that can be checked:** every part connected to a joint, parts touching but not overlapping,
  connections structural and electrical/thermal; a knowledge graph of parts and connection types.
- **Subsystem agents plus one integration agent** rather than one agent designing the whole plane.
- **Converge:** fewer artifacts (v2, v3 rather than new ones), one repository, synthesis over more exploration.
- Open questions raised in the meeting: wheels vs skids vs VTOL-only landing; 2 m vs 3 m size box (fit in a car);
  do rotors stop in cruise; materials.
