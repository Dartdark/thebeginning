// @ElementOfFear
// V4 H1 residual fair-value pure helpers (no NinjaTrader dependency).
// Frozen config: H1B_z_lb60_abs1.5. ASCII only.

using System;
using System.Collections.Generic;

namespace BtcReopenMr.Core
{
	public static class V4StrategyConstants
	{
		public const string StrategyName = "BTCFuturesReopenResidualFairValueV4";
		public const string ExplicitSpotTradingHoursTemplate = "Cryptocurrency";
		public const long ExpectedSpotMasterInstrumentId = 699839150753921L;
		public const string ExpectedSpotInstrumentType = "CryptoCurrency";
		public const string ExpectedSpotExchange = "Gdax";

		public const int ResidualLookbackEvents = 60;
		public const double AbsResidualZThreshold = 1.5;
		public const int ExecutableExitHoldMinutes = 60;
		public const double MinimumFuturesClosedMinutes = 30.0;
		public const double MaximumSpotAgeMinutes = 5.0;

		// V4 does NOT use V2/V3 spot-move or raw-dollar basis entry gates.
		public const bool UsesMinimumClosedSpotMoveGate = false;
		public const bool UsesRawDollarBasisGate = false;
		public const bool UsesBasisMeanExit = false;
	}

	public static class V4ResidualMath
	{
		public static double SpotGapReturn(double spotPreReopen, double spotAtFuturesClose)
		{
			return spotPreReopen / spotAtFuturesClose - 1.0;
		}

		public static double FuturesReopenReturn(double futuresFirstCausalReopen, double futuresLastPreclose)
		{
			return futuresFirstCausalReopen / futuresLastPreclose - 1.0;
		}

		public static double ResidualReturn(double futuresReopenReturn, double spotGapReturn)
		{
			return futuresReopenReturn - spotGapReturn;
		}

		public static double ResidualBps(double residualReturn)
		{
			return 10000.0 * residualReturn;
		}

		public static double CausalZ(double currentBps, double baselineMean, double baselineStd)
		{
			if (baselineStd <= 1e-12)
				return double.NaN;
			return (currentBps - baselineMean) / baselineStd;
		}

		public static SignalDirection DirectionFromZ(double z, double absThreshold)
		{
			if (double.IsNaN(z) || Math.Abs(z) < absThreshold)
				return SignalDirection.None;
			if (z > 0.0)
				return SignalDirection.Short;
			return SignalDirection.Long;
		}
	}

	/// <summary>
	/// Causal residual-bps history. Evaluate Z using prior samples, then AddCompleted.
	/// Capacity equals lookback; require Count == lookback before trading.
	/// </summary>
	public sealed class CausalResidualHistory
	{
		private readonly Queue<double> _values = new Queue<double>();
		private readonly int _lookback;

		public CausalResidualHistory(int lookback)
		{
			if (lookback < 2)
				throw new ArgumentOutOfRangeException("lookback");
			_lookback = lookback;
		}

		public int Count { get { return _values.Count; } }
		public int Lookback { get { return _lookback; } }

		public void Clear()
		{
			_values.Clear();
		}

		public bool IsReady
		{
			get { return _values.Count >= _lookback; }
		}

		public void AddCompleted(double residualBps)
		{
			_values.Enqueue(residualBps);
			while (_values.Count > _lookback)
				_values.Dequeue();
		}

		public bool TryGetMeanStd(out double mean, out double stdDev)
		{
			mean = 0.0;
			stdDev = 0.0;
			int n = _values.Count;
			if (n < _lookback)
				return false;

			double sum = 0.0;
			foreach (double v in _values)
				sum += v;
			mean = sum / n;

			double sse = 0.0;
			foreach (double v in _values)
			{
				double d = v - mean;
				sse += d * d;
			}
			stdDev = Math.Sqrt(sse / (n - 1));
			return true;
		}
	}

	public static class V4ExitSchedule
	{
		public static DateTime ScheduledExitTime(DateTime entryFillTime, int holdMinutes)
		{
			return entryFillTime.AddMinutes(holdMinutes);
		}

		public static bool ShouldSignalExit(DateTime barTime, DateTime scheduledExitTime)
		{
			return barTime >= scheduledExitTime;
		}
	}
}
