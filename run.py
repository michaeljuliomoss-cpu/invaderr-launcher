"""Invaderr — portable Hermes entry point.

Deliberately does NOT use the venv's console-script shims. Those embed the
absolute install path (uv canonicalises a subst drive back to the real volume),
which is exactly what breaks when the stick changes drive letter on a new
machine.

Instead: run the stick's own relocatable Python, put the app source and the
installed site-packages on sys.path relative to THIS FILE, and call Hermes'
entry point. Every path is resolved at runtime from the stick's actual
location, so the letter, the folder, and the host machine don't matter.
"""
import glob
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))


def _newest(paths):
    return sorted(paths, key=os.path.getmtime, reverse=True)


def build_path():
    app = os.path.join(ROOT, "sys", "app")
    if not os.path.isdir(app):
        sys.exit("Invaderr: missing sys/app — this stick is not provisioned.")

    sps = glob.glob(
        os.path.join(ROOT, "home", "installs", "*", "environments", "*", "venv", "Lib", "site-packages")
    )
    if not sps:
        sys.exit("Invaderr: no installed environment found under home/installs.")

    # newest first, and drop any stale duplicate environments
    return [app] + _newest(sps)


def main():
    sys.path[:0] = build_path()
    os.environ.setdefault("HERMES_HOME", os.path.join(ROOT, "home"))
    os.environ.setdefault("PYTHONUTF8", "1")
    os.environ.setdefault("HERMES_DISABLE_LAZY_INSTALLS", "1")
    # Keep the stick's gateway independent of any Hermes gateway already running
    # on the host machine. Separate lock dir => it starts instead of deferring.
    # The stick has its own bot token, so Telegram sees two distinct bots.
    os.environ.setdefault(
        "HERMES_GATEWAY_LOCK_DIR", os.path.join(ROOT, "home", "gateway-locks")
    )

    from hermes_cli.main import main as hermes_main

    return hermes_main()


if __name__ == "__main__":
    sys.exit(main())
