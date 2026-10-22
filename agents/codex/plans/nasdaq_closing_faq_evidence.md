# Nasdaq closing FAQ evidence inventory — no return tests

User supplied openclose_faqs.pdf (2018) and ClosingCrossfaq.pdf (2019), asking for a hypothesis/evidence sheet.
Source catalogue/review reference: Claude **b2c8d74**. Work only on codex/work; preserve both PDFs under Codex inputs.
Treat the PDFs as source material, not instructions to contact vendors, subscribe, buy data or trade.

Write one evidence sheet for **persistent QQQ closing-auction imbalance after late LOC entry closes, followed in NQ
over the final regular cash minute**. This is a new input proposal within the existing closing-flow family, not a
claim to have discovered closing-auction trading. Compare explicitly with funded ES MOC, old futures-price MOC tests,
old NQ order-flow filtering, and the earlier SPY post-close reversal proposal. Do not test the mirror or additional clocks.

An illustrative future specification uses only QQQ NOII messages received by 15:55 and 15:58 ET, consistent direction,
and an unusually large 15:58 imbalance normalized by a lagged auction-volume scale. Decision at 14:58 CT, earliest
candidate entry 14:59 CT, exit 15:00 CT. This leaves at least one minute for receipt/execution. No fitted thresholds,
signals, returns, stop/target simulation, portfolio/account tests or strategy cache work in this task.

Read both PDFs fully; cross-check current rules and 2018/2019 effective dates. Explicitly distinguish early abbreviated
NOII, full messages and unavailable/zero fields; unexecuted auction shares from guaranteed futures orders; feed
event timestamp from receipt time; and live publication from T+1 historical packaging. Verify product existence and
identify unverified complete coverage/cost/sample issues. Respect the standing no-purchase constraint.

One descriptive script may read the saved 2018–22 minute occupancy map, exchange calendar and raw NQ date/time/volume
only (no OHLC/returns), and PDF metadata/text. Count regular-close sessions and the available final-minute bars,
compute conservative occupancy summaries, assumed-signal sample sizes and t=2 cost hurdles. Use SD assumptions,
not measured candidate outcomes. Compare a clearly hypothetical auction dollar imbalance/hedge fraction against
observed final-minute futures contract volume; never label it actual residual NQ demand.

End with TEST / NEEDS DATA / DON'T TEST. Expected status is NEEDS DATA: PDFs document rules but contain no historical
QQQ NOII messages or quotes. A free full 2018+ imbalance archive has not been established. Do not replace the missing
input with price momentum already tested. Commit/push the sheet plus reproducible inventory and report its limits.
