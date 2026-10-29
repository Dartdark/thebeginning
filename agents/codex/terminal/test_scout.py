"""Offline integration checks for bounded discovery, provenance, dedup, and failed scans."""
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import tempfile
import unittest
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlsplit

import scout

NOW=datetime(2026,10,29,16,0,tzinfo=timezone.utc)


def paper(id='9000001', **extra):
    return dict(DOI='10.2139/ssrn.'+id, title=['Equity Index Futures Rebalancing and Dealer Hedging'],
                abstract='<jats:p>We find a scheduled flow in index futures at option expiration.</jats:p>',
                author=[{'given':'Jane','family':'Researcher'}], published={'date-parts':[[2026,5,2]]}, **extra)


class ScoutTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name)
        self.runtime=self.root/'runtime';(self.root/'agents/codex/results').mkdir(parents=True)

    def tearDown(self):self.temp.cleanup()

    def test_normalization_never_inherits_analysis_claims(self):
        p=scout.normalize_candidate(paper(status='verified',profit=4000,evidence_level='independent_validation'))
        self.assertEqual(p['evidence_level'],'metadata_only');self.assertNotIn('profit',p)
        self.assertEqual(p['authors'],['Jane Researcher']);self.assertNotIn('<',p['abstract'])
        self.assertEqual(p['published'],'2026-05-02')
        with self.assertRaises(ValueError):scout.normalize_candidate({'DOI':'10.9999/foo','title':'Other paper'})

    def test_topic_routing_is_not_profitable_verdict(self):
        category,score,reasons=scout.classify(scout.normalize_candidate(paper()))
        self.assertEqual(category,'strategy');self.assertGreater(score,0)
        self.assertTrue(any('Metadata routing only' in s for s in reasons))
        p=scout.normalize_candidate({'ssrn_id':'9000002','title':'Queue priority and transaction costs'})
        self.assertEqual(scout.classify(p)[0],'execution')
        p=scout.normalize_candidate({'ssrn_id':'9000003','title':'Corporate bond ESG preferences'})
        self.assertEqual(scout.classify(p)[0],'low_relevance')

    def test_duplicate_scan_and_primary_repository_review(self):
        path=self.root/'agents/codex/results/review.md'
        path.write_text('# Source review\nSource: https://ssrn.com/abstract=9000001\n## Findings\nFacts')
        first=scout.import_candidates(self.root,self.runtime,[paper(),paper()],now=NOW)
        self.assertEqual(len(first['papers']),1)
        self.assertEqual(first['papers'][0]['status'],'already_reviewed')
        self.assertEqual(first['runs'][-1]['counts']['already_reviewed'],1)
        self.assertEqual(first['papers'][0]['review_path'],'agents/codex/results/review.md')
        again=scout.import_candidates(self.root,self.runtime,[paper()],now=NOW)
        self.assertEqual(again['runs'][-1]['counts']['added'],0)
        self.assertEqual(again['runs'][-1]['counts']['seen_again'],1)
        self.assertEqual(again['papers'][0]['first_seen'],NOW.isoformat())
        self.assertEqual(len(scout.list_state(self.root,self.runtime)['papers']),1)

    def test_secondary_citation_is_not_a_completed_review(self):
        path=self.root/'agents/codex/results/review.md'
        path.write_text('# Different source\nSource: https://ssrn.com/abstract=1234567\n## Related literature\nhttps://ssrn.com/abstract=9000001')
        s=scout.import_candidates(self.root,self.runtime,[paper()],now=NOW)
        self.assertEqual(s['papers'][0]['status'],'needs_full_text')
        self.assertEqual(s['papers'][0]['reviewed_in'],[])
        self.assertEqual(s['papers'][0]['repository_mentions'],['agents/codex/results/review.md'])

    def test_discover_fixed_https_api_caps_and_receipts(self):
        requests=[]
        def opener(request,timeout):
            requests.append((request.full_url,timeout))
            return io.BytesIO(json.dumps({'message':{'items':[paper(),paper('9000002')]}}).encode())
        s=scout.discover(self.root,self.runtime,max_results=1,opener=opener,now=NOW)
        self.assertEqual(len(s['papers']),1);self.assertEqual(len(requests),len(scout.QUERIES))
        for url,timeout in requests:
            parsed=urlsplit(url);self.assertEqual(parsed.hostname,'api.crossref.org');self.assertEqual(parsed.scheme,'https')
            self.assertIn('query',parse_qs(parsed.query));self.assertEqual(timeout,8)
        self.assertEqual(s['runs'][-1]['status'],'completed');self.assertEqual(s['runs'][-1]['return_trials'],0)
        self.assertEqual(s['papers'][0]['status'],'needs_full_text')
        self.assertTrue((self.runtime/'scout.json').exists());self.assertFalse((self.runtime/'scout.lock').exists())

    def test_failure_is_not_empty_success_and_preserves_prior_candidates(self):
        scout.import_candidates(self.root,self.runtime,[paper()],now=NOW)
        def failed(request,timeout):raise URLError('destination unavailable')
        s=scout.discover(self.root,self.runtime,opener=failed,now=NOW)
        self.assertEqual(len(s['papers']),1);self.assertEqual(s['runs'][-1]['status'],'failed')
        self.assertEqual(len(s['runs'][-1]['errors']),4)
        self.assertTrue(all(x['status']=='failed' for x in s['runs'][-1]['attempts']))

    def test_partial_provider_failure_is_recorded(self):
        calls=[]
        def mixed(request,timeout):
            calls.append(request)
            if len(calls)==2:raise HTTPError(request.full_url,429,'rate limit',{},None)
            return io.BytesIO(json.dumps({'message':{'items':[paper()]}}).encode())
        s=scout.discover(self.root,self.runtime,opener=mixed,now=NOW)
        self.assertEqual(s['runs'][-1]['status'],'partial');self.assertIn('HTTP 429',s['runs'][-1]['errors'][0])
        self.assertEqual(len(calls),2)
        self.assertEqual(s['runs'][-1]['network_requests'],2)
        self.assertEqual([a['status'] for a in s['runs'][-1]['attempts']],['completed','failed','skipped','skipped'])

    def test_hard_denial_stops_host_requests(self):
        for failure in [401,403,429,'proxy 403 Forbidden']:
            with self.subTest(failure=failure):
                requests=[]
                def denied(request,timeout):
                    requests.append(request)
                    if isinstance(failure,int):raise HTTPError(request.full_url,failure,'denied',{},None)
                    raise URLError(failure)
                s=scout.discover(self.root,self.runtime,opener=denied,now=NOW)
                self.assertEqual(len(requests),1)
                run=s['runs'][-1]
                self.assertEqual(run['status'],'failed');self.assertEqual(run['network_requests'],1)
                self.assertEqual([a['status'] for a in run['attempts']],['failed','skipped','skipped','skipped'])
                self.assertEqual(run['stop_reason'],'rate_limited' if failure==429 else 'access_denied')

    def test_schema_limits_busy_lock_and_conflicting_ids(self):
        with self.assertRaises(ValueError):scout.discover(self.root,self.runtime,max_results=31,now=NOW)
        with self.assertRaises(ValueError):scout.discover(self.root,self.runtime,max_results=True,now=NOW)
        with self.assertRaises(ValueError):scout.normalize_candidate(paper(ssrn_id='9000002'))
        self.runtime.mkdir();(self.runtime/'scout.lock').write_text('123')
        with self.assertRaises(ValueError):scout.import_candidates(self.root,self.runtime,[paper()],now=NOW)

    def test_redirect_host_is_allowlisted(self):
        from urllib.request import Request
        with self.assertRaises(ValueError):
            scout._StrictRedirect().redirect_request(Request(scout.API_ROOT),None,302,'Found',{},'https://ssrn.com/download.pdf')

    def test_missing_abstract_and_invalid_metadata_remain_visible(self):
        s=scout.import_candidates(self.root,self.runtime,[{'ssrn_id':'9000008','title':'A generic survey'}, {'title':'No identifier'}],now=NOW)
        self.assertEqual(s['papers'][0]['status'],'metadata_only');self.assertEqual(s['runs'][-1]['status'],'partial')
        self.assertEqual(s['runs'][-1]['counts']['invalid'],1)

    def test_author_string_and_bad_provider_responses(self):
        p=scout.normalize_candidate({'ssrn_id':'9000008','title':'A paper','authors':'Jane Researcher'})
        self.assertEqual(p['authors'],['Jane Researcher'])
        def malformed(request,timeout):return io.BytesIO(b'{"message":{}}')
        s=scout.discover(self.root,self.runtime,opener=malformed,now=NOW)
        self.assertEqual(s['runs'][-1]['status'],'failed')
        self.assertEqual(s['runs'][-1]['counts']['added'],0)


if __name__=='__main__':unittest.main()
