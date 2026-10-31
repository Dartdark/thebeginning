# Persistent implied-volatility inversion on adopted OT: TEST for finite preregistration

Summary: test one new conditional curve input on the CURRENT adopted Overnight Tick/VIX long.
Keep the unchanged ticket only when fixedF2VIX>matchingF2VIX3M; unknownKEEP. F2is the second expected
daily session before the trigger RTH date, under a full-session/availability convention frozen below.
No compulsory order is identified. TEST means a bounded source-and-gross plan, not data admission.

Sources: latest read-only073e27ca7f0338aba2f771aeccb20c6eba0b1a41 (relevant definitions identical7f0800f),
TIER/MINED/current adopted books, exact OTsource/spec/rebuild/replica/verdict, vix_regime/vix_sleeve,
ONDsentiment/overnight anomaly definitions; `research/hunt_v2_ot_curve_nomination.md` has hashes and
the narrow independent counterpart check. No actual data/price/OF/trade/cache/workbook rows read,
imports/financial execution or new returns. Source addition0/0/0; program3/60evaluations,4/10hypotheses,
2gross screens, archivedt6=65. Root owns registration. All closed hypotheses/intakes stay closed.

## 1. Who trades, and what forces or causes the trade?

Near-term insurance buyers, investors cutting equity risk and dealers absorbing those orders can
leave a temporary equity concession that a later liquidity provider earns overnight. A30-day implied
volatility index above its3-month counterpart is a possible persistent near-term stress state beyond
VIX's own level or moving average. The prediction is poorer existing OTticket profitability when
that fixed lagged shape is not inverted.

These are contingent participants/risks, not an identified mandate, compulsory cash order, observed
inventory or measured hedge deadline. VIX/VIX3Mreflect option prices and expected uncertainty, not
actual net insurance quantity. Inversion may instead signal continuing adverse information and larger
overnight losses. The two-session lag can miss the acute stress entirely. This can refute the fixed
filter; it never authorizes switching to contango or a more favorable date after outcomes.

## 2. Direction, size and timing known before entry

LetDbe the parent RTH trigger date. Choose expectedF1/F2latest/second-latest Cboe/USindex daily sessions
strictly beforeD from a frozen historical calendar. Both must be full ordinary sessions; a short/
uncertain expected date makes the new featureUNKNOWN, never an instruction to walk back farther.
Require matching positive finite CLOSEs on F2. KEEP_KNOWN ifVIX(F2)>VIX3M(F2); equality/contangoDROP.
Missing/invalid/contradictory/identity-uncertain stateUNKNOWNKEEP, retained explicitly.

|Clock|Prospective fixed convention|
|---|---|
|Feature event_time|F2daily index close, same date for both indices|
|Feature available_at|Not before completion of interveningF1fullsession; assumed conservative allowance, NOT verified historical receipt|
|Parent decision|First original5-minute evening bar>=17:05CT using unchangedDstate/currentDparentVIX|
|First fill|Unchanged next5-minute open, normally wall17:05/native1-minute label17:06|
|Exit|Unchanged next-bar-market at wall03:00/native label03:01 next calendar day|

For FridayD/Sundayentry, F2normallyWednesday; curve date remains attached toD, not advanced toSunday.
One wholeMNQ for initial personal comparison, same parent order/side/cap/state; consumeStateUsed even
if the curve drops the order. No freed later entry, size change or added stop. Historical lag is chosen
before values; it supports a persistent-state question, not authenticated real-time latest-close flow.
Dollar demand/hedge fractions and quantity relative to NQvolume are unobserved, not inferred from VIX.

## 3. Does it reach the traded contract or its hedge?

Both indices concern SPXoption-implied uncertainty at different horizons. Equity risk repricing can
reach NQ/MNQ through baskets/options and cross-index hedges, but this is not an exact Nasdaq inventory
measure. It is also **not a VXfutures calendar curve/carry trade**. Liquidity may be absorbed elsewhere;
a different equity-index horizon indicator does not guarantee NQdirection or a book hedge.

## 4. New information and input feasibility

|Input|Source evidence before values|Outstanding admission requirements|
|---|---|---|
|Current OTparent|Pinned fundedsource00f4702cdc73a6cf11fc89aa3bc0d20c953731f6, SHA256f74269c71706bb79cbaaa3fb8d18d408e515db15f76f9739ecb3bb0c2da9866a; strategy body matches checked candidate|Exact literal session/state/entry/exit and independent entry metadata parity|
|NativeNQDAY/ON+OF|Required2018–22filenames owned; OF60labels14:16..15:15CT|No partial-sum/substitute endpoints, strict clocks/aliases/held gaps, source/contract/calendar audits|
|Parent dailyVIX|SameDclose vsSMA25, source claim closes before17:05; current Gitfile exists|25datedclose warmup and actual Data2date; original receipt/revision limits remain|
|CurveVIX/VIX3M|Latest Gitblobsd4101774924ca7d55dd67d014de2e43aaaac3b5e/0deb965a89bf3ef27ff6e54893e1f97a8c87b20e; source calls both Cboe|Archive same-pin pair before values; exact identity, expected matching dates/calendar, duplicates/conflicts, required history/vintages|
|Official source availability|VIX producer/independentREADME cite Cboe historical daily endpoint; VIX3Mownedsource claims Cboe|No authenticated VIX3Moriginal fetch/publication log or historical receipt was established here; source contradiction vetoes admission|

LocalVIXfile differs in bytes from the latest-source version; VIX3M is absent localroot but exists in
the fetched Git object. Do not mix versions or overwrite the old local file. Matching two source
claims/headers is not authenticated historical availability. Lag2is a prospective assumption, not
permission to ignore known revisions or a wrong series. Unknown curve is KEEP; unknown parent state
is an unresolved parent-admission problem, not a new invented ticket. No learned model is proposed.

