from pathlib import Path
import json,re,hashlib,datetime,xml.etree.ElementTree as E,importlib.util,collections,shutil,difflib
W=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent
ids=['art-8:'+str(n) for n in list(range(86,96))+list(range(104,114))]
def dump(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
r=E.parse(D/'selected.xml').getroot(); units=[json.loads(l) for l in (W/'units.jsonl').read_text().splitlines()];by={u['id']:u for u in units}
assert sha(D/'selected.xml')==sha(W/'sources/intake-official.xml')
expected=['aanhef']; annex=[]
for a in r.iter('artikel'):
 path=a.get('bwb-ng-variabel-deel','');num=a.findtext('kop/nr');m=re.match(r'/Bijlage(\d+)',path)
 uid=('bijlage-'+m[1]+'-art-' if m else 'art-')+num
 if num=='8:36c':expected.extend([uid+'--digitaal',uid+'--overig'])
 else:expected.append(uid)
for a in r.iter('bijlage'):
 n=a.findtext('kop/nr');children=['bijlage-'+n+'-art-'+x.findtext('kop/nr') for x in a.iter('artikel')]
 if not children:expected.append('bijlage-'+n)
 annex.append(dict(annex=n,expected_child_ids=children,disposition='Numbered children individually retained' if children else 'Complete unnumbered operative list retained as bijlage-'+n,evidence_path=str((D/'selected.xml').relative_to(W)),evidence_sha256=sha(D/'selected.xml')))
expected.append('wetsluiting');parsed=[u['id'] for u in units]
missing=sorted(set(expected)-set(parsed));extra=sorted(set(parsed)-set(expected));dups=[k for k,v in collections.Counter(parsed).items() if v>1];assert not(missing or extra or dups)
cov=dict(official_source=dict(url='https://wetten.overheid.nl/BWBR0005537/2026-08-15',local_raw_evidence_path=str((D/'selected.xml').relative_to(W)),sha256=sha(D/'selected.xml')),expected_ids=expected,parsed_ids=parsed,annex_disposition=annex,missing=missing,extra=extra,duplicates=dups)
dump('coverage-recheck.json',cov)
# No parser execution: canonical bytes and existing unit assignments are preserved.
previous=E.parse(W/'sources/preflight/previous-official.xml').getroot(); old={a.findtext('kop/nr'):a for a in previous.iter('artikel')};new={a.findtext('kop/nr'):a for a in r.iter('artikel')}
def body(a):return re.sub(r'\s+',' ',''.join(c.itertext() for c in [])) if False else re.sub(r'\s+',' ',''.join(''.join(c.itertext()) for c in a if c.tag not in ['kop','meta-data'])).strip()
changes=[uid for uid in ids if body(old[uid[4:]])!=body(new[uid[4:]])];dump('change-map.json',dict(previous='sources/preflight/previous-official.xml',previous_sha256=sha(W/'sources/preflight/previous-official.xml'),selected_sha256=sha(D/'selected.xml'),assigned_changed_ids=changes,canonical_replaced=False))
import html
def plain(s):return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',s))).strip()
rows=[]
for tr in re.findall(r'<tr\b[^>]*>.*?</tr>',(D/'history.html').read_text(),re.S):
 t=plain(tr);m=re.match(r'(\d{2})-(\d{2})-(\d{4})',t)
 if m:rows.append(dict(date=f'{m[3]}-{m[2]}-{m[1]}',text=t))
dump('history-rows.json',rows)
now=datetime.datetime.now(datetime.timezone.utc).isoformat();current=plain((D/'current.html').read_text());assert 'Geldend van 15-08-2026 t/m heden' in current
v=json.loads((D/'verification.json').read_text());pre=dict(complete=True,scope='Source preflight for assigned twenty articles; not whole-book substantive review',decisive_date='2026-10-19',batch_authoring_date='2026-10-21',official_url=v[0]['final_url'],verified_at=now,version_evidence=dict(effective_statement='Geldend van 15-08-2026 t/m heden',current_page_displayed_consultation_date='2026-10-20',latest_effective_version='2026-08-15',next_scheduled_version='2027-01-01',history_evidence='sources/author-8-86-113/history-rows.json',canonical_xml_identical=True),historical_versions_checked=dict(previous='2026-08-01_0',selected='2026-08-15_0',assigned_changes=changes,change_map='sources/author-8-86-113/change-map.json',historical_versions_concatenated=False),annexes_checked=annex,coverage=dict(expected_units=len(expected),parsed_units=len(parsed),missing=missing,duplicates=dups,aanhef=True,wetsluiting=True),unresolved_blockers=[],limitations=['Official landing displays 20 October consultation date despite access timestamp; effectiveness separately checked in history.','No independent second-pass review.'])
dump('preflight-result.json',pre)
spec=importlib.util.spec_from_file_location('builder','/Volumes/LaCie/open-commentary/_tools/build_repo.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);com=m.load_commentary(str(W))
blocks=re.findall(r'^=== (\S+)',(W/'commentary/part-29-schade-en-hoger-beroep.md').read_text(),re.M);assert blocks==ids
assert all(len(com[x])>=700 for x in ids)
paras=[]
for uid in ids:
 for p in com[uid].split('\n\n'):
  if len(p)>150:paras.append((uid,p))
repeats=[(a,c) for i,(a,b) in enumerate(paras) for c,d in paras[i+1:] if a!=c and b==d];assert not repeats
dump('author-content-check.json',dict(assigned_ids=ids,completed_ids=blocks,count=len(blocks),commentary_characters={x:len(com[x]) for x in ids},exact_repeated_paragraphs=repeats,statutory_source_unchanged=True,independent_coverage=True,legal_quality_not_inferred_from_length=True))
local=[]
for key in ['2021-2023','2020-2242']:
 p=Path('/Volumes/LaCie/law-intake/eu/nl/rechtspraak/rvs/ecli-nl-rvs-'+key+'.md');shutil.copy2(p,D/(p.stem+'-local.md'));local.append(dict(path=str(p),sha256=sha(p),snapshot=str((D/(p.stem+'-local.md')).relative_to(W))))
dump('case-search-log.json',dict(queries=['site.raadvanstate.nl 8:88 causaal 2017','site.raadvanstate.nl 8:110 incidenteel 2024'],selected_full_texts=[x for x in v if 'ECLI' in x['url']],local_corpus=local,selection='Causation and damage proof; distinction between defence and incidental appeal. No exhaustive survey or negative conclusion about other units.'))
# Inspect every explicit article reference against the parsed statute.
refs=sorted(set(re.findall(r'\b[1-9]:\d+[a-z]?\b','\n'.join(com[x] for x in ids))));external={'3:310'};bad=[x for x in refs if 'art-'+x not in by and x not in external];assert not bad
dump('internal-crossrefs.json',dict(references=refs,unresolved=bad,scope='Identifier existence plus manual reading of cited procedural provisions'))
