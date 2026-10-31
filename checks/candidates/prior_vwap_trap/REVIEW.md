# Prior VWAP Trap (user's upload 2026-10-29): review

**Grade B (TIER_LIST).** Independent rebuild `analysis/prior_vwap_trap_test.py` (our NQ 1-min, cash 08:31-15:00, the code's
roll list, $7.25 + 1 tick per fill) reproduces the PDF: 1,804 trades 2017 - 2026-10-09, $153 per NQ, PF 1.24, t 3.2
(PDF: $155-158, PF 1.25); by year within ~$1k of the PDF's research column (2022 $63.7k vs $64.1k).
Longs $175 (t 2.8), shorts $129 (t 1.8); 2018-22 $161 (t 3.1), 2023+ $141 (t 1.6). Daily corr with plan VB 0.22, ONB 0.25.

**Placebo (the key finding):** the level isn't what pays. Same rules on other levels: yesterday's close $107 (t 2.3),
yesterday's midpoint $115 (t 2.4), PVWAP shifted at random by up to +-0.3 ADR $88-169 (t 1.9-3.6; one of five beat
PVWAP). PVWAP adds maybe ~$30 a trade over a random nearby level, within noise. The engine looks like intraday momentum
held to 15:00 behind a 0.5 x ADR trailing stop, not a trapped-crowd effect at yesterday's VWAP.

**Feedback for the author**
1. Pre-registration and the honest 2023+ split are excellent; keep the kill test.
2. Run the placebo above before crediting the 'trap' story; test the trailing stop + time exit with a neutral entry
   (e.g. long/short on the first 08:35 move) to see how much is the exit engine.
3. The roll list (3 non-roll gaps, June 2024 roll missing) moves PVWAP on those days; a back-adjusted series removes it.
4. 2023+ t 1.6 / PF 1.16 is thin; the 788-day drawdown is a real live-trading risk at 1 NQ.
5. MultiCharts: the stop starts the bar after the fill (as you note); fine.
Next for us: plan benches (combine / funded / personal), as an addition and as a replacement for VB.
