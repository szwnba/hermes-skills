---
name: intelligence-agent-builder
description: "Build multi-source intelligence/monitoring agents that collect from GitHub, arXiv, RSS, Twitter, and web — then deliver structured daily reports via cron."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [intelligence, monitoring, multi-source, cron, github, arxiv, rss, twitter, automation]
    related_skills: [arxiv, blogwatcher, xurl, github-repo-management, todoist]
---

# Intelligence Agent Builder

Build agents that collect daily intelligence from multiple sources and deliver structured reports. This is a **class-level pattern** for combining APIs, RSS, and search into a single automated pipeline.

## When to Use

- User wants a "情报官" / "intelligence officer" / daily briefing agent
- Combining 2+ data sources (GitHub, arXiv, RSS, Twitter, web search) into one report
- Scheduled delivery via cron (daily/weekly digests)
- User asks for "monitor X and report daily"

## Architecture

```
Data Sources → Collectors → Report Builder → Delivery
     ↓              ↓             ↓            ↓
 GitHub API    functions    markdown/JSON   cron/Feishu
 arXiv API     per source   formatted report  webhook
 RSS feeds
 Twitter/X
 Web search
```

## Step-by-Step Build Process

### 1. Identify Data Sources

Match sources to user's interest area:

| Interest | Sources |
|----------|---------|
| AI/ML | arXiv (cs.AI, cs.LG), GitHub Trending, AI blogs via RSS, Twitter AI accounts |
| Tech News | Hacker News, Reddit, tech blogs RSS, Twitter trending |
| Crypto/DeFi | Polymarket, crypto blogs, Twitter, Reddit |
| Academic | arXiv, Google Scholar, Semantic Scholar |

### 2. Create the Collector Script

Template at `templates/intelligence_agent.py`. Key principles:

- **One function per source** — each collector is independent, failures don't cascade
- **Safe token loading** — use base64 file pattern (see Pitfalls)
- **Graceful degradation** — if a source fails, report it but continue with others
- **JSON output** — raw data to stdout, formatted report to stderr (or vice versa)

### 3. Set Up Cron Delivery

Use Hermes cronjob tool:

```python
cronjob(
    action='create',
    schedule='0 8 * * *',  # 8:00 AM daily
    prompt='Run the intelligence script and format results...',
    deliver='origin',  # or specific channel
    name='Daily Intelligence Briefing'
)
```

The cron prompt should:
1. Run the collector script
2. Format results into readable report
3. Handle partial failures gracefully (mark with ⚠️)
4. Deliver to user's channel

### 4. Report Format

Standard structure for Feishu/Telegram delivery:

```
🔍 情报官每日简报 [日期]
━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 GitHub Trending
  ★1234 owner/repo: Description...

📝 arXiv 最新论文
  2401.12345 Title...

📰 RSS 新文章
  - Article title...

🐦 X/Twitter 动态
  - Tweet content...

━━━━━━━━━━━━━━━━━━━━━━━━━━
回复序号深挖某个方向
```

## Pitfalls

### 1. Hermes Token Truncation
Same as hybrid-web-scraper. API keys in Python variables get truncated to 3-13 chars. Use base64 file pattern:

```python
import base64
token = base64.b64decode(open("/path/to/token.b64").read().strip()).decode()
```

### 2. execute_code Blocked in Cron
`execute_code` is blocked in cron mode with error: `BLOCKED: execute_code runs arbitrary local Python (including subprocess calls that bypass shell-string approval checks). Cron jobs run without a user present to approve it.` **Do not use `execute_code` in cron prompts.**

### 3. delegate_task Also Blocked in Cron
`delegate_task` is blocked in cron mode with the same error as `execute_code`. The suggested workaround of `delegate_task(toolsets=['terminal'])` does NOT work in cron. **Both `execute_code` and `delegate_task` are unavailable in cron jobs.**

### 4. Tiered Failure Diagnosis
When tools fail in sequence, rapidly narrow down the failure tier before attempting workarounds. **Do not retry the same failing tool 3+ times** — move through the layers:

| Tier | Check If | Then |
|------|----------|------|
| **Tier 1: Terminal only** | `terminal` fails but file tools (`read_file`, `skill_view`) work | Switch to `web_search`/`web_extract`/`browser` for data collection |
| **Tier 2: Terminal + web** | Both `terminal` and `web_search`/`web_extract` are down | Try `browser` + manual HTTP via `browser_console`
| **Tier 3: Everything except file tools** | All of terminal, web, browser fail | No data collection possible — go straight to failure report (Tier below) |
| **Tier 4: Complete blackout** | Even `write_file`/`skill_view` fail | Session itself is broken — unlikely in practice |

**In cron, Tier 2-3 is common**: terminal is blocked by tirith, Tavily may be expired, browser may be down. The agent should probe each tier quickly (2-3 attempts max) and then produce a failure report rather than retrying endlessly.

### 5. Terminal Commands Blocked by Security Scan (`tirith:unknown`)
In cron mode, ALL terminal commands may be blocked by the Hermes security scanner with `Security scan: security issue detected` / `pattern_key: "tirith:unknown"`. This affects even trivial commands like `pwd` and `ls`. **This is different from the "user approval" issue in interactive sessions** — no user is present in cron to approve, so the command simply fails.

