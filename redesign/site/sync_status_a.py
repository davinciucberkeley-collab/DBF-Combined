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
    ("PARTIAL", "Enclosed wiring", "C8 (D-199): phase leads enclosed from motor to ESC (arm tubes, hub conduits, raceway under the tray, foam ditch, bay cover), servo leads in foam grooves; exposed wire 9.09 to 0.87 strand-m; pitot tube run not designed"),
    ("NOT STARTED", "Order 1 and bench", "bench kit early December: thrust, current, yaw (M1 to M4), elevon coupon E1, weigh-in, hub and cup coupons"),
    ("NOT STARTED", "Main order", "gates G1 to G9 (QP-4 BOARD s4); latest safe date 28 Dec"),
    ("NOT STARTED", "Build and tethered hover", "January to February; lifeboat (ZOHD Altus) if no tethered hover by 15 Feb 2027"),
    ("NOT STARTED", "Flight test", "transition round trip and the mission profile, by 30 April 2027"),
]

ISSUES = [
    ("<b>Exposed wiring</b> (hard constraint C8): after D-199, 0.87 strand-m are still outside the skin (was 9.09; 0.60 without the vendor pack leads). The phase run is enclosed. What is left: vendor pack leads and the battery tail to the cover slot, short RX / airspeed / servo lead stubs, and the pitot silicone tube, which is not designed (0.45 m from the probe to the sensor, needs a foam groove across the spar).",
     "harness, CAD", "CLAUDE.md C8; " + L("review/QP-5/HARNESS-ENCLOSED.md", "HARNESS-ENCLOSED.md") + " s5", B("FAIL", "OPEN")),
    ("<b>Hub arm-socket wall</b>, 2.0 mm over the 12 mm mouth: the rough hoop check passes only with a 12 mm bearing patch (MS +0.05; <b>-0.47</b> at 6 mm).",
     "structures, bench", "ASM-A-HUB-WALL, D-196, " + L("qp/A/structures/qp5_checks.md", "qp5_checks.md") + " s2", B("UNVERIFIED")),
    ("<b>Mass has about 4 g of room</b>: predicted 1,455.6 g against the 1.46 kg target (weigh-in gate 1.47 kg) after D-198; most of the estimated cuts must prove real at the weigh-in.",
     "mass (A3)", "CL-A-MASS-PRED, CL-A-CUTS-REQUIRED, " + L("qp/A/MASS-GATE.md", "MASS-GATE.md") + " s11", B("UNVERIFIED")),
    ("<b>Elevon flutter</b> is cleared only with the silicone-fluid hinge damper (lowest onset 38.5 m/s hot against the 28.8 m/s line); the coupon must show K &ge; 2, free play &le; 0.5&deg;, damping &ge; 1 %.",
     "structures (C1, C2)", "G8, D-188, " + L("qp/A/structures/flutter_d195.md", "flutter_d195.md"), B("UNVERIFIED")),
    ("<b>Gusty hover heading</b>: excursion 25.4&deg; in one of seven turbulence seeds (8.5-14.0&deg; in the rest); flown with the pilot holding heading.",
     "flight controls", "A-P8a, " + L("review/QP-5/ANALYSES.md", "QP-5/ANALYSES.md"), B("UNVERIFIED", "MARGINAL")),
    ("<b>Prop adapter and spinner nut</b> (28.8 g, in the CAD) have no BOM line; G7 keeps only about $5 of room at +30 % if they must be bought. Ask T-Motor whether the hardware pack includes them.",
     "procurement", "D-194, review/QP-5/CAD-INTEGRATION.md s4", B("UNVERIFIED")),
    ("<b>S5010 CLmax and the neutral point</b> are estimates (no measured CLmax found); static margin 8.0 % against 5 %.",
     "aero", "ASM-A-NP, " + L("qp/A/aero_s5010.py", "aero_s5010.py"), B("UNVERIFIED", "EST")),
    ("<b>Elevon linkage sweep</b> is checked by the arm-angle table only; the collision poses move the elevon but leave the pushrod and servo arm at neutral.",
     "CAD", "review/QP-5/CAD-INTEGRATION.md s1", B("UNVERIFIED")),
    ("<b>D-195 sign-off</b>: design target 1.44 to 1.46 kg and CG band forward edge 20 to 19 mm need the aero lead's (A1) sign-off.",
     "A1", "params/CHANGE-LOG.md D-195", B("PROPOSED")),
]

