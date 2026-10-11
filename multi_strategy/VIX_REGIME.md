# VIX regime filter ("The Volatility Edge") tested on Vault Break

Started 2026-10-11. Source: Zarattini, Mele & Aziz (2025), *The Volatility Edge: A Dual
Approach for VIX ETNs Trading*. The paper sizes short-volatility positions with two
daily signals. This tests whether the same signals say anything about the NQ
strategies, mainly Vault Break.

## The regime (known at the previous day's close)

- **eVRP** (expected volatility risk premium) = VIX close − expected realized
  volatility.
- **Backwardation** = short-term fear above longer-term fear.

| Regime | Condition | Share of days |
|---|---|---|
| Short vol (calm, insurance overpriced) | eVRP > 0, no backwardation | 58% |
| Half short | eVRP ≤ 0, no backwardation | 22% |
| Long vol (stress building) | eVRP ≤ 0, backwardation | 4% |
| Cash | eVRP > 0, backwardation | 15% |

**Stand-ins:** VIX3M and SPY could not be downloaded from this environment. Daily VIX
is in `data/VIX_daily.csv`, from the public `datasets/finance-vix` repository, through
22 Sep 2026.
- Realized volatility = NQ's 10-day close-to-close volatility (15:00 CT closes) × 0.8,
  because NQ is about 1.25x as volatile as the S&P 500.
- Backwardation = VIX more than 10% above its 20-day average. This happens on 28% of
  days, against about 10–15% for the real VIX > VIX3M. It was the middle one of the
  three stand-ins tried.
- If you can export daily VIX3M and SPY from MultiCharts into `data/VIX3M_daily.csv`
  and `data/SPY_daily.csv` (`DATE,CLOSE`), `analysis/vix_regime.py` uses them instead.

## Results (per NQ after costs; Vault Break and Overnight Bias from the MultiCharts reports)

| Regime | Vault Break | Overnight Bias | Opening Drive | Overnight Drift |
|---|---|---|---|---|
| All | $99, PF 1.28 (1,743) | $278, PF 1.39 | $119, PF 1.23 | $83, PF 1.25 |
| **Short vol** | **$130, PF 1.42** (938) | **$341, PF 1.58** | $139, PF 1.30 | $49, PF 1.18 |
| Half short | $61, PF 1.17 (324) | $142, PF 1.17 | $17, PF 1.03 | $29, PF 1.08 |
| Long vol | $190, PF 1.55 (76) | $428, PF 1.49 (33) | $451, PF 1.80 | $160, PF 1.42 |
| Cash | **$42, PF 1.10** (405) | $218, PF 1.24 | $91, PF 1.16 | **$190, PF 1.51** |

By VIX level, Vault Break: VIX 11–16 $47, 16–19 $87, 19–24 **$158**, 24+ $105.
Overnight Drift **loses when VIX is under 15** (−$25, PF 0.90) and is best at 18–23
($191).

- **Vault Break and Overnight Bias do best in the paper's "short vol" regime** (calm,
  volatility premium positive): about 30% more per trade than average. They are weakest
  in "half short" and "cash".
- **Overnight Drift and Opening Drive lean the other way**, doing better in stress.
- **Vault Break is positive in every regime.** The filter changes how much it earns,
  not whether it earns.
- By year, Vault Break's short-vol-regime trades beat its other trades in 7 of 9 years.
  The exceptions are 2021 ($101 vs $210) and 2026 ($20 vs $96). The gap
  ($130 vs about $56) is about 1.5 standard errors: suggestive, not proven.

## Does it help the accounts?

Vault Break's size by regime, everything else unchanged:

| Rule for Vault Break | Challenge pass (VB 8 + ONB $1,100) | Funded payouts within 1 year (Balanced) |
|---|---|---|
| Same size every day | 43.8% | $5,919 |
| Skip "cash" days | 44.8% (2023–26: 48.5%) | $5,630 |
| **Half size on "cash" and "half short" days** | 44.4% | **$6,062** |
| Skip "cash", half on "half short" | 43.4% | $5,878 |

All within about a point of pass rate and about $300 of payouts, which is inside the
noise. Removing Vault Break's weaker trades also removes profit and qualifying days.
**No change to the plan.** It is worth keeping for later as:
- a **size tilt**: Vault Break and Overnight Bias up in "short vol", Overnight Drift and
  Opening Drive up in stress. The strategies' regime preferences are opposite, so a
  rotating book could be smoother. This is untested, and would be fitted on the same
  data.
- a **re-test with real VIX3M and SPY data**. The stand-ins blur the signal, especially
  the backwardation one.

## Files

| File | What it is |
|---|---|
| `NQ_Vault_Break_VIX.txt` | Vault Break + regime sizing. data2 = daily VIX. `UseRegime` false = plain Vault Break. Defaults: half size in "half short" and "cash" |
| `../analysis/vix_regime.py` | All tables above (about 20 s) |
| `../data/VIX_daily.csv` | Daily VIX 1990 – 22 Sep 2026 (CBOE, via github.com/datasets/finance-vix) |
