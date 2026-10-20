from pathlib import Path
import json,xml.etree.ElementTree as E,hashlib,re,copy
W=Path.cwd();D=W/'sources/review-030'
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ids=['bijlage-2-art-'+str(n) for n in range(7,13)]+['bijlage-3-art-1','bijlage-3-art-2']
units=[json.loads(l) for l in (W/'units.jsonl').read_text().splitlines()];root=E.parse(D/'selected.xml').getroot();old=E.parse(W/'sources/preflight/previous-official.xml').getroot()
# Structural inventory is derived from XML nodes, independently of parser output.
expected=[];annex=[]
for el in root.iter():
 if el.tag in ['aanhef','wetsluiting']:expected.append(el.tag)
 elif el.tag=='artikel':
  p=el.get('bwb-ng-variabel-deel','');n=el.findtext('kop/nr');m=re.match('/Bijlage(\\d+)',p)
  uid=f'bijlage-{m[1]}-art-{n}' if m else 'art-'+n
  expected.extend(['art-8:36c--digitaal','art-8:36c--overig'] if uid=='art-8:36c' else [uid])
 elif el.tag=='bijlage':
  nr=el.findtext('kop/nr');children=[f'bijlage-{nr}-art-'+a.findtext('kop/nr') for a in el.iter('artikel')]
  if not children:expected.append('bijlage-'+nr)
  annex.append({'annex':nr,'expected_child_ids':children,'disposition':'Alle genummerde artikelen afzonderlijk behouden.' if children else 'Volledige ongenummerde operationele lijst als bijlage-1 behouden.','evidence_path':'sources/review-030/selected.xml','evidence_sha256':sha(D/'selected.xml')})
parsed=[u['id'] for u in units];coverage={'official_source':{'url':json.loads((D/'verification.json').read_text())[2]['url'],'local_raw_evidence_path':'sources/review-030/selected.xml','sha256':sha(D/'selected.xml')},'expected_ids':expected,'parsed_ids':parsed,'annex_disposition':annex,'missing':sorted(set(expected)-set(parsed)),'extra':sorted(set(parsed)-set(expected)),'duplicates':[x for x in set(parsed) if parsed.count(x)>1]}
assert not coverage['missing'] and not coverage['extra'] and not coverage['duplicates'];save(D/'coverage-recheck.json',coverage)
# Reuse only lexical block extraction functions, not parser walk or its unit inventory.
ns={"__file__":str(W/"_parse.py")};exec((W/'_parse.py').read_text().split('units=[];chapter_specs=')[0],ns)
records=[];changes=[]
for uid in ids:
 u=next(u for u in units if u['id']==uid);el=next(e for e in root.iter('artikel') if e.get('bwb-ng-variabel-deel')==u['official_path']);prev=next(e for e in old.iter('artikel') if e.get('bwb-ng-variabel-deel')==u['official_path'])
 text='\n\n'.join(ns['blocks'](el));prior='\n\n'.join(ns['blocks'](prev));assert text==u['text']
 records.append({'id':uid,'official_path':u['official_path'],'official_text':text,'matches_units':True,'source_sha256':sha(D/'selected.xml'),'previous_text_sha256':hashlib.sha256(prior.encode()).hexdigest(),'current_text_sha256':hashlib.sha256(text.encode()).hexdigest(),'changed_since_previous':text!=prior})
 if text!=prior:changes.append(uid)
