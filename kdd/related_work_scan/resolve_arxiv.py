import json, re, time, urllib.request, urllib.parse, xml.etree.ElementTree as ET, sys
NS={"a":"http://www.w3.org/2005/Atom"}
sel=json.load(open('selected.json'))
def norm(s): return re.sub(r'[^a-z0-9]+',' ',s.lower()).strip()
n=0
for r in sel:
    if 'arxiv.org/pdf' in r['pdf'] or 'proceedings.mlr.press' in r['pdf']: continue
    q=urllib.parse.urlencode({"search_query":'ti:"%s"'%re.sub(r'[^A-Za-z0-9 ]+',' ',r['title'])[:150],"max_results":5})
    root=None
    for attempt in range(3):
        try:
            root=ET.fromstring(urllib.request.urlopen("https://export.arxiv.org/api/query?"+q,timeout=60).read()); break
        except Exception as e:
            time.sleep(5)
    if root is None: print('FAIL',r['title'][:50]); continue
    hit=None
    for e in root.findall('a:entry',NS):
        if norm(e.find('a:title',NS).text)[:50]==norm(r['title'])[:50]:
            hit=e.find('a:id',NS).text.strip(); break
    if hit:
        r['pdf']=hit.replace('/abs/','/pdf/'); r['arxiv']=hit; n+=1
    else:
        print('NO ARXIV', r['venue'], '|', r['title'][:70], '|', r['pdf'], file=sys.stderr)
    time.sleep(3.2)
json.dump(sel, open('selected.json','w'), indent=1)
print(len(sel),'selected;',n,'resolved', file=sys.stderr)
