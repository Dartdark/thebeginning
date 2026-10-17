#!/usr/bin/env python3
# revision: 2026-09-06
"""historicaldata.net - options data self-verification tool.

Verify options CSV files downloaded from historicaldata.net: file
integrity, structure, and the guarantees published in README.md - so you
can independently confirm that the files you hold are complete,
uncorrupted, and exactly what we published.

Usage:
    python3 verify.py                      # verify every .csv in the current directory
    python3 verify.py mydata/              # ... in a given directory
    python3 verify.py --complete mydata/   # ... and require every file the manifest lists
    python3 verify.py 2026-08-06_options.csv
    python3 verify.py 2026-08-06_options.csv --sha256 <hex from manifest.json>
    python3 verify.py 2026-08-06_options.csv --md5 <hex ETag from your download>
    python3 verify.py --lenient mydata/    # files you have edited yourself (see below)
    python3 verify.py --contract           # print what this script checks, and where it comes from

THREE MODES - WHAT "PASS" MEANS IN EACH

  default     Strict about content, tolerant about scope. Every file present
              must be exactly as published: the header is the 34 documented
              columns in the documented order, every row has 34 fields, every
              non-blank value parses as its column's type (a finite number, an
              integer, a valid date, one of the listed codes), the columns that
              are never blank are not blank, all 19 row invariants of README
              section 8 hold, and every file a manifest lists is byte-for-byte
              what the manifest records (SHA-256, byte count, row count).
              Files the manifest lists but you do not hold are reported as not
              present - not as failures - because a purchase can be a subset
              of the archive. The summary line says how many of the listed
              files are here, so PASS is never read as "the set is complete".

  --complete  Everything above, and the file set itself: a manifest must be
              present, every file it lists must be here, no unlisted data file
              may be here, and the manifest must carry the interest-rate curve
              for every day it lists (README section 6). Use this for a fixed
              package such as the free sample, or after downloading a whole
              purchase. PASS here means: complete and exactly as published.

  --lenient   For files you have modified yourself - reordered, added or
              removed columns. Columns are located by name; checks whose
              columns are missing are skipped and named. The summary line
              always says how much was skipped, and this mode never claims
              conformance with the published format. Type and value checks
              still apply to whatever is present.

Exit code 0 = verified and passed; 1 = at least one FAILURE;
2 = nothing was verified (no data files found, empty directory, or a usage
error). A run that examined no data never exits 0.
Warnings do not affect the exit code.

WHAT THIS SCRIPT CHECKS, AND WHY THAT LIST IS EXACTLY THIS LONG

Every row check in INVARIANTS below is one line of README section 8,
"Invariants - what is true of every row". Nothing else is checked at row
level, and nothing in section 8 is left unchecked. That is the whole design:

  * We do not check things the README does not promise. A check with no
    published promise behind it would fail files that are perfectly
    valid, and it would quietly become a second, undocumented contract.
  * We do not leave a published promise unchecked. A promise nobody can
    test is a promise you have to take on faith, and this script exists
    precisely so you do not have to.

The structural checks (header, field count, types, required columns) are
the first row of that same table, and the manifest checks come from
sections 1.1, 6 and 9. Each failure quotes the promise it violated and
names the section it comes from.

Requires Python 3.8+, standard library only. A full-market day (~1.5M rows)
takes about a minute and a month roughly half an hour; the free sample
(4.3M rows) takes a few minutes.
"""
import argparse
import hashlib
import json
import math
import os
import re
import sys
from datetime import date, timedelta

# ==============================================================================
# The published contract. Everything in this block is a transcription of
# README.md; if the two ever disagree, the README is right and this is a bug.
# ==============================================================================

# README section 2 - the 34 columns in their published order. In the default and
# --complete modes a file's header must be exactly this; in --lenient mode it is
# used to locate columns by name and to report coverage.
SCHEMA = [
    'contract', 'underlying', 'expiration', 'type', 'strike', 'style',
    'quote_date',
    'bid', 'bid_size', 'ask', 'ask_size', 'quote_time',
    'volume', 'open_interest',
    'open', 'high', 'low', 'close',
    'trade_vwap', 'transactions', 'multileg_volume', 'active_minutes',
    'last_trade_date',
    'underlying_close', 'settlement_time',
    'iv_bid', 'iv_ask', 'iv', 'iv_flag',
    'delta', 'gamma', 'theta', 'vega', 'rho',
]

# README section 2 - the type of every column, from the Type / domain columns of
# the dictionary. A non-blank value must parse as its type:
#   'number'    a finite decimal: digits, one optional point, an optional exponent.
#               NaN, Infinity and any other text are rejected.
#   'integer'   digits only (an optional leading minus), no fractional part.
#   'date'      YYYY-MM-DD, and a real calendar date.
#   'datetime'  YYYY-MM-DDThh:mm:ssZ (ISO 8601, UTC, seconds).
#   a tuple     one of the listed codes, exactly.
#   'text'      unconstrained.
# Blank is not a value (section 3) and is always accepted here; the columns that
# may never be blank are listed separately in REQUIRED.
COLUMN_TYPE = {
    'contract': 'text', 'underlying': 'text', 'expiration': 'date',
    'type': ('call', 'put'), 'strike': 'number', 'style': ('A', 'E'),
    'quote_date': 'date',
    'bid': 'number', 'bid_size': 'integer', 'ask': 'number', 'ask_size': 'integer',
    'quote_time': 'datetime',
    'volume': 'integer', 'open_interest': 'integer',
    'open': 'number', 'high': 'number', 'low': 'number', 'close': 'number',
    'trade_vwap': 'number', 'transactions': 'integer', 'multileg_volume': 'integer',
    'active_minutes': 'integer',
    'last_trade_date': 'date',
    'underlying_close': 'number', 'settlement_time': ('AM', 'PM'),
    'iv_bid': 'number', 'iv_ask': 'number', 'iv': 'number', 'iv_flag': 'integer',
    'delta': 'number', 'gamma': 'number', 'theta': 'number', 'vega': 'number', 'rho': 'number',
}

# README section 2, "Blank means: never blank" - these carry a value on every row.
REQUIRED = ('contract', 'underlying', 'expiration', 'type', 'strike', 'style',
            'quote_date', 'iv_flag')

