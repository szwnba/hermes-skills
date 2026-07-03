# Task-to-Knowledge-Base Matching Workflow

> **Created**: 2026-06-28 | **Updated**: 2026-06-28 (v3 — domain-hint mapping)
> **Source**: Live cron job sessions with 12 Todoist tasks × 308 Obsidian articles
> **Use**: Reference for cron jobs that must match tasks against a knowledge vault

## Problem

Todoist tasks are short, goal-oriented phrases. Matching them against a 308-article Obsidian vault using naive keyword search produces poor results:
- Too-specific phrases match 0 articles (e.g. "情报收集器要每天定期收集的")
- Too-common words match everything (e.g. "AI" appears in 285+ articles)
- Many articles are hollow shells (frontmatter only, no body content)

## Solution v3: Domain-Hint Mapping + Category-Scoped Search

**Result: match rate improved from 8% (1/12) to 100% (12/12)**

A standalone Python script (`scripts/cron_matcher.py`) does all mechanical matching, then the cron LLM enhances and formats the output.

### Architecture

```
Todoist API → tasks
     ↓
Domain Hint Mapping (keyword → target Wiki categories)
     ↓
Category-Scoped Search (only search within matched categories, not all 308)
     ↓
Quality Filter (only articles >1500 chars)
     ↓
Short 2-char keyword matching
     ↓
Pre-defined advice per domain
     ↓
LLM enhancement (filter weak matches, add actionable steps)
```

### Key Techniques

1. **Domain Hint Table** — pre-defined mapping from task keywords to Wiki categories + search terms + actionable advice. This replaces manual keyword guessing:

```python
DOMAIN_HINTS = {
    "github": {
        "cats": ["OpenClaw", "Claude Code & OpenCode", "开源工具"],
        "search_terms": ["github", "trending", "开源", "star"],
        "advice": "可用 Hermes cron 定时拉取 GitHub Trending + arXiv"
    },
    "知识库": {
        "cats": ["Hermes", "AI Agent", "AI 理念与范式"],
        "search_terms": ["知识库", "obsidian", "记忆", "sqlite", "wiki"],
        "advice": "已有 Obsidian 308篇 + Wiki 13主题"
    },
    # ... 25+ domain entries
}
```

2. **Short 2-char Chinese keywords** — extract `[\u4e00-\u9fff]{2}` instead of long phrases. "情报收集器要每天定期收集的" → ["情报", "收集", "定期"]

3. **Category-scoped search** — only search articles within matched Wiki categories, not the full 308. Dramatically reduces false positives.

4. **Quality filter** — only search articles with `content_length > 1500`. Eliminates empty shells.

5. **Threshold: 2 keyword matches** — require ≥2 keyword hits in article body for a valid match.

### Metadata Dependency

The script requires `/tmp/articles_meta.json` — a cached metadata index of all Inbox articles with fields: `filename`, `title`, `folder_normalized`, `content_length`, `quality`, `url`. If this file is stale or missing, regenerate from Inbox frontmatter.

### Script Location

``~/.hermes/profiles/collector/scripts/cron_matcher.py``

Cron job runs this script, then LLM filters top-2 matches per task and adds actionable advice.

## Previous Approach (v1-v2, deprecated)

Wiki-first matching using manual keyword extraction. Superseded by v3 due to 8% match rate. Details preserved for reference only.

## Vault Structure (Obsidian)

```
/path/to/vault/
├── 00_Inbox/     (308 raw articles, various quality)
├── 20_Wiki/      (13 theme pages, pre-summarized)
│   ├── INDEX.md
│   ├── AI_Agent.md      (15 articles, 82KB)
│   ├── OpenClaw.md      (41 articles, 233KB)
│   ├── Playwright_AI.md (40 articles, 201KB)
│   ├── 测试工程.md     (37 articles, 216KB)
│   ├── 投资与变现.md    (36 articles, 62KB)
│   ├── 浏览器自动化.md  (27 articles, 116KB)
│   ├── AI_Skill.md      (24 articles, 82KB)
│   ├── Claude_Code_and_OpenCode.md (23, 129KB)
│   ├── AI_理念与范式.md  (23 articles, 175KB)
│   ├── Onboarding.md    (21 articles, 126KB)
│   ├── Hermes.md        (10 articles, 61KB)
│   ├── 开源工具.md      (10 articles, 58KB)
│   └── 其他.md          (1 article, 0KB)
└── 30_Outputs/    (generated reports)
```
