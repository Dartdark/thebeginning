# Chan transcript: evidence-sheet supplement and auction sample feasibility

User approved the recommendation to adopt explicit failure/diversification questions and continue auction-data
feasibility before further strategy testing. Work only on `codex/work`; current starting commit `57321a5`.
Read the builder brief, development process and source catalogue; remote Claude reference is `57ebec3`.

## Authorized work

- Add a reusable evidence-sheet template under `agents/codex/`, preserving the seven evidence questions in the
  reviewed builder brief's step 0. Link it from the local builder brief without changing existing promotion gates.
- Require a stated failure mechanism, liquidity role, expected common losses, executable risk limits and whether
  an intended hedge can help before an account breaches its trail. Treat these as predictions until tested.
- Apply the supplement to the existing QQQ pre-close persistence sheet, leaving its illustrative direction,
  observations, entry/exit and thresholds unchanged. Keep post-close reversal as a separate, untested research
  direction within the previously proposed auction family; do not add it as a fallback variant.
- Check public primary-source product/schema/sample documentation. Record what can actually be accessed without
  a purchase or credentials, the limits of any public sample, and a narrow no-return validation handoff.
- Produce a short review report, with a Summary of at most five lines and links for Claude.

## Sources and limits

The user supplied a transcript of Ernest Chan's QuantInsti webinar, YouTube `sFwyS-L-aDE`, 0:00–48:35.
It supplies development lessons, not a complete reproducible strategy or evidence of an NQ/QQQ edge.
Use the transcript's stop-loss/Kelly/volatility discussion with the qualifications already given to the user.

Read public documentation and directory metadata only in this task. Do not compute auction signals, NQ/QQQ
returns, correlations, candidate-event occupancy, execution outcomes or funded-bench results. Do not build caches,
read existing strategies' return arrays, download large all-market feeds, create a vendor account, access API keys,
contact vendors, subscribe, spend money or free credits, or touch live files/VPS/settings. Small public sample
availability is a data-feasibility observation, not a strategy trial. Return trials: zero.

## Decision and stopping rule

The template is an addition to Codex's workflow, not a change to portfolio sizing or the repository's central
development policy. QQQ stays NEEDS DATA until usable messages and timing/coverage are independently checked.
A single sample can establish format and limited content; it cannot establish history, power, an edge, receipt
latency or diversification. If a no-credential sample cannot be inspected with available tools, document the exact
artifact and remaining work. A later local sample inspection needs its own scope recorded before processing;
any return study still needs a separate strategy preregistration and trial accounting.
