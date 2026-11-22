"""AI热榜导航 · 自动抓取引擎

职责：
1. fetch_feed()      —— 抓取 RSS/Atom，容忍单源失败（超时/403/429/解析错误）
2. heuristic_score() —— 纯启发式预打分（信源权重 × 关键词命中 × 新鲜度）
3. crawl()           —— 拉取全部信源 → 去重（相对 sites.json 与 seen 缓存）→
                        输出候选 new_items.json（供日报）+ candidates.json（候选优质站点）
4. merge_candidates()—— 将 LLM 判定优质（≥85 分）的新站点补入 sites.json 并重建 js/data.js
"""
import gzip
import io
import json
import os
import re
import time
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from urllib.parse import urlparse, urldefrag

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")

AI_KEYWORDS = [
    "ai", "artificial intelligence", "大模型", "模型", "llm", "gpt", "claude", "gemini",
    "深度学习", "机器学习", "神经网络", "智能体", "agent", "rag", "openai", "anthropic",
    "deepmind", "deepseek", "通义", "千问", "文心", "智谱", "glm", "llama", "stable diffusion",
    "diffusion", "生成式", "多模态", "具身", "机器人", "芯片", "nvidia", "算力", "推理",
    "fine-tun", "微调", "embedding", "向量", "benchmark", "评测", "开源模型", "hugging face",
]

# 已在 sites.json 中知悉的域名 -> 不重复作为"新站点候选"
def existing_domains():
    domains = set()
    sites_path = os.path.join(DATA, "sites.json")
    if os.path.exists(sites_path):
        for s in json.load(open(sites_path, encoding="utf-8")):
            try:
                domains.add(urlparse(s["url"]).hostname.lower().replace("www.", ""))
            except Exception:
                continue
    return domains

def load_feeds():
    with open(os.path.join(HERE, "feeds.json"), encoding="utf-8") as f:
        return json.load(f)

def _read_response(resp):
    raw = resp.read()
    ctype = resp.headers.get("Content-Encoding", "") + resp.headers.get("Content-Type", "")
    if "gzip" in ctype.lower() or raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return raw

