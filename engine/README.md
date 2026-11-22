# AI 引擎（自动抓取 + 日报生成）

纯 Python 标准库实现，无需 pip 安装。默认模型服务：**mosi.cn · nex-n2.6（Nex N2.6）**，OpenAI 兼容协议。

## 快速开始

```bash
# 1) 配置模型密钥（二选一）
export MODEL_API_KEY="sk-..."                 # 本地 / CI Secret
# 或创建未提交到 git 的 .env 后自行 source

# 2) 一键跑通：抓取 → 审核 → 合并 → 日报
python3 engine/run.py all
```

## 子命令

| 命令 | 作用 | 产物 |
| --- | --- | --- |
| `crawl` | 抓取 40+ RSS 信源，启发式打分、去重 | `data/new_items.json` `data/candidates.json` `data/crawler_status.json` |
| `review` | 调用模型给候选站点打质量分/分类/简介（≥85 且模型判定 keep 才通过） | 更新 `data/candidates.json` |
| `merge` | 把通过审核的候选补入站点库并重建前端数据 | `data/sites.json` `js/data.js` |
| `digest` | 用模型把 Top 28 条资讯写成结构化中文日报 | `data/digests/*.json` `data/digest.json` |
| `all` | 上述四步流水线（CI 每日任务） | 全部 |

## 模型配置（自定义模型服务）

默认配置在 `engine/model_config.json`（**不含密钥**）：

```json
{ "base_url": "https://api.mosi.cn/v1/chat/completions", "model": "nex-n2.6",
  "model_display": "Nex N2.6 (mosi.cn)", "temperature": 0.7, "max_tokens": 2400 }
```

环境变量覆盖任意项：`MODEL_BASE_URL` `MODEL_NAME` `MODEL_API_KEY` `MODEL_TEMPERATURE` `MODEL_MAX_TOKENS`。
任何 OpenAI 兼容服务（DeepSeek / 通义 / 月之暗面 / OpenAI / 本地 vLLM…）只需替换上述变量即可，无需改代码。

## 安全说明

- `MODEL_API_KEY` 只从环境变量读取，代码库与前端产物中均不含密钥。
- GitHub Actions 通过仓库 Secret `MODEL_API_KEY` 注入（Settings → Secrets and variables → Actions）。
- 前端页面上的「模型配置」面板仅做**本浏览器**级临时覆盖与连通性测试，配置存于 localStorage，不落服务器（本站为纯静态页面）。
