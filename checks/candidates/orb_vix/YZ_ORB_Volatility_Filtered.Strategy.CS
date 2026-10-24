using System;
using System.Drawing;
using PowerLanguage.Function;
using ATCenterProxy.interop;

namespace PowerLanguage.Strategy {

    // =====================================================================================
    // YZ_ORB_Volatility_Filtered  —  STEPS 1+2+3+4+5: Volatility-Qualified, Close-Based ORB
    //                                with a Scaled + ATR-Trailed Runner
    // -------------------------------------------------------------------------------------
    // Institutional Opening Range Breakout, built iteratively (one protocol step at a time).
    // THIS FILE IS STEPS 1+2+3+4+5:
    //   * Identify the 15-minute Opening Range (high/low) of the RTH session (09:30-09:45 ET).
    //   * DAY GATE (Step 4) — evaluated ONCE when the OR completes (~09:45 ET), latched for
    //     the day; failing the gate blocks ALL entries that day (red on-chart label says why;
    //     an unevaluated day is blocked too — fail closed):
    //       - VIX GATE: the VIX reading must satisfy VixMin <= VIX <= VixMax (default band
    //         15-30, inclusive; protocol 16-25). The LIVE intraday VIX from data2 = VIX 5-MIN (the bar
    //         aligned with the 09:45 data1 close) — the morning VIX in backtest, the latest
    //         live value. Blocks as STALE unless the bar is from TODAY (ET) — CBOE holidays
    //         / feed outages must not pass on an old reading.
    //   * ENTRY (Step 3): only the candle that actually BREAKS an OR line can enter — it
    //     must CLOSE strictly above the OR-High (long) / below the OR-Low (short) while the
    //     PREVIOUS bar's close had not broken that level (a close-cross). Touches/wicks
    //     never enter, and neither do bars merely drifting along beyond an already-broken
    //     level. Entry is a market order filled at the NEXT bar's open (signal-on-close
    //     semantics).
    //   * STOP LOSS (Step 4/5): the FULL-position stop walks through three states (precedence
    //     trail > break-even > frozen), re-sent every bar via the FromAll stop:
    //       1. FROZEN buffered base — base = the OPPOSITE OR edge (long below OR-Low, short
    //          above OR-High; the classic full-range stop), widened by StopAtrBufferMult x
    //          ATR(StopAtrLength) (protocol: 0.25 x ATR(14); 0 disables). FROZEN at the entry
    //          bar (a hard stop — never re-derived), tick-rounded. R := |entry - this stop|.
    //       2. BREAK-EVEN — once the open profit reaches BreakevenAtR x R (default 1R; 0
    //          disables), the stop moves to the actual entry fill. This is INDEPENDENT of the
    //          scale, so it can arm BEFORE T1 fills.
    //       3. ATR TRAIL (the runner) — once T1 scales, an ATR chandelier seeded at break-even
    //          that ratchets OUTWARD only: long = highest (High - TrailAtrMult x ATR), short =
    //          lowest (Low + TrailAtrMult x ATR), over ATR(TrailAtrLength). Never loosens.
    //   * TAKE PROFIT / SCALE (Step 5): ONE scale-out at T1 = entry +/- TargetORMult x OR size
    //     (protocol: 1.0x) for ceil(qty/2) (~50%). There is NO second target — the remaining
    //     ~50% (the runner) is managed by the ATR trail above, to let winners run. (Was Step-4
    //     two-tranche T1/T2; T2 has been removed.)
    //   * TRADE DIRECTION (Step 5): TradeLongs / TradeShorts gate which side may enter (default
    //     longs ON, shorts OFF). A disabled side still draws the OR box and day-gate label — only
    //     its entry order is withheld.
    //   * POSITION SIZING (Step 6 preview) — constant-dollar risk, ALWAYS ON: the entry quantity
    //     is sized so a stop-out risks ~RiskDollars (default $1000). Contracts =
    //     floor(RiskDollars / (stopDistance x BigPointValue)), capped at MaxContracts (default 4).
    //     stopDistance is THIS strategy's real (wide, full-range) stop distance — |close - (the
    //     opposite OR edge -/+ ATR buffer)| at the breakout close — NOT a generic ATR x multiplier,
    //     so the dollars actually at risk track the stop the trade really uses. The math is the
    //     reusable YZ_RiskPositionSize function. If even one contract would risk more than
    //     RiskDollars (a very wide OR), size is 0 and the trade is SKIPPED (never exceed the cap).
    //   * TIME EXIT (Step 5, now CONDITIONAL): a position that has NOT scaled flattens at 12:00
    //     PM ET (the noon exit) so nothing flat-out is held into the midday trough. A scaled
    //     RUNNER ignores noon and runs until its ATR trail is hit OR the SESSION CLOSE
    //     (SessionCloseTimeET, default 16:30 ET) — the runner's backstop flatten.
    //   * One trade per day.
    //   * Verification drawings: OR-High/Low/midpoint lines; a once-per-day FILTERS label at
    //     the box's top-left (green "FILTERS OK | VIX 18.4 @09:45" or
    //     red "DAY BLOCKED | <reasons>"); and while a trade is on: the T1 line (blue dashed)
    //     and the ACTIVE stop line (orange — frozen base, then a break-even / trailing staircase).
    //
    // OUT OF SCOPE here (later protocol steps): the Apex daily-loss kill switch (Step 6).
    // Constant-dollar-risk sizing (also Step 6) is PREVIEWED here and always on — see POSITION
    // SIZING above. (The Step-5 work in this file is the scaled + ATR-trailed runner plus the
    // long/short toggles; any fast-alpha pullback ENTRY remains a separate future effort.)
    //
    // CHART / STRATEGY-PROPERTIES SETUP REQUIRED BY STEPS 4-5:
    //   - data1: ES 5-min, 24h/Globex session — the session must carry bars through the runner's
    //     SessionCloseTimeET (default 16:30 ET) so the backstop flatten can fire.
    //   - data2: VIX 5-MIN (only when UseVixFilter=true) — the intraday reading aligned with
    //     the 09:45 data1 close. The data range must reach the PRESENT (an ended range reads
    //     as a stale bar and blocks every later day). Backtest days before the loaded VIX
    //     history begins are blocked as stale/missing — by design.
    //   - Strategy Properties: the trade-size field is IGNORED for entries now — the entry
    //     quantity is risk-sized in code (Contracts.UserSpecified). Set RiskDollars / MaxContracts
    //     instead. The scale + runner needs a sized qty >= 2 (a sized qty of 1 takes the whole
    //     position at T1 -> no runner, no trail — documented below); pick RiskDollars high enough
    //     that typical OR widths size to >= 2. A multi-data signal does not start until EVERY
    //     series has MaxBarsBack bars, so keep MaxBarsBack modest (~20).
    //
    // TIMEZONE HANDLING (the key to "always 9:30 ET"):
    //   Bars.Time[0] is in the CHART's display timezone, and MultiCharts exposes no UTC accessor.
    //   So we convert every bar chart-zone -> US Eastern via the reusable YZ_TimeZoneConvert
    //   function (System.TimeZoneInfo, auto-handles EST/EDT) and run ALL time logic against the
    //   Eastern result. The opening range is therefore anchored to 09:30 ET no matter the chart tz.
    //   Set SourceTimeZoneId to the Windows zone your chart shows:
    //       chart in CME/Exchange time -> "Central Standard Time"  (default; CT)
    //       chart in New York time     -> "Eastern Standard Time"  (conversion becomes identity)
    //       chart in GMT/UTC           -> "UTC"
    //   Drawing coordinates still use the raw chart time, so the box lands on the chart axis.
    //
    // Other design notes (verified against live MultiCharts .NET docs + built-in studies):
    //   - Bars.Time[0] is the bar's CLOSE time. On a 5-min chart the 09:30-09:45 ET OR is the
    //     bars whose ET close is 09:35/09:40/09:45, so the window test is (t > start && t <= orEnd).
    //   - IOG disabled: code runs on bar close. There are NO resting entry orders; the exit
    //     bracket (stop/limits) fills INTRABAR at its level (built-in pattern _StpOrLim_Exit /
    //     ATR_Trgt_And_Trail_LX). Exit orders auto-cancel unless re-sent every bar.
    //   - Multi-data: BarsOfData(n) -> IInstrument, refs cached in StartCalc; IsExist(n)
    //     guards a missing series (pattern: Portfolio_Rank_Signal_Base). The VIX 5-min
    //     reading is taken at the 09:45 data1 close; converting its stamp to ET before the
    //     staleness date-compare keeps a raw chart-tz compare from breaking when the session
    //     crosses midnight in the chart's zone.
    //   - Partial exits: IOrderPriced.Send(price, qty) with Contracts.UserSpecified (built-in
    //     pattern _StpOrLim_Exit); the T1 scale uses its OWN order object, separate from the
    //     stop, so the legs never collide; the full-size FromAll stop always covers exactly the
    //     remaining position (backtest engine resolves a same-bar T1-then-stop sweep without
    //     over-fill).
    //   - this.AverageTrueRange(len) computes on data1 ONLY (no multi-data overload exists) —
    //     used both for the FROZEN entry buffer and for the RUNNER TRAIL (the latter recomputed
    //     each bar, by design — a trail must breathe with current volatility). Its first lazy
    //     call can re-run StartCalc — StartCalc stays idempotent.
    //   - Chart uses a 24-hour/Globex session; the RTH open is found by ET time-of-day, and
    //     daily state resets on ET calendar-date change (ET midnight, before the OR window).
    //
    // Known limitations (accepted by design or resolved in later steps):
    //   - STOP MOVES ARM ONE BAR LATE: the break-even and trail triggers read the bar's
    //     High/Low and the scale is only OBSERVABLE at that bar's close, so the updated stop is
    //     re-sent from the NEXT bar — during the trigger bar the prior stop still stands.
    //     IOG-disabled latency, deliberate — same family as the entry-bar-unprotected note below.
    //   - ENTRY BAR UNPROTECTED: exits are first SENT at the entry bar's close, so they only
    //     work from the bar AFTER the entry bar. Deliberate — it also guarantees the
    //     one-trade/day latch can never be skipped by an intrabar round trip.
    //   - Odd lots / qty=1: T1 takes ceil(qty/2) (the larger half on odd lots). qty=1 -> T1 is
    //     the whole position, the scale never latches, and there is NO runner or trail — the
    //     position simply exits at T1 or the NOON flatten.
    //   - Early-history days are BLOCKED (red label) on all days before the loaded VIX
    //     (data2) history begins. Loud by design — lengthen the VIX history rather than
    //     trusting silent gaps.
    //   - VIX reading semantics: the 5-min VIX read at the 09:45 close uses the latest data2
    //     bar. Live, that just-ending VIX bar may not be closed yet, so live can read the
    //     09:40 bar where the backtest reads 09:45 — the label prints the bar's ET stamp, so
    //     every gate decision stays auditable on the chart.
    //   - VIX backfill: if a live morning had no VIX data (gate blocked, no trade) and the
    //     vendor backfills it later, a recalc can flip the historical verdict and replay a
    //     trade live execution never took. Inherent to gating on late-arriving data — keep
    //     position-mismatch alerts ON when live; the timestamped label is the audit trail.
    //   - LIVE over-fill window: orders rest at the broker with quantities fixed at send
    //     time, so during the T1-fill bar the resting stop is still full-size until the
    //     next-bar re-send. The backtest engine is immune. Verify the broker plugin's OCO /
    //     auto-cancel behavior in Market Data Sim before going live (Step 6 scope).
    //   - Carried position past ET midnight (live noon-exit failure): the date-flip reset
    //     flattens it immediately with a red "CARRIED POSITION FLATTENED" label instead of
    //     managing yesterday's position with reset state (which would have NO stop). One
    //     attempt at the flip bar; deeper failures are MC position-sync territory.
    //   - Last-candidate edge: a candidate closing on the last pre-noon bar fills at the
    //     noon bar's open and is flattened at that bar's close — a one-bar trade with no
    //     bracket working intrabar (only the noon flatten covers it).
    //   - RUNNER TRAIL conventions: the trail recomputes ATR(TrailAtrLength) EACH bar (it must
    //     breathe with volatility), unlike the frozen entry buffer. It is a RATCHET — the stop
    //     LEVEL only tightens (long up / short down) and is floored at break-even, so a later
    //     ATR expansion can never widen the live stop. Seeded at break-even on the scale bar.
    //   - RUNNER held into the afternoon: a scaled runner is EXEMPT from the noon flatten and
    //     can stay on for hours; it exits at the trail or the SessionCloseTimeET backstop
    //     (16:30 ET). If that session-close bar is missing (thin / holiday feed), the
    //     ET-midnight carried-position safety flatten is the final backstop.
    //   - BREAK-EVEN vs the scale: BreakevenAtR moves the stop to break-even independently of
    //     T1. With R ≈ the full OR width, 1R sits just beyond T1, so on most winners the trail
    //     (seeded at break-even on the scale) takes over before the 1R arm matters; lower
    //     BreakevenAtR (e.g. 0.5) to tighten to break-even sooner, before any scale.
    //   - Cross is measured close-to-close, not by candle color (rare gap opens can make a
    //     counter-colored candle the breaking candle — the trigger is the close's position).
    //   - Both levels in one bar resolve by MC's intra-bar path assumption (O-H-L-C or
    //     O-L-H-C), not true first-touch. Enable Bar Magnifier for spot checks.
    //   - Half-tick rounding: stop/target/trail prices snap to the tick grid via RoundToTick
    //     (half-tick rounds away from zero). The gray midline is a raw geometric-midpoint
    //     reference only and is NOT the stop — the orange line is (the frozen buffered base,
    //     then break-even, then the ATR trail).
    //   - Full-range stop risk: risk per trade spans the full OR (entry is just beyond one
    //     OR edge, stop beyond the other, plus the buffer) — roughly DOUBLE a midpoint
    //     stop. The constant-dollar-risk sizing above accounts for this directly: it sizes off
    //     THIS wide stop distance, so the wide stop just means fewer contracts, not more risk.
    //   - Gap-throughs (exit bracket): stop/limit fills at the bar's open beyond the level
    //     (standard). Targets are measured from the ACTUAL fill (AvgEntryPrice), so a gapped
    //     entry shifts the bracket with it. A long fill gapping below the buffered stop
    //     simply exits at the next open — the bracket cannot invert.
    //   - ATR conventions (documented decisions): the frozen buffer uses the ENTRY bar's
    //     ATR (includes the entry bar's own range — ATR_Trgt_And_Trail_LX precedent;
    //     recompute-per-bar and signal-bar variants were rejected: the protocol calls it a
    //     hard stop). The ATR is a SIMPLE average of TrueRange (MC's built-in convention —
    //     verifiable against the stock ATR indicator; Wilder smoothing would read a few
    //     percent different). The 5-min ATR for entries before ~10:40 ET reaches back into
    //     quieter pre-RTH bars, slightly deflating the buffer.
    //   - SIZING IS ESTIMATED ONE BAR EARLY: a MarketNextBar order's quantity is fixed at the
    //     candidate's close, but the fill is the next bar's open and the realized stop
    //     (m_frozenStopPx) uses the entry-bar ATR. So the size uses the close as a fill proxy
    //     and the candidate-bar ATR for the buffer; a stop-out therefore risks ~RiskDollars, not
    //     exactly (entry-bar gap + one-bar ATR drift). Inherent to next-bar-fill sizing.
    //   - SIZE-SKIP does NOT consume the one-trade/day latch (no position was taken), so a later
    //     fresh close-cross — typically the opposite side — can still enter that day. A same-
    //     direction re-trigger remains impossible (EvaluateBreakoutCandidate needs a fresh cross).
    //   - MaxContracts is a hard ceiling (default 4), not a parameter to optimize; it also caps a
    //     degenerate near-zero stop distance (thin early bars) from sizing to an absurd quantity.
    //   - RoundToTick stays a private helper: the repo factor-out rule triggers when a
    //     second STUDY needs it, and this is still the only consumer.
    // =====================================================================================
    [IOGMode(IOGMode.Disabled)]
    public class YZ_ORB_Volatility_Filtered : SignalObject {