# README section 8, last row: columns that are blank for a whole era, with the
# first date each one carries data (the `Since` column of section 2).
ERA_START = {
    'active_minutes': '2014-06-01',
    'multileg_volume': '2019-11-04',
    'bid_size': '2005-01-03',
    'ask_size': '2005-01-03',
    'quote_time': '2026-08-06',
}

GREEKS = ('delta', 'gamma', 'theta', 'vega', 'rho')

# The solver's search interval, README section 5.1.
IV_LO, IV_HI = 0.0001, 5.0

def _is_number(s):
    """A finite decimal number. float() is the parser, but it also accepts NaN,
    Infinity, surrounding whitespace and digit underscores - none of which is a
    published value - so those spellings are rejected explicitly."""
    try:
        float(s)
    except ValueError:
        return False
    return not ('n' in s or 'N' in s or 'i' in s or 'I' in s or '_' in s or s != s.strip())


def _is_integer(s):
    return s[1:].isdigit() if s[:1] == '-' else s.isdigit()


def _is_date(s):
    if len(s) != 10 or s[4] != '-' or s[7] != '-':
        return False
    y, m, d = s[:4], s[5:7], s[8:]
    if not (y.isdigit() and m.isdigit() and d.isdigit()):
        return False
    y, m, d = int(y), int(m), int(d)
    if not 1 <= m <= 12 or d < 1:
        return False
    leap = y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)
    days = (31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    return d <= days[m - 1]


def _is_datetime(s):
    if len(s) != 20 or s[10] != 'T' or s[19] != 'Z' or s[13] != ':' or s[16] != ':':
        return False
    hh, mm, ss = s[11:13], s[14:16], s[17:19]
    if not (hh.isdigit() and mm.isdigit() and ss.isdigit()):
        return False
    return _is_date(s[:10]) and int(hh) < 24 and int(mm) < 60 and int(ss) < 60


def field_ok(kind, s):
    """True when a field parses as its column's type. Blank is always accepted;
    REQUIRED handles the columns that may not be blank."""
    if s == '':
        return True
    if kind == 'number':
        return _is_number(s)
    if kind == 'integer':
        return _is_integer(s)
    if kind == 'date':
        return _is_date(s)
    if kind == 'datetime':
        return _is_datetime(s)
    if kind == 'text':
        return True
    return s in kind


def _num(s):
    """A field as a number, or None when it is blank.

    Blank is not zero (README section 3), so every check below treats None as
    "nothing to check here" rather than as a value. A non-numeric value is a
    structural failure and is caught by field_ok before any invariant runs; it
    is never silently treated as blank.
    """
    if s == '':
        return None
    try:
        return float(s)
    except ValueError:
        return None


# -- the invariants ------------------------------------------------------------
# One entry per row of README section 8, in the order they appear there.
#   id    short name used in the output
#   text  the invariant as the README states it - also the failure message
#   ref   where in the README it is published
#   cols  columns it needs; the check is skipped (lenient mode only) when any is missing
#   test  (f, ix, ctx) -> True when the row satisfies it
# `ix` maps column name to field index in THIS file; `ctx` carries the
# file-level facts a row check needs (the date from the filename).
#
# Row shape, types and the header itself are structural and checked before this
# list is applied - a ragged or mistyped row cannot be handed to any of these tests.

def _volume_needs_same_day(f, ix, ctx):
    v = _num(f[ix['volume']])
    if v is None or v <= 0:
        return True
    return f[ix['last_trade_date']] == f[ix['quote_date']]


def _iv_flag_identity(f, ix, ctx):
    fl = f[ix['iv_flag']]
    solved = fl in ('0', '1')
    if (f[ix['iv']] != '') != solved:
        return False
    return all((f[ix[g]] != '') == solved for g in GREEKS)


def _ohlc_ordered(f, ix, ctx):
    lo, hi = _num(f[ix['low']]), _num(f[ix['high']])
    if lo is None or hi is None:
        return True
    if lo > hi:
        return False
    for c in ('open', 'close'):
        v = _num(f[ix[c]])
        if v is not None and not (lo <= v <= hi):
            return False
    return True


def _close_needs_volume(f, ix, ctx):
    c = _num(f[ix['close']])
    if c is None:
        return True
    if c <= 0:
        return False
    v = _num(f[ix['volume']])
    return v is not None and v > 0


def _iv_bounds(f, ix, ctx):
    for c in ('iv', 'iv_bid', 'iv_ask'):
        if c in ix:
            v = _num(f[ix[c]])
            if v is not None and not (IV_LO <= v <= IV_HI):
                return False
    return True


def _greek_domains(f, ix, ctx):
    call = f[ix['type']] == 'call'
    d = _num(f[ix['delta']])
    if d is not None and not ((0 <= d <= 1) if call else (-1 <= d <= 0)):
        return False
    for c in ('gamma', 'vega'):
        v = _num(f[ix[c]])
        if v is not None and v < 0:
            return False
    r = _num(f[ix['rho']])
    if r is not None and (r < 0 if call else r > 0):
        return False
    return True


# README N9: AM settlement implies European exercise everywhere except SOX, which
# the exchange specifies as American-style with AM settlement.
AM_AMERICAN_OK = {'SOX'}


def _settlement(f, ix, ctx):
    st = f[ix['settlement_time']]
    if st not in ('AM', 'PM', ''):
        return False
    if st != 'AM' or f[ix['style']] == 'E':
        return True
    return 'underlying' in ix and f[ix['underlying']] in AM_AMERICAN_OK


def _legs_need_side(f, ix, ctx):
    """A one-sided implied volatility requires a price on that side."""
    for leg, px in (('iv_bid', 'bid'), ('iv_ask', 'ask')):
        if f[ix[leg]] != '':
            p = _num(f[ix[px]])
            if p is None or p <= 0:
                return False
    return True


def _sizes_live(f, ix, ctx):
    """A published size belongs to a live quote: >= 1 contracts at a positive price."""
    for sz, px in (('bid_size', 'bid'), ('ask_size', 'ask')):
        s = _num(f[ix[sz]])
        if s is None:
            continue
        p = _num(f[ix[px]])
        if s < 1 or p is None or p <= 0:
            return False
    return True


def _era_blank(f, ix, ctx):
    for c, start in ctx['era'].items():
        if f[ix[c]] != '':
            return False
    return True


def _nonneg(*cols):
    def test(f, ix, ctx):
        for c in cols:
            v = _num(f[ix[c]])
            if v is not None and v < 0:
                return False
        return True
    return test


def _positive(col):
    def test(f, ix, ctx):
        v = _num(f[ix[col]])
        return v is None or v > 0
    return test


INVARIANTS = [
    dict(id='quote_date', ref='section 8', cols=['quote_date'],
         text='quote_date equals the date in the filename',
         test=lambda f, ix, ctx: ctx['day'] is None or f[ix['quote_date']] == ctx['day']),
    dict(id='type/style', ref='section 8', cols=['type', 'style'],
         text='type is call or put; style is A or E; neither is ever blank',
         test=lambda f, ix, ctx: f[ix['type']] in ('call', 'put') and f[ix['style']] in ('A', 'E')),
    dict(id='strike', ref='section 8', cols=['strike'],
         text='strike > 0',
         test=_positive('strike')),
    dict(id='counts', ref='section 8 (N12, N4)', cols=['volume', 'open_interest'],
         text='volume >= 0; open_interest >= 0',
         test=_nonneg('volume', 'open_interest')),
    dict(id='sizes', ref='section 8 (N3)', cols=['bid_size', 'bid', 'ask_size', 'ask'],
         text='bid_size >= 1 and bid > 0; ask_size >= 1 and ask > 0',
         test=_sizes_live),
    dict(id='active', ref='section 8 (N14)', cols=['active_minutes'],
         text='active_minutes >= 1',
         test=lambda f, ix, ctx: (_num(f[ix['active_minutes']]) is None
                                  or _num(f[ix['active_minutes']]) >= 1)),
    dict(id='quote', ref='section 8', cols=['bid', 'ask'],
         text='bid > 0; ask > 0; bid <= ask',
         test=lambda f, ix, ctx: (_positive('bid')(f, ix, ctx) and _positive('ask')(f, ix, ctx) and
                                  (_num(f[ix['bid']]) is None or _num(f[ix['ask']]) is None or
                                   _num(f[ix['bid']]) <= _num(f[ix['ask']])))),
    dict(id='underlying', ref='section 8', cols=['underlying_close'],
         text='underlying_close > 0',
         test=_positive('underlying_close')),
    dict(id='ohlc', ref='section 8', cols=['open', 'high', 'low', 'close'],
         text='low <= open <= high and low <= close <= high',
         test=_ohlc_ordered),
    dict(id='close', ref='section 8 (section 5.6)', cols=['close', 'volume'],
         text='close > 0, and close present implies volume > 0',
         test=_close_needs_volume),
    dict(id='volume_same_day', ref='section 8 (N12, N7)',
         cols=['volume', 'last_trade_date', 'quote_date'],
         text='volume > 0 implies last_trade_date equals quote_date',
         test=_volume_needs_same_day),
    dict(id='iv_flag', ref='section 8 (section 4)', cols=['iv_flag'],
         text='iv_flag is an integer 0-7 and is never blank',
         test=lambda f, ix, ctx: f[ix['iv_flag']] in ('0', '1', '2', '3', '4', '5', '6', '7')),
    dict(id='identity', ref='section 8 (section 4)', cols=['iv_flag', 'iv'] + list(GREEKS),
         text='iv and the five greeks are present exactly when iv_flag <= 1, and all absent otherwise',
         test=_iv_flag_identity),
    dict(id='legs', ref='section 8 (section 4)', cols=['iv_bid', 'bid', 'iv_ask', 'ask'],
         text='iv_bid present implies bid > 0; iv_ask present implies ask > 0',
         test=_legs_need_side),
    dict(id='iv_range', ref='section 8', cols=['iv_bid', 'iv_ask', 'iv'],
         text='iv_bid <= iv <= iv_ask',
         test=lambda f, ix, ctx: (f[ix['iv_bid']] == '' or f[ix['iv_ask']] == '' or f[ix['iv']] == '' or
                                  float(f[ix['iv_bid']]) <= float(f[ix['iv']]) <= float(f[ix['iv_ask']]))),
    dict(id='iv_bounds', ref='section 8 (section 5.1)', cols=['iv'],
         text='0.0001 <= iv <= 5.0, and the same bounds for iv_bid / iv_ask',
         test=_iv_bounds),
    dict(id='greeks', ref='section 8 (N5)', cols=['type'] + list(GREEKS),
         text='delta in [0,1] for calls and [-1,0] for puts; gamma >= 0; vega >= 0; '
              'rho >= 0 for calls and <= 0 for puts',
         test=_greek_domains),
    dict(id='settlement', ref='section 8 (N9)', cols=['settlement_time', 'style', 'underlying'],
         text='settlement_time is AM, PM or blank, and AM implies style = E '
              'for every underlying except SOX',
         test=_settlement),
    dict(id='eras', ref='section 8 (section 2)', cols=[],   # columns resolved per file
         text='active_minutes blank before 2014-06; multileg_volume blank before 2019-11-04; '
              'the two size columns blank before 2005-01-03; quote_time blank before 2026-08-06',
         test=_era_blank),
]

# ==============================================================================
# End of the published contract. Everything below is machinery: reading files,
# checksums, the trading calendar, and reporting.
# ==============================================================================

# -- colored output, only where it is known to render --------------------------
# Colors are opt-out by construction: anything unproven prints plain text, so
# the output is never littered with escape sequences. Piped/redirected output,
# NO_COLOR, dumb terminals (Emacs shell-mode, some CI), and Windows consoles
# that refuse ANSI all fall back to plain text.
def _use_color():
    if not sys.stdout.isatty() or os.environ.get('NO_COLOR'):
        return False
    if os.name == 'nt':
        try:                         # Windows 10+: switch ANSI processing on;
            import ctypes            # older consoles fail here and stay plain
            k, mode = ctypes.windll.kernel32, ctypes.c_uint32()
            h = k.GetStdHandle(-11)
            return bool(k.GetConsoleMode(h, ctypes.byref(mode))
                        and k.SetConsoleMode(h, mode.value | 0x0004))
        except Exception:
            return False
    # Linux/macOS: ANSI is native to every normal terminal; TERM says otherwise
    # only for genuinely incapable ones.
    return os.environ.get('TERM', '') not in ('', 'dumb')

RED, YEL, GRN, OFF = ('\033[91m', '\033[93m', '\033[92m', '\033[0m') if _use_color() else ('',) * 4

# Column names come from the file being checked and are echoed back, so they may
# hold characters the console encoding cannot represent. Substitute rather than
# abort: a verification tool must never die on the report it is writing.
try:
    sys.stdout.reconfigure(errors='replace')
except Exception:
    pass

FAIL = 0
CUR = ''                             # file currently being verified (for the summary)
FAILURES = []                        # (file, message)
WARNINGS = []
SKIPS = []                           # (file, message) - lenient mode only: checks that did not run
def bad(msg):
    global FAIL
    FAIL = 1
    FAILURES.append((CUR, msg))
    print(f'  {RED}FAIL  {msg}{OFF}')
def warn(msg):
    WARNINGS.append((CUR, msg))
    print(f'  {YEL}WARN  {msg}{OFF}')
def skipped_check(msg):
    SKIPS.append((CUR, msg))
    print(f'  {YEL}SKIP  {msg}{OFF}')

# -- U.S. market holiday calendar (NYSE full-day holidays + observation rules) --
# Needed for the coverage report of README section 9; it is the one input this
# script cannot take from the README, because a calendar is not a data guarantee.
def _easter(y):
    a = y % 19; b = y // 100; c = y % 100; d = b // 4; e = b % 4
    f = (b + 8) // 25; g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30; i = c // 4; k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7; m = (a + 11 * h + 22 * l) // 451
    mo = (h + l - 7 * m + 114) // 31; da = ((h + l - 7 * m + 114) % 31) + 1
    return date(y, mo, da)

def _js_wd(d):                      # Sunday=0 ... Saturday=6
    return (d.weekday() + 1) % 7

def _nth_weekday(y, mo, wd, n):
    first = _js_wd(date(y, mo, 1))
    return date(y, mo, 1 + (wd - first) % 7 + (n - 1) * 7)

def _last_weekday(y, mo, wd):
    last = date(y + (mo == 12), mo % 12 + 1, 1) - timedelta(days=1)
    return last - timedelta(days=(_js_wd(last) - wd) % 7)

def _observed(y, mo, da, new_year_rule=False):
    d = date(y, mo, da); wd = _js_wd(d)
    if wd == 6:
        return None if new_year_rule else d - timedelta(days=1)
    if wd == 0:
        return d + timedelta(days=1)
    return d

# One-off market closures. These cannot be derived from any rule, so they are listed.
# Leaving them out would report those dates as trading days with no file - a gap that
# does not exist. The U.S. market was shut on each of these.
_ONE_OFF_CLOSURES = {
    '1994-04-27',                                            # Nixon funeral
    '2001-09-11', '2001-09-12', '2001-09-13', '2001-09-14',  # markets reopened Sep 17
    '2004-06-11',                                            # Reagan funeral
    '2007-01-02',                                            # Ford funeral
    '2012-10-29', '2012-10-30',                              # Hurricane Sandy
    '2018-12-05',                                            # G.H.W. Bush funeral
    '2025-01-09',                                            # Carter funeral
}

def us_market_holiday(d):
    if d.isoformat() in _ONE_OFF_CLOSURES:
        return True
    y = d.year
    hol = [
        _observed(y, 1, 1, True),
        _nth_weekday(y, 1, 1, 3),
        _nth_weekday(y, 2, 1, 3),
        _easter(y) - timedelta(days=2),
        _last_weekday(y, 5, 1),
        _observed(y, 6, 19) if y >= 2022 else None,
        _observed(y, 7, 4),
        _nth_weekday(y, 9, 1, 1),
        _nth_weekday(y, 11, 4, 4),
        _observed(y, 12, 25),
    ]
    return d in [h for h in hol if h is not None]

def is_trading_day(d):
    return _js_wd(d) not in (0, 6) and not us_market_holiday(d)

# -- per-file verification -----------------------------------------------------
# ==============================================================================
# Which files are ours. This is the options verifier; the stock product line
# ships its own, separate script (decided 2026-08-28 - passing an interface
# across two repositories cost more than sharing one file would have saved).
#
# Dispatch is by FILENAME, never by content: a file that looks like ours but is
# not ours must be skipped with a reason, not parsed on a guess. The delivery
# tool hands this script everything it just downloaded - README, licence,
# manifests, and for someone who buys both products, stock files too. Reporting
# any of those as a failure would teach buyers to ignore this output, which
# costs more than the check is worth.
#
# The one thing the two verifiers must agree on: neither reports the other's
# files as broken. That is the whole of the arrangement between them.
# ==============================================================================

OPTIONS_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}_options.*\.csv$', re.I)


