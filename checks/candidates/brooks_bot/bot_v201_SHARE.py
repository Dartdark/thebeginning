"""
Index Trading Bot v197 (score_signal logic inverted per Analyzer 7)
====================================================================
v167 -- direct response to Analyzer 7 findings on 361 resolved real-risk trades.

THE BIG FINDING (z=-5.06, smoking-gun strength):
  When score_signal() awarded "+1 entry away from key levels (clean)":
    WR was 43.1% on n=174 trades.
  When score_signal() did NOT award that point (= trade IS near a key level):
    WR was 69.5% on n=187 trades.

  When trades had NEITHER anti-signal firing (key_levels OR 15m_structure):
    WR was 73.8%, avg_R was +0.475 (vs +0.136 baseline).

The intuition was wrong. Brooks setups are REACTIONS at key levels -- that's
the whole point. A double_bottom at the prior day's low is the textbook
play. A double_bottom in the middle of nowhere is noise pretending to be
a setup. The bot was rewarding the noisy version and penalizing the real one.

v167 changes:

  1. score_signal() Factor 7 INVERTED.
     Was: +1 when entry is AWAY from key levels.
     Now: +1 when entry IS AT a key level (within 0.2% tol).
     Statistical confidence: very high (z=-5.06 over 361 trades).

  2. score_signal() Factor 1 INVERTED.
     Was: +1 when 15m structure agrees with signal direction.
     Now: +1 when 15m is ranging OR opposes signal (counter-trend setups).
     Logic: counter-trend Brooks setups catch pullback exhaustion -- higher
     probability than late-trend continuation. Statistical confidence:
     suggestive (z=-1.69, n=361). If this hurts, revert just this factor.

  3. score_15m_structure and score_key_levels TEMPORARILY NaN'd.
     The ML model trained on the OLD meaning of these flags. With logic
     inverted in v167, old training data and new trades have opposite
     interpretations. NaN'd until 200+ trades accumulate under v167 logic,
     then re-enable in v168 with retrained model. The score_signal() function
     still uses them to compute the integer score -- just the ML model
     ignores them as features.

NOT changed (deferred):
  - risk_from_score: The score-WR inversion in Analyzer 6 may resolve once
    factors are corrected. If it persists, flatten in v168.
  - Noise factors (score_1h_direction, score_volatility, etc.): not hurting,
    not helping. Leave alone for now.

v166 carried forward:
  - atomic_write loud on persistent failure
  - get_candles caches None results
  - MIN_SCORE_GATE = 0 (no gate -- score will need re-validation post-inversion)

v165 / v164 / earlier -- all carried forward.
====================

  1. REGIME-CONDITIONAL SETUP GATE -- DATA-DRIVEN.
     The previous creator left REGIME_GATE_ACTIVE=False with a placeholder
     matrix waiting for trending_bear validation. v159 enables the gate and
     populates it from the actual ml_report25 Section 7+13 data:
       ranging:        + double_top (34.6%/419), 15m double_top, 15m trend_bar
       trending_bull:  + double_top (counter-trend trap)
       trending_bear:  baseline only (everything works here -- 55-67% WR cluster)
       volatile:       + wedge (24%/33), two_leg_pullback (14%/14)
     Block list = always-disabled set ∪ regime-specific extras. Setups can
     fire in any regime where they're not in the block list, then ML decides.

  2. REGIME STABILITY GATE.
     New regime_stable() helper requires the same regime to persist across
     3 consecutive 30s polls (= 90 seconds) before being treated as actionable.
     If unstable (just flipped), the most-conservative union of all regime
     blocks is applied. Catches whipsaw entries on bar that just broke a range.

  3. ACCOUNT-LEVEL CIRCUIT BREAKER.
     If 8 consecutive resolved real-risk trades lose, halt ALL trading until
     the next session (midnight UTC reset). Catches silent model breakage,
     regime shift past what the gate handles, or news/data corruption that
     the per-setup cooldown wouldn't catch. ~1.6% account drawdown trigger
     (well inside daily limit) but a clear behavioral signal that something
     systemic is wrong. The bot pauses itself rather than letting the daily
     loss limit do it the hard way.

v157 changes (carried forward):
  - 0.01-lot bug fix: outside_hours and cooldown paths skip when risk=0
  - Symbols restricted to US30 + US100 only
  - DISABLED_SETUPS expanded from 3 to 5 (added 5m trend_bar + 5m bar_reversal)
  - LEAKY_FEATURES expanded from 14 to 31 (caught 17 missed rolling-stat features)
  - Dynamic threshold uses active symbols only
  - Mon/Tue 0.8x size penalty

v156 ML overhaul (carried forward):
  - LEAKY feature isolation
  - Platt monotonicity gate
  - GBM capacity reduction
  - Aggressive feature pruning
  - Weight scheme simplified
  - Dropped noisy 2/3-day windows
  - Save gate: separation_improvement_pass

v155 sizing/strategy (carried forward):
  - EOD retrain heartbeat
  - Kelly bypass when n<50 OR wr in 40-60%
  - DIRECTION_LOCK
  - GER40 hard cap (kept as defensive code even though GER40 not traded)
  - _BLOCKED_HOURS = {0, 3, 14, 19, 21}
  - ML_MIN_ENTRY_PROB 0.40
====================
Symbols  : GER40.cash, US30.cash, US100.cash, UK100.cash

Strategies
----------
1. 15m main       -- overnight range + key levels          (1.0% base risk)
2. 7th candle     -- GER40@London, US30/US100@NY open      (1.0% base risk)
3. UK100 5m       -- first 5m candle, 20pt/26pt            (1.0% base risk)
4. Brooks 5m      -- 4 setups, unlimited trades per day    (adaptive risk)
5. Brooks 15m     -- same 4 setups on 15m                  (adaptive risk)

Coordinator (internal AI scoring)
----------------------------------
Every signal gets a confidence score before a trade is placed:
  +1  Setup signal detected
  +1  Brooks pattern on same symbol agrees with direction
  +1  Market structure (EMA, trend) agrees with direction
  +1  Time of day is optimal (not in dead zone)
Score 4 = 100% risk  |  Score 3 = 75%  |  Score 2 = 50%  |  Score 1 = 25%

Adaptive Learning
-----------------
Tracks rolling win rate per setup (last 20 trades).
- Win rate > 60% after 10+ trades  -> risk boosted 25%
- Win rate < 35% after 10+ trades  -> setup enters 2hr cooldown
- 3 consecutive losses on a setup  -> 2hr cooldown immediately
- Brooks risk auto-scales: 0.1% (cold) to 0.5% (hot)

Safety
------
- 1% risk per trade (strategies 1-3), adaptive for Brooks
- 4% daily loss limit
- 8% max total drawdown
- Scale-in at 1:1 for strategies 1-3 only (no scale-in on Brooks)
"""

import MetaTrader5 as mt5
import pandas as pd
import json
import os
import time
import logging
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, asdict
from typing import Optional

# ── CONFIG ────────────────────────────────────────────────────────────────────

SYMBOLS_MAIN  = ["US30", "USTEC"]   # v201: IC Markets EU names (was US30.cash / US100.cash). USTEC = Nasdaq-100. GER40/UK100 still blocked.
SYMBOL_UK100  = "UK100.cash"                  # kept defined for reference but NOT in ALL_SYMBOLS
ALL_SYMBOLS   = SYMBOLS_MAIN                   # v157: UK100 removed -- was -88 net trades

TF_15M = mt5.TIMEFRAME_M15
TF_5M  = mt5.TIMEFRAME_M5

LIVE_MODE = False  # DEMO - data collection
_EOD_ACTIVE = False  # global flag -- blocks ALL trading during EOD close

CHECK_INTERVAL      = 1
import random as _rnd  # hoisted -- was rebuilt per signal inside loop
# v155: ml_report25 shows hours 0, 14, 19, 21 all <44% WR over 100+ trades each.
# Hour 14 was removed in v152 -- adding back. Hour 0 is dead time. 19+21 unchanged.
_BLOCKED_HOURS = {0, 3, 14, 19, 21}

# v155+v157: Hard-disable setups proven to lose money over large samples.
# Format: "{strategy}|{setup_name}". Match against setup_key built in main loop.
# v155 source: ml_report25 Section 1 (>100 trades, all <40% WR)
# v157 source: handoff doc section 5 -- added 2 more setups based on Apr 30 EOD data:
#   brooks_5m|trend_bar      38.4% over 141 trades  (-32 trades net loss)
#   brooks_5m|bar_reversal   43.1% over 1664 trades (-230 trades net loss -- biggest bleed)
DISABLED_SETUPS = {
    "brooks_5m|double_top",      # 35.5% WR / 541 trades
    "brooks_15m|wedge",          # 33.1% WR / 142 trades
    "brooks_15m|bar_reversal",   # 32.3% WR / 161 trades
    "brooks_5m|trend_bar",       # v157: 38.4% WR / 141 trades
    "brooks_5m|bar_reversal",    # v157: 43.1% WR / 1664 trades -- largest single bleed
}

# v155: Force directional bias on setups with extreme long/short asymmetry.
# Source: ml_report25 Section 14.
#   climactic_reversal long=81%, short=26%  -> long-only
#   double_top short=38%, long=??           -> short-only (already convention)
#   range_fade short=80%                    -> short-only
DIRECTION_LOCK = {
    "climactic_reversal": "long",
    "double_top":         "short",
    "range_fade":         "short",
}

# v155: GER40 hard risk cap. Section 1 shows 39.8% WR over 964 trades -- structural,
# not noise. Existing soft penalty in adaptive_brooks_risk only fires when ger40_wr
# is recomputed; we add a hard final clamp at signal level too.
GER40_HARD_RISK_CAP = 0.10  # never risk more than 0.10% on GER40 regardless of Kelly
# v154 FIX: Zero-noise mode -- every placed trade is a T1 candidate
# Data collection and random trades pollute training set without quality labels
# T1 requires: real risk >= 0.02% + enrichment_ok + mfe_r written
# With these at 0, every trade the bot places contributes clean training data
RANDOM_EXPLORE_RATE  = 0.0   # OFF: was 0.05 -- random bypass produces non-T1 trades
RANDOM_EXPLORE_RISK  = 0.0   # OFF: was 0.025
DATA_COLLECTION_RISK = 0.0   # OFF: was 0.015 -- data trades excluded from T1 by risk filter
                               # Used for: cooldown signals, ranging signals, overflow signals
                               # Outside-hours signals -- purely to capture what would happen

# ── LIVE MODE CONFIG ──────────────────────────────────────────────────────────
# DEMO bot (trading_bot_final): # LIVE bot (trading_bot_live):  LIVE_MODE = False  # <- CHANGE TO True IN LIVE FOLDER

# FTMO Challenge account -- server + account number redacted for sharing
# Profit target: 10% = £974
# Daily loss limit: 5% = £487  (we self-limit to 2% = £195)
# Max drawdown: 10% = £974     (we self-limit to 5% = £487)

# ── ML BEHAVIOUR FLAGS ────────────────────────────────────────────────────────
# These control how aggressively ML influences trading decisions.
#
# CURRENT STATUS: Day 4 -- only ~700 trades, mostly from 1 bad day.
# Model may be biased toward "everything loses" from today's ranging market.
# Safe features ON, aggressive features OFF until day 14+.
#
# SCHEDULE:
#   Day 7-10   : enable ML_FILTER_HIGH_CONFIDENCE_LOSS (500+ resolved trades)
#   Day 14     : enable ML_ENTRY_TIMING (enough variety in data)
#   Day 30+    : reversal auto-checks begin firing if conditions met

# Filter: skip trade entirely if ML has HIGH confidence it will lose
# OFF for now -- model may over-filter due to today's bad market bias
ML_FILTER_HIGH_CONFIDENCE_LOSS = True  # enabled on both demo and live (demo uses looser threshold)

# Minimum ML probability to enter a trade at all.
# Trades below this threshold are skipped regardless of setup quality.
# The old approach only blocked HIGH-confidence losses (prob < 25%).
# This adds a floor: below 50% = model thinks it's more likely to lose than win.
# Demo uses 50% (stricter -- protect FTMO balance, better data quality)
# Live uses 45% (slightly looser -- fewer trades but still filters noise)
ML_MIN_ENTRY_PROB = 0.40  # v155: lowered from 0.45 -- model currently INVERTED (sep=-0.084).
                          # Strict ML filtering is hurting (-4.8% delta in report25).
                          # Hold loose until model recovers post-class-balance retrain.
ML_MIN_EV         = 0.0   # skip if EV = P(win)*RR - P(loss) <= 0
# EV filter catches: low-prob trades even with OK RR, AND low-RR trades even with OK prob

# ── v200 AUDIT BASELINE: master switch for ALL ML-based trade action ─────────
# 2026-06-02 audit found the ensemble is anti-predictive out-of-sample:
#   CPCV (purged/embargoed) holdout AUC = 0.477 (< 0.50 random)
#   recent-50 separation = -1.52% (model ranks losers above winners)
#   the bot's own decision-quality diagnostic reported "FILTERING HURTS"
# Until the model demonstrates a real edge under PURGED cross-validation
# (not the shuffle=True CV that currently inflates AUC to 0.80+), the ML layer
# must be observational only: predictions are still computed and logged so data
# collection continues, but they MUST NOT filter entries, set position size, or
# flip trade direction. This guards every ML-driven `continue`/risk multiplier
# in the live path. Flip back to True only after honest validation shows
# positive separation on unseen data. This is a stop-the-bleeding baseline,
# not a claim that the strategy is now profitable -- validate on demo first.
ML_GATING_ENABLED = False

# v166: MIN_SCORE_GATE -- was set to 3 in v165 based on a hand-wave assumption
# (I claimed "score 1-2 had 40% WR historically" without checking). Walked back
# to MIN_SCORE_GATE = 0 as default = no gate, behave like v164. Run analyzer
# script analyze_06_score_wr.py against your trade log to find the real WR per
# score bucket. Then set this constant to whatever the data actually supports.
# If analyzer shows score 1-2 are losers, set to 2 or 3. If they're fine, leave 0.
MIN_SCORE_GATE = 0

# ── CLEAN LABEL CUTOFF ───────────────────────────────────────────────────────
# Pre-v98 trades had corrupted quality labels (wrong MFE logic, binary weights,
# incorrect outcome classification). Training on them creates adversarial
# supervision -- the model learns contradictory truth definitions.
# v98 deployed: ~2026-04-08. Use 2026-04-07 as conservative cutoff.
# Institutional principle: clean 463 samples >> corrupted 2263 samples.
# Effect: calibration self-corrects, Turing gap shrinks, separation flips positive.
CLEAN_LABEL_CUTOFF = "2026-04-07 00:00:00"  # original v98 contamination cutoff
# Rolling expansion: once 90 days of clean data exist, the fixed cutoff is no longer binding.
# Effective cutoff = whichever is older: fixed cutoff OR 90 days ago.
# This prevents the fixed date from excluding ever-growing fractions of history.
_cutoff_90d = (datetime.now(timezone.utc) - timedelta(days=90)).strftime("%Y-%m-%d %H:%M:%S")
CLEAN_LABEL_CUTOFF_EFFECTIVE = max(CLEAN_LABEL_CUTOFF, _cutoff_90d)  # max() = always use the NEWER date -- preserves contamination guard

# Reversal: auto-enables per setup when ALL 4 conditions pass nightly
# v200 audit: DISABLED. Flipping trade direction on a model with negative
# out-of-sample separation flips on noise. Was True; the in-code comment at the
# call site even claimed "False by default" -- that contradiction is now resolved.
ML_REVERSAL_AUTO = False  # was True -- disabled by 2026-06-02 audit
ML_REVERSAL_CONFIRMED = {}  # populated at runtime -- DO NOT EDIT

# Dynamic SL/TP: max 20% adjustment -- low risk, keep on
ML_DYNAMIC_SLTP = True   # enabled -- Turing gap=0.067 (gap < 0.15 threshold met after label cleanup)

# Entry timing: OFF for now -- model needs more bar variety data
ML_ENTRY_TIMING = False  # re-enable day 14

# v163: removed FTMO_CHALLENGE_MODE complexity. Single-folder bot.
# Demo branch (LIVE_MODE=False) runs at 2x risk with Challenge-tight safety limits.
FTMO_CHALLENGE_MODE = False  # kept defined-as-False for any leftover references

if LIVE_MODE:
    RISK_MAIN        = 0.10   # £10 per trade on live
    RISK_BROOKS_BASE = 0.10
    RISK_BROOKS_MIN  = 0.05
    RISK_BROOKS_MAX  = 0.15
    DAILY_LOSS_LIMIT = 2.0
    MAX_DRAWDOWN     = 5.0
else:
    # v197 DEFENSIVE PROFILE (2026-05-26): account at 7.6% DD, $380 from FTMO kill.
    # Halved risk to extend remaining margin (~16 trades to kill at 0.25% vs ~8 at 0.5%).
    # Max DD raised from 7.0 to 9.0 to allow bot to actually run from current DD level
    # (was halting at 7.76%). Trade-off: less protection from runaway loss.
    RISK_MAIN        = 1.0     # was 2.0
    RISK_BROOKS_BASE = 0.25    # was 0.50
    RISK_BROOKS_MIN  = 0.10    # was 0.20
    RISK_BROOKS_MAX  = 0.50    # was 1.00
    DAILY_LOSS_LIMIT = 2.5     # was 3.0  -- tightened given small remaining margin
    MAX_DRAWDOWN     = 9.0     # was 7.0  -- raised to allow trading from current DD

# ── BE / PARTIAL CONFIG ──────────────────────────────────────────────────────
# False = bot LOGS what would have happened (ML learns) but does NOT execute
# True  = bot actually moves SL / closes partial
ENABLE_BREAKEVEN = False   # theoretical only -- SL does NOT move. ML gets clean win/loss labels. be_trigger_hit tracks if 0.8R was reached.
ENABLE_PARTIALS  = False   # ML learns when partials help -- not hardcoded yet

LONDON_OPEN_HOUR = 8    # UTC -- 09:00 UK time, actual London market open
NY_OPEN_HOUR     = 15   # UTC -- 16:00 Lithuania
ASIAN_END_HOUR   = 9

UK100_STOP_PTS   = 20
UK100_TARGET_PTS = 26

EMA_PERIOD       = 20
STRONG_BAR       = 0.25
RANGE_LOOKBACK   = 20

# Learning thresholds
COOLDOWN_HOURS       = 1
# v164: Reduced from 3 to 1 per Analyzer 5 results.
# Real data: WR after 0 losses = 69.4%, after 1 loss = 31.7%, after 2 losses = 44.2%
# A single loss is a 25-point WR drop signal. Don't wait for 3.
LOSS_STREAK_COOLDOWN = 1   # 1 loss = cooldown. Validated by user's stats --
                            # WR drops massively after 1 loss for these setups.
                            # Watermark logic in get_setup_stats prevents the
                            # historical-losses-keep-retriggering loop.
MAX_BROOKS_OPEN      = 3    # max open Brooks positions at once (overflow still logs)
MAX_TOTAL_OPEN       = 10   # hard cap -- keeps exposure manageable
MAX_PER_SYMBOL       = 2    # max real-risk positions per symbol -- prevents stacking correlated bets
                             # e.g. 3 US30 longs = 1 big bet, not 3 independent trades
MIN_TRADES_TO_LEARN  = 30  # min trades before cooldown kicks in
WIN_RATE_BOOST_THRESH = 60  # win% above this -> +25% risk
WIN_RATE_COOL_THRESH  = 25  # win% below this -> cooldown (lowered from 35 -- tariff shock week distorted stats)

# v181: dates excluded from BOTH training and cooldown calculation due to known
# bug-impacted outcomes. NOT for "bad market days" -- that's overfitting in
# hindsight. ONLY for days where our own code was broken (deployment churn,
# cluster bug active, stuck positions distorting calcs, etc.) OR where the
# user manually traded the account alongside bot positions (data contamination).
# Single source of truth: previously duplicated as _CONTAMINATED_DAYS in
# online_retrain() and _COOLDOWN_CONTAMINATED_DAYS in get_setup_stats().
# Change here, both sites pick it up automatically.
#
# 2026-05-04: cluster bug + deployment churn (v174-v176 deployed mid-day).
#             Bot's own code was broken. Real bug, not market signal.
# 2026-05-15: user traveled and traded manually alongside bot during phase 2.
#             Bot positions and manual positions both in MT5 history. Outcomes
#             of bot trades likely affected by user's manual closes. Excluded
#             from training so the model doesn't learn from mixed bot+manual data.
CONTAMINATED_DAYS = ("2026-05-04", "2026-05-15", "2026-05-27")

LOG_FILE   = "trades_log.json"
STATS_FILE = "win_stats.json"
STATE_FILE = "bot_state.json"
# Path to demo bot's trades_log -- live bot reads this for GER40 WR stats (more data)
DEMO_LOG   = r"trades_log.json"   # path to demo bot's log (redacted for sharing -- set to your own)

# ── ACCOUNT CREDENTIALS ───────────────────────────────────────────────────────
# Centralised here -- change ONLY this block, not inline strings.
# Prevents accidental demo login if this file is copied to the live folder.
# Reads from environment variables if set (safer for production).
# Falls back to hardcoded defaults so behaviour is unchanged if env vars not set.
# To set on Windows: System Properties -> Environment Variables -> New
# v160: FTMO Challenge account credentials.
# IMPORTANT: do NOT commit the real password to this file.
# Set the env var MT5_PASSWORD before running, OR replace the placeholder below
# locally on the trading machine only.
# To set on Windows (run once in cmd):
#   setx MT5_PASSWORD "your_real_password_here"
#   then close and reopen cmd before running the bot.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# v162: HARDCODED CREDENTIALS  (per user request -- env var path was failing)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# WARNING: this file now contains the live MT5 password in plaintext.
# CONSEQUENCES:
#   - Anyone with read access to this file or this folder can log into the
#     account and place trades / withdraw funds.
#   - Do NOT commit this file to git, dropbox, onedrive, or any cloud sync.
#   - Do NOT share this file with anyone.
#   - Do NOT upload this file to any chat / forum / pastebin.
#   - If the machine is shared or has remote access enabled, change password.
#   - Reset the FTMO password if this file ever leaves the trading machine.
#
# Env var still works as override: if MT5_PASSWORD env var is set, it WINS.
# That lets you swap accounts without editing the file.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
_HARDCODED_LOGIN    = 0  # REPLACE with your account number -- e.g. 12345678
_HARDCODED_PASSWORD = "REPLACE_ME"  # REPLACE with your master password
_HARDCODED_SERVER   = "FTMO-Server4"  # v187: phase-2 account uses Server4. Change here if FTMO assigns differently.

# v188: MT5 terminal path configurable. Previous hardcoded FTMO-branded path
# could fail when switching between phase 1 (Server3) and phase 2 (Server4)
# accounts -- the FTMO terminal binary appears to retain its initial server
# binding across API connections. The generic "MetaTrader" install accepts any
# server. The init code tries _HARDCODED_MT5_PATH first; if not found OR auth
# fails on it, it tries the FTMO-branded path as a fallback. Either path can
# be overridden with env var MT5_PATH.
_HARDCODED_MT5_PATH = r"C:\Program Files\MetaTrader\terminal64.exe"

MT5_LOGIN    = int(os.environ.get("MT5_LOGIN",    str(_HARDCODED_LOGIN)))
MT5_PASSWORD = os.environ.get("MT5_PASSWORD",     _HARDCODED_PASSWORD)
MT5_SERVER   = os.environ.get("MT5_SERVER",       _HARDCODED_SERVER)
MT5_PATH     = os.environ.get("MT5_PATH",         _HARDCODED_MT5_PATH)

# v187: fail fast if credentials are placeholders (prevents accidental runs
# with the leaked-and-blanked v186 credentials still in code).
if MT5_LOGIN == 0 or MT5_PASSWORD in ("REPLACE_ME", "", None):
    print("=" * 70)
    print("ERROR: MT5 credentials not set.")
    print("=" * 70)
    print("Edit lines ~378-380 of bot.py:")
    print('    _HARDCODED_LOGIN    = 12345678       # your account number')
    print('    _HARDCODED_PASSWORD = "your-password"  # your master password')
    print('    _HARDCODED_SERVER   = "FTMO-Server4"   # check FTMO portal')
    print()
    print("OR set environment variables before running:")
    print('    set MT5_LOGIN=12345678')
    print('    set MT5_PASSWORD=your-password')
    print('    set MT5_SERVER=FTMO-Server4')
    print('    python bot.py')
    import sys
    sys.exit(1)

def atomic_write(filepath: str, data):
    """
    Write JSON atomically -- write to temp file first, then rename.
    Retries up to 3x on PermissionError (two bots writing simultaneously).
    v166: persistent failures now log.error AND attempt fallback write to
    {filepath}.fallback.<timestamp> so data is never silently lost.
    v186: explicit UTF-8 encoding. NamedTemporaryFile defaulted to system
    encoding (cp1257 on Windows-LT, cp1252 on Windows-EN, etc.) which fails
    on any non-ASCII character in the JSON. Crashed the bot mid-session
    when a comment or symbol name contained an em-dash or accented char.
    """
    import tempfile, os, time
    dirpath  = os.path.dirname(os.path.abspath(filepath)) or "."
    tmp_path = None
    last_err = None
    for attempt in range(3):
        try:
            with tempfile.NamedTemporaryFile("w", dir=dirpath, delete=False, suffix=".tmp",
                                              encoding="utf-8") as f:
                tmp_path = f.name
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(tmp_path, filepath)  # atomic on all platforms
            return  # success
        except PermissionError as e:
            last_err = e
            if tmp_path and os.path.exists(tmp_path):
                try: os.remove(tmp_path)
                except: pass
            tmp_path = None
            time.sleep(0.05 * (attempt + 1))  # 50ms, 100ms, 150ms backoff
        except Exception as e:
            if tmp_path and os.path.exists(tmp_path):
                try: os.remove(tmp_path)
                except: pass
            raise e
    # v166: All retries failed -- was log.debug (invisible). Now LOUD + fallback.
    log.error(f"atomic_write {filepath}: ALL 3 RETRIES FAILED ({last_err}). "
              f"This means data is being lost. Check file permissions / disk full / antivirus.")
    # Try a fallback location so the data isn't lost entirely.
    try:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        fallback = f"{filepath}.fallback.{ts}"
        # v186: explicit UTF-8 here too. Same bug as main path on Windows-LT.
        with open(fallback, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        log.error(f"atomic_write: data dumped to {fallback} -- "
                  f"investigate and merge manually before next session")
    except Exception as fb_err:
        log.error(f"atomic_write: fallback ALSO failed ({fb_err}) -- data lost")

# ── LOGGING ───────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# ── DATA CLASSES ──────────────────────────────────────────────────────────────

@dataclass
class KeyLevels:
    daily_open:     float
    yesterday_high: float
    yesterday_low:  float
    last_week_high: float
    last_week_low:  float

@dataclass
class SetupSignal:
    symbol:     str
    strategy:   str
    setup_type: str
    setup_name: str
    entry:      float
    stop_loss:  float
    take_profit: float
    direction:  str       # "long" | "short"
    timestamp:  str

# ── MT5 ───────────────────────────────────────────────────────────────────────

def connect_mt5() -> bool:
    # v162: refuse to start if password is empty or obviously a placeholder.
    # Better to fail loudly at startup than to silently spin retrying logins
    # against an account with bad credentials.
    _bad_passwords = {
        "REPLACE_ME_LOCALLY", "", "your_password_here",
        "your_actual_password_here", "CHANGE_ME", "password",
        "your_NEW_password_after_step_1",
    }
    if MT5_PASSWORD in _bad_passwords or len(MT5_PASSWORD) < 6:
        log.error("=" * 60)
        log.error("MT5_PASSWORD looks like a placeholder. The bot will NOT start.")
        log.error(f"Current password length: {len(MT5_PASSWORD)} (need >=6 chars)")
        log.error("Either:")
        log.error("  1. Edit this file: replace _HARDCODED_PASSWORD with the real one")
        log.error("  2. Set env var: setx MT5_PASSWORD \"your_password\"  (then REOPEN cmd)")
        log.error("=" * 60)
        return False
    # v190: try connecting to an already-running MT5 FIRST. If you've opened
    # MT5 manually and logged in (so the master password is cached in the
    # terminal session), this connects in one shot. Only if that fails do we
    # try launching MT5 from a path.
    #
    # Why this order matters: when the password isn't saved in MT5's profile,
    # Python's mt5.initialize(path=..., login=..., password=...) fails because
    # MT5 needs an interactive login. But mt5.initialize() with NO path
    # attaches to an existing MT5 process that's already authenticated.
    #
    # Workflow for the user:
    #   1. Open FTMO MT5, log in with master password, check "Save account information"
    #   2. Keep MT5 open
    #   3. Run bot.py
    import os as _os
    ok = False
    _last_err = None

    # ── Attempt 1: attach to already-running MT5 ─────────────────────────
    log.info("Attempting to attach to running MT5 terminal...")
    ok = mt5.initialize(login=MT5_LOGIN, password=MT5_PASSWORD, server=MT5_SERVER)
    if ok:
        log.info("MT5 connected via running terminal (attached)")
    else:
        _last_err = mt5.last_error()
        log.warning(f"  Attach failed: {_last_err} -- trying to launch from path...")
        try:
            mt5.shutdown()
        except Exception:
            pass

    # ── Attempt 2: launch MT5 from path ───────────────────────────────────
    if not ok:
        _path_candidates = []
        if MT5_PATH:
            _path_candidates.append(MT5_PATH)
        for _p in (
            r"C:\Program Files\FTMO Global Markets MT5 Terminal\terminal64.exe",
            r"C:\Program Files\MetaTrader\terminal64.exe",
        ):
            if _p not in _path_candidates:
                _path_candidates.append(_p)

        for _candidate in _path_candidates:
            if not _os.path.exists(_candidate):
                log.debug(f"MT5 path not found, skipping: {_candidate}")
                continue
            log.info(f"Trying MT5 terminal: {_candidate}")
            ok = mt5.initialize(path=_candidate, login=MT5_LOGIN, password=MT5_PASSWORD, server=MT5_SERVER)
            if ok:
                log.info(f"MT5 connected via: {_candidate}")
                break
            _last_err = mt5.last_error()
            log.warning(f"  init failed on {_candidate}: {_last_err}")
            try:
                mt5.shutdown()
            except Exception:
                pass

    if not ok:
        log.error(f"MT5 init failed everywhere. Last error: {_last_err or mt5.last_error()}")
        log.error(f"  Account: {MT5_LOGIN}  Server: {MT5_SERVER}")
        log.error("  To fix:")
        log.error("    1. Open MT5 (FTMO Global Markets terminal) manually")
        log.error("    2. Log in to your account with the MASTER password")
        log.error("    3. CHECK the 'Save account information' box")
        log.error("    4. Keep MT5 open")
        log.error("    5. Run python bot.py again")
        return False
    info = mt5.account_info()
    if info is None:
        log.error("Cannot get account info -- is MT5 open and logged in?")
        return False
    if info.login != MT5_LOGIN:
        log.warning(f"Wrong account {info.login} -- forcing switch to DEMO {MT5_LOGIN}")
        if not mt5.login(MT5_LOGIN, password=MT5_PASSWORD, server=MT5_SERVER):
            log.error(f"Failed to switch to DEMO {MT5_LOGIN}: {mt5.last_error()}")
            return False
        info = mt5.account_info()
    log.info(f"Connected: {info.name}  Balance: ${info.balance:,.2f}  Server: {info.server}")
    return True
def load_state() -> dict:
    # 10s TTL cache -- is_in_cooldown calls this on every signal (8+/tick)
    # Cooldowns change at most a few times per hour -- no need to re-read every second
    import time as _ls_time
    _ls_now = _ls_time.monotonic()
    _ls_cached = getattr(load_state, "_cache", None)
    _ls_ts     = getattr(load_state, "_cache_ts", 0)
    if _ls_cached is not None and (_ls_now - _ls_ts) < 10:
        return _ls_cached
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, encoding="utf-8") as f:
            try:
                result = json.load(f)
                setattr(load_state, "_cache", result)
                setattr(load_state, "_cache_ts", _ls_now)
                return result
            except json.JSONDecodeError:
                log.warning("State file corrupted -- resetting")
                return {}
    return {}


def _invalidate_state_cache():
    """Call after save_state() to force next load_state() to re-read."""
    setattr(load_state, "_cache", None)

def save_state(state: dict):
    atomic_write(STATE_FILE, state)
    _invalidate_state_cache()  # force next load_state() to re-read fresh data

def get_starting_balance() -> float:
    # 60s TTL cache -- sanity check calls account_info() but check_safety calls this every 5s
    # Without cache: 1 extra uncached account_info() call every 5s (720/hr wasted)
    import time as _gsb_time
    _gsb_now = _gsb_time.monotonic()
    _gsb_cached = getattr(get_starting_balance, "_cache", None)
    _gsb_ts     = getattr(get_starting_balance, "_cache_ts", 0)
    if _gsb_cached is not None and (_gsb_now - _gsb_ts) < 60:
        return _gsb_cached
    state = load_state()
    if "starting_balance" not in state:
        bal = mt5.account_info().balance
        state["starting_balance"] = bal
        save_state(state)
        log.info(f"Starting balance: ${bal:,.2f}")
    else:
        # Sanity check -- reset if stored balance is wrong account or old session
        # Runs at most every 60s (not every 5s via check_safety cache)
        stored = state["starting_balance"]
        current = mt5.account_info().balance
        if stored < current * 0.5 or stored > current * 1.5:
            log.warning(f"Starting balance ${stored:,.2f} looks wrong vs current ${current:,.2f} -- resetting to current")
            state["starting_balance"] = current
            state["daily_balance"]    = current  # also reset daily reference
            state["daily_date"]       = datetime.now(timezone.utc).date().isoformat()
            save_state(state)
            setattr(get_starting_balance, "_cache", None)  # invalidate on reset
    result = state["starting_balance"]
    setattr(get_starting_balance, "_cache", result)
    setattr(get_starting_balance, "_cache_ts", _gsb_now)
    return result

def get_daily_balance() -> float:
    state = load_state()
    today = datetime.now(timezone.utc).date().isoformat()  # UTC -- prevents mid-session reset
    if state.get("daily_date") != today:
        # New day -- reset to current balance (market hasn't opened yet)
        bal = mt5.account_info().balance
        state["daily_date"]    = today
        state["daily_balance"] = bal
        save_state(state)
        log.info(f"Daily balance reset: ${bal:,.2f}")
    elif "daily_balance" not in state:
        # Restart mid-day -- use stored value, NOT current balance
        # This prevents: crash at -3%, restart, daily loss shows 0%
        bal = mt5.account_info().balance
        state["daily_balance"] = bal
        save_state(state)
        log.info(f"Daily balance (mid-day restart): ${bal:,.2f}")
    return state["daily_balance"]

def check_safety() -> tuple[bool, str]:
    # Cache account_info with 5s TTL -- called every 1s, balance changes slowly
    _now_cs = datetime.now(timezone.utc).timestamp()
    _cs_cache = getattr(check_safety, "_cache", None)
    _cs_ts    = getattr(check_safety, "_cache_ts", 0)
    if _cs_cache is None or (_now_cs - _cs_ts) > 5:
        _cs_cache = mt5.account_info()
        setattr(check_safety, "_cache", _cs_cache)
        setattr(check_safety, "_cache_ts", _now_cs)
    info = _cs_cache
    if info is None:
        return False, "Cannot get account info"
    bal    = info.balance
    equity = info.equity  # includes floating P&L on open positions
    start  = get_starting_balance()
    daily  = get_daily_balance()
    # Use EQUITY not balance -- catches floating losses on open positions
    # Without this, 57 losing shorts show as 0% daily loss until they close
    dd    = (start - equity) / start * 100
    dl    = (daily - equity) / daily * 100
    if dd >= MAX_DRAWDOWN:
        return False, f"Max drawdown {dd:.2f}% (equity) -- bot stopped"
    if dl >= DAILY_LOSS_LIMIT:
        return False, f"Daily loss {dl:.2f}% (equity) -- no more trades today"

    # v159: ACCOUNT-LEVEL CIRCUIT BREAKER
    # If N consecutive trades lose (any symbol, any setup), halt for rest of day.
    # This catches silent model breakage, regime shift, news events, exchange data
    # corruption -- anything where the bot's edge is broken in a way the per-setup
    # cooldown doesn't catch. 8 losses in a row at the bot's average ~0.2% risk =
    # ~1.6% drawdown which is well inside the daily limit but a clear signal that
    # something is wrong.
    #
    # v194 BUG FIX: previously the breaker looked at the last 20 resolved trades
    # regardless of date. This created a deadlock: if yesterday's session ended
    # with 5+ consecutive losses, the bot would START today already over the
    # threshold and never be able to place a single trade -- forever stuck.
    # That happened on 2026-05-22 after May 21 ended with 8 consecutive losses.
    # Fix: filter to only trades placed SINCE the last midnight UTC (= today's
    # session). Matches the original design intent ("halt for rest of day") and
    # prevents the cross-session deadlock. Daily loss limit still catches multi-
    # day damage at the account level.
    try:
        if os.path.exists(LOG_FILE):
            # Cache for 60s -- this check runs every 3s in the main loop
            _cb_cached    = getattr(check_safety, "_circuit_breaker_cache", None)
            _cb_cached_ts = getattr(check_safety, "_circuit_breaker_ts", 0)
            import time as _cb_time
            _cb_now       = _cb_time.monotonic()
            if _cb_cached is None or (_cb_now - _cb_cached_ts) > 60:
                with open(LOG_FILE, encoding="utf-8") as _cbf:
                    _cb_trades = json.load(_cbf)
                # v194: session boundary = today's UTC date prefix.
                # _today_utc matches the format of trade timestamps ("YYYY-MM-DD HH:MM:SS")
                _today_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                # Look at TODAY's resolved real-risk trades only (skip data/random).
                # v181: also filter contaminated days. May 4 had 16 consecutive
                # losses from bug-driven trades -- without this filter, the breaker
                # would fire on every restart since startup until enough new
                # decisive trades pushed May 4 out of the window.
                _cb_recent = [t for t in _cb_trades[-300:]
                             if t.get("outcome") in ("win","loss","eod_win","eod_loss")
                             and not t.get("random", False)
                             and (t.get("risk_pct") or 0) >= 0.02
                             and not any(t.get("timestamp","").startswith(d) for d in CONTAMINATED_DAYS)
                             and t.get("timestamp","").startswith(_today_utc)  # v194: today only
                             ][-20:]
                # Count consecutive losses from most recent
                _consec = 0
                for t in reversed(_cb_recent):
                    if t.get("outcome") in ("loss", "eod_loss"):
                        _consec += 1
                    else:
                        break
                _cb_cached = _consec
                setattr(check_safety, "_circuit_breaker_cache", _cb_cached)
                setattr(check_safety, "_circuit_breaker_ts", _cb_now)
            # v161: mode-aware circuit breaker threshold.
            # Demo at 0.25% base: 8 losses = ~2% drawdown -- well under 4% daily limit
            # Challenge at 0.5% base: 8 losses = ~4% drawdown -- over 3% daily limit
            # Live at 0.10% base: 8 losses = ~0.8% -- well under 2% daily limit
            # Fix: trigger circuit breaker at consec count where 1.5x consec * BASE
            # would breach the self-imposed daily limit.
            _cb_threshold = max(5, int(DAILY_LOSS_LIMIT / max(RISK_BROOKS_BASE, 0.05) * 0.7))
            # Examples by mode:
            #   Demo:      max(5, int(4.0 / 0.25 * 0.7)) = max(5, 11) = 11
            #   Challenge: max(5, int(3.0 / 0.50 * 0.7)) = max(5, 4)  = 5
            #   Live:      max(5, int(2.0 / 0.10 * 0.7)) = max(5, 14) = 14
            # In Challenge mode the breaker now fires at 5 consecutive losses,
            # which is when the cumulative drawdown approaches the daily limit.
            if _cb_cached >= _cb_threshold:
                return False, (f"CIRCUIT BREAKER: {_cb_cached} consecutive losses "
                              f"(threshold={_cb_threshold} for current risk profile) -- "
                              f"halting until tomorrow (model may be broken or regime shifted)")
    except Exception as _cb_e:
        log.debug(f"Circuit breaker check error: {_cb_e}")

    _session_start = getattr(check_safety, "_session_start_bal", None)
    if _session_start is None:
        setattr(check_safety, "_session_start_bal", bal)
        _session_start = bal
    _session_pnl = bal - _session_start
    _session_str = f"  session={_session_pnl:+.0f}"
    # v153: count open positions for visibility
    try:
        _n_pos = len(mt5.positions_get() or [])
        _pos_str = f"  pos={_n_pos}"
    except Exception:
        _pos_str = ""
    return True, f"OK  bal=${bal:,.0f}  equity=${equity:,.0f}  daily={dl:.2f}%  dd={dd:.2f}%{_session_str}{_pos_str}"

def calc_lots(symbol: str, entry: float, sl: float, risk_pct: float) -> float:
    info = mt5.account_info()
    sym  = mt5.symbol_info(symbol)
    if not info or not sym:
        # v165: was returning 0.01 silently. Now warn -- silent fallback was hiding
        # MT5 connection issues that should be visible.
        log.warning(f"calc_lots: missing account/symbol info for {symbol} -- "
                    f"falling back to 0.01 lot (silent before v165)")
        return 0.01
    risk_amt = min(info.balance, info.equity) * (risk_pct / 100)  # use lower of balance/equity
    dist     = abs(entry - sl)
    if dist == 0 or sym.trade_tick_size == 0:
        log.warning(f"calc_lots: invalid geometry on {symbol} "
                    f"(dist={dist}, tick_size={sym.trade_tick_size}) -- "
                    f"falling back to 0.01 lot")
        return 0.01
    pt_val = sym.trade_tick_value / sym.trade_tick_size
    lot    = risk_amt / (dist * pt_val)
    lot    = max(sym.volume_min, min(sym.volume_max, lot))
    lot    = round(round(lot / sym.volume_step) * sym.volume_step, 2)
    # v165: detect when risk_pct asked for far more than volume_max would allow.
    # Rare but worth knowing about -- usually means stop is unusually wide.
    _intended_lot = risk_amt / (dist * pt_val) if (dist * pt_val) > 0 else 0
    if _intended_lot > sym.volume_max * 1.1:
        log.warning(f"calc_lots: {symbol} intended {_intended_lot:.2f} lots but "
                    f"capped at volume_max={sym.volume_max} -- risk_pct={risk_pct}% "
                    f"effectively reduced")
    return lot

def has_open_trade(symbol: str) -> bool:
    pos = mt5.positions_get(symbol=symbol)
    ord = mt5.orders_get(symbol=symbol)
    return bool((pos and len(pos)) or (ord and len(ord)))

# ── MARKET DATA ───────────────────────────────────────────────────────────────

def kalman_trend(prices: list) -> dict:
    """
    Kalman filter for trend estimation.
    More responsive than EMA -- adapts to volatility automatically.
    Returns: slope, direction, noise ratio
    """
    try:
        import numpy as np
        if len(prices) < 5:
            return {"kalman_slope": 0.0, "kalman_bull": False, "kalman_noise": 1.0}
        
        # Simple 1D Kalman filter
        # State: [price, velocity]
        # Tuning: Q=process noise, R=measurement noise
        n = len(prices)
        x = float(prices[0])   # initial estimate
        v = 0.0                 # initial velocity
        p = 1.0                 # initial uncertainty
        Q = 0.001               # process noise (how fast trend changes)
        R = 0.1                 # measurement noise (how noisy prices are)
        
        estimates = []
        for price in prices:
            # Predict
            x = x + v
            p = p + Q
            # Update
            K = p / (p + R)     # Kalman gain
            x = x + K * (float(price) - x)
            v = v + K * 0.1 * (float(price) - x)  # velocity update
            p = (1 - K) * p
            estimates.append(x)
        
        # Slope over last 5 estimates
        recent = estimates[-5:]
        slope = (recent[-1] - recent[0]) / recent[0] * 100 if recent[0] != 0 else 0
        
        # Noise ratio: how much price deviates from Kalman estimate
        residuals = [abs(float(prices[i]) - estimates[i]) for i in range(n)]
        avg_price = sum(float(p) for p in prices) / n
        noise_ratio = (sum(residuals) / n) / avg_price * 100 if avg_price > 0 else 1.0
        
        return {
            "kalman_slope":     round(slope, 4),
            "kalman_bull":      slope > 0,
            "kalman_noise":     round(noise_ratio, 4),
            "kalman_estimate":  round(estimates[-1], 2),
        }
    except Exception:
        return {"kalman_slope": 0.0, "kalman_bull": False, "kalman_noise": 1.0}

def get_candles(symbol: str, tf, count: int) -> Optional[pd.DataFrame]:
    # 10s TTL cache -- candles don't change tick-to-tick within same second
    # Eliminates 80%+ of MT5 reads: Brooks detectors, score_signal, capture_market_context
    # all call get_candles for same (symbol, tf) within the same iteration
    import time as _gc_time
    _gc_key = f"_gc_{symbol}_{tf}_{count}"
    _gc_ts  = f"_gc_ts_{symbol}_{tf}_{count}"
    _gc_now = _gc_time.monotonic()
    # v168 BUG FIX: previous code used string "__missing__" as a sentinel and
    # `_gc_cached != "__missing__"`. When _gc_cached was a DataFrame, that
    # `!=` triggers pandas elementwise comparison which raises
    # "truth value is ambiguous". Use a unique sentinel object and `is` check.
    _MISSING = get_candles  # any unique object -- using the function itself
    _gc_cached    = getattr(get_candles, _gc_key, _MISSING)
    _gc_cached_ts = getattr(get_candles, _gc_ts, 0)
    if _gc_cached is not _MISSING:
        if _gc_cached is None and (_gc_now - _gc_cached_ts) < 3:
            return None  # short-cache failed fetches
        if _gc_cached is not None and (_gc_now - _gc_cached_ts) < 10:
            return _gc_cached
    rates = mt5.copy_rates_from_pos(symbol, tf, 0, count)
    if rates is None or len(rates) == 0:
        # v166: cache the failure so we don't hammer MT5 on every call
        setattr(get_candles, _gc_key, None)
        setattr(get_candles, _gc_ts, _gc_now)
        return None
    df = pd.DataFrame(rates)
    df["time"]      = pd.to_datetime(df["time"], unit="s")
    df["green"]     = df["close"] > df["open"]
    df["bar_range"] = df["high"] - df["low"]
    df["ema20"]     = df["close"].ewm(span=EMA_PERIOD, adjust=False).mean()
    setattr(get_candles, _gc_key, df)
    setattr(get_candles, _gc_ts, _gc_now)
    return df

def get_key_levels(symbol: str) -> Optional[KeyLevels]:
    df = get_candles(symbol, mt5.TIMEFRAME_D1, 10)  # 10s cache -- was direct MT5 read
    if df is None or len(df) < 6:
        return None
    return KeyLevels(
        daily_open     = float(df.iloc[-1]["open"]),
        yesterday_high = float(df.iloc[-2]["high"]),
        yesterday_low  = float(df.iloc[-2]["low"]),
        last_week_high = float(df.iloc[-7:-1]["high"].max()),
        last_week_low  = float(df.iloc[-7:-1]["low"].min()),
    )

def get_overnight_range(symbol: str) -> Optional[tuple[float, float]]:
    df = get_candles(symbol, TF_15M, 60)
    if df is None:
        return None
    on = df[df["time"].dt.hour < ASIAN_END_HOUR]
    if on.empty:
        on = df.head(8)
    if on.empty:
        return None
    return float(on["high"].max()), float(on["low"].min())

def nearest_key_level(price: float, levels: KeyLevels, tol: float = 0.0015) -> Optional[str]:
    for name, lvl in {
        "daily_open":     levels.daily_open,
        "yesterday_high": levels.yesterday_high,
        "yesterday_low":  levels.yesterday_low,
        "last_week_high": levels.last_week_high,
        "last_week_low":  levels.last_week_low,
    }.items():
        if abs(price - lvl) / lvl < tol:
            return name
    return None

def measured_move(symbol: str, tf, direction: str, entry: float) -> float:
    df = get_candles(symbol, tf, 25)
    if df is None:
        sym  = mt5.symbol_info(symbol)
        move = 50 * (sym.point if sym else 0.01)
        return entry + move if direction == "long" else entry - move
    size = float(df.iloc[-20:-1]["high"].max()) - float(df.iloc[-20:-1]["low"].min())
    return entry + size if direction == "long" else entry - size

# ── MARKET STRUCTURE ──────────────────────────────────────────────────────────

def market_direction(df: pd.DataFrame) -> str:
    """Bull | bear | range -- based on EMA slope and recent structure."""
    if len(df) < 25:
        return "range"
    ema_now  = float(df.iloc[-1]["ema20"])
    ema_prev = float(df.iloc[-5]["ema20"])
    slope    = (ema_now - ema_prev) / ema_prev * 100
    r_high   = float(df.iloc[-10:]["high"].max())
    r_low    = float(df.iloc[-10:]["low"].min())
    p_high   = float(df.iloc[-20:-10]["high"].max())
    p_low    = float(df.iloc[-20:-10]["low"].min())
    hh_hl    = r_high > p_high and r_low > p_low
    lh_ll    = r_high < p_high and r_low < p_low
    if slope > 0.05 and hh_hl:
        return "bull"
    if slope < -0.05 and lh_ll:
        return "bear"
    return "range"

def is_optimal_time() -> bool:
    """
    Trade 00:00-20:30 UTC (01:00-21:30 Lithuania).
    1.5hrs after original 19:00 session end.
    """
    now = datetime.now(timezone.utc)
    h, m = now.hour, now.minute
    return (h < 20) or (h == 20 and m < 30)

def is_daily_close() -> bool:
    """
    Close all positions at 20:30 UTC (21:30 Lithuania) -- end of trading day.
    1.5hrs after original 19:00 close.
    Fires for a 30-min window to avoid re-closing repeatedly.
    """
    now = datetime.now(timezone.utc)
    return (now.hour == 20 and now.minute >= 28) or (now.hour == 21 and now.minute < 30)

def is_pre_eod() -> bool:
    """
    Stop opening NEW positions 30 minutes before EOD close (20:30 UTC).
    Prevents pile-up of positions right before the close.
    Includes data collection trades -- no new opens at all.
    """
    now = datetime.now(timezone.utc)
    return (now.hour == 20 and now.minute >= 0) or now.hour == 21

def is_friday_close() -> bool:
    """Friday close at 20:30 UTC (21:30 Lithuania) -- aligned with daily close."""
    now = datetime.now(timezone.utc)
    return now.weekday() == 4 and ((now.hour == 20 and now.minute >= 28) or now.hour == 21)

def is_weekend() -> bool:
    """Returns True on Saturday and Sunday -- markets closed, no trading."""
    return datetime.now(timezone.utc).weekday() in (5, 6)  # 5=Sat, 6=Sun


def close_all_positions(reason: str):
    """
    Close all open positions. Re-fetches position list on every pass
    so stale snapshots don't cause the retry to re-attempt already-closed trades.
    Loops until empty or 10 full passes with no progress.
    """
    # v176: reset market-closed tracking for this close session.
    setattr(close_all_positions, "_mc_seen", set())
    # Cancel ALL pending orders first -- repeat 3 times to catch broker-delayed fills
    for cancel_pass in range(3):
        orders = mt5.orders_get()
        if not orders:
            break
        for order in orders:
            result = mt5.order_send({
                "action": mt5.TRADE_ACTION_REMOVE,
                "order":  order.ticket,
            })
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                log.info(f"Cancelled order #{order.ticket} {order.symbol} -- {reason}")
        time.sleep(0.5)  # wait for broker to process cancellations

    time.sleep(1.0)  # extra wait for any in-flight orders to settle

    # Close positions in passes -- re-fetch list each pass
    max_passes   = 10
    no_progress  = 0
    for pass_num in range(max_passes):
        positions = mt5.positions_get()
        if not positions:
            log.info(f"All positions closed after {pass_num} passes -- {reason}")
            return
        # Safety: only close positions on our account
        _ai = mt5.account_info()
        if _ai and _ai.login != MT5_LOGIN:
            log.warning(f"close_all_positions: wrong account {_ai.login} vs expected {MT5_LOGIN} -- aborting")
            return
        prev_count = len(positions)
        log.info(f"EOD pass {pass_num+1}: {prev_count} positions to close")

        for pos in positions:
            tick     = mt5.symbol_info_tick(pos.symbol)
            sym_info = mt5.symbol_info(pos.symbol)
            if tick is None:
                continue
            is_long    = pos.type == mt5.ORDER_TYPE_BUY
            close_type = mt5.ORDER_TYPE_SELL if is_long else mt5.ORDER_TYPE_BUY
            price      = tick.bid if is_long else tick.ask

            # Use exact position volume -- never bump up (causes new positions)
            vol = pos.volume
            # Round to allowed step (round DOWN not up)
            if sym_info and sym_info.volume_step > 0:
                import math
                vol = round(math.floor(vol / sym_info.volume_step) * sym_info.volume_step,
                           len(str(sym_info.volume_step).rstrip("0").split(".")[-1]) if "." in str(sym_info.volume_step) else 0)
            # Skip if below broker minimum -- bumping up would open new positions
            if sym_info and vol < sym_info.volume_min:
                log.warning(f"Skip #{pos.ticket} {pos.symbol} vol={vol} below min -- close manually")
                continue

            result = mt5.order_send({
                "action":       mt5.TRADE_ACTION_DEAL,
                "symbol":       pos.symbol,
                "volume":       vol,
                "type":         close_type,
                "price":        price,
                "position":     pos.ticket,  # CRITICAL: tells MT5 which position to close
                "deviation":    200,
                "magic":        202401,
                "comment":      f"close:{reason}",
                "type_filling": mt5.ORDER_FILLING_IOC,
            })
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                log.info(f"Closed position #{pos.ticket} {pos.symbol} -- {reason}")
            else:
                code = result.retcode if result else "None"
                if code == 10040:
                    log.warning(f"Skip #{pos.ticket} {pos.symbol} vol={vol} below min -- broker rejected")
                elif code == 10018:
                    # v171: market closed (10018) is not actionable -- don't spam.
                    # Position will close on its own next session or via manual close.
                    # v176 FIX: previously this returned from the entire function,
                    # abandoning close attempts on OTHER positions whose markets WERE
                    # open. That caused 3 US30 brooks positions to be left open at EOD
                    # because the stuck UK100 was iterated first and triggered return.
                    # Track per-position so we log once per market-closed position,
                    # but continue trying the rest.
                    _market_closed_seen = getattr(close_all_positions, "_mc_seen", set())
                    if pos.ticket not in _market_closed_seen:
                        log.warning(f"Cannot close #{pos.ticket} {pos.symbol}: market closed (10018) -- will retry when market opens")
                        _market_closed_seen.add(pos.ticket)
                        setattr(close_all_positions, "_mc_seen", _market_closed_seen)
                    continue  # skip this position, try the next one
                else:
                    log.warning(f"Close failed #{pos.ticket} {pos.symbol}: {code}")

        # Check progress
        time.sleep(2)
        remaining = mt5.positions_get() or []
        if len(remaining) >= prev_count:
            no_progress += 1
            if no_progress >= 5:
                # v176: distinguish stuck-due-to-market-closed from genuinely stuck.
                # If all remaining are in the market-closed set, this is expected.
                _mc_seen = getattr(close_all_positions, "_mc_seen", set())
                _genuine_stuck = [p for p in remaining if p.ticket not in _mc_seen]
                if _genuine_stuck:
                    log.error(f"EOD: {len(_genuine_stuck)} positions STUCK -- no progress. Close manually in MT5!")
                else:
                    log.info(f"EOD: {len(remaining)} positions waiting for market to reopen -- will retry next session")
                return
        else:
            no_progress = 0

    remaining = mt5.positions_get() or []
    if remaining:
        # v176: market-closed positions are expected to remain -- don't error on them.
        _mc_seen = getattr(close_all_positions, "_mc_seen", set())
        _genuine_stuck = [p for p in remaining if p.ticket not in _mc_seen]
        if _genuine_stuck:
            log.error(f"EOD: {len(_genuine_stuck)} positions still open after {max_passes} passes -- close manually in MT5!")
        else:
            log.info(f"EOD: {len(remaining)} positions waiting for market to reopen -- will retry next session")

# ── AL BROOKS BAR ANALYSIS ────────────────────────────────────────────────────

def bar_close_pos(c: pd.Series) -> float:
    rng = c["high"] - c["low"]
    return (c["close"] - c["low"]) / rng if rng > 0 else 0.5

def is_strong_bull(c: pd.Series) -> bool:
    return bar_close_pos(c) >= (1 - STRONG_BAR)

def is_strong_bear(c: pd.Series) -> bool:
    return bar_close_pos(c) <= STRONG_BAR

def is_doji(c: pd.Series) -> bool:
    return 0.35 <= bar_close_pos(c) <= 0.65

def in_trading_range(df: pd.DataFrame) -> tuple[bool, float, float]:
    recent   = df.iloc[-RANGE_LOOKBACK:]
    rh       = float(recent["high"].max())
    rl       = float(recent["low"].min())
    mid      = (rh + rl) / 2
    is_range = ((rh - rl) / mid) < (RANGE_LOOKBACK * 0.0012)
    return is_range, rh, rl

# ── COORDINATOR: CONFIDENCE SCORING ───────────────────────────────────────────

def score_signal(signal: SetupSignal) -> tuple[int, list[str]]:
    """
    Score a signal 1-8 based on how many factors agree.
    More factors = more data for ML learning later.
    Returns (score, reasons_list).

    Factors:
    1. Signal detected
    2. 15m market structure agrees
    3. 5m Brooks bar agrees
    4. Optimal trading time (London/NY session)
    5. 1hr chart direction agrees
    6. Distance from daily high/low (not in middle)
    7. Volume/volatility spike (ATR above average)
    8. Not near a key level (clean setup)
    """
    score   = 1
    reasons = [f"+1 signal detected: {signal.setup_name}"]

    df_1h  = get_candles(signal.symbol, mt5.TIMEFRAME_H1, 30)
    df_15m = get_candles(signal.symbol, TF_15M, 30)
    df_5m  = get_candles(signal.symbol, TF_5M,  30)

    # ── Factor 1: 15m market structure ──
    # v167: INVERTED from previous logic.
    # Analyzer 7 finding: when 15m agreed with signal, WR was 47.9%. When 15m
    # was ranging or DISAGREED, WR was 59.0%. n=361, z=-1.69 (suggestive).
    # Logic post-hoc: Brooks counter-trend setups (double_bottom in a bull move,
    # double_top in a bear move) are reaction trades catching pullback exhaustion.
    # These are statistically higher-probability than buying breakouts late in
    # the trend. Reward the counter-trend setup, not the trend-following one.
    # NOTE: weaker statistical confidence (z=-1.69) -- fewer trades to be sure.
    # If this hurts post-deploy, revert just this factor.
    if df_15m is not None:
        direction_15m = market_direction(df_15m)
        if direction_15m == "range":
            score += 1
            reasons.append(f"+1 15m structure: ranging (clean reaction setup)")
        elif (signal.direction == "long"  and direction_15m == "bear") or \
             (signal.direction == "short" and direction_15m == "bull"):
            score += 1
            reasons.append(f"+1 15m structure counter-trend: {direction_15m} vs {signal.direction} (Brooks reversal)")
        else:
            reasons.append(f" 0 15m structure agrees with signal -- late-trend trade, lower probability")

    # ── Factor 2: 5m Brooks bar ──
    if df_5m is not None and len(df_5m) >= 5:
        candle_5m = df_5m.iloc[-2]
        if is_doji(candle_5m):
            reasons.append(f" 0 5m bar is doji -- no Brooks confirmation")
        elif (signal.direction == "long"  and is_strong_bull(candle_5m)) or \
             (signal.direction == "short" and is_strong_bear(candle_5m)):
            score += 1
            reasons.append(f"+1 5m Brooks bar confirms direction")
        else:
            reasons.append(f" 0 5m Brooks bar opposes direction")

    # ── Factor 3: Optimal trading time ──
    if is_optimal_time():
        score += 1
        reasons.append(f"+1 optimal trading window (London/NY session)")
    else:
        reasons.append(f" 0 outside optimal trading hours")

    # ── Factor 4: 1hr chart direction agrees ──
    if df_1h is not None and len(df_1h) >= 10:
        direction_1h = market_direction(df_1h)
        if (signal.direction == "long"  and direction_1h == "bull") or \
           (signal.direction == "short" and direction_1h == "bear"):
            score += 1
            reasons.append(f"+1 1hr chart direction: {direction_1h}")
        elif direction_1h == "range":
            reasons.append(f" 0 1hr chart: ranging")
        else:
            reasons.append(f" 0 1hr chart opposes signal")

    # ── Factor 5: Not in middle of daily range ──
    try:
        daily = get_candles(signal.symbol, mt5.TIMEFRAME_D1, 2)  # uses 10s cache
        if daily is not None and len(daily) >= 1:
            d_high = float(daily.iloc[-1]["high"])
            d_low  = float(daily.iloc[-1]["low"])
            d_range = d_high - d_low
            if d_range > 0:
                pos_in_range = (signal.entry - d_low) / d_range
                # Long near bottom (0-40%) or short near top (60-100%) = good
                if signal.direction == "long"  and pos_in_range < 0.4:
                    score += 1
                    reasons.append(f"+1 entry near daily low ({pos_in_range:.0%} of range)")
                elif signal.direction == "short" and pos_in_range > 0.6:
                    score += 1
                    reasons.append(f"+1 entry near daily high ({pos_in_range:.0%} of range)")
                else:
                    reasons.append(f" 0 entry in middle of daily range ({pos_in_range:.0%})")
    except Exception as _e:
        log.debug(f"score_signal daily range error: {_e}")

    # ── Factor 6: ATR spike (volatility above average = momentum) ──
    if df_15m is not None and len(df_15m) >= 20:
        recent_atr = float(df_15m.iloc[-2]["bar_range"])
        avg_atr    = float(df_15m.iloc[-20:-2]["bar_range"].mean())
        if avg_atr > 0 and recent_atr > avg_atr * 1.3:
            score += 1
            reasons.append(f"+1 volatility spike (bar {recent_atr:.1f} vs avg {avg_atr:.1f})")
        else:
            reasons.append(f" 0 normal volatility")

    # ── Factor 7: NEAR a key level (Brooks reaction setup) ──
    # v167: INVERTED from previous logic.
    # Analyzer 7 finding: when bot scored "+1 away from key levels (clean)" the
    # trade WR was 43%. When NOT scored (i.e. trade IS near a key level), WR was
    # 69.5%. n=361, z=-5.06 -- strongest single finding in the entire log.
    # Logic post-hoc: Brooks setups are reactions AT key levels -- that's the
    # whole point. A double_bottom in the middle of nowhere is noise pretending
    # to be a setup. A double_bottom at the prior day's low is the real thing.
    levels = get_key_levels(signal.symbol)
    if levels:
        nearest = nearest_key_level(signal.entry, levels, tol=0.002)
        if nearest is not None:
            score += 1
            reasons.append(f"+1 entry at key level: {nearest} (Brooks reaction)")
        else:
            reasons.append(f" 0 entry away from key levels -- likely noise setup")

    return score, reasons

def risk_from_score(base_risk: float, score: int) -> float:
    """Scale risk based on confidence score (1-8 scale)."""
    # Map score to multiplier: low score = tiny risk, high score = full risk
    multiplier = min(1.0, score / 6.0)  # score 6+ = full risk
    multiplier = max(0.125, multiplier)  # minimum 12.5% of base risk
    return round(base_risk * multiplier, 4)

# ── ADAPTIVE LEARNING ─────────────────────────────────────────────────────────

def get_setup_stats(setup_key: str) -> dict:
    """Get rolling stats for a specific setup (last 20 DECISIVE trades).
    BEs excluded entirely -- with ENABLE_BREAKEVEN=False, a BE is just
    EOD timing noise or spread rounding. No trading meaning.
    WR = W / (W + L). Streak counts consecutive losses only.
    """
    import time as _time
    # PERF: 30s TTL cache per setup_key -- called ~40x/min from adaptive_brooks_risk
    # and check_and_apply_learning. Stats change only when new outcomes appear.
    _cache_attr = f"_gss_cache_{setup_key.replace('|','_').replace('.','')}"
    _ts_attr    = f"_gss_ts_{setup_key.replace('|','_').replace('.','')}"
    _now_gss    = _time.monotonic()
    _cached     = getattr(get_setup_stats, _cache_attr, None)
    _cached_ts  = getattr(get_setup_stats, _ts_attr, 0)
    if _cached is not None and (_now_gss - _cached_ts) < 30:
        return _cached

    if not os.path.exists(LOG_FILE):
        return {}
    with open(LOG_FILE, encoding="utf-8") as f:
        trades = json.load(f)
    # Only win/loss -- BEs completely excluded from window
    decisive_outcomes = ("win", "eod_win", "loss", "eod_loss")
    # v181: exclude contaminated-day trades (May 4 etc.) from cooldown calc.
    # Same hygiene principle as training: bug-driven outcomes shouldn't
    # trigger cooldowns. Without this, May 4 losses kept the bot in a
    # cooldown loop -- every time a 1hr cooldown expired, the historical
    # losses were still in the rolling-20 window and re-triggered it.
    # Source of truth: CONTAMINATED_DAYS module constant.
    relevant = [t for t in trades if
                f"{t['strategy']}|{t['setup_name']}" == setup_key and
                t.get("outcome") in decisive_outcomes and
                not any(t.get("timestamp","").startswith(d) for d in CONTAMINATED_DAYS)
               ][-20:]
    if not relevant:
        return {}
    wins       = sum(1 for t in relevant if t["outcome"] in ("win", "eod_win"))
    losses     = sum(1 for t in relevant if t["outcome"] in ("loss", "eod_loss"))
    breakevens = 0  # excluded entirely
    decisive = wins + losses
    win_rate = round(wins / decisive * 100, 1) if decisive > 0 else 0.0

    # v183: load streak watermark -- losses BEFORE this timestamp don't count
    # toward the consecutive-loss streak. Set whenever set_cooldown() fires,
    # so once a cooldown has been served, those losses are "consumed" and
    # don't re-trigger cooldown immediately on the next check.
    # Without this: bot in permanent cooldown loop until a NEW winning trade
    # appears for the setup -- no way to ever recover from a 3-loss streak
    # except by trading the setup again, which the cooldown prevents.
    _watermark = None
    try:
        _state_for_watermark = load_state()
        _watermarks = _state_for_watermark.get("cooldown_streak_watermarks", {})
        _watermark_iso = _watermarks.get(setup_key)
        if _watermark_iso:
            _watermark = _watermark_iso  # ISO string compares lexicographically with timestamp prefix
    except Exception:
        pass

    # Loss streak -- clean, no BEs to worry about
    # Watermark filter: skip losses older than the most recent cooldown trigger
    streak = 0
    for t in reversed(relevant):
        if t["outcome"] in ("loss", "eod_loss"):
            # If we have a watermark, ignore losses that happened before it
            if _watermark is not None and t.get("timestamp", "") < _watermark[:19].replace("T", " "):
                # Loss is older than watermark -- treat as if streak broke
                break
            streak += 1
        else:
            break
    result = {
        "total":       len(relevant),
        "wins":        wins,
        "losses":      losses,
        "breakevens":  breakevens,
        "win_rate":    win_rate,
        "loss_streak": streak,
    }
    # Store in cache
    setattr(get_setup_stats, _cache_attr, result)
    setattr(get_setup_stats, _ts_attr, _now_gss)
    return result

def is_in_cooldown(setup_key: str) -> bool:
    """Check if a setup is currently in cooldown."""
    state = load_state()
    cooldowns = state.get("cooldowns", {})
    if setup_key not in cooldowns:
        return False
    cd_until = datetime.fromisoformat(cooldowns[setup_key])
    # Ensure timezone-aware comparison -- cooldowns stored as UTC isoformat
    _now_cd = datetime.now(timezone.utc)
    if cd_until.tzinfo is None:
        cd_until = cd_until.replace(tzinfo=timezone.utc)
    if _now_cd < cd_until:
        # v170: throttle log to once per minute per setup. The 15m bar doesn't
        # change for 15 minutes, so the same signal+cooldown rejection was
        # logging 900+ times per bar. Now logs once per minute per setup_key.
        _log_cache_attr = "_cooldown_log_cache"
        _log_cache = getattr(is_in_cooldown, _log_cache_attr, {})
        _last_logged = _log_cache.get(setup_key, 0)
        import time as _cd_t
        _now_mono = _cd_t.monotonic()
        if _now_mono - _last_logged > 60:
            remaining = int((cd_until - _now_cd).total_seconds() // 60)
            log.info(f"  {setup_key} in cooldown for {remaining} more minutes")
            _log_cache[setup_key] = _now_mono
            setattr(is_in_cooldown, _log_cache_attr, _log_cache)
        return True
    # Cooldown expired -- remove it
    del cooldowns[setup_key]
    state["cooldowns"] = cooldowns
    save_state(state)
    # v170: clear log cache when cooldown expires so the next one logs fresh
    _log_cache = getattr(is_in_cooldown, "_cooldown_log_cache", {})
    _log_cache.pop(setup_key, None)
    return False

def set_cooldown(setup_key: str):
    """Put a setup into cooldown for COOLDOWN_HOURS hours.

    v183: also save a "streak watermark" -- the timestamp at which this cooldown
    was set. get_setup_stats() will then count losses only AFTER this watermark,
    preventing the historical-losses-keep-retriggering-cooldown loop.

    With LOSS_STREAK_COOLDOWN=1 (validated by user stats), a single loss
    triggers cooldown. Without the watermark, that same loss would be in the
    rolling-20 window forever, re-triggering cooldown every time the previous
    one expired. Watermark says "I already paid for that loss" -- once consumed,
    it doesn't count again.
    """
    state = load_state()
    cooldowns = state.get("cooldowns", {})
    until = (datetime.now(timezone.utc) + timedelta(hours=COOLDOWN_HOURS)).isoformat()
    cooldowns[setup_key] = until
    state["cooldowns"]   = cooldowns
    # v183: watermark = now. Future streak checks ignore losses from before this.
    watermarks = state.get("cooldown_streak_watermarks", {})
    watermarks[setup_key] = datetime.now(timezone.utc).isoformat()
    state["cooldown_streak_watermarks"] = watermarks
    save_state(state)
    log.warning(f"  COOLDOWN set on {setup_key} for {COOLDOWN_HOURS}hrs")

def kelly_fraction(win_rate: float, rr_ratio: float = 1.0) -> float:
    """
    Calculate Kelly criterion optimal bet fraction.
    f* = W - (1-W)/R  where W=win_rate, R=reward/risk ratio
    We use quarter-Kelly for safety (Kelly is theoretically optimal
    but maximally aggressive -- quarter-Kelly gives 75% of growth
    with much lower variance).
    Returns fraction of capital to risk (0.0 to 1.0).
    """
    w = win_rate / 100.0
    if w <= 0 or rr_ratio <= 0:
        return 0.0
    kelly = w - (1.0 - w) / rr_ratio
    if kelly <= 0:
        return 0.0  # negative Kelly = don't trade (but we still trade for data)
    quarter_kelly = kelly * 0.25
    return min(quarter_kelly, 0.05)  # hard cap at 5% of capital

def correlated_kelly(signal, base_risk: float) -> float:
    """
    Thorp's correlated Kelly -- scales down risk when multiple correlated
    positions are open simultaneously. Three GER40 longs are NOT independent
    bets. The real Kelly for correlated positions is much smaller.
    Conversely when correlation is LOW, we can size up more than standard Kelly.
    """
    try:
        # 2s TTL cache -- positions only change when trades open/close (rare vs signal frequency)
        import time as _ck_time
        _ck_now = _ck_time.monotonic()
        _ck_cached = getattr(correlated_kelly, "_pos_cache", None)
        _ck_ts     = getattr(correlated_kelly, "_pos_ts", 0)
        if _ck_cached is None or (_ck_now - _ck_ts) > 2:
            _ck_cached = mt5.positions_get()
            setattr(correlated_kelly, "_pos_cache", _ck_cached)
            setattr(correlated_kelly, "_pos_ts", _ck_now)
        positions = _ck_cached
        if not positions:
            return base_risk  # no open positions, no correlation penalty

        # Count positions by direction per symbol group
        # GER40/US30/US100/UK100 are all correlated indices
        index_longs  = sum(1 for p in positions if p.type == 0)  # buy
        index_shorts = sum(1 for p in positions if p.type == 1)  # sell
        same_dir     = index_longs if signal.direction == "long" else index_shorts

        if same_dir == 0:
            # No correlated positions -- can size up slightly
            return min(base_risk * 1.1, RISK_BROOKS_MAX)

        # Correlation penalty -- each same-direction position reduces Kelly
        # 1 existing = 0.85x, 2 existing = 0.70x, 3+ = 0.50x
        penalty = {0: 1.0, 1: 0.85, 2: 0.70}.get(same_dir, 0.50)
        corr_risk = base_risk * penalty

        if same_dir >= 2:
            log.info(f"  Thorp corr penalty: {same_dir} same-dir positions "
                    f"-> risk x{penalty:.2f} ({base_risk:.3f}% -> {corr_risk:.3f}%)")
        return corr_risk
    except Exception as _e:
        log.debug(f"correlated_kelly error: {_e}")
        return base_risk

def get_current_regime(symbol: str = None) -> str:
    """
    Detect macro market regime across all symbols.
    Returns: trending_bull, trending_bear, ranging, volatile
    This is used to scale position sizes -- NOT to skip trades.
    """
    try:
        regimes = []
        symbols_to_check = ALL_SYMBOLS if symbol is None else [symbol]
        for sym in symbols_to_check[:2]:  # check max 2 symbols for speed
            df = get_candles(sym, TF_15M, 50)
            if df is not None:
                regimes.append(detect_regime(sym, TF_15M))

        if not regimes:
            return "unknown"

        # Count regime types
        bull_count  = sum(1 for r in regimes if r == "trending_bull")
        bear_count  = sum(1 for r in regimes if r == "trending_bear")
        range_count = sum(1 for r in regimes if r == "ranging")
        vol_count   = sum(1 for r in regimes if r == "volatile")

        total = len(regimes)
        if total == 0: return "ranging"  # safe default
        if bull_count / total >= 0.5:   return "trending_bull"
        if bear_count / total >= 0.5:   return "trending_bear"
        if vol_count / total >= 0.34:   return "volatile"
        if range_count / total >= 0.34: return "ranging"
        # Plurality vote -- use whichever regime has most symbols
        counts = {"trending_bull": bull_count, "trending_bear": bear_count,
                  "ranging": range_count, "volatile": vol_count}
        best = max(counts, key=counts.get)
        if counts[best] > 0:
            return best
        return "mixed"
    except Exception as _e:
        log.debug(f"get_current_regime error: {_e}")
        return "unknown"

def regime_risk_multiplier(regime: str, signal_direction: str) -> float:
    """
    Scale risk based on market regime and trade direction.
    We NEVER go to 0 (need data) but we scale way down in bad conditions.
    """
    multipliers = {
        # (regime, direction) -> multiplier
        # NEUTRAL until we have a full market cycle (bull + bear + ranging)
        # Current data is biased toward bear trend -- not enough to trust yet.
        # Revisit at day 30+ when we have 3000+ trades across multiple regimes.
        ("trending_bull",  "long"):  1.0,
        ("trending_bull",  "short"): 1.0,
        ("trending_bear",  "short"): 1.0,
        ("trending_bear",  "long"):  1.0,
        ("ranging",        "long"):  0.5,   # ranging = half size either way
        ("ranging",        "short"): 0.5,
        ("volatile",       "long"):  0.3,   # volatile = small, unpredictable
        ("volatile",       "short"): 0.3,
        ("mixed",          "long"):  0.7,
        ("mixed",          "short"): 0.7,
        ("unknown",        "long"):  1.0,
        ("unknown",        "short"): 1.0,
    }
    return multipliers.get((regime, signal_direction), 1.0)

def adaptive_brooks_risk(setup_key: str, signal=None) -> float:
    """
    Intelligent position sizing combining:
    1. Kelly criterion (mathematically optimal based on historical win rate)
    2. Regime multiplier (scale with/against market direction)
    3. Score-based scaling (existing system)
    4. Hard floor (never below minimum -- always collect data)
    """
    stats = get_setup_stats(setup_key)

    # Not enough data yet -- use base risk
    if not stats or stats["total"] < MIN_TRADES_TO_LEARN:
        return RISK_BROOKS_BASE

    wr = stats["win_rate"]

    # ── Kelly criterion ──────────────────────────────────────────────────
    # Estimate average RR ratio from recent trades
    rr = 1.0  # default 1:1
    if os.path.exists(LOG_FILE):
        try:
            # PERF: 60s TTL cache -- called per-signal for every setup, same frequency as get_setup_stats
            import time as _time_abr
            _rr_cache_key = f"_abr_rr_{setup_key.replace('|','_').replace('.','')}"
            _rr_ts_key    = f"_abr_rr_ts_{setup_key.replace('|','_').replace('.','')}"
            _now_abr      = _time_abr.monotonic()
            _rr_cached    = getattr(adaptive_brooks_risk, _rr_cache_key, None)
            _rr_cached_ts = getattr(adaptive_brooks_risk, _rr_ts_key, 0)
            if _rr_cached is None or (_now_abr - _rr_cached_ts) > 60:
                with open(LOG_FILE, encoding="utf-8") as f:
                    _all_trades_rr = json.load(f)
                _relevant_rr = [t for t in _all_trades_rr
                               if f"{t['strategy']}|{t['setup_name']}" == setup_key
                               and t.get("outcome") in ("win","loss","eod_win","eod_loss")][-20:]
                _rr_vals = [t.get("context",{}).get("rr_ratio", 1.0) for t in _relevant_rr
                            if t.get("context",{}).get("rr_ratio")]
                _rr_cached = sum(_rr_vals) / len(_rr_vals) if _rr_vals else 1.0
                setattr(adaptive_brooks_risk, _rr_cache_key, _rr_cached)
                setattr(adaptive_brooks_risk, _rr_ts_key, _now_abr)
            rr = _rr_cached
        except Exception as _e:
            log.debug(f"Feature block failed: {_e}")

    kelly = kelly_fraction(wr, rr)
    kelly_risk = kelly * 100  # convert to % of capital

    # v155 FIX: Kelly is unreliable when WR is in the 40-60% noise band with small n.
    # The 47.2% overall WR makes Kelly~0 for almost every setup, collapsing every
    # trade to RISK_BROOKS_MIN. Bypass Kelly in this band and use a setup-edge
    # multiplier off RISK_BROOKS_BASE instead. Kelly only kicks in when there's a
    # clear edge (>60% WR or n>=50 with significant separation from 50%).
    _kelly_unreliable = (
        stats["total"] < 50
        or (0.40 <= wr/100 <= 0.60 and stats["total"] < 100)
    )
    if _kelly_unreliable:
        # Use linear edge from 50% WR baseline, anchored on RISK_BROOKS_BASE
        # WR=50% -> 1.0x base, WR=60% -> 1.4x base, WR=40% -> 0.6x base
        edge_mult = 1.0 + (wr/100 - 0.50) * 4.0
        edge_mult = max(0.4, min(1.6, edge_mult))
        kelly_risk = RISK_BROOKS_BASE * edge_mult
        log.info(f"  {setup_key} Kelly bypassed (n={stats['total']} wr={wr}%) "
                 f"-> base*{edge_mult:.2f} = {kelly_risk:.3f}%")

    # ── Regime multiplier ────────────────────────────────────────────────
    regime_mult = 1.0
    if signal is not None:
        try:
            regime     = get_current_regime(signal.symbol)
            regime_mult = regime_risk_multiplier(regime, signal.direction)
        except Exception as _e:
            log.debug(f"Feature block failed: {_e}")

    # ── Combine: Kelly * regime, bounded by min/max ──────────────────────
    if kelly_risk <= 0:
        # Negative Kelly = losing setup mathematically
        # Still trade for data but at absolute minimum
        raw_risk = RISK_BROOKS_MIN
        log.info(f"  {setup_key} Kelly<0 (wr={wr}% rr={rr:.2f}) -> minimum risk {raw_risk}%")
    else:
        raw_risk = kelly_risk * regime_mult
        log.info(f"  {setup_key} Kelly={kelly_risk:.3f}% x regime={regime_mult:.1f} -> {raw_risk:.3f}%")

    # ── Thorp: correlated Kelly penalty ─────────────────────────────────────
    if signal is not None:
        raw_risk = correlated_kelly(signal, raw_risk)

    # ── Ensemble ML confidence multiplier ───────────────────────────────────
    # Uses calibrated probability from ensemble_predict (proper context, not dummy)
    # HIGH confidence WIN  -> 1.3x (bet more when ML agrees it will win)
    # HIGH confidence LOSS -> 0.1x (bet minimum when ML says it will lose)
    # low/no confidence    -> 1.0x (no adjustment)
    # NOTE: ensemble_predict is called with the signal's actual market context,
    # not a blank dummy -- the old code used {} which always returned 0.5 (never fired)
    try:
        if os.path.exists("ml_model.pkl") and signal is not None:
            # Cache CMC on signal object -- main loop reuses it, avoiding double MT5 reads
            if hasattr(signal, "_cached_ctx") and signal._cached_ctx:
                ctx_for_sizing = signal._cached_ctx
            else:
                ctx_for_sizing = capture_market_context(signal) if hasattr(signal, "symbol") else {}
                if hasattr(signal, "symbol"):
                    signal._cached_ctx = ctx_for_sizing
            ml_size_pred   = ensemble_predict(ctx_for_sizing)
            avg_p          = ml_size_pred.get("prob", 0.5)
            confidence     = ml_size_pred.get("confidence", "none")
            if ML_GATING_ENABLED and confidence == "HIGH":
                if avg_p >= 0.65:             # HIGH confidence WIN
                    raw_risk *= 1.3
                    log.info(f"  ML HIGH WIN ({avg_p:.0%}) -> risk x1.3")
                elif avg_p <= 0.35:           # HIGH confidence LOSS
                    raw_risk *= 0.1
                    raw_risk  = max(raw_risk, DATA_COLLECTION_RISK if DATA_COLLECTION_RISK > 0 else RISK_BROOKS_MIN)
                    log.info(f"  ML HIGH LOSS ({avg_p:.0%}) -> risk x0.1")
    except Exception as _e:
        log.debug(f"ML size adjustment error: {_e}")  # ML not available yet -- no adjustment

    # ── Losing streak penalty -- DATA ONLY, not active yet ──
    # streak_size_penalty logged in context. Will wire to sizing at day 14+

    # ── GER40 reduced risk until WR recovers ────────────────────────────────
    # GER40 currently 28% WR -- trade it but at 30% of normal risk
    # Has its own per-symbol ML model now (Option B) so won't poison US30/UK100
    # Auto-removes multiplier when GER40 WR > 50% over last 30 trades
    if signal is not None and getattr(signal, "symbol", "") == "GER40.cash":
        ger40_wr = 0.28  # default pessimistic
        try:
            # Use demo log for GER40 WR stats -- more data than live log
            _wr_log = (DEMO_LOG if os.path.exists(DEMO_LOG) else LOG_FILE) if LIVE_MODE else LOG_FILE
            # PERF: 60s TTL cache -- GER40 WR changes slowly, no need to reread every signal
            import time as _time_ger
            _ger_cache_key = "_abr_ger40_wr_cache"
            _ger_ts_key    = "_abr_ger40_wr_ts"
            _now_ger       = _time_ger.monotonic()
            _ger_cached    = getattr(adaptive_brooks_risk, _ger_cache_key, None)
            _ger_cached_ts = getattr(adaptive_brooks_risk, _ger_ts_key, 0)
            if _ger_cached is None or (_now_ger - _ger_cached_ts) > 60:
                if os.path.exists(_wr_log):
                    with open(_wr_log, encoding="utf-8") as _f:
                        _all_ger = json.load(_f)
                    ger_recent = [t for t in _all_ger[-60:]
                                 if t.get("symbol") == "GER40.cash"
                                 and t.get("outcome") in ("win", "loss", "eod_win", "eod_loss")
                                 and not t.get("random", False)           # exclude random-direction trades
                                 and (t.get("risk_pct") or 0) >= 0.02][-30:]  # exclude data-collection noise
                    if len(ger_recent) >= 15:
                        ger_w = sum(1 for t in ger_recent if t["outcome"] in ("win","eod_win"))
                        ger_d = sum(1 for t in ger_recent if t["outcome"] in ("win","eod_win","loss","eod_loss"))
                        _ger_cached = ger_w / max(ger_d, 1)
                    else:
                        _ger_cached = 0.28  # not enough data -- use pessimistic default
                else:
                    _ger_cached = 0.28
                setattr(adaptive_brooks_risk, _ger_cache_key, _ger_cached)
                setattr(adaptive_brooks_risk, _ger_ts_key, _now_ger)
            ger40_wr = _ger_cached
        except Exception as _e:
            log.debug(f"Feature block failed: {_e}")
        if ger40_wr < 0.55:  # raised from 0.50 -- GER40 at 39.6% WR (ml_report17)
            ger40_mult = 0.3   # 30% of normal risk until WR recovers above 55%
            log.info(f"  GER40 WR={ger40_wr:.0%} < 55% -> risk x{ger40_mult} (recovery mode)")
            raw_risk *= ger40_mult
        else:
            log.info(f"  GER40 WR={ger40_wr:.0%} >= 55% -> full risk (recovered)")

    # v155: GER40 hard cap (Section 1: 39.8% WR over 964 trades -- structural).
    # Soft Kelly penalty above isn't enough; clamp regardless.
    if signal is not None and getattr(signal, "symbol", "") == "GER40.cash":
        if raw_risk > GER40_HARD_RISK_CAP:
            log.info(f"  GER40 hard cap: {raw_risk:.3f}% -> {GER40_HARD_RISK_CAP}%")
            raw_risk = GER40_HARD_RISK_CAP

    # v157: Mon/Tue size penalty per handoff section 12 long-term roadmap.
    # ml_report25 day-of-week analysis: Mon=40.7% WR, Tue=42.9% WR vs Wed=49.6%,
    # Thu=53.4%, Fri=46.3%. Mon/Tue underperformance is structural (~700+ trades
    # each, large sample). Soft 20% size reduction reduces drawdown contribution
    # without disabling the days entirely (we still want the data + occasional
    # winners on those days, just at smaller stake).
    try:
        _dow = datetime.now(timezone.utc).weekday()  # 0=Mon, 1=Tue, 6=Sun
        if _dow in (0, 1):
            _dow_mult = 0.80
            _orig_dow = raw_risk
            raw_risk *= _dow_mult
            # Throttled log -- once per minute is enough
            _dow_key = "_dow_penalty_logged"
            _now_min_dow = datetime.now(timezone.utc).replace(second=0, microsecond=0)
            if getattr(adaptive_brooks_risk, _dow_key, None) != _now_min_dow:
                _day_name = "Monday" if _dow == 0 else "Tuesday"
                log.info(f"  {_day_name} penalty: risk x{_dow_mult} ({_orig_dow:.3f}% -> {raw_risk:.3f}%)")
                setattr(adaptive_brooks_risk, _dow_key, _now_min_dow)
    except Exception as _dow_e:
        log.debug(f"DOW penalty error: {_dow_e}")

    # Hard bounds
    risk = max(RISK_BROOKS_MIN, min(RISK_BROOKS_MAX, raw_risk))
    return round(risk, 4)

def check_and_apply_learning(setup_key: str) -> bool:
    """
    Check if this setup should be blocked due to learning.
    Returns False if it should be skipped.
    Also triggers cooldown if needed.
    """
    if is_in_cooldown(setup_key):
        return False

    stats = get_setup_stats(setup_key)
    if not stats:
        return True  # no data yet, allow

    # Consecutive loss streak check
    if stats["loss_streak"] >= LOSS_STREAK_COOLDOWN:
        log.warning(f"  {setup_key} -- {stats['loss_streak']} consecutive losses -> cooldown")
        set_cooldown(setup_key)
        return False

    # Win rate check (only after enough data)
    if stats["total"] >= MIN_TRADES_TO_LEARN and stats["win_rate"] <= WIN_RATE_COOL_THRESH:
        log.warning(f"  {setup_key} -- win rate {stats['win_rate']}% below threshold -> cooldown")
        set_cooldown(setup_key)
        return False

    return True

# ── AL BROOKS SETUPS ──────────────────────────────────────────────────────────

def brooks_trend_bar(symbol: str, tf, tf_name: str) -> Optional[SetupSignal]:
    df = get_candles(symbol, tf, 40)
    if df is None or len(df) < 10:
        return None
    direction = market_direction(df)
    if direction == "range":
        return None
    candle = df.iloc[-2]
    if direction == "bull" and is_strong_bull(candle):
        pb = df.iloc[-6:-2]
        if sum(1 for i in range(1, len(pb)) if pb.iloc[i]["close"] < pb.iloc[i-1]["close"]) < 2:
            return None
        entry = float(candle["high"]); sl = float(candle["low"])
        return SetupSignal(symbol=symbol, strategy=f"brooks_{tf_name}",
            setup_type="breakout_long", setup_name="trend_bar",
            entry=entry, stop_loss=sl, take_profit=entry + (entry - sl),
            direction="long", timestamp=str(candle["time"]))
    if direction == "bear" and is_strong_bear(candle):
        pb = df.iloc[-6:-2]
        if sum(1 for i in range(1, len(pb)) if pb.iloc[i]["close"] > pb.iloc[i-1]["close"]) < 2:
            return None
        entry = float(candle["low"]); sl = float(candle["high"])
        return SetupSignal(symbol=symbol, strategy=f"brooks_{tf_name}",
            setup_type="breakout_short", setup_name="trend_bar",
            entry=entry, stop_loss=sl, take_profit=entry - (sl - entry),
            direction="short", timestamp=str(candle["time"]))
    return None

def brooks_failed_bo(symbol: str, tf, tf_name: str) -> Optional[SetupSignal]:
    df = get_candles(symbol, tf, 30)
    if df is None or len(df) < 10:
        return None

    # Use tighter lookback -- only last 10 bars for swing levels
    lookback   = df.iloc[-12:-2]
    swing_high = float(lookback["high"].max())
    swing_low  = float(lookback["low"].min())
    candle     = df.iloc[-2]
    prev       = df.iloc[-3]

    c_high  = float(candle["high"])
    c_low   = float(candle["low"])
    c_close = float(candle["close"])
    p_high  = float(prev["high"])
    p_low   = float(prev["low"])

    # Sanity check: entry must be within 2% of current price
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        return None
    current_price = tick.bid

    # Failed bull BO: prev broke above swing high, candle closes back below
    if p_high > swing_high and c_close < swing_high and is_strong_bear(candle):
        entry = c_low
        sl    = c_high + (c_high - c_low) * 0.1  # 10% buffer above candle high
        dist  = sl - entry
        tp    = entry - dist
        # Sanity: entry must be close to current price
        if abs(entry - current_price) / current_price > 0.02:
            return None
        if dist <= 0:
            return None
        return SetupSignal(symbol=symbol, strategy=f"brooks_{tf_name}",
            setup_type="reversal_short", setup_name="failed_bo",
            entry=entry, stop_loss=sl, take_profit=tp,
            direction="short", timestamp=str(candle["time"]))

    # Failed bear BO: prev broke below swing low, candle closes back above
    if p_low < swing_low and c_close > swing_low and is_strong_bull(candle):
        entry = c_high
        sl    = c_low - (c_high - c_low) * 0.1
        dist  = entry - sl
        tp    = entry + dist
        if abs(entry - current_price) / current_price > 0.02:
            return None
        if dist <= 0:
            return None
        return SetupSignal(symbol=symbol, strategy=f"brooks_{tf_name}",
            setup_type="reversal_long", setup_name="failed_bo",
            entry=entry, stop_loss=sl, take_profit=tp,
            direction="long", timestamp=str(candle["time"]))

    return None

def brooks_two_leg(symbol: str, tf, tf_name: str) -> Optional[SetupSignal]:
    df = get_candles(symbol, tf, 40)
    if df is None or len(df) < 15:
        return None
    direction = market_direction(df)
    if direction == "range":
        return None
    candle  = df.iloc[-2]
    ema     = float(candle["ema20"])
    recent  = df.iloc[-8:-2]
    if direction == "bull":
        near_ema = abs(float(candle["low"]) - ema) / ema < 0.003
        lows     = recent["low"].values
        leg1 = any(lows[i] < lows[i-1] for i in range(1, 4))
        leg2 = any(lows[i] < lows[i-1] for i in range(4, len(lows)))
        if near_ema and leg1 and leg2 and is_strong_bull(candle):
            entry = float(candle["high"])
            sl    = float(recent["low"].min())
            return SetupSignal(symbol=symbol, strategy=f"brooks_{tf_name}",
                setup_type="reversal_long", setup_name="two_leg_pullback",
                entry=entry, stop_loss=sl, take_profit=entry + (entry - sl),
                direction="long", timestamp=str(candle["time"]))
    if direction == "bear":
        near_ema = abs(float(candle["high"]) - ema) / ema < 0.003
        highs    = recent["high"].values
        leg1 = any(highs[i] > highs[i-1] for i in range(1, 4))
        leg2 = any(highs[i] > highs[i-1] for i in range(4, len(highs)))
        if near_ema and leg1 and leg2 and is_strong_bear(candle):
            entry = float(candle["low"])
            sl    = float(recent["high"].max())
            return SetupSignal(symbol=symbol, strategy=f"brooks_{tf_name}",
                setup_type="reversal_short", setup_name="two_leg_pullback",
                entry=entry, stop_loss=sl, take_profit=entry - (sl - entry),
                direction="short", timestamp=str(candle["time"]))
    return None

def brooks_range_fade(symbol: str, tf, tf_name: str) -> Optional[SetupSignal]:
    df = get_candles(symbol, tf, 40)
    if df is None or len(df) < RANGE_LOOKBACK + 5:
        return None
    is_range, rh, rl = in_trading_range(df)
    if not is_range:
        return None
    rng    = rh - rl
    zone   = rng * 0.15
    candle = df.iloc[-2]
    c_close = float(candle["close"])
    if c_close >= (rh - zone) and is_strong_bear(candle):
        entry = float(candle["low"]); sl = rh + (rng * 0.1)
        return SetupSignal(symbol=symbol, strategy=f"brooks_{tf_name}",
            setup_type="reversal_short", setup_name="range_fade",
            entry=entry, stop_loss=sl, take_profit=entry - (sl - entry),
            direction="short", timestamp=str(candle["time"]))
    if c_close <= (rl + zone) and is_strong_bull(candle):
        entry = float(candle["high"]); sl = rl - (rng * 0.1)
        return SetupSignal(symbol=symbol, strategy=f"brooks_{tf_name}",
            setup_type="reversal_long", setup_name="range_fade",
            entry=entry, stop_loss=sl, take_profit=entry + (entry - sl),
            direction="long", timestamp=str(candle["time"]))
    return None

def brooks_wedge(symbol: str, tf, tf_name: str) -> Optional[SetupSignal]:
    """
    Rising wedge (bearish) or falling wedge (bullish).
    Price makes higher highs AND higher lows but converging -- wedge shape.
    Break below lower trendline = sell. Break above upper = buy.
    """
    df = get_candles(symbol, tf, 30)
    if df is None or len(df) < 15:
        return None
    candle = df.iloc[-2]
    recent = df.iloc[-10:-2]
    highs  = recent["high"].values
    lows   = recent["low"].values
    # Rising wedge: highs rising, lows rising but slower (converging)
    highs_rising = highs[-1] > highs[0]
    lows_rising  = lows[-1]  > lows[0]
    high_slope   = (highs[-1] - highs[0]) / len(highs)
    low_slope    = (lows[-1]  - lows[0])  / len(lows)
    if highs_rising and lows_rising and low_slope > high_slope and is_strong_bear(candle):
        entry = float(candle["low"]); sl = float(candle["high"])
        dist  = sl - entry
        if dist <= 0: return None
        tick = mt5.symbol_info_tick(symbol)
        if tick and abs(entry - tick.bid) / tick.bid > 0.015: return None
        return SetupSignal(symbol=symbol, strategy=f"brooks_{tf_name}",
            setup_type="reversal_short", setup_name="wedge",
            entry=entry, stop_loss=sl, take_profit=entry - dist,
            direction="short", timestamp=str(candle["time"]))
    # Falling wedge: highs falling, lows falling but slower (converging)
    highs_falling = highs[-1] < highs[0]
    lows_falling  = lows[-1]  < lows[0]
    if highs_falling and lows_falling and abs(low_slope) > abs(high_slope) and is_strong_bull(candle):
        entry = float(candle["high"]); sl = float(candle["low"])
        dist  = entry - sl
        if dist <= 0: return None
        tick = mt5.symbol_info_tick(symbol)
        if tick and abs(entry - tick.bid) / tick.bid > 0.015: return None
        return SetupSignal(symbol=symbol, strategy=f"brooks_{tf_name}",
            setup_type="reversal_long", setup_name="wedge",
            entry=entry, stop_loss=sl, take_profit=entry + dist,
            direction="long", timestamp=str(candle["time"]))
    return None

def brooks_double_top_bottom(symbol: str, tf, tf_name: str) -> Optional[SetupSignal]:
    """
    Double top: two peaks at similar level = sell on second peak rejection.
    Double bottom: two troughs at similar level = buy on second trough rejection.
    """
    df = get_candles(symbol, tf, 30)
    if df is None or len(df) < 15:
        return None
    candle = df.iloc[-2]
    recent = df.iloc[-15:-2]
    highs  = recent["high"].values
    lows   = recent["low"].values
    first_high = float(recent.iloc[:7]["high"].max())
    second_high = float(recent.iloc[7:]["high"].max())
    first_low  = float(recent.iloc[:7]["low"].min())
    second_low = float(recent.iloc[7:]["low"].min())
    tolerance  = 0.003  # 0.3% tolerance for double top/bottom
    # Double top
    if abs(first_high - second_high) / first_high < tolerance and is_strong_bear(candle):
        entry = float(candle["low"]); sl = second_high * 1.002
        dist  = sl - entry
        if dist <= 0: return None
        tick = mt5.symbol_info_tick(symbol)
        if tick and abs(entry - tick.bid) / tick.bid > 0.015: return None
        return SetupSignal(symbol=symbol, strategy=f"brooks_{tf_name}",
            setup_type="reversal_short", setup_name="double_top",
            entry=entry, stop_loss=sl, take_profit=entry - dist,
            direction="short", timestamp=str(candle["time"]))
    # Double bottom
    if abs(first_low - second_low) / first_low < tolerance and is_strong_bull(candle):
        entry = float(candle["high"]); sl = second_low * 0.998
        dist  = entry - sl
        if dist <= 0: return None
        tick = mt5.symbol_info_tick(symbol)
        if tick and abs(entry - tick.bid) / tick.bid > 0.015: return None
        return SetupSignal(symbol=symbol, strategy=f"brooks_{tf_name}",
            setup_type="reversal_long", setup_name="double_bottom",
            entry=entry, stop_loss=sl, take_profit=entry + dist,
            direction="long", timestamp=str(candle["time"]))
    return None

def brooks_bar_reversal(symbol: str, tf, tf_name: str) -> Optional[SetupSignal]:
    """
    Single strong reversal bar at a key level (EMA, swing high/low).
    Strong bull bar after touching key support = buy.
    Strong bear bar after touching key resistance = sell.
    """
    df = get_candles(symbol, tf, 30)
    if df is None or len(df) < 15:
        return None
    candle  = df.iloc[-2]
    ema     = float(candle["ema20"])
    c_low   = float(candle["low"])
    c_high  = float(candle["high"])
    recent  = df.iloc[-15:-2]
    s_high  = float(recent["high"].max())
    s_low   = float(recent["low"].min())
    near_ema_tol = 0.003
    near_level   = 0.002
    tick = mt5.symbol_info_tick(symbol)
    if tick is None: return None
    # Bull reversal at support (EMA or swing low)
    near_support = (abs(c_low - ema) / ema < near_ema_tol or
                    abs(c_low - s_low) / s_low < near_level)
    if near_support and is_strong_bull(candle):
        entry = c_high; sl = c_low - (c_high - c_low) * 0.1
        dist  = entry - sl
        if dist <= 0 or abs(entry - tick.bid) / tick.bid > 0.015: return None
        return SetupSignal(symbol=symbol, strategy=f"brooks_{tf_name}",
            setup_type="reversal_long", setup_name="bar_reversal",
            entry=entry, stop_loss=sl, take_profit=entry + dist,
            direction="long", timestamp=str(candle["time"]))
    # Bear reversal at resistance (EMA or swing high)
    near_resist = (abs(c_high - ema) / ema < near_ema_tol or
                   abs(c_high - s_high) / s_high < near_level)
    if near_resist and is_strong_bear(candle):
        entry = c_low; sl = c_high + (c_high - c_low) * 0.1
        dist  = sl - entry
        if dist <= 0 or abs(entry - tick.bid) / tick.bid > 0.015: return None
        return SetupSignal(symbol=symbol, strategy=f"brooks_{tf_name}",
            setup_type="reversal_short", setup_name="bar_reversal",
            entry=entry, stop_loss=sl, take_profit=entry - dist,
            direction="short", timestamp=str(candle["time"]))
    return None

def brooks_climactic_reversal(symbol: str, tf, tf_name: str) -> Optional[SetupSignal]:
    """
    Climactic exhaustion: very large bar (3x+ average) in trend direction
    followed by a reversal bar. Market exhausted, reversal likely.
    """
    df = get_candles(symbol, tf, 30)
    if df is None or len(df) < 10:
        return None
    candle   = df.iloc[-2]
    prev     = df.iloc[-3]
    avg_range = float(df.iloc[-20:-3]["bar_range"].mean())
    if avg_range == 0: return None
    prev_range = float(prev["bar_range"])
    # Previous bar was climactic (very large)
    is_climactic = prev_range > avg_range * 2.5
    if not is_climactic:
        return None
    tick = mt5.symbol_info_tick(symbol)
    if tick is None: return None
    # Climactic bull bar followed by bear reversal
    if bool(prev["green"]) and is_strong_bear(candle):
        entry = float(candle["low"]); sl = float(candle["high"])
        dist  = sl - entry
        if dist <= 0 or abs(entry - tick.bid) / tick.bid > 0.015: return None
        return SetupSignal(symbol=symbol, strategy=f"brooks_{tf_name}",
            setup_type="reversal_short", setup_name="climactic_reversal",
            entry=entry, stop_loss=sl, take_profit=entry - dist,
            direction="short", timestamp=str(candle["time"]))
    # Climactic bear bar followed by bull reversal
    if not bool(prev["green"]) and is_strong_bull(candle):
        entry = float(candle["high"]); sl = float(candle["low"])
        dist  = entry - sl
        if dist <= 0 or abs(entry - tick.bid) / tick.bid > 0.015: return None
        return SetupSignal(symbol=symbol, strategy=f"brooks_{tf_name}",
            setup_type="reversal_long", setup_name="climactic_reversal",
            entry=entry, stop_loss=sl, take_profit=entry + dist,
            direction="long", timestamp=str(candle["time"]))
    return None

def brooks_first_pullback(symbol: str, tf, tf_name: str) -> Optional[SetupSignal]:
    """
    First pullback after a strong breakout.
    Price breaks a swing high/low strongly, then pulls back 1-3 bars,
    then shows a reversal bar = enter in breakout direction.
    """
    df = get_candles(symbol, tf, 30)
    if df is None or len(df) < 15:
        return None
    direction = market_direction(df)
    if direction == "range":
        return None
    candle = df.iloc[-2]
    recent = df.iloc[-8:-2]
    tick   = mt5.symbol_info_tick(symbol)
    if tick is None: return None
    if direction == "bull":
        # Recent high broke above prior structure
        prior_high = float(df.iloc[-15:-8]["high"].max())
        recent_high = float(recent["high"].max())
        if recent_high <= prior_high: return None
        # Current candle is a pullback bar then resumes
        if is_strong_bull(candle) and float(candle["low"]) > prior_high:
            entry = float(candle["high"]); sl = float(candle["low"])
            dist  = entry - sl
            if dist <= 0 or abs(entry - tick.bid) / tick.bid > 0.015: return None
            return SetupSignal(symbol=symbol, strategy=f"brooks_{tf_name}",
                setup_type="breakout_long", setup_name="first_pullback",
                entry=entry, stop_loss=sl, take_profit=entry + dist,
                direction="long", timestamp=str(candle["time"]))
    if direction == "bear":
        prior_low  = float(df.iloc[-15:-8]["low"].min())
        recent_low = float(recent["low"].min())
        if recent_low >= prior_low: return None
        if is_strong_bear(candle) and float(candle["high"]) < prior_low:
            entry = float(candle["low"]); sl = float(candle["high"])
            dist  = sl - entry
            if dist <= 0 or abs(entry - tick.bid) / tick.bid > 0.015: return None
            return SetupSignal(symbol=symbol, strategy=f"brooks_{tf_name}",
                setup_type="breakout_short", setup_name="first_pullback",
                entry=entry, stop_loss=sl, take_profit=entry - dist,
                direction="short", timestamp=str(candle["time"]))
    return None

def brooks_inside_bars(symbol: str, tf, tf_name: str) -> Optional[SetupSignal]:
    """
    ii or iii pattern: 2-3 consecutive inside bars (each within prior range).
    Compression before expansion. Enter on break of the pattern high/low.
    """
    df = get_candles(symbol, tf, 30)
    if df is None or len(df) < 10:
        return None
    c1 = df.iloc[-2]  # last closed
    c2 = df.iloc[-3]  # one before
    c3 = df.iloc[-4]  # two before
    tick = mt5.symbol_info_tick(symbol)
    if tick is None: return None
    # ii pattern: c1 inside c2
    ii = (float(c1["high"]) < float(c2["high"]) and
          float(c1["low"])  > float(c2["low"]))
    # iii pattern: c1 inside c2 inside c3
    iii = ii and (float(c2["high"]) < float(c3["high"]) and
                  float(c2["low"])  > float(c3["low"]))
    if not ii:
        return None
    pattern_high = float(c2["high"]) if ii and not iii else float(c3["high"])
    pattern_low  = float(c2["low"])  if ii and not iii else float(c3["low"])
    setup_name   = "iii_pattern" if iii else "ii_pattern"
    direction    = market_direction(df)
    if direction == "bull":
        entry = pattern_high; sl = pattern_low
        dist  = entry - sl
        if dist <= 0 or abs(entry - tick.bid) / tick.bid > 0.02: return None
        return SetupSignal(symbol=symbol, strategy=f"brooks_{tf_name}",
            setup_type="breakout_long", setup_name=setup_name,
            entry=entry, stop_loss=sl, take_profit=entry + dist,
            direction="long", timestamp=str(c1["time"]))
    if direction == "bear":
        entry = pattern_low; sl = pattern_high
        dist  = sl - entry
        if dist <= 0 or abs(entry - tick.bid) / tick.bid > 0.02: return None
        return SetupSignal(symbol=symbol, strategy=f"brooks_{tf_name}",
            setup_type="breakout_short", setup_name=setup_name,
            entry=entry, stop_loss=sl, take_profit=entry - dist,
            direction="short", timestamp=str(c1["time"]))
    return None

def detect_regime(symbol: str, tf) -> str:
    """
    Hedge fund regime detection -- determines market regime with higher precision.
    Uses multiple timeframes and indicators.

    Returns: "trending_bull" | "trending_bear" | "ranging" | "volatile"

    Trending -> use trend following setups (trend_bar, first_pullback, two_leg)
    Ranging  -> use mean reversion setups (range_fade, double_top/bottom, bar_reversal)
    Volatile -> use reversal setups (climactic_reversal, failed_bo, wedge)
    """
    # 30s TTL cache -- regime doesn't change tick-to-tick
    # Called up to 16x per iteration without cache (4 symbols x 2 TFs x 2 paths)
    import time as _dr_time
    _dr_key    = f"_dr_{symbol}_{tf}"
    _dr_ts_key = f"_dr_ts_{symbol}_{tf}"
    _dr_now    = _dr_time.monotonic()
    _dr_cached = getattr(detect_regime, _dr_key, None)
    if _dr_cached is not None and (_dr_now - getattr(detect_regime, _dr_ts_key, 0)) < 30:
        return _dr_cached
    def _cache_and_return(result):
        setattr(detect_regime, _dr_key, result)
        setattr(detect_regime, _dr_ts_key, _dr_now)
        return result

    df     = get_candles(symbol, tf, 50)
    df_1h  = get_candles(symbol, mt5.TIMEFRAME_H1, 30)
    if df is None or len(df) < 30:
        return _cache_and_return("ranging")

    # ── ADX-like trend strength ──
    highs  = df["high"].values[-20:]
    lows   = df["low"].values[-20:]
    closes = df["close"].values[-20:]
    ranges = [highs[i] - lows[i] for i in range(len(highs))]
    atr    = sum(ranges) / len(ranges) if ranges else 1

    # Directional movement
    up_moves   = [max(highs[i] - highs[i-1], 0) for i in range(1, len(highs))]
    down_moves = [max(lows[i-1] - lows[i], 0) for i in range(1, len(lows))]
    avg_up     = sum(up_moves) / len(up_moves) if up_moves else 0
    avg_down   = sum(down_moves) / len(down_moves) if down_moves else 0.001
    dx         = abs(avg_up - avg_down) / (avg_up + avg_down) * 100 if (avg_up + avg_down) > 0 else 0

    # ── Volatility check ──
    recent_range  = float(df.iloc[-3:]["bar_range"].mean())
    avg_range     = float(df.iloc[-20:-3]["bar_range"].mean())
    is_volatile   = recent_range > avg_range * 2.0

    if is_volatile:
        return _cache_and_return("volatile")

    # ── Trend vs range ──
    direction = market_direction(df)
    # Also check 1hr for confirmation
    direction_1h = market_direction(df_1h) if df_1h is not None else "range"

    # Strong trend: dx > 20 with direction confirmation
    if dx > 20:
        if direction == "bull" or direction_1h == "bull":
            return _cache_and_return("trending_bull")
        if direction == "bear" or direction_1h == "bear":
            return _cache_and_return("trending_bear")

    # Weak trend: dx 10-20, use price direction as tiebreaker
    if dx > 10:
        if direction == "bull":
            return _cache_and_return("trending_bull")
        if direction == "bear":
            return _cache_and_return("trending_bear")

    return _cache_and_return("ranging")

def regime_stable(symbol: str, tf, min_consecutive_checks: int = 3,
                  poll_separation_seconds: int = 60) -> bool:
    """
    v165 FIX: regime_stable now actually enforces time separation between polls.

    Previous bug: detect_regime caches results for 30s. regime_stable was being
    called many times per second within the trade loop, all returning the same
    cached value, deque filling with identical entries, regime_stable always
    returning True after 3 fast calls. The "stability" check was meaningless.

    Now: each poll appended to history is timestamped. We require N polls each
    at least `poll_separation_seconds` apart, all returning the same regime,
    before regime is considered stable. Default = 3 polls × 60s = 3 minutes
    of regime persistence required.

    Returns True if stable OR if no history yet (first run = trust detect_regime).
    """
    from collections import deque
    import time as _rs_time
    _hist_key = f"_regime_hist_{symbol}_{tf}"
    _hist     = getattr(regime_stable, _hist_key, None)
    if _hist is None:
        _hist = deque(maxlen=20)
        setattr(regime_stable, _hist_key, _hist)
    current = detect_regime(symbol, tf)
    now_ts  = _rs_time.monotonic()
    # Only append if last entry is >= poll_separation_seconds old
    # OR if regime changed (always record state changes immediately)
    if not _hist or (now_ts - _hist[-1][1] >= poll_separation_seconds) or _hist[-1][0] != current:
        _hist.append((current, now_ts))
    if len(_hist) < min_consecutive_checks:
        return True   # not enough history -- trust the call
    last_n = list(_hist)[-min_consecutive_checks:]
    if not all(r[0] == current for r in last_n):
        return False
    span = last_n[-1][1] - last_n[0][1]
    return span >= (min_consecutive_checks - 1) * poll_separation_seconds * 0.9

# Setups grouped by regime
TRENDING_SETUPS  = {"trend_bar", "first_pullback", "two_leg_pullback", "wedge"}
RANGING_SETUPS   = {"range_fade", "double_top", "double_bottom", "bar_reversal", "ii_pattern", "iii_pattern"}
VOLATILE_SETUPS  = {"climactic_reversal", "failed_bo", "wedge", "double_top", "double_bottom"}

# v174: Setup priority cache for zone deduplication.
# Populated from win_stats.json at startup and refreshed by update_win_stats().
# Maps "strategy|setup_name" -> (win_rate, total_trades).
# Used by merge_zone_signals to pick the best signal in a cluster.
_setup_priority_cache: dict = {}

def _setup_priority(signal) -> float:
    """
    Priority score for picking which signal to keep when multiple cluster at the
    same zone. Higher = better.

    Logic:
    - If we have >=20 historical trades, use actual win_rate (0-100).
    - Otherwise fall back to a Brooks-principle default (15m > 5m, range_fade
      and trend setups score above bar_reversal/wedge which are weaker).
    - Final tiebreaker: signal index (deterministic).
    """
    key = f"{signal.strategy}|{signal.setup_name}"
    cached = _setup_priority_cache.get(key)
    if cached and cached[1] >= 20:  # require 20+ trades for stat significance
        return float(cached[0])

    # Default priorities -- rough Brooks-principle ranking when WR data is thin.
    DEFAULTS = {
        "range_fade":         70,
        "iii_pattern":        65,
        "trend_bar":          60,
        "two_leg_pullback":   58,
        "first_pullback":     55,
        "ii_pattern":         50,
        "double_bottom":      48,
        "double_top":         48,
        "climactic_reversal": 45,
        "wedge":              42,
        "bar_reversal":       38,
        "failed_bo":          35,
    }
    base = DEFAULTS.get(signal.setup_name, 50)
    # 15m setups generally have less noise than 5m
    if signal.strategy == "brooks_15m":
        base += 3
    return float(base)

def merge_zone_signals(signals: list) -> tuple[list, dict]:
    """
    v174 REWRITE: zone DEDUPLICATION, not zone splitting.

    Old behavior (v161-v173): if 3 signals fire at the same price zone, place
    3 positions at 1/3 risk each. Result: same total risk but 3× spread cost,
    3 positions to manage, and per-symbol cap=2 capped it at 2 positions for
    only 2/3 of intended risk.

    New behavior (v174): if N signals fire at the same zone (same direction,
    within 0.3% of each other), keep ONLY the highest-priority signal and drop
    the others. The kept signal trades at FULL risk. One zone = one position.

    Priority: actual historical WR if >=20 trades, else Brooks-principle defaults.

    Returns: (kept_signals_list, multipliers_dict {idx: 1.0})
    Signature kept for backward compat with main loop; multipliers always 1.0.
    """
    if len(signals) <= 1:
        return signals, {0: 1.0}

    used    = set()
    groups  = []  # list of lists of signal indices

    for i, sig in enumerate(signals):
        if i in used:
            continue
        group = [i]
        used.add(i)
        for j, other in enumerate(signals):
            if j in used or j == i:
                continue
            price_diff = abs(sig.entry - other.entry) / sig.entry
            if other.direction == sig.direction and price_diff < 0.003:
                group.append(j)
                used.add(j)
        groups.append(group)

    kept_signals = []
    risk_multipliers = {}
    for group in groups:
        if len(group) == 1:
            kept_signals.append(signals[group[0]])
            risk_multipliers[len(kept_signals) - 1] = 1.0
            continue

        # Multiple signals in zone -- pick the one with highest priority.
        best_idx = max(group, key=lambda i: (_setup_priority(signals[i]), -i))
        winner = signals[best_idx]
        kept_signals.append(winner)
        risk_multipliers[len(kept_signals) - 1] = 1.0

        # Log the dedup decision once per zone composition (with throttle).
        sig0 = signals[group[0]]
        names_sorted = "+".join(sorted(signals[i].setup_name for i in group))
        sym_tf_tag = f"{getattr(sig0, 'symbol', '?')}:{getattr(sig0, 'strategy', '?')}"
        zone_key = f"{sym_tf_tag}|{sig0.direction}:{names_sorted}"
        _seen = getattr(merge_zone_signals, "_seen_zones", set())
        if zone_key not in _seen:
            dropped = [signals[i].setup_name for i in group if i != best_idx]
            log.info(f"  Zone dedup ({len(group)} signals): kept "
                     f"{winner.setup_name} (priority={_setup_priority(winner):.0f}), "
                     f"dropped {'+'.join(dropped)}")
            _seen.add(zone_key)
            setattr(merge_zone_signals, "_seen_zones", _seen)
            if len(_seen) > 50:
                _seen.clear()

    return kept_signals, risk_multipliers

def dedupe_cross_tf(signals: list) -> list:
    """
    v174: cross-timeframe zone dedup. Called AFTER both 5m and 15m signals are
    collected for a symbol. If a 5m signal and a 15m signal cluster at the same
    zone (same direction, within 0.3%), keep only the higher-priority one.

    Without this, run_brooks dedupes within-tf but a 5m wedge and 15m wedge at
    the same level would both reach the main loop and both get placed.
    """
    if len(signals) <= 1:
        return signals

    used = set()
    kept = []
    dropped_pairs = []  # for logging

    for i, sig in enumerate(signals):
        if i in used:
            continue
        cluster = [i]
        used.add(i)
        for j, other in enumerate(signals):
            if j in used or j == i:
                continue
            if other.direction != sig.direction:
                continue
            price_diff = abs(sig.entry - other.entry) / sig.entry
            if price_diff < 0.003:
                cluster.append(j)
                used.add(j)

        if len(cluster) == 1:
            kept.append(signals[cluster[0]])
            continue

        best_idx = max(cluster, key=lambda i: (_setup_priority(signals[i]), -i))
        kept.append(signals[best_idx])
        for ci in cluster:
            if ci != best_idx:
                dropped_pairs.append((signals[ci].strategy, signals[ci].setup_name,
                                       signals[best_idx].strategy, signals[best_idx].setup_name))

    if dropped_pairs:
        # Throttle by composition so we don't spam.
        comp_key = "|".join(sorted(f"{a[0]}:{a[1]}->{a[2]}:{a[3]}" for a in dropped_pairs))
        _seen = getattr(dedupe_cross_tf, "_seen", set())
        if comp_key not in _seen:
            for sa, na, sb, nb in dropped_pairs:
                log.info(f"  Cross-tf dedup: dropped {sa}|{na}, kept {sb}|{nb} (same zone)")
            _seen.add(comp_key)
            setattr(dedupe_cross_tf, "_seen", _seen)
            if len(_seen) > 50:
                _seen.clear()

    return kept

def run_brooks(symbol: str, tf, tf_name: str) -> list[SetupSignal]:
    """
    Run all Brooks setups with regime filtering and zone merging.
    Only runs setups appropriate for the current market regime.
    Merges duplicate zone signals into single superior trades.
    """
    regime  = detect_regime(symbol, tf)
    signals = []

    # Select detectors based on regime
    if regime in ("trending_bull", "trending_bear"):
        active_setups = TRENDING_SETUPS | VOLATILE_SETUPS
    elif regime == "volatile":
        active_setups = VOLATILE_SETUPS
    else:  # ranging
        active_setups = RANGING_SETUPS | VOLATILE_SETUPS

    all_detectors = {
        "trend_bar":           brooks_trend_bar,
        "failed_bo":           brooks_failed_bo,
        "two_leg_pullback":    brooks_two_leg,
        "range_fade":          brooks_range_fade,
        "wedge":               brooks_wedge,
        "double_top":          brooks_double_top_bottom,
        "double_bottom":       brooks_double_top_bottom,
        "bar_reversal":        brooks_bar_reversal,
        "climactic_reversal":  brooks_climactic_reversal,
        "first_pullback":      brooks_first_pullback,
        "ii_pattern":          brooks_inside_bars,
        "iii_pattern":         brooks_inside_bars,
    }

    # Only run regime-appropriate detectors (deduplicated)
    run_fns = set()
    for setup_name, fn in all_detectors.items():
        if setup_name in active_setups:
            run_fns.add(fn)

    for fn in run_fns:
        try:
            s = fn(symbol, tf, tf_name)
            if s:
                signals.append(s)
        except Exception as e:
            log.warning(f"Brooks error {fn.__name__} {symbol}: {e}")

    # Separate by direction then apply zone risk reduction
    long_sigs  = [s for s in signals if s.direction == "long"]
    short_sigs = [s for s in signals if s.direction == "short"]
    long_sigs,  long_mults  = merge_zone_signals(long_sigs)
    short_sigs, short_mults = merge_zone_signals(short_sigs)

    # Combine -- short indices offset by number of longs
    all_sigs  = long_sigs + short_sigs
    all_mults = {}
    for i, m in long_mults.items():
        all_mults[i] = m
    for i, m in short_mults.items():
        all_mults[i + len(long_sigs)] = m

    # Ensure every index has a multiplier
    for i in range(len(all_sigs)):
        if i not in all_mults:
            all_mults[i] = 1.0

    # ── Ranging regime filters ──
    if regime == "ranging":
        # Get daily range for position filter
        try:
            daily = get_candles(symbol, mt5.TIMEFRAME_D1, 2)  # 10s cache -- avoid uncached D1 read per signal
            if daily is not None and len(daily) >= 1:
                d_high = float(daily.iloc[-1]["high"])
                d_low  = float(daily.iloc[-1]["low"])
                d_range = d_high - d_low
                if d_range > 0:
                    filtered = []
                    filtered_mults = {}
                    for i, sig in enumerate(all_sigs):
                        pos_in_range = (sig.entry - d_low) / d_range
                        # No ranging position filter -- ML learns from all positions
                        # pos_in_range logged as context feature for model to learn from
                        # Tighten TP to 0.5x risk in ranging (smaller targets, faster profits)
                        risk = abs(sig.entry - sig.stop_loss)
                        # TP set to 1.0R minimum -- below this fails the RR>=1.0 hard gate
                        # (was 0.75R but that caused all ranging signals to be rejected)
                        if sig.direction == "long":
                            tight_tp = round(sig.entry + risk * 1.0, 2)
                        else:
                            tight_tp = round(sig.entry - risk * 1.0, 2)
                        sig.take_profit = tight_tp
                        filtered_mults[len(filtered)] = all_mults.get(i, 1.0)
                        filtered.append(sig)
                    all_sigs  = filtered
                    all_mults = filtered_mults
        except Exception as e:
            log.warning(f"Range filter error {symbol}: {e}")

    if signals:
        # v171: throttle regime log keyed by (symbol, tf) so multiple call sites
        # (US30+5m, US30+15m, US100+5m, US100+15m) don't overwrite each other's
        # cached state every iteration. Was: single attribute, alternating
        # callers each saw a "different" state and re-logged.
        _cache = getattr(run_brooks, "_last_log_state", {})
        _key = (symbol, tf)
        _curr_state = (regime, len(signals), len(all_sigs))
        if _cache.get(_key) != _curr_state:
            log.info(f"  [{symbol} {tf_name}] Regime: {regime} -- {len(signals)} raw -> {len(all_sigs)} signals")
            _cache[_key] = _curr_state
            setattr(run_brooks, "_last_log_state", _cache)

    return all_sigs, all_mults

# ── WICK CLASSIFICATION ───────────────────────────────────────────────────────

# REMOVED: classify_wick -- dead code, 0 call sites

def make_signal(symbol: str, strategy: str, setup_name: str,
                direction: str, entry: float, sl: float, tf) -> SetupSignal:
    tp = measured_move(symbol, tf, direction, entry)
    stype = "breakout_long" if direction == "long" else "breakout_short"
    return SetupSignal(symbol=symbol, strategy=strategy,
        setup_type=stype, setup_name=setup_name,
        entry=entry, stop_loss=sl, take_profit=tp,
        direction=direction, timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))

# ── STRATEGIES 1-3 ────────────────────────────────────────────────────────────


# REMOVED: candle_signals -- dead code, never called from main signal loop

def place_order(signal: SetupSignal, risk_pct: float) -> Optional[int]:
    # Hard block -- no new orders during EOD close
    if _EOD_ACTIVE:
        return None
    # CRITICAL: Verify we are on the correct MT5 account before placing any order
    # Both bots share one MT5 terminal -- the other bot may have switched accounts
    _acct = mt5.account_info()
    if _acct is None or _acct.login != MT5_LOGIN:
        _login = _acct.login if _acct else "None"
        log.error(f"place_order BLOCKED: MT5 on account {_login}, expected {MT5_LOGIN} (DEMO). Re-logging in...")
        if not mt5.login(MT5_LOGIN, password=MT5_PASSWORD, server=MT5_SERVER):
            log.error("Re-login failed -- order cancelled")
            return None
        _acct = mt5.account_info()
        if _acct is None or _acct.login != MT5_LOGIN:
            log.error(f"Still on wrong account {_acct.login if _acct else 'None'} -- order cancelled")
            return None
        log.info(f"Re-logged into correct account {MT5_LOGIN}")
    sym_info = mt5.symbol_info(signal.symbol)
    if sym_info is None:
        log.error(f"Symbol {signal.symbol} not found")
        return None
    if not sym_info.visible:
        mt5.symbol_select(signal.symbol, True)

    is_long = signal.direction == "long"
    tick    = mt5.symbol_info_tick(signal.symbol)
    if tick is None:
        return None

    # Round prices to broker's tick size
    digits    = sym_info.digits
    entry     = round(signal.entry, digits)
    sl        = round(signal.stop_loss, digits)
    tp        = round(signal.take_profit, digits)
    min_dist  = sym_info.trade_stops_level * sym_info.point

    current   = tick.ask if is_long else tick.bid

    # Determine order type based on entry vs current price
    if is_long:
        if entry > current + min_dist:
            order_type = mt5.ORDER_TYPE_BUY_STOP
            action     = mt5.TRADE_ACTION_PENDING
        elif entry < current - min_dist:
            order_type = mt5.ORDER_TYPE_BUY_LIMIT
            action     = mt5.TRADE_ACTION_PENDING
        else:
            # Price too close -- use market order
            order_type = mt5.ORDER_TYPE_BUY
            action     = mt5.TRADE_ACTION_DEAL
            entry      = current
    else:
        if entry < current - min_dist:
            order_type = mt5.ORDER_TYPE_SELL_STOP
            action     = mt5.TRADE_ACTION_PENDING
        elif entry > current + min_dist:
            order_type = mt5.ORDER_TYPE_SELL_LIMIT
            action     = mt5.TRADE_ACTION_PENDING
        else:
            order_type = mt5.ORDER_TYPE_SELL
            action     = mt5.TRADE_ACTION_DEAL
            entry      = current

    lot = calc_lots(signal.symbol, entry, sl, risk_pct)
    if lot <= 0:
        return None

    request = {
        "action":    action,
        "symbol":    signal.symbol,
        "volume":    lot,
        "type":      order_type,
        "price":     entry,
        "sl":        sl,
        "tp":        tp,
        "deviation": 20,
        "magic":     202401,
        "comment":   f"{signal.strategy}:{signal.setup_name}",
    }
    if action == mt5.TRADE_ACTION_PENDING:
        request["type_time"]    = mt5.ORDER_TIME_DAY
        request["type_filling"] = mt5.ORDER_FILLING_IOC  # IOC for all -- avoids partial fills
    else:
        request["type_filling"] = mt5.ORDER_FILLING_IOC

    result = mt5.order_send(request)
    if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
        code = result.retcode if result else "None"
        msg  = result.comment if result else "no response"
        log.error(f"Order failed {code}: {msg}")
        return None
    log.info(f"ORDER #{result.order}  {signal.symbol}  {signal.strategy}  {signal.setup_name}  {lot}lots  risk={risk_pct}%")
    return result.order

# ── SCALE-IN (strategies 1-3 only) ───────────────────────────────────────────

def manage_brooks_trailing():
    """
    For Brooks positions:
    - At 0.5R: move SL to break even
    - At 1:1: close 50% of position (lock in profit), move SL to BE on remainder, start trailing
    """
    positions = mt5.positions_get()
    if not positions:
        return
    state    = load_state()
    be_done      = state.get("brooks_be_tickets", [])
    trailing     = state.get("brooks_trailing_tickets", [])
    partial_done = state.get("brooks_partial_tickets", [])
    changed  = False
    # Prune closed tickets -- lists grow indefinitely without this
    # Keep only tickets that belong to currently open positions
    _open_tickets = {p.ticket for p in positions}
    be_done      = [t for t in be_done      if t in _open_tickets]
    partial_done = [t for t in partial_done if t in _open_tickets]
    trailing     = [t for t in trailing     if t in _open_tickets]

    # Pre-load log once for entire loop -- avoid 1 read per position per tick
    _cached_log = []
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, encoding="utf-8") as _clf:
                _cached_log = json.load(_clf)
    except Exception as _lc_err:
        log.debug(f"Log cache load failed: {_lc_err}")
    _log_dirty = False  # track if we need to write back

    for pos in positions:
        # v176: match by magic (always preserved) OR comment (sometimes stripped)
        if pos.magic != 202401 and "brooks" not in (pos.comment or ""):
            continue
        entry   = pos.price_open
        sl      = pos.sl
        tp      = pos.tp
        current = pos.price_current
        is_long = pos.type == mt5.ORDER_TYPE_BUY
        if sl == 0 or tp == 0:
            continue

        risk   = abs(entry - sl)
        reward = abs(tp - entry)

        # Get ATR for trail distance
        df = get_candles(pos.symbol, TF_15M, 20)
        atr = float(df.iloc[-14:]["bar_range"].mean()) if df is not None else risk * 0.5
        trail_dist = atr * 0.5

        # ── Step 1: Move to break even at 0.8R ──
        # Was 0.5R -- too early, 68% of trades hit BE then reversed before TP
        # At 0.8R price has shown real commitment before we protect entry
        if pos.ticket not in be_done:
            half_r   = entry + (risk * 0.8) if is_long else entry - (risk * 0.8)
            hit_half = (current >= half_r) if is_long else (current <= half_r)
            if hit_half:
                be_done.append(pos.ticket)  # always log for ML tracking
                # Track BE trigger -- did price reach 0.8R? (theoretical -- SL does NOT move)
                # be_trigger_hit=True + win  -> strong setup, reached 0.8R then continued to TP
                # be_trigger_hit=True + loss -> price reached 0.8R then fully reversed to SL
                # be_trigger_hit=False + win  -> very clean setup, went straight to TP
                # be_trigger_hit=False + loss -> weak setup, went straight to SL (never reached 0.8R)
                # ML learns: which setups make price progress vs which fail immediately
                try:
                    for _t in _cached_log:
                        if int(_t.get("ticket", -1)) == int(pos.ticket) and _t.get("outcome") is None:
                            if "context" not in _t:
                                _t["context"] = {}
                            _t["context"]["be_trigger_hit"] = True
                            _log_dirty = True
                            break
                except Exception as _e:
                    log.debug(f"Feature block failed: {_e}")
                if ENABLE_BREAKEVEN:
                    result = mt5.order_send({
                        "action":   mt5.TRADE_ACTION_SLTP,
                        "position": pos.ticket,
                        "sl":       entry,
                        "tp":       tp,
                        "comment":  "trail_be",
                    })
                    if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                        log.info(f"Brooks BE: #{pos.ticket} {pos.symbol} SL moved to {entry}")
                        changed = True
                else:
                    log.info(f"Brooks BE: #{pos.ticket} {pos.symbol} would move to BE (disabled -- logging only)")


        # ── Step 2: Exit at 1:1 based on regime ──
        if pos.ticket in be_done and pos.ticket not in partial_done:
            hit_1r = (current >= entry + risk) if is_long else (current <= entry - risk)
            if hit_1r:
                # Detect current regime
                df_regime = get_candles(pos.symbol, TF_15M, 50)
                regime    = detect_regime(pos.symbol, TF_15M) if df_regime is not None else "ranging"
                is_trending = regime in ("trending_bull", "trending_bear")

                sym_info = mt5.symbol_info(pos.symbol)
                tick     = mt5.symbol_info_tick(pos.symbol)
                if not tick:
                    continue

                partial_done.append(pos.ticket)  # always log for ML tracking
                if ENABLE_PARTIALS and is_trending:
                    # Trending -- partial close 50%, let runner trail
                    half_vol = round(pos.volume * 0.5, 2 if sym_info and sym_info.volume_step < 0.1 else 1)
                    half_vol = max(half_vol, sym_info.volume_min if sym_info else 0.01)
                    close_price = tick.bid if is_long else tick.ask
                    close_type  = mt5.ORDER_TYPE_SELL if is_long else mt5.ORDER_TYPE_BUY
                    result = mt5.order_send({
                        "action":       mt5.TRADE_ACTION_DEAL,
                        "symbol":       pos.symbol,
                        "volume":       half_vol,
                        "type":         close_type,
                        "price":        close_price,
                        "position":     pos.ticket,
                        "deviation":    20,
                        "magic":        202401,
                        "comment":      "partial_close_1R",
                        "type_filling": mt5.ORDER_FILLING_IOC,
                    })
                    if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                        log.info(f"Brooks partial close (trending): #{pos.ticket} {pos.symbol} closed {half_vol}lots at 1:1 -- runner trailing")
                        mt5.order_send({
                            "action":   mt5.TRADE_ACTION_SLTP,
                            "position": pos.ticket,
                            "sl":       entry,
                            "tp":       0,
                        })
                        changed = True
                else:
                    log.info(f"Brooks partial/BE: #{pos.ticket} {pos.symbol} hit 1R (logging only -- ENABLE_PARTIALS=False)")

        # ── Step 3: Trail the runner -- REMOVED ──
        # Step 4c (volatility-adjusted trailing) is the authoritative trail logic.
        # Having both fire for the same position caused conflicting SL moves (last write wins).
        # Step 4c uses vol_ratio to tighten the trail when momentum is fading -- superior.

        # ── Step 4: Exit optimization ──
        now_utc = datetime.now(timezone.utc)

        # 4a. Session-based exit -- close GER40 before 17:00 UTC (Frankfurt close)
        if pos.symbol == "GER40.cash" and now_utc.hour >= 17 and pos.ticket not in partial_done:
            tick = mt5.symbol_info_tick(pos.symbol)
            if tick:
                close_type  = mt5.ORDER_TYPE_SELL if is_long else mt5.ORDER_TYPE_BUY
                close_price = tick.bid if is_long else tick.ask
                result = mt5.order_send({
                    "action":       mt5.TRADE_ACTION_DEAL,
                    "symbol":       pos.symbol,
                    "volume":       pos.volume,
                    "type":         close_type,
                    "price":        close_price,
                    "position":     pos.ticket,
                    "deviation":    50,
                    "magic":        202401,
                    "comment":      "session_close",
                    "type_filling": mt5.ORDER_FILLING_IOC,
                })
                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                    log.info(f"Session close GER40: #{pos.ticket} -- Frankfurt close 17:00 UTC")
                    changed = True
                    continue

        # 4b. MFE-based time exit -- exit only if price never showed real interest
        # OLD rule: exit if CURRENTLY below 50% of TP after 2hrs
        #   Problem: exits trades that reached 80% then pulled back -- premature
        #
        # NEW rule using Max Favorable Excursion (MFE):
        #   mfe = best price reached since open (relative to SL distance)
        #   After 2hrs: if mfe < 0.3R -> price never moved toward TP -> market rejected it -> EXIT
        #   After 2hrs: if mfe >= 0.3R -> price showed interest -> give it 5hrs total
        #   After 5hrs: if mfe < 0.5R -> still going nowhere -> EXIT
        #   This prevents closing trades that made real progress then pulled back
        try:
            open_time = datetime.fromtimestamp(pos.time, tz=timezone.utc)
            mins_open = (datetime.now(timezone.utc) - open_time).total_seconds() / 60
            if tp != 0 and pos.ticket not in partial_done and mins_open > 120:
                # Calculate MFE -- how far did price move toward TP?
                # mfe_r = best excursion / SL distance (in R units)
                # Get MFE from log (read once, works for both long/short)
                # ticket stored as int in log -- compare directly
                logged_mfe_r = 0
                try:
                    for _t in _cached_log:  # use pre-loaded cache, not raw file read
                        if _t.get("ticket") == pos.ticket:
                            logged_mfe_r = float(_t.get("context", {}).get("mfe_r", 0) or 0)
                            break
                except Exception as _e:
                    log.debug(f"Feature block failed: {_e}")

                if logged_mfe_r > 0:
                    mfe_r = logged_mfe_r  # use logged MFE directly (already in R units)
                else:
                    # Fallback: estimate from current price
                    if is_long:
                        mfe_r = max(0, (pos.price_current - entry) / risk) if risk > 0 else 0
                    else:
                        mfe_r = max(0, (entry - pos.price_current) / risk) if risk > 0 else 0

                # Apply exit rules based on MFE
                should_exit = False
                exit_reason = ""
                if mins_open > 120 and mfe_r < 0.3:
                    # 2hrs+ open, price never reached 30% of SL distance toward TP
                    # Market genuinely rejected this setup -> exit
                    should_exit = True
                    exit_reason = f"{mins_open:.0f}min open, MFE={mfe_r:.2f}R (<0.3R) -- market rejected"
                elif mins_open > 300 and mfe_r < 0.5:
                    # 5hrs+ open, price reached some progress but stalled below 50%
                    # Give it the extra time but now exit if still stuck
                    should_exit = True
                    exit_reason = f"{mins_open:.0f}min open, MFE={mfe_r:.2f}R (<0.5R after 5hrs) -- stalled"

                if should_exit:
                    tick = mt5.symbol_info_tick(pos.symbol)
                    if tick:
                        close_type  = mt5.ORDER_TYPE_SELL if is_long else mt5.ORDER_TYPE_BUY
                        close_price = tick.bid if is_long else tick.ask
                        result = mt5.order_send({
                            "action":       mt5.TRADE_ACTION_DEAL,
                            "symbol":       pos.symbol,
                            "volume":       pos.volume,
                            "type":         close_type,
                            "price":        close_price,
                            "position":     pos.ticket,
                            "deviation":    50,
                            "magic":        202401,
                            "comment":      "time_exit",
                            "type_filling": mt5.ORDER_FILLING_IOC,
                        })
                        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                            log.info(f"MFE time exit: #{pos.ticket} {pos.symbol} -- {exit_reason}")
                            changed = True
                            continue
                else:
                    # Log MFE hold every 30min only -- avoid spam every 5sec
                    if mins_open > 120 and int(mins_open) % 30 < 1:
                        log.info(f"  MFE hold: #{pos.ticket} {pos.symbol} -- {mins_open:.0f}min, MFE={mfe_r:.2f}R (showing interest)")
        except Exception as _e:
            log.debug(f"Feature block failed: {_e}")

        # 4c. Volatility-adjusted trailing -- tighter trail when vol drops
        if pos.ticket in partial_done:
            df_vol = get_candles(pos.symbol, TF_15M, 10)
            if df_vol is not None:
                recent_vol = float(df_vol.iloc[-3:-1]["bar_range"].mean())
                avg_vol    = float(df_vol.iloc[-10:-3]["bar_range"].mean())
                vol_ratio  = recent_vol / avg_vol if avg_vol > 0 else 1.0
                # Tighter trail when volatility drops (market losing momentum)
                vol_adjusted_trail = trail_dist * max(0.3, min(1.0, vol_ratio))
                if is_long:
                    new_sl = round(current - vol_adjusted_trail, 2)
                    if new_sl > sl:
                        result = mt5.order_send({
                            "action":   mt5.TRADE_ACTION_SLTP,
                            "position": pos.ticket,
                            "sl":       new_sl,
                            "tp":       0,
                        })
                        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                            log.info(f"Vol-adjusted trail: #{pos.ticket} SL -> {new_sl} (vol_ratio={vol_ratio:.2f})")
                            changed = True
                else:
                    new_sl = round(current + vol_adjusted_trail, 2)
                    if new_sl < sl:
                        result = mt5.order_send({
                            "action":   mt5.TRADE_ACTION_SLTP,
                            "position": pos.ticket,
                            "sl":       new_sl,
                            "tp":       0,
                        })
                        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                            log.info(f"Vol-adjusted trail: #{pos.ticket} SL -> {new_sl} (vol_ratio={vol_ratio:.2f})")
                            changed = True

        # 4d. Daily ATR remaining TP adjustment
        # If today's range is >80% of avg daily range, tighten TP to avoid reversal
        try:
            daily_data = get_candles(pos.symbol, mt5.TIMEFRAME_D1, 21)  # uses 10s cache
            if daily_data is not None and len(daily_data) >= 20:
                d_df = daily_data
                avg_daily = float((d_df["high"] - d_df["low"]).iloc[-20:].mean())
                today_range = float(d_df.iloc[-1]["high"]) - float(d_df.iloc[-1]["low"])
                range_used  = today_range / avg_daily if avg_daily > 0 else 0
                # If >80% of daily range used and TP still set, tighten it
                if range_used > 0.8 and tp != 0 and pos.ticket not in partial_done:
                    atr_remaining = max(0, avg_daily - today_range)
                    if is_long:
                        new_tp = round(current + atr_remaining * 0.5, 2)
                        if new_tp < tp and new_tp > current:
                            mt5.order_send({"action": mt5.TRADE_ACTION_SLTP,
                                          "position": pos.ticket, "sl": sl, "tp": new_tp})
                            log.info(f"ATR TP tightened: #{pos.ticket} {pos.symbol} -> {new_tp} (range {range_used:.0%} used)")
                    else:
                        new_tp = round(current - atr_remaining * 0.5, 2)
                        if new_tp > tp and new_tp < current:
                            mt5.order_send({"action": mt5.TRADE_ACTION_SLTP,
                                          "position": pos.ticket, "sl": sl, "tp": new_tp})
                            log.info(f"ATR TP tightened: #{pos.ticket} {pos.symbol} -> {new_tp} (range {range_used:.0%} used)")
        except Exception as _e:
            log.debug(f"Feature block failed: {_e}")

    # Write cached log once if dirty
    if _log_dirty and _cached_log:
        try:
            atomic_write(LOG_FILE, _cached_log)
        except Exception as _e:
            log.debug(f"Feature block failed: {_e}")

    if changed:
        state["brooks_be_tickets"]      = be_done
        state["brooks_trailing_tickets"] = trailing
        state["brooks_partial_tickets"] = partial_done
        save_state(state)

def manage_scale_in():
    positions = mt5.positions_get()
    if not positions:
        return
    state  = load_state()
    scaled = state.get("scaled_tickets", [])
    # Prune closed tickets -- same issue as be_done/partial_done in manage_brooks_trailing
    _open_tix_si = {p.ticket for p in positions}
    scaled = [t for t in scaled if t in _open_tix_si]
    for pos in positions:
        # v176: also exclude by magic, since broker may strip comments
        _is_brooks = pos.magic == 202401 or "brooks" in (pos.comment or "") or "partial_close" in (pos.comment or "")
        if _is_brooks or pos.ticket in scaled:
            continue
        entry   = pos.price_open
        sl      = pos.sl
        tp      = pos.tp
        current = pos.price_current
        is_long = pos.type == mt5.ORDER_TYPE_BUY
        if sl == 0 or tp == 0:
            continue
        risk   = abs(entry - sl)
        hit_1r = (current >= entry + risk) if is_long else (current <= entry - risk)
        if not hit_1r:
            continue
        log.info(f"Scale-in: #{pos.ticket} {pos.symbol}")
        be = mt5.order_send({"action": mt5.TRADE_ACTION_SLTP,
                              "position": pos.ticket, "sl": entry, "tp": tp})
        if be.retcode != mt5.TRADE_RETCODE_DONE:
            continue
        tick = mt5.symbol_info_tick(pos.symbol)
        if not tick:
            continue
        add = mt5.order_send({
            "action": mt5.TRADE_ACTION_DEAL, "symbol": pos.symbol,
            "volume": pos.volume,
            "type":   mt5.ORDER_TYPE_BUY if is_long else mt5.ORDER_TYPE_SELL,
            "price":  tick.ask if is_long else tick.bid,
            "sl": entry, "tp": tp, "deviation": 10, "magic": 202401,
            "comment": "scale_in", "type_filling": mt5.ORDER_FILLING_IOC,
        })
        if add.retcode == mt5.TRADE_RETCODE_DONE:
            log.info(f"Scale-in added #{add.order}")
            scaled.append(pos.ticket)
            state["scaled_tickets"] = scaled
            save_state(state)

# ── TRADE LOG & LEARNING ──────────────────────────────────────────────────────


# REMOVED: classify_outcome -- dead code, never called from main signal loop

def recover_missing_outcomes():
    """
    Backfill outcomes for trades that closed while bot was offline.
    Counts wins, losses AND breakevens (trailing/EOD closes).
    """
    if not os.path.exists(LOG_FILE):
        return
    with open(LOG_FILE, encoding="utf-8") as f:
        trades = json.load(f)

    open_trades = [t for t in trades if t.get("outcome") is None]
    if not open_trades:
        return

    history = mt5.history_deals_get(
        datetime.now(timezone.utc) - timedelta(days=30), datetime.now(timezone.utc))
    if not history:
        return

    closed_by_ticket = {d.order: d for d in history if d.entry == mt5.DEAL_ENTRY_OUT}
    closed_by_symbol = {}
    for d in history:
        if d.entry == mt5.DEAL_ENTRY_OUT:
            key = d.symbol
            if key not in closed_by_symbol:
                closed_by_symbol[key] = []
            closed_by_symbol[key].append(d)

    recovered = 0
    for t in open_trades:
        if t.get("ticket") in closed_by_ticket:
            d = closed_by_ticket[t.get("ticket")]
            _classify_outcome(t, d.profit, d.comment or "", deal_time=getattr(d, "time", None), deal_price=getattr(d, "price", None))
            recovered += 1
            continue
        # No ticket match -- skip rather than guess by price proximity
        # Price-match causes wrong outcomes (100pt tolerance on GER40)
        # Leave as None -- EOD retrain will catch it via position_profit dict

    if recovered > 0:
        atomic_write(LOG_FILE, trades)
        update_win_stats._log_enabled = False  # suppress log when called mid-session
        update_win_stats(trades)
        log.info(f"Recovered {recovered} missing trade outcomes from MT5 history")

def _impute_mfe_for_closed(trades: list) -> int:
    """v154 FIX: Retroactively impute mfe_r for closed trades that have outcome but no mfe_r.
    Uses outcome type + TP/SL geometry to infer minimum MFE.
    Ensures all post-cutoff real-risk trades become T1-eligible (mfe_r present).
    Runs at startup and after each EOD retrain.
    mfe_imputed=True flag distinguishes imputed from real MFE.
    """
    imputed = 0
    for t in trades:
        outcome = t.get("outcome", "")
        if not outcome:
            continue
        ctx = t.get("context", {}) or {}
        if ctx.get("mfe_r") is not None:
            continue  # already has real MFE -- don't overwrite
        entry_px  = float(t.get("entry", 0) or 0)
        sl_px     = float(t.get("stop_loss", 0) or 0)
        tp_px     = float(t.get("take_profit", 0) or 0)
        orig_risk = abs(sl_px - entry_px) if entry_px and sl_px else 0
        if orig_risk <= 0 or not tp_px or not entry_px:
            continue
        tp_dist = abs(tp_px - entry_px)
        rr      = tp_dist / orig_risk
        try:
            if outcome in ("win",):
                ctx["mfe_r"]     = round(rr, 2)       # hit TP -> MFE = RR
                ctx["mae_r"]     = ctx.get("mae_r") or 0.0
            elif outcome in ("loss",):
                ctx["mae_r"]     = 1.0                 # hit SL -> MAE = 1.0R
                ctx["mfe_r"]     = ctx.get("mfe_r") or 0.0
            elif outcome in ("eod_win",):
                ctx["mfe_r"]     = round(min(rr * 0.6, rr), 2)  # partial run to EOD
                ctx["mae_r"]     = ctx.get("mae_r") or 0.0
            elif outcome in ("eod_loss",):
                ctx["mfe_r"]     = ctx.get("mfe_r") or 0.0
                ctx["mae_r"]     = ctx.get("mae_r") or 0.3
            elif outcome in ("breakeven", "eod_breakeven"):
                ctx["mfe_r"]     = ctx.get("mfe_r") or round(rr * 0.5, 2)
                ctx["mae_r"]     = ctx.get("mae_r") or 0.0
            else:
                continue
            ctx["mfe_imputed"] = True   # flag -- report can weight these slightly lower
            t["context"] = ctx
            imputed += 1
        except Exception:
            continue
    return imputed

def update_outcomes():
    if not os.path.exists(LOG_FILE):
        return
    with open(LOG_FILE, encoding="utf-8") as f:
        trades = json.load(f)
    history = mt5.history_deals_get(
        datetime.now(timezone.utc) - timedelta(days=30), datetime.now(timezone.utc))
    if not history:
        return
    closed  = {d.order: d for d in history if d.entry == mt5.DEAL_ENTRY_OUT}
    updated = False
    for t in trades:
        if t.get("outcome") is None and t.get("ticket") in closed:
            d = closed[t.get("ticket")]
            _classify_outcome(t, d.profit, d.comment or "", deal_time=getattr(d, "time", None), deal_price=getattr(d, "price", None))  # full classification with all ML flags
            updated = True
    if updated:
        atomic_write(LOG_FILE, trades)
        update_win_stats._log_enabled = False  # suppress log when called mid-session
        update_win_stats(trades)

def update_win_stats(trades: list):
    stats = {}
    for t in trades:
        if not t.get("outcome"):  # safe -- handles missing key and None
            continue
        key = f"{t.get('strategy','?')}|{t.get('setup_name','?')}"
        if key not in stats:
            stats[key] = {"wins": 0, "losses": 0, "breakevens": 0,
                          "win_rate": 0.0, "total": 0,
                          "strategy": t.get("strategy", "?"), "setup_name": t.get("setup_name", "?")}
        outcome = t.get("outcome", "")
        if outcome in ("win", "eod_win"):
            stats[key]["wins"] += 1
        elif outcome in ("loss", "eod_loss"):
            stats[key]["losses"] += 1
        elif "breakeven" in str(outcome):
            stats[key].setdefault("breakevens", 0)
            stats[key]["breakevens"] += 1
    for s in stats.values():
        s.setdefault("breakevens", 0)
        decisive = s["wins"] + s["losses"]
        total    = decisive + s.get("breakevens", 0)
        # WR = W / (W + L) -- BEs excluded from WR formula
        s["win_rate"] = round(s["wins"] / decisive * 100, 1) if decisive > 0 else 0.0
        s["total"]    = total
    atomic_write(STATS_FILE, stats)
    # v174: refresh the in-memory priority cache used by merge_zone_signals
    # so zone-dedup picks based on current WR data, not stale startup data.
    global _setup_priority_cache
    _setup_priority_cache = {
        f"{s['strategy']}|{s['setup_name']}": (s["win_rate"], s["total"])
        for s in stats.values()
    }
    # Log is done by caller at startup only -- suppress here to avoid double logging
    if getattr(update_win_stats, '_log_enabled', True):
        log.info("--- Win stats ---")
        sorted_stats = sorted(stats.values(), key=lambda x: x["win_rate"], reverse=True)
        for s in sorted_stats:
            be = s.get("breakevens", 0)
            be_str = f"/{be}BE" if be > 0 else ""
            decisive = s["wins"] + s["losses"]
            if decisive == 0:
                continue
            log.info(f"  {s['strategy']:14} {s['setup_name']:22} {s['win_rate']:5.1f}%  {s['wins']}W/{s['losses']}L{be_str}  total={s['total']}")
    update_win_stats._log_enabled = True  # reset for next call

# REMOVED: already_today -- dead code, never called

def capture_market_context(signal) -> dict:
    """
    Capture 60+ market variables at signal time for future ML training.
    Based on Al Brooks price action principles.
    """
    ctx = {}
    # v175: store symbol in ctx so downstream loggers (ensemble_predict's
    # throttled ML log) can key by symbol. This is metadata, not an ML feature
    # -- features are listed in BASE_FEATURES and "symbol" is not in that list.
    ctx["symbol"] = getattr(signal, "symbol", "?")
    now = datetime.now(timezone.utc)  # UTC -- LONDON_OPEN_HOUR=8 and all cutoffs assume UTC

    # ── SHARED LOG CACHE -- single read serves all 11 feature blocks ──────────
    # capture_market_context() is called for every signal (~40x/min at peak).
    # Without this cache, each of the 11 features below opens and parses the
    # full 3,000-trade LOG_FILE independently = ~440 JSON parses/min.
    # With this 60s TTL cache: 1 parse/min. All features see a consistent
    # snapshot (no feature sees a trade that another feature missed mid-call).
    _ctx_ts_now = datetime.now(timezone.utc).timestamp()
    if (getattr(capture_market_context, '_log_cache', None) is None or
            (_ctx_ts_now - getattr(capture_market_context, '_log_cache_ts', 0)) > 60):
        try:
            with open(LOG_FILE, encoding="utf-8") as _ctxf:
                capture_market_context._log_cache = json.load(_ctxf)
        except Exception:
            capture_market_context._log_cache = []
        capture_market_context._log_cache_ts = _ctx_ts_now
    _cached_trades = capture_market_context._log_cache

    # ── GUARANTEED DEFAULTS -- every feature gets a value before any try block ──
    # This means candle-fetch failures produce 0/neutral values, NOT NaN.
    # NaN = sklearn drops the column. 0 = model treats it as "not present".
    # Features that have genuine neutral values use those (e.g. rsi=50, pos=0.5).
    _ZERO_FEATURES = [
        "score_15m_structure","score_1h_direction","score_5m_bar","score_optimal_time",
        "score_signal_detected","score_daily_position","score_volatility","score_key_levels",
        "candle_size","candle_close_pos","candle_body","candle_upper_wick","candle_lower_wick",
        "candle_body_ratio","candle_size_ratio","candle_streak","candle_is_green",
        "is_doji","is_inside_bar","is_outside_bar","is_strong_bull","is_strong_bear",
        "is_large_bar","is_small_bar","is_strong_bull_5m","is_strong_bear_5m",
        "prev_candle_green","prev_bar_climactic","prev_close_pos","prev_size_ratio","prev_is_doji",
        "volume_ratio","high_volume","low_volume","volume_vs_avg_20","high_volume_signal",
        "low_volume_signal","volume_trend_rising","volume_trend_falling","vix_equiv_pct",
        "spread_pts","spread_vs_avg","spread_wide","spread_vs_hourly_avg","spread_abnormal","spread_very_wide",
        "ema_slope","ema_slope_accel","distance_from_ema_pct","price_above_ema",
        "higher_highs","higher_lows","bars_since_1pct_move","bars_since_sig_move",
        "at_daily_open","at_yesterday_high","at_yesterday_low","at_weekly_high","at_weekly_low",
        "daily_range_pct_complete","daily_range_exceeded","distance_from_daily_open_pct",
        "in_range_15m","in_range_5m","in_range_1h","price_in_range_pct",
        "above_overnight","below_overnight","inside_overnight","overnight_atr_ratio","price_vs_overnight",
        "momentum_fresh","momentum_decayed","bearish_divergence","bullish_divergence",
        "near_round_number","level_test_count","level_tested_recently",
        "at_swing_high","at_swing_low","at_swing_extreme","at_swing_middle",
        "gap_size_pct","has_gap","gap_fill_setup","gap_filled_pct",
        "inside_bar_count","has_inside_bars","strong_compression","extreme_compression",
        "has_failed_breakout","entry_tightness","tight_entry",
        "pattern_bars_exact","pattern_bars","pattern_fast","pattern_slow","pattern_ideal",
        "pattern_clean","pattern_messy","pattern_quality","same_setup_yesterday",
        "dist_prev_high_atr","dist_prev_low_atr","dist_prev_close_atr",
        "near_prev_high","near_prev_low","near_prev_close","above_prev_high","below_prev_low",
        "pos_in_swing","daily_range_atr_ratio",
        # Session
        "london_first_30min","london_session","ny_first_30min","ny_session",
        "overlap_session","asian_session","monday_open","friday_close",
        "london_close_zone","mins_to_hour","near_hour_mark",
        "mins_to_news_event","near_news_event","very_near_news",
        "asia_lon_transition","lon_ny_transition","lon_close_transition",
        "ny_close_transition","any_session_transition","ny_close_zone",
        "is_opex_week","is_opex_day","is_month_end","is_month_start",
        "is_monday_open","is_friday_close_zone","calendar_risk",
        # Cross-symbol
        "n_symbols_same_dir","all_symbols_aligned","strong_confluence","ger40_leading_us30",
        "symbols_same_direction","open_longs","open_shorts","open_positions_total",
        # Pairs divergence -- these were NEVER computed, now default to 0
        "ger_us100_zscore","ger_us100_diverged","ger_us100_extreme",
        "us30_us100_zscore","us30_us100_diverged","us30_us100_extreme",
        "uk_ger_zscore","uk_ger_diverged","uk_ger_extreme",
        "ger_us_spread_zscore","ger_leading_up","ger_leading_down",
        "pairs_converging","pairs_diverged",
        # Statistical features
        "hurst_exponent","hurst_trending","hurst_reverting","hurst_random",
        "autocorr_lag1","autocorr_lag5","ac_trending","ac_reverting","ac_random",
        "ac5_trending","direction_consistency","strong_trend_signal",
        "price_entropy","low_entropy","high_entropy","entropy_tradeable",
        "vol_clustering_ratio","vol_expanding","vol_contracting","vol_stable",
        "vol_accelerating","vol_decelerating","vol_scale_ratio_5_15",
        "vol_scales_agree","vol_expanding_multi","vol_contracting_multi",
        # Kalman
        "kalman_slope_pct","kalman_bull","kalman_bear","kalman_flat",
        "price_above_kalman","dist_from_kalman_pct","extended_from_kalman",
        # AR3
        "ar3_prediction","ar3_bullish","ar3_bearish","ar3_neutral",
        # Fractal
        "fractal_dimension","fd_trending","fd_choppy","fd_neutral",
        # Momentum
        "momentum_confluence","strong_momentum","weak_momentum",
        "momentum_agrees_long","momentum_agrees_short","momentum_disagrees",
        "momentum_signal_agreement","momentum_signal_conflict","price_momentum_divergence",
        # VWAP
        "vwap_dist_pct","vwap_dist_pts","above_vwap","below_vwap",
        "far_above_vwap","far_below_vwap","near_vwap",
        "vwap_aligned_long","vwap_aligned_short","vwap_against_long","vwap_against_short",
        # Returns distribution
        "return_skewness","return_kurtosis","negative_skew","positive_skew",
        # Implied edge (set later after ML predict)
        "implied_edge","implied_rr",
        # ml_vs_implied_gap removed -- circular (uses current ML output as input)
        # "ml_overconfident",  # REMOVED: circular -- uses current ML output as input"ml_underconfident","high_conviction","dual_confirmation",
        # ML meta
        "ml_win_prob","ml_recent_accuracy","ml_avg_confidence","ml_mind_changes",
        "ml_indecisive","ml_confidence_rising","ml_confidence_falling",
        "ml_confidence_strength","ml_very_confident","ml_uncertain",
        # "model_vs_math_agree",  # REMOVED: circular -- uses current ML output as input"model_vs_math_conflict",
        # Regime
        "regime_multiplier","regime_with_trend","regime_against_trend",
        "regime_persistence","regime_established","regime_new","regime_mature",
        "consecutive_ranging_days",
        # Risk / portfolio
        "portfolio_heat_pct","correlated_long_exposure","correlated_short_exposure",
        "high_correlation_risk","max_correlation_risk","net_directional_bias",
        "corr_adjusted_long_heat","corr_adjusted_short_heat","corr_adjusted_total_heat",
        "true_portfolio_overweight","drawdown_velocity","losing_faster_than_avg",
        "today_loss_rate","hist_loss_rate","losing_days_streak","on_losing_streak","streak_size_penalty",
        # Symbol stats
        "symbol_win_rate_100","symbol_is_profitable","symbol_is_losing",
        "symbol_streak","symbol_on_hot_streak","symbol_on_cold_streak",
        # Per-setup stats
        "setup_wr_7d","setup_drift","setup_drifting_down","setup_improving",
        "setup_wr_last10_symbol","setup_wr_last20","setup_hot","setup_cold",
        "setup_consec_losses","setup_on_loss_streak","setup_trending_up","setup_streak_wins",
        "setup_freshness","setup_stale_bs","setup_fresh_bs","setup_stale","setup_fresh",
        # Time of day
        "this_hour_win_rate","this_hour_profitable","this_hour_losing",
        # Loss aversion
        "last_trade_was_loss","consecutive_setup_losses","win_rate_after_loss",
        # BE (now unused but keep defaults)
        "be_candidate","be_avg_mfe","be_count","be_was_protective","be_optimal",
        # Availability flags (start at 0 = not available, set to 1 when computed)
        "candles_ok", "kalman_available", "ar3_available", "stat_available",
        # ATR regime features
        "atr_regime_pct", "atr_low_vol", "atr_normal_vol", "atr_high_vol", "atr_extreme_vol",
    ]
    for _f in _ZERO_FEATURES:
        ctx[_f] = 0
    ctx["atr_regime_pct"] = 50.0  # neutral default (mid-range vol)

    # Features with non-zero neutral defaults
    ctx["rsi_14"]                = 50.0   # neutral RSI
    ctx["rsi_5m"]                = 50.0
    ctx["rsi_oversold"]          = 0
    ctx["rsi_overbought"]        = 0
    ctx["rsi_extreme"]           = 0
    ctx["atr_14"]                = 0.0
    ctx["spread_atr_ratio"]      = 1.0    # normal spread
    ctx["stop_atr_ratio"]        = 1.0
    ctx["rr_ratio"]              = 1.5    # neutral RR -- overwritten below from signal
    # Pre-compute RR from signal geometry BEFORE try blocks -- always available
    try:
        _sl_dist = abs(float(signal.stop_loss) - float(signal.entry))
        _tp_dist = abs(float(signal.take_profit) - float(signal.entry))
        if _sl_dist > 0:
            ctx["rr_ratio"] = round(_tp_dist / _sl_dist, 3)
        ctx["stop_atr_ratio"] = 0.0  # will be overwritten if ATR available
    except Exception:
        pass  # keep default 1.5
    ctx["confidence"]            = 0
    ctx["pos_in_daily_range"]    = 0.5   # middle of range
    ctx["price_in_range_pct"]    = 0.5
    ctx["pos_in_swing"]          = 0.5
    ctx["nearest_key_pct"]       = 1.0   # far from key level
    ctx["implied_edge"]          = 0.5   # no edge
    ctx["implied_rr"]            = 1.5
    ctx["hurst_exponent"]        = 0.5   # random walk
    ctx["fractal_dimension"]     = 1.5   # neutral
    ctx["price_entropy"]         = 0.8   # moderate entropy
    ctx["vol_clustering_ratio"]  = 1.0   # normal vol
    ctx["setup_freshness"]       = 0.5
    ctx["ml_win_prob"]           = 0.5
    ctx["ml_avg_confidence"]     = 0.5
    ctx["symbol_win_rate_100"]   = 0.5
    ctx["this_hour_win_rate"]    = 0.5
    ctx["setup_wr_7d"]           = 0.5
    ctx["setup_wr_last10_symbol"]= 0.5
    ctx["setup_wr_last20"]       = 0.5
    ctx["win_rate_after_loss"]   = 0.5
    ctx["corr_adjusted_total_heat"] = 0.0
    ctx["regime_multiplier"]     = 1.0   # no adjustment
    ctx["ml_vs_implied_gap"]     = 0.0   # no gap
    ctx["momentum_confluence"]   = 2     # neutral (out of 5)
    # Feature availability flags -- 0=data missing/failed, 1=real computed value
    # Model uses these to distinguish "neutral market" from "data unavailable"
    ctx["candles_ok"]       = 0   # set to 1 when candle fetch succeeds
    ctx["kalman_available"] = 0   # set to 1 when Kalman filter runs
    ctx["ar3_available"]    = 0   # set to 1 when AR3 model runs
    ctx["stat_available"]   = 0   # set to 1 when autocorr/Hurst/entropy run

    # ── 1-minute enriched features defaults (neutral values) ────────────────
    ctx["mom_5m"] = 0.0; ctx["mom_15m"] = 0.0
    ctx["mom_30m"] = 0.0; ctx["mom_60m"] = 0.0
    ctx["orb_position_1m"] = 0.5; ctx["above_orb_1m"] = 0
    ctx["below_orb_1m"] = 0; ctx["inside_orb_1m"] = 1
    ctx["vol_compression_ratio"] = 1.0
    ctx["pre_entry_bull_bars"] = 2; ctx["pre_entry_wick_ratio"] = 0.4
    import math as _math
    ctx["dow_sin_1m"] = round(_math.sin(2*_math.pi*now.weekday()/5), 4)
    ctx["dow_cos_1m"] = round(_math.cos(2*_math.pi*now.weekday()/5), 4)
    ctx["is_monday_1m"] = int(now.weekday()==0)
    ctx["is_friday_1m"] = int(now.weekday()==4)
    ctx["is_wednesday_1m"] = int(now.weekday()==2)
    ctx["ema_bull_align_1m"] = 0; ctx["ema_bear_align_1m"] = 0
    ctx["ema_slope_1m"] = 0.0; ctx["vol_profile_poc_dist_pct"] = 0.0
    ctx["above_session_vwap_1m"] = 0; ctx["session_vwap_dist_pct_1m"] = 0.0
    ctx["day_range_position_1m"] = 0.5; ctx["enrichment_ok"] = 0



    # ── Time & session ──
    ctx["hour_server"]      = now.hour
    ctx["minute"]           = now.minute
    ctx["day_of_week"]      = now.weekday()  # 0=Mon 4=Fri
    ctx["is_monday"]        = now.weekday() == 0
    ctx["is_friday"]        = now.weekday() == 4
    ctx["session"]          = ("london" if LONDON_OPEN_HOUR <= now.hour < 13
                                else "overlap" if now.hour == 13
                                else "ny" if 14 <= now.hour < 20
                                else "off")
    ctx["is_optimal_time"]  = is_optimal_time()
    ctx["hours_since_open"] = max(0, now.hour - LONDON_OPEN_HOUR)

    ctx["candles_ok"] = 0  # set to 1 only when candles load successfully
    try:
        df_15 = get_candles(signal.symbol, TF_15M, 60)
        df_5  = get_candles(signal.symbol, TF_5M,  40)
        df_1h = get_candles(signal.symbol, mt5.TIMEFRAME_H1, 30)

        if df_15 is not None and len(df_15) >= 25:
            ctx["candles_ok"] = 1  # candles loaded -- features are real, not defaults
            c     = df_15.iloc[-2]
            prev  = df_15.iloc[-3]
            prev2 = df_15.iloc[-4]

            # ── Signal candle properties (Brooks bar analysis) ──
            ctx["candle_size"]          = round(float(c["bar_range"]), 2)
            ctx["candle_close_pos"]     = round(bar_close_pos(c), 3)  # 0=bottom 1=top
            ctx["candle_is_green"]      = bool(c["green"])
            ctx["candle_body"]          = round(abs(float(c["close"]) - float(c["open"])), 2)
            ctx["candle_upper_wick"]    = round(float(c["high"]) - max(float(c["open"]), float(c["close"])), 2)
            ctx["candle_lower_wick"]    = round(min(float(c["open"]), float(c["close"])) - float(c["low"]), 2)
            ctx["candle_body_ratio"]    = round(ctx["candle_body"] / ctx["candle_size"], 3) if ctx["candle_size"] > 0 else 0
            ctx["is_doji"]              = is_doji(c)
            ctx["is_strong_bull"]       = is_strong_bull(c)
            ctx["is_strong_bear"]       = is_strong_bear(c)

            # ── Candle size vs recent average (Brooks: size matters) ──
            avg_range = float(df_15.iloc[-20:-2]["bar_range"].mean())
            ctx["candle_size_ratio"]    = round(ctx["candle_size"] / avg_range, 2) if avg_range > 0 else 1.0
            ctx["is_large_bar"]         = ctx["candle_size_ratio"] > 1.5
            ctx["is_small_bar"]         = ctx["candle_size_ratio"] < 0.5

            # ── Volume (tick volume -- proxy for real volume on CFDs) ──
            if "tick_volume" in df_15.columns:
                vol_now  = float(c["tick_volume"])
                avg_vol  = float(df_15.iloc[-20:-2]["tick_volume"].mean())
                ctx["volume"]            = int(vol_now)
                ctx["avg_volume"]        = round(avg_vol, 1)
                ctx["volume_ratio"]      = round(vol_now / avg_vol, 2) if avg_vol > 0 else 1.0
                ctx["high_volume"]       = ctx["volume_ratio"] > 1.5
                ctx["low_volume"]        = ctx["volume_ratio"] < 0.5
                ctx["prev_volume_ratio"] = round(float(prev["tick_volume"]) / avg_vol, 2) if avg_vol > 0 else 1.0

            # ── Previous bar properties ──
            ctx["prev_candle_green"]    = bool(prev["green"])
            ctx["prev_close_pos"]       = round(bar_close_pos(prev), 3)
            ctx["prev_size_ratio"]      = round(float(prev["bar_range"]) / avg_range, 2) if avg_range > 0 else 1.0
            ctx["prev_is_doji"]         = is_doji(prev)

            # ── Brooks: consecutive bars (streak) ──
            streak = 0
            for i in range(len(df_15)-3, max(len(df_15)-15, 0), -1):
                if df_15.iloc[i]["green"] == df_15.iloc[-2]["green"]:
                    streak += 1
                else:
                    break
            ctx["candle_streak"]        = streak

            # ── 1-minute enriched features (live computation) ────────────────────
            # Mirrors enrich_trades.py so train/live features match exactly.
            # Uses the same 15m candles already loaded above.
            try:
                _closes = [float(r["close"]) for r in df_15.to_dict("records")]
                _highs  = [float(r["high"])  for r in df_15.to_dict("records")]
                _lows   = [float(r["low"])   for r in df_15.to_dict("records")]
                _vols   = [float(r.get("tick_volume", r.get("tickvol", 1))) for r in df_15.to_dict("records")]
                _cur    = _closes[-1]

                # Momentum over multiple lookbacks (15m bars, so 1 bar = 15 min)
                # mom_5m  = 1 bar back, mom_15m = 1 bar, mom_30m = 2 bars, mom_60m = 4 bars
                _lb_map = {"mom_5m": 1, "mom_15m": 1, "mom_30m": 2, "mom_60m": 4}
                for _key, _lb in _lb_map.items():
                    if _lb < len(_closes):
                        _past = _closes[-_lb-1]
                        ctx[_key] = round((_cur - _past) / _past * 100, 4) if _past > 0 else 0.0

                # Volatility compression: short (3 bars = 45min) vs long (8 bars = 2hr)
                if len(_closes) >= 8:
                    _ranges = [_highs[i] - _lows[i] for i in range(len(_highs))]
                    _vol_s = sum(_ranges[-3:]) / 3
                    _vol_l = sum(_ranges[-8:]) / 8
                    ctx["vol_compression_ratio"] = round(_vol_s / _vol_l, 4) if _vol_l > 0 else 1.0

                # EMA alignment (5, 20, 60 bars on 15m = 75min, 5hr, 15hr)
                if len(_closes) >= 20:
                    import numpy as _np
                    _s = _np.array(_closes)
                    def _ema(arr, n):
                        k = 2/(n+1)
                        e = arr[0]
                        for v in arr[1:]: e = v*k + e*(1-k)
                        return float(e)
                    _ema5  = _ema(_closes[-20:], 5)
                    _ema20 = _ema(_closes[-20:], 20)
                    _ema60 = _ema(_closes[-min(60,len(_closes)):], min(60,len(_closes)))
                    ctx["ema_bull_align_1m"] = int(_cur > _ema5 > _ema20 > _ema60)
                    ctx["ema_bear_align_1m"] = int(_cur < _ema5 < _ema20 < _ema60)
                    if len(_closes) >= 10:
                        _ema20_prev = _ema(_closes[-30:-10], min(20,len(_closes)-10)) if len(_closes)>=30 else _ema20
                        ctx["ema_slope_1m"] = round((_ema20 - _ema20_prev)/_ema20_prev*100, 4) if _ema20_prev>0 else 0.0

                # Pre-entry candle quality (last 5 bars before signal)
                if len(_closes) >= 6:
                    _o5 = [float(r["open"]) for r in df_15.to_dict("records")][-5:]
                    _c5 = _closes[-5:]
                    _h5 = _highs[-5:]
                    _l5 = _lows[-5:]
                    _bull5 = sum(1 for o,c in zip(_o5,_c5) if c>o)
                    ctx["pre_entry_bull_bars"] = _bull5
                    _rng5 = [h-l for h,l in zip(_h5,_l5)]
                    _bod5 = [abs(c-o) for c,o in zip(_c5,_o5)]
                    ctx["pre_entry_wick_ratio"] = round(
                        sum(1-b/(r+1e-8) for b,r in zip(_bod5,_rng5))/5, 4)

                # Day range position from candle data
                _day_high = max(_highs)
                _day_low  = min(_lows)
                _day_rng  = _day_high - _day_low
                if _day_rng > 0:
                    ctx["day_range_position_1m"] = round((_cur-_day_low)/_day_rng, 4)

                # Day of week (already set in defaults above, refresh here)
                import math as _math
                _dow = now.weekday()
                ctx["dow_sin_1m"] = round(_math.sin(2*_math.pi*_dow/5), 4)
                ctx["dow_cos_1m"] = round(_math.cos(2*_math.pi*_dow/5), 4)
                ctx["is_monday_1m"]    = int(_dow == 0)
                ctx["is_friday_1m"]    = int(_dow == 4)
                ctx["is_wednesday_1m"] = int(_dow == 2)

                # Simple volume profile: where is vol concentrated in recent bars?
                # Use 15m bar range (already computed) not _day_rng which may not be set yet
                _15m_rng = max(_highs) - min(_lows)
                if len(_vols) >= 10 and _15m_rng > 0:
                    _mids = [(_highs[i]+_lows[i])/2 for i in range(len(_highs))]
                    _total_vol = sum(_vols) or 1
                    _poc_price = sum(m*v for m,v in zip(_mids,_vols))/_total_vol
                    ctx["vol_profile_poc_dist_pct"] = round((_cur-_poc_price)/_poc_price*100, 4) if _poc_price>0 else 0.0

                # ORB relationship: use daily_open and ATR as proxy
                # Full ORB needs session-start tracking; use simplified version
                _d_open = float(ctx.get("daily_open", _closes[0]) or _closes[0])
                _atr_val = float(ctx.get("atr_14", _day_rng/4) or _day_rng/4)
                _orb_high_approx = _d_open + _atr_val * 0.5
                _orb_low_approx  = _d_open - _atr_val * 0.5
                _orb_rng = _orb_high_approx - _orb_low_approx
                if _orb_rng > 0:
                    ctx["orb_position_1m"] = round((_cur - _orb_low_approx)/_orb_rng, 4)
                    ctx["above_orb_1m"]    = int(_cur > _orb_high_approx)
                    ctx["below_orb_1m"]    = int(_cur < _orb_low_approx)
                    ctx["inside_orb_1m"]   = int(_orb_low_approx <= _cur <= _orb_high_approx)

                # Session VWAP: use existing vwap context already computed
                _vwap = float(ctx.get("vwap", 0) or 0)
                if _vwap > 0:
                    ctx["above_session_vwap_1m"]     = int(_cur > _vwap)
                    ctx["session_vwap_dist_pct_1m"]  = round((_cur - _vwap)/_vwap*100, 4)

                ctx["enrichment_ok"] = 1  # live computation succeeded

            except Exception as _enrich_err:
                pass  # defaults already set above

            # ── Brooks: inside bar / outside bar ──
            ctx["is_inside_bar"]        = (float(c["high"]) < float(prev["high"]) and
                                           float(c["low"])  > float(prev["low"]))
            ctx["is_outside_bar"]       = (float(c["high"]) > float(prev["high"]) and
                                           float(c["low"])  < float(prev["low"]))
            ctx["ii_pattern"]           = (ctx["is_inside_bar"] and
                                           float(prev["high"]) < float(prev2["high"]) and
                                           float(prev["low"])  > float(prev2["low"]))

            # ── Trend & market structure ──
            ctx["direction_15m"]        = market_direction(df_15)
            ema_now  = float(df_15.iloc[-1]["ema20"])
            ema_prev = float(df_15.iloc[-5]["ema20"])
            ema_5ago = float(df_15.iloc[-10]["ema20"])
            ctx["ema20"]                = round(ema_now, 2)
            ctx["ema_slope"]            = round((ema_now - ema_prev) / ema_prev * 100, 4)
            ctx["ema_slope_accel"]      = round((ema_now - ema_prev) - (ema_prev - ema_5ago), 4)
            # Kalman filter trend -- more accurate than EMA slope
            _closes_15m = list(df_15["close"].values[-30:])
            _kalman = kalman_trend(_closes_15m)
            ctx["kalman_slope"]         = _kalman["kalman_slope"]
            ctx["kalman_bull"]          = _kalman["kalman_bull"]
            ctx["kalman_noise"]         = _kalman["kalman_noise"]
            ctx["kalman_estimate"]      = _kalman.get("kalman_estimate", ema_now)
            ctx["price_vs_kalman"]      = round((float(c["close"]) - _kalman.get("kalman_estimate", ema_now)) / ema_now * 100, 3)
            ctx["price_above_ema"]      = float(c["close"]) > ema_now
            ctx["distance_from_ema_pct"]= round(abs(float(c["close"]) - ema_now) / ema_now * 100, 3)

            # ── Brooks: higher highs / higher lows (trend quality) ──
            r10 = df_15.iloc[-12:-2]
            r20 = df_15.iloc[-22:-12]
            ctx["higher_highs"]         = float(r10["high"].max()) > float(r20["high"].max())
            ctx["higher_lows"]          = float(r10["low"].min())  > float(r20["low"].min())
            ctx["lower_highs"]          = float(r10["high"].max()) < float(r20["high"].max())
            ctx["lower_lows"]           = float(r10["low"].min())  < float(r20["low"].min())

            # ── Brooks: swing high/low proximity ──
            swing_high = float(df_15.iloc[-20:-2]["high"].max())
            swing_low  = float(df_15.iloc[-20:-2]["low"].min())
            ctx["near_swing_high"]      = abs(float(c["high"]) - swing_high) / swing_high < 0.002
            ctx["near_swing_low"]       = abs(float(c["low"]) - swing_low) / swing_low < 0.002
            ctx["pct_from_swing_high"]  = round((swing_high - float(c["close"])) / swing_high * 100, 3)
            ctx["pct_from_swing_low"]   = round((float(c["close"]) - swing_low) / swing_low * 100, 3)

            # ── Volatility: ATR 14 ──
            highs  = df_15["high"].values[-15:]
            lows   = df_15["low"].values[-15:]
            closes = df_15["close"].values[-15:]
            trs    = [max(highs[i]-lows[i], abs(highs[i]-closes[i-1]), abs(lows[i]-closes[i-1]))
                      for i in range(1, len(highs))]
            ctx["atr_14"]               = round(float(sum(trs)/len(trs)), 2) if trs else 0.0
            ctx["atr_ratio"]            = round(ctx["candle_size"] / ctx["atr_14"], 2) if ctx["atr_14"] > 0 else 1.0

            # ── RSI 14 ──
            closes_s = df_15["close"].values[-16:]
            deltas   = [closes_s[i]-closes_s[i-1] for i in range(1, len(closes_s))]
            gains    = [d for d in deltas if d > 0]
            losses   = [abs(d) for d in deltas if d < 0]
            avg_gain = sum(gains)/14 if gains else 0
            avg_loss = sum(losses)/14 if losses else 0.0001
            rsi      = round(100-(100/(1+(avg_gain/avg_loss))), 1)
            ctx["rsi_14"]               = rsi
            ctx["rsi_oversold"]         = rsi < 30
            ctx["rsi_overbought"]       = rsi > 70
            ctx["rsi_extreme"]          = rsi < 20 or rsi > 80

            # ── Brooks: trading range detection ──
            is_rng_15, rng_h, rng_l    = in_trading_range(df_15)
            ctx["in_range_15m"]         = is_rng_15
            ctx["range_size_15m"]       = round(rng_h - rng_l, 2)
            ctx["price_in_range_pct"]   = round((float(c["close"]) - rng_l) / (rng_h - rng_l), 3) if (rng_h - rng_l) > 0 else 0.5

            # ── Key levels ──
            levels = get_key_levels(signal.symbol)
            if levels:
                all_levels = [levels.daily_open, levels.yesterday_high,
                              levels.yesterday_low, levels.last_week_high, levels.last_week_low]
                dists = [abs(signal.entry-v)/signal.entry*100 for v in all_levels]
                ctx["nearest_key_pct"]      = round(min(dists), 4)
                ctx["at_daily_open"]        = dists[0] < 0.1
                ctx["at_yesterday_high"]    = dists[1] < 0.1
                ctx["at_yesterday_low"]     = dists[2] < 0.1
                ctx["at_weekly_high"]       = dists[3] < 0.15
                ctx["at_weekly_low"]        = dists[4] < 0.15

            # ── Trade setup properties ──
            stop_size = abs(signal.entry - signal.stop_loss)
            ctx["stop_size"]            = round(stop_size, 2)
            ctx["stop_atr_ratio"]       = round(stop_size / ctx["atr_14"], 2) if ctx["atr_14"] > 0 else 0
            ctx["reward_size"]          = round(abs(signal.take_profit - signal.entry), 2)
            ctx["rr_ratio"]             = round(ctx["reward_size"] / stop_size, 2) if stop_size > 0 else 0

            # ── Spread ──
            tick = mt5.symbol_info_tick(signal.symbol)
            if tick:
                ctx["spread"]           = round(tick.ask - tick.bid, 2)
                ctx["spread_atr_ratio"] = round(ctx["spread"] / ctx["atr_14"], 3) if ctx["atr_14"] > 0 else 0

            # ── Overnight range ──
            overnight = get_overnight_range(signal.symbol)
            if overnight:
                on_h, on_l = overnight
                on_sz = on_h - on_l
                ctx["overnight_range"]      = round(on_sz, 2)
                ctx["overnight_atr_ratio"]  = round(on_sz / ctx["atr_14"], 2) if ctx["atr_14"] > 0 else 0
                ctx["price_vs_overnight"]   = round((signal.entry-on_l)/on_sz, 3) if on_sz > 0 else 0.5
                ctx["above_overnight"]      = signal.entry > on_h
                ctx["below_overnight"]      = signal.entry < on_l
                ctx["inside_overnight"]     = on_l <= signal.entry <= on_h

            # ── Brooks: climactic move check ──
            last5_ranges = df_15.iloc[-7:-2]["bar_range"].values
            ctx["prev_bar_climactic"]   = float(prev["bar_range"]) > avg_range * 2.5
            ctx["momentum_5bars"]       = round(float(df_15.iloc[-2]["close"]) - float(df_15.iloc[-7]["close"]), 2)

            # ── RSI divergence ──
            price_high_recent  = float(df_15.iloc[-6:-2]["high"].max())
            price_high_prev    = float(df_15.iloc[-12:-6]["high"].max())
            price_low_recent   = float(df_15.iloc[-6:-2]["low"].min())
            price_low_prev     = float(df_15.iloc[-12:-6]["low"].min())
            ctx["bearish_divergence"] = (price_high_recent > price_high_prev and rsi < 55)
            ctx["bullish_divergence"] = (price_low_recent < price_low_prev and rsi > 45)

            # ── Daily context ──
            try:
                daily = get_candles(signal.symbol, mt5.TIMEFRAME_D1, 3)  # 10s cache -- was direct MT5
                if daily is not None and len(daily) >= 2:
                    d_today = daily.iloc[-1]
                    d_yest  = daily.iloc[-2]
                    d_open  = float(d_today["open"])
                    d_high  = float(d_today["high"])
                    d_low   = float(d_today["low"])
                    d_range = d_high - d_low
                    ctx["daily_open"]            = round(d_open, 2)
                    ctx["daily_range"]           = round(d_range, 2)
                    ctx["daily_range_atr_ratio"] = round(d_range / ctx["atr_14"], 2) if ctx["atr_14"] > 0 else 1.0
                    ctx["pos_in_daily_range"]    = round((signal.entry - d_low) / d_range, 3) if d_range > 0 else 0.5
                    ctx["daily_trend"]           = "bull" if float(d_today["close"]) > d_open else "bear"
                    ctx["daily_gap"]             = round(d_open - float(d_yest["close"]), 2)
                    ctx["daily_gap_pct"]         = round(ctx["daily_gap"] / float(d_yest["close"]) * 100, 3)
                    ctx["distance_from_daily_open_pct"] = round((signal.entry - d_open) / d_open * 100, 3)
            except Exception as _e:
                log.debug(f"Feature block failed: {_e}")

        # ── 5m context ──
        if df_5 is not None and len(df_5) >= 10:
            c5 = df_5.iloc[-2]
            ctx["direction_5m"]         = market_direction(df_5)
            ctx["rsi_5m"]               = round(bar_close_pos(c5) * 100, 1)
            ctx["is_strong_bull_5m"]    = is_strong_bull(c5)
            ctx["is_strong_bear_5m"]    = is_strong_bear(c5)
            is_rng_5, _, _              = in_trading_range(df_5)
            ctx["in_range_5m"]          = is_rng_5
            avg5 = float(df_5.iloc[-10:-2]["bar_range"].mean())
            ctx["candle_size_ratio_5m"] = round(float(c5["bar_range"]) / avg5, 2) if avg5 > 0 else 1.0

        # ── 1h context (higher timeframe bias) ──
        if df_1h is not None and len(df_1h) >= 10:
            ctx["direction_1h"]         = market_direction(df_1h)
            ctx["ema20_1h"]             = round(float(df_1h.iloc[-1]["ema20"]), 2)
            ctx["price_above_ema_1h"]   = float(df_1h.iloc[-2]["close"]) > float(df_1h.iloc[-1]["ema20"])
            is_rng_1h, _, _             = in_trading_range(df_1h)
            ctx["in_range_1h"]          = is_rng_1h

        # ── Advanced quant features ──

        # 1. VIX equivalent -- rolling 20-day ATR as % of price (implied vol proxy)
        try:
            d_df = get_candles(signal.symbol, mt5.TIMEFRAME_D1, 25)  # 10s cache -- was direct MT5
            if d_df is not None and len(d_df) >= 20:
                daily_ranges = d_df["high"] - d_df["low"]
                vix_equiv = float(daily_ranges.iloc[-20:].mean()) / float(d_df.iloc[-1]["close"]) * 100
                ctx["vix_equiv_pct"]        = round(vix_equiv, 3)
                ctx["vix_high"]             = vix_equiv > 1.5   # high vol regime
                ctx["vix_low"]              = vix_equiv < 0.5   # low vol regime

                # Daily range exceeded
                today_range = float(d_df.iloc[-1]["high"]) - float(d_df.iloc[-1]["low"])
                avg_daily_range = float(daily_ranges.iloc[-20:].mean())
                ctx["daily_range_pct_complete"] = round(today_range / avg_daily_range, 2) if avg_daily_range > 0 else 0
                ctx["daily_range_exceeded"]     = today_range > avg_daily_range

                # Consecutive ranging days
                ranging_days = 0
                for i in range(len(d_df)-2, max(len(d_df)-15, 0), -1):
                    row = d_df.iloc[i]
                    day_range = float(row["high"]) - float(row["low"])
                    if day_range < avg_daily_range * 0.75:
                        ranging_days += 1
                    else:
                        break
                ctx["consecutive_ranging_days"] = ranging_days

                # Monday gap size
                if now.weekday() == 0:  # Monday
                    gap = abs(float(d_df.iloc[-1]["open"]) - float(d_df.iloc[-2]["close"]))
                    ctx["monday_gap"]     = round(gap, 2)
                    ctx["monday_gap_pct"] = round(gap / float(d_df.iloc[-2]["close"]) * 100, 3)
                else:
                    ctx["monday_gap"]     = 0
                    ctx["monday_gap_pct"] = 0
        except Exception as e:
            log.warning(f"Advanced daily context error: {e}")

        # 2. Symbol correlation -- are other symbols trending same direction?
        try:
            other_symbols = [s for s in ALL_SYMBOLS if s != signal.symbol]
            same_direction = 0
            for other in other_symbols:
                df_other = get_candles(other, TF_15M, 30)
                if df_other is not None:
                    other_dir = market_direction(df_other)
                    my_dir = ctx.get("direction_15m", "range")
                    if other_dir == my_dir and my_dir != "range":
                        same_direction += 1
            ctx["symbols_same_direction"] = same_direction  # 0-3
            ctx["high_correlation"]       = same_direction >= 2
        except Exception as e:
            log.warning(f"Correlation context error: {e}")

        # 3. Level test count -- how many times has price been at this level?
        try:
            if df_15 is not None and len(df_15) >= 50:
                entry_price = signal.entry
                tolerance   = entry_price * 0.002  # 0.2% tolerance
                tests = sum(1 for i in range(len(df_15)-20, len(df_15)-2)
                           if abs(float(df_15.iloc[i]["high"]) - entry_price) < tolerance or
                              abs(float(df_15.iloc[i]["low"])  - entry_price) < tolerance)
                ctx["level_test_count"] = tests
                ctx["level_3rd_test"]   = tests >= 3  # 3rd test = weakest
        except Exception as e:
            log.warning(f"Level test context error: {e}")

        # 4. Round number distance -- price magnets
        try:
            round_levels = []
            base = signal.entry
            magnitude = 10 ** (len(str(int(base))) - 2)  # e.g. 22500 -> 100
            for mult in range(int(base / magnitude) - 2, int(base / magnitude) + 3):
                round_levels.append(mult * magnitude)
            nearest_round = min(round_levels, key=lambda x: abs(x - base))
            dist_to_round = abs(base - nearest_round)
            ctx["dist_to_round_number"]     = round(dist_to_round, 2)
            ctx["dist_to_round_number_pct"] = round(dist_to_round / base * 100, 3)
            ctx["near_round_number"]        = dist_to_round / base < 0.001  # within 0.1%
        except Exception as e:
            log.warning(f"Round number context error: {e}")

        # 5. Time since last 1% move -- momentum decay
        try:
            if df_15 is not None and len(df_15) >= 50:
                one_pct = signal.entry * 0.01
                bars_since_big_move = 0
                for i in range(len(df_15)-3, max(len(df_15)-50, 0), -1):
                    if float(df_15.iloc[i]["bar_range"]) >= one_pct:
                        break
                    bars_since_big_move += 1
                ctx["bars_since_1pct_move"]  = bars_since_big_move
                ctx["momentum_fresh"]        = bars_since_big_move < 5
                ctx["momentum_decayed"]      = bars_since_big_move > 20
        except Exception as e:
            log.warning(f"Momentum decay context error: {e}")

        # 6. London close flag -- choppy zone 13:00-15:00 UTC
        ctx["london_close_zone"] = 13 <= now.hour < 15

        # ── FEATURE 1: Calendar effects ───────────────────────────────
        # Structural market mechanics that repeat every cycle.
        # Options expiry, month-end flows, central bank days.
        try:
            import datetime as _dt
            today      = now.date()
            dom        = today.day        # day of month
            dow        = today.weekday()  # 0=Mon, 4=Fri
            month      = today.month

            # Options expiry: third Friday of every month
            # Find third Friday: first Friday + 14 days
            first_day  = today.replace(day=1)
            first_fri  = (4 - first_day.weekday()) % 7  # days until first Friday
            third_fri  = first_fri + 14 + 1             # +1 = day number
            is_opex_week = (dom >= third_fri - 1 and dom <= third_fri + 1)
            is_opex_day  = (dom == third_fri and dow == 4)

            # Month-end: last 2 trading days of month -- pension rebalancing
            import calendar
            last_day_of_month = calendar.monthrange(today.year, month)[1]
            is_month_end = dom >= last_day_of_month - 2

            # Month-start: first 2 days -- new allocations
            is_month_start = dom <= 2

            # Monday open: gaps from weekend, often reverses
            is_monday_open = (dow == 0 and now.hour < 6)

            # Friday close: position squaring before weekend
            is_friday_close_zone = (dow == 4 and now.hour >= 15)

            ctx["is_opex_week"]       = is_opex_week
            ctx["is_opex_day"]        = is_opex_day
            ctx["is_month_end"]       = is_month_end
            ctx["is_month_start"]     = is_month_start
            ctx["is_monday_open"]     = is_monday_open
            ctx["is_friday_close_zone"] = is_friday_close_zone
            ctx["calendar_risk"]      = is_opex_day or is_month_end or is_friday_close_zone
        except Exception as e:
            log.warning(f"Calendar effects error: {e}")

        # ── FEATURE 2: Spread gate ────────────────────────────────────
        # Wide spread = market maker protecting from unknown risk.
        # Track spread vs historical average for this hour.
        try:
            tick     = mt5.symbol_info_tick(signal.symbol)
            sym_info = mt5.symbol_info(signal.symbol)
            if tick and sym_info:
                raw_spread  = (tick.ask - tick.bid) / sym_info.point
                point_value = sym_info.point
                # Historical spread for this hour from recent trades
                # PERF: cache LOG_FILE read with 60s TTL -- called on every signal evaluation
                _sp_cache_key = "_spread_gate_cache"
                _sp_ts_key    = "_spread_gate_cache_ts"
                _now_sp       = datetime.now(timezone.utc).timestamp()
                _sp_cached    = getattr(capture_market_context, _sp_cache_key, None)
                _sp_cached_ts = getattr(capture_market_context, _sp_ts_key, 0)
                if _sp_cached is None or (_now_sp - _sp_cached_ts) > 60:
                    if os.path.exists(LOG_FILE):
                        with open(LOG_FILE, encoding="utf-8") as _f:
                            _sp_cached = json.load(_f)
                        setattr(capture_market_context, _sp_cache_key, _sp_cached)
                        setattr(capture_market_context, _sp_ts_key, _now_sp)
                _all = _sp_cached or []
                this_hour_trades = [
                    t for t in _all[-200:]
                    if t.get("context",{}).get("hour_server") == now.hour
                    and t.get("context",{}).get("spread_pts") is not None
                    and t.get("symbol") == signal.symbol
                ]
                if len(this_hour_trades) >= 5:
                    hist_spreads = [t["context"]["spread_pts"]
                                   for t in this_hour_trades]
                    avg_spread   = sum(hist_spreads) / len(hist_spreads) if hist_spreads else 0
                    spread_ratio = raw_spread / avg_spread if avg_spread > 0 else 1.0
                    ctx["spread_vs_hourly_avg"] = round(spread_ratio, 2)
                    ctx["spread_abnormal"]      = spread_ratio > 2.0
                    ctx["spread_very_wide"]     = spread_ratio > 3.0
                    if spread_ratio > 3.0:
                        log.warning(f"  SPREAD GATE: {signal.symbol} spread {raw_spread:.1f}pts "
                                   f"= {spread_ratio:.1f}x normal -- caution")
        except Exception as e:
            log.warning(f"Spread gate error: {e}")

        # ── FEATURE 3: More symbol pairs ─────────────────────────────
        # GER40 vs US100, US30 vs US100, UK100 vs GER40
        # Each pair adds uncorrelated signal.
        try:
            df_ger  = get_candles("GER40.cash", TF_15M, 30)
            df_us30 = get_candles("US30",  TF_15M, 30)
            df_us100= get_candles("USTEC", TF_15M, 30)
            df_uk   = get_candles("UK100.cash", TF_15M, 30)

            def _pair_zscore(df_a, df_b, name):
                if df_a is None or df_b is None:
                    return
                n = min(len(df_a), len(df_b), 25)
                a_norm = [float(df_a.iloc[i]["close"])/float(df_a.iloc[0]["close"])
                         for i in range(n)]
                b_norm = [float(df_b.iloc[i]["close"])/float(df_b.iloc[0]["close"])
                         for i in range(n)]
                spread = [a_norm[i]-b_norm[i] for i in range(n)]
                mean_s = sum(spread)/n
                std_s  = (sum((s-mean_s)**2 for s in spread)/n)**0.5
                if std_s > 0:
                    z = (spread[-1]-mean_s)/std_s
                    ctx[f"{name}_zscore"]   = round(z, 3)
                    ctx[f"{name}_diverged"] = abs(z) > 1.5
                    ctx[f"{name}_extreme"]  = abs(z) > 2.5

            _pair_zscore(df_ger,  df_us100, "ger_us100")
            _pair_zscore(df_us30, df_us100, "us30_us100")
            _pair_zscore(df_uk,   df_ger,   "uk_ger")
        except Exception as e:
            log.warning(f"Pairs expansion error: {e}")

        # ── FEATURE 4: Session transition detector ────────────────────
        # London->NY handoff 14:45-15:30 UTC = most volatile transition.
        # Asia->London handoff 07:45-08:30 UTC = second most important.
        try:
            h, m     = now.hour, now.minute
            hm       = h * 60 + m  # minutes since midnight UTC
            # London open: 08:00 UTC
            asia_lon_trans  = (7*60+45 <= hm <= 8*60+30)
            # NY open: 15:00 UTC (EST open, UK already open)
            lon_ny_trans    = (14*60+45 <= hm <= 15*60+30)
            # London close: 16:00-16:30 UTC (UK market closes)
            lon_close_trans = (16*60+0 <= hm <= 16*60+30)
            # NY close: 20:30-21:00 UTC
            ny_close_trans  = (20*60+30 <= hm <= 21*60+0)

            ctx["asia_lon_transition"]  = asia_lon_trans
            ctx["lon_ny_transition"]    = lon_ny_trans
            ctx["lon_close_transition"] = lon_close_trans
            ctx["ny_close_transition"]  = ny_close_trans
            ctx["any_session_transition"] = any([
                asia_lon_trans, lon_ny_trans, lon_close_trans, ny_close_trans
            ])
            # 20:00 UTC = 84.3% win rate -- that's NY close exhaustion
            ctx["ny_close_zone"] = (20*60 <= hm <= 21*60+30)
        except Exception as e:
            log.warning(f"Session transition error: {e}")

        # ── FEATURE 5: Consecutive losing days ───────────────────────
        # After 2 losing days -- regime may have shifted. Size down.
        # Simons reduced overall exposure after consecutive losing days.
        try:
            _all = _cached_trades  # shared log cache
            # Get daily P&L for last 5 days
            from collections import defaultdict
            daily_outcomes = defaultdict(lambda: {"wins":0,"losses":0})
            for t in _all:
                if t.get("outcome") not in ("win","loss","eod_win","eod_loss"):
                    continue
                date_str = t.get("timestamp","")[:10]
                if not date_str:
                    continue
                if t["outcome"] in ("win", "eod_win"):
                    daily_outcomes[date_str]["wins"] += 1
                else:
                    daily_outcomes[date_str]["losses"] += 1

            # Last 5 days sorted
            today_str   = now.strftime("%Y-%m-%d")
            sorted_days = sorted([d for d in daily_outcomes if d < today_str])[-5:]
            losing_streak = 0
            for day in reversed(sorted_days):
                d = daily_outcomes[day]
                total = d["wins"] + d["losses"]
                if total >= 5 and d["wins"]/total < 0.45:
                    losing_streak += 1
                else:
                    break

            ctx["losing_days_streak"]  = losing_streak
            ctx["on_losing_streak"]    = losing_streak >= 2
            ctx["streak_size_penalty"] = max(0.5, 1.0 - losing_streak * 0.15)
            if losing_streak >= 2:
                # Only log once per hour to avoid spam (computed every signal check)
                _streak_key = f"_last_streak_log_{losing_streak}"
                _now_h = datetime.now(timezone.utc).hour  # UTC for throttle key
                if not hasattr(capture_market_context, _streak_key) or                        getattr(capture_market_context, _streak_key) != _now_h:
                    # v181: log message clarified -- penalty is computed for ML feature
                    # but NOT applied to risk sizing (see streak_size_penalty=DATA ONLY
                    # comment in adaptive_brooks_risk).
                    log.warning(f"  LOSING STREAK: {losing_streak} consecutive losing days "
                               f"(ML feature: penalty would be {ctx['streak_size_penalty']:.2f}x -- not applied to risk)")
                    setattr(capture_market_context, _streak_key, _now_h)
        except Exception as e:
            log.warning(f"Losing days streak error: {e}")

        # ── SHANNON: Mutual information proxies ──────────────────────
        # Which features are genuinely independent vs redundant?
        # Measure correlation between key signals -- high correlation = redundant
        # ML learns to down-weight redundant signals automatically
        try:
            ema_s  = ctx.get("ema_slope", 0) or 0
            mom5   = ctx.get("momentum_5bars", 0) or 0
            kalman = ctx.get("kalman_slope_pct", 0) or 0
            ac1    = ctx.get("autocorr_lag1", 0) or 0
            # Agreement score -- how many momentum signals agree
            momentum_signals = [ema_s > 0, mom5 > 0, kalman > 0, ac1 > 0.05]
            momentum_agree   = sum(1 for x in momentum_signals if x)
            momentum_disagree= sum(1 for x in momentum_signals if not x)
            ctx["momentum_signal_agreement"] = momentum_agree / 4
            ctx["momentum_signal_conflict"]  = abs(momentum_agree - momentum_disagree) < 2
            # Price action vs momentum divergence (key reversal signal)
            price_up  = ctx.get("higher_highs", False)
            mom_down  = ema_s < 0
            ctx["price_momentum_divergence"] = price_up and mom_down
        except Exception as e:
            log.warning(f"Shannon mutual info error: {e}")

        # ── THORP: True portfolio heat ─────────────────────────────────
        # Not just number of positions -- correlation-weighted exposure
        # 3 GER40 longs + 1 US30 long = 3.5 effective positions not 4
        try:
            positions = mt5.positions_get() or []
            if positions:
                # Group by direction
                longs  = [p for p in positions if p.type == 0]
                shorts = [p for p in positions if p.type == 1]
                # Correlation-adjusted heat
                # Same symbol = 1.0 correlation, different = 0.6 correlation
                def corr_heat(pos_list):
                    if not pos_list: return 0
                    symbols = [p.symbol for p in pos_list]
                    heat = 0
                    for i, p in enumerate(pos_list):
                        # First position full weight, same symbol = 0.8x, diff symbol = 0.6x
                        if i == 0:
                            heat += 1.0
                        elif symbols[i] == symbols[i-1]:
                            heat += 0.8
                        else:
                            heat += 0.6
                    return heat
                ctx["corr_adjusted_long_heat"]  = round(corr_heat(longs), 2)
                ctx["corr_adjusted_short_heat"] = round(corr_heat(shorts), 2)
                ctx["corr_adjusted_total_heat"] = round(
                    corr_heat(longs) + corr_heat(shorts), 2)
                ctx["true_portfolio_overweight"] = (
                    corr_heat(longs) > 3 or corr_heat(shorts) > 3)
        except Exception as e:
            log.warning(f"Thorp portfolio heat error: {e}")

        # ── SIMONS: Regime persistence ─────────────────────────────────
        # How long has the current regime been active?
        # New regime = uncertain, established regime = more reliable
        try:
            _all_t = _cached_trades  # shared log cache
            current_regime = ctx.get("macro_regime", "unknown")
            # Look back through recent trades to find when regime changed
            recent_100 = [t for t in _all_t
                         if t.get("context",{}).get("macro_regime")][-100:]
            regime_streak = 0
            for t in reversed(recent_100):
                if t.get("context",{}).get("macro_regime") == current_regime:
                    regime_streak += 1
                else:
                    break
            ctx["regime_persistence"]    = regime_streak
            ctx["regime_established"]    = regime_streak >= 20
            ctx["regime_new"]            = regime_streak < 5
            ctx["regime_mature"]         = regime_streak >= 50
        except Exception as e:
            log.warning(f"Regime persistence error: {e}")

        # ── GAUSS: Residual analysis ───────────────────────────────────
        # The trades the model was most wrong about -- what's different about them?
        # High residual = model doesn't understand this condition
        # Log confidence gap as a feature -- ML learns its own blind spots
        try:
            ml_prob    = ctx.get("ml_win_prob", 0.5) or 0.5
            actual_win = None  # unknown at trade time
            # Log confidence as distance from 0.5 -- how certain is the model?
            ctx["ml_confidence_strength"] = abs(ml_prob - 0.5) * 2  # 0=uncertain, 1=certain
            ctx["ml_very_confident"]      = abs(ml_prob - 0.5) > 0.3
            ctx["ml_uncertain"]           = abs(ml_prob - 0.5) < 0.1
            # When model is uncertain -- market is genuinely unpredictable
            # When model is very confident -- either real signal or overfitting
            implied  = ctx.get("implied_edge", 0.5) or 0.5
            if implied > 0:
                ctx["model_vs_math_agree"] = abs(ml_prob - implied) < 0.1
                ctx["model_vs_math_conflict"] = abs(ml_prob - implied) > 0.2
        except Exception as e:
            log.warning(f"Gauss residual error: {e}")

        # ── MANDELBROT: Multi-scale volatility ────────────────────────
        # Volatility measured at 3 timescales simultaneously
        # When all 3 agree = reliable signal
        # When they disagree = volatility regime is transitioning
        try:
            vol_measures = {}
            for tf_name, tf_obj, n_bars in [
                ("5m", TF_5M, 20), ("15m", TF_15M, 20)
            ]:
                df_v = get_candles(signal.symbol, tf_obj, n_bars+5)
                if df_v is not None and len(df_v) >= n_bars:
                    ranges = df_v["bar_range"].values.astype(float)[-n_bars:]
                    vol_measures[tf_name] = float(ranges.mean())

            if len(vol_measures) >= 2:
                v5  = vol_measures.get("5m", 0)
                v15 = vol_measures.get("15m", 0)
                if v15 > 0:
                    vol_scale_ratio = v5 / v15
                    ctx["vol_scale_ratio_5_15"]   = round(vol_scale_ratio, 3)
                    ctx["vol_scales_agree"]        = 0.8 <= vol_scale_ratio <= 1.2
                    ctx["vol_expanding_multi"]     = vol_scale_ratio > 1.3
                    ctx["vol_contracting_multi"]   = vol_scale_ratio < 0.7
        except Exception as e:
            log.warning(f"Mandelbrot multi-scale vol error: {e}")

        # ── BLACK-SCHOLES: Time decay ──────────────────────────────────
        # Options lose value as expiry approaches -- same principle applies here
        # A setup that fires 10 minutes before a key level is "time-decayed"
        # vs one that fires right at the level
        try:
            # Time since last significant price level test
            level_tests = ctx.get("level_test_count", 0) or 0
            bars_since  = ctx.get("bars_since_sig_move", 999) or 999
            # "Freshness" of the setup -- higher = setup has aged well
            setup_freshness = 1.0 / (1 + bars_since * 0.1)
            ctx["setup_freshness"]     = round(setup_freshness, 3)
            ctx["setup_stale_bs"]      = bars_since > 10  # Black-Scholes time decay
            ctx["setup_fresh_bs"]      = bars_since <= 3
            ctx["level_tested_recently"] = level_tests >= 2 and bars_since <= 5
        except Exception as e:
            log.warning(f"Black-Scholes time decay error: {e}")

        # ── KAHNEMAN: Loss aversion index ─────────────────────────────
        # Track how often this setup wins after a recent loss on same setup
        # Humans (and bots) often overtrade after losses -- "revenge trading"
        # The ML needs to know: is this trade following a recent loss?
        try:
            _all_k = _cached_trades  # shared log cache
            setup_key_k = f"{signal.strategy}|{signal.setup_name}"
            recent_setup = [t for t in _all_k
                           if f"{t.get('strategy')}|{t.get('setup_name')}" == setup_key_k
                           and t.get("outcome") in ("win","loss")][-5:]
            if recent_setup:
                last_outcome   = recent_setup[-1].get("outcome")
                last_was_loss  = last_outcome in ("loss", "eod_loss")
                # Win rate after losses vs after wins for this setup
                after_loss_wins = sum(1 for i in range(1, len(recent_setup))
                                     if recent_setup[i-1]["outcome"] in ("loss","eod_loss")
                                     and recent_setup[i]["outcome"] in ("win","eod_win"))
                after_loss_total = sum(1 for i in range(1, len(recent_setup))
                                      if recent_setup[i-1]["outcome"] in ("loss","eod_loss"))
                ctx["last_trade_was_loss"]   = last_was_loss
                ctx["consecutive_setup_losses"] = sum(
                    1 for t in reversed(recent_setup)
                    if t.get("outcome") in ("loss","eod_loss")
                ) if recent_setup else 0
                if after_loss_total > 0:
                    ctx["win_rate_after_loss"] = round(
                        after_loss_wins/after_loss_total, 2)
        except Exception as e:
            log.warning(f"Kahneman loss aversion error: {e}")

        # ── Kelly and regime features for ML ──────────────────────────
        try:
            macro_regime = get_current_regime(signal.symbol)
            ctx["macro_regime"]         = macro_regime
            ctx["regime_with_trend"]    = (
                (macro_regime == "trending_bull" and signal.direction == "long") or
                (macro_regime == "trending_bear" and signal.direction == "short")
            )
            ctx["regime_against_trend"] = (
                (macro_regime == "trending_bull" and signal.direction == "short") or
                (macro_regime == "trending_bear" and signal.direction == "long")
            )
            ctx["regime_multiplier"]    = regime_risk_multiplier(macro_regime, signal.direction)
        except Exception as e:
            log.warning(f"Regime context error: {e}")

        # 7. Portfolio heat -- total % risk across all open positions
        try:
            positions = mt5.positions_get()
            total_heat = 0.0
            long_count = 0
            short_count = 0
            if positions:
                balance = mt5.account_info().balance
                for pos in positions:
                    if pos.sl != 0 and balance > 0:
                        risk_amt = abs(pos.price_open - pos.sl) * pos.volume
                        tick = mt5.symbol_info(pos.symbol)
                        if tick:
                            risk_pct_pos = risk_amt / balance * 100
                            total_heat += risk_pct_pos
                    if pos.type == mt5.ORDER_TYPE_BUY:
                        long_count += 1
                    else:
                        short_count += 1
            ctx["portfolio_heat_pct"]  = round(total_heat, 3)
            ctx["open_longs"]          = long_count
            ctx["open_shorts"]         = short_count
            ctx["open_positions_total"]= long_count + short_count
            ctx["high_portfolio_heat"] = total_heat > 2.0  # >2% total risk
        except Exception as e:
            log.warning(f"Portfolio heat context error: {e}")

        # 8. Same time yesterday -- recurring pattern check
        try:
            yesterday_hour  = now.hour
            yesterday_minute_band = now.minute // 15  # 15-min bands
            all_trades = _cached_trades  # shared log cache
            yesterday_str = (now - timedelta(days=1)).strftime("%Y-%m-%d")  # now is UTC
            same_time_trades = [
                t for t in all_trades
                if t.get("symbol") == signal.symbol
                and t.get("setup_name") == signal.setup_name
                and t.get("timestamp", "").startswith(yesterday_str)
                and t.get("context", {}).get("hour_server") == yesterday_hour
            ]
            yesterday_outcome = None
            if same_time_trades:
                last = same_time_trades[-1]
                yesterday_outcome = last.get("outcome")
            ctx["same_setup_yesterday"]         = len(same_time_trades) > 0
            # Encode string as int -- float() on strings silently gives NaN in training
            _enc = {"win": 1, "eod_win": 1, "loss": -1, "eod_loss": -1}
            ctx["same_setup_yesterday_outcome"] = _enc.get(yesterday_outcome or "none", 0)
        except Exception as e:
            log.warning(f"Yesterday pattern context error: {e}")

        # ── NEW: Market microstructure features ───────────────────────────

        # 9. Bid-ask spread quality -- wider spread = worse fill = harder to profit
        try:
            tick = mt5.symbol_info_tick(signal.symbol)
            sym_info = mt5.symbol_info(signal.symbol)
            if tick and sym_info:
                raw_spread = tick.ask - tick.bid
                avg_spread = sym_info.spread * sym_info.point
                ctx["spread_raw"]          = round(raw_spread, 4)
                ctx["spread_vs_avg"]       = round(raw_spread / avg_spread, 2) if avg_spread > 0 else 1.0
                ctx["spread_wide"]         = raw_spread > avg_spread * 1.5
                ctx["spread_pts"]          = round(raw_spread / sym_info.point, 1)
        except Exception as e:
            log.warning(f"Spread microstructure error: {e}")

        # 10. Volume quality -- signal bar volume vs recent average
        try:
            if df_15 is not None and len(df_15) >= 20:
                recent_vols   = df_15["tick_volume"].iloc[-20:-2].values.astype(float)
                signal_vol    = float(df_15.iloc[-2]["tick_volume"])
                avg_vol       = float(recent_vols.mean()) if len(recent_vols) > 0 else 1.0
                ctx["signal_bar_volume"]      = int(signal_vol)
                ctx["volume_vs_avg_20"]       = round(signal_vol / avg_vol, 2) if avg_vol > 0 else 1.0
                ctx["high_volume_signal"]     = signal_vol > avg_vol * 1.5
                ctx["low_volume_signal"]      = signal_vol < avg_vol * 0.5
                # Volume trend -- is volume picking up or dying?
                first_half  = float(recent_vols[:10].mean()) if len(recent_vols) >= 10 else avg_vol
                second_half = float(recent_vols[10:].mean()) if len(recent_vols) >= 20 else avg_vol
                ctx["volume_trend_rising"]    = second_half > first_half * 1.1
                ctx["volume_trend_falling"]   = second_half < first_half * 0.9
        except Exception as e:
            log.warning(f"Volume microstructure error: {e}")

        # 11. Time since last significant price move (staleness)
        try:
            if df_15 is not None and len(df_15) >= 50:
                atr = ctx.get("atr_14", 1)
                bars_since_sig_move = 0
                for i in range(len(df_15)-3, max(len(df_15)-50, 0), -1):
                    bar_move = float(df_15.iloc[i]["bar_range"])
                    if bar_move >= atr * 0.8:  # 80% of ATR = significant
                        break
                    bars_since_sig_move += 1
                ctx["bars_since_sig_move"]    = bars_since_sig_move
                ctx["setup_stale"]            = bars_since_sig_move > 15
                ctx["setup_fresh"]            = bars_since_sig_move < 5
        except Exception as e:
            log.warning(f"Staleness error: {e}")

        # 12. Distance from previous day high/low/close (magnetic levels)
        try:
            daily_bars = get_candles(signal.symbol, mt5.TIMEFRAME_D1, 3)  # 10s cache -- was direct MT5
            if daily_bars is not None and len(daily_bars) >= 2:
                prev_day   = daily_bars.iloc[-2]
                prev_high  = float(prev_day["high"])
                prev_low   = float(prev_day["low"])
                prev_close = float(prev_day["close"])
                entry      = signal.entry
                atr        = ctx.get("atr_14", 1)
                ctx["dist_to_prev_high"]      = round(abs(entry - prev_high), 2)
                ctx["dist_to_prev_low"]       = round(abs(entry - prev_low), 2)
                ctx["dist_to_prev_close"]     = round(abs(entry - prev_close), 2)
                ctx["dist_prev_high_atr"]     = round(abs(entry - prev_high) / atr, 2) if atr > 0 else 0
                ctx["dist_prev_low_atr"]      = round(abs(entry - prev_low)  / atr, 2) if atr > 0 else 0
                ctx["dist_prev_close_atr"]    = round(abs(entry - prev_close)/ atr, 2) if atr > 0 else 0
                ctx["near_prev_high"]         = abs(entry - prev_high) < atr * 0.3
                ctx["near_prev_low"]          = abs(entry - prev_low)  < atr * 0.3
                ctx["near_prev_close"]        = abs(entry - prev_close)< atr * 0.3
                ctx["above_prev_high"]        = entry > prev_high
                ctx["below_prev_low"]         = entry < prev_low
        except Exception as e:
            log.warning(f"Prev day levels error: {e}")

        # ── NEW: Cross-symbol correlation features ────────────────────────

        # 13. All symbols same direction + GER40 leading US30
        try:
            sym_directions = {}
            for s in ALL_SYMBOLS:
                df_s = get_candles(s, TF_15M, 30)
                if df_s is not None and len(df_s) >= 10:
                    sym_directions[s] = market_direction(df_s)

            my_dir = ctx.get("direction_15m", "range")
            n_same = sum(1 for d in sym_directions.values()
                        if d == my_dir and my_dir != "range")
            ctx["n_symbols_same_dir"]     = n_same
            ctx["all_symbols_aligned"]    = n_same >= 3
            ctx["strong_confluence"]      = n_same == 4

            # GER40 leading US30 -- check if GER40 moved before US30 did
            if "GER40.cash" in sym_directions and "US30" in sym_directions:
                df_ger = get_candles("GER40.cash", TF_15M, 5)
                df_us  = get_candles("US30",  TF_15M, 5)
                if df_ger is not None and df_us is not None and len(df_ger) >= 4 and len(df_us) >= 4:
                    # GER40 moved 2 bars ago, US30 moving now = GER40 led
                    ger_move_2bars = float(df_ger.iloc[-3]["close"]) - float(df_ger.iloc[-4]["close"])
                    us_move_now    = float(df_us.iloc[-2]["close"])  - float(df_us.iloc[-3]["close"])
                    ctx["ger40_leading_us30"] = (
                        (ger_move_2bars > 0 and us_move_now > 0) or
                        (ger_move_2bars < 0 and us_move_now < 0)
                    )
                else:
                    ctx["ger40_leading_us30"] = False

            # Count how many symbols have same SETUP firing simultaneously
            # (done at runtime in signal loop -- stored as ctx feature below)
        except Exception as e:
            log.warning(f"Cross-symbol correlation error: {e}")

        # ── NEW: Session context features ─────────────────────────────────

        # 14. Session quality -- first 30min of London open vs rest
        try:
            h = now.hour
            m = now.minute
            minutes_into_london = (h - 7) * 60 + m  # London opens 07:00 UTC
            minutes_into_ny     = (h - 13) * 60 + m  # NY opens 13:30 UTC

            ctx["london_first_30min"]     = 0 <= minutes_into_london <= 30
            ctx["london_session"]         = 7 <= h < 13
            ctx["ny_first_30min"]         = 0 <= minutes_into_ny <= 30
            ctx["ny_session"]             = 13 <= h < 19
            ctx["overlap_session"]        = 12 <= h < 14  # London/NY overlap
            ctx["asian_session"]          = 0 <= h < 7
            ctx["dead_zone"]              = 19 <= h or h < 1

            # Monday open -- markets gap, first hour is different
            ctx["monday_open"]            = now.weekday() == 0 and h < 10
            ctx["friday_close"]           = now.weekday() == 4 and h >= 15
            ctx["day_of_week_name"]       = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][now.weekday()]
        except Exception as e:
            log.warning(f"Session context error: {e}")

        # 15. Minutes to next round hour (news often on hour marks)
        try:
            mins_to_hour = 60 - now.minute
            ctx["mins_to_hour"]           = mins_to_hour
            ctx["near_hour_mark"]         = mins_to_hour <= 5 or now.minute <= 5
            # Known high-impact news hours (UTC): 13:30 (US open), 15:00, 08:30
            news_hours = [(8,30),(13,30),(15,0),(19,0)]
            mins_to_news = 999
            for nh, nm in news_hours:
                diff = (nh*60+nm) - (now.hour*60+now.minute)
                if 0 < diff < mins_to_news:
                    mins_to_news = diff
            ctx["mins_to_news_event"]     = mins_to_news if mins_to_news < 999 else 999
            ctx["near_news_event"]        = mins_to_news <= 10
            ctx["very_near_news"]         = mins_to_news <= 3
        except Exception as e:
            log.warning(f"News timing error: {e}")

        # ── NEW: Setup quality + pattern recognition ─────────────────────

        # 16. Pattern formation quality -- exact bar count + compression
        try:
            if df_15 is not None and len(df_15) >= 20:
                atr = ctx.get("atr_14", 1)

                # Exact bar count of Brooks pattern (count bars in the swing)
                swing_bars = 0
                prev_close = float(df_15.iloc[-2]["close"])
                for i in range(len(df_15)-3, max(len(df_15)-20, 0), -1):
                    c = float(df_15.iloc[i]["close"])
                    if float(df_15.iloc[i]["bar_range"]) > atr * 1.2:
                        break  # large bar = pattern boundary
                    swing_bars += 1
                ctx["pattern_bars_exact"]     = swing_bars
                ctx["pattern_bars"]           = swing_bars
                ctx["pattern_fast"]           = swing_bars <= 3
                ctx["pattern_slow"]           = swing_bars >= 8
                ctx["pattern_ideal"]          = 4 <= swing_bars <= 7  # sweet spot

                # Pattern cleanliness
                last_n = df_15.iloc[-max(swing_bars,2)-2:-2]
                if len(last_n) >= 2:
                    closes = last_n["close"].values.astype(float)
                    diffs  = [closes[i+1]-closes[i] for i in range(len(closes)-1)]
                    all_same = all(d > 0 for d in diffs) or all(d < 0 for d in diffs)
                    ctx["pattern_clean"]          = all_same
                    ctx["pattern_messy"]          = not all_same

                # Is setup at swing high/low vs middle of range?
                lookback = df_15.iloc[-20:-2]
                swing_high = float(lookback["high"].max())
                swing_low  = float(lookback["low"].min())
                swing_range = swing_high - swing_low
                entry = signal.entry
                if swing_range > 0:
                    pos_in_swing = (entry - swing_low) / swing_range
                    ctx["at_swing_high"]          = pos_in_swing > 0.8
                    ctx["at_swing_low"]           = pos_in_swing < 0.2
                    ctx["at_swing_extreme"]       = pos_in_swing > 0.8 or pos_in_swing < 0.2
                    ctx["at_swing_middle"]        = 0.35 < pos_in_swing < 0.65
                    ctx["pos_in_swing"]           = round(pos_in_swing, 2)

                # Gap fill setup -- is price closing a gap from previous session?
                try:
                    d_bars = get_candles(signal.symbol, mt5.TIMEFRAME_D1, 3)  # 10s cache -- was direct MT5
                    if d_bars is not None and len(d_bars) >= 2:
                        prev_close_d = float(d_bars.iloc[-2]["close"])
                        today_open   = float(d_bars.iloc[-1]["open"])
                        gap_size     = abs(today_open - prev_close_d)
                        gap_pct      = gap_size / prev_close_d * 100
                        # Price filling gap = moving back toward prev_close
                        filling_up   = prev_close_d > today_open and entry > today_open
                        filling_dn   = prev_close_d < today_open and entry < today_open
                        ctx["gap_size_pts"]           = round(gap_size, 2)
                        ctx["gap_size_pct"]           = round(gap_pct, 3)
                        ctx["has_gap"]                = gap_pct > 0.1
                        ctx["gap_fill_setup"]         = (filling_up or filling_dn) and gap_pct > 0.1
                        ctx["gap_filled_pct"]         = round(
                            abs(entry - today_open) / gap_size, 2) if gap_size > 0 else 0
                except Exception as _e:
                    log.debug(f"Feature block failed: {_e}")

                # Inside bar compression before breakout
                # Inside bar = current bar's range is within previous bar's range
                n_inside = 0
                for i in range(len(df_15)-3, max(len(df_15)-8, 0), -1):
                    b_curr = df_15.iloc[i]
                    b_prev = df_15.iloc[i-1]
                    if (float(b_curr["high"]) <= float(b_prev["high"]) and
                        float(b_curr["low"])  >= float(b_prev["low"])):
                        n_inside += 1
                    else:
                        break
                ctx["inside_bar_count"]       = n_inside
                ctx["has_inside_bars"]        = n_inside >= 1
                ctx["strong_compression"]     = n_inside >= 2  # ii pattern or more
                ctx["extreme_compression"]    = n_inside >= 3  # very coiled

                # Failed breakout before setup
                recent_high = float(df_15.iloc[-8:-4]["high"].max())
                recent_low  = float(df_15.iloc[-8:-4]["low"].min())
                current_price = float(df_15.iloc[-2]["close"])
                ctx["failed_breakout_up"]     = current_price < recent_high - atr * 0.3
                ctx["failed_breakout_dn"]     = current_price > recent_low  + atr * 0.3
                ctx["has_failed_breakout"]    = ctx["failed_breakout_up"] or ctx["failed_breakout_dn"]

                # Entry tightness
                pattern_high  = float(df_15.iloc[-6:-2]["high"].max())
                pattern_low   = float(df_15.iloc[-6:-2]["low"].min())
                pattern_range = pattern_high - pattern_low
                entry_dist    = min(abs(entry - pattern_high), abs(entry - pattern_low))
                ctx["entry_tightness"]        = round(entry_dist / pattern_range, 2) if pattern_range > 0 else 0.5
                ctx["tight_entry"]            = entry_dist < atr * 0.2

        except Exception as e:
            log.warning(f"Pattern quality error: {e}")

        # ── NEW: Self-improvement features ────────────────────────────────

        # 17. ML prediction tracking -- was the model right recently?
        try:
            _all = _cached_trades  # shared log cache
            recent_resolved = [t for t in _all[-50:]
                              if t.get("outcome") in ("win","loss","eod_win","eod_loss")
                              and t.get("context", {}).get("ml_win_prob") is not None]
            if len(recent_resolved) >= 5:
                ml_correct = 0
                ml_conf_sum = 0
                prev_prob = None
                mind_changes = 0
                for t in recent_resolved[-20:]:
                    ml_p = t.get("context", {}).get("ml_win_prob", 0.5)
                    actual_win = t.get("outcome", "") in ("win", "eod_win")
                    predicted_win = ml_p >= 0.5
                    if predicted_win == actual_win:
                        ml_correct += 1
                    ml_conf_sum += abs(ml_p - 0.5) * 2  # 0=uncertain, 1=certain
                    if prev_prob is not None:
                        # Mind change = prediction flipped direction between trades
                        if (ml_p >= 0.5) != (prev_prob >= 0.5):
                            mind_changes += 1
                    prev_prob = ml_p
                n = len(recent_resolved[-20:])
                ctx["ml_recent_accuracy"]     = round(ml_correct / n, 2)
                ctx["ml_avg_confidence"]      = round(ml_conf_sum / n, 2)
                ctx["ml_mind_changes"]        = mind_changes
                ctx["ml_indecisive"]          = mind_changes > n * 0.4

                # Confidence trend -- is model getting more or less confident?
                first_half_conf = sum(abs(t.get("context",{}).get("ml_win_prob",0.5)-0.5)*2
                                     for t in recent_resolved[-20:-10]) / 10 if len(recent_resolved) >= 20 else 0
                second_half_conf = sum(abs(t.get("context",{}).get("ml_win_prob",0.5)-0.5)*2
                                      for t in recent_resolved[-10:]) / 10 if len(recent_resolved) >= 10 else 0
                ctx["ml_confidence_rising"]   = second_half_conf > first_half_conf + 0.05
                ctx["ml_confidence_falling"]  = second_half_conf < first_half_conf - 0.05
        except Exception as e:
            log.warning(f"ML self-improvement context error: {e}")

        # 18. Setup drift detection -- win rate dropping in last 7 days?
        try:
            _all = _cached_trades  # shared log cache
            setup_key_ctx = f"{signal.strategy}|{signal.setup_name}"
            cutoff_7d  = (now - timedelta(days=7)).strftime("%Y-%m-%d")   # now is UTC
            cutoff_14d = (now - timedelta(days=14)).strftime("%Y-%m-%d")  # now is UTC

            recent_7d  = [t for t in _all
                         if t.get("setup_name") == signal.setup_name
                         and t.get("timestamp","") >= cutoff_7d
                         and t.get("outcome") in ("win","loss","eod_win","eod_loss")]
            prev_7d    = [t for t in _all
                         if t.get("setup_name") == signal.setup_name
                         and cutoff_14d <= t.get("timestamp","") < cutoff_7d
                         and t.get("outcome") in ("win","loss","eod_win","eod_loss")]

            if len(recent_7d) >= 5:
                _wr7d_w = sum(1 for t in recent_7d if t["outcome"] in ("win","eod_win"))
                _wr7d_d = sum(1 for t in recent_7d if t["outcome"] in ("win","eod_win","loss","eod_loss"))
                wr_recent = _wr7d_w / max(_wr7d_d, 1) if _wr7d_d > 0 else 0.5
                ctx["setup_wr_7d"]            = round(wr_recent * 100, 1)
                ctx["setup_n_7d"]             = len(recent_7d)
                if len(prev_7d) >= 5:
                    _wr_prev_w = sum(1 for t in prev_7d if t["outcome"] in ("win","eod_win"))
                    _wr_prev_d = sum(1 for t in prev_7d if t["outcome"] in ("win","eod_win","loss","eod_loss"))
                    wr_prev = _wr_prev_w / max(_wr_prev_d, 1) if _wr_prev_d > 0 else 0.5
                    drift   = wr_prev - wr_recent
                    ctx["setup_drift"]            = round(drift * 100, 1)
                    ctx["setup_drifting_down"]    = drift > 0.10  # >10% drop
                    ctx["setup_improving"]        = drift < -0.10  # >10% gain
                    if drift > 0.10:
                        # Throttle: log once per hour per setup to avoid spam
                        _dk = f"_drift_{signal.setup_name}"
                        _dh = datetime.now(timezone.utc).hour  # UTC for consistency
                        if not hasattr(capture_market_context, _dk) or                                getattr(capture_market_context, _dk) != _dh:
                            log.warning(f"DRIFT ALERT: {signal.setup_name} win rate dropped "
                                       f"{drift*100:.1f}% in last 7 days "
                                       f"({wr_prev*100:.1f}% -> {wr_recent*100:.1f}%)")
                            setattr(capture_market_context, _dk, _dh)
        except Exception as e:
            log.warning(f"Setup drift error: {e}")

        # ── NEW: Risk management intelligence ─────────────────────────────

        # 19. Drawdown velocity -- how fast are we losing vs historical average?
        try:
            _all = _cached_trades  # shared log cache
            today_str = now.strftime("%Y-%m-%d")  # now is UTC
            today_trades = [t for t in _all
                           if t.get("timestamp","").startswith(today_str)
                           and t.get("outcome") in ("win","loss","eod_win","eod_loss")]
            if today_trades:
                today_losses = sum(1 for t in today_trades if t["outcome"] in ("loss","eod_loss"))
                today_n      = len(today_trades)
                today_lr     = today_losses / today_n  # today's loss rate

                # Historical daily loss rate (last 30 days)
                hist = [t for t in _all
                       if t.get("timestamp","") < today_str
                       and t.get("outcome") in ("win","loss","eod_win","eod_loss")]
                if len(hist) >= 20:
                    hist_lr = sum(1 for t in hist if t["outcome"] in ("loss","eod_loss")) / len(hist)
                    ctx["drawdown_velocity"]      = round(today_lr - hist_lr, 3)
                    ctx["losing_faster_than_avg"] = today_lr > hist_lr + 0.15
                    ctx["losing_slower_than_avg"] = today_lr < hist_lr - 0.10
                    ctx["today_loss_rate"]        = round(today_lr, 2)
                    ctx["hist_loss_rate"]         = round(hist_lr, 2)
                    if today_lr > hist_lr + 0.20:
                        log.warning(f"DRAWDOWN VELOCITY: losing {today_lr*100:.0f}% today "
                                   f"vs {hist_lr*100:.0f}% historical -- elevated risk")
        except Exception as e:
            log.warning(f"Drawdown velocity error: {e}")

        # 20. Per-symbol P&L tracking
        try:
            _all = _cached_trades  # shared log cache
            sym = signal.symbol
            sym_trades = [t for t in _all[-100:]
                         if t.get("symbol") == sym
                         and t.get("outcome") in ("win","loss","eod_win","eod_loss")]
            if len(sym_trades) >= 5:
                _sym_w = sum(1 for t in sym_trades if t["outcome"] in ("win","eod_win"))
                sym_wr = _sym_w / len(sym_trades)
                ctx["symbol_win_rate_100"]    = round(sym_wr * 100, 1)
                ctx["symbol_is_profitable"]   = sym_wr >= 0.55
                ctx["symbol_is_losing"]       = sym_wr < 0.45

                # Per-symbol streak
                streak = 0
                for t in reversed(sym_trades):
                    if t["outcome"] == sym_trades[-1]["outcome"]:
                        streak += 1
                    else:
                        break
                ctx["symbol_streak"]          = streak
                ctx["symbol_on_hot_streak"]   = (streak >= 3 and
                                                 sym_trades[-1]["outcome"] in ("win","eod_win"))
                ctx["symbol_on_cold_streak"]  = (streak >= 3 and
                                                 sym_trades[-1]["outcome"] in ("loss","eod_loss"))
        except Exception as e:
            log.warning(f"Per-symbol P&L error: {e}")

        # 21. Correlation risk -- GER40 and US30 same direction = double exposure
        try:
            positions = mt5.positions_get() or []
            ger_longs  = sum(1 for p in positions if "GER40" in p.symbol
                            and p.type == mt5.ORDER_TYPE_BUY)
            ger_shorts = sum(1 for p in positions if "GER40" in p.symbol
                            and p.type == mt5.ORDER_TYPE_SELL)
            us30_longs  = sum(1 for p in positions if "US30" in p.symbol
                             and p.type == mt5.ORDER_TYPE_BUY)
            us30_shorts = sum(1 for p in positions if "US30" in p.symbol
                             and p.type == mt5.ORDER_TYPE_SELL)
            us100_longs  = sum(1 for p in positions if "USTEC" in p.symbol
                              and p.type == mt5.ORDER_TYPE_BUY)
            us100_shorts = sum(1 for p in positions if "USTEC" in p.symbol
                               and p.type == mt5.ORDER_TYPE_SELL)

            # Correlated long exposure = GER40 long + US30 long + US100 long
            corr_long  = ger_longs  + us30_longs  + us100_longs
            corr_short = ger_shorts + us30_shorts + us100_shorts
            ctx["correlated_long_exposure"]  = corr_long
            ctx["correlated_short_exposure"] = corr_short
            ctx["high_correlation_risk"]     = corr_long >= 2 or corr_short >= 2
            ctx["max_correlation_risk"]      = corr_long >= 3 or corr_short >= 3
            # Net directional bias across all symbols
            ctx["net_directional_bias"]      = corr_long - corr_short

            if corr_long >= 2 or corr_short >= 2:
                direction = "LONG" if corr_long > corr_short else "SHORT"
                log.info(f"  Correlation risk: {corr_long}L/{corr_short}S "
                        f"-- {direction} exposure elevated")
        except Exception as e:
            log.warning(f"Correlation risk error: {e}")

        # 22. Time-of-day equity curve -- are we consistently losing at this hour?
        try:
            _all = _cached_trades  # shared log cache
            this_hour = now.hour
            hour_trades = [t for t in _all
                          if t.get("context", {}).get("hour_server") == this_hour
                          and t.get("outcome") in ("win","loss","eod_win","eod_loss")]
            if len(hour_trades) >= 10:
                _hw = sum(1 for t in hour_trades if t["outcome"] in ("win","eod_win"))
                hour_wr = _hw / len(hour_trades)
                ctx["this_hour_win_rate"]     = round(hour_wr * 100, 1)
                ctx["this_hour_count"]        = len(hour_trades)
                ctx["this_hour_profitable"]   = hour_wr >= 0.55
                ctx["this_hour_losing"]       = hour_wr < 0.40
                if hour_wr < 0.40:
                    log.info(f"  Time-of-day: hour {this_hour:02d}:00 UTC "
                            f"historically {hour_wr*100:.0f}% win rate "
                            f"({len(hour_trades)} trades)")
        except Exception as e:
            log.warning(f"Time-of-day equity error: {e}")

        # ── SIMONS FORMULAS ───────────────────────────────────────────────
        # These are the statistical tools Renaissance Technologies used.
        # Each one becomes a feature for the ML to learn from.

        # ── Formula 1: Serial Autocorrelation ─────────────────────────────
        # Measures if recent price moves predict next move.
        # AC > 0.1 = trending, AC < -0.1 = mean reverting, near 0 = random.
        # Simons measured this across multiple lag periods simultaneously.
        try:
            if df_15 is not None and len(df_15) >= 30:
                closes = df_15["close"].values.astype(float)
                returns = [closes[i]/closes[i-1]-1 for i in range(1,len(closes))]
                n = len(returns)

                # Lag-1 autocorrelation (next bar predicted by this bar)
                if n >= 10:
                    mean_r = sum(returns)/n
                    num = sum((returns[i]-mean_r)*(returns[i-1]-mean_r)
                              for i in range(1,n))
                    den = sum((r-mean_r)**2 for r in returns)
                    ac1 = num/den if den > 0 else 0
                    ctx["autocorr_lag1"]      = round(ac1, 4)
                    ctx["ac_trending"]        = ac1 > 0.08   # persistent moves
                    ctx["ac_reverting"]       = ac1 < -0.08  # mean reverting
                    ctx["ac_random"]          = abs(ac1) < 0.04  # no signal

                # Lag-5 autocorrelation (5-bar momentum persistence)
                if n >= 20:
                    # Recompute mean_r/den safely in case lag1 block was skipped
                    _mean_r = sum(returns)/n
                    _den    = sum((r-_mean_r)**2 for r in returns)
                    num5 = sum((returns[i]-_mean_r)*(returns[i-5]-_mean_r)
                               for i in range(5,n))
                    ac5  = num5/_den if _den > 0 else 0
                    ctx["autocorr_lag5"]      = round(ac5, 4)
                    ctx["ac5_trending"]       = ac5 > 0.05

                # Direction consistency -- what % of last 10 bars moved same way
                last10 = returns[-10:]
                ups    = sum(1 for r in last10 if r > 0)
                ctx["direction_consistency"] = round(abs(ups/10 - 0.5) * 2, 2)
                # 0 = perfectly alternating, 1 = all same direction
                ctx["strong_trend_signal"]   = ctx["direction_consistency"] > 0.6
                ctx["stat_available"]         = 1   # statistical features computed successfully

        except Exception as e:
            log.warning(f"Autocorrelation error: {e}")

        # ── Formula 2: Hurst Exponent ──────────────────────────────────────
        # H > 0.5 = trending (persistent), H < 0.5 = mean reverting,
        # H = 0.5 = random walk (no edge). Simons used this to classify
        # whether ANY signal is worth trading right now.
        try:
            if df_15 is not None and len(df_15) >= 40:
                prices = df_15["close"].values.astype(float)[-40:]
                # R/S analysis -- simplified but accurate enough
                lags   = [4, 8, 16]
                rs_vals = []
                for lag in lags:
                    chunks = [prices[i:i+lag] for i in range(0,len(prices)-lag,lag)]
                    rs_chunk = []
                    for chunk in chunks:
                        mean_c = sum(chunk)/len(chunk)
                        devs   = [c - mean_c for c in chunk]
                        cum_devs = []
                        s = 0
                        for d in devs:
                            s += d
                            cum_devs.append(s)
                        R = max(cum_devs) - min(cum_devs)
                        std = (sum((c-mean_c)**2 for c in chunk)/len(chunk))**0.5
                        if std > 0:
                            rs_chunk.append(R/std)
                    if rs_chunk:
                        rs_vals.append((lag, sum(rs_chunk)/len(rs_chunk)))

                if len(rs_vals) >= 2:
                    import math
                    log_lags = [math.log(r[0]) for r in rs_vals]
                    log_rs   = [math.log(r[1]) for r in rs_vals if r[1] > 0]
                    if len(log_rs) >= 2:
                        # Linear regression slope = Hurst exponent
                        n_h = len(log_rs)
                        mean_x = sum(log_lags[:n_h])/n_h
                        mean_y = sum(log_rs)/n_h
                        num_h  = sum((log_lags[i]-mean_x)*(log_rs[i]-mean_y) for i in range(n_h))
                        den_h  = sum((log_lags[i]-mean_x)**2 for i in range(n_h))
                        hurst  = num_h/den_h if den_h > 0 else 0.5
                        ctx["hurst_exponent"]     = round(hurst, 3)
                        ctx["hurst_trending"]     = hurst > 0.55
                        ctx["hurst_reverting"]    = hurst < 0.45
                        ctx["hurst_random"]       = 0.45 <= hurst <= 0.55
                        # Log it when strongly trending
                        # v175: throttle -- was logging every iteration. Cache by
                        # (symbol, hurst_bucket) so only state changes log.
                        if hurst > 0.60 or hurst < 0.40:
                            _h_bucket = round(hurst * 20) / 20  # 0.05 buckets
                            _h_label = "TRENDING" if hurst > 0.60 else "REVERTING"
                            _h_key = (getattr(signal, "symbol", "?"), _h_label, _h_bucket)
                            _h_seen = getattr(capture_market_context, "_hurst_seen", {})
                            _h_now_ts = datetime.now(timezone.utc).timestamp()
                            _h_last = _h_seen.get(_h_key, 0)
                            if _h_now_ts - _h_last > 300:  # 5 min minimum gap per state
                                if hurst > 0.60:
                                    log.info(f"  Hurst={hurst:.2f} TRENDING -- good signal conditions")
                                else:
                                    log.info(f"  Hurst={hurst:.2f} REVERTING -- range conditions")
                                _h_seen[_h_key] = _h_now_ts
                                # Bound the cache
                                if len(_h_seen) > 50:
                                    _h_seen = {k: v for k, v in _h_seen.items()
                                               if _h_now_ts - v < 600}
                                setattr(capture_market_context, "_hurst_seen", _h_seen)
        except Exception as e:
            log.warning(f"Hurst exponent error: {e}")

        # ── Formula 3: Shannon Entropy ─────────────────────────────────────
        # Measures randomness in price direction.
        # Low entropy = directional, predictable = good time to trade.
        # High entropy = random, chaotic = avoid or reduce size.
        # Simons used entropy to filter out "uninformative" price periods.
        try:
            if df_15 is not None and len(df_15) >= 20:
                import math
                closes  = df_15["close"].values.astype(float)[-20:]
                # Discretise returns into up/flat/down
                returns = [closes[i]/closes[i-1]-1 for i in range(1,len(closes))]
                ups    = sum(1 for r in returns if r > 0.0002)
                downs  = sum(1 for r in returns if r < -0.0002)
                flats  = len(returns) - ups - downs
                n_e    = len(returns)
                probs  = [x/n_e for x in [ups, downs, flats] if x > 0]
                entropy = -sum(p * math.log2(p) for p in probs)
                # Max entropy = log2(3) ≈ 1.585 (perfectly random)
                # Min entropy = 0 (all bars same direction)
                norm_entropy = entropy / math.log2(3)
                ctx["price_entropy"]          = round(norm_entropy, 3)
                ctx["low_entropy"]            = norm_entropy < 0.7   # directional
                ctx["high_entropy"]           = norm_entropy > 0.9   # chaotic/random
                ctx["entropy_tradeable"]      = norm_entropy < 0.75
        except Exception as e:
            log.warning(f"Shannon entropy error: {e}")

        # ── Formula 4: Volatility Clustering (GARCH-lite) ─────────────────
        # High vol follows high vol. Low vol follows low vol.
        # Simons used this to size positions -- don't bet big in vol spikes.
        # Simple version: compare recent vol to longer-term vol.
        try:
            if df_15 is not None and len(df_15) >= 30:
                ranges    = df_15["bar_range"].values.astype(float)
                vol_5     = float(ranges[-6:-1].mean())   # last 5 bars
                vol_20    = float(ranges[-21:-1].mean())  # last 20 bars
                vol_ratio = vol_5 / vol_20 if vol_20 > 0 else 1.0
                ctx["vol_clustering_ratio"]   = round(vol_ratio, 3)
                ctx["vol_expanding"]          = vol_ratio > 1.3   # vol spike -- caution
                ctx["vol_contracting"]        = vol_ratio < 0.7   # vol squeeze -- breakout coming
                ctx["vol_stable"]             = 0.8 <= vol_ratio <= 1.2
                # Vol acceleration -- is vol increasing or decreasing?
                vol_3   = float(ranges[-4:-1].mean())
                vol_acc = vol_3 / vol_5 if vol_5 > 0 else 1.0
                ctx["vol_accelerating"]       = vol_acc > 1.2   # vol increasing fast
                ctx["vol_decelerating"]       = vol_acc < 0.8   # vol calming down
        except Exception as e:
            log.warning(f"Vol clustering error: {e}")

        # ── Formula 5: Kalman Filter (trend estimate) ─────────────────────
        # Estimates the "true" underlying trend, removing noise.
        # More adaptive than EMA -- speeds up in trends, slows in ranges.
        # Simons used this as a cleaner trend signal than moving averages.
        try:
            if df_15 is not None and len(df_15) >= 20:
                prices  = df_15["close"].values.astype(float)
                # Simplified 1D Kalman filter
                Q = 0.01   # process noise -- how fast trend changes
                R = 0.1    # measurement noise -- how noisy price is
                x = prices[0]  # initial state estimate
                P = 1.0        # initial uncertainty
                kalman_estimates = []
                for price in prices:
                    # Predict
                    P_pred = P + Q
                    # Update
                    K = P_pred / (P_pred + R)   # Kalman gain
                    x = x + K * (price - x)
                    P = (1 - K) * P_pred
                    kalman_estimates.append(x)

                kalman_now  = kalman_estimates[-1]
                kalman_prev = kalman_estimates[-6]
                kalman_slope = (kalman_now - kalman_prev) / kalman_prev * 100
                current_price = float(prices[-2])

                ctx["kalman_trend"]           = round(kalman_now, 2)
                ctx["kalman_available"]       = 1   # Kalman computed successfully
                ctx["kalman_slope_pct"]       = round(kalman_slope, 4)
                ctx["kalman_bull"]            = kalman_slope > 0.02   # uptrend
                ctx["kalman_bear"]            = kalman_slope < -0.02  # downtrend
                ctx["kalman_flat"]            = abs(kalman_slope) < 0.01
                ctx["price_above_kalman"]     = current_price > kalman_now
                ctx["price_below_kalman"]     = current_price < kalman_now
                # Distance from Kalman -- how far price has strayed from trend
                dist_from_kalman = abs(current_price - kalman_now) / kalman_now * 100
                ctx["dist_from_kalman_pct"]   = round(dist_from_kalman, 3)
                ctx["extended_from_kalman"]   = dist_from_kalman > 0.5  # overextended
                log.debug(f"Kalman: slope={kalman_slope:.4f} bull={kalman_slope > 0.02} dist={dist_from_kalman:.3f}%")
        except Exception as e:
            log.warning(f"Kalman filter error: {e}")

        # ── Formula 6: ARIMA-style momentum prediction ────────────────────
        # Weighted sum of past returns predicts next return.
        # Simons used this as a short-term price predictor.
        # We use a simple AR(3) -- last 3 returns predict next one.
        try:
            if df_15 is not None and len(df_15) >= 20:
                closes  = df_15["close"].values.astype(float)
                returns = [closes[i]/closes[i-1]-1 for i in range(1,len(closes))]
                if len(returns) >= 10:
                    # AR(3): predict next return from last 3
                    # Weights learned from last 20 observations
                    r = returns[-20:]
                    n_ar = len(r)
                    # Simple OLS for AR(3)
                    X = [[r[i-1], r[i-2], r[i-3]] for i in range(3, n_ar)]
                    y = [r[i] for i in range(3, n_ar)]
                    if len(X) >= 5:
                        # Solve via normal equations (no scipy needed)
                        xt = [[X[j][i] for j in range(len(X))] for i in range(3)]
                        xtx = [[sum(xt[a][k]*xt[b][k] for k in range(len(y)))
                                for b in range(3)] for a in range(3)]
                        xty = [sum(xt[a][k]*y[k] for k in range(len(y))) for a in range(3)]
                        # Simple 3x3 matrix inversion via Cramer's rule
                        a,b,c = xtx[0]; d,e,f = xtx[1]; g,h,i_ = xtx[2]
                        det = a*(e*i_-f*h) - b*(d*i_-f*g) + c*(d*h-e*g)
                        if abs(det) > 1e-12:
                            inv = [[(e*i_-f*h)/det, -(b*i_-c*h)/det, (b*f-c*e)/det],
                                   [-(d*i_-f*g)/det, (a*i_-c*g)/det, -(a*f-c*d)/det],
                                   [(d*h-e*g)/det, -(a*h-b*g)/det, (a*e-b*d)/det]]
                            w = [sum(inv[a][b]*xty[b] for b in range(3)) for a in range(3)]
                            ar_pred = w[0]*returns[-1] + w[1]*returns[-2] + w[2]*returns[-3]
                            ctx["ar3_available"]      = 1   # AR3 computed successfully
                            ctx["ar3_prediction"]     = round(ar_pred * 10000, 2)  # in bps
                            ctx["ar3_bullish"]        = ar_pred > 0.0001
                            ctx["ar3_bearish"]        = ar_pred < -0.0001
                            ctx["ar3_neutral"]        = abs(ar_pred) <= 0.0001
                            log.debug(f"AR3: pred={ar_pred*10000:.2f}bps bull={ar_pred > 0.0001}")
        except Exception as e:
            log.warning(f"AR3 prediction error: {e}")

        # ── Formula 7: Fractal Dimension ──────────────────────────────────
        # Measures how "jagged" the price path is.
        # Smooth path (dim near 1.0) = trending cleanly.
        # Jagged path (dim near 2.0) = random/choppy = avoid.
        # Related to Hurst: FD = 2 - H
        try:
            if df_15 is not None and len(df_15) >= 20:
                highs  = df_15["high"].values.astype(float)[-20:]
                lows   = df_15["low"].values.astype(float)[-20:]
                closes = df_15["close"].values.astype(float)[-20:]
                n_fd   = len(closes)
                # Path length = sum of |price changes|
                path_len = sum(abs(closes[i]-closes[i-1]) for i in range(1,n_fd))
                # Euclidean distance = straight line from start to end
                euclid   = abs(closes[-1] - closes[0])
                if euclid > 0 and path_len > 0:
                    import math
                    fd = 1 + math.log(path_len/euclid) / math.log(n_fd)
                    fd = max(1.0, min(2.0, fd))  # clamp to [1,2]
                    ctx["fractal_dimension"]      = round(fd, 3)
                    ctx["fd_trending"]            = fd < 1.3   # smooth trend
                    ctx["fd_choppy"]              = fd > 1.6   # jagged/random
                    ctx["fd_neutral"]             = 1.3 <= fd <= 1.6
        except Exception as e:
            log.warning(f"Fractal dimension error: {e}")

        # ── Formula 8: Cross-symbol divergence (pairs signal) ─────────────
        # When GER40 and US30 diverge from their normal relationship,
        # the divergence tends to close. Simons made billions from this.
        # Simple version: z-score of spread between the two symbols.
        try:
            df_ger = get_candles("GER40.cash", TF_15M, 30)
            df_us  = get_candles("US30",  TF_15M, 30)
            if df_ger is not None and df_us is not None and len(df_ger) >= 20 and len(df_us) >= 20:
                # Normalise both to their starting price
                ger_norm = [float(df_ger.iloc[i]["close"]) / float(df_ger.iloc[0]["close"])
                            for i in range(len(df_ger))]
                us_norm  = [float(df_us.iloc[i]["close"])  / float(df_us.iloc[0]["close"])
                            for i in range(len(df_us))]
                n_pairs  = min(len(ger_norm), len(us_norm))
                spread   = [ger_norm[i] - us_norm[i] for i in range(n_pairs)]
                mean_sp  = sum(spread) / n_pairs
                std_sp   = (sum((s-mean_sp)**2 for s in spread)/n_pairs)**0.5
                if std_sp > 0:
                    zscore = (spread[-1] - mean_sp) / std_sp
                    ctx["ger_us_spread_zscore"]   = round(zscore, 3)
                    ctx["ger_leading_up"]         = zscore > 1.5   # GER above US -- US may follow
                    ctx["ger_leading_down"]       = zscore < -1.5  # GER below US -- US may follow
                    ctx["pairs_converging"]       = abs(zscore) < 0.5  # normal relationship
                    ctx["pairs_diverged"]         = abs(zscore) > 2.0  # unusual divergence
        except Exception as e:
            log.warning(f"Pairs divergence error: {e}")

        # ── VWAP distance (institutional gravity) ────────────────────────────
        # Institutions anchor to VWAP. Price far above = selling pressure.
        # Price far below = buying pressure. Critical for setup quality.
        try:
            if df_15 is not None and len(df_15) >= 20:
                closes  = df_15["close"].values.astype(float)
                # MT5 returns tick_volume -- try both column names
                if "tick_volume" in df_15.columns:
                    volumes = df_15["tick_volume"].values.astype(float)
                elif "volume" in df_15.columns:
                    volumes = df_15["volume"].values.astype(float)
                else:
                    volumes = np.ones(len(df_15))  # fallback: equal weight
                highs   = df_15["high"].values.astype(float)
                lows    = df_15["low"].values.astype(float)
                # VWAP = sum(typical_price * volume) / sum(volume)
                typical = (highs + lows + closes) / 3
                total_vol = float(sum(volumes))
                if total_vol > 0:
                    vwap = float(sum(typical[i]*volumes[i] for i in range(len(typical)))
                                / total_vol)
                else:
                    # CFD feeds often have zero volume -- use simple average
                    vwap = float(sum(typical) / len(typical))
                entry   = float(signal.entry)
                vwap_dist_pts  = entry - vwap
                vwap_dist_pct  = (entry - vwap) / vwap * 100 if vwap > 0 else 0
                ctx["vwap"]                 = round(vwap, 2)
                ctx["vwap_dist_pct"]        = round(vwap_dist_pct, 3)
                ctx["vwap_dist_pts"]        = round(vwap_dist_pts, 2)
                ctx["above_vwap"]           = entry > vwap
                ctx["below_vwap"]           = entry < vwap
                ctx["far_above_vwap"]       = vwap_dist_pct > 0.5   # sell pressure
                ctx["far_below_vwap"]       = vwap_dist_pct < -0.5  # buy pressure
                ctx["near_vwap"]            = abs(vwap_dist_pct) < 0.1  # no edge
                # Direction alignment with VWAP
                ctx["vwap_aligned_long"]    = entry < vwap and signal.direction == "long"
                ctx["vwap_aligned_short"]   = entry > vwap and signal.direction == "short"
                ctx["vwap_against_long"]    = entry > vwap and signal.direction == "long"
                ctx["vwap_against_short"]   = entry < vwap and signal.direction == "short"
        except Exception as e:
            log.warning(f"VWAP error: {e}")

        # ── Kurtosis + Skewness (Mandelbrot fat tails) ────────────────────
        # Kurtosis: how fat are the tails right now?
        # High kurtosis = rare large moves more likely = reduce size
        # Skewness: is distribution biased up or down?
        # Negative skew = more large drops than rallies
        try:
            if df_15 is not None and len(df_15) >= 20:
                closes  = df_15["close"].values.astype(float)[-20:]
                returns = [closes[i]/closes[i-1]-1 for i in range(1, len(closes))]
                n       = len(returns)
                mean_r  = sum(returns) / n
                var_r   = sum((r-mean_r)**2 for r in returns) / n
                std_r   = var_r ** 0.5

                if std_r > 0:
                    # Skewness: third standardised moment
                    skew = sum((r-mean_r)**3 for r in returns) / (n * std_r**3)
                    # Excess kurtosis: fourth standardised moment - 3
                    kurt = sum((r-mean_r)**4 for r in returns) / (n * std_r**4) - 3

                    ctx["return_skewness"]      = round(skew, 3)
                    ctx["return_kurtosis"]      = round(kurt, 3)
                    ctx["negative_skew"]        = skew < -0.5  # more large drops
                    ctx["positive_skew"]        = skew > 0.5   # more large rallies
                    ctx["fat_tails"]            = kurt > 1.0   # dangerous conditions
                    ctx["thin_tails"]           = kurt < -0.5  # calm, predictable
                    ctx["tail_risk_high"]       = kurt > 2.0 and skew < 0  # worst combo
                    # Skew alignment with direction
                    ctx["skew_favours_long"]    = skew > 0.3 and signal.direction == "long"
                    ctx["skew_favours_short"]   = skew < -0.3 and signal.direction == "short"
        except Exception as e:
            log.warning(f"Kurtosis/skewness error: {e}")

        # ── MANDELBROT: Scaling law -- optimal timeframe measurement ──────────
        try:
            scaling_scores = {}
            for tf_name, tf_obj in [("5m", TF_5M), ("15m", TF_15M)]:
                df_tf = get_candles(signal.symbol, tf_obj, 35)
                if df_tf is None or len(df_tf) < 20:
                    continue
                closes = df_tf["close"].values.astype(float)[-20:]
                returns = [closes[i]/closes[i-1]-1 for i in range(1, len(closes))]
                if len(returns) < 5:
                    continue
                mean_r = sum(returns)/len(returns)
                std_r  = (sum((r-mean_r)**2 for r in returns)/len(returns))**0.5
                snr    = abs(mean_r) / std_r if std_r > 0 else 0
                scaling_scores[tf_name] = round(snr, 4)
            if scaling_scores:
                best_tf  = max(scaling_scores, key=scaling_scores.get)
                best_snr = scaling_scores[best_tf]
                ctx["scaling_snr_5m"]      = scaling_scores.get("5m", 0)
                ctx["scaling_snr_15m"]     = scaling_scores.get("15m", 0)
                ctx["scaling_best_tf"]     = best_tf
                ctx["scaling_signal_rich"] = best_snr > 0.15
                ctx["scaling_noisy"]       = best_snr < 0.05
                our_tf = "5m" if "5m" in signal.strategy else "15m"
                ctx["on_best_timeframe"]   = best_tf == our_tf
        except Exception as e:
            log.warning(f"Mandelbrot scaling error: {e}")

        # ── Formula 9: Momentum persistence score ─────────────────────────
        # Combines multiple momentum signals into one score.
        # Simons found that when multiple momentum signals agree,
        # the signal is far more reliable than any single one.
        try:
            if df_15 is not None and len(df_15) >= 20:
                closes = df_15["close"].values.astype(float)
                score  = 0
                # 5-bar momentum
                if closes[-2] > closes[-7]:   score += 1
                # 10-bar momentum
                if closes[-2] > closes[-12]:  score += 1
                # 20-bar momentum
                if len(closes) >= 22 and closes[-2] > closes[-22]: score += 1
                # Price above Kalman (if available)
                if ctx.get("price_above_kalman"): score += 1
                # Autocorrelation trending (if available)
                if ctx.get("ac_trending"):        score += 1

                ctx["momentum_confluence"]    = score  # 0-5
                ctx["strong_momentum"]        = score >= 4
                ctx["weak_momentum"]          = score <= 1
                ctx["momentum_agrees_long"]   = score >= 3 and signal.direction == "long"
                ctx["momentum_agrees_short"]  = score <= 2 and signal.direction == "short"
                ctx["momentum_disagrees"]     = (score >= 4 and signal.direction == "short") or                                                 (score <= 1 and signal.direction == "long")
        except Exception as e:
            log.warning(f"Momentum confluence error: {e}")

    except Exception as e:
        log.warning(f"Context capture error: {e}")

    # ── BLACK-SCHOLES: Implied edge calculation ───────────────────────────
    # Theoretical probability price reaches TP before SL based on
    # current volatility and distance. Compare to ML estimate.
    # When both agree = high conviction. When they disagree = caution.
    try:
        import math
        entry    = float(signal.entry)
        sl       = float(signal.stop_loss)
        tp       = float(signal.take_profit)
        sl_dist  = abs(entry - sl)
        tp_dist  = abs(entry - tp)
        atr      = ctx.get("atr_14", 0) or 0

        if sl_dist > 0 and tp_dist > 0 and atr > 0:
            # Geometric Brownian motion: P(TP before SL)
            # Using symmetric random walk approximation
            # P = sl_dist / (sl_dist + tp_dist) for zero drift
            # Adjust for drift using recent momentum
            drift    = ctx.get("ema_slope", 0) or 0
            rr_ratio = tp_dist / sl_dist

            # Zero-drift probability
            p_zero = sl_dist / (sl_dist + tp_dist)

            # Drift adjustment -- positive drift favours longs
            drift_adj = 0.0
            if atr > 0:
                drift_norm = drift / (atr / entry * 100) if entry > 0 else 0
                drift_adj  = drift_norm * 0.1  # conservative adjustment
                if signal.direction == "short":
                    drift_adj = -drift_adj

            p_implied = max(0.1, min(0.9, p_zero + drift_adj))
            ctx["implied_edge"]        = round(p_implied, 3)
            ctx["implied_rr"]          = round(rr_ratio, 2)

            # Compare to ML prediction if available
            ml_prob = ctx.get("ml_win_prob", 0.5) or 0.5
            edge_gap = ml_prob - p_implied
            ctx["ml_vs_implied_gap"]   = round(edge_gap, 3)
            ctx["ml_overconfident"]    = edge_gap > 0.15   # ML much higher than math
            ctx["ml_underconfident"]   = edge_gap < -0.15  # ML much lower than math
            ctx["high_conviction"]     = abs(edge_gap) < 0.08 and ml_prob > 0.6
            # When ML and implied edge agree AND both say >60% -- max conviction
            ctx["dual_confirmation"]   = (p_implied > 0.55 and ml_prob > 0.60
                                          and abs(edge_gap) < 0.10)
    except Exception as e:
        log.warning(f"Implied edge error: {e}")

    # ── KAHNEMAN: Counterfactual BE tracking ──────────────────────────
    # For every breakeven trade, we track what the MAX profit was
    # before it reversed. This tells us if BE moves help or hurt
    # per setup. The ML learns from this data.
    try:
        ctx["be_candidate"]     = False
        ctx["be_avg_mfe"]       = 0.0
        ctx["be_count"]         = 0
        ctx["be_was_protective"]= False
        ctx["be_optimal"]       = True   # assume BE is good until proven otherwise
        _all = _cached_trades  # shared log cache
        setup_key = f"{signal.strategy}|{signal.setup_name}"
        be_trades = [t for t in _all
                    if "breakeven" in str(t.get("outcome",""))
                    and f"{t.get('strategy')}|{t.get('setup_name')}" == setup_key]
        full_trades = [t for t in _all
                      if t.get("outcome") in ("win","loss","eod_win","eod_loss")
                      and f"{t.get('strategy')}|{t.get('setup_name')}" == setup_key]
        if len(be_trades) >= 5:
            mfe_vals   = [t.get("context",{}).get("mfe_pips", 0) or 0
                         for t in be_trades]
            avg_mfe_be = sum(mfe_vals)/len(mfe_vals) if mfe_vals else 0
            ctx["be_avg_mfe"]       = round(avg_mfe_be, 1)
            ctx["be_count"]         = len(be_trades)
            ctx["be_was_protective"]= avg_mfe_be > 8
            # KEY QUESTION: is the BE move hurting or helping?
            # Compare: what % of be_trades had MFE > their original TP distance?
            # If MFE often exceeded original TP = trade would have WON without BE move
            # = BE move is COSTING wins not protecting them
            if full_trades:
                avg_tp_dist = 0
                tp_dists = []
                for t in full_trades[-20:]:
                    c = t.get("context", {})
                    entry = c.get("entry_price", 0) or 0
                    tp    = c.get("tp_price", 0) or 0
                    if entry > 0 and tp > 0:
                        tp_dists.append(abs(tp - entry))
                if tp_dists:
                    avg_tp_dist = sum(tp_dists)/len(tp_dists)
                # BE trades where MFE exceeded original TP = would have been wins
                would_have_won = sum(1 for t in be_trades
                                   if (t.get("context",{}).get("mfe_pips",0) or 0)
                                   > avg_tp_dist * 0.8)
                be_win_rate_without_move = would_have_won / len(be_trades)
                ctx["be_would_win_without_move"] = round(be_win_rate_without_move, 2)
                # If >40% of BE trades would have won without the BE move
                # = BE move is suboptimal for this setup
                ctx["be_optimal"] = be_win_rate_without_move < 0.4
                ctx["be_hurting"] = be_win_rate_without_move > 0.5
                if ctx["be_hurting"]:
                    log.info(f"  KAHNEMAN: {setup_key} BE move may be hurting -- "
                            f"{be_win_rate_without_move:.0%} of BEs would have won "
                            f"without BE move")
    except Exception as e:
        log.warning(f"Kahneman BE tracking error: {e}")

    # ── ATR regime percentile feature ─────────────────────────────────────
    # Tells the model where current ATR sits in the historical distribution.
    # 0=very low vol, 50=normal, 100=extreme vol -- critical for regime awareness.
    try:
        import pickle as _pkl
        if os.path.exists("ml_model.pkl"):
            with open("ml_model.pkl", "rb") as _pf:
                _ens = _pkl.load(_pf)
            _atr_now = ctx.get("atr_14", 0) or 0
            _p10 = _ens.get("atr_p10", 0)
            _p50 = _ens.get("atr_p50", _atr_now)
            _p90 = _ens.get("atr_p90", _atr_now * 2)
            if _p90 > _p10 and _atr_now > 0:
                # Linear interpolation between percentiles
                if _atr_now <= _p10:
                    _pct = _atr_now / _p10 * 10
                elif _atr_now <= _p50:
                    _pct = 10 + (_atr_now - _p10) / (_p50 - _p10) * 40
                elif _atr_now <= _p90:
                    _pct = 50 + (_atr_now - _p50) / (_p90 - _p50) * 40
                else:
                    _pct = 90 + min(10, (_atr_now - _p90) / _p90 * 10)
                ctx["atr_regime_pct"]   = round(_pct, 1)
                ctx["atr_low_vol"]      = _pct < 25
                ctx["atr_normal_vol"]   = 25 <= _pct < 75
                ctx["atr_high_vol"]     = _pct >= 75
                ctx["atr_extreme_vol"]  = _pct >= 90
                ctx["atr_dead_market"]  = _pct < 5   # below p5 = no meaningful movement
    except Exception as _are:
        log.debug(f"ATR regime pct error: {_are}")

    # ── Regime backfill: infer if still unknown ────────────────────────────
    try:
        if not ctx.get("macro_regime") or ctx.get("macro_regime") == "unknown":
            ema_slope = ctx.get("ema_slope", 0) or 0
            hurst     = ctx.get("hurst_exponent", 0.5) or 0.5
            vol_ratio = ctx.get("vol_clustering_ratio", 1.0) or 1.0
            mom5      = ctx.get("momentum_5bars", 0) or 0
            if vol_ratio > 1.5:
                ctx["macro_regime"] = "volatile"
            elif abs(ema_slope) > 0.02:
                ctx["macro_regime"] = "trending_bull" if ema_slope > 0 else "trending_bear"
            elif hurst > 0.55:
                ctx["macro_regime"] = "trending_bull" if mom5 > 0 else "trending_bear"
            elif hurst < 0.45:
                ctx["macro_regime"] = "ranging"
            else:
                ctx["macro_regime"] = "ranging"
            ctx["regime_inferred"] = True
    except Exception as e:
        log.warning(f"Regime backfill error: {e}")

    # ── Ensemble ML prediction ─────────────────────────────────────────────
    # Run prediction on the context we just built, store results as features
    # so tomorrow's model can learn from ensemble agreement patterns
    try:
        pred = ensemble_predict(ctx)
        ctx["ml_win_prob"]      = pred["prob"]
        ctx["ml_confidence"]    = pred["confidence"]
        ctx["ml_votes"]         = pred.get("votes", 0)
        ctx["ml_agreement"]     = pred.get("agreement", 0.5)
        # Log HIGH confidence predictions prominently
        # v175: throttle -- was logging every iteration. Cache by
        # (symbol, prob_bucket) so only meaningful changes log.
        if pred["confidence"] == "HIGH":
            direction = "WIN" if pred["prob"] >= 0.6 else "LOSS"
            _ml_bucket = round(pred["prob"] * 20) / 20  # 0.05 buckets
            _ml_key = (ctx.get("symbol", "?"), direction, _ml_bucket)
            _ml_seen = getattr(ensemble_predict, "_ml_log_seen", {})
            _ml_now_ts = datetime.now(timezone.utc).timestamp()
            _ml_last = _ml_seen.get(_ml_key, 0)
            if _ml_now_ts - _ml_last > 300:  # 5 min minimum gap per (symbol, direction, bucket)
                log.info(f"  ML ensemble: {pred['prob']:.1%} {direction} "
                         f"({pred.get('votes',0)}/{pred.get('total',0)} models agree)")
                _ml_seen[_ml_key] = _ml_now_ts
                if len(_ml_seen) > 50:
                    _ml_seen = {k: v for k, v in _ml_seen.items()
                                if _ml_now_ts - v < 600}
                setattr(ensemble_predict, "_ml_log_seen", _ml_seen)
        # ── Update implied-edge comparison features now that ml_win_prob is real ──
        # These were computed earlier with ml_prob=0.5 (placeholder).
        # Now we have the actual ensemble prediction -- recompute with real value.
        try:
            ml_prob    = pred["prob"]
            p_implied  = ctx.get("implied_edge", 0.5) or 0.5
            edge_gap   = ml_prob - p_implied
            ctx["ml_vs_implied_gap"]  = round(edge_gap, 3)
            ctx["ml_overconfident"]   = edge_gap > 0.15
            ctx["ml_underconfident"]  = edge_gap < -0.15
            ctx["high_conviction"]    = abs(edge_gap) < 0.08 and ml_prob > 0.6
            ctx["dual_confirmation"]  = (p_implied > 0.55 and ml_prob > 0.60
                                         and abs(edge_gap) < 0.10)
            # model_vs_math_agree/conflict also depend on this
            ctx["model_vs_math_agree"]   = abs(edge_gap) < 0.10
            ctx["model_vs_math_conflict"] = abs(edge_gap) > 0.20
        except Exception as _e:
            log.debug(f"implied_edge update error: {_e}")
    except Exception as e:
        log.warning(f"Ensemble predict error: {e}")

    # ── PER-SETUP ROLLING WIN RATE ─────────────────────────────────────────
    # Mandelbrot recommendation: track how THIS SPECIFIC SETUP has performed
    # recently on THIS SPECIFIC SYMBOL. The model learns "this setup is hot
    # right now" vs "this setup is cold right now" -- much more useful than
    # global win rates which are stable and uninformative.
    try:
        _all_trades = _cached_trades  # shared log cache

        setup_key    = f"{signal.strategy}|{signal.setup_name}"
        symbol       = signal.symbol

        # Get last 10 and last 20 DECISIVE trades (win/loss only -- BEs excluded)
        # BE excluded: with ENABLE_BREAKEVEN=False, BEs are EOD noise
        # WR = W / (W+L) only -- same formula as get_setup_stats()
        _decisive = ('win', 'eod_win', 'loss', 'eod_loss')
        _setup_trades = [
            t for t in _all_trades
            if f"{t.get('strategy','?')}|{t.get('setup_name','?')}" == setup_key
            and t.get('symbol') == symbol
            and t.get('outcome') in _decisive
            and not t.get('random', False)
        ]

        # Last 10 on this setup+symbol
        recent_10 = _setup_trades[-10:]
        if len(recent_10) >= 3:
            w10 = sum(1 for t in recent_10 if t.get('outcome') in ('win','eod_win'))
            d10 = len(recent_10)  # all decisive -- no BEs in list
            ctx['setup_wr_last10_symbol']  = round(w10 / d10, 3)
            ctx['setup_hot']               = w10 / d10 >= 0.7
            ctx['setup_cold']              = w10 / d10 <= 0.3
            ctx['setup_streak_wins']       = sum(1 for t in reversed(recent_10)
                                                if t.get('outcome') in ('win','eod_win')
                                                and all(x.get('outcome') in ('win','eod_win')
                                                       for x in list(reversed(recent_10))[:list(reversed(recent_10)).index(t)+1]))
        else:
            ctx['setup_wr_last10_symbol']  = 0.5
            ctx['setup_hot']               = False
            ctx['setup_cold']              = False
            ctx['setup_streak_wins']       = 0

        # Last 20 on this setup across ALL symbols (broader signal)
        _setup_all_symbols = [
            t for t in _all_trades
            if f"{t.get('strategy','?')}|{t.get('setup_name','?')}" == setup_key
            and t.get('outcome') in _decisive
            and not t.get('random', False)
        ]
        recent_20 = _setup_all_symbols[-20:]
        if len(recent_20) >= 5:
            w20 = sum(1 for t in recent_20 if t.get('outcome') in ('win','eod_win'))
            d20 = len(recent_20)
            ctx['setup_wr_last20']         = round(w20 / d20, 3)
            prev_20 = _setup_all_symbols[-40:-20]
            prev_w  = sum(1 for t in prev_20 if t.get('outcome') in ('win','eod_win'))
            prev_d  = max(len(prev_20), 1)
            ctx['setup_trending_up']       = (w20 / d20 > prev_w / prev_d)
        else:
            ctx['setup_wr_last20']         = 0.5
            ctx['setup_trending_up']       = False

        # Consecutive losses on this setup -- cooldown signal for ML
        recent_5 = _setup_trades[-5:]
        consec_losses = 0
        for t in reversed(recent_5):
            if t.get('outcome') in ('loss', 'eod_loss'):
                consec_losses += 1
            else:
                break
        ctx['setup_consec_losses']         = consec_losses
        ctx['setup_on_loss_streak']        = consec_losses >= 3

    except Exception as e:
        log.warning(f"Per-setup rolling WR error: {e}")
        ctx['setup_wr_last10_symbol']  = 0.5
        ctx['setup_wr_last20']         = 0.5
        ctx['setup_hot']               = False
        ctx['setup_cold']              = False
        ctx['setup_consec_losses']     = 0
        ctx['setup_on_loss_streak']    = False
        ctx['setup_trending_up']       = False

    # ── Bool->int sweep: sklearn imputer needs numeric 0/1, not Python bool ──
    # Any feature set as True/False gets converted to 1/0 here
    # This fixes: is_doji, is_strong_bull, rsi_oversold, kalman_bull, etc.
    for _k, _v in ctx.items():
        if isinstance(_v, bool):
            ctx[_k] = int(_v)

    return ctx

def make_json_safe(obj):
    """Recursively convert non-JSON-serializable types."""
    if isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [make_json_safe(v) for v in obj]
    if isinstance(obj, bool):
        return int(obj)
    if isinstance(obj, (int, float, str)) or obj is None:
        return obj
    return str(obj)

# ── ML ENSEMBLE + ONLINE LEARNING ───────────────────────────────────────────

def build_feature_vector(trade: dict) -> list:
    """
    Build ML feature vector with interaction features.
    v2 -- all ctx gaps filled. 51 new features added.
    Direction encoded as int: 1=long/bull, -1=short/bear, 0=ranging/unknown.
    Stale BE features removed. All logged-but-not-trained features now included.

    v156: LEAKY_FEATURES are zeroed out (replaced with NaN -> imputed to median).
    These features are computed using rolling outcome stats that include the SAME
    trades the model is being trained on. They look predictive in-sample because
    they ARE the labels in disguise. In deployment they're stale and predictive
    in the opposite direction (regime-flip artefact), which is exactly the
    inversion pattern in ml_report25 (sep=-0.084, calibration non-monotonic).
    Removing them cleanly fixes the inversion at its root cause.
    """
    ctx = trade.get("context", {})

    # v156+v157: features that leak label information into the predictor.
    # All are computed from rolling WR/streak stats over the SAME trade history
    # the model trains on -- they ARE the labels in disguise. They drive in-sample
    # AUC up while destroying live separation (the inversion in ml_report25).
    #
    # v157 expansion: audited capture_market_context() exhaustively. Found 10
    # additional rolling-outcome features the v156 list missed. All bypass the
    # model now via NaN -> dead-feature pruner.
    LEAKY_FEATURES = {
        # ── v156 set ──────────────────────────────────────────────────────
        "this_hour_win_rate", "this_hour_profitable", "this_hour_losing",
        "setup_wr_last10_symbol", "setup_wr_last20",
        "setup_hot", "setup_cold",
        "setup_consec_losses", "setup_on_loss_streak",
        "setup_trending_up", "setup_streak_wins",
        "losing_days_streak", "on_losing_streak", "streak_size_penalty",
        # ── v157 additions ────────────────────────────────────────────────
        # Per-symbol rolling outcome stats:
        "symbol_win_rate_100", "symbol_is_profitable", "symbol_is_losing",
        "symbol_streak", "symbol_on_hot_streak", "symbol_on_cold_streak",
        # Per-setup rolling outcome stats:
        "setup_wr_7d",
        "today_loss_rate", "hist_loss_rate",
        # Recent trade-context outcome features:
        "last_trade_was_loss", "consecutive_setup_losses", "win_rate_after_loss",
        # Break-even rolling outcome stats (BE 'would-have' analysis is also a leak):
        "be_would_win_without_move", "be_optimal", "be_hurting",
        # ── v164 additions: ZERO PREDICTIVE POWER per Analyzer 3 ───────────
        # All show |t|=0.00 across n=100+ observations.
        # They take up model capacity and teach nothing. Drop entirely.
        "is_optimal_time",
        "bearish_divergence", "bullish_divergence",
        "vix_low",
        "score_signal_detected", "score_optimal_time",
        "regime_inferred",
        "enrichment_ok",
        "spread_vs_avg", "spread_wide",
        "london_first_30min",
        "extreme_compression",
        "hurst_trending", "hurst_reverting", "hurst_random",
        "regime_persistence", "regime_established", "regime_new", "regime_mature",
        "ml_confidence_strength",
        # ── v167: score_signal factor MEANING INVERSION ─────────────────────
        # In v167 the score_signal() logic for key_levels and 15m_structure was
        # INVERTED based on Analyzer 7 findings. Old trades have these flags set
        # under the old logic; new trades set them under inverted logic. The ML
        # model can't reconcile both -- temporarily NaN'd out so the model
        # ignores them. After the trade log accumulates 200+ trades under v167's
        # logic, we can re-enable these features for the model in v168.
        "score_15m_structure",
        "score_key_levels",
    }

    def _dir(val):
        """Encode direction string as int: bull/long=1, bear/short=-1, else=0."""
        if val in ("trending_bull", "long", "bull"): return 1
        if val in ("trending_bear", "short", "bear"): return -1
        return 0

    # Base features
    BASE = [
        # ── Score components ──────────────────────────────────────────────
        "score_15m_structure", "score_1h_direction", "score_5m_bar",
        "score_optimal_time", "score_signal_detected", "score_daily_position",
        "score_volatility", "score_key_levels",

        # ── Price action ──────────────────────────────────────────────────
        "rsi_14", "atr_14", "spread_atr_ratio", "candle_size_ratio",
        "candle_close_pos", "candle_body_ratio", "is_large_bar", "is_small_bar",
        "price_above_ema", "ema_slope", "distance_from_ema_pct",
        "higher_highs", "higher_lows", "pos_in_daily_range",
        "daily_range_atr_ratio", "hour_server", "day_of_week",
        "hours_since_open", "london_close_zone", "volume_ratio",
        "portfolio_heat_pct", "stop_atr_ratio", "rr_ratio", "confidence",
        "regime_multiplier", "regime_with_trend", "regime_against_trend",
        "bars_since_1pct_move", "near_round_number", "level_test_count",
        "consecutive_ranging_days", "symbols_same_direction",

        # ── NEW: Candle detail -- was logged but not trained ───────────────
        "candle_is_green",       # is entry candle bullish
        "candle_upper_wick",     # upper wick size -- rejection
        "candle_lower_wick",     # lower wick size -- support
        "candle_streak",         # consecutive same-colour bars
        "is_doji",               # indecision candle -- bad timing
        "is_inside_bar",         # compression before move
        "is_outside_bar",        # volatility expansion
        "is_strong_bull",        # strong bullish 15m candle
        "is_strong_bear",        # strong bearish 15m candle
        "is_strong_bull_5m",     # strong bullish 5m candle
        "is_strong_bear_5m",     # strong bearish 5m candle
        "prev_candle_green",     # previous candle direction
        "prev_bar_climactic",    # previous bar exhaustion signal
        "prev_close_pos",        # where previous bar closed in its range
        "prev_size_ratio",       # previous bar size vs average
        "prev_is_doji",          # previous bar was doji

        # ── NEW: Key levels -- computed but not trained ────────────────────
        "at_daily_open",         # price at daily open -- major level
        "at_yesterday_high",     # price at yesterday high -- resistance
        "at_yesterday_low",      # price at yesterday low -- support
        "at_weekly_high",        # at weekly high
        "at_weekly_low",         # at weekly low
        "nearest_key_pct",       # distance to nearest key level
        "daily_range_pct_complete",  # how much of daily range used
        "daily_range_exceeded",  # range exceeded avg -- exhaustion
        "distance_from_daily_open_pct",  # distance from daily open

        # ── NEW: Direction -- CRITICAL gap, was never trained ─────────────
        # Encoded as int via _dir(): bull/long=1, bear/short=-1, ranging=0
        # direction_15m/5m/1h/daily_trend are strings -- handled in special block below

        # ── NEW: RSI variants -- rsi_14 trained but booleans were not ─────
        "rsi_oversold",          # RSI < 30
        "rsi_overbought",        # RSI > 70
        "rsi_extreme",           # RSI < 20 or > 80
        "rsi_5m",                # 5m RSI value

        # ── NEW: Range context -- computed but not trained ─────────────────
        "in_range_15m",          # 15m currently ranging
        "in_range_5m",           # 5m currently ranging
        "in_range_1h",           # 1h currently ranging
        "price_in_range_pct",    # position within range

        # ── NEW: Overnight range context ──────────────────────────────────
        # PRUNED: "above_overnight",       # price above overnight range  # low-variance / constant feature
        # PRUNED: "below_overnight",       # price below overnight range  # low-variance / constant feature
        # PRUNED: "inside_overnight",      # price inside overnight range  # low-variance / constant feature
        # PRUNED: "overnight_atr_ratio",   # overnight range vs ATR  # low-variance / constant feature
        # PRUNED: "price_vs_overnight",    # position within overnight range  # low-variance / constant feature

        # ── NEW: Momentum ─────────────────────────────────────────────────
        "momentum_fresh",        # big move < 5 bars ago
        "momentum_decayed",      # big move > 20 bars ago
        "ema_slope_accel",       # EMA acceleration
        "bearish_divergence",    # RSI bearish divergence
        "bullish_divergence",    # RSI bullish divergence

        # ── NEW: Position context ─────────────────────────────────────────
        "open_longs",            # how many longs open
        "open_shorts",           # how many shorts open
        "open_positions_total",  # total open positions

        # ── NEW: Historical same-setup context ────────────────────────────
        "same_setup_yesterday",  # same setup fired yesterday at this time

        # ── NEW: TP outcome feature -- logged but not trained ──────────────
        # "tp_never_close" REMOVED -- populated post-trade (look-ahead bias)

        # ── NEW: Market volatility context ────────────────────────────────
        "vix_equiv_pct",         # implied volatility proxy

        # ── Market microstructure ─────────────────────────────────────────
        "spread_vs_avg", "spread_wide", "spread_pts",
        "volume_vs_avg_20", "high_volume_signal", "low_volume_signal",
        "volume_trend_rising", "volume_trend_falling",
        "bars_since_sig_move", "setup_stale", "setup_fresh",
        "dist_prev_high_atr", "dist_prev_low_atr", "dist_prev_close_atr",
        "near_prev_high", "near_prev_low", "near_prev_close",
        "above_prev_high", "below_prev_low",

        # ── Cross-symbol correlation ──────────────────────────────────────
        "n_symbols_same_dir", "all_symbols_aligned", "strong_confluence",
        "ger40_leading_us30",

        # ── Session context ───────────────────────────────────────────────
        "london_first_30min", "london_session", "ny_first_30min",
        "ny_session", "overlap_session", "asian_session",
        "monday_open", "friday_close",
        "mins_to_hour", "near_hour_mark",
        # PRUNED: "mins_to_news_event", "near_news_event", "very_near_news",  # low-variance / constant feature

        # ── Setup quality + pattern recognition ───────────────────────────
        "pattern_bars_exact", "pattern_bars", "pattern_fast", "pattern_slow", "pattern_ideal",
        "pattern_clean", "pattern_messy",
        "at_swing_high", "at_swing_low", "at_swing_extreme", "at_swing_middle", "pos_in_swing",
        # PRUNED: "gap_size_pct", "has_gap", "gap_fill_setup", "gap_filled_pct",  # low-variance / constant feature
        "inside_bar_count", "has_inside_bars", "strong_compression", "extreme_compression",
        "has_failed_breakout", "entry_tightness", "tight_entry",

        # ── Self-improvement ──────────────────────────────────────────────
        "ml_recent_accuracy", "ml_avg_confidence", "ml_mind_changes", "ml_indecisive",
        "ml_confidence_rising", "ml_confidence_falling",
        "setup_wr_7d", "setup_drift", "setup_drifting_down", "setup_improving",

        # ── Risk intelligence ─────────────────────────────────────────────
        "drawdown_velocity", "losing_faster_than_avg", "today_loss_rate", "hist_loss_rate",
        "symbol_win_rate_100", "symbol_is_profitable", "symbol_is_losing",
        "symbol_streak", "symbol_on_hot_streak", "symbol_on_cold_streak",
        "correlated_long_exposure", "correlated_short_exposure",
        "high_correlation_risk", "max_correlation_risk", "net_directional_bias",
        "this_hour_win_rate", "this_hour_profitable", "this_hour_losing",

        # ── Calendar effects ──────────────────────────────────────────────
        # PRUNED: "is_opex_week", "is_opex_day", "is_month_end", "is_month_start",  # low-variance / constant feature
        # PRUNED: "is_monday_open", "is_friday_close_zone", "calendar_risk",  # low-variance / constant feature

        # ── Spread gate ───────────────────────────────────────────────────
        "spread_vs_hourly_avg", "spread_abnormal", "spread_very_wide",

        # ── Pairs ─────────────────────────────────────────────────────────
        "ger_us100_zscore", "ger_us100_diverged", "ger_us100_extreme",
        "us30_us100_zscore", "us30_us100_diverged", "us30_us100_extreme",
        "uk_ger_zscore", "uk_ger_diverged", "uk_ger_extreme",

        # ── Session transitions ───────────────────────────────────────────
        "asia_lon_transition", "lon_ny_transition", "lon_close_transition",
        "ny_close_transition", "any_session_transition", "ny_close_zone",

        # ── Losing streak ─────────────────────────────────────────────────
        "losing_days_streak", "on_losing_streak", "streak_size_penalty",
        "setup_wr_last10_symbol", "setup_wr_last20", "setup_hot", "setup_cold",
        "setup_consec_losses", "setup_on_loss_streak", "setup_trending_up",
        "setup_streak_wins",

        # ── Shannon mutual info ───────────────────────────────────────────
        "momentum_signal_agreement", "momentum_signal_conflict",
        "price_momentum_divergence",

        # ── Thorp portfolio heat ──────────────────────────────────────────
        "corr_adjusted_long_heat", "corr_adjusted_short_heat",
        "corr_adjusted_total_heat", "true_portfolio_overweight",

        # ── Simons regime persistence ─────────────────────────────────────
        "regime_persistence", "regime_established", "regime_new", "regime_mature",

        # ── Gauss residual ────────────────────────────────────────────────
        "ml_confidence_strength", "ml_very_confident", "ml_uncertain",
        # model_vs_math_agree, model_vs_math_conflict -- REMOVED (circular).

        # ── Mandelbrot multi-scale vol ────────────────────────────────────
        "vol_scale_ratio_5_15", "vol_scales_agree",
        "vol_expanding_multi", "vol_contracting_multi",

        # ── Black-Scholes time decay ──────────────────────────────────────
        "setup_freshness", "setup_stale_bs", "setup_fresh_bs",
        "level_tested_recently",

        # ── Kahneman loss aversion ────────────────────────────────────────
        "last_trade_was_loss", "consecutive_setup_losses", "win_rate_after_loss",

        # ── Simons formulas ───────────────────────────────────────────────
        "autocorr_lag1", "autocorr_lag5", "ac_trending", "ac_reverting", "ac_random",
        "direction_consistency", "strong_trend_signal", "ac5_trending",
        "hurst_exponent", "hurst_trending", "hurst_reverting", "hurst_random",
        "price_entropy", "low_entropy", "high_entropy", "entropy_tradeable",
        "vol_clustering_ratio", "vol_expanding", "vol_contracting", "vol_stable",
        "vol_accelerating", "vol_decelerating",
        "kalman_slope_pct", "kalman_bull", "kalman_bear", "kalman_flat",
        "price_above_kalman", "dist_from_kalman_pct", "extended_from_kalman",

        # ── AR3, fractal, pairs, momentum confluence ──────────────────────
        "ar3_prediction", "ar3_bullish", "ar3_bearish", "ar3_neutral",
        "fractal_dimension", "fd_trending", "fd_choppy", "fd_neutral",
        "ger_us_spread_zscore", "ger_leading_up", "ger_leading_down",
        "pairs_converging", "pairs_diverged",
        "momentum_confluence", "strong_momentum", "weak_momentum",
        "momentum_agrees_long", "momentum_agrees_short", "momentum_disagrees",

        # ── Black-Scholes implied edge ────────────────────────────────────
        "implied_edge", "implied_rr",
        # ml_vs_implied_gap, ml_overconfident, ml_underconfident,
        # high_conviction, dual_confirmation -- REMOVED (circular: use current ML output as input).
        # These are kept in ctx for logging but not fed back into the model.

        # ── VWAP ─────────────────────────────────────────────────────────
        "vwap_dist_pct", "vwap_dist_pts", "above_vwap", "below_vwap",
        "far_above_vwap", "far_below_vwap", "near_vwap",
        "vwap_aligned_long", "vwap_aligned_short",
        "vwap_against_long", "vwap_against_short",

        # ── Kurtosis + skewness ───────────────────────────────────────────
        "return_skewness", "return_kurtosis", "negative_skew", "positive_skew",

        # ── Feature availability flags (0=missing/failed, 1=real data) ────────
        # These let the model distinguish "neutral market" from "data failure".
        # Standard practice in production ML -- prevents default bias.
        "candles_ok",        # 1 if candle fetch succeeded (all price features are real)
        "kalman_available",  # 1 if Kalman filter ran (kalman_slope_pct is real)
        "ar3_available",     # 1 if AR3 model ran (ar3_prediction is real)
        "stat_available",    # 1 if autocorr/Hurst/entropy ran (those features are real)

        # ── ATR regime (where is current vol in historical distribution?) ─────
        "atr_regime_pct",    # 0-100 percentile of current ATR (50=normal)
        "atr_low_vol",       # ATR in bottom quartile -- tight market
        "atr_normal_vol",    # ATR in middle 50% -- normal conditions
        "atr_high_vol",      # ATR in top quartile -- volatile market
        "atr_extreme_vol",   # ATR in top 10% -- dangerous conditions
        "atr_dead_market",   # ATR in bottom 5% -- market not moving, skip

        # ── 1-minute enriched features (SSRN-grounded, backtest-validated) ──────
        # Filled by enrich_trades.py for historical trades.
        # For live trades: computed from MT5 1m candles where candles_ok=1,
        # otherwise default to neutral (0 / 0.5). Train/live mismatch is
        # bounded by enrichment_ok flag -- model learns to discount when =0.
        # Ridge regression confirmed these as top predictors on 400k real bars.
        "mom_5m",               # 5-min price momentum %
        "mom_15m",              # 15-min price momentum %
        "mom_30m",              # 30-min price momentum %
        "mom_60m",              # 60-min price momentum % (strongest in backtest)
        "orb_position_1m",      # Position vs opening range (0=low, 1=high, >1=breakout)
        "above_orb_1m",         # 1 if price broke above ORB
        "below_orb_1m",         # 1 if price broke below ORB
        "inside_orb_1m",        # 1 if inside opening range
        "vol_compression_ratio",# Short vol / long vol (< 0.8 = compressed)
        "pre_entry_bull_bars",  # Bullish 1m bars in last 5 before entry
        "pre_entry_wick_ratio", # Average wick ratio (noise level)
        "dow_sin_1m",           # Day-of-week sine (Ridge: strongest feature)
        "dow_cos_1m",           # Day-of-week cosine
        "is_monday_1m",         # Monday flag
        "is_friday_1m",         # Friday flag
        "is_wednesday_1m",      # Wednesday flag
        "ema_bull_align_1m",    # All EMAs (5/20/60) aligned bullish on 1m
        "ema_bear_align_1m",    # All EMAs aligned bearish on 1m
        "ema_slope_1m",         # Medium EMA slope from 1m bars
        "vol_profile_poc_dist_pct", # Distance from volume POC
        "above_session_vwap_1m",    # Above session VWAP (session-specific)
        "session_vwap_dist_pct_1m", # Distance from session VWAP %
        "day_range_position_1m",    # Position in day range (0-1)
        "enrichment_ok",        # 1 = real enriched values, 0 = defaults

        # ── Outcome quality -- EXCLUDED FROM TRAINING (post-trade leakage) ──
        # These features are populated AFTER the trade closes (by update_mfe_mae).
        # At entry time they are 0/None. Including them in training means the model
        # sees the trade's actual path as an input -> classic look-ahead bias.
        # They are still logged in ctx for analysis purposes, just not trained on.
        # REMOVED: "mfe_r", "mae_r", "mfe_mae_ratio",
        # REMOVED: "tp_reach_pct", "tp_clean_hit", "tp_scraped",
        # REMOVED: "sl_reach_pct", "sl_close_call", "sl_barely_touched",
        # REMOVED: "high_quality_trade", "low_quality_trade",
        # REMOVED: "duration_minutes", "fast_resolution", "slow_grind",

        # ── REMOVED: BE features -- stale with ENABLE_BREAKEVEN=False ─────
        # be_avg_mfe, be_count, be_was_protective, be_would_win_without_move,
        # be_optimal, be_hurting, be_trigger_hit
        # These were computed from BE trades which are now excluded from training.
        # Keeping them would feed the model features computed on data it never trains on.
    ]

    row = []
    for f in BASE:
        # v156: leaky features replaced with NaN so imputer fills median (uninformative)
        if f in LEAKY_FEATURES:
            row.append(float("nan"))
            continue
        val = ctx.get(f, trade.get(f))
        if val is None:
            row.append(float("nan"))
        elif isinstance(val, bool):
            row.append(int(val))
        else:
            try:
                row.append(float(val))
            except Exception:
                row.append(float("nan"))

    # ── Direction features -- string encoded as int ────────────────────────
    # CRITICAL gap fix: model now knows if trade is long or short
    # direction_15m, direction_5m, direction_1h, daily_trend are strings
    # _dir() converts: bull/long=1, bear/short=-1, ranging/unknown=0
    row.append(_dir(ctx.get("direction_15m", "")))   # 15m market direction
    row.append(_dir(ctx.get("direction_5m", "")))    # 5m market direction
    row.append(_dir(ctx.get("direction_1h", "")))    # 1h market direction
    row.append(_dir(ctx.get("daily_trend", "")))     # daily bias

    # ── Trade direction (long=1, short=-1) ───────────────────────────────
    # The actual trade direction -- long or short. This is the single most
    # important missing feature: without it the model treats long and short
    # entries identically even though their win rates differ by setup.
    trade_dir = trade.get("direction", ctx.get("trade_direction", ""))
    row.append(_dir(trade_dir))

    # ── Interaction features ──────────────────────────────────────────────

    # 1. Trend alignment -- 1h + 15m + regime all agree
    s15 = float(ctx.get("score_15m_structure", 0))
    s1h = float(ctx.get("score_1h_direction", 0))
    rwt = float(ctx.get("regime_with_trend", 0))
    row.append(s15 * s1h * rwt)

    # 2. Volatility-adjusted spread
    spread = float(ctx.get("spread_atr_ratio", 1.0) or 1.0)
    vix    = float(ctx.get("vix_equiv_pct", 1.0) or 1.0)
    row.append(spread / max(vix, 0.01))

    # 3. Time quality -- optimal time AND not london close
    opt = float(ctx.get("score_optimal_time", 0))
    lc  = float(ctx.get("london_close_zone", 0))
    row.append(opt * (1 - lc))

    # 4. Score density
    total_score = sum(float(ctx.get(f"score_{k}", 0)) for k in
                     ["signal_detected","15m_structure","5m_bar","optimal_time",
                      "1h_direction","daily_position","volatility","key_levels"])
    row.append(total_score / 8.0)

    # 5. Range position quality
    pos = float(ctx.get("pos_in_daily_range", 0.5) or 0.5)
    row.append(abs(pos - 0.5) * 2)

    # 6. Volume confirmation
    vol_ratio = float(ctx.get("volume_ratio", 1.0) or 1.0)
    s5m = float(ctx.get("score_5m_bar", 0))
    row.append(vol_ratio * s5m)

    # 7. Momentum health
    bars = float(ctx.get("bars_since_1pct_move", 10) or 10)
    row.append(1.0 / (1 + bars / 10))

    # 8. Portfolio heat penalty
    heat = float(ctx.get("portfolio_heat_pct", 0) or 0)
    row.append(1.0 / (1 + heat))

    # 9. NEW: Direction × range position
    # Long at bottom of range (pos~0) = good. Long at top (pos~1) = bad.
    # Short at top of range = good. Short at bottom = bad.
    # Encodes the directional quality of the entry location.
    trade_dir_int = _dir(trade_dir)
    pos_quality = (1 - pos) if trade_dir_int == 1 else pos if trade_dir_int == -1 else 0.5
    row.append(pos_quality)

    # 10. NEW: Candle alignment with direction
    # Green candle for long = aligned. Red candle for short = aligned.
    candle_green = int(bool(ctx.get("candle_is_green", False)))
    aligned = (candle_green == 1 and trade_dir_int == 1) or               (candle_green == 0 and trade_dir_int == -1)
    row.append(int(aligned))

    # 11. NEW: Volatility regime × setup freshness
    vix_val = float(ctx.get("vix_equiv_pct", 1.0) or 1.0)
    freshness = float(ctx.get("setup_freshness", 0.5) or 0.5)
    row.append(vix_val * freshness)

    # ── Final feature sanitisation ────────────────────────────────────────
    # 1. Replace any remaining NaN/inf with 0 (should be rare with defaults block)
    # 2. Clip extreme values -- Platt calibration is sensitive to outliers even
    #    though GBM is not. Clips at 99th-percentile-ish bounds per feature type.
    import math as _math
    sanitised = []
    for i, v in enumerate(row):
        # Replace NaN / inf
        if v is None or (isinstance(v, float) and (_math.isnan(v) or _math.isinf(v))):
            sanitised.append(0.0)
            continue
        v = float(v)
        # Clip by feature type using position-agnostic bounds
        # Counts / ratios / z-scores: clip to [-10, 10]
        # Percentages 0-100: clip to [0, 100]
        # Binary flags: clip to [0, 1]
        # We use a broad safe clip that preserves signal
        v = max(-50.0, min(50.0, v))  # global safety clip -- removes true outliers only
        sanitised.append(v)
    return sanitised


def _ml_outcome(t):
    """Get the best available outcome label for ML training.
    STRICT: only real win/loss outcomes. ALL breakevens excluded.
    BEs are noise -- trade didn't reach TP, calling it a win/loss
    based on virtual_outcome was corrupting US30 WR to 96.8%.
    """
    real = t.get("outcome")
    # Real win/loss outcomes -- use directly
    if real in ("win", "loss"):
        return real
    # EOD closes -- treat as win/loss for ML (they are real outcomes)
    if real == "eod_win":
        return "win"
    if real == "eod_loss":
        return "loss"
    # ALL breakevens excluded -- including virtual_outcome logic
    # BE = trade didn't reach TP. Not a win. Not a loss. Skip.
    if real in ("breakeven", "eod_breakeven"):
        return None
    return None  # skip -- no usable label


def _ml_quality_label(t):
    """Quality-weighted continuous label for ML training.
    
    Replaces binary 0/1 with a float that captures HOW WELL a trade
    performed -- not just whether it won or lost.
    
    Uses MFE (max favorable excursion) and MAE (max adverse excursion)
    stored in context after trade closes via update_mfe_mae().
    
    Returns float in roughly [-1.0, 1.5] range:
      +1.0 = clean win (hit TP cleanly, low drawdown)
      +0.5 = scraped win (barely hit TP, was underwater first)
       0.0 = breakeven or boundary
      -0.5 = loss that teased (got close to TP before stopping out)
      -1.0 = clean loss (straight to SL, never in profit)
    
    Falls back to binary 0/1 if MFE/MAE not available (old trades).
    """
    outcome = _ml_outcome(t)
    if outcome is None:
        return None
    
    ctx = t.get("context", {})
    mfe = ctx.get("mfe_r")   # max favorable excursion in R
    mae = ctx.get("mae_r")   # max adverse excursion in R
    
    # Fallback: no MFE/MAE data (old trades, data collection trades)
    if mfe is None or mae is None:
        return 1.0 if outcome == "win" else -0.5
    
    try:
        mfe = float(mfe)
        mae = float(mae)
    except (TypeError, ValueError):
        return 1.0 if outcome == "win" else -0.5
    
    if outcome == "win":
        # Clean win: MFE >> MAE (went straight to TP)
        # Scraped win: MFE ≈ 1.0 (just barely hit TP), MAE was high
        # Quality bonus for trades that ran beyond TP before closing
        mfe_quality = min(mfe / 1.0, 1.5)   # cap at 1.5x (outlier trades)
        drawdown_penalty = min(mae / 0.5, 0.5)  # penalise for going underwater
        raw = mfe_quality - drawdown_penalty
        # Clip to [-1, 1] and apply tanh-style soft clamp for stability.
        # Prevents outlier trades from dominating gradient during training.
        clipped = max(-1.0, min(1.0, raw))
        return round(max(0.0, clipped), 3)  # wins: [0.0, 1.0]
    else:
        # Clean loss: went straight to SL (mae=1.0, mfe≈0)
        # Teaser loss: got close to TP before reversing to SL
        tease_bonus = min(mfe / 1.0, 0.5)
        raw = -(1.0 - tease_bonus)
        clipped = max(-1.0, min(0.0, raw))  # losses: [-1.0, 0.0]
        return round(clipped, 3)



def cpcv_turing_test(placed, build_feature_vector, _ml_outcome,
                     _quality_weight, _ml_quality_label, _age_weight,
                     avg_auc, col_filter, log,
                     n_splits=6, k_test=2, embargo_hours=12):
    """
    Combinatorial Purged Cross-Validation Turing test (SSRN 4686376).
    Replaces single walk-forward split with C(n_splits, k_test) combinations.
    Gap is averaged across all splits -- stable, not window-sensitive.
    col_filter: the _col_filter from online_retrain (may be None).
    """
    import numpy as np
    from itertools import combinations
    from datetime import datetime, timedelta, timezone
    from sklearn.pipeline import Pipeline
    from sklearn.impute import SimpleImputer
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.metrics import roc_auc_score

    result = {
        "turing_auc": None, "turing_gap": None, "turing_gap_std": None,
        "turing_real": False, "turing_n_splits": 0, "turing_method": "cpcv",
    }
    min_trades = n_splits * 20
    if len(placed) < min_trades:
        log.info(f"  CPCV: insufficient data ({len(placed)} < {min_trades}) -- skipping")
        return result

    def _ts(t): return t.get("timestamp", "") or ""
    sorted_trades = sorted(placed, key=_ts)
    n = len(sorted_trades)
    fold_size = n // n_splits
    folds = []
    for i in range(n_splits):
        start = i * fold_size
        end = start + fold_size if i < n_splits - 1 else n
        folds.append(sorted_trades[start:end])

    test_combinations = list(combinations(range(n_splits), k_test))
    auc_scores, gap_scores = [], []

    for test_idx_combo in test_combinations:
        test_trades = []
        for idx in test_idx_combo:
            test_trades.extend(folds[idx])

        test_ts = [_ts(t) for t in test_trades if _ts(t)]
        if not test_ts: continue
        try:
            ts_start_dt = datetime.fromisoformat(min(test_ts)[:19]).replace(tzinfo=timezone.utc)
            ts_end_dt   = datetime.fromisoformat(max(test_ts)[:19]).replace(tzinfo=timezone.utc)
            embargo_before = (ts_start_dt - timedelta(hours=embargo_hours)).strftime("%Y-%m-%d %H:%M:%S")
            embargo_after  = (ts_end_dt   + timedelta(hours=embargo_hours)).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            continue

        train_raw = []
        for idx in range(n_splits):
            if idx not in test_idx_combo:
                train_raw.extend(folds[idx])
        train_trades = [t for t in train_raw
                        if _ts(t) < embargo_before or _ts(t) > embargo_after]

        if len(train_trades) < 30 or len(test_trades) < 10: continue

        # Filter to resolved outcomes only (no BEs in test set)
        test_resolved = [t for t in test_trades if _ml_outcome(t) in ("win", "loss")]
        if len(test_resolved) < 5: test_resolved = test_trades

        try:
            X_tr = np.array([build_feature_vector(t) for t in train_trades])
            y_tr = np.array([1 if _ml_outcome(t) == "win" else 0 for t in train_trades])
            X_te = np.array([build_feature_vector(t) for t in test_resolved])
            y_te = np.array([1 if _ml_outcome(t) == "win" else 0 for t in test_resolved])
            # Apply col_filter to match exact feature set used by ensemble
            if col_filter is not None:
                X_tr = X_tr[:, col_filter]
                X_te = X_te[:, col_filter]
        except Exception as e:
            log.debug(f"  CPCV split build error: {e}"); continue

        if len(set(y_tr)) < 2 or len(set(y_te)) < 2: continue

        try:
            w_tr = np.array([
                _quality_weight(_ml_quality_label(t) or 0) * _age_weight(t)
                for t in train_trades
            ])
            w_tr = np.clip(np.nan_to_num(w_tr, nan=1.0), 0.01, 10.0)
        except Exception:
            w_tr = np.ones(len(train_trades))

        try:
            model = Pipeline([
                ("imp", SimpleImputer(strategy="median")),
                ("clf", GradientBoostingClassifier(
                    n_estimators=50, max_depth=3, learning_rate=0.1, random_state=42))
            ])
            model.fit(X_tr, y_tr, clf__sample_weight=w_tr)
            probs = model.predict_proba(X_te)[:, 1]
            fold_auc = roc_auc_score(y_te, probs)
            auc_scores.append(fold_auc)
            gap_scores.append(avg_auc - fold_auc)
        except Exception as e:
            log.debug(f"  CPCV split fit error: {e}"); continue

    if len(auc_scores) < 2:
        log.warning(f"  CPCV: too few valid splits ({len(auc_scores)}) -- falling back")
        return result

    mean_auc = float(np.mean(auc_scores))
    mean_gap = float(np.mean(gap_scores))
    std_gap  = float(np.std(gap_scores))
    result.update({
        "turing_auc": round(mean_auc, 3), "turing_gap": round(mean_gap, 3),
        "turing_gap_std": round(std_gap, 3), "turing_real": mean_auc > 0.60,
        "turing_n_splits": len(auc_scores), "turing_method": "cpcv",
    })
    return result


def online_retrain(trades: list, n_resolved: int):
    """
    Retrain ensemble of 5 models on different time windows.
    Called automatically when 5+ new trade outcomes appear.
    Each model covers a different time horizon -- ensemble voting
    requires 3/5 agreement before a trade is considered HIGH confidence.
    """
    try:
        import pickle
        import numpy as np
        from sklearn.ensemble import GradientBoostingClassifier
        from sklearn.pipeline import Pipeline
        from sklearn.impute import SimpleImputer
        from sklearn.model_selection import cross_val_score, StratifiedKFold

        # Include random trades in ML training -- they are our most unbiased data.
        # Random trades fire in ALL conditions regardless of filters, giving the ML
        # a true picture of what happens in bad conditions vs good ones.
        # We weight them at 0.5 (half weight) vs normal trades (weight 1.0)
        # so they inform but don't dominate the model.
        # NOTE: Global model trains on ALL symbols mixed (for cross-symbol signals).
        # Per-symbol models (Option B) train each symbol independently.
        # GER40 excluded from SYMBOLS_MAIN (not traded) but has its own ML model.
        # ML trains on win/loss/eod_win/eod_loss ONLY
        # ALL breakevens (breakeven, eod_breakeven) excluded from ML training
        # virtual_outcome logic REMOVED -- was inflating US30 WR to 96.8%
        # BE trades still used for Kelly/cooldown stats (outcome="breakeven")
        placed = [t for t in trades
                 if t.get("placed", True)
                 and _ml_outcome(t) is not None
                 and not t.get("restart_close", False)   # exclude restart-closed trades -- random outcomes
                 and not t.get("random", False)]          # exclude random-direction exploration trades -- 50/50 noise

        # v180: REMOVED the off-symbol filter that v178/v179 had. The previous
        # version filtered placed[] to only US30 + US100 BEFORE training, which
        # cut ~280 GER40/UK100 historical trades. That dropped us under the
        # 300-trade minimum and blocked retrains entirely.
        #
        # Reasoning for the reversal: GER40 and UK100 had per-symbol AUCs of
        # 0.811 and 0.744 -- the model WAS learning real patterns from them.
        # Those patterns (Brooks setup-level behavior, hour-of-day effects,
        # volatility spikes) generalize across major indices. Removing them
        # was a guess that proved too aggressive.
        #
        # What v180 keeps: only-traded-symbol PER-SYMBOL models (handled by
        # the ALL_SYMBOLS loop downstream), and the May 4 exclusion.
        # What it removes: the global-model symbol filter that gutted training data.
        _excluded_off_symbol = 0  # always 0 in v180 -- kept var for log compat

        # v178: exclude contaminated-day trades. They combine the cluster bug,
        # deployment churn, and other bug-driven anomalies. Not a normal losing
        # day -- bug-driven, so keep out of training. Source of truth:
        # CONTAMINATED_DAYS module constant -- also used by get_setup_stats().
        # Date check is on the timestamp string prefix -- works because timestamps
        # are stored as "YYYY-MM-DD HH:MM:SS" so prefix match is correct.
        _pre_date_n = len(placed)
        placed = [t for t in placed
                  if not any(t.get("timestamp", "").startswith(d) for d in CONTAMINATED_DAYS)]
        _excluded_dates = _pre_date_n - len(placed)

        if _excluded_dates:
            log.info(f"  Training filter: excluded {_excluded_dates} contaminated-day trades "
                     f"-> {len(placed)} trades remain")

        if len(placed) < 30:
            return

        # Hard skip if insufficient unique samples for reliable global model
        # 300+ needed for meaningful generalisation with 308 features
        _min_for_global = 300
        if len(placed) < _min_for_global:
            log.warning(f"  Insufficient data for reliable ML ({len(placed)} < {_min_for_global})"
                       f" -- keeping previous model, skipping retrain")
            return

        # ── Clustering deduplication ──────────────────────────────────────
        # Problem: bot fires multiple trades per minute (same setup, same symbol).
        # Training treats them as independent samples but they share the exact
        # same market context -> model sees correlated trades as independent,
        # inflates dataset size, overestimates confidence on clustered setups.
        #
        # Fix: within each (symbol, setup_name, minute) group, keep only the
        # FIRST trade. Later trades in same minute have identical context.
        # Random trades kept regardless -- they are intentionally diverse.
        def _deduplicate_clustered(trades_list):
            # Note: random=True trades are excluded from placed before this runs
            seen = set()
            result = []
            for t in trades_list:
                ts  = t.get("timestamp", "")[:16]   # minute precision "YYYY-MM-DD HH:MM"
                sym = t.get("symbol", "")
                stp = t.get("setup_name", "")
                key = f"{ts}|{sym}|{stp}"
                if key not in seen:
                    seen.add(key)
                    result.append(t)
            removed = len(trades_list) - len(result)
            if removed > 0:
                log.info(f"  Clustering dedup: removed {removed} correlated trades "
                         f"({len(result)} unique remain)")
            return result

        placed = _deduplicate_clustered(placed)

        if len(placed) < 30:
            return

        # ── Turing holdout split -- TIME-BASED not count-based ────────────
        # Count-based holdout fails with high-frequency data (500+ trades/day)
        # because the holdout always contains only today's session.
        # Time-based holdout ensures the test set spans multiple regime changes.
        #
        # Auto-scaling based on total days of data:
        #   < 7 days:  hold out 2 days
        #   7-14 days: hold out 3 days
        #   14-30 days: hold out 5 days
        #   30+ days:  hold out 7 days (full week)
        from datetime import datetime as _dt, timedelta as _td, timezone as _tz
        try:
            timestamps = [t.get("timestamp","") for t in placed if t.get("timestamp")]
            if timestamps:
                earliest = min(timestamps)[:10]
                latest   = max(timestamps)[:10]
                from datetime import datetime as _dt2
                days_of_data = (_dt2.fromisoformat(latest) - _dt2.fromisoformat(earliest)).days + 1
            else:
                days_of_data = 1
        except Exception as _dod_e:
            log.debug(f"days_of_data fallback: {_dod_e}")
            days_of_data = 1

        if days_of_data < 7:
            holdout_days = 2
        elif days_of_data < 14:
            holdout_days = 5
        elif days_of_data < 30:
            holdout_days = 10
        else:
            holdout_days = 14

        # Use strftime to match stored timestamp format "%Y-%m-%d %H:%M:%S"
        # isoformat() produces "2026-04-08T21:59:10+00:00" which doesn't sort
        # correctly against stored "2026-04-08 21:59:10" due to T vs space and +00:00
        holdout_cutoff = (_dt.now(_tz.utc) - _td(days=holdout_days)).strftime("%Y-%m-%d %H:%M:%S")
        train_placed = [t for t in placed if t.get("timestamp","") < holdout_cutoff]
        test_placed  = [t for t in placed if t.get("timestamp","") >= holdout_cutoff]

        log.info(f"  Turing holdout: {days_of_data} days data -> "
                f"holdout={holdout_days} days | "
                f"train={len(train_placed)} test={len(test_placed)}")

        if len(train_placed) < 30:
            train_placed = placed  # not enough data yet, train on all
            test_placed  = placed[-max(50, len(placed)//5):]

        # ── Reserve Platt validation set BEFORE training ──────────────────
        # 20% of placed (min 60, max 200 most recent trades) held out for
        # Platt calibration ONLY -- never seen by the model during training.
        # This is the fix for data leakage: Platt now calibrates on truly
        # unseen data, so 80% model confidence will actually mean ~80% WR.
        platt_val_n   = max(60, min(200, len(placed) // 5)) if len(placed) >= 150 else 0
        # Platt val set carved from OLDER trades -- disjoint from Turing holdout.
        # Turing test_p = placed[-30:] (most recent). If Platt also uses placed[-200:],
        # the 30 Turing test trades are a strict subset of Platt val, making both
        # diagnostics measure the same recent regime and unable to contradict each other.
        # Fix: use placed[-2*platt_val_n : -platt_val_n] (the preceding window).
        # This is disjoint from Turing[-30:] and covers a different regime slice.
        # Graceful degradation: if placed has fewer than 2*platt_val_n trades,
        # the slice naturally collapses to whatever older data is available.
        # Filter to real-risk trades only -- data collection trades (0.015% risk)
        # have different feature distributions (score 2-4/8 vs 5+/8 for real trades)
        # and would corrupt Platt calibration with a mixed distribution.
        _real_placed = [t for t in placed if (t.get("risk_pct") or 0) > 0.02]
        _platt_base  = _real_placed if len(_real_placed) >= platt_val_n else placed
        if platt_val_n > 0 and len(_platt_base) >= platt_val_n * 2:
            platt_val_set = _platt_base[-platt_val_n * 2 : -platt_val_n]
        elif platt_val_n > 0:
            platt_val_set = _platt_base[-platt_val_n:]  # fallback: newest trades (oldest are most contaminated)
        else:
            platt_val_set = []
        # Remove platt validation trades from training windows
        platt_val_ts  = set(t.get("timestamp","") + str(t.get("symbol","")) for t in platt_val_set)

        def _exclude_platt_val(trades_list):
            """Remove Platt validation trades from a training window."""
            if not platt_val_ts:
                return trades_list
            return [t for t in trades_list
                    if t.get("timestamp","") + str(t.get("symbol","")) not in platt_val_ts]

        # Apply exclusion to train_placed so global model never sees platt_val_set
        train_placed = _exclude_platt_val(train_placed)
        if len(train_placed) < 20:
            # Edge case: too few trades left after exclusion -- relax
            platt_val_set = []
            platt_val_n   = 0
            train_placed  = placed  # fallback: use all (old behaviour)

        # Build dataset with sample weights
        # ── Exclude candle-fail trades from training ─────────────────────────
        # Trades where candles_ok=0 have all-default feature vectors.
        # Training on them injects noise: same features, different outcomes.
        # candles_ok defaults to 1 for old trades (backward compat).
        # v154 FIX: enrichment_ok=1 (true 1m data) is better than candles_ok=1 (15m proxy)
        # Accept a trade as having real features if EITHER candles_ok=1 OR enrichment_ok=1
        # This prevents the 1m-enriched repair trades from being incorrectly excluded
        train_placed = [t for t in train_placed
                        if (t.get("context", {}).get("candles_ok", 1) != 0
                            or t.get("context", {}).get("enrichment_ok", 0) == 1)]
        n_candle_fail = len(placed) - len(train_placed) - len([t for t in placed
                           if t.get("outcome") not in ("win","loss","eod_win","eod_loss")])
        if n_candle_fail > 0:
            log.info(f"  Excluded {n_candle_fail} candle-fail trades from training")

        # ── v179: Manual exclusion filter ────────────────────────────────────
        # Trades tagged with `excluded_from_training=True` are skipped entirely.
        # Used for one-time data hygiene actions, e.g. excluding May 4 2026
        # which had bug-induced trades from cluster fix deployment churn.
        # Tag is set by exclude_date.py -- check that script's --reason field
        # to see why specific trades were excluded.
        _n_before_excl = len(train_placed)
        train_placed = [t for t in train_placed if not t.get("excluded_from_training", False)]
        _n_excluded = _n_before_excl - len(train_placed)
        if _n_excluded > 0:
            # Show breakdown by reason for transparency
            from collections import Counter as _Counter
            _reasons = _Counter()
            for t in placed:
                if t.get("excluded_from_training", False):
                    _reasons[t.get("excluded_reason", "?")] += 1
            _reason_str = ", ".join(f"{r}={n}" for r, n in _reasons.most_common())
            log.info(f"  Excluded {_n_excluded} manually-tagged trades from training ({_reason_str})")

        # ── Clean label filter ────────────────────────────────────────────────
        # Pre-v98 trades have corrupted quality labels (wrong MFE logic, binary
        # weights, incorrect outcome classification). Training on them creates
        # adversarial supervision: model sees contradictory truth definitions.
        # Institutional principle: clean small dataset >> large corrupted dataset.
        # We keep pre-cutoff trades ONLY as a fallback if clean data is too sparse.
        # ── v154: HYBRID LABEL STRATEGY ──────────────────────────────────────
        # Problem: only 40 clean trades (post-2026-04-07) -- far below the 100+ needed.
        # Old approach: fall back to ALL 3478 trades with contaminated quality labels.
        # New approach: split the dataset by cleanliness:
        #   POST-CUTOFF  (clean):   full quality-weighted labels + all weights active
        #   PRE-CUTOFF (tainted):   binary labels ONLY (quality=fallback), down-weighted 0.3x
        #                           Binary win/loss IS correct even before v98 -- only the
        #                           quality_label float and MFE/MAE features were wrong.
        # Result: ~3400 pre-cutoff trades contribute with reduced but non-zero influence.
        # This is equivalent to "coarse supervision" -- model learns setup patterns from
        # all history while trusting recent trades most for quality calibration.
        # v154 FIX: Run MFE imputation on all trades before training
        # Ensures every closed trade has mfe_r -> more T1 candidates
        _n_imputed = _impute_mfe_for_closed(placed)
        if _n_imputed > 0:
            log.info(f"  MFE imputed: {_n_imputed} closed trades now have mfe_r (mfe_imputed=True)")
            # Persist imputed values to disk so they survive restarts
            try:
                atomic_write(LOG_FILE, all_trades)
            except Exception as _aw_e:
                log.debug(f"MFE impute write error: {_aw_e}")

        n_before_cutoff = len(train_placed)
        train_clean = [t for t in train_placed
                       if t.get("timestamp", "") >= CLEAN_LABEL_CUTOFF_EFFECTIVE]
        train_legacy = [t for t in train_placed
                        if t.get("timestamp", "") < CLEAN_LABEL_CUTOFF_EFFECTIVE]

        # ── Session label remediation (applies to ALL trades) ─────────────────
        # Session bug (fixed v137): trades at 05-07 UTC got "london" label (wrong).
        # Correct before training so model doesn't learn false London->outcome pattern.
        _remediated = 0
        for _t in train_placed:
            try:
                _ts = _t.get("timestamp", "")
                _utc_h = int(_ts[11:13]) if len(_ts) >= 13 else -1
                _ctx = _t.get("context", {})
                if _utc_h in (5, 6, 7) and _ctx.get("session") == "london":
                    _ctx["session"] = "pre_london"
                    _t["context"]   = _ctx
                    _remediated += 1
            except Exception:
                pass
        if _remediated:
            log.info(f"  Session remediation: corrected {_remediated} pre-London mislabelled trades")

        n_corrupted = len(train_legacy)
        n_clean     = len(train_clean)

        # v191: GRADIENT TRANSITION (ported from v189) instead of hard cutoff at
        # n_clean >= 100. The old behavior dropped the dataset from 575 -> 100
        # trades the moment we crossed 100 clean labels. That cliff caused a real
        # session loss (May 12: -$238 on 0% WR after May 11 retrain shrunk to 100
        # clean trades). The fix: keep legacy trades for training until clean
        # data accumulates fully, with their weight scaled down gradually as
        # n_clean grows. Actual down-weighting happens in _hybrid_tier() below.
        #
        # Schedule:
        #   n_clean   <100:   T3 legacy weight = 0.50x  (need legacy badly)
        #   n_clean 100-200:  T3 legacy weight = 0.30x  (clean dominant, legacy helps)
        #   n_clean 200-300:  T3 legacy weight = 0.15x  (legacy minor contributor)
        #   n_clean   >=300:  T3 legacy weight = 0.00x  (clean-only, full transition)
        #
        # Always go through HYBRID mode now. The hard-cutoff branch is removed.
        if n_corrupted > 0:
            # HYBRID MODE: use all trades but with two-tier labelling
            # Pre-cutoff trades: quality_label forced to binary fallback (not MFE-based)
            # This prevents bad MFE/MAE values from poisoning the quality weights
            # while still allowing the binary outcome signal to train setup patterns.
            _hybrid_zeroed = 0
            for _t in train_legacy:
                _ctx = _t.get("context", {})
                _ctx.pop("mfe_r", None); _ctx.pop("mae_r", None)
                _ctx.pop("tp_reach_pct", None); _ctx.pop("tp_clean_hit", None)
                _t["context"] = _ctx
                _hybrid_zeroed += 1
            # Compute legacy weight from gradient schedule
            if   n_clean >= 300: _legacy_w = 0.00
            elif n_clean >= 200: _legacy_w = 0.15
            elif n_clean >= 100: _legacy_w = 0.30
            else:                _legacy_w = 0.50
            log.warning(
                f"  GRADIENT HYBRID MODE: {n_clean} T1-clean + {n_corrupted} legacy "
                f"(legacy weight={_legacy_w:.2f}x based on n_clean={n_clean})"
            )
            # Strip legacy trades entirely if their weight is 0 (transition complete)
            if _legacy_w == 0.0:
                train_placed = train_clean
                log.info(f"  Label cutoff: n_clean={n_clean} >= 300 -- legacy excluded entirely")
            _hybrid_mode = True
        else:
            _hybrid_mode = False
            _legacy_w = 0.0
        # Store hybrid mode so weight block can log it
        online_retrain._hybrid_mode_active = _hybrid_mode
        # If n_corrupted == 0 all trades are already post-cutoff -- nothing to do

        X_all  = np.array([build_feature_vector(t) for t in train_placed])
        # Quality-weighted labels: float target capturing trade cleanness
        # Falls back to binary 0/1 for old trades without MFE/MAE data
        y_all_q = np.array([_ml_quality_label(t) for t in train_placed])
        y_all   = np.array([1 if _ml_outcome(t) == "win" else 0 for t in train_placed])
        # Quality labels -> WEIGHTS ONLY, not classifier targets.
        # GradientBoostingClassifier needs discrete 0/1 targets.
        # Quality labels [-1..+1] are continuous -> "Unknown label type" error.
        #
        # Design: y_train = binary 0/1 (what happened)
        #         w_quality = continuous weight (how clean/informative the trade was)
        # The asymmetric quality weights already encode quality into gradient strength.
        # This is cleaner: labels = outcome, weights = signal quality.
        has_mfe = np.array([t.get("context",{}).get("mfe_r") is not None
                            for t in train_placed])
        pct_quality = has_mfe.sum() / max(len(has_mfe), 1) * 100
        # y_train is binary (classifier-compatible): 1=win, 0=loss
        y_train = y_all.astype(int)  # strict binary -- quality encoded via weights below
        # Validate label distribution -- catch instability early
        # Log y_all_q (continuous quality scores) not y_train (binary classifier targets)
        # y_train is always [0,1] -- that's correct. y_all_q shows actual quality distribution.
        _q_valid = y_all_q[y_all_q != 0]  # exclude 0.0 (neutral/fallback wins treated as 0 by fallback)
        q_mean = float(np.mean(y_all_q))
        q_std  = float(np.std(y_all_q))
        q_min  = float(np.min(y_all_q))
        q_max  = float(np.max(y_all_q))
        n_neg  = int((y_all_q < 0).sum())
        n_pos  = int((y_all_q > 0).sum())
        # Decision quality audit -- how well does ML score predict outcomes?
        # If working correctly: winners should have higher avg ML score than losers
        # Pre-initialise separation vars -- exist even if computation raises early
        _sep_overall_val = -1.0
        _sep_recent_val  = -1.0
        try:
            ml_scores_w = [t.get("context",{}).get("ml_win_prob",0) or 0
                           for t in train_placed if _ml_outcome(t) == "win"
                           and t.get("context",{}).get("ml_win_prob")]
            ml_scores_l = [t.get("context",{}).get("ml_win_prob",0) or 0
                           for t in train_placed if _ml_outcome(t) == "loss"
                           and t.get("context",{}).get("ml_win_prob")]
            if ml_scores_w and ml_scores_l:
                avg_w = sum(ml_scores_w)/len(ml_scores_w)
                avg_l = sum(ml_scores_l)/len(ml_scores_l)
                sep = avg_w - avg_l
                status = "GOOD" if sep > 0.05 else ("WEAK" if sep > 0 else "INVERTED!")
                log.info(f"  ML decision quality: winners avg={avg_w:.2%} losers avg={avg_l:.2%} "
                         f"separation={sep:+.2%} [{status}]")
                # Store in ensemble so hardened save logic can use it
                # NOTE: stored into local variables here -- added to ensemble dict below
                # (ensemble dict doesn't exist yet at this point in the function)
                _sep_overall_val = round(sep, 4)

                # Recent separation (last 50 resolved trades only)
                # Use placed (not train_placed) -- train_placed excludes 10-day holdout,
                # so train_placed[-50:] would show trades from 10-14 days ago, not recent
                _recent_placed = [t for t in placed
                                  if t.get("context", {}).get("ml_win_prob")][-50:]
                _rw = [t["context"]["ml_win_prob"] for t in _recent_placed
                       if _ml_outcome(t) == "win"]
                _rl = [t["context"]["ml_win_prob"] for t in _recent_placed
                       if _ml_outcome(t) == "loss"]
                if _rw and _rl:
                    _rsep = sum(_rw)/len(_rw) - sum(_rl)/len(_rl)
                    _sep_recent_val = round(_rsep, 4)  # stored into ensemble dict below
                    log.info(f"  Recent 50 separation: {_rsep:+.2%}")
        except Exception as _sep_e:
            log.debug(f"Separation calc error: {_sep_e}")

        # ── Decision quality metric ───────────────────────────────────────────
        try:
            _real_res = [t for t in placed
                         if t.get("outcome") in ("win","loss","eod_win","eod_loss")
                         and not t.get("random", False)
                         and (t.get("risk_pct") or 0) >= 0.02]
            if len(_real_res) >= 20:
                _ovr_wr  = sum(1 for t in _real_res if t["outcome"] in ("win","eod_win")) / len(_real_res)
                _thresh  = ML_MIN_ENTRY_PROB - 0.05
                _allowed = [t for t in _real_res
                            if (t.get("context",{}).get("ml_win_prob") or 0) >= _thresh]
                _blocked = [t for t in _real_res
                            if 0 < (t.get("context",{}).get("ml_win_prob") or 0) < _thresh]
                _all_wr  = (sum(1 for t in _allowed if t["outcome"] in ("win","eod_win"))
                            / max(len(_allowed), 1))
                _blk_wr  = (sum(1 for t in _blocked if t["outcome"] in ("win","eod_win"))
                            / max(len(_blocked), 1))
                # v200 audit fix: the old metric compared allowed-WR against an
                # "overall" that included trades with NO ml_win_prob (default/0),
                # so the three numbers never reconciled (e.g. 53% overall but a
                # 48%/37% allowed/blocked split that weight-averages to ~47%).
                # The only honest "does the filter help?" contrast is allowed vs
                # blocked over the SAME scored population. We also refuse a verdict
                # unless both buckets have enough samples to mean anything.
                _scored_n = len(_allowed) + len(_blocked)
                _delta   = _all_wr - _blk_wr   # filter helps iff allowed beats blocked
                if len(_allowed) >= 20 and len(_blocked) >= 20:
                    _dq_status = ("FILTERING HELPS" if _delta > 0.02
                                  else ("NEUTRAL" if _delta > -0.02 else "FILTERING HURTS"))
                else:
                    _dq_status = f"INSUFFICIENT (allowed={len(_allowed)} blocked={len(_blocked)})"
                log.info(f"  ML DECISION QUALITY: overall={_ovr_wr:.0%}(n={len(_real_res)}) "
                         f"allowed={_all_wr:.0%}(n={len(_allowed)}) "
                         f"blocked={_blk_wr:.0%}(n={len(_blocked)}) "
                         f"allowed-vs-blocked delta={_delta:+.0%} -- {_dq_status}")
                ensemble["ml_allowed_wr"]     = round(_all_wr, 3)
                ensemble["ml_blocked_wr"]     = round(_blk_wr, 3)
                ensemble["ml_decision_delta"] = round(_delta, 3)
        except Exception as _dqe:
            log.debug(f"Decision quality metric error: {_dqe}")
        except Exception as _dq_e:
            log.debug(f"Decision quality audit: {_dq_e}")

        log.info(f"  Quality labels: {has_mfe.sum()}/{len(has_mfe)} with MFE ({pct_quality:.0f}%)"
                 f" | mean={q_mean:.3f} std={q_std:.3f} range=[{q_min:.2f},{q_max:.2f}]"
                 f" | pos={n_pos} neg={n_neg}")
        # y_train is binary -- validate it separately
        wr = float(y_train.mean())
        log.info(f"  Binary labels: WR={wr:.0%} ({int(y_train.sum())}W/{int((1-y_train).sum())}L)")
        if q_std < 0.05:
            log.warning("  Quality std < 0.05 -- weights nearly uniform, quality signal weak")
        if n_neg == 0:
            log.warning("  No negative quality labels -- losses not represented in quality weights")

        # ── Confidence-weighted training ──────────────────────────────────────
        # Trades with strong signal (clear win or clear loss) influence model more.
        # Marginal trades (scraped wins, teaser losses) have lower weight.
        # weight = f(|quality_label|): clean = 2.0x, marginal = 0.3x
        # Combined with existing _tw() completion weight (random=0.5x, old=0.7x, new=1.5x).
        def _quality_weight(q):
            """Asymmetric quality weight -- wins weighted much higher than losses,
            but losses preserve structure (clean loss > noisy loss).
            
            Wins dominate learning (there are few consistent edges).
            Losses contribute lightly (there are infinite failure modes).
            But structured losses teach setup-specific failure modes.
            
            Weight table:
              +1.0 (clean win)   -> 2.0   clean trend to TP
              +0.5 (scraped win) -> 1.15  barely hit TP
              +0.1 (marginal)    -> 0.47  lucky scrape
               0.0 (neutral)     -> 0.30  floor
              -0.5 (teaser loss) -> 0.35  got close to TP, then reversed
              -1.0 (clean loss)  -> 0.50  straight to SL -- clear failure signal
            """
            if q >= 0:
                # Wins: linear 0.30 -> 2.0
                return float(np.clip(0.3 + 1.7 * q, 0.3, 2.0))
            else:
                # Losses: graded 0.20 -> 0.50 -- preserves structure without dominating
                # Teaser losses (label ≈ -0.5) slightly below neutral (0.30)
                # because chop/reversal after near-TP is more noise than signal.
                # Clean losses (label = -1.0) informative: 0.50
                raw = 0.2 + 0.3 * min(1.0, abs(q))
                # Cap teaser zone to stay at or below neutral baseline
                if abs(q) < 0.6:
                    raw = min(raw, 0.29)
                return float(raw)
        w_quality = np.array([_quality_weight(q) for q in y_all_q])  # uses continuous quality labels [-1..+1] for granular weights
        # Combine with completeness weight (already computed in w_all)
        # Final weight = quality_weight * completeness_weight
        # This gives: clean new trade = 2.0 * 1.5 = 3.0 (max influence)
        #             random marginal old = 0.2 * 0.5 = 0.1 (near-zero influence)
        # Weight by feature completeness to reduce NaN era leakage:
        # New trades (have Hurst = proxy for all new features) = 1.5x
        # Old trades (no new features, lots of NaN) = 0.7x
        # Random trades = 0.5x regardless

        def _tw(t):
            # random=True trades excluded from placed before training -- never reach here
            # Weight by feature completeness:
            # New trades (have candle_is_green = post-v66) = 1.5x
            # Old trades (pre-v66, missing 51 new features) = 0.7x
            # candle_is_green is a good proxy -- only set in new trades
            return 1.5 if t.get("context",{}).get("candle_is_green") is not None else 0.7
        import math as _math
        _now_ts = _dt.now(_tz.utc)
        def _age_weight(t, half_life_days=21):  # demo: 21d window -> 21d half-life
            """Exponential temporal decay -- recent trades weighted higher.
            half_life=14: trade 14 days ago = 0.5x weight of today's trade.
            Prevents old regime patterns from dominating current predictions.
            """
            try:
                ts_str = t.get("timestamp", "")
                if not ts_str:
                    return 0.5  # unknown age -- moderate weight
                ts = _dt.strptime(ts_str[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=_tz.utc)
                age_days = (_now_ts - ts).total_seconds() / 86400.0
                return float(_math.exp(-age_days * _math.log(2) / half_life_days))
            except Exception:
                return 0.5

        w_all  = np.array([_tw(t) for t in train_placed])  # completeness weights

        # 5 models with TIME-BASED windows -- not count-based
        # This prevents clustering: 500 micro trades in 1 hour no longer
        # dominate a "recent_30" window. Each window spans real calendar time.
        #
        # Window definitions:
        #   last_2days  = trades from last 2 calendar days
        #   last_5days  = trades from last 5 calendar days
        #   last_10days = trades from last 10 calendar days
        #   last_3days  = trades from last 3 calendar days
        #   all         = full history (unchanged)
        #
        # Minimum 20 trades required per window -- falls back to count-based
        # if not enough time has passed to fill the window.

        # Build a set of holdout timestamps for fast exclusion
        _holdout_keys = set(
            t.get("timestamp","") + str(t.get("symbol",""))
            for t in placed if t.get("timestamp","") >= holdout_cutoff
        )

        def _time_window(trades_list, days):
            """Get trades from last N calendar days for window model training.

            Design principle: window models need RECENT data to be temporally
            diverse. The Turing holdout tests all models (including window models)
            independently -- window models do NOT need to exclude their own training
            data from the holdout. That is the Turing test's job.

            Exclusions applied:
              - platt_val_ts: excluded so window models never train on Platt
                calibration trades (preserves "unseen" property of calibration)
              - holdout_keys: NOT excluded here -- removing the holdout from
                recent windows leaves them empty (10-day holdout + 2-day window
                has zero overlap) and collapses all windows to the same April 10
                fallback slice, destroying temporal diversity entirely.

            The global "all" model (train_placed) still excludes both holdout
            and platt_val -- it is the reference model that Turing tests against.
            Window models supplement it with recency signal.
            """
            _key = lambda t: t.get("timestamp","") + str(t.get("symbol",""))
            cutoff = (_dt.now(_tz.utc) - _td(days=days)).strftime("%Y-%m-%d %H:%M:%S")
            subset = [t for t in trades_list if t.get("timestamp","") >= cutoff]
            # Remove Platt validation trades -- preserve calibration integrity
            # Do NOT remove holdout trades -- window models need them for recency
            subset = [t for t in subset if _key(t) not in platt_val_ts]
            # Fallback to count-based if not enough data
            if len(subset) < 20:
                count = days * 30  # rough estimate: 30 trades per day
                base = [t for t in trades_list if _key(t) not in platt_val_ts]
                subset = base[-count:] if len(base) >= count else base
            return subset

        windows = {
            "all":         train_placed,                    # already excludes holdout
            "last_2days":  _time_window(placed, 2),        # use full placed, not train_placed
            "last_5days":  _time_window(placed, 5),
            "last_10days": _time_window(placed, 10),
            "last_3days":  _time_window(placed, 3),
        }

        # Log what each window actually covers
        for wname, wdata in windows.items():
            if wdata and wname != "all":
                ts_list = [t.get("timestamp","") for t in wdata if t.get("timestamp")]
                if ts_list:
                    span = f"{min(ts_list)[:10]} to {max(ts_list)[:10]}"
                    log.info(f"  Window {wname}: {len(wdata)} trades ({span})")

        # ── Option B: Per-symbol time-window ensemble ─────────────────────
        # Each symbol trains its own set of models independently.
        # This prevents GER40 (28% WR) from poisoning US30 (96% WR) patterns.
        # Architecture: 4 symbols × up to 3 windows = up to 12 symbol-window models
        #               + 1 global "all" model for cross-symbol context signals
        # Minimum 20 trades per window per symbol -- skip if not enough data yet.
        # As trades accumulate, more windows activate automatically.

        models = {}       # global models (window name -> model)
        aucs   = {}
        symbol_models = {}  # symbol-specific models (sym|window -> model)
        symbol_aucs   = {}

        # ── Drop permanently dead features BEFORE fitting ─────────────────
        # Build full X to identify features that are always NaN (broken features).
        # These cause silent sklearn imputer warnings and waste model capacity.
        # Professional standard: drop any feature that's null > 95% of the time.
        # v156: ALSO drop features with <1% variance (constants in disguise) and
        # features with <0.1% importance from the previous pkl. With 332 features
        # and ~3k samples, the bias-variance balance is firmly in overfit territory
        # (target ratio is samples/features > 50; we are at ~9). Pruning hard.
        try:
            import warnings as _w
            _w.filterwarnings("ignore", category=UserWarning, module="sklearn")
            _X_probe = np.array([build_feature_vector(t) for t in train_placed])
            _non_null = np.mean(~np.isnan(_X_probe), axis=0)

            # v156: variance-based pruning -- features that barely vary teach nothing
            # and just take up model-capacity budget.
            try:
                _variance = np.nanvar(_X_probe, axis=0)
                _var_floor = max(1e-6, np.nanmedian(_variance) * 0.001)  # 0.1% of median variance
                _low_var_mask = _variance < _var_floor
            except Exception:
                _low_var_mask = np.zeros(_X_probe.shape[1], dtype=bool)

            # v156: low-importance pruning from previous pkl (if available)
            # IMPORTANT: previous v155 pkl's feature_importance_avg keys are post-
            # col_filter indices (relative to whichever cols survived the dead-feature
            # check that day). They don't reliably map to current original-column
            # indices. Only apply this prune when prev pkl was saved by v156+ which
            # stores the importance against ORIGINAL column indices.
            _low_imp_mask = np.zeros(_X_probe.shape[1], dtype=bool)
            try:
                if os.path.exists("ml_model.pkl"):
                    with open("ml_model.pkl", "rb") as _pf2:
                        _prev_pkl = pickle.load(_pf2)
                    _prev_version = _prev_pkl.get("training_version", "")
                    _prev_fi = _prev_pkl.get("feature_importance_orig_idx", {})
                    # v161: simpler accept-any-v156-format check via tuple
                    _compatible_versions = ("v156", "v157", "v158", "v159", "v160", "v161", "v162", "v163", "v164", "v165", "v166", "v167", "v168", "v169", "v170", "v171", "v172", "v173", "v174", "v175", "v176", "v177", "v178", "v179", "v180", "v181", "v182", "v183", "v184", "v185", "v186", "v187", "v188", "v189", "v190", "v191", "v192", "v193", "v194", "v195", "v196", "v197")
                    if _prev_fi and _prev_version.startswith(_compatible_versions):
                        _expected_n = _X_probe.shape[1]
                        for _k_str, _v in _prev_fi.items():
                            try:
                                _k = int(_k_str)
                                if _k < _expected_n and _v < 0.001:
                                    _low_imp_mask[_k] = True
                            except (ValueError, TypeError):
                                pass
            except Exception as _imp_e:
                log.debug(f"Low-importance prune skipped: {_imp_e}")

            _dead_mask = _non_null < 0.05
            # Combined drop: dead OR low-variance OR low-importance from prev model
            _drop_mask = _dead_mask | _low_var_mask | _low_imp_mask
            _good_cols = np.where(~_drop_mask)[0]
            _n_dead = int(_dead_mask.sum())
            if len(_good_cols) < _X_probe.shape[1]:
                log.info(
                    f"  Feature prune: kept {len(_good_cols)}/{_X_probe.shape[1]} "
                    f"(dropped {_n_dead} dead, {int(_low_var_mask.sum())} low-var, "
                    f"{int(_low_imp_mask.sum())} low-imp)"
                )
                _col_filter = _good_cols
            else:
                _col_filter = None
                log.info(f"  Feature health OK: all {_X_probe.shape[1]} features have data")
        except Exception as _fe:
            log.warning(f"Dead-feature check error: {_fe}")
            _col_filter = None

        # Global "all" model -- still useful for cross-symbol features
        # (pairs_converging, correlation signals, session patterns)
        X_all2 = np.array([build_feature_vector(t) for t in train_placed])
        if _col_filter is not None:
            X_all2 = X_all2[:, _col_filter]
        y_all2 = y_train   # binary 0/1 (quality encoded in w_all2 weights)
        w_all2_base  = np.array([_tw(t) for t in train_placed])
        w_all2_decay = np.array([_age_weight(t) for t in train_placed])
        # v152: risk-weighted training -- bigger trades matter more for P&L
        _risk_weights = np.array([
            max(0.1, min(4.0, (t.get("risk_pct") or 0.015) / 0.25))
            for t in train_placed
        ])
        # v154: class-balanced weights (from live bot v146/v147 -- prevents ML inversion)
        # GradientBoosting has no class_weight -- compensate via sample_weight
        # Minority class (losses) upweighted so model learns what losing looks like
        _y_for_bal  = np.array([1 if _ml_outcome(t) == "win" else 0 for t in train_placed])
        _n_pos_bal  = max(1, int(_y_for_bal.sum()))
        _n_neg_bal  = max(1, int(len(_y_for_bal) - _n_pos_bal))
        _n_tot_bal  = len(_y_for_bal)
        _class_w    = np.where(_y_for_bal == 1,
                               _n_tot_bal / (2.0 * _n_pos_bal),   # wins: down if majority
                               _n_tot_bal / (2.0 * _n_neg_bal))   # losses: up if minority
        _class_w    = np.clip(_class_w, 0.2, 5.0)
        _global_wr  = _n_pos_bal / max(1, _n_tot_bal)
        log.info(f"  Class balance: {_n_pos_bal}W/{_n_neg_bal}L -> win_w={_n_tot_bal/(2.0*_n_pos_bal):.2f} loss_w={_n_tot_bal/(2.0*_n_neg_bal):.2f}")
        if _global_wr > 0.80:
            log.warning(f"  HIGH WIN RATE WARNING: {_global_wr:.0%} WR in training -- ML inversion risk")
        if _global_wr > 0.90:
            log.warning(f"  CRITICAL: {_global_wr:.0%} WR -- extreme imbalance, class weights at max 5x")

        # v154 FIXED: Three-tier hybrid weights -- prevents orphan-repaired trades
        # from claiming full quality weight they haven't earned.
        #
        # TIER 1 -- Genuine clean (1.0x):
        #   post-cutoff + enrichment_ok=1 + has mfe_r (quality label is real)
        #   These are the most valuable -- model was live when trade resolved
        #
        # TIER 2 -- Repaired/binary-only (0.50x):
        #   post-cutoff BUT no mfe_r (orphan-repaired from M1 price, no context)
        #   OR pre-cutoff + enriched (1m features but binary labels only)
        #   Contributes outcome signal but quality label is fallback only
        #
        # TIER 3 -- Legacy unverified (v191: gradient weight):
        #   pre-cutoff + no enrichment (old candle-fail trades, zero features)
        #   Weight now scales with n_clean (computed in cutoff block above):
        #     <100 clean: 0.50x | 100-200: 0.30x | 200-300: 0.15x | >=300: 0.00x
        _cutoff_eff = CLEAN_LABEL_CUTOFF_EFFECTIVE
        _legacy_w_local = _legacy_w if _hybrid_mode else 0.15
        def _hybrid_tier(t):
            ts      = t.get("timestamp", "")
            ctx     = t.get("context", {}) or {}
            is_post = ts >= _cutoff_eff
            has_mfe = ctx.get("mfe_r") is not None
            enr_ok  = ctx.get("enrichment_ok", 0) == 1
            imputed = ctx.get("mfe_imputed", False)  # imputed from TP/SL geometry
            if t.get("cluster_split", False):
                return 0.25  # cluster-tier -- kept for signal but heavily discounted
            if is_post and has_mfe and enr_ok and not imputed:
                return 1.00  # Tier 1: genuine real MFE + enrichment + post-cutoff
            elif is_post and has_mfe and enr_ok and imputed:
                return 0.75  # Tier 1.5: imputed MFE (outcome-derived) + enrichment
            elif is_post or enr_ok:
                return 0.50  # Tier 2: post-cutoff but binary-only (no mfe at all)
            else:
                return _legacy_w_local  # Tier 3 (v191): gradient -- see schedule above
        _hybrid_w = np.array([_hybrid_tier(t) for t in train_placed])
        n_t1  = int((_hybrid_w >= 0.99).sum())
        n_t15 = int(((_hybrid_w >= 0.74) & (_hybrid_w < 0.99)).sum())
        n_t2  = int(((_hybrid_w >= 0.49) & (_hybrid_w < 0.74)).sum())
        n_cluster = int(((_hybrid_w >= 0.24) & (_hybrid_w < 0.26)).sum())  # exactly 0.25
        n_t3  = int((_hybrid_w < 0.24).sum())
        log.info(f"  Hybrid weights: {n_t1} T1(1.0x) + {n_t15} T1.5-imputed(0.75x) + "
                 f"{n_t2} T2-binary(0.5x) + {n_cluster} cluster(0.25x) + "
                 f"{n_t3} T3-legacy({_legacy_w_local:.2f}x)")

        # v156: SIMPLIFIED WEIGHT SCHEME.
        # Was: w_base * w_quality * w_decay * w_risk * w_hybrid * w_class
        #      Six multiplicative weights with 60x range (min=0.019 max=1.193 in report25).
        #      Compound multiplication of independent uncertain weights = unstable training
        #      signal. Each weight individually is sensible; the product is not.
        #
        # Now: w_data_quality * w_recency * w_class_balance
        #   - data_quality = hybrid_tier × completeness × quality_label  (collapsed)
        #     covers: how trustworthy is this trade's labels and features
        #   - recency = age-decay only
        #     covers: how relevant is this trade to current regime
        #   - class_balance = compensation for label imbalance
        #     covers: ensures model sees losses, not just wins
        #
        # Risk-pct weighting REMOVED -- high-risk trades are more important for P&L
        # but training a CLASSIFIER on P&L weighting biases the model toward setups
        # that happened to have larger position sizing rather than what predicts
        # outcomes. The ranking task is the same regardless of position size.
        _data_quality_w = w_all2_base * w_quality * _hybrid_w
        # Clip individual data quality before multiplying by recency/class
        # so a single near-zero factor can't kill a sample entirely
        _data_quality_w = np.clip(_data_quality_w, 0.05, 3.0)

        w_all2 = _data_quality_w * w_all2_decay * _class_w
        # Final clamp: 0.05 floor (sample never fully ignored), 5.0 ceiling
        w_all2 = np.clip(w_all2, 0.05, 5.0)
        _wp = np.percentile(w_all2, [10, 50, 90])
        log.info(f"  Training weights (v156 simplified): mean={w_all2.mean():.3f} "
                 f"p10={_wp[0]:.3f} p50={_wp[1]:.3f} p90={_wp[2]:.3f} "
                 f"min={w_all2.min():.3f} max={w_all2.max():.3f}")
        # Flag pathological distributions
        if _wp[1] < 0.10:
            log.warning("  Weight p50 < 0.10 -- most training data nearly ignored")
        if w_all2.mean() > 1.5:
            log.warning(f"  Weight mean={w_all2.mean():.2f} > 1.5 -- weights too aggressive")
        if _wp[2] >= w_all2.max() * 0.99:
            log.warning("  Weight p90 ≈ max -- many extreme outlier weights")
        # ── Confidence gate ────────────────────────────────────────────────
        # Remove samples with combined weight < 0.15 -- these contribute noise.
        # Very old random losses, candle-fail residuals, etc.
        _gate_thresh   = 0.08
        _gate_mask   = w_all2 >= _gate_thresh
        if _gate_mask.sum() < 30:
            log.warning(f"  Confidence gate: would leave {_gate_mask.sum()} samples -- skipping gate")
        else:
            _n_gated = len(w_all2) - int(_gate_mask.sum())
            if _n_gated > 0:
                pct_gated = _n_gated / max(len(w_all2), 1) * 100
                log.info(f"  Confidence gate: removed {_n_gated} samples ({pct_gated:.0f}% noise-floor trades)")
                X_all2 = X_all2[_gate_mask]
                y_all2 = y_all2[_gate_mask]
                w_all2 = w_all2[_gate_mask]

        # y_all2 is already binary -- use directly for AUC
        y_all2_bin = y_all2
        if len(set(y_all2_bin)) > 1 and len(train_placed) >= 30:
            # v156: regularized model -- was overfitting with depth=4 on ~3k trades.
            # Sample-to-feature ratio is ~9:1 (3000 trades / 332 features) which is
            # well into overfit territory (rule of thumb is 50:1+). Compensate with
            # shallower trees, more leaf samples, lower learning rate, more subsample
            # randomization. Even after feature pruning ratio is still <30:1.
            _n_train = len(train_placed)
            _n_estim = (60 if _n_train >= 500 else 35 if _n_train >= 200 else 20)
            _max_dep = (3 if _n_train >= 500 else 2)  # was 4/3/2 -- capped at 3
            _min_leaf = max(10, _n_train // 60)        # bigger leaves = less overfit
            _lr       = 0.03                           # was 0.05 -- slower learning
            _sub      = 0.7                            # was 0.8 -- more bagging noise
            m_global = Pipeline([
                ("imp", SimpleImputer(strategy="median")),
                ("clf", GradientBoostingClassifier(
                    n_estimators=_n_estim, max_depth=_max_dep,
                    min_samples_leaf=_min_leaf, learning_rate=_lr,
                    random_state=42, subsample=_sub,
                    max_features="sqrt"))   # v156: random feature subset per split -- dropout-like
            ])
            log.info(f"  Global model: n_est={_n_estim} depth={_max_dep} leaf={_min_leaf} lr={_lr} sub={_sub}")
            try:
                cv_g = StratifiedKFold(n_splits=min(5, len(set(y_all2_bin))), shuffle=True, random_state=42)
                sc_g = cross_val_score(m_global, X_all2, y_all2_bin, cv=cv_g, scoring="roc_auc")
                aucs["all"] = float(sc_g.mean())
            except Exception as _cv_err:
                log.warning(f"  Global AUC cross-val failed: {_cv_err} -- using 0.5")
                aucs["all"] = 0.5
            m_global.fit(X_all2, y_all2, clf__sample_weight=w_all2)
            models["all"] = m_global

        # Per-symbol models with auto-expanding time windows
        # Windows activate automatically as data grows -- no manual action needed
        # Each window needs min 50 trades per symbol to activate
        # More data = more windows = better ensemble coverage
        # NOTE: _time_window now uses placed (full set) internally, excludes holdout
        # v156: dropped 2-day and 3-day windows. With ~50-100 trades per symbol per
        # 2 days and 332 features, those models were pure noise fitting and dragged
        # the ensemble's separation toward zero. Keep "all" (long-term context) and
        # "last_10days" (recent-regime adaptation). Two windows is enough -- more
        # adds variance without information gain in this data regime.
        sym_window_defs = {
            "all":         train_placed,               # global ref: excludes holdout + platt_val
            "last_10days": _time_window(placed, 10),  # recent: excludes only platt_val (not holdout)
        }

        # v178: only train symbol models for symbols actually traded in production.
        # Was hardcoded ["GER40.cash", "US30.cash", "US100.cash", "UK100.cash"];
        # now uses ALL_SYMBOLS. With placed[] also filtered above, GER40/UK100
        # contribute nothing -- they would have hit the <50 trades skip below anyway,
        # but the explicit filter is clearer.
        for sym in ALL_SYMBOLS:
            sym_all_trades = [t for t in train_placed if t.get("symbol") == sym]
            if len(sym_all_trades) < 50:  # minimum for meaningful symbol model
                continue
            best_auc = 0.5
            for wname, wdata in sym_window_defs.items():
                sym_trades = [t for t in wdata if t.get("symbol") == sym]
                if len(sym_trades) < 50:  # minimum 50 for reliable model (was 20)
                    continue
                X_s = np.array([build_feature_vector(t) for t in sym_trades])
                if _col_filter is not None:
                    X_s = X_s[:, _col_filter]
                # Quality-weighted labels for symbol models too
                y_s_q = np.array([_ml_quality_label(t) for t in sym_trades])
                y_s_b = np.array([1 if _ml_outcome(t) == "win" else 0 for t in sym_trades])
                y_s = y_s_b.astype(int)  # binary -- quality in weights
                w_s_base  = np.array([_tw(t) for t in sym_trades])
                w_s_qual  = np.array([_quality_weight(q) for q in y_s_q])  # continuous quality not binary
                w_s_decay = np.array([_age_weight(t) for t in sym_trades])
                _w_s_risk = np.array([
                    max(0.1, min(4.0, (t.get("risk_pct") or 0.015) / 0.25))
                    for t in sym_trades
                ])
                # v154 FIXED: Three-tier hybrid for symbol models (same logic as global)
                _w_s_hybrid = np.array([_hybrid_tier(t) for t in sym_trades])
                _y_s_bal   = np.array([1 if _ml_outcome(t)=="win" else 0 for t in sym_trades])
                _n_pos_s   = max(1, int(_y_s_bal.sum()))
                _n_neg_s   = max(1, int(len(_y_s_bal)-_n_pos_s))
                _class_w_s = np.where(_y_s_bal==1,
                                      len(_y_s_bal)/(2.0*_n_pos_s),
                                      len(_y_s_bal)/(2.0*_n_neg_s))
                _class_w_s = np.clip(_class_w_s, 0.2, 5.0)
                # v156: same simplification as global model -- collapse to 3 weights
                _data_q_s = np.clip(w_s_base * w_s_qual * _w_s_hybrid, 0.05, 3.0)
                w_s = _data_q_s * w_s_decay * _class_w_s
                w_s = np.clip(w_s, 0.05, 5.0)
                if len(set(y_s_b)) < 2:
                    continue
                # v152: skip windows with >90% one class -- model can't learn without minority class
                _wr_s = y_s_b.mean()
                if _wr_s > 0.90 or _wr_s < 0.10:
                    log.warning(f"  Symbol model {sym}|{wname}: WR={_wr_s:.0%} -- extreme imbalance, skipping")
                    continue
                # Scale symbol model complexity to sample size
                # v156: tighter caps -- symbol models on small data overfit hard.
                _ns = len(sym_trades)
                _ne_s = 50 if _ns >= 200 else (30 if _ns >= 100 else 20)
                _nd_s = 2  # always depth 2 for symbol models (small data)
                _msl_s = max(8, _ns // 12)  # bigger leaves than v155
                m = Pipeline([
                    ("imp", SimpleImputer(strategy="median")),
                    ("clf", GradientBoostingClassifier(
                        n_estimators=_ne_s, max_depth=_nd_s,
                        min_samples_leaf=_msl_s, learning_rate=0.03,
                        random_state=42, subsample=0.7,
                        max_features="sqrt"))
                ])
                # v154: WR diversity gate -- skip if >90% one class (would memorize)
                _sym_wr_pct = float(y_s_b.mean()) if len(y_s_b) > 0 else 0.5
                if _sym_wr_pct > 0.90 or _sym_wr_pct < 0.10:
                    log.info(f"  Symbol model {sym}|{wname}: skipped -- WR={_sym_wr_pct:.0%} (>90% one class)")
                    continue
                try:
                    if len(set(y_s_b.tolist())) < 2 or len(y_s) < 20:
                        auc_s = 0.5
                    else:
                        import warnings as _w
                        with _w.catch_warnings():
                            _w.simplefilter("ignore")  # suppress FitFailedWarning on small folds
                            cv_s = StratifiedKFold(n_splits=min(5, max(3, len(y_s)//20)),
                                                   shuffle=True, random_state=42)
                            sc = cross_val_score(m, X_s, y_s_b, cv=cv_s, scoring="roc_auc")
                        auc_s = float(np.nan_to_num(sc, nan=0.5).mean())
                except Exception as _cv_sym_err:
                    log.debug(f"  Symbol AUC cross-val failed ({sym}|{wname}): {_cv_sym_err}")
                    auc_s = 0.5
                m.fit(X_s, y_s, clf__sample_weight=w_s)
                key = f"{sym}|{wname}"
                # v152: reject AUC>=0.99 symbol models -- perfect AUC = memorization not learning
                if auc_s >= 0.99:
                    log.warning(f"  Symbol model {sym}|{wname}: AUC={auc_s:.3f} >= 0.99 -- REJECTED (memorized)")
                    continue
                # v198: reject AUC<0.52 symbol models -- below random = anti-predictive.
                # Two consecutive nights showed US100|last_10days at 0.395/0.429 -- when
                # averaged into ensemble, it dragged combined predictions toward wrong
                # direction, causing non-monotone calibration. Floor at 0.52 (just above
                # random) prevents this. Note: global model still trains on all symbols.
                if auc_s < 0.52:
                    log.warning(f"  Symbol model {sym}|{wname}: AUC={auc_s:.3f} < 0.52 -- REJECTED (anti-predictive)")
                    continue
                symbol_models[key] = m
                symbol_aucs[key]   = auc_s
                if wname == "all":
                    best_auc = auc_s
            if sym in [s.split("|")[0] for s in symbol_models]:
                log.info(f"  Symbol model {sym}: {len(sym_all_trades)} trades "
                        f"AUC={best_auc:.3f}")

        if not models and not symbol_models:
            return

        all_aucs = list(aucs.values()) + list(symbol_aucs.values())
        valid_aucs = [v for v in all_aucs if v == v and v > 0]
        avg_auc = sum(valid_aucs) / len(valid_aucs) if valid_aucs else float('nan')

        ensemble = {
            "models":        models,
            "aucs":          aucs,
            "symbol_models": symbol_models,
            "symbol_aucs":   symbol_aucs,
            "col_filter":    _col_filter.tolist() if _col_filter is not None else None,
            "symbol_n":      {                              # n resolved trades per symbol for weighting
                sym: sum(1 for t in placed if t.get("symbol") == sym)
                for sym in ALL_SYMBOLS  # v178: was hardcoded list including GER40/UK100
            },
            "trained_at":    datetime.now(timezone.utc).isoformat(),
            "training_version": "v178",  # marks pkl as v156-format-compatible for low-imp prune
            "n_resolved":    n_resolved,
            "avg_auc":       avg_auc,
            "n_features":    len(build_feature_vector(placed[0])),
            # Separation metrics -- computed above in decision quality audit block.
            # Stored here (not earlier) because ensemble dict didn't exist yet at
            # computation time. Old pkls missing these fields load with -1.0 fallback
            # via ensemble.get("separation_overall", -1.0) in the save gate below.
            "separation_overall": _sep_overall_val,  # pre-initialised to -1.0 before try block
            "separation_recent":  _sep_recent_val,   # pre-initialised to -1.0 before try block
        }

        # ── Feature importance audit ──────────────────────────────────────────
        # Aggregate importance across all models. Log bottom features for pruning.
        # Bottom features waste model capacity -- target: keep top ~100.
        try:
            all_importances = {}
            all_models_fi = {**models, **symbol_models}
            n_fi_models = 0
            for mname, mobj in all_models_fi.items():
                try:
                    fi = mobj.named_steps["clf"].feature_importances_
                    for i, imp in enumerate(fi):
                        all_importances[i] = all_importances.get(i, 0) + imp
                    n_fi_models += 1
                except Exception:
                    pass
            if n_fi_models > 0 and all_importances:
                for k in all_importances:
                    all_importances[k] /= n_fi_models
                total_imp = sum(all_importances.values())
                sorted_fi = sorted(all_importances.items(), key=lambda x: x[1])
                # Log bottom 10 by importance -- candidates for pruning
                bottom10 = sorted_fi[:10]
                bottom_pct = sum(v for _, v in bottom10) / total_imp * 100 if total_imp > 0 else 0
                log.info(f"  Feature audit: {len(all_importances)} features, "
                         f"bottom 10 account for {bottom_pct:.1f}% total importance")
                # Store aggregate importance for ml_report (post-filter indices)
                ensemble["feature_importance_avg"] = {
                    str(k): round(v / total_imp, 6) for k, v in all_importances.items()
                }
                # v156: ALSO store importance against ORIGINAL pre-filter column indices.
                # This lets next run's low-imp pruner identify which original columns
                # to drop without ambiguity. Mapping: post-filter idx i corresponds to
                # original idx _col_filter[i] (or i if no filter).
                if total_imp > 0:
                    if _col_filter is not None:
                        _orig_imp = {}
                        for k, v in all_importances.items():
                            if 0 <= k < len(_col_filter):
                                _orig_imp[str(int(_col_filter[k]))] = round(v / total_imp, 6)
                        ensemble["feature_importance_orig_idx"] = _orig_imp
                    else:
                        ensemble["feature_importance_orig_idx"] = {
                            str(k): round(v / total_imp, 6) for k, v in all_importances.items()
                        }
        except Exception as _fi_err:
            log.debug(f"Feature importance audit error: {_fi_err}")

        # ── ATR percentile regime feature ─────────────────────────────────────
        # Store trailing ATR percentile so the model can learn "this is a high-vol
        # regime" vs "this is a low-vol regime" explicitly, rather than inferring it.
        # Stored in ensemble so it's available at prediction time.
        try:
            all_atrs = [t.get("context", {}).get("atr_14", 0) or 0 for t in placed[-200:]]
            all_atrs = [a for a in all_atrs if a > 0]
            if len(all_atrs) >= 20:
                all_atrs.sort()
                ensemble["atr_p10"] = all_atrs[len(all_atrs)//10]
                ensemble["atr_p50"] = all_atrs[len(all_atrs)//2]
                ensemble["atr_p90"] = all_atrs[int(len(all_atrs)*0.9)]
                log.info(f"  ATR regime: p10={ensemble['atr_p10']:.1f} "
                         f"p50={ensemble['atr_p50']:.1f} p90={ensemble['atr_p90']:.1f}")
                # Extreme low-vol threshold: below p5 = market not moving
                all_atrs_s = sorted(all_atrs)
                ensemble["atr_p05"] = all_atrs_s[max(0, len(all_atrs_s)//20)]
        except Exception as _atr_err:
            log.debug(f"ATR percentile error: {_atr_err}")

        # Store current regime in pkl so dynamic threshold can access it
        try:
            from collections import Counter as _Counter
            _recent_regimes = [t.get("context", {}).get("macro_regime", "ranging")
                               for t in placed[-20:] if t.get("context")]
            if _recent_regimes:
                ensemble["last_regime"] = _Counter(_recent_regimes).most_common(1)[0][0]
        except Exception:
            ensemble["last_regime"] = "ranging"

        sym_summary = " ".join(
            f"{s.split('.')[0]}({s.split('|')[1] if '|' in s else 'all'})={v:.3f}"
            for s,v in symbol_aucs.items() if v == v
        )
        n_sym_base    = len(set(k.split("|")[0] for k in symbol_models))
        n_sym_windows = len(symbol_models)
        log.info(f"Ensemble retrained: {len(models)} global + "
                 f"{n_sym_windows} symbol-window models ({n_sym_base} symbols), "
                 f"{n_resolved} trades, avg_AUC={avg_auc:.3f}")
        if sym_summary:
            log.info(f"  Symbol AUCs: {sym_summary}")

        # ── SIMONS: Signal decay detector ─────────────────────────────────
        # Measure how predictive each feature was in last 50 trades vs last 200.
        # If a feature was important before but is now random = regime shifted.
        try:
            if "all" in models and len(placed) >= 50:
                m_all    = models["all"]
                # Window models live in symbol_models, not models. Find most recent active window.
                _recent_keys = [k for k in symbol_models if "|last_2days" in k or "|last_3days" in k]
                m_recent = symbol_models.get(_recent_keys[0]) if _recent_keys else None
                if m_all and m_recent:
                    fi_all    = m_all.named_steps["clf"].feature_importances_
                    fi_recent = m_recent.named_steps["clf"].feature_importances_
                    # Align lengths -- imputer drops all-NaN cols differently per window
                    # Pad shorter with zeros (missing features = no importance)
                    max_len = max(len(fi_all), len(fi_recent))
                    fi_all    = np.pad(fi_all,    (0, max_len - len(fi_all)))
                    fi_recent = np.pad(fi_recent, (0, max_len - len(fi_recent)))
                    # Features that decayed most: was important, now not
                    decay     = fi_all - fi_recent
                    top_decay = sorted(enumerate(decay), key=lambda x: -x[1])[:5]
                    # Features that gained most: was unimportant, now matters
                    gaining   = sorted(enumerate(decay), key=lambda x: x[1])[:5]
                    decay_log = []
                    for idx, d in top_decay:
                        if d > 0.01:  # meaningful decay
                            decay_log.append(f"feat_{idx}(decay={d:.3f})")
                    if decay_log:
                        log.warning(f"  SIMONS DECAY: features losing power: "
                                   f"{', '.join(decay_log)}")
                    gain_log = []
                    for idx, d in gaining:
                        if d < -0.01:  # gaining importance
                            gain_log.append(f"feat_{idx}(gain={-d:.3f})")
                    if gain_log:
                        log.info(f"  SIMONS GAIN: features gaining power: "
                                f"{', '.join(gain_log)}")
        except Exception as e:
            log.warning(f"Simons decay detector error: {e}")

        # ── GAUSS: Platt scaling calibration (FIXED -- calibrates ensemble output) ──
        # Previous bug: Platt fitted on global "all" model predictions only,
        # but ensemble_predict combines global(1x) + symbol(2x weighted).
        # Those are different distributions -> calibration was applied incorrectly.
        #
        # Fix: run the full ensemble voting logic on platt_val_set to get the
        # actual final probs the system produces, then fit Platt on those.
        # Now: "Platt input distribution" == "live inference distribution" -> honest.
        try:
            from sklearn.linear_model import LogisticRegression
            if len(platt_val_set) >= 60 and (models or symbol_models):
                # v195: log Platt loop entry state -- helps diagnose why final_probs ends up empty
                log.info(f"  Platt diagnostic: entering loop with {len(platt_val_set)} val trades, "
                         f"{len(models)} global models, {len(symbol_models)} symbol models")
                final_probs = []   # what ensemble_predict would actually output
                y_val       = []

                for t in platt_val_set:
                    ctx_v = t.get("context", {})
                    sym_v = t.get("symbol", "")
                    dummy = {"context": ctx_v, "outcome": None}
                    X_v   = np.array([build_feature_vector(dummy)])
                    # v196 FIX: apply same _col_filter as training (line 6869) and
                    # ensemble_predict (line 7646). Without this, X_v has 332 features
                    # but models trained on 217 -- every predict_proba raises ValueError,
                    # caught silently, final_probs stays empty, Platt skipped EVERY EOD.
                    # This bug existed since feature pruning was added (~v156).
                    if _col_filter is not None:
                        X_v = X_v[:, _col_filter]

                    # Replicate exact ensemble_predict weighting logic
                    ep = []
                    ev = 0
                    for m in models.values():
                        try:
                            p = float(m.predict_proba(X_v)[0][1])
                            ep.append(p)
                            if p > 0.5: ev += 1   # match ensemble_predict threshold
                        except Exception as _ep_e:
                            # v195: was log.debug -- elevated to track silent calibration failures.
                            # Every EOD has shown "insufficient val probs: 0" -- need visibility
                            # into why predictions are failing in this loop. If we never see this
                            # warning fire and val probs are still 0, the issue is upstream
                            # (empty platt_val_set, etc.) and we'll know from absence.
                            log.warning(f"  Platt global pred error: {type(_ep_e).__name__}: {_ep_e}")

                    # Symbol model: sample-size-weighted (same logic as prediction)
                    sym_ps = []
                    for key, m in symbol_models.items():
                        if key == sym_v or key.startswith(sym_v + "|"):
                            try:
                                sp = float(m.predict_proba(X_v)[0][1])
                                sym_ps.append(sp)
                            except Exception as _sp_e:
                                # v195: was log.debug -- elevated to track silent calibration failures
                                log.warning(f"  Platt sym pred error ({key}): {type(_sp_e).__name__}: {_sp_e}")
                    if sym_ps:
                        sym_n   = sum(1 for tr in train_placed if tr.get("symbol") == sym_v)
                        sym_w   = min(2.0, (sym_n / 100.0) ** 0.5)
                        sym_avg = sum(sym_ps) / len(sym_ps)
                        for _ in range(max(1, round(sym_w))):
                            ep.append(sym_avg)
                            if sym_avg > 0.5: ev += 1   # match ensemble_predict threshold

                    if ep:
                        final_probs.append(sum(ep) / len(ep))
                        y_val.append(1 if t.get("outcome") in ("win","eod_win") else 0)

                # v195: post-loop diagnostic
                log.info(f"  Platt diagnostic: loop complete, "
                         f"final_probs={len(final_probs)} (need >=30 to fit Platt)")

                if len(final_probs) >= 30:
                    fp_arr = np.array(final_probs).reshape(-1, 1)
                    y_arr  = np.array(y_val)
                    platt  = LogisticRegression(C=1.0, max_iter=500)
                    platt.fit(fp_arr, y_arr)

                    # v156: MONOTONICITY GATE for Platt.
                    # Calibration buckets in ml_report25 are NON-MONOTONIC:
                    # ML 0-9% -> actual 55%, ML 90-99% -> actual 50%, middle is noise.
                    # Fitting Platt to non-monotone scores produces garbage -- Platt
                    # assumes the raw scores RANK trades correctly (just need rescaling).
                    # If they don't rank correctly, Platt amplifies the wrongness.
                    #
                    # Test: split raw probs into low/mid/high terciles and check that
                    # actual WR is monotonically increasing. If not, refuse to apply Platt
                    # at inference (just use raw probs directly -- at least their ranking
                    # is preserved within each fold).
                    try:
                        _sorted = sorted(zip(final_probs, y_val), key=lambda z: z[0])
                        _n = len(_sorted)
                        _t1 = _sorted[: _n // 3]
                        _t2 = _sorted[_n // 3 : 2 * _n // 3]
                        _t3 = _sorted[2 * _n // 3 :]
                        _wr1 = sum(y for _, y in _t1) / max(len(_t1), 1)
                        _wr2 = sum(y for _, y in _t2) / max(len(_t2), 1)
                        _wr3 = sum(y for _, y in _t3) / max(len(_t3), 1)
                        # Monotone if WR(low) <= WR(mid) <= WR(high) within tolerance
                        _is_monotone = (_wr1 <= _wr2 + 0.05) and (_wr2 <= _wr3 + 0.05)
                        # Also require some real spread -- flat WR is uninformative
                        _spread_ok = (_wr3 - _wr1) >= 0.05
                        ensemble["platt_monotone"] = bool(_is_monotone and _spread_ok)
                        log.info(
                            f"  Platt monotonicity: tercile WR [{_wr1:.0%}, {_wr2:.0%}, {_wr3:.0%}] "
                            f"-> {'MONOTONE' if ensemble['platt_monotone'] else 'NON-MONOTONE -- calibration gated OFF'}"
                        )
                    except Exception as _mono_e:
                        log.debug(f"Monotonicity check error: {_mono_e}")
                        ensemble["platt_monotone"] = False

                    # Calibration quality check
                    buckets = {"0-25%": [], "25-50%": [], "50-75%": [], "75-100%": []}
                    for p, y in zip(final_probs, y_val):
                        if   p < 0.25: buckets["0-25%"].append(y)
                        elif p < 0.50: buckets["25-50%"].append(y)
                        elif p < 0.75: buckets["50-75%"].append(y)
                        else:          buckets["75-100%"].append(y)
                    calib_log = [f"ML{lb}->{sum(ys)/len(ys):.0%}actual"
                                 for lb, ys in buckets.items() if len(ys) >= 5]
                    cal_err = sum(abs(p - y) for p, y in zip(final_probs, y_val)) / len(y_val)
                    # NOTE: If quality labels just changed, this calibration
                    # is on the new label regime. Check cal_err carefully.
                    log.info(f"  GAUSS calibration on ensemble output "
                             f"(n={len(final_probs)}, cal_err={cal_err:.3f}): "
                             f"{', '.join(calib_log) if calib_log else 'insufficient per bucket'}")
                    ensemble["platt_scaler"]  = platt
                    ensemble["platt_val_n"]   = len(final_probs)
                    ensemble["platt_cal_err"] = round(cal_err, 3)
                    # EMA smoothed cal_err for dynamic threshold stability
                    _prev_smoothed = ensemble.get("cal_err_smoothed", cal_err)
                    ensemble["cal_err_smoothed"] = round(0.7 * _prev_smoothed + 0.3 * cal_err, 4)
                else:
                    log.info(f"  GAUSS calibration: skipped (insufficient val probs: {len(final_probs)})")
                    ensemble["platt_scaler"] = None
            else:
                log.info(f"  GAUSS calibration: skipped (need 60+ val trades, have {len(platt_val_set)})")
                ensemble["platt_scaler"] = None
        except Exception as e:
            log.warning(f"Gauss Platt scaling error: {e}")

        # ── TURING(CPCV): Combinatorial Purged Cross-Validation generalization test ──
        # Replaces single walk-forward split (gap was unstable: 0.048->0.269->0.095->0.117).
        # CPCV averages over C(6,2)=15 fold combinations -- stable gap with std dev.
        # Reference: Arian, Norouzi, Seco (2024) SSRN 4686376.
        try:
            _cpcv = cpcv_turing_test(
                placed=placed, build_feature_vector=build_feature_vector,
                _ml_outcome=_ml_outcome, _quality_weight=_quality_weight,
                _ml_quality_label=_ml_quality_label, _age_weight=_age_weight,
                avg_auc=avg_auc, col_filter=_col_filter, log=log,
                n_splits=6, k_test=2, embargo_hours=12,
            )
            if _cpcv["turing_auc"] is not None:
                turing_auc  = _cpcv["turing_auc"]
                overfit_gap = _cpcv["turing_gap"]
                gap_std     = _cpcv["turing_gap_std"]
                n_splits_ok = _cpcv["turing_n_splits"]
                ensemble["turing_auc"]         = round(avg_auc, 3)
                ensemble["turing_holdout_auc"] = turing_auc
                ensemble["turing_gap"]         = overfit_gap
                ensemble["turing_gap_std"]     = gap_std
                ensemble["turing_real"]        = _cpcv["turing_real"]
                ensemble["turing_method"]      = "cpcv"
                # v154 FIX: Threshold based on n_usable_training (not n_placed)
                # n_placed includes data-collection/random/candle-fail trades
                # that never make it into training. The model's generalization
                # ability depends on how many samples it actually trained on.
                # With 217 usable samples, gap=0.334 is expected, not overfit.
                _n_placed   = len(placed)
                _n_usable   = len(train_placed)  # after dedup + candle-fail filter
                if _n_usable >= 500:
                    _gap_thresh = 0.15   # strict -- enough data to expect tight generalization
                elif _n_usable >= 200:
                    _gap_thresh = 0.35   # moderate -- small-data regime, allow higher gap
                elif _n_usable >= 100:
                    _gap_thresh = 0.45   # lenient -- very few samples
                else:
                    _gap_thresh = 0.55   # minimal -- barely enough to train at all
                log.info(f"  Turing threshold: {_gap_thresh:.2f} (n_usable={_n_usable}, n_placed={_n_placed})")
                online_retrain._last_gap_thresh = _gap_thresh  # store for save gate
                if overfit_gap > _gap_thresh:
                    log.warning(
                        f"  TURING(CPCV): AUC={avg_auc:.3f} holdout={turing_auc:.3f} "
                        f"gap={overfit_gap:.3f}\xb1{gap_std:.3f} "
                        f"splits={n_splits_ok} -- POSSIBLE OVERFIT (thresh={_gap_thresh})"
                    )
                else:
                    log.info(
                        f"  TURING(CPCV): AUC={avg_auc:.3f} holdout={turing_auc:.3f} "
                        f"gap={overfit_gap:.3f}\xb1{gap_std:.3f} "
                        f"splits={n_splits_ok} -- patterns look REAL"
                    )
            else:
                # CPCV insufficient data -- fall back to simple walk-forward
                log.info("  TURING(CPCV): skipped (insufficient data) -- no Turing test this cycle")
        except Exception as e:
            log.warning(f"CPCV Turing error: {e}")

        # ── Hardened model save logic (v105) ────────────────────────────────
        # Save only if generalization is confirmed. Rules:
        #   HARD PASS:  gap <= 0.15  (clean generalization)
        #   SOFT PASS:  gap <= 0.20 AND gap improved vs previous AND sep_recent > 0
        #   REJECT:     anything else -- keep previous model
        _gap_now     = ensemble.get("turing_gap", 999)
        _turing_reject = ensemble.get("turing_reject", False)
        # NOTE: _sep_recent read is BELOW the carry-forward block intentionally.
        # The carry-forward may update ensemble["separation_recent"] from the previous
        # pkl. Reading _sep_recent before that block means the carry-forward value
        # never reaches the soft-pass gate -- it always sees the pre-carry snapshot.

        # Load previous gap and sep_recent for comparison
        _prev_gap = 999
        _prev_sep = -1.0
        try:
            if os.path.exists("ml_model.pkl"):
                with open("ml_model.pkl", "rb") as _pf:
                    _prev = pickle.load(_pf)
                    _prev_gap = _prev.get("turing_gap", 999)
                    _prev_sep = _prev.get("separation_recent",
                                          _prev.get("separation_overall", -1.0))
                    # Carry forward sep_recent from previous pkl if this retrain couldn't compute it.
                    # Condition: separation_recent is missing OR still at -1.0 default
                    # (old pkls pre-fix had NameError so field was never stored)
                    if ensemble.get("separation_recent", -1.0) <= -1.0:
                        ensemble["separation_recent"] = _prev.get("separation_recent",
                                                         _prev.get("separation_overall", -1.0))
        except Exception:
            _prev_gap = 999
            _prev_sep = -1.0

        # Read _sep_recent NOW -- after carry-forward has had a chance to fill it
        _sep_recent = ensemble.get("separation_recent", -1)

        # v154 FIX: hard/soft pass relative to dynamic threshold
        # _gap_thresh was set by n_usable above -- use it here too
        _gap_thresh_save = getattr(online_retrain, "_last_gap_thresh", 0.35)
        _hard_pass = (_gap_now <= _gap_thresh_save * 0.80)        # 80% of threshold = clear pass
        _soft_pass = (_gap_now <= _gap_thresh_save                 # within threshold
                      and _gap_now < _prev_gap                     # improved vs previous
                      and _sep_recent > 0)                         # model scores correctly

        # v155: RECOVERY pass -- if the existing model is inverted (sep <= -0.05),
        # any non-inverted new model is an improvement. Without this, an inverted
        # pkl can never be replaced because soft_pass requires sep_recent > 0
        # AND the previous model's "improvement" comparison favors the broken one.
        # This is exactly the situation in ml_report25: pkl sep=-0.084, model 7 days
        # stale, no path to recovery without manual intervention.
        # _prev_sep was loaded above alongside _prev_gap.
        _recovery_pass = (
            _prev_sep <= -0.05                       # current model is broken
            and _gap_now <= _gap_thresh_save         # new model has acceptable gap
            and _sep_recent >= -0.02                 # new model is at least near-neutral
        )

        # v193: SEP_IMPROV threshold relaxed from +0.05 to +0.025.
        # Reason: observed sep_recent improvement rate is ~+0.015 per retrain in
        # current data composition (May 14 saved with +0.006, May 18=+0.018,
        # May 19=+0.035, May 20=+0.011). The +0.05 bar required ~4 days of
        # consecutive improvement to clear, but model-vs-market drift over that
        # period means the deployed model degrades on current conditions before
        # promotion can occur. May 20 audit confirmed degradation:
        #   - Recent 50 WR dropped from baseline 49% to 38% (-13%)
        #   - US30 symbol WR dropped to 33% over 21 recent trades
        #   - Two setups (brooks_5m|wedge 30% n=10, brooks_15m|double_top 25% n=8)
        #     showing regime mismatch with the May 14 model
        # Relaxed threshold lets models with meaningful (not just noise) sep
        # improvement promote. Old +0.05 would not have promoted any model
        # since May 14. New +0.025 would have promoted May 19's model.
        # The gap ceiling (gap <= 0.4025) is unchanged -- still rejects
        # high-variance models. Only the improvement-over-prev bar moves.
        _separation_improvement_pass = (
            _gap_now <= _gap_thresh_save * 1.15      # within 15% of threshold ceiling
            and _sep_recent > 0.02                   # model has real positive separation
            and _sep_recent > _prev_sep + 0.025      # v193: relaxed from +0.05 to +0.025
        )

        _save_model = _hard_pass or _soft_pass or _recovery_pass or _separation_improvement_pass

        if _turing_reject:
            log.warning("  Model save SKIPPED -- Turing reject flag set")
        elif not _save_model:
            log.warning(f"  Model save SKIPPED -- gap={_gap_now:.3f} prev={_prev_gap:.3f} "                       f"sep_recent={_sep_recent:+.3f} prev_sep={_prev_sep:+.3f} -- keeping previous model")
        else:
            if _hard_pass:
                reason = "hard_pass"
            elif _soft_pass:
                reason = "soft_pass"
            elif _separation_improvement_pass:
                reason = "separation_improvement"
            else:
                reason = "recovery_pass"
            # EOD-only save gate: intraday retrains collect stats and log diagnostics
            # but do NOT swap the pkl. Only the EOD retrain (called with _eod_mode=True)
            # is allowed to save. Prevents mid-session model swaps during recovery phase
            # where a 25-trade morning sample could temporarily pass the Turing gate.
            _eod_mode = getattr(online_retrain, '_eod_mode', False)
            if _eod_mode:
                _pkl_tmp = "ml_model.pkl.tmp"
                with open(_pkl_tmp, "wb") as f:
                    pickle.dump(ensemble, f)
                os.replace(_pkl_tmp, "ml_model.pkl")  # atomic -- previous model safe until overwrite
                log.info(f"  Model saved to ml_model.pkl (EOD {reason}: gap={_gap_now:.3f} prev={_prev_gap:.3f})")
            else:
                log.info(f"  Model would save (intraday {reason}: gap={_gap_now:.3f}) -- EOD-only, not swapping pkl")

    except ImportError:
        pass  # scikit-learn not available
    except Exception as e:
        log.warning(f"Online retrain error: {e}")

def ensemble_predict(trade_context: dict) -> dict:
    import warnings
    warnings.filterwarnings("ignore", category=UserWarning, module="sklearn.impute")

    """
    Get ensemble prediction for a trade context.
    Returns win probability and confidence level.
    Requires 3/5 models to agree for HIGH confidence.
    """
    try:
        import pickle
        import numpy as np

        if not os.path.exists("ml_model.pkl"):
            return {"prob": 0.5, "confidence": "none", "votes": 0}

        # PERF: cache pkl load with 60s TTL -- ensemble_predict called on every signal
        # pkl only changes at EOD retrain (once per day) -- no need to re-read every second
        _pkl_cache_key = "_ensemble_pkl_cache"
        _pkl_ts_key    = "_ensemble_pkl_cache_ts"
        _now_pkl       = datetime.now(timezone.utc).timestamp()
        _pkl_cached    = getattr(ensemble_predict, _pkl_cache_key, None)
        _pkl_cached_ts = getattr(ensemble_predict, _pkl_ts_key, 0)
        if _pkl_cached is None or (_now_pkl - _pkl_cached_ts) > 60:
            with open("ml_model.pkl", "rb") as f:
                _pkl_cached = pickle.load(f)
            setattr(ensemble_predict, _pkl_cache_key, _pkl_cached)
            setattr(ensemble_predict, _pkl_ts_key, _now_pkl)
        ensemble = _pkl_cached

        # Handle old single-model format
        if "model" in ensemble and "models" not in ensemble:
            return {"prob": 0.5, "confidence": "legacy", "votes": 0}

        models = ensemble.get("models", {})
        if not models:
            return {"prob": 0.5, "confidence": "none", "votes": 0}

        # Create a dummy trade dict for feature extraction
        dummy = {"context": trade_context, "outcome": None}
        X = np.array([build_feature_vector(dummy)])

        # Apply column filter -- use same feature subset as training
        import warnings as _w2
        _w2.filterwarnings("ignore", category=UserWarning, module="sklearn")
        _cf = ensemble.get("col_filter")
        if _cf is not None:
            import numpy as _np2
            X = X[:, _np2.array(_cf)]

        probs  = []
        votes  = 0  # votes for WIN
        for name, model in models.items():
            try:
                p = float(model.predict_proba(X)[0][1])
                probs.append(p)      # global model = 1x weight
                if p > 0.5:          # majority vote -- consistent with ML_MIN_ENTRY_PROB
                    votes += 1
            except Exception as _e:
                log.debug(f"Feature block failed: {_e}")

        # Add per-symbol models -- weight based on sample size, not fixed 2x
        # w = min(2.0, sqrt(n_symbol / 100))
        #   25 trades  -> w ≈ 0.5  (noisy model, low trust)
        #   100 trades -> w = 1.0  (equal to global)
        #   400 trades -> w = 2.0  (dominant, full trust)
        # This prevents a noisy 25-trade symbol model from swamping the global model
        symbol = trade_context.get("symbol", "")
        symbol_models = ensemble.get("symbol_models", {})
        symbol_n      = ensemble.get("symbol_n", {})   # real trade counts per symbol
        sym_prob = None
        if symbol:
            sym_probs = []
            for key, m in symbol_models.items():
                if key == symbol or key.startswith(symbol + "|"):
                    try:
                        sp = float(m.predict_proba(X)[0][1])
                        sym_probs.append(sp)
                    except Exception as _e:
                        log.debug(f"Feature block failed: {_e}")
            if sym_probs:
                sym_prob = sum(sym_probs) / len(sym_probs)
                # Real n from pkl; fallback to conservative 50 if not stored
                sym_n    = symbol_n.get(symbol, 50)
                sym_w    = min(2.0, (sym_n / 100.0) ** 0.5)
                n_votes  = max(1, round(sym_w))
                for _ in range(n_votes):
                    probs.append(sym_prob)
                if sym_prob > 0.5:
                    votes += n_votes  # majority vote, consistent with global threshold

        if not probs:
            return {"prob": 0.5, "confidence": "none", "votes": 0}

        avg_prob   = sum(probs) / len(probs)
        agreement  = votes / len(probs)

        # Apply Platt scaler calibration if available
        # GUARD: only apply when separation_overall > 0 (model direction is correct).
        # When separation is inverted (losers score higher than winners), Platt learns
        # and amplifies the inversion -- mapping high raw probs DOWN and low probs UP,
        # compressing everything to 46-48% and blocking all signals.
        # When inverted: use raw_prob directly -- preserves the model's internal ranking
        # even though absolute values are wrong. Platt re-enables automatically once
        # separation turns positive after contamination clears.
        raw_prob = avg_prob
        platt = ensemble.get("platt_scaler")
        _sep_overall = ensemble.get("separation_overall", -1.0)
        # v156: Platt requires BOTH positive separation AND monotone calibration buckets.
        # A model can have positive overall separation but non-monotone middle buckets
        # (exactly what ml_report25 showed). Fitting Platt to non-monotone scores
        # produces garbage and amplifies the wrongness -- see retrain block for the test.
        _platt_monotone = ensemble.get("platt_monotone", False)
        if platt is not None and _sep_overall > 0 and _platt_monotone:
            try:
                avg_prob = float(platt.predict_proba([[avg_prob]])[0][1])
            except Exception as _pe:
                log.debug(f"Platt calibration skipped: {_pe}")  # fallback to raw_prob
        # else: raw_prob used directly -- inversion or non-monotonicity guard active

        # Confidence based on model agreement
        if agreement >= 0.8 or agreement <= 0.2:
            confidence = "HIGH"
        elif agreement >= 0.6 or agreement <= 0.4:
            confidence = "medium"
        else:
            confidence = "low"  # models disagree

        return {
            "prob":        round(avg_prob, 3),
            "raw_prob":    round(raw_prob, 3),  # before calibration
            "confidence":  confidence,
            "votes":       votes,
            "total":       len(probs),
            "agreement":   round(agreement, 2),
            "symbol_prob": round(sym_prob, 3) if sym_prob is not None else None,
        }

    except Exception as e:
        return {"prob": 0.5, "confidence": "error", "votes": 0}

# ── ML INTELLIGENCE LAYER ────────────────────────────────────────────────────

def ml_should_filter(pred: dict) -> bool:
    """
    Returns True if ML says skip this trade entirely.
    Only fires when ML has HIGH confidence it will lose.
    Skipped trades are still logged as rejected signals -- data is never wasted.

    Thresholds:
      Live mode:  prob < 15% AND HIGH confidence (4+/5 models) -- very conservative
      Demo mode:  prob < 25% AND HIGH confidence (3+/5 models) -- slightly looser,
                  lets us measure how much the filter saves on demo data too.
                  Demo has 3x more trades so the filter fires more meaningfully.
    """
    if not ML_FILTER_HIGH_CONFIDENCE_LOSS:
        return False
    prob       = pred.get("prob", 0.5)
    confidence = pred.get("confidence", "none")
    votes      = pred.get("votes", 0)
    total      = pred.get("total", 1)

    if LIVE_MODE:
        # Live: only block when extremely confident it will lose
        # prob < 15% AND 4+/5 models agree on LOSS
        if prob < 0.15 and confidence == "HIGH" and votes <= 1 and total >= 4:
            log.info(f"  ML FILTER [live]: {prob:.0%} loss prob ({votes}/{total} models agree) -- skipping")
            return True
    else:
        # Demo: slightly looser -- block when highly confident of loss
        # prob < 25% AND 3+/5 models agree on LOSS (or only 1 model = HIGH still applies)
        # This protects the FTMO demo balance while collecting filter performance data
        if prob < 0.25 and confidence == "HIGH" and votes <= (total // 3):
            log.info(f"  ML FILTER [demo]: {prob:.0%} loss prob ({votes}/{total} models agree) -- skipping")
            return True
    return False

def check_reversal_conditions(setup_key: str) -> bool:
    """
    Check if a specific setup meets ALL conditions for auto-reversal.
    Called nightly during retrain. Updates ML_REVERSAL_CONFIRMED dict.

    Conditions (ALL must be true):
    1. 50+ resolved trades on this setup
    2. Overall win rate < 38%
    3. Last 10 trades win rate < 40% (not recovering)
    4. ML HIGH confidence loss rate > 65% on this setup historically
    """
    if not ML_REVERSAL_AUTO:
        return False

    try:
        if not os.path.exists(LOG_FILE):
            return False

        with open(LOG_FILE, encoding="utf-8") as f:
            all_trades = json.load(f)

        # Get all resolved trades for this setup
        # Decisive only -- BEs excluded everywhere in reversal logic
        _dec = ("win", "eod_win", "loss", "eod_loss")
        setup_trades = [t for t in all_trades
                       if f"{t.get('strategy','?')}|{t.get('setup_name','?')}" == setup_key
                       and t.get("placed", True)
                       and t.get("outcome") in _dec
                       and not t.get("random", False)]

        if len(setup_trades) < 50:
            return False  # need more data

        # Condition 1: overall win rate < 38%  (W / W+L only)
        wins = sum(1 for t in setup_trades if t.get("outcome") in ("win","eod_win"))
        wr   = wins / len(setup_trades) * 100
        if wr >= 38:
            return False

        # Condition 2: last 10 trades still losing
        recent = setup_trades[-10:]
        recent_wins = sum(1 for t in recent if t.get("outcome") in ("win","eod_win"))
        recent_wr   = recent_wins / len(recent) * 100
        if recent_wr >= 40:
            return False  # recovering -- don't reverse yet

        # Condition 3: ML was correct about losses most of the time
        ml_correct_loss = 0
        ml_had_pred     = 0
        for t in setup_trades[-30:]:
            ctx = t.get("context", {})
            ml_prob = ctx.get("ml_win_prob")
            if ml_prob is not None:
                ml_had_pred += 1
                if ml_prob < 0.35 and t.get("outcome") in ("loss", "eod_loss"):
                    ml_correct_loss += 1

        if ml_had_pred >= 10:
            ml_accuracy = ml_correct_loss / ml_had_pred
            if ml_accuracy < 0.65:
                return False  # ML not confident enough about this setup

        log.warning(f"AUTO-REVERSAL ENABLED for {setup_key}: "
                   f"win_rate={wr:.1f}% recent={recent_wr:.1f}% "
                   f"trades={len(setup_trades)}")
        return True

    except Exception as e:
        log.warning(f"check_reversal_conditions error: {e}")
        return False

def ml_check_reversal(signal, pred: dict, setup_stats: dict) -> bool:
    """
    Check if this signal should be REVERSED based on ML + historical win rate.
    Returns True if reversal conditions are confirmed for this setup.

    Auto-enables per setup when check_reversal_conditions() passes.
    Never reverses a setup that hasn't been confirmed.
    """
    if not ML_REVERSAL_AUTO:
        return False

    setup_key = f"{signal.symbol}|{signal.strategy}|{signal.setup_name}"

    # Check if this setup has been confirmed for reversal
    if not ML_REVERSAL_CONFIRMED.get(setup_key, False):
        return False

    # Additional real-time check: ML must also agree right now
    prob       = pred.get("prob", 0.5)
    confidence = pred.get("confidence", "none")
    votes      = pred.get("votes", 0)
    total      = pred.get("total", 5)

    # Only reverse when ML is also currently saying HIGH confidence LOSS
    if prob < 0.25 and confidence == "HIGH" and votes <= 1 and total >= 4:
        log.warning(f"  ML REVERSAL: {setup_key} confirmed loser + ML HIGH LOSS -> reversing")
        return True

    return False

def ml_adjust_sltp(signal, pred: dict):
    """
    Adjust stop loss and take profit based on ML confidence.
    HIGH confidence WIN  -> extend TP by 20% (let winners run)
    HIGH confidence LOSS -> tighten SL by 20% (protect capital)
    low confidence       -> no change
    Returns modified signal (modifies in place).
    """
    if not ML_DYNAMIC_SLTP:
        return signal

    # Guard: don't adjust SL/TP when model is overfit or separation inverted
    # An overfit model calling "HIGH confidence" is unreliable -- don't change geometry
    try:
        import pickle as _adj_pkl
        if os.path.exists("ml_model.pkl"):
            _adj_ens = getattr(ml_adjust_sltp, "_ens_cache", None)
            _adj_ts  = getattr(ml_adjust_sltp, "_ens_ts", 0)
            _adj_now = datetime.now(timezone.utc).timestamp()
            if _adj_ens is None or (_adj_now - _adj_ts) > 60:
                with open("ml_model.pkl", "rb") as _af:
                    _adj_ens = _adj_pkl.load(_af)
                setattr(ml_adjust_sltp, "_ens_cache", _adj_ens)
                setattr(ml_adjust_sltp, "_ens_ts", _adj_now)
            if _adj_ens.get("turing_gap", 999) > 0.20:
                return signal  # model overfit -- don't adjust
            if _adj_ens.get("separation_overall", -1.0) < 0:
                return signal  # separation inverted -- don't adjust
    except Exception:
        pass  # if pkl unreadable, skip adjustment (safe default)

    prob       = pred.get("prob", 0.5)
    confidence = pred.get("confidence", "none")

    if confidence != "HIGH":
        return signal

    try:
        sl_dist = abs(signal.entry - signal.stop_loss)
        tp_dist = abs(signal.take_profit - signal.entry)

        if prob >= 0.70:
            # HIGH confidence WIN -- extend TP by 20%
            if signal.direction == "long":
                signal.take_profit = signal.entry + tp_dist * 1.2
            else:
                signal.take_profit = signal.entry - tp_dist * 1.2
            log.info(f"  ML SL/TP: HIGH WIN confidence -- TP extended 20%")

        elif prob <= 0.25:
            # HIGH confidence LOSS -- tighten SL by 20%
            if signal.direction == "long":
                signal.stop_loss = signal.entry - sl_dist * 0.8
            else:
                signal.stop_loss = signal.entry + sl_dist * 0.8
            log.info(f"  ML SL/TP: HIGH LOSS confidence -- SL tightened 20%")

    except Exception as e:
        log.warning(f"ml_adjust_sltp error: {e}")

    return signal

def ml_entry_timing(signal, tf: int, max_bars: int = 3) -> bool:
    """
    Wait up to max_bars candles for a better entry bar.
    ML learns which bar patterns within a setup have the best win rate.
    Returns True if current bar is good for entry, False to skip this bar.

    Logic: check if current bar is better than average for this setup.
    Uses: bar close position, body ratio, volume -- the features ML weights most.
    """
    if not ML_ENTRY_TIMING:
        return True  # always enter if timing disabled

    try:
        df = get_candles(signal.symbol, tf, 5)
        if df is None or len(df) < 3:
            return True  # can't check, proceed

        bar = df.iloc[-2]  # use last CLOSED bar, not current forming bar

        bar_range  = float(bar["high"] - bar["low"])
        if bar_range == 0:
            return True

        body       = abs(float(bar["close"]) - float(bar["open"]))
        body_ratio = body / bar_range
        close_pos  = (float(bar["close"]) - float(bar["low"])) / bar_range

        # For longs: want bar closing near top (close_pos > 0.6) with decent body
        # For shorts: want bar closing near bottom (close_pos < 0.4) with decent body
        if signal.direction == "long":
            good_entry = close_pos > 0.55 and body_ratio > 0.4
        else:
            good_entry = close_pos < 0.45 and body_ratio > 0.4

        if not good_entry:
            log.info(f"  ML TIMING: bar not ideal (close_pos={close_pos:.2f} body={body_ratio:.2f}) -- waiting")
            return False

        return True

    except Exception as e:
        return True  # on any error, proceed with entry

def parse_score_breakdown(reasons: list) -> dict:
    """Convert score reasons list into individual ML features."""
    bd = {
        "score_signal_detected":   0,
        "score_15m_structure":     0,
        "score_5m_bar":            0,
        "score_optimal_time":      0,
        "score_1h_direction":      0,
        "score_daily_position":    0,
        "score_volatility":        0,
        "score_key_levels":        0,
    }
    for r in reasons:
        r = r.strip()
        if r.startswith("+1") and "signal detected"    in r: bd["score_signal_detected"]  = 1
        # v173 BUG FIX: factor reason strings changed in v167 but parser was never updated.
        # Old text was "15m market structure: bull"; v167 says "15m structure: ranging" or
        # "15m structure counter-trend: ...". Match both old and new for backward compat
        # with pre-v167 trade history.
        if r.startswith("+1") and ("15m market" in r or "15m structure" in r):
            bd["score_15m_structure"] = 1
        if r.startswith("+1") and "5m Brooks bar"      in r: bd["score_5m_bar"]           = 1
        if r.startswith("+1") and "optimal trading"    in r: bd["score_optimal_time"]     = 1
        if r.startswith("+1") and "1hr chart"          in r: bd["score_1h_direction"]     = 1
        if r.startswith("+1") and ("daily low" in r or "daily high" in r): bd["score_daily_position"] = 1
        if r.startswith("+1") and "volatility spike"   in r: bd["score_volatility"]       = 1
        # v173 BUG FIX: same as above. Old: "away from key levels (clean)" plural;
        # v167: "entry at key level: <level>" singular. Match both.
        if r.startswith("+1") and ("key levels" in r or "key level" in r):
            bd["score_key_levels"] = 1
    return bd

def log_signal(signal, ticket, risk_pct, confidence, reasons=None, ctx: dict = None):
    entry = asdict(signal)
    # Reuse pre-computed CMC if available (avoids 3rd full CMC call per placed trade)
    if ctx is None:
        ctx = capture_market_context(signal)
    # Add score breakdown as individual ML features
    if reasons:
        ctx.update(parse_score_breakdown(reasons))
    # Break even tracking -- will be updated by update_mfe_mae
    ctx["hit_breakeven"] = False
    ctx["be_trigger_hit"] = False   # initialized False -- set True when price hits 0.8R
    entry.update({"ticket": ticket, "outcome": None,
                  "risk_pct": risk_pct, "confidence": confidence, "context": ctx,
                  "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),  # UTC -- matches holdout cutoffs
                  "placed": True, "skip_reason": None,
                  "random": log_signal.is_random if hasattr(log_signal, "is_random") else False})
    log_signal.is_random = False  # reset after use
    entry = make_json_safe(entry)
    # Placed trades write immediately (important to not lose on crash) + flush queue
    _flush_log_queue()
    trades = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, encoding="utf-8") as f:
            trades = json.load(f)
    trades.append(entry)
    atomic_write(LOG_FILE, trades)
    log.info(f"  Logged: RSI={ctx.get('rsi_14','?')}  ATR={ctx.get('atr_14','?')}  session={ctx.get('session','?')}  streak={ctx.get('candle_streak','?')}")




# ── In-memory LOG_FILE append queue ──────────────────────────────────────────
# log_rejected_signal fires ~50x per tick. Without this, each call does a full
# LOG_FILE read + atomic write (O(n) on 5,000+ trades). That's 3,000 reads/min.
# Queue buffers rejected entries in memory, flushes every 30s or on placed trade.
# Placed trades always write immediately (via _flush_log_queue + direct write).
_log_append_queue = []
_log_queue_last_flush = 0.0


def _flush_log_queue():
    """Flush the in-memory rejected-signal queue to LOG_FILE atomically.
    Called from log_signal (on every placed trade) and the 30s slow loop.
    Safe to call when queue is empty -- exits immediately.
    """
    global _log_append_queue, _log_queue_last_flush
    if not _log_append_queue:
        return
    import time as _flt
    pending = list(_log_append_queue)
    _log_append_queue = []
    _log_queue_last_flush = _flt.monotonic()
    try:
        trades = []
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, encoding="utf-8") as _fqf:
                trades = json.load(_fqf)
        trades.extend(pending)
        atomic_write(LOG_FILE, trades)
    except Exception as _fle:
        log.warning(f"Log queue flush error: {_fle}")
        # Put entries back on front of queue -- don't lose data on crash
        _log_append_queue = pending + _log_append_queue


def log_rejected_signal(signal, reason: str, score: int, reasons: list, ctx: dict = None):
    """
    Log signals that were rejected by filters.
    Critical for ML -- model needs negative examples too.
    outcome stays None until we check what price did afterward.

    ctx: optional pre-computed market context (from _ml_ctx in main loop).
    When provided, skips CMC recomputation -- avoids 14 redundant MT5 reads per rejection.
    Pre-filter rejections (before CMC is available) pass no ctx -> use empty dict.

    v175: also produces a THROTTLED console line per (symbol, reason_prefix) so
    silent rejections become visible. Without this, dozens of rejection paths
    were invisible -- the bot looked broken when it was actually rejecting trades
    correctly. Throttle is 5 minutes per (symbol, reason_prefix).
    """
    try:
        if ctx is None:
            # Pre-filter rejection (blocked hours, cooldown, disabled setup)
            # CMC not yet computed -- use minimal context to avoid 14 MT5 reads
            ctx = {}
        ctx.update(parse_score_breakdown(reasons))
        ctx["hit_breakeven"] = False
        entry = asdict(signal)
        entry.update({
            "ticket":      None,
            "outcome":     None,
            "risk_pct":    0,
            "confidence":  score,
            "context":     ctx,
            "timestamp":   datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),  # UTC
            "placed":      False,
            "skip_reason": reason,
            "random":      False,
        })
        entry = make_json_safe(entry)
        # Append to in-memory queue -- flushed every 30s to avoid per-rejection file I/O
        _log_append_queue.append(entry)

        # v175: throttled console log so silent rejections are visible.
        # Reason_prefix = first 2 underscore-separated tokens (e.g. "cooldown_skip",
        # "per_symbol", "inverted_rr", "ml_neg", "risk_too"). This collapses
        # numeric-suffix variants like "per_symbol_cap_US30.cash_2" into one bucket.
        # Skip the noisiest categories that don't add value (e.g. blocked hours
        # which we already block silently for spam reasons).
        _SKIP_VISIBLE = {"outside_hours_skip_zero_risk"}
        _reason_prefix = "_".join(reason.split("_")[:3])
        if _reason_prefix not in _SKIP_VISIBLE:
            _rej_key = (getattr(signal, "symbol", "?"), _reason_prefix)
            _rej_seen = getattr(log_rejected_signal, "_seen", {})
            _rej_now_ts = datetime.now(timezone.utc).timestamp()
            _rej_last = _rej_seen.get(_rej_key, 0)
            if _rej_now_ts - _rej_last > 300:  # 5 min minimum between same (symbol, reason)
                log.info(f"  REJECT {signal.symbol} {signal.setup_name}: {reason}")
                _rej_seen[_rej_key] = _rej_now_ts
                if len(_rej_seen) > 100:
                    _rej_seen = {k: v for k, v in _rej_seen.items()
                                 if _rej_now_ts - v < 600}
                setattr(log_rejected_signal, "_seen", _rej_seen)
    except Exception as e:
        log.warning(f"log_rejected_signal error: {e}")

def update_mfe_mae():
    """
    Update Max Favorable Excursion and Max Adverse Excursion for open trades.
    MFE = furthest price moved in your favour (missed profit if exited early)
    MAE = furthest price moved against you (how close to SL it got)
    Also tracks trade duration in minutes.
    """
    positions = mt5.positions_get()
    if not positions or not os.path.exists(LOG_FILE):
        return
    with open(LOG_FILE, encoding="utf-8") as f:
        trades = json.load(f)

    pos_by_ticket = {p.ticket: p for p in positions}
    updated = False
    now = datetime.now(timezone.utc)

    for t in trades:
        if t.get("outcome") is not None:  # safe -- handles missing key
            continue
        ticket = t.get("ticket")
        if ticket not in pos_by_ticket:
            continue
        pos     = pos_by_ticket[ticket]
        entry   = t.get("entry", pos.price_open)
        current = pos.price_current
        is_long = pos.type == mt5.ORDER_TYPE_BUY

        # Favorable = in direction of trade
        if is_long:
            favorable = current - entry
            adverse   = entry - current
        else:
            favorable = entry - current
            adverse   = current - entry

        ctx = t.get("context", {})
        old_mfe = ctx.get("mfe", 0)
        old_mae = ctx.get("mae", 0)
        ctx["mfe"] = round(max(old_mfe, favorable), 2)
        ctx["mae"] = round(max(old_mae, adverse), 2)

        # Break even detection -- SL moved to entry means pos.sl ~= entry
        if not ctx.get("hit_breakeven", False):
            sl = pos.sl
            if sl != 0 and abs(sl - entry) / entry < 0.0003:
                ctx["hit_breakeven"] = True

        # MFE as ratio of original risk (how many R did it go in favour)
        original_risk = abs(t.get("stop_loss", entry) - entry)
        if original_risk > 0:
            ctx["mfe_r"] = round(ctx["mfe"] / original_risk, 2)
            ctx["mae_r"] = round(ctx["mae"] / original_risk, 2)

        # Trade duration in minutes
        try:
            entry_time = datetime.fromtimestamp(pos.time, tz=timezone.utc)
            ctx["duration_minutes"] = int((now - entry_time).total_seconds() / 60)
        except Exception as _e:
            log.debug(f"Feature block failed: {_e}")

        # ── Outcome quality features (updated live as trade progresses) ──
        try:
            tp = t.get("take_profit", 0)
            sl = t.get("stop_loss", 0)
            tp_dist = abs(tp - entry) if tp and entry else 0
            sl_dist = abs(sl - entry) if sl and entry else 0

            mfe = ctx.get("mfe", 0)
            mae = ctx.get("mae", 0)

            # Did price reach TP cleanly? (got to 90%+ of TP distance)
            if tp_dist > 0:
                ctx["tp_reach_pct"]        = round(mfe / tp_dist, 2)
                ctx["tp_clean_hit"]        = mfe >= tp_dist * 0.9
                ctx["tp_scraped"]          = 0.7 <= mfe / tp_dist < 0.9
                ctx["tp_never_close"]      = mfe < tp_dist * 0.5

            # How deep into loss did it go before recovering?
            if sl_dist > 0:
                ctx["sl_reach_pct"]        = round(mae / sl_dist, 2)
                ctx["sl_close_call"]       = mae >= sl_dist * 0.8  # nearly stopped out
                ctx["sl_barely_touched"]   = mae < sl_dist * 0.2   # barely went against

            # MFE vs MAE ratio -- trade quality score
            # High = went far in favour, barely against = good quality
            # Low = went against a lot, barely in favour = bad quality
            if mae > 0:
                ctx["mfe_mae_ratio"]       = round(mfe / mae, 2)
                ctx["high_quality_trade"]  = mfe / mae >= 2.0
                ctx["low_quality_trade"]   = mfe / mae <= 0.5
            elif mfe > 0:
                ctx["mfe_mae_ratio"]       = 99.0  # never went against -- perfect
                ctx["high_quality_trade"]  = True
                ctx["low_quality_trade"]   = False

            # Speed of resolution -- fast wins vs slow grind
            dur = ctx.get("duration_minutes", 0)
            ctx["fast_resolution"]         = dur < 30
            ctx["slow_grind"]              = dur > 180

        except Exception as _oq:
            pass

        t["context"] = ctx
        updated = True

    if updated:
        atomic_write(LOG_FILE, trades)

def cancel_old_pending_orders():
    """
    Cancel pending orders that are:
    1. Older than 4 hours
    2. Invalidated -- price has moved past the stop loss (trade already a loser)
    3. Missed -- price has moved past the take profit (trade would have won but wasn't filled)
    """
    orders = mt5.orders_get()
    if not orders:
        return
    cutoff = datetime.now(timezone.utc) - timedelta(hours=2)
    for order in orders:
        cancel = False
        reason = ""

        # Check age
        order_time = datetime.fromtimestamp(order.time_setup, tz=timezone.utc)
        if order_time < cutoff:
            cancel = True
            reason = "expired (>2hrs)"

        # Check invalidation and missed TP
        if not cancel and order.sl != 0:
            tick = mt5.symbol_info_tick(order.symbol)
            if tick:
                bid = tick.bid
                ask = tick.ask
                is_buy_stop   = order.type == mt5.ORDER_TYPE_BUY_STOP
                is_sell_stop  = order.type == mt5.ORDER_TYPE_SELL_STOP
                is_buy_limit  = order.type == mt5.ORDER_TYPE_BUY_LIMIT
                is_sell_limit = order.type == mt5.ORDER_TYPE_SELL_LIMIT

                # Buy stop: entry ABOVE current price - wait for breakout
                if is_buy_stop:
                    if bid < order.sl:
                        cancel = True
                        reason = f"invalidated -- price {bid:.2f} below SL {order.sl:.2f}"
                    elif order.tp > 0 and bid > order.tp:
                        cancel = True
                        reason = f"missed -- price {bid:.2f} above TP {order.tp:.2f}"
                    elif order.tp > 0:
                        # Price moved halfway to TP without filling -- momentum spent
                        halfway_to_tp = order.price_open + (order.tp - order.price_open) * 0.5
                        if bid >= halfway_to_tp:
                            cancel = True
                            reason = f"halfway to TP -- price {bid:.2f} >= halfway {halfway_to_tp:.2f}"

                # Buy limit: entry BELOW current price - wait for pullback
                # Price must pull back DOWN to entry to fill
                # If price runs UP past TP or halfway to TP -- move is done, cancel
                if is_buy_limit:
                    if bid < order.sl:
                        cancel = True
                        reason = f"invalidated -- price {bid:.2f} below SL {order.sl:.2f}"
                    elif order.tp > 0 and bid >= order.tp:
                        cancel = True
                        reason = f"missed -- price {bid:.2f} reached TP {order.tp:.2f} without fill"
                    elif order.tp > 0:
                        halfway_to_tp = order.price_open + (order.tp - order.price_open) * 0.5
                        if bid >= halfway_to_tp:
                            cancel = True
                            reason = f"halfway to TP -- price {bid:.2f} >= halfway {halfway_to_tp:.2f} -- move done"

                # Sell stop: entry BELOW current price - wait for breakdown
                if is_sell_stop:
                    if ask > order.sl:
                        cancel = True
                        reason = f"invalidated -- price {ask:.2f} above SL {order.sl:.2f}"
                    elif order.tp > 0 and ask < order.tp:
                        cancel = True
                        reason = f"missed -- price {ask:.2f} below TP {order.tp:.2f}"
                    elif order.tp > 0:
                        halfway_to_tp = order.price_open - (order.price_open - order.tp) * 0.5
                        if ask <= halfway_to_tp:
                            cancel = True
                            reason = f"halfway to TP -- price {ask:.2f} <= halfway {halfway_to_tp:.2f}"

                # Sell limit: entry ABOVE current price - wait for rally
                # Price must rally UP to entry to fill
                # If price drops DOWN past TP or halfway to TP -- move is done, cancel
                if is_sell_limit:
                    if ask > order.sl:
                        cancel = True
                        reason = f"invalidated -- price {ask:.2f} above SL {order.sl:.2f}"
                    elif order.tp > 0 and ask <= order.tp:
                        cancel = True
                        reason = f"missed -- price {ask:.2f} reached TP {order.tp:.2f} without fill"
                    elif order.tp > 0:
                        halfway_to_tp = order.price_open - (order.price_open - order.tp) * 0.5
                        if ask <= halfway_to_tp:
                            cancel = True
                            reason = f"halfway to TP -- price {ask:.2f} <= halfway {halfway_to_tp:.2f}"

        if cancel and reason:
            result = mt5.order_send({
                "action": mt5.TRADE_ACTION_REMOVE,
                "order":  order.ticket,
            })
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                log.info(f"Cancelled order #{order.ticket} {order.symbol} -- {reason}")
        elif cancel and not reason:
            log.warning(f"Cancel triggered with no reason for #{order.ticket} {order.symbol} sl={order.sl} tp={order.tp} type={order.type}")

# REMOVED: already_brooks_recent -- dead code, never called

def _classify_outcome(t, profit, comment, deal_time=None, deal_price=None):
    """Classify a closed trade outcome from profit and broker comment.
    Shared helper used by both position_profit and closing_deals EOD paths.
    Eliminates duplicate classification code in the EOD outcome fix cycle.

    v185: also captures close_time, close_price, hold_minutes, and realized_r.
    Without these, post-hoc analysis can't tell if a "loss" hit SL in 5min
    (chop) or 50min (slow grind) -- you only know it lost. Same for wins.

    deal_time and deal_price are optional -- older callers may not pass them.
    Falls back to current time/price-from-profit if missing.
    """
    entry    = t.get("entry", 0)
    # Tolerance = spread/commission only (0.01% of entry)
    # Old: risk_pts * 0.05 was too wide -- a 3pt loss on 100pt risk = "breakeven"
    # ML should see small losses as real losses, not BEs
    tol      = entry * 0.0001 if entry > 0 else 0.01
    if any(x in comment for x in ["end_of_day","session_close","time_exit","friday_close","session_start_cleanup"]):
        t["outcome"] = "eod_win" if profit > tol else ("eod_loss" if profit < -tol else "eod_breakeven")
    elif abs(profit) <= tol:
        t["outcome"] = "breakeven"
        mfe = t.get("context", {}).get("mfe_r", 0) or 0
        if t.get("context", {}).get("be_trigger_hit"):
            if "context" not in t:
                t["context"] = {}
            t["context"]["virtual_outcome"] = "win" if mfe >= 0.95 else "loss"
    elif profit > 0:
        t["outcome"] = "win"
    else:
        t["outcome"] = "loss"
    if any(x in comment for x in ["trail","atr","tighten","partial"]):
        t["atr_exit"] = True
        t["atr_exit_outcome"] = t["outcome"]
    if "session_start_cleanup" in comment:
        t["restart_close"] = True
    if "time_exit" in comment:
        t["time_exit_close"] = True

    # v185: capture close_time, close_price, hold time, and realized R
    # for post-hoc analysis. Hold time tells us if losses were quick chops
    # vs slow grinds. Realized_r normalizes profit to risk units so we can
    # compare 0.25%-risk and 0.50%-risk trades on equal footing.
    try:
        if deal_time is not None:
            # MT5 deal.time is unix timestamp (seconds)
            close_dt = datetime.fromtimestamp(deal_time, tz=timezone.utc)
            t["close_time"] = close_dt.strftime("%Y-%m-%d %H:%M:%S")
            # Compute hold minutes from open timestamp
            try:
                open_dt = datetime.strptime(t["timestamp"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                t["hold_minutes"] = round((close_dt - open_dt).total_seconds() / 60, 1)
            except Exception:
                pass
        if deal_price is not None and deal_price > 0:
            t["close_price"] = float(deal_price)
        # realized_r = profit / risk_in_dollars. Risk is risk_pct * balance_at_open.
        # We don't have balance_at_open stored, so use a proxy: SL-distance × lot_value
        # would require contract specs. Simplest: compute from price distances.
        sl_d = abs((t.get("entry") or 0) - (t.get("stop_loss") or 0))
        if sl_d > 0 and deal_price is not None and deal_price > 0:
            entry_p = t.get("entry") or 0
            is_long = (t.get("direction") or "").lower() == "long"
            move = (deal_price - entry_p) if is_long else (entry_p - deal_price)
            t["context"] = t.get("context", {}) or {}
            t["context"]["realized_r"] = round(move / sl_d, 3)
    except Exception as _r_err:
        # Don't let instrumentation errors block outcome classification
        pass

    # v154 FIX: Finalize MFE/MAE at close if not already fully written
    # Ensures mfe_r is always present for T1 label qualification
    # Uses profit-implied close price to reconstruct final MFE
    try:
        ctx = t.get("context", {}) or {}
        if ctx.get("mfe_r") is None:
            entry_px    = float(t.get("entry", 0) or 0)
            sl_px       = float(t.get("stop_loss", 0) or 0)
            tp_px       = float(t.get("take_profit", 0) or 0)
            orig_risk   = abs(sl_px - entry_px) if entry_px and sl_px else 0
            if orig_risk > 0 and tp_px and entry_px:
                tp_dist = abs(tp_px - entry_px)
                # Infer MFE from outcome:
                # win = price reached TP -> MFE = 1.0R
                # eod_win = closed before TP -> estimate from profit
                # loss = stopped out -> MAE = 1.0R (SL hit)
                outcome = t.get("outcome", "")
                if outcome in ("win",):
                    ctx["mfe_r"] = round(tp_dist / orig_risk, 2)
                    ctx["mae_r"] = ctx.get("mae_r", 0) or 0
                elif outcome in ("loss",):
                    ctx["mae_r"] = 1.0  # SL hit = 1.0R adverse
                    ctx["mfe_r"] = ctx.get("mfe_r", 0) or 0
                elif outcome in ("eod_win", "eod_loss") and profit != 0:
                    implied_r = abs(profit) / (orig_risk * 0.01 * entry_px + 1e-8)
                    if outcome == "eod_win":
                        ctx["mfe_r"] = round(min(implied_r, tp_dist / orig_risk), 2)
                    else:
                        ctx["mae_r"] = round(min(implied_r, 1.0), 2)
                        ctx["mfe_r"] = ctx.get("mfe_r", 0) or 0
                ctx["mfe_imputed"] = True  # flag so report can distinguish real vs imputed
                t["context"] = ctx
    except Exception:
        pass


# ── Setup hard blocks and regime gate ──────────────────────────────────────────
# Defined at module level (not inside main()) -- no reconstruction per signal.
# v159: kept for fallback when REGIME_GATE_ACTIVE=False, but expanded to match
# DISABLED_SETUPS at top of file (5 setups, set up there with handoff data).
DISABLE_SETUPS = DISABLED_SETUPS  # alias to v157 set defined at top of file

NO_DATA_COLLECTION = DISABLED_SETUPS

# v164: REGIME GATE LOOSENED -- per Analyzer 2 results on real post-cleanup data.
# =============================================================================
# Analyzer 2 ran the v159 regime block rules over 361 resolved real-risk trades
# from the post-cleanup log. Result:
#   GATE WOULD HAVE BLOCKED 136 trades with sum_R = +7.5 (POSITIVE)
#   = gate filtering OUT winners on net = HURTING profitability
#
# Per-regime breakdown of what the v159 gate would have blocked:
#   trending_bull: 65 trades  60.0% WR  +13.0R  (gate blocking PROFITABLE trades)
#   ranging:       36 trades  52.8% WR   +1.5R  (slightly profitable, gate ~neutral)
#   trending_bear: 23 trades  56.5% WR   +3.0R  (profitable, gate hurting)
#   volatile:      12 trades   8.3% WR  -10.0R  (gate WORKS here -- block stays)
#
# So: the volatile-regime block is the only part of the gate that earns its keep.
# v164 keeps DISABLED_SETUPS (the always-block list -- those are confirmed dead)
# and adds extra blocks ONLY in volatile regime. All other regimes use just the
# baseline DISABLED_SETUPS.
REGIME_SETUP_BLOCK = {
    "ranging":       DISABLED_SETUPS,     # v164: was blocking profitable trades, removed extras
    "trending_bull": DISABLED_SETUPS,     # v164: was blocking profitable trades, removed extras
    "trending_bear": DISABLED_SETUPS,     # already minimal
    # volatile: keep extras -- Analyzer 2 confirmed -10R in volatile is real bleed
    "volatile": DISABLED_SETUPS | {
        "brooks_5m|double_top",       # 30% WR over 56 trades in volatile
        "brooks_15m|double_top",
        "brooks_15m|wedge",           # 24% WR over 33 trades in volatile
        "brooks_5m|wedge",
        "brooks_5m|two_leg_pullback", # 14% WR / 14 trades -- small sample but extreme bleed
        "brooks_15m|two_leg_pullback",
    },
    "mixed":   DISABLED_SETUPS,
    "unknown": DISABLED_SETUPS,
}
# v159: gate is active. v164 keeps it active but the matrix above is now mostly
# pass-through (only volatile regime adds blocks).
REGIME_GATE_ACTIVE = True

def main():
    log.info("=" * 70)
    log.info("=== Trading Bot v197 Starting ===")
    _mode_banner = "LIVE (real money)" if LIVE_MODE else "DEMO/CHALLENGE (2x risk profile)"
    log.info(f"  Mode:           {_mode_banner}")
    log.info(f"  Account:        {MT5_LOGIN}")
    log.info(f"  Server:         {MT5_SERVER}")
    log.info(f"  Symbols:        {ALL_SYMBOLS}")
    log.info(f"  Risk:           BASE={RISK_BROOKS_BASE}%  MIN={RISK_BROOKS_MIN}%  MAX={RISK_BROOKS_MAX}%")
    log.info(f"  Safety limits:  daily={DAILY_LOSS_LIMIT}%  max_dd={MAX_DRAWDOWN}%")
    log.info(f"  Cooldown:       {LOSS_STREAK_COOLDOWN} consecutive losses")
    _score_gate_text = f"score >= {MIN_SCORE_GATE}/8 required" if MIN_SCORE_GATE > 0 else "OFF (run analyzer 6 first)"
    log.info(f"  Score gate:     {_score_gate_text}")
    log.info(f"  Per-symbol cap: max {MAX_PER_SYMBOL} positions/symbol")
    log.info(f"  Regime gate:    {'volatile-only' if REGIME_GATE_ACTIVE else 'OFF'}")
    log.info("=" * 70)
    if not connect_mt5():
        return

    get_starting_balance()
    recover_missing_outcomes()
    # Always regenerate win stats from current trades_log on startup
    # This ensures display matches actual log contents after any cleaning
    # v173: suppress the internal log inside update_win_stats -- we'll log
    # explicitly below from STATS_FILE. Without suppression, "--- Win stats ---"
    # printed twice on every startup.
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, encoding="utf-8") as f:
            _all_trades = json.load(f)
        update_win_stats._log_enabled = False
        update_win_stats(_all_trades)
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, encoding="utf-8") as f:
            stats = json.load(f)
        log.info("--- Win stats ---")
        for s in sorted(stats.values(), key=lambda x: x.get("win_rate",0), reverse=True):
            if s.get("total", 0) < 3:
                continue
            be  = s.get("breakevens", 0)
            be_str = f"/{be}BE" if be > 0 else ""
            log.info(f"  {s['strategy']:14} {s['setup_name']:22} {s['win_rate']:5.1f}%  {s['wins']}W/{s['losses']}L{be_str}  total={s['total']}")
    log.info(f"Symbols: {ALL_SYMBOLS}")
    log.info(f"Risk: main={RISK_MAIN}%  brooks_base={RISK_BROOKS_BASE}%  "
             f"daily_limit={DAILY_LOSS_LIMIT}%  max_dd={MAX_DRAWDOWN}%")

    # Clear any active cooldowns at startup that were set under previous code.
    # v183: also seed watermarks for ALL setups to "now" -- this is what actually
    # fixes the cooldown loop. With LOSS_STREAK_COOLDOWN=1 (validated by user
    # stats showing WR drops massively after 1 loss), a setup whose last trade
    # was a loss would re-trigger cooldown on every restart unless we filter
    # out historical losses. Watermark = "ignore losses before this timestamp".
    # First v183 startup: watermark = now for every setup, so no historical
    # loss can trigger cooldown. From this point, only NEW losses count.
    try:
        _state_v181 = load_state()
        _old_cooldowns = _state_v181.get("cooldowns", {})
        if _old_cooldowns:
            log.info(f"Clearing {len(_old_cooldowns)} active cooldowns from previous policy: "
                     f"{', '.join(sorted(_old_cooldowns.keys()))}")
            _state_v181["cooldowns"] = {}
        # v183: set watermark = now for every setup that has historical trades.
        # This is a one-time clean-slate operation. After this, watermarks update
        # naturally via set_cooldown() when real cooldowns trigger.
        _now_iso_v183 = datetime.now(timezone.utc).isoformat()
        _all_setups = set()
        try:
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, encoding="utf-8") as _lf_v183:
                    _trades_v183 = json.load(_lf_v183)
                _all_setups = {f"{t.get('strategy','')}|{t.get('setup_name','')}"
                               for t in _trades_v183
                               if t.get("strategy") and t.get("setup_name")}
        except Exception as _ws_e:
            log.debug(f"Watermark setup enumeration failed: {_ws_e}")
        _existing_watermarks = _state_v181.get("cooldown_streak_watermarks", {})
        _new_watermark_count = 0
        for _sk in _all_setups:
            if _sk not in _existing_watermarks:
                _existing_watermarks[_sk] = _now_iso_v183
                _new_watermark_count += 1
        if _new_watermark_count > 0:
            _state_v181["cooldown_streak_watermarks"] = _existing_watermarks
            log.info(f"v183: set initial streak watermarks for {_new_watermark_count} setups "
                     f"(historical losses won't trigger cooldowns until new losses occur)")
        save_state(_state_v181)
    except Exception as _cd_clear_err:
        log.warning(f"Cooldown clear at startup failed: {_cd_clear_err}")

    # Close any positions left open from previous session (e.g. stuck EOD)
    # Verify we're on the correct account before closing positions
    _acct_info = mt5.account_info()
    _expected  = MT5_LOGIN
    leftover   = mt5.positions_get() or []
    if leftover and _acct_info and _acct_info.login == _expected:
        log.warning(f"Found {len(leftover)} leftover positions from previous session -- closing before starting")
        close_all_positions("session_start_cleanup")
    elif leftover and _acct_info and _acct_info.login != _expected:
        log.warning(f"Skipping cleanup -- MT5 shows account {_acct_info.login}, expected {_expected}. Not closing foreign positions.")

    while True:
        try:
            # ── Weekend guard: Saturday/Sunday -- markets closed ──
            if is_weekend():
                _now_wk = datetime.now(timezone.utc)
                _days_to_monday = (7 - _now_wk.weekday()) % 7 or 7
                _monday_wk = (_now_wk + timedelta(days=_days_to_monday)).replace(
                    hour=0, minute=0, second=0, microsecond=0)
                _sleep_wk = max((_monday_wk - _now_wk).total_seconds(), 3600)
                log.info(f"Weekend -- sleeping {_sleep_wk/3600:.1f}hrs until Monday")
                time.sleep(_sleep_wk)
                continue

            # ── Weekend close: Friday 17:00 UTC ──
            if is_friday_close():
                log.warning("FRIDAY CLOSE -- closing all positions for weekend")
                close_all_positions("friday_close")
                log.info("All positions closed. Sleeping until Monday 00:00 UTC.")
                _now_fri = datetime.now(timezone.utc)
                # Calculate days until Monday (weekday 0) at 00:00 UTC
                _days_to_monday = (7 - _now_fri.weekday()) % 7 or 7  # always at least 1 day
                _monday_open = (_now_fri + timedelta(days=_days_to_monday)).replace(
                    hour=0, minute=0, second=0, microsecond=0)
                _sleep_secs = (_monday_open - _now_fri).total_seconds()
                log.info(f"Sleeping {_sleep_secs/3600:.1f}hrs until Monday {_monday_open.strftime('%Y-%m-%d %H:%M')} UTC")
                time.sleep(max(_sleep_secs, 3600))  # minimum 1hr safety floor
                continue

            # ── Daily close at 19:00 UTC (21:00 Lithuania) ──
            # v165: EOD-fired-today guard. Without this, a bot crash + restart
            # during the 20:28-21:30 window re-triggers EOD close + retrain.
            # State stored in bot_state.json under key "eod_fired_date".
            if is_daily_close():
                global _EOD_ACTIVE
                _today_iso = datetime.now(timezone.utc).date().isoformat()
                _state_eod = load_state()
                if _state_eod.get("eod_fired_date") == _today_iso:
                    # Already EOD'd today -- just sleep until next session
                    log.info(f"EOD already completed today ({_today_iso}) -- sleeping until 00:00 UTC")
                    _now_eod   = datetime.now(timezone.utc)
                    _next_open = _now_eod.replace(hour=0, minute=0, second=0, microsecond=0)
                    if _now_eod >= _next_open:
                        _next_open = _next_open + timedelta(days=1)
                    time.sleep((_next_open - _now_eod).total_seconds())
                    _EOD_ACTIVE = False
                    continue
                # Mark as fired BEFORE running EOD ops so a crash mid-EOD doesn't
                # cause a re-run on restart (we'd rather skip a partial second run
                # than do everything twice).
                _state_eod["eod_fired_date"] = _today_iso
                save_state(_state_eod)

                _EOD_ACTIVE = True  # block ALL new trades immediately
                log.warning("END OF DAY 20:30 UTC (21:30 Lithuania) -- closing ALL positions")
                close_all_positions("end_of_day")
                # close_all_positions handles its own passes and re-fetches each time
                remaining = mt5.positions_get() or []
                if not remaining:
                    log.info("End of day complete -- all positions closed.")
                else:
                    log.error(f"EOD: {len(remaining)} positions STILL open -- close manually in MT5!")

                # ── Midnight ML retrain ──────────────────────────────────────
                # Run fix_outcomes + retrain ML model while market is closed
                _flush_log_queue()  # write pending rejected signals before retrain reads LOG_FILE
                try:
                                        # 1. Fix outcomes from MT5 history
                    history = mt5.history_deals_get(
                        datetime.now(timezone.utc) - timedelta(days=60), datetime.now(timezone.utc))
                    if history and os.path.exists(LOG_FILE):
                        with open(LOG_FILE, encoding="utf-8") as f:
                            trades = json.load(f)

                        closing_deals    = {d.order: d for d in history if d.entry == mt5.DEAL_ENTRY_OUT}
                        position_profit  = {}
                        position_comment = {}
                        for d in history:
                            if d.entry == mt5.DEAL_ENTRY_OUT:
                                pid = d.position_id
                                position_profit[pid]   = position_profit.get(pid, 0) + d.profit
                                position_comment[pid]  = d.comment or ""
                                # ALSO key by d.order -- bot stores order ticket, not position_id
                                # For most trades these are equal, but not always (partials etc.)
                                position_profit[d.order]  = position_profit.get(d.order, 0) + d.profit
                                position_comment[d.order] = d.comment or ""

                        updated = 0
                        for t in trades:
                            if not t.get("placed", True) or not t.get("ticket"):
                                continue
                            ticket = t.get("ticket")
                            entry  = t.get("entry", 0)
                            if t.get("outcome") is not None:
                                continue
                            if ticket in position_profit:
                                profit  = position_profit[ticket]
                                comment = position_comment.get(ticket, "")
                                _classify_outcome(t, profit, comment)
                                updated += 1
                            elif ticket in closing_deals:
                                d       = closing_deals[ticket]
                                profit  = d.profit
                                comment = d.comment or ""
                                _classify_outcome(t, profit, comment,
                                                  deal_time=getattr(d, "time", None),
                                                  deal_price=getattr(d, "price", None))
                                updated += 1

                        if updated > 0:
                            atomic_write(LOG_FILE, trades)
                            update_win_stats(trades)
                            log.info(f"Midnight fix: updated {updated} trade outcomes")

                    # 2. Retrain ML model if scikit-learn available
                    # EOD retrain -- uses same online_retrain() as intraday
                    # Single training path ensures consistency
                    # v155: write retrain.heartbeat so external monitor can see if EOD fired.
                    # Previous behavior swallowed exceptions silently -- model was 7 days
                    # stale in ml_report25 with no warning.
                    _retrain_started_at = datetime.now(timezone.utc)
                    try:
                        with open("retrain.heartbeat", "w", encoding="utf-8") as _hb:
                            _hb.write(f"started={_retrain_started_at.isoformat()}\n")
                    except Exception as _hbe:
                        log.warning(f"retrain.heartbeat write failed: {_hbe}")
                    try:
                        if os.path.exists(LOG_FILE):
                            with open(LOG_FILE, encoding="utf-8") as f:
                                all_trades = json.load(f)
                            n_resolved = sum(1 for t in all_trades
                                           if t.get("placed", True)
                                           and t.get("outcome") in ("win","loss","eod_win","eod_loss","breakeven","eod_breakeven"))
                            log.info(f"EOD retrain: {n_resolved} resolved trades")
                            online_retrain._eod_mode = True   # allow pkl save at EOD only
                            try:
                                online_retrain(all_trades, n_resolved)
                            finally:
                                online_retrain._eod_mode = False  # ALWAYS reset -- even on crash
                            # v155: confirm completion in heartbeat
                            try:
                                _pkl_mtime = os.path.getmtime("ml_model.pkl") if os.path.exists("ml_model.pkl") else 0
                                _pkl_age_s = time.time() - _pkl_mtime if _pkl_mtime else -1
                                with open("retrain.heartbeat", "a", encoding="utf-8") as _hb:
                                    _hb.write(
                                        f"completed={datetime.now(timezone.utc).isoformat()}\n"
                                        f"n_resolved={n_resolved}\n"
                                        f"pkl_age_seconds={_pkl_age_s:.0f}\n"
                                    )
                                # Loud warning if pkl wasn't actually updated (gate rejected)
                                if _pkl_age_s > 3600:
                                    log.error(
                                        f"EOD RETRAIN: pkl is still {_pkl_age_s/3600:.1f}h old "
                                        f"after retrain -- save gate rejected the new model. "
                                        f"Check separation_recent and Turing gap thresholds."
                                    )
                            except Exception as _vfe:
                                log.warning(f"retrain post-check failed: {_vfe}")
                            # Update reversal conditions after retrain
                            if ML_REVERSAL_AUTO:
                                try:
                                    all_setup_keys = set(
                                        f"{t.get('strategy')}|{t.get('setup_name')}"
                                        for t in all_trades
                                        if t.get('strategy') and t.get('setup_name')
                                    )
                                    for sk in all_setup_keys:
                                        ML_REVERSAL_CONFIRMED[sk] = check_reversal_conditions(sk)
                                except Exception as _re:
                                    log.warning(f"Reversal conditions check error: {_re}")
                    except Exception as e:
                        # v155: was log.warning -- promoting to log.exception so the
                        # full traceback hits the log. Silent EOD retrain failures
                        # are how we ended up with a 7-day-old pkl.
                        log.exception(f"EOD retrain FAILED: {e}")
                        try:
                            with open("retrain.heartbeat", "a", encoding="utf-8") as _hb:
                                _hb.write(f"FAILED={datetime.now(timezone.utc).isoformat()}\nerror={e}\n")
                        except Exception:
                            pass

                except Exception as e:
                    log.warning(f"Midnight ML cycle error: {e}")

                # Sleep until 00:00 UTC (01:00 Lithuania) -- session starts at midnight UTC
                now       = datetime.now(timezone.utc)
                next_open = now.replace(hour=0, minute=0, second=0, microsecond=0)
                if now >= next_open:
                    next_open = next_open + timedelta(days=1)
                secs = (next_open - now).total_seconds()
                log.info(f"Sleeping {secs/3600:.1f}hrs until next session (00:00 UTC = 01:00 Lithuania)")
                time.sleep(secs)
                _EOD_ACTIVE = False  # reset flag for next session
                continue

            can_trade, reason = check_safety()
            if not can_trade:
                log.warning(f"SAFETY: {reason}")
                time.sleep(CHECK_INTERVAL)
                continue

            # Hard block: only trade 00:00-20:30 UTC (01:00-21:30 Lithuania)
            now_h = datetime.now(timezone.utc).hour
            now_m = datetime.now(timezone.utc).minute
            _outside_hours = not ((now_h < 20) or (now_h == 20 and now_m < 30))
            if _outside_hours:
                # Outside normal session -- NO data trades, NO signal processing
                # EOD already ran, positions already closed
                # Just sleep until next check -- main loop will hit is_daily_close()
                # and go into the proper sleep cycle
                time.sleep(CHECK_INTERVAL)
                continue
            _outside_hour_data = False  # only set True for genuine overnight data

            log.info(reason)

            # Fast loop (every second) -- critical execution only
            # (update_mfe_mae moved to slow loop -- reads LOG_FILE every call)

            # Slow loop (every 60 seconds) -- expensive MT5 calls
            now_tick = datetime.now(timezone.utc)
            if not hasattr(main, "_last_slow") or (now_tick - main._last_slow).total_seconds() >= 60:
                cancel_old_pending_orders()  # in slow loop -- orders don't change every second
                update_mfe_mae()            # moved to slow loop -- reads LOG_FILE every call
                # Flush rejected-signal log queue -- batches up to 30s of rejections
                import time as _slt
                if (not _log_queue_last_flush or
                        _slt.monotonic() - _log_queue_last_flush > 30):
                    _flush_log_queue()
                manage_brooks_trailing()
                manage_scale_in()
                # v153: init _last_resolved_count to current on first run
                # prevents wasted retrain on every restart (EOD already did it)
                if not hasattr(main, "_last_resolved_count"):
                    try:
                        if os.path.exists(LOG_FILE):
                            with open(LOG_FILE, encoding="utf-8") as _f0:
                                _t0 = json.load(_f0)
                            main._last_resolved_count = sum(1 for t in _t0
                                if t.get("placed", True) and
                                t.get("outcome") in ("win","loss","eod_win","eod_loss","breakeven","eod_breakeven"))
                        else:
                            main._last_resolved_count = 0
                    except Exception:
                        main._last_resolved_count = 0
                prev_resolved = main._last_resolved_count
                update_outcomes()
                # Online learning: retrain if new outcomes appeared
                try:
                    if os.path.exists(LOG_FILE):
                        # PERF: cache LOG_FILE read with 60s TTL -- this runs every slow-cycle
                        # new_resolved count changes at most a few times per hour
                        _now_rt = now_tick.timestamp()
                        if not hasattr(main, '_rt_cache') or (_now_rt - getattr(main, '_rt_cache_ts', 0)) > 60:
                            with open(LOG_FILE, encoding="utf-8") as f:
                                main._rt_cache = json.load(f)
                            main._rt_cache_ts = _now_rt
                        _trades = main._rt_cache
                        new_resolved = sum(1 for t in _trades
                                          if t.get("placed", True)
                                          and t.get("outcome") in ("win","loss","eod_win","eod_loss","breakeven","eod_breakeven"))
                        _last_retrain = getattr(main, "_last_retrain_time", None)
                        _retrain_due = _last_retrain is None or (now_tick - _last_retrain).total_seconds() > 1800
                        if new_resolved > prev_resolved + 20 and _retrain_due:  # max retrain every 30min
                            main._last_resolved_count = new_resolved
                            main._last_retrain_time = now_tick
                            online_retrain(_trades, new_resolved)
                except Exception as _e:
                    log.warning(f"Online learning check error: {_e}")
                main._last_slow = now_tick

            # ── Non-Brooks strategies removed -- Brooks only ──
            # 15m candle, 7th candle, UK100 5m strategies removed
            # Brooks covers all symbols/timeframes with full ML integration

            # ── Brooks: unlimited, adaptive risk, learning, regime-filtered ──
            for symbol in ALL_SYMBOLS:
                # v174: collect signals from both timeframes BEFORE iterating,
                # so cross-tf zone dedup can drop a 5m wedge + 15m wedge at the
                # same level into a single position. Previously each tf was
                # processed independently and both could place trades.
                _all_symbol_sigs = []
                for tf, tf_name in [(TF_5M, "5m"), (TF_15M, "15m")]:
                    _tf_sigs, _tf_mults = run_brooks(symbol, tf, tf_name)
                    _all_symbol_sigs.extend(_tf_sigs)
                # Cross-tf dedup -- one position per zone across all timeframes.
                sigs = dedupe_cross_tf(_all_symbol_sigs)
                # All kept signals trade at full risk (zone_mults always 1.0
                # post-v174 -- split-risk behavior was the bug).
                zone_mults = {i: 1.0 for i in range(len(sigs))}

                for idx, sig in enumerate(sigs):
                    setup_key = f"{sig.strategy}|{sig.setup_name}"

                    # ── HARD TIME BLOCK -- first check, zero cost ─────────────
                    _now_h = datetime.now(timezone.utc).hour
                    if _now_h in _BLOCKED_HOURS:
                        continue  # silent -- no log_rejected_signal to avoid log spam

                    # ── Pre-EOD hard stop -- no new trades 30min before close ──
                    _pre_eod_now = is_pre_eod()  # computed once -- reused below
                    if _pre_eod_now:
                        continue

                    # ── Spread gate -- DATA ONLY, not active yet ──
                    # Will enable at day 14+ once ML has learned spread patterns
                    # ctx["spread_abnormal"] already logged in capture_market_context

                    # ── Random exploration: 20% chance bypass all filters ──
                    is_random_trade = _rnd.random() < RANDOM_EXPLORE_RATE

                    # Sanity check: entry within 3% of current price (demo wider -- data collection)
                    tick = mt5.symbol_info_tick(sig.symbol)
                    if tick:
                        _drift = abs(sig.entry - tick.bid) / tick.bid
                        _thresh = 0.03 if not LIVE_MODE else 0.015
                        if _drift > _thresh:
                            log.info(f"  SKIP {sig.symbol} {sig.setup_name} stale_entry drift={_drift:.1%}")
                            continue

                    # Note: already_brooks_recent is NOT a hard block anymore
                    # ML learns from repeated signals -- cooldown state logged as context feature
                    # setup_wr_last10_symbol already captures recent performance

                    # v155: hard reject disabled setups (proven losers, see DISABLED_SETUPS)
                    if setup_key in DISABLED_SETUPS:
                        log_rejected_signal(sig, f"disabled_setup_{setup_key}", 0, ["v155 DISABLED_SETUPS"])
                        continue

                    # v155: enforce direction lock on asymmetric setups
                    _required_dir = DIRECTION_LOCK.get(sig.setup_name)
                    if _required_dir and sig.direction != _required_dir:
                        log_rejected_signal(
                            sig,
                            f"direction_lock_{sig.setup_name}_only_{_required_dir}",
                            0,
                            [f"v155 DIRECTION_LOCK: {sig.setup_name} {_required_dir}-only"]
                        )
                        continue

                    score, reasons  = score_signal(sig)

                    # v166: minimum score gate -- DEFAULT 0 (no gate).
                    # Set MIN_SCORE_GATE > 0 to enable based on analyzer 6 results.
                    # Random/data trades bypass this check (they fire at micro risk).
                    if (MIN_SCORE_GATE > 0 and
                        not is_random_trade and
                        not _outside_hour_data and
                        score < MIN_SCORE_GATE):
                        log_rejected_signal(sig, f"score_below_gate_{score}_lt_{MIN_SCORE_GATE}", score, reasons)
                        continue

                    base_risk       = adaptive_brooks_risk(setup_key, sig)
                    zone_multiplier = zone_mults.get(idx, 1.0)
                    risk            = round(risk_from_score(base_risk, score) * zone_multiplier, 4)

                    # ── BLIND SPOT FIX 1: Outside trading hours ──────────────
                    # Place micro-risk trade so ML learns overnight/late outcomes
                    if _outside_hour_data and not _pre_eod_now:
                        # v157: skip entirely when DATA_COLLECTION_RISK is 0.
                        # Otherwise place_order receives risk=0 and broker fills
                        # at volume_min (0.01 lot) -- produces hundreds of noise
                        # trades/day that pollute T2 training data and consume
                        # the position cap. Handoff doc identifies this as the
                        # #1 unfixed bug (was scheduled for v159).
                        if DATA_COLLECTION_RISK <= 0.0:
                            log_rejected_signal(sig, f"outside_hours_skip_zero_risk_{sig.setup_name}", score, reasons)
                            continue
                        log.info(f"DATA[outside_hours] {sig.symbol} {sig.setup_name} score={score}/8 risk={DATA_COLLECTION_RISK}%")
                        ticket = place_order(sig, DATA_COLLECTION_RISK)
                        if ticket:
                            # NOT random=True -- real setup direction, just reduced risk
                            # adaptive_brooks_risk set sig._cached_ctx -- pass it through
                            log_signal(sig, ticket, DATA_COLLECTION_RISK, score, reasons,
                                       ctx=getattr(sig, "_cached_ctx", None))
                        continue

                    if is_random_trade and not _pre_eod_now:
                        # Random exploration -- bypass most filters, micro risk
                        # But respect hard total position cap
                        try:
                            _total_open = len(mt5.positions_get() or [])
                        except Exception as _e:
                            log.debug(f"positions_get error (random cap): {_e}")
                            _total_open = 0
                        if _total_open >= MAX_TOTAL_OPEN:
                            log_rejected_signal(sig, f"total_cap_{_total_open}", score, reasons)
                            continue
                        log.info(f"RANDOM [{sig.symbol} {sig.setup_name} score={score}/8 risk={RANDOM_EXPLORE_RISK}%]")
                        ticket = place_order(sig, RANDOM_EXPLORE_RISK)
                        if ticket:
                            log_signal.is_random = True
                            log_signal(sig, ticket, RANDOM_EXPLORE_RISK, score, reasons)
                        continue

                    # ── Normal filters ──
                    # ── BLIND SPOT FIX 2: Cooldown -- place micro-risk instead of skip ──
                    _sig_key = f"{sig.strategy}|{sig.setup_name}"  # defined here -- used by both cooldown AND disable gate below
                    if not check_and_apply_learning(setup_key) and not _pre_eod_now:
                        # Skip data collection entirely for confirmed losers (v105)
                        # Reasoning: 200+ decisive trades at <42% WR = enough data, more = noise
                        if _sig_key in NO_DATA_COLLECTION:
                            log_rejected_signal(sig, f"no_data_collection_{sig.setup_name}", score, reasons)
                            continue
                        # Instead of silent skip, place data trade at micro risk
                        # ML learns: "what happens when we trade a setup in cooldown?"
                        # Cap: don't pile up data trades beyond MAX_TOTAL_OPEN
                        try:
                            _n_open_data = len(mt5.positions_get() or [])
                        except Exception:
                            _n_open_data = 0
                        if _n_open_data >= MAX_TOTAL_OPEN:
                            log_rejected_signal(sig, f"data_cap_{_n_open_data}_open", score, reasons)
                            continue
                        # v157: skip entirely when DATA_COLLECTION_RISK is 0.
                        # Same reason as outside_hours guard above -- handoff #1 bug.
                        if DATA_COLLECTION_RISK <= 0.0:
                            log_rejected_signal(sig, f"cooldown_skip_zero_risk_{sig.setup_name}", score, reasons)
                            continue
                        log.info(f"DATA[cooldown] {sig.symbol} {sig.setup_name} score={score}/8 risk={DATA_COLLECTION_RISK}% open={_n_open_data}/{MAX_TOTAL_OPEN}")
                        ticket = place_order(sig, DATA_COLLECTION_RISK)
                        if ticket:
                            # NOT random=True -- real setup direction, just reduced risk during cooldown
                            # adaptive_brooks_risk set sig._cached_ctx -- pass it through
                            log_signal(sig, ticket, DATA_COLLECTION_RISK, score, reasons,
                                       ctx=getattr(sig, "_cached_ctx", None))
                        else:
                            log_rejected_signal(sig, "cooldown_data_failed", score, reasons)
                        continue

                    # ── Ranging regime: strict range position filter ──
                    current_regime = detect_regime(symbol, tf)
                    skipped_by_range = False
                    # Ranging filter removed on demo -- ML learns from all market conditions
                    # pos_in_range still captured as context feature for ML
                    try:
                        daily = get_candles(symbol, mt5.TIMEFRAME_D1, 2)  # uses 10s cache
                        if daily is not None and len(daily) >= 1:
                            d_high = float(daily.iloc[-1]["high"])
                            d_low  = float(daily.iloc[-1]["low"])
                            d_range = d_high - d_low
                            if d_range > 0:
                                pos_in_range = (sig.entry - d_low) / d_range
                                log.debug(f"  Ranging context: {sig.direction} at {pos_in_range:.0%} of daily range")
                    except Exception as e:
                        log.warning(f"Range context error: {e}")
                    # ── Execution Gates (v104) ───────────────────────────
                    # Hard blocks based on 400k-bar backtest + ml_report14.
                    # These fire BEFORE ML to avoid polluting training data.
                    # NOTE: time block (_BLOCKED_HOURS) was moved to top of
                    # signal loop (before scoring) -- see above.
                    # DISABLE_SETUPS / NO_DATA_COLLECTION are module-level
                    # constants (defined above def main()) -- not rebuilt here.
                    # _sig_key already assigned above before cooldown check
                    # Regime-conditional gate: use REGIME_SETUP_BLOCK when validated,
                    # fall back to hard DISABLE_SETUPS until then.
                    # v159: if regime is unstable (just flipped), default to the
                    # stricter DISABLED_SETUPS list -- don't trust a fresh regime call.
                    if REGIME_GATE_ACTIVE:
                        _regime_for_gate = detect_regime(symbol, tf)  # cached
                        _regime_is_stable = regime_stable(symbol, tf, min_consecutive_checks=3)
                        if _regime_is_stable:
                            _regime_blocks = REGIME_SETUP_BLOCK.get(_regime_for_gate, DISABLED_SETUPS)
                        else:
                            # Unstable regime -- use union of all blocks (most conservative)
                            # This blocks anything that's bad in ANY regime
                            _regime_blocks = DISABLED_SETUPS
                            for _rb in REGIME_SETUP_BLOCK.values():
                                _regime_blocks = _regime_blocks | _rb
                        if _sig_key in _regime_blocks:
                            _block_reason = (f"regime_block_{_regime_for_gate}_{sig.setup_name}"
                                             if _regime_is_stable
                                             else f"regime_unstable_block_{sig.setup_name}")
                            log_rejected_signal(sig, _block_reason, score, reasons)
                            continue
                    elif _sig_key in DISABLED_SETUPS:
                        log_rejected_signal(sig, f"disabled_setup_{sig.setup_name}", score, reasons)
                        continue

                    # ── ML Intelligence Layer ────────────────────────────
                    # Build prediction using current context
                    ml_pred = {"prob": 0.5, "confidence": "none", "votes": 0, "total": 0}
                    _ml_ctx = {}  # safe initialisation -- always defined before ML filters
                    try:
                        # Reuse CMC cached by adaptive_brooks_risk -- same signal, avoids 14 redundant MT5 reads
                        if hasattr(sig, "_cached_ctx") and sig._cached_ctx:
                            _ml_ctx = sig._cached_ctx
                        else:
                            _ml_ctx = capture_market_context(sig)
                        _ml_ctx.update(parse_score_breakdown(reasons))
                        ml_pred = ensemble_predict(_ml_ctx)
                    except Exception as _e:
                        log.debug(f"ML context/predict error: {_e}")

                    # 1. ML Filter -- skip HIGH confidence losses entirely
                    if ML_GATING_ENABLED and ml_should_filter(ml_pred):
                        log_rejected_signal(sig, f"ml_filter_{ml_pred['prob']:.0%}", score, reasons, ctx=_ml_ctx)
                        continue

                    # 1b. ML Minimum entry threshold -- skip if model thinks loss is more likely
                    # Only applies when we have a real prediction (not default 0.5)
                    _ml_prob = ml_pred.get("prob", 0.5)
                    _ml_conf = ml_pred.get("confidence", "none")
                    # ── Dynamic threshold: adjust based on model quality ──────
                    # Base threshold shifts based on recent calibration error
                    # and recent approved-trade win rate.
                    try:
                        import pickle as _dpkl
                        _dyn_thresh = ML_MIN_ENTRY_PROB
                        if os.path.exists("ml_model.pkl"):
                            # PERF: reuse the same 60s TTL cache as ensemble_predict
                            # pkl only changes at EOD retrain -- no need to reload every signal
                            _dens_cached    = getattr(ensemble_predict, "_ensemble_pkl_cache", None)
                            _dens_cached_ts = getattr(ensemble_predict, "_ensemble_pkl_cache_ts", 0)
                            _now_dens       = datetime.now(timezone.utc).timestamp()
                            if _dens_cached is None or (_now_dens - _dens_cached_ts) > 60:
                                with open("ml_model.pkl", "rb") as _dpf:
                                    _dens_cached = _dpkl.load(_dpf)
                                setattr(ensemble_predict, "_ensemble_pkl_cache", _dens_cached)
                                setattr(ensemble_predict, "_ensemble_pkl_cache_ts", _now_dens)
                            _dens = _dens_cached
                            # Calibration quality adjustment -- smoothed to prevent jitter
                            # Raw cal_err can spike on a single retrain -- use EMA to stabilize.
                            # smoothed = 0.7 * previous + 0.3 * current (emphasises history)
                            _cal_err_raw  = _dens.get("platt_cal_err", 0.1) or 0.1
                            _cal_err_prev = _dens.get("cal_err_smoothed", _cal_err_raw) or _cal_err_raw
                            _cal_err = 0.7 * _cal_err_prev + 0.3 * _cal_err_raw
                            # Note: smoothed value is saved back to pkl after retrain (below)
                            if _cal_err > 0.15:
                                _dyn_thresh += 0.05  # model uncertain -> stricter
                            elif _cal_err < 0.08:
                                _dyn_thresh -= 0.03  # well calibrated -> slightly looser
                            # Recent approved-trade performance adjustment
                            # Look at last 20 trades the model passed (prob >= base threshold)
                            # PERF: cache LOG_FILE read with 60s TTL -- this runs every signal evaluation
                            import json as _djson
                            _cache_key = "_dyn_thresh_trades_cache"
                            _cache_ts_key = "_dyn_thresh_cache_ts"
                            _now_cache = datetime.now(timezone.utc).timestamp()
                            _cached = getattr(main, _cache_key, None)
                            _cached_ts = getattr(main, _cache_ts_key, 0)
                            if _cached is None or (_now_cache - _cached_ts) > 60:
                                if os.path.exists(LOG_FILE):
                                    with open(LOG_FILE, encoding="utf-8") as _dlf:
                                        _cached = _djson.load(_dlf)
                                    setattr(main, _cache_key, _cached)
                                    setattr(main, _cache_ts_key, _now_cache)
                            _dall = _cached or []
                            # v157: filter to currently-active symbols only.
                            # Was including GER40/UK100 trade history (lower WR)
                            # which suppressed the dynamic threshold incorrectly.
                            # Now uses only the symbols we actually trade post-v157.
                            _approved = [t for t in _dall[-200:]
                                         if t.get("symbol") in ALL_SYMBOLS
                                         and t.get("context", {}).get("ml_win_prob", 0) >= ML_MIN_ENTRY_PROB - 0.05
                                         and t.get("outcome") in ("win","loss","eod_win","eod_loss")
                                         and not t.get("random", False)
                                         and (t.get("risk_pct") or 0) >= 0.02][-20:]
                            _recent_wr = 0.5  # default -- overwritten if >= 10 approved trades
                            if len(_approved) >= 10:
                                _recent_wr = sum(1 for t in _approved
                                                 if t.get("outcome") in ("win","eod_win")) / len(_approved)
                                if _recent_wr > 0.65:
                                    _dyn_thresh -= 0.03  # model doing well -> more trades
                                elif _recent_wr < 0.45:
                                    _dyn_thresh += 0.05  # model struggling -> fewer trades

                            # Regime-specific adjustment
                            # Model confidence behaves differently across regimes.
                            # Trending: cleaner signals -> lower threshold (trust model more)
                            # Ranging: noisier signals -> higher threshold (be selective)
                            # Volatile: weakest edge -> highest threshold
                            # v165 FIX: was reading "last_regime" from pkl (regime at last
                            # EOD retrain -- could be 12+ hours stale). Now uses current
                            # regime detected on the symbol+tf for THIS signal.
                            try:
                                _regime_now = detect_regime(sig.symbol, tf)
                            except Exception:
                                _regime_now = _dens.get("last_regime", "ranging")
                            if _regime_now in ("trending_bull", "trending_bear"):
                                _dyn_thresh -= 0.02  # cleaner trends = more trustworthy model
                            elif _regime_now == "volatile":
                                _dyn_thresh += 0.05  # highest noise = strictest gate

                            # Hard bounds: never go below base-0.08 or above base+0.12
                            _dyn_thresh = max(ML_MIN_ENTRY_PROB - 0.08,
                                              min(ML_MIN_ENTRY_PROB + 0.12, _dyn_thresh))
                            # v153: only log when threshold meaningfully changed from base (reduces log noise)
                            if abs(_dyn_thresh - ML_MIN_ENTRY_PROB) > 0.015:
                                _dyn_log_key = "_dyn_last_thresh_logged"
                                _dyn_last = getattr(main, _dyn_log_key, None)
                                if _dyn_last != round(_dyn_thresh, 3):
                                    log.info(f"    DYN thresh: {ML_MIN_ENTRY_PROB:.0%}->{_dyn_thresh:.0%} "
                                             f"cal={_cal_err:.3f} wr={_recent_wr:.0%} regime={_regime_now}")
                                    setattr(main, _dyn_log_key, round(_dyn_thresh, 3))
                    except Exception as _dt_e:
                        _dyn_thresh = ML_MIN_ENTRY_PROB
                        log.debug(f"Dynamic threshold error: {_dt_e}")

                    # Apply dynamic threshold (replaces static ML_MIN_ENTRY_PROB check)
                    if ML_GATING_ENABLED and _ml_conf != "none" and _ml_prob < _dyn_thresh:
                        log_rejected_signal(sig, f"ml_below_dyn_{_ml_prob:.0%}", score, reasons, ctx=_ml_ctx)
                        log.info(f"    ML ENTRY BLOCK: {_ml_prob:.0%} < dyn {_dyn_thresh:.0%} -- skipping")
                        continue

                    # ── EV filter: skip negative expected value trades ──
                    # EV = P(win)*RR - P(loss)*1
                    # Catches 52% win / 0.8 RR (gamble). Allows 44% win / 2.5 RR (good bet).
                    try:
                        # _ml_ctx is the context dict built by capture_market_context
                        _rr = float(_ml_ctx.get("rr_ratio", 0) or 0)
                        if _rr <= 0:
                            _rr = abs(float(sig.take_profit - sig.entry)) / max(abs(float(sig.stop_loss - sig.entry)), 0.001)
                        _ev = _ml_prob * _rr - (1.0 - _ml_prob) * 1.0
                        if ML_GATING_ENABLED and _ev <= ML_MIN_EV and _ml_conf != "none":
                            log_rejected_signal(sig, f"ml_neg_ev_{_ev:.3f}", score, reasons, ctx=_ml_ctx)
                            log.info(f"    ML EV BLOCK: EV={_ev:.3f} (P={_ml_prob:.0%} x RR={_rr:.1f}) -- skipping")
                            continue
                    except Exception as _ev_e:
                        log.debug(f"EV filter error: {_ev_e}")

                    # ── Dead market guard ──────────────────────────────────
                    # ATR below historical p5 = market barely moving.
                    # All signals in dead markets are noise -- skip entirely.
                    if _ml_ctx.get("atr_dead_market", 0):
                        log.info(f"    ATR DEAD MARKET: ATR at historic p5 or below -- skipping")
                        continue

                    # 2. ML Reversal -- flip direction if setup is proven loser
                    # (ML_ENABLE_REVERSAL = False by default, manual enable only)
                    setup_stats_for_reversal = get_setup_stats(setup_key)
                    if ml_check_reversal(sig, ml_pred, setup_stats_for_reversal):
                        # Flip direction and swap SL/TP
                        orig_direction = sig.direction
                        if sig.direction == "long":
                            sig.direction  = "short"
                            # entry stays at original price -- signal already computed
                            old_sl         = sig.stop_loss
                            sig.stop_loss  = sig.take_profit  # old TP becomes new SL
                            sig.take_profit = old_sl          # old SL becomes new TP
                        else:
                            sig.direction  = "long"
                            old_sl         = sig.stop_loss
                            sig.stop_loss  = sig.take_profit
                            sig.take_profit = old_sl
                        log.warning(f"  ML REVERSAL active: {orig_direction} -> {sig.direction}")
                        reasons.append(f"ML_REVERSED from {orig_direction}")

                    # 3. ML Dynamic SL/TP adjustment
                    sig = ml_adjust_sltp(sig, ml_pred)

                    # 4. ML Entry timing -- check if current bar is ideal (only when enabled)
                    if ML_ENTRY_TIMING and not ml_entry_timing(sig, tf):
                        # Not ideal bar -- skip this candle, will retry next candle
                        # Do NOT log as rejected signal -- this is just bar timing, not a setup rejection
                        continue

                    # ── Pre-EOD: stop opening new trades 15 min before close ────
                    if _pre_eod_now:
                        log_rejected_signal(sig, "pre_eod_cutoff", score, reasons, ctx=_ml_ctx)
                        continue

                    # ── BLIND SPOT FIX 4: Max open positions overflow ────
                    # v176: count BOTH live positions AND pending orders. Previously
                    # used positions_get() only -- pending orders weren't counted, so
                    # 3 SELL_LIMIT orders for the same setup got placed in 6 minutes
                    # before the first one filled. Also: use magic-number match (202401)
                    # in addition to comment, since some brokers strip comments from
                    # filled positions.
                    # v181: define all_pos/all_orders/_is_brooks BEFORE try block so
                    # downstream per-symbol cap doesn't NameError if MT5 raises.
                    all_pos = []
                    all_orders = []
                    def _is_brooks(item):
                        # Match by magic first (always preserved), comment second (sometimes stripped)
                        if getattr(item, "magic", 0) == 202401:
                            return True
                        cm = getattr(item, "comment", "") or ""
                        return "brooks" in cm or "BROOKS" in cm
                    try:
                        all_pos = mt5.positions_get() or []
                        all_orders = mt5.orders_get() or []  # pending orders not yet filled
                        n_brooks_open = sum(1 for p in all_pos if _is_brooks(p))
                        n_brooks_pending = sum(1 for o in all_orders if _is_brooks(o))
                        n_brooks_total = n_brooks_open + n_brooks_pending
                    except Exception as _e:
                        log.debug(f"n_brooks count error: {_e}")
                        n_brooks_open = 0
                        n_brooks_pending = 0
                        n_brooks_total = 0

                    if n_brooks_total >= MAX_BROOKS_OPEN:
                        if DATA_COLLECTION_RISK <= 0.0:
                            log_rejected_signal(sig, f"overflow_{n_brooks_total}_open", score, reasons, ctx=_ml_ctx)
                            continue
                        # Reuse all_pos already fetched -- avoid second positions_get() call
                        _total_open = len(all_pos)
                        if _total_open >= MAX_TOTAL_OPEN:
                            log_rejected_signal(sig, f"total_cap_{_total_open}", score, reasons, ctx=_ml_ctx)
                            # v153: log once per minute when at cap (not every signal)
                            _cap_key = "_cap_logged_min"
                            _now_min = datetime.now(timezone.utc).replace(second=0, microsecond=0)
                            if getattr(main, _cap_key, None) != _now_min:
                                log.info(f"  AT POSITION CAP: {_total_open}/{MAX_TOTAL_OPEN} open -- blocking all new trades")
                                setattr(main, _cap_key, _now_min)
                            continue
                        log.info(f"DATA[overflow] {sig.symbol} {sig.setup_name} score={score}/8 open={n_brooks_total} risk={DATA_COLLECTION_RISK}%")
                        ticket = place_order(sig, DATA_COLLECTION_RISK)
                        if ticket:
                            # NOT random=True -- real setup direction, just reduced risk at overflow
                            log_signal(sig, ticket, DATA_COLLECTION_RISK, score, reasons, ctx=_ml_ctx)
                        else:
                            log_rejected_signal(sig, f"overflow_{n_brooks_total}_open", score, reasons, ctx=_ml_ctx)
                        continue

                    # v165 FIX: enforce MAX_PER_SYMBOL -- was defined but unused since v153.
                    # v176: count pending orders too. Same-symbol pending SELL_LIMITs
                    # were invisible to mt5.positions_get(), so 3 same-symbol orders
                    # could queue up before any filled.
                    try:
                        _same_symbol_open = sum(1 for p in all_pos
                                                if p.symbol == sig.symbol and _is_brooks(p))
                        _same_symbol_pending = sum(1 for o in all_orders
                                                   if o.symbol == sig.symbol and _is_brooks(o))
                        _same_symbol_total = _same_symbol_open + _same_symbol_pending
                    except Exception as _e:
                        log.debug(f"per-symbol count error: {_e}")
                        _same_symbol_total = 0
                    if _same_symbol_total >= MAX_PER_SYMBOL:
                        log_rejected_signal(sig,
                            f"per_symbol_cap_{sig.symbol}_{_same_symbol_total}",
                            score, reasons, ctx=_ml_ctx)
                        continue

                    # v176: same-setup-at-same-level dedup.
                    # Brooks 15m setups persist across multiple 5m iterations, so the
                    # bot was placing 3 identical pending orders for the same level
                    # within minutes. The MAX_PER_SYMBOL cap can't catch this because
                    # mt5.positions_get() doesn't include pending orders, so each
                    # iteration looked like there were 0 same-symbol positions.
                    # Cache by (symbol, strategy, setup_name, direction, price_bucket)
                    # for 15 minutes -- enough for a 15m candle to fully form/break.
                    # price_bucket = entry rounded to 0.1% so micro-different ticks
                    # don't bypass the cache.
                    # Cache by (symbol, strategy, setup_name, direction, price_bucket)
                    # for 15 minutes -- enough for a 15m candle to fully form/break.
                    # price_bucket: entry rounded to 0.1% of entry value, so micro-different
                    # ticks don't bypass the cache, but genuinely different price levels do.
                    _bucket_size = max(sig.entry * 0.001, 0.01)
                    _recent_key = (sig.symbol, sig.strategy, sig.setup_name, sig.direction,
                                   round(sig.entry / _bucket_size))
                    _recent_seen = getattr(main, "_recent_placed", {})
                    _recent_now_ts = datetime.now(timezone.utc).timestamp()
                    _recent_last_ts = _recent_seen.get(_recent_key, 0)
                    if _recent_now_ts - _recent_last_ts < 900:  # 15 min
                        log_rejected_signal(
                            sig,
                            f"recent_dup_{int(_recent_now_ts - _recent_last_ts)}s_ago",
                            score, reasons, ctx=_ml_ctx,
                        )
                        continue
                    # Note: we set _recent_seen AFTER successful placement (below)
                    # so a failed order doesn't lock out a retry.

                    # Skip if risk too small -- would fire at broker minimum lot
                    # This happens when zone multiplier divides risk below meaningful level
                    if risk < 0.015:
                        log_rejected_signal(sig, f"risk_too_small_{risk:.4f}pct", score, reasons, ctx=_ml_ctx)
                        continue
                    # Hard reject if RR < 1.0 -- never risk more than potential reward
                    _sl_d = abs(sig.entry - sig.stop_loss)
                    _tp_d = abs(sig.take_profit - sig.entry)
                    if _sl_d > 0 and _tp_d / _sl_d < 1.0:
                        log_rejected_signal(sig, f"inverted_rr_{_tp_d/_sl_d:.2f}", score, reasons, ctx=_ml_ctx)
                        continue
                    log.info(f"BROOKS {sig.symbol} {sig.strategy} {sig.setup_name} score={score}/8 risk={risk}% RR={_tp_d/_sl_d:.2f}{' (zone-reduced)' if zone_multiplier < 1.0 else ''}")
                    for r in reasons: log.info(f"  {r}")
                    ticket = place_order(sig, risk)
                    if ticket:
                        log_signal(sig, ticket, risk, score, reasons, ctx=_ml_ctx)
                        # v176: record successful placement so duplicates are blocked
                        _recent_seen[_recent_key] = _recent_now_ts
                        # Bound the cache -- purge entries older than 1 hour
                        if len(_recent_seen) > 100:
                            _recent_seen = {k: v for k, v in _recent_seen.items()
                                            if _recent_now_ts - v < 3600}
                        setattr(main, "_recent_placed", _recent_seen)
                    else:
                        log_rejected_signal(sig, "order_failed", score, reasons, ctx=_ml_ctx)

        except Exception as e:
            log.exception(f"Error: {e}")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    import sys as _sys
    # v162: --check-mt5 connects to MT5, prints account info, exits.
    # Use this to verify credentials WITHOUT starting trading. Run as:
    #   python bot.py --check-mt5
    if "--check-mt5" in _sys.argv:
        log.info("=" * 70)
        log.info("v162 CONNECTION TEST -- connecting to MT5 then exiting")
        log.info(f"  Login:  {MT5_LOGIN}")
        log.info(f"  Server: {MT5_SERVER}")
        log.info(f"  Password length: {len(MT5_PASSWORD)} chars")
        log.info("=" * 70)
        if connect_mt5():
            try:
                _info = mt5.account_info()
                if _info is not None:
                    log.info(f"  CONNECTED -- balance=${_info.balance:,.2f}  equity=${_info.equity:,.2f}")
                    log.info(f"  Account holder: {_info.name}")
                    log.info(f"  Currency: {_info.currency}")
                    log.info(f"  Leverage: 1:{_info.leverage}")
                    log.info("CONNECTION TEST PASSED -- safe to run `python bot.py` for real")
                else:
                    log.error("Connected but account_info() returned None")
            finally:
                try: mt5.shutdown()
                except Exception: pass
        else:
            log.error("CONNECTION TEST FAILED -- see errors above")
        _sys.exit(0)
    main()
