"""Offline bug reproductions against pinned Claude source; no live state or notifications.

Reads Git objects, writes temporary fixtures, mocks every Git/HTTP/Windows operation,
and exports a review patch. It never applies that patch to the project/live files.
Run: python analysis/codex_alert_review_20261110.py [--pwsh /path/to/pwsh]
"""
from pathlib import Path
import argparse
import contextlib
import copy
import csv
import datetime as dt
import difflib
import hashlib
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import tempfile
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
PIN = "25ca95560627f94dc1d9850b823cb5bfe2f9dbc2"
OUT = ROOT / "analysis/outputs/codex_alert_review_20261110"
CODE = ROOT / "agents/codex/code/alert_review_20261110"
PATHS = ["analysis/send_alert.py", "analysis/live_guard.py", "analysis/premarket_check.py",
         "analysis/vps_health.py", "live/vps/claude_alert_relay.ps1", "live/vps/watchdog.ps1",
         "live/expected_setup.json"]


def replace_once(text, old, new):
    assert text.count(old) == 1, old[:100]
    return text.replace(old, new, 1)


def candidates(raw):
    result = dict(raw)
    p = "analysis/send_alert.py"
    s = raw[p].replace("import sys, subprocess, datetime as dt", "import sys, subprocess, datetime as dt\nfrom pathlib import Path\nfrom zoneinfo import ZoneInfo\nROOT = Path(__file__).resolve().parents[1]")
    start = s.index("def send(text):")
    end = s.index('\n\nif __name__', start)
    s = s[:start] + '''def send(text):
    text = " ".join(text.split())[:300]
    if not text:
        raise ValueError("An alert message is required")
    now = dt.datetime.now(ZoneInfo("America/Chicago")).strftime("%Y-%m-%d %H:%M")
    def run(*args):
        return subprocess.run(args, check=True, capture_output=True, text=True, cwd=ROOT)
    head = run("git", "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if not head.startswith("claude/"):
        raise RuntimeError("Alert publisher must run on the designated Claude branch")
    if run("git", "diff", "--cached", "--name-only").stdout.strip():
        raise RuntimeError("Finish the staged commit before publishing an alert")
    run("git", "pull", "-q", "--no-rebase", "origin", BRANCHES[0])
    with (ROOT / "live/claude_alerts.txt").open("a", encoding="utf-8") as f:
        f.write(f"{now} CT | {text}\\n")
    run("git", "add", "live/claude_alerts.txt")
    run("git", "commit", "-q", "-m", f"alert: {text[:60]}", "--only", "--", "live/claude_alerts.txt")
    for branch in BRANCHES + ([head] if head not in BRANCHES else []):
        run("git", "push", "-q", "origin", f"HEAD:{branch}")
    print("queued on GitHub for the phone relay (delivery not confirmed):", text)
''' + s[end:]
    s = s.replace('send(" ".join(sys.argv[1:]) or "test alert from Claude")', 'send(" ".join(sys.argv[1:]))')
    result[p] = s

    p = "analysis/live_guard.py"
    s = raw[p].replace('d < v["started"]', 'd < str(v["started"]).replace("-", "")')
    s = replace_once(s, '        floor = min(peak - v["trail"], v["lock"])', '''        floor = peak - v["trail"]
        phase = v.get("phase") or ("funded" if v["id"].startswith("PA-") else "evaluation")
        if phase == "funded":
            floor = min(floor, v.get("lock") or v["start"] + 100)
        elif phase != "evaluation":
            raise ValueError(f"Unknown account phase for {name}: {phase}")''')
    s = replace_once(s, 'max_stop=v["max_stop"]', 'max_stop=v.get("max_stop")')
    result[p] = s

    p = "analysis/premarket_check.py"
    s = raw[p]
    needle = '        if want[tag] and r.side != want[tag][0]: out.append(f"{tag}: monitor account {r.side}, expected {want[tag][0]}.")'
    s = replace_once(s, needle, needle + '''
        expected = cfg["accounts"].get(cfg["charts"][tag].get("account", ""), {}).get("id")
        route = "" if pd.isna(r.exit_date) else str(r.exit_date).strip()
        if expected and route != expected:
            out.append(f"{tag}: routed account {route or 'UNKNOWN'}, expected {expected} (Auto Trading gear).")''')
    s = replace_once(s, 'if sig.empty and has_sig(tag):', 'if sig.empty:')
    result[p] = s

    p = "analysis/vps_health.py"
    result[p] = raw[p].replace('Alarm sent during the day:', 'Watchdog log (delivery status is in the entry):').replace('            if tag not in ever: continue\n', '')

    p = "live/vps/claude_alert_relay.ps1"
    s = raw[p]
    s = replace_once(s, '$lines = @(git show "origin/${branch}:live/claude_alerts.txt" 2>$null)', '''if (-not $fetchOk) { Say "alert fetch FAILED; cursor unchanged"; exit 1 }
$lines = @(git show "origin/${branch}:live/claude_alerts.txt" 2>$null)
if ($LASTEXITCODE -ne 0) { Say "alert read FAILED; cursor unchanged"; exit 1 }''')
    s = replace_once(s, 'if (-not (Test-Path $State)) { Set-Content $State $lines.Count; Say "first run: recorded $($lines.Count) existing lines"; exit 0 }', 'if (-not (Test-Path $State)) { Set-Content $State 0 -ErrorAction Stop; Say "first run: replay from first unacknowledged line" }')
    s = replace_once(s, '-ErrorAction Stop | Out-Null\n        Say "sent:', '-TimeoutSec 15 -ErrorAction Stop | Out-Null\n        Set-Content $State ($i + 1) -ErrorAction Stop\n        Say "accepted by ntfy:')
    s = replace_once(s, '} catch { Say "ntfy FAILED: $($_.Exception.Message)" }', '} catch { Say "delivery/checkpoint FAILED; pending line $i retained: $($_.Exception.Message)"; exit 1 }')
    s = replace_once(s, 'Set-Content $State $lines.Count\nexit 0', 'exit 0')
    result[p] = s

    p = "live/vps/watchdog.ps1"
    s = raw[p]
    old = 'if ($cfg) { $live = @($cfg.charts.PSObject.Properties.Name); foreach ($t in @($tags.Keys)) { if ($live -notcontains $t) { $tags.Remove($t) } } }'
    new = '''if ($cfg) {
    $live = @($cfg.charts.PSObject.Properties | Where-Object { $cfg.accounts.($_.Value.account).status -eq "live" } | ForEach-Object { $_.Name })
    $tags = @{}; foreach ($t in $live) { $tags[$t] = $true }
} else { $problems += "CONFIG|Cannot read expected_setup.json: chart coverage is UNKNOWN" }'''
    s = replace_once(s, old, new)
    s = replace_once(s, '    foreach ($t in $acct.Keys) {\n        $c = $acct[$t]', '    foreach ($t in $acct.Keys) {\n        if ($cfg -and $live -notcontains $t) { continue }\n        $c = $acct[$t]')
    needle = '# 2e. order routing'
    start = s.index(needle)
    s = s[:start] + '''# Unknown tags on a live account are a configuration fault, not retired-chart noise.
if ($cfg) {
    $liveIds = @($cfg.accounts.PSObject.Properties | Where-Object { $_.Value.status -eq "live" } | ForEach-Object { $_.Value.id })
    foreach ($t in $acct.Keys) {
        if ($t -ne "SCAN" -and $live -notcontains $t -and $liveIds -contains $acct[$t][3]) {
            $problems += "UNEXPECTED_$t|Chart tag $t is on a live account but absent from expected_setup.json; reconcile Tag and HeartbeatTag."
        }
    }
}

''' + s[start:]
    s = replace_once(s, 'Where-Object { $_.BaseName -ge $v.started }', 'Where-Object { $_.BaseName -ge ($v.started -replace "-", "") }')
    s = replace_once(s, '        $floor = [math]::Min($peak - [double]$v.trail, [double]$v.lock); $room = $eqNow - $floor; $n = $ap.Name', '''        $floor = $peak - [double]$v.trail
        $phase = $v.phase; if (-not $phase) { $phase = if ($v.id -like "PA-*") { "funded" } else { "evaluation" } }
        if ($phase -eq "funded") {
            $lock = if ($null -ne $v.lock) { [double]$v.lock } else { [double]$v.start + 100 }
            $floor = [math]::Min($floor, $lock)
        } elseif ($phase -ne "evaluation") { $problems += "CONFIG|Unknown account phase for $($ap.Name)"; continue }
        if ($null -eq $v.max_stop) { $problems += "CONFIG|Missing max_stop for $($ap.Name); thin-cushion threshold is UNKNOWN" }
        $room = $eqNow - $floor; $n = $ap.Name''')
    s = s.replace('0.5 * [double]$v.max_stop', '[double]$v.max_stop')
    s = s.replace('elseif ($room -lt [double]$v.max_stop)', 'elseif ($room -le [double]$v.max_stop)')
    s = s.replace('half a stop is', 'one planned stop before costs/slippage is')
    needle = '    Get-Content $_.FullName | Where-Object { $_ -like "SIG,*" } | ForEach-Object { $sigTags[$_.Split(",")[1]] = $true } }'
    s = replace_once(s, needle, needle + '\nif ($cfg) { $sigTags = @{}; foreach ($t in $live) { $sigTags[$t] = $true } }')
    s = replace_once(s, 'foreach ($p in $problems) {\n    $key, $text', '$sendFailed = $false\nforeach ($p in $problems) {\n    $key, $text')
    old = '''        try { Invoke-RestMethod -Method Post -Uri "https://ntfy.sh/$Topic" -Body "VPS: $text" -Headers @{ Title = "Trading alarm"; Priority = "high" } | Out-Null } catch {}
        "$($now.ToString('yyyy-MM-dd HH:mm')) ALERT $text" | Add-Content "$Logs\\alerts.txt"
        $state[$k] = $now.ToString("o")'''
    new = '''        try {
            Invoke-RestMethod -Method Post -Uri "https://ntfy.sh/$Topic" -Body "VPS: $text" -Headers @{ Title = "Trading alarm"; Priority = "high" } -TimeoutSec 15 -ErrorAction Stop | Out-Null
            "$($now.ToString('yyyy-MM-dd HH:mm')) ALERT $text" | Add-Content "$Logs\\alerts.txt"
            $state[$k] = $now.ToString("o")
        } catch {
            "$($now.ToString('yyyy-MM-dd HH:mm')) SEND_FAILED $text" | Add-Content "$Logs\\alerts.txt"
            $sendFailed = $true
        }'''
    s = replace_once(s, old, new)
    s += '\nif ($sendFailed) { exit 1 }\n'
    result[p] = s

    p = "live/expected_setup.json"
    s = raw[p]
    # The new live account already has phase=evaluation, so a fabricated funded lock is not added.
    s = replace_once(s, '   "trail": 4000,\n   "target": 159050,', '   "trail": 4000,\n   "max_stop": 2750,\n   "target": 159050,')
    result[p] = s
    return result


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@contextlib.contextmanager
def cwd(path):
    old = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old)


