// @ElementOfFear
// V1 frozen event gate, timezone conversion, and rollover state machine.
// Pure deterministic. No NinjaTrader dependencies. ASCII only.

using System;
using System.Collections.Generic;

namespace BtcReopenMr.Core
{
	public enum ReopenType
	{
		None = 0,
		RegularDailyMaintenance = 1,
		RegularWeekend = 2
	}

	public static class V1FrozenConstants
	{
		// Certified: Ninja application/chart timezone on the development machine.
		public const string NinjaApplicationTimeZoneId = "Eastern Standard Time";
		// Certified: Trading Hours template timezone for CME FX Futures ETH.
		public const string ScheduleTimeZoneId = "Central Standard Time";

		public const int TimelyFirstBarMaxLagMinutes = 15;
		public const int CloseAnchorToleranceMinutes = 15;

		// First-test scientific window (PRE-24/7 only).
		public static readonly DateTime FirstTestStartChicagoDate = new DateTime(2018, 6, 11);
		public static readonly DateTime FirstTestEndChicagoDate = new DateTime(2024, 9, 1);
	}

	public static class SessionTimeConversion
	{
		private static readonly TimeZoneInfo AppTz = TimeZoneInfo.FindSystemTimeZoneById(
			V1FrozenConstants.NinjaApplicationTimeZoneId);
		private static readonly TimeZoneInfo ChicagoTz = TimeZoneInfo.FindSystemTimeZoneById(
			V1FrozenConstants.ScheduleTimeZoneId);

		public static TimeZoneInfo ApplicationTimeZone { get { return AppTz; } }
		public static TimeZoneInfo ChicagoTimeZone { get { return ChicagoTz; } }

		// Treat NT Times[0][0] as an Unspecified wall-clock in the application timezone.
		// Convert to America/Chicago wall-clock (Unspecified). Avoids DateTimeKind.Local accidents.
		public static DateTime NinjaBarTimeToChicago(DateTime ninjaBarTime)
		{
			DateTime unspecified = DateTime.SpecifyKind(ninjaBarTime, DateTimeKind.Unspecified);
			DateTime utc = TimeZoneInfo.ConvertTimeToUtc(unspecified, AppTz);
			DateTime chicago = TimeZoneInfo.ConvertTimeFromUtc(utc, ChicagoTz);
			return DateTime.SpecifyKind(chicago, DateTimeKind.Unspecified);
		}

		public static DateTime ChicagoWall(int year, int month, int day, int hour, int minute)
		{
			return new DateTime(year, month, day, hour, minute, 0, DateTimeKind.Unspecified);
		}
	}

	public sealed class ScheduledReopenMatch
	{
		public ReopenType Type;
		public DateTime ScheduledReopenChicago;
		public DateTime ScheduledCloseChicago;
	}

	public static class ExpectedReopenSchedule
	{
		// Causal: find the unique regular scheduled reopen R (if any) such that
		// previousChicago < R <= currentChicago, excluding special-session dates.
		public static bool TryFindScheduledReopenBetween(
			DateTime previousChicago,
			DateTime currentChicago,
			out ScheduledReopenMatch match)
		{
			match = null;
			if (currentChicago <= previousChicago)
				return false;

			// Candidate reopen clocks that can fall inside (prev, current]:
			// daily 17:00 Mon-Thu on currentChicago.Date and previousChicago.Date,
			// weekend Sunday 17:00 on those dates.
			List<ScheduledReopenMatch> candidates = new List<ScheduledReopenMatch>(4);
			AddCandidatesForCalendarDate(previousChicago.Date, candidates);
			if (currentChicago.Date != previousChicago.Date)
				AddCandidatesForCalendarDate(currentChicago.Date, candidates);

			ScheduledReopenMatch best = null;
			for (int i = 0; i < candidates.Count; i++)
			{
				ScheduledReopenMatch c = candidates[i];
				if (c.ScheduledReopenChicago > previousChicago
					&& c.ScheduledReopenChicago <= currentChicago)
				{
					if (best == null
						|| c.ScheduledReopenChicago < best.ScheduledReopenChicago)
						best = c;
				}
			}

			if (best == null)
				return false;
			match = best;
			return true;
		}

