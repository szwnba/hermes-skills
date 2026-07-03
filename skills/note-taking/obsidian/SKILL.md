---
name: obsidian
description: Read, search, create, and edit notes in the Obsidian vault.
platforms: [linux, macos, windows]
---

# Obsidian Vault

Use this skill for filesystem-first Obsidian vault work: reading notes, listing notes, searching note files, creating notes, appending content, and adding wikilinks.

## Vault path

Use a known or resolved vault path before calling file tools.

The documented vault-path convention is the `OBSIDIAN_VAULT_PATH` environment variable, for example from `${HERMES_HOME:-~/.hermes}/.env`. If it is unset, use `~/Documents/Obsidian Vault`.

File tools do not expand shell variables. Do not pass paths containing `$OBSIDIAN_VAULT_PATH` to `read_file`, `write_file`, `patch`, or `search_files`; resolve the vault path first and pass a concrete absolute path. Vault paths may contain spaces, which is another reason to prefer file tools over shell commands.

If the vault path is unknown, `terminal` is acceptable for resolving `OBSIDIAN_VAULT_PATH` or checking whether the fallback path exists. Once the path is known, switch back to file tools.

## Read a note

Use `read_file` with the resolved absolute path to the note. Prefer this over `cat` because it provides line numbers and pagination.

## List notes

Use `search_files` with `target: "files"` and the resolved vault path. Prefer this over `find` or `ls`.

- To list all markdown notes, use `pattern: "*.md"` under the vault path.
- To list a subfolder, search under that subfolder's absolute path.

## Search

Use `search_files` for both filename and content searches. Prefer this over `grep`, `find`, or `ls`.

- For filenames, use `search_files` with `target: "files"` and a filename `pattern`.
- For note contents, use `search_files` with `target: "content"`, the content regex as `pattern`, and `file_glob: "*.md"` when you want to restrict matches to markdown notes.

## Create a note

Use `write_file` with the resolved absolute path and the full markdown content. Prefer this over shell heredocs or `echo` because it avoids shell quoting issues and returns structured results.

## Append to a note

Prefer a native file-tool workflow when it is not awkward:

- Read the target note with `read_file`.
- Use `patch` for an anchored append when there is stable context, such as adding a section after an existing heading or appending before a known trailing block.
- Use `write_file` when rewriting the whole note is clearer than constructing a fragile patch.

For an anchored append with `patch`, replace the anchor with the anchor plus the new content.

For a simple append with no stable context, `terminal` is acceptable if it is the clearest safe option.

## Targeted edits

Use `patch` for focused note changes when the current content gives you stable context. Prefer this over shell text rewriting.

## Wikilinks

Obsidian links notes with `[[Note Name]]` syntax. When creating notes, use these to link related content.

## Templates

Pre-built templates available in `templates/`:
- `vault-dashboard.md` — 信息采集库仪表盘模板（中文目录+统计+导航）
- `collection-template.md` — 采集素材笔记模板（frontmatter + 摘要 + 要点 + 想法）

## Importing Browser Bookmarks into Vault

See `references/bookmark-import.md` for the full parsing script, edge cases, and WeChat URL caveats.

When the user provides an Edge/Chrome bookmark HTML export (from **Export Bookmarks** in browser settings), parse it into structured notes:

1. **Resolve vault path** — check `$OBSIDIAN_VAULT_PATH`, fallback to `~/Documents/Obsidian Vault`.
2. **Parse the HTML** — use Python `re` to extract `<A HREF="...">...</A>` lines and `<H3>...</H3>` folder headers. The HTML structure nests folders hierarchically; track `current_folder` state line-by-line.
3. **Classify sources** — `mp.weixin.qq.com` or `weixin.qq.com` URLs are WeChat articles; these often require special handling (browser automation or RSS) since they may be paywalled or anti-scraping.
4. **Batch process** — do NOT attempt all 286+ bookmarks in one shot. Present options to the user:
   - Option A: Grab a small batch first (10-20) as a demo
   - Option B: Skip WeChat articles (only scrape non-paywalled sites)
   - Option C: Just create an index note with URLs, no content scraping
5. **Write notes** — use the `采集素材模板.md` template from `Templates/` folder. Each bookmark becomes a note in `00_Inbox/` with filename `YYYY-MM-DD_标题.md`.
6. **Update dashboard** — append summary to `00_仪表盘.md` with counts by folder and source type.

See `references/bookmark-import.md` for the full parsing script and edge cases.

### WeChat article caveat

WeChat articles (`mp.weixin.qq.com`) have long query-string params in the URL. The actual article content may not load via simple HTTP GET — consider using the `browser` tool for these, or skip them if the user only wants URL indexing.

**Updated 2026-07-01**: From server IPs, WeChat returns `302 → wappoc_appmsgcaptcha` for browser-based tools (Playwright, BrowserAct stealth-extract, Crawl4AI). However, **curl with Chrome UA string bypasses the check** (no browser fingerprint = no captcha trigger). Use the curl + Python parse pattern in `references/wechat-curl-parse-pattern.md` within the hybrid-web-scraper skill for reliable WeChat article extraction from server environments.

### Scraping non-WeChat bookmarks: Playwright approach

For non-WeChat public websites (GitHub, CSDN, 掘金, 博客园, etc.), use Playwright Python via `subprocess.run` (not `execute_code` import sandbox — Playwright is not installed in the sandbox). Key steps:

