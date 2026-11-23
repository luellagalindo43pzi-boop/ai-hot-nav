---
name: ai-hot-nav
description: Search and recommend AI websites from the public AI Hot Nav directory, then research topics and produce source-linked AI briefings. Use for AI tool discovery, site recommendations, research starting points, and topic-specific AI digests.
license: MIT
compatibility: Works with any agent that can fetch public HTTPS URLs and run Python 3.10+. No credentials required for directory search. Optional model/search API keys are supplied by the user and must not be exposed.
metadata:
  author: luellagalindo43pzi-boop
  version: "1.0.0"
---

# AI Hot Nav — public directory research skill

Use this skill to search the public catalog of 2,457 AI-related websites, recommend useful sources, and ground reports in links. Catalog data is public and refreshed by the project automation. The site directory is a discovery index, not an endorsement or a guarantee that every external page is current.

## Public endpoints

- Website: <https://luellagalindo43pzi-boop.github.io/ai-hot-nav/>
- Full structured site catalog: <https://luellagalindo43pzi-boop.github.io/ai-hot-nav/data/sites.json>
- Compact browser bundle: <https://luellagalindo43pzi-boop.github.io/ai-hot-nav/js/data.js>
- Latest digest: <https://luellagalindo43pzi-boop.github.io/ai-hot-nav/data/digest.json>
- Digest archive index: <https://luellagalindo43pzi-boop.github.io/ai-hot-nav/data/digests/index.json>
- Crawl status: <https://luellagalindo43pzi-boop.github.io/ai-hot-nav/data/crawler_status.json>
- Project and source code: <https://github.com/luellagalindo43pzi-boop/ai-hot-nav>

## Workflow

1. Fetch `data/sites.json` and parse it as an array of records. Fields include `name`, `url`, `desc`, `cat`, `subcat`, `tags`, `region`, `source`, `heat`, `quality`, `score`, and, for repositories, `stars`.
2. Search case-insensitively across name, description, category, subcategory, tags, and URL host. Rank exact name/tag matches first, then `score` (or heat and quality), and return a diverse set of 5–12 items. Explain why each fits and include its direct URL. Filter by category/region when the user requests it.
3. For current facts or a dated/topic-specific report, fetch relevant source pages and use the agent's actual web-search/browsing tool. The local MCP server also offers `search_web` (Tavily; requires user-provided `TAVILY_API_KEY`) and `search_github_repositories` (official GitHub Search API; unauthenticated rate limits apply). The directory is a discovery index, not a live search engine; do not claim it searched the web unless a web-search tool was actually used. Clearly separate directory recommendations from verified current findings.
4. For a requested digest, ask for a date range, audience, language, and desired length only if essential. Search the public directory for sources, browse/search those sources for the requested topic and time range, deduplicate findings, and write a concise synthesis with date, source links, and uncertainty noted. Never invent events, metrics, or citations.
5. In the website assistant, choose Auto / Site recommendations / Research brief / Topic digest / Weekly report / Comparison. Digest modes request structured JSON and validate citations against URLs retrieved in the current context; the UI can export Markdown, HTML, JSON, CSV, or plain text. If structured parsing fails, disclose that and export the preserved response with matching source links.
6. Fetch the latest digest/archive for existing coverage; treat it as context, not proof that every linked report remains current.

## Local search tool (optional)

From a checkout or download of this repository, run:

```bash
python3 skills/ai-hot-nav/search.py "RAG vector database" --limit 10
python3 skills/ai-hot-nav/search.py "开源大模型" --category github --limit 8
```

The tool uses the checked-in `data/sites.json` by default. Set `AI_HOT_NAV_DATA` to another local catalog path. It performs local ranking only and makes no network request.

## Safety and privacy

The public site is static and does not provide a server-side chat endpoint. Never expect or reuse the website owner's model key. Ask the user to configure their own model/search credentials in their own agent environment. Do not print, transmit, or commit credentials. If the agent's browser environment cannot access a third-party API due to CORS or network policy, use its own server-side tools instead. Do not bypass access controls, paywalls, robots policies, or source-site terms.
