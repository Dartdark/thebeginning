"""Causal research brokers/features for daily stocks and intraday MNQ.

No broker/network interface. New adaptations, not the paper's historical engine.
"""
from __future__ import annotations
from pathlib import Path
import hashlib
import json
import pickle
import sys
import os
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = Path(os.environ.get("RL3690996_RUNTIME",str(ROOT / "agents/codex/runtime/rl3690996")))
RAW = Path(os.environ.get("RL3690996_STOCK_DATA","/workspace/scratch/rl3690996/dow_30_2009_2020.csv"))
DEFAULTS = dict(stock_capital=10000., stock_fee=.001, stock_slip=.0005,
                stock_weight_cap=.1, futures_fee=.62, futures_tick=.25,
                futures_pv=2., futures_daily_loss=250., turbulence_quantile=.95,
                timesteps=8192, primary_seed=3690996)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def technical(close, high, low):
    """Five fixed-scale, past-only features; supports (time, assets) panels."""
    c, h, l = (pd.DataFrame(x) for x in (close, high, low))
    ret = c.pct_change(fill_method=None)
    macd = (c.ewm(span=12, adjust=False, min_periods=26).mean()
            - c.ewm(span=26, adjust=False, min_periods=26).mean()) / c
    change = c.diff()
    up = change.clip(lower=0).ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    dn = (-change.clip(upper=0)).ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    rsi = (up / (up + dn)).fillna(.5) * 2 - 1
    typical = (c + h + l) / 3
    a = typical.to_numpy()
    mad = np.full(a.shape, np.nan)
    if len(a) >= 20:
        windows = np.lib.stride_tricks.sliding_window_view(a, 20, axis=0)
        mad[19:] = np.abs(windows - windows.mean(axis=2, keepdims=True)).mean(axis=2)
    cci = (typical - typical.rolling(20).mean()) / (.015 * mad)
    tr = np.maximum.reduce([(h-l).to_numpy(), abs(h-c.shift()).to_numpy(), abs(l-c.shift()).to_numpy()])
    atr = pd.DataFrame(tr).ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    plus, minus = h.diff(), -l.diff()
    pdm = plus.where((plus > minus) & (plus > 0), 0).ewm(alpha=1/14, adjust=False).mean() / atr
    mdm = minus.where((minus > plus) & (minus > 0), 0).ewm(alpha=1/14, adjust=False).mean() / atr
    dx = (pdm-mdm).abs() / (pdm+mdm).replace(0, np.nan)
    adx = dx.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    return np.stack([ret.clip(-.05,.05).to_numpy()*100,
                     macd.clip(-.05,.05).to_numpy()*100, rsi.to_numpy(),
                     (cci/200).clip(-5,5).to_numpy(), adx.to_numpy()], axis=-1)


def turbulence(returns, window=252):
    """Current return vs strictly earlier covariance, then earlier score quantile."""
    r = np.asarray(returns, float)
    if r.ndim == 1:
        r = r[:, None]
    score = np.full(len(r), np.nan)
    for i in range(window, len(r)):
        history = r[i-window:i]
        if not np.isfinite(history).all() or not np.isfinite(r[i]).all():
            continue
        cov = np.atleast_2d(np.cov(history, rowvar=False))
        cov = .5*cov + .5*np.diag(np.diag(cov))
        cov += np.eye(r.shape[1]) * (1e-6*np.trace(cov)/r.shape[1] + 1e-10)
        v = r[i] - history.mean(axis=0)
        score[i] = v @ np.linalg.solve(cov, v)
    threshold = pd.Series(score).shift().rolling(window, min_periods=window).quantile(.95).to_numpy()
    return score, threshold


