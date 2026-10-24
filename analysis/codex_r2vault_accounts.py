"""R2Vault Apex comparison using the reviewed Anson account engine.

No import-time market-data read or return calculation. Full execution requires
the committed R2Vault preregistration. Candidate paths use replay-supplied causal
entry/exit boundary extrema rather than whole-minute extrema across fills.
"""
from __future__ import annotations

import argparse
import gc
import importlib
import json
import pickle
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agents/codex/runtime/or_pullback_python"))
sys.path.insert(0, str(ROOT / "analysis"))
import numpy as np
import pandas as pd
import codex_anson_plan as A
import codex_anson_accounts as B

OUT = ROOT / "analysis/outputs/codex_r2vault/accounts"
REPLAY = OUT.parent / "replay"
CONTEXT = "172322e5151f45e2cbf1da4dbd9efb20ba12d1a9"
CALENDAR_COMMIT = "dab01a8eab5dad576474d28e4a03280a98e69af6"
MODES = ("et_apex", "ct_apex")
PREPARED = ROOT / "agents/codex/runtime/anson_plan.pkl"
BASE_MANIFEST = ROOT / "analysis/outputs/codex_anson/baseline/prepared_manifest.json"
INVENTORY = ROOT / "analysis/outputs/codex_r2vault/context_inventory.json"
COHORTS = B.COHORTS


class ChronologicalCI:
    """Cache the identical paired20-start block draws, preserving missing starts.

    Draw order and floating reductions match the existing helper. Reusing the
    same index matrix across outcomes avoids regenerating it hundreds of times.
    """
    def __init__(self, valid, seed=903, samples=5000, block=20):
        self.valid = np.asarray(valid, bool)
        T = len(self.valid)
        rng = np.random.default_rng(seed)
        self.idx = np.empty((samples, T), dtype=np.int32)
        for start in range(0, samples, 100):
            size = min(100, samples-start)
            st = rng.integers(0, T, (size, int(np.ceil(T/block))))
            self.idx[start:start+size] = ((st[:, :, None]+np.arange(block)) % T).reshape(size, -1)[:, :T]
        self.take_valid = self.valid[self.idx]
        self.denominator = self.take_valid.sum(axis=1)
        if not (self.denominator > 0).all():
            raise ValueError("An entire confidence resample contains no eligible start")

    def interval(self, delta):
        delta = np.asarray(delta, float)
        if not np.any(delta[self.valid]):
            return [0., 0.]
        value = delta[self.idx]
        np.multiply(value, self.take_valid, out=value)
        return np.percentile(value.sum(axis=1)/self.denominator, [2.5, 97.5]).tolist()


def candidate_paths(g, trades, fee=1.04, known_closed=None):
    """One-MNQ adverse/closed paths from executable fills and causal extrema.

    The RT fee and entry slip0.50 are reserved from entry. Targets have no exit
    slip; stops and market exits pay0.50. The replay owns intraminute ordering:
    only actually traversed held prices may set each boundary minimum.
    """
    w, r = np.zeros(g.o.shape), np.zeros(g.o.shape)
    for t in trades.itertuples():
        d, e, z = int(t.day), int(t.entry_j), int(t.exit_j)
        if int(t.side) != 1 or not (0 <= e <= z < g.o.shape[1]):
            raise ValueError("Expected same-date long-only Apex ledger")
        if t.entry_phase not in ("open", "intrabar") or t.exit_phase not in ("open", "intrabar"):
            raise ValueError("Unknown executable fill phase")
        if bool(t.cross_date) or int(t.unknown_held_minutes):
            raise ValueError("Unknown/cross-date source return included")
        end = z+int(t.exit_phase != "open")
        price = np.array(g.l[d, e:end], copy=True)
        if len(price):
            price[0] = float(t.entry_minute_adverse_px)
            if t.exit_phase != "open":
                price[-1] = float(t.exit_minute_adverse_px)
            if e == z and t.exit_phase != "open" and not np.isclose(
                t.entry_minute_adverse_px, t.exit_minute_adverse_px, rtol=0, atol=1e-10):
                raise ValueError("Same-minute boundary extrema disagree")
            for offset in np.flatnonzero(~np.isfinite(price)):
                minute = e+int(offset)
                if known_closed is None or not known_closed[d,minute]:
                    raise ValueError("Unknown missing causal held-minute price")
                earlier = np.flatnonzero(np.isfinite(g.c[d,e:minute]))
                if not len(earlier):
                    raise ValueError("No prior observable held Close for a known-closure mark")
                price[offset] = g.c[d,e+earlier[-1]]
        exit_slip = .0 if int(t.kind) == 1 else .5
        net = (float(t.exit)-float(t.entry))*2.-float(fee)-.5-exit_slip
        gross_points = getattr(t, "gross_points", float(t.exit)-float(t.entry))
        if not np.isclose(gross_points, t.exit-t.entry, rtol=0, atol=1e-7):
            raise ValueError("Source fill geometry disagrees with gross ledger")
        marks = (price-float(t.entry))*2.-float(fee)-.5
        if len(marks) and t.exit_phase != "open":
            # Retain any earlier adverse move and the executable close cost.
            marks[-1] = min(marks[-1], net)
        w[d, e:end] += marks
        w[d, end:] += net
        r[d, z:] += net
    return w, r