		private static void AddCandidatesForCalendarDate(DateTime date, List<ScheduledReopenMatch> into)
		{
			int wd = (int)date.DayOfWeek; // Sunday=0 ... Saturday=6
			if (wd >= 1 && wd <= 4)
			{
				// Mon-Thu daily maintenance reopen 17:00 CT; close same day 16:00 CT
				into.Add(new ScheduledReopenMatch
				{
					Type = ReopenType.RegularDailyMaintenance,
					ScheduledCloseChicago = SessionTimeConversion.ChicagoWall(
						date.Year, date.Month, date.Day, 16, 0),
					ScheduledReopenChicago = SessionTimeConversion.ChicagoWall(
						date.Year, date.Month, date.Day, 17, 0)
				});
			}
			else if (wd == 0)
			{
				// Sunday weekend reopen 17:00 CT; Friday close 16:00 CT
				DateTime friday = date.AddDays(-2);
				into.Add(new ScheduledReopenMatch
				{
					Type = ReopenType.RegularWeekend,
					ScheduledCloseChicago = SessionTimeConversion.ChicagoWall(
						friday.Year, friday.Month, friday.Day, 16, 0),
					ScheduledReopenChicago = SessionTimeConversion.ChicagoWall(
						date.Year, date.Month, date.Day, 17, 0)
				});
			}
		}

		public static bool IsInsideFirstTestInterval(DateTime chicagoBarTime)
		{
			DateTime d = chicagoBarTime.Date;
			return d >= V1FrozenConstants.FirstTestStartChicagoDate
				&& d <= V1FrozenConstants.FirstTestEndChicagoDate;
		}
	}

	public static class CloseAnchorRule
	{
		// Frozen meaning (recert):
		// previousObservedFuturesBar <= scheduledClose + CLOSE_ANCHOR_TOLERANCE_MINUTES
		// Exact inequality: previousChicago <= scheduledCloseChicago.AddMinutes(15)
		// Boundary previous == close+15 is ACCEPTED.
		// previous == close+15+epsilon is REJECTED.
		public static bool Passes(
			DateTime previousChicago,
			DateTime scheduledCloseChicago,
			out double minutesAfterClose)
		{
			minutesAfterClose = (previousChicago - scheduledCloseChicago).TotalMinutes;
			return previousChicago
				<= scheduledCloseChicago.AddMinutes(V1FrozenConstants.CloseAnchorToleranceMinutes);
		}
	}

	public static class TimelyFirstBarRule
	{
		// Frozen: 0 <= lagMinutes <= 15 where lag = current - scheduledReopen.
		// Boundary lag == 15 ACCEPTED. lag > 15 REJECTED. lag < 0 REJECTED.
		public static bool Passes(DateTime currentChicago, DateTime scheduledReopenChicago, out double lagMinutes)
		{
			lagMinutes = (currentChicago - scheduledReopenChicago).TotalMinutes;
			return lagMinutes >= 0.0
				&& lagMinutes <= (double)V1FrozenConstants.TimelyFirstBarMaxLagMinutes;
		}
	}

	public sealed class V1EventGateResult
	{
		public bool IsEventEligible;
		public DiagnosticCode Code;
		public ReopenType ReopenType;
		public DateTime ScheduledReopenChicago;
		public DateTime ScheduledCloseChicago;
		public double LagMinutes;
		public double MinutesAfterClose;
		public double FuturesGapMinutes;
		public bool DuplicateSuppressed;
		public string Detail;
	}

	// Causal first-observed-bar-after-reopen detector with duplicate suppression.
	public sealed class V1ReopenEventGate
	{
		private DateTime _lastProcessedScheduledReopenChicago = DateTime.MinValue;
		private bool _hasLastProcessed;

		public void Reset()
		{
			_hasLastProcessed = false;
			_lastProcessedScheduledReopenChicago = DateTime.MinValue;
		}

