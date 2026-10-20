#!/usr/bin/env python3
"""Independent official identifier inventory; no dependency on parser helpers."""
import xml.etree.ElementTree as E,json,hashlib,collections,re
from pathlib import Path
w=Path(__file__).resolve().parent;raw=w/'sources/intake-official.xml';r=E.parse(raw).getroot()
expected=[];ann=[]
for a in r.findall('.//artikel'):
 p=a.get('bwb-ng-variabel-deel');n=a.findtext('kop/nr');b=re.match('/Bijlage([0-9]+)',p)
 uid=('bijlage-'+b[1]+'-art-' if b else 'art-')+n
 if n=='8:36c' and any('Voor overige gevallen' in ''.join(x.itertext()) for x in a.findall('al')):expected.extend([uid+'--digitaal',uid+'--overig'])
 else:expected.append(uid)
for b in r.findall('.//bijlage'):
 n=b.findtext('kop/nr');aa=list(b.iter('artikel'))
 if not aa:expected.append('bijlage-'+n)
 ann.append({'annex':n,'official_path':b.get('bwb-ng-variabel-deel'),'title':' '.join(b.find('kop').itertext()).strip(),'article_count':len(aa),'disposition':'Afzonderlijke volledige bijlage-eenheid' if not aa else 'Alle genummerde artikelen als afzonderlijke eenheden, met bijlagevoorvoegsel'})
parsed=[json.loads(l) for l in (w/'units.jsonl').read_text().splitlines()];ids=[x['id'] for x in parsed]
report={'official_source':{'url':'https://repository.officiele-overheidspublicaties.nl/bwb/BWBR0005537/2026-08-15_0/xml/BWBR0005537_2026-08-15_0.xml','local_raw_evidence_path':'sources/intake-official.xml','sha256':hashlib.sha256(raw.read_bytes()).hexdigest()},'expected_ids':expected,'parsed_ids':ids,'annex_disposition':ann,'missing_ids':sorted(set(expected)-set(ids)),'unexpected_ids':sorted(set(ids)-set(expected)),'duplicate_expected_ids':[x for x,c in collections.Counter(expected).items() if c>1],'duplicate_parsed_ids':[x for x,c in collections.Counter(ids).items() if c>1],'official_article_count':len(list(r.iter('artikel'))),'expected_count':len(expected),'parsed_count':len(ids),'repealed_units':[u['id'] for u in parsed if u['text']=='Vervallen'],'conditional_variants':{'art-8:36c':'Twee in de officiële consolidatie opgenomen toepassingsvarianten blijven afzonderlijk gemarkeerd; geen gelijktijdige ledenreeks.'},'limitations':['Identifierdekking bewijst geen inhoudelijke juistheid van commentaar.','Niet in werking getreden leden en redactionele toelichtingen zijn afzonderlijk herkenbaar; operationele toepasselijkheid moet per procedure worden beoordeeld.']}
report['ok']=not any(report[k] for k in ['missing_ids','unexpected_ids','duplicate_expected_ids','duplicate_parsed_ids'])
(w/'coverage-evidence.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['expected_count','parsed_count','missing_ids','duplicate_parsed_ids','ok']}))
