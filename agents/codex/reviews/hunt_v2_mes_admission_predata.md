# H09 admission: independent source/synthetic review PASS

The reviewed SOURCE adapter may proceed to its frozen, committed input/support gate. This is a software review, **not** a source-support pass, measured gross effect, design result, MC parity, or book-improvement candidate. The reviewer accessed no actual ES input header, schema, row, price, ATR, event count, generated exchange schedule, cached market frame, terminal return, or financial study.

Budget at review: **5 economic evaluations / 9 registered hypotheses / 4 gross screens**, plus archived t6 history. This review adds none. The original parent and related sizing selection history remain binding.

## Bound implementation

| Source | SHA256 |
|---|---|
| `analysis/codex_hunt_v2_mes_moc_admit.py` | `a6e88a6314524483fbd5f2b0e537a4dbd6bee69cd517047aea6838e9881dd2d5` |
| `agents/codex/plans/hunt_v2_mes_moc_affordability.md` | `2ae71ec9c6d3b479b9d780e5fdda2b662393a70da7d5d82a1c208df21f3349a3` |
| `analysis/codex_hunt_v2_mes_parent.py` | `b69057f5967a35d45619a60476c4a821edccda6e578483ce4c34044ae56302c3` |
| `analysis/grid24.py` | `3f041b5f8c2b2a0d89d299749ec867d2314c78ea006cbe47f699e8d4f0468b9c` |
| `analysis/codex_s03_calendar.py` | `705713195b1be61cd648d1b72718442b6cec7581587ca8c537d491cf1312bceb` |
| `analysis/replica.py` | `c0ae001152c75395748b0f3fdb4bdcbc589d0a124befce0170ef454c3da6f58f` |

The implementation resolves the immutable preregistration and verifies it is an ancestor on `codex/work`; the original plan/evidence must be byte-identical. Every used local code/dependency must match committed HEAD. Pinned parent source commit/path/blob and SHA are recorded, alongside Python/numpy/pandas versions. A changed code or plan hash invalidates this review binding.

## Findings

- All six exact 2017–22 ES regular files are size/SHA bound before the first CSV header is interpreted. There is no broad raw-data glob, maker or all-year cache. The shared grid reads only the six corresponding symlinks under the allowed Codex cache, with no night pattern. Existing unexpected cache contents or redirecting links fail.
- The schema is explicitly seven lowercase fields, strict YYYYMMDD/HHMM and source-year membership. All owned rows would be audited globally for finite positive quarter-tick ES OHLC, ordering, nonnegative volume and duplicate conflicts **before** shared Grid24 can select first duplicates. Identical duplicates retain every CSV source ID. The fixed tick representation tolerance does not authorize substantive quote repair. An unexpected actual schema is a source failure, not permission to guess a new parser silently.
- The shared grid arrays are checked against the global native audit, including presence. Its `trading`, later `last_j` and `daily_atr` do not choose membership or ATR. Shared midnight-aligned observed five-minute bars retain contributing IDs, incomplete buckets, exact native close availability and chart-date boundaries. The independently reviewed parent helper owns causal literal ATR/decision state; this adapter does not substitute an ideal daily range or use a current day's terminal range.
- Every normal cash date permitted by the preregistered literal/calendar port must have a recorded, complete exact C1400 and C1450 decision audit and positive ready prior ATR, including nonsignals. Entire absent dates or partial references produce whole-phase failure, not no-trade deletion. Every provisional parent retains its identity and requires every native minute891..900, O1451 and exact C1500. Future path presence can veto the whole study; it cannot selectively remove losing paths.
- Affordability comes from the exact-rational parent helper and native-ceiled stop distance. Support enforces the frozen100parents/50EXTRA/10EXTRA per side/3years/95%known criteria. Null combinatorics match year, parent side and exact move/ATR bins, fix unknown EXTRA0, require a variable cell and at least1000 **distinct** possible masks. A constant-two allocation cannot pass through repeated draws. No masks or financial paths are sampled here.
- Known cash closures/early sessions are an explicitly frozen conservative research port beyond the literal PL predicate. Per-date disagreement flags and observed late bars are retained even when the literal early predicate also agrees with the shared calendar. This is not exact MC parity. The author corrected that late-bar audit omission before any actual data run; the current hash includes the correction.
- Source code contains no terminal C1500-minus-O1451 calculation, stop walker, gross/net return, economic metric, account bench or 2023+ input path. `--fixtures` reads no actual source or schedule. The exclusive source lock, write-once attempt/artifacts, rehash after execution and immutable marker prevent an unchanged hidden retry. A failed source/support gate authorizes closure only, not a new gross phase.

The adapter's observed historical ATR ranges, upstream exporter civil-clock/roll assumptions, ES-price proxy/MES prelisting and liquidity, and ordinary next-open availability remain limits. A software PASS does not establish authenticated receipt, complete feed or executable historic MES fills. Runtime/schema failure must be retained and adjudicated; it cannot silently become an economic pass.

## Synthetic evidence