def synthetic_paths():
    from types import SimpleNamespace
    g = SimpleNamespace(o=np.full((1, 12), 100.), l=np.full((1, 12), 99.),
                        h=np.full((1, 12), 101.),c=np.full((1,12),100.))
    g.l[0, 2], g.l[0, 5] = 1., 1.  # Entire-bar lows occurred outside this trade.
    row = dict(day=0, entry_j=2, exit_j=5, side=1, entry=100., exit=140.,
        gross_points=40., entry_phase="intrabar", exit_phase="intrabar", kind=1,
        entry_minute_adverse_px=100., exit_minute_adverse_px=135.,
        cross_date=False, unknown_held_minutes=0)
    w,r = candidate_paths(g, pd.DataFrame([row]))
    np.testing.assert_allclose(w[0, 2], -1.54)
    np.testing.assert_allclose(w[0, 3:5], -3.54)
    np.testing.assert_allclose(w[0, 5], 68.46)
    np.testing.assert_allclose(w[0, 6:], 78.46)
    np.testing.assert_allclose(r[0, 5:], 78.46)
    g.l[0,4],g.c[0,3] = np.nan,98.
    known = np.zeros(g.l.shape,dtype=bool)
    known[0,4] = True
    wc,_ = candidate_paths(g,pd.DataFrame([row]),known_closed=known)
    np.testing.assert_allclose(wc[0,4],-5.54)
    try:
        candidate_paths(g,pd.DataFrame([row]))
        raise AssertionError("Unknown held price was accepted")
    except ValueError:
        pass
    g.l[0,4],g.c[0,3] = 99.,100.
    row.update(exit=25., gross_points=-75., kind=0, exit_minute_adverse_px=25.)
    w,r = candidate_paths(g, pd.DataFrame([row]))
    np.testing.assert_allclose(w[0, 5:], -152.04)
    row.update(exit=20., gross_points=-80., exit_phase="open")
    w,r = candidate_paths(g, pd.DataFrame([row]))
    np.testing.assert_allclose(w[0, 5:], -162.04)
    row.update(exit_j=2, exit=25., gross_points=-75., exit_phase="intrabar",
               entry_minute_adverse_px=25., exit_minute_adverse_px=25.)
    w,r = candidate_paths(g, pd.DataFrame([row]))
    np.testing.assert_allclose(w[0, 2:], -152.04)
    twice = pd.DataFrame([row, dict(row, entry_j=7, exit_j=9, entry_minute_adverse_px=100.,
                                  exit_minute_adverse_px=25.)])
    w,r = candidate_paths(g, twice)
    np.testing.assert_allclose(r[0, -1], -304.08)
    ws,rs = candidate_paths(g, twice, 1.24)
    np.testing.assert_allclose(ws[0, 7:]-w[0, 7:], -.4)
    np.testing.assert_allclose(rs[0, -1]-r[0, -1], -.4)
    delta = np.sin(np.arange(173))*3
    valid = np.arange(173) % 19 != 0
    cached = ChronologicalCI(valid).interval(delta)
    expected = B.chronological_ci(delta, valid)
    np.testing.assert_allclose(cached, expected, rtol=0, atol=1e-12)
    return dict(pre_entry_low_excluded=True, post_exit_low_excluded=True,
        entry_RT_fee_reservation=True, no_target_exit_slip=True, stop_exit_slip=True,
        open_gap_fill=True, same_minute_fills=True, every_reentry_pays_fee=True,
        cached_chronological_CI_matches_original=True,known_closure_stale_mark_only=True,
        unknown_missing_price_rejected=True)


