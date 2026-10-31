# Current portfolio audit: TEST existing-book diagnostics

User authorized a portfolio audit after the October30 RL builds failed. This is an audit of existing allocations,
not a new alpha hypothesis, tuning run, strategy retirement or live change. New signal definitions: zero.

Source snapshot: Claude c3126aa01796133f3aecb368e688726931dea440, fetched October31. Research on codex/work.
Its NEW_CHAT_BRIEF explicitly keeps T_ONESIDE on50K funded, restores VB2/1, restores DT2 on150K funded,
and removes Swing Target from funded accounts. Personal retains Swing Target. Older Codex rosters are superseded.

## Evidence questions

1. Participants/mechanism: inherit the existing plan's separately tested flows and rules. Audit whether costs,
   shared market exposure and account constraints preserve their reported portfolio benefit; no new edge proposed.
2. Clock: existing report/strategy decision and later fills; archive report settings and source trade clocks.
   Grid24 timestamps are close-stamped Central calendar minutes. Evening holds belong to the following Apex day.
   Inferred within-bar clocks, unknown orders and actual broker fills remain separate evidence categories.
3. Contract transmission: normalize NQ/ES/CL to actual MNQ/MES/MCL point/tick values and integer quantities.
   Do not scale a full contract's dollar commission to a micro. Do not claim any quote/queue certification.
4. Data: owned raw minute grids and MultiCharts/Python ledgers; latest source fixes explicit MC `open` rows.
   Order-flow for Overnight Tick ends2026-07-07. Shared comparisons stop there, rather than counting later
   missing signals as zero. Census report settings, warm-up, missing held bars, version and clock mismatches.
5. Costs/overlap: inspect real_fee_bench.py and E09/E43/E04. Actual all-in fees requested asynchronously.
   If absent, fixed assumed micro commissions1.04/1.24RT plus native tick slippage, explicitly not a verified tariff.
   Count every trade/reentry. Report cost bridge and overlapping losses/exposure, including opposite NQ positions.
6. Power: this is historical implementation/accounting analysis, not promotion significance. No new selection,
   fitted filter or claim of prospective portfolio improvement. Bootstrap preserves all strategies' sampled dates.
7. Falsifiers: baseline identity, cash-cost bridge, integer lots, daily/path totals and first-passage parity must pass.
   Missing inputs block certification; retain useful conditional diagnostics without inventing orders, bars or returns.

## Failure/diversification boundary

Common equity exposure may dominate apparent strategy count. Daily correlation does not establish that a hedge
arrives before liquidation. Reconstruct position occupancy and identify the evidence quality of each path. Minute
OHLC cannot establish simultaneous cross-market extrema or order/stop chronology inside a bar. Personal overnight
roll/corporate-contract identity and current-version parity remain admission questions. Stops are not loss guarantees.
No existing strategy is removed or resized after inspecting its contribution in this audit.