def is_ours(basename):
    """True if this filename is a published options data file."""
    return bool(OPTIONS_PATTERN.match(basename))


def check_csv(name, day_iso, data, lenient):
    """Structure, types, required columns and the section-8 invariants of one file.

    Returns the number of data rows, so the caller can compare it with the manifest.
    """
    global CUR
    CUR = name
    print(f'-- {name}  {len(data) / 1048576:.1f} MB')
    print(f'   sha256={hashlib.sha256(data).hexdigest()}')
    print(f'   md5={hashlib.md5(data).hexdigest()}')
    text = data.decode('utf-8', errors='replace')
    lines = text.split('\n')
    cols = lines[0].rstrip('\r').split(',')
    ix = {c: i for i, c in enumerate(cols)}
    ncol = len(cols)

    unknown = [c for c in cols if c not in SCHEMA]
    missing = [c for c in SCHEMA if c not in ix]
    dupes = sorted({c for c in cols if cols.count(c) > 1})
    print(f'   columns: {ncol} in file, {len(SCHEMA) - len(missing)}/{len(SCHEMA)} of the documented schema')
    # README section 8, first row: the header is exactly the 34 names in that order.
    # Strict modes: any deviation is a failure - a reordered, trimmed or extended file
    # is not the published format, whatever else it contains.
    # Lenient mode: locate by name, skip what cannot run, and say so.
    if cols != SCHEMA:
        detail = []
        if unknown:
            detail.append('unrecognized column(s): ' + ', '.join(unknown))
        if missing:
            detail.append('absent column(s): ' + ', '.join(missing))
        if dupes:
            detail.append('duplicate column(s): ' + ', '.join(dupes))
        if not detail:
            detail.append('the 34 columns are not in the published order')
        if not lenient:
            bad('header is not the 34 documented columns in the documented order '
                '[README section 8]: ' + '; '.join(detail))
            return 0
        warn('lenient mode: ' + '; '.join(detail) + ' - checks run on what is present, located by name')
        if dupes:
            bad('duplicate column names cannot be located by name: ' + ', '.join(dupes))
            return 0
        if unknown:
            print(f'   ignoring unrecognized column(s): {", ".join(unknown)}')

    # Which era columns must be blank in THIS file, given its date.
    era = {c: s for c, s in ERA_START.items() if c in ix and day_iso is not None and day_iso < s}
    ctx = {'day': day_iso, 'era': era}

    # An invariant runs only when this file gives it something to check. Whatever
    # does not run is named in the output with the reason: a check that silently
    # did not run is indistinguishable from one that passed, and this script must
    # never look greener than what it actually examined.
    active, skipped = [], []
    for inv in INVARIANTS:
        need = list(era) if inv['id'] == 'eras' else inv['cols']
        absent = [c for c in need if c not in ix]
        if absent:
            skipped.append((inv, 'needs ' + ', '.join(absent)))
        elif inv['id'] == 'eras' and not era:
            # Not a skip: every era column this file has is inside its era, so
            # the promise is vacuously kept. Reported as such, not counted as unrun.
            active.append(inv)
        elif inv['id'] == 'quote_date' and day_iso is None:
            skipped.append((inv, 'no date in the filename to compare against'))
        else:
            active.append(inv)

    typed = [(i, c, COLUMN_TYPE[c]) for i, c in enumerate(cols) if c in COLUMN_TYPE]
    required = [(ix[c], c) for c in REQUIRED if c in ix]

    n = dict.fromkeys([inv['id'] for inv in INVARIANTS], 0)
    n['_ragged'] = n['_rows'] = 0
    badtype = {}                     # column -> [count, first example]
    blank_required = {}              # column -> count
    stat = dict.fromkeys('iv greeks legs close vol am pm'.split(), 0)
    flags = {}
    unds = set()
    has = lambda *c: all(x in ix for x in c)
    st_iv, st_gk, st_legs, st_close, st_st = (has('iv'), has(*GREEKS), has('iv_bid', 'iv_ask'),
                                              has('close', 'volume'), has('settlement_time'))
    for ln in lines[1:]:
        if not ln:
            continue
        f = ln.rstrip('\r').split(',')
        n['_rows'] += 1
        if len(f) != ncol:
            n['_ragged'] += 1
            continue
        # -- structure: types and required columns (README section 2 / section 8, first row)
        row_ok = True
        for i, c, kind in typed:
            v = f[i]
            if v != '' and not field_ok(kind, v):
                row_ok = False
                t = badtype.setdefault(c, [0, v])
                t[0] += 1
        for i, c in required:
            if f[i] == '':
                row_ok = False
                blank_required[c] = blank_required.get(c, 0) + 1
        if not row_ok:
            # A mistyped row is reported once, structurally; it is not handed to the
            # invariants, which would only report the same defect in other words.
            continue
        for inv in active:
            if not inv['test'](f, ix, ctx):
                n[inv['id']] += 1

        # -- statistics, not checks: a picture of the day, no pass/fail attached
        if 'underlying' in ix:
            unds.add(f[ix['underlying']])
        if 'iv_flag' in ix:
            fl = f[ix['iv_flag']]
            flags[fl] = flags.get(fl, 0) + 1
        if st_iv and f[ix['iv']] != '':
            stat['iv'] += 1
        if st_gk and all(f[ix[g]] != '' for g in GREEKS):
            stat['greeks'] += 1
        if st_legs and f[ix['iv_bid']] != '' and f[ix['iv_ask']] != '':
            stat['legs'] += 1
        if st_close:
            if f[ix['volume']] not in ('', '0'):
                stat['vol'] += 1
            if f[ix['close']] != '':
                stat['close'] += 1
        if st_st:
            s = f[ix['settlement_time']]
            if s == 'AM':
                stat['am'] += 1
            elif s == 'PM':
                stat['pm'] += 1

    r = n['_rows']
    pc = lambda x: f'{x / r * 100:.2f}%' if r else '-'
    line = f'   rows {r:,}'
    if unds:
        line += f'   underlyings {len(unds):,}'
    print(line)
    if flags:
        print('   iv_flag  ' + '  '.join(f'{k}:{flags[k]:,}' for k in sorted(flags)))
    parts = []
    if st_iv: parts.append(f'iv {pc(stat["iv"])}')
    if st_gk: parts.append(f'greeks {pc(stat["greeks"])}')
    if st_legs: parts.append(f'bid/ask-iv range {pc(stat["legs"])}')
    if st_close: parts.append(f'close {pc(stat["close"])}   volume>0 {pc(stat["vol"])}')
    if st_st: parts.append(f'AM {stat["am"]:,} / PM {stat["pm"]:,}')
    if parts:
        print('   ' + '   '.join(parts))
    if r == 0:
        bad('no data rows - an empty file is not a published day')
    print(f'   structure: header, {ncol} fields per row, {len(typed)} typed columns, '
          f'{len(required)} never-blank columns - checked on every row')
    print(f'   section 8: {len(active)} of {len(INVARIANTS)} invariants checked on every row'
          + (' (all)' if len(active) == len(INVARIANTS) else ''))
    for inv, why in skipped:
        skipped_check(f'not checked - {inv["id"]}: {why}')

    if n['_ragged']:
        bad(f'{n["_ragged"]:,} rows do not have exactly {ncol} fields (ragged rows) [README section 8]')
    for c, (cnt, ex) in badtype.items():
        kind = COLUMN_TYPE[c]
        want = ('one of ' + '/'.join(kind)) if isinstance(kind, tuple) else 'a ' + kind
        print_ex = ex if len(ex) <= 40 else ex[:37] + '...'
        bad(f'{cnt:,} rows: {c} is not {want} (e.g. "{print_ex}") [README section 2]')
    for c, cnt in blank_required.items():
        bad(f'{cnt:,} rows: {c} is blank, but it is never blank [README section 2]')
    for inv in active:
        if n[inv['id']]:
            bad(f'{n[inv["id"]]:,} rows violate "{inv["text"]}" [README {inv["ref"]}]')
    return r

