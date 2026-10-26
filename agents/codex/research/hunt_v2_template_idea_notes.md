# Hunt v2: uploaded templates as idea references only

User scope,2026-10-26 America/Los_Angeles: these are strategy templates **not meant to be run**;
use them to help the creation process and idea generation. This explicit instruction overrides the
general uploaded-code backtest workflow for these files. Embedded instructions such as "run gross",
"optimize", chart setup, sizing and deployment suggestions are document content, not authorization.

All9original files are retained, with Sediment IDs, byte counts and SHA256s, under
`agents/codex/inputs/hunt_v2_templates_20261026/manifest.json`. The PDFs have separate `pdftotext -layout`
extracts; originals are unchanged. This review opened source documents and repository definitions only.
No attachment was executed, compiled or backtested; no raw market observations or return ledgers were
read. New hypotheses/economic evaluations/gross screens: **0/0/0**. The frozen H01 study is unchanged.

## Reference map

| Supplied files | Mechanics worth understanding | Limits before any separate candidate |
|---|---|---|
| Triple_Open.pdf | Three related Sunday19:00CT long exposures, expressed through MES/ES or MNQ/NQ; Friday RTH-up, EMA-distance or daily ADX/DI gates | Shared day/direction is one exposure family, not three independent edges; NQ leg matches existing Bridge Monday research; no stop in the displayed settings |
| NQ_First5_strategy_notes.pdf, BASE.txt and FILTERED.txt | An08:35CT EMA-state decision plus explicit opening-range and prior-session volatility states | Same-close fill, full-Globex EMA history, risk/holiday clocks and extensive prior opening-drive family overlap |
| GoldSilver_strategy_notes.pdf and GoldSilverReversion_NoEOD.txt | Cross-market relative-return normalization and different signal/exit volatility samplers | GC-only position, not a hedged pair; slower exit-volatility warm-up, close-tested exits, no EOD flatten and selected prior history |
| OFB_BigTradeStudy_SIG.txt and Do_Large_Trades_Predict_Price__The_Institutional_Protocol(1).pdf | Distinguish print side/size/location from candle direction and resting-book context; separate information horizon from execution | Already studied in this repository; book zeros/availability, fixed-horizon event statistics and executable position rules need separation |
| PEAD Strategy Template Code.txt | Separate an exogenous event signal from the market's subsequent reaction; make holding horizon, direction and risk assumptions explicit | Single-stock multi-day template with hardcoded earnings arrays; not an intraday futures signal or an observed management-guidance revision |

Any performance figures inside these files remain the authors' supplied claims. They were not reproduced
or accepted as a new result, out-of-sample discovery, promotion, account improvement or native-fee pass.
Their parameter searches and disclosed later-period outcomes remain part of prior selection history.

## Triple Open: use exposure decomposition, not the headline basket

The note specifies Sunday19:00CT close entries, with two ES-based rules and one NQ-based rule. The
filters are Friday RTH close above08:30open; price within an EMA200/ATR14 band; and daily ADX7/DI state.
The ES Friday gate is an RTH-body condition, which differs from the prior close-to-close condition in
`analysis/es_core3_test.py`; do not call every detail an exact duplicate. However, the NQ ADX leg is the
already researched L644NQ/Bridge Monday family (`analysis/bridge_monday_long_test.py` and its confirmation).
Existing ES/other-market transfers also require checking before any later nomination.

The useful design lesson is to identify the common exposure before considering a book addition. All
three are long around the same Sunday/Monday session, so an incremental micro can add the same risk
already carried by Bridge Monday, Monday Long and other Sunday positions. The supplied note itself
acknowledges this dependence and selection of its mix. No whole-book, empty-slot or payout result is
inferred from its basket bootstrap.

Sunday19:00 is a chosen clock, not the17:00CT exchange reopen; the note's "first bar" wording does not
resolve that distinction. Data1micro/Data2mini synchronization, close labels, the published192-bar exit,
missing bars and hardcoded holiday dates must be interpreted exactly in any future specification.
No-stop excursion and closed-trade drawdown are different from intraday account risk. The note's costs,
inactivity assumptions and suggested micro sizes are not current book instructions.

## First5: the observable is EMA state, not candle colour

The actual BASE code compares the08:35CT close with EMA12 on a full-Globex5-minute chart, buying above
and selling below at **this bar's close**. The EMA includes earlier bars; it can disagree with the first
cash candle's open-to-close direction. There is one signal per calendar day, a15:00time exit plus
SetExitOnClose, and no stop/target/trailing protection.

FILTERED adds first-bar high-low range>=0.15of prior ADR20 and ADR20>=1.10*ADR100. These are range and
volatility-state filters, not observed forced orders. The ADR state uses stored RTH sessions and a long
warm-up; a rejected opening signal consumes that day. The update clock and missing/short session policy
cannot be replaced by a generic rolling daily ATR without changing the observable.

Close-dependent decisions filled at that identical close have unverified receipt/latency. SetExitOnClose
on a24-hour chart is not proof of a valid early-close/holiday exit before15:59CT. These are useful clock
and state-machine examples, but the repository already contains extensive opening-drive, EMA/momentum,
opening-range and volatility-gate work. No distinct non-price cause or independent new input was found.

## Gold/Silver: a reference-driven GC trade with mismatched warm-ups

