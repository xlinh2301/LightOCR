import os,json,requests
from datetime import datetime,timezone
from .db import connect
def search(query,years=None,limit=100):
 key=os.getenv('S2_API_KEY')
 if not key: raise RuntimeError('S2_API_KEY missing; add to .env')
 params={'query':query,'limit':max(1,min(limit,100)),'fields':'title,authors,year,abstract,venue,externalIds,url,openAccessPdf,citationCount,publicationTypes'}
 if years:params['year']=years
 r=requests.get('https://api.semanticscholar.org/graph/v1/paper/search',params=params,headers={'x-api-key':key},timeout=45);r.raise_for_status();items=r.json().get('data',[]);now=datetime.now(timezone.utc).isoformat()
 with connect() as c:
  sid=c.execute('INSERT INTO searches(query,year_from,year_to,source_api,retrieved_at,result_count) VALUES(?,?,?,?,?,?)',(query,int(years[:4]) if years else None,int(years[-4:]) if years else None,'Semantic Scholar',now,len(items))).lastrowid
  for x in items:
   if not x.get('paperId') or not x.get('title'):continue
   c.execute('INSERT OR REPLACE INTO sources VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(x['paperId'],x['title'],json.dumps(x.get('authors') or []),x.get('year'),x.get('venue'),x.get('abstract'),(x.get('externalIds') or {}).get('DOI'),x.get('url'),(x.get('openAccessPdf') or {}).get('url'),x.get('citationCount'),json.dumps(x.get('publicationTypes') or []),now,sid,'unreviewed',''))
   c.execute('INSERT INTO source_fts VALUES(?,?,?)',(x['paperId'],x['title'],x.get('abstract') or ''))
 return sid,len(items)
