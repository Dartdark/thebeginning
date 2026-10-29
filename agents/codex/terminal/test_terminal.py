"""HTTP integration tests using an isolated temporary inbox and note store."""
import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest
import server


class TerminalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.http=server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
        cls.thread=threading.Thread(target=cls.http.serve_forever,daemon=True);cls.thread.start()

    @classmethod
    def tearDownClass(cls):cls.http.shutdown();cls.http.server_close();cls.thread.join()

    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.original=server.RUNTIME;server.RUNTIME=Path(self.tmp.name)

    def tearDown(self):server.RUNTIME=self.original;self.tmp.cleanup()

    def request(self,path,method='GET',body=None,headers=None):
        c=http.client.HTTPConnection('127.0.0.1',self.http.server_port)
        c.request(method,path,body=body,headers=headers or {})
        r=c.getresponse();raw=r.read();status=r.status;c.close()
        try:return status,json.loads(raw)
        except ValueError:return status,raw

    def test_catalog_and_source_document(self):
        status,c=self.request('/api/catalog');self.assertEqual(status,200)
        self.assertGreater(len(c['documents']),100)
        self.assertTrue(any('overnight_tail_risk' in d['path'] for d in c['documents']))
        status,doc=self.request('/api/document?path=agents/codex/EXECUTION_REFERENCES.md')
        self.assertEqual(status,200);self.assertIn('E15',doc['content'])

    def test_research_boundary(self):
        for p in ['../../etc/passwd','live/trades/20261029.csv','AGENTS.md']:
            status,_=self.request('/api/document?path='+p);self.assertEqual(status,400)
        status,_=self.request('/api/result?path=../../etc/passwd');self.assertEqual(status,400)
        status,_=self.request('/server.py');self.assertEqual(status,404)

    def test_notes_persist_and_stale_save_rejected(self):
        note=dict(id='1',title='Tail risk',source='SSRN 2494387',body='User note, not a verified result')
        payload=json.dumps(dict(revision=0,notes=[note]))
        status,x=self.request('/api/notes','POST',payload);self.assertEqual(status,200)
        self.assertEqual(x['revision'],1);self.assertEqual(server.state()['notes'],[note])
        status,_=self.request('/api/notes','POST',payload);self.assertEqual(status,409)
        status,x=self.request('/api/state');self.assertEqual(x['notes'],[note])

    def test_foreign_origin_and_host_rejected(self):
        status,_=self.request('/api/notes','POST','{}',{'Origin':'https://untrusted.example'})
        self.assertEqual(status,403)
        status,_=self.request('/api/catalog',headers={'Host':'untrusted.example'})
        self.assertEqual(status,403)

    def test_pdf_validation_dedup_and_preview(self):
        status,_=self.request('/api/upload','POST',b'not a PDF');self.assertEqual(status,400)
        # Deliberately minimal unparseable PDF: extraction failure must not claim a successful review.
        pdf=b'%PDF-1.4\n%%EOF'
        status,s=self.request('/api/upload','POST',pdf,{'X-Filename':'../../paper.pdf'})
        self.assertEqual(status,200);self.assertEqual(s['inbox'][0]['name'],'paper.pdf')
        self.assertEqual(s['inbox'][0]['status'],'Awaiting review')
        status,s=self.request('/api/upload','POST',pdf);self.assertEqual(len(s['inbox']),1)
        status,raw=self.request('/api/pdf?id='+s['inbox'][0]['id'])
        self.assertEqual(status,200);self.assertEqual(raw,pdf)

    def test_saved_result_and_static_assets(self):
        path='analysis/outputs/codex_vrp_monthly_proxy_20261029/primary_endpoints/endpoint_metrics.csv'
        status,x=self.request('/api/result?path='+path);self.assertEqual(status,200)
        self.assertEqual(x['rows'][0]['name'],'P');self.assertFalse(x['truncated'])
        for path in ['/','/style.css','/app.js']:
            status,_=self.request(path);self.assertEqual(status,200)

    def test_invalid_note_shape_and_oversized_body(self):
        status,_=self.request('/api/notes','POST','[]');self.assertEqual(status,400)
        status,_=self.request('/api/notes','POST',json.dumps({'revision':0,'notes':[{'body':3}]}))
        self.assertEqual(status,400)
        status,_=self.request('/api/upload','POST',headers={'Content-Length':str(21*1024*1024)})
        self.assertEqual(status,400)


if __name__=='__main__':unittest.main()
