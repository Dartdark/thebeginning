# dot: FOMC reversal and intraday replication audit
Author: dot. 2026-11-10. Research only. No return tests or deployment.

## 53. The FOMC Announcement Reversal
**Conditional intraday event hypothesis. Personal or no-overnight timing fit; no blanket Apex certification. Existing-data feasibility remains conditional, not verified.**

[SSRN 4182628](https://ssrn.com/abstract=4182628), Baglioni and Ribeiro. Reviewed [author-uploaded February 2025 full text](https://www.researchgate.net/publication/362775066_The_FOMC_Announcement_Reversal) and the [2023 thesis](https://repositorio-api.insper.edu.br/server/api/core/bitstreams/fb55a5bb-06c8-4ed4-aa81-054742c3b42d/content).

### Source specification
Fade the prior 24-hour E-mini S&P 500 return at 13:50 Eastern, close at 15:50. Eight historical 12:30 announcements instead use 12:15–14:15. Current source: 180 events through January 2020, 17.86 bp/event after bid/ask spreads, annualized Sharpe .56. Brokerage fees and impact are excluded; no postpublication holdout established. The older thesis's 1.02 overall/1.60 post-2011 Sharpe additionally scales two trading hours to a 6.5-hour session. February 2025 removes this step, giving .56/.89 with unchanged event returns. This is a normalization correction, not deteriorating observed performance.

### Independent implementation assessment
- Same-day US exposure ends well before the repository's 15:59 Central flatten cutoff. No overnight position is required merely because the signal looks back 24 hours.
- Actual announcement dates/times, exceptional meetings, holidays and quote clocks must be preserved. Do not hard-code 14:00 throughout history.
- Signal and fill cannot both use an unknowable completed bar close. Define the observed price and first executable subsequent bid/ask before replay.
- A small number of event days creates concentration and inference fragility. Scheduled news gaps, adverse fills and intratrade losses matter even if the position exits within two hours. A positive historical mean does not show improved trailing-limit survival.
- Owned ES minute data may support a clearly labeled price-only approximation, but this pass has not authenticated complete dated rows, timestamps, contract rolls, bid/ask history or event endpoints. It does not earn a current-data-ready tag.
- No exact 4182628 rule was found in current TIER_LIST/DATA_NEEDED. Existing liquidity-based FOMC shorts (4304807), poststatement reaction trades, pre-FOMC drift, minutes trades and GC/BTC reaction tests remain unchanged. They are related exposures, not exact implementations.
- Compared with broad curve research this needs fewer signal inputs, but the evidence is old and modest. A future source/data feasibility audit, not another parameter search, is the next gate.

## External fifty-rule replication: discovery aid, not verified preregistration
[Repository at public initial commit](https://github.com/NostroBenJ/intraday-strategy-replication/commit/233c09b7d817ae7e002fd2fd4df9560e145cf2e7). The catalog admits it did not check PDFs and uses summarized proxies. Public history first shows plan and results together on October 6, 2026; the claimed October 1 freeze has no independently verified timestamp. Its FOMC proxy uses a different signal and 14:05 entry, so cannot reject entry 53. Costs in older/index datasets are normalized to current NQ ranges rather than actual historical fees; ES confirmation only requires positive gross mean. IID day resampling is not block inference. Simulations acknowledge family acceptance above 5%. A postpublication split is explicitly post hoc. See [catalog](https://github.com/NostroBenJ/intraday-strategy-replication/blob/main/CATALOG.md), [plan](https://github.com/NostroBenJ/intraday-strategy-replication/blob/main/PREREGISTRATION.md), [results](https://github.com/NostroBenJ/intraday-strategy-replication/blob/main/RESULT.md).

**Assessment:** useful negative evidence and rule-discovery leads, not proof all underlying papers fail, nor independently verified funded-account survival. No external code was run.

## Failed weekly auction reversion, SSRN 6728359
[Primary abstract](https://ssrn.com/abstract=6728359) available; full PDF unavailable. Companion-code audit, not a full paper review:
- [State machine](https://github.com/desmonperry1213/failed-auction-reversion/blob/main/paper1/tpo_state_machine.py) updates profile using the current bar then fills against that bar's range. It grants boundary fills when price only approaches within four ticks, and begins risk management next bar.
- P&L in R omits execution costs. EOD flatten requires an exact 16:00 Central bar, without verified fallback when the futures halt removes it.
- [Loader](https://github.com/desmonperry1213/failed-auction-reversion/blob/main/paper1/run_tpo_confirmation_5m.py) chooses the day's contract using full-day volume.
- [Record](https://github.com/desmonperry1213/failed-auction-reversion/blob/main/paper1/PRE_REGISTRATION_RECORD.md) shows full-history calibration and five-minute redesign after failed hourly experiments. Initial public history already contains outcomes.
- Missing imported strategy module and trade-wise bootstrap further obstruct reproduction.

**Decision:** do not promote. Static defects undermine executable evidence; numerical consequences were not tested. Repairing code would create new research, not validate the existing headline.

## Order-flow paper screens
- [7053198, October 3, 2026 revision](https://papers.ssrn.com/sol3/Delivery.cfm/7053198.pdf?abstractid=7053198&mirid=1&type=2): indexed primary abstract reports mean fold gross/net Sharpe .981/−1.726 with **30-minute** rebalancing; equal-capital daily portfolio 2.75/−1.59. The separate 10-second cost sweep is not that strategy. Prospective June–August IC in two of eight cells is not net live profit. [Author repository](https://github.com/kethanse66-cyber/quant-research-ofi) retains superseded descriptions; inspected source has backward fills, missing-target handling and no explicit daily flatten, but provenance to revised results is unverified. Full paper unavailable. Net-rejection/method reference, not a new allocation.
- [7067778](https://ssrn.com/abstract=7067778): primary abstract covers 2025 CME MBO, eight instruments and 46 cells. All predict direction; zero profit at stated retail costs. Market-maker assumptions do not establish accessible fills or queues. Full strategy/cost/holdout audit unavailable. Not an owned-minute-data lead.
- [7245981](https://ssrn.com/abstract=7245981): already DATA_NEEDED D47. Twenty-market L1 OFI residual/PCA rotation strategy; abstract explicitly calls weaker-half improvement subperiod robustness, not formal OOS. Newly located [TickBroker](https://github.com/JvalterLevander/tickbroker) is an engine library, not the PCA strategy, full paper or historical panel. Preserve existing source/data gate.

These source-gated exclusions do not increase the numbered or qualified strategy count.
