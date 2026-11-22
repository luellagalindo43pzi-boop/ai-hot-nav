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