        // ---- Inputs (Steps 1-3) ----
        [Input] public int    SessionStartTimeET { get; set; } // RTH open, HHMM in US Eastern
        [Input] public int    ORRangeMinutes     { get; set; } // opening-range duration (min)
        [Input] public int    ExitTimeET         { get; set; } // noon flatten (non-runner positions), HHMM in US Eastern
        [Input] public double TargetORMult       { get; set; } // T1 distance = this x OR size (protocol: 1.0; ~50% scales out)
        [Input] public bool   ShowORLines        { get; set; } // draw OR-High/Low/mid (+ trade) lines
        [Input] public string SourceTimeZoneId   { get; set; } // Windows tz the chart displays

        // ---- Inputs (Step 4) ----
        [Input] public bool   UseVixFilter       { get; set; } // gate the day on VIX (needs data2 = VIX 5-min)
        [Input] public double VixMin             { get; set; } // VIX floor, inclusive (default 15; protocol 16)
        [Input] public double VixMax             { get; set; } // VIX ceiling, inclusive (default 30; protocol 25)
        [Input] public int    VixDataStream      { get; set; } // chart data# carrying VIX
        [Input] public double StopAtrBufferMult  { get; set; } // protocol: 0.25 x ATR beyond the stop base (0 disables the buffer)
        [Input] public int    StopAtrLength      { get; set; } // protocol: 14 (on this 5-min data1)
        [Input] public bool   ShowFilterLabels   { get; set; } // draw the once-per-day FILTERS OK / DAY BLOCKED label

