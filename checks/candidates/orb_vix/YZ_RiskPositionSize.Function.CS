using System;

namespace PowerLanguage.Function
{
    // =====================================================================================
    // YZ_RiskPositionSize  —  reusable constant-dollar-risk position sizer (FunctionSeries<int>)
    // -------------------------------------------------------------------------------------
    // Turns a fixed dollar risk into a contract count, given how far the stop sits from the
    // entry (constant-dollar-risk / "volatility" sizing): a wider stop -> fewer contracts, a
    // tighter stop -> more, so the dollars at risk on a stop-out stay roughly constant no
    // matter the instrument's volatility.
    //
    //     contracts = floor( riskDollars / (stopDistancePoints * bigPointValue) ), capped.
    //
    // The function is deliberately GENERIC: it takes the stop distance in PRICE POINTS, so the
    // caller decides how that distance is derived (ATR x multiplier, a fixed structural stop,
    // the opposite OR edge + buffer, ...). It never touches Bars, so it is pure and reusable
    // from any study.
    //
    //   stopDistancePoints : |entry - stop| in full price points (NOT ticks, NOT dollars).
    //   bigPointValue      : dollars per one full point for the instrument (Bars.Info.BigPointValue;
    //                        ES = 50). riskPerContract = stopDistancePoints * bigPointValue.
    //   maxContracts       : hard ceiling on the returned size (a sanity cap).
    //
    // Returns 0 when any input is non-positive OR when even ONE contract would risk more than
    // riskDollars (the affordable size rounds below 1). 0 means "do not size in" — the caller
    // decides whether that skips the trade or forces a floor of 1.
    //
    // Use it from a study (instantiate once in Create(): m_sizer = new YZ_RiskPositionSize(this);):
    //   * Method (preferred): int lots = m_sizer.ContractsForRisk(1000, distPts, Bars.Info.BigPointValue, 4);
    //   * Indexer (current bar): set the properties, then read m_sizer[0].
    // =====================================================================================
    public class YZ_RiskPositionSize : FunctionSeries<int>
    {
        public double RiskDollars        { get; set; } // dollars to risk per trade
        public double StopDistancePoints { get; set; } // |entry - stop| in full price points
        public double BigPointValue      { get; set; } // dollars per one full point (Bars.Info.BigPointValue)
        public int    MaxContracts       { get; set; } // hard ceiling on the returned size

        public YZ_RiskPositionSize(CStudyControl ctx) : base(ctx) { SetDefaults(); }
        public YZ_RiskPositionSize(CStudyControl ctx, int data_stream) : base(ctx, data_stream) { SetDefaults(); }

        private void SetDefaults() {
            RiskDollars        = 1000;
            StopDistancePoints = 0;
            BigPointValue      = 0;
            MaxContracts       = 4;
        }

        // FunctionSeries indexer entry point: size from the currently-set properties.
        protected override int CalcBar() {
            return ContractsForRisk(RiskDollars, StopDistancePoints, BigPointValue, MaxContracts);
        }

        // Constant-dollar-risk contract count (pure; no Bars dependency).
        public int ContractsForRisk(double riskDollars, double stopDistancePoints,
                                    double bigPointValue, int maxContracts) {
            if (riskDollars <= 0 || stopDistancePoints <= 0 || bigPointValue <= 0 || maxContracts <= 0)
                return 0;

            double riskPerContract = stopDistancePoints * bigPointValue;
            double affordable      = Math.Floor(riskDollars / riskPerContract);

            if (affordable < 1) return 0;                       // even one contract exceeds the budget
            return (int)Math.Min(affordable, maxContracts);     // cap in double space, then cast (no overflow)
        }
    }
}