**Workaround**: The only reliable data collection tools in cron mode are `web_search`, `web_extract`, and `browser_navigate` — but these can also fail (see below).

### 6. web_search / web_extract (Tavily) Can Fail with 401
The Tavily API (backend for `web_search` and `web_extract`) can return `401 Unauthorized` if the API key is missing or expired. When this happens, both tools fail simultaneously. **Always have a fallback plan that does not depend on web_search.**

### 7. browser_navigate Can Time Out
The browser tool can time out (60s) if the Chromium/Chrome instance is not running or the network is slow. **Do not rely on browser as the sole fallback.**

### 8. Complete Failure Mode: Produce a Failure Report
When ALL data collection tools fail (terminal blocked, web_search 401, browser timeout), the cron job should produce a **failure report** that clearly states:
- Which tools were attempted (and failed)
- The specific error for each
- Suggested remediation steps
- What the agent *can* still do (file reads, skills, memory)

**Do not silently deliver nothing** — a failure report is a valid and useful cron output. See `references/failure-report-template.md` for the format.

### 9. Feishu Delivery Field Validation Failed ([99992402])
Feishu API can reject messages with `[99992402] field validation failed`. This typically happens when the message content contains unsupported characters, excessive length, or malformed Markdown. **Mitigation**: 
- Keep message body under 3000 chars for Feishu card messages
- Avoid emoji sequences that may not render in Feishu's parser
- Strip or escape any non-standard Unicode
- Log the exact `last_delivery_error` from cron job state for diagnosis
- If delivery fails, still produce the report locally — the failure is in the delivery layer, not the collection layer

### 10. arXiv API Rate Limit
~1 request per 3 seconds. Don't parallelize arXiv calls aggressively.

### 11. GitHub Search API Rate Limit
30 requests/minute for authenticated users. Use `pushed:>=YYYY-MM-DD` filter to get recent activity rather than polling all repos.

### 12. xurl Auth State
`xurl` requires OAuth setup outside agent sessions. If `xurl auth status` shows no tokens, the Twitter collector will fail gracefully — make sure your report builder handles this.

### 13. blogwatcher-cli Not Installed
If not installed, RSS collection fails. The agent should detect this (`which blogwatcher-cli`) and skip RSS rather than crash.

Install via binary tarball (no package manager):
```bash
curl -sL https://github.com/JulienTant/blogwatcher-cli/releases/latest/download/blogwatcher-cli_linux_amd64.tar.gz | tar xz -C /usr/local/bin blogwatcher-cli
```

### 14. GitHub Search Query Quality
Broad queries like `pushed:>=DATE&sort=stars` return generic repos (awesome lists, freeCodeCamp). For AI/Agent results, use topic filters:
```
q=pushed:>=DATE+topic:ai+topic:agent+stars:>100&sort=stars&order=desc
```
See `references/search-query-patterns.md` for per-domain recipes.

### 15. arXiv Search Scope
`cat:cs.AI+OR+cat:cs.LG` alone is too broad — returns 1000+ papers across all ML. Add keyword filters:
```
search_query=(cat:cs.AI+OR+cat:cs.LG)+AND+(all:agent+OR+all:LLM+OR+all:reinforcement+learning+OR+all:multimodal)
```

### 16. Network Reliability (urllib)
`urllib.request.urlopen` can fail on first call with transient DNS errors (`No address associated with hostname`). Always implement retry logic:
```python
def fetch_json(url, headers=None, retries=3, timeout=20):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers or {})
            resp = urllib.request.urlopen(req, timeout=timeout)
            return json.loads(resp.read())
        except Exception:
            if attempt < retries - 1:
                continue
            raise
```

### 17. blogwatcher Feed Discovery
Many RSS feeds fail silently (404, 308, 403, 410). Verified working feeds (2026-07):
- Hacker News: `https://news.ycombinator.com/rss`
- Hugging Face Blog: `https://huggingface.co/blog/feed.xml`
- DeepMind Blog: `https://deepmind.google/blog/rss.xml`
- TechCrunch AI: `https://techcrunch.com/category/artificial-intelligence/feed/`
- The Verge AI: `https://www.theverge.com/rss/ai-artificial-intelligence/index.xml`

Known broken (do not attempt without verification):
- OpenAI Blog (404), Google AI Blog (308), Anthropic News (404), Microsoft AI (410), MIT News AI (EOF)

## References

- `references/total-failure-2026-07.md` — Complete tool blackout case study (tirith + Tavily 401 + browser timeout)
- `references/script-template.md` — Full Python template for multi-source intelligence agent
- `references/failure-report-template.md` — Structured failure report template for when all data sources are unreachable
- `references/cron-prompt-patterns.md` — Effective cron prompt structures for report delivery
- `references/source-comparison.md` — When to use which data source (API vs RSS vs search)
- `references/search-query-patterns.md` — Verified working search queries and RSS feed URLs (updated 2026-07)

## Related Skills

- `arxiv` — arXiv paper search and parsing
- `blogwatcher` — RSS feed monitoring
- `xurl` — Twitter/X API access
- `github-repo-management` — GitHub API and `gh` CLI
- `todoist` — Task management (for action items from intelligence)
- `hybrid-web-scraper` — Web scraping for sources without APIs
