"""After training: roll each fold's best model over its TEST window; per-trade R, longs / shorts, by fold; vs always-long."""
import sys, os
def main():
    os.chdir(sys.argv[1]); sys.path.insert(0, sys.argv[1])
    import numpy as np, pandas as pd
    import config, train_ppo as T
    from data_loader import make_sliding_folds
    CFG = config.CFG
    m1, feat, fc = T._load_decision_features()
    folds = make_sliding_folds(feat, train_years=CFG.sliding_train_years, val_months=CFG.sliding_val_months, test_months=CFG.sliding_test_months,
                               step_months=CFG.sliding_step_months, embargo_bars=CFG.split_embargo_bars)
    allt = []
    for k, (tr, va, te) in enumerate(folds, start=1):
        model, vp = T._load_fold_model(f"models/sliding/fold_{k}")
        eq, t, rep = T._rollout_on_split(model, vp, m1, fc, te)
        t = t.assign(fold=k); allt.append(t); r = t.r_mult
        print(f"fold {k} {te.index.min().date()}->{te.index.max().date()}: n {len(r)}, sum {r.sum():+.1f}R, longs {(t.direction==1).sum()} {r[t.direction==1].sum():+.1f}R, shorts {(t.direction==-1).sum()} {r[t.direction==-1].sum():+.1f}R")
    t = pd.concat(allt, ignore_index=True); t.to_csv("ppo_test_trades.csv", index=False); r = t.r_mult
    print(f"ALL TEST: n {len(r)}, sum {r.sum():+.1f}R, mean {r.mean():+.3f}R, t {r.mean() / r.std(ddof=1) * np.sqrt(len(r)):+.2f}, win {np.mean(r>0):.0%}; "
          f"longs {(t.direction==1).sum()} {r[t.direction==1].sum():+.1f}R (t {r[t.direction==1].mean() / r[t.direction==1].std(ddof=1) * np.sqrt((t.direction==1).sum()):+.2f}); "
          f"shorts {(t.direction==-1).sum()} {r[t.direction==-1].sum():+.1f}R; time long share {t[t.direction==1].bars_in_trade.sum() / max(t.bars_in_trade.sum(), 1):.0%}")
if __name__ == "__main__":
    main()
