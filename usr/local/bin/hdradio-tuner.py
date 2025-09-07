""" permissions: 755 root root """

from flask import Flask, request, redirect, jsonify, Response
import subprocess, time, os, json, urllib.request

MOUNT_URL  = "http://127.0.0.1:8000/hd.mp3"
STATUS_URL = "http://127.0.0.1:8000/status-json.xsl"

app = Flask(__name__)

def set_env_and_restart(freq, prog):
    body = f"FREQ={freq}\nPROG={prog}\n"
    tmp = "/etc/default/hdradio.tmp"
    with open(tmp, "w") as f:
        f.write(body)
    os.replace(tmp, "/etc/default/hdradio")
    subprocess.run(["systemctl", "restart", "hdradio@active.service"], check=False)

def wait_until_mount(timeout=5.0, interval=0.25):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(STATUS_URL, timeout=1) as r:
                data = json.loads(r.read().decode("utf-8", "ignore"))
            src = data.get("icestats", {}).get("source", [])
            if isinstance(src, dict):
                src = [src]
            for s in src:
                if isinstance(s, dict) and s.get("listenurl", "").endswith("/hd.mp3"):
                    return True
        except Exception:
            pass
        time.sleep(interval)
    return False

@app.route("/tune", methods=["GET", "HEAD"])
@app.route("/tune/", methods=["GET", "HEAD"])
def tune():
    freq = request.args.get("freq", "97.1")
    prog = request.args.get("prog", "0")
    set_env_and_restart(freq, prog)

    if wait_until_mount(timeout=7.0, interval=0.25):
        return redirect(MOUNT_URL, code=302)
    return Response("Tuner not ready", status=503, mimetype="text/plain")

@app.get("/status")
def status():
    out = subprocess.run(["systemctl", "is-active", "hdradio@active.service"],
                         capture_output=True, text=True)
    active = out.stdout.strip()
    env = {}
    try:
        with open("/etc/default/hdradio", "r") as f:
            env = dict(line.strip().split("=", 1) for line in f if "=" in line)
    except FileNotFoundError:
        pass
    return jsonify({
        "service": active,
        "freq": env.get("FREQ"),
        "prog": env.get("PROG"),
        "mount": MOUNT_URL
    })

@app.get("/ping")
def ping():
    return "pong", 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=False, use_reloader=False)