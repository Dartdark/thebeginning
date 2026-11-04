# Independent result and recommendation-gate review — 2026-11-04

Summary: **Artifact checks PASS; neither replacement recommendation gate is earned.**
Verified all 12 cost/cushion scenarios, 86,016 saved cases and 96 paired 90% bootstrap calculations without replaying a strategy.
The four nominees have no reached UNKNOWN outcomes, but CURRENT remains 88.50%/85.04% UNKNOWN for fresh 50K/150K comparisons.
The strongest fresh 50K candidate passes 45.09% and fails 45.65%; a quarter cushion raises its failure rate to 81.58%.
These conditional historical results authorize no allocation, installed guard, funded/personal inference or native-execution claim.

Reviewer: `eval_loss_forensics`, independent of pipeline/strategy implementers. Exact machine-readable evidence and report/case hashes are in `final_results_review.json`; reproduction is `final_results_check.py`. This script reads existing artifacts and repeats statistical arithmetic only. It generates no trade, account replay or new definition.

## Frozen identities, counts and integrity

- Original preregistration: `a087708b13697df4c3dd0b0814f98cb53a2b254a`.
- Fixed-arm amendment: `e8e249b4e7c8946d517e8e4c9a4a3b4e62063e24`.
- Final nomination: commit `588e6b6`, exact full identity in the JSON receipt; its committed file bytes match the current frozen selection.
- Definitions observed before final validation: **2,965** = 2,485 original + 460 fixed + 20 earned governor definitions. Prior results/aliases remain retained; the hard 3,000 cap was not exceeded.
- Four frozen nominees plus CURRENT and EMPTY for each account = **8 policies**. All four nominees have `risk_fraction=0`; three model prospective target guards, while plain 150K LDF does not.
- Three frozen cost scenarios × four cushion states = **12** scenarios, each **8 × 896 = 7,168** cases; verified total **86,016**. Every CSV hash and policy/config/tape/selection fingerprint matches its completed receipt.
- Every scenario retains the same 896 weekday purchase starts, **2023-01-02 through 2026-06-08**. The 2026 subset contains **113** starts, with full expiry no later than the July 7 source end. This excludes the recent October/November losses and is not full-year 2026 evidence.
- Checked purchase at prior-calendar-day16:30 Chicago, 30-calendar-date17:00 expiry, initial cash/floor states, cost arithmetic, terminal timestamps, integer capacity and EMPTY's896 expirations. No post-death source P&L is added by this audit.

Main costs are $1.24 round trip per micro plus one adverse tick per market side; stress is $2.48/two ticks and low is $1.04/one tick. Fees are study assumptions, not independently confirmed broker schedules. Synthetic cushion states are fresh cash/floor experiments, not reconstructed live accounts.

## Main costs, fresh accounts

Each row has 896 starts. P/F/E/U = pass/fail/expire/unknown. Times are conditional medians among confirmed passes, not unconditional time to funding.

|Account and frozen policy|P/F/E/U|Pass|Fail|Median pass, calendar days|
|---|---|---:|---:|---:|
|50K ONBML,20MNQ, prospective market target guard|404/409/83/0|45.09%|45.65%|9.72|
|50K FC2B,20MNQ, prospective market target guard|348/547/1/0|38.84%|61.05%|3.76|
|150K FC2B,20MNQ, prospective market target guard|254/584/58/0|28.35%|65.18%|10.26|
|150K LDF,20MNQ, source exits without target guard|60/352/484/0|6.70%|39.29%|21.92|
|CURRENT50K|23/80/0/793|**2.57–91.07% identified range**|8.93–97.43%|5.90 among only23known passes|
|CURRENT150K|6/128/0/762|**0.67–85.71% identified range**|14.29–99.33%|10.42 among only6known passes|

The candidate confirmed-pass share cannot be subtracted from an assumed zero baseline. The earlier design baseline had no confirmed passes, but validation has23/6. In both periods, extensive unidentified baseline outcomes prevent treating its confirmed-pass share as the true pass probability. Failure shares have the same identification issue.

## Costs, thin cushions and 2026

|Policy|Stress/fresh P/F/E|Main/quarter-cushion P/F/E|2026 main/fresh P/F/E|
|---|---|---|---|
|50K ONBML20 + prospective guard|385/429/82|143/731/22|51/47/15|
|50K FC2B20 + prospective guard|339/556/1|139/757/0|21/92/0|
|150K FC2B20 + prospective guard|247/585/64|77/814/5|35/78/0|
|150K LDF20|55/394/447|45/673/178|14/72/27|

