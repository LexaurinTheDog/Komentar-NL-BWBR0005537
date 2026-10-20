from pathlib import Path
import json,sys,re,datetime,hashlib,subprocess,shutil,difflib,xml.etree.ElementTree as E
W=Path(__file__).resolve().parents[2];D=Path(__file__).parent;sys.path.insert(0,'/Volumes/LaCie/open-commentary/_tools')
from build_repo import load_units,load_commentary,quote
O=Path(json.loads((W/'meta.json').read_text())['repo_dir']);meta=json.loads((W/'meta.json').read_text());write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();now=datetime.datetime.now(datetime.timezone.utc).isoformat()
ids=['art-10:'+str(n) for n in range(17,38) if n!=24]; before=load_commentary(W);baseline=subprocess.check_output(['git','rev-parse','HEAD'],cwd=W,text=True).strip()
p=W/'commentary/part-33-delegatie-toezicht.md';s=p.read_text();s=s.replace('De aangevoerde strijd met het algemeen belang droeg de vernietiging daarom niet.','De Afdeling aanvaardde dat de Kroon de naleving van die internationale afspraken als algemeen belang kon aanmerken. Het bestaan van dat belang was dus niet het probleem; de gestelde strijd van het concrete besluit daarmee was niet aangetoond. De aangevoerde strijd met het algemeen belang droeg de vernietiging daarom niet.');p.write_text(s)
cs=load_commentary(W);us=load_units(W);by={u['id']:u for u in us};assert [i for i in cs if cs[i]!=before[i]]==['art-10:35'];assert all(cs[i]==before[i] for i in cs if i not in ids)
notes=[
'Enige volzin: verlies eigen uitoefening binnen gedelegeerd bereik, tegenover mandaat10:7. Intrekking en beleidsregels correct onderscheiden; categorievoorbeeld behouden.',
'Enige volzin: te allen tijde intrekken van overdracht, geen automatische aantasting eerdere concrete besluiten. Werkingsmoment en lopende dossiers met overgangsrecht correct; behouden.',
'Enige volzin: zowel delegatiebesluit als vindplaats verplicht. Eigen verantwoordelijkheid versus namens, vermeldingsgebrek versus ontbrekende bevoegdheid; behouden.',
'Alle drie leden: derdenoverdracht, uitzondering10:16, bijzondere beleidsregelbasis oorspronkelijke orgaan, twee informatiegerechtigden. Geen individuele instructies uit informatieplicht afgeleid; behouden.',
'Enige volzin met slotclausule: andere handelingen, eigen verantwoordelijkheid en overeenkomstige delegatievoorwaarden.10:19 alleen voor zover aard handeling toelaat.10:12 correct onderscheiden; behouden.',
'Beide leden: wettelijke attributie aan onder verantwoordelijkheid werkende persoon/college; algemene en individuele instructies en inlichtingen op verzoek. Geen zelfstandige vervangingsbevoegdheid verantwoordelijke orgaan; behouden.',
'Enige verwijzing: wettelijke attributie andere handelingen met vereiste verantwoordelijkheidsrelatie. Geen intrekking wettelijke toedeling als mandaat of automatische appellabiliteit; behouden.',
'Enige definitie: toestemming ander bestuursorgaan voor inwerkingtreding reeds genomen besluit. Onderscheid voorafgaande toestemming10:32 en andere inwerkingtredingseisen; behouden.',
'Enige grondslageis: bij of krachtens wet bepaalde gevallen, anders dan10:34. Convenant/overleg niet zonder wettelijke grondslag als preventief veto; behouden.',
'Beide grondcategorieën: strijd recht of in bijzondere wet neergelegde grond. Geen algemeenbelanggrond geïmporteerd uit10:35. Overleg en rechterlijke grenzen correct; behouden.',
'Beide rechterlijke situaties en mede dragende rechtsgronden gelezen. Kracht gewijsde expliciet bij uitvoering; andere zelfstandige grond niet zonder meer uitgesloten. Partijstelling onderscheiden; behouden.',
'Beide leden: deelbaarheid naar aard en inhoud; geen tijdelijkheid, voorwaarden of intrekking goedkeuring. Wijzigen onderliggend besluit apart; financieel voorbeeld behouden.',
'Beide leden: vooraf gelegenheid overleg, geen overeenstemmingsvereiste; motivering verwijst naar besproken inhoud. Uitnodiging en inhoudelijke behandeling correct; behouden.',
'Alle vier leden: verzending/bekendmaking dertien weken, eenmaal verdagen, bijzondere adviesvariant zes maanden in plaats van lid2, positieve fictie tenzij afwijking.3:5 en4:20a–f volledig nagelezen; behouden.',
'Beide leden: toestemming vóór nemen besluit, overeenkomstige afdeling en expliciet termijn stellen. Onderscheid tijdelijke goedkeuring10:29 juist; voorbeeld gewijzigde inhoud/late vaststelling behouden.',
'Enige toepassingsvoorwaarde: vernietiging ander orgaan buiten administratief beroep. Geen eigen bevoegdheid, bezwaar of rechterlijke vernietiging.10:38 en10:41 nagelezen; behouden.',
'Enige formeelwettelijke bevoegdheidsvoorwaarde; bewust onderscheid bij of krachtens10:26. Bevoegdheid gaat vóór gronden10:35; behouden.',
'Beide vernietigingsgronden gelezen. Volledige uitspraak BC2506 en dictum herlezen;2.3.1 Kroonbetoog versus2.3.2 rechter. Verduidelijkt dat kwalificatie NAVO-belang aanvaard is maar concrete strijd ontbreekt. Historisch materieel recht niet als actueel gebruikt.',
'Enige deelbaarheidseis: gedeeltelijke instandhouding strookt aard/inhoud.10:42 lid2 rechtsgevolgen versus behouden deel besluit correct onderscheiden; behouden.',
'Beide rechterlijke situaties, mede dragende rechtsgronden en kracht gewijsde bij uitvoering. Geen algemeen verbod later toezicht, geen omzeiling rechterlijke rechtsgrond via etiket algemeen belang.10:28 juist parallel; behouden.'
]
findings=[dict(id=i,checked_against_full_source=True,disposition='corrected' if i=='art-10:35' else 'retained',review=n,commentary_chars=len(cs[i])) for i,n in zip(ids,notes)];write(D/'unit-review.json',findings)
root=E.parse(D/'selected.xml').getroot();snapshot=E.parse(W/'sources/intake-official.xml').getroot();assert sha(D/'selected.xml')==sha(W/'sources/intake-official.xml')
# Compare extracted statutory wording using the existing reproducible extraction functions, without rerunning their write side effects.
ns={}; code=(W/'_parse.py').read_text().split('units=[];chapter_specs=[]')[0];exec(code.replace("W=Path(__file__).resolve().parent","W=Path("+repr(str(W))+")"),ns)
records=[]
for i in ids:
 a=next(a for a in root.iter('artikel') if a.findtext('kop/nr')==i[4:]);text='\n\n'.join(ns['blocks'](a));assert text==by[i]['text'],i;records.append(dict(id=i,text_agreement=True,official_path=a.get('bwb-ng-variabel-deel'),effective_from=a.get('inwerking'),statutory_text=text))
