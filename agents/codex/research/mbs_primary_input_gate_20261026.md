# MBS primary-input gate: bounded negative source audit

Decision: **NEEDS DATA**, unchanged. This continuation checked the contents of the four saved research
PDFs for an original mortgage-specific risk/exposure series or an evidenced intraday hedge allocation
into ZN. It found neither. No economic rule, timeframe, threshold or entry clock was frozen; no price
rows, strategy ledgers or financial output files were opened, and no returns were calculated.

## What was new in this check

The earlier review, `mbs_duration_state_feasibility.md`, established the relevant section in
*151 Trading Strategies* and the missing inputs. This audit adds a content check and SHA256 binding
for the other three saved research PDFs. It does not repeat the earlier data-header census or the
completed available-input screens. It does not assert that all possible public or offline sources
have been exhausted.

The PDFs were converted to text in memory with `pdftotext <file> -`. Searches covered `mortgage`,
`MBS`, `prepayment`, `negative convexity` and `DV01`, case insensitive. First-page text was used to
identify each document; PDF metadata alone was not treated as its title or primary-source status.
Page numbers below are one-based PDF pages.

Reproducer: `analysis/codex_mbs_primary_input_gate.py`. Retained artifacts:
`analysis/outputs/codex_mbs_primary_input_gate/manifest.json` and `page_hits.csv`.
The script uses four predefined paths and the reviewed hashes below, the exact case-insensitive
word-boundary terms above, and `pdftotext` form-feed page boundaries. It retains every hit with its
page and bounded context, the tool version, source hashes and its own source hash. It refuses to
overwrite an existing successful audit or read a source whose reviewed hash changed.

```text
/workspace/venvs/thebeginning/bin/python -B analysis/codex_mbs_primary_input_gate.py
```

One saved script execution reproduced this same audit: hit counts were0,0,78,1 respectively for
1405583,2679218,3247865,4501707;79total rows. The cited pages101–102 and136 were manually inspected
against their retained contexts. These are text matches, not independent mortgage observations,
economic configurations, or new return trials. Zero term matches alone cannot establish absence of
every relevant exposure concept. The human finding is conditional on this bounded source set and
the lack of an actual as-of exposure/clock/transmission dataset, not an automatic gate from counts.
Do not rerun the saved audit against the same hashes.

| Saved source | Content finding relevant to this gate |
|---|---|
| `papers/ssrn-1405583.pdf`, Lo and Wang, *Stock Market Trading Volume* | No matches to the stated mortgage/risk terms. This is not an original mortgage exposure or hedge-clock dataset. |
| `papers/ssrn-2679218.pdf`, Farkas et al., *A Two-Factor Cointegrated Commodity Price Model with an Application to Spread Option Pricing* | No matches to the stated terms. Its first-page description concerns commodity prices and spread-option pricing, not measured MBS duration states. |
| `papers/ssrn-4501707.pdf`, Kelly and Xiu, *Financial Machine Learning* | One match, on page136, refers to Fuster et al.(2022) and machine-learning algorithms in mortgage markets. The paragraph supplies no portfolio risk/exposure series, hedge mandate, intraday receipt clock or futures allocation. A citation is not the cited original paper or its data. |
| `papers/ssrn-3247865.pdf`, Kakushadze and Serur, *151 Trading Strategies* | The previously reviewed pages101–102 explain passthrough duration hedging with interest-rate swaps and model-dependent prepayment risk. Other matches include bibliography entries and descriptions. They do not establish observed ZN hedge orders. The source remains secondary. |

## Source bindings

| Path | SHA256 |
|---|---|
| `papers/ssrn-1405583.pdf` | `107648166b70e3f991b17bcf48575801472129247cf724ed61e7eb8426176095` |
| `papers/ssrn-2679218.pdf` | `fc1c13d5514f48b18aaef3a19efac4092a8fe8133c70b9904ce751714da1ab94` |
| `papers/ssrn-3247865.pdf` | `1bc54915eb2778b1b6a8eacfa0b07fb8c568f2cd5caa3ded45fa28f47c83c73e` |
| `papers/ssrn-4501707.pdf` | `e2068d89c2a7bfe38de36f695186991a16b6e5c87724751083d351993f119cce` |

## Inputs still required before TEST

1. Historical as-of effective duration/DV01, coupon/refinancing/prepayment state and weights of an
   identified MBS exposure, together with its stated risk target and existing hedges. A theoretical
   negative-convexity relationship does not identify the net adjustment of a real portfolio.
2. Original publication/receipt vintages and model-update/hedge triggers available before the proposed
   decision. Neither a paper date nor a recurring calendar is an observed intraday hedge deadline.
3. Primary evidence linking the resulting adjustment into ZN rather than swaps, cash bonds or another
   contract, including direction, hedge fraction and timing. No universal futures allocation is assumed.
4. The native contract/session/roll, transaction-cost, target-through and smaller-contract feasibility
   audits required by the existing evidence sheet. No risk or payout improvement can be inferred by
   dividing a ZN return series.

The required state remains unobserved. A prior ZN move, aggregate COT rank, month-end indicator or
stock/bond covariance transformation cannot replace it: those definitions already belong to other
research families. The frozen flow-innovation family also remains closed.

Resume this source gate when genuinely new primary material or an auditable as-of dataset arrives;
do not rerun this content audit against the same hashes. There is no justified economic TEST or new
configuration from this audit. No new user-action blocker, milestone alert, trading approval or pause
of the continuing research program follows. The separate EIA access record is unchanged.
