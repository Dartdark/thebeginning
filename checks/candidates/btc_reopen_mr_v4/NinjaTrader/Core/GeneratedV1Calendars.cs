// @ElementOfFear
// AUTO-GENERATED from certified CSV artifacts. Do not hand-edit.
// Generator: tools/generate_v1_calendars.py
// ASCII only.

using System;
using System.Collections.Generic;

namespace BtcReopenMr.Core
{
	public static class GeneratedV1Calendars
	{
		public const string ExclusionCsvSha256 = "AD30E6B5187E8245AC95F9CB25E8027C11DB0F6B36990798461FB1457CEB08F8";
		public const string RolloverLedgerCsvSha256 = "F97CAEBB30BABB1185DEB601DE831B6042D9188018D11686DA457E7AC3CA7240";

		// Dates from data/btc_excluded_special_session_dates.csv
		private static readonly DateTime[] SpecialSessionExclusionDates = new DateTime[]
		{
			new DateTime(2018, 7, 4),
			new DateTime(2018, 9, 3),
			new DateTime(2018, 11, 22),
			new DateTime(2018, 11, 23),
			new DateTime(2018, 12, 24),
			new DateTime(2018, 12, 25),
			new DateTime(2019, 1, 1),
			new DateTime(2019, 1, 21),
			new DateTime(2019, 2, 18),
			new DateTime(2019, 4, 19),
			new DateTime(2019, 5, 27),
			new DateTime(2019, 7, 4),
			new DateTime(2019, 9, 2),
			new DateTime(2019, 12, 24),
			new DateTime(2019, 12, 25),
			new DateTime(2020, 1, 1),
			new DateTime(2020, 1, 20),
			new DateTime(2020, 2, 17),
			new DateTime(2020, 4, 10),
			new DateTime(2020, 5, 25),
			new DateTime(2020, 7, 3),
			new DateTime(2020, 9, 7),
			new DateTime(2020, 12, 24),
			new DateTime(2020, 12, 25),
			new DateTime(2021, 1, 1),
			new DateTime(2021, 1, 18),
			new DateTime(2021, 2, 15),
			new DateTime(2021, 4, 2),
			new DateTime(2021, 5, 31),
			new DateTime(2021, 7, 5),
			new DateTime(2021, 9, 6),
			new DateTime(2021, 12, 24),
			new DateTime(2022, 1, 1),
			new DateTime(2022, 1, 17),
			new DateTime(2022, 2, 21),
			new DateTime(2022, 4, 15),
			new DateTime(2022, 5, 30),
			new DateTime(2022, 7, 4),
			new DateTime(2022, 9, 5),
			new DateTime(2022, 12, 24),
			new DateTime(2022, 12, 26),
			new DateTime(2023, 1, 2),
			new DateTime(2023, 1, 16),
			new DateTime(2023, 2, 20),
			new DateTime(2023, 4, 7),
			new DateTime(2023, 5, 29),
			new DateTime(2023, 9, 4),
			new DateTime(2023, 11, 24),
			new DateTime(2023, 12, 24),
			new DateTime(2023, 12, 25),
			new DateTime(2024, 1, 1),
			new DateTime(2024, 3, 29),
			new DateTime(2024, 6, 19),
			new DateTime(2024, 7, 4),
		};

