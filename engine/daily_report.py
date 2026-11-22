"""AI热榜导航 · AI 日报生成器

流程：crawl（或使用已有 new_items.json）→ 取 Top N → 调用默认模型服务（mosi.cn / nex-n2.6）
生成结构化中文日报 → 写入 data/digests/YYYY-MM-DD.json + data/digest.json（前端直接读取）
未配置 MODEL_API_KEY 时回退为本地模板日报（明确标注，不假装是模型生成）。
"""
import json
import os
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model_client import load_config, chat_json, chat_completion  # noqa: E402
import crawler  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
TZ = timezone(timedelta(hours=8))  # Asia/Shanghai


def llm_review_candidates(limit=12):
    """用模型对新站点候选打质量分并归类；写回 candidates.json。"""
    cand_path = os.path.join(DATA, "candidates.json")
    if not os.path.exists(cand_path):
        return 0
    candidates = json.load(open(cand_path, encoding="utf-8"))
    pending = [c for c in candidates if c.get("status") == "pending-review"][:limit]
    if not pending:
        return 0
    cfg = load_config()
    if not cfg.get("api_key"):
        print("[review] 未配置 MODEL_API_KEY，跳过候选审核")
        return 0

    listing = "\n".join(
        f"{i+1}. 域名:{c['domain']} | 标题:{c['title'][:80]} | 摘要:{c['summary'][:120]}"
        for i, c in enumerate(pending)
    )
    prompt = f"""你是 AI 站点质量审核员。以下是从 AI 资讯 RSS 中发现的候选新站点/新链接，请逐个评估：
{listing}

请严格只输出 JSON（不要 Markdown 包裹），格式：
{{"reviews":[{{"index":1,"site_name":"站点名","quality":0-100,"category":"daily|nav|research|media|resource|community|benchmark|llm|trending","desc":"一句话中文简介（≤60字）","keep":true或false}}]}}
评分标准：AI 领域专业度、内容质量、长期价值；明显是广告/采集站/低质内容农场给 <40 分并 keep=false。"""
    try:
        result = chat_json([{"role": "user", "content": prompt}], cfg=cfg, max_tokens=1800)
        reviews = {r["index"]: r for r in result.get("reviews", [])}
        for i, c in enumerate(pending):
            r = reviews.get(i + 1)
            if not r:
                continue
            c["llm_score"] = int(r.get("quality", 0))
            c["llm_cat"] = r.get("category") or "nav"
            c["llm_desc"] = (r.get("desc") or "")[:120]
            c["site_name"] = r.get("site_name") or c["domain"]
            c["status"] = "approved" if (r.get("keep") and c["llm_score"] >= 85) else "rejected"
        json.dump(candidates, open(cand_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        approved = sum(1 for c in candidates if c.get("status") == "approved")
        print(f"[review] 审核 {len(pending)} 个候选，累计通过 {approved} 个")
        return approved
    except Exception as e:  # noqa: BLE001
        print(f"[review] 模型审核失败（不影响日报生成）：{e}")
        return 0


def build_digest_with_llm(items, cfg):
    # 注意：Nex N2.6 的 reasoning 会消耗 completion 额度，输入过大时 content 会被吃空。
    # 实测：14 条（≤80字摘要）+ max_tokens=6500 可稳定产出 finish_reason=stop 的合法 JSON。
    picked = items[:14]
    listing = "\n".join(
        f"[{i+1}] {it['source']}|{it['title']}|{it['url']}|{it.get('summary','')[:80]}"
        for i, it in enumerate(picked)
    )
    prompt = f"""基于以下AI资讯清单生成日报JSON。清单：
{listing}

要求：只输出紧凑JSON（不要Markdown、不要解释、不要英文双引号，引用用「」）。
结构：{{"overview":"100字总览（含具体事件/公司/模型名）","sections":[{{"title":"板块名","items":[{{"title":"中文标题≤36字","url":"原样复制清单url","source":"来源","one_liner":"≤60字","impact":"high|medium|low"}}]}}]}}
sections 分3-5个板块（大模型与产品 / 开源与GitHub / 学术前沿 / 产业·投融资·政策 / 工具与实践）按重要性排序；url必须原样来自清单；impact=high仅给3-4条；不得编造清单外事件。"""
    messages = [
        {"role": "system", "content": "直接输出JSON对象，不输出任何思考过程，不输出Markdown代码块，不输出解释。"},
        {"role": "user", "content": prompt},
    ]
    last_err = None
    for attempt in range(2):
        try:
            result = chat_json(messages, cfg=cfg, max_tokens=6500, temperature=0.3)
            result["_usage"] = result.get("_usage", {})
            return result
        except Exception as e:  # noqa: BLE001
            last_err = e
            messages.append({"role": "user", "content": "上一次输出无法解析，请重新输出：只输出一个合法JSON对象，字符串内不得出现英文双引号。"})
            print(f"[digest] 第 {attempt+1} 次解析失败，重试…")
    raise last_err


def fallback_digest(items, reason):
    sections = {}
    for it in items[:24]:
        src = it["source"]
        sections.setdefault(src, []).append({
            "title": it["title"][:80],
            "url": it["url"],
            "source": src,
            "one_liner": (it.get("summary") or "（无摘要）")[:80],
            "impact": "medium",
        })
    return {
        "overview": f"今日自动抓取 {len(items)} 条有效 AI 资讯（本版为本地模板日报：{reason}）。配置 MODEL_API_KEY 后即可生成模型撰写的深度总览与分板块解读。",
        "sections": [{"title": f"信源 · {k}", "items": v} for k, v in list(sections.items())[:6]],
        "_usage": {},
        "_fallback": reason,
    }


def write_digests(digest, model_label, cfg):
    date_str = datetime.now(TZ).strftime("%Y-%m-%d")
    out = {
        "date": date_str,
        "title": f"AI热榜日报 · {date_str}",
        "generated_at": datetime.now(TZ).isoformat(timespec="seconds"),
        "model": model_label,
        "item_count": sum(len(s.get("items", [])) for s in digest.get("sections", [])),
        "overview": digest.get("overview", ""),
        "sections": digest.get("sections", []),
        "usage": digest.get("_usage", {}),
    }
    digest_dir = os.path.join(DATA, "digests")
    os.makedirs(digest_dir, exist_ok=True)
    with open(os.path.join(digest_dir, f"{date_str}.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    with open(os.path.join(DATA, "digest.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    # 历史索引
    idx_path = os.path.join(digest_dir, "index.json")
    dates = set()
    for fn in os.listdir(digest_dir):
        if fn.endswith(".json") and fn != "index.json":
            dates.add(fn[:-5])
    dates = sorted(dates, reverse=True)
    with open(idx_path, "w", encoding="utf-8") as f:
        json.dump({"latest": date_str, "dates": dates}, f, ensure_ascii=False, indent=1)
    return date_str


def generate(items=None, reuse_existing=True):
    cfg = load_config()
    items_path = os.path.join(DATA, "new_items.json")
    if items is None:
        if reuse_existing and os.path.exists(items_path):
            items = json.load(open(items_path, encoding="utf-8"))
            if items:
                print(f"[digest] 使用已有 new_items.json（{len(items)} 条）")
        if items is None:
            print("[digest] 未找到 new_items.json，先执行抓取…")
            items, _, _ = crawler.crawl()
    if not items:
        print("[digest] 无可用条目，终止")
        return None

    if cfg.get("api_key"):
        try:
            digest = build_digest_with_llm(items, cfg)
            model_label = cfg.get("model_display") or cfg["model"]
            print(f"[digest] 模型生成完成（{model_label}）")
        except Exception as e:  # noqa: BLE001
            print(f"[digest] 模型生成失败，回退本地模板：{e}")
            digest = fallback_digest(items, str(e)[:120])
            model_label = "本地模板回退"
    else:
        digest = fallback_digest(items, "未配置 MODEL_API_KEY")
        model_label = "本地模板回退"

    date_str = write_digests(digest, model_label, cfg)
    crawler.mark_seen(items)
    print(f"[digest] 已写入 digests/{date_str}.json 与 digest.json")
    return date_str


if __name__ == "__main__":
    generate()
