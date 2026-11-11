# Invaderr launcher

Portable Hermes launcher for the INVADERR USB stick.

These files live at the **root** of the stick, next to `runtime/`, `sys/` and `home/`.
They are not a standalone app: `boot.py` finds the runtime relative to its own location.

## Using it on a PC

1. Double-click **`Invaderr.vbs`** — normal double-click.
   **Never "Run as administrator."** Elevated runs break file access on the USB home.
2. Wait up to 150 seconds. You get a green message on Telegram when it is connected.

## If Telegram will not connect

Symptom in the alert: `Permission denied: ...\gateway-locks\telegram-bot-token-...`

Cause: the stick is NTFS, and NTFS permissions are stored as user IDs tied to the
machine that created them. Move the stick to another PC and those IDs no longer
resolve, so your own account gets locked out of its own folder.

Fix: run **`FIX-PERMISSIONS.cmd`** once. It self-elevates, takes ownership of
`home\`, grants full control to everyone, and deletes the stale lock folder.
That is the only step that needs admin, and it is not launching the agent.

## Files

| File | Purpose |
|---|---|
| `Invaderr.vbs` | windowless launcher, the only thing you click |
| `boot.py` | starts the gateway, announces online/failure to Telegram |
| `run.py` | sets the portable environment and calls the Hermes CLI |
| `FIX-PERMISSIONS.cmd` | one-time ACL repair for a moved stick |

## Notes

- One launcher per machine. Double-clicking twice is harmless.
- Never force-kill the gateway. SQLite can corrupt mid-write.
- Unplugging while it runs is the other way to corrupt the database.
