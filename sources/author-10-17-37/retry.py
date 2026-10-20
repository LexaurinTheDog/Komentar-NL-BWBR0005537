from pathlib import Path
import subprocess,json,hashlib,datetime
D=Path(__file__).resolve().parent
rows=json.loads((D/'verification.json').read_text())
for name,url in [('current.html','https://wetten.overheid.nl/BWBR0005537/2026-08-15'),('history.html','https://wetten.overheid.nl/BWBR0005537/2026-08-15/0/informatie?view=changes')]:
 p=D/name;r=subprocess.run(['curl','-sS','-L','--max-time','45','-A','Mozilla/5.0','-o',str(p),'-w','%{json}',url],capture_output=True,text=True);row={'url':url,'accessed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'curl_exit':r.returncode}
 if r.returncode==0:
  info=json.loads(r.stdout);b=p.read_bytes();row.update(http_status=info['http_code'],final_url=info['url_effective'],path=str(p.relative_to(D.parents[1])),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),accepted_format=b'Algemene wet bestuursrecht' in b and b'Geldend' in b)
 else:row.update(error=r.stderr,accepted_format=False)
 rows.append(row)
(D/'verification.json').write_text(json.dumps(rows,indent=2))
print(rows[-2:])