def allocations(base, vb_keys, context):
    empty = {k:v for k,v in base.items() if k not in vb_keys}
    plans = dict(BASE=dict(base), EMPTY_VB=empty)
    for mode in MODES:
        for n in ((1,2,4) if context.startswith("150") else (1,2)):
            plans[f"{mode}__ADD{n}"] = {**base, mode:n}
        plans[f"{mode}__REPLACE_VB2"] = {**empty, mode:2}
    return plans


def verify_reuse():
    inv = json.loads(INVENTORY.read_text())
    if inv["reference"] != CONTEXT or inv["changed"] or not inv["expanded_cache_matches"]:
        raise ValueError("Current-plan reuse has not been verified at the declared context")
    base = json.loads(BASE_MANIFEST.read_text())
    if A.file_sha(PREPARED) != base["expanded_cache_sha256"] or base["fee"] != 1.04:
        raise ValueError("Prepared real-fee baseline changed")
    return inv, base


def read_inputs(lab):
    ledgers, masks, inputs = {}, [], {}
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr])
    combined = pd.DataFrame(index=dates)
    for mode in MODES:
        tp, ap = REPLAY/f"{mode}_trades.csv", REPLAY/f"{mode}_audit.csv"
        t, audit = pd.read_csv(tp, parse_dates=["date"]), pd.read_csv(ap, parse_dates=["date"])
        if audit.gridrow.duplicated().any() or audit.account_eligible.dtype != bool:
            raise ValueError("Invalid model coverage audit")
        if not set(lab.tr).issubset(set(audit.gridrow)):
            raise ValueError("Source audit omits baseline trading dates")
        if not np.array_equal(audit.date.to_numpy(), pd.DatetimeIndex(lab.g.ts[audit.gridrow.to_numpy(int)]).to_numpy()):
            raise ValueError("Replay calendar differs from the baseline grid")
        masks.append(dates.isin(set(audit.loc[audit.account_eligible, "date"])))
        detail = audit.set_index("date").reindex(dates)
        for col in detail:
            combined[f"{mode}__{col}"] = detail[col].to_numpy()
        ledgers[mode] = t
        inputs[str(tp.relative_to(ROOT))],inputs[str(ap.relative_to(ROOT))] = A.file_sha(tp),A.file_sha(ap)
    eligible = np.logical_and.reduce(masks)
    baseline_finite = np.ones(lab.D,dtype=bool)
    for leg in set().union(*[set(p) for p in A.funded_plans().values()]):
        baseline_finite &= np.isfinite(lab.W[leg]).all(axis=1)&np.isfinite(lab.C[leg])
    if not baseline_finite.all():
        raise ValueError("Prepared baseline contains nonfinite paths; audit rather than silently discard")
    combined["baseline_paths_finite"] = baseline_finite
    combined["common_account_eligible"] = eligible
    combined.to_csv(OUT/"common_day_audit.csv",index_label="date")
    eligible_dates = set(dates[eligible])
    counts = {}
    for mode,t in ledgers.items():
        keep = t.date.isin(eligible_dates)
        counts[mode] = dict(raw=len(t), shared_eligible=int(keep.sum()), excluded=int((~keep).sum()))
        ledgers[mode] = t.loc[keep].copy()
    A.dump(OUT/"account_calendar.json", dict(total=lab.D, common_eligible=int(eligible.sum()),
        excluded_dates=dates[~eligible].strftime("%Y-%m-%d").tolist(), trades=counts,inputs=inputs,
        funded_policy="both clocks and all allocations use the same complete-day universe; block adjacency changes",
        evaluation_policy="same full real21day windows wholly inside each cohort; missing days omitted without calendar compression"))
    return ledgers,eligible,inputs


