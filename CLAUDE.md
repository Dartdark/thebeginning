# Project notes for Claude

NQ/ES futures strategies in MultiCharts PowerLanguage for Apex 50K prop accounts (challenge and
funded). Start with `HANDOFF.md`, `funded_strategies/README.md` and `TIER_LIST.md`.

## Working rules

- **Apex only** (ignore Topstep). Positions flat by 15:59 CT; $2,000 end-of-day trailing drawdown.
- **Branches:** work on `claude/nq-trading-strategy-params-5h9d20`; keep
  `claude/quirky-noether-4dla64` and the session's designated branch identical; push every
  commit to all of them.
- **Links:** always give direct GitHub links, and raw links
  (`raw.githubusercontent.com/...`) for code to paste into MultiCharts.
- **Folders:** `apex_strategies/` = challenge-only strategies (Vault Break, Overnight Bias);
  `funded_strategies/` = funded strategies. Comparing them is fine; the challenge ones are not
  meant for making money in funded accounts.
- **Preferences:** low-correlation strategies preferred; regime-dependent ones welcome but not
  preferred; funded payouts are the main goal, challenge improvements are a bonus.
- **Testing standard:** costs $7.25/NQ ($5/ES) + 1 tick slippage per market/stop fill; 2018–2026;
  by year and 2023 onward; placebo / walk-forward where relevant; funded bench
  (`analysis/funded_lab.py`). **Always report Sharpe, Sortino, profit factor, Calmar and Ulcer
  index** (`analysis/metrics.py`), for the whole strategy and for longs and shorts separately,
  with bootstrap intervals and drawdown permutation (`analysis/resampling.py`) on the
  2023-onward holdout.
- **Development process:** follow `DEVELOPMENT_PROCESS.md`. Every strategy is checked as a
  whole first, then its **longs and shorts are analysed and improved separately** and
  recombined.
- **Papers / articles:** summarize (what it's about, findings, why it should make money), say
  whether a strategy can be built on top of it as a foundation, test it when there's a fit,
  and **rank every tested item in `TIER_LIST.md`** (S–F).
