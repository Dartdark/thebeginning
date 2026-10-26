# Forward guidance: public GitHub source discovery, NEEDS DATA

Summary: A new public-corpus inspection found management-guidance language in ECTSum transcript files.
It did not establish original issuer releases, event-time versions, exact publication/receipt clocks,
comparable old/new guidance ranges or historical index exposure. No guidance pair is admitted and no
economic rule, timeframe, clock or direction is selected. No prices, strategy returns or remote code ran.

This extends the earlier local-only source census; it does not rerun that completed census or make its
report-date counts into guidance events. Actual connector responses and hashes are retained in
`analysis/outputs/codex_guidance_public_source/`, with the inventory in `review_manifest.json`.

## Discovery scope and the sample-budget exception

Four bounded discovery calls used the connected GitHub app: repository searches for `ECTSum`,
`earnings guidance dataset` and `management earnings forecast data`, plus a scoped `guidance` file search
in `ylwpaopao/Earnings-Guidance`. Targeted README, preprocessing-source, file-list, sample and license
reads followed; no cloned/fetched code was executed. The first small repository's `README.md` returned
404 and its scoped search returned no results. That is a path/search result, not proof the repository
contains no files or useful material. Other search hits were not treated as qualified input products.

Before receiving the parent agent's later source-extension plan `0e991ef` and its allocation of one
ECTSum example, this discovery had already read three transcript files and one associated summary.
That timing mismatch was reported immediately and sample reads stopped. These captures are retained
as discovery preceding receipt of the allocation message, not represented as a compliant three-sample
combined canonical intake or as proven to precede the source-plan commit chronologically.
No sample, guidance pair, economic configuration or outcome was admitted under that extension plan.
The later correction `a7a551d` preserves those actual reads and separately authorizes root's two further
primary-document candidates. No further delegated sample reads followed. The source discovery does not
establish that all public sources have been exhausted.

## Offline verification and capture limits

`analysis/codex_guidance_corpus_capture_audit.py` was executed once, entirely offline, and saved
`analysis/outputs/codex_guidance_public_source/capture_audit.json`. It verifies all16 capture SHA256s
against the retained review manifest and reconstructs Git blob SHA1s from UTF-8 bytes for all8 file
responses. Those files comprise3 transcripts,1 summary, README, preprocessing source, training-filename
list and license. It also retains bounded source-line contexts supporting the processing finding below.
No old capture or review manifest was changed; the completed audit refuses overwrite or repetition.

These are actual response captures, **not a complete request ledger**. Their wrappers contain
`capture_id` and `tool_response`, without exact request arguments or independent acquisition timestamps.
For example, the directory-not-file response from the `data` path was not retained as actual JSON.
Display URLs, immutable file blobs and the later observed repository head cannot reconstruct missing
arguments, prove original event-time versions or establish receipt chronology. The old review manifest's
"pre-extension" wording is retained unchanged and qualified here and in the new capture audit: it means
before receiving the allocation message, not proof of when the reads occurred relative to its commit.
Hash integrity verifies retained bytes; it does not cure those provenance limits or admit guidance pairs.

## Corpus identity, source text and processing risk

