# REVIEW PROPOSAL ONLY. Pure decision functions, not a replacement scheduled job.
# No file access, notifications, process control, broker access or top-level invocation.
# Caller supplies only NEW COMPLETE appended rows, a recursively deserialized hashtable,
# a unique poll UTC time, and confirmed expected tags. See watchdog_stateful_proposal.md.
function Update-DraftPositions {
    param(
        [hashtable]$State,
        [object[]]$NewRows,
        [string[]]$ExpectedTags,
        [DateTimeOffset]$NowUtc,
        [string]$CentralDay,
        [bool]$SourceReset = $false,
        [double]$MismatchMinutes = 3,
        [double]$StaleMinutes = 45
    )
    if ($MismatchMinutes -lt 0 -or $StaleMinutes -le 0) { throw 'Invalid thresholds' }
    $nowText = $NowUtc.ToString('o')
    if (-not $State.ContainsKey('day') -or $State.day -ne $CentralDay -or $SourceReset) {
        $State.day = $CentralDay
        $State.positions = @{}
        $State.baseline_at_utc = $nowText
    }
    $diagnostics = @()
    foreach ($row in $NewRows) {
        # Adapter must check CSV column count, POS type, finite numeric quantities,
        # current file/record date, source generation and monotonically increasing byte offset.
        if ($ExpectedTags -notcontains $row.Tag) {
            $diagnostics += "UNKNOWN_TAG|$($row.Tag) requires explicit deployment/account review"
            continue
        }
        $tag = [string]$row.Tag
        if (-not $State.positions.ContainsKey($tag)) {
            $State.positions[$tag] = @{
                cursor = ''; symbol = ''; last_append_utc = ''; last_poll_bad_utc = '';
                first_bad_observed_utc = ''; bad_polls = 0; strategy_qty = 0.0; broker_qty = 0.0
            }
        }
        $p = $State.positions[$tag]
        if ($p.cursor -eq [string]$row.RecordId) { continue } # no new evidence
        $gapTooLong = $p.last_append_utc -and
            (($NowUtc - [DateTimeOffset]::Parse($p.last_append_utc)).TotalMinutes -gt $StaleMinutes)
        if (($p.symbol -and $p.symbol -ne $row.Symbol) -or $gapTooLong) {
            $p.first_bad_observed_utc = ''; $p.last_poll_bad_utc = ''; $p.bad_polls = 0
        }
        $p.cursor = [string]$row.RecordId
        $p.symbol = [string]$row.Symbol
        $p.last_append_utc = $nowText # observation time of a new row, never bar HHMM
        $p.strategy_qty = [double]$row.StrategyQty
        $p.broker_qty = [double]$row.BrokerQty
        if ($p.strategy_qty -eq $p.broker_qty) {
            # Process every appended row in order: a later flat row clears a prior bad row,
            # even when both carry the same chart-bar date/time.
            $p.first_bad_observed_utc = ''; $p.last_poll_bad_utc = ''; $p.bad_polls = 0
        }
        else {
            if (-not $p.first_bad_observed_utc) { $p.first_bad_observed_utc = $nowText }
            if ($p.last_poll_bad_utc -ne $nowText) { $p.bad_polls++ }
            $p.last_poll_bad_utc = $nowText
        }
    }
    $problems = @()
    foreach ($tag in $ExpectedTags) {
        if (-not $State.positions.ContainsKey($tag)) {
            $age = ($NowUtc - [DateTimeOffset]::Parse($State.baseline_at_utc)).TotalMinutes
            if ($age -gt $StaleMinutes) { $problems += "STALE_$tag|No POS observation since watchdog baseline; investigate logging coverage" }
            else { $diagnostics += "UNKNOWN_FRESHNESS_$tag|No POS observation; startup baseline is not a healthy heartbeat" }
            continue
        }
        $p = $State.positions[$tag]
        $age = ($NowUtc - [DateTimeOffset]::Parse($p.last_append_utc)).TotalMinutes
        if ($age -lt 0) { throw 'UTC clock moved backwards; invalidate state and rebaseline' }
        if ($age -gt $StaleMinutes) {
            $problems += "STALE_$tag|No newly appended POS row observed for $([math]::Round($age)) minutes"
            continue # old mismatched data is not fresh repeated confirmation
        }
        if ($p.first_bad_observed_utc -and $p.last_poll_bad_utc -eq $nowText -and $p.bad_polls -ge 2) {
            $span = ($NowUtc - [DateTimeOffset]::Parse($p.first_bad_observed_utc)).TotalMinutes
            if ($span -ge $MismatchMinutes) {
                $problems += "MISMATCH_$tag|Position discrepancy on fresh rows in $($p.bad_polls) polls spanning $([math]::Round($span)) minutes: chart $($p.strategy_qty), broker sample $($p.broker_qty). Verify account/orders; no automated trading action."
            }
        }
    }
    return @{ State = $State; Problems = $problems; Diagnostics = $diagnostics }
}

