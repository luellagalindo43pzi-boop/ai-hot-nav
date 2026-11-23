#!/usr/bin/env python3
"""Minimal stdio MCP server exposing AI Hot Nav catalog search and digest tools.

Run: python3 skills/ai-hot-nav/mcp_server.py
Configure any MCP client with this command and the repository checkout as cwd.
No network calls or API keys are needed for catalog tools.
"""
import json, os, sys
from pathlib import Path
from search import terms

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
          {'name':'get_catalog_stats','description':'Return the number of catalog records and category counts.','inputSchema':{'type':'object','properties':{}}}
        ]})
    elif method=='tools/call':
        p=m.get('params',{}); name=p.get('name'); a=p.get('arguments') or {}
        if name=='search_ai_sites': result=search(a.get('query',''),a.get('limit',10),a.get('category',''),a.get('region',''))
        elif name=='get_latest_digest': result=json.loads(DIGEST.read_text(encoding='utf-8'))
        elif name=='get_catalog_stats':
            rows=json.loads(DATA.read_text(encoding='utf-8')); cats={}
            for r in rows: cats[r.get('cat','unknown')]=cats.get(r.get('cat','unknown'),0)+1
            result={'total':len(rows),'categories':cats,'catalog_url':'https://luellagalindo43pzi-boop.github.io/ai-hot-nav/data/sites.json'}
        else:
            reply(mid,{'content':[{'type':'text','text':'Unknown tool'}],'isError':True});return
        text=json.dumps(result,ensure_ascii=False,indent=2)
        reply(mid,{'content':[{'type':'text','text':text}],'structuredContent':{'result':result}})
    elif method and method.startswith('notifications/'): return
    elif mid is not None: sys.stdout.write(json.dumps({'jsonrpc':'2.0','id':mid,'error':{'code':-32601,'message':'Method not found'}},separators=(',',':'))+'\n');sys.stdout.flush()

for line in sys.stdin:
    try: handle(json.loads(line))
    except Exception as e:
        # Keep stdout protocol-only; diagnostics go to stderr.
        print(f'MCP request failed: {e}',file=sys.stderr)
