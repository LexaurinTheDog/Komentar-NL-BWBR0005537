from pathlib import Path
import urllib.request,json,hashlib,datetime,xml.etree.ElementTree as E,re
W=Path(__file__).resolve().parents[2]; D=Path(__file__).parent
records=[]
urls=[('current.html','https://wetten.overheid.nl/BWBR0005537'),('history.html','https://wetten.overheid.nl/BWBR0005537/2026-08-15/0/informatie'),('selected.xml','https://repository.officiele-overheidspublicaties.nl/bwb/BWBR0005537/2026-08-15_0/xml/BWBR0005537_2026-08-15_0.xml'),('case.xml','https://data.rechtspraak.nl/uitspraken/content?id=ECLI:NL:CRVB:2013:2659')]
for name,url in urls:
 with urllib.request.urlopen(url,timeout=50) as r:
  b=r.read(); rec=dict(url=url,final_url=r.url,http_status=r.status,accessed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),content_type=r.headers.get('Content-Type'),path=str((D/name).relative_to(W)),sha256=hashlib.sha256(b).hexdigest())
 if name.endswith('.xml'):rec['xml_root']=E.fromstring(b).tag; assert rec['xml_root'] in ['toestand','open-rechtspraak']
 else:assert b'<html' in b.lower() and b'BWBR0005537' in b
 rec['accepted_format']=True; (D/name).write_bytes(b);records.append(rec)
(D/'verification.json').write_text(json.dumps(records,indent=2))
root=E.parse(D/'selected.xml').getroot(); us=[json.loads(l) for l in (W/'units.jsonl').read_text().splitlines()]; ids=['art-10:'+str(n) for n in range(38,46)]+['art-11:'+str(n) for n in range(1,5)]+['wetsluiting','bijlage-1']+['bijlage-2-art-'+str(n) for n in range(1,7)]
nodes={ 'art-'+a.findtext('kop/nr'):a for a in root.iter('artikel') if '/Bijlage' not in a.get('bwb-ng-variabel-deel','')}
paths={a.get('bwb-ng-variabel-deel'):a for a in root.iter() if a.tag in ['artikel','bijlage']}
prev=E.parse(W/'sources/preflight/previous-official.xml').getroot();oldpaths={a.get('bwb-ng-variabel-deel'):a for a in prev.iter() if a.tag in ['artikel','bijlage']}
ns={};exec((W/'_parse.py').read_text().split('units=[];chapter_specs=[]')[0].replace('W=Path(__file__).resolve().parent','W=Path('+repr(str(W))+')'),ns)
changes=[];records=[]
for u in us:
 if u['id'] not in ids:continue
 a=root.find('.//wetsluiting') if u['id']=='wetsluiting' else paths[u['official_path']]
 old=prev.find('.//wetsluiting') if u['id']=='wetsluiting' else oldpaths[u['official_path']]
 t='\n\n'.join(ns['blocks'](a));assert t==u['text'],u['id']
 if t!='\n\n'.join(ns['blocks'](old)):changes.append(u['id'])
 (D/(u['id'].replace(':','-')+'.xml')).write_text(E.tostring(a,encoding='unicode'))
 records.append(dict(id=u['id'],text=t,text_agreement=True))
(D/'assigned-source-records.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
(D/'history-comparison.json').write_text(json.dumps({'previous':'2026-08-01_0','assigned_changed_ids':changes},indent=2))
case=E.parse(D/'case.xml');(D/'case.txt').write_text('\n'.join(''.join(a.itertext()) for a in case.iter() if a.tag.endswith('para')))
# Independent structural enumeration, without using parser's units as expected inventory.
expected=[];annex=[]
for node in root.iter():
 if node.tag in ['aanhef','wetsluiting']:expected.append(node.tag)
 if node.tag=='artikel':
  path=node.get('bwb-ng-variabel-deel',''); n=node.findtext('kop/nr'); m=re.match('/Bijlage(\d+)',path); uid=('bijlage-'+m[1]+'-art-' if m else 'art-')+n
  expected.extend([uid+'--digitaal',uid+'--overig'] if uid=='art-8:36c' else [uid])
 if node.tag=='bijlage':
  n=node.findtext('kop/nr');children=['bijlage-'+n+'-art-'+a.findtext('kop/nr') for a in node.iter('artikel')]
  if not children:expected.append('bijlage-'+n)
  annex.append(dict(annex=n,expected_child_ids=children,disposition='Volledige ongenummerde lijst behouden' if not children else 'Alle genummerde artikelen afzonderlijk behouden'))
parsed=[u['id'] for u in us]; report=dict(official_source={'url':urls[2][1],'local_raw_evidence_path':'sources/review-029/selected.xml','sha256':hashlib.sha256((D/'selected.xml').read_bytes()).hexdigest()},expected_ids=expected,parsed_ids=parsed,annex_disposition=annex,missing_ids=sorted(set(expected)-set(parsed)),extra_ids=sorted(set(parsed)-set(expected)),duplicate_ids=sorted({x for x in parsed if parsed.count(x)>1}))
report['ok']=not any(report[k] for k in ['missing_ids','extra_ids','duplicate_ids']);(D/'coverage-recheck.json').write_text(json.dumps(report,indent=2))
print(json.dumps(records,indent=2));print('coverage',report['ok'],len(expected),'changes',changes)
