"""Fetch the public snapshot used by the factor screen; reject changed/partial files."""
import hashlib,json,urllib.request,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
META=ROOT/'agents/codex/inputs/factor_beta_sessions/source_manifest.json'
DATA=ROOT/'scratch_data/factor_sessions'

def main():
    DATA.mkdir(parents=True,exist_ok=True)
    for a in json.loads(META.read_text())['assets']:
        p=DATA/a['name'];expected=a['digest'].removeprefix('sha256:')
        valid=lambda: p.exists() and p.stat().st_size==a['size'] and hashlib.sha256(p.read_bytes()).hexdigest()==expected
        if not valid():
            temp=p.with_suffix(p.suffix+'.download')
            with urllib.request.urlopen(a['url'],timeout=120) as r,temp.open('wb') as f:
                while b:=r.read(1024*1024):f.write(b)
            if temp.stat().st_size!=a['size'] or hashlib.sha256(temp.read_bytes()).hexdigest()!=expected:
                raise ValueError('Snapshot changed or partial; do not silently replace preregistered input: '+a['name'])
            os.replace(temp,p)
        assert valid()
        print(a['name'],'verified',flush=True)

if __name__=='__main__':main()