The curve must add to the existing parentRSV/VIXcell and to lagged spot-level/own-price controls.
One fixed unselectable level control is F2VIX>its25daily-closeSMA throughF2, unknownKEEP.1000matched
subsets must retain IDs/paths and condition on year, parentcell, knownness and fixed spot-level/cash
down-move strata frozen before data. No return-chosen bins or choosing the best control after2023+.

## 5. Costs and actual intraday gaps

NativeMNQ research fee1.24RT plus one adverse.50tick per marketfill gives2.24RT and4.48gross hurdle.
This is an assumption, not a verified broker quote or NQnet/10. Both parentfills are market; no target/
stop exists by default, so adding protection would be a changed strategy rather than a harmless repair.
Keep native spread/latency/cost stress and worse-gap treatment explicit. No loss cap is guaranteed.

Parent is5-minute, unchanged17:05→03:00inside a single Apexday; initial personal1MNQ,50K1/150K2source
funded settings remain context, not new sizing selections. It replaces an occupied OTslot, potentially
overlapping Twin/Kusho/S30/Bridge and other overnight risk. No stale'01–03always empty'claim applies.
No events are selected from whether another leg is flat. Known holiday/session carries and exact
observed endpoints require audit; do not turn a large losing gap into an inferred roll/holiday deletion.

## 6. Power before returns

Backwardation may be rare, and the parent already selects down days/twoempirical cells. Generic
backwardation frequency cannot supply this conditional sample. Actual kept/removed counts were not
read. Freeze a count gate before endpoint returns;100kept design events is the preferred cheap minimum
and a possible failure accepted here. Do not expand the window or flip the sign to manufacture counts.

For assumed eventSD100USD/MNQ, n100requires netmean≈20USD for t≈2; n50≈28.28USD, plus2.24cost for gross.
These are planning assumptions, not observed power or promotion. Stress clustering/outliers and the
large inherited fear/curve/parent selection history reduce effective information. Total kept profit
must beat BASE and removed trades must lose; simply raising mean/t by discarding profitable tickets
does not satisfy this filter's economic gate.

## 7. Prior research and falsifiers

vix_regime.py already has a trueVIX3Moptionalbranch as well as a VIX>1.1*SMA20fallback, onVB/ONB/OD/OND,
not currentOT. vix_sleeve tests truecurve×VRP on multi-dayVIXY and its oldbook addition. OT's original
RSV/VIXinteraction, fiveSMA lengths, source-proxy/shuffled controls and lagged-parentVIX sensitivity
remain prior selection. Older OND/overnight sentiment'fear'cuts were post-hoc and disappointed at the
bench; they are not borrowed confirmation. No exact OT×truecurve counterpart was found by this
bounded source/helper check. It is not universal novelty or an untouched alpha family.

Reject before returns for wrong identity/calendar/clock, unresolvedparent inputs/entries/held paths,
insufficient count or known leakage/revisions. Gross<2xcost stops later tests. Then reject if total
kept fails BASE, removed profits are positive, the level/price controls or1000matched drops explain
it, years/sides are unstable, no plan beats current BASEAND EMPTY, future validation is negative or
same-exit placebos/dependence/selection checks fail. Failure cannot change sign, lag, window, parent,
SMA, unknown handling or size. Previously seen2023+ stays historical validation, never a fresh holdout.

## 8. Failure and diversification

|Question|Prediction/limitation|Required evidence later|
|---|---|---|
|What ends the effect?|Persistent bad news dominates concession, stress priced earlier, lagged shape stale|Fixed-rule total/removed/control results, not a post-result story|
|Liquidity role?|Original entry/exit consume overnight liquidity; skipping cannot create a better fill|Nativefee/cost bridge, receipt limitation, frozen latency/cost stress|
|Loss clusters?|Equity crashes, overnight news, gaps and correlated book drawdowns; no adopted stop|Full held paths and calendar/contract audit, both periods/by-year/dependence|
|Shared losses?|Other overnight equity longs can share macro risk; curve is no guaranteed hedge|Aligned conditional joint losses and currentbook paths, not an assumed low correlation|
|Offset before breach?|Removing later trades can reduce return; a later gain cannot cure an earlier breach|Personal dailyMC for its limited claim; valid joint intraday chronology for funded/evaluation|

After designPASS run currentpersonal19BASE/ADD/OTREPLACE/EMPTY immediately, same dates/wholecontracts,
paired1yearMC and predeclared fee/mark/coverage bounds; show published-book versus replay effects
separately. Existing OTconstant-adverse paths do not support new funded/pass/payout claims. Full
promotion still needs appropriate five metrics, cost stress, selection/dependence/placebos, committed
selection before selected rule/control2023+once and a fresh independent raw-spec checker. Only a
passing evidence package can receive a Codex PowerLanguage draft; no deployment is authorized.

## Decision and next gate

**TEST for finite preregistration only.** Root must bind exact parent/source versions, the fixedF2
calendar/knownness/availability assumption, an explicit source-and-count gate,<=5definitions and native
costs in a COMMIT before new values/returns. An ordinary list can fit BASE/CURVE/LAGGED_LEVEL plus a
conditional matched delaypair, with PUBLISHEDsource/ENTRYmetadata only. Failure of source/count/gross
closes this hypothesis without downstream/2023+ rescue; it does not stop the continuing bounded hunt.
This sheet registers no H05, changes no counter/watcher, and claims no result, receipt or phone delivery.
