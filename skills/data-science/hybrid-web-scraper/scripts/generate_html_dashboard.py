#!/usr/bin/env python3
"""
Generate an HTML dashboard for the knowledge base.
Reads articles from Obsidian Vault 00_Inbox/ and produces a single self-contained HTML file.

Usage:
    python3 scripts/generate_html_dashboard.py --vault /path/to/vault --output dashboard.html

The generated HTML is fully self-contained (no external deps) and includes:
- Full-text search across titles and previews
- Category filter buttons
- Article cards with tags, size, source link
- Dark theme (GitHub-style)
"""
import json, os, re, sys, argparse
from pathlib import Path
from collections import Counter

def parse_frontmatter(content, max_chars=2000):
    fm = content[:max_chars]
    title = (re.search(r'title:\s*"?([^"\n]+)"?', fm) or [None,''])[1].strip() if re.search(r'title:\s*"?([^"\n]+)"?', fm) else ''
    url = (re.search(r'url:\s*"?([^"\n]+)"?', fm).group(1).strip() if re.search(r'url:\s*"?([^"\n]+)"?', fm) else '')
    date = (re.search(r'date_added:\s*(\d{4}-\d{2}-\d{2})', fm).group(1) if re.search(r'date_added:\s*(\d{4}-\d{2}-\d{2})', fm) else '')
    folder = (re.search(r'folder:\s*"?([^"\n]+)"?', fm).group(1).strip() if re.search(r'folder:\s*"?([^"\n]+)"?', fm) else '')
    tags_m = re.search(r'tags:\s*\[([^\]]+)\]', fm)
    tags = [t.strip() for t in tags_m.group(1).split(',')] if tags_m else []
    return title, url, date, folder, tags

def extract_preview(content):
    body_start = content.find('\n## ')
    if body_start > 0:
        return content[body_start:body_start+300].replace('\n',' ').strip()[:200]
    return content[2000:2300].replace('\n',' ').strip()[:200]

def normalize_folder(folder):
    """Consolidate fragmented folder names into canonical categories."""
    mapping = {
        'AI_Skill':'AI Skill','AI智能体':'AI Agent',
        'Playwright_MCP':'Playwright MCP','Playwright_AI':'Playwright MCP',
        'Playwright测试':'Playwright MCP','playwright 集成AI + 自愈':'Playwright AI',
        'playwright  CLI skill':'Playwright CLI','playwright test agent':'Playwright AI',
        'Playwright × AI自动化实战索引':'Playwright AI',
        'BrowserUse':'Browser Use','AgentBrowser':'Browser Use','Agent Browser':'Browser Use',
        'Onboarding':'Onboarding','OpenClaw':'OpenClaw','OpenClaw测试':'OpenClaw',
        'OpenClaw自动化测试':'OpenClaw','openclaw':'OpenClaw',
        '测试用例':'测试用例生成','测试Agent':'测试Agent开发','测试skill':'测试 Skill',
        'Claude_OpenCode':'Claude/OpenCode','ClaudeCode':'Claude Code',
        'claudecode':'Claude Code','Claude  Opencode CLI 自动化':'Claude/OpenCode',
        'AI前沿理念':'AI 前沿','AI范式':'AI 范式','opencode':'OpenCode',
        '量化交易':'投资',
    }
    return mapping.get(folder, folder)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--vault', required=True, help='Path to Obsidian Vault')
    parser.add_argument('--output', default='/tmp/knowledge_dashboard.html')
    args = parser.parse_args()

    inbox = Path(args.vault) / '00_Inbox'
    if not inbox.exists():
        print(f"Error: {inbox} not found"); sys.exit(1)

    files = sorted(inbox.glob('*.md'), key=lambda x: x.stat().st_mtime, reverse=True)
    articles = []
    for f in files:
        content = f.read_text(errors='ignore')
        title, url, date, folder, tags = parse_frontmatter(content)
        if not title: title = f.stem.replace('_',' ')
        articles.append({
            'title': title, 'url': url, 'date': date,
            'folder_normalized': normalize_folder(folder),
            'content_length': len(content),
            'preview': extract_preview(content),
            'tags': tags[:5], 'filename': f.name,
        })

    total = len(articles)
    total_size = sum(a['content_length'] for a in articles)
    folders = Counter(a['folder_normalized'] for a in articles)
    summary = {'total': total, 'total_size_kb': round(total_size/1024,1),
               'folders_normalized': dict(folders), 'articles': articles}

    # Inline HTML template (self-contained, dark theme)
    data_json = json.dumps(summary, ensure_ascii=False)
    html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>📚 知识库看板</title>
