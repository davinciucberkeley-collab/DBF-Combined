-- RETIRED (D-256, 2026-11-24, AM-060): dropped from the concept A build; with the X2216 (D-227) every path set Q_M_SPIN_MAX 1.0, the A.param value.
--   Kept only so the earlier *_lua SITL runs (T-076, T-097, T-101) can be reproduced. Do not load it on the aircraft.
-- spin_cap.lua  (T-076, concept A O4b)  Voltage-scheduled Q_M_SPIN_MAX.
-- T-083 (D-227): SunnySky X2216 V3 880KV. cap(V_rest) = largest duty with ONE saturated motor + three hovering <= 24.94 A (450 W / 16.8 V x 12.1/13, EST),
-- 1.912 kg, from redesign/qp/A/prop_a.py cap_sched() (Kv 880, Rm 0.089, I0 0.5 A, pack R 30 mohm EST): 1.0 at every voltage (one motor 20.1 A fresh).
-- The pack limit (73 A all-four at full duty fresh) is held by Q_M_BAT_CURR_MAX 72 A in A.param, not here. The script now only ramps the cap from 0.90 to 1.0
-- and holds the 0.90 failsafe. Was (MN2212, 12.1 A, 1.64 kg): 15.4 V 0.992 .. 17.0 V 0.891.
-- Resting voltage: battery:voltage_resting_estimate(0) (AP_Scripting docs.lua, read 2026-11-19).
-- Rate limit: cap may fall at once (voltage rose) but rises at most RISE_PER_S per second.
-- Failsafe: unhealthy battery, nil / out-of-range reading (< 12.0 or > 17.2 V for 4S) -> FAILSAFE_CAP (T-083: 1.0 = the A.param value) and held there.
-- Parameters touched: Q_M_SPIN_MAX only (param:set, RAM; not saved).  Q_M_BAT_CURR_MAX must be set to 72 in the parameter file (T-083; was 45, T-074).
local UPDATE_MS    = 200
local RISE_PER_S   = 0.01
local FAILSAFE_CAP = 1.0    -- T-083: X2216 needs no cap; 0.90 would cut the sag window to +4.6 % (was 0.90, MN2212)
local V_MIN, V_MAX = 12.0, 17.2
local CAP_FLOOR = 0.90   -- Q_M_SPIN_MAX documented range 0.9-1.0 (AP_MotorsMulticopter.cpp, read 2026-11-19); a 4S pack does not rest above 16.8 V so this binds only on a bad but in-range reading
local TABLE = { {15.4, 1.000}, {17.0, 1.000} }  -- T-083: V_rest, cap (X2216: 1.0 everywhere); above 17.0 hold the last, below 15.4 cap = 1.0

local function cap_of_raw(v)
  if v <= TABLE[1][1] then return 1.0 end
  for i = 1, #TABLE - 1 do
    local a, b = TABLE[i], TABLE[i + 1]
    if v <= b[1] then return a[2] + (b[2] - a[2]) * (v - a[1]) / (b[1] - a[1]) end
  end
  return TABLE[#TABLE][2]
end

local function cap_of(v) return math.max(CAP_FLOOR, cap_of_raw(v)) end

local cur = nil          -- cap currently applied
local failed = false
local last_ms = nil
local last_msg = -100000

local function set_cap(c)
  if param:set("Q_M_SPIN_MAX", c) then cur = c end
end

local function update()
  local v = nil
  if battery:healthy(0) then v = battery:voltage_resting_estimate(0) end
  if failed or v == nil or v ~= v or v < V_MIN or v > V_MAX then
    if not failed then gcs:send_text(4, "spin_cap: bad battery reading, SPIN_MAX failsafe") end
    failed = true
    if cur ~= FAILSAFE_CAP then set_cap(FAILSAFE_CAP) end
    return update, UPDATE_MS
  end
  local target = cap_of(v)
  local now = millis():tofloat()
  local dt = last_ms and (now - last_ms) * 0.001 or 0.0
  last_ms = now
  if cur == nil then
    set_cap(math.min(target, FAILSAFE_CAP))           -- first pass: start at or below the failsafe cap and ramp up
  elseif target <= cur then
    set_cap(target)
  else
    set_cap(math.min(target, cur + RISE_PER_S * dt))
  end
  if now - last_msg >= 10000 then last_msg = now; gcs:send_text(6, string.format("spin_cap V %.2f cap %.3f", v, cur or -1)) end
  return update, UPDATE_MS
end

gcs:send_text(6, "spin_cap.lua loaded")
return update, UPDATE_MS
