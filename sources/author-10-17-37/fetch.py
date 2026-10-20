from pathlib import Path
import requests,hashlib,json,datetime,xml.etree.ElementTree as ET
D=Path(__file__).resolve().parent
items=[('selected.xml','https://repository.officiele-overheidspublicaties.nl/bwb/BWBR0005537/2026-08-15_0/xml/BWBR0005537_2026-08-15_0.xml'),('current.html','https://wetten.overheid.nl/BWBR0005537/2026-08-15'),('history.html','https://wetten.overheid.nl/BWBR0005537/2026-08-15/0/informatie?view=changes'),('ECLI-NL-RVS-2008-BC2506.xml','https://data.rechtspraak.nl/uitspraken/content?id=ECLI:NL:RVS:2008:BC2506')]
rows=[]
for name,url in items:
 row={'url':url,'accessed_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  r=requests.get(url,timeout=45);row.update(http_status=r.status_code,final_url=r.url);r.raise_for_status()
  if name.endswith('.xml'):ET.fromstring(r.content)
  else:assert b'BWBR0005537' in r.content and b'Geldend' in r.content
  (D/name).write_bytes(r.content);row.update(path=str((D/name).relative_to(D.parents[1])),sha256=hashlib.sha256(r.content).hexdigest(),bytes=len(r.content),accepted_format=True)
 except Exception as e:row.update(error=str(e),accepted_format=False)
 rows.append(row)
(D/'verification.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
p=D/'ECLI-NL-RVS-2008-BC2506.xml'
if p.exists():
 root=ET.parse(p).getroot(); ns={'r':'http://www.rechtspraak.nl/schema/rechtspraak-1.0'}
 (D/'ECLI-NL-RVS-2008-BC2506.txt').write_text('\n'.join(''.join(e.itertext()) for e in root.findall('.//r:uitspraak',ns)))
print(json.dumps(rows,indent=2))
