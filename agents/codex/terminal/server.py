"""Beginning Research Terminal. Standard-library only; localhost and research files only."""
from __future__ import annotations
import argparse
import csv
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import threading
import webbrowser
from urllib.parse import unquote, urlsplit, parse_qs

ROOT = Path(__file__).resolve().parents[3]
STATIC = Path(__file__).parent / 'static'
RUNTIME = ROOT / 'agents/codex/runtime/terminal'
LOCK = threading.Lock()
DOC_DIRS = ('agents/codex/results', 'agents/codex/evidence', 'agents/codex/plans')
SINGLE = ('TODO.md', 'agents/codex/EXECUTION_REFERENCES.md', 'agents/codex/RESEARCH_CONTROLS.md')
CSV_NAMES = {'endpoint_metrics.csv', 'personal.csv', 'funded.csv', 'evaluations.csv'}


def relative(p): return str(p.relative_to(ROOT)).replace(os.sep, '/')


def document_paths():
    return [p for d in DOC_DIRS for p in (ROOT/d).glob('*.md')] + [ROOT/p for p in SINGLE if (ROOT/p).exists()]


def resolve_document(path):
    resolved = (ROOT/path).resolve()
    if resolved not in [p.resolve() for p in document_paths()]:
        raise ValueError('Document is outside the research library')
    return resolved


def result_paths():
    return sorted(p for p in (ROOT/'analysis/outputs').glob('codex_*/**/*.csv')
                  if p.name in CSV_NAMES and p.stat().st_size < 2_000_000)


def state():
    p=RUNTIME/'state.json'
    return json.loads(p.read_text()) if p.exists() else {'revision':0,'notes':[],'inbox':[]}


def save(value):
    RUNTIME.mkdir(parents=True,exist_ok=True)
    temp=RUNTIME/'state.tmp'
    temp.write_text(json.dumps(value,indent=2))
    temp.replace(RUNTIME/'state.json')


def catalog():
    docs=[]
    for p in document_paths():
        content=p.read_text(errors='replace')
        lines=content.splitlines()
        title=next((s.lstrip('# ').strip() for s in lines if s.startswith('# ')),p.stem)
        summary=content.split('Summary:',1)[1].split('\n\n',1)[0].strip() if 'Summary:' in content else ''
        status=next((s for s in ['REJECT','DON’T TEST',"DON'T TEST",'NEEDS DATA','CANDIDATE','WATCH','CLOSED'] if s in title.upper()),'REFERENCE')
        kind=p.parent.name if p.name not in ['TODO.md','EXECUTION_REFERENCES.md','RESEARCH_CONTROLS.md'] else 'reference'
        docs.append(dict(path=relative(p),title=title,summary=summary,kind=kind,status=status,
                         updated=p.stat().st_mtime,search=content.lower()))
    try: commit=subprocess.check_output(['git','rev-parse','--short','HEAD'],cwd=ROOT,text=True).strip()
    except (OSError,subprocess.CalledProcessError): commit='unavailable'
    return dict(documents=docs,commit=commit,branch='codex/work',
                results=[dict(path=relative(p),name=relative(p).replace('analysis/outputs/','')) for p in result_paths()],
                queue=(ROOT/'TODO.md').read_text().split('## Promising strategies awaiting verification',1)[-1].split('\n## Later',1)[0],
                execution=(ROOT/'agents/codex/EXECUTION_REFERENCES.md').read_text())


