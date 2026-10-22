# ETF fails-to-deliver → pre-open closeout buying: DON'T TEST

Summary: Rule 204 supplies a real closeout mechanism, but public SEC balances arrive weeks after the relevant deadlines.
Aggregate fails do not reveal their age, the responsible participant or an active obligation to buy before today's open.
An optimistic 251-trade design scenario needs $93 gross per ES at assumed $500 SD; the data timing fails first.
08:01–08:25 CT is about 87.1% flat by weekday-weighted minute averages, not verified event-specific availability.
Do not test historical settlement dates as if the files had been published then; FINRA short volume does not repair this.

Evidence inventory: `analysis/codex_free_data_evidence_inventory.py` →
`analysis/outputs/codex_free_data_evidence/inventory.json`.
Scope record: `agents/codex/plans/free_data_evidence.md`, **41ffc93**. Catalogue/task source: **e097c0f**.
Candidate return tests / strategy trials: **0**. No downloaded fails history joined to prices; no live changes.

## 1. Who trades, and what forces it?

Clearing participants have closeout requirements for delivery failures under
[Regulation SHO Rule 204](https://www.sec.gov/investor/pubs/regsho.htm). A purchase may close out a short-sale fail;
deadlines and permitted remedies vary with its cause. A fail is not necessarily a short sale. Some categories permit
borrowing or different timing. Thus a fails balance does not mean the same number of shares must be bought today.
Use the settlement rules applicable to the historical date, not a fixed trade-date offset across changing regimes.

The proposal is to anticipate SPY closeout purchases before the 08:30 CT cash open through ES. QQQ could analogously
reach NQ. It is a real settlement obligation in the underlying ETF, but the public data cannot identify active orders.

## 2. Direction, size and timing before entry

Hypothetical trade: long ES 08:01–08:25 CT when an **observable, still-active SPY closeout obligation** is unusually
large. This is a feasibility specification, not a backtest rule or registered trial. The crucial observable does not exist
in the proposed public dataset. Sorting historical settlement balances and trading their presumed deadline would look ahead.

`fails quantity × prior close` gives dollar value of a dated outstanding settlement balance. It gives neither today's
required cash purchase nor today's ES hedge. The balance includes different underlying fails over time; its changes
cannot recover the age of an individual fail. There is no defensible estimate of net buying dollars, futures hedge
fraction, or participation versus pre-open ES volume. Reporting those as known would defeat the evidence gate.
Post-publication trading would be a different, stale-information hypothesis without the proposed compulsory-buy deadline.

## 3. Does it reach NQ/ES directly?

The required delivery is in the ETF. An intermediary might hedge a SPY purchase with ES, but buying SPY and **selling**
ES as a hedge can have the opposite futures sign from the proposed long. Whether the hedge is initiated or removed,
and when, are unobserved. A SPY closeout requirement is therefore not proof of a same-sign ES order. QQQ/NQ has the
same identification problem. No reliable direct-hedge size or sign is established.

## 4. Free history, availability and the FINRA trap

The [SEC fails archive](https://www.sec.gov/data-research/sec-markets-data/fails-deliver-data) is free, reaches back
to 2004, and lists both half-month ZIPs throughout 2018–22. Fields include settlement date, CUSIP, symbol, quantity
and prior close. The first half is released at month-end, the second around the middle of the following month;
the SEC guarantees no exact posting date. These lags occur after the relevant closeout clock.

The archive reports aggregate outstanding balances, not daily new fails or their age. Neither responsible participant
nor fail category/deadline is supplied. Historical archive links and documentation were inspected; full ZIP coverage
and point-in-time publication receipts were not downloaded or audited. An attempted archive-link resolution through
the research browser failed; the documented timing/identification failure already stops the proposal without a bulk download.

[FINRA's daily short-sale files](https://www.finra.org/finra-data/browse-catalog/short-sale-volume-data/daily-short-sale-volume-files)
are also free, but describe reported trading volume, not outstanding shorts or delivery failures. FINRA's
[interpretation notice](https://www.finra.org/rules-guidance/notices/information-notice-051019) explains that offsetting
buying may be absent and the reporting venues are incomplete relative to the whole market. They cannot identify
today's still-open closeout obligation.

Publication is no later than 18:00 ET (17:00 CT), with possible subsequent updates; same-day pre-close use is invalid.
The **Consolidated NMS** product starts **2018-08-01**, not January 2018. Older individual-facility files cannot silently
be spliced into the consolidated series as identical coverage. An attempted January-2018 consolidated URL was
inaccessible; the official start date is the authoritative reason not to assume that coverage.

The input is genuinely non-price settlement information and costs **$0**, but public history does not imply timely
knowledge of the forced flow. Private participant-level obligations would be different data, outside this task's budget.

## 5. Costs and gap check

`analysis/s_rank_es_round1_test.py` sets ES commission $5, tick 0.25 × $50 = $12.50, plus one tick per market fill:
**$30/ES round trip**. Its 1.5× gross-cost floor is $45. This differs from the brief's full-NQ $17.25 convention.
No expected move can be assigned to an unidentified current closeout flow.

For 08:01–08:25 CT, the saved funded-roster occupancy map gives marginal flat-minute fractions Monday 49.2%,
Tuesday–Thursday 100%, Friday 83.0%. Equal weekday weighting gives **86.4%**; weighting by the 2018–22 cash-session
weekday mix gives **87.1%**. Existing Monday holdings and Friday morning trades are the main overlaps. These are
minute averages, not event-conditioned flat dates or the probability that a whole trade window is flat. Test populations
must include all eligible events; overlap would be handled later at account level, never by selecting quiet roster days.

## 6. Numerical power check, despite the earlier stop

There are **1,259 cash sessions** in the 2018–22 XNYS calendar. For scale only, a top-quintile signal would yield
approximately **251 trades**, before missing or late publications. This fraction is an assumption, not an observed
count. The proposed public source identifies **zero verified timely active closeout events here**; that describes
the evidence available, not an assertion that no closeouts occurred.

| Assumed one-ES per-trade SD | Hypothetical n | Net mean for t ≥ 2 | Gross mean including $30 costs |
|---|---:|---:|---:|
| $500 | 251 | $63.12 | $93.12 |
| $1,000 sensitivity | 251 | $126.24 | $156.24 |

Formula: `2 × assumed_SD / sqrt(n)`. SDs are planning assumptions, not measured strategy SDs. Persistent fails
would make events dependent and raise the hurdle. The figures are a single-trial screening illustration, not evidence
of an edge or the repository's promotion threshold. More observations cannot repair unavailable decision-time data.

## 7. Catalogue difference and decision

`TIER_LIST.md` already includes DIX-high long and several opening/expiry/flow rules. This proposal concerns an
explicit delivery-closeout clock and SEC settlement obligations, not the old short-volume sentiment signal.
A FINRA short-volume long would recycle the already explored family and is **not** counted as another candidate.

**DON'T TEST.** The required balance cannot be dated to an active obligation known before entry; the futures hedge
sign is also unobserved. Drop this public-data specification without a return trial. Reconsider only if a genuinely
free, historical, pre-deadline obligation feed with identifiable cause and age appears. No paid data or private account
access is proposed. Claude reviews before any replacement plan.
