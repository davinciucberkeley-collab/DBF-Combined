"""H2 flight-test plan checks (closure round 2026-11-14). Read-only: prints PASS / FAIL lines, writes nothing.

Run:  python -I redesign/team/H2/plan_checks.py
Sources are named next to each input. EST marks an H2 estimate.
"""
import math

G = 9.807                      # m/s2, params env.g_ms2
BANK = math.radians(30)        # A2 closure 2.1 / H3 FLIGHT-CARD 4b racetrack bank
FENCE_R = 250.0                # K09L.param l.407 FENCE_RADIUS
FENCE_ALT = 110.0              # K09L.param l.405 FENCE_ALT_MAX (breach test has no margin: AC_Fence.cpp, ArduPilot-4.7)
CEILING = 400 * 0.3048         # m, 400 ft AGL, H3 FLIGHT-CARD l.20 (mission.ceiling_ft_agl)
WIND = 5.0                     # m/s mean, flight-card limit
V_CRUISE = 17.0                # performance.cruise_ms
LAP_PASS, LAP_FAIL = 55.7, 68.0  # s, A2 closure M2
CLIMB_TRANS = 49.5             # m, B3 closure 1.3 CL-B3-TRANS-CLIMB (high edge, incl. 2.0 s pre-climb)
LAND_PER_CART = 2.6143         # CL-C5-LANDINGS-PER-CARTRIDGE (graph 2026-11-14 23:26)
lines = []


def chk(name, ok, text):
    lines.append(f"{'PASS' if ok else 'FAIL'} {name}: {text}")


def r_turn(vg):
    """Ground turn radius that keeps bank <= 30 deg at ground speed vg (steady wind)."""
    return vg ** 2 / (G * math.tan(BANK))


def lap(L, V, w):
    """Ground-fixed racetrack, straights along the wind. Ground radius set by the fastest ground speed V + w.
    Turn time = integral of R dpsi / Vg(psi), Vg = w cos psi + sqrt(V^2 - w^2 sin^2 psi)."""
    R = r_turn(V + w)
    n = 3600
    t_turn = sum(R * (2 * math.pi / n) / (w * math.cos(p) + math.sqrt(V ** 2 - (w * math.sin(p)) ** 2))
                 for p in ((i + 0.5) * 2 * math.pi / n for i in range(n)))
    t_str = L / (V + w) + L / (V - w) if w else 2 * L / V
    return t_str + t_turn, L / 2 + R, R


# 1. Gate 9 / M2: 300 m racetrack at 17 m/s
for w in (0.0, WIND):
    t, far, R = lap(300, V_CRUISE, w)
    chk(f"G9 racetrack 300 m, wind {w:.0f}", far <= FENCE_R and t <= LAP_PASS,
        f"lap {t:.1f} s (M2 pass <= {LAP_PASS}), R {R:.1f} m, far point {far:.1f} m (fence {FENCE_R:.0f}, buffer {FENCE_R - far:.1f})")
# straight length that holds the calm A2 lap (54.2 s) and the 201 m far point at the 5 m/s card limit
L_ok = max(L for L in range(100, 301, 10) if lap(L, V_CRUISE, WIND)[0] <= 54.2 and lap(L, V_CRUISE, WIND)[1] <= 201)
t, far, R = lap(L_ok, V_CRUISE, WIND)
chk(f"G9 racetrack {L_ok} m, wind 5", True, f"lap {t:.1f} s <= 54.2, far point {far:.1f} m; calm lap {lap(L_ok, V_CRUISE, 0)[0]:.1f} s")
# day table: longest straight (10 m steps) whose lap stays <= 54.2 s at the measured mean wind
for w in range(0, 6):
    Lw = max(L for L in range(50, 301, 10) if lap(L, V_CRUISE, w)[0] <= 54.2)
    t, far, _ = lap(Lw, V_CRUISE, w)
    chk(f"G9 straight for wind {w}", far <= 201.05, f"{Lw} m: lap {t:.1f} s, far {far:.1f} m (300 m would lap {lap(300, V_CRUISE, w)[0]:.1f} s)")