write(D/'assigned-source-records.json',records)
refs=set(re.findall(r'\b[1-9]:\d+[a-z]*\b','\n'.join(cs[i] for i in ids)));assert all('art-'+r in by for r in refs);write(D/'internal-crossrefs.json',[by['art-'+r] for r in sorted(refs)])
coverage=json.loads((D/'coverage-recheck.json').read_text());assert coverage['ok'];prior=json.loads((W/'sources/review-027/preflight-result.json').read_text());pre=dict(complete=True,decisive_date=meta['decisive_date'],review_date='2026-10-21',official_url=meta['official_source_url'],verified_at=now,version_evidence=dict(effective_statement='Geraadpleegd op 20-10-2026. Geldend van 15-08-2026 t/m heden.',latest_effective_on_decisive_date='2026-08-15',latest_effective_on_review_date='2026-08-15',first_future_change='2027-01-01',selected_xml_sha256=sha(D/'selected.xml'),identical_to_canonical=True,http_results='sources/review-028/verification.json',history='sources/review-028/history-rows.json'),historical_versions_checked=dict(previous='2026-08-01_0',previous_xml='sources/preflight/previous-official.xml',previous_sha256=sha(W/'sources/preflight/previous-official.xml'),assigned_changed_ids=[],historical_versions_concatenated=False,missing_10_24='No article 10:24 in selected official structure; no statutory slot manufactured.'),annexes_checked=coverage['annex_disposition'],coverage=dict(expected_units=len(coverage['expected_ids']),parsed_units=len(us),missing=[],duplicates=[],aanhef_and_wetsluiting='Both preserved',evidence='sources/review-028/coverage-recheck.json'),unresolved_blockers=[],limitations=['History table and preceding consolidation checked; not every historical consolidation downloaded.','Source inventory check is not legal review of unassigned articles.'])
for target in [W/'preflight-result.json',D/'preflight-result.json']:write(target,pre)
case=dict(ecli='ECLI:NL:RVS:2008:BC2506',court='Afdeling bestuursrechtspraak Raad van State',date='2008-01-23',docket='200700877/1',full_text_read=True,paragraphs=['2.1','2.2','2.3','2.3.1','2.3.2','2.4','dictum'],supported_ids=['art-10:35'],official_snapshot='sources/review-028/case.xml',sha256=sha(D/'case.xml'),holding='NAVO-afspraken kunnen algemeen belang vormen, maar ontheffingsvereiste maakt dienen ervan niet onmogelijk; ook geen strijd met wet of algemeen rechtsbeginsel. Vernietigingsbesluit Kroon vernietigd.',context_limits='Oude WRO, PML en specifieke provinciale grondslag historische context; geen huidige materiële rechtsregel of algemeen verbod nationale belangen.2.3.1 is Kroonbetoog;2.3.2 rechterlijk oordeel.',prior_primary_snapshot_agreement=sha(D/'case.xml')==sha(W/'sources/author-10-17-37/ECLI-NL-RVS-2008-BC2506.xml'),later_treatment_exhaustive=False)
write(D/'case-review.json',case);write(D/'case-search-log.json',dict(at=now,query=case['ecli'],method='Gerichte volledige hercontrole bestaande primaire autoriteit en aanwezige nationale corpusafschrift; geen nieuw breed jurisprudentieonderzoek.',other_units='Geen nieuwe individuele zaak toegevoegd aan technische eenheden; geen volledigheidsclaim.',exhaustive=False))
missing=[u['id'] for u in us if not cs.get(u['id'])];limits=['Alleen exact twintig toegewezen artikelen inhoudelijk beoordeeld.',str(len(missing))+' eenheden buiten deze opdracht missen commentaar; boek onvoltooid.','Selectieve rechtspraak; geen uitputtende controle latere behandeling.','Geen externe professionele goedkeuring.']
result=dict(complete=True,units_reviewed=20,reviewed_ids=ids,changed_commentary_ids=['art-10:35'],unresolved_blockers=[],findings=findings,limitations=limits,whole_book_complete=False,source_preflight='sources/review-028/preflight-result.json',reviewed_at=now)
for p in [W/'review-result.json',D/'review-result.json']:write(p,result)
summary='\n\n## Tweede beoordeling batch 028 — artikelen 10:17–10:37 (zonder niet-bestaand 10:24)\n\nPrecies twintig toegewezen artikelen volledig tegen de officiële XML nagelezen. Negentien toelichtingen behouden; bij 10:35 verduidelijkt dat de Afdeling het NAVO-belang als algemeen belang aanvaardde maar de concrete strijd daarmee niet aanwezig achtte. Alle leden, voorbeelden en praktische checklists beoordeeld. De volledige uitspraak BC2506, inclusief partijstellingen en dictum, opnieuw gelezen. Toestand 15 augustus 2026 blijft volgens de officiële actuele pagina geldig; bronhash identiek aan het canonieke bronbestand. De onafhankelijke XML-inventaris telt 588 unieke eenheden, inclusief aanhef, slot en drie bijlagen; geen ontbrekende of dubbele IDs.\n\n[Exacte reviewed_ids en bevindingen](sources/review-028/review-result.json), [bronpreflight](sources/review-028/preflight-result.json), [HTTP en hashes](sources/review-028/verification.json), [rechtspraakcontrole](sources/review-028/case-review.json). '+str(len(missing))+' eenheden buiten deze opdracht missen commentaar. Dit is een begrensde review, geen voltooiing van het boek of externe professionele goedkeuring.\n'
for n in ['README.md','REVIEW.md','SOURCES.md']:
 p=W/n;p.write_text(p.read_text()+summary)
