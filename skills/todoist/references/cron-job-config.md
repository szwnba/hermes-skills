# Cron Job: Todoist + Knowledge Base Analysis

## Job Configuration (2026-06-28)

**Job ID**: `2bfa791c177d`
**Name**: Todoist 任务 + 知识库智能方案
**Schedule**: Every 1 hour
**Deliver**: origin (this conversation)

## What It Does

1. Lists all incomplete Todoist tasks
2. Searches Obsidian knowledge base for matching solutions
3. Outputs a prioritized analysis with recommendations

## Known Issues

- Keyword matching against 308 articles is unreliable (see `../knowledge-base-utilization/references/knowledge-search-limitations.md`)
- Many articles are shallow (Tavily shells with empty content)
- False positives on common words (AI, 测试, etc.)

## Recommended Improvement

Change from hourly to weekly, and focus on:
1. New articles added since last run
2. Tasks marked as high priority
3. Cross-reference with Wiki themes (not raw articles)
