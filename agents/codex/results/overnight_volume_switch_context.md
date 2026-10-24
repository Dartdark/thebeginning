# Overnight volume switch: context and data gate - WATCH

Summary: Claude has already tested the T_ONESIDE family; do not repeat it as a new discovery.
The supplied explicit-stop source changes volume, session anchors, missing-bar handling and protective-order timing.
Prior family performance therefore does not establish this version's performance or parity.
Night volume exists on priced cache bars, but sparse/absent bars and five missing 08:29 stress observations need a frozen policy.
Use ONB ML as the single structural replacement control for a whole-book comparison; no swap or new returns are authorized by this note.

Source inspected: `C:/Users/dmoto/Downloads/overnight volume switch.txt` (194 lines).
Repository context pinned to Claude `febc65f1573040abf9a697d1d3468e1bce48c4c0`.
New candidate return trials: **0**. This is source/context and data-availability work only.

## Existing research, not an exact-source result

Pinned `checks/candidates/t_oneside/REVIEW.md` and `analysis/t_oneside_test.py` already test the heavy-night fade plus
quiet-night one-sided long family. The review reports 874 trades with the note's stop, $150/NQ, PF 1.51, t 4.3,
9/9 positive years, DSR 0.93. Its separate post-2023-09-08 book t is 1.9. The fade is stronger than OS; the OS symmetry
cell fails, and the review interprets OS as largely NQ upward drift during a trending morning.

The original upload lacked a stop; `T_ONESIDE_v2.txt` added the note's 0.40/0.30 ADR stop using `SetStopLoss`.
The pinned review's evaluation comparisons show no material gain: whole-book additions peak at +0.8 percentage
point over its saved baseline, within noise; EOS and ONB replacements are worse. Its funded bootstrap is still marked
pending at this pin. No committed `analysis/outputs/t_oneside_bench_output.txt` exists at this revision.
These figures use the previous rule/fills and scaled NQ fee convention, not current-source actual-micro-cost results.

## Changes that prevent transferring those results

| Area | Pinned v2 / replay | Supplied explicit-stop source |
|---|---|---|
| Volume keyword in native code | `Volume` | `Ticks`, with Trade Volume setting requested |
| Night start | `>=17:00` | `>16:00` |
| Morning range / VWAP anchor | 08:30 bar, whose open is 08:29 on a close-stamped one-minute chart | first bar `>08:30`, normally 08:31, open at the cash bell |
| Protection | built-in stop, entry-bar protection | stop placed after detecting the filled position at the entry-bar close; entry minute unprotected |
| Warm-up | original v2 can send an entry before a positive stop distance exists | `atrD>0` required before both entries |
| Missing 08:29 | fallback classifies on first non-night bar | classification occurs only at exactly 08:29 |
| Current night too short | OS requires `validNight` | OS only requires `classified` and `heavy=false`; it can accept a current night shorter than 30 bars |
| Quantity / backstop | explicit Qty input and late kill orders | no order quantity input and no terminal kill block |

The pinned Python replay already uses exported total volume, whereas its native v2 uses `Volume`. Its own comments
and review disagree about whether the exports contain up-tick or total volume. The exporter source settles the file
field: `tools/exporters/NQ_Bar_Exporter.txt` writes **Ticks** into the CSV `volume` column. A historical MC source using
`Volume` still needs its own flag/trade pairing. Changing to Ticks is a source change even when the intended measure
is total volume. Stop survival during a disconnect also depends on actual platform/broker order settings; the source
comment alone does not verify native broker-held protection.

## Cheap data availability check, no signals or returns

The existing `scratch_data/g24.pkl` carries OHLC and volume through 2026-10-09. Across its 2,262 trading mornings,
the supplied `>16:00` through 08:29 window has 2,094,067 priced bars. None has missing, zero or negative volume;
every inspected night has positive aggregate volume. There is no evidence here that an old overnight volume column
is absent or has been filled with zeros.

This is **not** a finding that every expected minute is complete. Median priced bars are 927-928 per night in
2018-22 and 929 in 2023 onward. A nominal 17:01-08:29 contiguous window has 929 slots, but 17:01 is absent on most
older nights (for example 251 of 257 in 2018). Omitted no-trade bars, session conventions, halts and feed gaps cannot
be distinguished solely by a missing minute. Requiring all 929 slots would exclude almost all older history and
must not be introduced silently as a harmless data cleanup.

The 08:29 bar is absent on 2020-03-09, 2020-03-12, 2020-03-13, 2020-03-16 and 2020-03-18. This matters directly:
the new source leaves classification false, whereas the old v2 can classify on its fallback. These are stress dates,
not a random sample of missing observations. Several other nights have large holes despite meeting MinNightBars=30.
Freeze a literal-source and any separate completeness policy before looking at new strategy returns; do not infer
missing night volume from price direction or from the candidate's eventual profitability.

The source's 16:01-16:59 extension contains no priced bars on nearly every inspected night; one such priced bar
appears in 2023. This makes its measured window close to 17:00 on this cache, without making the definitions equivalent.

## Prespecified plan control

For a whole-book addition/replacement exercise, choose **ONB_ML2_MC** as the one replacement slot before any new
results. Both classify overnight context and allocate NQ risk during the morning on ordinary trading days.
EOS overlaps the short open-fade clock but is a rare expiration event; Monday Long is a calendar drift position.
Removing either merely because it looks weak would muddle a new general morning strategy with loss of an existing
diversifier. The OS leg can also overlap VB and RS; actual daily/held-position correlation and common-loss contribution
must be measured rather than asserted. Keep the whole current plan, ONB slot empty and that one replacement as paired
controls. Selection of a replacement comparator is not a recommendation to replace ONB.

## Reproduce the volume-availability counts only

Run with the configured scientific Python and existing cache; this code computes no price changes, signals or returns:

```python
import pickle
import numpy as np
import pandas as pd
import grid24
g = pickle.load(open("scratch_data/g24.pkl", "rb"))
records = []
for d in g.trading:
    if d < 1:
        continue
    ix = np.r_[np.arange((d-1)*1440+961, d*1440), np.arange(d*1440, d*1440+510)]
    priced = np.isfinite(g.c.ravel()[ix])
    volume = g.v.ravel()[ix]
    records.append(dict(date=pd.Timestamp(g.ts[d]), bars=int(priced.sum()),
                        missing=int((priced & ~np.isfinite(volume)).sum()),
                        zero=int((priced & (volume == 0)).sum()),
                        negative=int((priced & (volume < 0)).sum()),
                        night_volume=float(np.nansum(volume[priced])),
                        bar829=bool(np.isfinite(g.c[d, 509])),
                        missing1701=not np.isfinite(g.c[d-1, 1021]),
                        extension_bars=int(np.isfinite(g.c[d-1, 961:1020]).sum())))
a = pd.DataFrame(records)
print(a[["bars", "missing", "zero", "negative", "extension_bars"]].sum())
print(a.groupby(a.date.dt.year).agg(nights=("bars", "size"), median_bars=("bars", "median"),
                                   missing1701=("missing1701", "sum")))
print(a.loc[~a.bar829, "date"].tolist())
print("Nonpositive night totals:", int((a.night_volume <= 0).sum()))
```
