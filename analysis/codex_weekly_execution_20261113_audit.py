"""Read-only execution audit of the pinned Nov 7--13 Claude source.

No monitoring script is executed. PowerShell parsing only reads files; the
rejection replay executes two extracted decision blocks with a local ntfy stub,
synthetic counters and temporary paths. No strategy backtest, API or live action.
"""
from __future__ import annotations

import argparse
import ast
import datetime as dt
import difflib
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile


PIN = "7b0caeff98ead324ecc492375659b0b89db13d9f"
BASE = "fe35af99"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def powershell(binary, text, folder):
    env = os.environ.copy()
    for name in ("CACHE", "CONFIG", "DATA"):
        env[f"XDG_{name}_HOME"] = str(folder / name.lower())
    script = folder / "synthetic.ps1"
    script.write_text(text)
    run = subprocess.run([str(binary), "-NoLogo", "-NoProfile", "-File", str(script)],
                         cwd=folder, env=env, text=True, capture_output=True)
    if run.returncode:
        raise RuntimeError(f"Synthetic PowerShell failed: {run.stderr}\n{run.stdout}")
    return json.loads(run.stdout)


def rejection_retry(source, binary, folder):
    src = (source / "live/vps/watchdog.ps1").read_text()
    detection = src[src.index('$prev = 0; if ($state["rej_day"]'):src.index("# 4. alert")]
    delivery = src[src.index("$sendFailed = $false"):src.index("if ($sendFailed) { exit 1 }")]
    # Actual source decision blocks; all ntfy requests are intercepted by this
    # function, and all file writes are redirected to this temporary directory.
    toy = r'''
$ErrorActionPreference = "Stop"
$script:attempts = 0
$script:failDelivery = $true
function Invoke-RestMethod {
    [CmdletBinding()]
    param($Method, $Uri, $Body, $Headers, $TimeoutSec)
    $script:attempts++
    if ($script:failDelivery) { throw "synthetic delivery failure" }
    return @{ ok = $true }
}
$Logs = (Get-Location).Path
$StateFile = Join-Path $Logs "toy_state.json"
$Topic = "toy-never-contacted"
$state = @{}
$now = [datetime]"2026-11-13T09:05:00"
$day = "20261113"
$passes = @()
for ($pass = 0; $pass -lt 2; $pass++) {
    $problems = @()
    $rej = 1
    $msg = "13.11.2026/09:02:23 Rejected OrderName=toy"
    __DETECTION__
    $generated = $problems.Count
    __DELIVERY__
    $passes += [pscustomobject]@{
        pass = $pass + 1
        generated_problems = $generated
        total_delivery_attempts = $script:attempts
        send_failed = $sendFailed
        persisted_rejection_count = $state["rej_count"]
        persisted_sent_timestamp = $state["sent_REJECT"]
    }
    # The next scheduler run loads exactly the state saved by the first run.
    $loaded = Get-Content $StateFile -Raw | ConvertFrom-Json
    $state = @{}
    $loaded.PSObject.Properties | ForEach-Object { $state[$_.Name] = $_.Value }
    $script:failDelivery = $false
    $now = $now.AddMinutes(5)
}
$passes | ConvertTo-Json -Depth 8
'''.replace("__DETECTION__", detection).replace("__DELIVERY__", delivery)
    result = powershell(binary, toy, folder)
    assert result[0]["send_failed"] is True
    assert result[0]["persisted_rejection_count"] == 1
    assert result[1]["generated_problems"] == 0
    assert result[1]["total_delivery_attempts"] == 1
    return {"method": "actual extracted source blocks, stubbed network, synthetic counters",
            "passes": result, "confirmed": "failed rejection alert is not retried when the rejection count stays unchanged"}


def parser_checks(source, binary, folder):
    paths = subprocess.check_output(["git", "diff", "--name-only", f"{BASE}..{PIN}", "--", "live/vps"],
                                    cwd=source, text=True).splitlines()
    paths = [str(source / p) for p in paths if p.endswith(".ps1")]
    quoted = ",".join("'" + p.replace("'", "''") + "'" for p in paths)
    ps = '''$results = @()
foreach ($path in @(__PATHS__)) {
    $tokens = $null; $errors = $null
    $null = [System.Management.Automation.Language.Parser]::ParseFile($path, [ref]$tokens, [ref]$errors)
    $results += [pscustomobject]@{ path = $path; errors = @($errors | ForEach-Object { $_.Message }) }
}
$results | ConvertTo-Json -Depth 6
'''.replace("__PATHS__", quoted)
    result = powershell(binary, ps, folder)
    assert all(not r["errors"] for r in result)
    return result


