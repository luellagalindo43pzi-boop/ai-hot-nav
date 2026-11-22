import json, time, urllib.request, urllib.parse, os

TOKEN = os.environ['GH_TOKEN']
QUERIES = [
    ("topic:artificial-intelligence stars:>1000", "AI"),
    ("topic:machine-learning stars:>2500", "ML"),
    ("topic:deep-learning stars:>2500", "DL"),
    ("topic:llm stars:>1000", "LLM"),
    ("topic:large-language-models stars:>500", "LLM"),
    ("topic:generative-ai stars:>500", "GenAI"),
    ("topic:ai-agent stars:>300", "Agent"),
    ("topic:stable-diffusion stars:>1000", "Diffusion"),
    ("topic:diffusion-models stars:>300", "Diffusion"),
    ("topic:computer-vision stars:>2500", "CV"),
    ("topic:nlp stars:>2500", "NLP"),
    ("topic:chatgpt stars:>1000", "ChatGPT"),
    ("topic:transformers stars:>1000", "Transformers"),
    ("topic:rag stars:>200", "RAG"),
    ("topic:openai stars:>1500", "OpenAI"),
    ("topic:pytorch stars:>3500", "PyTorch"),
    ("topic:reinforcement-learning stars:>1000", "RL"),
    ("topic:multimodal stars:>300", "Multimodal"),
    ("topic:whisper stars:>200", "Speech"),
    ("topic:text-to-image stars:>500", "T2I"),
    ("topic:llm-agent stars:>200", "Agent"),
    ("topic:fine-tuning stars:>500", "FineTune"),
]

all_repos = {}
for i, (q, tag) in enumerate(QUERIES):
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
            fid = it["id"]
            if fid not in all_repos:
                all_repos[fid] = {
                    "id": fid,
                    "name": it["full_name"],
                    "url": it["html_url"],
                    "desc": (it.get("description") or "").strip(),
                    "stars": it["stargazers_count"],
                    "forks": it["forks_count"],
                    "language": it.get("language") or "",
                    "topics": (it.get("topics") or [])[:8],
                    "pushed_at": it.get("pushed_at", "")[:10],
                    "license": (it.get("license") or {}).get("spdx_id", "") if it.get("license") else "",
                    "query_tags": [tag],
                }
            else:
                all_repos[fid]["query_tags"].append(tag)
        print(f"[{i+1}/{len(QUERIES)}] {q} -> {len(items)} items, total unique: {len(all_repos)}")
    except Exception as e:
        print(f"[{i+1}] FAILED {q}: {e}")
    time.sleep(2.2)

repos = list(all_repos.values())
repos.sort(key=lambda r: -r["stars"])
print("TOTAL unique repos:", len(repos))
json.dump(repos, open("data/repos.json", "w"), ensure_ascii=False)
