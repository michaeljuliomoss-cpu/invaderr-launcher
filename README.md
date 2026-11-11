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

Cause: the stick is NTFS, and its files were created while Hermes ran elevated
(administrator). Those files belong to Administrators, so a normal launch cannot
write to them. The repair is a one-time command on the affected PC.

**The fix that works (run in an ADMIN PowerShell):**

```powershell
Remove-Item "E:\home\gateway-locks" -Recurse -Force
```

If that reports access denied:

```powershell
C:\Windows\System32\icacls.exe "E:\home\gateway-locks" /reset /t
Remove-Item "E:\home\gateway-locks" -Recurse -Force
```

Then double-click `Invaderr.vbs` normally. This grants Everyone full control on
`home\`, so the stick then works on any PC, any account, with no admin — as long
as it is never launched elevated again.

## Safe shutdown

Never pull the stick while the gateway is running; that is how the SQLite
database gets corrupted. Stop it first:

```powershell
$env:HERMES_HOME="E:\home"
E:\runtime\python\cpython-3.14.9-windows-x86_64-none\python.exe E:\run.py gateway stop
```

Wait a few seconds after it returns, then remove the stick.

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