def write_rows(root, day, rows):
    p = root / f"live/trades/{day}.csv"
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w") as f:
        csv.writer(f).writerows(rows)


def acct(tag, equity=150000, time=1000, auto="1", account="APEX-DEMO-05", route=None):
    return ["ACCT", tag, "@MNQ", account, auto, "0", str(equity), "0", route or account, "", "", "", "20261110", str(time)]


def event(kind, tag, time=1000):
    return [kind, tag, "@MNQ", "", "0", "", "", "", "", "", "", "0", "20261110", str(time)]


def python_checks(root, label, production_cfg):
    result = {}
    cfg = copy.deepcopy(production_cfg)
    cfg["accounts"]["#5"]["id"] = "APEX-DEMO-05"
    (root / "live/expected_setup.json").write_text(json.dumps(cfg))
    with cwd(root):
        guard = load_module(root / "analysis/live_guard.py", f"guard_{label}")
        write_rows(root, "20261110", [acct("VB150-5")])
        try:
            got = guard.floors("20261110", cfg)["#5"]
            result["new_account_floor"] = dict(ok=got["floor"] == 146000, floor=got["floor"])
        except Exception as exc:
            result["new_account_floor"] = dict(ok=False, error=f"{type(exc).__name__}: {exc}")
        cfg["accounts"]["#5"].update(lock=150100, max_stop=2750)
        cfg["accounts"]["#5"]["started"] = "2026-11-09"
        prior = acct("VB150-5", 156000, time=1600); prior[12] = "20261109"
        write_rows(root, "20261109", [prior])
        got = guard.floors("20261110", cfg)["#5"]
        result["evaluation_floor_keeps_trailing"] = dict(ok=got["floor"] == 152000, floor=got["floor"])
        cfg["accounts"]["#5"]["phase"] = "funded"
        got = guard.floors("20261110", cfg)["#5"]
        result["funded_floor_still_locks"] = dict(ok=got["floor"] == 150100, floor=got["floor"])
        cfg["accounts"]["#5"]["phase"] = "evaluation"
        (root / "live/trades/20261109.csv").unlink()

        cfg["charts"] = {"VB150-5": cfg["charts"]["VB150-5"]}
        (root / "live/expected_setup.json").write_text(json.dumps(cfg))
        pre = load_module(root / "analysis/premarket_check.py", f"premarket_{label}")
        health = load_module(root / "analysis/vps_health.py", f"health_{label}")
        write_rows(root, "20261110", [acct("VB150-5", route="APEX-OTHER-06"), event("POS", "VB150-5"), event("SIG", "VB150-5")])
        with patch.dict(sys.modules, {"live_guard": guard}):
            messages = pre.check(dt.date(2026, 11, 10))
        result["premarket_detects_wrong_route"] = dict(ok=any("routed account" in m for m in messages))
        write_rows(root, "20261110", [acct("VB150-5"), event("POS", "VB150-5")])
        with patch.dict(sys.modules, {"live_guard": guard}):
            messages = pre.check(dt.date(2026, 11, 10))
        result["premarket_requires_new_strategy_heartbeat"] = dict(ok=any("STRATEGY wrote no heartbeat" in m for m in messages))
        import pandas as pd
        frame = pd.read_csv(root / "live/trades/20261110.csv", names=health.COLS, header=None, dtype=str)
        messages = health.monitor_check(frame, dt.date(2026, 11, 10), cfg)
        result["health_requires_new_strategy_heartbeat"] = dict(ok=any("no heartbeat from the strategy" in m for m in messages))

        sender = load_module(root / "analysis/send_alert.py", f"sender_{label}")
        alert_path = root / "live/claude_alerts.txt"
        for fail_op in ["pull", "commit", "push"]:
            alert_path.write_text("")
            calls = []
            def fake(*args, **kwargs):
                cmd = list(args[0]); calls.append(cmd)
                code = int(fail_op in cmd)
                if code and kwargs.get("check"):
                    raise subprocess.CalledProcessError(code, cmd, stderr="invented failure")
                stdout = "claude/review-fixture\n" if "rev-parse" in cmd else ""
                return SimpleNamespace(returncode=code, stdout=stdout, stderr="invented failure" if code else "")
            output = io.StringIO(); raised = None
            with patch.object(sender.subprocess, "run", fake), contextlib.redirect_stdout(output):
                try:
                    sender.send("invented isolated alert")
                except Exception as exc:
                    raised = type(exc).__name__
            result[f"publisher_{fail_op}_failure"] = dict(ok=bool(raised) and "queued" not in output.getvalue(),
                                                          exception=raised, falsely_queued="queued" in output.getvalue())
            if fail_op == "pull":
                result["failed_pull_does_not_append"] = dict(ok=not alert_path.read_text())
        original_datetime = dt.datetime
        base = original_datetime(2026, 11, 10, 21, 0, tzinfo=dt.timezone.utc)
        class FrozenDatetime(original_datetime):
            @classmethod
            def now(cls, tz=None):
                return base.astimezone(tz) if tz is not None else base.replace(tzinfo=None)
        def successful_git(*args, **kwargs):
            return SimpleNamespace(returncode=0, stdout="claude/review-fixture\n" if "rev-parse" in args[0] else "", stderr="")
        alert_path.write_text("")
        with patch.object(sender.subprocess, "run", successful_git), patch.object(sender.dt, "datetime", FrozenDatetime), contextlib.redirect_stdout(io.StringIO()):
            sender.send("invented winter timestamp")
        result["publisher_uses_winter_Chicago_time"] = dict(ok=alert_path.read_text().startswith("2026-11-10 15:00 CT |"), recorded_hour=alert_path.read_text()[11:16])
    return result


