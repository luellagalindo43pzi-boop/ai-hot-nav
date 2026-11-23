# AI 引擎（自动抓取 + 日报生成）

纯 Python 标准库实现，无需 pip 安装。默认模型服务：**mosi.cn · nex-n2.6（Nex N2.6）**，OpenAI 兼容协议。

## 快速开始

```bash
# 1) 配置密钥（Tavily 可选）
export MODEL_API_KEY="..."  # mosi.cn / 其它 OpenAI-compatible 模型服务
export TAVILY_API_KEY="..." # 可选：联网补充搜索结果

# 2) 一键跑通：抓取 → 审核 → 合并 → 搜索 → 日报
DIGEST_TOPIC='AI Agent 与开源框架' DIGEST_DAYS=3 python3 engine/run.py all
```

## 子命令

| 命令 | 作用 | 产物 |
| --- | --- | --- |
| `crawl` | 抓取 40+ RSS 信源，启发式打分、去重 | `data/new_items.json` `data/candidates.json` `data/crawler_status.json` |
| `review` | 调用模型给候选站点打质量分/分类/简介（≥85 且模型判定 keep 才通过） | 更新 `data/candidates.json` |
| `merge` | 把通过审核的候选补入站点库并重建前端数据 | `data/sites.json` `js/data.js` |
| `digest` | 用模型把精选资讯写成结构化中文日报 | `data/digests/*.json` `data/digest.json` |
| `all` | RSS 抓取 → 候选审核 → 合并 → 可选 Tavily 搜索 → 日报（每 6 小时） | 全部 |

## 模型配置（自定义模型服务）

默认配置在 `engine/model_config.json`（**不含密钥**）：

```json
{ "base_url": "https://api.mosi.cn/v1/chat/completions", "model": "nex-n2.6",
  "model_display": "Nex N2.6 (mosi.cn)", "temperature": 0.7, "max_tokens": 2400 }
```

环境变量覆盖任意项：`MODEL_BASE_URL` `MODEL_NAME` `MODEL_API_KEY` `MODEL_TEMPERATURE` `MODEL_MAX_TOKENS`。
任何 OpenAI 兼容服务（DeepSeek / 通义 / 月之暗面 / OpenAI / 本地 vLLM…）只需替换上述变量即可，无需改代码。

## 安全说明

- `MODEL_API_KEY` 与 `TAVILY_API_KEY` 只从环境变量读取，代码库与前端产物中均不含服务端密钥。
- GitHub Actions 通过仓库 Secret `MODEL_API_KEY`、`TAVILY_API_KEY` 注入（Settings → Secrets and variables → Actions）。
- 前端页面上的模型与 Tavily 配置仅做**本浏览器**级直连，不访问仓库 Actions Secret；浏览器 CORS 与第三方条款适用。
- 本地 stdio MCP server 提供目录搜索、最新日报、GitHub Search 和可选 Tavily `search_web`。配置 `TAVILY_API_KEY` 于你信任的 MCP host 环境，不要放入公开配置文件。
