# Kill switch (2026-11-01)

Two levels. Use the one that fits the moment.

## Level 1: STOP TRADING (code; reacts within one bar)
While `C:\TradingLogs\KILL` exists, every live strategy places **no new entries** and **exits any open position at market on
its next bar** (up to 30 min on Vault Break's 30-min chart, 15 min on ONB). Backtests are not affected (real time only).

Three ways to switch it on:
- **From your phone, through Claude:** write **KILL** (or "KILL because ...") in the master chat. Claude runs
  `python3 analysis/kill_switch.py kill "..."`; the VPS relay applies it within ~1-2 minutes and ntfy says **KILL ACTIVE**.
  **RESUME** in the chat switches it off (only a kill made this way).
- **On the VPS:** `powershell -ExecutionPolicy Bypass -File C:\TradingRepo\live\vps\kill.ps1`
  (off again: same with `-Resume`).
- **By hand:** create an empty file named `KILL` (no extension) in `C:\TradingLogs`; delete it to resume.

Every switch sends an ntfy alert and a line to `C:\TradingLogs\kill_log.txt`.

## Level 2: FLATTEN NOW (by hand; seconds)
For a real emergency (crash, news shock, runaway orders), do this AND Level 1:
1. MultiCharts: turn **Auto Trading off** on every live chart (the AA button on each chart), so nothing re-enters.
2. MultiCharts **Order and Position Tracker > Positions**: close every open position (or flatten in R|Trader Pro / the
   broker platform for each Apex account).
3. **Orders** tab: cancel every working order (stops / targets left behind).
4. Check the Apex dashboard: every account flat.
Level 1 stays on until you decide to trade again, so a restarted chart can't re-enter.

## Install (weekend only, never mid-session)
1. **Check EL Collections first (1 minute).** PowerLanguage Editor > New indicator, paste
   `if LastBarOnChart then Print(ELC.PathExists("C:\TradingLogs"));` and compile. "Compiled successfully" means the
   library is there. If it fails to compile, stop and tell Claude: the strategies need another way to read the flag, and
   Level 2 is the kill switch until then.
2. `cd C:\TradingRepo; git pull`.
3. Paste the new code of each live strategy (version date 2026-11-01) from the repo: NQ_Vault_Break(_SP),
   NQ_Overnight_Bias_ADX30, NQ_Expiration_Open_Short, Bridge_Monday_Long_L644NQ. Confirm **compiled successfully** each time.
   The pre-market check flags any chart still on the old version.
4. The relay task picks up the remote kill by itself (it already runs every minute).
5. **Latch test first (2026-11-01, Codex review #3):** `powershell -ExecutionPolicy Bypass -File C:\TradingRepo\live\vps\kill_test.ps1`
   -> every line PASS, last line `ALL PASS` (scratch folder, no alerts, no charts touched). Two latches: KILL_LOCAL (kill.ps1)
   and KILL_REMOTE (Claude via the relay); the strategies' KILL file stays while either is set, so a remote RESUME never
   clears a kill you made on the VPS, and a failed GitHub read never resumes anything.
6. **Live test on Sunday before the open:** run `kill.ps1`, check ntfy says KILL ACTIVE and `C:\TradingLogs\KILL` exists; then
   `kill.ps1 -Resume`. Then ask Claude to send a remote KILL and RESUME and watch both alerts arrive.
