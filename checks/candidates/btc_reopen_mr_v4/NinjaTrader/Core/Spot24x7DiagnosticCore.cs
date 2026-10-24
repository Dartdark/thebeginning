// @ElementOfFear
// V2 spot 24x7 diagnostic helpers. No NinjaTrader deps. ASCII only.
// ZERO_ORDER_DESIGN. Thresholds frozen at V1 defaults.

using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;

namespace BtcReopenMr.Core
{
	public static class Spot24x7DiagnosticConstants
	{
		public const string StrategyName = "BTCFuturesReopenSpot24x7Diagnostic";
		public const string ExplicitSpotTradingHoursTemplate = "Cryptocurrency";
		public const string CanonicalOutputDirectory =
			@"C:\Data\BTCREOPENMR\results\nt_spot24x7_diagnostic";

		public const long ExpectedSpotMasterInstrumentId = 699839150753921L;
		public const string ExpectedSpotInstrumentType = "CryptoCurrency";
		public const string ExpectedSpotExchange = "Gdax";

		public const double SpotMoveThresholdPct = 1.0;
		public const double BasisZThreshold = 2.0;
		public const int BasisLookbackBars = 60;
		public const double MaximumSpotAgeMinutes = 5.0;
		public const double MinimumFuturesClosedMinutes = 30.0;

		public const string RuntimeIdentityCsvHeader =
			"RequestedSpotInstrument,ResolvedFullName,ResolvedMasterInstrumentName,ResolvedMasterInstrumentId,"
			+ "ResolvedInstrumentType,ResolvedExchange,INSTRUMENT_DEFAULT_TRADING_HOURS,BIP1_ACTUAL_BARS_TRADING_HOURS,"
			+ "RequestedExplicitTradingHours,BarsPeriod,MarketDataType,DIAGNOSTIC_IDENTITY_PASS,BIP1_BARS_TH_PASS";

		public const string ReopenEventsCsvHeader =
			"event_id,scheduled_reopen_time,primary_bar_time,previous_primary_bar_time,"
			+ "resolved_spot_master_id,resolved_spot_type,resolved_spot_exchange,"
			+ "bars_in_progress,visible_spot_time_at_bip0,visible_spot_close_at_bip0,"
			+ "spot_previous_time,spot_previous_close,"
			+ "spot_current_eq_primary,spot_previous_age_from_primary_minutes,"
			+ "spot_current_time_lt_primary,spot_current_time_eq_primary,spot_current_time_gt_primary,"
			+ "EXPECTED_REOPEN_GATE,RAW_GAP_GATE,TIMELY_BAR_GATE,CLOSE_ANCHOR_GATE,SPECIAL_SESSION_GATE,"
			+ "ROLLOVER_STATE,BASIS_HISTORY_COUNT,POST_ROLL_WARMUP_GATE,"
			+ "spot_before_time,spot_before_close,spot_reopen_time_used,spot_reopen_close,"
			+ "spot_before_age_minutes,spot_reopen_age_minutes,SPOT_FRESHNESS_GATE,"
			+ "spot_closed_move_pct,abs_spot_closed_move_pct,SPOT_MOVE_GATE,"
			+ "basis,basis_mean,basis_std,basis_z,abs_basis_z,BASIS_GATE,"
			+ "source_direction,ALL_PREENTRY_GATES_PASS,FIRST_FAILED_GATE,"
			+ "forensic_flag,known_nt_entry_id";
	}

	public sealed class Spot24x7IdentitySnapshot
	{
		public string RequestedSpotInstrument;
		public string ResolvedFullName;
		public string ResolvedMasterInstrumentName;
		public long ResolvedMasterInstrumentId;
		public string ResolvedInstrumentType;
		public string ResolvedExchange;
		public string InstrumentDefaultTradingHours;
		public string Bip1ActualBarsTradingHours;
		public string RequestedExplicitTradingHours;
		public string BarsPeriod;
		public string MarketDataType;
	}

