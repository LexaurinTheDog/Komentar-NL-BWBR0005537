from pathlib import Path
import json,sys,re,datetime,hashlib,subprocess,shutil,difflib,html
W=Path(__file__).resolve().parents[2];D=Path(__file__).parent;sys.path.insert(0,'/Volumes/LaCie/open-commentary/_tools')
from build_repo import load_units,load_commentary,quote
M=json.loads((W/'meta.json').read_text());O=Path(M['repo_dir']);write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();now=datetime.datetime.now(datetime.timezone.utc).isoformat()
ids=['art-10:'+str(n) for n in range(38,46)]+['art-11:'+str(n) for n in range(1,5)]+['wetsluiting','bijlage-1']+['bijlage-2-art-'+str(n) for n in range(1,7)]
before=load_commentary(W);p=W/'commentary/part-35-slot-en-rechtsgang.md';s=p.read_text().replace('Deze worden jaarlijks per 1 januari bij ministeriële regeling gewijzigd','Deze worden jaarlijks per 1 januari bij regeling van de Minister van Justitie en Veiligheid gewijzigd').replace('de overige bij of krachtens de Awb vastgestelde bedragen kunnen bij ministeriële regeling worden gewijzigd','de overige bij of krachtens de Awb vastgestelde bedragen kunnen bij regeling van dezelfde minister worden gewijzigd');p.write_text(s)
cs=load_commentary(W);us=load_units(W);by={u['id']:u for u in us};assert [i for i in cs if cs[i]!=before[i]]==['art-11:2'];assert sha(D/'selected.xml')==M['official_xml_sha256']
notes=[
'Beide leden: goedkeuring en openstaand/aanhangig bezwaar of beroep; alleen lid1 via10:45. Voorbeeld correct; behouden.',
'Alle vier leden: dertien weken, tijdige schorsing, verschoven aanvang bij goedkeuring en specifieke verdragsuitzondering. Geen algemene financiële termijn; behouden.',
'Enige volzin: na einde bestuurlijke schorsing geen vernietiging, ook opheffing; rechterlijke voorziening onderscheiden. Behouden.',
'Beide leden: reële overleggelegenheid vooraf aan besluitnemer, geen overeenstemming vereist; verwijzing inhoud overleg in motivering. Geen onjuiste verwijzing10:45; behouden.',
'Alle drie leden: alle rechtsgevolgen, geheel/deels behoud, contractuitvoering en onverlet schadevergoeding. Geen automatische civiele nietigheid afgeleid; behouden.',
'Enige volzin: bevoegd vernietigingsorgaan, hangend onderzoek en tijdelijk karakter; duur en10:40 correct gekoppeld. Behouden.',
'Alle vijf leden: bepaalde duur, eenmaal verlengen, totaaljaar, bijzondere voortduring tot dertien weken na onherroepelijkheid en opheffing. Behouden.',
'Alle verwijzingen en uitdrukkelijk beperkte leden gecontroleerd; Europese uitzondering10:39 lid4 niet meegelezen. Praktische checklist beoordeeld; behouden.',
'Vervallen slot, overgangsnotitie uit metadata niet als geldend lid verwerkt; historische toepasselijkheid niet verondersteld. Behouden.',
'Beide leden: verplichte jaarlijkse indexering kostenbedragen versus facultatieve overige bedragen; afronding en aanspraak/tarief onderscheiden. Minister van Justitie en Veiligheid in beide leden expliciet verduidelijkt.',
'Volledige volzin: bekendmaking besluit versus uitspraak, bijlagewijziging en specifiek overgangsrecht. Volledige primaire uitspraak2659 opnieuw gelezen,4.1 partijstelling versus4.4–4.7 oordeel; beperkte lacune-uitzondering correct. Behouden.',
'Enige citeertitel; onderscheid hoofdtekst/bijlage en versie niet uit naam afgeleid. Behouden.',
'Volledige slotformule, ondertekenaars,4 juni en30 juni1992 gecontroleerd; geen verwarring met inwerkingtreding. Checklist behouden.',
'Volledige operationele lijst gelezen; geen bezwaar versus geen beroep,7:1g versus7:1a, ACM- en datumvoorwaarden, Omgevingswet-clausules, zelfstandige inreisverboden en Wft-boete-uitzondering correct; behouden.',
'Volledige lijst en alle geneste onderdelen gelezen. Uitsluiting versus uitzonderingen Invorderingswet/Kostenwet, positieve/negatieve besluiten, appellant-hoedanigheid, Omgevingswet-programmaclausules, pensioenfondsen en rechterlijke ambtenaren gecontroleerd. Bijzondere rechtsgangen niet ongeverifieerd ingevuld; behouden.',
'Volledige lijst en alle geneste onderdelen gelezen. Eerste/enige aanleg versus bezwaar, toezicht-hoedanigheid, Omgevingswet-uitvoering, continentaal plat, emissieautoriteit, luchtvaart-AVV, milieu-uitzonderingen en onderwijs/zorgclausules nagelezen; behouden.',
'Alle persoonscategorieën a–d en bijzondere wetten gelezen; als zodanig, gewezen ambtenaren en nabestaanden, AOR versus artikel6 en beperkte Liquidatiewet-verwijzing correct. Behouden.',
'Volledige lijst en alle geneste onderdelen gelezen. SER/KvK-uitzonderingen, ACM-openbaarmaking, Energiewet-AVV, authentieke8.3-bronverwijzing, BW vóór1 juli2011, landbouw/marktuitzonderingen en specifieke Wft/EU-onderdelen correct afgebakend. Behouden.',
'Volledige tekst: hof als rechter van beroep op uitspraken op bezwaar95/97 Wfsv; geen verplichte rechtbankfase bedacht; onderscheid artikel91 in artikel2 correct. Behouden.',
'Volledige lijst gelezen: relatieve concentratie versus zittingsplaats, Vw43/45-uitzonderingen, Wav-boete, COA, AOR-complement, specifieke Wm-leden en overige pensioen/defensiecategorieën. Checklist verwijst correct naar volgende bijlageartikelen; behouden.'
]
findings=[dict(id=i,checked_against_full_source=True,disposition='corrected' if i=='art-11:2' else 'retained',review=n,commentary_chars=len(cs[i])) for i,n in zip(ids,notes)];write(D/'unit-review.json',findings)
coverage=json.loads((D/'coverage-recheck.json').read_text());assert coverage['ok'];plain=re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>',' ',(D/'history.html').read_text())));statement=re.search(r'Geraadpleegd op .*?Geldend van .*?heden\.',plain).group();assert '15-08-2026' in statement and 'eerste op 01-01-2027' in plain
pre=dict(complete=True,decisive_date=M['decisive_date'],review_date='2026-10-21',official_url=M['official_source_url'],verified_at=now,version_evidence=dict(effective_statement=statement,first_future_change='2027-01-01',selected_xml_sha256=sha(D/'selected.xml'),identical_to_canonical=True,http_results='sources/review-029/verification.json',history='sources/review-029/history.html'),historical_versions_checked=dict(previous='2026-08-01_0',evidence='sources/preflight/previous-official.xml',sha256=sha(W/'sources/preflight/previous-official.xml'),assigned_changed_ids=[],versions_concatenated=False,explicit_repealed_slot='art-11:1',historical_current_rule='Bijlage2 artikel4: BW-besluiten bekendgemaakt vóór1 juli2011'),annexes_checked=coverage['annex_disposition'],coverage=dict(expected_units=588,parsed_units=588,missing=[],duplicates=[],aanhef_and_wetsluiting='Beide behouden',evidence='sources/review-029/coverage-recheck.json'),unresolved_blockers=[],limitations=['Voorafgaande toestand en actuele historie gelezen; niet elke historische consolidatie gedownload.','Broninventaris is geen inhoudelijke beoordeling van andere eenheden.'])
for p in [W/'preflight-result.json',D/'preflight-result.json']:write(p,pre)
case=dict(ecli='ECLI:NL:CRVB:2013:2659',court='Centrale Raad van Beroep',date='2013-12-03',docket='12/3640 Wpb',full_text_read=True,paragraphs=['4.1','4.2','4.3','4.4','4.5','4.6','4.7','5–9','dictum'],supported_ids=['art-11:3'],official_snapshot='sources/review-029/case.xml',sha256=sha(D/'case.xml'),holding='Raad bevoegd ondanks eerdere ontbrekende Wpb-vermelding: onmiskenbaar onbedoeld hiaat plus sterke verwantschap met WWB. Hoger beroep slaagt; beroep terugvorderingsbesluit ongegrond.',context_limits='4.1 is collegebetoog. Historische Wpb/WWB niet als actueel materieel recht gebruikt. Geen vrije rechterkeuze bij bijlagewijziging.',prior_primary_snapshot_agreement=sha(D/'case.xml')==sha(W/'sources/author-10-38-annex6/CRVB-2013-2659.xml'),local_corpus='sources/author-10-38-annex6/CRVB-2013-2659-local.md',later_treatment_exhaustive=False);write(D/'case-review.json',case)
write(D/'search-log.json',dict(at=now,query=case['ecli'],method='Gerichte hercontrole bestaande primaire volledige uitspraak en aanwezige nationale corpuskopie; geen breed nieuw onderzoek.',other_assigned_units='Geen afzonderlijke nieuwe relevante uitspraak geselecteerd.',exhaustive=False))
missing=[u['id'] for u in us if not cs.get(u['id'])];result=dict(complete=True,units_reviewed=20,reviewed_ids=ids,changed_commentary_ids=['art-11:2'],unresolved_blockers=[],findings=findings,limitations=['Exact twintig toegewezen eenheden beoordeeld.','Acht buiten deze opdracht ontbreken; boek onvoltooid.','Selectieve rechtspraak, latere behandeling niet uitputtend onderzocht.','Geen externe professionele goedkeuring.'],whole_book_complete=False,reviewed_at=now)
for p in [W/'review-result.json',D/'review-result.json']:write(p,result)
summary='\n\n## Tweede beoordeling batch 029 — 10:38 tot bijlage 2 artikel 6\n\nPrecies twintig toegewezen eenheden volledig tegen de officiële XML gelezen, inclusief de operationele lijsten en alle geneste onderdelen. Negentien toelichtingen behouden; bij 11:2 de bevoegde minister expliciet gemaakt. De volledige primaire uitspraak CRvB 2013:2659 opnieuw gelezen; partijstelling en beperkte lacune-uitzondering correct onderscheiden. Actuele officiële HTML en historie opnieuw opgehaald: geldend vanaf 15 augustus 2026, eerste toekomstige wijziging 1 januari 2027. De XML is identiek aan de canonieke bron; zelfstandige structurele inventaris: 588 unieke eenheden, alle bijlagen, aanhef en slot behouden.\n\n[Exacte IDs en bevindingen](sources/review-029/review-result.json), [preflight](sources/review-029/preflight-result.json), [HTTP en hashes](sources/review-029/verification.json), [rechtspraakcontrole](sources/review-029/case-review.json). Acht eenheden buiten deze opdracht missen commentaar. Deze begrensde tweede beoordeling voltooit het boek niet en is geen externe professionele goedkeuring.\n'
for n in ['README.md','REVIEW.md','SOURCES.md']:
 p=W/n;p.write_text(p.read_text()+summary)
