from pathlib import Path
import json,re,hashlib,datetime,collections,xml.etree.ElementTree as ET,shutil
from html.parser import HTMLParser
from html import unescape
def plaintext(t):return re.sub(r"\s+"," ",unescape(re.sub(r"<[^>]*>"," ",t))).strip()
W=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
units=[json.loads(l) for l in (W/'units.jsonl').read_text().splitlines()]; ids=['art-9:'+n for n in ['34','35','36','36a']]+['art-10:'+str(n) for n in range(1,17)]
raw=D/'selected.xml';root=ET.parse(raw).getroot();previous=ET.parse(W/'sources/preflight/previous-official.xml').getroot()
assert sha(raw)==sha(W/'sources/intake-official.xml')
# Independent inventory from the official XML hierarchy, with the conditional
# article8:36c branches identified by the official separator, not the parser IDs.
expected=[];annexes=[]
def inventory(e,annex=None):
 if e.tag in ['aanhef','wetsluiting']:expected.append(e.tag);return
 if e.tag=='bijlage':
  annex=e.findtext('kop/nr'); children=list(e.iter('artikel'))
  childids=['bijlage-'+annex+'-art-'+x.findtext('kop/nr') for x in children]
  annexes.append(dict(annex=annex,expected_child_ids=childids,evidence_path=str(raw.relative_to(W)),evidence_sha256=sha(raw),disposition='Numbered articles individually retained' if children else 'Unnumbered operative list retained whole as bijlage-'+annex))
  if not children:expected.append('bijlage-'+annex);return
 if e.tag=='artikel':
  n=e.findtext('kop/nr');uid=('bijlage-'+annex+'-art-' if annex else 'art-')+n
  if n=='8:36c' and any('Voor overige gevallen' in ''.join(x.itertext()) for x in e.findall('al')):expected.extend([uid+'--digitaal',uid+'--overig'])
  else:expected.append(uid)
  return
 for child in e:inventory(child,annex)
inventory(root)
parsed=[u['id'] for u in units];missing=sorted(set(expected)-set(parsed));extra=sorted(set(parsed)-set(expected));dups=[k for k,v in collections.Counter(parsed).items() if v>1]
assert not missing and not extra and not dups and len(expected)==len(parsed)
coverage=dict(official_source=dict(url='https://wetten.overheid.nl/BWBR0005537/2026-08-15',local_raw_evidence_path=str(raw.relative_to(W)),sha256=sha(raw)),expected_ids=expected,parsed_ids=parsed,annex_disposition=annexes,missing=missing,extra=extra,duplicates=dups,ok=True)
write(D/'coverage-recheck.json',coverage)
# Parse history independently; scheduled versions are not effective versions.
rows=[]
for tr in re.findall(r'<tr\b[^>]*>(.*?)</tr>',(D/'history.html').read_text(),re.S):
 t=plaintext(tr);m=re.match(r'(\d{2})-(\d{2})-(\d{4})\b',t)
 if m:rows.append(dict(date=f'{m[3]}-{m[2]}-{m[1]}',text=t))
write(D/'history-rows.json',rows)
assert rows
past=sorted(set(r['date'] for r in rows if r['date']<='2026-10-21'));future=sorted(set(r['date'] for r in rows if r['date']>'2026-10-21'))
assert past[-1]=='2026-08-15'
plain=plaintext((D/'current.html').read_text())
m=re.search(r'Geraadpleegd op.{0,160}',plain);effective=re.search(r'Geldend van.{0,80}',plain)
# Compare historical and selected articles using raw element text, not reconstructed prose.
def articles(r):return {e.findtext('kop/nr'):e for e in r.iter('artikel') if ':' in (e.findtext('kop/nr') or '')}
a=articles(root);b=articles(previous);changed=[];records=[]
for uid in ids:
 n=uid[4:];cur=a[n];old=b.get(n);eq=old is not None and re.sub(r'\s+',' ',''.join(cur.itertext()))==re.sub(r'\s+',' ',''.join(old.itertext()))
 if not eq:changed.append(uid)
 records.append(dict(id=uid,current_xml_label=cur.get('label-id'),effective_from=cur.get('inwerking'),same_as_previous=eq,operative_text=next(u['text'] for u in units if u['id']==uid)))
write(D/'assigned-source-records.json',records)
pre=dict(complete=True,scope='Source/parser preflight for the assigned twenty units only; no whole-book content review',decisive_date=json.loads((W/'meta.json').read_text())['decisive_date'],batch_authoring_date='2026-10-21',official_url='https://wetten.overheid.nl/BWBR0005537/2026-08-15',verified_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),version_evidence=dict(effective_statement=effective.group() if effective else None,consultation=m.group() if m else None,latest_effective_on_decisive_date=max(x['date'] for x in rows if x['date']<='2026-10-19'),latest_effective_on_recheck=past[-1],next_scheduled_version=future[0],history=str((D/'history-rows.json').relative_to(W)),selected_xml_sha256=sha(raw),identical_to_canonical=True,http_results=str((D/'verification.json').relative_to(W))),historical_versions_checked=dict(previous='2026-08-01_0',previous_xml='sources/preflight/previous-official.xml',previous_sha256=sha(W/'sources/preflight/previous-official.xml'),selected='2026-08-15_0',assigned_changed_ids=changed,versions_concatenated=False,assigned_repealed_slots=[]),annexes_checked=annexes,coverage=dict(expected_units=len(expected),parsed_units=len(parsed),missing=missing,extra=extra,duplicates=dups,aanhef_and_wetsluiting='both present',evidence=str((D/'coverage-recheck.json').relative_to(W))),unresolved_blockers=[],limitations=['Fresh first landing/history requests failed; dated official URL and history query retry succeeded and bodies were validated.','Selective case research, no independent second content review.'])
write(D/'preflight-result.json',pre)
# Preserve national corpus corroboration of the complete selected judgment.
local=Path('/Volumes/LaCie/law-intake/eu/nl/rechtspraak/rvs/ecli-nl-rvs-2025-5425.md');shutil.copyfile(local,D/'ECLI-NL-RVS-2025-5425-local.md')
write(D/'case-search-log.json',dict(date='2026-10-21',web_queries=['site.raadvanstate.nl "10:3" "mandaat" "bezwaar" uitspraak','site.rechtspraak.nl "9:36a" ombudsman'],local_corpus_root='/Volumes/LaCie/law-intake/eu/nl/rechtspraak',selected='ECLI:NL:RVS:2025:5425',local_path=str(local),local_sha256=sha(local),read_also=['ECLI:NL:RVS:2022:3004'],primary_full_text_read=True,supported_units=['art-10:3'],selected_paragraphs=['5','5.1','5.2','5.3'],remaining_units='No separately sufficiently relevant verified judicial full text selected; statutory analysis only.',limits=['Selective research; not exhaustive','Historical Wabo facts not treated as current environmental law','No full subsequent-treatment search']))
print(json.dumps(dict(expected=len(expected),parsed=len(parsed),changed=changed,effective=pre['version_evidence']),ensure_ascii=False,indent=2))
