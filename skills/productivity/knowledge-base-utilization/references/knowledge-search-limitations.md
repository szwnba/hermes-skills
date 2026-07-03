# Knowledge Search Limitations

## Problem (2026-06-28)

Tried to match Todoist tasks against 308 Obsidian articles using keyword search. Results were poor:

| Issue | Example |
|-------|---------|
| Too-specific phrases match nothing | "情报收集器要每天定期收集的" → 0 matches |
| Common words match everything | "AI" → 285 matches (useless) |
| Empty article bodies | Many articles have only frontmatter, no content |
| Chinese tokenization | No NLP library → pure string matching fails on phrases |

## Root Causes

1. **Article quality variance**: 1KB-10KB, many are Tavily shells
2. **No Chinese NLP**: Simple `in` operator can't handle phrase matching
3. **Vault structure**: 308 raw files, only 13 wiki summaries — too granular for search

## Recommended Approach

1. **Search Wiki first** — 13 theme pages have structured summaries
2. **Use broad keywords** — 2-3 core terms, not full task titles
3. **Fall back to web_search** — When vault has no depth on a topic
4. **Supplement the vault** — Add deep reference articles for key tools (TrendRadar, ComfyUI, xurl, etc.)

## When Vault Search Works Well

- Topic-level queries: "What do we know about Browser-Use?" (27 articles)
- Theme navigation: Browse Wiki pages for structured overviews
- Frontmatter filtering: "Show me all ⭐⭐⭐⭐⭐ rated articles in OpenClaw"

## When It Fails

- Specific task matching: "How do I build a daily intelligence collector?"
- Cross-topic synthesis: "Compare all my notes on AI testing frameworks"
- Deep technical queries: "What's the best way to scrape WeChat articles?"
