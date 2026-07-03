#!/usr/bin/env python3
"""Hybrid web scraper with Crawl4AI + Playwright + Tavily"""
import argparse
import json
import os
import sys
import time
import asyncio
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from playwright.async_api import async_playwright
import requests

# ── Config ──────────────────────────────────────────────────────────
TAVILY_API_KEY=os.getenv('TAVILY_API_KEY', '')
VAULT_BASE = Path(os.getenv('OBSIDIAN_VAULT', '/root/Documents/Obsidian Vault/00_Inbox'))
TODAY = datetime.now().strftime('%Y-%m-%d')

FOLDER_MAP = {
    'investment': '投资', 'AI Skill': 'AI_Skill', 'openclaw': 'OpenClaw',
    'onboarding': 'Onboarding', 'Hermes': 'Hermes', 'claudecode': 'ClaudeCode',
    'opencode': 'OpenCode', 'BrowserUse': 'BrowserUse',
    'Playwright MCP': 'Playwright_MCP', '测试skill': '测试Skill',
    'AI智能体': 'AI智能体', 'playwright 集成AI + 自愈': 'Playwright_AI',
    '测试用例生成': '测试用例', '测试Agent开发': '测试Agent',
    '开源平台': '开源平台', 'AI前沿理念': 'AI前沿理念',
    'AI范式': 'AI范式', 'OpenClaw自动化测试': 'OpenClaw测试',
    'playwright test agent': 'Playwright测试',
    'playwright  CLI skill': 'PlaywrightCLI', '爬虫': '爬虫',
    'Stagehand': 'Stagehand', '视觉AI测试': '视觉AI测试',
    'Agent Browser': 'AgentBrowser',
    'Claude  Opencode CLI 自动化': 'Claude_OpenCode',
    'Playwright × AI自动化实战索引': 'Playwright实战',
    '量化交易': '量化交易', '工作流': '工作流',
}


def clean_title(title):
    """Clean title for use as filename."""
    clean = ''.join(c for c in title if c.isalnum() or c in ' _-.')
    clean = clean.replace(' ', '_')[:60]
    return clean if clean else 'bookmark'


