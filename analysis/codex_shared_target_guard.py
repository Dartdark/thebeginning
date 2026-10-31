"""Research-only manual balance publisher and reference checks. No broker access."""
from __future__ import annotations

import argparse
import configparser
from contextlib import contextmanager
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation, ROUND_CEILING, ROUND_FLOOR
import json
import os
from pathlib import Path
import re
import secrets
import tempfile
from zoneinfo import ZoneInfo

CT = ZoneInfo("America/Chicago")
MAX_INT = 2_147_483_647
FIELDS = ("Schema", "Token", "Revision", "SessionDate", "AsOfDate", "AsOfTime",
          "BalanceCents", "TargetCents", "FlatConfirmed")


def cents(text):
    try:
        x = Decimal(str(text))
        if not x.is_finite() or x <= 0 or x * 100 != (x * 100).to_integral_value():
            raise ValueError("Use a positive dollar amount with at most two decimal places")
        n = int(x * 100)
        if n > MAX_INT:
            raise ValueError("Amount exceeds the signed 32-bit cents format")
        return n
    except (InvalidOperation, OverflowError) as exc:
        raise ValueError("Invalid dollar amount") from exc


def alias(value):
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,39}", value):
        raise ValueError("Use an ASCII account alias, not a broker account identifier")
    return value


def chicago(now):
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("An aware timestamp is required")
    return now.astimezone(CT)


def session_date(now, publishing=False):
    now = chicago(now)
    minute = now.hour * 60 + now.minute
    start = 16 * 60 if publishing else 17 * 60
    weekday = now.weekday()
    if weekday == 5 or (weekday == 4 and minute >= 16 * 60) or (weekday == 6 and minute < start):
        raise ValueError("Weekend closed window")
    if not publishing and 16 * 60 <= minute < 17 * 60:
        raise ValueError("Maintenance window")
    d = now.date() + timedelta(days=1 if minute >= start else 0)
    return int(d.strftime("%Y%m%d"))


def checksum(row):
    return 1 + sum((i + 1) * row[k] for i, k in enumerate(FIELDS)) % 1_000_000_006


def check_config(c):
    if set(c) != {"schema", "account_alias", "token", "size", "target_cents"}:
        raise ValueError("Unexpected account configuration")
    alias(c["account_alias"])
    if c["schema"] != 1 or type(c["token"]) is not int or not 1 <= c["token"] <= MAX_INT:
        raise ValueError("Invalid account configuration token/schema")
    if c["size"] not in (50000, 150000) or type(c["target_cents"]) is not int:
        raise ValueError("Only the existing 50K and 150K evaluation profiles are supported")
    if not c["size"] * 100 < c["target_cents"] <= MAX_INT:
        raise ValueError("Invalid fixed target")
    return c


def make_snapshot(c, balance, now, revision, flat_confirmed):
    check_config(c)
    if not flat_confirmed:
        raise ValueError("Confirm ALL account positions are flat and the balance is reconciled")
    if type(revision) is not int or not 1 <= revision <= MAX_INT:
        raise ValueError("Invalid/exhausted revision")
    local = chicago(now)
    row = dict(Schema=1, Token=c["token"], Revision=revision,
               SessionDate=session_date(local, publishing=True),
               AsOfDate=int(local.strftime("%Y%m%d")), AsOfTime=local.hour * 100 + local.minute,
               BalanceCents=cents(balance), TargetCents=c["target_cents"], FlatConfirmed=1)
    row["Checksum"] = checksum(row)
    return row


def parse_snapshot(text):
    p = configparser.ConfigParser(interpolation=None, strict=True)
    p.optionxform = str
    p.read_string(text)
    if p.sections() != ["Guard"] or p.defaults():
        raise ValueError("Expected exactly one Guard section, without defaults")
    values = dict(p["Guard"])
    if set(values) != set(FIELDS) | {"Checksum"}:
        raise ValueError("Unexpected snapshot fields")
    if any(not re.fullmatch(r"[0-9]+", s) for s in values.values()):
        raise ValueError("Snapshot fields must be nonnegative decimal integers")
    row = {k: int(v) for k, v in values.items()}
    if any(not 0 <= v <= MAX_INT for v in row.values()):
        raise ValueError("Snapshot integer out of range")
    if row["Checksum"] != checksum(row):
        raise ValueError("Snapshot checksum mismatch")
    return row


def encode(row):
    return "[Guard]\n" + "".join(f"{k}={row[k]}\n" for k in (*FIELDS, "Checksum"))


