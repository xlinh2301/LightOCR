import argparse
from dotenv import load_dotenv
from .db import connect
from .scholar import search
def main():
 load_dotenv();p=argparse.ArgumentParser();s=p.add_subparsers(dest='cmd',required=True);d=s.add_parser('db');d.add_argument('action',choices=['init']);q=s.add_parser('search');q.add_argument('query');q.add_argument('--year');q.add_argument('--limit',type=int,default=100);s.add_parser('sources');a=p.parse_args()
 if a.cmd=='db':connect().close();print('database initialized')
 elif a.cmd=='search':sid,n=search(a.query,a.year,a.limit);print(f'search {sid}: {n} records')
 else:
  with connect() as c:
   for r in c.execute('SELECT paper_id,year,title,url FROM sources ORDER BY year DESC,title'):print(r['year'],r['paper_id'],r['title'],r['url'])
if __name__=='__main__':main()
