"""Optional Tavily web search integration. API key is read only from TAVILY_API_KEY."""
import os
import requests

ENDPOINT = os.environ.get("TAVILY_ENDPOINT", "https://api.tavily.com/search")

def search(query, limit=6, topic="general", days=None):
    key = os.environ.get("TAVILY_API_KEY", "").strip()
    if not key:
        return []
    payload = {"api_key": key, "query": query, "search_depth": "advanced", "max_results": max(1, min(int(limit), 10)), "include_answer": False, "include_raw_content": False, "topic": topic}
    if days: payload["days"] = int(days)
    response = requests.post(ENDPOINT, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    return [{"title": r.get("title", ""), "url": r.get("url", ""), "summary": r.get("content", ""), "published_at": r.get("published_date"), "score": r.get("score", 0)} for r in data.get("results", []) if r.get("url")]

def search_for_digest(topic="AI news", days=2, limit_per_query=4):
    """Run focused searches and return de-duplicated, dated sources for digest synthesis."""
    queries = [
        (f"latest AI news models product releases {topic}", "news"),
        (f"AI research papers open source projects {topic}", "general"),
        (f"AI industry policy funding tools {topic}", "news"),
    ]
    results, seen = [], set()
    for query, kind in queries:
        try:
            for r in search(query, limit=limit_per_query, topic=kind, days=days):
                u = r["url"].rstrip("/").lower()
                if not u or u in seen: continue
                seen.add(u)
                host = r["url"].split("/")[2] if "://" in r["url"] else "Web"
                results.append({"source": f"Web · {host}", "title": r["title"][:180], "url": r["url"], "summary": r["summary"][:500], "published_at": r.get("published_at"), "web_score": r.get("score", 0), "score": 78, "heat": 78, "quality": 78, "cat": "daily", "region": "global", "tags": ["联网搜索", "Tavily"]})
        except Exception as exc:  # search integration must not block RSS crawl
            print(f"[web-search] Tavily query failed: {type(exc).__name__}: {exc}")
    return results
