// @ElementOfFear
// Pure deterministic signal core for BTC futures reopen / basis MR.
// No NinjaTrader dependencies. ASCII only.

using System;
using System.Collections.Generic;

namespace BtcReopenMr.Core
{
	public enum BasisMode
	{
		DollarSpread = 0,
		PercentSpread = 1,
		LogRatio = 2
	}

	public enum BasisThresholdMode
	{
		AbsoluteDeviation = 0,
		ZScore = 1
	}

	public enum SignalDirection
	{
		None = 0,
		Long = 1,
		Short = 2
	}

	public enum DiagnosticCode
	{
		None = 0,
		NotReopen = 1,
		NoSpot = 2,
		StaleSpot = 3,
		InsufficientBasisHistory = 4,
		SpotMoveTooSmall = 5,
		BasisNotExtreme = 6,
		PositionAlreadyOpen = 7,
		EntryLong = 8,
		EntryShort = 9,
		ExitBasisMean = 10,
		ExitMaxHold = 11,
		SkipPositionOpen = 12,
		TinyBasisStdDev = 13,
		StaleSpotBeforeClosure = 14,
		StaleSpotAtReopen = 15,
		FutureDatedSpotBeforeClosure = 16,
		FutureDatedSpotAtReopen = 17,
		InvalidPrimaryBarsPeriod = 18,
		StaleSpotAtExit = 19,
		FutureDatedSpotAtExit = 20,
		// V1 frozen event-gate / rollover diagnostics
		NotExpectedReopen = 21,
		SpecialSessionExcluded = 22,
		RawGapTooSmall = 23,
		ReopenBarTooLate = 24,
		CloseAnchorInvalid = 25,
		RolloverDetected = 26,
		BasisHistoryResetForRollover = 27,
		InsufficientPostRollBasisHistory = 28,
		ExpectedReopenEligible = 29,
		OutsideV1Interval = 30,
		DuplicateReopenSuppressed = 31,
		BasisExitDisabledAtRollover = 32,
		ExitRolloverBoundary = 33,
		ExitV1TestWindowEnd = 34,
		ForcedExitPending = 35
	}

	public enum SpotEndpointFreshness
	{
		Ok = 0,
		Missing = 1,
		FutureDated = 2,
		Stale = 3
	}

	public static class SpotFreshness
	{
		// Age = referenceFuturesTime - spotTimestamp.
		// Requires 0 <= age <= maximumSpotAgeMinutes.
		public static SpotEndpointFreshness Evaluate(
			DateTime referenceFuturesTime,
			DateTime spotTimestamp,
			bool hasSpot,
			double maximumSpotAgeMinutes,
			out double ageMinutes)
		{
			ageMinutes = double.NaN;
			if (!hasSpot)
				return SpotEndpointFreshness.Missing;

			ageMinutes = (referenceFuturesTime - spotTimestamp).TotalMinutes;
			if (ageMinutes < 0.0 || spotTimestamp > referenceFuturesTime)
				return SpotEndpointFreshness.FutureDated;
			if (ageMinutes > maximumSpotAgeMinutes)
				return SpotEndpointFreshness.Stale;
			return SpotEndpointFreshness.Ok;
		}

		public static DiagnosticCode ToBeforeClosureCode(SpotEndpointFreshness f)
		{
			if (f == SpotEndpointFreshness.FutureDated)
				return DiagnosticCode.FutureDatedSpotBeforeClosure;
			if (f == SpotEndpointFreshness.Stale)
				return DiagnosticCode.StaleSpotBeforeClosure;
			if (f == SpotEndpointFreshness.Missing)
				return DiagnosticCode.NoSpot;
			return DiagnosticCode.None;
		}

		public static DiagnosticCode ToReopenCode(SpotEndpointFreshness f)
		{
			if (f == SpotEndpointFreshness.FutureDated)
				return DiagnosticCode.FutureDatedSpotAtReopen;
			if (f == SpotEndpointFreshness.Stale)
				return DiagnosticCode.StaleSpotAtReopen;
			if (f == SpotEndpointFreshness.Missing)
				return DiagnosticCode.NoSpot;
			return DiagnosticCode.None;
		}

		public static DiagnosticCode ToExitCode(SpotEndpointFreshness f)
		{
			if (f == SpotEndpointFreshness.FutureDated)
				return DiagnosticCode.FutureDatedSpotAtExit;
			if (f == SpotEndpointFreshness.Stale)
				return DiagnosticCode.StaleSpotAtExit;
			if (f == SpotEndpointFreshness.Missing)
				return DiagnosticCode.NoSpot;
			return DiagnosticCode.None;
		}
	}

