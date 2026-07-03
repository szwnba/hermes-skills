# Parsing Script for Bookmark HTML

## Python Parsing Script

```python
import re, html

with open('bookmarks.html', 'r', encoding='utf-8') as f:
    content = f.read()

current_folder = "root"
bookmarks = []

for line in content.split('\n'):
    line_stripped = line.strip()
    
    # Check for folder (H3 tag)
    folder_match = re.search(r'<H3[^>]*>(.*?)</H3>', line_stripped, re.DOTALL)
    if folder_match:
        current_folder = folder_match.group(1).strip()
        continue
    
    # Check for bookmark (A tag with HREF)
    bm_match = re.search(r'<A\s+HREF="([^"]+)".*?ADD_DATE="([^"]+)".*?>(.*?)</A>', line_stripped, re.DOTALL)
    if bm_match:
        url = bm_match.group(1)
        add_date = bm_match.group(2)
        title_raw = bm_match.group(3).strip()
        title = html.unescape(re.sub(r'<[^>]+>', '', title_raw)).strip()
        if title:
            bookmarks.append({
                'folder': current_folder,
                'title': title,
                'url': url,
                'add_date': add_date,
                'is_wechat': 'mp.weixin.qq.com' in url or 'weixin.qq.com' in url
            })
```

## Edge Cases

1. **Nested folders** — Simple line-by-line parser works because each line has at most one tag. For deeply nested structures, a proper HTML parser may be needed.
2. **WeChat URLs** — Extremely long query strings with tracking params. Short form URLs are preferred for scraping.
3. **Missing titles** — Always check `title` is non-empty before adding.
4. **HTML entities** — Titles may contain `&amp;`, `&quot;`, `&#39;` etc. Always use `html.unescape()`.
5. **Special characters in titles** — Sanitize filenames (replace `/`, `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|` with `_`).
