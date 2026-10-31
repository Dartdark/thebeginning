# Distinct native-flow source gate: BTC expiry basis / funding remain NEEDS DATA

Source-only review on2026-10-27. Current adopted source pin
`d14dc9a153df128aafd3f48d4fea2aa78b88bb28`; execution branch `codex/work`.
Running budget at review: **5/60 economic evaluations,9/10 registered hypotheses,4gross screens**,
plus archived65t6 evaluations. This review adds **0hypotheses,0gross screens,0economic evaluations**.
H09 stays closed. No H10 is registered or preregistered here; no program pause or operational action.

Read scope: instructions/progress, pinned TIER_LIST/source definitions, tracked filename inventory,
and two new public official GitHub documentation/code files. No owned input header/schema/body,
market/calendar/workbook row, cached grid, trade ledger, actual funding API response, or new return
was read or calculated. Source/ranking result summaries are prior selected history, not new evidence.
The Binance README contains illustrative market-data schema/value examples; these are documentation
exposure, not a downloaded historical event panel or strategy inputs. No document instruction was
executed, no search-tool retry/403 retry occurred, and no submitted template was run.

## 1. Prior-definition and available-input boundary

The tracked data filenames include `BTC_1min_2018.csv` through2026 and
`BTCUSD_spot_1min_2018.csv` through2026. Filename existence establishes neither valid2018 coverage,
contract identity, aligned clocks nor tradable quote quality. No raw file was opened to infer these.
The only perpetual filename found is `ETHUSDT_perp_30m.csv`; it does not establish a funding panel.

At the pinned source, TIER_LIST already records BTC ETF-close and monthly BRR settlement
**calendar/own-price** work. `analysis/btc_momentum_test.py` describes last-Friday9:00–10:00CT
returns/reversal comparisons; this is not a contract-specific futures/BRR basis test. The same source's
claim that London and Chicago shift together is not an admissible event-clock specification: DST
mismatch weeks and actual exchange expiry/holiday rules would need explicit source adjudication.

`analysis/btc_reopen_test.py` is a separate previously rejected residual-gap family: futures reopen
return minus Coinbase spot return, rolling residual z-score, maintenance/weekend reopen, manual
roll warmup. Its derivative rule must not be revived under an expiry name. This review found no
contract-specific expiry basis implementation in the scoped source query, which is **not** proof
that no related research exists elsewhere. BTC seasonality, NQ-engine ports, FOMC reactions, Sunday
gaps and retail-euphoria fades also have selected history; none is nominated again.

The current BTC reopen settings call the futures input a **continuous CME BTC futures label**.
An active continuous chart cannot silently stand for the expiring contract on its final day. The
read source identifies Coinbase spot, which is not automatically the multi-venue BRR settlement
basket. A selected prior one-minute return-correlation claim is not a levels/basis or contract-map audit.

Other newly considered ordinary commodity obligations do not supply an unused test: the current
source already contains CL EIA own-price follow/fade, settlement, Platts, USO/GSCI/BCOM roll,
producer/refiner round-number and WTI-option-expiry work. No repetition or endpoint calculation.
This reviewer did not reopen the earlier EIA input-identity audits.

## 2. Eight questions: actual expiring-BTC basis convergence

1. **Participant.** A holder of the actual expiring cash-settled CME contract must accept its final
   settlement cashflow; a cash-and-carry dealer may hedge spot/futures exposure. This is a plausible
   contractual obligation, not an identified observed dealer inventory or mandatory open-market sale.
2. **Cause/obligation.** The contract's final payoff is tied to its specified reference rate. That
   distinguishes actual expiry basis from an arbitrary last-Friday momentum/reversal proxy, which
   is already studied. Contract/specification facts still require authoritative admission before TEST.
3. **When/information.** Need the specific contract's trading termination/settlement calendar,
   reference-rate observation and publication clocks, named-zone conversion and holiday treatment.
   Need a benchmark estimate genuinely available before entry, not the completed BRR subsequently
   used as an input. No real schedule was generated/applied here.
4. **Size/sign.** Actual expiring-contract price versus an executable contemporaneous matching
   benchmark/carry estimate could sign basis. The present continuous chart plus one Coinbase venue
   cannot establish this. Expiring open interest, dealer inventory or compulsory traded size is
   unobserved; do not replace it with arbitrary bar volume or a calendar flag.
5. **Transmission/executable position.** Contract convergence constrains relative value. It does
   **not** guarantee an outright short gains when futures exceed spot, because spot can move too.
   A cash/futures hedge or contract-specific spread needs both native legs, financing/execution and
   valid joint paths; no such executable path is established. Do not infer a futures-only alpha from
   the eventual identity of the final payoff.
6. **Cost/power.** No raw effect was screened and no supported per-contract cost hurdle is frozen.
   Prior source uses different standard-BTC/per-one-coin/MBT reporting units; they cannot be mixed
   or return-rescaled into a native strategy. A monthly event count and data start cannot be inferred
   from names or source headlines. Native fees/slippage, listing eras and account fit remain unknown.