	// V1 scientific testing requires a 1-minute time-based primary futures series.
	// Reopen detection uses futuresGapMinutes >= MinimumFuturesClosedMinutes; a primary
	// bar interval that can itself satisfy that threshold falsely classifies ordinary bars.
	public enum PrimaryBarsCompatibility
	{
		Compatible = 0,
		UnsupportedBarsType = 1,
		IntervalTooLargeForGapDetector = 2,
		NotExactlyOneMinute = 3
	}

	public static class PrimaryBarsPeriodGuard
	{
		public const int RequiredMinuteValue = 1;

		// barsPeriodTypeName: NT BarsPeriodType name (Minute, Tick, Volume, ...).
		// value: BarsPeriod.Value (minutes for Minute type).
		public static PrimaryBarsCompatibility Evaluate(
			string barsPeriodTypeName,
			int value,
			double minimumFuturesClosedMinutes,
			out string reason)
		{
			reason = string.Empty;
			if (string.IsNullOrWhiteSpace(barsPeriodTypeName))
			{
				reason = "Primary BarsPeriodType is missing.";
				return PrimaryBarsCompatibility.UnsupportedBarsType;
			}

			string t = barsPeriodTypeName.Trim();
			bool isMinute = string.Equals(t, "Minute", StringComparison.OrdinalIgnoreCase);
			if (!isMinute)
			{
				reason = "V1 requires primary BarsPeriodType=Minute Value=1. Rejected type='" + t + "' Value=" + value.ToString() + ".";
				return PrimaryBarsCompatibility.UnsupportedBarsType;
			}

			if (value <= 0)
			{
				reason = "Primary Minute Value must be positive.";
				return PrimaryBarsCompatibility.UnsupportedBarsType;
			}

			// Ordinary consecutive bars of this interval must not satisfy the reopen threshold.
			if ((double)value >= minimumFuturesClosedMinutes)
			{
				reason = "Primary minute interval " + value.ToString()
					+ " >= MinimumFuturesClosedMinutes " + minimumFuturesClosedMinutes.ToString("G17")
					+ "; ordinary bars would falsely classify as reopens.";
				return PrimaryBarsCompatibility.IntervalTooLargeForGapDetector;
			}

			if (value != RequiredMinuteValue)
			{
				reason = "V1 scientific testing freezes primary futures bars at 1 Minute. Got Minute Value=" + value.ToString() + ".";
				return PrimaryBarsCompatibility.NotExactlyOneMinute;
			}

			reason = "OK";
			return PrimaryBarsCompatibility.Compatible;
		}

		public static bool IsCompatible(string barsPeriodTypeName, int value, double minimumFuturesClosedMinutes)
		{
			string reason;
			return Evaluate(barsPeriodTypeName, value, minimumFuturesClosedMinutes, out reason) == PrimaryBarsCompatibility.Compatible;
		}
	}

	public static class BasisMath
	{
		public static double CalculateBasis(BasisMode mode, double futuresPrice, double spotPrice)
		{
			if (spotPrice <= 0.0 || futuresPrice <= 0.0)
				throw new ArgumentOutOfRangeException("prices must be positive");

			switch (mode)
			{
				case BasisMode.DollarSpread:
					return futuresPrice - spotPrice;
				case BasisMode.PercentSpread:
					return 100.0 * (futuresPrice / spotPrice - 1.0);
				case BasisMode.LogRatio:
					return Math.Log(futuresPrice / spotPrice);
				default:
					throw new ArgumentOutOfRangeException("mode");
			}
		}

		public static double SpotClosedMovePct(double spotBeforeClosure, double spotAtReopen)
		{
			if (spotBeforeClosure <= 0.0 || spotAtReopen <= 0.0)
				throw new ArgumentOutOfRangeException("spot prices must be positive");
			return 100.0 * (spotAtReopen / spotBeforeClosure - 1.0);
		}

		public static bool IsReopenGap(double futuresGapMinutes, double minimumFuturesClosedMinutes)
		{
			return futuresGapMinutes >= minimumFuturesClosedMinutes;
		}
	}

	public sealed class CausalBasisHistory
	{
		private readonly Queue<double> _values = new Queue<double>();
		private readonly int _capacity;

		public CausalBasisHistory(int capacity)
		{
			if (capacity < 1)
				throw new ArgumentOutOfRangeException("capacity");
			_capacity = capacity;
		}

		public int Count { get { return _values.Count; } }

		public void Clear()
		{
			_values.Clear();
		}

