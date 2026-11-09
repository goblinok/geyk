#!/usr/bin/env python3
"""Fetch the actual published article Sheet and build a static Pages artifact."""
import csv
import datetime
import hashlib
import io
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'_site'

class GoogleRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,request,response,code,message,headers,new_url):
        value=urllib.parse.urlsplit(new_url)
        host=value.hostname or ''
        if value.scheme!='https' or not (host=='docs.google.com' or host.endswith('.googleusercontent.com')):
            raise ValueError('Unexpected redirect from the published Sheet')
        return super().redirect_request(request,response,code,message,headers,new_url)

def main():
    html=(ROOT/'index.html').read_text(encoding='utf-8')
    url=json.loads(re.search(r'const PRESS_SHEET_URL=("[^"\n]+");',html).group(1))
    parsed=urllib.parse.urlsplit(url)
    if parsed.scheme!='https' or parsed.hostname!='docs.google.com' or not parsed.path.startswith('/spreadsheets/d/e/'):
        raise ValueError('Only a published Google Sheet is allowed')
    if urllib.parse.parse_qs(parsed.query).get('output')!=['csv']:
        raise ValueError('The source must be published as CSV')
    opener=urllib.request.build_opener(GoogleRedirects())
    data=None
    for attempt in range(3):
        try:
            request=urllib.request.Request(url,headers={'User-Agent':'GEYK-Pages-Builder/1.0','Cache-Control':'no-cache'})
            with opener.open(request,timeout=30) as response:
                data=response.read(2*1024*1024+1)
            break
        except Exception:
            if attempt==2:raise
            time.sleep(2*(attempt+1))
    if len(data)>2*1024*1024:raise ValueError('CSV exceeds the supported size')
    text=data.decode('utf-8-sig')
    reader=csv.DictReader(io.StringIO(text))
    if not {'date','title','media','url'}.issubset(reader.fieldnames or []):
        raise ValueError('The published response is not the required article CSV')
    rows=list(reader)
    for row in rows:
        if not any(row.values()):continue
        if not all(row.get(k,'').strip() for k in ['date','title','media','url']):
            raise ValueError('Incomplete article row: fix the Sheet before deployment')
        link=urllib.parse.urlsplit(row['url'])
        if link.scheme not in ['http','https'] or not link.hostname or link.username or link.password:
            raise ValueError('Unsafe article URL')
    if '127.0.0.1' in html or '/Users/' in html or 'localhost:' in html:
        raise ValueError('Local-only dependencies must not be published')
    scan=re.sub(r'data:[^\s\"<>]+','[embedded asset]',html)
    if re.search(r'gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}',scan):
        raise ValueError('Potential secret in the deployable HTML')
    stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
    if html.count('__PRESS_SYNCED_AT__')!=1:raise ValueError('Build timestamp marker missing')
    (OUT/'data').mkdir(parents=True,exist_ok=True)
    (OUT/'index.html').write_text(html.replace('__PRESS_SYNCED_AT__',stamp),encoding='utf-8')
    (OUT/'data/press.csv').write_text(text,encoding='utf-8')
    (OUT/'data/sync.json').write_text(json.dumps({'source_url':url,'fetched_at':stamp,'row_count':len(rows),'sha256':hashlib.sha256(text.encode('utf-8')).hexdigest()},ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'.nojekyll').write_text('',encoding='utf-8')
    print(json.dumps({'built':True,'article_count':len(rows),'with_image_url':sum(bool(r.get('image_url','').strip()) for r in rows),'output':'_site','fetched_at':stamp},ensure_ascii=False))

if __name__=='__main__':main()
