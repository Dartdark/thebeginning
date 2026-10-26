# Distinct earnings information: definition gate, NEEDS DATA

Summary: The local EPS-surprise fields are not a new standalone research lead: the existing NQ study
already trades their weighted sign. A possible distinct information input is a change in an issuer's
forward guidance for the **same fiscal horizon**, observed in the original announcement. No usable
guidance history, exact announcement/receipt clock or intraday transmission evidence was established here.
Do not write an economic preregistration or run prices from this note.

Scope: saved source-code definitions, source document, filenames and the two earnings CSV header lines;
file hashes bind the reviewed inputs. The separate completed source-census manifest was then read to
integrate its limited metadata findings below. No raw futures values, strategy ledgers, new price/return
calculations, new network calls or account tests. New economic configurations: **zero**. This is a bounded definition
review, not an exhaustive claim about every file or an independent promotion checker.

## Existing mechanism that must stay closed

`analysis/megacap_earnings_nq_test.py:1–13` already defines event-session earnings trades and specifically
`S = sum(weight × sign(surprise %))`. Lines34–58 read `surprisePercentage`, assign fixed approximate
Nasdaq-100 weights, aggregate the signed surprises and trade `sign(S)`. It also defines following/fading
the earnings-night price move, changes to the name subset, a move threshold and a later entry clock.
Consequently EPS actual-minus-estimate, a weighted EPS-beat score, a different normalization, a different
index or a nearby entry time would not independently establish the user's requested new mechanism.

`analysis/megacap_earnings_intraday_test.py:1–9` adds report-day run-up, first-half-hour continuation and
the existing gamma-conditioned earnings-night rule. `analysis/ym_dow_events_test.py:1–11` adds Dow
earnings-calendar conditioning to overnight YM/ES and ZN price signals. The YM definition does not
independently test EPS surprise; that omission is not permission to port the already tested NQ mechanism.

Both local CSV schemas are exactly:

`ticker,fiscalDateEnding,reportedDate,reportedEPS,estimatedEPS,surprise,surprisePercentage,reportTime`.

The old NQ source identifies Alpha Vantage EARNINGS as the source. It does not provide a retained original
response, acquisition/receipt timestamp, forecast-vintage timestamp or issuer-release document in this
CSV. `pre-market`/`post-market` is an event bucket, not an observed minute of publication. This review
does not establish whether any value was revised or whether an estimate was available before the release.

## Completed source-only metadata census

Authority: `analysis/outputs/codex_forward_guidance_input_gate/manifest.json`, completed
`2026-10-26T11:32:21.513915+00:00`, source plan `ac88ccd`. It selected only ticker, fiscalDateEnding,
reportedDate and reportTime; the manifest records no EPS/surprise-value use, price/financial-output reads,
signal generation, strategy replay or network request.

For reportedDate2018-01-01through2022-12-31, the saved census retains310metadata rows from16collected
issuers on227distinct reported dates;58dates have multiple issuers. It records zero repeated identity
rows/groups and zero selected metadata exceptions. These counts describe the collected tables only.
They are a local report-date ceiling, **not guidance changes, original issue documents, futures trade
sessions, independent events or effective n**. No observed comparable guidance pair is identified.
The historical selection of the collected issuer sets remains unresolved; modern names and weights
cannot establish historical constituent coverage.

Both schemas lack all literal required fields named by the plan for same future horizon, guidance
intervals, units/accounting basis, original documents, publication/receipt, vintage/status/currency/share
basis and index membership/weights. This is an exact-schema finding with no alias inference, not proof
that no external free source exists. An absence of metadata exceptions does not certify the underlying
EPS table's original vintages, announcement identity, timeliness or economic validity.

## One distinct input hypothesis, not a selected trading rule

**Forward-guidance revision repricing:** an issuer changes an earlier management revenue/earnings range
for the same future fiscal period. Investors may revise cash-flow expectations and portfolios as the
announcement is read. That information is economically different from a just-reported quarter beating
analyst EPS estimates. There is no established compulsory futures order, known hedge amount or delayed
positive return in this review. Guidance can already be priced, offset by other news, withdrawn rather
than quantified, or interpreted differently from its midpoint change.

