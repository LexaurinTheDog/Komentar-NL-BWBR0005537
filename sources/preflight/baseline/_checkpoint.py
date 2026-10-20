#!/usr/bin/env python3
"""Bewaar uitsluitend werkelijk geschreven commentaar als expliciet onvoltooide uitvoer.
Vervangt niet de vereiste gedeelde eindbouw of strikte eindvalidatie.
"""
import sys,json,re,shutil,hashlib,datetime,collections
from pathlib import Path
W=Path(__file__).resolve().parent
sys.path.insert(0,'/Volumes/LaCie/open-commentary/_tools')
from build_repo import load_units,load_commentary,quote
meta=json.loads((W/'meta.json').read_text());out=Path(meta['repo_dir']);out.mkdir(parents=True,exist_ok=True)
us=load_units(str(W));cs=load_commentary(str(W));done=[u for u in us if cs.get(u['id'])];missing=[u['id'] for u in us if not cs.get(u['id'])]
idx=['# INDEX — Onvoltooid werkmanuscript','',f'{len(done)} van {len(us)} commentaareenheden geschreven. De volledige brondekking is afzonderlijk verantwoord.','', '- [Inleiding](00-inleiding.md)','- [Bronnen](SOURCES.md)','- [Beoordelingsstaat](REVIEW.md)']
for c in meta['chapters']:
 part=[u for u in done if u['chapter']==c['n']]
 if not part:continue
 fn=f"{c['n']:02d}-{c['slug']}.md";allpart=[u for u in us if u['chapter']==c['n']]
 buf=[f"# {c['title']}",f"Auteurscheckpoint: {len(part)} van {len(allpart)} eenheden in dit commentaarhoofdstuk geschreven. Het totale boek is onvoltooid."]
 for u in part:
  buf.extend(['\n#### '+' / '.join(u.get('structure',[])), '\n### '+u['label']+(' — '+u['title'] if u['title'] else ''),'\n**Wettekst:**\n',quote(u['text'])])
  for n in u.get('notes',[]):buf.append('\n*Bronnotitie:* '+n)
  buf.append('\n'+cs[u['id']])
 (out/fn).write_text('\n\n'.join(buf)+'\n');idx.append(f"- [{c['title']}]({fn}) — {len(part)}/{len(allpart)}")
(out/'INDEX.md').write_text('\n'.join(idx)+'\n')
for n in ['README.md','00-inleiding.md','LICENSE','SOURCES.md','REVIEW.md','coverage-evidence.json','meta.json','units.jsonl']:
 shutil.copyfile(W/n,out/n)
for d in ['sources','case-cards']:shutil.copytree(W/d,out/d,dirs_exist_ok=True)
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
status={'stage':'authoring_incomplete','updated_at':now,'title':meta['title'],'decisive_date':'2026-10-19','selected_official_version':'2026-08-15_0','source_checks':{'official_xml_http':200,'valid_xml':True,'landing_http':200,'landing_effective_statement':'Geraadpleegd op 19-10-2026. Geldend van 15-08-2026 t/m heden.','date_url_http':404,'version_information_http':200,'evidence':'sources/verification.json'},'official_articles':584,'total_units':len(us),'completed_units':len(done),'completed_ids':[u['id'] for u in done],'missing_commentary_ids':missing,'case_law_sources':{'read_and_used':['ECLI:NL:RVS:2021:953','ECLI:NL:RVS:2022:285'],'fetched_not_yet_assessed':['ECLI:NL:CBB:2024:31'],'scope':'selective'},'coverage':json.loads((W/'coverage-evidence.json').read_text())['ok'],'validation_result':{'complete':False,'reason':'Volledige gedeelde bouw en eindvalidatie zijn geblokkeerd door ontbrekende commentaren.','not_independent_review':True},'remaining_limitations':['Niet alle commentaareenheden zijn geschreven.','Nog geen onafhankelijke tweede inhoudelijke beoordeling.','Geen uitputtende rechtspraakrecherche of inventaris van alle lagere en tijdelijke uitzonderingsregelingen.','Technische identifierdekking vervangt geen juridische kwaliteitscontrole.']}
if (W/'strict-validation.json').exists():status['validation_result']['strict_validator']=json.loads((W/'strict-validation.json').read_text())
if (W/'technical-audit.json').exists():status['technical_audit']='technical-audit.json'
(W/'status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n');shutil.copyfile(W/'status.json',out/'status.json')
for evidence in ['technical-audit.json','strict-validation.json','build-validation-log.json']:
 if (W/evidence).exists():shutil.copyfile(W/evidence,out/evidence)
manifest=[]
for p in sorted((W/'sources').rglob('*')):
 if p.is_file():manifest.append({'path':str(p.relative_to(W)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
for dest in [W,out]:(dest/'source-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'completed':len(done),'total':len(us),'output':str(out)},ensure_ascii=False))