Repository: [rajdeep345/ECTSum](https://github.com/rajdeep345/ECTSum).
The fetched README describes an EMNLP2022 earnings-call-transcript summarization benchmark and states a
dataset release on November1,2022. This is a corpus release date, not the original release time of any
issuer statement. The separately observed current repository head is
`6909f1fc543104c1c60cf9de63e799f6620d1b0a` (May22,2024). Samples were read from `main` and bound by
their immutable Git blob IDs below; no event-time repository vintage is established.

| Inspected file | Git blob SHA | What it establishes |
|---|---|---|
| `README.md` | `c1415924bac81b683ffb463418b9210f815af672` | Benchmark identity and corpus-release notice; no original issuer/SEC receipt lineage |
| `prepare_data_ectbps_ext.py` | `beab527916c391258114420d163602c22d769169` | Text inputs under `data/final/<split>/ects/`, paired summaries, extractive training-data construction |
| `codes/ECT-BPS/ectbps_ext/data/train_files.txt` | `a8afa0d8f9a4fc077cd32cd000bd258ae4cd36c6` | Names of training fixtures; fiscal-quarter filenames do not prove original announcement dates or coverage |
| `data/final/train/ects/LYB_q1_2021.txt` | `5ad307b1d3cb7a47ea8e09ca7d2af0e00515bea1` | Transcript-style near-term outlook discussion; no authenticated issuer release header or exact timestamp established |
| `data/final/train/gt_summaries/LYB_q1_2021.txt` | `5e52e98b96f755a78f88944663af1a43eea2e0ff` | Associated short summary; it is not a substitute for original guidance or an admissible timing input |
| `data/final/train/ects/NOC_q2_2021.txt` | `4df31824acb337649fd7821a2c7fa6edcdf9ae75` | Statements about an increase in full-year2021 transaction-adjusted EPS guidance, including a $0.35 midpoint change |
| `data/final/train/ects/NOC_q3_2021.txt` | `1273b6068f8f893f4ae0d4bd1216593b92026205` | Further full-year2021 EPS-guidance improvement and separate2022 outlook; comparable underlying intervals and original clocks remain unverified |

The NOC files demonstrate that guidance language exists in this public corpus. They do not constitute
an admitted source pair merely because both mention2021: statement attribution, the earlier original
range, accounting/divestiture/tax bases, horizon comparability and availability before a decision remain
unresolved. NOC's index membership or weight is not established here. No NQ trade or direction is derived.

The preprocessing source says its gold extractive summaries use corresponding abstractive summaries
or Reuters articles. It assigns labels by numerical overlap or semantic similarity and constructs a
training document containing numerical lines or lines belonging to the derived extractive summary.
Consequently the generated `codes/.../train.json` document is not an untouched event-time transcript;
summary-conditioned sentence selection could contaminate a trading input. That processed training JSON
was not read or used. Even the inspected `data/final/.../ects/` text remains a derivative transcript
fixture, not authenticated original issuer guidance or a first-publication/receipt record.

## License and provenance limits

A targeted `LICENSE` read returned404, but a later repository-head inspection identified `LICENSE.txt`.
The pinned read at commit `6909f1fc543104c1c60cf9de63e799f6620d1b0a` confirms GNU GPL version3 text,
Git blob `f288702d2fa16d3cdf0035b15a9fcbc552cd88e7`. Do not describe the repository as having no license.
The repository license does not independently establish rights/provenance of every third-party
transcript or Reuters item, original historical timing, or a real-time redistribution/receipt service.
No account, paid product, third-party code execution or external message was used or requested.

The corpus's `main` filenames and Git timestamps establish only the inspected repository state.
No original issuer URL, SEC accession/acceptance header, original release time/timezone, actual receipt,
revision chain or historical constituent-weight input was established by these samples. The inspected
texts start mid-call/discussion rather than supplying an authenticated release header. Do not infer
those missing facts from a filename, quarter, dollar amount, source-code comment or a later market move.

## Decision and next useful gate

**NEEDS DATA.** This is a concrete guidance-text lead, not a TEST decision. Obtain actual original
issuer/SEC statements and their source identity and timing, then compare old/new guidance for the same
future horizon with interval/basis changes and withdrawals explicitly retained. SEC acceptance, issuer
publication and actual receipt must remain separate clocks. Establish relevant historical index
exposure/transmission and native contract execution feasibility before considering a price test.

No economic preregistration, trade t, daily Newey-West(5) t, measured strategy costs, validation or account
paths were produced. Economic trial counts, the closed flow-innovation family and all milestone alerts
are unchanged. The failed EIA access route and completed unchanged local audits were not retried.