The independently varying observable would require the old and new management ranges, units, accounting
basis, fiscal-horizon identity, original document identity and timestamps. No threshold, direction, bar
clock or symbol is selected. NQ could be a direct hedge only after constituent membership/weights and
index transmission are evidenced; a company-specific announcement need not create net NQ demand.
An eligible eventual signal frame must be one of1/5/15/30minutes, with publication → receipt → decision →
order → fill explicitly separated. The existing CSV fields cannot manufacture that clock or observable.
Changes in interval width, overlapping ranges, withdrawal/reinstatement, currency, fiscal weeks,
split-adjusted share counts and GAAP/non-GAAP basis must remain explicit. A new midpoint is not automatically
an economically comparable revision. The proposed variable is issuer guidance against its earlier guidance;
it is neither a consensus forecast surprise nor a realized-quarter EPS beat. Full eight-question evidence
sheet: `agents/codex/evidence/forward_guidance_revision.md`.

| Required input before TEST | What this review establishes | Concrete next source gate |
|---|---|---|
| Original old/new issuer guidance for the same fiscal horizon | No guidance field in either CSV; no guidance/consensus/revenue/press-release filename found in the bounded local data/input filename search | Retain actual issuer release documents, original units/basis and fiscal-period mapping; reject incompatible comparisons |
| Original announcement and receipt clocks | Only reported date and coarse reportTime bucket are present | Verify exact timestamp/timezone, revisions and an implementable data receipt convention; do not infer it from a price spike |
| Point-in-time constituent membership and weights | The old NQ code uses fixed approximate weights, not a historical constituent series | Supply as-of membership/weights before claiming index exposure or sizing demand |
| Intraday economics and native costs | No guidance-event count, gross effect or return test exists | Count audited2018–22 events without outcomes, then assess effect-size/power and realistic NQ/MNQ fees/slippage before any economic plan |

The ordinary repository NQ cost assumption is$7.25roundtrip plus$5for each market/stop fill
($17.25for two market fills). MNQ is modeled separately at$1.24roundtrip plus$0.50per market/stop fill
($2.24for two). These are research assumptions, not verified new broker quotes. They establish a hurdle,
not that guidance information can overcome it. Native micro listing/parity and event-time execution still
need checking. No opportunity count or assumed profit is invented.

Potential falsifiers before returns include no comparable same-horizon pair, no original observable clock,
the update arriving after the proposed decision, no constituent relevance, or a supposedly new variable
collapsing to the existing EPS-surprise/overnight-return signal. If these source gates fail, do not replace
guidance with the old EPS fields under the same label. At a later economic stage the predeclared failure
cases must include opposite revenue/margin news, immediate price incorporation, scheduled-news confounds,
thin-session gaps and clustered earnings-season exposure. Marketable entries consume liquidity; no passive
liquidity benefit, empty account window, hedge or before-breach offset is established.

Decision: **NEEDS DATA**, with no claim that this candidate is more promising than the current source gates.
The smallest next step is a bounded original-document/clock feasibility study, not a new futures return run.
The committed source-only metadata plan `agents/codex/plans/forward_guidance_input_gate.md` (`ac88ccd`)
freezes an outcome-blind census; its execution and report remain separate from this definition review.
Any eventual TEST decision still needs a complete evidence sheet and a separately committed≤5configuration
plan before2018–22 prices, followed by the user's full validation, dependence, selection and checker gates.
This note adds no trial, milestone, notification, user-action request or reason to pause continuing research.

## Reviewed file bindings

| File | SHA256 |
|---|---|
| `analysis/megacap_earnings_nq_test.py` | `e8665de46140c989f537a955bb16f8545fd9ae2b0d6c778a74b06eb35a159b43` |
| `analysis/megacap_earnings_intraday_test.py` | `c5ff4cc9634f1cfff01c50be887536aa8c8dbcfcb43402020f595826d25e11e4` |
| `analysis/ym_dow_events_test.py` | `af1f4969ade0384cadbbcadcaecab255b5f2b13183af2b8e84cac55fd421957f` |
| `data/ndx_megacap_earnings.csv` | `97d87d8de9470143d14c6513cd9c0a5eaead5b6867af03f15acfb57cde2ec5b2` |
| `data/dow_heavy_earnings.csv` | `3e8ae8677c7024377b09139ce3b8296c4da2dd77fc17cbb90221309579a00e00` |

Separate quote-field caution: `tools/exporters/OFB_OrderFlow_Exporter.txt` binds slot9/10 to pulled bid/ask,
but only reads values from a historical DLL by bar key. Its names and historical accessor do not establish
underlying cancellation definitions, resetting/normalization rules, absence of retrospective corrections,
or original receipt time. It explicitly says zero means no data for a bar, not a real zero. Existing
`analysis/bridge_filter_scan.py` already uses five-minute pulling/depletion differences as plan filters.
A cancellation/depth label alone is therefore neither a new economic mechanism nor verified point-in-time
history. No quote-cancellation candidate is proposed or tested in this note.