def fetch_feed(feed, timeout=20):
    """抓取并解析单个信源，返回 (items, status_str)。"""
    req = urllib.request.Request(
        feed["url"],
        headers={
            "User-Agent": "AIHOTNavBot/2.0 (+https://github.com/luellagalindo43pzi-boop/ai-hot-nav; RSS reader)",
            "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*",
            "Accept-Encoding": "gzip",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = _read_response(resp)
    except urllib.error.HTTPError as e:
        return [], f"HTTP {e.code}"
    except Exception as e:  # noqa: BLE001
        return [], f"{type(e).__name__}: {e}"

    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        # 粗暴剥掉控制字符再试一次
        try:
            cleaned = re.sub(rb"[\x00-\x08\x0b\x0c\x0e-\x1f]", b"", raw)
            root = ET.fromstring(cleaned)
        except ET.ParseError:
            return [], "XML parse error"

    items = []
    ns = {"a": "http://www.w3.org/2005/Atom"}

    def _text(el):
        return (el.text or "").strip() if el is not None else ""

    # RSS 2.0
    for item in root.iter("item"):
        link = _text(item.find("link")) or _text(item.find("guid"))
        items.append({
            "title": _text(item.find("title")),
            "url": urldefrag(link)[0],
            "published": _text(item.find("pubDate")),
            "summary": re.sub(r"<[^>]+>", "", _text(item.find("description")))[:300],
        })
    # Atom
    for entry in root.findall("a:entry", ns):
        link = ""
        for l in entry.findall("a:link", ns):
            if l.get("rel", "alternate") == "alternate":
                link = l.get("href", "")
                break
        items.append({
            "title": _text(entry.find("a:title", ns)),
            "url": urldefrag(link)[0],
            "published": _text(entry.find("a:published", ns)) or _text(entry.find("a:updated", ns)),
            "summary": re.sub(r"<[^>]+>", "", _text(entry.find("a:summary", ns)) or _text(entry.find("a:content", ns)))[:300],
        })

    # 统一字段 + 兜底
    out = []
    for it in items:
        if not it["title"] or not it["url"].startswith("http"):
            continue
        it["source"] = feed["name"]
        it["feed_weight"] = feed.get("weight", 5)
        it["region"] = feed.get("region", "global")
        out.append(it)
    return out, f"ok ({len(out)})"

def heuristic_score(item):
    text = f"{item.get('title','')} {item.get('summary','')}".lower()
    hits = sum(1 for kw in AI_KEYWORDS if kw.lower() in text)
    recency = 0.5
    pub = item.get("published", "") or ""
    for fmt in ("%a, %d %b %Y %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            dt = datetime.strptime(pub[:25].strip(), fmt).replace(tzinfo=timezone.utc)
            days = (datetime.now(timezone.utc) - dt).days
            recency = 1.0 if days <= 2 else 0.8 if days <= 7 else 0.6 if days <= 30 else 0.3
            break
        except Exception:
            continue
    return round(item.get("feed_weight", 5) * (1 + min(hits, 8) * 0.35) * (0.4 + recency), 2)

def crawl(max_items_per_feed=12, top_n=60):
    feeds = load_feeds()
    seen_path = os.path.join(DATA, "seen_links.json")
    seen = set(json.load(open(seen_path, encoding="utf-8"))) if os.path.exists(seen_path) else set()
    known_domains = existing_domains()

    all_items, feed_status = [], []
    for i, feed in enumerate(feeds):
        items, status = fetch_feed(feed)
        feed_status.append({"name": feed["name"], "url": feed["url"], "status": status, "items": len(items)})
        print(f"[{i+1:2d}/{len(feeds)}] {feed['name']:<28} {status}")
        for it in items[:max_items_per_feed]:
            key = it["url"].rstrip("/").lower()
            if key in seen:
                continue
            it["score"] = heuristic_score(it)
            all_items.append(it)
        time.sleep(0.8)  # 对目标站点友好

    # 去重 + 排序
    uniq = {}
    for it in all_items:
        uniq.setdefault(it["url"].rstrip("/").lower(), it)
    ranked = sorted(uniq.values(), key=lambda x: -x["score"])[:top_n]

    # 新站点候选：不在 sites.json 中的域名
    candidates = []
    for it in ranked:
        try:
            dom = urlparse(it["url"]).hostname.lower().replace("www.", "")
        except Exception:
            continue
        if dom in known_domains:
            continue
        if dom.endswith((".gov", ".mil")):
            continue
        candidates.append({
            "name": it["source"] + " · 外链",
            "url": it["url"],
            "domain": dom,
            "title": it["title"],
            "summary": it["summary"],
            "score": it["score"],
            "region": it["region"],
            "discovered_at": datetime.now(timezone.utc).isoformat(),
            "status": "pending-review",
        })

    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "new_items.json"), "w", encoding="utf-8") as f:
        json.dump(ranked, f, ensure_ascii=False, indent=1)
    with open(os.path.join(DATA, "candidates.json"), "w", encoding="utf-8") as f:
        json.dump(candidates, f, ensure_ascii=False, indent=1)
    status = {
        "crawled_at": datetime.now(timezone.utc).isoformat(),
        "feeds_total": len(feeds),
        "feeds_ok": sum(1 for s in feed_status if s["status"].startswith("ok")),
        "feeds": feed_status,
        "new_items": len(ranked),
        "candidates": len(candidates),
    }
    with open(os.path.join(DATA, "crawler_status.json"), "w", encoding="utf-8") as f:
        json.dump(status, f, ensure_ascii=False, indent=2)
    return ranked, candidates, status

def mark_seen(items):
    seen_path = os.path.join(DATA, "seen_links.json")
    seen = set(json.load(open(seen_path, encoding="utf-8"))) if os.path.exists(seen_path) else set()
    for it in items:
        seen.add(it["url"].rstrip("/").lower())
    with open(seen_path, "w", encoding="utf-8") as f:
        json.dump(sorted(seen), f, ensure_ascii=False)

def merge_candidates(min_score=85.0):
    """把审核通过的候选站点补入 sites.json 并重建 js/data.js。返回新增数量。"""
    cand_path = os.path.join(DATA, "candidates.json")
    sites_path = os.path.join(DATA, "sites.json")
    if not os.path.exists(cand_path):
        return 0
    candidates = json.load(open(cand_path, encoding="utf-8"))
    sites = json.load(open(sites_path, encoding="utf-8"))
    have = {s["url"].rstrip("/").lower() for s in sites}
    have_domains = {urlparse(s["url"]).hostname.lower().replace("www.", "") for s in sites}
    # 同一域名只入库一次（取最高分候选），避免把 RSS 里的文章链接当成多个"新站点"
    best_per_domain = {}
    for c in candidates:
        if c.get("status") != "approved":
            continue
        if c.get("llm_score", 0) < min_score:
            continue
        dom = (c.get("domain") or "").lower().replace("www.", "")
        if not dom or dom in have_domains:
            continue
        cur = best_per_domain.get(dom)
        if cur is None or c.get("llm_score", 0) > cur.get("llm_score", 0):
            best_per_domain[dom] = c
    added = 0
    for dom, c in best_per_domain.items():
        c = dict(c)
        c["url"] = "https://" + dom + "/"
        key = c["url"].rstrip("/").lower()
        if key in have:
            continue
        sites.append({
            "name": c.get("site_name") or c.get("domain"),
            "url": c["url"],
            "desc": c.get("llm_desc") or (c.get("title") or "")[:120],
            "cat": c.get("llm_cat") or "nav",
            "subcat": "自动收录",
            "tags": ["自动收录"],
            "region": c.get("region", "global"),
            "heat": int(c.get("llm_score", 80)),
            "quality": int(c.get("llm_score", 80)),
            "stars": 0, "forks": 0, "language": "", "license": "",
            "updated": "", "source": "自动收录",
            "score": int(c.get("llm_score", 80)),
            "id": len(sites),
        })
        have.add(key)
        added += 1
    if added:
        json.dump(sites, open(sites_path, "w", encoding="utf-8"), ensure_ascii=False)
        rebuild_js_data(sites)
    return added

def rebuild_js_data(sites=None):
    """根据 data/sites.json + data/stats.json 重建 js/data.js，并同步统计。"""
    sites = sites or json.load(open(os.path.join(DATA, "sites.json"), encoding="utf-8"))
    max_id = max((s.get("id", i) for i, s in enumerate(sites)), default=len(sites))
    for i, s in enumerate(sites):
        s["id"] = s.get("id", i)
    cats = {}
    for s in sites:
        cats[s["cat"]] = cats.get(s["cat"], 0) + 1
    stats = {
        "total": len(sites),
        "categories": cats,
        "curated": sum(1 for s in sites if s.get("source") == "精选"),
        "github": sum(1 for s in sites if s.get("source") == "GitHub"),
        "auto": sum(1 for s in sites if s.get("source") == "自动收录"),
        "total_stars": sum(s.get("stars", 0) for s in sites),
        "updated": datetime.now().strftime("%Y-%m-%d"),
    }
    with open(os.path.join(DATA, "stats.json"), "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    with open(os.path.join(ROOT, "js", "data.js"), "w", encoding="utf-8") as f:
        f.write("// AI热榜导航 · 数据集（自动生成，请勿手改）\nwindow.SITES=")
        json.dump(sites, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\nwindow.STATS=")
        json.dump(stats, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")