	public static class Spot24x7IdentityValidator
	{
		public static bool IsIntendedCryptoBtcUsd(Spot24x7IdentitySnapshot s, out string reason)
		{
			if (s == null)
			{
				reason = "IDENTITY_NULL";
				return false;
			}
			if (s.ResolvedMasterInstrumentId != Spot24x7DiagnosticConstants.ExpectedSpotMasterInstrumentId)
			{
				reason = "MASTER_ID_MISMATCH";
				return false;
			}
			if (!string.Equals(s.ResolvedInstrumentType, Spot24x7DiagnosticConstants.ExpectedSpotInstrumentType, StringComparison.OrdinalIgnoreCase))
			{
				reason = "INSTRUMENT_TYPE_MISMATCH";
				return false;
			}
			string ex = s.ResolvedExchange ?? string.Empty;
			if (!string.Equals(ex, Spot24x7DiagnosticConstants.ExpectedSpotExchange, StringComparison.OrdinalIgnoreCase)
				&& !string.Equals(ex, "87", StringComparison.Ordinal))
			{
				reason = "EXCHANGE_MISMATCH";
				return false;
			}
			reason = "OK";
			return true;
		}

		public static bool BarsTradingHoursMatchesExplicit(Spot24x7IdentitySnapshot s, out string reason)
		{
			if (s == null)
			{
				reason = "IDENTITY_NULL";
				return false;
			}
			if (!string.Equals(
				s.Bip1ActualBarsTradingHours,
				Spot24x7DiagnosticConstants.ExplicitSpotTradingHoursTemplate,
				StringComparison.OrdinalIgnoreCase))
			{
				reason = "BIP1_BARS_TH_MISMATCH actual="
					+ (s.Bip1ActualBarsTradingHours ?? string.Empty)
					+ " expected="
					+ Spot24x7DiagnosticConstants.ExplicitSpotTradingHoursTemplate;
				return false;
			}
			reason = "OK";
			return true;
		}

		public static string ToRuntimeIdentityCsvRow(Spot24x7IdentitySnapshot s, bool identityPass, bool barsThPass)
		{
			return string.Join(",", new string[]
			{
				C(s != null ? s.RequestedSpotInstrument : string.Empty),
				C(s != null ? s.ResolvedFullName : string.Empty),
				C(s != null ? s.ResolvedMasterInstrumentName : string.Empty),
				s != null ? s.ResolvedMasterInstrumentId.ToString(CultureInfo.InvariantCulture) : string.Empty,
				C(s != null ? s.ResolvedInstrumentType : string.Empty),
				C(s != null ? s.ResolvedExchange : string.Empty),
				C(s != null ? s.InstrumentDefaultTradingHours : string.Empty),
				C(s != null ? s.Bip1ActualBarsTradingHours : string.Empty),
				C(s != null ? s.RequestedExplicitTradingHours : string.Empty),
				C(s != null ? s.BarsPeriod : string.Empty),
				C(s != null ? s.MarketDataType : string.Empty),
				identityPass ? "YES" : "NO",
				barsThPass ? "YES" : "NO"
			});
		}

		private static string C(string v)
		{
			if (string.IsNullOrEmpty(v))
				return string.Empty;
			if (v.IndexOf(',') >= 0 || v.IndexOf('"') >= 0)
				return "\"" + v.Replace("\"", "\"\"") + "\"";
			return v;
		}
	}

	public sealed class Spot24x7SummaryCounters
	{
		public string RequestedSpotName = "BTCUSD";
		public long ResolvedSpotMasterId;
		public string ResolvedSpotType = string.Empty;
		public string ResolvedSpotExchange = string.Empty;
		public string InstrumentDefaultTradingHours = string.Empty;
		public string Bip1ActualBarsTradingHours = string.Empty;
		public string RequestedExplicitTradingHours = Spot24x7DiagnosticConstants.ExplicitSpotTradingHoursTemplate;
		public bool DiagnosticIdentityPass;
		public bool Bip1BarsTradingHoursPass;
		public bool Bip1CryptoIdentityCertified;

		public int ExpectedReopensSeen;
		public int EligibleReopens;
		public int SpotFreshnessPass;
		public int SpotFreshnessFail;
		public int SpotMovePass;
		public int BasisPass;
		public int PreentryCandidates;
		public HashSet<string> CandidateMonths = new HashSet<string>(StringComparer.Ordinal);

		public int CountVisibleSpotTimeLtPrimary;
		public int CountVisibleSpotTimeEqPrimary;
		public int CountVisibleSpotTimeGtPrimary;

