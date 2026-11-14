import sys, os
def main():
    os.chdir(sys.argv[1]); sys.path.insert(0, sys.argv[1])
    from pathlib import Path
    import config
    config.CFG.csv_path = Path("data/GC_1min_adj.csv")
    config.CFG.spread_price = 0.0
    config.CFG.slippage_price = 0.4625     # per side: 1 GC tick (0.10) + half of $7.25 commission (0.3625 pts)
    config.CFG.commission_per_trade = 0.0
    import train_ppo
    train_ppo.train_sliding_walk_forward(n_envs=int(sys.argv[2]) if len(sys.argv) > 2 else 8)
if __name__ == "__main__":
    main()
