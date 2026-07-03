#!/usr/bin/env python3
"""Crawl4AI and Playwright scrapers"""
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from playwright.async_api import async_playwright

async def crawl4ai_scrape(url, max_retries=2):
    """Scrape using Crawl4AI. Returns result dict."""
    for attempt in range(max_retries + 1):
        try:
            async with AsyncWebCrawler(verbose=False) as crawler:
                config = CrawlerRunConfig(
                    word_count_threshold=100,
                    excluded_tags=['nav', 'header', 'footer', 'aside'],
                )
                result = await crawler.arun(
                    url=url,
                    config=config,
                    session_id=f'scrape_{hash(url) % 99999}'
                )
                if result.success and result.markdown:
                    return {
                        'success': True,
                        'content': result.markdown,
                        'source': 'Crawl4AI',
                    }
        except Exception as e:
            if attempt < max_retries:
                await asyncio.sleep(2 ** attempt)
            else:
                return {
                    'success': False,
                    'content': f'Crawl4AI error: {e}',
                    'source': 'Crawl4AI',
                }
    return {
        'success': False,
        'content': 'Crawl4AI returned empty',
        'source': 'Crawl4AI',
    }

async def playwright_scrape(url, max_retries=2):
    """Scrape using Playwright for JS-heavy pages."""
    for attempt in range(max_retries + 1):
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-dev-shm-usage']
                )
                page = await browser.new_page()
                try:
                    await page.goto(
                        url,
                        timeout=25000,
                        wait_until='domcontentloaded'
                    )
                    await page.wait_for_timeout(2000)
                    content = await page.evaluate("""
                        () => {
                            const selectors = [
                                'article', '.post', '.content', '#content',
                                '.markdown-body', '.article-content',
                                '.entry-content', '.rich_media_content',
                                '#js_content', '.post-body'
                            ];
                            for (const sel of selectors) {
                                const el = document.querySelector(sel);
                                if (el && el.innerText.length > 100) {
                                    return el.innerText;
                                }
                            }
                            return document.body.innerText;
                        }
                    """)
                    return {
                        'success': True,
                        'content': content,
                        'source': 'Playwright',
                    }
                finally:
                    await page.close()
                    await browser.close()
        except Exception as e:
            if attempt < max_retries:
                await asyncio.sleep(2 ** attempt)
            else:
                return {
                    'success': False,
                    'content': f'Playwright error: {e}',
                    'source': 'Playwright',
                }
    return {
        'success': False,
        'content': 'Playwright failed',
        'source': 'Playwright',
    }