def funded(lab,fb,F50,F150,fee,eligible):
    histories = {}
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr])
    for cohort,(start,stop) in COHORTS.items():
        boot = fb.Boot(lab,start=start)
        boot.days = boot.days[eligible[boot.days]&np.asarray(dates[boot.days]<stop)]
        histories[cohort] = np.concatenate([boot._histories(250,500,20,s) for s in (1,2,3,4)])
        np.save(OUT/f"funded_histories_{cohort}.npy",histories[cohort])
    rows,paired,checks,resources = [],[],[],[]
    for context,F in (("50K_funded",F50),("150K_funded",F150)):
        parameters = B.rules(F,context)
        results = {}
        for name,plan in allocations(A.funded_plans()[context],("VB_N","VB_F"),context).items():
            start = time.monotonic()
            keys = sorted(plan)
            w,c = np.stack([lab.W[k] for k in keys]),np.stack([lab.C[k] for k in keys])
            names,size = lab._base({k:plan[k] for k in keys})
            assert names == keys
            if not np.isfinite(w).all() or not np.isfinite(c).all():
                raise ValueError("Nonfinite joint account path")
            table = B.acc.make_table(w,c,size)
            checks += B.parity_check(w,c,table,histories["2018_plus"][[0,1,17,333,999]],
                                     F,parameters,f"{fee}/{context}/{name}")
            for cohort,h in histories.items():
                results.setdefault(cohort,{})[name] = (B.run_table(table,h,250,parameters),
                                                        B.run_table(table,h,500,parameters))
            resources.append(dict(fee=fee,context=context,config=name,seconds=time.monotonic()-start,
                                  max_quantity_states=int(table["counts"].max())))
            print(f"funded {fee:.2f} {context} {name} {resources[-1]['seconds']:.1f}s",flush=True)
            del w,c,table
            gc.collect()
        for cohort,result in results.items():
            a,b = B.funded_summaries(result,fee,context,cohort)
            rows += a
            paired += b
            np.savez_compressed(OUT/f"funded_results_{fee:.2f}_{context}_{cohort}.npz",
                **{f"{k}__{h}":result[k][i] for k in result for i,h in enumerate((250,500))})
    A.dump(OUT/f"funded_parity_{fee:.2f}.json",checks)
    A.dump(OUT/f"funded_resources_{fee:.2f}.json",resources)
    return rows,paired