def prepare_stocks(out=RUNTIME):
    out.mkdir(parents=True, exist_ok=True)
    frame = pd.read_csv(RAW)
    frame = frame[~frame.tic.isin(["DD", "RTX"])].sort_values(["datadate", "tic"])
    tickers = sorted(frame.tic.unique())
    dates = np.sort(frame.datadate.unique())
    get = lambda col: frame.pivot(index="datadate", columns="tic", values=col).reindex(columns=tickers).to_numpy(float)
    o, c, h, l, factor = (get(x) for x in ["prcod", "prccd", "prchd", "prcld", "ajexdi"])
    assert np.isfinite(np.stack([o,c,h,l,factor])).all() and (factor > 0).all()
    adj = c/factor
    features = technical(adj, h/factor, l/factor)
    rets = pd.DataFrame(adj).pct_change(fill_method=None).to_numpy()
    score, threshold = turbulence(rets)
    valid = np.isfinite(features).all(axis=(1,2)) & np.isfinite(threshold)
    momentum = pd.DataFrame(adj).pct_change(63, fill_method=None).to_numpy()
    split = np.ones_like(c); split[1:] = factor[:-1]/factor[1:]
    assert np.all(np.isclose(split, 1) | np.isclose(split, 2) | np.isclose(split, 4) | np.isclose(split, 7))
    np.savez_compressed(out/"stocks.npz", dates=dates, tickers=np.array(tickers), o=o, c=c, h=h, l=l,
                        features=features, score=score, threshold=threshold, valid=valid,
                        momentum=momentum, split=split)
    return dict(raw_sha256=sha(RAW), assets=tickers, rows=len(dates), first=int(dates[0]), last=int(dates[-1]),
                valid_days=int(valid.sum()), excluded_names=["DD", "RTX"],
                limits=["static author-provided universe, not point-in-time certified", "dividends absent",
                        "factor-ratio split ledger is conditional, not verified corporate-action cash"])


def prepare_futures(out=RUNTIME):
    from grid24 import jof
    out.mkdir(parents=True, exist_ok=True)
    gridpath = Path(os.environ.get("RL3690996_GRID","/workspace/scratch/g24.pkl"))
    with gridpath.open("rb") as f:
        g = pickle.load(f)
    begin, end = int(jof(831)), int(jof(1500))
    days = g.trading[g.dates[g.trading] >= 20170501]
    admitted, omitted, ranges, last = [], [], [], []
    for d in days:
        arrays = np.array([getattr(g, k)[d, begin:end+1] for k in "ohlc"])
        complete = np.isfinite(arrays).all()
        if not complete:
            omitted.append(dict(date=int(g.dates[d]), missing_cells=int((~np.isfinite(arrays)).sum())))
            continue
        admitted.append(d); ranges.append(float(arrays[1].max()-arrays[2].min())); last.append(float(arrays[3,-1]))
    ix = np.array(admitted, int)
    o, h, l, c = (getattr(g,k)[ix, begin:end+1].copy() for k in "ohlc")
    # 390 observed minutes -> 78 bars closing 08:35 through 15:00.
    oc = o.reshape(-1,78,5)[:,:,0]
    hc = h.reshape(-1,78,5).max(axis=2)
    lc = l.reshape(-1,78,5).min(axis=2)
    cc = c.reshape(-1,78,5)[:,:,-1]
    features = technical(cc.ravel()[:,None], hc.ravel()[:,None], lc.ravel()[:,None])[:,0,:].reshape(-1,78,5)
    ret = pd.Series(cc.ravel()).pct_change(fill_method=None).to_numpy()
    score, threshold = turbulence(ret)
    score, threshold = score.reshape(-1,78), threshold.reshape(-1,78)
    ranges = np.asarray(ranges)
    prev = np.r_[np.nan, last[:-1]]
    tr = np.maximum.reduce([ranges, abs(hc.max(axis=1)-prev), abs(lc.min(axis=1)-prev)])
    atr = pd.Series(tr).shift().rolling(15, min_periods=15).mean().to_numpy()
    valid = np.isfinite(features).all(axis=(1,2)) & np.isfinite(threshold).all(axis=1) & np.isfinite(atr)
    np.savez_compressed(out/"futures.npz", dates=g.dates[ix], o=o, h=h, l=l, c=c,
                        features=features, score=score, threshold=threshold, atr=atr, valid=valid)
    (out/"futures_exclusions.json").write_text(json.dumps(omitted,indent=2)+"\n")
    return dict(grid_sha256=sha(gridpath), admitted_days=len(ix), valid_days=int(valid.sum()),
                incomplete_days=len(omitted), first=int(g.dates[ix[0]]), last=int(g.dates[ix[-1]]),
                limits=["conditional on complete observed RTH sessions", "NQ bars proxy MNQ executions",
                        "no actual contract/auction queue/latency certification"])


