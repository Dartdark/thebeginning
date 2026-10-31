"""Engineering fixtures for entry diagnostics; no strategy tests or live reads."""
from pathlib import Path
import json
import re
import tempfile
import unittest

import numpy as np
import pandas as pd

import codex_execution_diagnostics as D


class Checks(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='codex_entry_checks_');self.p=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def row(self,**changes):
        r=dict(attempt_id='a1',event_id='signal1',trading_date='2026-10-21',strategy='VB',account='SYNTH-01',
          instrument='MNQZ6',actual_contract='MNQZ6',side=1,qty=8,filled_qty=8,order_type='market',status='filled',
          reason='',order_id='synthetic-order',fill_price=100.5,signal_time_utc='2026-10-21T17:00:00Z',
          submission_time_utc='2026-10-21T17:00:00.100Z',fill_time_utc='2026-10-21T17:00:00.200Z')
        r.update(changes);return r
    def orders(self,rows):
        p=self.p/'orders.csv';pd.DataFrame(rows).to_csv(p,index=False);return D.read_orders(p)
    def quote(self,basis,**changes):
        r=dict(attempt_id='a1',basis=basis,quote_time_utc='2026-10-21T17:00:00Z',bid=100.,ask=100.5,
          symbol='MNQ',actual_contract='MNQZ6',freshness_verified=True)
        r.update(changes);return r
    def quotes(self,orders,rows):
        p=self.p/'quotes.csv';pd.DataFrame(rows).to_csv(p,index=False);return D.quote_costs(orders,p)
    def bar(self,time,price=100.,**changes):
        r=dict(bar_close_time_utc=pd.Timestamp(time),symbol='NQ',actual_contract='',open=price,high=price,low=price,close=price)
        r.update(changes);return r

    def test_two_accounts_one_event_and_distinct_signals(self):
        d=self.orders([self.row(),self.row(attempt_id='a2',account='SYNTH-02',order_id='other'),
                       self.row(attempt_id='a3',event_id='signal2')])
        e=D.event_summary(d);self.assertEqual(len(e),2)
        self.assertEqual(e.loc[e.event_id.eq('signal1'),'order_attempt_rows'].item(),2)
        self.assertEqual(e.market_event_count.sum(),2)
    def test_conflicting_event_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'Conflicting event'):
            self.orders([self.row(),self.row(attempt_id='a2',side=-1)])
    def test_naive_utc_refused(self):
        with self.assertRaisesRegex(ValueError,'explicit timezone'):
            self.orders([self.row(fill_time_utc='2026-10-21 17:00:00')])
    def test_clock_order_refused(self):
        with self.assertRaisesRegex(ValueError,'out of order'):
            self.orders([self.row(fill_time_utc='2026-10-21T16:59:00Z')])
    def test_rejected_order_is_not_a_fill(self):
        d=self.orders([self.row(status='rejected',filled_qty=0,fill_price='',fill_time_utc='')])
        self.assertEqual(D.windows(d,None).query("basis=='fill'").availability.unique().tolist(),['unavailable_no_fill'])
        with self.assertRaisesRegex(ValueError,'cannot carry a fill'):
            self.orders([self.row(status='rejected')])
    def test_missed_requires_declared_coverage(self):
        r=self.row(status='missed',filled_qty=0,fill_price='',fill_time_utc='')
        self.assertEqual(self.orders([r]).classification.item(),'unresolved_no_fill')
        self.assertEqual(self.orders([dict(r,coverage_verified=True)]).classification.item(),'missed')
    def test_real_transcription_preserves_broker_zero_and_fraction(self):
        text=(D.ROOT/'agents/codex/inputs/execution_diagnostics/orders_20261020_21.md').read_text()
        d=D.tracker_entries(text)
        self.assertEqual(len(d),6);self.assertEqual(d.order_id.eq('0').sum(),2)
        self.assertEqual(d.account.ne('').sum(),0);self.assertTrue(d.fill_time_utc.eq('').all())
        self.assertEqual(d.loc[d.source_row.eq('12'),'fill_price'].item(),30086.5)
        p=self.p/'actual_transcription.csv';d.to_csv(p,index=False)
        self.assertEqual(len(D.event_summary(D.read_orders(p))),3)
    def test_tracker_timezone_only_when_explicit(self):
        text=(D.ROOT/'agents/codex/inputs/execution_diagnostics/orders_20261020_21.md').read_text()
        d=D.tracker_entries(text,'America/Chicago')
        value=d.loc[d.source_row.eq('18'),'fill_time_utc'].item()
        self.assertEqual(pd.Timestamp(value),pd.Timestamp('2026-10-21T17:00:00.300Z'))
        self.assertTrue(d.signal_time_utc.eq('').all());self.assertTrue(d.submission_time_utc.eq('').all())
    def test_last_completed_bar_not_next_close(self):
        bars=pd.DataFrame([self.bar('2026-10-21T17:00:00Z',100),self.bar('2026-10-21T17:01:00Z',999)])
        z=D.window_sample(pd.Timestamp('2026-10-21T17:00:30Z'),0,bars,'MNQZ6')
        self.assertEqual(z['price'],100);self.assertEqual(z['sample_lag_seconds'],30)
        self.assertEqual(z['benchmark_kind'],'NQ_continuous_price_proxy')
    def test_sunday_preopen_unavailable_and_no_friday_carry(self):
        t=pd.Timestamp('2026-10-18T22:00:00Z') # Sunday 17:00 CT
        b=pd.DataFrame([self.bar('2026-10-18T21:59:00Z')])
        self.assertEqual(D.window_sample(t,-1,b,'MNQZ6')['availability'],'unavailable_weekend_preopen')
        self.assertNotEqual(D.window_sample(t,0,b,'MNQZ6')['availability'],'observed_completed_minute_close')
    def test_exact_contract_beats_proxy_and_wrong_month_unavailable(self):
        tm='2026-10-21T17:00:00Z'
        b=pd.DataFrame([self.bar(tm,90),self.bar(tm,100,symbol='MNQ',actual_contract='MNQZ6')])
        z=D.window_sample(pd.Timestamp(tm),0,b,'MNQZ6');self.assertEqual(z['price'],100)
        self.assertEqual(z['benchmark_kind'],'same_contract_minute_close')
        only_wrong=b[b.symbol.eq('MNQ')]
        self.assertNotEqual(D.window_sample(pd.Timestamp(tm),0,only_wrong,'MNQH7')['availability'],'observed_completed_minute_close')
    def test_quote_decomposition_and_spread(self):
        d=self.orders([self.row(fill_price=101.5)])
        q=self.quotes(d,[self.quote('signal'),self.quote('submission'),self.quote('fill',bid=101,ask=101.5)])
        z=q.iloc[0]
        self.assertEqual(z.quoted_spread_fill_ticks,2)
        self.assertEqual(z.effective_fill_cost_vs_mid_ticks,1)
        self.assertEqual(z.signed_signal_to_fill_mid_move_ticks,4)
        self.assertEqual(z.total_fill_vs_signal_mid_ticks,5)
    def test_crossed_stale_future_and_proxy_quotes_unmeasurable(self):
        d=self.orders([self.row()])
        for change in [dict(bid=101,ask=100),dict(freshness_verified=False),dict(quote_time_utc='2026-10-21T16:59:58Z'),
                       dict(quote_time_utc='2026-10-21T17:00:01Z'),dict(symbol='NQ'),dict(actual_contract='MNQH7')]:
            q=self.quotes(d,[self.quote('fill',**change)])
            self.assertTrue(np.isnan(q.effective_fill_cost_vs_mid_ticks.item()))
    def test_duplicate_bars_refused(self):
        b=pd.DataFrame([self.bar('2026-10-21T17:00:00Z')]*2);p=self.p/'bars.csv';b.to_csv(p,index=False)
        with self.assertRaisesRegex(ValueError,'duplicate'):D.load_bars(p)
    def test_empty_orders_have_stable_output_schemas(self):
        p=self.p/'empty.csv';pd.DataFrame(columns=D.REQUIRED).to_csv(p,index=False);d=D.read_orders(p)
        self.assertTrue(D.event_summary(d).empty);self.assertIn('price',D.windows(d,None))
        self.assertIn('quoted_spread_fill_ticks',D.quote_costs(d,None))
    def test_proposed_logger_preserves_legacy_rows_and_sidecar_field_count(self):
        original=(D.ROOT/'agents/codex/inputs/execution_diagnostics/Apex_Trade_Logger_original.txt').read_text()
        proposal=(D.ROOT/'agents/codex/proposals/Apex_Trade_Logger_bidask.txt').read_text()
        pattern=r'(?ms)^\s*Row\s*=.*?FileAppend\(FileName, Row \+ NewLine\);'
        legacy=lambda text:[re.sub(r'\s+',' ',x).strip() for x in re.findall(pattern,text)]
        self.assertEqual(len(legacy(original)),3);self.assertEqual(legacy(original),legacy(proposal))
        marker='// ---------- health rows'
        self.assertEqual(original[original.index(marker):].strip(),proposal[proposal.index(marker):].strip())
        assignments=re.findall(r'(?s)ObsRow = (.*?);',proposal)
        self.assertEqual(len(assignments),2)
        for a in assignments:
            literals=re.findall(r'"([^"]*)"',a)
            self.assertEqual(sum(x.count(',') for x in literals)+1,21)
        self.assertEqual(proposal.count('FileAppend(ObsFile, ObsRow + NewLine);'),2)
        self.assertIn('ObsPCDateTime = ComputerDateTime;',proposal)
        self.assertNotRegex(proposal,r'(?mi)^\s*(buy|sell|sellshort|buytocover)\b')


if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks))
    out=D.ROOT/'analysis/outputs/codex_execution_diagnostics';out.mkdir(parents=True,exist_ok=True)
    (out/'fixture_checks.json').write_text(json.dumps(dict(tests_run=result.testsRun,successful=result.wasSuccessful(),
      failures=[str(t) for t,_ in result.failures],errors=[str(t) for t,_ in result.errors]),indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
