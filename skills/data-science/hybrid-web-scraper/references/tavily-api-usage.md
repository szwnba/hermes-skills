# Tavily API Usage for WeChat Article Scraping

## Working Configuration (2026-06-27)

### API Endpoint
```
POST https://api.tavily.com/search
Content-Type: application/json
```

### Request Payload
```python
payload = {
    'api_key': 'tvly-Y...UDHn',
    'query': article_title,
    'max_results': 1,
    'include_answer': True,
    'search_depth': 'advanced',
    'include_raw_content': True,
}
```

### Response Fields
- `results[0].raw_content` — Full article text (preferred)
- `results[0].content` — Snippet (fallback)
- `answer` — AI-generated summary

### Key Observations
- Works reliably for WeChat article titles
- Returns 9000-13000 chars of raw content
- Includes AI-generated answer/summary
- Search depth 'advanced' is necessary for full content
- `include_raw_content: True` is essential

### Rate Limits
- Unknown — test with small batches first
- Recommend 3-second delay between requests

### Common Errors
- 401 Unauthorized: Invalid/expired API key
- Empty results: Title doesn't match indexed content
- Timeout: Network issues or slow response
