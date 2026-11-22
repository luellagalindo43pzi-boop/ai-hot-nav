# AI热榜导航 · AI HOT NAV

> **2456 个优质 AI 站点，一站直达，热度排序。**
> AI 日报周报 · GitHub 趋势榜 · 开源热榜 · AI 学术前沿 · 工具导航 · 提示词知识库 —— 按 **热度 × 质量** 智能排序推荐。

🌐 **在线访问**：https://ravenculbertsonzqgqq-ux.github.io/ai-hot-nav/

## ✨ 特性

- **2456 条收录**：302 项人工精选（AI日报/周报/工具导航/学术前沿/科技媒体/提示词知识库）+ **2154 个 GitHub 高星 AI 开源项目**（累计 3200 万+ Stars，非 fork、非归档，数据快照 2026-11-23）
- **热度 × 质量 双分制排序**：
  - 精选站点：编辑评估的热度 / 质量分（0–100）
  - GitHub 项目：热度 = `20 × log₁₀(Stars)` 归一化；质量分综合 Stars、Forks、近期活跃度（pushed_at）、描述与 License 完整度
  - 综合分 = 热度 × 0.65 + 质量 × 0.35
- **全功能前端**：实时搜索（支持 `/` 快捷键）、11 个分类筛选、中文圈/全球区域过滤、精选/GitHub 来源过滤、5 种排序（综合/热度/质量/Stars/最近更新）、网格/列表双视图、深色/浅色主题（跟随系统 + 手动切换）
- **TOP 榜单**：GitHub Stars 榜 / 综合质量榜 / 精选站点榜，实时生成 TOP 20
- **Google Material 3 设计**：Google 品牌四色 × 现代 M3 组件语言，纯静态、零依赖、秒开

## 📂 分类

| 分类 | 数量 |
| --- | --- |
| GitHub 高星开源项目 | 2154 |
| 学术 · 前沿实验室 / 论文 | 46 |
| 大模型平台（官方/开放平台） | 43 |
| AI日报 · 资讯流 | 41 |
| AI导航 · 工具索引 | 38 |
| 科技媒体 AI 专栏 | 36 |
| 提示词 · 知识库 · RSS | 28 |
| GitHub趋势榜 · 开源热榜 | 26 |
| 开发者社区 | 25 |
| 评测 · 榜单 | 20 |

## 🛠 技术栈

纯静态站点：HTML + CSS（Material 3 设计系统，CSS 变量驱动深浅双主题）+ 原生 JavaScript（零框架零构建）。
数据管线：Python 脚本整合人工精选种子 + GitHub Search API（按 Stars 排序、去 fork/归档、去重），输出 `js/data.js`。

## 📁 目录结构

```
index.html          # 页面结构（应用栏 / Hero / 工具条 / 卡片 / 页脚 / TOP弹窗）
css/style.css       # Material 3 设计系统（Google 四色 + CSS 变量双主题）
js/app.js           # 搜索/过滤/排序/渲染/TOP榜/主题 全部交互逻辑
js/data.js          # 2456 条站点数据（SITES + STATS）
data/               # 原始数据与种子（精选 / GitHub 抓取 / 合并结果）
fetch_repos*.py     # GitHub Search API 抓取脚本
build_dataset.py    # 评分归一化 + 分类聚合 + 合并
```

## 🔄 数据更新

```bash
export GH_TOKEN=<your_github_token>
python3 fetch_repos.py   # 抓取 GitHub 高星 AI 项目（需 Search 权限）
python3 build_dataset.py # 重新计算评分并合并
python3 -c "import json; sites=json.load(open('data/sites.json')); open('js/data.js','w').write('window.SITES=%s;' % json.dumps(sites, ensure_ascii=False, separators=(',',':')))"
```

## ⚠️ 免责声明

本站为导航索引，所有外链指向第三方站点，其内容版权归原站点所有。收录不代表背书，请自行甄别。
精选站点的热度/质量分为编辑主观评估；GitHub 项目数据为 2026-11-23 的 API 快照，Stars 数会随时间变化。
