---
name: obsidian-bookmark-import
description: Parse browser bookmark HTML exports and import into Obsidian vault as structured notes with URL, title, folder, and optional scraped content.
---

# Obsidian Bookmark Import

Parse browser (Edge/Chrome/Firefox) bookmark HTML exports into structured Obsidian notes.

## Quick Reference

- **Parsing script**: See `references/parsing-script.md`
- **Template**: See `templates/collection-note.md`
- **Scraping fallback**: See `references/scraping-strategy.md`

## Core Workflow

1. Resolve vault path ($OBSIDIAN_VAULT_PATH or ~/Documents/Obsidian Vault)
2. Parse HTML with regex line-by-line (see references/parsing-script.md)
3. Classify sources (WeChat vs. other)
4. Present batch options to user (demo batch / skip WeChat / index-only)
5. Scrape content where possible, write notes to 00_Inbox/
6. Update dashboard with counts
7. **Post-import maintenance** (see `hybrid-web-scraper` skill → `references/vault-maintenance-workflow.md`): normalize folder names (40+ raw → ~12 clean), recompile 20_Wiki, generate 30_Outputs analysis report

## Key Pitfalls

- **Browser timeouts**: In headless/server environments, `browser_navigate` frequently times out. Have a fallback ready (index-only notes) and present options upfront rather than retrying indefinitely.
- **web_extract unavailable**: This tool may not exist in all environments. Don't assume it's available.
- **WeChat articles**: Anti-bot verification ("环境异常") blocks both browser and API scraping. Use Tavily search as fallback; mark as "待手动阅读" if neither works.
- **Filename sanitization**: Remove / \ : * ? " < > | from titles. Chinese characters are fine.
- **execute_code sandbox Python**: The sandbox may not have playwright installed. Use `subprocess.run(['python3', '-c', code], ...)` instead of importing directly in `execute_code`.
- **Brave Search keys expire**: Subscription tokens can be deactivated. Always verify API keys with a test call before committing to Brave as the primary scraper.

## Linked Files

- `references/parsing-script.md` — Python parsing script + edge cases
- `references/scraping-strategy.md` — Fallback strategy when browser/web_extract unavailable
- `references/progress-tracking.md` — Compare collected notes vs. full bookmark list to find gaps
- `templates/collection-note.md` — Note template with YAML frontmatter
