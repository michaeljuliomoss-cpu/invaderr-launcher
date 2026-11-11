' Invaderr — silent launcher.
'
' Double-click this file. Nothing appears: no console, no tray icon, no window.
' It starts the agent in the background and the agent messages you on Telegram
' once it is actually connected.
'
' Use start.cmd instead when you want to watch it work (chat mode, diagnostics).

Option Explicit

Dim fso, sh, dir, py, sub_
Set fso = CreateObject("Scripting.FileSystemObject")
Set sh  = CreateObject("WScript.Shell")

dir = fso.GetParentFolderName(WScript.ScriptFullName)
py  = ""

' find the bundled interpreter (version folder changes between builds)
If fso.FolderExists(dir & "\runtime\python") Then
  For Each sub_ In fso.GetFolder(dir & "\runtime\python").SubFolders
    If fso.FileExists(sub_ & "\pythonw.exe") Then
      py = sub_ & "\pythonw.exe"
      Exit For
    End If
  Next
End If

If py = "" Then
  MsgBox "Could not find pythonw.exe in runtime\python." & vbCrLf & _
         "Is the whole Invaderr folder on this drive?", 16, "Invaderr"
  WScript.Quit 1
End If

sh.CurrentDirectory = dir
sh.Run """" & py & """ """ & dir & "\boot.py""", 0, False
