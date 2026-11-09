# Simulation tools available on the design machine

Analysis agents may use these (and only these — do not install software). Every simulation must be scripted and
re-runnable from the repo, record its inputs from `params.json`, state its mesh/convergence check, and emit claims
for the proof chain.

| Tool | Path / import | Use for |
|---|---|---|
| XFOIL 6.x | `C:/Users/dillo/tools/xfoil/xfoil.exe` | 2D airfoil polars, Re sweeps, transition, control-surface hinge moments |
| AVL 3.52 | `C:/Users/dillo/tools/avl/avl352.exe` | Vortex-lattice: lift distribution, induced drag, stability derivatives, neutral point, trim, control authority |
| SU2 (CFD + linear elasticity FEM) | `C:/Users/dillo/tools/su2/bin/bin/SU2_CFD.exe` (+ `SU2_DEF.exe`) | 3D/2D RANS/Euler where justified; `SOLVER= ELASTICITY` for structural FEA on gmsh meshes |
| gmsh (Python API) | `import gmsh` | Meshing for SU2 (CFD and FEA) |
| NumPy 2.5 / SciPy 1.18 | `import numpy, scipy` | Beam/plate models, sizing, ODE flight dynamics, optimisation |
| Matplotlib | `import matplotlib` | Plots (follow `redesign/design-system/` styling) |
| Blender 4.2.3 | `C:/Users/dillo/tools/blender/blender-4.2.3-windows-x64/blender.exe` | Renders, animations, GLB export (via `redesign/blender/`) |
| ArduPilot SITL | not installed | Flight-control agents write parameter files and test plans; mark SITL runs `UNVERIFIED` |

Previous usage patterns worth reusing: `analysis/` (XFOIL/AVL drivers, `cfd3d/` SU2 cases, validation scripts),
`tools/opencae-studio/` (CalculiX/SU2 desktop app — CalculiX itself is not installed here).

Professional practice expected: state assumptions and load cases; mesh/grid convergence (at least 3 levels) for any
CFD/FEA result that drives a decision; compare against a hand calculation or published data; report margins of
safety with the factor used; keep each run's inputs, outputs and a one-paragraph summary in the agent's folder.
Buildability first: run detailed CFD/FEA only on geometry the designers have settled.
