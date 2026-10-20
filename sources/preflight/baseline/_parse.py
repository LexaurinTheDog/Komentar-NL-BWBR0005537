#!/usr/bin/env python3
"""Reproduceerbare omzetting van de officiële BWB-toestand, inclusief bijlagen.
Geen samenvoeging van de twee toepassingsvarianten van artikel 8:36c.
"""
from pathlib import Path
import copy,json,re,hashlib,xml.etree.ElementTree as ET
W=Path(__file__).resolve().parent
RAW=W/'sources/intake-official.xml'
ROOT=ET.parse(RAW).getroot()
assert ROOT.tag=='toestand' and ROOT.get('bwb-id')=='BWBR0005537'
STRUCT={'hoofdstuk','titeldeel','afdeling','paragraaf','divisie','bijlage'}
SKIP={'meta-data','kop'}
def norm(t):return re.sub(r'\s+',' ',t).strip()
def inline(e):
    if e.tag=='meta-data' or (e.tag=='redactie' and e.get('type')=='extra'):return ''
    return (e.text or '')+''.join(inline(c)+(c.tail or '') for c in e)
def blocks(e):
    if e.tag in SKIP:return []
    if e.tag=='redactie':return [norm(inline(e))] if e.get('type')!='extra' else []
    if e.tag in {'al','tussenkop'}:
        return [norm(inline(e))] if norm(inline(e)) else []
    out=[]
    if e.tag=='lid':
        n=e.findtext('lidnr',''); cs=[x for x in e if x.tag!='lidnr']
        out=[p for c in cs for p in blocks(c)]
        if out:out[0]=n+' '+out[0]
        return out
    if e.tag=='li':
        n=e.findtext('li.nr','');out=[p for c in e if c.tag!='li.nr' for p in blocks(c)]
        if out:out[0]=n+' '+out[0]
        return out
    return [p for c in e for p in blocks(c)]
def heading(e):return norm(' '.join(inline(c) for c in e.find('kop'))) if e.find('kop') is not None else e.get('label','')
def stable(e):
    path=e.get('bwb-ng-variabel-deel','')
    if e.tag=='bijlage':return 'bijlage-'+e.findtext('kop/nr')
    n=e.findtext('kop/nr');m=re.match(r'/Bijlage(\d+)',path)
    return ('bijlage-'+m[1]+'-art-' if m else 'art-')+n
units=[];chapter_specs=[];notes=[];current_main=None;part=0;inpart=0

def walk(e,structure=(),annex=None):
    global current_main,part,inpart
    if e.tag in STRUCT:
        structure=structure+(heading(e),)
    if e.tag in {'hoofdstuk','bijlage'}:
        current_main=heading(e);inpart=0
    emit=e.tag=='artikel' or (e.tag=='bijlage' and not list(e.iter('artikel')))
    if emit:
        if not inpart or inpart>=25:
            part+=1;inpart=0
            chapter_specs.append({'n':part,'slug':f'deel-{part:02d}','title':current_main})
        inpart+=1; n=e.findtext('kop/nr','');uid=stable(e)
        extras=[norm(''.join(x.itertext())) for x in e.iter('redactie') if x.get('type')=='extra']
        metadata_notes=[]
        for x in e.findall('meta-data/brondata/opmerkingen-inhoud/al'):metadata_notes.append(norm(''.join(x.itertext())))
        variants=[[]]
        for c in e:
            if c.tag=='al' and 'Voor overige gevallen' in ''.join(c.itertext()):
                variants.append([]);continue
            if uid=='art-8:36c' and c.tag=='tussenkop':continue
            variants[-1].extend(blocks(c))
        u={'id':uid,'label':e.get('label',heading(e)),'title':norm(inline(e.find('kop/titel'))) if e.find('kop/titel') is not None else '', 'chapter':part,'structure':list(structure[:-1] if e.tag=='bijlage' else structure),'text':'\n\n'.join(variants[0]),'notes':extras+metadata_notes,'official_path':e.get('bwb-ng-variabel-deel'),'effective_from':e.get('inwerking'),'xml_label_id':e.get('label-id')}
        if len(variants)>1:
            u['id']=uid+'--digitaal';u['title']='Toepassingsvariant digitaal procederen (zie bronnotities)'
            units.append(u.copy())
            u['id']=uid+'--overig';u['title']='Toepassingsvariant overige gevallen';u['text']='\n\n'.join(variants[1])
        units.append(u)
        if extras or metadata_notes:notes.append({'id':uid,'notes':extras+metadata_notes})
        return
    for c in e:walk(c,structure,annex)
walk(ROOT)
# Canonical plain-text derivative preserves separate conditional units without inserting normative text.
canonical='\n\n'.join(u['label']+'\n\n'+u['text'] for u in units)+'\n'
(W/'sources/canonical.txt').write_text(canonical)
(W/'units.jsonl').write_text(''.join(json.dumps(u,ensure_ascii=False)+'\n' for u in units))
meta={'cc':'nl','lang':'nl','repo':'Komentar-NL-BWBR0005537','repo_dir':'/Volumes/LaCie/open-commentary/nl/Komentar-NL-BWBR0005537','title':'Commentaar op de Algemene wet bestuursrecht','source_path':str(W/'sources/canonical.txt'),'intro_file':'00-inleiding.md','intro_desc':'Afbakening, bronnen en leeswijzer','labels':{'text':'Wettekst','chapter':'Commentaarhoofdstuk','notes':'Bronnotitie'},'chapters':chapter_specs,'decisive_date':'2026-10-19','consolidation_date':ROOT.get('inwerkingtreding')}
(W/'meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
(W/'sources/editorial-notes.json').write_text(json.dumps(notes,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'units':len(units),'chapters':len(chapter_specs),'characters':len(canonical)},ensure_ascii=False))
