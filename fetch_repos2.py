import json, time, urllib.request, urllib.parse, os, sys

TOKEN = os.environ['GH_TOKEN']
QUERIES = [
    "topic:llm-inference stars:>100",
    "topic:mcp stars:>100",
    "topic:prompt-engineering stars:>150",
    "topic:llama stars:>300",
    "topic:deepseek stars:>50",
    "topic:ai-tools stars:>200",
    "topic:gpt stars:>1500",
    "topic:robotics stars:>1500",
]

all_repos = {str(r["id"]): r for r in json.load(open("data/repos.json"))}
start = len(all_repos)
for i, q in enumerate(QUERIES):
    url = "https://api.github.com/search/repositories?" + urllib.parse.urlencode({
        "q": q, "sort": "stars", "order": "desc", "per_page": 100
    })
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "ai-hot-nav-builder"
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.load(r)
        items = data.get("items", [])
        for it in items:
            if it.get("archived") or it.get("fork"):
                continue
            fid = str(it["id"])
            if fid not in all_repos:
                all_repos[fid] = {
                    "id": it["id"], "name": it["full_name"], "url": it["html_url"],
                    "desc": (it.get("description") or "").strip(),
                    "stars": it["stargazers_count"], "forks": it["forks_count"],
                    "language": it.get("language") or "",
                    "topics": (it.get("topics") or [])[:8],
                    "pushed_at": it.get("pushed_at", "")[:10],
                    "license": (it.get("license") or {}).get("spdx_id", "") if it.get("license") else "",
                    "query_tags": [],
                }
        print(f"[{i+1}/{len(QUERIES)}] {q} -> {len(items)} items, total unique: {len(all_repos)}")
    except Exception as e:
        print(f"[{i+1}] FAILED {q}: {e}")
    time.sleep(2.2)

repos = list(all_repos.values())
repos.sort(key=lambda r: -r["stars"])
print(f"added {len(repos)-start}, TOTAL: {len(repos)}")
json.dump(repos, open("data/repos.json","w"), ensure_ascii=False)