The first two columns each use896 starts; the last uses113. All these nominee cases have zero UNKNOWN. That establishes reached-case completeness under this model, not source-feed/tick verification. At a quarter cushion, main-cost failures are **81.58%,84.49%,90.85%,75.11%** respectively. No cost/cushion sensitivity can be chosen as a new rule after viewing it.

2026 materially differs across candidates: 50K FC2B passes18.58% and fails81.42%, while 50K ONBML passes45.13% and fails41.59%. The 150K FC2B row passes30.97% and fails69.03%; LDF passes12.39% and fails63.72%. These are heavily overlapping historical windows, not independent accounts or calibrated forward probabilities.

## Exact recommendation gates

The frozen efficiency gate requires a paired historical pass gain of at least3pp, a positive90% lower bound, failure increase no greater than1pp, cost stress and native/data checks. The safety gate requires a failure reduction of at least5pp with a negative90% upper bound, pass loss no greater than2pp, pass lower bound at least−5pp, fee/pass increase no greater than5%, and median pass delay no greater than10calendar days.

Paired uncertainty uses **180 matching Monday starts**, separately from the896-weekday point estimates. I independently reproduced all96prespecified4/8-week moving-block calculations, their5,000resample index hashes, point identification bounds and90% identified confidence intervals. No UNKNOWN was dropped, renamed a failure or imputed as a return.

Main/fresh **90% identified intervals for candidate-minus-CURRENT pass probability**, in percentage points:

|Policy|4-week blocks|8-week blocks|
|---|---:|---:|
|50K ONBML20 + guard|−56.11 to+51.11|−56.11 to+52.22|
|50K FC2B20 + guard|−60.00 to+45.56|−58.89 to+46.67|
|150K FC2B20 + guard|−67.78 to+36.11|−67.22 to+37.22|
|150K LDF20|−87.22 to+9.44|−86.67 to+8.89|

**Every nominee in every scenario fails the efficiency gate's necessary positive identified pass lower bound. Every nominee also fails the safety gate's necessary negative identified failure upper bound.** Neither recommendation gate is earned. The JSON additionally records identified point pass/failure bounds and conservative fee/pass ratios for every scenario. The<=5%fee condition cannot be established; baseline unknown passes also prevent certifying its full conditional pass-time distribution. Known-pass-only speed comparisons do not repair that missing information.

This is a failed superiority claim, not proof that a nominee is worse than the unidentified current book. No fine-grained "optimal" size, guaranteed pass probability or deployment instruction is supported.

## Source and governor qualifications

The original tape records1,213hard source-uncertainty rows. Unallocated or unreached source uncertainty does not contaminate another strategy's observed price; a reached allocated bad fill remains UNKNOWN. Zero nominee UNKNOWN is therefore conditional account-path evidence rather than an assertion that the entire source bank is clean.

The separate DT overlay manifest records401exact source-open matches, zero unmatched corrections, unchanged common prices/times and unchanged other source events. None of the final four nominees containsDT. Its factual repair does not provide independent economic support for these nominees.

**Material governor limitation:** frozen `risk_fraction>0` code sets quantity to zero when its stop-risk input is NaN/nonfinite. Infinity for a documented no-stop Bridge/OT is an intentional admission rejection; historical NaN ATR is missing data. LDF/ONBML cap views showing244expirations and zero failures must be labeled **data-rejection outcomes, not clean safety evidence**. Known-stop FC2B caps are distinct: the fully governed design views show22pass/222expire/0fail for50K and11pass/233expire/0fail for150K, an expiration-heavy observed tradeoff. All four validated nominees have risk fraction zero, so these rejected-risk cap views do not supply their claimed validation results. No frozen code or historical record was changed to conceal the limitation.

## Final disposition

**Artifact arithmetic, frozen identity and statistical reproduction: PASS. Portfolio replacement recommendation: NOT EARNED.** Native source matching and Claude's economic verification remain pending. The target guard is a prospective modeled execution policy whose live installation is unverified. Conditional OHLC chronology, source-ledger reuse after position changes, sparse minima, gaps, fees and platform assumptions remain material.

No trading allocation, evaluation purchase, funded/personal extrapolation, installed strategy, broker setting or VPS was changed. The user decides any later allocation after review.
