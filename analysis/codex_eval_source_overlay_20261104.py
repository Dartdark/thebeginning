"""Separately preregistered factual DT flat-exit clock repair.

The original prepared tape, builder, engine and experiment are never changed.
Only DT kind2 source exits move from an erroneously assumed close to the
documented next-observed-bar OPEN. No favorable touch search or price change.
Import and selftest use no historical input. Actual repair requires a new
commit freezing this file and the source-justification files.
"""
from __future__ import annotations

import argparse
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
import pandas as pd

from codex_eval_paths_20261104 import ROOT, Tape, _time_seconds, segment_bounds, sha

SCRIPT="analysis/codex_eval_source_overlay_20261104.py"
SOURCES={
    "analysis/dual_thrust_test.py":
        "trade(): previous observed bar time>=1455 exits at current o[j]; flat and fallback close mapped to kind2 by lab_trades().",
    "analysis/codex_portfolio_audit_prepare.py":
        "Legacy DT normalization retained exit clock/raw price but record() default exit_open=False wrongly selected the minute close.",
    "checks/candidates/dual_thrust/trades.csv":
        "The frozen2018-04-02..2026-07-07 source cohort has401flat exits and zero fallbackclose exits; all selected kind2 exits are source-known OPEN.",
}
EXPECTED_CLOCK_COUNTS={'14:56':400,'14:57':1}
DT_LEDGER_SHA256='b34479fcda8d59aad27aed75712dbe166ce8f26740e91a27af8b376696bc577d'


def array_sha(a):
    a=np.ascontiguousarray(a)
    h=hashlib.sha256(json.dumps([a.dtype.str,list(a.shape)]).encode())
    h.update(memoryview(a).cast('B'))
    return h.hexdigest()


def _guard(commit):
    if not isinstance(commit,str) or len(commit)!=40:
        raise ValueError('A full separate committed amendment SHA is required')
    for name in [SCRIPT,*SOURCES]:
        if subprocess.check_output(['git','show',f'{commit}:{name}'],cwd=ROOT)!=(ROOT/name).read_bytes():
            raise ValueError('Changed amendment/source artifact: '+name)


def _repair(tape, trades):
    """Pure transform shared by guarded execution and fabricated selftests."""
    events=tape.events.copy()
    original_events=events.copy()
    selected=trades[(trades.key=='DT')&(pd.to_numeric(trades.kind)==2)]
    rows=[]
    for trade in selected.itertuples():
        tid=int(trade.trade_id)
        found=np.flatnonzero((events[:,1]==tid)&(events[:,4]==-1))
        if len(found)!=1:raise ValueError(f'DT trade{tid}: expected exactly one own exit')
        ix=int(found[0]);event=events[ix];old_row=int(event[0]);asset=int(event[3])
        if tape.keys[int(event[2])]!='DT' or tape.markets[asset]!='NQ' or int(event[9])!=0:
            raise ValueError('DT flat source event classification mismatch')
        source_stamp=pd.Timestamp(trade.exit_at)
        if source_stamp.tzinfo is not None:raise ValueError('Source exit_at must retain naive Chicago close label')
        target_time=float(_time_seconds(source_stamp)-60.)
        # At a minute boundary, previous-close and current-open rows may share
        # the same epoch. The RIGHTMOST equal-time row is the already-built
        # current minute phase0 (including any identical own-roundtrip node).
        left=int(np.searchsorted(tape.times,target_time,side='left'))
        right=int(np.searchsorted(tape.times,target_time,side='right'))
        new_row=right-1 if right>left else old_row
        reason=None
        if right==left:reason='known open clock has no existing tape row'
        elif tape.session[new_row]!=tape.session[old_row]:reason='known open clock maps outside original account session'
        entries=np.flatnonzero((events[:,1]==tid)&(events[:,4]==1))
        if len(entries)!=1:raise ValueError(f'DT trade{tid}: expected exactly one own entry')
        if reason is None and target_time<tape.times[int(events[int(entries[0]),0])]-1e-7:
            reason='known source exit clock precedes its own source entry'
        if reason is not None:new_row=old_row
        if reason is None:
            earlier_entries=(events[:,4]==1)&(events[:,0]<new_row)&\
                (np.abs(tape.times[events[:,0].astype(np.int64)]-target_time)<1e-7)
            if earlier_entries.any():
                reason='same-clock earlier new entry makes existing DT exit priority ambiguous'
                # This is an UNKNOWN admission point, not an executable fill.
                # Stop before any same-clock new entry can affect the account.
                new_row=left
        raw=float(trade.exit)
        if reason is None and not (np.isfinite(raw) and np.isfinite(tape.prices[new_row,asset]) and
                np.isclose(tape.prices[new_row,asset],raw,rtol=0,atol=1e-7)):
            reason='owned common OPEN quote does not exactly match raw source exit'
        events[ix,0]=new_row
        events[ix,6]=raw if reason is None else np.nan
        rows.append(dict(trade_id=tid,source_exit_at=source_stamp.isoformat(),
            requested_open_utc=target_time,old_row=old_row,new_row=int(new_row),
            old_event_time=float(tape.times[old_row]),new_event_time=float(tape.times[new_row]),
            raw_source_exit=raw,old_event_raw_fill=float(original_events[ix,6]),
            matched=reason is None,unknown_reason=reason))
    allowed=np.zeros_like(events,dtype=bool)
    for row in rows:
        ix=np.flatnonzero((original_events[:,1]==row['trade_id'])&(original_events[:,4]==-1))[0]
        allowed[ix,[0,6]]=True
    assert np.array_equal(events[~allowed],original_events[~allowed],equal_nan=True)
    # No other field or event is permitted to change. Keep a stable order for
    # existing exits/entries; the frozen engine performs own-trade topology.
    order=np.lexsort((events[:,1],events[:,4],events[:,0])) if len(events) else np.array([],int)
    events=events[order]
    nodes=np.unique(np.r_[tape.node_rows,events[:,0].astype(np.int64),0,len(tape.times)-1])
    lo,hi,missing=segment_bounds(tape.prices,nodes)
    metadata=dict(tape.metadata)
    metadata.update(source_overlay='DT kind2 known next-observed-bar OPEN; original baseline preserved',
        overlay_original_event_sha256=array_sha(tape.events),overlay_event_sha256=array_sha(events),
        overlay_legacy_quality_preserved=True,
        overlay_admission='Exact saved raw exit at known open clock or own-eventNaN; original OHLC model remains conditional')
    out=replace(tape,events=events,node_rows=nodes,segment_min=lo,segment_max=hi,
        segment_missing=missing,metadata=metadata)
    return out,pd.DataFrame(rows)