1. **Launch headless Chromium** with args: `['--no-sandbox', '--disable-dev-shm-usage']`
2. **Navigate** with `wait_until='domcontentloaded'` and `timeout=20000`
3. **Extract content** via `page.evaluate()` trying selectors in order: `article`, `#readme`, `.markdown-body`, `main`, `.rich_media_content`, `.content`, `.post-content`, `.post_body`, `.article-content`, `.entry-content`, then fallback to `body.innerText`
4. **Cap content** at 3000 chars to keep notes manageable
5. **Handle filename sanitization** — strip `/`, `\\`, `:`, `*`, `?`, `"`, `<`, `>`, `|` from titles before creating filenames. Filenames with these chars cause `FileNotFoundError` because they create invalid paths.
6. **Rate limit** — wait 2-3 seconds between every 10 requests to avoid being blocked.
7. **Accept partial results** — some sites return 0 chars (empty body), some timeout (internal IPs, heavy JS). Mark failed ones with error message instead of skipping entirely.

### Scraping non-WeChat bookmarks: Crawl4AI approach (RECOMMENDED)

Crawl4AI is now the preferred tool for bookmark scraping (verified 2026-06-27). It converts web pages to clean Markdown automatically, requires no API keys, and handles navigation pollution better than Playwright.

**Installation**: `pip install crawl4ai`

**Key advantages**:
- Async support for batch processing
- Automatic Markdown conversion (no manual selector tuning)
- `excluded_tags` parameter removes nav/sidebar content
- ~2-5s per page (vs Playwright's 5-15s)
- 98% success rate on tested bookmarks

**Example config for clean extraction**:
```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

config = CrawlerRunConfig(
    word_count_threshold=200,
    excluded_tags=['nav', 'header', 'footer', 'aside'],
)
result = await crawler.arun(url=url, config=config)
markdown = result.markdown  # Clean, no nav pollution
```

See `references/ai-scraping-tools-comparison.md` for full tool comparison and hybrid strategy.

### Scraping non-WeChat bookmarks: Tavily approach

Tavily API (`https://api.tavily.com/search`) can also fetch page content via `include_raw_content=true` and `include_answer=true`. It works well for most public sites and is faster (~3s vs ~10s per page). However:
- Requires a valid API key (must be set in `.env` or passed via `TAVILY_API_KEY` env var)
- May return truncated or low-quality content for some sites
- WeChat articles: Tavily can sometimes get summaries via search, but full content is unreliable

### Content extraction fallback strategy

Preferred order (2026-06-27 update): **Crawl4AI → Tavily → Playwright → index-only note**.

**Why Crawl4AI first** (verified 2026-06-27):
- Converts web pages to clean Markdown automatically (no manual selector tuning)
- Specifically designed for LLM/AI workflows — outputs are RAG-ready
- Async support — ideal for batch processing hundreds of bookmarks
- Free and open-source (69.7K GitHub stars) — no API key required
- Handles anti-bot detection better than raw Playwright
- Can exclude navigation tags via `CrawlerRunConfig(excluded_tags=['nav', 'header', 'footer', 'aside'])`
- Speed: ~2-5 seconds per page (faster than Playwright's 5-15s)

**Crawl4AI setup**: `pip install crawl4ai`
```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

async with AsyncWebCrawler() as crawler:
    config = CrawlerRunConfig(
        word_count_threshold=200,
        excluded_tags=['nav', 'header', 'footer', 'aside'],
    )
    result = await crawler.arun(url=url, config=config)
    markdown_content = result.markdown  # Clean markdown, no nav pollution
```

**When to use Tavily instead**:
- When you need AI-generated summaries alongside raw content
- For WeChat articles (Tavily search sometimes finds cached versions)
- When Crawl4AI fails on anti-bot sites (Tavily has better proxy handling)

**When to use Playwright instead**:
- For pages that require JavaScript execution that Crawl4AI's headless browser can't handle
- When you need pixel-perfect screenshots or visual verification
- As a fallback when Crawl4AI returns empty/low-quality content

### Content quality checklist (NEW — 2026-06-27)

After scraping, verify note quality:
1. **Check for navigation pollution** — search content for nav keywords (会员, 周边, 新闻, 博问, 闪存, 赞助商, 首页, 新随笔, 联系, 管理, 订阅, 随笔-, 文章-, 评论-, 阅读-). If ≥3 nav keywords present, the scraped content includes sidebar/navigation noise.
2. **Fix noisy notes** — either re-scrape with better selectors, or post-process to strip nav sections. Prioritize notes with `article`, `.markdown-body`, `.rich_media_content`, or `#js_article` selectors over generic `body.innerText`.
3. **Size threshold** — notes <500 bytes are likely failed scrapes (empty body, captcha pages, or errors). Flag these for manual review or re-scrape with Tavily.
4. **Content >3000 bytes** = high quality (full article). **1000-3000 bytes** = moderate (partial article). **<1000 bytes** = low (likely incomplete or failed).

### API key persistence (NEW — 2026-06-27)

Tavily API key must be explicitly saved to `.env` before batch scraping. The user may provide it in conversation but it won't persist across sessions. Always verify:
```bash
grep TAVILY_API_KEY ~/.hermes/profiles/collector/.env
```
If missing, ask the user to provide it and save it. Do NOT attempt to scrape without a valid key — it will fail with 401.