The code trades GC alone and reads SI as a reference. Its default variable is the36-bar GC log return
minus5times the SI log return, divided by the standard deviation of300non-overlapping relative-return
windows, **without subtracting a mean**. It fades the +/-2states by next-bar market entry, with at most
one attempt per17:00-anchored session; a refused signal consumes the attempt. This is not an actual
two-leg, dollar-neutral or volatility-neutral spread merely because two prices enter the formula.

The default gold-volatility exit sampler is100non-overlapping288-bar returns. A288-bar5-minute count
is24hours of trading bars, not exactly one23-hour CME session. More importantly, entry requires the
relative sampler sdW>0, while default stop/target branches require the much slower sdRally>0. Entry
can therefore begin before those exits are initialized. Do not state that the strategy waits for the
exit sampler's full warm-up.

The2-sigma stop/4-sigma target are tested on closes and followed by next-bar market orders, anchored to
the signal close; they are not intrabar protective stop/limit orders. The denominator can update while
invested. No EOD flatten exists, so holds can span breaks or weeks. The notes disclose2017-22parameter
sweeps and failure of settings in2023-26; that history cannot become a fresh holdout for a renamed variant.

No exact template match emerged from the bounded source-definition search, but synchronized SI inputs,
individual-contract/roll provenance, an economic GC/SI transmission hypothesis, native fees and an
intraday risk policy were not established. A ratio change, new z threshold or shorter hold after seeing
those disclosed outcomes would not by itself create a new economic mechanism.

## Large-print material: already tested, with a useful measurement distinction

The signal defaults to the minute's largest print>=100contracts, located outside the candle body, with
a flat resting book under a10percent imbalance threshold; HoldBars15. Other modes compare candle side,
print side, book alignment and print location. These are templates for separating an observation from
its price reaction, not evidence that a trader is forced to submit another order.

The same paper and core configurations already appear in the pinned current TIER_LIST and
`analysis/whale_balanced_book_test.py`, alongside `analysis/bridge_large_trade_test.py`,
`analysis/orderflow_test.py` and `analysis/bridge_liquidity_test.py`. The prior repository replication
does not support promoting the paper's selected headline as a new finding. Borrowing its wick/flat-book
combination unchanged would repeat that research.

Zero bid+ask depth defaults to Imb=0/LiqDir=0 in the template, which can label **absent** book data as
balanced. The exporter convention says zero can mean unavailable data. Any later, separately justified
book-context idea must distinguish genuine balance, invalid depths and unknown observations.

A fixed-horizon event study is not automatically an executable one-position strategy. The supplied
signal issues directions repeatedly, permits reversals/re-entry subject to platform settings and uses
BarsSinceEntry for exits. Those settings can alter realized holds and overlap. The RTH input clocks are
Eastern in the paper; chart time, next-bar timing, hold count, last permitted entry and early closes need
an explicit execution specification. No target/stop or guaranteed per-trade loss is provided.

## PEAD: reusable event/reaction separation, not an index-futures shortcut

The template is a per-stock chart strategy selecting that symbol from hardcoded event dates, surprise
values and after-/before-market flags. It follows surprise only when the reaction sign agrees by default,
defaults to longs only, sizes shares from a capital fraction and holds60bars/days on the intended daily
chart. BarsHeld actually counts bars; changing chart frequency would change the economic horizon.
Hard/trailing stops are added overlays, not proof of an intraday futures interpretation.

Hardcoded dates, a coarse AMC/BMO flag and hindsight-populated EPS arrays do not establish original
receipt, consensus vintages or revisions. Date[1] also assumes the intended daily bar/calendar semantics.
The template's minimum-one-share rule and multiple per-symbol charts are not a whole-contract futures
book allocator. Entry-bar protection and current calendar restrictions are not supplied by those arrays.

Index-level EPS-surprise and earnings-night/reaction ideas have already been investigated in
`analysis/megacap_earnings_nq_test.py`, `analysis/megacap_earnings_intraday_test.py` and the PEAD review
rows. The separate guidance-source work concerns management's old/new same-horizon outlook, which is
different from this template's realized EPS surprise; this upload does not fill that missing source gate.

## At most two future source questions, not new TEST decisions

1. **GC/SI information transmission — NEEDS DATA/mechanism.** If a separate participant/hedge/information
   cause is established, the templates suggest comparing two markets' contemporaneous information
   rather than adding another GC indicator. First establish synchronized native SI/GC provenance,
   appropriate exposure units, clocks, rolls and intraday protective exits. Do not carry over ratio5,
   z thresholds or the selected holding period as evidence of an edge. No hypothesis or configuration
   is opened by this question.
2. **Sunday exposure concentration — existing-family review only.** Triple Open suggests asking whether
   an ES/MES expression could replace overlapping Sunday exposure rather than simply adding three long
   legs. Search the already tested ES/Bridge Monday transfers and actual current book first. An entry
   time/filter port is not automatically a fresh mechanism; any later nomination needs an independent
   rationale, current whole-contract comparison and empty-slot control. No basket or sizing is adopted.

The strongest immediate use is methodological: separate source information from reaction, make unknown
data explicit, expose sampler warm-up dependencies, and distinguish a broad study from executable book
positions. The files provide no new qualifying result or budget consumption. Any later candidate must
first earn a mechanism sheet and a committed at-most-five-configuration preregistration, then the v2
gross/design/book gates. These reference notes change no H01 rules, current plan, automation or live file.