        // ---- Inputs (Step 6 preview: constant-dollar-risk position sizing) ----
        // Sizing is ALWAYS on: each entry is sized so a stop-out risks ~RiskDollars (see header).
        [Input] public double RiskDollars        { get; set; } // dollars risked per trade (protocol: 1000)
        [Input] public int    MaxContracts       { get; set; } // hard ceiling on sized contracts (also caps a near-zero-stop blowup)

        // ---- Inputs (Step 5 trade management: scale + break-even + ATR-trailed runner) ----
        [Input] public bool   TradeLongs         { get; set; } // take long breakouts
        [Input] public bool   TradeShorts        { get; set; } // take short breakouts
        [Input] public double BreakevenAtR       { get; set; } // move stop to break-even at this x R (R = entry->initial-stop); 0 disables
        [Input] public double TrailAtrMult       { get; set; } // runner trail = this x ATR(TrailAtrLength) below the high / above the low
        [Input] public int    TrailAtrLength     { get; set; } // ATR length for the runner trail (on this 5-min data1)
        [Input] public int    SessionCloseTimeET { get; set; } // runner backstop flatten, HHMM in US Eastern (RTH close)

        // ---- Order objects ----
        private IOrderMarket m_LE;     // long entry  : market at next bar's open after a qualifying close
        private IOrderMarket m_SE;     // short entry : market at next bar's open after a qualifying close
        private IOrderMarket m_LX;     // long exit   : flatten all at noon / session close (and date-flip safety)
        private IOrderMarket m_SX;     // short exit  : flatten all at noon / session close (and date-flip safety)
        private IOrderPriced m_LXStop; // long exit   : sell-stop, buffered base -> break-even -> ATR trail (full size)
        private IOrderPriced m_SXStop; // short exit  : cover-stop, buffered base -> break-even -> ATR trail (full size)
        private IOrderPriced m_LXT1;   // long exit   : sell-limit  T1, ceil(qty/2)
        private IOrderPriced m_SXT1;   // short exit  : cover-limit T1, ceil(qty/2)

        // ---- Per-day state ----
        private double   m_orHigh;
        private double   m_orLow;
        private DateTime m_orStartTime;  // CHART-tz time of the first OR bar (drawing left edge)
        private DateTime m_curDay;       // ET calendar day currently being tracked
        private bool     m_tradedToday;  // one-shot latch: once we hold a position, no re-entry

