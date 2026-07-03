# Bookmark Collection Progress Tracking

## Overview
Track which bookmarks have been scraped vs. which remain unscraped by comparing collected URLs against the parsed bookmark list.

## Method

### Step 1: Extract collected URLs from 00_Inbox/
```python
import os, re, json

inbox_dir = "/path/to/vault/00_Inbox"
collected_urls = set()

for fn in os.listdir(inbox_dir):
    if not fn.endswith(".md"):
        continue
    with open(os.path.join(inbox_dir, fn), "r") as f:
        content = f.read()
    # Extract URL from YAML frontmatter
    url_match = re.search(r'url:\s*"?([^\s"]+)"?', content[:2000])
    if url_match:
        collected_urls.add(url_match.group(1).strip())

print(f"Collected: {len(collected_urls)} unique URLs")
```

### Step 2: Compare with bookmark list
```python
with open("/tmp/bookmarks_with_index.json") as f:
    bookmarks = json.load(f)

missing = []
for bm in bookmarks:
    url = bm["url"].strip().rstrip("/")
    found = any(url in cu or cu in url for cu in collected_urls)
    if not found:
        missing.append(bm)

print(f"Missing: {len(missing)} / {len(bookmarks)}")
```

### Step 3: Normalize WeChat URLs
WeChat URLs contain many query parameters (`__biz`, `mid`, `idx`, `sn`, `pass_ticket`, etc.). Two URLs pointing to the same article may differ in these params.

**Normalization strategy:**
1. Strip trailing slashes
2. For WeChat URLs, keep only the base URL + essential params (`__biz`, `mid`, `idx`)
3. Compare case-insensitively

```python
import re

def normalize_wechat_url(url):
    """Keep only essential WeChat URL components."""
    if "mp.weixin.qq.com" not in url:
        return url.strip().rstrip("/").lower()
    # Extract base + __biz + mid + idx
    match = re.match(r'([^?]*\?[^&]*)?(__biz=[^&]+&mid=[^&]+&idx=[^&]+)?(.*)', url, re.IGNORECASE)
    if match:
        base = match.group(1) or ""
        essential = match.group(2) or ""
        return (base + "&" + essential).rstrip("&").lower()
    return url.strip().rstrip("/").lower()
```

## Expected Results (as of 2026-06-28)
- Total bookmarks: 286
- WeChat articles: 221
- Other bookmarks: 65
- Collected: ~77 (27%)
  - WeChat: ~12 (5%)
  - Other: 65 (100%)
- Remaining: ~209 (all WeChat)

## Automation
Save the missing list for batch processing:
```python
with open("/tmp/missing_bookmarks.json", "w") as f:
    json.dump(missing, f, ensure_ascii=False)
```
Then feed to `batch_scrape.py` or `compile_wiki.py`.
