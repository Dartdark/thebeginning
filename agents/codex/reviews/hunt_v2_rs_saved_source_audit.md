# H04 saved-artifact audit: independent source gate failed; no return test

Reviewed only retained H04 artifacts and committed/current code. No native, OF, workbook or cache row was reopened; neither study script nor its XML reader was rerun. No observed return was calculated. This is a reconciliation of the completed pre_gross attempt, not a new experiment or source repair.

Run: preregistration `7784493`, implementation `7784493258b793f98fd39a010d2fa6459e465bdf`,2026-10-26T18:46:47.508526Z–18:47:23.240023Z. Main SHA256 `e352e718a1706ad47e0d7065bd83c08d18ab8596ba521f911ad1d0d09e4bbef0`; XML helper `2aca3ed1d94ce67406ff5682277a49b42438ad72d22fc67358e2b2e6103a6c49`. Both current code hashes match the retained input binding. All16 artifact hashes in `analysis/outputs/codex_hunt_v2_rs_classified_support/pre_gross_verified_execution.json` verified. The47 code/source hash bindings remain preserved; this audit did not reopen raw inputs to recompute their hashes.

## Independently reconciled counts

Counts below were recomputed from selected saved audit columns, rather than copied only from the headline gate.

|Saved-source quantity|Reconciled count|
|---|---:|
|Reconstructed parent entries|608|
|Entries with unresolved references|571|
|Otherwise eligible decision days with unresolved references, including no-entry days|1166|
|Unresolved prefix days|9|
|Missing/invalid entry bars|0|
|Events with an unresolved held native path|1|
|Conflicting duplicate source keys|0|
|Known FLOW15 entry features|589|

The nine prefix dates are2019-12-05;2020-03-09,03-12,03-13,03-16,03-18,03-24,11-30; and2021-09-17. The missing whole normal session on2020-11-30 has no decision and is retained as a prefix failure, rather than silently counted as a zero/no-trade day. All values are source/entry metadata counts, not profits or successful coverage admission.

The first causal source fault on a literal eligible weekday is **2018-04-30**: one missing native RTH minute, zero missing ES RTH minutes, normal first RTH label511 and an observed valid08:30anchor. Stored reference163 contains389RTH bars and is marked incomplete. The first unresolved reference decision and first affected reconstructed entry are **2018-05-01**, whose saved lineage lists2018-04-30. The registered EWMA retains that uncertainty indefinitely; it is still explicitly listed on2022-12-30. The incomplete range reference eventually leaves the20-slot buffer, which does not clear the independent EWMA lineage.

The single held-path failure is the reconstructed **2018-07-26 short**, event `RS_RAW_20180726_01`, with **2missing native held minutes**. Its existing reference lineage also contains2018-04-30. The saved held audit reports the count, not exact missing-minute labels; this review did not reopen native rows to infer them. The source audit records no invalid observed OHLCV rows and no duplicate conflicts, so these particular missing observations were not repaired through duplicate selection. March2020 gaps and anchors remain unresolved under the frozen calendar; their existence alone does not establish whether an exchange halt or feed omission caused them.

## MC parity is NOT ESTABLISHED

The raw-XML metadata audit identified611eligible2018–22ENTRY records, but all611failed the implemented numeric Time convention with `Excel Time must be a finite fraction of one day.` Consequently zero records reached the admitted MC-entry table. The saved zero-match headline is a **parser/admission result, not611observed strategy mismatches** and not evidence that the reconstructed parent entries are wrong. An unsupported numeric time encoding is plausible; its actual encoding was not diagnosed by this audit, and no timestamp correction or offset search was attempted.

The saved helper audit reports611selected entry-price conversions,0future/exit price conversions, and no exit/gross/net/fee/commission-cell interpretation. This does not establish MC date/side/price/clock parity. The native/reference failures above independently veto admission even if MC format parity were later established. No codec rerun, availability/calendar rescue, truncation or economic continuation is authorized here.

## Zero-return boundary and disposition

The retained gate is failed `pre_gross`. In the reviewed code, `raw_after_admission` returns immediately when admission fails, before invoking endpoint attachment. The marker reports `raw_returns_calculated=false`,0gross screens,0counted evaluations, no stopped returns, no validation and no account test. `gross_events.csv`, `gross_summary.csv`, `gross_gate.json` and `gross_verified_execution.json` are absent; `gross_summary_status.json` explicitly records the unavailable result. These facts agree with the source boundary and saved gate.

**CLOSE H04 at its frozen independent source/reference gate, with no economic verdict.** Gross mean/t, net t/NW/DSR, kept/removed profits, placebos, book improvement and account outcomes were not measured. Registration adds1hypothesis, but this attempt adds0gross screens and0economic evaluations: program4/10hypotheses,3/60evaluations,2prior gross screens, plus archived65t6. The v2 program may continue with a distinct hypothesis; this failure is neither promotion nor a reason to restart t6 or pause the whole hunt.
