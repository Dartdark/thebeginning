# User-supplied intended settings and claims, 2026-10-24

Summary: The user's intended strategy overrides the uploaded file defaults: threshold4.5 and hold20.
NQ,5-minute bars,Default session,CT;12-bar momentum divided by the preceding20-bar mean range.
Both directions,entries08:30-14:30,forced exit14:55,no stop/target or volatility sizing.

The file has threshold3.0/hold6. Preserve it unchanged; these are user-provided chart inputs, not inferred settings.
Hypothesis: strong intraday NQ momentum tends to persist. There is no volume term despite the filename.

Author's reported development: research-paper idea adapted to NQ; tested stops,targets,volatility sizing,long-only
and adaptive walk-forward parameters, rejected those additions. The original paper and complete trial registry
were not supplied. Final freeze provenance is user-reported, not independently established.

Reported IS2016-2024:2023trades,53.3%win,PF~1.22,netEV+$86/NQ,95%interval+$26..+$149.
Reported OOS2025onward:352trades,50-51%win,PF~1.18,netEV+$160/NQ,95%interval−$170..+$485;
both directions positive but a rougher equity curve. These are claims, not a supplied original trade ledger.
Reported EV cost:$2.25commission+$5slippage per contract per trade (total$7.25,roundtrip meaning not independently verified).

The user asks whether smaller OOS count explains the negative lower interval, whether selection overfit the rule,
and whether the rough OOS curve can survive prop-account rules. Standing scope is placement in50K/150K
evaluation,funded or personal plans; if no useful place, move on.