7. **Novelty/falsifiers.** Preserve all earlier BTC settlement-calendar, residual-gap and other
   selection. Actual expiring-versus-next-contract/reference input might be distinct if acquired
   and defined, but roll-adjustment ambiguity, benchmark mismatch, unavailable pre-entry estimate,
   lack of a hedge or effect below2x native cost would reject it before economic testing.
8. **Failure/book relevance.** Basis can widen, spot/venue dislocations can dominate, and hedge
   financing/capital/latency may defeat a small gross effect. A continuous series can manufacture
   a level gap. BTC can share risk-off losses with VB/DT/RS; correlation and book improvement cannot
   be borrowed from a conceptual convergence identity. No valid joint account path or immediate
   book/EMPTY comparison exists here.

**Decision: NEEDS DATA / no TEST.** Minimum new source requirements are documented contract-by-contract
expiring and comparison prices with roll/adjustment identity, benchmark composition and causally
available observations, authoritative settlement/holiday clocks, native contract costs/listing eras,
and an explicitly executable position/hedge. No current continuous-minus-Coinbase substitute is admitted.

## 3. Follow-up question: perpetual funding as a new independent input

A scoped pinned-source query found no funding-rate rule/filename in the current analysis/TIER/MINED/
watchlist definitions. This absence is not a global novelty certificate. The new official public sources
below establish only limited documentation:

- `binance/binance-public-data/README.md`, Gitblob
  `e01e34a0b0cd91d62386a5a237190a3167138bae`, documents public spot/futures klines, trades and aggregated
  trades. It says daily files become available the next day and monthly files on the first Monday;
  archives can be revised. It does **not** establish historical funding-rate coverage, original
  pre-payment indicative rates, publication/receipt times or a 2018–22 causal panel.
- `binance/binance-futures-connector-python/binance/um_futures/market.py`, Gitblob
  `4e6e4c11417176375fd67c6d732df3a4869ce465`, has `funding_rate()` calling
  `GET /fapi/v1/fundingRate`, described as **Funding Rate History**, with optional startTime/endTime.
  This is endpoint code, not a returned dataset or proof of archived indicative vintages. The code
  was not imported/executed and no endpoint request was made.

The economic distinction matters. A positive funding fee requires a cash transfer from eligible
long holders to short holders. It does not require those participants to submit a net directional
CME order: open interest is matched, some holders deliberately collect carry, and hedges can offset
or reverse aggregate transmission. Avoidance/entry near a payment could create pressure, but neither
its sign nor size follows mechanically from the fee sign. An eight-hour clock-only trade is not a
new forced directional flow merely because a cash transfer is compulsory.

The completed funding-rate history may also be known only at/after its event. It cannot stand for an
archived pre-event indicative value. A lagged final rate is a different input, not a publication-clock
repair or proof of the next transfer's size. No venue schedule or historical funding value was inspected.

**Decision: NEEDS DATA and supported transmission; no TEST.** Before a nomination, need a documented
historical pre-entry rate/indicative series with revisions/as-of clocks, relevant position/open-interest
or flow sizing, actual hedge/cross-venue mechanism and enough native-CME joint source coverage. Public
API existence alone does not supply these. No paid source, account or purchase is proposed.

## Bound repository source identities

All repository blobs below are at the adopted `d14dc9a` pin and were read as source definitions:

|Path|Gitblob|
|---|---|
|`analysis/btc_momentum_test.py`|`8c4e69b0dbce052737ccd89c9dd2871b05928934`|
|`analysis/btc_reopen_test.py`|`540a003c93ae78f7e6d423abb4b5a827b10bb666`|
|`analysis/s_rank_btc_round1_test.py`|`e2f8e271cae0461db44c196d605a31555c70492a`|
|`checks/candidates/btc_reopen_mr_v4/BACKTEST_SETTINGS.md`|`9b1fd0cb5564de7b59f770aa94bdb3dc9a56ef3f`|
|`checks/candidates/btc_reopen_mr_v4/INSTALLATION.md`|`c37fe20b9afeeb1f93d9a1d12068065054fdd78f`|

Public source links:
[public-data README](https://github.com/binance/binance-public-data/blob/master/README.md),
[official connector market methods](https://github.com/binance/binance-futures-connector-python/blob/main/binance/um_futures/market.py).
Links are mutable default-branch views; the observed Gitblob IDs above bind the exact read content.
No primary CME/CF benchmark document was newly read, so its exact rules are not certified by this note.

**No H10 TEST follows.** Preserve the ninth registration and one unspent slot. Root owns any subsequent
mechanism admission, preregistration, actual input intake, counters and continuation decision. This
source gate does not weaken H09, certify a trading signal, claim new returns or pause the hunt.