		public int FailReopen;
		public int FailGap;
		public int FailTimely;
		public int FailCloseAnchor;
		public int FailSpecialSession;
		public int FailRollWarmup;
		public int FailSpotFreshness;
		public int FailSpotMove;
		public int FailBasis;

		public Dictionary<string, int> SpotReopenAgeBuckets = new Dictionary<string, int>(StringComparer.Ordinal);

		public void NoteSpotReopenAge(double ageMinutes)
		{
			string bucket;
			if (double.IsNaN(ageMinutes) || double.IsInfinity(ageMinutes))
				bucket = "NA";
			else if (ageMinutes <= 5.0)
				bucket = "0_to_5";
			else if (ageMinutes <= 15.0)
				bucket = "gt5_to_15";
			else if (ageMinutes <= 60.0)
				bucket = "gt15_to_60";
			else if (ageMinutes <= 120.0)
				bucket = "gt60_to_120";
			else if (ageMinutes <= 3000.0)
				bucket = "gt120_to_3000";
			else
				bucket = "gt3000";

			int n;
			if (!SpotReopenAgeBuckets.TryGetValue(bucket, out n))
				n = 0;
			SpotReopenAgeBuckets[bucket] = n + 1;
		}

		public void NoteGateFailure(string firstFailedGate)
		{
			if (string.IsNullOrEmpty(firstFailedGate) || firstFailedGate == "NONE")
				return;
			switch (firstFailedGate)
			{
				case "EXPECTED_REOPEN":
				case "DUPLICATE_REOPEN":
					FailReopen++;
					break;
				case "RAW_GAP":
					FailGap++;
					break;
				case "TIMELY_BAR":
					FailTimely++;
					break;
				case "CLOSE_ANCHOR":
					FailCloseAnchor++;
					break;
				case "SPECIAL_SESSION":
					FailSpecialSession++;
					break;
				case "POST_ROLL_WARMUP":
					FailRollWarmup++;
					break;
				case "SPOT_FRESHNESS":
					FailSpotFreshness++;
					break;
				case "SPOT_MOVE":
					FailSpotMove++;
					break;
				case "BASIS":
					FailBasis++;
					break;
			}
		}

