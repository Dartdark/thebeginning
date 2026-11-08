# VPS screenshot for Claude (2026-11-01, user: "dont drop it i want to do it"). Separate from status_push.ps1 so the text
# status keeps working if Windows Defender blocks this one. Saves C:\TradingStatus\screen.jpg; status_push.ps1 (next run)
# includes it in the vps-status push. Defender flagged screen capture + upload as spyware-like: allowing it is the user's
# own decision on their own machine (VPS_STATUS.md), never by disguising the code.
#   Task: schtasks /Create /TN "VpsScreenshot" /SC MINUTE /MO 5 /TR "C:\TradingRepo\live\vps\run_screen.cmd" /F
$ErrorActionPreference = "SilentlyContinue"
$Out = "C:\TradingStatus"; New-Item -ItemType Directory -Force $Out | Out-Null
# 1. screenshot (all monitors). Black/blank if the RDP window was minimized or disconnected: see VPS_STATUS.md
try {
    Add-Type -AssemblyName System.Windows.Forms, System.Drawing
    $b = [System.Windows.Forms.SystemInformation]::VirtualScreen
    $bmp = New-Object System.Drawing.Bitmap $b.Width, $b.Height
    $g = [System.Drawing.Graphics]::FromImage($bmp); $g.CopyFromScreen($b.Left, $b.Top, 0, 0, $bmp.Size)
    $codec = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq "image/jpeg" }
    $ep = New-Object System.Drawing.Imaging.EncoderParameters 1
    $ep.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter ([System.Drawing.Imaging.Encoder]::Quality), 70L
    $bmp.Save("$Out\screen_new.jpg", $codec, $ep); $g.Dispose(); $bmp.Dispose(); $shot = "ok"
} catch { $shot = "FAILED: $($_.Exception.Message)" }

Set-Content "$Out\screen_status.txt" "$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss')) $shot"