<style>
:root{{--bg:#0d1117;--surface:#161b22;--border:#30363d;--text:#e6edf3;--text2:#8b949e;--accent:#58a6ff;--purple:#bc8cff;--green:#3fb950}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:var(--bg);color:var(--text);line-height:1.6}}
.container{{max-width:1400px;margin:0 auto;padding:20px}}
header{{text-align:center;padding:40px 20px 30px;border-bottom:1px solid var(--border);margin-bottom:30px}}
header h1{{font-size:2em;background:linear-gradient(135deg,var(--accent),var(--purple));-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.stats{{display:flex;gap:15px;justify-content:center;flex-wrap:wrap;margin:25px 0}}
.stat-card{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:18px 28px;text-align:center;min-width:140px}}
.stat-card .num{{font-size:2em;font-weight:700;color:var(--accent)}}
.stat-card .label{{font-size:0.85em;color:var(--text2)}}
.toolbar{{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin-bottom:20px}}
.search-box{{flex:1;min-width:250px;padding:10px 16px;background:var(--surface);border:1px solid var(--border);border-radius:8px;color:var(--text);font-size:15px;outline:none}}
.search-box:focus{{border-color:var(--accent)}}
.filter-btn{{padding:8px 16px;background:var(--surface);border:1px solid var(--border);border-radius:20px;color:var(--text2);cursor:pointer;font-size:13px;transition:all .2s}}
.filter-btn:hover,.filter-btn.active{{background:var(--accent);color:#fff;border-color:var(--accent)}}
.article-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(380px,1fr));gap:16px}}
.article-card{{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:20px;transition:all .2s;cursor:pointer}}
.article-card:hover{{border-color:var(--accent);transform:translateY(-2px);box-shadow:0 4px 20px rgba(88,166,255,.15)}}
.card-title{{font-size:15px;font-weight:600;margin-bottom:8px}}
.badge{{display:inline-block;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:600;margin-left:6px}}
.badge-folder{{background:rgba(88,166,255,.15);color:var(--accent)}}
.badge-size{{background:rgba(188,140,255,.15);color:var(--purple)}}
.card-preview{{font-size:13px;color:var(--text2);margin-bottom:10px;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}}
.card-url a{{color:var(--accent);text-decoration:none;font-size:12px}}
.tag{{font-size:11px;padding:1px 6px;background:rgba(63,185,80,.1);color:var(--green);border-radius:8px;margin-right:4px}}
@media(max-width:600px){{.article-grid{{grid-template-columns:1fr}}}}
</style></head><body>
<div class="container">
<header>
<h1>📚 AI 进化型知识库</h1>
<div class="stats">
<div class="stat-card"><div class="num">{total}</div><div class="label">总文章</div></div>
<div class="stat-card"><div class="num">{len(folders)}</div><div class="label">分类</div></div>
<div class="stat-card"><div class="num">{summary['total_size_kb']}KB</div><div class="label">总大小</div></div>
</div></header>
<div class="toolbar">
<input type="text" class="search-box" id="search" placeholder="🔍 搜索标题、内容...">
<button class="filter-btn active" data-filter="all" onclick="setFilter('all')">全部</button>
<div id="filters" style="display:flex;gap:8px;flex-wrap:wrap"></div>
</div>
<div id="content"></div>
</div>
<script>
const DATA={data_json};
const grouped={{}};
DATA.articles.forEach(a=>{{const c=a.folder_normalized||'其他';if(!grouped[c])grouped[c]=[];grouped[c].push(a)}});
const cats=Object.entries(grouped).sort((a,b)=>b[1].length-a[1].length);
const fc=document.getElementById('filters');
cats.forEach(([cat,count])=>{{const b=document.createElement('button');b.className='filter-btn';b.dataset.filter=cat;b.textContent=`${{cat}} (${{count}})`;b.onclick=()=>setFilter(cat);fc.appendChild(b)}});
const ct=document.getElementById('content');
cats.forEach(([cat,arts])=>{{let h=`<div class="cat-section" data-cat="${{cat}}"><h2 style="padding:15px 0;border-bottom:2px solid var(--border);margin-bottom:15px">${{cat}} <span style="background:var(--accent);color:#fff;padding:2px 10px;border-radius:12px;font-size:13px">${{arts.length}}</span></h2><div class="article-grid">`;arts.forEach(a=>{{const k=(a.content_length/1024).toFixed(1);const tags=a.tags.map(t=>`<span class="tag">${{t}}</span>`).join('');h+=`<div class="article-card" data-title="${{a.title.toLowerCase()}}" data-preview="${{a.preview.toLowerCase()}}"><div class="card-title">${{a.title}}<span class="badge badge-folder">${{a.folder_normalized}}</span><span class="badge badge-size">${{k}}KB</span></div><div class="card-preview">${{a.preview}}</div><div style="display:flex;justify-content:space-between;align-items:center">${{tags}}${{a.url?`<a href="${{a.url}}" target="_blank">🔗 原文</a>`:''}}</div></div>`}});h+='</div></div>';ct.innerHTML+=h}});
let activeFilter='all';
function setFilter(f){{activeFilter=f;document.querySelectorAll('.filter-btn').forEach(b=>b.classList.toggle('active',b.dataset.filter===f));document.querySelectorAll('.cat-section').forEach(s=>s.style.display=(f==='all'||s.dataset.cat===f)?'':'none');document.getElementById('search').value='';document.querySelectorAll('.article-card').forEach(c=>c.style.display='')}}
document.getElementById('search').addEventListener('input',e=>{{const q=e.target.value.toLowerCase();document.querySelectorAll('.article-card').forEach(c=>{{const m=!q||(c.dataset.title||'').includes(q)||(c.dataset.preview||'').includes(q);c.style.display=m?'':'none'}});document.querySelectorAll('.cat-section').forEach(s=>{{const v=s.querySelectorAll('.article-card:not([style*="display: none"])').length;s.style.display=v?'':'none'}})}});
</script></body></html>"""

    output = Path(args.output)
    output.write_text(html, encoding='utf-8')
    print(f"✅ Dashboard: {output} ({output.stat().st_size/1024:.1f} KB)")
    print(f"   Articles: {total} | Categories: {len(folders)}")

if __name__ == '__main__':
    main()
