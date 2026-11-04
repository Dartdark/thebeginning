# Input-compatible fixed quantity arm: evidence receipt

Summary: Original account results are retained; an input-compatible sizing arm is separately preregistered.
Missing expected-open ATR inputs prevent certifying risk-budget quantities; fixed contracts avoid that dependency.
An independently reproduced DT source-clock error is repaired without changing its economic exit rule.
460 new definitions plus2,485 prior definitions and30 shared reservations fit the3,000 hard cap.
No amended account outcome preceded this evidence/plan/code/registry commit.

## What changed in our information?

Prepared source metadata at the original frozen commit found known stop inputs in only58/639 ONB30 trades,
10/99EOS and65/848LDF, with0/187MOC and0/87CLS. Fixed source stops remain known. These counts cover the full
existing source window; they are data-admission counts, not portfolio returns or independent source verification.
Independent timestamp checks reproduced the first ONB30 missing lookback: missing17:01 minutes and other overnight
holes occur during expected-open trading. A later source ATR estimate cannot certify the absent observations.

The old DT normalization sets kind2 time exits to close phase despite the existing strategy implementation's
next-bar open. The independent engineering review reports401 such exits,390 incorrect close mismatches, and
the2018-04-11 14:56 open6592 versus close6588.25 example. The new overlay must mechanically fix the source clock
for every such exit or preserve UNKNOWN. It may not repair only losing or mismatched-price cases.

## Why does this arm qualify for testing?

Quantity1,2,4,8,12,20 or equal2/4 in a predeclared pair is known before every source entry. No missing ATR is
needed to calculate the lot count. Source orders, protective exits, market quotes, target qualification and
account floor/DLL/cost rules remain material inputs and keep their original strict gates. This is a sizing test
of existing strategies, with no new alpha claim, indicator, timing filter, side selection or invented protective stop.

The menu covers all original18 sources for standalone sizing and the original12-source pair universe. It does
not select which strategies to include from their reported returns. Every reviewed menu request and alias is saved.
The amendment is an explicit correction to the initial design scope, with its prior outcomes counted, rather than
a replacement of the initial preregistration or a claim that only the new arm was searched.

## What has been observed already?

The original design completed2,485 definitions×244 starts=606,340 account cases. CURRENT50K has0confirmed passes,
4confirmed failures and240unknown outcomes; CURRENT150K has0confirmed passes,11confirmed failures and233unknown.
These imply wide unidentified pass probabilities, not evidence of zero true pass rates. Only three nonempty
original policies per account, all FC2B, clear pooled<=1%UNKNOWN; the original summaries remain fully retained.
For context, the original largest FC2B risk level has44/61/139 pass/fail/expire for50K and14/64/166 for150K.
The fixed-quantity menu was specified from admission/clock findings before these FC2B summaries informed selection.
No2023+ account validation or amended fixed-arm account result was inspected before this amendment commitment.

## What would disconfirm an improvement?

The new arm can expire too often, fail more frequently, lose on costs, have incomplete held quotes/source fills,
lack stable design neighborhoods, or fail the original historical recommendation gates. A baseline with nearly
all unknown risk-sized outcomes cannot support a narrow claimed pass-rate improvement. Preserve that limitation.
Conditional OHLC ordering, source signal reuse after resized/skipped trades and exact platform matching remain
unverified. Neither a repaired clock nor a broad fixed-lot search proves a tradable edge or global optimality.

Full frozen definitions and execution stages: `../plans/eval_audit_fixed_arm_20261104.md`.
Existing forensic/source/rule/quality records and original results remain under
`agents/codex/inputs/eval_audit_20261104/` and the hashed runtime archive. User decides allocation after review;
no trading plan, live account, broker setting, VPS, purchase or external message changes follow from this arm.
