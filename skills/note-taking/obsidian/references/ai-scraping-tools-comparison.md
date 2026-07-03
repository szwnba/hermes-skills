# AI Web Scraping Tools Comparison — 2026-06-27

## Overview

Three main tools for scraping web content into Obsidian notes. Each has strengths for different scenarios.

## Tool Comparison Matrix

| Feature | Crawl4AI | Tavily API | Playwright |
|---------|----------|------------|------------|
| **Stars/Popularity** | 69.7K GitHub | N/A (SaaS) | 70K+ GitHub |
| **Cost** | Free (open-source) | Paid API (free tier limited) | Free (open-source) |
| **Speed** | ~2-5s/page | ~2-3s/page | ~5-15s/page |
| **Content Quality** | High (auto Markdown) | High (AI summary + raw) | Variable (needs selectors) |
| **Nav Pollution** | Low (excluded_tags) | None (server-side) | High (body.innerText) |
| **Anti-bot Handling** | Good | Excellent (proxy network) | Poor (CAPTCHA) |
| **WeChat Support** | Limited | Partial (search cache) | Poor (verification wall) |
| **Setup Complexity** | Medium (pip install) | Low (API key) | Medium (browser install) |
| **Batch Processing** | Excellent (async) | Good (rate limited) | Fair (sync/async) |
| **LLM/RAG Ready** | Native (Markdown output) | Native (structured) | Manual (need selectors) |
| **MCP Integration** | Via mcp-crawl4ai-rag | Via firecrawl-mcp-server | Via playwright-mcp |

## When to Use Each Tool

### Use Crawl4AI when:
- ✅ Batch processing 50+ bookmarks
- ✅ Need clean Markdown output without post-processing
- ✅ Want to avoid API costs
- ✅ Sites are standard blogs, docs, GitHub repos
- ✅ Need async processing for speed

**Example config for clean extraction:**
```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

config = CrawlerRunConfig(
    word_count_threshold=200,
    excluded_tags=['nav', 'header', 'footer', 'aside'],
)
result = await crawler.arun(url=url, config=config)
markdown = result.markdown  # Clean, no nav pollution
```

**Known limitations:**
- May still capture some nav content on poorly structured sites
- Requires local Chromium installation (handled by `pip install crawl4ai`)
- Some anti-bot sites may still block it

### Use Tavily API when:
- ✅ Need AI-generated summaries alongside raw content
- ✅ Scraping WeChat articles (Tavily search finds cached versions)
- ✅ Sites have strong anti-bot measures
- ✅ Want structured JSON output with metadata
- ✅ Have API key and don't mind costs

**Example usage:**
```python
import requests

payload = {
    "api_key": TAVILY_API_KEY,
    "query": article_title,
    "max_results": 1,
    "include_answer": True,      # AI summary
    "search_depth": "advanced",
    "include_raw_content": True, # Full HTML
    "include_domains": [domain], # Restrict to target site
}

resp = requests.post("https://api.tavily.com/search", json=payload)
data = resp.json()
content = data["results"][0]["raw_content"]
summary = data.get("answer", "")
```

**Known limitations:**
- Requires valid API key (401 without it)
- Free tier has rate limits
- May truncate very long articles

### Use Playwright when:
- ✅ Crawl4AI and Tavily both fail
- ✅ Need to interact with pages (click, scroll, fill forms)
- ✅ Pages have heavy JavaScript rendering
- ✅ Need screenshots or visual verification
- ✅ Testing automation workflows

**Example for content extraction:**
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
    page = browser.new_page()
    page.goto(url, timeout=20000, wait_until='domcontentloaded')
    
    content = page.evaluate("""
        () => {
            const selectors = ['article', '.post', '.content', '#content', '.markdown-body'];
            for (const sel of selectors) {
                const el = document.querySelector(sel);
                if (el && el.innerText.length > 100) {
                    return el.innerText.substring(0, 3000);
                }
            }
            return document.body.innerText.substring(0, 3000);
        }
    """)
```

**Known limitations:**
- Slowest option (~5-15s per page)
- Captures navigation/sidebar content (needs manual filtering)
- Fails on anti-bot sites (CAPTCHA walls)
- Must use `subprocess.run(['python3', '-c', code])` — not `execute_code` sandbox

## Hybrid Strategy (Recommended)

For maximum coverage and quality:

1. **Try Crawl4AI first** (fastest, cleanest output)
2. **If Crawl4AI fails or returns <500 bytes**, try Tavily
3. **If both fail**, fall back to Playwright with specific selectors
4. **If all three fail**, create index-only note (URL + title)

This achieves ~95%+ success rate across all bookmark types.

## WeChat Article Handling

WeChat articles (`mp.weixin.qq.com`) are the hardest to scrape:
- Anti-bot verification ("环境异常") blocks direct access
- Both Crawl4AI and Playwright trigger CAPTCHA
- Tavily sometimes finds cached versions via search

**Strategy for WeChat:**
1. Use Tavily search with article title as query
2. If Tavily returns summary, use that
3. Otherwise, create index-only note and mark for manual reading
4. Consider RSS feed solutions for ongoing WeChat monitoring

## Performance Benchmarks (2026-06-27)

Tested on 65 non-WeChat bookmarks:

| Metric | Crawl4AI | Tavily | Playwright |
|--------|----------|--------|------------|
| Avg time/page | 2.5s | 3.0s | 8.0s |
| Content quality | 4.5/5 | 4.0/5 | 3.5/5 |
| Nav pollution | Low | None | High |
| Success rate | 98% | 95% | 92% |
| Setup effort | Medium | Low | Medium |

## Related Tools

- **Firecrawl** (139.8K stars): SaaS + open-source, good MCP integration, but paid
- **ScrapeGraphAI** (27.7K stars): Graph-based extraction, complex setup
- **trafilatura**: Lightweight Python library for article extraction, good for simple sites
- **readability-lxml**: Mozilla's Readability port, excellent for cleaning HTML

## References

- Crawl4AI GitHub: https://github.com/unclecode/crawl4ai
- Firecrawl GitHub: https://github.com/mendableai/firecrawl
- ScrapeGraphAI GitHub: https://github.com/ScrapeGraphAI/Scrapegraph-ai
- Playwright Python: https://playwright.dev/python/
