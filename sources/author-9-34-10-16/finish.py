from pathlib import Path
import sys,json,re,subprocess,hashlib,datetime,collections,difflib,shutil
W=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent
sys.path.insert(0,'/Volumes/LaCie/open-commentary/_tools')
from build_repo import load_units,load_commentary,quote
M=json.loads((W/'meta.json').read_text());O=Path(M['repo_dir']);units=load_units(str(W));comments=load_commentary(str(W));ids=['art-9:'+n for n in ['34','35','36','36a']]+['art-10:'+str(n) for n in range(1,17)]
write=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base='b296bb7';prior={}
for name in subprocess.check_output(['git','ls-tree','-r','--name-only',base,'commentary'],cwd=W,text=True).splitlines():
 s=subprocess.check_output(['git','show',base+':'+name],cwd=W,text=True)
 for m in re.finditer(r'^=== (\S+)\s*\n(.*?)(?=^=== |\Z)',s,re.M|re.S):prior[m[1]]=m[2].strip()
assert set(comments)-set(prior)==set(ids)
assert all(comments[k]==v for k,v in prior.items())
counts=collections.Counter(re.findall(r'^=== (\S+)', '\n'.join(p.read_text() for p in (W/'commentary').glob('*.md')),re.M));assert all(v==1 for v in counts.values())
checks=[]
for uid in ids:
 c=comments[uid];assert len(c)>1000 and 'Fictief voorbeeld:' in c
 assert not re.search(r'\b(TODO|FIXME|TBD)\b',c)
 checks.append(dict(id=uid,chars=len(c),source_read=True,fictional_example=True))
similar=[]
for i,a in enumerate(ids):
 for b in ids[i+1:]:
  ratio=difflib.SequenceMatcher(None,comments[a],comments[b],autojunk=False).ratio()
  if ratio>.60:similar.append(dict(a=a,b=b,ratio=ratio))
assert not similar
write(D/'author-content-check.json',dict(independent_review=False,units=checks,prior_commentaries_preserved=len(prior),no_missing_assigned=True,duplicate_delimiters=[],similar_pairs_over_060=similar,checks='Meaning, paragraph distinctions, statutory cross-references, contemporary version, fictional examples and authority scope checked by author; length is not a quality certificate.'))
build=subprocess.run(['python3','/Volumes/LaCie/open-commentary/_tools/build_repo.py',str(W)],capture_output=True,text=True)
missing=[u['id'] for u in units if not comments.get(u['id'])];assert build.returncode!=0 and str(len(missing)) in build.stderr
chapters=sorted({u['chapter'] for u in units if u['id'] in ids})
for n in chapters:
 chapter=next(c for c in M['chapters'] if c['n']==n);allpart=[u for u in units if u['chapter']==n];part=[u for u in allpart if u['id'] in comments]
 buf=[f'# Commentaarhoofdstuk {n:02d} — {chapter["title"]}',f'Auteurscheckpoint: {len(part)} van {len(allpart)} eenheden geschreven. Het boek is onvoltooid.'];last=None
 for u in part:
  if u.get('structure')!=last:buf.append('#### '+' / '.join(u.get('structure',[])));last=u.get('structure')
  buf.extend(['### '+u['label']+(' — '+u['title'] if u.get('title') else ''),'**Wettekst:**',quote(u['text'])]);buf.extend('*Bronnotitie:* '+x for x in u.get('notes',[]));buf.append(comments[u['id']])
 (O/f'{n:02d}-{chapter["slug"]}.md').write_text('\n\n'.join(buf)+'\n')
