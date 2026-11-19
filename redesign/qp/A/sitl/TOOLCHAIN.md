# SITL toolchain for concept A (record, 2026-11-19)

The concept A SITL runs (`run_fwd.py`, `fwd_sum.py`) need an ArduPlane SITL binary and a Python venv with pymavlink.
Neither is in the repo. Until 2026-11-19 they lived only in a temporary session scratchpad (session dd3758e5),
which can be cleared at any time. They are now copied to a durable folder outside the repo (T-058 open item 4).

| Item | Value | Source |
|---|---|---|
| Location | `C:/Users/dillo/tools/ardupilot-sitl/` (`sitl/` binary + Cygwin DLLs, `src/` parameter files and patched sources) | copied 2026-11-19 from the dd3758e5 scratchpad |
| Binary | `sitl/ArduPlane.elf`, Cygwin x86_64 SITL build, g++ 13.5.0 | `sitl/build.txt` |
| SHA-256 | `de67d448946ccdf5f8c77f6ba5383086f040a34ae6014921fe3f50b4d935aacc` | `sha256sum`, 2026-11-19 |
| ArduPilot source | commit `bf693f316b0144fb4fac3893956f80f4c277fa3f` ("Plane: version to 4.7.3-beta1", 2026-10-13) | `sitl/git.txt` |
| Parameter files | `src/quadplane.parm`, `src/quadplane-copter_tailsitter.parm`, `src/plane.parm` | `src/` |
| Python | 3.14.2 venv; `fastcrc==0.5.0`, `lxml==6.1.3`, `pymavlink==2.4.50` | `requirements-venv.txt` (pip freeze of the old venv) |

Venv recreated there on 2026-11-19 (`venv/`, imports checked). To rebuild it:

```
python -m venv C:/Users/dillo/tools/ardupilot-sitl/venv
C:/Users/dillo/tools/ardupilot-sitl/venv/Scripts/python.exe -m pip install -r C:/Users/dillo/tools/ardupilot-sitl/requirements-venv.txt
```

Point the runner at it the way the 2026-11-19 rerun did (`SCR=<folder> $SCR/venv/Scripts/python.exe run_fwd.py ...`,
see `redesign/qp/A/mechanism/out/T057_T058_repro.md` section 1). Whether this binary is the one that produced the
2026-11-15 runs is not recorded ("-"); the 2026-11-19 Z5_gb0 rerun reproduced the categorical outcomes (AR-010).