        // ---- Per-day day-gate state (Step 4) ----
        private bool     m_filtersDone;     // gates evaluated once at OR completion
        private bool     m_dayGo;           // FAIL-CLOSED: false (incl. unevaluated) blocks all entries
        private string   m_blockReason;     // human-readable reason(s) for the label
        private double   m_vixReading;      // VIX value captured at evaluation (label)
        private DateTime m_vixStamp;        // ET stamp of the VIX bar used (staleness + label)
        private bool     m_filterLabelDone; // once-per-day guard for the filters label

        // ---- Per-trade state (Step 4; one trade/day) ----
        private VariableSeries<int> m_mp;   // MarketPosition series: entry & scale detection
        private int      m_entryQty;        // contracts at the entry bar's close
        private double   m_entryFill;       // AvgEntryPrice at entry (BE level; partial exits don't move it)
        private double   m_frozenStopPx;    // stop base -/+ buffer, FROZEN at the entry bar, tick-rounded
        private bool     m_beArmed;         // open profit reached BreakevenAtR x R -> stop moves to break-even
        private bool     m_scaled;          // T1 partial SEEN at a bar close -> runner: ATR trail, run past noon
        private double   m_trailStop;       // runner's ratcheting ATR trail level (seeded at BE on the scale)

        // ---- Per-bar breakout-candidate state (Step 3) ----
        // Written once per bar by EvaluateBreakoutCandidate; consumed by the entry sender,
        // so the signal logic lives in exactly one place.
        private int    m_candDir;  // +1 long candidate, -1 short candidate, 0 none

        // ---- Derived session times (ET) ----
        private TimeSpan m_startTS;
        private TimeSpan m_orEndTS;
        private TimeSpan m_exitTS;          // noon flatten (non-runner)
        private TimeSpan m_sessionCloseTS;  // runner backstop flatten (RTH close)

        // ---- Timezone conversion (delegated to the reusable YZ_TimeZoneConvert function) ----
        private YZ_TimeZoneConvert m_etTime; // converts each bar's time to US Eastern

        // ---- Position sizing (delegated to the reusable YZ_RiskPositionSize function) ----
        private YZ_RiskPositionSize m_sizer; // contracts = RiskDollars / (stop distance x BigPointValue)

        // ---- Cached secondary stream (StartCalc; null = filter off) ----
        private IInstrument m_vixData;   // VIX 5-min (data2 by default)

        // ---- Drawing ----
        private ITrendLineObject m_lnHigh;
        private ITrendLineObject m_lnLow;
        private ITrendLineObject m_lnMid;
        private ITrendLineObject m_lnTgt;    // T1 line (blue dashed)
        private ITrendLineObject m_lnStop;   // ACTIVE stop line (orange; buffered -> BE -> trailing)
        private double           m_lnStopPx; // last drawn stop price (BE jump -> new segment)

        public YZ_ORB_Volatility_Filtered(object _ctx) : base(_ctx) {
            SessionStartTimeET = 930;
            ORRangeMinutes     = 15;
            ExitTimeET         = 1200;
            TargetORMult       = 1.0;                     // protocol: T1 at 1.0x OR size
            ShowORLines        = true;
            SourceTimeZoneId   = "Central Standard Time"; // chart displays CME exchange (CT)

            UseVixFilter       = true;                    // protocol Step 4: VIX regime gate
            VixMin             = 15;                       // widened default (protocol: 16)
            VixMax             = 30;                       // widened default (protocol: 25)
            VixDataStream      = 2;                       // VIX 5-min (intraday morning reading)
            StopAtrBufferMult  = 0.25;                    // protocol Step 4: stop buffer
            StopAtrLength      = 14;
            ShowFilterLabels   = true;

            RiskDollars        = 1000;                    // constant-dollar-risk sizing target
            MaxContracts       = 4;                       // hard ceiling on sized contracts

            TradeLongs         = true;                    // Step 5: longs on by default
            TradeShorts        = false;                   // Step 5: shorts off by default
            BreakevenAtR       = 1.0;                     // move to break-even at 1R
            TrailAtrMult       = 4.0;                     // runner trail at 4x ATR
            TrailAtrLength     = 14;
            SessionCloseTimeET = 1630;                    // runner backstop flatten (RTH close)
        }

        protected override void Create() {
            // Entries are risk-sized -> quantity given at Send time -> Contracts.UserSpecified.
            m_LE = OrderCreator.MarketNextBar(
                new SOrderParameters(Contracts.UserSpecified, "ORB_LE", EOrderAction.Buy));
            m_SE = OrderCreator.MarketNextBar(
                new SOrderParameters(Contracts.UserSpecified, "ORB_SE", EOrderAction.SellShort));
            m_LX = OrderCreator.MarketThisBar(
                new SOrderParameters(Contracts.Default, "ORB_LX", EOrderAction.Sell,        OrderExit.FromAll));
            m_SX = OrderCreator.MarketThisBar(
                new SOrderParameters(Contracts.Default, "ORB_SX", EOrderAction.BuyToCover,  OrderExit.FromAll));
            m_LXStop = OrderCreator.Stop(
                new SOrderParameters(Contracts.Default, "ORB_Stop_LX", EOrderAction.Sell,       OrderExit.FromAll));
            m_SXStop = OrderCreator.Stop(
                new SOrderParameters(Contracts.Default, "ORB_Stop_SX", EOrderAction.BuyToCover, OrderExit.FromAll));
            // T1 scale-out (Step 4/5): quantity given at Send time -> Contracts.UserSpecified.
            // A SEPARATE order object from the stop so the legs never collide.
            m_LXT1 = OrderCreator.Limit(
                new SOrderParameters(Contracts.UserSpecified, "ORB_T1_LX", EOrderAction.Sell,       OrderExit.FromAll));
            m_SXT1 = OrderCreator.Limit(
                new SOrderParameters(Contracts.UserSpecified, "ORB_T1_SX", EOrderAction.BuyToCover, OrderExit.FromAll));

            m_mp     = new VariableSeries<int>(this);
            m_etTime = new YZ_TimeZoneConvert(this);
            m_sizer  = new YZ_RiskPositionSize(this);
        }

        protected override void StartCalc() {
            // StartCalc can run twice (a recalc/refresh re-enters it) — keep it idempotent.
            m_startTS        = FromHHMM(SessionStartTimeET);
            m_orEndTS        = m_startTS + TimeSpan.FromMinutes(ORRangeMinutes);
            m_exitTS         = FromHHMM(ExitTimeET);
            m_sessionCloseTS = FromHHMM(SessionCloseTimeET);

            // Anchor all time logic to US Eastern via the reusable YZ_TimeZoneConvert function.
            m_etTime.SourceTimeZoneId = SourceTimeZoneId;          // the zone the chart displays
            m_etTime.TargetTimeZoneId = "Eastern Standard Time";

            // Step 4: validate the multi-data config LOUDLY, then cache the IInstrument ref.
            // The stream is NEVER touched when UseVixFilter is OFF, so the chart needn't carry it.
            m_vixData = null;
            if (UseVixFilter) {
                if (!IsExist(VixDataStream))
                    throw new ApplicationException(
                        "YZ_ORB: UseVixFilter=true but the chart has no data" + VixDataStream +
                        " — add a VIX 5-min series there, or set UseVixFilter=false.");
                m_vixData = BarsOfData(VixDataStream);
            }

            NullLineRefs(); // MultiCharts clears our drawings on a full recalc; just reset refs
            m_curDay       = DateTime.MinValue;
            m_orStartTime  = DateTime.MinValue;
            m_orHigh       = double.MinValue;
            m_orLow        = double.MaxValue;
            m_tradedToday  = false;
            m_candDir      = 0;
            ResetDayGateState();
            ResetTradeState();
        }

