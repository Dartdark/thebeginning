# OT curve clock admission: NEEDS DATA

**Decision: the proposed F2daily-history feature is not yet admitted under RESEARCH_CONTROLS.**
A fixed delay reduces timing risk, but cannot by itself establish when the exact historical CLOSE
values were public or rule out later revisions. The earlier TEST nomination permits source inquiry;
it is not a sufficient availability finding and must not authorize an economic run while this gate
is unresolved. No sign, lag, window or parent rule was changed, and no H05 was registered here.

Source-only follow-up,2026-10-26. Read the runtime skill/networking reference and current executor
`/etc/codex/network-policy.json` before network calls. Environment status reported running,
observations_current=true, restricted policy enforced; GitHub/raw hosts are allowed, Cboe/CDN hosts
are not, VPNfalse. No Cboe request, policy bypass, stopped web tool or403retry occurred. Only allowed
GitHub source/document searches and document text were used. No historical input CSV/workbook/cache,
new input values, signals or returns were opened/computed. No counter, source data or other note changed.

## Primary text actually located

Cboe Exchange, Inc., **White Paper: Cboe Volatility Index**, copyright2019, printed pp.3–4. A
third-party PDF-to-Markdown copy was read at:

<https://github.com/chanmainvest/paper_library/blob/6677522b06dc1d9be923c094500433b78b7682c6/papers/white-paper/index.md>

Git blob4e7a989ae4574203adeeb6064e2a3e8d98c02997; inspected lines1–102only, not numerical appendices.
This is a mirror/conversion of attributed primary text, not a newly authenticated download from Cboe.

- Printed p.3 states: **"The VIX index is now available ... during regular trading hours between
  9:30 a.m. and 4:15 p.m. ET."** It separately describes extended-hours dissemination beginning2016.
- Printed p.4 names **"the Cboe S&P 500® 3-Month Volatility Index (VIX3M)"** among Cboe's other indices.
- Those passages support the VIX public calculation/dissemination concept and VIX3M instrument
  identity. They do **not** specify VIX3M's exact closing-value/publication schedule, the time the
  historical CSV row first appears, or a guarantee that today's historical CLOSE equals the value
  observable at the proposed past decision. VIX derivative final settlement is a separate concept.

A source-document registry was also located at OpenBB commit7df7d0c5592bf25be88e87e130a05c71e243d2d8,
`openbb_platform/providers/cboe/openbb_cboe/assets/index_documents.json`,
Gitblobc1a78582d2df64b885b8b4913bb4613a5605e728. It links Cboe's **Volatility Index Methodology —
Selected SPX Target Expected Volatility Term Indices** and **Cboe Volatility Index Mathematics
Methodology** under `cdn.cboe.com/api/global/us_indices/governance/`. The primary documents' bodies
were not located at an allowed source in this bounded lookup. A registry link is not a quote
from the document, so no VIX3M closing/publication/revision rule is attributed to it.

## Practical public information versus file/vintage evidence

Individual historical receipt logs are not inherently the only possible evidence. Documented
public dissemination, the exact closing-observation definition and a defensible binding of the
historical series to that observation could establish a usable public information time without
claiming that this research machine received each historical tick. That finding still needs actual
source support. It cannot follow merely from a familiar index name, two matching date labels or a
retrospective file called Cboe history.

Three distinct clocks must remain separate: the underlying option/index observation; dissemination
of an indicative/closing index value; and publication/revision of a daily historical-file row. A
market close is not automatically a file-availability timestamp. Nor does a present-day publication
schedule prove every historical schema/vintage behaved identically.

The proposed F2rule selected the second expected session before parent RTH dateD and assigned
availability after the intervening F1close. That allowance is **an assumption**, not evidence. For
ordinary dates it assigns availability roughly24hours after F2close and enters roughly50hours after
that close; neither elapsed interval proves the specific row was available or final. Do not walk
back to another lag, use today's archive to label missing historical receipts as known, or promote
UNKNOWNKEEP into observed backwardation merely to get a test running.

For example,F2Wednesday16:15ET,F1Thursday16:15ET andDFriday18:05ETentry are49hours50minutes from
F2close to decision, although the draft assigned availability at F1close after only24hours. These
are different claims. Since no H05data/returns have been inspected, a later **source-justified**
predata clock correction is possible if documented, its initial-assumption history retained and the
finite plan committed before execution. That would not be return tuning; adding delay without new
availability evidence would still not establish admission. No such correction is made in this note.

## Additional warning context, not a primary historical guarantee

A new secondary source, Radu Pop's ADR-0009, records that Cboe daily-file updates can arrive about
18:00NewYork through two days after the close and explicitly retains fetch hashes/provenance:

<https://github.com/raadupop/primescore-markets/blob/98da792c8f4a11e0aa43de54aa733a1730ac7ceb/doc/adr/0009-cboe-index-history-and-fred-cross-check.md>

Gitblob3a54e528ccc7630e437448b114bc94a7dfa8f1ec. Its LIMITATIONS search excerpt reports a measured
VIX delay of about57hours in2026. These are a secondary operator's claims, **not independently
verified primary observations or2018–26 bounds**. They cannot prove a leak in the owned data/OTbook,
but they are enough to reject reasoning that "calculation ends16:15, therefore the history file
must be available then." A copy of a current close does not authenticate a particular earlier vintage.

## Smallest remaining admission evidence

Before economic execution, establish both the exact VIX3M closing/dissemination definition and why
the selected same-pin historical CLOSEs represent information available by the fixed F2/F1bound.
Suitable evidence could be primary closing/publication/revision documentation plus a supported
historical source binding, or genuine contemporaneous archived observations/as-published vintages
with known instrument/date/capture clocks. If evidence only supports public broadcast values rather
than CSVavailability, say so and verify that the input is the same closing observation; do not
silently equate the two. The unchanged parent's current-day VIX input retains its separate source/
Data2-date admission questions; this note does not allege that its adopted result is wrong.

This bounded lookup used nine targeted GitHub searches and a small set of source/document reads.
The last two searched the exact Selected-SPX-Target-Term methodology filename and'VIX3M disseminated
Cboe'; they found document links and secondary implementation descriptions, not the missing primary
VIX3Mclosing/publication/revision passage. It stops here rather than repeating broad searches.
**NEEDS DATA, no economic authorization from
the clock assumption alone.** This is a candidate-specific prerequisite, not a workspace blocker,
request for purchases/settings changes, trading instruction, alert milestone or pause of the hunt.
