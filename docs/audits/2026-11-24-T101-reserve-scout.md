# T-101 scout: elevon deflection reserve beyond pitch demand (roll, gust, combination) (2026-11-24)

Role: scout. Records options with evidence; picks none, derives no final number. Date checked for every URL: 2026-11-24. Only pages opened in this run are cited. Unknowns are "—". Numbers marked "own calc" are my arithmetic from repo values, for orientation only.

## 0. Headline finding

- No source found gives a "reserve beyond pitch" rule for a small flying wing or tailsitter. D-245 and AR-017 say the same of the repo (the 0.60-of-15-deg line has no derivation).
- Roll: sourced criteria exist as time-to-bank (MIL-F-8785C Table IXa; FAR 23.157; Sadraey/Raymer-type method). None is scaled for a 0.9 m UAV in anything I opened. The repo's own A-P11 (>= 90 deg/s) is "SRC-A-REQ" with no derivation read here.
- Gust: sourced gust inputs exist (14 CFR 25.341 1-cos, Dryden sigma = 0.1 x W20). A conversion method to elevon deflection (alpha_g = w/V into the plant's trim moment) is first-order physics; no opened source states it for elevons.
- Combination: only ArduPilot documents the mixer as a linear sum (roll +/- pitch) with saturation. Mason et al. say the stochastic (gust) margin is added on top of the deterministic demand and "requires further research". No RSS source found.

## 1. (a) Roll authority

| # | Who | Link opened | Numbers |
|---|---|---|---|
| a1 | MIL-F-8785C Table IXa (DoD), Class I (small light airplane) | http://www2.coe.pku.edu.cn/tpic/2011971042474.pdf (11-page excerpt incl. 3.3.4) | Time to achieve a bank-angle change. Class I, Level 1: 1.3 / 1.7 / 1.3 s; Level 2: 1.7 / 2.5 / 1.8 s; Level 3: 2.6 / 3.4 / 2.6 s. Column headers in the extracted text are ambiguous. Table is laid out Category A (60, 45 deg), Category B (60, 45 deg), Category C (30, 25 deg); a search summary reads A 60 deg 1.3 s and B 60 deg 1.7 s. Which angle goes with which number is not confirmed here (read the original table before use). "Inputs shall be abrupt"; pitch control fixed; takeoff time may scale with roll inertia ratio. |
| a2 | Sadraey, "Aircraft Design: A Systems Engineering Approach" ch. 12 (aileron design) | https://aero.us.es/adesign/Slides/Extra/Stability/Design_Control_Surface/Chapter%2012.%20Desig%20of%20Control%20Surfaces%20%28Aileron%29.pdf (PDF converted with pdftotext) | Method: size ailerons on time to a bank angle at the lowest-speed phase, level 1. Worked example: Class II, Phase C, Level 1 requires 30 deg in 1.8 s. Quotes MIL-STD table "12.12" (table values not extractable here). Aileron span 60-80 % of wing span; typical deflection limits +/-25-30 deg (table 12.1 aircraft examples). Method steps: aileron rolling moment, steady roll rate Pss limited by roll damping, then time to bank. |
| a3 | KITPLANES "Design Process: Roll Control" | https://www.kitplanes.com/design-process-roll-control/ | FAR 23.157 style: below 6,000 lb, 30 deg bank one way to 30 deg the other within 5 s (takeoff) and 4 s (landing). Steady-state roll rate spec is "simple" but of limited use except fighters and aerobatic. Aileron also has to trim crosswind sideslip rolling moment and still leave roll power (not quantified). |
| a4 | Kay, Mason, Durham, Lutze, Benoliel, VPI-Aero-200 (1993), control authority in conceptual design | https://archive.aoe.vt.edu/mason/Mason_f/VPI-Aero-200.pdf (pdftotext) | Reproduces MIL-STD-1797 Table 4 (roll performance Class I and II). Low airspeed and gusts "traditionally place the greatest demands on control authority". Roll sizing is a deterministic demand; see section 3 for the stochastic margin. |
| a5 | ArduPilot parameter page | https://ardupilot.org/plane/docs/parameters.html | RLL2SRV_RMAX: max roll rate the attitude controller will demand, range 0-180 deg/s. ACRO_ROLL_RATE range 10-500 deg/s. RLL_RATE_SMAX: keep slew demand <= 25 % of the actuator maximum slew rate. No recommended roll rate and no elevon headroom rule. |
| a6 | ArduPilot elevon page | https://ardupilot.org/plane/docs/guide-elevon-plane.html | MIXING_GAIN default 0.5, "ensures that the mixer doesn't saturate". Gain above 0.5 can saturate when both inputs are on. See section 3. |
| a7 | ArduPilot tailsitter guide | https://ardupilot.org/plane/docs/guide-tailsitter.html | Fixed-wing mode uses the RLL_RATE and PTCH_RATE gains; MIXING_GAIN combines with vectored-thrust gains. No roll headroom rule. |

Options for the roll criterion (not picked):
- O-R1: MIL-F-8785C Class I Level 1 time-to-bank (1.3-1.7 s class), checked at cruise with the elevon at the deflection left after pitch.
- O-R2: FAR 23.157-style 30 to 30 deg reversal in 4-5 s (about 60 deg in 4-5 s, far lower rate than O-R1).
- O-R3: The repo's A-P11, steady roll rate >= 90 deg/s at cruise within +/-20 deg (D-195 SITL 106.9 / 106.4 deg/s). Derivation not read here (REQUIREMENTS-A.md A-P11 line, "—").
- O-R4: ArduPilot setting basis: RLL2SRV_RMAX = 150 in A.param (line 172); range 0-180.
- Scaling for small UAVs: none of the opened sources gives a scaled number. Time-to-bank scales with b/V in nondimensional roll (p b / 2V), so a 0.9 m wing at 17 m/s can be compared on that basis (own observation, no source).

## 2. (b) Gust

| # | Who | Link opened | Numbers |
|---|---|---|---|
| b1 | 14 CFR 25.341 (eCFR API, text as of 2024-12-01) | https://www.ecfr.gov/api/versioner/v1/full/2024-12-01/title-14.xml?part=25&section=25.341 | 1-cos discrete gust (shape equation not extracted; formula given as "for 0 <= s <= 2H"), gust gradient H 30-350 ft, reference gust 56.0 ft/s EAS (17.1 m/s) at VB-VC at sea level, 0.5 x at VD. Symmetric vertical and lateral gusts. Transport category: a size and mission mismatch to a UAV; shows the form only. |
| b2 | MathWorks Dryden continuous model | https://www.mathworks.com/help/aeroblks/drydenwindturbulencemodelcontinuous.html | Low altitude (< 1000 ft): sigma_w = 0.1 x W20, W20 = wind speed at 20 ft: light 15 kt (7.7 m/s), moderate 30 kt (15.4 m/s), severe 45 kt (23.1 m/s). Resulting sigma_w light about 0.77 m/s, moderate about 1.54 m/s (my conversion from knots; page prints values without units). High-altitude exceedance probabilities 1e-2 / 1e-3 / 1e-5 (light / moderate / severe). Page cites MIL-F-8785C / MIL-HDBK-1797 conventions. |
| b3 | Szabolcsi, low-altitude turbulence models for small UAV (Knowledge-Based Organization 2017) | https://reference-global.com/download/article/10.1515/kbo-2017-0165.pdf (pdftotext) | sigma_w = 0.1 u20 (cites MIL-STD-1797A); extreme weather sigma 7 m/s with L = 580 m; scale lengths Lu = 2 Lv = h / (0.177 + 0.000823 h)^1.2, Lw = 0.5 h. Example UAV (Boomerang-60, 19 m/s): elevator to vertical speed transfer function w/delta_e = 1.2965/(1+1.0034 s), i.e. a worked small-UAV gust-to-elevator example. Light/moderate/severe intensity table is garbled in extraction (values read: 0.85, 0.7, 0.45, 4.5; assignment unclear): not used. |
| b4 | Wind modelling for UAV simulation (ar5iv of arXiv 1905.09954) | https://ar5iv.labs.arxiv.org/html/1905.09954 | Von Karman sigma_w = 0.1 u20, below 610 m; gust amplitude fit vgust = (52/43) va_ir - 1/8 (m/s); gust duration 0.71 (vgust - va_ir) + 3.51 s; about 13.5 gusts per hour; Von Karman is MIL-F-8785C preferred. Dryden intensities by severity: not in page. |
| b5 | Mason et al. VPI-Aero-200 | https://archive.aoe.vt.edu/mason/Mason_f/VPI-Aero-200.pdf | Section 2.3.1: gust effects are not in their spreadsheet; MIL-STD-1797 gives turbulence intensity, gust length, magnitude and wind shear tables by severity (not reproduced). Flying qualities in light-to-moderate atmospheric disturbance must be Level 1 or Level 2 per Tables 9 and 10 (normal states, operational / service envelope). |
| b6 | Repo plant | `redesign/qp/A/sitl/a_plant.py` lines 19-20, 123-126 | 1-cos gust on top of mean wind (cfg gust, gust_s default 2.0 s rise) and OU turbulence (sigma `turb`, tau 2 s, vertical 0.5 x). Uses the plant for hover wind limits (4 / 6.4 m/s, SCHEDULE-A). Forward-flight gust-to-elevon case: none read. |

ASTM F3298: the standard's text was not opened (iTeh sample fetch returned an invalid file). No F3298 gust figure can be cited ("—"). Search results said gust envelope specifications for small UAS are not standardised; not used as evidence.

Method for converting a gust to elevon deflection (candidate, not sourced to an opened page; own calc, consistent with the plant terms in the 2026-11-23 scout section 2):
- Vertical gust w_g gives delta_alpha = w_g / V (small angle). Extra lift gives a pitching moment about the CG of CLA delta_alpha SM c q S. Holding attitude takes delta = c CLA delta_alpha SM / (|x_e| CLD) (the same moment balance as the trim formula).
- Illustration, plant values as read 2026-11-24 (CLA 3.737, SM 0.0761, c 0.245 m, |x_e| 0.1923 m, CLD 0.3226 at cf/c 0.25): w_g = 1 m/s at 17 m/s gives about 3.8 deg of static elevon to hold attitude (own calc). Dynamic response (pitch damping CMQ -1.0, loop) would reduce the peak demand; not computed.
- Roll from a gust (asymmetric/side) uses CLB -0.04 per rad (dihedral effect) and Clp; not computed.

Options for the gust criterion (not picked):
- O-G1: RFS limit gust 8 m/s with 5 m/s mean (SCHEDULE-A line 12): gust increment 3 m/s above the mean, applied as a 1-cos vertical gust at 17 m/s.
- O-G2: Dryden light or moderate sigma_w (0.77 / 1.54 m/s from b2) times a peak factor (3 sigma is not sourced here, "—").
- O-G3: a FAR-form reference gust scaled to the UAV (b1 shows the form only; no UAV scale found).

## 3. (c) Combining pitch, roll and gust on mixed elevons

| # | Who | Link opened | What it says |
|---|---|---|---|
| c1 | ArduPilot elevon plane page | https://ardupilot.org/plane/docs/guide-elevon-plane.html | LEFT ELEVON = (roll + pitch) x gain, RIGHT = (roll - pitch) x gain. Gain 0.5: full roll plus full pitch gives full travel (linear sum); above 0.5 the surfaces saturate when both inputs are on, and holding full roll while adding pitch reduces effective roll (one elevon already at its limit). Linear sum, no RSS, no priority. |
| c2 | ArduPilot parameter page (MIXING_GAIN) | https://ardupilot.org/plane/docs/parameters.html | MIXING_GAIN range 0.5-1.2; default 0.5 "ensures that the mixer doesn't saturate". The mixer allows outputs 900-2100 us. A.param uses 0.65 (line 52), SERVO5 1003-1976, SERVO6 1024-1997 us. |
| c3 | Mason et al. VPI-Aero-200 | https://archive.aoe.vt.edu/mason/Mason_f/VPI-Aero-200.pdf | Deterministic demands (trim, clean-air maneuvers) are repeatable; stochastic demands (turbulence, aerodynamic uncertainty) "should be included by allowing for a margin of control power beyond that required for the deterministic demands. The estimation of the size of the margin requires further research." Section 2.1.1.3: multi-surface allocation usually chosen for minimum trimmed drag. This is an additive-margin statement; no number, no RSS. |
| c4 | MIL-F-8785C excerpt | http://www2.coe.pku.edu.cn/tpic/2011971042474.pdf | 3.3.2.1: control response in atmospheric disturbances "shall be considered"; the roll-rate requirement is met with pitch control fixed (no combination rule). |
| c5 | A search result summarising multirotor mixer patents | not opened (search summary only; not used as evidence) | — |

Options for the combination (not picked):
- O-C1: Linear sum of pitch demand + roll demand + gust demand (conservative worst case; matches the ArduPilot mixer and the repo's metric style).
- O-C2: RSS of independent items (gust and roll commands uncorrelated). No source found; physical argument only. Marked "—".
- O-C3: Deterministic items summed (trim + pitch maneuver + roll command), stochastic gust margin added on top (Mason c3 wording).

## 4. Inputs a derivation needs, and where they live

| Input | Value | Where | Status |
|---|---|---|---|
| Wing span / area / chord / AR | 0.90 m / 0.22 m2 / 0.245 m / 3.68 | `sitl/a_aero.py` lines 9-11 | read |
| Lift slope CLA | 3.737 /rad (Helmbold, EST) | `a_aero.py` line 11 | read (computed) |
| Elevon effectiveness CLD | 0.3226 /rad of mean deflection at cf/c 0.25, tau 0.5 EST | `a_aero.py` EL_* lines | file changed during this run: at first read it had EL_CF 0.30 (EL_TAU 0.5 x ratio), at last read EL_CF 0.25; `git status` shows a_aero.py modified. Re-read at derivation time |
| Elevon span stations, centroid arm | y 0.04-0.35 m (mean y 0.195 m); centroid 192.3 mm aft of the CG at cf/c 0.25 (186.2 mm at 0.30) | `a_aero.py` | read |
| Roll damping Clp | -0.30 (EST, Helmbold-type); pitch damping CMQ -1.0; dihedral effect CLB -0.04 /rad | `a_aero.py` line 28-29 | EST, none measured |
| Roll moment per elevon deflection | Cl = EL_Y CLD delta / b = 0.0699 per rad (antisymmetric +/-delta, own calc from `a_aero.py` lines 105-108) | derived | own calc |
| Steady roll rate formula | p = (Cl_delta / -Clp) delta (2V / b) = 8.8 delta rad/s at 17 m/s; 9 deg gives about 79 deg/s, 20 deg about 176 deg/s (own calc, no roll-mode lag, no adverse yaw, linear aero) | derived | own calc. Compare D-195 SITL 106.9 deg/s (params-A.json `sim.roll_141_degs`) and A-P11 >= 90 deg/s |
| Roll moment of inertia | I_cad_axes Ixx 0.0882, Iyy 0.0351, Izz 0.0985 kg m2 | `sitl/cad_mass.json` | which axis is the forward-flight roll axis is not confirmed (A.param comment says I_z 0.05, I_y 0.03 EST); "—" until checked |
| Cruise speed | 17 m/s (AIRSPEED_CRUISE), AIRSPEED_MIN 16 | `A.param` lines 162, 164 | read |
| Mass, CG, SM | 1.881 kg EST; CG 22.049 mm aft of LE; NP 40.7 mm EST; SM 7.61 % | `params-A.json`, `a_aero.py` | per 2026-11-23 scout |
| Elevon limits | stops +/-20 deg; pitch-use line 0.60 x 15 deg = 9 deg; roll min 90 deg/s | `params-A.json` (`req.pitch_use_max`, `req.roll_min_degs`), D-245 | read |
| RFS wind limits | mean <= 5 m/s, gust <= 8 m/s (hover edge: 4 / 6.4 m/s per D-192 update, SCHEDULE-A lines 166-168) | `redesign/qp/A/SCHEDULE-A.md` line 12 | read; RFS wind unmeasured (0 of 3, SCHEDULE line 13); WN1 anemometer task planned |
| Mixer / servo settings | MIXING_GAIN 0.65; RLL2SRV_RMAX 150; SERVO5 1003-1976, SERVO6 1024-1997; ELEVON_OUTPUT not read | `A.param` lines 46-52, 172 | read |
| Gust plant | 1-cos gust and OU turbulence in the SITL plant | `sitl/a_plant.py` lines 19-20, 123-126 | read; cruise gust case none |
| Measured peaks to compare | pitch use 0.605-0.79 of 15 deg (T-097 / AR-015 / AR-017) | D-245, D-249, `T101_results.json` | read via 2026-11-23 scout and D-245 |

Open dependency: the elevon-chord ruling (cf/c 0.25 vs 0.30; AR-017 text I read reports C3 "old chord" and a new-chord result with rod force and hinge moment changes) changes CLD, |x_e| and every number above by about 1/1.26. The derivation should state which chord it uses.

## 5. Limits of this scout
- No source opened gives a reserve for a small flying wing or tailsitter. The MIL-F-8785C Class I table is for piloted airplanes; applying it to a 1.88 kg UAV is the team's decision.
- Table IXa column-to-angle alignment is ambiguous in the extracted text. MIL-HDBK-1797 / MIL-STD-1797A text was not opened (a DTIC fetch returned 403; the pku excerpt is MIL-F-8785C only).
- ASTM F3298, FAA/EASA small-UAS gust guidance: not opened, no numbers.
- No RSS combination source for control deflection found.
- The illustrative gust and roll-rate numbers are first-order own calcs; not a criterion.

## 6. Sources opened (2026-11-24)
Repo: docs/reference/agent-standard/LOCAL.md; docs/audits/2026-11-23-T101-scout-trim.md; redesign/params/CHANGE-LOG.md (D-245); docs/analysis-records.md (AR-017 head); redesign/qp/A/SCHEDULE-A.md (lines 12, 13, 166-168); params-A.json (roll_min_degs, pitch_use_max, sim.roll_*); A.param (lines 46-52, 162-172); sitl/a_aero.py; sitl/a_plant.py (lines 19-20, 118-126); sitl/cad_mass.json; REQUIREMENTS-A.md (A-P11 line). CLAUDE.md read as context.
Web:
- http://www2.coe.pku.edu.cn/tpic/2011971042474.pdf : MIL-F-8785C excerpt, 3.3.2.1, 3.3.4, Table IXa.
- https://aero.us.es/adesign/Slides/Extra/Stability/Design_Control_Surface/Chapter%2012.%20Desig%20of%20Control%20Surfaces%20%28Aileron%29.pdf : Sadraey ch. 12 aileron sizing method and Class II example.
- https://www.kitplanes.com/design-process-roll-control/ : FAR 23.157 roll-reversal times, time-to-bank vs rate.
- https://archive.aoe.vt.edu/mason/Mason_f/VPI-Aero-200.pdf : control authority, stochastic margin statement, gust section.
- https://ardupilot.org/plane/docs/parameters.html : MIXING_GAIN, RLL2SRV_RMAX, ACRO_ROLL_RATE, RLL_RATE_SMAX.
- https://ardupilot.org/plane/docs/guide-elevon-plane.html : elevon mixing formula and saturation.
- https://ardupilot.org/plane/docs/guide-tailsitter.html : fixed-wing gains, MIXING_GAIN with vectored thrust gains.
- https://www.ecfr.gov/api/versioner/v1/full/2024-12-01/title-14.xml?part=25&section=25.341 : 14 CFR 25.341 text.
- https://www.mathworks.com/help/aeroblks/drydenwindturbulencemodelcontinuous.html : Dryden W20 15/30/45 kt and sigma_w = 0.1 W20.
- https://reference-global.com/download/article/10.1515/kbo-2017-0165.pdf : Szabolcsi small-UAV turbulence model.
- https://ar5iv.labs.arxiv.org/html/1905.09954 : UAV wind/gust model, Von Karman sigma_w, gust amplitude fit.
- Failed or unusable: https://apps.dtic.mil/sti/pdfs/ADA119421.pdf (403); https://uwarg-docs.atlassian.net/wiki/x/GYCCnQ (empty); https://www.law.cornell.edu/cfr/text/14/23.333 (404); ecfr.gov section page for 23.2230 (redirect); iTeh ASTM F3298 sample (not a PDF).
