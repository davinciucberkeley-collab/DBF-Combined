"""Load A.param names into SITL via --defaults (the file run_case.py builds, but with NO filtering) and report names the build does not know.
usage: check_names.py   (needs SCR; run with the venv python)"""
import json, os, subprocess, sys, time
from pymavlink import mavutil
H = os.path.dirname(os.path.abspath(__file__)); SCR = os.environ["SCR"]; SITL = os.path.join(SCR, "sitl")
run = os.path.join(H, "runs", "names"); os.makedirs(run, exist_ok=True)
want = {}
for ln in open(os.path.join(H, "..", "A.param"), encoding="utf-8"):
    s = ln.strip()
    if s and not s.startswith("#") and "," in s:
        k, v = [x.strip() for x in s.split(",", 1)]; want[k] = float(v)
open(os.path.join(run, "all.parm"), "w").write("\n".join(f"{k} {v}" for k, v in want.items()) + "\n")
plant = subprocess.Popen([sys.executable, os.path.join(H, "a_plant.py"), json.dumps(dict(out=os.path.join(run, "c"), max_t=60))], stdout=subprocess.DEVNULL)
time.sleep(1)
env = dict(os.environ); env["PATH"] = SITL + os.pathsep + env["PATH"]
sitl = subprocess.Popen([os.path.join(SITL, "ArduPlane.elf"), "--model", "JSON:127.0.0.1", "--defaults", os.path.join(SCR, "src", "quadplane.parm") + "," + os.path.join(run, "all.parm"),
                         "--home", "37.9150,-122.3340,5,0", "--wipe", "-I0"], cwd=run, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(2)
m = mavutil.mavlink_connection("tcp:127.0.0.1:5760", source_system=255); m.wait_heartbeat(timeout=60)
time.sleep(5)
got = {}
m.mav.param_request_list_send(m.target_system, m.target_component)
t0 = time.time(); n = None
while time.time() - t0 < 90:
    msg = m.recv_match(type="PARAM_VALUE", blocking=True, timeout=3)
    if msg is None:
        if n and len(got) >= n: break
        continue
    got[msg.param_id] = msg.param_value; n = msg.param_count
    if len(got) >= n: break
sitl.terminate(); plant.terminate()
unk = [k for k in want if k not in got]; diff = [(k, want[k], got[k]) for k in want if k in got and abs(got[k] - want[k]) > 1e-3 * max(1, abs(want[k]))]
print("names", len(want), "params in build", len(got), "unknown", unk); print("value differs", diff)