		public string ToJson()
		{
			var sb = new StringBuilder(2048);
			sb.Append("{\n");
			A(sb, "requested_spot_name", Q(RequestedSpotName), true);
			A(sb, "resolved_master_id", ResolvedSpotMasterId.ToString(CultureInfo.InvariantCulture), true);
			A(sb, "resolved_instrument_type", Q(ResolvedSpotType), true);
			A(sb, "resolved_exchange", Q(ResolvedSpotExchange), true);
			A(sb, "INSTRUMENT_DEFAULT_TRADING_HOURS", Q(InstrumentDefaultTradingHours), true);
			A(sb, "BIP1_ACTUAL_BARS_TRADING_HOURS", Q(Bip1ActualBarsTradingHours), true);
			A(sb, "V2_EXPLICIT_SPOT_TRADING_HOURS_TEMPLATE", Q(RequestedExplicitTradingHours), true);
			A(sb, "BIP1_CRYPTO_IDENTITY_CERTIFIED", Bip1CryptoIdentityCertified ? "true" : "false", true);
			A(sb, "BIP1_BARS_TH_PASS", Bip1BarsTradingHoursPass ? "true" : "false", true);
			A(sb, "diagnostic_identity_pass", DiagnosticIdentityPass ? "true" : "false", true);
			A(sb, "EXPECTED_REOPENS_SEEN", ExpectedReopensSeen.ToString(CultureInfo.InvariantCulture), true);
			A(sb, "ELIGIBLE_REOPENS", EligibleReopens.ToString(CultureInfo.InvariantCulture), true);
			A(sb, "SPOT_FRESHNESS_PASS", SpotFreshnessPass.ToString(CultureInfo.InvariantCulture), true);
			A(sb, "SPOT_FRESHNESS_FAIL", SpotFreshnessFail.ToString(CultureInfo.InvariantCulture), true);
			A(sb, "SPOT_MOVE_PASS", SpotMovePass.ToString(CultureInfo.InvariantCulture), true);
			A(sb, "BASIS_PASS", BasisPass.ToString(CultureInfo.InvariantCulture), true);
			A(sb, "NT_NATIVE_PREENTRY_CANDIDATES", PreentryCandidates.ToString(CultureInfo.InvariantCulture), true);
			A(sb, "CANDIDATE_MONTHS", CandidateMonths.Count.ToString(CultureInfo.InvariantCulture), true);
			A(sb, "count_visible_spot_time_lt_primary", CountVisibleSpotTimeLtPrimary.ToString(CultureInfo.InvariantCulture), true);
			A(sb, "count_visible_spot_time_eq_primary", CountVisibleSpotTimeEqPrimary.ToString(CultureInfo.InvariantCulture), true);
			A(sb, "count_visible_spot_time_gt_primary", CountVisibleSpotTimeGtPrimary.ToString(CultureInfo.InvariantCulture), true);
			sb.Append("  \"gate_failure_counts\": {\n");
			A(sb, "reopen", FailReopen.ToString(CultureInfo.InvariantCulture), true, "    ");
			A(sb, "gap", FailGap.ToString(CultureInfo.InvariantCulture), true, "    ");
			A(sb, "timely", FailTimely.ToString(CultureInfo.InvariantCulture), true, "    ");
			A(sb, "close_anchor", FailCloseAnchor.ToString(CultureInfo.InvariantCulture), true, "    ");
			A(sb, "special_session", FailSpecialSession.ToString(CultureInfo.InvariantCulture), true, "    ");
			A(sb, "roll_warmup", FailRollWarmup.ToString(CultureInfo.InvariantCulture), true, "    ");
			A(sb, "spot_freshness", FailSpotFreshness.ToString(CultureInfo.InvariantCulture), true, "    ");
			A(sb, "spot_move", FailSpotMove.ToString(CultureInfo.InvariantCulture), true, "    ");
			A(sb, "basis", FailBasis.ToString(CultureInfo.InvariantCulture), false, "    ");
			sb.Append("\n  },\n");
			sb.Append("  \"spot_reopen_age_minutes_distribution\": {\n");
			List<string> keys = new List<string>(SpotReopenAgeBuckets.Keys);
			keys.Sort(StringComparer.Ordinal);
			for (int i = 0; i < keys.Count; i++)
			{
				A(sb, keys[i], SpotReopenAgeBuckets[keys[i]].ToString(CultureInfo.InvariantCulture), i < keys.Count - 1, "    ");
			}
			if (keys.Count == 0)
				sb.Append("    \"none\": 0\n");
			sb.Append("  },\n");
			A(sb, "ZERO_ORDER_DESIGN", "true", true);
			A(sb, "ORDERS_SUBMITTED_BY_DIAGNOSTIC", "0", true);
			A(sb, "V2_THRESHOLDS_CHANGED", "false", true);
			A(sb, "VALIDATION_DATA_ACCESSED", "false", false);
			sb.Append("\n}\n");
			return sb.ToString();
		}

		private static void A(StringBuilder sb, string key, string value, bool comma, string indent = "  ")
		{
			sb.Append(indent);
			sb.Append('"');
			sb.Append(key);
			sb.Append("\": ");
			sb.Append(value);
			if (comma)
				sb.Append(',');
			sb.Append('\n');
		}

		private static string Q(string s)
		{
			return "\"" + (s ?? string.Empty).Replace("\\", "\\\\").Replace("\"", "\\\"") + "\"";
		}
	}

	public static class Spot24x7TemplateGuard
	{
		public static bool TemplateHasValidationDates(string xml)
		{
			if (string.IsNullOrEmpty(xml))
				return false;
			return xml.IndexOf("2022-01-01", StringComparison.Ordinal) >= 0
				|| xml.IndexOf("2024-09-01", StringComparison.Ordinal) >= 0;
		}

		public static bool TemplateHasOutcomeColumns(string xml)
		{
			if (string.IsNullOrEmpty(xml))
				return false;
			string[] bad = new string[] { "pnl", "MAE", "MFE", "exit_price", "win_rate" };
			for (int i = 0; i < bad.Length; i++)
			{
				if (xml.IndexOf(bad[i], StringComparison.OrdinalIgnoreCase) >= 0)
					return true;
			}
			return false;
		}
	}
}
