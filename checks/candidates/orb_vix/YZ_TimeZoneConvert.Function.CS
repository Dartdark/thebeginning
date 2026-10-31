using System;

namespace PowerLanguage.Function
{
    // =====================================================================================
    // YZ_TimeZoneConvert  —  reusable timezone converter (FunctionSeries<DateTime>)
    // -------------------------------------------------------------------------------------
    // Converts a DateTime from one Windows timezone to another via System.TimeZoneInfo, which
    // handles DST (EST/EDT, CST/CDT, ...) automatically. Purpose: let ANY study anchor its
    // session logic to a fixed exchange clock (e.g. 09:30 US Eastern) no matter what timezone
    // the chart actually displays. MultiCharts exposes no UTC bar-time accessor, so this routes
    // chart-zone -> UTC -> target-zone internally.
    //
    // Use it from a study (instantiate once in Create(): m_fn = new YZ_TimeZoneConvert(this);):
    //   * Method (any DateTime):  DateTime et = m_fn.ConvertTime(Bars.Time[0]);
    //   * Indexer (current bar):  set the id properties, then read m_fn[0].
    //
    // TimeZoneIds are Windows ids, e.g. "Central Standard Time" (CME/CT), "Eastern Standard
    // Time" (NY/ET), "Israel Standard Time" (Jerusalem), "UTC". CT<->ET is always 1h (both
    // observe US DST together); cross-region pairs (e.g. Israel<->ET) vary by a week or two
    // each spring/autumn because the regions switch DST on different dates — handled per-date.
    // DST spring-forward gap: a wall-clock time the source zone skips is nudged out of the gap
    // so the convert never throws (see ConvertTime) — relevant for non-US chart zones.
    // =====================================================================================
    public class YZ_TimeZoneConvert : FunctionSeries<DateTime>
    {
        public string SourceTimeZoneId { get; set; } // zone the input DateTime is expressed in
        public string TargetTimeZoneId { get; set; } // zone to convert into

        private TimeZoneInfo m_src;
        private TimeZoneInfo m_dst;
        private string m_srcResolved;
        private string m_dstResolved;

        public YZ_TimeZoneConvert(CStudyControl ctx) : base(ctx) { SetDefaults(); }
        public YZ_TimeZoneConvert(CStudyControl ctx, int data_stream) : base(ctx, data_stream) { SetDefaults(); }

        private void SetDefaults() {
            SourceTimeZoneId = "Central Standard Time"; // CME exchange time
            TargetTimeZoneId = "Eastern Standard Time"; // US cash-session anchor
        }

        // FunctionSeries indexer entry point: this bar's time (Bars.Time[0]) in the target zone.
        protected override DateTime CalcBar() {
            return ConvertTime(Bars.Time[0]);
        }

        // Convert an arbitrary time from the source zone to the target zone (DST-correct).
        public DateTime ConvertTime(DateTime time) {
            EnsureZones();
            DateTime unspecified = DateTime.SpecifyKind(time, DateTimeKind.Unspecified);
            // Spring-forward gap: a wall-clock time the source zone skips for DST does not
            // exist there, and ConvertTimeToUtc would throw ArgumentException ("invalid time").
            // Nudge it out of the gap by the DST delta (1h in every real zone) so the conversion
            // is well-defined. Only matters for the handful of overnight bars on the source
            // zone's DST change day — far from any RTH session anchor. (Ambiguous fall-back
            // times do NOT throw: ConvertTimeToUtc resolves them to standard time.)
            if (m_src.IsInvalidTime(unspecified))
                unspecified = unspecified.AddHours(1);
            DateTime utc = TimeZoneInfo.ConvertTimeToUtc(unspecified, m_src);
            return TimeZoneInfo.ConvertTimeFromUtc(utc, m_dst);
        }

        // Resolve & cache the TimeZoneInfo objects; re-resolve only when an id actually changes.
        private void EnsureZones() {
            if (m_src == null || SourceTimeZoneId != m_srcResolved) {
                m_src = FindZone(SourceTimeZoneId);
                m_srcResolved = SourceTimeZoneId;
            }
            if (m_dst == null || TargetTimeZoneId != m_dstResolved) {
                m_dst = FindZone(TargetTimeZoneId);
                m_dstResolved = TargetTimeZoneId;
            }
        }

        private static TimeZoneInfo FindZone(string id) {
            try {
                return TimeZoneInfo.FindSystemTimeZoneById(id);
            } catch (Exception ex) {
                throw new Exception(
                    "YZ_TimeZoneConvert: '" + id + "' is not a valid Windows timezone id " +
                    "(use e.g. 'Central Standard Time', 'Eastern Standard Time', 'UTC').", ex);
            }
        }
    }
}
