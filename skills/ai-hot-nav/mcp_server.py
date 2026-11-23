#!/usr/bin/env python3
"""Minimal stdio MCP server exposing AI Hot Nav catalog search and digest tools.

Run: python3 skills/ai-hot-nav/mcp_server.py
Configure any MCP client with this command and the repository checkout as cwd.
No network calls or API keys are needed for catalog tools.
"""
import json, os, sys
import requests
from pathlib import Path
from search import terms
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'engine'))
try:
    import web_search as tavily
except ImportError:
    tavily = None

ROOT = Path(__file__).resolve().parents[2]
DATA = Path(os.environ.get('AI_HOT_NAV_DATA', ROOT / 'data' / 'sites.json'))
DIGEST = ROOT / 'data' / 'digest.json'

def search(query, limit=10, category='', region=''):
    rows=json.loads(DATA.read_text(encoding='utf-8')); qs=terms(query); found=[]
    for r in rows:
        if category and r.get('cat')!=category: continue
        if region and r.get('region')!=region: continue
        fields=[str(r.get('name','')).lower(),str(r.get('desc','')).lower(),' '.join(r.get('tags',[])).lower(),str(r.get('cat','')).lower(),str(r.get('subcat','')).lower(),str(r.get('url','')).lower()]
        score=float(r.get('score',0))*.02+float(r.get('heat',0))*.01+float(r.get('quality',0))*.01
        for q in qs:
            if q in fields[0]: score+=8
            elif any(q in f for f in fields[2:5]): score+=5
            elif q in fields[1] or q in fields[5]: score+=1
        if qs and all(any(q in f for f in fields) for q in qs): score+=6
        if score>0: found.append((score,r))
    found.sort(key=lambda x:(x[0],x[1].get('score',0)),reverse=True)
    return [r for _,r in found[:max(1,min(int(limit),30))]]

def reply(msgid, result):
    sys.stdout.write(json.dumps({'jsonrpc':'2.0','id':msgid,'result':result},ensure_ascii=False,separators=(',',':'))+'\n');sys.stdout.flush()

def handle(m):
    mid=m.get('id'); method=m.get('method')
    if method=='initialize':
        reply(mid,{'protocolVersion':m.get('params',{}).get('protocolVersion','2024-11-05'),'capabilities':{'tools':{}},'serverInfo':{'name':'ai-hot-nav','version':'1.0.0'}})
    elif method=='ping': reply(mid,{})
    elif method=='tools/list':
        reply(mid,{'tools':[
          {'name':'search_ai_sites','description':'Search the full public AI Hot Nav directory and rank recommendations by relevance and heat/quality. Returns direct source URLs.','inputSchema':{'type':'object','properties':{'query':{'type':'string'},'limit':{'type':'integer','minimum':1,'maximum':30},'category':{'type':'string'},'region':{'type':'string','enum':['','cn','global']}},'required':['query']}},
          {'name':'get_latest_digest','description':'Return latest source-linked AI Hot Nav digest. This is published editorial/model output, not a guarantee of current truth.','inputSchema':{'type':'object','properties':{}}},
          {'name':'get_catalog_stats','description':'Return the number of catalog records and category counts.','inputSchema':{'type':'object','properties':{}}},
          {'name':'search_web','description':'Search the live web through Tavily using the local TAVILY_API_KEY environment variable. Requires a user-owned key; never returns or exposes the key.','inputSchema':{'type':'object','properties':{'query':{'type':'string'},'limit':{'type':'integer','minimum':1,'maximum':10},'topic':{'type':'string','enum':['general','news']}},'required':['query']}},
          {'name':'search_github_repositories','description':'Search public GitHub repositories via the official GitHub Search API; returns stars, language, description, and repository URLs. Subject to unauthenticated rate limits.','inputSchema':{'type':'object','properties':{'query':{'type':'string'},'limit':{'type':'integer','minimum':1,'maximum':10}},'required':['query']}}
        ]})
    elif method=='tools/call':
        p=m.get('params',{}); name=p.get('name'); a=p.get('arguments') or {}
        if name=='search_ai_sites': result=search(a.get('query',''),a.get('limit',10),a.get('category',''),a.get('region',''))
        elif name=='get_latest_digest': result=json.loads(DIGEST.read_text(encoding='utf-8'))
        elif name=='get_catalog_stats':
            rows=json.loads(DATA.read_text(encoding='utf-8')); cats={}
            for r in rows: cats[r.get('cat','unknown')]=cats.get(r.get('cat','unknown'),0)+1
            result={'total':len(rows),'categories':cats,'catalog_url':'https://luellagalindo43pzi-boop.github.io/ai-hot-nav/data/sites.json'}
        elif name=='search_web':
            if tavily is None: raise RuntimeError('web search module missing')
            query=a.get('query','').strip()
            if not os.environ.get('TAVILY_API_KEY'): raise RuntimeError('Set TAVILY_API_KEY in this trusted MCP host environment.')
            result=tavily.search(query,a.get('limit',6),a.get('topic','general'))
        elif name=='search_github_repositories':
            q=a.get('query','').strip()
            if not q: raise RuntimeError('query is required')
            resp=requests.get('https://api.github.com/search/repositories',params={'q':q,'sort':'stars','order':'desc','per_page':max(1,min(int(a.get('limit',8)),10))},headers={'Accept':'application/vnd.github+json','User-Agent':'AI-Hot-Nav-MCP'},timeout=20)
            resp.raise_for_status(); payload=resp.json()
            result=[{'name':x['full_name'],'url':x['html_url'],'description':x.get('description'),'stars':x.get('stargazers_count',0),'language':x.get('language'),'updated_at':x.get('updated_at')} for x in payload.get('items',[])]
        else:
            reply(mid,{'content':[{'type':'text','text':'Unknown tool'}],'isError':True});return
        text=json.dumps(result,ensure_ascii=False,indent=2)
        reply(mid,{'content':[{'type':'text','text':text}],'structuredContent':{'result':result}})
    elif method and method.startswith('notifications/'): return
    elif mid is not None: sys.stdout.write(json.dumps({'jsonrpc':'2.0','id':mid,'error':{'code':-32601,'message':'Method not found'}},separators=(',',':'))+'\n');sys.stdout.flush()

for line in sys.stdin:
    msg = None
    try: msg = json.loads(line); handle(msg)
    except Exception as e:
        # Keep stdout protocol-only; return tool errors as MCP content and diagnostics to stderr.
        if isinstance(msg, dict) and msg.get('id') is not None:
            reply(msg['id'], {'content':[{'type':'text','text':str(e)}],'isError':True})
        print(f'MCP request failed: {e}',file=sys.stderr)
