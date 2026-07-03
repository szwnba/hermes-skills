# Bookmark Import into Obsidian

## Parsing Edge/Chrome Bookmark HTML

Browser bookmark exports use the Netscape Bookmark File Format. Structure:

```html
<DL><p>
    <DT><H3>Folder Name</H3>
    <DL><p>
        <DT><A HREF="https://..." ADD_DATE="1234567890">Title Text</A>
    </DL><p>
</DL><p>
```

### Python parsing script

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

### Edge cases

1. **Nested folders** — H3 tags nest with DL/DT/ DL structure. The simple line-by-line parser above works because each line contains at most one tag. For deeply nested structures, a proper HTML parser may be needed.

2. **WeChat URLs** — Extremely long query strings with tracking params (`__biz`, `mid`, `sn`, `pass_ticket`, etc.). The clean URL is often available as a shorter form (e.g. `https://mp.weixin.qq.com/s/SHORT_ID`). For scraping, the short form is preferred.

3. **Missing titles** — Some `<A>` tags have no visible text between opening and closing tags. Always check `title` is non-empty before adding.

4. **HTML entities** — Titles may contain `&amp;`, `&quot;`, `&#39;` etc. Always use `html.unescape()`.

5. **Special characters in titles** — Chinese characters, emojis, punctuation. Use `encoding='utf-8'` for file output and sanitize filenames (replace `/`, `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|` with `_`).

### Folder classification heuristic

After parsing, group bookmarks by folder name. Common patterns:
- `investment` → business/money topics
- `AI Skill`, `openclaw`, `Hermes`, `claudecode` → AI agent tools
- `爬虫` → web scraping
- `大模型` → LLM topics
- `工作流` → workflow/automation

Use these to auto-categorize into Obsidian's folder structure (`10_Articles/技术/`, `10_Articles/行业/`, etc.).
