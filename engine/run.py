"""AI热榜导航 · 引擎入口
用法：
  python3 engine/run.py crawl    # 仅抓取
  python3 engine/run.py review   # 仅 LLM 审核候选站点
  python3 engine/run.py merge    # 审核通过的候选补入 sites.json 并重建 js/data.js
  python3 engine/run.py digest   # 生成 AI 日报（默认使用已有 new_items.json）
  python3 engine/run.py all      # crawl → review → merge → digest（CI 每日任务）
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import crawler  # noqa: E402
import daily_report  # noqa: E402
import web_search  # noqa: E402


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd == "crawl":
        crawler.crawl()
    elif cmd == "review":
        daily_report.llm_review_candidates()
    elif cmd == "merge":
        added = crawler.merge_candidates()
        print(f"[merge] 新增 {added} 个站点")
    elif cmd == "digest":
        daily_report.generate()
    elif cmd == "all":
        print("═" * 52, "\nSTEP 1/4 抓取 RSS 信源\n", "═" * 52)
        items, candidates, status = crawler.crawl()
        print(f"抓取完成：{status['feeds_ok']}/{status['feeds_total']} 个信源成功，{len(items)} 条有效资讯，{len(candidates)} 个新站点候选")
        web_items = web_search.search_for_digest(topic=os.environ.get('DIGEST_TOPIC', 'AI'), days=int(os.environ.get('DIGEST_DAYS', '2')), limit_per_query=4)
        if web_items:
            # Reserve slots for quality RSS sources and Tavily web results; remove URL duplicates.
            known = {x.get('url', '').rstrip('/').lower() for x in items}
            fresh_web = [x for x in web_items if x.get('url', '').rstrip('/').lower() not in known]
            items = items[:10] + fresh_web[:4]
            import json
            with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'new_items.json'), 'w', encoding='utf-8') as f:
                json.dump(items, f, ensure_ascii=False, indent=1)
            print(f"联网搜索：合并 {min(len(fresh_web), 4)} 条 Tavily 网络结果到本次日报")
        print("═" * 52, "\nSTEP 2/4 模型审核候选站点\n", "═" * 52)
        daily_report.llm_review_candidates()
        print("═" * 52, "\nSTEP 3/4 合并通过审核的候选到站点库\n", "═" * 52)
        added = crawler.merge_candidates()
        print(f"新增入库：{added} 个")
        print("═" * 52, "\nSTEP 4/4 生成 AI 日报\n", "═" * 52)
        daily_report.generate(items=items)
        print("\n全部完成 ✓")
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
