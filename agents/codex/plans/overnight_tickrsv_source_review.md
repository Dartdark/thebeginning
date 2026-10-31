# Overnight TickRSV/VIX: source and data review only

Summary: The upload describes a strategy and supplies screenshots, but includes no PowerLanguage code.
Verify owned data, reported arithmetic, selection history and account eligibility before a return trial.
Do not substitute aggressor delta for tick direction or claim an exact replication from a description.
Evidence currently NEEDS DATA; return testing is blocked on exact source/data, not on user authorization.

Source: `agents/codex/inputs/overnight_tickrsv/source.txt`, preserved byte-for-byte.
Script: `analysis/codex_overnight_tickrsv_review.py`. Output: `analysis/outputs/codex_overnight_tickrsv_review/summary.json`.

Allowed now: source inspection; bounded input schema/endpoints; dependency readiness; screenshot arithmetic;
prior-idea comparison; identifying exact missing inputs. No candidate signals, outcome screens, returns,
backtests, bootstrap simulations, re-optimization, research caches or trading changes. Return trials: zero.

Once exact data semantics and source are available, a SEPARATE evidence TEST verdict and committed return
preregistration must freeze MA20 versus selected25, all chart/session clocks, VIX as-of joining, costs and
roll handling before computing any new strategy returns. At most five variants; design screen first;
then historical replication and all five account destinations if the applicable gates pass. Source's full
2017-2026 history is already selected/seen; no claim of a clean untouched holdout is permitted.

This review does not reject the edge or infer portfolio contribution. It records why those questions are
unanswered with the current upload. Work stays on `codex/work`; no live/VPS/broker/ranking/plan changes.