# 2. Gate 5 legs: 200 m straights, the same ground pattern at every speed
L5 = 200.0
for V in (14.0, 16.0, 17.0, 18.0):
    t_calm = L5 / V
    _, far_w, R_w = lap(L5, V, WIND)
    chk(f"G5 leg {V:.0f} m/s", t_calm <= 20 and far_w <= FENCE_R - 25,
        f"leg {t_calm:.1f} s calm (<= 20), upwind leg {L5 / (V - WIND):.1f} s at 5 m/s; far point {far_w:.1f} m at 5 m/s "
        f"(R {R_w:.1f}), buffer {FENCE_R - far_w:.1f} m (>= 25 EST)")
# what the old card asked for: 60 s legs
for V in (14.0, 16.0, 18.0):
    chk(f"old 60 s leg at {V:.0f} m/s", 60 * V <= 2 * FENCE_R, f"{60 * V:.0f} m vs fence diameter {2 * FENCE_R:.0f} m")

# 3. Transition top vs the altitude fence and the legal ceiling
for h0 in (50.0, 55.0):
    top = h0 + CLIMB_TRANS
    chk(f"transition from {h0:.0f} m", top < FENCE_ALT and top < CEILING,
        f"top {top:.1f} m: {FENCE_ALT - top:.1f} m under FENCE_ALT_MAX {FENCE_ALT:.0f}, {CEILING - top:.1f} m under 400 ft")

# 4. Touchdowns per sortie vs the cartridge claim
TD = 1 + 1   # one landing + at most one go-around touchdown (this plan, section 4)
chk("touchdowns per sortie", LAND_PER_CART >= TD, f"{LAND_PER_CART:.2f} landings per cartridge >= {TD} (margin {LAND_PER_CART / TD - 1:+.1%})")

# 5. Schedule: flight mornings needed per I2 block (I2 SCHEDULE.md I2-R2); 2 sorties / morning (CL-E2-SORTIES-PACKS)
UM = 5.0 / 7   # usable mornings per day, low end Mar-Apr (config-study/tiebreak/DECISION.md l.68); Feb: unknown
blocks = [  # (task, gates, days, mornings needed EST, basis)
    ("F01", "3", 3, 2, "weigh-in + 4 tethered sorties"),
    ("F02", "4", 8, 5, "20 touchdowns at 2 per sortie = 10 sorties"),
    ("F04", "6-7", 7, 3, "6 round-trip sorties (transition, half lap, back-transition)"),
    ("F03", "5", 9, 4, "8 sorties: autotune, stall x3, dive, level leg, airspeed cal, polar 3 x 3 laps, M2"),
    ("F05", "7-8", 12, 5, "20 touchdowns after a back-transition = 10 sorties"),
    ("F06", "9", 16, 3, "full missions, >= 3 logged EST"),
]
for task, gates, days, need, basis in blocks:
    have = days * UM
    chk(f"{task} gate {gates}", have >= need, f"{need} mornings needed ({basis}), {have:.1f} usable in {days} d")
chk("first hover", True, "F01 12 Feb 2027 (I2-R2), latest 24 Feb (A2 2.5); I2-R1 fallback 22 Feb also meets")
chk("end date", True, "F06 ends 18 Apr with CR1 (11 d) inside; 12 d slack to 30 Apr (I2 SCHEDULE.md l.15, 31)")

print("\n".join(lines))
print(f"\n{sum(l.startswith('PASS') for l in lines)} PASS, {sum(l.startswith('FAIL') for l in lines)} FAIL "
      "(expected FAILs, shown for the record: the three retired 60 s legs and the fixed 300 m track at 5 m/s, which the wind table replaces)")
