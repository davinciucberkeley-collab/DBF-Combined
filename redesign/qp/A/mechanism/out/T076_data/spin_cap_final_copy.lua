-- spin_cap.lua  (T-076, concept A O4b)  Voltage-scheduled Q_M_SPIN_MAX.
-- cap(V_rest) = largest duty with ONE saturated motor + three hovering <= 12.1 A (A-P16), 1.64 kg, from redesign/qp/A/prop_a.py cap_sched()
-- (illustrative motor model: Kv 780, Rm 0.173, I0 0.5 A EST, pack R 30 mohm EST).  Values below are rounded DOWN at the 3rd decimal.
-- Resting voltage: battery:voltage_resting_estimate(0) (AP_Scripting docs.lua, read 2026-11-19).
-- Rate limit: cap may fall at once (voltage rose) but rises at most RISE_PER_S per second.
-- Failsafe: unhealthy battery, nil / out-of-range reading (< 12.0 or > 17.2 V for 4S) -> 0.90 (the A.param value, A-P16 fixed-cap case) and held there.
-- Parameters touched: Q_M_SPIN_MAX only (param:set, RAM; not saved).  Q_M_BAT_CURR_MAX must be set to 45 in the parameter file (T-074).
local UPDATE_MS    = 200
local RISE_PER_S   = 0.01
local FAILSAFE_CAP = 0.90
local V_MIN, V_MAX = 12.0, 17.2
local CAP_FLOOR = 0.90   -- Q_M_SPIN_MAX documented range 0.9-1.0 (AP_MotorsMulticopter.cpp, read 2026-11-19); a 4S pack does not rest above 16.8 V so this binds only on a bad but in-range reading
local TABLE = { {15.4, 0.992}, {15.6, 0.978}, {16.0, 0.952}, {16.4, 0.926}, {16.8, 0.903}, {17.0, 0.891} }  -- V_rest, cap; above 17.0 hold the last, below 15.4 cap = 1.0

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
    if not failed then gcs:send_text(4, "spin_cap: bad battery reading, SPIN_MAX 0.90") end
    failed = true
    if cur ~= FAILSAFE_CAP then set_cap(FAILSAFE_CAP) end
    return update, UPDATE_MS
  end
  local target = cap_of(v)
  local now = millis():tofloat()
  local dt = last_ms and (now - last_ms) * 0.001 or 0.0
  last_ms = now
  if cur == nil then
    set_cap(math.min(target, FAILSAFE_CAP))           -- first pass: start at or below 0.90 and ramp up
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