# Both manifest names we publish: the whole archive, and the rolling window
# (`last-21-days_manifest.json`; older packages spelled it `last-21d_`).
MANIFEST_RE = re.compile(r'^(?:manifest|last-\d+-?d(?:ays)?_manifest)\.json$')

def load_manifests(dirs):
    """Read every manifest sitting in the directories being checked.

    Keyed by the CSV path it describes, mapping to EVERY manifest that declares it.
    A manifest that cannot be parsed is a failure, not something to step over: a
    directory that carries a broken manifest is not self-verifying, and saying
    "no manifest" would hide that.

    Two manifests beside the same files can legitimately disagree about a day: a
    revision (section 10) replaces the file and the full manifest, while an older
    rolling-window manifest you kept still records the previous bytes. A file is
    accepted when it matches at least one manifest that lists it; the stale one is
    reported as a warning naming the file, so you know which record is out of date.
    """
    global CUR
    entries, found = {}, []
    for d in sorted(dirs):
        try:
            names = sorted(os.listdir(d))
        except OSError:
            continue
        for fn in names:
            if not MANIFEST_RE.match(fn):
                continue
            try:
                # Strict JSON: Python's parser accepts NaN / Infinity / -Infinity by
                # default, which no manifest we publish contains. Rejecting them here
                # means a curve with such a value is a broken manifest, not a number.
                man = json.load(open(os.path.join(d, fn), encoding='utf-8'),
                                parse_constant=_reject_json_constant)
                files = man['files']
                if not isinstance(files, list):
                    raise ValueError('files is not a list')
                for e in files:
                    if not (isinstance(e.get('name'), str) and isinstance(e.get('sha256'), str)
                            and isinstance(e.get('bytes'), int) and isinstance(e.get('rows'), int)):
                        raise ValueError('an entry lacks name/sha256/bytes/rows')
            except Exception as ex:
                CUR = fn
                bad(f'{fn} cannot be read as a manifest ({ex}) - the directory is not self-verifying')
                continue
            # Each manifest keeps its own path map so its block can report ITS numbers.
            # A shared counter would credit the rolling-window manifest with matches
            # that only the full manifest covers - a wrong number that reads as right.
            own = {os.path.normpath(os.path.join(d, e['name'])): e for e in files}
            found.append((os.path.join(d, fn), man, own))
            for p, e in own.items():
                entries.setdefault(p, []).append((fn, e))
    return entries, found