save(D/'assigned-source-check.json',records)
p=W/'commentary/part-36-bevoegdheid-en-griffierecht.md';s=p.read_text();before=s
s=s.replace('Voor een besluit over nadeelcompensatie moet de afzonderlijke vermelding van 4:126 in de toepasselijke bevoegdheidsregel worden gecontroleerd.','Voor een besluit over nadeelcompensatie bevat artikel 7 zelf geen afzonderlijke vermelding van 4:126. De concentratie bij Rotterdam volgt daarvoor uit 8:7, derde lid, tweede zin, wanneer de schade is veroorzaakt door een hier bedoeld besluit of een handeling ter uitvoering daarvan. Voor het hoger beroep wordt de afzonderlijke vermelding van 4:126 in artikel 11 getoetst.')
p.write_text(s)
notes=[
'Volledige lijst inclusief sectoren cyberbeveiliging, medische hulpmiddelen, spooruitzonderingen, ACM, Wft en geneste Telecomonderdelen gelezen. Verwijzing voor nadeelcompensatie verduidelijkt: artikel7 bevat geen4:126-vermelding; rechtbankconcentratie volgt uit8:7 lid3 tweede zin, hoger beroep afzonderlijk via11. Overige tekst behouden.',
'Alle tien leden en onderverdelingen gelezen: ressort versus arrondissement, buitenlandse woonplaats, Raad voor rechtsbijstand, Haarlem-bronformulering, Kadaster, kinderrechter, EFRO, Flevoland en twee Groningen-besluiten. Voorbeeld en checklist correct; behouden.',
'Volledige lijst met Wlz-, Wfsv-, Participatiewet-, toeslagen- en Zvw-uitzonderingen gelezen. Beide CRvB-uitspraken volledig gelezen: schuldhulpgrondslag en opschorting eerdere inhoudelijke uitspraak onderscheiden van8:106 lid2. Behouden.',
'Volledige lijst gelezen: hoedanigheid Ambtenarenwet, Jeugdwet, Wmo-uitzonderingen, nadeelcompensatie9/10, historische wetten en toeslagen3.10/3.12. Geen automatische9-opschorting overgenomen; schuldhulpuitspraak begrensd. Behouden.',
'Volledige lijst met alle geneste uitzonderingen gelezen; verschillen7/11 en4/11, Overgangswet/Gelderland, EU-instellingen, APB-bronfout en dubbel woord in EU2021/23 correct. Geen stille correctie authentiek citaat. Behouden.',
'Volledige lijst gelezen: douane,4:126, AWR26, afzonderlijke Mijnbouwwetafdelingen en strategische diensten18 lid3. Rechtstreeks hofberoep5 onderscheiden,8:106 lid1b/lid2 en invordering correct begrensd. Behouden.',
'Alle onderdelen a–d gelezen met8:41/8:109. Natuurlijke persoon, inclusieve340-grens, invaliditeit en P9, bestuursdwang versus dwangsom,5:32 lid3 en samenhang8:41 lid3 correct. HR1231 volledig gelezen, historische tarieven niet overgenomen. Behouden.',
'Volledige lijst inclusief zes fiscale uitzonderingen, rechtszoekende, Wlz, hersteloperatie en schuldhulp gelezen. HR1231 partijstelling versus oordeel en2019-tarieven correct begrensd. Beide voorbeelden en checklist correct; behouden.'
]
reviews=[{'id':uid,'checked_against_full_source':True,'disposition':'corrected' if i==0 else 'retained','review':notes[i]} for i,uid in enumerate(ids)];save(D/'unit-review.json',reviews)
current=(D/'current.html').read_text();history=(D/'history.html').read_text();statement=re.search(r'Geldend van.{0,150}',current)
# Retain the literal published effective statement, rather than treating fetch time as version proof.
import html
ct=html.unescape(re.sub('<[^>]+>', ' ', current));ct=re.sub(r'\s+',' ',ct);ht=html.unescape(re.sub('<[^>]+>', ' ', history));ht=re.sub(r'\s+',' ',ht)
ix=ct.index('Geldend van');eff=ct[ix:ix+70];(D/'version-extract.txt').write_text(eff+'\n\n'+ht)
assert '15-08-2026' in eff and 'heden' in eff and '2027' in ht
pre={'complete':True,'decisive_date':'2026-10-19','review_date':'2026-10-21','official_url':'https://wetten.overheid.nl/BWBR0005537/2026-08-15','verified_at':json.loads((D/'verification.json').read_text())[0]['accessed_at'],'version_evidence':{'effective_statement':eff,'history':'sources/review-030/history.html','first_future_change':'2027-01-01','selected_xml_sha256':sha(D/'selected.xml'),'identical_to_canonical':sha(D/'selected.xml')==sha(W/'sources/intake-official.xml'),'http_results':'sources/review-030/verification.json'},'historical_versions_checked':{'previous':'2026-08-01_0','evidence':'sources/preflight/previous-official.xml','sha256':sha(W/'sources/preflight/previous-official.xml'),'assigned_changed_ids':changes,'versions_concatenated':False,'comparison':'sources/review-030/assigned-source-check.json'},'annexes_checked':annex,'coverage':{'expected_units':len(expected),'parsed_units':len(parsed),'missing':coverage['missing'],'duplicates':coverage['duplicates'],'aanhef_and_wetsluiting':'Beide behouden; geen parserreparatie nodig.','evidence':'sources/review-030/coverage-recheck.json'},'unresolved_blockers':[],'limitations':['Niet elke historische consolidatie gedownload.','Broninventaris buiten de acht revieweenheden is geen inhoudelijke boekreview.']}
if (W/'preflight-result.json').exists():save(D/'prior-preflight-result.json',json.loads((W/'preflight-result.json').read_text()))
save(W/'preflight-result.json',pre);save(D/'preflight-result.json',pre)
cases=[]
for code,units_,paras,holding in [('CRVB-2025-1470',ids[2:4],'3.1–3.3,4','Wgs-grondslag valt buiten9/10; onbevoegd en doorzenden. Geen inhoudelijke schuldhulpbeslissing.'),('CRVB-2024-2006',[ids[2]],'4.2–4.6','Opschorting inhoudelijke ZW-uitspraak omvat opgedragen beslistermijn; latere ingebrekestelling prematuur. Lid2 niet buiten toepassing verklaard.'),('HR-2021-1231',ids[6:],'2.1.1–2.3,3,4','Natuurlijke persoon betaalt gewoon tarief omdat verrekeningsbesluit niet in bijlage3 staat; geen rechtspersonentarief, geen laag tarief. Bedragen2019.')]:
 p=D/(code+'.xml');assert sha(p)==sha(W/'sources/author-annex7-end'/p.name);cases.append({'case':code,'full_text_read':True,'new_response_identical_to_author_source':True,'sha256':sha(p),'paragraphs':paras,'holding_and_limits':holding,'supported_units':units_})
