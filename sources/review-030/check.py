from pathlib import Path
import urllib.request,hashlib,json,datetime,concurrent.futures,xml.etree.ElementTree as E
W=Path.cwd();D=W/'sources/review-030'
urls={'current.html':'https://wetten.overheid.nl/BWBR0005537','history.html':'https://wetten.overheid.nl/BWBR0005537/2026-08-15/0/informatie','selected.xml':'https://repository.officiele-overheidspublicaties.nl/bwb/BWBR0005537/2026-08-15_0/xml/BWBR0005537_2026-08-15_0.xml'}
for c in ['CRVB:2025:1470','CRVB:2024:2006','HR:2021:1231']:urls[c.replace(':','-')+'.xml']='https://data.rechtspraak.nl/uitspraken/content?id=ECLI:NL:'+c
def fetch(kv):
 name,url=kv;r={'url':url,'accessed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'path':str((D/name).relative_to(W))}
 try:
  with urllib.request.urlopen(url,timeout=35) as f:b=f.read();r.update(http_status=f.status,final_url=f.url,content_type=f.headers.get('Content-Type'))
  (D/name).write_bytes(b);r['sha256']=hashlib.sha256(b).hexdigest();r['accepted_format']=(E.fromstring(b).tag in ['toestand','open-rechtspraak']) if name.endswith('.xml') else b'BWBR0005537' in b and b'<html' in b.lower()
 except Exception as e:r.update(http_status=None,accepted_format=False,error=str(e))
 return r
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as x:r=list(x.map(fetch,urls.items()))
(D/'verification.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