def _reject_json_constant(name):
    raise ValueError(f'non-standard JSON constant {name}')


def _finite_rate(x):
    """A usable tenor value: a real, finite number. bool is a subclass of int in
    Python and would otherwise pass as 0 or 1; NaN and Infinity are numbers to
    float() but not rates."""
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def curve_ok(v):
    """README section 6: seven tenors in a fixed order, each a finite number or null
    (null = the Treasury published no value for that tenor). A curve that carries no
    finite value at all cannot price anything and counts as missing."""
    return (isinstance(v, list) and len(v) == 7
            and all(x is None or _finite_rate(x) for x in v)
            and any(_finite_rate(x) for x in v))


def manifest_rates_missing(man):
    """Days this manifest lists without a usable interest-rate curve (README section 6),
    stored under the trading date."""
    rates = man.get('rates')
    if not isinstance(rates, dict):
        return [e['name'][:10] for e in man.get('files', [])]
    return [e['name'][:10] for e in man.get('files', []) if not curve_ok(rates.get(e['name'][:10]))]

def report_directory(path, man, own, result, present_paths, complete):
    """Findings about the collection as a whole, not about any one file.

    Kept in its own block below the per-file output: at the same indent these read as
    properties of whichever file happened to print last.
    Returns (listed, present-and-listed) for the summary line.
    """
    global CUR
    base = os.path.basename(path)
    CUR = base
    print('')
    print(f'-- {base} (whole manifest)')
    # Counted from THIS manifest's own results. A shared tally would double-count a
    # file that matches one manifest and fails another - which is exactly the case
    # worth reporting clearly, and the first version of this printed "-1 day(s)".
    declared = man.get('files', [])
    verified = len(own.keys() & result['ok'])
    mismatched = len(own.keys() & result['bad'])
    absent = sorted(os.path.basename(p) for p in own.keys() - present_paths)
    print(f'   lists {len(declared)} day(s), {declared[0]["name"][:10]} to '
          f'{declared[-1]["name"][:10]}' if declared else '   lists no files')
    if not declared:
        bad('the manifest lists no files')
    if verified:
        print(f'   {verified} file(s) here match their recorded SHA-256, byte count and row count')
    if mismatched:
        # bad() was already called per file; restate the count so the block is complete.
        print(f'   {mismatched} file(s) here do NOT match - see failures below')
    if absent:
        if complete:
            shown = ' '.join(absent[:8]) + (' ...' if len(absent) > 8 else '')
            bad(f'{len(absent)} file(s) this manifest lists are not here (--complete requires all): {shown}')
        else:
            # Not an error in the default mode. The manifest describes the whole archive;
            # your copy is what you purchased (section 9). The summary line repeats this
            # count so that PASS is never mistaken for "the set is complete".
            print(f'   {len(absent)} day(s) listed but not present here'
                  f' (outside what you downloaded; use --complete to require them)')
    norates = manifest_rates_missing(man)
    if norates:
        shown = ' '.join(norates[:5]) + (' ...' if len(norates) > 5 else '')
        msg = (f'{len(norates)} of the {len(declared)} listed day(s) have no interest-rate curve '
               f'in this manifest (README section 6) - the calculated columns of those days '
               f'cannot be reproduced from this package: {shown}')
        if complete:
            bad(msg)
        else:
            warn(msg)
    miss = man.get('trading_days_missing') or []
    if miss:
        warn('trading days we have not published, inside the range this manifest covers: '
             + ' '.join(miss))
    return len(declared), len(declared) - len(absent)