		public void AddCompleted(double basisValue)
		{
			_values.Enqueue(basisValue);
			while (_values.Count > _capacity)
				_values.Dequeue();
		}

		public bool TryGetMeanStd(out double mean, out double stdDev)
		{
			mean = 0.0;
			stdDev = 0.0;
			int n = _values.Count;
			if (n < 1)
				return false;

			double sum = 0.0;
			foreach (double v in _values)
				sum += v;
			mean = sum / n;

			if (n < 2)
			{
				stdDev = 0.0;
				return true;
			}

			double sse = 0.0;
			foreach (double v in _values)
			{
				double d = v - mean;
				sse += d * d;
			}
			stdDev = Math.Sqrt(sse / (n - 1));
			return true;
		}

		public double[] Snapshot()
		{
			double[] arr = new double[_values.Count];
			_values.CopyTo(arr, 0);
			return arr;
		}
	}

	public sealed class SpotObservationBuffer
	{
		private readonly List<DateTime> _times = new List<DateTime>();
		private readonly List<double> _prices = new List<double>();
		private readonly int _maxCount;

		public SpotObservationBuffer(int maxCount)
		{
			if (maxCount < 1)
				throw new ArgumentOutOfRangeException("maxCount");
			_maxCount = maxCount;
		}

		public int Count { get { return _times.Count; } }

		public void Add(DateTime time, double price)
		{
			if (price <= 0.0)
				return;

			if (_times.Count > 0 && time < _times[_times.Count - 1])
			{
				// Keep buffer sorted by time; ignore out-of-order older prints.
				return;
			}

			if (_times.Count > 0 && time == _times[_times.Count - 1])
			{
				_prices[_prices.Count - 1] = price;
				return;
			}

			_times.Add(time);
			_prices.Add(price);
			while (_times.Count > _maxCount)
			{
				_times.RemoveAt(0);
				_prices.RemoveAt(0);
			}
		}

		public bool TryGetAtOrBefore(DateTime signalTime, out double price, out DateTime obsTime)
		{
			price = 0.0;
			obsTime = DateTime.MinValue;
			int best = -1;
			for (int i = 0; i < _times.Count; i++)
			{
				if (_times[i] <= signalTime)
					best = i;
				else
					break;
			}
			if (best < 0)
				return false;
			price = _prices[best];
			obsTime = _times[best];
			return true;
		}

		public bool WouldUseFutureDatedSpot(DateTime signalTime, DateTime candidateSpotTime)
		{
			return candidateSpotTime > signalTime;
		}
	}

	public sealed class EntryParams
	{
		public double MinimumClosedSpotMovePct;
		public BasisThresholdMode ThresholdMode;
		public double BasisAbsoluteThreshold;
		public double BasisZThreshold;
		public double MinStdDev;
		public bool PositionIsFlat;
	}

	public sealed class EntryEvalResult
	{
		public SignalDirection Direction;
		public DiagnosticCode Code;
		public bool SpotMovePassed;
		public bool BasisThresholdPassed;
		public double SpotClosedMovePct;
		public double Basis;
		public double BasisMean;
		public double BasisStdDev;
		public double BasisDeviation;
		public double BasisZ;
	}

	public static class EntryLogic
	{
		public static EntryEvalResult EvaluateReopenEntry(
			double spotClosedMovePct,
			double currentBasis,
			double basisMean,
			double basisStdDev,
			int basisHistoryCount,
			int requiredLookback,
			EntryParams p)
		{
			var r = new EntryEvalResult();
			r.SpotClosedMovePct = spotClosedMovePct;
			r.Basis = currentBasis;
			r.BasisMean = basisMean;
			r.BasisStdDev = basisStdDev;
			r.BasisDeviation = currentBasis - basisMean;
			r.Direction = SignalDirection.None;
			r.Code = DiagnosticCode.None;

			if (basisHistoryCount < requiredLookback)
			{
				r.Code = DiagnosticCode.InsufficientBasisHistory;
				return r;
			}

			if (!p.PositionIsFlat)
			{
				r.Code = DiagnosticCode.SkipPositionOpen;
				return r;
			}

			r.SpotMovePassed = Math.Abs(spotClosedMovePct) >= p.MinimumClosedSpotMovePct;

			if (p.ThresholdMode == BasisThresholdMode.AbsoluteDeviation)
			{
				r.BasisThresholdPassed = Math.Abs(r.BasisDeviation) >= p.BasisAbsoluteThreshold;
				r.BasisZ = basisStdDev > p.MinStdDev ? r.BasisDeviation / basisStdDev : 0.0;
			}
			else
			{
				if (basisStdDev <= p.MinStdDev)
				{
					r.Code = DiagnosticCode.TinyBasisStdDev;
					r.BasisThresholdPassed = false;
					return r;
				}
				r.BasisZ = r.BasisDeviation / basisStdDev;
				r.BasisThresholdPassed = Math.Abs(r.BasisZ) >= p.BasisZThreshold;
			}

			if (!r.SpotMovePassed)
			{
				r.Code = DiagnosticCode.SpotMoveTooSmall;
				return r;
			}

			if (!r.BasisThresholdPassed)
			{
				r.Code = DiagnosticCode.BasisNotExtreme;
				return r;
			}

			// SOURCE_DEFINED_LOGIC (literal):
			// spot up while futures closed -> SHORT futures
			// spot down while futures closed -> LONG futures
			if (spotClosedMovePct >= p.MinimumClosedSpotMovePct)
			{
				r.Direction = SignalDirection.Short;
				r.Code = DiagnosticCode.EntryShort;
				return r;
			}

			if (spotClosedMovePct <= -p.MinimumClosedSpotMovePct)
			{
				r.Direction = SignalDirection.Long;
				r.Code = DiagnosticCode.EntryLong;
				return r;
			}

			r.Code = DiagnosticCode.SpotMoveTooSmall;
			return r;
		}
	}