save(D/'case-review.json',cases)
save(D/'search-log.json',{'method':'Hercontrole bestaande drie geselecteerde primaire uitspraken, geen nieuwe juridische autoriteit toegevoegd.','prior_search_log':'sources/author-annex7-end/case-search-log.json','official_full_texts':list(c['case'] for c in cases),'limits':'Geen uitputtende rechtspraak- of latere-behandelingscontrole; geen afzonderlijke zaak voor7,8,11,12.'})
res={'complete':True,'units_reviewed':8,'reviewed_ids':ids,'unresolved_blockers':[],'findings':reviews,'limitations':['Alleen deze acht eenheden inhoudelijk beoordeeld; geen gehele boekvoltooiing.','Rechtspraak selectief; geen uitputtend onderzoek naar latere behandeling.','Geen externe professionele goedkeuring.'],'source_preflight':'sources/review-030/preflight-result.json','coverage_evidence':'sources/review-030/coverage-recheck.json','case_review':'sources/review-030/case-review.json'}
save(W/'review-result.json',res);save(D/'review-result.json',res)
review='\n\n## Dertigste afgebakende review — 21 oktober 2026\n\nUitsluitend bijlage 2, artikelen 7–12, en bijlage 3, artikelen 1–2, zijn in deze tweede beoordeling geheel tegen de officiële tekst gelezen. Zeven toelichtingen behouden; bij artikel 7 de nadeelcompensatieroute verduidelijkt met 8:7, derde lid, tweede zin. De eerdere beoordelingsverslagen hierboven beschrijven hun eigen historische batch en zijn geen actuele gehele boekstatus.\n\n[Exacte acht reviewed_ids en bevindingen](sources/review-030/review-result.json), [bron- en versiecontrole](sources/review-030/preflight-result.json), [zelfstandige XML-inventaris](sources/review-030/coverage-recheck.json), [rechtspraakcontrole](sources/review-030/case-review.json), [HTTP en hashes](sources/review-030/verification.json).\n\n'
review+='\n'.join('- **'+r['id']+'**: '+r['review'] for r in reviews)
review+='\n\nAlle drie geciteerde uitspraken geheel gelezen; nieuwe officiële responses zijn bytegelijk aan de bewaarde auteursbronnen. Historische bedragen, partijstellingen en toepassingsgrenzen onderscheiden. Geen uitputtende rechtspraakdekking, geen externe professionele goedkeuring en geen conclusie over niet toegewezen eenheden.\n'
with (W/'REVIEW.md').open('a') as f:f.write(review)
print('Preflight complete; reviewed',len(ids),'independent inventory',len(expected),'historical changed:',changes)