PS_WRAPPER = r'''
param([string]$Source,[string]$Sandbox,[string]$Case)
$ErrorActionPreference = "Stop"
New-PSDrive -Name C -PSProvider FileSystem -Root $Sandbox | Out-Null
$env:LOCALAPPDATA = "C:\Unused"; $env:APPDATA = "C:\Unused"
$global:attempts = 0
function Get-Date { param([string]$Format) $d = [datetime]"2026-11-10T10:00:00"; if ($Format) { $d.ToString($Format) } else { $d } }
function Get-Process { [pscustomobject]@{ProcessName="MultiCharts64";Id=1} }
function Get-NetTCPConnection { param($State) [pscustomobject]@{OwningProcess=1;RemoteAddress="192.0.2.1"} }
function Start-Sleep { param($Seconds,$Milliseconds) }
function powershell { $global:LASTEXITCODE=0 }
function git {
    if ($args[0] -eq "fetch") { $global:LASTEXITCODE=0; return }
    if ($args[0] -eq "ls-tree") { $global:LASTEXITCODE=0; return "live/claude_alerts.txt","live/expected_setup.json" }
    if ($args[0] -eq "show") { $global:LASTEXITCODE=0; return "alert one","alert two","alert three" }
    throw "Unexpected mock Git command"
}
function Invoke-RestMethod {
    [CmdletBinding()]param($Method,$Uri,$Body,$Headers,[int]$TimeoutSec)
    $global:attempts++
    if ($Case -in "relay_fail","relay_retry" -and $global:attempts -eq 2) { throw "invented notification outage" }
    if ($Case -eq "watchdog_fail") { throw "invented notification outage" }
    [pscustomobject]@{accepted=$true}
}
if ($Case -like "relay_*") {
    & $Source
    $code=$LASTEXITCODE
    $cursor=[int](Get-Content "C:\TradingLogs\claude_alerts_sent.txt" -Raw)
    $firstAttempts=$global:attempts
    if ($Case -eq "relay_retry") {
        $Case="relay_ok"; $global:attempts=0
        & $Source
        $code=$LASTEXITCODE
        $retryCursor=[int](Get-Content "C:\TradingLogs\claude_alerts_sent.txt" -Raw)
        [ordered]@{first_attempts=$firstAttempts;first_cursor=$cursor;retry_attempts=$global:attempts;cursor=$retryCursor;exit=$code}|ConvertTo-Json -Compress
    } else { [ordered]@{attempts=$global:attempts;cursor=$cursor;exit=$code}|ConvertTo-Json -Compress }
} else {
    $global:LASTEXITCODE=0
    . $Source
    $code=$LASTEXITCODE
    $sent = @($state.Keys | Where-Object { $_ -like "sent_*" })
    [ordered]@{attempts=$global:attempts;floor=$floor;sent=$sent;exit=$code;problems=@($problems)}|ConvertTo-Json -Compress -Depth 4
}
'''