	public static class ExitLogic
	{
		// entryBasisDeviationSign: +1 if entryBasis > entryBasisMean, -1 if entryBasis < entryBasisMean, 0 if equal
		public static bool ShouldExitBasisMeanReversion(
			double currentBasis,
			double entryBasisMean,
			int entryBasisDeviationSign)
		{
			if (entryBasisDeviationSign > 0)
				return currentBasis <= entryBasisMean;
			if (entryBasisDeviationSign < 0)
				return currentBasis >= entryBasisMean;
			return false;
		}

		public static int DeviationSign(double entryBasis, double entryBasisMean)
		{
			double d = entryBasis - entryBasisMean;
			if (d > 0.0)
				return 1;
			if (d < 0.0)
				return -1;
			return 0;
		}

		public static bool ShouldExitMaxHold(bool useMaxHoldBars, int barsHeld, int maxHoldBars)
		{
			if (!useMaxHoldBars)
				return false;
			return barsHeld >= maxHoldBars;
		}
	}

	public sealed class DefaultParameters
	{
		public const int SpotBarsPeriodMinutes = 1;
		public const double MaximumSpotAgeMinutes = 5.0;
		public const double MinimumFuturesClosedMinutes = 30.0;
		public const double MinimumClosedSpotMovePct = 1.0;
		public const BasisMode BasisModeDefault = BasisMode.DollarSpread;
		public const int BasisLookbackBars = 60;
		public const BasisThresholdMode BasisThresholdModeDefault = BasisThresholdMode.ZScore;
		public const double BasisAbsoluteThreshold = 100.0;
		public const double BasisZThreshold = 2.0;
		public const bool UseMaxHoldBars = false;
		public const int MaxHoldBars = 60;
		public const bool EnableDiagnostics = true;
		public const string SpotInstrumentPlaceholder = "REQUIRED_SELECT_VALID_BTC_SPOT";
		public const double MinBasisStdDev = 1e-12;

		public static string SerializeDeterministic()
		{
			return string.Join("|", new string[]
			{
				"SpotBarsPeriodMinutes=" + SpotBarsPeriodMinutes.ToString(),
				"MaximumSpotAgeMinutes=" + MaximumSpotAgeMinutes.ToString("G17"),
				"MinimumFuturesClosedMinutes=" + MinimumFuturesClosedMinutes.ToString("G17"),
				"MinimumClosedSpotMovePct=" + MinimumClosedSpotMovePct.ToString("G17"),
				"BasisMode=" + BasisModeDefault.ToString(),
				"BasisLookbackBars=" + BasisLookbackBars.ToString(),
				"BasisThresholdMode=" + BasisThresholdModeDefault.ToString(),
				"BasisAbsoluteThreshold=" + BasisAbsoluteThreshold.ToString("G17"),
				"BasisZThreshold=" + BasisZThreshold.ToString("G17"),
				"UseMaxHoldBars=" + UseMaxHoldBars.ToString(),
				"MaxHoldBars=" + MaxHoldBars.ToString(),
				"EnableDiagnostics=" + EnableDiagnostics.ToString(),
				"SpotInstrumentPlaceholder=" + SpotInstrumentPlaceholder
			});
		}
	}
}