        protected override void CalcBar() {
            // Convert this bar's close to US Eastern (reusable function); ALL time logic uses it.
            DateTime etNow   = m_etTime.ConvertTime(Bars.Time[0]);
            TimeSpan barTime = etNow.TimeOfDay;

            ResetDailyState(etNow);             // 1.  new ET day -> reset (+ carried-position safety flatten)
            LatchTradedToday();                 // 2.  one-shot one-trade-per-day latch
            TrackTradeState();                  // 3.  Step 4: entry capture, frozen stop, scale latch
            UpdateOpeningRange(barTime);        // 4.  accumulate the OR price range
            EvaluateDayFilters(etNow, barTime); // 5.  Step 4: VIX gate, once at OR completion
            EvaluateBreakoutCandidate(barTime); // 6.  Step 3: close-based breakout candidate
            DrawORBox(barTime);                 // 7.  draw the box once the OR completes
            DrawDayFilterLabel();               // 8.  Step 4: green/red day-gate label at the box
            SendEntryOrders();                  // 9.  Step 3: market entry on a qualifying close
            SendScaledExits(barTime);           // 10. Step 4/5: stop (buffered->BE->trail) + T1 scale
            SendTimeExits(barTime);             // 11. noon flatten (non-runner) / session-close flatten (runner)
            ExtendORBox(barTime);               // 12. extend the box's right edge to the current bar
        }

        // 1. New trading day (ET) -> reset state. ET date flips at ET midnight, well before
        //    the OR window, and OR accumulation is purely time-windowed -> robust on 24h.
        //    SAFETY (Step 4): a position carried past the flip means the noon exit failed
        //    (live outage/rejection — cannot happen in backtest). Flatten it IMMEDIATELY and
        //    say so: starting a new day managing yesterday's position with reset per-trade
        //    state would leave it with NO stop. One attempt at the flip bar; anything deeper
        //    is MC position-sync territory.
        private void ResetDailyState(DateTime etNow) {
            if (Bars.CurrentBar > 1 && etNow.Date != m_curDay) {
                if (StrategyInfo.MarketPosition != 0) {
                    if (StrategyInfo.MarketPosition > 0) m_LX.Send();
                    else                                 m_SX.Send();
                    if (DrawGuardsOK()) {
                        ITextObject warn = DrwText.Create(
                            new ChartPoint(Bars.Time[0], Bars.Close[0]), "CARRIED POSITION FLATTENED");
                        warn.HStyle = ETextStyleH.Center;
                        warn.VStyle = ETextStyleV.Above;
                        warn.Color  = Color.Red;
                    }
                }
                m_curDay       = etNow.Date;
                m_orStartTime  = DateTime.MinValue;
                m_orHigh       = double.MinValue;
                m_orLow        = double.MaxValue;
                m_tradedToday  = false;
                ResetDayGateState();
                ResetTradeState();
                NullLineRefs(); // start a fresh box; keep the prior day's lines on the chart
            }
        }

        // 2. One-shot latch (runs BEFORE candidate evaluation): once we ever hold a position
        //    today, block further entries — even after an exit (stop/target/noon) flattens us.
        //    => one trade per day. A shrinking (scaled) position only re-asserts the latch.
        private void LatchTradedToday() {
            if (StrategyInfo.MarketPosition != 0)
                m_tradedToday = true;
        }

        // 3. Step-4 trade-state tracker (pattern: ATR_Trgt_And_Trail_LX m_mp series).
        //    m_mp is assigned unconditionally FIRST so [1] is always last bar's position.
        //    On the entry bar (flat -> in position at this close) freeze everything the
        //    exits need: quantity, the actual fill (BE level), and the buffered stop —
        //    STOP BASE -/+ StopAtrBufferMult x ATR(StopAtrLength) on this 5-min data1,
        //    where the base is ALWAYS the OPPOSITE OR edge (long: OR-Low; short: OR-High —
        //    the full-range stop). The stop is computed ONCE here (a hard stop; the ATR
        //    includes the entry bar's own range — ATR_Trgt_And_Trail precedent) and never
        //    re-derived later. NOTE: the
        //    first-ever AverageTrueRange call can trigger a recalc that re-runs StartCalc —
        //    it is idempotent, and the replay re-derives identical frozen values.
        //    The scale latch is strict (MP != 0 AND smaller than entry): the noon flatten
        //    fills at this bar's close, so the NEXT bar sees MP == 0 and cannot latch.
        //    Step 5 adds two more managed states here: (a) the BREAK-EVEN arm — when the open
        //    profit reaches BreakevenAtR x R (R = the entry->frozen-stop distance) the stop is
        //    allowed to move to break-even, possibly BEFORE T1 scales; and (b) the RUNNER TRAIL
        //    — once scaled, an ATR chandelier seeded at break-even that ratchets outward only.
        //    Both react to the bar's high/low, so (like BE) they take effect from the next bar.
        private void TrackTradeState() {
            m_mp.Value = StrategyInfo.MarketPosition;

            if (m_mp[1] == 0 && m_mp.Value != 0) {                       // entry bar
                m_entryQty  = Math.Abs(m_mp.Value);
                m_entryFill = StrategyInfo.AvgEntryPrice;
                double buf  = StopAtrBufferMult * this.AverageTrueRange(StopAtrLength);
                double bse  = (m_mp.Value > 0) ? m_orLow : m_orHigh; // full-range stop: the opposite OR edge
                m_frozenStopPx = RoundToTick(m_mp.Value > 0 ? bse - buf : bse + buf);
                m_beArmed   = false;
                m_scaled    = false;
                m_trailStop = 0;
            }

            // BREAK-EVEN trigger (independent of the scale): arm once the open profit reaches
            // BreakevenAtR x R, where R = the initial entry->frozen-stop distance. Measured on
            // the bar's FAVORABLE extreme (high for longs, low for shorts). BreakevenAtR <= 0
            // disables it (the stop just stays on the frozen base until the trail takes over).
            if (m_mp.Value != 0 && !m_beArmed && m_entryFill > 0 && BreakevenAtR > 0) {
                double r = Math.Abs(m_entryFill - m_frozenStopPx);
                if (r > 0 && (m_mp.Value > 0 ? Bars.High[0] >= m_entryFill + BreakevenAtR * r
                                             : Bars.Low[0]  <= m_entryFill - BreakevenAtR * r))
                    m_beArmed = true;
            }

            bool wasScaled = m_scaled;
            if (m_mp.Value != 0 && m_entryQty > 0 && Math.Abs(m_mp.Value) < m_entryQty)
                m_scaled = true;                                          // T1 (partially) filled

            // RUNNER TRAIL: on the bar the scale is first seen, seed the trail at break-even;
            // thereafter ratchet it OUTWARD each bar by TrailAtrMult x ATR(TrailAtrLength) off
            // the current high/low (a chandelier from the scale). It never loosens, so the
            // runner can only give back to break-even (worst case), then locks in more as it runs.
            if (m_scaled && !wasScaled)
                m_trailStop = (m_entryFill > 0) ? RoundToTick(m_entryFill) : m_frozenStopPx;

            if (m_scaled && m_mp.Value != 0) {
                double atr = this.AverageTrueRange(TrailAtrLength);
                if (m_mp.Value > 0) {
                    double c = RoundToTick(Bars.High[0] - TrailAtrMult * atr);
                    if (c > m_trailStop) m_trailStop = c;
                } else {
                    double c = RoundToTick(Bars.Low[0] + TrailAtrMult * atr);
                    if (c < m_trailStop) m_trailStop = c;
                }
            }
        }