r=subprocess.run(['python3','/Volumes/LaCie/open-commentary/_tools/build_repo.py',str(W)],capture_output=True,text=True);write(D/'build-result.json',dict(exit_code=r.returncode,stdout=r.stdout,stderr=r.stderr))
assert len(missing)==8
if r.returncode:
 assert 'CHYBÍ' in r.stderr
 for n in sorted({by[i]['chapter'] for i in ids}):
  c=next(c for c in M['chapters'] if c['n']==n);allpart=[u for u in us if u['chapter']==n];part=[u for u in allpart if u['id'] in cs];buf=[f'# Commentaarhoofdstuk {n:02d} — {c["title"]}',f'Begrensd checkpoint: {len(part)} van {len(allpart)} eenheden geschreven. Het boek is onvoltooid.'];last=None
  for u in part:
   st=u.get('structure') or []
   if st and st!=last:buf.append('#### '+' / '.join(st));last=st
   buf.extend(['### '+u['label']+(' — '+u['title'] if u.get('title') else ''),'**Wettekst:**',quote(u['text'])]);buf.extend('*Bronnotitie:* '+s for s in u.get('notes',[]));buf.append(cs[u['id']])
  (O/f'{n:02d}-{c["slug"]}.md').write_text('\n\n'.join(buf)+'\n')