def finish_cache_toy():
    # Directly transcribes ONB 208--223's branch conditions. This verifies the
    # day-key and group override, not PowerLanguage broker/fill semantics.
    cached_key = None
    cached_group = -1
    cached_eq = 0
    rows = []
    for date, time, disk_group, equity in [
        (20261111, 1600, 0, 156100),
        (20261111, 1700, 1, 156100),
        (20261112, 900, 1, 156100),
    ]:
        key = date + 1 if time >= 1600 else date
        read = key != cached_key
        if read and equity > 0:
            cached_eq, cached_key, cached_group = equity, key, disk_group
        finish = cached_key == key and cached_eq >= 156000
        if cached_group == 1:
            finish = cached_key == key
        if cached_group == 0:
            finish = False
        qty = max(1, int(10 * .5 + .5)) if finish else 10
        rows.append(dict(date=date, time=time, disk_group=disk_group, read=read,
                         cached_group=cached_group, finish=finish, contracts=qty))
    assert rows[-1]["contracts"] == 10 and rows[-1]["cached_group"] == 0
    return {"method": "minimal transcription of ONB finish-key/cache/override conditions",
            "writer_event": "16:10 final close push changes EVAL_FULL to EVAL_FINISH",
            "trace": rows, "expected_after_final_group_update": 5,
            "actual_cached_contracts": 10,
            "caveat": "Conditional on a change after the prior 15:15 push and a 16:00 strategy calculation; no actual excess-size trade claimed."}


def gap_controls(source, folder):
    # Execute only this pure reader function from vps_health.py, against toy
    # files. Importing the whole monitoring program or calling check() is avoided.
    mod = ast.parse((source / "analysis/vps_health.py").read_text())
    fn = next(n for n in mod.body if isinstance(n, ast.FunctionDef) and n.name == "new_today")
    ns = {"os": os}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), "new_today-extracted", "exec"), ns)
    toy = folder / "gap" / "live/trades"
    toy.mkdir(parents=True)
    previous = Path.cwd()
    os.chdir(folder / "gap")
    try:
        (toy / "20261112.csv").write_text("SIG,OLD,symbol,version1\nSIG,CHANGED,symbol,version1\n")
        (toy / "20261113.csv").write_text("SIG,OLD,symbol,version1\nSIG,CHANGED,symbol,version2\nSIG,NEW,symbol,version1\n")
        day = dt.date(2026, 11, 13)
        flags = {tag: ns["new_today"](tag, day) for tag in ("OLD", "CHANGED", "NEW")}
        assert flags == {"OLD": False, "CHANGED": True, "NEW": True}
        return {"method": "actual extracted new_today reader against temporary logs", "new_today": flags}
    finally:
        os.chdir(previous)


def watchdog_proposal_text(original):
    """Produce an offline proposal; the pinned source is never written."""
    old = '    $problems += "REJECT_$rej|$($rej - $prev) new rejected order(s). Last: $($msg.Substring(0, [math]::Min(140, $msg.Length))).$hint"'
    new = '''    # The scan cursor records observations; pending delivery has a separate acknowledgement.
    # Coalesce new observations with any failed delivery, preserving their first/latest timestamps.
    if (-not $state["rej_pending_count"]) { $state["rej_pending_first"] = $now.ToString("yyyy-MM-dd HH:mm") }
    $state["rej_pending_count"] = [int]$state["rej_pending_count"] + ($rej - $prev)
    $state["rej_pending_last"] = $now.ToString("yyyy-MM-dd HH:mm")
    $state["rej_pending_detail"] = "Last: $($msg.Substring(0, [math]::Min(140, $msg.Length))).$hint"'''
    assert original.count(old) == 1
    proposed = original.replace(old, new)
    cursor = '$state["rej_day"] = $day; $state["rej_count"] = $rej'
    pending = '''
# Retry pending observations even if today's count is unchanged or the day has rolled.
if ([int]$state["rej_pending_count"] -gt 0) {
    $problems += "REJECT_PENDING|$($state['rej_pending_count']) unacknowledged rejected order(s), first observed $($state['rej_pending_first']), latest $($state['rej_pending_last']). $($state['rej_pending_detail'])"
}'''
    assert proposed.count(cursor) == 1
    proposed = proposed.replace(cursor, cursor + pending)
    mute = '    $problems = @()\n}\n$sendFailed = $false'
    mute_new = '''    # Preserve the no-live-account policy: MUTED observations are logged and acknowledged.
    foreach ($pendingKey in @("rej_pending_count", "rej_pending_first", "rej_pending_last", "rej_pending_detail")) { $state.Remove($pendingKey) }
    $problems = @()
}
$sendFailed = $false'''
    assert proposed.count(mute) == 1
    proposed = proposed.replace(mute, mute_new)
    ack = '            $state[$k] = $now.ToString("o")'
    ack_new = '''            $state[$k] = $now.ToString("o")
            if ($key -eq "REJECT_PENDING") {
                foreach ($pendingKey in @("rej_pending_count", "rej_pending_first", "rej_pending_last", "rej_pending_detail")) { $state.Remove($pendingKey) }
            }'''
    assert proposed.count(ack) == 1
    return proposed.replace(ack, ack_new)


