"""Run a list of run_fwd.py jobs on up to 4 SITL instances. usage: SCR=... python queue.py jobs.txt  (one job per line: tag args...)"""
import os, subprocess, sys, threading, queue
HERE = os.path.dirname(os.path.abspath(__file__)); SCR = os.environ["SCR"]
PY = os.path.join(SCR, "venv", "Scripts", "python.exe")
jobs = [l.split() for l in open(sys.argv[1]) if l.strip() and not l.startswith("#")]
q = queue.Queue()
for j in jobs: q.put(j)
def worker(inst):
    while True:
        try: j = q.get_nowait()
        except queue.Empty: return
        tag = j[0]
        with open(os.path.join(HERE, "runs", tag + ".out"), "w") as f:
            subprocess.call([PY, os.path.join(HERE, "run_fwd.py"), tag, "inst=%d" % inst] + j[1:], stdout=f, stderr=subprocess.STDOUT, cwd=HERE, env=dict(os.environ, SCR=SCR))
        print("done", tag, flush=True)
ts = [threading.Thread(target=worker, args=(i,)) for i in range(int(os.environ.get("NW", 4)))]
[t.start() for t in ts]; [t.join() for t in ts]
print("ALL DONE")
