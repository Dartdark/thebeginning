# NQDB2 / DriftBreak v2 evidence: NEEDS DATA for source validation

Source-only; no new return trials. Upload and pinned current VB source/context are in `agents/codex/inputs/nqdb2/`.
Audit: `analysis/codex_nqdb2_review.py`; context Claude `febc65f`, Codex `73a5f24`.

1. **Who trades/why?** Price-only upside noise-band continuation, already the VB family. A default veto avoids entries
   after four 30-minute closes' return is <=-0.10%. No distinct forced buyer, mandate, order deadline or flow size is
   documented. A plausible losing-breakout filter is a hypothesis, not a demonstrated causal mechanism.
2. **Direction/size/timing known?** Close, completed-date mean ranges and intraday VWAP can be known at the decision
   under fixed bar-close settings. The precise session template and IOG are unspecified; code resets on calendar Date.
   No forced-dollar-demand estimate is provided. Header optimization suggestions are not adopted.
3. **Direct traded market?** NQ chart, long only. Executing MNQ from NQ signals is distinct from switching Data1 to MNQ:
   its per-contract dollar brackets are not symbol-normalized. Signal/execution instruments must be documented.
4. **Independent data?** None: the context veto is past price momentum; VWAP uses the source-specific Volume field.
   Existing NQ OHLCV prices are available. Exact MC intraday Volume semantics/split-volume history or a parity export
   is needed to avoid silently substituting total volume. No GLD/external daily file like GC_COMBO is required.
5. **Costs and gap?** Default NQ target/stop are 40/75 points, $800/$1,500 before costs. No source net performance is
   supplied. The clock overlaps current morning/afternoon NQ exposure; independent account diversification is unproved.
   Test all eligible events first; no selection by hours when the existing plan is flat.
6. **Power?** No trade list, variance, removed-trade count or original selection ledger is supplied. A numeric power
   calculation cannot be completed honestly. For m removed trades with net SD s, even elementary t=2 requires a losing
   mean of magnitude at least 2*s/sqrt(m); use paired strategy/path comparisons when re-entry changes. Seen 2023+ is
   historical replication, not a fresh holdout for a revised veto.
7. **Already tested?** Latest TIER_LIST row101 already lists the Bridge's VaultBreak v8: calendar high-low mean including
   Sunday partials, seven-bar VWAP exit and next-bar flatten. Its old mean/PF were $82/1.23 vs v1 $92/1.26; those are not
   this veto's results. VB Combined's rejected clock/VWAP-distance filter is another rule, not a test of this drift veto.

Failure/risk: the added exposure is long NQ, so shared losses with VB/ONB/RS/Monday legs are plausible and no offset
before a trail breach is established. Dollar brackets total $3,000 at two contracts before fills/fees; unchanged MNQ
chart defaults widen to 400/750 points. Built-in protection is prearmed, but holiday exit and IOG behavior need checking.

**NEEDS DATA**, principally original chart/IOG/volume settings, untrimmed header and exact-version MC trades/settings.
Treat this as a VB improvement candidate, not another independent strategy. A later pre-registered test must isolate
veto on/off from range, weighting, timing, re-entry and risk differences; then require current-plan contribution.
