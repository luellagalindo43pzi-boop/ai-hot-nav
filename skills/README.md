# Public AI Hot Nav integrations

This repository exposes a public static catalog, an Agent Skills-compatible instruction file, a local directory-search CLI, and an optional stdio MCP server.

- Skill definition: [`ai-hot-nav/SKILL.md`](ai-hot-nav/SKILL.md)
- MCP server (local stdio): [`ai-hot-nav/mcp_server.py`](ai-hot-nav/mcp_server.py)
- Local CLI: [`ai-hot-nav/search.py`](ai-hot-nav/search.py)
- Public catalog JSON: <https://luellagalindo43pzi-boop.github.io/ai-hot-nav/data/sites.json>
- Latest digest: <https://luellagalindo43pzi-boop.github.io/ai-hot-nav/data/digest.json>

## Use from an agent

Import this repository's `skills/ai-hot-nav/SKILL.md` into an agent that supports Agent Skills, or point the agent to the raw GitHub file. For autonomous local search, clone/download this repository and register `python3 /absolute/path/to/ai-hot-nav/skills/ai-hot-nav/mcp_server.py` as a stdio MCP server. The MCP server exposes `search_ai_sites`, `get_latest_digest`, and `get_catalog_stats`; search needs no credentials and runs against the local JSON catalog. Any agent can also fetch the public catalog URL directly.

This project does not host a public remote MCP server or a server-side chat proxy: GitHub Pages is static hosting. Avoid putting private model/search keys in a public site or public MCP endpoint. Agents that need live web search should use their own built-in browsing/search tool, or a user-configured search provider in a trusted runtime.
