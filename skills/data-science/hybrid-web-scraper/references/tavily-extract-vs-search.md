# Tavily Extract vs Search API for WeChat Scraping

## TL;DR
For WeChat (mp.weixin.qq.com) articles, use the **Extract API** (`/extract`), not the Search API (`/search`). Search by title has ~8% success rate; Extract by URL has ~93%.

## Problem
WeChat article URLs look like:
```
https://mp.weixin.qq.com/s?__biz=MzIyMzA5NjEyMA==&mid=2647680550&idx=1&sn=61057f...
```
Search API queries by keyword/title and returns "best match" results. For WeChat:
- Titles are often non-unique or clickbait
- The URL params (`__biz`, `mid`, `sn`) act as identifiers but aren't searchable
- Result: Tavily Search returns wrong articles or nothing

## Solution: Extract API
```python
resp = requests.post('https://api.tavily.com/extract', json={
    'api_key': api_key,
    'urls': [url],  # Direct URL → content extraction
}, timeout=30)
data = resp.json()
# Response: {'results': {'<url>': {'raw_content': '...', 'text': '...'}}}
```

## API Limits (Researcher Plan)
- Total: 1,000 calls/month
- Shared across: search + extract + crawl + map + research
- Check usage: `GET https://api.tavily.com/usage` with `Authorization: Bearer <key>`

## Batch Collection Strategy
1. Check `/usage` endpoint before starting
2. Process in chunks with checkpointing every 5 items
3. Rate limit: 1.0s between requests
4. Expected throughput: ~7-8 articles/minute
5. A 200-article batch takes ~25 minutes and ~200 API calls

## Error Handling
- **429 (Rate Limited)**: Exponential backoff (5s × attempt)
- **401 (Invalid Key)**: Check key loading (see `.b64` workaround)
- **`'list' object has no attribute 'keys'`**: Some URLs return results as list instead of dict — handle both formats
- **Empty results**: Article may be deleted or access-restricted; skip and retry later
