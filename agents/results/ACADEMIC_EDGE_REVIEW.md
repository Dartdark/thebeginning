# Antigravity's RESEARCH_ACADEMIC_EDGE.md (antigravity/jesse 11ab109): Claude's review (2026-10-18)

A literature write-up, no new backtest. Useful as an explanation of why the plan works; not a source of a new trade.

**Correct:** the core principle (forced flows, not chart patterns); Cheng & Madhavan's leveraged-ETF rebalancing formula
(Late-Day Flow, ES MOC Follow); Chan's half-life formula; CPPI = our cushion sizing.

**Wrong or unsupported (do not cite these):**
- Cheng & Madhavan say nothing about a 0.40 ATR threshold (that is our LDF setting).
- Berkman et al. 2012 is about retail attention lifting overnight returns that reverse intraday; it does not describe a
  30-minute opening range, and Vault Break's band is midnight open + 0.30 ATR15, not an opening range.
- Ni, Pearson & Poteshman 2005 find strike pinning on expiration, not a directional drop at the open; our pinning test is F.
- Europe closes at 10:30 CT, not 12:30-13:30 (and the 10:30 trade, ESEuroCloseTrend, is F).
- "Chan proves breakouts must be scaled by ATR(15)": Chan scales gaps by the standard deviation of daily returns; ATR15 is ours.
- OU half-life exits for CL Sunday Fade / NFP Fade: those are event trades with mechanism-set exits, not cointegrated
  spreads; our OU regime filter test is F.
- Sizes "1 mini / 10 micros full, 2-3 micros defensive" and quarter-Kelly are not the plan (half size below $1,500).

**Missed from Chan's book (the two parts that matter to us):**
- His leveraged-ETF trade (buy / sell ~15 min before the close after a big day): independent support for ES MOC Follow
  and Late-Day Flow.
- Opening-gap momentum on index futures (gap beyond the prior high / low by 0.1 x the 90-day sd of daily returns, enter
  at the open, out at the close): the one new, untested, mechanism-based idea (stops triggered past the prior range).
  Offered to the user; not tested.