TESTS = [
    ("Motor thrust, hover power, one-motor current and can temperature, yaw torque", "model only (APC data, mission_gate_a.py)", "bench M1-M4 on Order 1 (G1-G4), by 17 Dec"),
    ("Elevon stiffness, free play, damping, lead-bond pull", "model only (D-188 damper)", "elevon coupon E1 (G8), by 18 Dec"),
    ("Foam density, printed parts, epoxy, lead strip, servo mass", "CAD and estimates", "weigh-in (G6): at least 40.8 g of the estimated cuts real"),
    ("Hub socket wall and motor cup", "analysis (D-196, D-197)", "coupons: hub pull 1.5 x 332 N; cup axial 65 N, transverse 65 N at 35 mm, torque 5.2 / 3.0 N&middot;m; pull one screw from a real motor"),
    ("Motor and cup heat", "not analysed", "30 min thrust-stand soak per motor with a tap test before and after; cup plate &le; 55 &deg;C (EST)"),
    ("Cage and fin vibration modes", "FE (structures/iter3_run.md)", "tap test within &plusmn;20 % of FE (T-A-TAP)"),
    ("CG and neutral point", "CAD (CG 21.1 mm; NP 40.7 mm EST)", "knife-edge CG breadboard (T-A-CG-BREADBOARD)"),
    ("IMU vibration in hover", "model", "first tethered hover, VIBE &lt; 30 m/s&sup2; (T-A-TETHER-VIBE)"),
]

DECISIONS = [
    ("T-Motor stock and lead time for the MN2212", "ask now; no answer by 4 Dec means buy all 5 motors in Order 1 ($1,123.02)", "team member", "4 Dec"),
    ("Order 1 go, with the 3 ES3054HV servos pulled forward", "+$46.27, same total (D-J6-5); lets the elevon coupon run in December", "team lead", "early Dec"),
    ("Written booking plan for test mornings from 8 Feb", "at least 4 mornings a week (G9); 5 suggested after the 4 m/s wind limit (D-192)", "team", "18 Dec"),
    ("Main order go / no-go", "after G1-G9 close (QP-4 BOARD s4)", "team lead and board", "28 Dec"),
    ("Lifeboat trigger", "buy the ZOHD Altus VTOL if there is no tethered hover by 15 Feb 2027", "team lead", "15 Feb"),
    ("Declare the design final", "starts the concept A simulation round and brings back the Simulations tab (held until then, 2026-11-15)", "team lead", "&mdash;"),
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
    <span class="secno">Status &middot; concept A (D-182) &middot; 2026-11-15</span>
    <h2 class="ds-h1">Designed and checked on paper, in SITL and the 3-D gates. Nothing bought, built or flown.</h2>
    <p class="use">Phases follow the concept A rounds ({L("qp/README.md", "qp/README.md")}). Done means the round delivered and its decisions are logged in CHANGE-LOG; it does not mean verified. Claims: strict build, 0 failing ({L("qp/A/proofs/out/CHAIN.md", "qp/A/proofs")}). The K09-L programme status stays in redesign/STATUS.md as the record.</p>
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
  <span class="ds-source">qp/README.md "Before the main order" &middot; review/QP-4/BOARD.md &middot; params/CHANGE-LOG.md D-182 to D-198 &middot; regenerated by site/sync_status_a.py</span>
</section>'''

s = open(APP, encoding="utf-8").read()
a = s.index('<section class="view" id="status" hidden>')
i = s.index('<section class="c" id="ov-status">', a)
j = s.index('</section>\n\n  </div>\n</section>', i) + len('</section>')
assert j < s.index('<section class="view" id="bom" hidden>')
open(APP, "w", encoding="utf-8").write(s[:i] + NEW + s[j:])
print(f"Status tab: {nd} done, {npart} partial, {nn} not started; {len(ISSUES)} issues, {len(TESTS)} tests, {len(DECISIONS)} decisions")
