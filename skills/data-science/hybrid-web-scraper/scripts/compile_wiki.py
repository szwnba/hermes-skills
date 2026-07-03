#!/usr/bin/env python3
"""
Compile Wiki from 00_Inbox raw materials.
Usage: python3 compile_wiki.py [--vault /path/to/vault]

This is the "evolution" step: reads all raw articles, groups by topic,
generates wiki pages with cross-links, and maintains INDEX.md.
"""
import os, re, argparse
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def compile_wiki(vault_path):
    vault = Path(vault_path)
    inbox = vault / '00_Inbox'
    wiki = vault / '20_Wiki'
    wiki.mkdir(exist_ok=True)

    # Read all raw materials
    articles = []
    for f in sorted(inbox.glob('*.md')):
        if f.name.startswith('00_'):
            continue
        with open(f, 'r', encoding='utf-8') as fh:
            content = fh.read()
        title = f.stem
        folder = ''
        url = ''
        date = ''
        size = f.stat().st_size
        in_fm = False
        for line in content.split('\n'):
            if line.strip() == '---':
                if not in_fm:
                    in_fm = True; continue
                else: break
            if in_fm:
                if line.startswith('title:'):
                    m = re.search(r'"(.*)"', line)
                    if m: title = m.group(1)
                elif line.startswith('folder:'):
                    folder = line.split(':', 1)[1].strip()
                elif line.startswith('url:'):
                    m = re.search(r'"(.*)"', line)
                    if m: url = m.group(1)
        articles.append({
            'title': title, 'folder': folder or '未分类',
            'url': url, 'date': date, 'size': size,
            'stem': f.stem,
        })

    # Topic clusters
    TOPIC_CLUSTERS = {
        'AI Agent 与自主代理': ['OpenClaw', 'OpenClaw测试', 'AI_Skill', 'AI智能体'],
        '浏览器自动化': ['BrowserUse', 'AgentBrowser', 'Playwright_MCP', 'Playwright_AI', 'Playwright测试', 'Stagehand'],
        '编程助手': ['ClaudeCode', 'Claude_OpenCode'],
        '测试自动化': ['测试用例', '测试Agent', '视觉AI测试'],
        '开源平台与工具': ['开源平台', 'Onboarding'],
        '投资与交易': ['投资'],
    }
    folder_to_cluster = {}
    for cluster, folders in TOPIC_CLUSTERS.items():
        for f in folders:
            folder_to_cluster[f] = cluster

    cluster_articles = defaultdict(list)
    for a in articles:
        cluster = folder_to_cluster.get(a['folder'], '未分类')
        cluster_articles[cluster].append(a)

    wiki_entries = []
    for cluster, items in sorted(cluster_articles.items(), key=lambda x: -len(x[1])):
        safe_name = cluster.replace(' ', '_').replace('/', '_')
        wiki_file = wiki / f'{safe_name}.md'
        total_size = sum(i['size'] for i in items)
        lines = [
            f'# {cluster}', '',
            f'> **摘要**: 本主题收录了 {len(items)} 篇相关素材，总计 {total_size/1024:.1f} KB。',
            f'> **最后更新**: {datetime.now().strftime("%Y-%m-%d")}', '',
        ]
        sub_folders = defaultdict(list)
        for item in items:
            sub_folders[item['folder']].append(item)
        if len(sub_folders) > 1:
            lines += ['## 子主题', '']
            for sf, sf_items in sorted(sub_folders.items(), key=lambda x: -len(x[1])):
                lines.append(f'- **{sf}** ({len(sf_items)} 篇)')
            lines.append('')
        lines += ['## 收录文章', '', '| # | 标题 | 质量 | 大小 |', '|---|------|------|------|']
        for i, a in enumerate(items, 1):
            quality = '\U0001F7E2' if a['size'] > 3000 else ('\U0001F7E1' if a['size'] > 1000 else '\U0001F534')
            size_kb = f'{a["size"]/1024:.1f}KB'
            title_short = a['title'][:40]
            if len(a['title']) > 40: title_short += '...'
            lines.append(f'| {i} | [[{a["stem"]}|{title_short}]] | {quality} | {size_kb} |')
        lines.append('')
        lines += ['## 相关主题', '']
        for oc in cluster_articles:
            if oc != cluster:
                os_name = oc.replace(' ', '_').replace('/', '_')
                lines.append(f'- [[{os_name}|{oc}]]')
        lines.append('')
        with open(wiki_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        wiki_entries.append({'name': cluster, 'file': safe_name, 'count': len(items), 'size': total_size})

    # INDEX.md
    idx = [
        '# Wiki Index', '',
        f'> Compiled: {datetime.now().strftime("%Y-%m-%d %H:%M")}',
        f'> Source: 00_Inbox ({len(articles)} articles)',
        f'> Topics: {len(wiki_entries)}', '', '---', '',
        '| Topic | Articles | Size | Link |',
        '|-------|----------|------|------|',
    ]
    for e in sorted(wiki_entries, key=lambda x: -x['count']):
        idx.append(f'| {e["name"]} | {e["count"]} | {e["size"]/1024:.1f}KB | [[{e["file"]}|Open]] |')
    idx += ['', '---', '', 'Evolution loop:', '', '`00_Inbox -> 20_Wiki -> 30_Outputs -> Update Wiki`', '']
    with open(wiki / 'INDEX.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(idx))

    print(f'Wiki compiled: {len(wiki_entries)} topics, {len(articles)} articles')
    return len(wiki_entries), len(articles)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--vault', default=str(Path.home() / 'Documents' / 'Obsidian Vault'))
    args = parser.parse_args()
    compile_wiki(args.vault)