class StockBook:
    def __init__(self, n, capital=10000., cost_multiplier=1., log=False):
        self.cash = float(capital); self.initial = capital; self.q = np.zeros(n, np.int64)
        self.mult = cost_multiplier; self.log = log; self.fills = []
        self.basis = np.zeros(n); self.closed = []
        self.fees = self.slip = self.cash_in_lieu = 0.

    def equity(self, price):
        return float(self.cash + self.q @ price)

    def transition(self, weights, decision_price, opening, closing, split, decision_date, fill_date):
        if fill_date <= decision_date:
            raise ValueError("Execution must occur after observation")
        market=np.array([decision_price,opening,closing,split])
        if not np.isfinite(market).all() or (market<=0).any():
            raise ValueError("Missing/invalid stock quote or split")
        weights = np.asarray(weights, float)
        if not np.isfinite(weights).all() or (weights < 0).any() or weights.sum() > 1+1e-8:
            raise ValueError("Invalid long/cash target")
        intended = np.floor(weights*self.equity(decision_price)/decision_price + 1e-10).astype(np.int64)
        qexact = self.q*split
        fraction = qexact-np.floor(qexact+1e-10)
        cash_lieu = float(fraction @ opening)
        self.cash += cash_lieu; self.cash_in_lieu += cash_lieu
        self.q = np.floor(qexact+1e-10).astype(np.int64)
        fraction_share=np.divide(fraction,qexact,out=np.zeros_like(fraction),where=qexact>0)
        self.basis *= 1-fraction_share
        target = np.floor(intended*split+1e-10).astype(np.int64)
        delta = target-self.q
        order = list(np.flatnonzero(delta<0)) + sorted(np.flatnonzero(delta>0), key=lambda j: -delta[j]*opening[j])
        for j in order:
            side = 1 if delta[j]>0 else -1
            px = float(opening[j]*(1+side*.0005*self.mult))
            if side<0:
                qty = min(-int(delta[j]), int(self.q[j]))
            else:
                qty = min(int(delta[j]), int(np.floor((self.cash+1e-9)/(px*(1+.001*self.mult)))))
            if qty <= 0:
                continue
            fee = qty*px*.001*self.mult
            slip = abs(px-opening[j])*qty
            if side<0:
                allocated=self.basis[j]*qty/self.q[j]
                self.basis[j]-=allocated
                if self.log:
                    self.closed.append(dict(date=int(fill_date),asset=int(j),qty=qty,side=1,
                        proceeds=qty*px-fee,basis=allocated,net=qty*px-fee-allocated,
                        convention="average-cost partial-close realization"))
            else:
                self.basis[j]+=qty*px+fee
            self.cash -= side*qty*px+fee
            self.q[j] += side*qty
            self.fees += fee; self.slip += slip
            if self.log:
                self.fills.append(dict(decision_date=int(decision_date), fill_date=int(fill_date), asset=int(j),
                    side=side, qty=qty, raw_price=float(opening[j]), price=px, fee=fee, slippage=slip,
                    cash_after=self.cash, holdings_after=int(self.q[j]), intended_change=int(delta[j])))
        assert self.cash >= -1e-7 and (self.q >= 0).all() and np.issubdtype(self.q.dtype,np.integer)
        self.cash = max(self.cash,0.)
        return self.equity(closing)


def stock_weights(action, n):
    w = np.clip(np.asarray(action, float).reshape(n), 0, 1)
    w /= max(float(w.sum()),1.)
    return np.minimum(w,.1)