        // 4. Accumulate the opening range over ET (start, orEnd]  (close-stamped bars):
        //    the price extremes for the breakout levels.
        private void UpdateOpeningRange(TimeSpan barTime) {
            if (barTime > m_startTS && barTime <= m_orEndTS) {
                if (m_orStartTime == DateTime.MinValue)
                    // Bars are CLOSE-stamped: the first OR bar (ET 09:35) OPENS at the prior bar's
                    // timestamp, so Bars.Time[1] (= this bar's open = the 09:30 ET session open) is
                    // the box's true left edge. Bars.Time[0] would start it one bar late (09:35).
                    m_orStartTime = (Bars.CurrentBar > 0) ? Bars.Time[1] : Bars.Time[0];
                m_orHigh = Math.Max(m_orHigh, Bars.High[0]);
                m_orLow  = Math.Min(m_orLow,  Bars.Low[0]);
            }
        }

        // 5. Step-4 day gate — evaluated ONCE per day, at the first bar whose ET close is at
        //    or past the OR end (works even if the exact 09:45 bar is missing on a thin day),
        //    then LATCHED. Runs BEFORE candidate evaluation in the dispatcher, and the first
        //    possible candidate closes one bar later, so m_dayGo is always decided first.
        //    FAIL CLOSED: m_dayGo starts false each day; only a clean evaluation with the VIX
        //    gate passing sets it.
        //    - VIX: the data2 5-min bar aligned with this 09:45 close = the morning VIX in
        //      backtest, the latest live value (possibly the 09:40 bar — stamp printed). A
        //      bar not from TODAY (ET) blocks as STALE. Missing/empty/non-positive data
        //      blocks too.
        private void EvaluateDayFilters(DateTime etNow, TimeSpan barTime) {
            if (m_filtersDone || !OrValid() || barTime < m_orEndTS)
                return;
            m_filtersDone = true;

            string reasons = "";

            if (UseVixFilter) {
                // Read the latest data2 5-min VIX bar aligned with this 09:45 close.
                if (m_vixData == null || m_vixData.CurrentBar <= 0 || m_vixData.Close[0] <= 0) {
                    reasons = AppendReason(reasons, "VIX data missing (data" + VixDataStream + ")");
                } else {
                    m_vixReading = m_vixData.Close[0];
                    m_vixStamp   = m_etTime.ConvertTime(m_vixData.Time[0]);
                    if (m_vixStamp.Date != etNow.Date)
                        reasons = AppendReason(reasons,
                            "VIX stale (last " + m_vixStamp.ToString("MM/dd HH:mm") + " ET)");
                    else if (m_vixReading < VixMin)
                        reasons = AppendReason(reasons,
                            "VIX " + m_vixReading.ToString("N1") + " < " + VixMin.ToString("N0"));
                    else if (m_vixReading > VixMax)
                        reasons = AppendReason(reasons,
                            "VIX " + m_vixReading.ToString("N1") + " > " + VixMax.ToString("N0"));
                }
            }

            m_blockReason = reasons;
            m_dayGo       = (reasons.Length == 0);
        }

        // 6. Step-3 close-based breakout candidate — pure signal, no orders, no drawing.
        //    A candidate is an entry-eligible bar (flat, not latched, post-OR, pre-noon,
        //    Step-4 day gate passed) whose CLOSE CROSSES an OR level: it closes strictly
        //    beyond a level the PREVIOUS bar's close had NOT broken (a close exactly AT the
        //    level is NOT a breakout). Only the candle that actually breaks the line counts —
        //    bars merely continuing beyond an already-broken level are NOT candidates.
        //    The 09:45 OR-end bar can never qualify — the barTime <= m_orEndTS gate rejects
        //    it outright. The first post-OR bar (closing 09:50 ET) compares against the last
        //    OR bar's close, which is inside the range by construction. Bars.Close[1] is safe
        //    unguarded: OrValid() plus a post-OR bar time imply prior bars exist today.
        private void EvaluateBreakoutCandidate(TimeSpan barTime) {
            m_candDir = 0;

            if (!OrValid() || !m_dayGo || barTime <= m_orEndTS || barTime >= m_exitTS
                || StrategyInfo.MarketPosition != 0 || m_tradedToday)
                return;

            if      (Bars.Close[0] > m_orHigh && Bars.Close[1] <= m_orHigh) m_candDir = +1;
            else if (Bars.Close[0] < m_orLow  && Bars.Close[1] >= m_orLow)  m_candDir = -1;

            // Step 5 direction toggles: suppress the entry on a disabled side (the OR box,
            // day gate, and labels still draw — only the order is withheld).
            if (m_candDir > 0 && !TradeLongs)  m_candDir = 0;
            if (m_candDir < 0 && !TradeShorts) m_candDir = 0;
        }

