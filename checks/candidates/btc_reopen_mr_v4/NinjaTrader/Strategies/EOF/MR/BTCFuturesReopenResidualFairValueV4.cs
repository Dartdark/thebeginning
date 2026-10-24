// Public forum copy.
// Strategy/trading semantics are unchanged from the authoritative
// BTCREOPENMR V4 source. Machine-specific/private metadata has been
// removed or replaced. See SANITIZATION_REPORT.
//
// Research concept inspired by Matteo's BTC reopen mean-reversion video.
// This implementation, testing, execution qualification, and residual
// fair-value formulation are the author's subsequent research work.

// @ElementOfFear
// BTCFuturesReopenResidualFairValueV4 — NinjaTrader 8
// Frozen H1B_z_lb60_abs1.5 executable translation. No V2/V3 spot-move gate.
// Fixed 60-minute exit from entry fill. One position. ASCII only.

#region Using declarations
using System;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.Globalization;
using System.IO;
using System.Text;
using System.Xml.Serialization;
using BtcReopenMr.Core;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
#endregion

namespace NinjaTrader.NinjaScript.Strategies.EOF.MR
{
	public class BTCFuturesReopenResidualFairValueV4 : Strategy
	{
		private const int SpotBarsIndex = 1;
		private const string ExplicitSpotTradingHoursLiteral = "Cryptocurrency";
		private const string LongSignal = "H1_L";
		private const string ShortSignal = "H1_S";
		private const string ExitLongSignal = "ExitL";
		private const string ExitShortSignal = "ExitS";

		private SpotObservationBuffer _spotBuffer;
		private CausalResidualHistory _residualHistory;
		private V1ReopenEventGate _eventGate;
		private NtRolloverStateMachine _rolloverState;

		private DateTime _lastFuturesBarTime = DateTime.MinValue;
		private bool _hasLastFuturesBarTime;
		private double _futuresLastPreclosePrice;
		private double _spotAtFuturesClose;
		private DateTime _spotAtFuturesCloseTime = DateTime.MinValue;
		private bool _hasSpotAtFuturesClose;

		private bool _entryPending;
		private bool _exitPending;
		private bool _hasScheduledExit;
		private DateTime _entryFillTime = DateTime.MinValue;
		private DateTime _scheduledExitTime = DateTime.MinValue;
		private string _activeEntrySignal = string.Empty;
		private bool _forcedExitPending;
		private ForcedExitKind _forcedExitPendingKind;

		private StreamWriter _csvWriter;
		private bool _spotSeriesVerified;

		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Name = V4StrategyConstants.StrategyName;
				Description = "V4 H1 residual fair-value (H1B_z_lb60_abs1.5). Fade residual Z. Fixed 60m exit from entry fill. Explicit Cryptocurrency BIP1 + hard identity. No V2/V3 spot-move gate.";
				Calculate = Calculate.OnBarClose;
				EntriesPerDirection = 1;
				EntryHandling = EntryHandling.AllEntries;
				IsExitOnSessionCloseStrategy = false;
				IsFillLimitOnTouch = false;
				MaximumBarsLookBack = MaximumBarsLookBack.TwoHundredFiftySix;
				OrderFillResolution = OrderFillResolution.Standard;
				Slippage = 0;
				StartBehavior = StartBehavior.WaitUntilFlat;
				TimeInForce = TimeInForce.Gtc;
				TraceOrders = false;
				RealtimeErrorHandling = RealtimeErrorHandling.StopCancelClose;
				StopTargetHandling = StopTargetHandling.PerEntryExecution;
				BarsRequiredToTrade = 1;
				IsInstantiatedOnEachOptimizationIteration = true;
				DefaultQuantity = 1;

