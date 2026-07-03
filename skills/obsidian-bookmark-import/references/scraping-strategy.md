# Tavily + Playwright Scraping Strategy

## Overview

Two-tier scraping approach for bookmark content collection:

1. **Tier 1: Tavily API** (primary) — fast, reliable, includes AI summary
2. **Tier 2: Playwright Python** (fallback) — for JS-rendered pages Tavily can't handle

## Tier 1: Tavily API

### Configuration
- Endpoint: `POST https://api.tavily.com/search`
- Required param: `api_key`
- Key params for scraping:
  - `include_raw_content: true` — returns full HTML source (up to 10KB+)
  - `include_answer: true` — returns AI-generated summary
  - `search_depth: "basic"` or `"advanced"`
  - `max_results: 1`

### Usage Pattern
```python
import requests

resp = requests.post("https://api.tavily.com/search", json={
    "api_key": "<YOUR_KEY>",
    "query": "<page_title_or_url>",
    "max_results": 1,
    "include_answer": True,
    "include_raw_content": True,
    "search_depth": "basic"
}, timeout=15)

data = resp.json()
# data["results"][0]["content"] — extracted text
# data["results"][0]["raw_content"] — full HTML
# data["answer"] — AI summary
```

### Pros
- Fast (1-3 seconds per request)
- Built-in AI summarization
- Handles most static pages well
- Returns cleaned text content

### Cons
- May not get full content for JS-heavy sites
- Rate limited (check plan)
- WeChat articles sometimes blocked

### Key Gotcha
- API key must be the FULL key string — truncation causes 401 errors
- Always test with a simple query first to verify key validity

## Tier 2: Playwright Python

### When to Use
- Tavily returns insufficient content
- Page is heavily JS-rendered (SPA, React, Vue)
- Need to interact with the page (click, scroll) before scraping

### Setup
```bash
pip install playwright  # if not already installed
playwright install chromium  # downloads browser binaries
```

### Direct Execution (NOT via execute_code import)
The sandbox Python may lack playwright. Use subprocess instead:
```python
import subprocess

code = """
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
    page = browser.new_page()
    page.goto('https://example.com', timeout=20000, wait_until='domcontentloaded')
    title = page.title()
    content = page.evaluate('document.querySelector("article")?.innerText || document.body.innerText')
    print(f'{title}\\n{content[:2000]}')
    browser.close()
"""
result = subprocess.run(['python3', '-c', code], capture_output=True, text=True, timeout=30)
```

### Content Extraction Selectors (priority order)
1. `article` — standard article pages
2. `#readme` — GitHub README pages
3. `.markdown-body` — GitHub rendered markdown
4. `main` — semantic HTML5
5. `.rich_media_content` — WeChat articles (usually blocked)
6. `#js_article` — WeChat article container
7. `.content`, `.post-content`, `.entry-content` — WordPress/blog
8. `document.body.innerText` — fallback

### Timeout Settings
- `timeout=20000` (20 seconds) — generous for slow sites
- `wait_until='domcontentloaded'` — don't wait for images/scripts

### Known Failures
- **WeChat**: Returns "环境异常" (anti-bot verification)
- **Heavy SPAs** (Polymarket, SkillsMP): May timeout even with 20s
- **Rate-limited sites**: Cloudflare protection returns captcha pages

## Decision Flow

```
Start scraping
    │
    ▼
Try Tavily (include_raw_content=true)
    │
    ├─ Got good content? → Use it ✅
    │
    └─ Content insufficient?
        │
        ▼
    Try Playwright
        │
        ├─ Got content? → Use it ✅
        │
        └─ Failed/timeout?
            │
            ▼
        Write index-only note + flag "待补充"
```

## WeChat Article Handling

WeChat articles are a special case:
- **Tavily**: Sometimes returns summary if the article was indexed
- **Playwright**: Always triggers anti-bot ("环境异常")
- **Best effort**: Search the article title via Tavily to get any available summary
- **Fallback**: Create note with title + URL, mark as `待手动阅读`
