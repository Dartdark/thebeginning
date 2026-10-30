# VPS maintenance: no surprise restarts (user's to-do, 2026-10-30)

Goal: Windows never restarts the VPS during trading, and a planned restart every Saturday clears half-closed MultiCharts copies
(the 10/29 "session terminated" problem). About 10 minutes, once. Do it on the VPS, logged in as Administrator.

## 1. Find which Windows it is
Start > type `winver` > Enter. "Windows Server 2019/2022" -> use the **Server** steps. "Windows 10/11" -> the **Desktop** steps.

## 2. Keep updates out of trading hours

**Server (most VPSs):**
1. Start > type `gpedit.msc` > Enter.
2. Computer Configuration > Administrative Templates > Windows Components > Windows Update
   (on Server 2022: ... > Windows Update > Manage end user experience).
3. Double-click **Configure Automatic Updates** > Enabled >
   - Configure automatic updating: **4 - Auto download and schedule the install**
   - Scheduled install day: **7 - Every Saturday**, time **10:00**
   > OK.
4. Double-click **No auto-restart with logged on users for scheduled automatic updates installations** > Enabled > OK.
5. Close gpedit. Open PowerShell as Administrator and run `gpupdate /force`.

**Desktop (Windows 10/11):**
1. Settings > Windows Update > Advanced options > **Active hours**: Manually, **6:00 AM to 6:00 PM** (the VPS clock is
   Central time: check the clock in the taskbar).
2. Same page: turn **off** "Get me up to date" (it restarts as soon as possible).
3. Windows Update > **Pause updates** for 1 week whenever an update is waiting on a weekday; let it install on Saturday.

## 3. A planned restart every Saturday 10:30 CT
PowerShell as Administrator, one line:
```
schtasks /Create /TN "WeeklyRestart" /SC WEEKLY /D SAT /ST 10:30 /TR "shutdown /r /t 120 /c Weekly-restart" /RU SYSTEM /F
```
Check it: `schtasks /Query /TN "WeeklyRestart"` shows Next Run Time = next Saturday 10:30.
All trades are flat by Friday 15:59, so nothing is open on Saturday.

## 4. Sunday before the open (by ~16:30 CT; the Bridge trade enters Sunday 19:00 CT)
1. Log in to the VPS. Task Manager > Details: no MultiCharts64 / TradingServer / tsServer left over.
2. Start **MultiCharts64** only. Wait for Rithmic and dxFeed to connect (green).
3. Order and Position Tracker > Positions: every account flat.
4. Auto-trading **on** on every live chart (initial position **Flat**). Check each strategy's Auto Trading account once.
5. `cd C:\TradingRepo; git pull` (picks up anything Claude changed during the week).

The watchdog and the pre-market check only run on weekdays, so Sunday evening is checked by you.

## 5. Already done (2026-10-30)
- "Stop auto-trading after 10 rejected orders" on every live strategy (Format Signals > Properties > Auto Trading).
- Watchdog alarms: account at or near its Apex floor, Apex lock / failure in rejection messages.