function Get-DraftRejection {
    param([string]$Line, [DateTimeOffset]$NowUtc)
    $looksBad = $Line -match '(?i)\breject(?:ed|ion)?\b|\binvalid\b|\bdone\s+for\s+day\b'
    if (-not $looksBad) { return @{ Kind = 'ignore' } }
    $orderContext = $Line -match '(?i)\border\b|\b(?:IntID|B_ID|ROB_ID)\s*=|\b(?:Buy|Sell)\s+(?:Stop|Limit)\b'
    $orderFailure = $Line -match '(?i)\breject(?:ed|ion)?\b|\binvalid\s+(?:(?:Market|StopMarket|StopLimit|Limit|Stop)\s+)?order\s+parameters\b|\baccount\s+is\s+done\s+for\s+day\b'
    if (-not ($orderContext -and $orderFailure)) { return @{ Kind = 'diagnostic'; Reason = 'Unclassified failure-like line; not a verified order rejection' } }
    $dateText = ''; $formats = @()
    if ($Line -match '(?<!\d)(\d{2}\.\d{2}\.\d{4}/\d{2}:\d{2}:\d{2}(?:\.\d{1,7})?)') {
        $dateText = $Matches[1]
        $formats = @('dd.MM.yyyy/HH:mm:ss', 'dd.MM.yyyy/HH:mm:ss.FFFFFFF')
    }
    elseif ($Line -match '(?<!\d)(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:\.\d{1,7})?)(?![.\dZ+\-]|\s*[+\-]\d{2}:?\d{2})') {
        $dateText = $Matches[1]
        $formats = @('yyyy-MM-dd HH:mm:ss', 'yyyy-MM-dd HH:mm:ss.FFFFFFF',
                     "yyyy-MM-dd'T'HH:mm:ss", "yyyy-MM-dd'T'HH:mm:ss.FFFFFFF")
    }
    else { return @{ Kind = 'diagnostic'; Reason = 'Order failure has no supported explicit local timestamp' } }
    $localStamp = [datetime]::MinValue
    $valid = [datetime]::TryParseExact($dateText, [string[]]$formats,
        [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::None, [ref]$localStamp)
    if (-not $valid) { return @{ Kind = 'diagnostic'; Reason = 'Invalid timestamp' } }
    $central = [TimeZoneInfo]::FindSystemTimeZoneById('Central Standard Time')
    $today = [TimeZoneInfo]::ConvertTime($NowUtc, $central).Date
    if ($localStamp.Date -ne $today) { return @{ Kind = 'ignore'; Reason = 'Not today in Central time' } }
    # Only verified Central-local log sources may be passed here. No timezone guess from file mtime.
    if ($central.IsAmbiguousTime($localStamp) -or $central.IsInvalidTime($localStamp)) {
        return @{ Kind = 'diagnostic'; Reason = 'DST-ambiguous/invalid local log timestamp' }
    }
    $eventUtc = [TimeZoneInfo]::ConvertTimeToUtc($localStamp, $central)
    if ($eventUtc -gt $NowUtc.UtcDateTime.AddMinutes(2)) {
        return @{ Kind = 'diagnostic'; Reason = 'Future-dated log event; clock/source timezone needs review' }
    }
    return @{ Kind = 'order_rejection_event'; EventUtc = $eventUtc.ToString('o'); Line = $Line }
}

function Select-DraftNewRejections {
    param([hashtable]$State, [object[]]$NewLines, [DateTimeOffset]$NowUtc, [string]$CentralDay)
    if (-not $State.ContainsKey('rejection_day') -or $State.rejection_day -ne $CentralDay) {
        $State.rejection_day = $CentralDay; $State.seen_rejection_events = @{}
    }
    $events = @(); $diagnostics = @()
    foreach ($item in $NewLines) {
        # SourceScope is the verified log-producing installation/profile, shared by duplicate copies.
        $r = Get-DraftRejection -Line $item.Line -NowUtc $NowUtc
        if ($r.Kind -eq 'diagnostic') { $diagnostics += "$($item.SourceScope)|$($r.Reason)"; continue }
        if ($r.Kind -ne 'order_rejection_event') { continue }
        $normalized = ($item.Line.Trim() -replace '\s+', ' ')
        $identity = "$CentralDay|$($item.SourceScope)|$normalized"
        $sha = [Security.Cryptography.SHA256]::Create()
        try { $key = [BitConverter]::ToString($sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($identity))) }
        finally { $sha.Dispose() }
        if (-not $State.seen_rejection_events.ContainsKey($key)) {
            $State.seen_rejection_events[$key] = $true
            $events += @{ Key = $key; EventUtc = $r.EventUtc; Line = $r.Line; SourceScope = $item.SourceScope }
        }
    }
    # Counts are new unique log events, NOT order counts. One order can emit different rejection events.
    return @{ State = $State; Events = $events; Diagnostics = $diagnostics }
}