        // 7. Draw the box once, the moment the OR is complete (>= orEnd: at the last OR bar's
        //    close, after UpdateOpeningRange has folded that bar into the range). The box
        //    also draws on BLOCKED days so the OR stays visible for verification.
        private void DrawORBox(TimeSpan barTime) {
            if (ShowORLines && DrawGuardsOK() && OrValid() && barTime >= m_orEndTS && m_lnHigh == null) {
                double mid = RawMidpoint();

                m_lnHigh = DrwTrendLine.Create(new ChartPoint(m_orStartTime, m_orHigh),
                                               new ChartPoint(Bars.Time[0],  m_orHigh));
                m_lnHigh.Color = Color.LimeGreen; m_lnHigh.Size = 2;
                m_lnHigh.ExtLeft = false; m_lnHigh.ExtRight = false;

                m_lnLow = DrwTrendLine.Create(new ChartPoint(m_orStartTime, m_orLow),
                                              new ChartPoint(Bars.Time[0],  m_orLow));
                m_lnLow.Color = Color.Red; m_lnLow.Size = 2;
                m_lnLow.ExtLeft = false; m_lnLow.ExtRight = false;

                m_lnMid = DrwTrendLine.Create(new ChartPoint(m_orStartTime, mid),
                                              new ChartPoint(Bars.Time[0],  mid));
                m_lnMid.Color = Color.Gray; m_lnMid.Size = 1; m_lnMid.Style = ETLStyle.ToolDashed;
                m_lnMid.ExtLeft = false; m_lnMid.ExtRight = false;
            }
        }

        // 8. Step-4 verification: one label per day above the OR box's left edge with the
        //    day-gate verdict — green "FILTERS OK | VIX 18.4 @09:45" (the VIX part shows the
        //    5-min bar's ET time; the gate toggled off prints "off" so a consciously bypassed
        //    gate stays visible) or red "DAY BLOCKED | <reasons>".
        private void DrawDayFilterLabel() {
            if (!ShowFilterLabels || !DrawGuardsOK() || m_filterLabelDone || !m_filtersDone)
                return;
            string txt;
            if (m_dayGo) {
                string vixPart = UseVixFilter
                    ? "VIX " + m_vixReading.ToString("N1") + " @" + m_vixStamp.ToString("HH:mm")
                    : "VIX off";
                txt = "FILTERS OK | " + vixPart;
            } else {
                txt = "DAY BLOCKED | " + m_blockReason;
            }
            ITextObject t = DrwText.Create(new ChartPoint(m_orStartTime, m_orHigh), txt);
            t.HStyle = ETextStyleH.Center;
            t.VStyle = ETextStyleV.Above;
            t.Color  = m_dayGo ? Color.LimeGreen : Color.Red;
            m_filterLabelDone = true;
        }

        // 9. Step-3 entry: market order sent on the candidate's close, filled at the NEXT
        //    bar's open (IOG-disabled signal-on-close). ALL signal gating (flat, latch, post-OR,
        //    pre-noon, day gates, crossing close) lives in EvaluateBreakoutCandidate.
        //    SIZING (Step 6 preview): the quantity is risk-sized at THIS close (see ComputeEntryLots).
        //    A size of 0 (the OR is so wide that even one contract would risk > RiskDollars) SKIPS
        //    the entry — the day's one-trade latch is NOT consumed (no position taken), so a later
        //    fresh close-cross can still enter.
        private void SendEntryOrders() {
            if (m_candDir == 0)
                return;
            int lots = ComputeEntryLots(m_candDir);
            if (lots <= 0) { NoteSizeSkip(); return; }
            if      (m_candDir > 0) m_LE.Send(lots);
            else if (m_candDir < 0) m_SE.Send(lots);
        }

        // Constant-dollar-risk size for the candidate, computed at its CLOSE (one bar before the
        // fill — a MarketNextBar order's quantity is fixed at Send time). The stop LEVEL is the
        // same value the entry bar will freeze into m_frozenStopPx: the opposite OR edge widened
        // by StopAtrBufferMult x ATR(StopAtrLength). The entry PRICE is proxied by this bar's
        // close (Bars.Close[0]) since the fill is the next bar's open. distPts is therefore the
        // full-range stop distance in points; risk/contract = distPts x BigPointValue.
        //   contracts = floor(RiskDollars / risk-per-contract), capped at MaxContracts, 0 if < 1.
        // Sizing is an ESTIMATE made one bar early: the realized stop uses the entry-bar ATR and
        // the actual fill, so a stop-out risks ~RiskDollars, not exactly (header note).
        private int ComputeEntryLots(int dir) {
            double buf     = StopAtrBufferMult * this.AverageTrueRange(StopAtrLength);
            double stopLvl = (dir > 0) ? (m_orLow - buf) : (m_orHigh + buf); // opposite OR edge + buffer
            double distPts = Math.Abs(Bars.Close[0] - stopLvl);
            return m_sizer.ContractsForRisk(RiskDollars, distPts, Bars.Info.BigPointValue, MaxContracts);
        }

        // Audit marker when a qualifying breakout is skipped purely for size (mirrors the day-gate
        // label's style). Guarded like the other drawings; off in portfolio/optimization runs.
        private void NoteSizeSkip() {
            if (!ShowFilterLabels || !DrawGuardsOK())
                return;
            ITextObject t = DrwText.Create(
                new ChartPoint(Bars.Time[0], Bars.Close[0]), "SKIPPED: size<1");
            t.HStyle = ETextStyleH.Center;
            t.VStyle = ETextStyleV.Below;
            t.Color  = Color.Orange;
        }

        // 10. Step-4/5 exits: while in a position, keep the bracket working — exit orders
        //     auto-cancel unless re-sent each bar. The re-send continues up to the NOON bar
        //     when NOT scaled, but up to the SESSION CLOSE once scaled, so the trailed runner
        //     stays protected through the afternoon.
        //     STOP (always, FULL remaining position via FromAll-no-qty), by precedence:
        //       scaled    -> the ATR TRAIL (m_trailStop, ratcheting; seeded at break-even);
        //       BE armed  -> BREAK-EVEN (the entry fill, tick-rounded) — reached BreakevenAtR x R;
        //       otherwise -> the frozen buffered stop (base = the opposite OR edge).
        //     SCALE-OUT: pre-scale only — a single T1 limit at entry +/- TargetORMult x OR for
        //       ceil(qty/2) (~50%). Once scaled, T1 is no longer sent and there is NO second
        //       target: the runner is pure-trail (let winners run).
        //     T1 is measured from the ACTUAL fill (m_entryFill; 0 = anomalous -> only the stop
        //     is sent, protection is never absent). The stop precedence and trail react one bar
        //     after their trigger (the high/low is seen at the close) — the documented IOG latency.
        private void SendScaledExits(TimeSpan barTime) {
            // Not scaled: bracket lives until noon (the noon flatten then takes over). Scaled:
            // the runner trails until the session-close flatten — keep re-sending until then.
            TimeSpan stopSending = m_scaled ? m_sessionCloseTS : m_exitTS;
            if (!OrValid() || StrategyInfo.MarketPosition == 0 || barTime >= stopSending)
                return;

            bool   isLong = StrategyInfo.MarketPosition > 0;
            double orSz   = m_orHigh - m_orLow;
            double stopPx = m_scaled  ? m_trailStop                  // runner: ATR trail
                          : m_beArmed ? RoundToTick(m_entryFill)     // reached BreakevenAtR x R
                          :             m_frozenStopPx;              // initial buffered stop
            double t1Px   = 0;
            int    t1Qty  = T1Qty();

            if (isLong) {
                if (stopPx > 0) m_LXStop.Send(stopPx);
                if (!m_scaled && m_entryFill > 0) {                  // pre-scale: arm the T1 scale-out
                    t1Px = RoundToTick(m_entryFill + TargetORMult * orSz);
                    m_LXT1.Send(t1Px, t1Qty);
                }
            } else {
                if (stopPx > 0) m_SXStop.Send(stopPx);
                if (!m_scaled && m_entryFill > 0) {
                    t1Px = RoundToTick(m_entryFill - TargetORMult * orSz);
                    m_SXT1.Send(t1Px, t1Qty);
                }
            }

            DrawTradeLines(stopPx, t1Px);
        }