def evaluation(lab,scratch,fee,paths,eligible,prereg):
    bundle = A.evaluation_parts(scratch,preregistration_commit=prereg,
        authorized_returns=True,fee=fee,grid=lab.g)
    complete = np.array([s+21 <= lab.D and eligible[s:s+21].all() for s in range(lab.D)])
    last_dates = np.full(lab.D,np.datetime64("NaT"),dtype="datetime64[ns]")
    last_dates[:lab.D-20] = bundle.dates[20:].to_numpy()
    # Cohort membership requires every one of the21 real sessions, not only
    # its start, to remain inside the declared design/validation interval.
    masks = {k:np.asarray((bundle.dates>=lo)&(bundle.dates<hi)&(last_dates<np.datetime64(hi)))
             for k,(lo,hi) in COHORTS.items()}
    ci = {k:ChronologicalCI(complete[mask]) for k,mask in masks.items()}
    rows,paired,references = [],[],[]
    for context,part in bundle.contexts.items():
        pp,q = part.parts,part.quantities
        bw,br = sum(pp[k][0]*q[k] for k in q),sum(pp[k][1]*q[k] for k in q)
        ew,er = bw-pp["VB"][0]*q["VB"],br-pp["VB"][1]*q["VB"]
        raw = {}
        for name,plan in allocations({k:1 for k in pp},("VB",),context).items():
            if name == "BASE":
                w,r = bw,br
            elif name == "EMPTY_VB":
                w,r = ew,er
            else:
                mode = name.split("__")[0]
                w0,r0 = (ew,er) if "REPLACE" in name else (bw,br)
                cw,cr = paths[mode]
                w,r = w0+cw*plan[mode],r0+cr*plan[mode]
            if context.startswith("50"):
                result = [part.challenge(w,r,np.arange(s,min(s+21,lab.D)),lambda p,c,n:1.) for s in range(lab.D)]
            else:
                result = [part.challenge(w,r,s,lab.D,part.rules) for s in range(lab.D)]
            o = np.array([x[0] if x else "" for x in result])
            d = np.array([x[1] if x else 0 for x in result])
            raw[name] = (o,d)
            for cohort,mask in masks.items():
                ok = complete&mask
                rows.append(dict(fee=fee,context=context,cohort=cohort,config=name,starts=int(ok.sum()),
                    passed=float((o[ok]=="pass").mean()),failed=float((o[ok]=="fail").mean()),
                    timed_out=float((o[ok]=="time").mean()),median_pass_days=float(np.median(d[ok&(o=="pass")])),
                    changed_vs_base=float((o[ok]!=raw["BASE"][0][ok]).mean())))
            if name not in ("BASE","EMPTY_VB"):
                del w,r
            print(f"evaluation {fee:.2f} {context} {name}",flush=True)
        for name,(o,d) in raw.items():
            for cohort,mask in masks.items():
                for ref in ("BASE","EMPTY_VB"):
                    for metric,label in (("passed","pass"),("failed","fail"),("timed_out","time")):
                        delta = (o[mask]==label).astype(float)-(raw[ref][0][mask]==label)
                        lo,hi = ci[cohort].interval(delta)
                        paired.append(dict(fee=fee,context=context,cohort=cohort,config=name,reference=ref,
                            metric=metric,delta=float(delta[complete[mask]].mean()),lo=lo,hi=hi))
        frame = pd.DataFrame({f"{k}__{col}":v[i] for k,v in raw.items()
                              for i,col in enumerate(("outcome","days"))},index=bundle.dates)
        frame["common_complete_21day_start"] = complete
        frame["window_last_date"] = last_dates
        for cohort,mask in masks.items():
            frame[f"{cohort}__whole_window_inside"] = mask
        frame.to_csv(OUT/f"evaluation_starts_{fee:.2f}_{context}.csv",index_label="date")
        for cohort,mask in masks.items():
            ok = mask&(np.arange(lab.D)+21<=lab.D)
            o,d = raw["BASE"]
            references.append(dict(fee=fee,context=context,cohort=cohort,starts=int(ok.sum()),
                passed=float((o[ok]=="pass").mean()),failed=float((o[ok]=="fail").mean()),
                timed_out=float((o[ok]=="time").mean()),median_pass_days=float(np.median(d[ok&(o=="pass")]))))
    A.dump(OUT/f"evaluation_full_calendar_BASE_{fee:.2f}.json",references)
    return rows,paired


def overlap(lab,eligible):
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr])
    rows = []
    for context,plan in A.funded_plans().items():
        names,size = lab._base(plan)
        q = np.floor(size+1e-9)
        baseline = sum(lab.C[k]*q[i] for i,k in enumerate(names))
        frame = pd.DataFrame({"BASE_FULL_SIZE":baseline,**{m:lab.C[m] for m in MODES}},index=dates)
        frame.loc[eligible].to_csv(OUT/f"daily_joint_pnl_{context}.csv",index_label="date")
        for mode in MODES:
            cc = lab.C[mode]
            for cohort,(lo,hi) in COHORTS.items():
                ok = eligible&np.asarray((dates>=lo)&(dates<hi))
                loss = ok&(baseline<0)
                rows.append(dict(context=context,mode=mode,cohort=cohort,eligible_days=int(ok.sum()),
                    correlation=float(np.corrcoef(baseline[ok],cc[ok])[0,1]),plan_loss_days=int(loss.sum()),
                    joint_loss_days=int((loss&(cc<0)).sum()),candidate_net_on_plan_loss_days=float(cc[loss].sum())))
    pd.DataFrame(rows).to_csv(OUT/"overlap_daily.csv",index=False)


