"""Rebuild the Explorer Status tab (#status in app.html) for concept A. Edit the lists below, then:
python -I redesign/site/sync_status_a.py && python -I redesign/site/make_index.py
Sources are named on each row (qp/README.md, review/QP-4/BOARD.md, review/QP-5/*, params/CHANGE-LOG.md)."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.join(HERE, "app.html")
GH = "https://github.com/davinciucberkeley-collab/DBF-Combined/blob/redesign/v1/redesign/"


def L(path, txt):
    return f'<a class="ds-link" href="{GH}{path}" target="_blank" rel="noopener">{txt}</a>'


def B(st, t=None):
    return f'<span class="ds-badge" data-status="{st}">{t or st}</span>'


PHASES = [
    ("DONE", "Re-study and selection", "RESTUDY 2026-11-14, QP-1 sizing of A, B, T, D2; J6 board picks A (D-182)"),
    ("DONE", "Sizing and SITL", "QP-2: wind, bench plan, baseline (D-183, D-184)"),
    ("DONE", "Pre-order validation", "QP-3: SITL flight, structures, cost and schedule, CAD through the 3-D gates (D-185, D-186)"),
    ("DONE", "Fixes and board re-sit", "QP-4: elevon balance and hinge damper, caps and stops (D-187, D-188); Order 1 YES, main order NOT YET"),
    ("DONE", "Claims and real-shape CAD", "QP-5: claims cleared (D-189 to D-192), CAD to vendor geometry (D-193, D-194), analyses on it (D-195), hub walls (D-196), arms and motor cups (D-197)"),
    ("DONE", "O4b re-sit and X2216 redesign", "D-217 to D-241: O4b (9x4.5 props, Kakute H743-Wing, 4S 2,800 mAh), SunnySky X2216 880KV (D-227), wing torsion cell (D-226), FC 75 mm left of centre (D-239, D-240), Order 1 rebuilt (D-238), bench tests TP-15 to TP-18 (T-094, D-241); 14 strict proof FAILs open (run_all 2026-11-23, D-245)"),
    ("PARTIAL", "Enclosed wiring", "C8 (D-199): phase leads enclosed from motor to ESC (arm tubes, hub conduits, raceway under the tray, foam ditch, bay cover), servo leads in foam grooves; exposed wire 0.597 strand-m after D-240 (per-wire table: qp/A/cad/out/EXPOSED-WIRING.md, from wire_inventory.json); pitot lines AVN-009-T / S drawn (E3d, 39 mm each)"),
    ("NOT STARTED", "Order 1 and bench", "Order 1 (bench kit) 1-4 Dec; no fabrication before Jacobs reopens (AM-037): stand build, prints, soldering and bench tests TP-1 / TP-2 run 19-28 Jan 2027; weigh-in, SITL and wind measuring run over the break"),
    ("NOT STARTED", "Main order", "split (D-248): config-independent lines and the R15 rib tube in Dec ($1,478.94 with Order 1), the size-sensitive lines ($113.29) after the 29 Jan 2027 go / no-go"),
    ("NOT STARTED", "Build and tethered hover", "January to February; lifeboat trigger (ZOHD Altus; withdrawn by AM-008, earlier design (record))"),
    ("NOT STARTED", "Flight test", "transition round trip and the mission profile, by 30 April 2027"),
]

ISSUES = [
    ("<b>Exposed wiring</b> (hard constraint C8): 0.597 strand-m exposed in the CAD after D-240 (FC moved, routes re-run inside the cover; wire_inventory.json). Per wire: 0.253 vendor pack power leads (E-HRN-13), 0.105 phase-lead joint samples, 0.085 battery tail (XT60 field disconnect), 0.071 servo-lead last runs, 0.064 pack balance lead, 0.019 GPS, 0.001 connector; RX and airspeed leads have none. The pitot lines AVN-009-T / S are drawn (E3d, 39 mm each). Table with reasons: qp/A/cad/out/EXPOSED-WIRING.md.",
     "harness, CAD", "CLAUDE.md C8; qp/A/cad/out/EXPOSED-WIRING.md (exposed_wire_table.py); " + L("review/QP-5/HARNESS-ENCLOSED.md", "HARNESS-ENCLOSED.md") + " D-199.2 reasons", B("FAIL", "OPEN")),
    ("<b>Hub and arm tube under the landing load</b>: the hub is machined 6061-T6 since D-220 (the printed PETG hub was sized on the wrong load). In the aluminium-hub FEA (T-076c, run H-A1) the hub passes; the CF arm-tube shear and the arm-tube / sleeve bond rows fail for the landing demand (they also fail with a PETG hub), so they are routed to D-226 (landing load through the wing torsion cell) and to the tests TP-4 and TP-5. The 2026-11-17 PETG hub map is an earlier design (record).",
     "structures, bench", "D-220, D-226, " + L("qp/A/mechanism/out/T076c_hub_al.md", "T076c_hub_al.md") + " s0", B("FAIL", "OPEN")),
    ("<b>Mass gate missed</b>: predicted 1,881 g EST (CAD basic 1,641.0 g x 1.1174 + 48 g, 129 placed parts) against the 1.47 kg weigh-in gate, -27.9 %; physics checks govern (D-219, D-233). Earlier design (record): 1,455.6 g against 1.46 kg after D-198.",
     "mass (A3)", "params-A.json, CL-A-MASS-PRED (FAIL), CL-A-CUTS-REQUIRED, " + L("qp/A/MASS-GATE.md", "MASS-GATE.md") + " s11", B("UNVERIFIED")),
    ("<b>Elevon flutter</b> is cleared only with the silicone-fluid hinge damper (lowest onset 37.5 m/s hot, 41 m/s nominal, against the 28.8 m/s line); TP-15 must show free play &le; 1.0&deg; (the claim CL-A-LINKAGE-FREEPLAY FAILS on the model: 1.28&deg; against 1&deg;), damping &ge; 1 %.",
     "structures (C1, C2)", "CL-A-FLUTTER-ELEVON-HOT / -NOM, CL-A-LINKAGE-FREEPLAY, D-188, " + L("qp/A/structures/flutter_d205.md", "flutter_d205.md"), B("UNVERIFIED")),
    ("<b>14 claims FAIL in the strict proof build</b> (run_all, 2026-11-23, after D-245): the 12 of D-237 (mass gate and prediction, hover vibration in band, gain margin, FC vibration, elevon horn / rib / free play and others) plus elevon pitch use and the stall check at the predicted mass; the elevon flutter claim (nominal) is UNVERIFIED. To be decided by the bench tests TP-10b and TP-15 to TP-18.",
     "all", "qp/A/proofs/out/graph.js, D-232, D-236, D-237, D-241, D-245", B("FAIL", "OPEN")),
    ("<b>Elevon pitch use in transition</b>: 0.69 (Z5) to 0.79 (T-074) of the 15&deg; basis against the 0.60 line (9&deg;), FAIL, open (AR-015, AR-016). D-245 keeps the 15&deg; basis and supersedes the QP-4 board's 20&deg; stop basis (no A-specific roll / gust reserve derivation exists; the 20&deg; basis would cut the reserve from 16&deg; to 8&deg;). Information only: 20&deg; basis 0.52-0.59.",
     "flight controls", "D-244, D-245, AR-015, AR-016, CL-A-PITCH-USE", B("FAIL", "OPEN")),
    ("<b>Stall at the predicted mass (A-P6)</b>: 1.3 Vs = 17.74 m/s at 1.8807 kg EST (17.75 at the rounded 1.881 kg of AR-015) (rho 1.20, S 0.22 m&sup2;, CLmax 0.75 EST) against the 17.0 m/s cruise, FAIL; the pass line is a measured CLmax of 0.81 or more (TP-11). (rho 1.225 gives 17.56 m/s, same verdict.)",
     "aero", "CL-A-STALL-PRED, A-P6, D-228, AR-015", B("FAIL", "OPEN")),
    ("<b>Landing stroke</b> passes (17.2 mm of 20, 10.76 g) only inside the foam region Fp 37.5-39.0 N and zeta 0.02-0.05; outside it the stroke bottoms (20.2-20.6 mm). The foam plateau and damping are unmeasured.",
     "structures", "D-243, AR-016, CL-A-LANDING-STROKE, TP-3", B("UNVERIFIED")),
    ("<b>Gusty hover heading</b>: excursion 25.4&deg; in one of seven turbulence seeds (8.5-14.0&deg; in the rest); flown with the pilot holding heading.",
     "flight controls", "A-P8a, " + L("review/QP-5/ANALYSES.md", "QP-5/ANALYSES.md"), B("UNVERIFIED", "MARGINAL")),
    ("<b>Budget room</b>: spend $1,592.23 plus crash reserve $346.94 = $1,939.17 of $2,000 (margin $60.83); the +30 % line on unverified prices reads $2,029.68, information only (AM-013) and over $2,000. The prop adapter is part of BOM line P01 (X-mount, screws, adapter).",
     "procurement", "bom_a.py (2026-11-23), BOM-A.csv P01, D-235", B("UNVERIFIED")),
    ("<b>S5010 CLmax and the neutral point</b> are estimates (no measured CLmax found); static margin 7.61 % at the CAD CG 22.05 mm against 5 % (CL-A-SM, D-240).",
     "aero", "ASM-A-NP, " + L("qp/A/aero_s5010.py", "aero_s5010.py"), B("UNVERIFIED", "EST")),
    ("<b>Elevon linkage sweep</b> is checked by the arm-angle table only; the collision poses move the elevon but leave the pushrod and servo arm at neutral.",
     "CAD", "review/QP-5/CAD-INTEGRATION.md s1", B("UNVERIFIED")),
    ("<b>D-195 sign-off</b> (earlier design, record): design target 1.44 to 1.46 kg and CG band forward edge 20 to 19 mm need the aero lead's (A1) sign-off.",
     "A1", "params/CHANGE-LOG.md D-195", B("PROPOSED")),
]

TESTS = [
    ("Elevon free play, horn / rib / foam hold, elevon torsion, stall load on the built elevon", "model; 14 strict proof FAILs", "TP-15 free play, TP-16 horn-rib coupon, TP-17 elevon torsion, TP-18 bench stall (T-094, TEST-PLAN-O4B)"),
    ("Motor thrust, hover power, one-motor current and can temperature, yaw torque", "model only (APC data, mission_gate_a.py)", "bench M1-M4 on Order 1 (G1-G4), 28 Jan 2027 (after Jacobs reopens, AM-037)"),
    ("Elevon stiffness, free play, damping, lead-bond pull", "model only (D-188 damper)", "elevon coupon E1 (G8), after 19 Jan 2027 (AM-037)"),
    ("Foam density, printed parts, epoxy, lead strip, servo mass", "CAD and estimates", "weigh-in (G6): at least 27.2 g of the 41.6 g estimated cuts real (CL-A-CUTS-REQUIRED, T-A-WEIGH)"),
    ("Hub socket wall and motor cup", "analysis (D-196, D-197)", "coupons: hub pull 1.5 x 332 N; cup axial 65 N, transverse 65 N at 35 mm, torque 5.2 / 3.0 N&middot;m; pull one screw from a real motor"),
    ("Motor and cup heat", "not analysed", "30 min thrust-stand soak per motor with a tap test before and after; cup plate &le; 55 &deg;C (EST)"),
    ("Cage and fin vibration modes", "FE (structures/iter3_run.md)", "tap test within &plusmn;20 % of FE (T-A-TAP)"),
    ("CG and neutral point", "CAD CG 22.05 mm, static margin 7.61 % (D-240, CL-A-CG, CL-A-SM); earlier design (record): CG 21.1 mm", "knife-edge CG breadboard (T-A-CG-BREADBOARD)"),
    ("IMU vibration in hover", "model", "first tethered hover, VIBE &lt; 30 m/s&sup2; (T-A-TETHER-VIBE)"),
]

DECISIONS = [
    ("SunnySky X2216 V3 short-shaft stock (RMRC backorder, D-228)", "check stock before Order 1; Order 1 is $887.25 EST for 4 X2216 (ORDER-1.csv, D-238). Earlier design (record): T-Motor MN2212 stock, buy all 5 motors ($1,123.02)", "team member", "4 Dec"),
    ("Order 1 go", "$887.25 incl. tax and shipping EST (ORDER-1.csv, D-238); servo quantity 2 (D-234). Earlier design (record): 3 ES3054HV servos pulled forward, +$46.27 (D-J6-5)", "team lead", "early Dec"),
    ("Written booking plan for test mornings from 16 Feb", "at least 4 mornings a week (G9); 5 suggested after the 4 m/s wind limit (D-192) and needed for slack at p 0.60 (SCHEDULE-A, AM-037 re-plan)", "team", "29 Jan 2027"),
    ("ANSWERED: go / no-go date (F-6, T-099 round 12)", "Go / no-go and bench decision: Fri 29 Jan 2027, one date (D-248; replaces 15 Dec, 18 Dec and 28 Dec). Basis: user constraint AM-037 (no fabrication until after winter break, orders from early December); spring instruction begins 19 Jan 2027 (Registrar calendar), Jacobs reopening date assumed 19 Jan (not published). Schedule slack to 30 Apr is +2 d at baseline, negative at p 0.60 (-13 d) or 3 mornings a week (-16 d); $0 options in SCHEDULE-A", "team (AM-037, user)", "decided 2026-11-23"),
    ("Main order go / no-go", "Order 1b (config-independent lines and R15, $591.69 with its shipping) 1-11 Dec; order 2 ($113.29) after the 29 Jan go / no-go if TP-1 / TP-2 pass; a failed bench reopens the configuration (AM-016)", "team lead and board", "11 Dec / 29 Jan 2027"),
    ("Lifeboat trigger", "earlier design (record): buy the ZOHD Altus VTOL if there is no tethered hover by 15 Feb 2027; the kit airframe is withdrawn (AM-008, D-218 reversed)", "team lead", "15 Feb"),
    ("Declare the design final", "the Simulations tab is already published (T-097 / T-098, 2026-11-23); the declaration is the team's call", "team lead", "&mdash;"),
]

nd = sum(p[0] == "DONE" for p in PHASES)
npart = sum(p[0] == "PARTIAL" for p in PHASES)
nn = len(PHASES) - nd - npart
track = "".join('<i class="d"></i>' if p[0] == "DONE" else '<i class="p"></i>' if p[0] == "PARTIAL" else "<i></i>" for p in PHASES)
phases = "".join(f'<div class="phase" data-phase="{s}"><span class="n">{i + 1:02d}</span><b>{n}</b><span>{d}</span><span class="ds-badge" data-phase="{s}">{s}</span></div>'
                 for i, (s, n, d) in enumerate(PHASES))
rows = "".join(f'<tr><td class="id">{i + 1}</td><td class="what">{w}</td><td class="who">{o}</td><td class="src">{s}</td><td>{b}</td></tr>' for i, (w, o, s, b) in enumerate(ISSUES))
trows = "".join(f'<tr><td class="first">{a}</td><td>{b}</td><td>{c}</td></tr>' for a, b, c in TESTS)
drows = "".join(f'<tr><td class="first"><b>{a}</b></td><td>{b}</td><td>{c}</td><td>{d}</td></tr>' for a, b, c, d in DECISIONS)

NEW = f'''<section class="c" id="ov-status">
  <header>
    <h1 class="sh-t">Status</h1>
    <p class="sh-meta">Concept A (D-182) &middot; 2026-11-23</p>
    <p class="summary">Designed and checked on paper, in SITL and the 3-D gates; 14 strict proof claims FAIL (2026-11-23, D-245). Nothing bought, built or flown.</p>
    <p class="use">Phases follow the concept A rounds ({L("qp/README.md", "qp/README.md")}). Done means the round delivered and its decisions are logged in CHANGE-LOG; it does not mean verified. Claims: strict build, 14 FAIL as of 2026-11-23 (run_all; earlier design, record: 0 failing) ({L("qp/A/proofs/out/CHAIN.md", "qp/A/proofs")}). The K09-L programme status stays in redesign/STATUS.md as the record.</p>
  </header>
  <div class="progress"><span>Programme progress</span><span class="ds-num">{nd} done &middot; {npart} partial &middot; {nn} not started</span><div class="track">{track}</div></div>
  <div class="phases">{phases}</div>

  <h3 class="ds-h2">Top open issues</h3>
  <div class="scroll">
    <table class="ds-table" id="issues">
      <thead><tr><th>#</th><th>Issue</th><th>Owner</th><th>Claim / source</th><th>Status</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </div>

  <h3 class="ds-h2" id="tests">What needs physical tests</h3>
  <p class="use">Nothing is VERIFIED: no part has been bought, weighed or flown. Each row names the test that closes it.</p>
  <div class="scroll"><table class="ds-table"><thead><tr><th>Item</th><th>State</th><th>Closes with</th></tr></thead><tbody>{trows}</tbody></table></div>
  <span class="ds-source">review/QP-4/BOARD.md s4, s6.2 &middot; review/QP-5/ARMS.md s7 &middot; qp/A/proofs/claims_a0_base.py (T-A-* tests)</span>
  <h3 class="ds-h2" id="next">Next steps: decisions only humans can make</h3>
  <div class="scroll wide"><table class="ds-table"><thead><tr><th>Decision</th><th>What and why</th><th>Who</th><th>By</th></tr></thead><tbody>{drows}</tbody></table></div>
  <span class="ds-source">qp/README.md "Before the main order" &middot; review/QP-4/BOARD.md &middot; params/CHANGE-LOG.md D-182 to D-241 &middot; regenerated by site/sync_status_a.py</span>

  <h3 class="ds-h2" id="status-key">Status key</h3>
  <p class="use">The words used on every page and in the 3-D explorer. A word always accompanies its colour. Wording follows redesign/design-system/README.md (rule 3).</p>
  <dl class="key">
    <div><dt><span class="ds-badge" data-status="PROPOSED">PROPOSED</span></dt><dd>Chosen by the team, not yet modelled. Shown as plain grey text, since most items are here.</dd></div>
    <div><dt><span class="ds-badge" data-status="MODELLED">MODELLED</span></dt><dd>Computed in CAD, a calculation or a simulation. Not measured.</dd></div>
    <div><dt><span class="ds-badge" data-status="CHECKED">CHECKED</span></dt><dd>Passed a stated check or gate (collision, assembly, SITL, reviewer). Not measured on hardware.</dd></div>
    <div><dt><span class="ds-badge" data-status="UNVERIFIED">UNVERIFIED</span></dt><dd>Stated but not yet checked against a source or test.</dd></div>
    <div><dt><span class="ds-badge" data-status="VERIFIED">VERIFIED</span></dt><dd>Measured on built hardware. Nothing is verified yet.</dd></div>
    <div><dt><span class="ds-badge" data-status="FAIL">FAIL</span></dt><dd>A negative margin against its limit.</dd></div>
    <div><dt><span class="ds-tag">EST</span></dt><dd>An estimate, not a measurement or a vendor figure.</dd></div>
    <div><dt><span class="ds-tag">V / U</span></dt><dd>In the BOM: V = price read on the vendor page; U = unverified price.</dd></div>
    <div><dt><span class="ds-tag">DONE / PARTIAL / NOT STARTED</span></dt><dd>Programme phase: the round delivered, delivered in part, or not begun. Done does not mean verified.</dd></div>
  </dl>
</section>'''

s = open(APP, encoding="utf-8").read()
a = s.index('<section class="view" id="status" hidden>')
i = s.index('<section class="c" id="ov-status">', a)
j = s.index('</section>\n\n  </div>\n</section>', i) + len('</section>')
assert j < s.index('<section class="view" id="bom" hidden>')
open(APP, "w", encoding="utf-8").write(s[:i] + NEW + s[j:])
print(f"Status tab: {nd} done, {npart} partial, {nn} not started; {len(ISSUES)} issues, {len(TESTS)} tests, {len(DECISIONS)} decisions")