		public V1EventGateResult Evaluate(
			DateTime previousChicago,
			DateTime currentChicago,
			double futuresGapMinutes,
			double minimumFuturesClosedMinutes,
			bool postRollBasisReady)
		{
			var r = new V1EventGateResult();
			r.FuturesGapMinutes = futuresGapMinutes;
			r.LagMinutes = double.NaN;
			r.MinutesAfterClose = double.NaN;
			r.Detail = string.Empty;
			r.ReopenType = ReopenType.None;

			if (!ExpectedReopenSchedule.IsInsideFirstTestInterval(currentChicago))
			{
				r.Code = DiagnosticCode.OutsideV1Interval;
				r.Detail = "NOT_IN_FIRST_TEST_INTERVAL";
				return r;
			}

			ScheduledReopenMatch match;
			if (!ExpectedReopenSchedule.TryFindScheduledReopenBetween(
				previousChicago, currentChicago, out match))
			{
				r.Code = DiagnosticCode.NotExpectedReopen;
				r.Detail = "NOT_EXPECTED_REOPEN";
				return r;
			}

			r.ReopenType = match.Type;
			r.ScheduledReopenChicago = match.ScheduledReopenChicago;
			r.ScheduledCloseChicago = match.ScheduledCloseChicago;

			if (_hasLastProcessed
				&& match.ScheduledReopenChicago == _lastProcessedScheduledReopenChicago)
			{
				r.DuplicateSuppressed = true;
				r.Code = DiagnosticCode.DuplicateReopenSuppressed;
				r.Detail = "DUPLICATE_REOPEN_SUPPRESSED";
				return r;
			}

			// Mark processed once we have identified this scheduled reopen on its first bar,
			// regardless of later gate failures, so later bars do not re-evaluate it.
			_lastProcessedScheduledReopenChicago = match.ScheduledReopenChicago;
			_hasLastProcessed = true;

			DateTime exclusionDate = match.ScheduledReopenChicago.Date;
			if (match.Type == ReopenType.RegularWeekend)
			{
				// Weekend exclusions: Sunday reopen date or Friday close date in exclusion set.
				if (GeneratedV1Calendars.IsSpecialSessionExcluded(exclusionDate)
					|| GeneratedV1Calendars.IsSpecialSessionExcluded(match.ScheduledCloseChicago.Date))
				{
					r.Code = DiagnosticCode.SpecialSessionExcluded;
					r.Detail = "SPECIAL_SESSION_EXCLUDED";
					return r;
				}
			}
			else if (GeneratedV1Calendars.IsSpecialSessionExcluded(exclusionDate))
			{
				r.Code = DiagnosticCode.SpecialSessionExcluded;
				r.Detail = "SPECIAL_SESSION_EXCLUDED";
				return r;
			}

			if (!BasisMath.IsReopenGap(futuresGapMinutes, minimumFuturesClosedMinutes))
			{
				r.Code = DiagnosticCode.RawGapTooSmall;
				r.Detail = "RAW_GAP_TOO_SMALL";
				return r;
			}

			double lag;
			if (!TimelyFirstBarRule.Passes(currentChicago, match.ScheduledReopenChicago, out lag))
			{
				r.LagMinutes = lag;
				r.Code = DiagnosticCode.ReopenBarTooLate;
				r.Detail = "REOPEN_BAR_TOO_LATE";
				return r;
			}
			r.LagMinutes = lag;

			double afterClose;
			if (!CloseAnchorRule.Passes(previousChicago, match.ScheduledCloseChicago, out afterClose))
			{
				r.MinutesAfterClose = afterClose;
				r.Code = DiagnosticCode.CloseAnchorInvalid;
				r.Detail = "CLOSE_ANCHOR_INVALID";
				return r;
			}
			r.MinutesAfterClose = afterClose;

			if (!postRollBasisReady)
			{
				r.Code = DiagnosticCode.InsufficientPostRollBasisHistory;
				r.Detail = "POST_ROLL_BASIS_WARMUP";
				return r;
			}

			r.IsEventEligible = true;
			r.Code = DiagnosticCode.ExpectedReopenEligible;
			r.Detail = "EXPECTED_REOPEN_ELIGIBLE";
			return r;
		}
	}

	public sealed class RolloverProcessResult
	{
		public bool RolloverDetected;
		public bool BasisHistoryReset;
		public bool OpenPositionBasisExitDisabled;
		public bool RequiresForcedRolloverExit;
		public bool InvalidateEntryFreeze;
		public NtRolloverTransition Transition;
		public string Detail;
	}

	public enum ForcedExitKind
	{
		None = 0,
		RolloverBoundary = 1,
		V1TestWindowEnd = 2
	}

	// Pure V1 position lifecycle rules (no NinjaTrader dependency).
	public static class PositionLifecycleRules
	{
		public const string ExitRolloverBoundaryReason = "EXIT_ROLLOVER_BOUNDARY";
		public const string ExitV1TestWindowEndReason = "EXIT_V1_TEST_WINDOW_END";

		// Primary outcome policy (frozen before outcomes):
		// ROLLOVER_FORCED_EXIT_TRADE_TREATMENT = INCLUDE_IN_PRIMARY_RESULTS
		// V1_TERMINAL_FORCED_EXIT_TRADE_TREATMENT = INCLUDE_IN_PRIMARY_RESULTS
		public const string RolloverForcedExitTradeTreatment = "INCLUDE_IN_PRIMARY_RESULTS";
		public const string V1TerminalForcedExitTradeTreatment = "INCLUDE_IN_PRIMARY_RESULTS";