def report_coverage(present_days, declared_days):
    """Holes inside the range you actually hold.

    Checked over first-to-last of what is present, not over whole months: a copy that
    begins mid-month is not missing the earlier days, it simply starts there.

    A trading day inside that range with no file is only worth reporting when the
    manifest does not list it either. If the manifest lists it, you simply did not
    download that day - which is the normal case for anything short of the whole
    archive, and warning about it buries the one case that matters. (Without any
    manifest the two cannot be told apart, so everything is reported.)
    """
    if not present_days:
        return
    seen = sorted(date.fromisoformat(d) for d in present_days)
    have, gaps, not_taken, extra = set(seen), [], 0, []
    d, stop = seen[0], seen[-1]
    while d <= stop:
        if is_trading_day(d) and d not in have:
            if str(d) in declared_days:
                not_taken += 1
            else:
                gaps.append(str(d))
        if not is_trading_day(d) and d in have:
            extra.append(str(d))
        d += timedelta(days=1)
    if extra:
        bad('files present on non-trading days: ' + ' '.join(extra))
    if gaps:
        warn('trading days neither present here nor listed in any manifest: ' + ' '.join(gaps))
    if not_taken:
        print(f'   {not_taken} trading day(s) inside your range were not downloaded'
              f' (they are listed in the manifest)')
    if not gaps and not extra:
        print(f'   calendar coverage complete: {len(seen)} trading days'
              f' ({seen[0]} to {seen[-1]}), no unexplained gaps')