class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass

    def respond(self,value,status=200,ctype='application/json; charset=utf-8'):
        data=json.dumps(value).encode() if ctype.startswith('application/json') else value
        self.send_response(status)
        self.send_header('Content-Type',ctype)
        self.send_header('Content-Length',str(len(data)))
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        ancestor="'self'" if ctype=='application/pdf' else "'none'"
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; frame-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors "+ancestor)
        self.end_headers();self.wfile.write(data)

    def trusted(self):
        hosts={f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}'}
        origin=self.headers.get('Origin')
        return self.headers.get('Host') in hosts and (not origin or origin in {'http://'+h for h in hosts})

    def do_GET(self):
        if not self.trusted(): return self.respond({'error':'Local origin required'},403)
        u=urlsplit(self.path);q=parse_qs(u.query)
        try:
            if u.path=='/api/catalog': return self.respond(catalog())
            if u.path=='/api/state': return self.respond(state())
            if u.path=='/api/document':
                p=resolve_document(q.get('path',[''])[0]);return self.respond({'content':p.read_text()})
            if u.path=='/api/result':
                p=(ROOT/q.get('path',[''])[0]).resolve()
                if p not in [v.resolve() for v in result_paths()]:raise ValueError('Unknown result')
                with p.open() as f: rows=list(csv.DictReader(f))
                return self.respond({'rows':rows[:5000],'total':len(rows),'truncated':len(rows)>5000})
            if u.path=='/api/pdf':
                file_id=q.get('id',[''])[0]
                item=next((x for x in state()['inbox'] if x['id']==file_id),None)
                if not item: raise ValueError('Unknown PDF')
                return self.respond((RUNTIME/(file_id+'.pdf')).read_bytes(),ctype='application/pdf')
            paths={'/':'index.html','/app.js':'app.js','/style.css':'style.css'}
            if u.path not in paths:return self.respond({'error':'Not found'},404)
            p=STATIC/paths[u.path]
            mime={'html':'text/html','js':'text/javascript','css':'text/css'}[p.suffix[1:]]
            return self.respond(p.read_bytes(),ctype=mime+'; charset=utf-8')
        except (ValueError,OSError,KeyError) as e: return self.respond({'error':str(e)},400)

    def do_POST(self):
        if not self.trusted():return self.respond({'error':'Local origin required'},403)
        try:
            size=int(self.headers.get('Content-Length','0'))
            if not 0<size<=20*1024*1024:raise ValueError('Choose a file or request under 20 MB')
            body=self.rfile.read(size)
            with LOCK:
                s=state()
                if self.path=='/api/upload':
                    if not body.startswith(b'%PDF-'):raise ValueError('A PDF file is required')
                    digest=hashlib.sha256(body).hexdigest()
                    if any(x['id']==digest for x in s['inbox']):return self.respond(s)
                    name=Path(unquote(self.headers.get('X-Filename','paper.pdf')).replace('\\','/')).name[:180]
                    RUNTIME.mkdir(parents=True,exist_ok=True)
                    path=RUNTIME/(digest+'.pdf');path.write_bytes(body)
                    try:
                        text=subprocess.run(['pdftotext','-layout',str(path),'-'],capture_output=True,timeout=20,check=True).stdout.decode(errors='replace')
                        extraction='Extracted' if text.strip() else 'Scanned PDF · no text'
                    except (OSError,subprocess.SubprocessError):text='';extraction='Text extraction unavailable'
                    s['inbox'].insert(0,dict(id=digest,name=name,size=size,text=text[:100000],extraction=extraction,status='Awaiting review'))
                elif self.path=='/api/notes':
                    payload=json.loads(body)
                    if payload.get('revision')!=s['revision']:return self.respond({'error':'Notes changed in another tab. Refresh before saving.'},409)
                    notes=payload.get('notes')
                    if not isinstance(notes,list) or len(notes)>300:raise ValueError('Invalid notes')
                    for n in notes:
                        if set(n)!={'id','title','body','source'} or not all(isinstance(v,str) and len(v)<=20000 for v in n.values()):raise ValueError('Invalid note fields')
                    s['notes']=notes
                else:return self.respond({'error':'Unknown action'},404)
                s['revision']+=1;save(s);return self.respond(s)
        except (ValueError,OSError,KeyError,TypeError,AttributeError) as e:return self.respond({'error':str(e)},400)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8765);parser.add_argument('--open',action='store_true')
    args=parser.parse_args()
    branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()
    if branch!='codex/work':raise SystemExit('Open a research checkout on codex/work before starting the terminal.')
    server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    print(f'Beginning Research Terminal: http://127.0.0.1:{server.server_port}',flush=True)
    if args.open: threading.Timer(.5,lambda:webbrowser.open(f'http://127.0.0.1:{server.server_port}')).start()
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