		// Causal terminal rule (America/Chicago calendar date):
		// First completed primary bar with chicagoBarTime.Date > FirstTestEndChicagoDate (2024-09-01)
		// triggers EXIT_V1_TEST_WINDOW_END when a position is still open.
		// Bars on 2024-09-01 remain inside the V1 event window (entries still allowed if eligible).
		public static bool IsPastV1TestWindowEnd(DateTime chicagoBarTime)
		{
			return chicagoBarTime.Date > V1FrozenConstants.FirstTestEndChicagoDate.Date;
		}

		public static ForcedExitKind EvaluateForcedExit(
			bool positionIsOpen,
			bool rolloverDetectedThisBar,
			DateTime chicagoBarTime,
			bool forcedExitAlreadyPending)
		{
			if (!positionIsOpen)
				return ForcedExitKind.None;
			if (forcedExitAlreadyPending)
				return ForcedExitKind.None;

			if (rolloverDetectedThisBar)
				return ForcedExitKind.RolloverBoundary;

			if (IsPastV1TestWindowEnd(chicagoBarTime))
				return ForcedExitKind.V1TestWindowEnd;

			return ForcedExitKind.None;
		}

		public static string ReasonString(ForcedExitKind kind)
		{
			if (kind == ForcedExitKind.RolloverBoundary)
				return ExitRolloverBoundaryReason;
			if (kind == ForcedExitKind.V1TestWindowEnd)
				return ExitV1TestWindowEndReason;
			return string.Empty;
		}

		public static DiagnosticCode ToDiagnosticCode(ForcedExitKind kind)
		{
			if (kind == ForcedExitKind.RolloverBoundary)
				return DiagnosticCode.ExitRolloverBoundary;
			if (kind == ForcedExitKind.V1TestWindowEnd)
				return DiagnosticCode.ExitV1TestWindowEnd;
			return DiagnosticCode.None;
		}

		// No new entry while a forced exit is pending or position remains open.
		public static bool AllowNewEntryEvaluation(
			bool positionIsOpen,
			bool forcedExitPending)
		{
			return !positionIsOpen && !forcedExitPending;
		}

		// After forced rollover exit request, basis-mean exit using old freeze must not run.
		public static bool AllowBasisMeanExit(
			bool hasEntryFreeze,
			bool forcedExitPending,
			bool basisExitDisabledForOpenPosition)
		{
			if (forcedExitPending)
				return false;
			if (basisExitDisabledForOpenPosition)
				return false;
			return hasEntryFreeze;
		}
	}

	// Tracks forced-exit pending state for deterministic unit tests of strategy lifecycle.
	public sealed class PositionLifecycleState
	{
		private bool _forcedExitPending;
		private ForcedExitKind _pendingKind;
		private double _entryBasisMean;
		private int _entryBasisDeviationSign;
		private bool _hasEntryFreeze;

		public bool ForcedExitPending { get { return _forcedExitPending; } }
		public ForcedExitKind PendingKind { get { return _pendingKind; } }
		public bool HasEntryFreeze { get { return _hasEntryFreeze; } }
		public double EntryBasisMean { get { return _entryBasisMean; } }
		public int EntryBasisDeviationSign { get { return _entryBasisDeviationSign; } }

		public void FreezeEntry(double entryBasis, double entryBasisMean)
		{
			_entryBasisMean = entryBasisMean;
			_entryBasisDeviationSign = ExitLogic.DeviationSign(entryBasis, entryBasisMean);
			_hasEntryFreeze = true;
		}

		public void InvalidateEntryFreeze()
		{
			_hasEntryFreeze = false;
			_entryBasisMean = 0.0;
			_entryBasisDeviationSign = 0;
		}

		public ForcedExitKind OnRolloverProcessed(bool positionIsOpen, bool rolloverDetected)
		{
			if (!rolloverDetected)
				return ForcedExitKind.None;

			InvalidateEntryFreeze();
			ForcedExitKind kind = PositionLifecycleRules.EvaluateForcedExit(
				positionIsOpen, true, DateTime.MinValue, _forcedExitPending);
			if (kind == ForcedExitKind.RolloverBoundary)
			{
				_forcedExitPending = true;
				_pendingKind = kind;
			}
			return kind;
		}

