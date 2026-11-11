"""Invaderr silent boot.

Starts the messaging gateway with no console window, waits until it is actually
connected to Telegram, then messages the owner that the agent is up.

Launched by Invaderr.vbs through pythonw.exe, so nothing is ever visible.
Idempotent: if a gateway for this profile is already running, it announces
nothing and exits quietly.
"""

from __future__ import annotations

import datetime
import glob
import json
import os
import socket
import subprocess
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.join(ROOT, "home")
LOG = os.path.join(ROOT, "_build", "gateway-boot.log")
CONNECT_MARKER = "Connected to Telegram"
WAIT_SECONDS = 150
CREATE_NO_WINDOW = 0x08000000


def find_python(exe: str = "python.exe") -> str:
    pats = [
        os.path.join(ROOT, "runtime", "python", "*", exe),
        os.path.join(ROOT, "runtime", "python", exe),
    ]
    for pat in pats:
        hits = glob.glob(pat)
        if hits:
            return hits[0]
    raise SystemExit(f"{exe} not found under {ROOT}/runtime/python")


def read_env(path: str) -> dict:
    out = {}
    try:
        with open(path, encoding="utf-8-sig", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                out[k.strip()] = v.strip().strip('"').strip("'")
    except OSError:
        pass
    return out


def tail_err(n=6, width=200):
    """Last meaningful error lines from the boot log, for the Telegram alert."""
    try:
        with open(LOG, encoding="utf-8", errors="ignore") as f:
            lines = [l.strip() for l in f if l.strip()]
    except Exception:
        return ""
    keys = ("Error", "error:", "Traceback", "Exception", "malformed", "denied",
            "No such", "Failed", "failed", "not found")
    hits = [l for l in lines if any(k in l for k in keys)]
    tail = lines[-3:]
    pick = (hits[-n:] + [l for l in tail if l not in hits])[-n:]
    return "\n".join(l[:width] for l in pick)


def announce(token: str, chat: str, text: str) -> bool:
    if not token or not chat:
        _note(f"announce skipped: token={bool(token)} chat={bool(chat)}")
        return False
    data = urllib.parse.urlencode({"chat_id": chat, "text": text}).encode()
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        req = urllib.request.Request(url, data=data, headers={"User-Agent": "invaderr"})
        with urllib.request.urlopen(req, timeout=20) as r:
            body = r.read().decode("utf-8", "ignore")
        _note(f"announce ok: {body[:120]}")
        return True
    except Exception as e:
        _note(f"announce failed: {type(e).__name__}: {e}")
        return False


def _note(msg: str) -> None:
    """Append a diagnostic line to the boot log (never raises)."""
    try:
        with open(LOG, "a", encoding="utf-8", errors="ignore") as f:
            f.write(f"\n[boot] {datetime.datetime.now():%H:%M:%S} {msg}\n")
    except OSError:
        pass


def main() -> int:
    env = os.environ.copy()
    env["HERMES_HOME"] = HOME
    env["HERMES_DISABLE_LAZY_INSTALLS"] = "1"
    env["HERMES_GATEWAY_LOCK_DIR"] = os.path.join(HOME, "gateway-locks")
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "w", encoding="utf-8", errors="ignore") as log:
        proc = subprocess.Popen(
            [find_python(), "-u", os.path.join(ROOT, "run.py"), "gateway"],
            env=env,
            cwd=ROOT,
            stdout=log,
            stderr=subprocess.STDOUT,
            creationflags=CREATE_NO_WINDOW,
            close_fds=True,
        )

    deadline = time.time() + WAIT_SECONDS
    connected = False
    already = False
    exited_at = None
    while time.time() < deadline:
        time.sleep(2)
        try:
            with open(LOG, encoding="utf-8", errors="ignore") as f:
                body = f.read()
        except OSError:
            body = ""
        if CONNECT_MARKER in body:
            connected = True
            break
        if "A gateway is already running" in body:
            already = True
            break
        if proc.poll() is not None:
            # parent can exit after handing off to the real gateway child
            if exited_at is None:
                exited_at = time.time()
            elif time.time() - exited_at > 30:
                break


    conf = read_env(os.path.join(HOME, ".env"))
    token = conf.get("TELEGRAM_BOT_TOKEN", "")
    chat = conf.get("TELEGRAM_HOME_CHANNEL") or conf.get("TELEGRAM_ALLOWED_USERS", "").split(",")[0].strip()

    host = socket.gethostname()
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    if connected:
        announce(token, chat, f"\U0001F7E2 Invaderr online \u2014 {host}\n{stamp}")
        return 0

    if already:
        announce(token, chat, f"\U0001F7E2 Invaderr already running on {host}\n{stamp}")
        return 0

    if proc.poll() is not None:
        # exited on its own: usually another gateway already owns this host
        announce(token, chat, f"\u26A0\uFE0F Invaderr exited on start \u2014 {host}\n{stamp}\n\n{tail_err()}")
        return 1

    announce(token, chat, f"\u26A0\uFE0F Invaderr running but Telegram not connected \u2014 {host}\n{stamp}\n\n{tail_err()}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
