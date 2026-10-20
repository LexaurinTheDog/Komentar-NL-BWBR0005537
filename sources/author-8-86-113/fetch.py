from pathlib import Path
import urllib.request,json,hashlib,datetime,xml.etree.ElementTree as E
p=Path(__file__).resolve().parent
urls={'current.html':'https://wetten.overheid.nl/BWBR0005537','history.html':'https://wetten.overheid.nl/BWBR0005537/2026-08-15/0/informatie','selected.xml':'https://repository.officiele-overheidspublicaties.nl/bwb/BWBR0005537/2026-08-15_0/xml/BWBR0005537_2026-08-15_0.xml','ECLI-NL-RVS-2021-2023.xml':'https://data.rechtspraak.nl/uitspraken/content?id=ECLI:NL:RVS:2021:2023','ECLI-NL-RVS-2020-2242.xml':'https://data.rechtspraak.nl/uitspraken/content?id=ECLI:NL:RVS:2020:2242'}
a=[]
for name,url in urls.items():
 t=datetime.datetime.now(datetime.timezone.utc).isoformat()
 with urllib.request.urlopen(url,timeout=90) as r:
  b=r.read(); d=dict(url=url,accessed_at=t,http_status=r.status,final_url=r.url,content_type=r.headers.get('Content-Type'),path=str((p/name).relative_to(p.parent.parent)),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
 if name.endswith('.xml'):
  root=E.fromstring(b);d['xml_root']=root.tag;assert root.tag in ['toestand','open-rechtspraak'];
  if 'ECLI' in name:(p/name.replace('.xml','.txt')).write_text('\n'.join(''.join(e.itertext()) for e in root.iter() if e.tag.endswith('}para')),encoding='utf8')
 else: assert b'BWBR0005537' in b and b'<html' in b
 (p/name).write_bytes(b);a.append(d)
(p/'verification.json').write_text(json.dumps(a,indent=2))