		public ForcedExitKind OnBarLifecycle(
			bool positionIsOpen,
			bool rolloverDetectedThisBar,
			DateTime chicagoBarTime)
		{
			if (rolloverDetectedThisBar)
				InvalidateEntryFreeze();

			ForcedExitKind kind = PositionLifecycleRules.EvaluateForcedExit(
				positionIsOpen, rolloverDetectedThisBar, chicagoBarTime, _forcedExitPending);
			if (kind != ForcedExitKind.None)
			{
				InvalidateEntryFreeze();
				_forcedExitPending = true;
				_pendingKind = kind;
			}
			return kind;
		}

		public void NoteFlat()
		{
			_forcedExitPending = false;
			_pendingKind = ForcedExitKind.None;
			InvalidateEntryFreeze();
		}

		public bool AllowNewEntry()
		{
			return PositionLifecycleRules.AllowNewEntryEvaluation(false, _forcedExitPending)
				&& !_hasEntryFreeze;
		}
	}

	// Applies certified NT rollover dates (calendar date America/Chicago).
	public sealed class NtRolloverStateMachine
	{
		private readonly NtRolloverTransition[] _transitions;
		private readonly bool[] _applied;
		private int _postRollBasisSamples;
		private bool _warmupActive;
		private bool _basisExitDisabledForOpenPosition;

		public NtRolloverStateMachine()
		{
			IReadOnlyList<NtRolloverTransition> src = GeneratedV1Calendars.GetRolloverTransitions();
			_transitions = new NtRolloverTransition[src.Count];
			for (int i = 0; i < src.Count; i++)
				_transitions[i] = src[i];
			_applied = new bool[_transitions.Length];
			_postRollBasisSamples = 0;
			_warmupActive = false;
			_basisExitDisabledForOpenPosition = false;
		}

		public int PostRollBasisSamples { get { return _postRollBasisSamples; } }
		public bool WarmupActive { get { return _warmupActive; } }
		public bool BasisExitDisabledForOpenPosition { get { return _basisExitDisabledForOpenPosition; } }

		public bool IsPostRollBasisReady(int requiredLookback)
		{
			if (!_warmupActive)
				return true;
			if (_postRollBasisSamples >= requiredLookback)
			{
				_warmupActive = false;
				return true;
			}
			return false;
		}

		public void NoteBasisSampleAdded()
		{
			if (_warmupActive)
				_postRollBasisSamples++;
		}

		public void ClearOpenPositionBasisExitDisableWhenFlat()
		{
			_basisExitDisabledForOpenPosition = false;
		}

		// Detect only: mark transition applied. Does NOT clear basis history.
		// Strategy must call ApplyRolloverReset after invalidating freeze / submitting forced exit.
		public RolloverProcessResult DetectRollover(DateTime chicagoBarTime, bool positionIsOpen)
		{
			var result = new RolloverProcessResult();
			result.Detail = string.Empty;
			DateTime d = chicagoBarTime.Date;

			for (int i = 0; i < _transitions.Length; i++)
			{
				if (_applied[i])
					continue;
				if (d < _transitions[i].NtRolloverDate)
					break;

				_applied[i] = true;
				result.RolloverDetected = true;
				result.InvalidateEntryFreeze = true;
				result.Transition = _transitions[i];
				result.Detail = "ROLLOVER_DETECTED|" + _transitions[i].OldContract
					+ "->" + _transitions[i].NewContract
					+ "|date=" + _transitions[i].NtRolloverDate.ToString("yyyy-MM-dd");

				if (positionIsOpen)
				{
					_basisExitDisabledForOpenPosition = true;
					result.OpenPositionBasisExitDisabled = true;
					result.RequiresForcedRolloverExit = true;
					result.Detail += "|REQUIRES_EXIT_ROLLOVER_BOUNDARY";
				}
			}

			return result;
		}

		public void ApplyRolloverReset(CausalBasisHistory basisHistory)
		{
			basisHistory.Clear();
			_postRollBasisSamples = 0;
			_warmupActive = true;
		}

		// V4 residual history stays continuous across rolls. Only structural bar-level
		// post-roll warmup is armed (matches Stage2A event-universe gate).
		public void BeginPostRollWarmup()
		{
			_postRollBasisSamples = 0;
			_warmupActive = true;
		}

		// Combined helper for tests: detect then reset (same net effect as historical ProcessBar).
		public RolloverProcessResult ProcessBar(
			DateTime chicagoBarTime,
			CausalBasisHistory basisHistory,
			bool positionIsOpen)
		{
			RolloverProcessResult result = DetectRollover(chicagoBarTime, positionIsOpen);
			if (result.RolloverDetected)
			{
				ApplyRolloverReset(basisHistory);
				result.BasisHistoryReset = true;
			}
			return result;
		}
	}
}