def tavily_search(title, api_key):
    """Search Tavily API for article content."""
    if not api_key:
        return None
    
    try:
        payload = {
            'api_key': api_key,
            'query': title,
            'max_results': 1,
            'include_answer': True,
            'search_depth': 'advanced',
            'include_raw_content': True,
        }
        resp = requests.post('https://api.tavily.com/search', json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        
        if data.get('results'):
            result = data['results'][0]
            return {
                'raw_content': result.get('raw_content', ''),
                'content': result.get('content', ''),
                'answer': data.get('answer', ''),
            }
    except Exception as e:
        print(f"   ⚠️  Tavily error: {e}")
    
    return None


async def crawl4ai_scrape(url, title):
    """Scrape using Crawl4AI with optimized config."""
    try:
        async with AsyncWebCrawler(verbose=False) as crawler:
            config = CrawlerRunConfig(
                word_count_threshold=200,
                excluded_tags=['nav', 'header', 'footer', 'aside'],
            )
            result = await crawler.arun(url=url, config=config, session_id='single')
            
            if result.success and result.markdown:
                # Check content quality
                nav_keywords = ['会员', '周边', '新闻', '博问', '闪存', '赞助商']
                nav_count = sum(1 for kw in nav_keywords if kw in result.markdown)
                
                return {
                    'success': True,
                    'content': result.markdown[:5000],
                    'source': 'Crawl4AI',
                    'quality': 'good' if nav_count < 2 else 'needs_cleanup',
                }
    except Exception as e:
        return {'success': False, 'content': f'Crawl4AI error: {e}', 'source': 'Crawl4AI'}
    
    return {'success': False, 'content': 'Crawl4AI returned empty', 'source': 'Crawl4AI'}


async def playwright_scrape(url):
    """Fallback: Scrape using Playwright for JS-heavy pages."""
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
            page = await browser.new_page()
            try:
                await page.goto(url, timeout=20000, wait_until='domcontentloaded')
                title = await page.title()
                content = await page.evaluate("""
                    () => {
                        const selectors = ['article', '.post', '.content', '#content', 
                                         '.markdown-body', '.article-content', '.entry-content'];
                        for (const sel of selectors) {
                            const el = document.querySelector(sel);
                            if (el && el.innerText.length > 100) {
                                return el.innerText.substring(0, 5000);
                            }
                        }
                        return document.body.innerText.substring(0, 5000);
                    }
                """)
                return {
                    'success': True,
                    'content': content,
                    'source': 'Playwright',
                    'quality': 'good',
                }
            finally:
                await page.close()
                await browser.close()
    except Exception as e:
        return {'success': False, 'content': f'Playwright error: {e}', 'source': 'Playwright'}


def select_strategy(url, title):
    """Select best scraping strategy based on URL type."""
    if 'mp.weixin.qq.com' in url or 'weixin' in url:
        return 'tavily'
    return 'crawl4ai'  # Default to Crawl4AI


async def hybrid_scrape(url, title, folder='其他'):
    """Main hybrid scraping function."""
    strategy = select_strategy(url, title)
    folder_cn = FOLDER_MAP.get(folder, folder)
    
    print(f'🎯 Strategy: {strategy}')
    
    result = None
    if strategy == 'tavily':
        # Use Tavily for WeChat articles
        tavily_data = tavily_search(title, TAVILY_API_KEY)
        if tavily_data:
            content = tavily_data['raw_content'] or tavily_data['content']
            result = {
                'success': True,
                'content': content[:5000],
                'source': 'Tavily',
                'quality': 'good',
                'summary': tavily_data.get('answer', ''),
            }
        else:
            result = {'success': False, 'content': 'Tavily returned no data', 'source': 'Tavily'}
    else:
        # Try Crawl4AI first
        result = await crawl4ai_scrape(url, title)
        
        # Fallback to Playwright if Crawl4AI fails
        if not result['success']:
            print('  ⬇️  Falling back to Playwright...')
            result = await playwright_scrape(url)
    
    # Generate note
    note = generate_note(url, title, folder_cn, result)
    
    # Save
    VAULT_BASE.mkdir(parents=True, exist_ok=True)
    clean_name = clean_title(title)
    filename = f'{TODAY}_{clean_name}.md'
    filepath = VAULT_BASE / filename
    
    counter = 1
    while filepath.exists():
        filename = f'{TODAY}_{clean_name}_{counter}.md'
        filepath = VAULT_BASE / filename
        counter += 1
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(note)
    
    return {
        'url': url,
        'title': title,
        'folder': folder_cn,
        'strategy': result['source'],
        'success': result['success'],
        'content_length': len(result.get('content', '')),
        'saved': str(filepath),
        'quality': result.get('quality', 'unknown'),
    }


def generate_note(url, title, folder_cn, result):
    """Generate Obsidian note markdown."""
    content_md = ''
    if result.get('success'):
        content_md += f'## 📄 正文内容\n\n```\n{result["content"][:5000]}\n```\n\n'
        if result.get('summary'):
            content_md += f'## 📝 摘要\n\n{result["summary"]}\n\n'
    else:
        content_md += f'> ⚠️ 采集失败: {result.get("content", "Unknown error")[:300]}\n\n'
        content_md += f'> 尝试工具: {result.get("source", "N/A")}\n\n'
    
    return f"""---
title: "{title}"
source: 网页
url: "{url}"
date_added: {TODAY}
tags: [采集, 网页, {folder_cn}]
status: inbox
folder: {folder_cn}
rating: ⭐⭐⭐⭐⭐
---

# {title}

> **来源**: 网页 | **文件夹**: [[{folder_cn}]]
> **链接**: [原文]({url})
> **采集时间**: {TODAY}
> **采集工具**: {result.get('source', 'N/A')}

## 🔑 关键要点

{content_md}
## 💡 我的想法

{{待补充}}

## 🔗 相关笔记

- 
"""


async def main():
    parser = argparse.ArgumentParser(description='Hybrid web scraper')
    parser.add_argument('--url', required=True, help='URL to scrape')
    parser.add_argument('--title', required=True, help='Article title')
    parser.add_argument('--folder', default='其他', help='Folder name')
    args = parser.parse_args()
    
    print(f'📌 Scraping: {args.title}')
    print(f'   URL: {args.url}')
    print(f'   Folder: {args.folder}\n')
    
    result = await hybrid_scrape(args.url, args.title, args.folder)
    
    if result['success']:
        print(f'✅ Success!')
        print(f'   Strategy: {result["strategy"]}')
        print(f'   Content: {result["content_length"]} chars')
        print(f'   Saved: {result["saved"]}')
    else:
        print(f'❌ Failed: {result.get("content_length", "")}')
    
    # Save result to JSON for batch processing
    with open('/tmp/scrape_results.json', 'a', encoding='utf-8') as f:
        f.write(json.dumps(result, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    asyncio.run(main())