def powershell_checks(root, pwsh, label, cfg):
    results = {}
    wrapper = root / "mock_windows.ps1"
    wrapper.write_text(PS_WRAPPER)
    for case in ["relay_fail", "relay_retry", "relay_bootstrap", "watchdog_floor", "watchdog_thin", "watchdog_missing", "watchdog_retired", "watchdog_fail"]:
        with tempfile.TemporaryDirectory(prefix="codex_notification_fixture_") as folder:
            sandbox = Path(folder)
            (sandbox / "TradingLogs").mkdir()
            repo = sandbox / "TradingRepo/live"; repo.mkdir(parents=True)
            fixture = copy.deepcopy(cfg)
            fixture["accounts"]["#5"]["id"] = "APEX-DEMO-05"
            fixture["charts"] = {"VB150-5": fixture["charts"]["VB150-5"]}
            if case == "watchdog_thin": fixture["accounts"]["#5"].update(lock=1e12, max_stop=2750)
            (repo / "expected_setup.json").write_text(json.dumps(fixture))
            logs = sandbox / "TradingLogs"
            if case in ["relay_fail", "relay_retry"]: (logs / "claude_alerts_sent.txt").write_text("0")
            if case.startswith("watchdog"):
                eq = 145900 if case == "watchdog_floor" else (148000 if case == "watchdog_thin" else 150000)
                rows = [] if case == "watchdog_missing" else [acct("VB150-5", eq, auto="0" if case == "watchdog_fail" else "1"), event("POS", "VB150-5"), event("SIG", "VB150-5")]
                if case == "watchdog_retired": rows += [acct("OLD", auto="0", account="APEX-RETIRED-02"), event("SIG", "OLD", time=800)]
                with (logs / "20261110.csv").open("w") as f: csv.writer(f).writerows(rows)
            source = root / ("live/vps/claude_alert_relay.ps1" if case.startswith("relay") else "live/vps/watchdog.ps1")
            env = dict(os.environ, XDG_CACHE_HOME="/workspace/review_tools/cache", XDG_CONFIG_HOME="/workspace/review_tools/config", XDG_DATA_HOME="/workspace/review_tools/data", POWERSHELL_TELEMETRY_OPTOUT="1")
            r = subprocess.run([str(pwsh), "-NoProfile", "-File", str(wrapper), "-Source", str(source), "-Sandbox", str(sandbox), "-Case", case], capture_output=True, text=True, env=env, timeout=20)
            if case == "watchdog_fail":
                state_path = logs / "watchdog_state.json"
                state = json.loads(state_path.read_text()) if state_path.exists() else {}
                sent = sorted(k for k in state if k.startswith("sent_"))
                script_exit = json.loads(r.stdout.strip().splitlines()[-1])["exit"] if r.returncode == 0 else r.returncode
                result = dict(ok=not sent and script_exit != 0, sent=sent, exit=script_exit)
            else:
                assert r.returncode == 0, (label, case, r.stdout, r.stderr)
                result = json.loads(r.stdout.strip().splitlines()[-1])
                if case == "relay_fail": result["ok"] = result["cursor"] == 1 and result["exit"] != 0
                if case == "relay_retry": result["ok"] = result["first_cursor"] == 1 and result["retry_attempts"] == 2 and result["cursor"] == 3 and result["exit"] == 0
                if case == "relay_bootstrap": result["ok"] = result["attempts"] == 3 and result["cursor"] == 3
                if case == "watchdog_floor": result["ok"] = result["floor"] == 146000 and any(p.startswith("ACCTFAIL_") for p in result["problems"])
                if case == "watchdog_thin": result["ok"] = any(p.startswith("NEARFLOOR_") for p in result["problems"])
                if case == "watchdog_missing": result["ok"] = any(p.startswith("STALE_VB150-5|") for p in result["problems"]) and any(p.startswith("NOSTRAT_VB150-5|") for p in result["problems"])
                if case == "watchdog_retired": result["ok"] = not any(p.startswith(("AUTOOFF_OLD|", "NOSTRAT_OLD|")) for p in result["problems"])
                # No real IDs, balances or endpoint values belong in the saved test output.
                result.pop("problems", None)
            results[case] = result
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pwsh", type=Path, default=Path("/workspace/review_tools/pwsh/pwsh"))
    args = parser.parse_args()
    assert args.pwsh.exists(), "Install the pinned official PowerShell runtime first"
    raw = {p: subprocess.check_output(["git", "show", f"{PIN}:{p}"], cwd=ROOT, text=True) for p in PATHS}
    fixed = candidates(raw)
    diff = "".join("".join(difflib.unified_diff(raw[p].splitlines(True), fixed[p].splitlines(True), fromfile=f"a/{p}", tofile=f"b/{p}", n=1)) for p in PATHS if raw[p] != fixed[p])
    assert not re.search(r"(?:PA-)?APEX-\d{4,}-\d{2}", diff) and "apex-alarm-" not in diff
    CODE.mkdir(parents=True, exist_ok=True); OUT.mkdir(parents=True, exist_ok=True)
    (CODE / "reliability.patch").write_text(diff)
    with tempfile.TemporaryDirectory(prefix="codex_patch_apply_") as folder:
        target = Path(folder)
        for p, text in raw.items():
            dest = target / p; dest.parent.mkdir(parents=True, exist_ok=True); dest.write_text(text)
        subprocess.run(["git", "apply", "--check", str(CODE / "reliability.patch")], cwd=target, check=True, capture_output=True)
        subprocess.run(["git", "apply", str(CODE / "reliability.patch")], cwd=target, check=True, capture_output=True)
        assert all((target / p).read_text() == text for p, text in fixed.items())
    checks = {}
    for label, source in [("original", raw), ("candidate", fixed)]:
        with tempfile.TemporaryDirectory(prefix=f"codex_alert_{label}_") as folder:
            root = Path(folder)
            for p, text in source.items():
                dest = root / p; dest.parent.mkdir(parents=True, exist_ok=True); dest.write_text(text)
            cfg = json.loads(source["live/expected_setup.json"])
            checks[label] = {**python_checks(root, label, cfg), **powershell_checks(root, args.pwsh, label, cfg)}
    manifest = dict(reviewed_head=PIN, source_text_normalization="UTF-8, Python universal newline decoding",
                    files={p: hashlib.sha256(s.encode()).hexdigest() for p, s in raw.items()},
                    git_blobs={p: subprocess.check_output(["git", "rev-parse", f"{PIN}:{p}"], cwd=ROOT, text=True).strip() for p in PATHS},
                    patch_sha256=hashlib.sha256(diff.encode()).hexdigest(), script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    patch_applied_to_temporary_source_and_matched_candidates=True,
                    runtime_archive=dict(url="https://github.com/PowerShell/PowerShell/releases/download/v7.6.9/powershell-7.6.9-linux-x64.tar.gz", sha256="1da6d6d6035d651f20e70ddee7c4c15ac6ab8b9fb40ee92240d91263f28a884b"),
                    ps_version=subprocess.check_output([str(args.pwsh), "-NoProfile", "-Command", "$PSVersionTable.PSVersion.ToString()"], env=dict(os.environ, XDG_CACHE_HOME="/workspace/review_tools/cache", XDG_CONFIG_HOME="/workspace/review_tools/config", XDG_DATA_HOME="/workspace/review_tools/data", POWERSHELL_TELEMETRY_OPTOUT="1"), text=True).strip(),
                    external_notifications_sent=0, live_state_changed=False, new_economic_trials=0)
    (OUT / "checks.json").write_text(json.dumps(checks, indent=2) + "\n")
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(checks, indent=2))
    failed = [name for name, value in checks["candidate"].items() if not value["ok"]]
    assert not failed, failed


if __name__ == "__main__":
    main()
