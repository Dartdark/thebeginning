# Mined index: what has already been tested (auto-built from TIER_LIST.md by `tools/build_mined_index.py`)

Stage-0 check (S_RANK_PROGRAM.md): before proposing an idea, find its family and market here, then read the full
TIER_LIST row (search the item name) and its script / output. Also grep HANDOFF.md, NEW_CHAT_BRIEF.md and
analysis/outputs/ for the mechanism. Tiers: A/B work, C weak, D below costs, F fails. Markets '-' = not named in the row,
almost always NQ (the repo's default market). Rebuild after new TIER_LIST rows.

324 items. Families by count: Close / auction / settlement flows 51, Options / dealer flow / volatility products 38, Mean reversion / fades 34, Overnight / session handoffs 33, Opening range / breakouts 31, Other 31, Calendar / rebalancing 26, Momentum / trend 24, News / scheduled releases 19, Order flow / microstructure 17, ML / signal search / filters / sizing 12, Cross-asset / pairs / relative value 8

## Options / dealer flow / volatility products (38)

| Tier | Item | Markets | Where |
|---|---|---|---|
| A | Expiration Open Short | - | analysis/option_income_etf_test.py |
| A | Overnight TickRSV / VIX | NQ, YM | analysis/overnight_tick_bench.py, analysis/overnight_tick_mc_confirm.py |
| B | ONB skips the day after negative GEX | - |  |
| C | DriftPullBack v3 | NQ | analysis/drift_pullback_v3_test.py, checks/candidates/drift_pullback_v3/ |
| C | EOS in calm markets | NQ, ES, YM | analysis/s_rank_misc_round2_test.py |
| C | Late-Day Flow sized by the 0DTE gamma flip at 14:00 | - |  |
| C | VIX term-structure sleeve | ES | analysis/vix_sleeve_test.py, checks/candidates/vix_sleeve/ |
| D | 0DTE NDX gamma regime from The Bridge | NQ |  |
| D | Day after triple witching, long | - |  |
| D | Gamma last-30 trade | - |  |
| D | Gold | GC |  |
| D | Overnight Drift GEX filter | - |  |
| D | VIX regime size tilt | - |  |
| D | YZ ORB Volatility Filtered, ES + GC | ES, GC | analysis/orb_vix_test.py, checks/candidates/orb_vix/ |
| F | 0DTE gamma and volatility (Paper/book) | - |  |
| F | 0DTE Index Options and Market Volatility (Paper/book) | - |  |
| F | 0DTE strike pin | - |  |
| F | 0DTE trading rules (Paper/book) | - |  |
| F | CL forced flows | YM, CL |  |
| F | Do S&P 500 Options Increase Market Volatility? Evidence from 0DTEs | ES | analysis/papers_2025_tests.py |
| F | Gamma flip cross breakout | NQ |  |
| F | Gamma regime follow / fade | - |  |
| F | Gamma-conditioned end-of-day momentum | NQ, ES |  |
| F | Implied volatility as the volatility unit | - | analysis/implied_vol_test.py, analysis/onb_vxn_sizing_test.py |
| F | Index rebalance days, buyback blackout, VIX-expiration Wednesday | - |  |
| F | Mega-cap earnings intraday shape on NQ | NQ | analysis/megacap_earnings_intraday_test.py |
| F | NDX 0DTE open interest by strike | NQ | analysis/gex_oi_pin_test.py |
| F | Option-income | NQ, YM |  |
| F | Price-pattern direction search | NQ, ES, FX |  |
| F | Regime gauges as sizing rules (Paper/book) | - | analysis/regime_gauges_test.py |
| F | S-rank round 1 failures | NQ, ES, YM, GC, CL, BTC | analysis/s_rank_<symbol>_round1_test.py |
| F | S-rank round 2 failures | NQ, ES, YM, GC, BTC | analysis/s_rank_gap_round2_test.py, analysis/s_rank_misc_round2_test.py |
| F | SPX / SPXW option open interest → next ES session | ES | analysis/spx_gex_sample_test.py |
| F | The Bridge's exported indicators as filters on the current plan | - | analysis/bridge_filter_scan.py, analysis/onb_delta_bench.py |
| F | The Bridge's indicators, round 2 | - | analysis/bridge_filter_scan2.py, analysis/bridge_gamma_ldf_check.py |
| F | Trading VIX Futures under Mean Reversion with Regime Switching (Paper/book) | - |  |
| F | VIX-ETP end-of-day rebalancing | - | analysis/vix_etp_eod_test.py |
| F | Weekly | NQ |  |

## News / scheduled releases (19)

| Tier | Item | Markets | Where |
|---|---|---|---|
| B | ES versions of the plan's forced flows | ES |  |
| B | NFP Fade | - |  |
| C | Bundle of the three edges | - |  |
| C | The Bridge's COT Dealer Rank, weekly hold | - |  |
| D | Fade NQ's 7:30–7:45 reaction on non-NFP data days | NQ |  |
| D | FOMC | NQ, ES | analysis/anti_papers_1018_test.py |
| D | FOMC statement reaction | - |  |
| D | Release fade | - |  |
| D | Treasury auction price pressure (Paper/book) | GC, ZN, FX | analysis/treasury_auction_test.py |
| F | 9:00 CT releases and non-payroll 7:30 releases | - |  |
| F | Antigravity's paper screen, batch 2026_10_18 (Paper/book) | YM, ZN | agents/tasks/TASK_PAPER_SCREEN.md, analysis/anti_papers_1018_test.py |
| F | Antigravity's per-symbol 'proven structural edges' | NQ, ES, YM, GC, CL, ZN | analysis/anti_symbol_edges_test.py |
| F | CL forced flows from the user's AI chat | YM, CL | analysis/cl_forced_flows_round2_test.py |
| F | Codex | NQ | agents/codex/plans/fomc_minutes_screen.md, analysis/codex_fomc_minutes_screen.py |
| F | Gold and bitcoin follow-ups after the CL fade joined the plan | GC, CL, BTC | analysis/gold_btc_next_test.py |
| F | Limit instead of market entries for the plan | ES | analysis/limit_entry_test.py |
| F | Markov regime transitions | NQ, ES, YM, GC, CL, BTC | analysis/regime_markov_test.py |
| F | NFP Fade replacement hunt | - | analysis/nfp_replacement_test.py |
| F | Pre-FOMC drift (Paper/book) | - |  |

## Close / auction / settlement flows (51)

| Tier | Item | Markets | Where |
|---|---|---|---|
| A | Dual Thrust v4, NQ, Central-time build | NQ | analysis/dual_thrust_150k_test.py, analysis/dual_thrust_bench.py |
| A | Late-Day Flow | NQ |  |
| B | BB_MRM Bollinger mean reversion at the open | NQ | analysis/bb_mrm_bench.py, analysis/bb_mrm_test.py |
| B | Combine add-ons | NQ |  |
| B | ES MOC auction follow | ES | analysis/s_rank_es_round1_test.py, analysis/s_rank_moc_round2_test.py |
| B | FVB 'First Valid Breakout', NQ | NQ | analysis/fvb_bench.py, analysis/fvb_test.py |
| B | PAPERTREND v2, NQ | NQ, YM | analysis/papertrend_bench.py, analysis/papertrend_test.py |
| B | S03 noise-area intraday momentum v2 | NQ | agents/codex/results/s03_v2.md |
| B | The Bridge's Overnight Bias ORB | - |  |
| C | IntradayMomentum_Signal_EN, NQ 30-min | NQ, ES | analysis/intraday_momentum_30m_test.py |
| C | MAGNET18 | NQ | analysis/magnet18_bench.py, analysis/magnet18_test.py |
| C | MOC imbalance follow | - |  |
| C | Morning direction at the European close | FX | analysis/moc_london_close_test.py |
| C | Open-breakout pullback on 15-min bars | - |  |
| C | VaultBreak 'CircuitBreaker ApexLimit GVReader' + DailyATR GVWriter | - | analysis/vb_gv_limit_bench.py, analysis/vb_gv_limit_test.py |
| C | VWAP Drift Continuation, MNQ | NQ | analysis/vwap_drift_test.py, checks/candidates/vwap_drift/ |
| C | YM MOC auction follow | YM |  |
| C | YM post-settlement fade | YM |  |
| D | Antigravity's Vault Break Combined | NQ | agents/results/VB_COMBINED_REVIEW.md, analysis/anti_vb_combined_test.py |
| D | Last-30-minute momentum (Paper/book) | - |  |
| D | Late-Day Flow longs only when the last 30 minutes of order-flow delta agree | - |  |
| D | MNQ portfolio 'v4 + N-Day Long' | NQ | analysis/mnq_v4_nday_test.py |
| D | Month-end close momentum | - |  |
| D | ORPullback | NQ | agents/codex/results/or_pullback_portfolio.md |
| D | Pension / balanced-fund rebalancing conditional on stocks vs bonds | ES, ZN | analysis/forced_flows_round5_test.py |
| D | Post-settlement reversal | - |  |
| D | Post-settlement reversal, cheaper execution | - | analysis/post_settlement_test.py, checks/candidates/post_settlement/PREREG.md |
| F | 101 Formulaic Alphas (Paper/book) | NQ, ES |  |
| F | 20-day regime filter | - | analysis/regime20_bench.py, analysis/regime20_filter_test.py |
| F | Antigravity's 'where real alpha comes from' list | ES, FX | analysis/anti_forced_flow_ideas_test.py |
| F | Antigravity's ESEuroCloseTrend | ES, FX | agents/results/PHASE2_VERDICT.md, analysis/es_euro_close_check.py |
| F | Antigravity's NQBreakoutATR | NQ | analysis/anti_nq_breakout_atr_test.py |
| F | Antigravity's NQRelWeaknessShort | NQ, ES | analysis/anti_nq_rel_weakness_short_audit.py, analysis/anti_nq_rel_weakness_short_test.py |
| F | Bitcoin forced flows | BTC |  |
| F | Bollinger Band reversals | - |  |
| F | Building blocks Step 1 | NQ, ES | analysis/blocks_step1_test.py |
| F | Codex | NQ, FX | agents/codex/plans/ldf_flow_sizing.md |
| F | Codex | FX | agents/codex/plans/fx_fix_reversal.md, analysis/codex_fx_fix_reversal.py |
| F | Grimes, *The Art and Science of Technical Analysis*, Antigravity's book reading (Paper/book) | ES | analysis/grimes_failure_test.py |
| F | Intraday market-wide ups / downs (Paper/book) | YM | analysis/intraday_updown_test.py |
| F | Intraday trend seasonality | ES | analysis/late_day_trend_test.py |
| F | Leveraged-ETF / closing push reverses overnight | - | analysis/letf_overnight_reversal_test.py |
| F | Market Intraday Momentum (Paper/book) | - |  |
| F | Meta-labeling Late-Day Flow | - | analysis/ldf_meta_label_test.py |
| F | MOC auction follow filtered by order flow | NQ | analysis/moc_orderflow_test.py |
| F | Offset Donchian breakout + MA5 / MA50 | GC | analysis/donchian_mavs_test.py, checks/candidates/donchian_mavs/ |
| F | Overnight-Intraday Reversal Everywhere (Paper/book) | - | analysis/co_oc_reversal_test.py |
| F | Price gaps (Paper/book) | YM, FX | analysis/fx_gap_fade_test.py |
| F | ReversionCheck | FX | analysis/reversion_check_test.py |
| F | The Bridge's VWAP Fade | - |  |
| F | Who Trades at the Close? | ES | analysis/papers_2025_tests.py |

## Calendar / rebalancing (26)

| Tier | Item | Markets | Where |
|---|---|---|---|
| A | CL Sunday up-gap fade | CL | analysis/cl_sunday_fade_confirm.py, funded_strategies/CL_Sunday_Gap_Fade.txt |
| A | Monday Long | - |  |
| A | The Bridge's Monday Long NQ | NQ |  |
| B | Kusho v9 / FAR | NQ, YM | analysis/kusho_test.py, checks/candidates/kusho/ |
| C | BTC CME weekend-gap continuation | BTC |  |
| C | NQ Sunday reopen first-minute push | NQ | analysis/sunday_reopen_test.py |
| C | Overnight Drift | - |  |
| C | Turn of the month | - |  |
| C | VaultBreak v8 | - |  |
| D | CL holiday-reopen up-gap fade | CL |  |
| D | ES 'Core 3' | ES | analysis/es_core3_test.py |
| D | Month-end rebalancing fade | - |  |
| D | MSCI quarterly review closes | - |  |
| D | NQ after mega-cap earnings | NQ | analysis/megacap_earnings_nq_test.py |
| D | Time clusters in the plans' trades | - |  |
| D | Wednesday overnight long | - |  |
| F | Bitcoin seasonality + trend / bounce | BTC | analysis/btc_seasonality_trend_test.py |
| F | CL round 3 | CL | analysis/cl_round3_test.py |
| F | Forced-flow round 3 | - |  |
| F | Index rebalancing next-morning reversal | NQ, ES | analysis/index_rebalance_reversal_test.py |
| F | Intraday Bias Check + Time Rotation Strategy | NQ, ES, YM | analysis/time_rotation_test.py |
| F | JPMorgan Hedged Equity collar reset | - |  |
| F | Month-end Treasury index extension on ZN | ZN | analysis/zn_month_end_test.py |
| F | Nasdaq-100 / S&P quarterly rebalance closes | NQ, ES |  |
| F | Nasdaq-100 special rebalance | NQ |  |
| F | Pre-holiday / post-holiday / mid-month pay days | - |  |

## Overnight / session handoffs (33)

| Tier | Item | Markets | Where |
|---|---|---|---|
| S | Overnight Bias ML | - |  |
| A | Overnight Bias | - | agents/codex/results/break_vb_onb.md |
| A | Twin Continuation | NQ | analysis/twin_apex_test.py, analysis/twin_continuation_test.py |
| B | OB v2 | NQ | agents/codex/results/REVIEW_c03_kusho_obv2.md, agents/codex/results/ob_v2_plan_test.md |
| B | S47 v2, Europe-Open Impulse | NQ, FX | analysis/s47_test.py, checks/candidates/s47_v2/ |
| B | T_ONESIDE | NQ | analysis/t_oneside_bench.py, analysis/t_oneside_test.py |
| C | Gold Asian-range breakout on gold | GC |  |
| C | Overnight Bias ML | - | analysis/combine_swap_test.py |
| C | Overnight-range breakout | - |  |
| C | OvernightAnomaly v4.1 | NQ, YM | analysis/overnight_anomaly_bench.py, analysis/overnight_anomaly_test.py |
| D | BTC Overnight Bias port | BTC |  |
| D | Gap Fill | - |  |
| D | MNQ_Portfolio_SharedCap_v2 | NQ | analysis/mnq_sharedcap_test.py, checks/candidates/mnq_sharedcap/ |
| D | NQ–YM relative value | NQ, YM |  |
| D | Overnight round for a personal account | - | analysis/overnight_round.py |
| D | RSI(2) dip-buying held overnight | NQ |  |
| D | Vault Break sized up after Overnight Bias ML has gone long the same day | - | analysis/plan_agreement_test.py, analysis/vb_after_onb_bench.py |
| D | Yes/no | - |  |
| F | Asian and European opens, followed | FX | analysis/forced_groups_round4_test.py |
| F | BTC Reopen MR V4 | BTC | analysis/btc_reopen_test.py, checks/candidates/btc_reopen_mr_v4/ |
| F | Codex | ES | agents/codex/plans/davey_keltner_screen.md, analysis/codex_davey_keltner.py |
| F | Cross-asset overnight signals | NQ, GC, CL, BTC |  |
| F | ES versions of VB / ONB / OND | ES |  |
| F | Fading headline jumps | - |  |
| F | Gold Asian-range breakout ported to NQ / ES | NQ, ES, GC |  |
| F | Gold Breakout 15M | NQ, GC |  |
| F | Gold vs rates and the dollar | YM, GC, ZN, FX | analysis/gold_rates_dollar_test.py |
| F | Golden Cross 50 / 200 SMA on gold | GC | analysis/gc_golden_cross_test.py |
| F | Market Sentiment and an Overnight Anomaly (Paper/book) | - | analysis/ond_sentiment_filter_test.py, analysis/overnight_sentiment_vote_test.py |
| F | Meta-labeling Vault Break | - | analysis/vb_meta_label_test.py |
| F | Overnight range vs RTH open position | NQ | analysis/overnight_midpoint_test.py |
| F | Overnight VWAP fades | - |  |
| F | Tokyo open reversal | NQ | analysis/tokyo_open_stage1.py, checks/ideas/tokyo_open.md |

## Opening range / breakouts (31)

| Tier | Item | Markets | Where |
|---|---|---|---|
| A | FC 2B, Flow-Confirmed Opening Drive | NQ | analysis/fc_2b_bench.py, analysis/fc_2b_mc_confirm.py |
| A | Vault Break | - | agents/codex/results/vb_parity_stress.md |
| B | Crabel Stretch Breakout | - |  |
| B | High-win-rate search round 3 | NQ | analysis/high_winrate_test.py |
| B | Kusho 'Finished Auction Retest' v0.9 | NQ | analysis/kusho_far_pdf_test.py, checks/candidates/kusho_far/ |
| B | Single-print day filter on Vault Break | NQ | analysis/single_print_test.py, checks/candidates/vb_single_print_filter/verdict.md |
| C | 60-min breakout, longs only, entries 9:00–14:00, flat 15:00 | - |  |
| C | Antigravity's NQIBBreakout | NQ, YM | analysis/anti_nq_ib_breakout_test.py |
| C | Gold Breakout 15M | GC | analysis/gold_breakout_15m_bench.py, analysis/gold_breakout_15m_test.py |
| C | NQDB2 / DriftBreak v2 | - | agents/codex/results/nqdb2_test.md |
| C | Opening Drive | - |  |
| C | R2Vault | NQ | agents/codex/results/r2vault.md |
| C | Vault Break sized by NR7 day | - | analysis/kaufman_day_filters_test.py, analysis/vb_nr7_bench.py |
| D | Donchian(96) breakout + Larry Williams Large Trade Index > / < 50 + volume above average,  | - | analysis/donchian_lwti_volfilter_test.py |
| D | Fabio Valentini ORB with a delta filter | NQ | analysis/fabio_orb_test.py |
| D | Improvements to Intraday Momentum Strategies (Paper/book) | - |  |
| D | Midday Range Breakout | NQ | analysis/midday_breakout_test.py |
| D | Open-breakout pullback | - |  |
| D | ORB + opening-volume filter (Paper/book) | - |  |
| D | ORB + Shock Reversal | NQ | analysis/shock_reversal_test.py, checks/candidates/shock_reversal/ |
| D | QQQ 5-minute ORB (Paper/book) | NQ |  |
| D | Supply disruptions and trend-following in crude oil (Paper/book) | YM, CL | analysis/oil_supply_windows_test.py |
| D | Timeframe ensemble | NQ |  |
| F | 60-min 40-bar breakout + 200 SMA, 2x ATR stop | - |  |
| F | Codex | GC | agents/codex/plans/xau_st_break_free_screen.md, analysis/codex_xau_st_break_free.py |
| F | Hybrid channel breakout + MA retrace + volume (Paper/book) | - |  |
| F | Kaufman, *Trading Systems and Methods* (Paper/book) | - |  |
| F | NR7 family test | NQ, YM, GC, CL | analysis/nr7_family_test.py |
| F | Open-breakout pullback on 1-min bars | - |  |
| F | ORB -> VWAP Fade v1.1, ES | ES | analysis/orb_vwap_fade_test.py, checks/candidates/orb_vwap_fade/ |
| F | VWAP pullback after a 30-min opening-range break | - |  |

## Order flow / microstructure (17)

| Tier | Item | Markets | Where |
|---|---|---|---|
| D | Do Large Trades Predict Price? | - | analysis/whale_balanced_book_test.py |
| F | Antigravity book readings, batch 2026-10-18 (Paper/book) | - |  |
| F | Beta from A to Z (Paper/book) | NQ, ES, YM |  |
| F | Big prints | - |  |
| F | Carver, *Systematic Trading* (Paper/book) | - |  |
| F | Chan, *Algorithmic Trading* (Paper/book) | NQ, ES | analysis/chan_book_ideas_test.py |
| F | Hilpisch, *Python for Algorithmic Trading* (Paper/book) | - |  |
| F | López de Prado, *Advances in Financial Machine Learning* (Paper/book) | - | agents/results/BOOK_PRADO_AFML_REVIEW.md |
| F | Mean-reversion Colab notebook (Paper/book) | - |  |
| F | Opening order flow | - |  |
| F | Order-flow prediction | - |  |
| F | Pedersen, *Efficiently Inefficient* and Chan, *Machine Trading* (Paper/book) | - | agents/results/BOOKS_PEDERSEN_CHANML_REVIEW.md, analysis/zn_release_momentum_test.py |
| F | Prop-firm economics papers (Paper/book) | NQ, YM | analysis/random_strategy_bench.py |
| F | Stock Market Trading Volume (Paper/book) | - |  |
| F | The Bridge's Large Trade Predictability | - |  |
| F | The Bridge's Liquidity Predictability | - |  |
| F | The plan's strategies on CL and GC | GC, CL |  |

## Mean reversion / fades (34)

| Tier | Item | Markets | Where |
|---|---|---|---|
| B | DriftPullback v2.1 | - |  |
| B | Morning Momentum, tight stop | NQ | analysis/mo_pullback_test.py, analysis/mo_tight_bench.py |
| B | S30, cash-session IBS reversal | NQ, ES | analysis/s30_ibs_test.py, checks/candidates/s30_ibs/ |
| C | 'Beat the Market' SPY intraday momentum, the user's EasyLanguage replication (Paper/book) | NQ, ES | analysis/beat_the_market_es_test.py, checks/candidates/beat_the_market_spy/ |
| C | Asymmetric reversal (Paper/book) | YM |  |
| C | GC_COMBO v2 | GC, CL | analysis/gc_combo_bench.py, analysis/gc_combo_test.py |
| D | AlphaFlow ETH 30m short-only pullback | BTC | analysis/alphaflow_eth_test.py, analysis/c/lorentzian_ann.c |
| D | CTA trend-signal flip, fade next day | - |  |
| D | Fade yesterday's session move | NQ, ES |  |
| D | Gold 3-Candle Reversal H4, long only | GC | analysis/gold_h4_reversal_bench.py, analysis/gold_h4_reversal_test.py |
| D | Noise-band intraday momentum on NQ (Paper/book) | NQ | analysis/noise_band_bench.py, analysis/noise_band_chuk_test.py |
| D | Quiet-day midday fade | - |  |
| D | VWAP Pullback + ADX gate | - | analysis/vwap_adx_fixed_exits_test.py |
| D | VWAP trend, slow version (Paper/book) | - |  |
| D | YM–ES prior-day rotation reversal | ES, YM |  |
| F | 20/50 EMA zone pullback, 10-min, stop 30 / target 65 points | - |  |
| F | A Tale of One Day (Paper/book) | NQ, ES, YM | analysis/morning_afternoon_test.py |
| F | Antigravity's NarangBlackBox | ES | agents/results/NARANG_BLACKBOX_VERDICT.md |
| F | Antigravity's NQIntradayMR | - |  |
| F | Bhatti gold VWAP-EMA pullback (Paper/book) | GC |  |
| F | BTC short-only 'fade the retail euphoria' | BTC | analysis/btc_retail_fade_test.py |
| F | Codex | NQ, GC, BTC | agents/codex/plans/rsi_bollinger_screen.md, analysis/codex_rsi_bollinger_screen.py |
| F | CoT reversal index | NQ, ES | analysis/cot_reversal_index_test.py |
| F | ES mean reversion | NQ, ES | analysis/es_mean_reversion_premise.py, analysis/es_mean_reversion_test.py |
| F | Futures short-term reversal | - |  |
| F | Glow Ribbon Flip | - |  |
| F | Golden Cross 50 / 200 SMA | NQ, GC | analysis/jesse/strategies/GoldenCross |
| F | IBS, pivot points | - |  |
| F | Multi-day pullback | - |  |
| F | Ornstein-Uhlenbeck regime filter for mean reversion | - | analysis/ou_regime_test.py |
| F | Round numbers | - |  |
| F | RSI + EMA + rolling VWAP on QQQ | NQ |  |
| F | VWAP always-in, 1-minute (Paper/book) | - |  |
| F | VWAP Pullback ADX | - |  |

## Momentum / trend (24)

| Tier | Item | Markets | Where |
|---|---|---|---|
| B | Noise-area momentum, long only | - |  |
| B | Twin Continuation on an Apex 150K account | YM | analysis/twin_150k_test.py |
| C | Headline Shock Follow | - |  |
| D | Anson intraday momentum / range | NQ | agents/codex/results/anson_momentum.md |
| D | Antigravity's NQESCrossFlow | NQ, ES | analysis/anti_nq_es_crossflow_test.py |
| D | BTC Momentum "September Winner" | YM, BTC |  |
| D | Multi-timeframe trend filter on the plan's strategies | - |  |
| D | NQ–ES spread | NQ, ES |  |
| F | A confirmed beta-harvest cannot pass a prop-firm challenge without regime foreknowledge (Paper/book) | NQ, GC | analysis/combine_driftless_test.py |
| F | A review of the Post-Earnings-Announcement Drift (Paper/book) | - |  |
| F | Abnormal trading volume (Paper/book) | - |  |
| F | Building blocks Step 1b | NQ, ES, YM, GC, CL, ZN, FX | analysis/blocks_step1b_daily_test.py |
| F | Codex | GC | agents/codex/plans/sge_delivery_screen.md, analysis/codex_sge_delivery_screen.py |
| F | Commodity storage/momentum (Paper/book) | - |  |
| F | Cross-sectional momentum (Paper/book) | - | analysis/xsec_momentum_test.py |
| F | Fact, Fiction and Momentum Investing (Paper/book) | - |  |
| F | Following CTA flows | - |  |
| F | Gold when NQ <= its 200-day average | NQ, GC | analysis/gold_when_nq_below_200_test.py |
| F | Momentum Turning Points (Paper/book) | - |  |
| F | Morning Momentum | NQ | analysis/twin_mo_risk_bench.py |
| F | Plan-combination ideas | YM | analysis/plan_agreement_test.py |
| F | Post Earnings Announcement Drift (Paper/book) | - |  |
| F | Structural Limits of OHLCV-Based Intraday Momentum Signals in MNQ (Paper/book) | NQ | analysis/london_signal_b_test.py |
| F | Twin Continuation on other markets | ES, YM, GC, CL | analysis/twin_family_test.py |

## Cross-asset / pairs / relative value (8)

| Tier | Item | Markets | Where |
|---|---|---|---|
| B | Relative Strength NQ / ES | NQ, ES | analysis/relative_strength_bench.py, analysis/relative_strength_mc_confirm.py |
| C | Antigravity's NQAlignedWeaknessShort | NQ, ES, YM | analysis/anti_aws_mc_confirm.py, analysis/anti_nq_aligned_weakness_short_test.py |
| F | Cross-asset lead-lag and morning decoupling | NQ, ES, YM, GC, CL, BTC |  |
| F | GIO Valuation Tool 2.0 | NQ, ZN | analysis/gio_valuation_test.py |
| F | Quantitative Spread Trading on Crude Oil and Refined Products Markets (Paper/book) | CL |  |
| F | Session Efficiency Forecast | - | analysis/session_efficiency_bench.py, analysis/session_efficiency_check.py |
| F | Signature Decomposition Method Applying to Pair Trading (Paper/book) | - | analysis/signature_pairs_test.py |
| F | YM's own events | YM, ZN | analysis/ym_dow_events_test.py |

## ML / signal search / filters / sizing (12)

| Tier | Item | Markets | Where |
|---|---|---|---|
| A | Cushion sizing | - |  |
| D | Combine state levers | - | analysis/combine_levers_test.py |
| D | Scaling size up as a funded account grows | - | analysis/payout_scaling_test.py |
| F | 'Bench a strategy in heavy drawdown; failures and passes cluster' | YM | analysis/bench_in_dd_test.py |
| F | Brooks price-action bot v201 | NQ, YM | analysis/brooks_bot_test.py, checks/candidates/brooks_bot/ |
| F | CFTC positioning | - |  |
| F | From Funded to Paid (Paper/book) | - | analysis/funded_to_paid_check.py |
| F | MaxAI (Paper/book) | NQ |  |
| F | MinervaScore (Paper/book) | - | analysis/checker.py |
| F | MNQ ADX + Accelerator Oscillator, 1% risk | NQ | analysis/adx_ac_test.py, checks/candidates/adx_ac/ |
| F | The Bridge's COT Dealer Rank as an Apex day trade | - |  |
| F | Volatility targeting | NQ |  |

## Other (31)

| Tier | Item | Markets | Where |
|---|---|---|---|
| A | The plan on Apex 150K accounts | - | analysis/apex_paths_test.py, analysis/plan_150k_test.py |
| B | Bootstrap + permutation | - |  |
| B | r/algotrading post | - |  |
| B | Vol-Control Sell Flow | ES |  |
| C | Building blocks Step 1 survivor | NQ, ES | analysis/blocks.py, analysis/blocks_step1_test.py |
| C | C03 | NQ | analysis/kusho_test.py |
| D | Abnormal volume on gold | NQ, GC | analysis/abnormal_volume_gc_test.py |
| D | CL | CL |  |
| D | Daily profit cap vs the 50% consistency rule | - | analysis/profit_cap_test.py |
| D | DIX-high long | - |  |
| D | Extreme Money Flow | NQ | analysis/emf_cmf_test.py |
| D | Roll-week short | - |  |
| F | 50 Years in PEAD Research (Paper/book) | - |  |
| F | Announcement-day premium (Paper/book) | - |  |
| F | Antigravity Phase 2 | - | agents/results/PHASE2_VERDICT.md, analysis/antigravity_phase2_bench.py |
| F | Contrarian VRP ETF strategy (Paper/book) | - |  |
| F | Fading big intraday moves | - |  |
| F | Fast alphas as an execution overlay | - |  |
| F | Gold first-notice-day long liquidation | GC | analysis/forced_flows_round5_test.py |
| F | Implied equity term structure (Paper/book) | - |  |
| F | Index MA agreement for ES | NQ, ES, YM |  |
| F | Netting script | - | analysis/plan_overlap_check.py |
| F | SPY/TQQQ "arbitrage" (Paper/book) | NQ, ES |  |
| F | Statistical Arbitrage in the U.S. Equities Market (Paper/book) | - |  |
| F | Technical rules and FX intervention (Paper/book) | FX |  |
| F | The Golden Dilemma (Paper/book) | GC |  |
| F | The plan's strategies on YM | YM |  |
| F | The Power of Price Action Reading (Paper/book) | - |  |
| F | The Probability of Backtest Overfitting (Paper/book) | - | analysis/metrics.py, analysis/pbo_audit.py |
| F | What Is Alpha (Paper/book) | - | analysis/plan_alpha_test.py |
| F | Window trades | YM |  |
