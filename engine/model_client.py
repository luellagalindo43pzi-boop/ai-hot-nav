"""AI热榜导航 · 模型服务客户端（OpenAI 兼容协议）

默认配置见 engine/model_config.json（mosi.cn / nex-n2.6），
API Key 仅通过环境变量 MODEL_API_KEY 注入，绝不落盘。
环境变量可覆盖任意默认项：
  MODEL_BASE_URL · MODEL_API_KEY · MODEL_NAME · MODEL_TEMPERATURE · MODEL_MAX_TOKENS
  MODEL_API_KEY_AGNES (optional secondary fallback) · MODEL_AGNES_BASE_URL · MODEL_AGNES_NAME
"""
import json
import re
import os
import time
import urllib.request
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))


def load_config():
    cfg_path = os.path.join(HERE, "model_config.json")
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    cfg.pop("_comment", None)
    cfg["base_url"] = os.environ.get("MODEL_BASE_URL", cfg["base_url"])
    cfg["model"] = os.environ.get("MODEL_NAME", cfg["model"])
    cfg["model_display"] = os.environ.get(
        "MODEL_NAME", cfg.get("model_display") or cfg["model"]
    )
    if os.environ.get("MODEL_TEMPERATURE"):
        cfg["temperature"] = float(os.environ["MODEL_TEMPERATURE"])
    if os.environ.get("MODEL_MAX_TOKENS"):
        cfg["max_tokens"] = int(os.environ["MODEL_MAX_TOKENS"])
    cfg["api_key"] = os.environ.get("MODEL_API_KEY", "")
    # Secondary provider is enabled only when its private Actions/environment secret exists.
    configured_fallbacks = cfg.get("fallbacks", [])
    active_fallbacks = []
    for fallback in configured_fallbacks:
        key = os.environ.get(fallback.get("api_key_env", ""), "")
        if key:
            active_fallbacks.append({
                **fallback,
                "base_url": os.environ.get("MODEL_AGNES_BASE_URL", fallback["base_url"]),
                "model": os.environ.get("MODEL_AGNES_NAME", fallback["model"]),
                "api_key": key,
            })
    cfg["fallbacks"] = active_fallbacks
    return cfg


def chat_completion(messages, cfg=None, temperature=None, max_tokens=None, timeout=None):
    """调用 OpenAI 兼容 /chat/completions，返回 (content, raw_json)。失败抛 RuntimeError。"""
    cfg = cfg or load_config()
    if not cfg.get("api_key"):
        raise RuntimeError("MODEL_API_KEY 未配置（请设置环境变量或 GitHub Actions Secret）")

    body = {
        "model": cfg["model"],
        "messages": messages,
        "temperature": cfg["temperature"] if temperature is None else temperature,
        "max_tokens": cfg["max_tokens"] if max_tokens is None else max_tokens,
    }
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        cfg["base_url"],
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {cfg['api_key']}",
            "Content-Type": "application/json",
            "User-Agent": "ai-hot-nav-engine/2.0",
        },
    )
    timeout = timeout or cfg.get("timeout_seconds", 120)
    last_err = None
    for attempt in range(1, int(cfg.get("retries", 2)) + 2):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            message = payload["choices"][0]["message"]
            content = message.get("content") or ""
            if not content.strip():
                raise RuntimeError("模型响应成功但 content 为空（推理链可能耗尽输出额度）")
            return content.strip(), payload
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="replace")[:500]
            last_err = f"HTTP {e.code}: {detail}"
            # 4xx 属于请求问题，重试无意义
            if 400 <= e.code < 500:
                break
        except Exception as e:  # noqa: BLE001
            last_err = f"{type(e).__name__}: {e}"
        if attempt <= int(cfg.get("retries", 2)):
            time.sleep(2 * attempt)
    # If primary provider fails (including empty response), try configured private fallbacks.
    for fallback in cfg.get("fallbacks", []):
        alt_cfg = {**cfg, **fallback, "fallbacks": []}
        print(f"[model] 主模型不可用，切换候选服务：{alt_cfg.get('model_display', alt_cfg['model'])}")
        try:
            return chat_completion(messages, cfg=alt_cfg, temperature=temperature, max_tokens=max_tokens, timeout=timeout)
        except Exception as fallback_err:  # noqa: BLE001
            last_err = f"primary={last_err}; fallback={fallback_err}"
    raise RuntimeError(f"模型服务调用失败（{cfg['base_url']}）：{last_err}")


def chat_json(messages, cfg=None, **kwargs):
    """要求模型返回 JSON 并解析；容忍 ```json 包裹。"""
    content, raw = chat_completion(messages, cfg=cfg, **kwargs)
    text = content.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise RuntimeError(f"模型未返回 JSON：{content[:200]}")
    body = text[start:end + 1]
    body = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", " ", body)
    body = re.sub(r",\s*([}\]])", r"\1", body)  # 去掉尾随逗号
    try:
        parsed = json.loads(body, strict=False)
    except json.JSONDecodeError:
        # 常见问题：字符串内未转义的英文双引号 → 尝试成对转义
        fixed = re.sub(r":\s*\"", ": \"", body)
        fixed = body
        # 粗暴修复：把中文引号还原法不可靠，直接报原始错误便于重试
        raise RuntimeError(f"JSON解析失败：{body[:300]}")
    parsed["_usage"] = (raw or {}).get("usage", {})
    parsed["_model"] = (raw or {}).get("model", "")
    return parsed
