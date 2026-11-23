#!/usr/bin/env python3
"""Local search over the public AI Hot Nav catalog; no network or credentials."""
import argparse
import json
import os
import re
from pathlib import Path
from urllib.parse import urlparse

DEFAULT = Path(__file__).resolve().parents[2] / "data" / "sites.json"

def terms(s):
    return [x.lower() for x in re.findall(r"[\w+#.-]+|[\u3400-\u9fff]", s, re.UNICODE) if x.strip()]

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("query")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--category", default="", help="category id, e.g. github, research, llm, media")
    p.add_argument("--region", default="", choices=["", "cn", "global"])
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    path = Path(os.environ.get("AI_HOT_NAV_DATA", DEFAULT))
    rows = json.loads(path.read_text(encoding="utf-8"))
    qs = terms(args.query)
    found = []
    for row in rows:
        if args.category and row.get("cat") != args.category: continue
        if args.region and row.get("region") != args.region: continue
        name = str(row.get("name", "")); desc = str(row.get("desc", "")); tags = " ".join(row.get("tags", []))
        cat = str(row.get("cat", "")); sub = str(row.get("subcat", "")); host = urlparse(row.get("url", "")).netloc
        fields = [name.lower(), desc.lower(), tags.lower(), cat.lower(), sub.lower(), host.lower()]
        score = float(row.get("score", 0)) * .02 + float(row.get("heat", 0)) * .01 + float(row.get("quality", 0)) * .01
        for q in qs:
            if q in fields[0]: score += 8
            elif q in fields[2]: score += 5
            elif q in fields[4] or q in fields[3]: score += 3
            elif q in fields[1] or q in fields[5]: score += 1
        if qs and all(any(q in f for f in fields) for q in qs): score += 6
        if score > 0: found.append((score, row))
    found.sort(key=lambda x: (x[0], x[1].get("score", 0), x[1].get("quality", 0)), reverse=True)
    result = [r for _, r in found[:max(1, min(args.limit, 100))]]
    if args.json: print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for i, r in enumerate(result, 1):
            print(f"{i}. {r.get('name','')} [{r.get('cat','')}/{r.get('subcat','')}] — {r.get('desc','')}\n   {r.get('url','')} | heat {r.get('heat',0)} · quality {r.get('quality',0)}")
        print(f"\n{len(result)} results")

if __name__ == "__main__": main()
