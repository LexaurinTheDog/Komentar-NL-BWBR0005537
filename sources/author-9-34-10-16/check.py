from pathlib import Path
import requests,datetime,hashlib,json,xml.etree.ElementTree as E
W=Path(__file__).resolve().parents[2]; D=Path(__file__).resolve().parent
items=[('current.html','https://wetten.overheid.nl/BWBR0005537'),('history.html','https://wetten.overheid.nl/BWBR0005537/2026-08-15/0/informatie'),('selected.xml','https://repository.officiele-overheidspublicaties.nl/bwb/BWBR0005537/2026-08-15_0/xml/BWBR0005537_2026-08-15_0.xml'),('ECLI-NL-RVS-2025-5425.xml','https://data.rechtspraak.nl/uitspraken/content?id=ECLI:NL:RVS:2025:5425')]
session=requests.Session();session.trust_env=False
records=[]
for name,url in items:
 
 try:r=session.get(url,timeout=25)
 except requests.RequestException as e:
  records.append(dict(url=url,error=str(e),accessed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),accepted_format=False));continue
 p=D/name;p.write_bytes(r.content)
 ok=r.status_code==200
 if name.endswith('.xml'):
  try: root=E.fromstring(r.content);ok=ok and (root.tag=='toestand' if name=='selected.xml' else root.tag.endswith('open-rechtspraak'))
  except E.ParseError:ok=False
 else:ok=ok and b'BWBR0005537' in r.content
 records.append(dict(url=url,accessed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),http_status=r.status_code,final_url=r.url,path=str(p.relative_to(W)),sha256=hashlib.sha256(r.content).hexdigest(),bytes=len(r.content),accepted_format=ok))
 if name.startswith('ECLI') and ok:
  (D/name.replace('.xml','.txt')).write_text('\n'.join(''.join(e.itertext()) for e in root.iter() if e.tag.endswith('}uitspraak')),encoding='utf-8')
(D/'verification.json').write_text(json.dumps(records,indent=2))
print(json.dumps(records,indent=2))