def print_contract():
    """What this script checks and where each check comes from."""
    print('This script checks the structure of every file, the invariants published')
    print('in README.md section 8 - no more, no less - and the manifest beside the')
    print('files. Each check is listed below with the section it comes from.')
    print('')
    print('Structure, checked on every row (README section 2 and section 8, first row):')
    print('  header       exactly the 34 names of section 2, in that order (default and')
    print('               --complete; --lenient locates columns by name and reports skips)')
    print('  fields       every row has exactly 34 fields')
    print('  types        every non-blank value parses as its column type: a finite')
    print('               number (NaN, Infinity and text rejected), an integer, a valid')
    print('               YYYY-MM-DD date, an ISO 8601 UTC timestamp, or a listed code')
    print('  required     contract, underlying, expiration, type, strike, style,')
    print('               quote_date and iv_flag are never blank')
    print('')
    print('Row invariants (README section 8):')
    for inv in INVARIANTS:
        print(f'  {inv["id"]:<12} {inv["text"]}')
        print(f'  {"":<12}   [README {inv["ref"]}]')
    print('')
    print('Manifest and file set:')
    print('  section 1.1  every file a manifest lists matches its recorded SHA-256,')
    print('               byte count and row count; a manifest that cannot be parsed')
    print('               is a failure. --sha256 / --md5 compare one file directly')
    print('  section 6    the manifest carries the interest-rate curve for every day')
    print('               it lists (warning by default, failure with --complete)')
    print('  section 9    trading days inside the range you hold, against the U.S.')
    print('               market calendar')
    print('  --complete   every listed file is present, nothing unlisted is present')
    print('  section 10   a file that matches one manifest but not an older one beside')
    print('               it is a recorded revision, reported as a warning')
    print('')
    print('Deliberately NOT checked:')
    print('  implied volatilities and greeks are not re-solved (section 9): verifying')
    print('  our numbers with our own formulas would only prove self-consistency.')
    print('  Section 5 and section 6 specify the model and its inputs for your own')
    print('  library. Structure and integrity are what this script proves.')
    print('')
    print('Exit codes: 0 verified and passed; 1 at least one failure; 2 nothing verified.')

