# Morning jump fade + jump-bar volume (user 2026-11-12, ahead of the forward log: EXPLORATORY)
Written before running. Source: drift-burst paper (reversal strongest after high-volume, negative bursts).
Volume = vz = jump bar volume / mean volume of the same 5-min slot over the previous 20 sessions (jump_lib).
Variants (fixed): V1 keep vz >= 2; V2 keep vz < 2 (control); V3 longs only (fading drops) with vz >= 2.
Base: analysis/jump_morning_fade.py rule, costs as there. Pass: V1 beats base PF in BOTH 2018-22 and 2023+.
