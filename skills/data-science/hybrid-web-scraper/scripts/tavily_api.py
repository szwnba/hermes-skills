#!/usr/bin/env python3
"""Tavily API integration with retry logic"""
import time
import requests

def tavily_search(title, api_key, max_retries=2):
    """Search Tavily API for article content. Returns dict or None."""
    if not api_key:
        return None

    for attempt in range(max_retries + 1):
        try:
            payload = {
                'api_key': api_key,
                'query': title,
                'max_results': 1,
                'include_answer': True,
                'search_depth': 'advanced',
                'include_raw_content': True,
            }
            resp = requests.post(
                'https://api.tavily.com/search',
                json=payload,
                timeout=30
            )
            resp.raise_for_status()
            data = resp.json()

            if data.get('results'):
                result = data['results'][0]
                raw = result.get('raw_content', '')
                content = result.get('content', '')
                answer = data.get('answer', '')
                return {
                    'raw_content': raw,
                    'content': content,
                    'answer': answer,
                }
            return None

        except requests.exceptions.HTTPError as e:
            if resp.status_code == 401:
                print(f'   ❌ Tavily API Key 无效 (401)')
                return None
            if attempt < max_retries:
                wait = 2 ** attempt
                print(f'   ⏳ 重试 {attempt+1}/{max_retries}，等待 {wait}s...')
                time.sleep(wait)
            else:
                return None
        except Exception as e:
            if attempt < max_retries:
                wait = 2 ** attempt
                print(f'   ⏳ 重试 {attempt+1}/{max_retries}，等待 {wait}s...')
                time.sleep(wait)
            else:
                return None

    return None

def verify_tavily_key(api_key):
    """Verify Tavily API key is valid."""
    result = tavily_search('test', api_key)
    return result is not None
