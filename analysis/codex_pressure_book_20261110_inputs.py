"""Input-only archival book-state adapter; no labels, models or return outcomes.

The exporter reads indexed historical OFB_GetAt(slot, BarKey) values at bar close.
Closed-DLL calculation/revision vintages and original receipt clocks are unknown.
These scalar summaries are not a price-level ladder or native book-gap measure.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FILE_SHA256 = {'data/OF_1min_2018_1.csv': '2bc0e1ad344cc93d8685b6016b255ef1e642f30d6364245f51557e6999eff114', 'data/OF_1min_2018_2.csv': '5639a66d95ab2435c0f75896245bc21d20c1685b53c7fd68c89b051d817e9414', 'data/OF_1min_2018_3.csv': '7dd6824acaea62821ae9e785d528c9532c3b92dedbd7d8640c20faae473db696', 'data/OF_1min_2018_4.csv': '805500d67bd03bbacb9245957b8c9d0e9b33edf3006370779637515767a76ff7', 'data/OF_1min_2019_1.csv': 'ae84a55a44fe0379a6afbf4ae781b59fd1604bf584d37c97531174df804836fc', 'data/OF_1min_2019_2.csv': '15933657a4e742254b5dd3a854dae2ea4eb3dbc42e4efafa62a607eaee6a4845', 'data/OF_1min_2019_3.csv': '995f81a181173d2c7879fd108bbf6c47055286eede57d9b2b55c604a6445735a', 'data/OF_1min_2019_4.csv': '667ed887abdcd91bb02cb3419b5a49c0ef003d19466c7658f7a78107cbac4b69', 'data/OF_1min_2020_1.csv': '67c7fb1166730e4d5eedf871f2a08875e2c71a8889f048bd81282c98ce9ae0f4', 'data/OF_1min_2020_2.csv': 'be8963123cc649e11298d626f79beb3e31306fa9ccb3f4f247aa7ddccd11d95f', 'data/OF_1min_2020_3.csv': 'b7501ad273ccd4259f909614ac7be8838588ee62df5f5038086a4cd82e0ec72d', 'data/OF_1min_2020_4.csv': '603d3fea3f59b2d97d67f1bb6613b54da3a6a7f548fa071a85d74d41cc376cc6', 'data/OF_1min_2021_1.csv': '0a7d801e97cbe38a414ca0207d09de5494eb0671f3b719c2f5e3c2d611251483', 'data/OF_1min_2021_2.csv': '0fcd3408675768576890e38f93c52359feffa3fd47e01d6e9ee10d69566b93fe', 'data/OF_1min_2021_3.csv': '64efc51c20ba33489377e3e2e620fee4415f565a6c7e434701741a35b7fa7f12', 'data/OF_1min_2021_4.csv': '60bf703a22c44cd6c928ff8d475a1199574a061d0fb86b5a37711055ed7837ab', 'data/OF_1min_2022_1.csv': 'b5ec87cbadb2c62cd502a15b0d6cc595a0c383815a97a62b3687f14e7b1dac45', 'data/OF_1min_2022_2.csv': '5938d4a02c8b1bfac001da685758deb77cc679b9704c0303d697f1ae8f721cbe', 'data/OF_1min_2022_3.csv': 'e935c507d69c4adc899d7e1b3d2488a7b2f6d2fa77df9b0e331828496c120028', 'data/OF_1min_2022_4.csv': '59f4b0dc8596ea7772a801b65db33b1ef98cda594932fb6b8d16ffab4d2a4a5b'}
EXPECTED_HEADER = ['date', 'time', 'open', 'high', 'low', 'close', 'volume', 'upvol', 'downvol', 'spread_ticks', 'bid_sz_top', 'ask_sz_top', 'size_imb', 'count_imb', 'qdepl_bid', 'qdepl_ask', 'pulled_bid', 'pulled_ask', 'ice_bid', 'ice_ask', 'trade_rate', 'cum_delta', 'event_rate', 'levels_bid', 'levels_ask', 'big_trade', 'big_trade_px', 's48', 's49', 's50', 's51', 's52', 's53', 's54', 's55', 's56', 's57', 's58', 's59', 's60', 's61', 'vwap', 'vwap_sd', 'poc', 'poc_prev', 'vah', 'val']
RENAME = {"close":"source_close", "upvol":"buy", "downvol":"sell",
          "s48":"bid_depth10", "s49":"ask_depth10", "s50":"bid_depth20", "s51":"ask_depth20",
          "s52":"bid_depth50", "s53":"ask_depth50"}
RAW = ["spread_ticks", "bid_sz_top", "ask_sz_top", "s48", "s49", "s50", "s51", "s52", "s53", "close", "upvol", "downvol"]
FEATURES = ["spread", "topimb", "depth10imb", "depth50imb", "near_fraction", "log_depth10_ratio",
            "log_depth10_growth5min", "spread_change5min", "imbalance_change5min"]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _support(frame):
    quote = np.isfinite(frame[["spread_ticks", "bid_sz_top", "ask_sz_top"]]).all(axis=1) & frame[["spread_ticks", "bid_sz_top", "ask_sz_top"]].gt(0).all(axis=1)
    names = [f"{s}_depth{k}" for s in ("bid", "ask") for k in (10,20,50)]
    depth = np.isfinite(frame[names]).all(axis=1) & frame[names].gt(0).all(axis=1)
    monotonic = (frame.bid_depth10.le(frame.bid_depth20) & frame.bid_depth20.le(frame.bid_depth50)
                 & frame.ask_depth10.le(frame.ask_depth20) & frame.ask_depth20.le(frame.ask_depth50))
    top = frame.bid_sz_top.le(frame.bid_depth10) & frame.ask_sz_top.le(frame.ask_depth10)
    return quote, depth, monotonic, top


def load_book_minutes(root=ROOT, native_minutes=None):
    """Return raw book minutes plus row-level availability and source audit.

    Invalid support is retained as book_known=False, never filled or repaired.
    Native join uses only the same CT minute-close key. Legacy Volume is ignored.
    No numerical result below measures future price behavior or profitability.
    """
    root = Path(root)
    if len(FILE_SHA256) != 20: raise ValueError("The exact20-file source binding is required")
    pieces, sources = [], {}
    for rel, expected in sorted(FILE_SHA256.items()):
        path = root / rel
        actual = sha(path)
        if actual != expected: raise ValueError(f"Archival book input changed: {rel}")
        header = pd.read_csv(path, nrows=0).columns.tolist()
        if header != EXPECTED_HEADER: raise ValueError(f"Book export schema changed: {rel}")
        x = pd.read_csv(path, usecols=["date","time"] + RAW)
        numbers = x[RAW].apply(pd.to_numeric, errors="raise")
        if not np.isfinite(numbers).all(axis=None): raise ValueError(f"Nonfinite selected book inputs: {rel}")
        times = pd.to_datetime(x.date.astype(str) + x.time.astype(str).str.zfill(4), format="%Y%m%d%H%M", errors="raise")
        index = pd.DatetimeIndex(times).tz_localize("America/New_York", ambiguous="raise", nonexistent="raise").tz_convert("America/Chicago").tz_localize(None)
        frame = numbers.rename(columns=RENAME); frame.index = index
        for field in ["buy","sell","bid_sz_top","ask_sz_top","bid_depth10","ask_depth10","bid_depth20","ask_depth20","bid_depth50","ask_depth50"]:
            values = frame[field].to_numpy(float)
            if (values < 0).any() or not np.allclose(values, np.round(values), rtol=0, atol=1e-8):
                raise ValueError(f"Noninteger/negative quantity {field}: {rel}")
        if not np.allclose(frame.source_close.to_numpy()*4, np.round(frame.source_close.to_numpy()*4), rtol=0, atol=1e-8):
            raise ValueError(f"Non-tick source close: {rel}")
        sources[rel] = dict(sha256=actual, rows=len(frame), first=str(index.min()), last=str(index.max()))
        pieces.append(frame)
    book = pd.concat(pieces).sort_index()
    if book.index.has_duplicates: raise ValueError("Duplicate book minute keys, including exact duplicates")
    quote, depth, monotonic, top = _support(book)
    book["quote_positive"] = quote
    book["depth_positive"] = depth
    book["depth_monotonic"] = monotonic
    book["top_within_depth10"] = top
    book["book_support_known"] = quote & depth & monotonic & top
    if native_minutes is None:
        from codex_pressure_build_20261110_inputs import load_design_native
        native_minutes = load_design_native(root=root)
    if native_minutes.index.has_duplicates: raise ValueError("Native join keys are not unique")
    native = native_minutes[["close","buy","sell"]].rename(columns={"close":"native_close","buy":"native_buy","sell":"native_sell"})
    book = book.join(native, how="left", validate="one_to_one")
    book["native_key_known"] = np.isfinite(book[["native_close","native_buy","native_sell"]]).all(axis=1)
    book["close_exact_match"] = book.source_close.eq(book.native_close) & book.native_key_known
    book["close_match"] = book.source_close.sub(book.native_close).abs().le(.25) & book.native_key_known
    book["buy_exact_match"] = book.buy.eq(book.native_buy) & book.native_key_known
    book["sell_exact_match"] = book.sell.eq(book.native_sell) & book.native_key_known
    book["book_known"] = book.book_support_known & book.close_match & book.buy_exact_match & book.sell_exact_match
    yearly = {}
    for year, frame in book.groupby(book.index.year):
        yearly[str(year)] = dict(rows=len(frame), dates=int(frame.index.normalize().nunique()),
                                **{k:int(frame[k].sum()) for k in ["quote_positive","depth_positive","depth_monotonic","top_within_depth10","book_support_known","native_key_known","close_exact_match","close_match","buy_exact_match","sell_exact_match","book_known"]})
    audit = dict(files=sources, rows=len(book), by_year=yearly, duplicate_keys=0,
                 selected_fields=RAW, native_input_audit=native_minutes.attrs.get("input_audit",{}),
                 clock="ET close label -> naive CT close label, America/New_York to America/Chicago; no extra minute",
                 legacy_total="CSV Volume ignored: it is buyer volume in these exports; buy/sell use UpTicks/DownTicks mapped fields",
                 availability="Conditional archival indexed-DLL close values; original receipt, calculation and revision vintages unverified",
                 support_rule="positive spread/top/six depths; monotonic10<=20<=50; top<=depth10; native key/closewithin.25/buy/sell matches",
                 unsupported="No complete quote-price ladder, native gap spacing, order-ID/add/cancel stream or individual replenishment receipts",
                 raw_zero_policy="Do not blanket-convert all derived zeros. Support invalidity is explicit, raw rows retained.")
    book.attrs["input_audit"] = audit
    return book, audit


def make_book_features(book, calendar):
    """Completed5min endpoints with exact t-5 reference; no forward fill.

    Calendar is the declared normal-cash calendar, not dates discovered from
    later prices. Median uses exactly the preceding20 calendar slots at the same
    clock and requires20 known observations. It includes roll-date book slots;
    the parent independently controls candidate/training date exclusions.
    """
    if book.index.has_duplicates or not book.index.is_monotonic_increasing:
        raise ValueError("Sorted unique book keys required")
    b = book[book.index.minute % 5 == 0].copy()
    calendar = pd.DatetimeIndex(calendar).normalize()
    if calendar.has_duplicates or not calendar.is_monotonic_increasing:
        raise ValueError("Sorted unique normal-cash calendar required")
    b["date"] = b.index.normalize()
    b["signal_j"] = b.index.hour * 60 + b.index.minute
    out = pd.DataFrame(index=b.index)
    top = b.bid_sz_top + b.ask_sz_top
    depth10 = b.bid_depth10 + b.ask_depth10
    depth50 = b.bid_depth50 + b.ask_depth50
    out["spread"] = b.spread_ticks
    out["topimb"] = (b.bid_sz_top - b.ask_sz_top) / top.replace(0,np.nan)
    out["depth10imb"] = (b.bid_depth10 - b.ask_depth10) / depth10.replace(0,np.nan)
    out["depth50imb"] = (b.bid_depth50 - b.ask_depth50) / depth50.replace(0,np.nan)
    out["near_fraction"] = depth10 / depth50.replace(0,np.nan)
    # Context for a separately frozen capacity proxy; not part of FEATURES.
    out["bid_depth10"] = b.bid_depth10
    out["ask_depth10"] = b.ask_depth10
    out["depth10_total"] = depth10
    out["book_current_known"] = b.book_known.astype(bool)
    lag = b.reindex(b.index - pd.Timedelta(minutes=5))
    lag.index = b.index
    out["book_lag5_known"] = lag.book_known.eq(True)
    lag10 = lag.bid_depth10 + lag.ask_depth10
    lagimb = (lag.bid_depth10 - lag.ask_depth10) / lag10.replace(0,np.nan)
    out["log_depth10_growth5min"] = np.log(depth10 / lag10.replace(0,np.nan))
    out["spread_change5min"] = b.spread_ticks - lag.spread_ticks
    out["imbalance_change5min"] = out.depth10imb - lagimb
    observed = pd.DataFrame({"date":b.date,"j":b.signal_j,"depth10":depth10.where(b.book_known)})
    wide = observed.pivot(index="date",columns="j",values="depth10").reindex(calendar)
    matrix = wide.shift(1).rolling(20,min_periods=20).median()
    medians = pd.Series(matrix.to_numpy().ravel(), index=pd.MultiIndex.from_product([matrix.index,matrix.columns]))
    key = pd.MultiIndex.from_arrays([b.date.to_numpy(),b.signal_j.to_numpy()])
    baseline = medians.reindex(key).to_numpy()
    out["book_baseline20_known"] = np.isfinite(baseline) & (baseline > 0)
    out["log_depth10_ratio"] = np.log(depth10 / np.where(baseline > 0,baseline,np.nan))
    out.loc[~out.book_current_known,FEATURES] = np.nan
    out.loc[~out.book_lag5_known,["log_depth10_growth5min","spread_change5min","imbalance_change5min"]] = np.nan
    out["book_features_known"] = (out.book_current_known & out.book_lag5_known & out.book_baseline20_known
                                  & np.isfinite(out[FEATURES]).all(axis=1))
    out["book_status"] = np.select([~out.book_current_known,~out.book_lag5_known,~out.book_baseline20_known],
                                  ["CURRENT_UNKNOWN","LAG5_UNKNOWN","BASELINE20_UNKNOWN"], default="KNOWN")
    out.attrs["input_audit"] = dict(source=book.attrs.get("input_audit",{}),endpoint_rows=len(out),
                                    feature_known_rows=int(out.book_features_known.sum()),
                                    status_counts=out.book_status.value_counts().to_dict(),feature_columns=FEATURES,
                                    change_imbalance="depth10 imbalance current minus exact t-5min",
                                    no_fill=True, native_book_gap_claim=False)
    return out


def self_check():
    calendar=pd.bdate_range("2020-01-01",periods=22)
    ix=pd.DatetimeIndex([d+pd.Timedelta(hours=9,minutes=m) for d in calendar for m in (0,5)])
    b=pd.DataFrame({"spread_ticks":1.,"bid_sz_top":10.,"ask_sz_top":10.,"bid_depth10":100.,"ask_depth10":100.,
                    "bid_depth20":200.,"ask_depth20":200.,"bid_depth50":500.,"ask_depth50":500.,"book_known":True},index=ix)
    f=make_book_features(b,calendar)
    stamp=calendar[20]+pd.Timedelta(hours=9,minutes=5)
    assert f.loc[stamp,"book_features_known"] and f.loc[stamp,"near_fraction"]==.2
    assert f.loc[stamp,"log_depth10_ratio"]==0 and f.loc[stamp,"log_depth10_growth5min"]==0
    # Current value must never enter its own same-clock history.
    b.loc[stamp,"bid_depth10"]=300.
    f=make_book_features(b,calendar)
    np.testing.assert_allclose(f.loc[stamp,"log_depth10_ratio"],np.log(2.))
    # No stale lag substitution, even if yesterday's endpoint exists.
    b=b.drop(stamp-pd.Timedelta(minutes=5));f=make_book_features(b,calendar)
    assert not f.loc[stamp,"book_lag5_known"] and pd.isna(f.loc[stamp,"log_depth10_growth5min"])
    # One unknown prior slot breaks the exact20 requirement; window cannot stretch.
    b.loc[calendar[1]+pd.Timedelta(hours=9,minutes=5),"book_known"]=False
    f=make_book_features(b,calendar)
    assert not f.loc[stamp,"book_baseline20_known"]
    q,d,m,t=_support(pd.DataFrame({"spread_ticks":[1.,0.],"bid_sz_top":[101.,10.],"ask_sz_top":[10.,10.],
                                  "bid_depth10":[100.,100.],"ask_depth10":[100.,100.],"bid_depth20":[200.,200.],"ask_depth20":[200.,200.],"bid_depth50":[500.,500.],"ask_depth50":[500.,500.]}))
    assert not t.iloc[0] and not q.iloc[1]
    return dict(passed=True,checks=["exact_prior20_sameclock","current_excluded_from_baseline","exact5min_lag_no_fill",
                                    "unknown_history_slot_not_stretched","top_le_depth10","positive_quote_support"],
                real_labels_or_outcomes_read=False)


if __name__ == "__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--intake",action="store_true");parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    if args.intake:
        from codex_pressure_build_20261110_inputs import load_design_native
        import codex_cash_open_repair as C
        native=load_design_native();book,audit=load_book_minutes(native_minutes=native)
        calendar=pd.DatetimeIndex(sorted(set(native.index.normalize())))
        calendar=pd.DatetimeIndex([d for d in calendar if C.normal_cash(d)])
        features=make_book_features(book,calendar)
        result={"minutes":audit,"features":features.attrs["input_audit"],"self_check":self_check(),"labels_or_outcomes_computed":False}
        if args.out: args.out.write_text(json.dumps(result,indent=2,default=str)+"\n")
        print(json.dumps({"rows":len(book),"known_rows":int(book.book_known.sum()),"known_endpoints":int(features.book_features_known.sum()),"by_year":audit['by_year']},indent=2))
    else:print(json.dumps(self_check(),indent=2))
