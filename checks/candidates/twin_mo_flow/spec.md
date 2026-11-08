# Twin MO x closing order flow (2026-11-08)
Base: Twin cap1 v2.1 Morning Momentum trades on NQ ($7.25 + 1 tick). Filter: keep an MO trade when its side equals the previous session's Overnight Tick cell direction (+1 when (flow 14:15-15:15 CT < 0 and VIX > SMA25) or (flow >= 0 and VIX <= SMA25), else -1). Order flow = The Bridge aggressor volume (NQ).
