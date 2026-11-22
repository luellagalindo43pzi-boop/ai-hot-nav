import json, math, hashlib
from datetime import date

TODAY = date(2026, 11, 23)

def heat_from_stars(stars):
    return max(40, min(99, round(20 * math.log10(max(stars, 10)))))

def quality_from_repo(r):
    heat = heat_from_stars(r["stars"])
    forks = r.get("forks", 0)
    fork_comp = min(15, round(3.5 * math.log10(forks + 1)))
    try:
        pushed = date.fromisoformat(r["pushed_at"])
        days = (TODAY - pushed).days
    except Exception:
        days = 9999
    rec = 15 if days < 30 else 12 if days < 90 else 9 if days < 180 else 6 if days < 365 else 3
    desc = 10 if r.get("desc") else 0
    lic = 5 if r.get("license") else 0
    return max(20, min(99, round(heat * 0.55) + fork_comp + rec + desc + lic))

def subcat_from_topics(topics):
    t = set(topics or [])
    rules = [
        ("MCP / 工具调用", {"mcp", "model-context-protocol", "mcp-server", "mcp-client"}),
        ("AI Agent 智能体", {"ai-agent", "llm-agent", "agents", "agentic", "autonomous-agents", "ai-agents"}),
        ("AI 绘图 / 图像生成", {"stable-diffusion", "diffusion-models", "text-to-image", "comfyui", "flux", "ai-art", "image-generation"}),
        ("语音 / 音频", {"whisper", "speech-recognition", "tts", "asr", "text-to-speech", "audio", "voice"}),
        ("RAG / 检索增强", {"rag", "retrieval-augmented-generation", "vector-database", "embeddings", "llama-index"}),
        ("推理部署 / LLMOps", {"llm-inference", "vllm", "ollama", "inference", "llm-serving", "llmops", "model-serving"}),
        ("训练 / 微调", {"fine-tuning", "rlhf", "training", "pretraining", "lora", "qlora", "deepspeed", "llm-training"}),
        ("计算机视觉", {"computer-vision", "object-detection", "opencv", "image-segmentation", "vision"}),
        ("NLP / 大语言模型", {"nlp", "natural-language-processing", "large-language-models", "llm", "llms", "transformers", "bert", "gpt", "text-generation"}),
        ("强化学习 / 机器人", {"reinforcement-learning", "robotics", "embodied-ai", "robot-learning"}),
        ("多模态", {"multimodal", "vision-language", "vision-language-model", "multi-modal"}),
        ("深度学习框架", {"pytorch", "tensorflow", "jax", "deep-learning", "machine-learning", "neural-network", "keras"}),
        ("数据集 / 评测", {"dataset", "datasets", "benchmark", "benchmarks"}),
        ("Awesome 合集", {"awesome", "awesome-list", "curated-list"}),
        ("ChatGPT / OpenAI 生态", {"chatgpt", "openai", "openai-api", "gpt-4", "chatgpt-api"}),
    ]
    for name, keys in rules:
        if t & keys:
            return name
    return "其他 AI 项目"

curated = json.load(open("data/curated.json"))
repos = json.load(open("data/repos.json"))

out = []
for e in curated:
    out.append({
        "name": e["name"], "url": e["url"], "desc": e["desc"],
        "cat": e["cat"], "subcat": "", "tags": e.get("tags", [])[:4],
        "region": e.get("region", "global"),
        "heat": e["heat"], "quality": e["quality"],
        "stars": 0, "forks": 0, "language": "", "license": "",
        "updated": "", "source": "精选",
    })

for r in repos:
    heat = heat_from_stars(r["stars"])
    quality = quality_from_repo(r)
    subcat = subcat_from_topics(r.get("topics", []))
    tags = [t for t in r.get("topics", [])][:4]
    if r.get("language"):
        tags = [r["language"]] + tags
    out.append({
        "name": r["name"], "url": r["url"],
        "desc": r["desc"] or "（暂无英文简介，详见仓库 README）",
        "cat": "github", "subcat": subcat, "tags": tags[:5],
        "region": "global",
        "heat": heat, "quality": quality,
        "stars": r["stars"], "forks": r.get("forks", 0),
        "language": r.get("language") or "",
        "license": r.get("license") or "",
        "updated": r.get("pushed_at") or "", "source": "GitHub",
    })

# composite ranking score
for e in out:
    e["score"] = round(e["heat"] * 0.65 + e["quality"] * 0.35)

# assign ids stable by url hash
for i, e in enumerate(out):
    e["id"] = i

out.sort(key=lambda e: -e["score"])
json.dump(out, open("data/sites.json", "w"), ensure_ascii=False, indent=None)

cats = {}
for e in out:
    cats[e["cat"]] = cats.get(e["cat"], 0) + 1
total_stars = sum(e["stars"] for e in out)
stats = {
    "total": len(out),
    "categories": cats,
    "curated": len(curated),
    "github": len(repos),
    "total_stars": total_stars,
    "updated": "2026-11-23",
}
json.dump(stats, open("data/stats.json", "w"), ensure_ascii=False, indent=2)
print(json.dumps(stats, ensure_ascii=False, indent=2))
