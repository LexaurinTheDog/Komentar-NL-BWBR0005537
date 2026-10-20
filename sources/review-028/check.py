from pathlib import Path
import urllib.request,json,hashlib,datetime,xml.etree.ElementTree as E,re
W=Path(__file__).resolve().parents[2]; D=Path(__file__).parent
records=[]
urls=[('current.html','https://wetten.overheid.nl/BWBR0005537'),('history.html','https://wetten.overheid.nl/BWBR0005537/2026-08-15/0/informatie'),('selected.xml','https://repository.officiele-overheidspublicaties.nl/bwb/BWBR0005537/2026-08-15_0/xml/BWBR0005537_2026-08-15_0.xml'),('case.xml','https://data.rechtspraak.nl/uitspraken/content?id=ECLI:NL:RVS:2008:BC2506')]
for name,url in urls:
 with urllib.request.urlopen(url,timeout=50) as r:
  b=r.read(); rec=dict(url=url,final_url=r.url,http_status=r.status,accessed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),content_type=r.headers.get('Content-Type'),path=str((D/name).relative_to(W)),sha256=hashlib.sha256(b).hexdigest())
 if name.endswith('.xml'):rec['xml_root']=E.fromstring(b).tag; assert rec['xml_root'] in ['toestand','open-rechtspraak']
 else:assert b'<html' in b.lower() and b'BWBR0005537' in b
 rec['accepted_format']=True; (D/name).write_bytes(b);records.append(rec)
(D/'verification.json').write_text(json.dumps(records,indent=2))
root=E.parse(D/'selected.xml').getroot(); us=[json.loads(l) for l in (W/'units.jsonl').read_text().splitlines()]; ids=['art-10:'+str(n) for n in range(17,38) if n!=24]
nodes={ 'art-'+a.findtext('kop/nr'):a for a in root.iter('artikel') if '/Bijlage' not in a.get('bwb-ng-variabel-deel','')}
for uid in ids:
 a=nodes[uid]; (D/(uid.replace(':','-')+'.xml')).write_text(E.tostring(a,encoding='unicode'))
prev=E.parse(W/'sources/preflight/previous-official.xml').getroot(); old={'art-'+a.findtext('kop/nr'):a for a in prev.iter('artikel') if '/Bijlage' not in a.get('bwb-ng-variabel-deel','')}
def norm(a):return re.sub(r'\s+',' ',''.join(a.itertext())).strip()
changes=[i for i in ids if norm(nodes[i])!=norm(old[i])]
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
parsed=[u['id'] for u in us]; report=dict(official_source={'url':urls[2][1],'local_raw_evidence_path':'sources/review-028/selected.xml','sha256':records[2]['sha256']},expected_ids=expected,parsed_ids=parsed,annex_disposition=annex,missing_ids=sorted(set(expected)-set(parsed)),extra_ids=sorted(set(parsed)-set(expected)),duplicate_ids=sorted({x for x in parsed if parsed.count(x)>1}))
report['ok']=not any(report[k] for k in ['missing_ids','extra_ids','duplicate_ids']);(D/'coverage-recheck.json').write_text(json.dumps(report,indent=2))
print(json.dumps(records,indent=2));print('coverage',report['ok'],len(expected),'changes',changes)
