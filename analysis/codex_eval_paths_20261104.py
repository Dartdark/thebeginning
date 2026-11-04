"""Research-only event tape for the November 4 evaluation audit.

Import, inventory and selftest do not compute market paths. ``build`` is guarded
by an exact committed configuration and implementation. The tape retains NaNs,
coverage limits and source-fill inference flags; it is a conditional OHLC model,
not native tick or broker-fill verification.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import gc
import hashlib
import json
from pathlib import Path
import re
import subprocess
import warnings

import numpy as np
import pandas as pd

from grid24 import Grid24

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = "analysis/codex_eval_paths_20261104.py"
DEFAULT_LEDGER = "analysis/outputs/codex_portfolio_audit_20261031"
POINT_VALUES = {"NQ": 2., "ES": 5., "GC": 10., "CL": 100.}
TICKS = {"NQ": .25, "ES": .25, "GC": .1, "CL": .01}
OPEN_ENTRIES = {"RS", "DT", "TOS", "OT", "CLS", "MOC"}
OPEN_TIME_EXITS = {"TOS", "OT"}
SAMPLE_FALLBACK = ("2018-04-02", "2026-07-07")
STOP_SPECS = {
    "VB": ("fixed", 75.), "VB_N": ("fixed", 75.), "VB_F": ("fixed", 75.),
    "ONB30": ("atr15", .25), "ONBML": ("atr15", .30),
    "EOS": ("atr15", .30), "LDF": ("atr15", .25),
    "MON": ("atr15", .50), "NFP": ("atr15", .50),
    "MOC": ("atr15", .25), "CLS": ("atr15", .75),
    "DT": ("fixed", 50.), "RS": ("rth20", .60), "TOS": ("rth20", .40),
    "BRIDGE": ("none", np.inf), "OT": ("none", np.inf),
}


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, default=str, allow_nan=False) + "\n")


def account_date(value):
    """Close-labelled17:01 first belongs to the following account date."""
    ts = pd.Timestamp(value)
    return ts.normalize() + pd.Timedelta(days=int(ts.hour * 60 + ts.minute > 1020))


def account_minute(value):
    ts = pd.Timestamp(value)
    return (ts.hour * 60 + ts.minute - 1021) % 1440


def common_path(ohlc):
    """Portfolio-independent O→nearest extreme→other extreme→C per asset.

    All four prices are observed OHLC; their within-minute order is a declared
    model. Missing input leaves the entire asset minute unknown. Opposite
    sleeves see this SAME path, never separate adverse extrema.
    """
    a = np.asarray(ohlc, float)
    out = np.full(a.shape, np.nan)
    o, h, l, c = (a[..., i] for i in range(4))
    good = np.isfinite(a).all(axis=-1) & (h >= l) & (h >= np.maximum(o, c)) & (l <= np.minimum(o, c))
    high_first = h - o <= o - l
    out[..., 0] = np.where(good, o, np.nan)
    out[..., 1] = np.where(good, np.where(high_first, h, l), np.nan)
    out[..., 2] = np.where(good, np.where(high_first, l, h), np.nan)
    out[..., 3] = np.where(good, c, np.nan)
    return out


def crossing_phase(path, fill, lower=0.):
    """First crossing on the frozen path, not a claim about real tick order."""
    if not np.isfinite(path).all() or not np.isfinite(fill):
        return np.nan
    if lower <= 0 and np.isclose(path[0], fill, rtol=0, atol=1e-7):
        return 0.
    for leg in range(3):
        a, b = float(path[leg]), float(path[leg + 1])
        if min(a, b) - 1e-7 <= fill <= max(a, b) + 1e-7:
            phase = leg if a == b else leg + abs(fill - a) / abs(b - a)
            if phase + 1e-9 >= lower:
                return min(3., max(float(phase), float(lower)))
    if lower <= 3 and np.isclose(path[3], fill, rtol=0, atol=1e-7):
        return 3.
    return np.nan


def phase_price(path, phase):
    """Use the preceding declared phase; never interpolate another asset."""
    return path[:, min(3, max(0, int(np.floor(phase + 1e-10))))].copy()


def _files_for_market(market, spec=None):
    spec = spec or {}
    if "files" in spec:
        files = [ROOT / p for p in spec["files"]]
    else:
        files = sorted((ROOT / "data").glob(market + "_1min_20*.csv"))
        if market == "NQ":
            files += sorted((ROOT / "data").glob("NQ_1min_ON_20*.csv"))
    if not files or any(not p.is_file() for p in files):
        raise FileNotFoundError("Missing owned raw files for " + market)
    return files


def inventory(config_path, output=None):
    """Hashes and timestamp/coverage metadata only; no prices/PnL loaded."""
    cp = Path(config_path)
    cfg = json.loads(cp.read_text())
    inputs = []
    for market in cfg["markets"]:
        for p in _files_for_market(market, cfg.get("market_sources", {}).get(market)):
            d = pd.read_csv(p, usecols=["date", "time"])
            inputs.append(dict(market=market, path=str(p.relative_to(ROOT)),
                sha256=sha(p), bytes=p.stat().st_size, rows=len(d),
                first_date=int(d.date.min()), last_date=int(d.date.max()),
                duplicate_timestamps=int(d.duplicated(["date", "time"]).sum())))
    ledgers = []
    for key, spec in cfg["ledgers"].items():
        p = ROOT / spec.get("path", f"{DEFAULT_LEDGER}/{key}_unit_ledger.csv")
        if p.exists():
            d = pd.read_csv(p, usecols=["entry_at", "exit_at", "market"])
            ledgers.append(dict(key=key, path=str(p.relative_to(ROOT)), sha256=sha(p),
                bytes=p.stat().st_size, rows=len(d), first_entry=d.entry_at.min(),
                last_exit=d.exit_at.max(), sampling_start=spec.get("sampling_start"),
                sampling_end=spec.get("sampling_end"),
                warning="First/last trade is not a sampling boundary."))
        elif spec.get("generated"):
            ledgers.append(dict(key=key, path=str(p.relative_to(ROOT)),
                status="generated_after_preregistration_by_frozen_adapter"))
        else:
            raise FileNotFoundError(p)
    result = dict(scope="hash/timestamp metadata only; no market path or new return",
        config_path=str(cp), config_sha256=sha(cp), inputs=inputs, ledgers=ledgers,
        builder_sha256=sha(ROOT / SCRIPT), grid24_sha256=sha(ROOT / "analysis/grid24.py"))
    if output:
        dump(output, result)
    return result


def verify_preregistration(config_path, commit):
    if not commit or len(commit) != 40:
        raise ValueError("Full committed preregistration SHA is required")
    cp = Path(config_path).resolve()
    relative = str(cp.relative_to(ROOT))
    cfg = json.loads(cp.read_text())
    frozen = [relative, SCRIPT, "analysis/grid24.py"] + cfg.get("frozen_files", [])
    for name in dict.fromkeys(frozen):
        before = subprocess.check_output(["git", "show", f"{commit}:{name}"], cwd=ROOT)
        if before != (ROOT / name).read_bytes():
            raise ValueError("Preregistered artifact changed: " + name)
    for name, expected in cfg.get("input_sha256", {}).items():
        if sha(ROOT / name) != expected:
            raise ValueError("Input changed: " + name)
    registered = cfg.get("input_sha256", {})
    for market in cfg["markets"]:
        for p in _files_for_market(market, cfg.get("market_sources", {}).get(market)):
            if str(p.relative_to(ROOT)) not in registered:
                raise ValueError("Raw input is not hash-registered: " + str(p.relative_to(ROOT)))
    for key, spec in cfg["ledgers"].items():
        name = spec.get("path", f"{DEFAULT_LEDGER}/{key}_unit_ledger.csv")
        if spec.get("generated"):
            if "analysis/codex_eval_extra_ledgers_20261104.py" not in frozen:
                raise ValueError("Generated ledger requires frozen source adapter: " + key)
        elif name not in registered:
            raise ValueError("Static ledger is not hash-registered: " + name)
    return cfg


def _grid(market, files):
    """Reuse Grid24 on exact registered paths, using an isolated symlink set."""
    folder = ROOT / "agents/codex/runtime/eval_audit_20261104/raw_links" / market
    folder.mkdir(parents=True, exist_ok=True)
    for p in files:
        dest = folder / p.name
        if dest.exists():
            if dest.resolve() != p.resolve():
                raise ValueError("Unexpected registered raw symlink " + str(dest))
        else:
            dest.symlink_to(p)
    if set(p.name for p in folder.glob("*.csv")) != set(p.name for p in files):
        raise ValueError("Unregistered file in raw-link directory")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return Grid24(str(folder / (market + "_1min_20*.csv")),
                      str(folder / "NQ_1min_ON_20*.csv") if market == "NQ" else "")


def prior_rth20(grid):
    """Past-only20 full-RTH range mean; no future exit may size an entry."""
    result = np.full(grid.D, np.nan)
    gaps=np.full(grid.D,-1,int)
    history = []
    for d in range(grid.D):
        if len(history) >= 20:
            result[d] = float(np.mean([v[0] for v in history[-20:]]))
            gaps[d]=sum(v[1] for v in history[-20:])
        if pd.Timestamp(grid.ts[d]).dayofweek >= 5 or not np.isfinite(grid.c[d, 900]):
            continue
        h, l = grid.h[d, 511:901], grid.l[d, 511:901]
        if np.isfinite(h).any() and np.isfinite(l).any():
            complete=np.isfinite(grid.o[d,511:901])&np.isfinite(h)&np.isfinite(l)&np.isfinite(grid.c[d,511:901])
            history.append((float(np.nanmax(h)-np.nanmin(l)),int((~complete).sum())))
    return result,gaps


def source_calendar_atr(grid, bar_minutes, n=15, clock_offset_minutes=0, closed_minutes=None):
    """Past-only source chart-date ATR bank, not civil one-minute-date ATR.

    A midnight close-labelled chart candle contains the preceding k-1 minutes.
    Sunday bars update PrevDayClose, but only weekday completed chart dates
    enter the ring. Missing candles are not imputed. The second array counts
    incomplete OBSERVED source candles in the n stored dates; it is an audit
    limit, not proof that absent candles were exchange closures.
    """
    k = int(bar_minutes)
    if k <= 0 or 1440 % k:
        raise ValueError('Source bar compression must divide1440')
    bars = grid.bars(k)
    offset=int(clock_offset_minutes)
    if offset<0 or offset>=1440 or offset%k:
        raise ValueError('Source clock offset must be nonnegative and align with chartcompression')
    native_ok=np.isfinite(grid.o)&np.isfinite(grid.h)&np.isfinite(grid.l)&np.isfinite(grid.c)
    native_closed=np.zeros_like(native_ok) if closed_minutes is None else np.asarray(closed_minutes,bool)
    if native_closed.shape!=native_ok.shape:raise ValueError('Riskclosure shape mismatch')
    # A source quote in a frozen closed interval is a contradiction, not
    # permission to silently include or erase an exceptional observation.
    flat_ok=((native_ok|native_closed)&~(native_ok&native_closed)).ravel()
    padded = np.r_[np.zeros(k-1,bool),flat_ok]
    padded = np.r_[padded,np.zeros((-len(padded))%k,bool)].reshape(-1,k)
    complete = padded.all(axis=1)[:grid.D*(1440//k)].reshape(grid.D,1440//k)
    if offset:
        shift=offset//k
        # Source Eastern bank boundaries lead Chicago by60minutes during
        # observed CME hours. The Sunday DST transition hour is closed and
        # cannot grant an inferred quote. Shift completed candles
        # into their source calendar-date bank before taking date extrema.
        bars={name:np.r_[np.full(shift,np.nan),values.ravel()][:values.size].reshape(values.shape)
              for name,values in bars.items() if name in {'o','h','l','c'}}
        complete=np.r_[np.zeros(shift,bool),complete.ravel()][:complete.size].reshape(complete.shape)
    result,gaps=np.full(grid.D,np.nan),np.full(grid.D,-1,int)
    history=[];previous_close=np.nan
    for d in range(grid.D):
        if len(history)>=n:
            result[d]=np.mean([v[0] for v in history[-n:]])
            gaps[d]=sum(v[1] for v in history[-n:])
        seen=np.flatnonzero(np.isfinite(bars['c'][d]))
        if not len(seen):continue
        hi,lo=np.nanmax(bars['h'][d]),np.nanmin(bars['l'][d])
        if pd.Timestamp(grid.ts[d]).dayofweek<5:
            tr=hi-lo if not np.isfinite(previous_close) else max(hi,previous_close)-min(lo,previous_close)
            span=np.arange(seen[0],seen[-1]+1)
            history.append((float(tr),int((~complete[d,span]).sum())))
        previous_close=bars['c'][d,seen[-1]]
    return result,gaps


def _as_bool(values, default=False):
    if values is None:
        return default
    if isinstance(values, (bool, np.bool_)):
        return bool(values)
    return str(values).lower() in {"true", "1", "yes"}


def _sampling_bounds(key, spec):
    a, b = spec.get("sampling_start"), spec.get("sampling_end")
    if not a or not b:
        raise ValueError(f"{key}: explicit source sampling bounds required; last trade is insufficient")
    if not all(isinstance(v, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", v) for v in (a,b)):
        raise ValueError(f"{key}: declare certified FULL account dates asYYYY-MM-DD; do not round partial source timestamps into coverage")
    return pd.Timestamp(a).normalize(), pd.Timestamp(b).normalize()


def load_ledgers(cfg, grids, dates):
    frames = []
    dates = pd.DatetimeIndex(dates)
    for keyid, (key, spec) in enumerate(cfg["ledgers"].items()):
        path = ROOT / spec.get("path", f"{DEFAULT_LEDGER}/{key}_unit_ledger.csv")
        frame = pd.read_csv(path, parse_dates=["entry_at", "exit_at"])
        required = {"entry_at", "exit_at", "side", "entry", "exit", "kind", "market"}
        if not required.issubset(frame.columns):
            raise ValueError(f"{key}: missing ledger columns {required - set(frame.columns)}")
        if not pd.to_numeric(frame.kind, errors="coerce").isin([0, 1, 2]).all():
            raise ValueError(f"{key}: source exit strings require explicit frozen classification")
        frame["key"] = key
        frame["key_id"] = keyid
        frame["kind"] = frame.kind.astype(int)
        frame['source_target_qualifier_declared']='target_trade_through_1point' in frame.columns
        frame["entry_session"] = frame.entry_at.map(account_date)
        frame["exit_session"] = frame.exit_at.map(account_date)
        frame = frame[(frame.entry_session <= dates[-1]) & (frame.exit_session >= dates[0])].copy()
        if not frame.side.isin([-1, 1]).all():
            raise ValueError(f"{key}: invalid direction")
        a, b = _sampling_bounds(key, spec)
        frame["sampling_start"], frame["sampling_end"] = a, b
        frame["source_path"] = str(path.relative_to(ROOT))
        frame["source_sha256"] = sha(path)
        frame["source_inference"] = spec.get("source_inference", "saved conditional report/adapter ledger")
        frame["source_inferred_entry"] = key not in OPEN_ENTRIES
        frame["exit_open"] = frame.get("exit_open", pd.Series(key in OPEN_TIME_EXITS, index=frame.index)).map(_as_bool)
        frame["entry_phase_hint"] = frame.get("entry_phase_hint", pd.Series("open" if key in OPEN_ENTRIES else "touch_inferred", index=frame.index))
        formula, multiplier = STOP_SPECS.get(key, ("unknown", np.nan))
        formula, multiplier = spec.get("stop_formula", formula), spec.get("stop_multiplier", multiplier)
        stops,risk_gaps,estimates = [],[],[]
        for row in frame.itertuples():
            if hasattr(row, "stop_points_at_entry"):
                value=float(row.stop_points_at_entry)
                gaps=getattr(row,'risk_input_missing_bars',np.nan)
                estimates.append(float(getattr(row,'stop_points_owned_feed_estimate',value)))
                stops.append(value if gaps==0 else np.nan)
                risk_gaps.append(gaps)
                continue
            g = grids[row.market]
            source_entry=row.entry_at+pd.Timedelta(minutes=int(spec.get('source_clock_offset_minutes',0)))
            source_date=int(source_entry.strftime('%Y%m%d'))
            d = int(np.searchsorted(g["dates"], source_date))
            if d >= len(g["dates"]) or g["dates"][d] != source_date:
                stops.append(np.nan)
                risk_gaps.append(-1)
            elif formula == "fixed":
                stops.append(float(multiplier))
                risk_gaps.append(0)
            elif formula == "none":
                stops.append(np.inf)
                risk_gaps.append(0)
            elif formula == 'atr15':
                if 'source_bar_minutes' not in spec:
                    raise ValueError(f'{key}: ATR sizing needs certified source_bar_minutes')
                k=int(spec['source_bar_minutes'])
                values,gaps=g['atr15_by_bar'][(k,int(spec.get('source_clock_offset_minutes',0)))]
                stops.append(float(multiplier)*values[d])
                risk_gaps.append(int(gaps[d]))
            elif formula == 'rth20':
                values,gaps=g[formula]
                stops.append(float(multiplier) * values[d])
                risk_gaps.append(int(gaps[d]))
            else:
                stops.append(np.nan)
                risk_gaps.append(-1)
            estimates.append(stops[-1])
            if risk_gaps[-1]!=0:stops[-1]=np.nan
        frame["stop_points_at_entry"] = stops
        frame['stop_points_owned_feed_estimate']=estimates
        frame['risk_input_missing_bars'] = risk_gaps
        frame["stop_formula"] = formula
        frames.append(frame)
    out = pd.concat(frames, ignore_index=True)
    out = out.sort_values(["entry_at", "exit_at", "key_id"], kind="stable").reset_index(drop=True)
    out["trade_id"] = np.arange(len(out))
    return out


def segment_bounds(prices, node_rows):
    nodes = np.asarray(node_rows, np.int64)
    if len(nodes) < 2:
        return np.empty((0, prices.shape[1])), np.empty((0, prices.shape[1])), np.empty((0, prices.shape[1]), bool)
    lo = np.empty((len(nodes) - 1, prices.shape[1]))
    hi = lo.copy()
    missing = np.zeros(lo.shape, bool)
    for i, (a, b) in enumerate(zip(nodes[:-1], nodes[1:])):
        x = prices[a + 1:b + 1]
        missing[i] = ~np.isfinite(x).all(axis=0)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            lo[i], hi[i] = np.nanmin(x, axis=0), np.nanmax(x, axis=0)
    return lo, hi, missing


def _time_seconds(ts):
    # No invented DST disambiguation. Active CME data should not land in the
    # Sunday closed-market fallback/spring-forward ambiguity interval.
    return pd.Timestamp(ts).tz_localize("America/Chicago").tz_convert("UTC").timestamp()


@dataclass
class Tape:
    prices: np.ndarray
    times: np.ndarray
    session: np.ndarray
    events: np.ndarray
    node_rows: np.ndarray
    segment_min: np.ndarray
    segment_max: np.ndarray
    segment_missing: np.ndarray
    eod: np.ndarray
    cutoff: np.ndarray
    session_start: np.ndarray
    dates: np.ndarray
    markets: tuple
    keys: tuple
    trades: pd.DataFrame
    quality: pd.DataFrame
    coverage: np.ndarray
    trading_day: np.ndarray
    metadata: dict


def closure_mask(dates, markets, rules):
    """Frozen dated close-label schedules only; never infer closure from NaNs."""
    dates=pd.DatetimeIndex(dates)
    result=np.zeros((len(markets),len(dates),1440),bool)
    civil_minutes=(np.arange(1440)+1021)%1440
    for rule in rules or []:
        def minute(value):
            hour,part=map(int,value.split(':'))
            return hour*60+part
        lo,hi=minute(rule['close_label_start']),minute(rule['close_label_end'])
        keep=np.ones(len(dates),bool)
        if rule.get('start_account_date'):keep&=dates>=pd.Timestamp(rule['start_account_date'])
        if rule.get('end_account_date'):keep&=dates<=pd.Timestamp(rule['end_account_date'])
        if rule.get('weekdays') is not None:keep&=np.isin(dates.dayofweek,rule['weekdays'])
        minutes=(civil_minutes>=lo)&(civil_minutes<=hi) if lo<=hi else ((civil_minutes>=lo)|(civil_minutes<=hi))
        for asset,market in enumerate(markets):
            if market in rule['markets']:
                result[asset]|=keep[:,None]&minutes[None,:]
    return result


def civil_closure_mask(grid, market, rules):
    """Map frozen account-session close schedules onto civil minute columns."""
    dates=pd.date_range(pd.Timestamp(grid.ts[0]),pd.Timestamp(grid.ts[-1])+pd.Timedelta(days=1),freq='D')
    account=closure_mask(dates,(market,),rules)[0]
    civil=np.empty((grid.D,1440),bool)
    civil[:,:1021]=account[:-1,419:]
    civil[:,1021:]=account[1:,:419]
    return civil


def assemble(ohlc, dates, markets, trades, *, keys=None, market_closures=None,
             target_trade_through_points=None):
    """Construct a conditional event tape from actual OHLC and saved fills.

    ohlc shape[A,D,1440,4] holds close-labelled minute bars. This function is
    independent of account weights. It emits observed OHLC endpoints and saved
    source fill prices only. No missing quote/return is interpolated or filled.
    """
    dates = pd.DatetimeIndex(dates)
    markets = tuple(markets)
    keys = tuple(keys or dict.fromkeys(trades.key))
    A, D, M, C = ohlc.shape
    assert (A, D, M, C) == (len(markets), len(dates), 1440, 4)
    market_index = {m:i for i,m in enumerate(markets)}
    active_by_asset = np.zeros((A, D, 1440), bool)
    closed = closure_mask(dates, markets, market_closures)
    minute_events = {}
    quality = []
    frame = trades.copy()
    if "trade_id" not in frame:
        frame["trade_id"] = np.arange(len(frame))
    if "key_id" not in frame:
        frame["key_id"] = frame.key.map({k:i for i,k in enumerate(keys)})
    frame["entry_session"] = frame.entry_at.map(account_date)
    frame["exit_session"] = frame.exit_at.map(account_date)
    frame["entry_d"] = dates.searchsorted(frame.entry_session)
    frame["exit_d"] = dates.searchsorted(frame.exit_session)
    frame["entry_j"] = frame.entry_at.map(account_minute)
    frame["exit_j"] = frame.exit_at.map(account_minute)
    frame["asset"] = frame.market.map(market_index)
    for r in frame.itertuples():
        if r.entry_d >= D or r.exit_d >= D or r.entry_session < dates[0] or r.exit_session > dates[-1]:
            quality.append(dict(trade_id=r.trade_id, key=r.key, issue="entry/exit outside declared dataset", hard_unknown=True))
            continue
        aa = int(r.entry_d * 1440 + r.entry_j)
        bb = int(r.exit_d * 1440 + r.exit_j)
        if bb < aa:
            raise ValueError("Exit before entry")
        active_by_asset[r.asset].ravel()[aa:bb + 1] = True
        if r.entry_session != r.exit_session:
            quality.append(dict(trade_id=r.trade_id, key=r.key, issue="crosses daily account session", hard_unknown=True))
        path = common_path(ohlc[r.asset, r.entry_d, r.entry_j])
        if closed[r.asset,r.entry_d,r.entry_j]:
            quality.append(dict(trade_id=r.trade_id,key=r.key,
                issue='source entry in frozen documented market closure',hard_unknown=True))
            path[:]=np.nan
        hint = getattr(r, "entry_phase_hint", "touch_inferred")
        phase = 0. if hint == "open" else 3. if hint == "close" else crossing_phase(path, r.entry)
        good = np.isfinite(phase) and np.isfinite(path).all()
        if hasattr(r, 'entry_touch') and pd.notna(r.entry_touch) and not _as_bool(r.entry_touch):
            good = False
        if good and hint in {"open", "close"}:
            good = bool(np.isclose(path[int(phase)], r.entry, rtol=0, atol=1e-6))
        if not good:
            quality.append(dict(trade_id=r.trade_id, key=r.key, issue="entry quote missing or source fill not matched to declared minute phase", hard_unknown=True))
            phase = 0.
        if hint == "touch_inferred":
            quality.append(dict(trade_id=r.trade_id, key=r.key, issue="entry time/within-minute phase inferred from source report; OHLC order modeled", hard_unknown=False))
        common = dict(trade_id=int(r.trade_id), key_id=int(r.key_id), asset=int(r.asset),
            side=int(r.side), stop_points=float(r.stop_points_at_entry), qty=float(getattr(r, "qty", 1.)))
        entry_kind = getattr(r, "entry_fill_kind", 0)
        entry_kind = 0 if pd.isna(entry_kind) else int(entry_kind)
        if entry_kind not in {0, 1, 2}:
            raise ValueError("Unsupported source entry fill kind")
        minute_events.setdefault((int(r.entry_d), int(r.entry_j)), []).append(dict(
            **common, action=1, fill=float(r.entry), phase=float(phase), fill_kind=entry_kind,
            matched=good))
        xp = common_path(ohlc[r.asset, r.exit_d, r.exit_j])
        if closed[r.asset,r.exit_d,r.exit_j]:
            quality.append(dict(trade_id=r.trade_id,key=r.key,
                issue='source exit in frozen documented market closure',hard_unknown=True))
            xp[:]=np.nan
        lower = phase if aa == bb else 0.
        exit_open = _as_bool(getattr(r, "exit_open", False))
        phase_x = 0. if exit_open else 3. if r.kind == 2 else crossing_phase(xp, r.exit, lower)
        xgood = np.isfinite(phase_x) and np.isfinite(xp).all()
        if hasattr(r, 'exit_touch') and pd.notna(r.exit_touch) and not _as_bool(r.exit_touch):
            xgood = False
        if xgood and (exit_open or r.kind == 2):
            xgood = bool(np.isclose(xp[int(phase_x)], r.exit, rtol=0, atol=1e-6))
        if r.kind==1 and target_trade_through_points is not None:
            through=float(target_trade_through_points[r.market])
            # A pre-entry/pre-target high cannot prove queue clearance for a
            # target only reached later in the same minute. Use the remaining
            # frozen common path after this target crossing.
            remaining=xp[int(np.ceil(phase_x)):] if np.isfinite(phase_x) else np.array([np.nan])
            supported=bool(np.isfinite(remaining).all() and
                (np.max(remaining)>=r.exit+through-1e-7 if r.side>0 else np.min(remaining)<=r.exit-through+1e-7))
            declared=_as_bool(getattr(r,'source_target_qualifier_declared',
                hasattr(r,'target_trade_through_1point')))
            if declared:
                qualifier=getattr(r,'target_trade_through_1point',np.nan)
                supported &= bool(pd.notna(qualifier) and _as_bool(qualifier))
            if not supported:
                quality.append(dict(trade_id=r.trade_id,key=r.key,
                    issue=f'required target trade-through of {through}points absent/unknown',hard_unknown=True))
                xgood=False
        if not xgood or (aa == bb and phase_x < phase):
            quality.append(dict(trade_id=r.trade_id, key=r.key, issue="exit quote/phase missing, source mismatch or incompatible same-minute order", hard_unknown=True))
            phase_x = max(float(lower), 3. if not exit_open else 0.)
            xgood = False
        minute_events.setdefault((int(r.exit_d), int(r.exit_j)), []).append(dict(
            **common, action=-1, fill=float(r.exit), phase=float(phase_x),
            fill_kind=1 if r.kind == 1 else 2 if r.kind == 0 else 0, matched=xgood))

    active = active_by_asset.any(axis=0)
    # Bound the tape once rather than keeping millions of tiny ndarray/list
    # objects before making a second full numeric copy. Each active minute
    # needs at most4OHLC rows plus one insertion per event/ownexit tie.
    capacity=int(4*active.sum()+4*len(frame)+3*D)
    p_rows=np.empty((capacity,A),float);times=np.empty(capacity,float)
    sessions=np.empty(capacity,np.int32)
    eod=np.zeros(capacity,bool);cutoff=np.zeros(capacity,bool);startflag=np.zeros(capacity,bool)
    event_rows,nodes=[],[]
    row_count=0
    omitted_closed_minutes=0
    mixed_closed_open_minutes=0
    observed_closed_exceptions=0

    def append(price, when, d, *, is_eod=False, is_cutoff=False, is_start=False, node=False):
        nonlocal row_count
        row=row_count
        if row>=capacity:raise AssertionError('Synthetic-reviewed tape capacity bound exceeded')
        p_rows[row]=price
        times[row]=float(when) if isinstance(when,(float,np.floating)) else _time_seconds(when)
        sessions[row]=d
        eod[row]=is_eod;cutoff[row]=is_cutoff;startflag[row]=is_start
        row_count+=1
        if node or is_eod or is_cutoff or is_start:
            nodes.append(row)
        return row

    for d, date in enumerate(dates):
        day_open = date - pd.Timedelta(days=1) + pd.Timedelta(hours=17)
        day_open_epoch=_time_seconds(day_open)
        day_end_epoch=_time_seconds(date+pd.Timedelta(hours=17))
        ordinary_clock=abs(day_end_epoch-day_open_epoch-86400.)<1e-6
        append(np.full(A, np.nan), float(day_open_epoch), d, is_start=True)
        cutoff_done = False
        missing_group_row = None
        for j in np.flatnonzero(active[d]):
            close = day_open + pd.Timedelta(minutes=int(j) + 1)
            if close > date + pd.Timedelta(hours=15, minutes=59) and not cutoff_done:
                append(np.full(A, np.nan), date + pd.Timedelta(hours=15, minutes=59), d, is_cutoff=True)
                cutoff_done = True
            paths = common_path(ohlc[:, d, j, :])
            events = minute_events.get((d, int(j)), [])
            potentially_held=active_by_asset[:,d,j]
            observed_closed = closed[:,d,j]&potentially_held&np.isfinite(paths).any(axis=1)
            if observed_closed.any():
                observed_closed_exceptions+=1
                quality.append(dict(trade_id=-1,key='calendar',issue=
                    f'observed source quote contradicts frozen documented closure at {close}',hard_unknown=True))
            if not events and not observed_closed.any() and potentially_held.any() and closed[potentially_held,d,j].all():
                # The source market is documented closed: no price or order
                # event occurs. Omit this time, preserving the observed reopen
                # gap. This is NOT filling an absent open-market quote.
                omitted_closed_minutes+=1
                continue
            if (closed[:,d,j]&potentially_held).any() and (~closed[:,d,j]&potentially_held).any():
                mixed_closed_open_minutes+=1
            paths[closed[:,d,j]]=np.nan
            try:
                close_epoch = day_open_epoch+60.*(int(j)+1) if ordinary_clock else _time_seconds(close)
            except Exception as exc:
                # A source carry through a wholly closed DST Sunday may span
                # ambiguous/nonexistent civil labels. Do not invent a fold or
                # fail every unrelated account: retain UNKNOWN at the preceding
                # known clock within this source account session.
                if exc.__class__.__name__ not in {"AmbiguousTimeError", "NonExistentTimeError"}:
                    raise
                close_epoch = None
                paths[:] = np.nan
            if not np.isfinite(paths).any():
                if missing_group_row is None:
                    stamp = times[row_count-1] if close_epoch is None else close_epoch - 60.
                    missing_group_row = append(np.full(A, np.nan), float(stamp), d, node=True)
                # No missing-price sequence is filled. One UNKNOWN node is
                # enough while there are no asset observations; source events
                # in that gap also remain explicitly unmatchable.
                for event in sorted(events, key=lambda x:(x["action"], x["trade_id"])):
                    event_rows.append([missing_group_row, event["trade_id"], event["key_id"], event["asset"],
                        event["action"], event["side"], event["fill"] if event['matched'] else np.nan, event["stop_points"],
                        event["qty"], event["fill_kind"]])
                continue
            missing_group_row = None
            phases = sorted(set([0., 1., 2., 3.] + [x["phase"] for x in events]))
            current_price = paths[:, 0].copy()
            for phase in phases:
                if abs(phase - round(phase)) < 1e-10:
                    current_price = paths[:, int(round(phase))].copy()
                price = current_price.copy()
                same = [x for x in events if x["phase"] == phase]
                # Insertion price is the source's saved fill only for that asset.
                # Other assets retain their latest modeled point WITHIN this
                # minute, preventing a later different-asset insertion from
                # resetting an earlier fill back to the old integer endpoint.
                # Integer phases advance all assets. This synchronization is a
                # model, not a recovered simultaneous quote; no cross-minute
                # quote/return fill is introduced.
                for event in same:
                    if event['matched']:price[event["asset"]]=event["fill"]
                is_cutoff = close == date + pd.Timedelta(hours=15, minutes=59) and phase == 3.
                row = append(price, float(close_epoch - 60. + 20. * phase), d,
                    is_cutoff=is_cutoff, node=bool(same))
                current_price = price
                cutoff_done |= is_cutoff
                entering = {event["trade_id"] for event in same if event["action"] == 1}
                own_exits = [event for event in same if event["action"] == -1 and event["trade_id"] in entering]
                first_events = [event for event in same if event not in own_exits]
                for event in sorted(first_events, key=lambda x:(x["action"], x["trade_id"])):
                    event_rows.append([row, event["trade_id"], event["key_id"], event["asset"],
                        event["action"], event["side"], event["fill"] if event['matched'] else np.nan, event["stop_points"],
                        event["qty"], event["fill_kind"]])
                if own_exits:
                    # Closed zero-duration source tickets establish entry→own
                    # exit causality even when both map to the same OHLC point.
                    # Duplicate the SAME observed/modelled price/time, rather
                    # than letting exit-before-entry leave a phantom holding.
                    row = append(price.copy(), float(close_epoch - 60. + 20. * phase), d, node=True)
                    for event in sorted(own_exits, key=lambda x:x["trade_id"]):
                        event_rows.append([row, event["trade_id"], event["key_id"], event["asset"],
                            event["action"], event["side"], event["fill"] if event['matched'] else np.nan, event["stop_points"],
                            event["qty"], event["fill_kind"]])
        if not cutoff_done:
            append(np.full(A, np.nan), date + pd.Timedelta(hours=15, minutes=59), d, is_cutoff=True)
        append(np.full(A, np.nan), date + pd.Timedelta(hours=17), d, is_eod=True)
    prices=p_rows[:row_count]
    times=times[:row_count]
    sessions=sessions[:row_count]
    eod=eod[:row_count];cutoff=cutoff[:row_count];startflag=startflag[:row_count]
    if np.any(np.diff(times) < -1e-6):
        raise ValueError("Nonchronological tape; inspect source sessions and boundary insertion")
    node_rows = np.unique(np.r_[0, np.asarray(nodes, np.int64), len(prices) - 1])
    lo, hi, missing = segment_bounds(prices, node_rows)
    coverage = np.ones((len(keys), D), bool)
    for keyid, key in enumerate(keys):
        q = frame[frame.key == key]
        if len(q):
            a, b = pd.Timestamp(q.sampling_start.iloc[0]), pd.Timestamp(q.sampling_end.iloc[0])
            coverage[keyid] = (dates >= a) & (dates <= b)
        else:
            coverage[keyid] = False  # caller may overwrite from declared source bounds
    ev = np.asarray(event_rows, float).reshape(-1, 10)
    if len(ev):
        ev = ev[np.lexsort((ev[:,1], ev[:,4], ev[:,0]))]
    return Tape(prices, times, np.asarray(sessions, np.int32),
        ev, node_rows, lo, hi, missing,
        np.asarray(eod, bool), np.asarray(cutoff, bool), np.asarray(startflag, bool),
        dates.strftime("%Y%m%d").astype(int).to_numpy(), markets, keys, frame,
        pd.DataFrame(quality, columns=["trade_id", "key", "issue", "hard_unknown"]), coverage,
        np.asarray(dates.dayofweek<5,bool),
        dict(path_model="O-nearest-extreme-other-C shared per asset; source fill insertion; phase synchronization conditional",
             no_missing_quote_fill=True, no_sleeve_adverse_extrema_sum=True,
             source_fill_inference_not_native_confirmation=True,
             omitted_documented_closed_minutes=omitted_closed_minutes,
             mixed_closed_open_held_minutes=mixed_closed_open_minutes,
             observed_closed_schedule_exceptions=observed_closed_exceptions,
             numeric_row_capacity=capacity,
             market_closures=market_closures or [],
             target_trade_through_points=target_trade_through_points,
             trading_day_source='synthetic weekday fixture proxy; build() overwrites with observed Grid24.trading'))


def build(config_path, preregistration_commit, output=None):
    cfg = verify_preregistration(config_path, preregistration_commit)
    dates = pd.date_range(cfg["start"], cfg["end"], freq="D")
    markets = tuple(cfg["markets"])
    arrays = np.full((len(markets), len(dates), 1440, 4), np.nan)
    summaries, grids = [], {}
    observed_trading_day=None
    source_compressions=set()
    generated=[key for key,spec in cfg['ledgers'].items() if spec.get('generated')]
    for key,spec in cfg['ledgers'].items():
        formula=spec.get('stop_formula',STOP_SPECS.get(key,('unknown',None))[0])
        if formula=='atr15':
            if 'source_bar_minutes' not in spec:
                raise ValueError(f'{key}: ATR sizing needs certified source_bar_minutes')
            source_compressions.add((int(spec['source_bar_minutes']),int(spec.get('source_clock_offset_minutes',0))))
    for asset, market in enumerate(markets):
        files = _files_for_market(market, cfg.get("market_sources", {}).get(market))
        g = _grid(market, files)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            risk_closed=civil_closure_mask(g,market,cfg.get('market_closures',[]))
            atr_by_bar={(k,offset):source_calendar_atr(g,k,15,offset,risk_closed)
                        for k,offset in sorted(source_compressions)}
            rth = prior_rth20(g)
        grids[market] = dict(dates=g.dates.copy(), atr15_by_bar=atr_by_bar, rth20=rth)
        if market=='NQ' and generated:
            from codex_eval_extra_ledgers_20261104 import build as build_extra, SPECS, DEST
            if set(generated)-set(SPECS):
                raise ValueError('Unsupported generated ledger keys: '+str(set(generated)-set(SPECS)))
            folders={str(Path(cfg['ledgers'][key].get('path',f'{DEST}/{key}_unit_ledger.csv')).parent)
                     for key in generated}
            if len(folders)!=1:
                raise ValueError('Generated ledger adapter needs one registered output directory')
            receipt=build_extra(config_path,preregistration_commit,{'NQ':g},
                keys=generated,output_dir=folders.pop())
            for key in generated:
                if receipt[key]['path']!=cfg['ledgers'][key].get('path',f'{DEFAULT_LEDGER}/{key}_unit_ledger.csv'):
                    raise ValueError('Generated ledger path differs from configuration: '+key)
        if market=='NQ' or observed_trading_day is None:
            observed_trading_day=np.isin(dates.strftime('%Y%m%d').astype(int),g.dates[g.trading])
            trading_day_market=market
        for d, date in enumerate(dates):
            for offset in [-1, 0]:
                civil = int((date + pd.Timedelta(days=offset)).strftime("%Y%m%d"))
                row = np.searchsorted(g.dates, civil)
                if row >= g.D or g.dates[row] != civil:
                    continue
                src = slice(1021, 1440) if offset == -1 else slice(0, 1021)
                dest = slice(0, 419) if offset == -1 else slice(419, 1440)
                for k, name in enumerate(["o", "h", "l", "c"]):
                    arrays[asset, d, dest, k] = getattr(g, name)[row, src]
        summaries.append(dict(market=market, files=[dict(path=str(p.relative_to(ROOT)),
            sha256=sha(p), bytes=p.stat().st_size) for p in files],
            first_date=str(pd.Timestamp(g.ts[0])), last_date=str(pd.Timestamp(g.ts[-1]))))
        del g
        gc.collect()
    trades = load_ledgers(cfg, grids, dates)
    through=cfg.get('target_trade_through_points')
    if not isinstance(through,dict) or any(m not in through for m in markets):
        raise ValueError('Explicit per-market target_trade_through_points required')
    tape = assemble(arrays, dates, markets, trades, keys=tuple(cfg["ledgers"]),
                    market_closures=cfg.get('market_closures',[]),target_trade_through_points=through)
    tape.trading_day=observed_trading_day
    tape.metadata['trading_day_source']='observed Grid24.trading for '+trading_day_market+'; not a newly certified official session calendar'
    # Explicit sampling declarations remain valid even if there were no trades.
    for keyid, (key, spec) in enumerate(cfg["ledgers"].items()):
        a, b = _sampling_bounds(key, spec)
        tape.coverage[keyid] = (dates >= a) & (dates <= b)
    tape.metadata.update(preregistration_commit=preregistration_commit,
        config_path=str(Path(config_path).resolve().relative_to(ROOT)),
        config_sha256=sha(config_path), source_inputs=summaries,
        point_values=[POINT_VALUES[m] for m in markets], ticks=[TICKS[m] for m in markets],
        source_ledger_hashes={key:sha(ROOT/spec.get("path",f"{DEFAULT_LEDGER}/{key}_unit_ledger.csv")) for key,spec in cfg["ledgers"].items()},
        source_stop_specs={k:[spec.get("stop_formula",STOP_SPECS.get(k,("unknown",None))[0]),
            spec.get("stop_multiplier",STOP_SPECS.get(k,("unknown",None))[1])]
            for k,spec in cfg["ledgers"].items()},
        source_atr_chart_compressions={k:spec.get('source_bar_minutes') for k,spec in cfg['ledgers'].items()},
        source_clock_offsets={k:spec.get('source_clock_offset_minutes',0) for k,spec in cfg['ledgers'].items()},
        risk_input_limit='source-chart past-only bank; any detected incomplete required candles makes sizing riskNaN; estimate diagnostic only; exact feed/risk parity not certified')
    if output:
        dest = Path(output)
        dest.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(dest/"tape.npz", **{n:getattr(tape,n) for n in
            ["prices","times","session","events","node_rows","segment_min","segment_max",
             "segment_missing","eod","cutoff","session_start","dates","coverage","trading_day"]})
        tape.trades.to_csv(dest/"trades.csv", index=False)
        tape.quality.to_csv(dest/"quality.csv", index=False)
        metadata = dict(tape.metadata)
        metadata["source_stop_specs"] = {k:[v[0],
            v[1] if v[1] is None or np.isfinite(v[1]) else
            "infinity_no_source_stop" if v[0]=="none" and np.isinf(v[1]) else
            "unresolved_nonfinite"] for k,v in metadata["source_stop_specs"].items()}
        metadata.update(markets=list(markets), keys=list(tape.keys), rows=len(tape.prices),
            source_events=len(tape.events), trades=len(tape.trades), segments=len(tape.node_rows)-1,
            hard_unknown_source_rows=int(tape.quality.hard_unknown.sum()) if len(tape.quality) else 0)
        dump(dest/"metadata.json", metadata)
    return tape


def selftest():
    assert account_date("2026-11-01 19:00") == pd.Timestamp("2026-11-02")
    assert account_date("2026-11-02 17:00") == pd.Timestamp("2026-11-02")
    assert account_minute("2026-11-01 19:00") == 119
    x = np.array([[100., 110., 99., 105.], [100., 101., 90., 95.]])
    p = common_path(x)
    assert np.array_equal(p[0], [100., 99., 110., 105.])
    assert np.array_equal(p[1], [100., 101., 90., 95.])
    assert np.isnan(common_path(np.array([100., np.nan, 99., 105.]))).all()
    assert np.isnan(common_path(np.array([100., 99., 90., 105.]))).all()
    # Source chart-date banking differs from naive civil1m banking at00:00.
    # The23:59 extreme belongs to tomorrow's00:00five-minute chart candle.
    fake=object.__new__(Grid24)
    fake.ts=pd.date_range('2020-01-06','2020-01-08').to_numpy();fake.D=3
    for name in ['o','h','l','c','v']:setattr(fake,name,np.full((3,1440),100.))
    fake.h[0,1439]=200.
    a1,_=source_calendar_atr(fake,1,n=1);a5,_=source_calendar_atr(fake,5,n=1)
    assert a1[1]==100. and a5[1]==0. and a1[2]==0. and a5[2]==100.
    fake.h[2,:]=1000.
    mutated,_=source_calendar_atr(fake,5,n=1)
    assert np.array_equal(a5,mutated,equal_nan=True)
    fake.h[:]=100.;fake.h[0,23*60]=200.
    ct,_=source_calendar_atr(fake,5,n=1)
    et,_=source_calendar_atr(fake,5,n=1,clock_offset_minutes=60)
    assert ct[1]==100. and et[1]==0. and et[2]==100.
    # A whole absent open-market candle must not vanish from risk admission.
    for name in ['o','h','l','c']:getattr(fake,name)[0,721:726]=np.nan
    _,gaps=source_calendar_atr(fake,5,n=1)
    assert gaps[1]>0
    closed=np.zeros((3,1440),bool);closed[0,721:726]=True
    _,legitimate=source_calendar_atr(fake,5,n=1,closed_minutes=closed)
    assert legitimate[1]==1  # only leading first-history warm-up candle
    assert np.isclose(crossing_phase(p[0], 104.5), 1.5)
    assert np.isnan(crossing_phase(p[0], 120.))
    # Same instrument longs/shorts share ONE mark: their unrealized PnL nets0.
    assert np.allclose((p[0]-100.)*2. + (p[0]-100.)*-2., 0.)
    prices = np.array([[10.,20.],[8.,22.],[11.,19.],[np.nan,21.],[9.,20.]])
    lo,hi,missing = segment_bounds(prices,np.array([0,2,4]))
    assert np.array_equal(lo[0],[8.,19.]) and np.array_equal(hi[0],[11.,22.])
    assert missing[1,0] and not missing[1,1]
    # Every source event and EOD/cutoff is retained in the segment index.
    dates = pd.DatetimeIndex(["2026-11-02"])
    raw = np.full((1,1,1440,4),np.nan)
    raw[0,0,119]=[100.,102.,99.,101.]
    raw[0,0,120]=[101.,103.,100.,102.]
    trades=pd.DataFrame([dict(key="SYN",key_id=0,market="NQ",entry_at=pd.Timestamp("2026-11-01 19:00"),
        exit_at=pd.Timestamp("2026-11-01 19:01"),side=1,entry=100.,exit=102.,kind=2,qty=1.,
        stop_points_at_entry=5.,entry_phase_hint="open",exit_open=False,
        sampling_start="2026-11-02",sampling_end="2026-11-02")])
    tape=assemble(raw,dates,("NQ",),trades)
    assert tape.events.shape==(2,10)
    assert set(tape.events[:,0].astype(int)).issubset(set(tape.node_rows))
    assert tape.eod.sum()==tape.cutoff.sum()==tape.session_start.sum()==1
    assert not tape.quality.hard_unknown.any() if len(tape.quality) else True
    assert np.all(np.diff(tape.times)>=0)
    ztrades=trades.copy();ztrades['exit_at']=ztrades.entry_at
    ztrades['entry_phase_hint']='close';ztrades['entry']=101.;ztrades['exit']=101.
    z=assemble(raw,dates,("NQ",),ztrades)
    assert z.events[0,4]==1 and z.events[1,4]==-1
    assert z.events[0,0]<z.events[1,0]
    assert np.array_equal(z.prices[int(z.events[0,0])],z.prices[int(z.events[1,0])])
    # Two different assets exit on distinct fractional points in the same leg.
    # The second insertion must not reset the first asset back to its oldH.
    raw2=np.full((2,1,1440,4),np.nan)
    raw2[:,0,119]=[100.,110.,90.,105.]
    trades2=pd.DataFrame([dict(key=key,key_id=i,market=market,
        entry_at=pd.Timestamp("2026-11-01 19:00"),exit_at=pd.Timestamp("2026-11-01 19:00"),
        side=1,entry=110.,exit=x,kind=0,qty=1.,stop_points_at_entry=110.-x,
        entry_phase_hint="touch_inferred",exit_open=False,
        sampling_start="2026-11-02",sampling_end="2026-11-02")
        for i,(key,market,x) in enumerate([("A","NQ",100.),("B","ES",106.)])])
    t2=assemble(raw2,dates,("NQ","ES"),trades2)
    aexit=t2.events[(t2.events[:,3]==0)&(t2.events[:,4]==-1)][0]
    assert t2.prices[int(aexit[0]),1]==106.
    # Illegitimate weekend carry across both closed Sunday DST transitions
    # retains missing-price uncertainty and known calendar boundaries, rather
    # than inventing a fold/clock or crashing unrelated source histories.
    for first,last in [("2026-03-06","2026-03-09"),("2026-10-30","2026-11-02")]:
        ds=pd.date_range(first,last,freq='D'); rr=np.full((1,len(ds),1440,4),np.nan)
        rr[0,0,1374]=[100.,100.,100.,100.];rr[0,-1,959]=[102.,102.,102.,102.]
        tr=pd.DataFrame([dict(key='GAP',key_id=0,market='NQ',entry_at=ds[0]+pd.Timedelta(hours=15,minutes=55),
            exit_at=ds[-1]+pd.Timedelta(hours=9),side=1,entry=100.,exit=102.,kind=2,qty=1.,
            stop_points_at_entry=75.,entry_phase_hint='close',exit_open=False,
            sampling_start=first,sampling_end=last)])
        gap=assemble(rr,ds,('NQ',),tr)
        assert gap.quality.hard_unknown.any() and np.isnan(gap.prices).any()
        assert len(gap.prices)<100 and np.all(np.diff(gap.times)>=0)
    # Dated venue closures omit only times with no executable market, never
    # an unexplained open-market gap. All dates/prices here are synthetic.
    rule=dict(markets=['NQ','ES'],end_account_date='2021-06-27',
        close_label_start='15:16',close_label_end='15:30',weekdays=[0,1,2,3,4])
    def halted_fixture(date, *, mixed=False, inside_event=False, observed_exception=False):
        ds=pd.DatetimeIndex([date]);rr=np.full((2 if mixed else 1,1,1440,4),np.nan)
        first_j=account_minute(date+' 15:15');last_j=account_minute(date+' 15:31')
        rr[0,0,first_j]=100.;rr[0,0,last_j]=102.
        if mixed:rr[1,0,first_j:last_j+1]=50.
        if observed_exception:rr[0,0,first_j+1]=101.
        tr=pd.DataFrame([dict(key='H',key_id=0,market='NQ',
            entry_at=pd.Timestamp(date+' 15:'+('16' if inside_event else '15')),
            exit_at=pd.Timestamp(date+' 15:31'),side=1,entry=100.,exit=102.,kind=2,qty=1.,
            stop_points_at_entry=75.,entry_phase_hint='close',exit_open=False,
            sampling_start=date,sampling_end=date)])
        if mixed:
            cl=tr.iloc[0].to_dict();cl.update(key='CLH',key_id=1,market='CL',entry=50.,exit=50.)
            tr=pd.concat([tr,pd.DataFrame([cl])],ignore_index=True)
        return assemble(rr,ds,('NQ','CL') if mixed else ('NQ',),tr,market_closures=[rule])
    pre=halted_fixture('2021-06-25')
    assert pre.metadata['omitted_documented_closed_minutes']==15
    assert not pre.quality.hard_unknown.any()
    post=halted_fixture('2021-06-28')
    assert post.metadata['omitted_documented_closed_minutes']==0
    # The open-era gap is an explicit unknown between the entry and exit.
    a,b=post.events[:,0].astype(int)
    assert np.isnan(post.prices[a+1:b]).any()
    mixed=halted_fixture('2021-06-25',mixed=True)
    assert mixed.metadata['omitted_documented_closed_minutes']==0
    assert mixed.metadata['mixed_closed_open_held_minutes']==15
    assert ((~np.isfinite(mixed.prices[:,0]))&np.isfinite(mixed.prices[:,1])).any()
    forbidden=halted_fixture('2021-06-25',inside_event=True)
    assert forbidden.quality.hard_unknown.any()
    assert np.isnan(forbidden.prices[int(forbidden.events[0,0]),0])
    exception=halted_fixture('2021-06-25',observed_exception=True)
    assert exception.metadata['observed_closed_schedule_exceptions']==1
    assert exception.metadata['omitted_documented_closed_minutes']==14
    assert exception.quality.hard_unknown.any()
    # Explicit adapter mismatch cannot be repaired just because a source
    # level happens to match this reconstructed OHLC point.
    mismatch=trades.copy();mismatch['entry_touch']=False
    false_touch=assemble(raw,dates,('NQ',),mismatch)
    assert false_touch.quality.hard_unknown.any()
    assert np.isfinite(false_touch.prices[int(false_touch.events[0,0]),0])
    assert np.isnan(false_touch.events[0,6])
    target=trades.copy();target['kind']=1;target['exit']=103.
    no_through=assemble(raw,dates,('NQ',),target,target_trade_through_points={'NQ':1.})
    assert no_through.quality.hard_unknown.any()
    assert np.isfinite(no_through.prices[int(no_through.events[-1,0]),0])
    assert np.isnan(no_through.events[-1,6])
    # A bad source fill stays in its own raw-fill event, not the common quote:
    # an account that never allocates that sleeve must retain the good tape.
    bad=trades.copy();bad['key']='BAD';bad['key_id']=1;bad['entry']=999.
    joined=assemble(raw,dates,('NQ',),pd.concat([trades,bad],ignore_index=True))
    badentry=joined.events[(joined.events[:,2]==1)&(joined.events[:,4]==1)][0]
    assert np.isnan(badentry[6]) and np.isfinite(joined.prices[int(badentry[0]),0])
    # A high occurring before entry cannot certify a later targetthrough.
    rr=np.full((1,1,1440,4),np.nan);rr[0,0,119]=[110.,120.,90.,105.5]
    tr=trades.iloc[[0]].copy();tr['entry']=100.;tr['exit']=105.;tr['kind']=1
    tr['exit_at']=tr.entry_at;tr['entry_phase_hint']='touch_inferred'
    early_high=assemble(rr,dates,('NQ',),tr,target_trade_through_points={'NQ':1.})
    assert np.isnan(early_high.events[-1,6])
    try:_sampling_bounds('X',dict(sampling_start='2018-04-02',sampling_end='2026-07-07 04:45'))
    except ValueError:pass
    else:raise AssertionError('Partial sampling endpoint silently rounded')
    print("PASS:synthetic sessionclock,common-price netting,crossing,missing-quote,segment-bound and event-node fixtures. No market paths/outcomes.")


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("command",choices=["inventory","selftest","build"])
    parser.add_argument("--config")
    parser.add_argument("--commit")
    parser.add_argument("--output")
    args=parser.parse_args()
    if args.command=="selftest":
        selftest()
    elif args.command=="inventory":
        if not args.config:parser.error("--config required")
        result=inventory(args.config,args.output)
        print(json.dumps(dict(inputs=len(result["inputs"]),ledgers=len(result["ledgers"]),scope=result["scope"])))
    else:
        if not args.config or not args.commit or not args.output:parser.error("--config,--commit,--output required")
        result=build(args.config,args.commit,args.output)
        print(json.dumps(dict(rows=len(result.prices),source_events=len(result.events),segments=len(result.node_rows)-1,
            scope="conditional common-OHLC model; see metadata/quality, no account outcome computed")))