rep=[[a,b] for k,a in enumerate(ids) for b in ids[k+1:] if difflib.SequenceMatcher(None,cs[a],cs[b]).ratio()>.55];assert not rep
write(D/'batch-validation.json',dict(reviewed_units=20,statutory_text_agreement=1.0,outside_scope_commentary_unchanged=True,high_similarity_pairs=rep,missing_outside_scope=missing,whole_book_complete=False,build_method='Shared builder attempted; affected chapters rendered with unchanged load_units/load_commentary/quote because eight out-of-scope commentaries missing.'))
v=json.loads((W/'sources/verification.json').read_text());v['review_029']={'requests':json.loads((D/'verification.json').read_text()),'preflight':'sources/review-029/preflight-result.json'};write(W/'sources/verification.json',v)
for n in ['README.md','REVIEW.md','SOURCES.md','review-result.json','preflight-result.json']:shutil.copyfile(W/n,O/n)
shutil.copytree(D,O/'sources/review-029',dirs_exist_ok=True);shutil.copyfile(W/'sources/verification.json',O/'sources/verification.json')
errors=[]
for p in [O/f'{n:02d}-deel-{n:02d}.md' for n in sorted({by[i]['chapter'] for i in ids})]+[O/'case-cards/ECLI-NL-CRVB-2013-2659.md']:
 for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
  if not re.match(r'https?://|#',link) and not (p.parent/link.split('#')[0]).exists():errors.append([str(p),link])
assert not errors;write(D/'link-check.json',dict(errors=errors));shutil.copyfile(D/'link-check.json',O/'sources/review-029/link-check.json')
print(json.dumps(dict(reviewed=20,corrected=1,unwritten_outside_scope=len(missing))))