The adapter's **six bundled invented groups** passed. An independent check passed **six additional groups**: identical duplicates/source IDs; conflicting duplicate global veto; off-tick/clock/year/volume failures retained together; entire expected date absent; partial reference on a nonsignal date; and a missing held minute preserving the ticket while later-day presence cannot rescue it. A seventh independent invented calendar case confirmed late bars are retained for both literal-early agreement and literal/shared disagreement. No market returns were calculated.

Reproduce the bundled groups with `/workspace/venvs/thebeginning/bin/python -B analysis/codex_hunt_v2_mes_moc_admit.py --fixtures`. The following independent check reads only temporary invented CSV rows under the allowed Codex output tree, deletes those temporary files, restores injected module constants, and never imports/applies a real schedule:

```python
import sys, tempfile, pathlib
from datetime import date
sys.dont_write_bytecode = True
sys.path.insert(0, 'analysis')
import codex_hunt_v2_mes_moc_admit as m
import numpy as np
base = pathlib.Path.cwd() / 'analysis/outputs/codex_hunt_v2_mes_affordability/review_synthetic'
base.mkdir(parents=True, exist_ok=True)
original = {k: getattr(m, k) for k in ('ROOT', 'NATIVE', 'FIRST', 'LAST')}
try:
    with tempfile.TemporaryDirectory(prefix='invented_', dir=base) as t:
        tmp = pathlib.Path(t); (tmp/'data').mkdir()
        m.ROOT = tmp
        m.NATIVE = ('data/ES_1min_2018.csv',)
        m.FIRST, m.LAST = date(2018,1,1), date(2018,1,3)
        p = tmp/m.NATIVE[0]
        header = 'date,time,open,high,low,close,volume\n'
        good = '20180102,1450,100,101,99,100.25,7\n'
        p.write_text(header+good+good)
        a, records, duplicates, audit = m.audit_native()
        assert audit['passed'] and audit['identical_duplicate_rows'] == 1
        assert m.source_ids(1,890,records,duplicates) == [
            'data/ES_1min_2018.csv:csv:2', 'data/ES_1min_2018.csv:csv:3']
        p.write_text(header+good+'20180102,1450,100,101,99,100.50,7\n')
        a, records, duplicates, audit = m.audit_native()
        assert not audit['passed'] and 'Conflicting duplicate' in audit['issues'][0]['issue']
        assert a[3,1,890] == 100.25
        p.write_text(header+good+
            '20180103,1450,100.1,101,99,100.25,7\n'+
            '20180102,2460,100,101,99,100.25,7\n'+
            '20190102,1450,100,101,99,100.25,7\n'+
            '20180103,1451,100,101,99,100.25,-1\n')
        _, _, _, audit = m.audit_native()
        assert not audit['passed'] and len(audit['issues']) == 4
        def fake_calendar(s):
            return dict(kind='normal',cash_close_j=900,reason='INVENTED') if s == '2018-01-02' else dict(kind='holiday',cash_close_j=None,reason='INVENTED')
        presence = dict(date='2018-01-02',reference_state='COMPLETE_EXACT',decision_state='COMPLETE_EXACT')
        decision = dict(date='2018-01-02',atr=10,source_flags=[],literal_parent_qualified=True)
        parent = dict(decision_audit=[decision],observed_date_coverage=[presence])
        records = np.zeros((3,1440),dtype=np.uint32); records[1,836:901] = 2
        expected, _ = m.expected_date_audit(parent,records,{},fake_calendar)
        assert all(x['passed'] for x in expected)
        empty = dict(decision_audit=[],observed_date_coverage=[])
        expected, _ = m.expected_date_audit(empty,records,{},fake_calendar)
        assert [x['date'] for x in expected if not x['passed']] == ['2018-01-02']
        partial = dict(presence,reference_state='PARTIAL')
        expected, _ = m.expected_date_audit(dict(parent,observed_date_coverage=[partial]),records,{},fake_calendar)
        assert not next(x for x in expected if x['date']=='2018-01-02')['passed']
        rows = [dict(event_id=0,date='2018-01-02',side=1)]
        assert m.held_path_audit(rows,records,{})[0]['passed']
        records[1,896] = 0
        held = m.held_path_audit(rows,records,{})
        assert not held[0]['passed'] and held[0]['missing_native_keys']==[896] and held[0]['event_id']==0
        records[1,1439] = 2
        assert m.held_path_audit(rows,records,{}) == held
        records = np.zeros((3,1440),dtype=np.uint32)
        records[0,890], records[1,890] = 3,4
        def fake_closed(s):
            return dict(kind='early' if s=='2018-01-01' else 'holiday',cash_close_j=720 if s=='2018-01-01' else None,reason='ARTIFICIAL_NOT_A_REAL_SCHEDULE')
        expected, contradictions = m.expected_date_audit(empty,records,{},fake_closed)
        assert {x['date'] for x in contradictions} == {'2018-01-01','2018-01-02'}
        assert not expected[0]['calendar_literal_disagreement'] and expected[1]['calendar_literal_disagreement']
finally:
    for k,v in original.items(): setattr(m,k,v)
print('PASS: seven independent invented admission groups; no market data or returns')
```

No code, progress record, shared source, strategy definition, live setting or branch was changed by this reviewer. Only this review artifact and temporary invented fixtures under the declared Codex output tree were written. Actual execution remains the root researcher's responsibility after preregistration and reviewed implementation are committed.