def repair_dt_time_exits(tape, amendment_commit, output_directory=None, *, source_directory=None):
    """Return new Tape; optionally save overlay-only arrays and audit receipt.

    ``tape`` must be the original hash-verified prepared tape. Supply its
    directory when the loader omitted trades.csv. The original experiment's
    preregistration metadata remains; the distinct amendment is added.
    """
    _guard(amendment_commit)
    original_commit=tape.metadata.get('preregistration_commit')
    if not isinstance(original_commit,str) or len(original_commit)!=40 or original_commit==amendment_commit:
        raise ValueError('A distinct original prepared-study preregistration is required')
    source_receipt=None
    if source_directory is not None:
        folder=Path(source_directory)
        source_receipt=json.loads((folder/'prepare_receipt.json').read_text())
        if source_receipt['preregistration_commit']!=original_commit:
            raise ValueError('Original prepared receipt belongs to another study')
        for name,expected in source_receipt['artifacts'].items():
            if sha(folder/name)!=expected:raise ValueError('Original prepared artifact changed: '+name)
        stored=json.loads((folder/'metadata.json').read_text())
        if stored!=tape.metadata:raise ValueError('Original tape metadata differs from verified prepared artifact')
        trades=pd.read_csv(folder/'trades.csv',parse_dates=['entry_at','exit_at'])
    elif isinstance(tape.trades,pd.DataFrame):
        trades=tape.trades.copy()
    else:
        raise ValueError('Original verified trades.csv directory is required')
    selected=trades[(trades.key=='DT')&(pd.to_numeric(trades.kind)==2)]
    clocks=pd.to_datetime(selected.exit_at).dt.strftime('%H:%M').value_counts().to_dict()
    if clocks!=EXPECTED_CLOCK_COUNTS:
        raise ValueError('DT overlay scope differs from frozen401 source-flat exits')
    if tape.metadata.get('source_ledger_hashes',{}).get('DT')!=DT_LEDGER_SHA256:
        raise ValueError('DT original normalized source ledger differs from frozen factual-repair scope')
    before=array_sha(tape.events)
    corrected,changes=_repair(tape,trades)
    assert array_sha(tape.events)==before
    assert corrected.prices is tape.prices and corrected.times is tape.times
    manifest=dict(amendment_commit=amendment_commit,original_preregistration_commit=original_commit,
        overlay_script_sha256=sha(ROOT/SCRIPT),original_prepare_receipt=source_receipt,
        sources={name:dict(sha256=sha(ROOT/name),justification=why) for name,why in SOURCES.items()},
        original_event_sha256=before,corrected_event_sha256=array_sha(corrected.events),
        original_price_sha256=array_sha(tape.prices),original_time_sha256=array_sha(tape.times),
        common_prices_and_times_unchanged=True,other_source_events_unchanged=True,
        selected_dt_kind2_exits=len(changes),matched=int(changes.matched.sum()) if len(changes) else 0,
        unknown=int((~changes.matched).sum()) if len(changes) else 0,
        status='Factual adapter repair only; no allocation change; independent economic verification pending')
    corrected.metadata.update(source_overlay_amendment_commit=amendment_commit,
        source_overlay_manifest=manifest)
    if output_directory is not None:
        dest=Path(output_directory)
        if source_directory is not None and dest.resolve()==Path(source_directory).resolve():
            raise ValueError('Overlay must not overwrite original prepared directory')
        dest.mkdir(parents=True,exist_ok=True)
        names=['overlay.npz','repair_changes.csv','repair_manifest.json']
        if any((dest/name).exists() for name in names):raise FileExistsError('Preserve existing overlay artifacts')
        np.savez_compressed(dest/'overlay.npz',events=corrected.events,node_rows=corrected.node_rows,
            segment_min=corrected.segment_min,segment_max=corrected.segment_max,segment_missing=corrected.segment_missing)
        changes.to_csv(dest/'repair_changes.csv',index=False)
        manifest['overlay_artifacts']={name:sha(dest/name) for name in names[:2]}
        (dest/'repair_manifest.json').write_text(json.dumps(manifest,indent=2,allow_nan=False)+'\n')
    return corrected,manifest


