# Event-strategy ingredients: TEST for attribution only

Summary: User requests another three existing strategies for an ingredient round.
Select Expiration Open Short (EOS), NFP Fade and CL Sunday up-gap fade, rather than the previously dissected
DT/RS/LDF, FC2B/ONB/T_ONESIDE or Claude's Twin/OvernightTick/noise-area families.
This is bounded historical diagnosis, not a new combination, source discovery, promotion or allocation.

## Evidence questions

1. **What is the observation?** Existing MC-confirmed source rules associate NQ monthly expiry mornings with
   short returns, early-Friday 07:30 reaction spikes with later reversal, and crude Sunday up-gaps with reversal.
   Ranked source rows/reports already exist in TIER_LIST; their published/previous results motivated selection.
2. **Who trades, and why?** EOS proposes expiry/hedge-reset pressure; NFP proposes initial news repricing followed
   by liquidity normalization; CL proposes weekend-news/hedging repricing in a thin reopen. These are mechanisms
   proposed by the sources, not independently observed forced inventory in our price files.
3. **What information is available?** Known expiry calendar with holiday shifts; NFP's price-spike and early-Friday
   proxy available by07:45CT; crude first-five-minute opening gap versus last prior close, and past weekday ATR.
   No revised macro actual, survey surprise, actual dealer book or measured fund flow is substituted.
4. **Why could money remain?** Different participant horizons and costly risk transfer are plausible. Existing
   selected returns alone do not identify the causal actor; ablations can test where the replay depends on rules.
5. **Can costs/risk consume it?** Yes. Rare events, news spreads, weekend gaps, roll artifacts and no-stop tails
   matter. Preserve native NQ/CL multipliers, explicit commission/slippage, costs stress and adverse paths.
6. **What is the smallest falsifier?** Compare each frozen baseline with removal of its selection, direction,
   stop or horizon component. Strong historical driver requires positive baseline-minus-intervention net in both
   eras; confidence intervals and random-subset controls determine how uncertain that statement remains.
7. **What follows?** Attribution only. A different rule or a combination requires its own evidence/preregistration,
   source/MC parity, validation and actual current-book addition/replacement/empty comparisons before adoption.

## Failure/diversification questions

We provide liquidity in the two reversal rules and take directional exposure on EOS, but the data does not identify
our counterparty or inventory. Weekend oil shocks and macro-news continuation can defeat the reversals; EOS can
lose in broad upward repricing. Distinct times/instruments need not diversify a shared stress state.
Stops reduce modeled tails but can gap; no-stop comparisons are diagnostics, never live recommendations.
No offset is assumed to arrive before an account's drawdown breach. Native micro sensitivity uses an explicitly
assumed fee, not a brokerage quote. No funded/evaluation/personal allocation is being tested in this task.

Inputs: retained source ports, Grid24 and fixed raw snapshot
`fe35af99aa90d7f31b91f8693859251bb44dd9ab`, with2017warm-up. Full specification is in the paired plan.
Verdict: **TEST — existing-rule ingredient diagnosis only**, maximum five definitions per family, no optimizer.