def minute_overlap(lab,scratch,ledgers,eligible,known_closed):
    """Descriptive ledger occupancy and candidate marks at VB's adverse minute.

    Full-size integer quantities bound cushion-scaled exposure. Inclusive MC
    endpoints retain minute ambiguity; they do not prove tick-level overlap.
    No actual account breach time is inferred from closed daily P&L.
    """
    import codex_or_pullback_exposure as ex
    pf,build = importlib.import_module("portfolio"),importlib.import_module("build_lab")
    bridge,dt = importlib.import_module("bridge_monday_confirm"),importlib.import_module("dual_thrust_test")
    dates = pd.DatetimeIndex(lab.g.ts[lab.tr])
    shape,lookup = (lab.D,lab.g.o.shape[1]),{int(row):i for i,row in enumerate(lab.tr)}
    flags = pd.read_pickle(Path(scratch)/"single_print_sessions.pkl").flag.reindex(dates).fillna(False).to_numpy(bool)
    raw,files = {},{}
    for key in ("VB","ONB_ML2_MC","MON_MC","EOS","LDF_MC","NFP_MC"):
        files[key] = ROOT/build.REPORTS[key][0]
        raw[key] = pf.load_mc(lab.g,str(files[key]))
    files["MON_BR_MC"] = ROOT/bridge.F
    raw["MON_BR_MC"] = bridge.load_bridge_mc(lab.g,str(files["MON_BR_MC"]))
    files["RS"] = A.RS_REPLAY
    raw["RS"] = pd.read_csv(files["RS"])
    raw["RS_L"] = raw["RS"].loc[raw["RS"].side>0].copy()
    files["DT"] = A.RUNTIME/"DT_timed.csv"
    raw["DT"] = dt.lab_trades(lab.g,pd.read_csv(files["DT"],parse_dates=["date"]))
    byrow = dict(zip(lab.tr,flags))
    vbflag = raw["VB"].day.map(byrow).fillna(False).to_numpy(bool)
    raw["VB_N"],raw["VB_F"] = raw["VB"].loc[~vbflag],raw["VB"].loc[vbflag]
    occupancy_rows,timing_rows,baseline_gaps = [],[],[]
    for context,plan in A.funded_plans().items():
        nq = {k:v for k,v in plan.items() if k not in ("CLS","MOC_MES")}
        names,size = lab._base(nq)
        quantity = np.floor(size+1e-9)
        current = {}
        for i,leg in enumerate(names):
            current[leg] = ex.occupancy(raw[leg],lookup,quantity[i],shape)
            count = np.bincount(raw[leg].day.to_numpy(int),minlength=len(lab.g.ts))[lab.tr]
            np.testing.assert_allclose(count,lab.N[leg],rtol=0,atol=0,err_msg=f"Ledger occupancy count:{leg}")
            held_qty = current[leg][0]+current[leg][1]
            gap = known_closed[lab.tr]&~np.isfinite(lab.g.l[lab.tr])&eligible[:,None]
            baseline_gaps.append(dict(context=context,leg=leg,
                known_closed_held_minutes=int(((held_qty>0)&gap).sum()),
                known_closed_contract_minutes=int(held_qty[gap].sum()),
                inherited_mark="cached portfolio.paths substitutes entry for missing adverse OHLC; baseline paths unchanged"))
        longs,shorts = sum(v[0] for v in current.values()),sum(v[1] for v in current.values())
        vblong = current["VB_N"][0]+current["VB_F"][0]
        vbgross = vblong+current["VB_N"][1]+current["VB_F"][1]
        qmap = {k:quantity[i] for i,k in enumerate(names)}
        vbw = lab.W["VB_N"]*qmap["VB_N"][:,None]+lab.W["VB_F"]*qmap["VB_F"][:,None]
        low_j,low_value = vbw.argmin(axis=1),vbw.min(axis=1)
        for mode,t in ledgers.items():
            held_t = t.copy()
            held_t["j0"] = held_t.entry_j
            held_t["j1"] = held_t.exit_j-(held_t.exit_phase=="open").astype(int)
            candidate,_,_ = ex.occupancy(held_t,lookup,np.ones(lab.D),shape)
            held = candidate>0
            if candidate.max()>1:
                raise ValueError("Candidate positions overlap despite one-position rule")
            mark = lab.W[mode][np.arange(lab.D),low_j]
            final = lab.C[mode]
            trade_row = t.day.map(lookup).to_numpy(int)
            trade_net = (t.exit-t.entry).to_numpy()*2.-1.04-.5-.5*(t.kind.to_numpy(int)!=1)
            for cohort,(lo,hi) in COHORTS.items():
                day = eligible&np.asarray((dates>=lo)&(dates<hi))
                mask = held&day[:,None]
                n = int(mask.sum())
                if n:
                    for amount in ((1,2,4) if context.startswith("150") else (1,2)):
                        occupancy_rows.append(dict(context=context,mode=mode,cohort=cohort,candidate_mnq=amount,
                            held_minutes=n,held_days=int(mask.any(axis=1).sum()),
                            VB_overlap_fraction=float((mask&(vbgross>0)).sum()/n),
                            any_NQ_overlap_fraction=float((mask&(longs+shorts>0)).sum()/n),
                            same_side_long_overlap_fraction=float((mask&(longs>0)).sum()/n),
                            opposite_side_short_overlap_fraction=float((mask&(shorts>0)).sum()/n),
                            maximum_current_long_MNQ_while_candidate_held=int(longs[mask].max()),
                            maximum_added_long_MNQ=int((longs[mask]+amount).max()),
                            maximum_replaceVB_long_MNQ=int((longs[mask]-vblong[mask]+amount).max())))
                adverse = day&(low_value<0)
                positive = adverse&(final>0)
                win = day[trade_row]&(trade_net>0)&(low_value[trade_row]<0)
                late = win&(t.exit_j.to_numpy(int)>low_j[trade_row])
                timing_rows.append(dict(context=context,mode=mode,cohort=cohort,
                    VB_adverse_days=int(adverse.sum()),positive_candidate_close_days=int(positive.sum()),
                    positive_close_days_already_positive_at_VB_low=int((positive&(mark>0)).sum()),
                    candidate_adverse_mark_sum_at_VB_low=float(mark[adverse].sum()),
                    candidate_positive_final_sum_on_VB_adverse_days=float(final[positive].sum()),
                    winning_trades_on_VB_adverse_days=int(win.sum()),wins_closing_after_VB_low=int(late.sum()),
                    wins_closing_in_same_minute_as_VB_low=int((win&(t.exit_j.to_numpy(int)==low_j[trade_row])).sum())))
        del current,longs,shorts,vbw
    pd.DataFrame(occupancy_rows).to_csv(OUT/"minute_occupancy.csv",index=False)
    pd.DataFrame(timing_rows).to_csv(OUT/"VB_low_timing.csv",index=False)
    pd.DataFrame(baseline_gaps).to_csv(OUT/"baseline_known_closure_positions.csv",index=False)
    A.dump(OUT/"minute_overlap_manifest.json",dict(
        inputs={k:dict(path=str(p),sha256=A.file_sha(p)) for k,p in files.items()},
        fee=1.04,scope="NQ only; baseline full-size integer quantities, not per-bootstrap cushion quantities",
        timing="MC endpoints inclusive; R2 causal held minutes include entry and exclude open exit minute",
        interpretation="minute occupancy is conservative; opposite NQ shorts do not cancel gross longs",
        account_breach_limit="actual account breach minute/cushion was not retained; VB adverse-minute timing is descriptive and is not an account-breach claim"))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--scratch",default="scratch_data")
    ap.add_argument("--prereg")
    ap.add_argument("--plan-path",default="agents/codex/plans/r2vault.md")
    ap.add_argument("--closure-mask",default=str(REPLAY/"known_closed.npy"))
    ap.add_argument("--fixtures-only",action="store_true")
    args = ap.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    A.dump(OUT/"path_fixtures.json",synthetic_paths())
    if args.fixtures_only:
        return
    A.authorize(args.prereg,True)
    A.P._git("cat-file","-e",f"{args.prereg}:{args.plan_path}")
    A.P._git("cat-file","-e",f"{CALENDAR_COMMIT}:agents/codex/inputs/r2vault/calendar_metadata.md")
    inventory,provenance = verify_reuse()
    started = time.monotonic()
    with A.pinned_imports(args.scratch):
        F50,F150 = importlib.import_module("funded_sim"),importlib.import_module("funded_sim150")
        fb = importlib.import_module("funded_bootstrap")
        previous_out = B.OUT
        try:
            B.OUT = OUT
            B.synthetic_checks(F50,F150)
        finally:
            B.OUT = previous_out
        with PREPARED.open("rb") as f:
            lab = pickle.load(f)
        ledgers,eligible,inputs = read_inputs(lab)
        known_closed = np.load(args.closure_mask)
        if known_closed.shape!=lab.g.o.shape or known_closed.dtype!=bool:
            raise ValueError("Unexpected shared known-closure mask")
        inputs[str(Path(args.closure_mask).resolve().relative_to(ROOT))] = A.file_sha(args.closure_mask)
        fr,fd,er,ed = [],[],[],[]
        totals = {}
        for fee in (1.04,1.24):
            if fee>1.04:
                totals = lab.real_fees(.20,list(set(A.P.CURRENT_PLAN)|{"RS","DT"}))
            paths = {}
            for mode,t in ledgers.items():
                w,r = candidate_paths(lab.g,t,fee,known_closed)
                paths[mode] = (w[lab.tr],r[lab.tr])
                lab.W[mode],lab.C[mode] = paths[mode][0],paths[mode][1][:,-1]
                del w,r
            if fee==1.04:
                overlap(lab,eligible)
                minute_overlap(lab,args.scratch,ledgers,eligible,known_closed)
            a,b = funded(lab,fb,F50,F150,fee,eligible)
            fr += a
            fd += b
            pd.DataFrame(fr).to_csv(OUT/"funded_summary.csv",index=False)
            pd.DataFrame(fd).to_csv(OUT/"funded_paired_differences.csv",index=False)
            a,b = evaluation(lab,args.scratch,fee,paths,eligible,args.prereg)
            er += a
            ed += b
            pd.DataFrame(er).to_csv(OUT/"evaluation_summary.csv",index=False)
            pd.DataFrame(ed).to_csv(OUT/"evaluation_paired_differences.csv",index=False)
    A.dump(OUT/"reproduction.json",dict(preregistration=args.prereg,plan_path=args.plan_path,
        pre_return_calendar_clarification=dict(commit=CALENDAR_COMMIT,
            sha256=A.file_sha(ROOT/"agents/codex/inputs/r2vault/calendar_metadata.md")),
        current_context=CONTEXT,reused_source_pin=A.PIN,reused_baseline_sha256=provenance["expanded_cache_sha256"],
        current_context_inventory_sha256=A.file_sha(INVENTORY),replay_inputs=inputs,
        scripts={p:A.file_sha(ROOT/"analysis"/p) for p in (Path(__file__).name,"codex_anson_accounts.py","codex_anson_plan.py","codex_ob_v2_accounts.py","codex_or_pullback_exposure.py")},
        models=list(MODES),unique_allocations={"50K":8,"150K":10},fees=[1.04,1.24],
        funded=dict(histories=1000,horizons=[250,500],circular_block=20,seeds=[1,2,3,4],
                    cohorts=list(COHORTS),expected_production_parity_records=360),
        evaluation=dict(real_full_windows=21,CI_block=20,CI_resamples=5000,
                        cohort_rule="entire21session window must lie inside the cohort; date[start+20] precedes its exclusive end",
                        tie_policy={"50K":"pass first","150K":"breach first"}),
        candidate_cost_timing="RTfee and0.50entry slip reserved from entry; exit target0,stop/market0.50",
        sensitivity_extra_fee_totals=totals,seconds=time.monotonic()-started,
        limits=A.P.BASELINE_LIMITS+[
            "The prior50Kprepared cache has a small unresolved difference from the published funded reference.",
            "150Kfunded fractional full-size bases precede cushion rounding; evaluation risk sizes floor after dollar scaling.",
            "Missing-day exclusions are shared; funded block adjacency changes and omitted stress dates remain a limitation.",
            "Minute boundary marks rely on the replay's declared intraminute path rather than verified tick order.",
            "Candidate marks stale at prior observed Close during verified closures; inherited baseline portfolio.paths missing-price substitutions are preserved and audited by position ledger.",
            "Closed daily P&L correlation does not establish protection before an account breach."]))
    print(f"completed {time.monotonic()-started:.1f}s",flush=True)


if __name__=="__main__":
    main()
