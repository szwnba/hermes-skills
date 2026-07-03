# Search Query Patterns for Intelligence Agents

Verified working search queries for each data source (2026-07).

## GitHub Search API

### AI/Agent Repos (Recommended)
```
q=pushed:>=DATE+topic:ai+topic:agent+stars:>100&sort=stars&order=desc&per_page=10
```
- Returns: dify, lobehub, deer-flow, LlamaFactory, headroom, etc.
- Why: `topic:ai+topic:agent` filters for repos tagged with both AI and agent topics; `stars:>100` removes toy projects

### Generic Trending (Avoid for AI focus)
```
q=pushed:>=DATE+stars:>50&sort=stars&order=desc
```
- Returns: awesome lists, freeCodeCamp, public-apis — too broad for AI intelligence

### Language-Specific
```
q=pushed:>=DATE+language:python+topic:machine-learning+stars:>100&sort=stars
q=pushed:>=DATE+language:typescript+topic:ai+stars:>50&sort=stars
```

### Headers Required
```python
headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "Hermes-Agent"  # GitHub requires User-Agent
}
```

## arXiv API

### AI/Agent Papers (Recommended)
```
search_query=(cat:cs.AI+OR+cat:cs.LG)+AND+(all:agent+OR+all:LLM+OR+all:reinforcement+learning+OR+all:multimodal)&sortBy=submittedDate&sortOrder=descending&max_results=8
```

### LLM Focus
```
search_query=cat:cs.CL+AND+(all:large+language+model+OR+all:LLM+OR+all:prompt+engineering)&sortBy=submittedDate&descending&max_results=5
```

### Robotics/Manipulation
```
search_query=cat.RO+AND+(all:reinforcement+learning+OR+all:imitation+learning)&sortBy=submittedDate&descending&max_results=5
```

## RSS Feeds — Verified Working (2026-07)

| Blog | URL | Feed URL | Status |
|------|-----|----------|--------|
| Hacker News | https://news.ycombinator.com | https://news.ycombinator.com/rss | ✅ |
| Hugging Face Blog | https://huggingface.co/blog | https://huggingface.co/blog/feed.xml | ✅ |
| DeepMind Blog | https://deepmind.google/discover/blog | https://deepmind.google/blog/rss.xml | ✅ |
| TechCrunch AI | https://techcrunch.com/category/ai/ | https://techcrunch.com/category/artificial-intelligence/feed/ | ✅ |
| The Verge AI | https://www.theverge.com/ai-artificial-intelligence | https://www.theverge.com/rss/ai-artificial-intelligence/index.xml | ✅ |

### Known Broken Feeds
| Blog | Feed URL | Error |
|------|----------|-------|
| OpenAI Blog | https://openai.com/feed/ | 404 |
| Google AI Blog | https://ai.googleblog.com/feeds/posts/default | 308 |
| Anthropic News | https://www.anthropic.com/news/rss.xml | 404 |
| Microsoft AI | https://blogs.microsoft.com/ai/feed/ | 410 |
| MIT News AI | https://news.mit.edu/topic/.../rss.xml | EOF |

### Adding Feeds
```bash
blogwatcher-cli add "Blog Name" <url> --feed-url <feed_url>
blogwatcher-cli scan  # verify it works
blogwatcher-cli articles  # check output
```

## Report Format — Feishu Markdown

Use this structure for Feishu delivery:

```
🔍 **情报官每日简报** YYYY-MM-DD HH:MM
━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **GitHub Trending（AI/Agent 方向，过去24h Star 增长）**
```
★{stars} {name}
  {language} | {description}
  {url}

📝 **arXiv 最新论文（AI Agent / LLM / RL）**
**[arXiv ID]** {title}
_{authors}_
{abstract snippet}
🔗 https://arxiv.org/abs/{id}

📰 **RSS 资讯**
- {article title}
- ...

🐦 **X/Twitter AI 动态**
{content or ⚠️ error}

━━━━━━━━━━━━━━━━━━━━━━━━━━
_回复序号深挖某个方向 | 数据来源: GitHub, arXiv, RSS_
```

Key formatting:
- Use `**bold**` for section headers
- Use code blocks for GitHub repo listings (monospace, preserves alignment)
- Include arxiv links as clickable URLs
- Mark failed sources with ⚠️ and continue