		// Transitions from data/btc_nt_rollover_ledger.csv (ntRolloverDate)
		private static readonly NtRolloverTransition[] RolloverTransitions = new NtRolloverTransition[]
		{
			new NtRolloverTransition(new DateTime(2018, 6, 28), "BTC 06-18", "BTC 07-18"),
			new NtRolloverTransition(new DateTime(2018, 7, 26), "BTC 07-18", "BTC 08-18"),
			new NtRolloverTransition(new DateTime(2018, 8, 30), "BTC 08-18", "BTC 09-18"),
			new NtRolloverTransition(new DateTime(2018, 9, 27), "BTC 09-18", "BTC 10-18"),
			new NtRolloverTransition(new DateTime(2018, 10, 25), "BTC 10-18", "BTC 11-18"),
			new NtRolloverTransition(new DateTime(2018, 11, 29), "BTC 11-18", "BTC 12-18"),
			new NtRolloverTransition(new DateTime(2018, 12, 27), "BTC 12-18", "BTC 01-19"),
			new NtRolloverTransition(new DateTime(2019, 1, 24), "BTC 01-19", "BTC 02-19"),
			new NtRolloverTransition(new DateTime(2019, 2, 21), "BTC 02-19", "BTC 03-19"),
			new NtRolloverTransition(new DateTime(2019, 3, 28), "BTC 03-19", "BTC 04-19"),
			new NtRolloverTransition(new DateTime(2019, 4, 25), "BTC 04-19", "BTC 05-19"),
			new NtRolloverTransition(new DateTime(2019, 5, 30), "BTC 05-19", "BTC 06-19"),
			new NtRolloverTransition(new DateTime(2019, 6, 27), "BTC 06-19", "BTC 07-19"),
			new NtRolloverTransition(new DateTime(2019, 7, 25), "BTC 07-19", "BTC 08-19"),
			new NtRolloverTransition(new DateTime(2019, 8, 29), "BTC 08-19", "BTC 09-19"),
			new NtRolloverTransition(new DateTime(2019, 9, 26), "BTC 09-19", "BTC 10-19"),
			new NtRolloverTransition(new DateTime(2019, 10, 24), "BTC 10-19", "BTC 11-19"),
			new NtRolloverTransition(new DateTime(2019, 11, 28), "BTC 11-19", "BTC 12-19"),
			new NtRolloverTransition(new DateTime(2019, 12, 26), "BTC 12-19", "BTC 01-20"),
			new NtRolloverTransition(new DateTime(2020, 1, 30), "BTC 01-20", "BTC 02-20"),
			new NtRolloverTransition(new DateTime(2020, 2, 27), "BTC 02-20", "BTC 03-20"),
			new NtRolloverTransition(new DateTime(2020, 3, 26), "BTC 03-20", "BTC 04-20"),
			new NtRolloverTransition(new DateTime(2020, 4, 23), "BTC 04-20", "BTC 05-20"),
			new NtRolloverTransition(new DateTime(2020, 5, 28), "BTC 05-20", "BTC 06-20"),
			new NtRolloverTransition(new DateTime(2020, 6, 25), "BTC 06-20", "BTC 07-20"),
			new NtRolloverTransition(new DateTime(2020, 7, 30), "BTC 07-20", "BTC 08-20"),
			new NtRolloverTransition(new DateTime(2020, 8, 27), "BTC 08-20", "BTC 09-20"),
			new NtRolloverTransition(new DateTime(2020, 9, 24), "BTC 09-20", "BTC 10-20"),
			new NtRolloverTransition(new DateTime(2020, 10, 29), "BTC 10-20", "BTC 11-20"),
			new NtRolloverTransition(new DateTime(2020, 11, 25), "BTC 11-20", "BTC 12-20"),
			new NtRolloverTransition(new DateTime(2020, 12, 24), "BTC 12-20", "BTC 01-21"),
			new NtRolloverTransition(new DateTime(2021, 1, 28), "BTC 01-21", "BTC 02-21"),
			new NtRolloverTransition(new DateTime(2021, 2, 25), "BTC 02-21", "BTC 03-21"),
			new NtRolloverTransition(new DateTime(2021, 3, 25), "BTC 03-21", "BTC 04-21"),
			new NtRolloverTransition(new DateTime(2021, 4, 29), "BTC 04-21", "BTC 05-21"),
			new NtRolloverTransition(new DateTime(2021, 5, 27), "BTC 05-21", "BTC 06-21"),
			new NtRolloverTransition(new DateTime(2021, 6, 24), "BTC 06-21", "BTC 07-21"),
			new NtRolloverTransition(new DateTime(2021, 7, 29), "BTC 07-21", "BTC 08-21"),
			new NtRolloverTransition(new DateTime(2021, 8, 26), "BTC 08-21", "BTC 09-21"),
			new NtRolloverTransition(new DateTime(2021, 9, 23), "BTC 09-21", "BTC 10-21"),
			new NtRolloverTransition(new DateTime(2021, 10, 28), "BTC 10-21", "BTC 11-21"),
			new NtRolloverTransition(new DateTime(2021, 11, 25), "BTC 11-21", "BTC 12-21"),
			new NtRolloverTransition(new DateTime(2021, 12, 29), "BTC 12-21", "BTC 01-22"),
			new NtRolloverTransition(new DateTime(2022, 1, 26), "BTC 01-22", "BTC 02-22"),
			new NtRolloverTransition(new DateTime(2022, 2, 23), "BTC 02-22", "BTC 03-22"),
			new NtRolloverTransition(new DateTime(2022, 3, 23), "BTC 03-22", "BTC 04-22"),
			new NtRolloverTransition(new DateTime(2022, 4, 27), "BTC 04-22", "BTC 05-22"),
			new NtRolloverTransition(new DateTime(2022, 5, 25), "BTC 05-22", "BTC 06-22"),
			new NtRolloverTransition(new DateTime(2022, 6, 22), "BTC 06-22", "BTC 07-22"),
			new NtRolloverTransition(new DateTime(2022, 7, 27), "BTC 07-22", "BTC 08-22"),
			new NtRolloverTransition(new DateTime(2022, 8, 24), "BTC 08-22", "BTC 09-22"),
			new NtRolloverTransition(new DateTime(2022, 9, 28), "BTC 09-22", "BTC 10-22"),
			new NtRolloverTransition(new DateTime(2022, 10, 26), "BTC 10-22", "BTC 11-22"),
			new NtRolloverTransition(new DateTime(2022, 11, 24), "BTC 11-22", "BTC 12-22"),
			new NtRolloverTransition(new DateTime(2022, 12, 28), "BTC 12-22", "BTC 01-23"),
			new NtRolloverTransition(new DateTime(2023, 1, 25), "BTC 01-23", "BTC 02-23"),
			new NtRolloverTransition(new DateTime(2023, 2, 23), "BTC 02-23", "BTC 03-23"),
			new NtRolloverTransition(new DateTime(2023, 3, 29), "BTC 03-23", "BTC 04-23"),
			new NtRolloverTransition(new DateTime(2023, 4, 26), "BTC 04-23", "BTC 05-23"),
			new NtRolloverTransition(new DateTime(2023, 5, 25), "BTC 05-23", "BTC 06-23"),
			new NtRolloverTransition(new DateTime(2023, 6, 28), "BTC 06-23", "BTC 07-23"),
			new NtRolloverTransition(new DateTime(2023, 7, 26), "BTC 07-23", "BTC 08-23"),
			new NtRolloverTransition(new DateTime(2023, 8, 24), "BTC 08-23", "BTC 09-23"),
			new NtRolloverTransition(new DateTime(2023, 9, 27), "BTC 09-23", "BTC 10-23"),
			new NtRolloverTransition(new DateTime(2023, 10, 25), "BTC 10-23", "BTC 11-23"),
			new NtRolloverTransition(new DateTime(2023, 11, 24), "BTC 11-23", "BTC 12-23"),
			new NtRolloverTransition(new DateTime(2023, 12, 27), "BTC 12-23", "BTC 01-24"),
			new NtRolloverTransition(new DateTime(2024, 1, 24), "BTC 01-24", "BTC 02-24"),
			new NtRolloverTransition(new DateTime(2024, 2, 23), "BTC 02-24", "BTC 03-24"),
			new NtRolloverTransition(new DateTime(2024, 3, 26), "BTC 03-24", "BTC 04-24"),
			new NtRolloverTransition(new DateTime(2024, 4, 24), "BTC 04-24", "BTC 05-24"),
			new NtRolloverTransition(new DateTime(2024, 5, 24), "BTC 05-24", "BTC 06-24"),
			new NtRolloverTransition(new DateTime(2024, 6, 26), "BTC 06-24", "BTC 07-24"),
			new NtRolloverTransition(new DateTime(2024, 7, 24), "BTC 07-24", "BTC 08-24"),
			new NtRolloverTransition(new DateTime(2024, 8, 23), "BTC 08-24", "BTC 09-24"),
		};

		public static IReadOnlyList<DateTime> GetSpecialSessionExclusionDates()
		{
			return SpecialSessionExclusionDates;
		}

		public static IReadOnlyList<NtRolloverTransition> GetRolloverTransitions()
		{
			return RolloverTransitions;
		}

		public static bool IsSpecialSessionExcluded(DateTime chicagoCalendarDate)
		{
			DateTime d = chicagoCalendarDate.Date;
			for (int i = 0; i < SpecialSessionExclusionDates.Length; i++)
			{
				if (SpecialSessionExclusionDates[i].Date == d)
					return true;
			}
			return false;
		}
	}

	public readonly struct NtRolloverTransition
	{
		public readonly DateTime NtRolloverDate;
		public readonly string OldContract;
		public readonly string NewContract;

		public NtRolloverTransition(DateTime ntRolloverDate, string oldContract, string newContract)
		{
			NtRolloverDate = ntRolloverDate.Date;
			OldContract = oldContract;
			NewContract = newContract;
		}
	}
}