class FuturesBook:
    """One intraday MNQ position; all fills/costs in native dollars."""
    def __init__(self, contracts=1, cost_multiplier=1., log=False):
        self.contracts = int(contracts); self.mult = cost_multiplier; self.log = log
        self.fills = []; self.trades = []; self.q = 0; self.net = 0.; self.entry = self.raw_entry = 0.
        self.stop = np.nan; self.latched = False; self.low = 0.; self.fees = self.slip = 0.

    def equity(self, price):
        return self.net + (price-self.entry)*self.q*2 if self.q else self.net

    def _fill(self, raw, q, date, minute, why, decision):
        px = raw + np.sign(q)*.25*self.mult
        fee = abs(q)*.62*self.mult
        self.fees += fee; self.slip += abs(q)*.5*self.mult
        if self.log:
            self.fills.append(dict(date=int(date), decision_minute=int(decision), minute=int(minute),
                qty=int(q), raw_price=float(raw), price=float(px), fee=fee,
                slippage=abs(q)*.5*self.mult, reason=why))
        return px, fee

    def _exit(self, raw, date, minute, why, decision):
        q = self.q
        px, fee = self._fill(raw,-q,date,minute,why,decision)
        profit = (px-self.entry)*q*2 - 2*abs(q)*.62*self.mult
        self.net += (px-self.entry)*q*2-fee
        if self.log:
            self.trades.append(dict(date=int(date), entry_minute=self.entry_minute, exit_minute=int(minute),
                side=int(np.sign(q)), qty=abs(q), entry=self.entry, exit=px, raw_entry=self.raw_entry,
                raw_exit=float(raw), gross=(raw-self.raw_entry)*q*2, fee=2*abs(q)*.62*self.mult,
                slippage=abs(q)*self.mult, net=profit, reason=why))
        self.q = 0; self.stop = np.nan

    def step(self, target, o, h, l, c, atr, date, k):
        # k=0: decision08:35, execute08:36, mark08:40; k=76: flatten14:56.
        start = 5*(k+1); end = start+5
        if not 0<=k<=76 or not np.isfinite(np.array([o[start:end],h[start:end],l[start:end],c[start:end]])).all():
            raise ValueError("Missing/invalid execution interval")
        if not np.isfinite(atr) or atr<=0:
            raise ValueError("Unavailable prior-session ATR")
        decision = 515+5*k
        minute = 511+start
        target = int(np.sign(target))*self.contracts
        remaining = 250*self.contracts+self.net
        if remaining <= 2.24*self.contracts or self.latched or k==76:
            target = 0
        if self.q and self.q != target:
            self._exit(float(o[start]),date,minute,"flatten" if k==76 else "target_change",decision)
        if target and not self.q:
            px, fee = self._fill(float(o[start]),target,date,minute,"entry",decision)
            self.net -= fee; self.q = target; self.entry = px; self.raw_entry=float(o[start]); self.entry_minute=minute
            budget_distance = (250*self.contracts+self.net-abs(target)*(.62+.5)*self.mult)/(2*abs(target))
            distance = .25*np.floor(min(.5*atr,budget_distance)/.25)
            if distance < .25:
                self._exit(float(o[start]),date,minute,"budget_reject_exit",decision); self.latched=True
            else:
                self.stop = self.entry-np.sign(self.q)*distance
        for j in range(start,end):
            if self.q:
                hit = l[j]<=self.stop if self.q>0 else h[j]>=self.stop
                if hit:
                    raw = min(o[j],self.stop) if self.q>0 else max(o[j],self.stop)
                    self._exit(float(raw),date,511+j,"protective_stop",decision)
                    worst = self.net  # do not mark prices occurring after the protective exit
                else:
                    adverse = l[j] if self.q>0 else h[j]
                    worst = self.equity(adverse)-abs(self.q)*(.62+.5)*self.mult
            else:
                worst = self.net
            self.low = min(self.low,float(worst))
            if self.net <= -250*self.contracts or 250*self.contracts+self.net <= 2.24*self.contracts:
                self.latched=True
        if k==76:
            assert self.q==0
        return self.equity(float(c[end-1]))


if __name__ == "__main__":
    RUNTIME.mkdir(parents=True,exist_ok=True)
    meta = dict(stock=prepare_stocks(), futures=prepare_futures(), defaults=DEFAULTS)
    meta["script_sha256"] = sha(__file__)
    (RUNTIME/"preparation.json").write_text(json.dumps(meta,indent=2)+"\n")
    print(json.dumps(meta,indent=2))
