# Candidate: Twin Continuation (NQ), user's MultiCharts strategy

**Kind:** strategy, two setups in one position (Swing Breakout + Morning Momentum). The full rules are the PowerLanguage
code in `Twin_Continuation.txt` in this folder (the user's code, unchanged) -- that file IS the spec. Defaults only;
one variant tested (pre-registered = the user's own settings, nothing tuned).

**Data / conventions:** NQ continuous 1-minute bars, CT, close-stamped, 24h session 17:00-16:00 CT, 2018-2026.
Grid: `scratch_data/g24.pkl` (grid24.Grid24; rows = calendar dates, column j = bar closing at 00:00 + j min, CT).

**Costs in trades.csv (`net`, $ per 1 NQ):** $7.25 commission + 1 tick ($5) slippage per market or stop fill (entries
and exits); limit (target) exits fill at the limit with no slippage. Same-bar stop and target: stop first.

**trades.csv columns:** date (exit date), side, net, setup (BO / MO), entry_date, entry_time_ct / exit_time_ct (HHMM,
bar-close times of the entry / exit bars), entry, exit (prices before slippage).

**placebo.csv:** 10 runs of the same system with a random side at every entry (same entry times; BO stop and target
distances mirrored), same costs.

**Things the maker is unsure about:** MultiCharts fills for stop entries that gap (filled at the open here), the
'late' bucket handling when a minute is missing (the code processes a 15-min / 10-min bucket on the next bar; the port
processes it on the last existing bar), and BO positions held overnight (5% of trades).