def selftest():
    """Fabricated clocks only. No saved ledger, owned price or return loaded."""
    stamp=pd.Timestamp('2020-01-02 14:56');clock=_time_seconds(stamp)
    # Previous14:55close and14:56open share a clock but have different prices.
    # The source open must select the latter, never search a later matchingtouch.
    times=np.array([clock-120,clock-60,clock-60,clock-40,clock-20,clock])
    prices=np.array([[100.],[99.],[101.],[103.],[98.],[102.]])
    events=np.array([[0,0,0,0,1,1,100,50,1,0],[5,0,0,0,-1,1,np.nan,50,1,0],
                     [0,1,1,0,1,1,100,5,1,0],[5,1,1,0,-1,1,102,5,1,0]],float)
    nodes=np.array([0,5]);lo,hi,miss=segment_bounds(prices,nodes)
    tape=Tape(prices,times,np.zeros(6,np.int32),events,nodes,lo,hi,miss,
        np.zeros(6,bool),np.zeros(6,bool),np.zeros(6,bool),np.array([20200102]),
        ('NQ',),('DT','OTHER'),None,None,np.ones((2,1),bool),np.ones(1,bool),{})
    trades=pd.DataFrame([dict(key='DT',kind=2,trade_id=0,exit_at=stamp,exit=101.)])
    before=tape.events.copy();fixed,rows=_repair(tape,trades)
    dt=fixed.events[(fixed.events[:,1]==0)&(fixed.events[:,4]==-1)][0]
    assert dt[0]==2 and dt[6]==101. and rows.matched.all()
    assert np.array_equal(tape.events,before,equal_nan=True)
    assert fixed.prices is tape.prices and 2 in fixed.node_rows
    assert np.array_equal(fixed.events[fixed.events[:,1]==1],events[events[:,1]==1],equal_nan=True)
    # If another new entry occupies an earlier same-clock point, the DT
    # existing-exit priority is uncertain. OwnNaN belongs at the FIRST equal
    # epoch row, before any such entry; never at the oldclose/late point.
    collision_events=tape.events.copy();collision_events[2,0]=1
    collision,rows=_repair(replace(tape,events=collision_events),trades)
    dt=collision.events[(collision.events[:,1]==0)&(collision.events[:,4]==-1)][0]
    assert dt[0]==1 and np.isnan(dt[6]) and not rows.matched.any()
    # Raw source102 appears later atclose, butknownopen101cannotmovethere.
    trades['exit']=102.;unknown,rows=_repair(tape,trades)
    dt=unknown.events[(unknown.events[:,1]==0)&(unknown.events[:,4]==-1)][0]
    assert dt[0]==2 and np.isnan(dt[6]) and not rows.matched.any()
    # A source clock later than every prepared point remains an own UNKNOWN;
    # no nearest-time fallback or fabricated point is inserted.
    trades['exit_at']=stamp+pd.Timedelta(minutes=5)
    late,rows=_repair(tape,trades)
    dt=late.events[(late.events[:,1]==0)&(late.events[:,4]==-1)][0]
    assert dt[0]==5 and np.isnan(dt[6])
    # An impossible clock before its ownentry is also unqualified.
    trades['exit_at']=stamp;trades['exit']=101.
    late_entry=tape.events.copy();late_entry[0,0]=3
    early,rows=_repair(replace(tape,events=late_entry),trades)
    dt=early.events[(early.events[:,1]==0)&(early.events[:,4]==-1)][0]
    assert np.isnan(dt[6])
    print('PASS: synthetic DT known-open clock, exact quote, immutable baseline, unrelated events, and early/late mismatch checks; no market outcomes.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['selftest'])
    args=parser.parse_args()
    selftest()