vproc=subprocess.run(['python3','/Volumes/LaCie/open-commentary/_tools/validate.py',str(W)],capture_output=True,text=True);v=json.loads(vproc.stdout);assert v['verbatim_ratio']==1.0
validation=dict(bounded_author_technical_ok=True,assigned_units=len(ids),preserved_prior_commentaries=len(prior),commented_book_units=len(comments),remaining_unwritten=len(missing),strict_validator=v,shared_builder=dict(exit_code=build.returncode,stderr=build.stderr),build_method='Shared builder invoked; refuses missing out-of-scope commentary. Only affected chapters rendered with unchanged shared load_units/load_commentary/quote functions.',source_text_agreement=1.0,whole_book_complete=False,independent_review=False)
write(W/'batch-9-34-10-16-validation.json',validation)
limits=[f'{len(missing)} eenheden buiten deze batch nog ongeschreven.','Deze twintig toelichtingen wachten op onafhankelijke tweede beoordeling.','Selectieve rechtspraak; geen uitputtende dekking of volledige controle van latere behandeling.','Technische validatie bewijst geen juridische kwaliteit.']
result=dict(complete=True,kind='bounded_author',authored_ids=ids,completed_units=len(ids),total_assigned=len(ids),written_book_units=len(comments),total_book_units=len(units),whole_book_complete=False,independent_review=False,source_preflight='sources/author-9-34-10-16/preflight-result.json',validation='batch-9-34-10-16-validation.json',unresolved_blockers=[],limitations=limits)
write(W/'batch-9-34-10-16-result.json',result)
now=datetime.datetime.now(datetime.timezone.utc).isoformat();status=json.loads((W/'status.json').read_text());status.update(stage='authoring_incomplete',updated_at=now,completed_units=len(comments),completed_ids=[u['id'] for u in units if u['id'] in comments],missing_commentary_ids=missing,remaining_limitations=limits,last_author_batch=result);status['source_checks'].update(author_batch_verified_at=now,author_batch_evidence='sources/author-9-34-10-16/verification.json');status['validation_result']=dict(whole_book_complete=False,bounded_author_passed=True,strict_validator=v,evidence='batch-9-34-10-16-validation.json');status.setdefault('case_law_sources',{}).setdefault('additional_author_batch',[]).append('ECLI:NL:RVS:2025:5425');write(W/'status.json',status)
note='''\n\n## Auteurscheckpoint 9:34–10:16\n\nPrecies twintig toegewezen bepalingen zijn toegelicht: 9:34–9:36a en 10:1–10:16. De eerdere 520 toelichtingen zijn ongewijzigd behouden. Stand: **540 van 588 eenheden geschreven**; 48 buiten deze batch ontbreken. [Batchresultaat](batch-9-34-10-16-result.json), [bronpreflight](sources/author-9-34-10-16/preflight-result.json), [HTTP en hashes](sources/author-9-34-10-16/verification.json), [auteurscontrole](sources/author-9-34-10-16/author-content-check.json) en [technische validatie](batch-9-34-10-16-validation.json) leggen de controles vast. De opnieuw opgehaalde officiële XML is identiek aan de canonieke bron. Officiële wijzigingshistorie bevestigt 15 augustus 2026 als actuele toestand; eerstvolgende aangekondigde toestand is 1 januari 2027. De 588 broneenheden inclusief aanhef, slot en drie bijlagen zijn onafhankelijk geïnventariseerd. De toegewezen artikelen verschillen niet van de bewaarde toestand van 1 augustus 2026.\n\nDe volledige [ABRvS-uitspraak van 12 november 2025](cases/ECLI-NL-RVS-2025-5425.md) is met de lokale nationale corpusbron gelezen en uitsluitend voor de uitleg van 10:3, derde lid, gebruikt. De overige artikelen zijn niet met een afzonderlijke voldoende relevante geverifieerde uitspraak onderbouwd. De volledige gedeelde bouw en validator falen nog op ontbrekende toelichtingen buiten deze batch; de getroffen hoofdstukken zijn als onvoltooid checkpoint opgebouwd. Deze twintig nieuwe toelichtingen wachten op onafhankelijke tweede beoordeling. Geen boekvoltooiing, uitputtende rechtspraakdekking of externe professionele goedkeuring.\n'''
for name in ['README.md','SOURCES.md','REVIEW.md']:
 p=W/name;s=p.read_text()
 if name=='README.md':s=re.sub(r'Onvoltooid werkmanuscript — \d+ van 588',f'Onvoltooid werkmanuscript — {len(comments)} van 588',s,count=1)
 p.write_text(s+note)
p=O/'INDEX.md';s=p.read_text().replace('520 van 588','540 van 588');s+='\n\n[Auteurscheckpoint 9:34–10:16](batch-9-34-10-16-result.json): twintig nieuwe toelichtingen; boek onvoltooid.\n';p.write_text(s)
for name in ['README.md','SOURCES.md','REVIEW.md','status.json','batch-9-34-10-16-result.json','batch-9-34-10-16-validation.json']:shutil.copyfile(W/name,O/name)
shutil.copytree(D,O/'sources/author-9-34-10-16',dirs_exist_ok=True);(O/'cases').mkdir(exist_ok=True);shutil.copyfile(W/'cases/ECLI-NL-RVS-2025-5425.md',O/'cases/ECLI-NL-RVS-2025-5425.md')
files=[O/f'{n:02d}-deel-{n:02d}.md' for n in chapters]+[O/'cases/ECLI-NL-RVS-2025-5425.md'];errors=[]
for p in files:
 for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
  if not re.match(r'https?://|#',link) and not (p.parent/link.split('#')[0]).exists():errors.append([str(p),link])
assert not errors
write(D/'link-check.json',dict(checked_files=[str(p.relative_to(O)) for p in files],errors=errors))
shutil.copyfile(D/'link-check.json',O/'sources/author-9-34-10-16/link-check.json')
manifest=[dict(path=str(p.relative_to(W)),sha256=sha(p),bytes=p.stat().st_size) for p in sorted((W/'sources').rglob('*')) if p.is_file()]
for directory in [W,O]:write(directory/'source-manifest.json',manifest)
print(json.dumps(validation,ensure_ascii=False))