				SpotInstrument = "BTCUSD";
				SpotBarsPeriodMinutes = 1;
				MaximumSpotAgeMinutes = V4StrategyConstants.MaximumSpotAgeMinutes;
				MinimumFuturesClosedMinutes = V4StrategyConstants.MinimumFuturesClosedMinutes;
				ResidualLookbackEvents = V4StrategyConstants.ResidualLookbackEvents;
				AbsResidualZThreshold = V4StrategyConstants.AbsResidualZThreshold;
				ExecutableExitHoldMinutes = V4StrategyConstants.ExecutableExitHoldMinutes;
				EnableDiagnostics = true;
				DiagnosticsCsvPath = string.Empty;
			}
			else if (State == State.Configure)
			{
				ValidateSpotInstrumentOrThrow();
				AddDataSeries(
					"BTCUSD",
					new BarsPeriod
					{
						BarsPeriodType = BarsPeriodType.Minute,
						Value = SpotBarsPeriodMinutes,
						MarketDataType = MarketDataType.Last
					},
					ExplicitSpotTradingHoursLiteral);
			}
			else if (State == State.DataLoaded)
			{
				if (BarsArray == null || BarsArray.Length <= SpotBarsIndex || BarsArray[SpotBarsIndex] == null)
				{
					throw new InvalidOperationException(
						"BTCFuturesReopenResidualFairValueV4: failed to load SpotInstrument series '" + SpotInstrument
						+ "'. Refusing to substitute another instrument.");
				}

				EnforcePrimaryBarsPeriodOrThrow();
				EnforceSpotIdentityOrThrow();

				_spotSeriesVerified = true;
				_spotBuffer = new SpotObservationBuffer(4096);
				_residualHistory = new CausalResidualHistory(Math.Max(2, ResidualLookbackEvents));
				_eventGate = new V1ReopenEventGate();
				_rolloverState = new NtRolloverStateMachine();
				_hasLastFuturesBarTime = false;
				_hasSpotAtFuturesClose = false;
				_entryPending = false;
				_exitPending = false;
				_hasScheduledExit = false;
				_forcedExitPending = false;
				_forcedExitPendingKind = ForcedExitKind.None;
				_activeEntrySignal = string.Empty;

				OpenCsvIfConfigured();
				DiagPrint("DataLoaded primary=" + (Instrument != null ? Instrument.FullName : string.Empty)
					+ " spot=" + (BarsArray[SpotBarsIndex].Instrument != null ? BarsArray[SpotBarsIndex].Instrument.FullName : SpotInstrument)
					+ " explicitSpotTH=" + ExplicitSpotTradingHoursLiteral
					+ " lookback=" + ResidualLookbackEvents.ToString(CultureInfo.InvariantCulture)
					+ " absZ=" + AbsResidualZThreshold.ToString("G17", CultureInfo.InvariantCulture)
					+ " exitHoldMin=" + ExecutableExitHoldMinutes.ToString(CultureInfo.InvariantCulture)
					+ " noSpotMoveGate=1 noRawDollarBasisGate=1 noBasisMeanExit=1"
					+ " Calculate=OnBarClose OrderFillResolution=Standard");
			}
			else if (State == State.Terminated)
			{
				CloseCsv();
			}
		}

		protected override void OnBarUpdate()
		{
			if (!_spotSeriesVerified)
				return;

			if (BarsInProgress == SpotBarsIndex)
			{
				if (CurrentBars[SpotBarsIndex] >= 0)
					_spotBuffer.Add(Times[SpotBarsIndex][0], Closes[SpotBarsIndex][0]);
				return;
			}

			if (BarsInProgress != 0)
				return;
			if (CurrentBars[0] < 0)
				return;

			DateTime currentFuturesBarTime = Times[0][0];
			double futuresPrice = Closes[0][0];
			DateTime currentChicago = SessionTimeConversion.NinjaBarTimeToChicago(currentFuturesBarTime);

			bool positionOpen = Position.MarketPosition != MarketPosition.Flat;

			if (!positionOpen && _forcedExitPending)
			{
				_forcedExitPending = false;
				_forcedExitPendingKind = ForcedExitKind.None;
				ClearLifecycleFlags();
				DiagPrint("FORCED_EXIT_FLAT_CLEARED");
			}

			RolloverProcessResult roll = _rolloverState.DetectRollover(currentChicago, positionOpen);
			if (roll.RolloverDetected)
			{
				// Residual event history remains continuous (Stage1 event-ordered Z).
				// Arm Stage2A structural post-roll warmup only; do not Clear residual history.
				_rolloverState.BeginPostRollWarmup();
				DiagPrint("ROLLOVER_DETECTED " + roll.Detail + " postRollWarmupArmed=1 residualHistoryCleared=0");
			}

			ForcedExitKind forced = PositionLifecycleRules.EvaluateForcedExit(
				positionOpen,
				roll.RequiresForcedRolloverExit,
				currentChicago,
				_forcedExitPending);
			if (forced != ForcedExitKind.None)
			{
				SubmitExit(PositionLifecycleRules.ReasonString(forced));
				_forcedExitPending = true;
				_forcedExitPendingKind = forced;
				_hasScheduledExit = false;
			}

			// Fixed 60m exit from entry fill (clock minutes, not bars).
			if (positionOpen && !_forcedExitPending && _hasScheduledExit
				&& V4ExitSchedule.ShouldSignalExit(currentFuturesBarTime, _scheduledExitTime)
				&& !_exitPending)
			{
				SubmitExit("EXIT_FIXED_60M");
				_exitPending = true;
			}

			double futuresGapMinutes = 0.0;
			if (_hasLastFuturesBarTime)
				futuresGapMinutes = (currentFuturesBarTime - _lastFuturesBarTime).TotalMinutes;

			// Equal-timestamp BIP parity: if BIP0 runs before BIP1, the spot buffer may still
			// lack Times[1][0]==primary. Offline Stage2A uses at_or_before(reopen) inclusive.
			// Sync current BIP1 bar into the buffer before residual evaluation.
			SyncSpotBufferFromBip1(currentFuturesBarTime);

			DateTime spotTimeAtSignal = DateTime.MinValue;
			double spotAtSignal = 0.0;
			bool hasSpotAtSignal = _spotBuffer.TryGetAtOrBefore(
				currentFuturesBarTime, out spotAtSignal, out spotTimeAtSignal);
			double spotAgeMinutes;
			SpotEndpointFreshness spotFresh = SpotFreshness.Evaluate(
				currentFuturesBarTime, spotTimeAtSignal, hasSpotAtSignal, MaximumSpotAgeMinutes, out spotAgeMinutes);
			if (spotFresh != SpotEndpointFreshness.Ok)
				hasSpotAtSignal = false;

			bool allowEntryEval = PositionLifecycleRules.AllowNewEntryEvaluation(
				positionOpen, _forcedExitPending)
				&& !_entryPending
				&& !_exitPending;

			if (_hasLastFuturesBarTime && allowEntryEval)
			{
				DateTime previousChicago = SessionTimeConversion.NinjaBarTimeToChicago(_lastFuturesBarTime);
				bool postRollReady = _rolloverState.IsPostRollBasisReady(ResidualLookbackEvents);
				V1EventGateResult gate = _eventGate.Evaluate(
					previousChicago,
					currentChicago,
					futuresGapMinutes,
					MinimumFuturesClosedMinutes,
					postRollReady);

				if (gate.IsEventEligible)
				{
					EvaluateResidualReopen(
						currentFuturesBarTime,
						_lastFuturesBarTime,
						futuresPrice,
						hasSpotAtSignal,
						spotAtSignal,
						spotTimeAtSignal);
				}
				else if (gate.Code == DiagnosticCode.InsufficientPostRollBasisHistory)
				{
					DiagPrint("INSUFFICIENT_POST_ROLL_WARMUP samples="
						+ _rolloverState.PostRollBasisSamples.ToString(CultureInfo.InvariantCulture)
						+ " required=" + ResidualLookbackEvents.ToString(CultureInfo.InvariantCulture));
				}
			}

			// Structural post-roll warmup samples (bar-level, same as Stage2A).
			if (hasSpotAtSignal && spotAtSignal > 0.0 && futuresPrice > 0.0)
				_rolloverState.NoteBasisSampleAdded();

			// Preserve preclose anchors for next bar (spot/futures at this bar become prior).
			_futuresLastPreclosePrice = futuresPrice;
			_spotAtFuturesClose = spotAtSignal;
			_spotAtFuturesCloseTime = spotTimeAtSignal;
			_hasSpotAtFuturesClose = hasSpotAtSignal;
			_lastFuturesBarTime = currentFuturesBarTime;
			_hasLastFuturesBarTime = true;
		}

		protected override void OnExecutionUpdate(
			Execution execution,
			string executionId,
			double price,
			int quantity,
			MarketPosition marketPosition,
			string orderId,
			DateTime time)
		{
			if (execution == null || execution.Order == null)
				return;
			string sig = execution.Order.Name ?? string.Empty;
			if (sig == LongSignal || sig == ShortSignal)
			{
				_entryPending = false;
				_entryFillTime = time;
				_scheduledExitTime = V4ExitSchedule.ScheduledExitTime(time, ExecutableExitHoldMinutes);
				_hasScheduledExit = true;
				DiagPrint("ENTRY_FILL signal=" + sig
					+ " time=" + time.ToString("o", CultureInfo.InvariantCulture)
					+ " px=" + price.ToString("G17", CultureInfo.InvariantCulture)
					+ " scheduledExit=" + _scheduledExitTime.ToString("o", CultureInfo.InvariantCulture));
				WriteDiagCsv(
					"ENTRY_FILL", time, time, price, string.Empty, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
					sig, time, price, _scheduledExitTime, DateTime.MinValue, DateTime.MinValue, 0.0, string.Empty);
			}
			else if (sig == ExitLongSignal || sig == ExitShortSignal)
			{
				_exitPending = false;
				_hasScheduledExit = false;
				_activeEntrySignal = string.Empty;
				DiagPrint("EXIT_FILL signal=" + sig
					+ " time=" + time.ToString("o", CultureInfo.InvariantCulture)
					+ " px=" + price.ToString("G17", CultureInfo.InvariantCulture));
			}
		}

		private void EvaluateResidualReopen(
			DateTime reopenTime,
			DateTime precloseTime,
			double futuresReopenPrice,
			bool hasSpotPreReopen,
			double spotPreReopen,
			DateTime spotPreReopenTime)
		{
			string suppression = string.Empty;
			SignalDirection direction = SignalDirection.None;
			double spotGap = double.NaN;
			double futReopenRet = double.NaN;
			double residual = double.NaN;
			double residualBps = double.NaN;
			double z = double.NaN;
			double baseMean = double.NaN;
			double baseStd = double.NaN;

			if (!_hasSpotAtFuturesClose || !hasSpotPreReopen
				|| _spotAtFuturesClose <= 0.0 || spotPreReopen <= 0.0
				|| _futuresLastPreclosePrice <= 0.0 || futuresReopenPrice <= 0.0)
			{
				suppression = "SPOT_OR_FUTURES_ANCHOR_MISSING";
				WriteSignalDiag(reopenTime, precloseTime, futuresReopenPrice, spotPreReopen, spotPreReopenTime,
					spotGap, futReopenRet, residual, residualBps, baseMean, baseStd, z, direction, suppression);
				return;
			}

			spotGap = V4ResidualMath.SpotGapReturn(spotPreReopen, _spotAtFuturesClose);
			futReopenRet = V4ResidualMath.FuturesReopenReturn(futuresReopenPrice, _futuresLastPreclosePrice);
			residual = V4ResidualMath.ResidualReturn(futReopenRet, spotGap);
			residualBps = V4ResidualMath.ResidualBps(residual);

			bool ready = _residualHistory.TryGetMeanStd(out baseMean, out baseStd);
			if (ready)
				z = V4ResidualMath.CausalZ(residualBps, baseMean, baseStd);

			// Always append current residual AFTER baseline read (exclude current).
			_residualHistory.AddCompleted(residualBps);

			if (!ready)
			{
				suppression = "RESIDUAL_LOOKBACK_WARMUP";
				WriteSignalDiag(reopenTime, precloseTime, futuresReopenPrice, spotPreReopen, spotPreReopenTime,
					spotGap, futReopenRet, residual, residualBps, baseMean, baseStd, z, direction, suppression);
				return;
			}

			direction = V4ResidualMath.DirectionFromZ(z, AbsResidualZThreshold);
			if (direction == SignalDirection.None)
			{
				suppression = "ABS_Z_BELOW_THRESHOLD";
				WriteSignalDiag(reopenTime, precloseTime, futuresReopenPrice, spotPreReopen, spotPreReopenTime,
					spotGap, futReopenRet, residual, residualBps, baseMean, baseStd, z, direction, suppression);
				return;
			}

			if (Position.MarketPosition != MarketPosition.Flat || _entryPending || _exitPending || _forcedExitPending)
			{
				if (_entryPending)
					suppression = "SUPPRESSED_ENTRY_PENDING";
				else if (_exitPending)
					suppression = "SUPPRESSED_EXIT_PENDING";
				else if (_forcedExitPending)
					suppression = "SUPPRESSED_FORCED_EXIT_PENDING";
				else
					suppression = "SUPPRESSED_OPEN";
				WriteSignalDiag(reopenTime, precloseTime, futuresReopenPrice, spotPreReopen, spotPreReopenTime,
					spotGap, futReopenRet, residual, residualBps, baseMean, baseStd, z, direction, suppression);
				return;
			}

			if (direction == SignalDirection.Long)
			{
				EnterLong(DefaultQuantity, LongSignal);
				_activeEntrySignal = LongSignal;
			}
			else
			{
				EnterShort(DefaultQuantity, ShortSignal);
				_activeEntrySignal = ShortSignal;
			}
			_entryPending = true;

			WriteSignalDiag(reopenTime, precloseTime, futuresReopenPrice, spotPreReopen, spotPreReopenTime,
				spotGap, futReopenRet, residual, residualBps, baseMean, baseStd, z, direction, string.Empty);
			DiagPrint("ENTRY_SIGNAL dir=" + direction
				+ " z=" + z.ToString("G17", CultureInfo.InvariantCulture)
				+ " residualBps=" + residualBps.ToString("G17", CultureInfo.InvariantCulture)
				+ " reopen=" + reopenTime.ToString("o", CultureInfo.InvariantCulture));
		}

		private void SubmitExit(string reason)
		{
			if (Position.MarketPosition == MarketPosition.Long)
				ExitLong(ExitLongSignal, LongSignal);
			else if (Position.MarketPosition == MarketPosition.Short)
				ExitShort(ExitShortSignal, ShortSignal);
			else
				return;
			DiagPrint(reason + " time=" + Times[0][0].ToString("o", CultureInfo.InvariantCulture));
		}

		private void ClearLifecycleFlags()
		{
			_entryPending = false;
			_exitPending = false;
			_hasScheduledExit = false;
			_activeEntrySignal = string.Empty;
		}

		// Offline Stage2A residual uses spot.at_or_before(reopen) inclusive of equal timestamps.
		// NT may invoke BIP0 before BIP1 on the same timestamp; pull BarsArray[1] explicitly.
		private void SyncSpotBufferFromBip1(DateTime currentFuturesBarTime)
		{
			if (CurrentBars == null || CurrentBars.Length <= SpotBarsIndex)
				return;
			if (CurrentBars[SpotBarsIndex] < 0)
				return;
			DateTime spotBarTime = Times[SpotBarsIndex][0];
			double spotBarPx = Closes[SpotBarsIndex][0];
			if (spotBarPx > 0.0 && spotBarTime <= currentFuturesBarTime)
				_spotBuffer.Add(spotBarTime, spotBarPx);
		}

		private void EnforceSpotIdentityOrThrow()
		{
			Instrument spotInst = BarsArray[SpotBarsIndex].Instrument;
			MasterInstrument mi = spotInst != null ? spotInst.MasterInstrument : null;

			string instrumentDefaultTh = string.Empty;
			if (mi != null && mi.TradingHours != null)
				instrumentDefaultTh = mi.TradingHours.Name ?? string.Empty;

			string bip1BarsTh = string.Empty;
			if (BarsArray[SpotBarsIndex].TradingHours != null)
				bip1BarsTh = BarsArray[SpotBarsIndex].TradingHours.Name ?? string.Empty;

			long masterId = mi != null ? mi.Id : 0L;
			string typeName = mi != null ? mi.InstrumentType.ToString() : string.Empty;
			string exchangeName = spotInst != null ? spotInst.Exchange.ToString() : string.Empty;

			var snap = new Spot24x7IdentitySnapshot
			{
				RequestedSpotInstrument = SpotInstrument,
				ResolvedFullName = spotInst != null ? (spotInst.FullName ?? string.Empty) : string.Empty,
				ResolvedMasterInstrumentName = mi != null ? (mi.Name ?? string.Empty) : string.Empty,
				ResolvedMasterInstrumentId = masterId,
				ResolvedInstrumentType = typeName,
				ResolvedExchange = exchangeName,
				InstrumentDefaultTradingHours = instrumentDefaultTh,
				Bip1ActualBarsTradingHours = bip1BarsTh,
				RequestedExplicitTradingHours = ExplicitSpotTradingHoursLiteral
			};

			string idReason;
			string thReason;
			bool idOk = Spot24x7IdentityValidator.IsIntendedCryptoBtcUsd(snap, out idReason);
			bool thOk = Spot24x7IdentityValidator.BarsTradingHoursMatchesExplicit(snap, out thReason);
			if (!idOk || !thOk)
			{
				throw new InvalidOperationException(
					"BTCFuturesReopenResidualFairValueV4: BIP1 identity/TradingHours certification FAILED. "
					+ "idReason=" + idReason
					+ " thReason=" + thReason
					+ " actual masterId=" + masterId.ToString(CultureInfo.InvariantCulture)
					+ " type=" + typeName
					+ " exchange=" + exchangeName
					+ " bip1BarsTH=" + bip1BarsTh
					+ ". Expected masterId=" + V4StrategyConstants.ExpectedSpotMasterInstrumentId.ToString(CultureInfo.InvariantCulture)
					+ " type=" + V4StrategyConstants.ExpectedSpotInstrumentType
					+ " exchange=" + V4StrategyConstants.ExpectedSpotExchange
					+ " BarsArray[1].TradingHours=" + V4StrategyConstants.ExplicitSpotTradingHoursTemplate
					+ ". No silent fallback.");
			}
		}

		private void ValidateSpotInstrumentOrThrow()
		{
			if (string.IsNullOrWhiteSpace(SpotInstrument)
				|| SpotInstrument.Trim().StartsWith("REQUIRED_SELECT", StringComparison.OrdinalIgnoreCase))
			{
				throw new InvalidOperationException(
					"BTCFuturesReopenResidualFairValueV4: SpotInstrument must be explicitly set to BTCUSD.");
			}
		}

		private void EnforcePrimaryBarsPeriodOrThrow()
		{
			string typeName = "UNKNOWN";
			int value = 0;
			if (BarsPeriod != null)
			{
				typeName = BarsPeriod.BarsPeriodType.ToString();
				value = BarsPeriod.Value;
			}
			string reason;
			PrimaryBarsCompatibility compat = PrimaryBarsPeriodGuard.Evaluate(
				typeName, value, MinimumFuturesClosedMinutes, out reason);
			if (compat != PrimaryBarsCompatibility.Compatible)
			{
				throw new InvalidOperationException(
					"BTCFuturesReopenResidualFairValueV4: invalid primary bars period. " + reason);
			}
		}

		private void WriteSignalDiag(
			DateTime reopenTime,
			DateTime precloseTime,
			double futuresReopenPrice,
			double spotPreReopen,
			DateTime spotPreReopenTime,
			double spotGap,
			double futReopenRet,
			double residual,
			double residualBps,
			double baseMean,
			double baseStd,
			double z,
			SignalDirection direction,
			string suppression)
		{
			WriteDiagCsv(
				"SIGNAL",
				reopenTime,
				precloseTime,
				futuresReopenPrice,
				spotPreReopenTime.ToString("o", CultureInfo.InvariantCulture),
				_hasSpotAtFuturesClose ? _spotAtFuturesClose : 0.0,
				spotPreReopen,
				_futuresLastPreclosePrice,
				spotGap,
				futReopenRet,
				residual,
				z,
				direction.ToString(),
				DateTime.MinValue,
				0.0,
				DateTime.MinValue,
				DateTime.MinValue,
				DateTime.MinValue,
				0.0,
				suppression);
			DiagPrint("SIGNAL z=" + z.ToString("G17", CultureInfo.InvariantCulture)
				+ " residualBps=" + residualBps.ToString("G17", CultureInfo.InvariantCulture)
				+ " dir=" + direction
				+ " suppression=" + suppression
				+ " baseMean=" + baseMean.ToString("G17", CultureInfo.InvariantCulture)
				+ " baseStd=" + baseStd.ToString("G17", CultureInfo.InvariantCulture));
		}

		private void WriteDiagCsv(
			string tag,
			DateTime reopenTime,
			DateTime precloseTime,
			double futuresReopenPrice,
			string spotPreReopenTime,
			double spotClose,
			double spotPre,
			double futPreclose,
			double spotGap,
			double futReopenRet,
			double residual,
			double z,
			string direction,
			DateTime entrySignalTime,
			double entryFillPrice,
			DateTime scheduledExit,
			DateTime exitSignalTime,
			DateTime exitFillTime,
			double returnBps,
			string suppression)
		{
			if (_csvWriter == null)
				return;
			string line = string.Join(",", new string[]
			{
				tag,
				reopenTime.ToString("o", CultureInfo.InvariantCulture),
				precloseTime.ToString("o", CultureInfo.InvariantCulture),
				_spotAtFuturesCloseTime.ToString("o", CultureInfo.InvariantCulture),
				spotClose.ToString("G17", CultureInfo.InvariantCulture),
				spotPreReopenTime,
				spotPre.ToString("G17", CultureInfo.InvariantCulture),
				futPreclose.ToString("G17", CultureInfo.InvariantCulture),
				futuresReopenPrice.ToString("G17", CultureInfo.InvariantCulture),
				spotGap.ToString("G17", CultureInfo.InvariantCulture),
				futReopenRet.ToString("G17", CultureInfo.InvariantCulture),
				residual.ToString("G17", CultureInfo.InvariantCulture),
				z.ToString("G17", CultureInfo.InvariantCulture),
				direction,
				entrySignalTime == DateTime.MinValue ? string.Empty : entrySignalTime.ToString("o", CultureInfo.InvariantCulture),
				entryFillPrice.ToString("G17", CultureInfo.InvariantCulture),
				scheduledExit == DateTime.MinValue ? string.Empty : scheduledExit.ToString("o", CultureInfo.InvariantCulture),
				exitSignalTime == DateTime.MinValue ? string.Empty : exitSignalTime.ToString("o", CultureInfo.InvariantCulture),
				exitFillTime == DateTime.MinValue ? string.Empty : exitFillTime.ToString("o", CultureInfo.InvariantCulture),
				returnBps.ToString("G17", CultureInfo.InvariantCulture),
				suppression ?? string.Empty
			});
			_csvWriter.WriteLine(line);
			_csvWriter.Flush();
		}

		private void DiagPrint(string message)
		{
			if (EnableDiagnostics)
				Print("BTCFuturesReopenResidualFairValueV4|" + message);
		}

		private void OpenCsvIfConfigured()
		{
			CloseCsv();
			if (!EnableDiagnostics || string.IsNullOrWhiteSpace(DiagnosticsCsvPath))
				return;
			string path = DiagnosticsCsvPath.Trim();
			string dir = Path.GetDirectoryName(path);
			if (!string.IsNullOrEmpty(dir) && !Directory.Exists(dir))
				Directory.CreateDirectory(dir);
			_csvWriter = new StreamWriter(path, false, Encoding.ASCII);
			_csvWriter.WriteLine(
				"tag,reopen_time,futures_preclose_time,spot_close_time,spot_at_futures_close,spot_pre_reopen_time,spot_pre_reopen,"
				+ "futures_preclose_price,futures_reopen_price,spot_gap_return,futures_reopen_return,residual_return,residual_z,"
				+ "signal_direction,entry_signal_time,entry_fill_price,scheduled_exit_time,exit_signal_time,exit_fill_time,return_bps,suppression_reason");
			_csvWriter.Flush();
		}

		private void CloseCsv()
		{
			if (_csvWriter != null)
			{
				_csvWriter.Flush();
				_csvWriter.Dispose();
				_csvWriter = null;
			}
		}

		#region Properties

		[NinjaScriptProperty]
		[Display(Name = "SpotInstrument", Description = "Must resolve to BIP1 CryptoCurrency BTCUSD Gdax.", Order = 1, GroupName = "01 Data")]
		public string SpotInstrument { get; set; }

		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name = "SpotBarsPeriodMinutes", Order = 2, GroupName = "01 Data")]
		public int SpotBarsPeriodMinutes { get; set; }

		[NinjaScriptProperty]
		[Range(0.0, double.MaxValue)]
		[Display(Name = "MaximumSpotAgeMinutes", Order = 3, GroupName = "01 Data")]
		public double MaximumSpotAgeMinutes { get; set; }

		[NinjaScriptProperty]
		[Range(1.0, double.MaxValue)]
		[Display(Name = "MinimumFuturesClosedMinutes", Order = 1, GroupName = "02 Reopen Detection")]
		public double MinimumFuturesClosedMinutes { get; set; }

		[NinjaScriptProperty]
		[Range(2, int.MaxValue)]
		[Display(Name = "ResidualLookbackEvents", Description = "Frozen H1B lookback = 60 prior eligible residuals.", Order = 1, GroupName = "03 Residual H1")]
		public int ResidualLookbackEvents { get; set; }

		[NinjaScriptProperty]
		[Range(0.0, double.MaxValue)]
		[Display(Name = "AbsResidualZThreshold", Description = "Frozen H1B abs Z = 1.5.", Order = 2, GroupName = "03 Residual H1")]
		public double AbsResidualZThreshold { get; set; }

		[NinjaScriptProperty]
		[Range(1, int.MaxValue)]
		[Display(Name = "ExecutableExitHoldMinutes", Description = "Frozen 60 clock minutes from entry fill.", Order = 1, GroupName = "04 Exit")]
		public int ExecutableExitHoldMinutes { get; set; }

		[NinjaScriptProperty]
		[Display(Name = "EnableDiagnostics", Order = 1, GroupName = "05 Diagnostics")]
		public bool EnableDiagnostics { get; set; }

		[NinjaScriptProperty]
		[Display(Name = "DiagnosticsCsvPath", Order = 2, GroupName = "05 Diagnostics")]
		public string DiagnosticsCsvPath { get; set; }

		#endregion
	}
}
