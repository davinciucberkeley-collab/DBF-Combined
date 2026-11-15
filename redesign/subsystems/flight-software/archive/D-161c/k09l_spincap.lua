-- k09l_spincap.lua: K09-L voltage-scheduled motor output cap (E1 "D-161 spin cap" section 5, A1 D-161b; owner F4).
--
-- Q_M_SPIN_MAX = min(0.93, 11.2 V / V_bus): each motor's average terminal voltage stays <= 11.2 V, so its winding
-- current stays <= 25 A in any attitude differential (E1), while a sagged pack still gets the output it needs for T/W.
--
-- Bindings (ArduPilot libraries/AP_Scripting/docs/docs.lua, tag Plane-4.7.2, read 2026-11-14):
--   param:set(name, value)        "set parameter value, this will not be retained over a reboot" (no EEPROM write)
--   param:get(name)               current value, nil if the parameter is not found
--   battery:voltage(instance)     measured (loaded) voltage of the battery monitor instance
--   battery:healthy(instance)     true while ArduPilot can monitor the battery
--   arming:get_aux_auth_id(), arming:set_aux_auth_passed(id), arming:set_aux_auth_failed(id, msg): script pre-arm check
--   gcs:send_text(severity, text), logger:write(name, labels, format, ...), millis()
--
-- Behaviour:
--   * runs every PERIOD_MS = 100 ms (10 Hz); V_bus low-pass filtered with TAU_S = 0.5 s;
--   * any error (battery unhealthy, voltage outside 9-18 V, a Lua error, SCR_USER1 = 99 test hook) sets the cap to
--     CAP_FAULT = 0.746 (never higher), fails the aux pre-arm check, and sends a critical message once;
--   * the saved Q_M_SPIN_MAX in K09L.param is 0.746, so the cap is 0.746 at boot until the script runs, and again
--     after any reboot. The script never saves (param:set only);
--   * if the scripting engine itself dies (out of memory, panic) the cap freezes at its last value and ArduPilot's
--     own scripting pre-arm check fails ("Scripting: ..."), so the aircraft cannot be re-armed. F4.md D-161c.
-- Log message SPNC: V (raw V_bus), Vf (filtered), Cap (set), F (1 = fault).

local CAP_MAX     = 0.93     -- E1: ceiling (the limiter binds below it at 3.60 V/cell)
local V_TERM      = 11.2     -- E1: terminal voltage at which one motor reaches 25 A winding (R_m -10 %)
local CAP_FAULT   = 0.746    -- E1 / A1: fall-back, fresh-pack value under four-motor load (never higher)
local PERIOD_MS   = 100
local TAU_S       = 0.5
local V_LO, V_HI  = 9.0, 18.0
local MAV_CRIT, MAV_INFO = 2, 6

local QUIET_MS    = 5000     -- no fault message in the first 5 s after boot (battery monitor not yet healthy; cap stays 0.746)

local boot_ms   = millis()
local auth_id   = arming:get_aux_auth_id()
local v_filt    = nil
local cap_now   = CAP_FAULT
local fault_msg = nil
local fault_sent = false

local function set_cap(c)
  if not param:set('Q_M_SPIN_MAX', c) then
    error('Q_M_SPIN_MAX not found')
  end
  cap_now = c
end

local function step()
  if param:get('SCR_USER1') == 99 then
    error('test fault (SCR_USER1 99)')
  end
  if not battery:healthy(0) then
    error('battery monitor 0 unhealthy')
  end
  local v = battery:voltage(0)
  if (v == nil) or (v < V_LO) or (v > V_HI) then
    error('V_bus out of range: ' .. tostring(v))
  end
  local dt = PERIOD_MS / 1000.0
  if v_filt == nil then
    v_filt = v
  else
    v_filt = v_filt + (dt / (TAU_S + dt)) * (v - v_filt)
  end
  set_cap(math.min(CAP_MAX, V_TERM / v_filt))
  return v
end

local function update()
  local ok, res = pcall(step)
  local v = 0.0
  if ok then
    v = res
    if auth_id then arming:set_aux_auth_passed(auth_id) end
    if fault_msg then
      if fault_sent then gcs:send_text(MAV_INFO, 'SPINCAP: recovered') end
      fault_msg = nil
      fault_sent = false
    end
  else
    pcall(set_cap, CAP_FAULT)
    v_filt = nil
    if auth_id then arming:set_aux_auth_failed(auth_id, 'SPINCAP fault') end
    if fault_msg ~= tostring(res) then
      fault_msg = tostring(res)
      if (millis() - boot_ms) > QUIET_MS then
        gcs:send_text(MAV_CRIT, 'SPINCAP fault, cap ' .. CAP_FAULT .. ': ' .. fault_msg)
        fault_sent = true
      end
    end
  end
  logger:write('SPNC', 'V,Vf,Cap,F', 'fffB', v, v_filt or 0.0, cap_now, fault_msg and 1 or 0)
  return update, PERIOD_MS
end

gcs:send_text(MAV_INFO, 'SPINCAP: running, cap = min(0.93, 11.2 / V_bus)')
if auth_id == nil then
  gcs:send_text(MAV_CRIT, 'SPINCAP: no aux auth id')
end
return update()