def proposal_replay(text, binary, folder):
    detection = text[text.index('$prev = 0; if ($state["rej_day"]'):text.index("# 4. alert")]
    delivery = text[text.index('$anyLive = $true'):text.index("if ($sendFailed) { exit 1 }")]
    fixtures = [
        {"name": "same_count_retry_then_no_duplicate", "runs": [
            ["2026-11-13T09:05:00", 1, True, True],
            ["2026-11-13T09:10:00", 1, False, True],
            ["2026-11-13T09:15:00", 1, False, True]]},
        {"name": "pending_survives_day_roll_with_zero_new", "runs": [
            ["2026-11-13T09:05:00", 1, True, True],
            ["2026-11-16T08:15:00", 0, False, True],
            ["2026-11-16T08:20:00", 0, False, True]]},
        {"name": "new_rejection_coalesces_while_pending", "runs": [
            ["2026-11-13T09:05:00", 1, True, True],
            ["2026-11-13T09:10:00", 2, True, True],
            ["2026-11-13T09:15:00", 2, False, True],
            ["2026-11-13T09:20:00", 2, False, True]]},
        {"name": "new_next_day_rejection_coalesces_with_old_pending", "runs": [
            ["2026-11-13T09:05:00", 1, True, True],
            ["2026-11-16T08:15:00", 1, False, True],
            ["2026-11-16T08:20:00", 1, False, True]]},
        {"name": "muted_observation_acknowledged_before_account_returns", "runs": [
            ["2026-11-13T09:05:00", 1, False, False],
            ["2026-11-13T09:10:00", 1, False, True],
            ["2026-11-13T09:15:00", 2, False, True]]},
        {"name": "active_failure_then_muted_acknowledgement", "runs": [
            ["2026-11-13T09:05:00", 1, True, True],
            ["2026-11-13T09:10:00", 1, False, False],
            ["2026-11-13T09:15:00", 1, False, True]]},
        {"name": "other_failure_does_not_resurrect_acknowledged_rejection", "runs": [
            ["2026-11-13T09:05:00", 1, False, True, True, True],
            ["2026-11-13T09:10:00", 1, False, True, True, False],
            ["2026-11-13T09:15:00", 1, False, True, True, False]]},
        {"name": "other_success_does_not_acknowledge_failed_rejection", "runs": [
            ["2026-11-13T09:05:00", 1, True, True, True, False],
            ["2026-11-13T09:10:00", 1, False, True, True, False],
            ["2026-11-13T09:15:00", 1, False, True, True, False]]},
    ]
    fixture_json = json.dumps(fixtures).replace("'", "''")
    toy = r'''
$ErrorActionPreference = "Stop"
$fixtures = '__FIXTURES__' | ConvertFrom-Json
$all = @()
$Logs = (Get-Location).Path
$StateFile = Join-Path $Logs "proposal_toy_state.json"
$Topic = "toy-never-contacted"
$script:attempts = 0
$script:failDelivery = $false
$script:failOther = $false
$script:bodies = @()
function Invoke-RestMethod {
    [CmdletBinding()]
    param($Method, $Uri, $Body, $Headers, $TimeoutSec)
    $script:attempts++
    $script:bodies += $Body
    $isOther = $Body -like "*synthetic standing alert*"
    if (($script:failDelivery -and -not $isOther) -or ($script:failOther -and $isOther)) { throw "synthetic delivery failure" }
    return @{ ok = $true }
}
foreach ($fixture in $fixtures) {
    $state = @{}
    $script:attempts = 0
    $script:bodies = @()
    $passes = @()
    $alertPath = Join-Path $Logs "alerts.txt"
    Remove-Item $alertPath -ErrorAction SilentlyContinue
    foreach ($step in $fixture.runs) {
        $now = [datetime]$step[0]; $day = $now.ToString("yyyyMMdd")
        $rej = [int]$step[1]; $script:failDelivery = [bool]$step[2]
        $script:failOther = $step.Count -gt 5 -and [bool]$step[5]
        $status = if ([bool]$step[3]) { "live" } else { "closed" }
        $cfg = @{ accounts = [pscustomobject]@{ toy = [pscustomobject]@{ status = $status } } }
        $msg = "$($now.ToString('dd.MM.yyyy/HH:mm:ss')) Rejected OrderName=toy_$rej"
        $problems = @()
        if ($step.Count -gt 4 -and [bool]$step[4]) { $problems += "OTHER|synthetic standing alert" }
        __DETECTION__
        $generated = $problems.Count
        __DELIVERY__
        $pendingCount = [int]$state["rej_pending_count"]
        $passes += [pscustomobject]@{
            at = $now.ToString("o")
            observed_count = $rej
            live = [bool]$step[3]
            generated_problems = $generated
            total_delivery_attempts = $script:attempts
            send_failed = $sendFailed
            pending_count = $pendingCount
            pending_first = $state["rej_pending_first"]
            pending_last = $state["rej_pending_last"]
            cursor_day = $state["rej_day"]
            cursor_count = $state["rej_count"]
        }
        $loaded = Get-Content $StateFile -Raw | ConvertFrom-Json
        $state = @{}
        $loaded.PSObject.Properties | ForEach-Object { $state[$_.Name] = $_.Value }
    }
    $fixtureLogLines = @(Get-Content $alertPath -ErrorAction SilentlyContinue)
    $all += [pscustomobject]@{ name = $fixture.name; passes = $passes; bodies = $script:bodies; logs = $fixtureLogLines }
}
$all | ConvertTo-Json -Depth 12
'''.replace("__FIXTURES__", fixture_json).replace("__DETECTION__", detection).replace("__DELIVERY__", delivery)
    return powershell(binary, toy, folder)


