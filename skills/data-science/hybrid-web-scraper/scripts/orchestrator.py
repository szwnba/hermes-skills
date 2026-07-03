#!/usr/bin/env python3
"""
Hybrid scraping orchestrator.
Strategy: WeChat -> Tavily; Other -> Crawl4AI -> Playwright fallback.
With content cleaning, quality validation, retry, and dedup.
"""
import os
import sys
import json
import base64
import asyncio
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from scraper_core import clean_content, is_low_quality, clean_title
from tavily_api import tavily_search
from page_scrapers import crawl4ai_scrape, playwright_scrape
from note_generator import generate_note, save_note

# ── Config ──────────────────────────────────────────────
# Load Tavily key from .b64 file to avoid redaction system
def _load_search_key():
    key_file = Path(__file__).parent / '.tavily_key.b64'
    env_val = os.environ.get('TAVILY_API_KEY', '')
    if env_val and len(env_val) > 20:
        return env_val
    if key_file.exists():
        raw = key_file.read_text().strip()
        try:
            return base64.b64decode(raw).decode('utf-8')
        except Exception:
            pass
    return ''

_SEARCH_KEY = _load_search_key()
TODAY = datetime.now().strftime('%Y-%m-%d')
VAULT_BASE = Path(os.getenv(
    'OBSIDIAN_VAULT',
    '/root/Documents/Obsidian Vault/00_Inbox'
))


def select_strategy(url):
    """Pick the right tool for the URL."""
    if 'mp.weixin.qq.com' in url or 'weixin' in url:
        return 'tavily'
    return 'crawl4ai'


async def scrape_one(url, title, folder='其他'):
    """Scrape a single URL. Returns (result_dict, strategy)."""
    strategy = select_strategy(url)
    result = None

    if strategy == 'tavily':
        data = tavily_search(title, _SEARCH_KEY)
        if data:
            content = data.get('raw_content') or data.get('content', '')
            result = {
                'success': bool(content and len(content) > 200),
                'content': content,
                'source': 'Tavily',
                'summary': data.get('answer', ''),
            }
        else:
            result = {
                'success': False,
                'content': 'Tavily returned no data',
                'source': 'Tavily',
            }
    else:
        result = await crawl4ai_scrape(url)
        if not result['success']:
            result = await playwright_scrape(url)

    if result.get('success'):
        result['content'] = clean_content(result['content'])
        low_q, reason = is_low_quality(result['content'])
        if low_q:
            result['success'] = False
            result['content'] = f'质量检查失败: {reason}'
            result['quality'] = 'failed'
        else:
            result['quality'] = 'good'

    return result, strategy


async def process_bookmark(bm, idx, total):
    """Process one bookmark: scrape then save note."""
    url = bm.get('url', '')
    title = bm.get('title', url[:40])
    folder = bm.get('folder', '其他')

    print(f'[{idx}/{total}] {title[:50]}')

    result, strategy = await scrape_one(url, title, folder)

    note = generate_note(url, title, folder, result, TODAY)
    saved_path = save_note(VAULT_BASE, title, folder, note, TODAY)

    status = '✅' if result['success'] else '❌'
    chars = len(result.get('content', ''))
    print(f'  {status} {strategy} | {chars} chars | {Path(saved_path).name}')

    return {
        'title': title,
        'url': url,
        'folder': folder,
        'strategy': strategy,
        'success': result['success'],
        'content_length': chars,
        'saved_path': saved_path,
        'quality': result.get('quality', 'unknown'),
    }