        // 11. Time-based flatten (MarketThisBar -> fills at THAT bar's close, so the marker sits
        //     on the exit bar; MarketNextBar would fill one bar later). The flatten time is
        //     STATE-DEPENDENT: a runner (scaled -> being trailed) IGNORES the noon exit and runs
        //     to the SESSION CLOSE (16:30 ET); everything else still flattens at NOON. Fires only
        //     if no stop / target / trail already flattened us intrabar.
        private void SendTimeExits(TimeSpan barTime) {
            if (StrategyInfo.MarketPosition == 0)
                return;
            TimeSpan flatAt = m_scaled ? m_sessionCloseTS : m_exitTS; // runner -> 16:30 ET; else -> noon
            if (barTime >= flatAt) {
                if (StrategyInfo.MarketPosition > 0) m_LX.Send();
                else                                 m_SX.Send();
            }
        }

        // 12. Extend the box's right edge to the current bar, up to the noon exit.
        private void ExtendORBox(TimeSpan barTime) {
            if (ShowORLines && DrawGuardsOK() && m_lnHigh != null && barTime < m_exitTS) {
                m_lnHigh.End = new ChartPoint(Bars.Time[0], m_orHigh);
                m_lnLow.End  = new ChartPoint(Bars.Time[0], m_orLow);
                m_lnMid.End  = new ChartPoint(Bars.Time[0], RawMidpoint());
            }
        }

        // Step-4/5 verification aid: the dashed T1 line and the ACTIVE stop line while the trade
        // is on. T1 stops extending once scaled (t1Px == 0 then); the stop line starts a NEW flat
        // segment whenever its price changes, so the BE jump and the ATR trail render as a rising
        // (long) / falling (short) staircase rather than one sloped line. Bars.Time[1] is safe
        // here: a position can't exist before the OR completes (4+ bars into the day), and on the
        // first in-position bar Time[1] = the entry bar's open.
        private void DrawTradeLines(double stopPx, double t1Px) {
            if (!ShowORLines || !DrawGuardsOK())
                return;
            if (t1Px > 0) UpdateLine(ref m_lnTgt, t1Px, Color.DodgerBlue, true);
            if (stopPx > 0) {
                if (m_lnStop != null && stopPx != m_lnStopPx)
                    m_lnStop = null; // price changed: leave the old segment, start a fresh one
                UpdateLine(ref m_lnStop, stopPx, Color.Orange, false);
                m_lnStopPx = stopPx;
            }
        }

        // Create-or-extend a horizontal level line (create at the prior bar's stamp = this
        // bar's open; extend the End on later bars — the existing Step-2 pattern).
        private void UpdateLine(ref ITrendLineObject ln, double px, Color color, bool dashed) {
            if (ln == null) {
                ln = DrwTrendLine.Create(new ChartPoint(Bars.Time[1], px),
                                         new ChartPoint(Bars.Time[0], px));
                ln.Color = color; ln.Size = 1;
                if (dashed) ln.Style = ETLStyle.ToolDashed;
                ln.ExtLeft = false; ln.ExtRight = false;
            } else {
                ln.End = new ChartPoint(Bars.Time[0], px);
            }
        }

        // T1 tranche size: ceil of half the entry quantity. ceil (not floor) de-risks the
        // larger half first on odd lots; qty=1 -> T1 is the whole position (T2 never sent).
        private int T1Qty() {
            return (m_entryQty + 1) / 2;
        }

        // Join day-gate block reasons for the label.
        private static string AppendReason(string acc, string reason) {
            return acc.Length == 0 ? reason : acc + " & " + reason;
        }

        // True once the day's opening range holds at least one bar.
        private bool OrValid() {
            return m_orHigh > double.MinValue && m_orLow < double.MaxValue;
        }

        // Don't draw during portfolio backtests / optimization runs.
        private bool DrawGuardsOK() {
            return this.Environment.ApplicationCode != EApplicationCode.Portfolio
                   && !this.Environment.Optimizing;
        }

        // Raw geometric OR midpoint (the drawn gray midline; may sit on a half tick).
        private double RawMidpoint() {
            return (m_orHigh + m_orLow) / 2.0;
        }

        // Snap a raw price to the instrument's tick grid (Bars.Point = one min tick).
        // AwayFromZero => a half-tick value deterministically rounds UP.
        private double RoundToTick(double price) {
            return Math.Round(price / Bars.Point, MidpointRounding.AwayFromZero) * Bars.Point;
        }

        // HHMM int (e.g. 930, 1200) -> TimeSpan.
        private static TimeSpan FromHHMM(int t) {
            return new TimeSpan(t / 100, t % 100, 0);
        }

        // Step-4 per-day day-gate resets (StartCalc + the daily roll).
        private void ResetDayGateState() {
            m_filtersDone     = false;
            m_dayGo           = false;          // fail closed until evaluated
            m_blockReason     = "";
            m_vixReading      = 0;
            m_vixStamp        = DateTime.MinValue;
            m_filterLabelDone = false;
        }

        // Step-4 per-trade resets (StartCalc + the daily roll; safe daily because of the
        // one-trade/day latch — the entry bar re-initializes everything per trade).
        private void ResetTradeState() {
            m_entryQty     = 0;
            m_entryFill    = 0;
            m_frozenStopPx = 0;
            m_beArmed      = false;
            m_scaled       = false;
            m_trailStop    = 0;
        }

        // Drop our line references so the next day creates a fresh box. We deliberately do NOT
        // Delete() the prior day's lines: MultiCharts keeps study-created drawings across the
        // chart (and clears them itself on a full recalc), so every session's box stays visible
        // for historical verification — deleting here would leave only the last session drawn.
        private void NullLineRefs() {
            m_lnHigh   = null;
            m_lnLow    = null;
            m_lnMid    = null;
            m_lnTgt    = null;
            m_lnStop   = null;
            m_lnStopPx = 0;
        }
    }
}
