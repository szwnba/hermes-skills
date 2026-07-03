# 情报官 Agent (Intelligence Officer)

情报收集 Agent，每日从多个渠道获取 AI/科技情报并生成结构化报告。

## 数据源

| 来源 | 方式 | 内容 |
|------|------|------|
| GitHub Trending | GitHub API + Token | 最近24h Star 增长最快的仓库 |
| arXiv | export.arxiv.org API | cs.AI / cs.LG 最新论文 |
| RSS/Blogs | blogwatcher-cli | 已订阅博客的最新文章 |
| X/Twitter | xurl CLI | AI Agent 相关推文 |
| Web Search | Tavily AI | 科技/AI 行业新闻 |

## 调度

通过 Hermes cron 每天 08:00 (北京时间) 运行，结果推送到 Feishu。

## 文件结构

```
scripts/intelligence_agent.py     # 主脚本
scripts/feishu_reporter.py       # Feishu 推送模块
```

## Cron Job

通过 Hermes cronjob 配置（参见下方 YAML）。