def validate(row, c, now, end_revision=None):
    """Reference consumer; no financial/account P&L is inferred."""
    check_config(c)
    row = parse_snapshot(encode(row))
    if row["Schema"] != 1 or row["Token"] != c["token"] or row["FlatConfirmed"] != 1:
        raise ValueError("Schema/account/flat mismatch")
    if row["TargetCents"] != c["target_cents"] or row["BalanceCents"] <= 0:
        raise ValueError("Target/balance mismatch")
    if row["Revision"] <= 0 or (end_revision is not None and end_revision != row["Revision"]):
        raise ValueError("Mixed/invalid revision")
    local = chicago(now)
    stamp = datetime.strptime(f"{row['AsOfDate']:08d}{row['AsOfTime']:04d}", "%Y%m%d%H%M").replace(tzinfo=CT)
    if stamp > local or session_date(stamp, publishing=True) != row["SessionDate"]:
        raise ValueError("Future or inconsistent as-of time")
    if session_date(local) != row["SessionDate"]:
        raise ValueError("Stale or wrong session")
    return "TARGET_ALREADY_MET" if row["BalanceCents"] >= row["TargetCents"] else "VALID_SNAPSHOT"


def limit_price(balance_cents, target_cents, entry, point_value, quantity, tick, side):
    if side not in (-1, 1) or quantity <= 0 or int(quantity) != quantity:
        raise ValueError("Invalid side/whole-contract quantity")
    b, t, e, pv, q, tk = map(lambda x: Decimal(str(x)),
                            (balance_cents, target_cents, entry, point_value, quantity, tick))
    if not 0 < b < t or pv <= 0 or tk <= 0:
        raise ValueError("Invalid balance, target or instrument")
    raw = e + side * (t - b) / (100 * pv * q)
    rounding = ROUND_CEILING if side == 1 else ROUND_FLOOR
    return (raw / tk).to_integral_value(rounding=rounding) * tk


@contextmanager
def writer_lock(path):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        os.write(fd, str(os.getpid()).encode("ascii"))
        os.close(fd)
        fd = None
        yield
    finally:
        if fd is not None:
            os.close(fd)
        path.unlink(missing_ok=True)


def atomic_write(path, text):
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="ascii", newline="\n") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def initialize(folder, account, size, buffer="50.00"):
    account = alias(account)
    if size not in (50000, 150000):
        raise ValueError("Choose 50000 or 150000")
    buf = cents(buffer)
    target = (size + (3000 if size == 50000 else 9000)) * 100 + buf
    c = check_config(dict(schema=1, account_alias=account, token=secrets.randbelow(MAX_INT) + 1,
                          size=size, target_cents=target))
    folder.mkdir(parents=True, exist_ok=True)
    with writer_lock(folder / f"{account}.lock"):
        path = folder / f"{account}.json"
        if path.exists() or (folder / f"{account}.ini").exists():
            raise ValueError("Account already exists; fixed configuration will not be overwritten")
        atomic_write(path, json.dumps(c, indent=2) + "\n")
    return c


def publish(folder, account, balance, now, flat_confirmed):
    account = alias(account)
    with writer_lock(folder / f"{account}.lock"):
        c = check_config(json.loads((folder / f"{account}.json").read_text(encoding="ascii")))
        if c["account_alias"] != account:
            raise ValueError("Configuration alias mismatch")
        path = folder / f"{account}.ini"
        previous = parse_snapshot(path.read_text(encoding="ascii")) if path.exists() else None
        if previous and (previous["Token"] != c["token"] or previous["TargetCents"] != c["target_cents"]):
            raise ValueError("Existing state belongs to a different account/target")
        row = make_snapshot(c, balance, now, 1 + (previous["Revision"] if previous else 0), flat_confirmed)
        atomic_write(path, encode(row))
        return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, required=True, help="Explicit LOCAL PAPER/RESEARCH state folder")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    init.add_argument("--account", required=True)
    init.add_argument("--size", type=int, choices=[50000, 150000], required=True)
    init.add_argument("--buffer", default="50.00")
    update = sub.add_parser("update")
    update.add_argument("--account", required=True)
    update.add_argument("--balance", help="Omit to enter the balance at a prompt")
    update.add_argument("--flat-confirmed", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "init":
            result = initialize(args.state_dir, args.account, args.size, args.buffer)
        else:
            if not args.flat_confirmed:
                raise ValueError("Requires --flat-confirmed after checking ALL account positions")
            balance = args.balance if args.balance is not None else input(f"Verified flat-account balance for {args.account}: ")
            result = publish(args.state_dir, args.account, balance, datetime.now(CT), True)
        print(json.dumps(result, indent=2))
        print("RESEARCH ONLY: no broker queried, no orders sent, no chart settings changed.")
    except (ValueError, OSError, configparser.Error, json.JSONDecodeError) as exc:
        parser.exit(2, f"No update published: {exc}\n")


if __name__ == "__main__":
    main()
