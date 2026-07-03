#!/usr/bin/env python3
"""Note generator for Obsidian"""
from pathlib import Path

def generate_note(url, title, folder_cn, result, today):
    """Generate Obsidian note markdown from scrape result."""
    content_md = ''
    if result.get('success'):
        content_md += f'## 📄 正文内容\n\n```\n{result["content"][:8000]}\n```\n\n'
        if result.get('summary'):
            content_md += f'## 📝 摘要\n\n{result["summary"]}\n\n'
    else:
        content_md += f'> ⚠️ 采集失败: {result.get("content", "Unknown error")[:500]}\n\n'
        content_md += f'> 尝试工具: {result.get("source", "N/A")}\n\n'

    return f"""---
title: "{title}"
source: 网页
url: "{url}"
date_added: {today}
tags: [采集, 网页, {folder_cn}]
status: inbox
folder: {folder_cn}
rating: ⭐⭐⭐⭐⭐
---

# {title}

> **来源**: 网页 | **文件夹**: [[{folder_cn}]]
> **链接**: [原文]({url})
> **采集时间**: {today}
> **采集工具**: {result.get('source', 'N/A')}

## 🔑 关键要点

{content_md}
## 💡 我的想法

{{待补充}}

## 🔗 相关笔记

- 
"""

def save_note(vault_base, title, folder_cn, note, today):
    """Save note to vault, handling filename conflicts."""
    import re, unicodedata

    clean = []
    for c in title:
        if c.isalnum() or c in ' _-.':
            clean.append(c)
        elif unicodedata.category(c).startswith(('Lo', 'Lu', 'Ll')):
            clean.append(c)
    clean_name = ''.join(clean).replace(' ', '_').strip('_')[:80]
    if not clean_name:
        clean_name = 'bookmark'

    filename = f'{today}_{clean_name}.md'
    filepath = vault_base / filename

    counter = 1
    while filepath.exists():
        filename = f'{today}_{clean_name}_{counter}.md'
        filepath = vault_base / filename
        counter += 1

    vault_base.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(note)

    return str(filepath)