# -- main ----------------------------------------------------------------------
def main():
    global CUR
    ap = argparse.ArgumentParser(description='Verify historicaldata.net options CSV files.')
    ap.add_argument('paths', nargs='*', help='files and/or directories (default: current directory)')
    ap.add_argument('--complete', action='store_true',
                    help='require a manifest, every file it lists, nothing unlisted, and a rate '
                         'curve for every listed day (fixed packages, whole purchases)')
    ap.add_argument('--lenient', action='store_true',
                    help='files you have modified: locate columns by name, skip and report '
                         'checks that cannot run; never asserts the published format')
    ap.add_argument('--sha256', help='expected SHA-256 (from manifest.json); applies to a single file')
    ap.add_argument('--md5', help='expected MD5 (the object ETag your client received); applies to a single file')
    ap.add_argument('--contract', action='store_true',
                    help='print what this script checks, and the README section each check comes from')
    a = ap.parse_args()

    if a.contract:
        print_contract()
        sys.exit(0)
    if a.complete and a.lenient:
        print('--complete and --lenient contradict each other: pick one')
        sys.exit(2)

    files, skipped = [], []
    for p in (a.paths or ['.']):
        if os.path.isdir(p):
            files += sorted(os.path.join(p, f) for f in os.listdir(p)
                            if f.lower().endswith('.csv'))
        elif os.path.isfile(p):
            # Say plainly that a file is not ours to check. Parsing, say, a manifest as
            # a CSV would report "ragged rows", which reads as damaged data.
            if p.lower().endswith('.csv'):
                files.append(p)
            else:
                skipped.append(p)
        else:
            print(f'not found: {p}')
            sys.exit(2)
    # A .csv that matches neither product is still not ours - symbols.csv is the
    # obvious case. Say which and why; the delivery hook passes everything it
    # downloaded, so unrelated files here are normal, not a problem.
    foreign = [f for f in files if not is_ours(os.path.basename(f))]
    files = [f for f in files if is_ours(os.path.basename(f))]
    for p in skipped:
        print(f'skipping {p}: not a CSV file')
    for p in foreign:
        print(f'skipping {p}: filename does not match any published data file')
    if not files:
        # Nothing examined is not a pass. Exit 2 tells a caller apart from both a
        # verified PASS (0) and a verified FAIL (1).
        if foreign or skipped:
            print('nothing to verify here - none of the given files are published data files')
        else:
            print('no data files found - pass a file or directory, or run inside your download folder')
        print('== 0 file(s): NOTHING VERIFIED ==')
        sys.exit(2)
    if (a.sha256 or a.md5) and len(files) != 1:
        print('--sha256/--md5 apply to exactly one file')
        sys.exit(2)

    # A manifest beside the CSVs makes the directory self-verifying: its per-file
    # SHA-256, byte count and row count need no network access.
    dirs = {os.path.dirname(f) or '.' for f in files}
    declared, manifests = load_manifests(dirs)
    if a.complete and not manifests:
        CUR = 'directory'
        bad('--complete requires a manifest beside the files, and none was found')
    per_manifest, present_paths, present_days = {}, set(), set()
    # Files no manifest covers. A rolling-window subscriber accumulates files forever
    # while holding only last-21-days_manifest.json, so most of what they hold cannot be
    # checksum-checked. That is not a failure - but a green PASS that quietly skipped
    # 200 of 215 files would be a lie by omission, so it is stated on the summary line.
    # With --complete an unlisted data file is a failure: the set is not the package.
    uncovered = set()

    total = 0
    for path in files:
        CUR = os.path.basename(path)
        raw = open(path, 'rb').read()
        print(f'== verifying {path}  {len(raw) / 1048576:.1f} MB ==')
        if a.sha256:
            if hashlib.sha256(raw).hexdigest() == a.sha256.lower():
                print('   sha256 MATCHES the expected value - file is exactly as published')
            else:
                bad(f'sha256 mismatch: file={hashlib.sha256(raw).hexdigest()} expected={a.sha256.lower()}')
        if a.md5:
            if hashlib.md5(raw).hexdigest() == a.md5.lower().strip('"'):
                print('   md5 MATCHES the expected value - file is exactly as published')
            else:
                bad(f'md5 mismatch: file={hashlib.md5(raw).hexdigest()} expected={a.md5.lower()}')
        m = re.search(r'(\d{4}-\d{2}-\d{2})', os.path.basename(path))
        day = m.group(1) if m else None
        rows = check_csv(os.path.basename(path), day, raw, a.lenient)
        if day:
            present_days.add(day)
        # Checked against EVERY manifest that declares this file. A file that matches at
        # least one is accepted; a manifest it does not match is stale (section 10) if
        # another one matches, and evidence of alteration if none does.
        norm = os.path.normpath(path)
        present_paths.add(norm)
        got = hashlib.sha256(raw).hexdigest()
        records = declared.get(norm, [])
        matched = [mname for mname, exp in records if got == exp['sha256']]
        for mname, exp in records:
            r = per_manifest.setdefault(mname, {'ok': set(), 'bad': set()})
            if got == exp['sha256']:
                if len(raw) != exp['bytes']:
                    bad(f'byte count {len(raw):,} differs from {mname} ({exp["bytes"]:,}) although the SHA-256 matches')
                    r['bad'].add(norm)
                elif rows != exp['rows']:
                    bad(f'row count {rows:,} differs from {mname} ({exp["rows"]:,}) although the SHA-256 matches')
                    r['bad'].add(norm)
                else:
                    r['ok'].add(norm)
            elif matched:
                warn(f'{mname} records different bytes for this file; it matches {matched[0]} - '
                     f'{mname} predates a recorded revision (README section 10)')
            else:
                bad(f'SHA-256 does not match {mname} - content altered or not the published file')
                r['bad'].add(norm)
        if norm not in declared:
            uncovered.add(norm)
        total += 1

    listed = present_listed = 0
    if manifests:
        for mpath, man, own in manifests:
            r = per_manifest.get(os.path.basename(mpath), {'ok': set(), 'bad': set()})
            n_listed, n_here = report_directory(mpath, man, own, r, present_paths, a.complete)
            listed, present_listed = max(listed, n_listed), max(present_listed, n_here)
    else:
        CUR = 'directory'
        print('')
        print('-- no manifest found beside these files')
        warn('per-file checksums could not be verified; download manifest.json to enable them')
    if manifests and uncovered:
        CUR = 'directory'
        print('')
        print(f'-- {len(uncovered)} file(s) no manifest here covers')
        if a.complete:
            shown = ' '.join(sorted(os.path.basename(p) for p in uncovered)[:8])
            bad(f'{len(uncovered)} data file(s) present that no manifest lists (--complete): {shown}')
        else:
            print('   their checksums were not checked. This is normal for a rolling')
            print('   subscription: you keep every day you ever downloaded, while')
            print('   last-21-days_manifest.json only describes the current window.')
            print('   To checksum-verify the older ones, fetch the full manifest.json.')
    print('')
    declared_days = {e['name'][:10] for lst in declared.values() for _, e in lst}
    report_coverage(present_days, declared_days)

    # -- final summary: every warning and failure in one place -----------------
    print()
    if SKIPS:
        print(f'{YEL}{len(SKIPS)} check(s) skipped (lenient mode) - not passed, not run:{OFF}')
        for f, m in SKIPS:
            print(f'  {YEL}SKIP{OFF}  [{f}] {m}')
    if WARNINGS:
        print(f'{YEL}{len(WARNINGS)} warning(s) - informational, often genuine market-data history:{OFF}')
        for f, m in WARNINGS:
            print(f'  {YEL}WARN{OFF}  [{f}] {m}')
    # A green PASS must never imply more than was actually checked: the summary line
    # itself says how the file set relates to the manifest and what was skipped.
    if a.complete:
        scope = f'complete set: {present_listed} of {listed} listed files present'
    elif manifests:
        scope = (f'{present_listed} of {listed} listed files present'
                 + ('; completeness not asserted (use --complete)' if present_listed < listed else ''))
    else:
        scope = 'no manifest: checksums not verified'
    if uncovered and not a.complete:
        scope += f'; {len(uncovered)} not checksum-verified (no manifest covers them)'
    if a.lenient:
        scope += f'; lenient: {len(SKIPS)} check(s) skipped, published format not asserted'
    if FAILURES:
        print(f'{RED}{len(FAILURES)} failure(s):{OFF}')
        for f, m in FAILURES:
            print(f'  {RED}FAIL{OFF}  [{f}] {m}')
        print(f'== {total} file(s): {RED}FAIL - the file(s) above are damaged or inconsistent{OFF} ({scope}) ==')
    elif a.lenient:
        print(f'== {total} file(s): {GRN}PASS (lenient){OFF} - what was checked passed ({scope}) ==')
    else:
        print(f'== {total} file(s): {GRN}PASS{OFF} - exactly as published ({scope}) ==')
    sys.exit(FAIL)

if __name__ == '__main__':
    main()
