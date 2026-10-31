# Overnight-volume switch upload: TEST

Summary: Assess the supplied source against the current plan, including an actual portfolio comparison.
Claude has already tested the related T_ONESIDE family; this file changes volume, morning anchors and stop timing.
Existing minute caches contain positive trade-volume values; the fixed source is sufficiently specified for a proxy.
TEST permits historical research only; exact MultiCharts parity and venue stop behavior remain unverified.

Source: unchanged `agents/codex/inputs/night_volume_switch/source.txt`.
Latest context: Claude `febc65f1573040abf9a697d1d3468e1bce48c4c0`, including
`checks/candidates/t_oneside/REVIEW.md`, original/v2 sources and committed Python trade ledger.
No new source-version price returns have been run. Prior family returns are already known and must not
be called fresh evidence. The previous ORPullback research has two additional Codex return variants.

1. **Who/why?** Heavy overnight activity may predict inventory reversal near the cash open; quieter nights
   permit a one-sided-morning long. No measured investor mandate or independent order-flow imbalance establishes
   this mechanism. The OS leg may reflect ordinary positive Nasdaq drift, as the prior family review found.
2. **Known timing/direction:** at the exact08:29 close, compare current night Ticks volume with1.4 times the
   prior20 valid-night median and fade the night price move if heavy. Otherwise use the observed09:59 morning
   range/VWAP test for a long. Source inputs and chart assumptions are explicit:1-minute NQ,CT,IOG off.
   No volume-dollar flow magnitude or participation share is inferred from a thresholded bar-volume sum.
3. **Transmission:** directly NQ/MNQ; Ticks is activity, not a signed futures buying imbalance.
4. **Data:** the owned exporter writes Ticks. On priced overnight cache bars, volume is finite and positive;
   no old-year volume field failure was found. Night minute gaps are not all feed failures (breaks/halts exist).
   The source's observed-bar state and minimum-count rules are preserved; exact08:29 absence is audited.
5. **Costs/gaps:** use$1.04/MNQ round trip plus1tick per market/stop fill, sensitivity$1.24. Previous related
   stopped-family averages about$15/MNQ exceed the ordinary$2.04 cost allowance; that is a feasibility screen,
   not evidence for this changed source. Fade overlaps EOS/ONB at the open, OS overlaps morning NQ long legs.
6. **Power:** prior family~100 trades/year suggests~500 design events. At assumedSD$1,000/NQ, t2 requires
   mean~$89/NQ net before dependence; prior family mean~$150 makes measurement plausible. No power exemption.
7. **Already tested:** latest t_oneside_test/bench and review. The new source uses Ticks instead of Volume,
   first RTH bar strictly after08:30 rather than08:30, no missing08:29 fallback and delayed explicit stops.
   Its OS condition also omits a current-night MinNightBars guard. None is silently corrected in the primary model.
8. **Failure/diversification:** overnight volume can be heavy from news/rolls or trend continuation, not trapped
   inventory. Entry-bar spikes precede explicit protection; stops can gap or reject. Morning longs may share
   VB/ONB/RS losses. Joint account minute paths must establish whether any offset arrives before a breach.

Decision: **TEST** two frozen execution timings plus predeclared falsification controls, with a committed
preregistration before returns. Compare addition1/2MNQ, replacement of the ONB slot at2MNQ, and empty slot.
ONB is the preselected overnight-classified morning overlap control; this does not restrict the overall-plan scope.
No live settings, PowerLanguage source repair or deployment is authorized.
