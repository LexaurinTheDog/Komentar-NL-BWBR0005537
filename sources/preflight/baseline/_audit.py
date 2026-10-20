#!/usr/bin/env python3
"""Reproduceerbare technische audit, ook bij een onvoltooid manuscript."""
from pathlib import Path
import json,re,collections,xml.etree.ElementTree as E,hashlib,subprocess,sys,difflib,datetime
W=Path(__file__).resolve().parent
sys.path.insert(0,'/Volumes/LaCie/open-commentary/_tools')
from build_repo import load_commentary,load_units
from validate import norm
us=load_units(str(W));com=load_commentary(str(W));root=E.parse(W/'sources/intake-official.xml').getroot()
def flat(e):
 if e.tag in {'kop','meta-data'} or (e.tag=='redactie' and e.get('type')=='extra'):return ''
 return (e.text or '')+''.join(flat(c)+(c.tail or '') for c in e)
def plain(s):return ' '.join(s.split())
# Independent comparison against all operative XML text, excluding structural headings and notes.
by_path={x.get('bwb-ng-variabel-deel'):x for x in root.iter() if x.tag in {'artikel','bijlage'}}
text_errors=[];checked=0
for u in us:
 e=by_path[u['official_path']]
 if u['id'].startswith('art-8:36c--'):
  version=1;parts={1:[],2:[]}
  for c in e:
   if c.tag=='al' and 'Voor overige gevallen' in ''.join(c.itertext()):version=2;continue
   if c.tag=='tussenkop':continue
   parts[version].append(flat(c))
  official=plain(' '.join(parts[1 if u['id'].endswith('digitaal') else 2]))
 else:official=plain(flat(e))
 actual=plain(u['text'])
 if actual!=official:text_errors.append({'id':u['id'],'official_excerpt':official[:200],'parsed_excerpt':actual[:200],'diff':list(difflib.unified_diff(official.split(),actual.split()))[:80]})
 checked+=1
# Compare the old main-article extraction with the repaired source. Preserve every difference.
old=(W/'sources/original-intake.md').read_text();matches=list(re.finditer(r'^#### Artikel ([^\n]+)\n',old,re.M));oldmap={}
for i,m in enumerate(matches):
 end=matches[i+1].start() if i+1<len(matches) else len(old)
 text=old[m.end():end];text=re.split(r'^### ',text,flags=re.M)[0].strip();oldmap['art-'+m[1]]=text
changes=[]
for uid,ot in oldmap.items():
 new=[u for u in us if u['id']==uid or (uid=='art-8:36c' and u['id'].startswith(uid+'--'))]
 nt='\n\n'.join(u['text'] for u in new)
 if norm(ot)!=norm(nt):changes.append({'id':uid,'type':'intake_vs_verified_xml_derivative','old_chars':len(ot),'canonical_chars':len(nt),'old_excerpt':ot[:180],'canonical_excerpt':nt[:180],'diff':list(difflib.unified_diff(ot.splitlines(),nt.splitlines(),fromfile='original-intake',tofile='canonical'))})
change=json.loads((W/'sources/change-map.json').read_text());change['main_article_wording_comparison']={'compared_main_articles':len(oldmap),'normalized_identical':len(oldmap)-len(changes),'differences':changes,'interpretation':'Alle afwijkingen blijven hieronder zichtbaar. Redactionele extra-noten staan nu afzonderlijk; voor 8:36c zijn de twee ledenreeksen juridisch gescheiden. Een tekstverschil wordt niet automatisch een wetswijziging genoemd.'};(W/'sources/change-map.json').write_text(json.dumps(change,ensure_ascii=False,indent=2)+'\n')
short=[];paragraphs=collections.defaultdict(list);sentences=collections.defaultdict(list)
for u in us:
 if u['id'] not in com:continue
 c=com[u['id']];need=120 if len(u['text'])<160 else 400
 if len(c)<need:short.append({'id':u['id'],'chars':len(c),'minimum':need})
 for p in re.split(r'\n\s*\n',c):
  if len(p)>160:paragraphs[plain(p)].append(u['id'])
 for s in re.split(r'(?<=[.!?])\s+',c):
  if len(s)>100:sentences[plain(s)].append(u['id'])
out=Path(json.loads((W/'meta.json').read_text())['repo_dir']);link_errors=[];link_count=0
for p in out.rglob('*.md'):
 for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
  if target.startswith(('http:','https:','mailto:','#')):continue
  target=target.split('#')[0].strip('<>');link_count+=1
  if target and not (p.parent/target).exists():link_errors.append({'file':str(p.relative_to(out)),'target':target})
rep={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'independent_review':False,'official_text_units_compared':checked,'official_xml_text_errors':text_errors,'source_xml_sha256':hashlib.sha256((W/'sources/intake-official.xml').read_bytes()).hexdigest(),'commented_units':len(com),'total_units':len(us),'commentary_chars':sum(len(x) for x in com.values()),'commentary_minimum_length_failures':short,'exact_repeated_paragraphs':[{'text':p,'units':ids} for p,ids in paragraphs.items() if len(set(ids))>1],'exact_repeated_long_sentences':[{'text':s,'units':ids} for s,ids in sentences.items() if len(set(ids))>1],'local_links_checked':link_count,'broken_local_links':link_errors,'limitations':['Geen inhoudelijke of onafhankelijke juridische kwaliteitscertificering.','Geen voltooiing zolang niet alle eenheden werkelijk zijn becommentarieerd.','De lengtecontrole is alleen een technische ondergrens.']}
(W/'technical-audit.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:len(v) if isinstance(v,list) else v for k,v in rep.items() if k not in ['limitations']},ensure_ascii=False))
