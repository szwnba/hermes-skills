#!/usr/bin/env python3
"""Core scraping engine: Crawl4AI + Playwright + Tavily"""
import re
import os
import asyncio
from datetime import datetime
from pathlib import Path

import requests
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from playwright.async_api import async_playwright

# ── Config ──────────────────────────────────────────────
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY', '')
TODAY = datetime.now().strftime('%Y-%m-%d')

# ── Content cleanup ─────────────────────────────────────
NAV_PATTERNS = [
    r'会员|周边|新闻|博问|闪存|赞助商|Chat2DB',
    r'首页|新随笔|联系|管理|订阅|所有博客|当前博客',
    r'随笔-\s*\d+.*?阅读-\s*\d+',
    r'百度首页|腾讯云|华为云|博客园',
]

def clean_content(text):
    """Remove navigation/sidebar noise from scraped text."""
    lines = text.split('\n')
    cleaned = []
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            cleaned.append(line)
            continue
        is_nav = False
        for pat in NAV_PATTERNS:
            if re.fullmatch(pat, line_stripped) or (
                len(line_stripped) < 15 and re.search(pat, line_stripped)
            ):
                is_nav = True
                break
        if not is_nav:
            cleaned.append(line)
    result = '\n'.join(cleaned)
    result = re.sub(r'\n{3,}', '\n\n', result)
    return result.strip()

def is_low_quality(text):
    """Check if content is too short or is just an error page."""
    if len(text) < 200:
        return True, f'内容过短 ({len(text)} chars)'
    if '环境异常' in text[:200]:
        return True, '微信反爬拦截 (环境异常)'
    if text.count('\n') < 3 and len(text) < 500:
        return True, '内容结构异常'
    return False, ''

def clean_title(title):
    """Clean title for filename, preserves Chinese chars."""
    import unicodedata
    keep = []
    for c in title:
        if c.isalnum() or c in ' _-.':
            keep.append(c)
        elif unicodedata.category(c).startswith(('Lo', 'Lu', 'Ll')):
            keep.append(c)
    result = ''.join(keep).replace(' ', '_').strip('_')
    return result[:80] if result else 'bookmark'
