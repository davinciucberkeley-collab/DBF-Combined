# Proof chains

Every engineering claim in the redesign, traced to the calculation that produced it, the parameters that calculation
read, and the sources behind those parameters, in one graph. You can read it as text (`CHAIN.md`) or explore it in
3-D (`viewer/`). The tools do not depend on the aircraft configuration. They are shown here on a small demo aircraft
in `examples/`.

| You want to… | Run (from the repo root) | Time |
|---|---|---|
| Rebuild the graph and confirm every stored number | `python -I redesign/proofs/build_graph.py` | < 1 s |
| The same for the demo aircraft | `python -I redesign/proofs/build_graph.py --examples` | < 1 s |
| Fail on negative margins too (release gate) | `python -I redesign/proofs/build_graph.py --strict` | < 1 s |
| Read the chains | open `redesign/proofs/out/CHAIN.md` (demo: `examples/out/CHAIN.md`) | — |
| Explore in 3-D | open `redesign/proofs/viewer/index.html` (double-click works, no server) | — |
| Self-test the tools | `python -I redesign/proofs/test_proofs.py` and `node redesign/proofs/viewer/check_viewer.js` | ~1 s |

Format and status rules: [`SCHEMA.md`](SCHEMA.md). Python 3 standard library only.

## How an analysis script emits claims

Use [`proofkit.py`](proofkit.py). The working pattern is in [`examples/power/analysis.py`](examples/power/analysis.py).

```python
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "proofs"))   # adjust depth to reach redesign/proofs
import proofkit as pk

kit = pk.Kit(__file__, params=["../../params/params.json"])        # paths relative to this script

@kit.calc("CALC-AERO-STALL", equation="Vs = sqrt(2 m g / (rho S CLmax))",
          inputs={"m": "CL-MASS-MTOW", "S": "P:wing.area_m2", "rho": "P:env.rho", "CLmax": "ASM-AERO-CLMAX"},
          units={"S": "m2", "rho": "kg/m3"}, output="Vs")
def stall_speed(m, S, rho, CLmax):
    return (2 * m * 9.80665 / (rho * S * CLmax)) ** 0.5

kit.claim("CL-AERO-STALL", "Stall speed at MTOW", calc="CALC-AERO-STALL", output="Vs", unit="m/s",
          limit=("<=", "P:requirements.stall_max"), verifies=["R-STALL"], parts=["WNG-001"],
          how="Slow-flight stall at MTOW with airspeed logging.")

if __name__ == "__main__":
    kit.write()            # runs the calcs, writes claims.json beside the script, prints value + margin per claim
```

Rules (each one keeps the re-check cheap and honest):

1. **Inputs are node ids, never typed numbers.** Use `P:<key>` for a `params.json` value, another claim's id for its
   value (also from another folder: proofkit finds it), or an `ASM-…` assumption. Add a constant with its source to
   `params.json` (for example `env.g_ms2`, cited to `SRC-…`).
2. **A calculation is a pure function of its named inputs.** `build_graph.py` imports your script and calls the
   function again with the current parameters. Keep the script's top level free of side effects (`if __name__ == "__main__":`).
3. **Re-run your script after any parameter change** that affects it. If you do not, the build fails with
   `DRIFT CALC-…: stored X, re-runs to Y. Changed inputs: batt 0.82 -> 0.95 (P:mass.battery_kg). Re-run <script>`.
4. **Every claim needs a `how`** (how to verify) and, where it is about hardware, `parts` (ids from `interfaces.json`).
5. **Declare sources and assumptions** with `kit.source(...)` / `kit.assumption(...)`, or in a hand-written
   `claims.json` (see `examples/requirements/claims.json`). Give a source a `checked` date only after you have compared
   the value with the source. Mark a guess `status="UNVERIFIED"`.
6. **Record tests** with `kit.test(...)`: `state="planned"` now; when it has run, `state="run", result="pass"`,
   `measured=…`, `evidence=<file>`. A passed run test makes the claim `VERIFIED`.

You never type a claim's status. `build_graph.py` works it out from the evidence (`PROPOSED` → `CHECKED` →
`VERIFIED`, or `UNVERIFIED` with the reasons listed) and marks any claim with a negative margin `FAILS`. One
`claims.json` per script. If two scripts share a folder, pass `out="claims.<name>.json"` to `Kit`.

## What the build checks

The build fails (exit 1, every problem printed at once) when:

- a calculation does not re-run to its stored outputs (drift);
- a claim's value differs from its calculation's output;
- an id is unknown or duplicated;
- one parameter key has two different values in two files;
- a declared input unit differs from the parameter's unit (`mm` vs `m`).

With `--strict`, a negative margin or a requirement that no claim verifies also fails the build. Missing part ids and
sources without a URL produce warnings. The graph and `CHAIN.md` are still written when the build fails, with the
errors at the top, so you can see what broke.

## The viewer

`viewer/index.html` loads `out/graph.js` (written next to `graph.json` so the page works from `file://`). If the real
graph has no claims yet, it falls back to the demo aircraft and says so.

- **Search** (`/`): ids, titles, equations.
- **Click a node** to see its value against its limit and its margin, the calculation (equation, inputs with values and
  where each comes from, outputs), the source links, the path **up to the requirement**, and the tree **down to the
  sources**. Each part id links to the aircraft viewer (`redesign/viewer/index.html#part=<id>`; change it with
  `build_graph.py --part-link`).
- **Status chips**: the first click shows only that status (click `UNVERIFIED` to list everything still to check);
  `Fails only` shows negative margins and failed tests. The list on the left follows the filters.
- **Colour by** status or type. **Layered** puts sources at the bottom and requirements at the top. **2D** is the
  low-power fallback (canvas, one shape per type) and is chosen automatically when WebGL is missing.
- Light/dark follows the system; the ◐ button overrides it. Shareable URLs: `#node=CL-…`, `?data=examples`,
  `?mode=2d`, `?theme=dark`, `?layout=layered`, `?graph=<url of a graph.json>`.

The page computes no engineering number. It only draws what `build_graph.py` wrote. Libraries are vendored in
`viewer/vendor/` (versions, licences and hashes: [`viewer/vendor/README.md`](viewer/vendor/README.md)). It works offline
and from GitHub Pages if the repo, or `redesign/`, is published.

## Files

| Path | What |
|---|---|
| `SCHEMA.md` | node and edge types, status rules, build rules |
| `proofkit.py` | what analysis scripts import (`Kit`, `@kit.calc`, `kit.claim`, …) and the shared engine |
| `build_graph.py` | merge, re-compute, status, write `out/graph.json`, `out/graph.js`, `out/CHAIN.md` |
| `test_proofs.py` | breaks a copy of the demo on purpose (drift, unit, bad id) and checks the build catches it |
| `viewer/` | `index.html`, `app.js` (UI), `model.js` (chain logic, also run by `check_viewer.js` in Node) |
| `examples/` | demo aircraft: `params.json`, `interfaces.json`, `requirements/claims.json` (hand-written), `power/` and `wing/` analysis scripts with their `claims.json`, `out/` |
| `out/` | the real graph (empty until subsystem/analysis agents write `claims.json` files) |

The demo shows all the cases: a claim `VERIFIED` by a run test (mass), `CHECKED` claims (hover T/W, spar), a claim
`UNVERIFIED` because it rests on a guessed `CLmax` (stall), one because a source was never checked (main disconnect),
and one that `FAILS` (an XT60 rated 30 A against 1.25 × 27.7 A). Its numbers are real catalogue values where a source
is cited. The masses and geometry are illustrative, and the weigh test is labelled illustrative.