r=subprocess.run(['python3','/Volumes/LaCie/open-commentary/_tools/build_repo.py',str(W)],capture_output=True,text=True);write(D/'build-result.json',dict(exit_code=r.returncode,stdout=r.stdout,stderr=r.stderr))
if r.returncode:
 assert missing and 'CHYBÍ' in r.stderr
 for n in sorted({by[i]['chapter'] for i in ids}):
  c=next(c for c in meta['chapters'] if c['n']==n);allpart=[u for u in us if u['chapter']==n];part=[u for u in allpart if u['id'] in cs];buf=[f'# Commentaarhoofdstuk {n:02d} — {c["title"]}',f'Begrensd checkpoint: {len(part)} van {len(allpart)} eenheden geschreven. Het boek is onvoltooid.'];last=None
  for u in part:
   if u.get('structure')!=last:buf.append('#### '+' / '.join(u.get('structure',[])));last=u.get('structure')
   buf.extend(['### '+u['label'],'**Wettekst:**',quote(u['text'])]);buf.extend('*Bronnotitie:* '+s for s in u.get('notes',[]));buf.append(cs[u['id']])
  (O/f'{n:02d}-{c["slug"]}.md').write_text('\n\n'.join(buf)+'\n')
repeated=[[i,j] for i in ids for j in ids if i<j and difflib.SequenceMatcher(None,cs[i],cs[j]).ratio()>.55];assert not repeated
write(D/'batch-validation.json',dict(reviewed_units=20,statutory_text_agreement=1.0,all_assigned_have_specific_commentary=all(len(cs[i])>=700 for i in ids),high_similarity_pairs=repeated,outside_scope_commentary_unchanged=True,baseline_work_commit=baseline,missing_outside_scope=missing,whole_book_complete=False,build_method='Shared builder attempted; affected chapters rendered with unchanged shared load_units/load_commentary/quote because out-of-scope commentary missing.'))
p=json.loads((W/'sources/verification.json').read_text());p['review_028']={'requests':json.loads((D/'verification.json').read_text()),'preflight':'sources/review-028/preflight-result.json'};write(W/'sources/verification.json',p)
for n in ['README.md','REVIEW.md','SOURCES.md','review-result.json','preflight-result.json']:shutil.copyfile(W/n,O/n)
shutil.copytree(D,O/'sources/review-028',dirs_exist_ok=True);shutil.copyfile(W/'sources/verification.json',O/'sources/verification.json')
errors=[]
for p in [O/'27-deel-27.md',O/'case-cards/ECLI-NL-RVS-2008-BC2506.md']:
 for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
  if not re.match(r'https?://|#',link) and not (p.parent/link.split('#')[0]).exists():errors.append([str(p),link])
assert not errors,errors
write(D/'link-check.json',dict(errors=errors,checked=['27-deel-27.md','case-cards/ECLI-NL-RVS-2008-BC2506.md']))
shutil.copyfile(D/'link-check.json',O/'sources/review-028/link-check.json')
print(json.dumps(dict(reviewed=20,corrected=1,missing_outside_scope=len(missing),whole_book_complete=False)))