def proposal_checks(args):
    source = args.source / "live/vps/watchdog.ps1"
    original = source.read_text()
    proposed = watchdog_proposal_text(original)
    safe = Path(__file__).resolve().parents[1]
    patch_path = safe / "agents/codex/proposals/weekly_20261113_watchdog_retry.patch"
    patch = "".join(difflib.unified_diff(original.splitlines(keepends=True), proposed.splitlines(keepends=True),
                                        fromfile="a/live/vps/watchdog.ps1", tofile="b/live/vps/watchdog.ps1"))
    patch_path.parent.mkdir(parents=True, exist_ok=True)
    patch_path.write_text(patch)
    with tempfile.TemporaryDirectory(prefix="codex-weekly-retry-proposal-") as name:
        folder = Path(name)
        # Apply the exact reviewable patch to a temporary copy, never to source.
        target = folder / "live/vps/watchdog.ps1"
        target.parent.mkdir(parents=True)
        target.write_text(original)
        subprocess.run(["git", "apply", str(patch_path)], cwd=folder,
                       check=True, text=True, capture_output=True)
        patched = target.read_text()
        assert patched == proposed
        quoted = str(target).replace("'", "''")
        parse = powershell(args.pwsh, f'''$tokens = $null; $errors = $null
$null = [System.Management.Automation.Language.Parser]::ParseFile('{quoted}', [ref]$tokens, [ref]$errors)
[pscustomobject]@{{ errors = @($errors | ForEach-Object {{ $_.Message }}) }} | ConvertTo-Json -Depth 5
''', folder)
        assert not parse["errors"]
        controls = proposal_replay(original, args.pwsh, folder)
        fixes = proposal_replay(patched, args.pwsh, folder)
        orig = {x["name"]: x for x in controls}
        fixed = {x["name"]: x for x in fixes}
        same = "same_count_retry_then_no_duplicate"
        assert [p["total_delivery_attempts"] for p in orig[same]["passes"]] == [1, 1, 1]
        assert [p["total_delivery_attempts"] for p in fixed[same]["passes"]] == [1, 2, 2]
        assert [p["pending_count"] for p in fixed[same]["passes"]] == [1, 0, 0]
        day = "pending_survives_day_roll_with_zero_new"
        assert [p["total_delivery_attempts"] for p in fixed[day]["passes"]] == [1, 2, 2]
        assert "2026-11-13 09:05" in fixed[day]["bodies"][-1]
        more = "new_rejection_coalesces_while_pending"
        assert [p["pending_count"] for p in fixed[more]["passes"]] == [1, 2, 0, 0]
        assert [p["total_delivery_attempts"] for p in fixed[more]["passes"]] == [1, 2, 3, 3]
        assert "2 unacknowledged" in fixed[more]["bodies"][-1]
        more_day = "new_next_day_rejection_coalesces_with_old_pending"
        assert "2 unacknowledged" in fixed[more_day]["bodies"][-1]
        assert "2026-11-13 09:05" in fixed[more_day]["bodies"][-1]
        assert "2026-11-16 08:15" in fixed[more_day]["bodies"][-1]
        mute = "muted_observation_acknowledged_before_account_returns"
        assert [p["total_delivery_attempts"] for p in fixed[mute]["passes"]] == [0, 0, 1]
        assert fixed[mute]["passes"][0]["pending_count"] == 0
        assert any("MUTED" in line for line in fixed[mute]["logs"])
        then_mute = "active_failure_then_muted_acknowledgement"
        assert [p["total_delivery_attempts"] for p in fixed[then_mute]["passes"]] == [1, 1, 1]
        assert [p["pending_count"] for p in fixed[then_mute]["passes"]] == [1, 0, 0]
        other_fail = "other_failure_does_not_resurrect_acknowledged_rejection"
        assert [p["pending_count"] for p in fixed[other_fail]["passes"]] == [0, 0, 0]
        assert sum("unacknowledged rejected" in body for body in fixed[other_fail]["bodies"]) == 1
        other_ok = "other_success_does_not_acknowledge_failed_rejection"
        assert [p["pending_count"] for p in fixed[other_ok]["passes"]] == [1, 0, 0]
        assert sum("unacknowledged rejected" in body for body in fixed[other_ok]["bodies"]) == 2
        result = {"source_head": PIN, "source_sha256": digest(source),
                  "proposal": str(patch_path), "proposal_sha256": digest(patch_path),
                  "patched_sha256": hashlib.sha256(patched.encode()).hexdigest(),
                  "exact_patch_applied_to_temporary_copy": True, "full_patched_powershell_parse": parse,
                  "all_assertions_passed": True, "original_replays": controls, "patched_replays": fixes,
                  "boundaries": "Offline proposal only. Extracted actual blocks, synthetic state, stubbed HTTP; no real network, source, live/VPS/account/notification change.",
                  "limitations": "PowerShell 7.6.9 parser/runtime; Windows PowerShell 5.1 and live task installation not exercised. Existing state-file write failure and underlying rejection scan/count semantics are unchanged."}
    output = safe / "analysis/outputs/codex_weekly_cross_review_20261113/execution_watchdog_proposal_proof.json"
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"proposal": str(patch_path), "proof": str(output), "fixtures": len(fixes), "all_assertions_passed": True}))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, default=Path("/workspace/thebeginning_weekly_source_20261113"))
    ap.add_argument("--output", type=Path, default=Path("/workspace/thebeginning_papers_20261110/analysis/outputs/codex_weekly_cross_review_20261113/execution_audit.json"))
    ap.add_argument("--pwsh", type=Path, default=Path("/workspace/review_tools/pwsh/pwsh"))
    ap.add_argument("--proposal", action="store_true", help="Build and verify an offline watchdog patch in the safe worktree")
    args = ap.parse_args()
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=args.source, text=True).strip()
    assert head == PIN, (head, PIN)
    if args.proposal:
        proposal_checks(args)
        return
    relevant = ["live/vps/watchdog.ps1", "live/vps/push_trade_logs.ps1", "live/vps/cushion_peak.ps1",
                "apex_strategies/NQ_Overnight_Bias_ADX30.txt", "apex_strategies/Twin_Continuation_150K.txt",
                "funded_strategies/NQ_Late_Day_Flow.txt", "analysis/vps_health.py", "live/expected_setup.json"]
    with tempfile.TemporaryDirectory(prefix="codex-weekly-execution-") as name:
        folder = Path(name)
        out = {"source_head": head, "base": BASE,
               "source_sha256": {p: digest(args.source / p) for p in relevant},
               "powershell_parse_checks": parser_checks(args.source, args.pwsh, folder),
               "rejection_retry": rejection_retry(args.source, args.pwsh, folder),
               "finish_cache": finish_cache_toy(),
               "gap_controls": gap_controls(args.source, folder),
               "boundaries": "No live/VPS/account/API/notification action; no real monitoring script run; no strategy backtest."}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"output": str(args.output), "parse_checked": len(out["powershell_parse_checks"]),
                      "rejection_retry_confirmed": True, "finish_cache_confirmed": True}))


if __name__ == "__main__":
    main()
