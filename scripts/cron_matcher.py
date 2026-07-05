#!/usr/bin/env python3
"""
Todoist × Knowledge Base Smart Matcher v3
核心改进：
1. 任务模式识别（预定义 domain hints）
2. 混合关键词提取（2字词 + 英文词）
3. 降阈值到1但按匹配数排序
4. 输出结构化 JSON 供 LLM 增强
"""

import os, sys, json, re
from pathlib import Path
from collections import defaultdict

os.environ["TODOIST_API_TOKEN"] = os.environ.get("TODOIST_API_TOKEN", "")
sys.path.insert(0, "/root/.hermes/profiles/collector/skills/todoist/scripts")
from todoist_helper import TodoistHelper
from datetime import date, datetime, timezone

KB = Path("/root/Documents/Obsidian Vault/00_Inbox")
META_PATH = Path("/tmp/articles_meta.json")
INBOX_PROJECT_ID = "6CrfQpMFrw9RJ6GW"  # 收集箱 project ID

with open(META_PATH) as f:
    META = json.load(f)

# Category → quality articles index
cat_index = defaultdict(list)
for a in META:
    if a.get("content_length", 0) > 1500:
        cat_index[a.get("folder_normalized", "其他")].append(a)

# ── Task domain hints (pre-defined expert knowledge) ───
DOMAIN_HINTS = {
    "github": {
        "cats": ["OpenClaw", "Claude Code & OpenCode", "开源工具"],
        "search_terms": ["github", "trending", "开源", "star"],
        "advice": "知识库有大量 GitHub 项目分析文章。可用 Hermes cron 定时拉取 GitHub Trending + arXiv，自动生成日报。"
    },
    "视频": {
        "cats": ["AI Skill", "开源工具"],
        "search_terms": ["视频", "字幕", "comfyui", "语音"],
        "advice": "可用 ComfyUI 生成视频，Whisper 提取字幕，AI 配音合成。知识库有相关工具文章。"
    },
    "教程": {
        "cats": ["AI Skill", "Onboarding"],
        "search_terms": ["教程", "入门", "实战", "上手"],
        "advice": None
    },
    "情报": {
        "cats": ["开源工具", "AI Agent", "Hermes"],
        "search_terms": ["trending", "arxiv", "rss", "监控", "采集", "blogwatcher"],
        "advice": "搭建情报 Agent：Hermes cron + blogwatcher(RSS) + arXiv skill + GitHub Trending。知识库有 Hermes 多 Agent 军团教程。"
    },
    "收集": {
        "cats": ["开源工具", "AI Agent", "Hermes"],
        "search_terms": ["采集", "爬虫", "rss", "订阅", "监控"],
        "advice": "你已有 hybrid-web-scraper（Tavily+Playwright），308篇已入库。可用 blogwatcher 做 RSS 订阅 + cron 定时采集。"
    },
    "采集": {
        "cats": ["开源工具", "AI Agent", "Hermes"],
        "search_terms": ["采集", "爬虫", "tavily", "playwright", "scrapling"],
        "advice": "采集链已跑通：Tavily Extract + Playwright，成功率96%。可扩展 RSS/博客监控。"
    },
    "知识库": {
        "cats": ["Hermes", "AI Agent", "AI 理念与范式"],
        "search_terms": ["知识库", "obsidian", "记忆", "sqlite", "wiki"],
        "advice": "你已有 Obsidian 308篇 + Wiki 13主题 + Output分析报告。下一步：MemOS 记忆插件 + LLM Wiki 知识检索。"
    },
    "汇总": {
        "cats": ["AI 理念与范式", "Hermes"],
        "search_terms": ["汇总", "总结", "报告", "分析"],
        "advice": None
    },
    "文章生成": {
        "cats": ["AI Skill", "AI Agent"],
        "search_terms": ["生成", "内容", "写作", "文案"],
        "advice": "可用 Hermes + LLM 自动生成内容。知识库有 AI 写作和爆款文案相关文章。"
    },
    "公众号": {
        "cats": ["浏览器自动化", "开源工具"],
        "search_terms": ["公众号", "微信", "推送", "订阅"],
        "advice": "微信公众号采集已跑通（Tavily+Playwright）。自动推送可用飞书 webhook 或 Server酱。"
    },
    "推送": {
        "cats": ["开源工具", "AI Agent"],
        "search_terms": ["推送", "通知", "webhook", "飞书"],
        "advice": "Hermes 已连接飞书，可用 cron 定时推送。"
    },
    "提示词": {
        "cats": ["AI Skill", "AI 理念与范式"],
        "search_terms": ["提示词", "prompt", "seo", "关键词"],
        "advice": "知识库有大量 Prompt 工程文章。可用 AI Skill 分类中的内容优化提示词。"
    },
    "文案": {
        "cats": ["AI Skill", "投资与变现"],
        "search_terms": ["文案", "爆款", "营销", "变现"],
        "advice": None
    },
    "推特": {
        "cats": ["开源工具", "投资与变现"],
        "search_terms": ["twitter", "xurl", "reddit", "社交"],
        "advice": "Hermes 有 xurl skill 可采集 X/Twitter。配合 polymarket skill 做交易情报。"
    },
    "reddit": {
        "cats": ["开源工具", "投资与变现"],
        "search_terms": ["reddit", "社区", "热门"],
        "advice": "可用 web_search + cron 定时搜索 Reddit 热门内容。"
    },
    "套利": {
        "cats": ["投资与变现"],
        "search_terms": ["套利", "交易", "polymarket", "加密"],
        "advice": "知识库有 Polymarket 交易和加密货币机器人文章。Hermes 有 polymarket skill。"
    },
    "微信": {
        "cats": ["浏览器自动化", "开源工具", "Hermes"],
        "search_terms": ["微信", "公众号", "文章", "采集"],
        "advice": "微信文章采集已完成（308篇）。存到 Notion 可用 Notion API skill 的 ntn CLI。"
    },
    "notion": {
        "cats": ["开源工具", "AI Skill"],
        "search_terms": ["notion", "ntn", "文档", "知识"],
        "advice": "Hermes 有 notion skill（ntn CLI），可直接操作 Notion 页面和数据库。"
    },
    "邮箱": {
        "cats": ["AI Agent", "开源工具"],
        "search_terms": ["邮件", "邮箱", "imap", "日报"],
        "advice": "可用 Hermes himalaya skill（IMAP）读取邮件 + LLM 生成精华日报。"
    },
    "测试": {
        "cats": ["测试工程", "Playwright AI", "OpenClaw"],
        "search_terms": ["测试", "自动化", "playwright", "用例"],
        "advice": "知识库有37篇测试工程文章。可用 OpenClaw/Playwright AI 自动生成测试用例。"
    },
    "自动化": {
        "cats": ["OpenClaw", "浏览器自动化", "Playwright AI"],
        "search_terms": ["自动化", "browser", "agent", "playwright"],
        "advice": None
    },
    "agent": {
        "cats": ["AI Agent", "Hermes", "OpenClaw"],
        "search_terms": ["agent", "智能体", "军团", "协同"],
        "advice": "知识库有 Hermes 多 Agent 军团完整教程（万字保姆级）。可搭建总管→调研→开发→测试流水线。"
    },
    "idea": {
        "cats": ["AI 理念与范式", "投资与变现"],
        "search_terms": ["idea", "创意", "变现", "落地"],
        "advice": None
    },
    "人格": {
        "cats": [],
        "search_terms": [],
        "advice": "知识库暂无相关内容。建议外部搜索：人格测试开源项目 + AI 评测系统。"
    },
}


def extract_keywords(text):
    """Extract meaningful 2-char Chinese words + English words."""
    clean = re.sub(r'https?://\S+', '', text)
    clean = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', clean)
    
    STOP = {'的','了','要','和','与','一个','这个','那个','什么','怎么','如何',
            '可以','能够','需要','需求','做','看','发','出','到','有','没',
            '系统','资料','文章','网站','关于','比较','方便','应该','然后',
            'https','www','com','cn','uuhb','tools'}
    
    words = []
    # Chinese 2-char words
    for seg in re.findall(r'[\u4e00-\u9fff]{2}', clean):
        if seg not in STOP:
            words.append(seg)
    # English words
    for w in re.findall(r'[a-zA-Z]{3,}', clean):
        wl = w.lower()
        if wl not in STOP:
            words.append(wl)
    
    # Deduplicate
    seen = set()
    unique = []
    for w in words:
        if w not in seen:
            seen.add(w)
            unique.append(w)
    return unique[:8]


def match_task(title):
    """Match a task to KB articles and generate advice."""
    text_lower = title.lower()
    
    # Find matching domains
    matched_domains = []
    cats = set()
    search_terms = set()
    advices = []
    
    for kw, hint in DOMAIN_HINTS.items():
        if kw in text_lower:
            matched_domains.append(kw)
            cats.update(hint["cats"])
            search_terms.update(hint["search_terms"])
            if hint["advice"]:
                advices.append(hint["advice"])
    
    # Also extract keywords from title
    title_keywords = extract_keywords(title)
    all_search_terms = list(search_terms) + title_keywords
    
    # Search in targeted categories
    results = []
    for cat in cats:
        for a in cat_index.get(cat, []):
            fn = a["filename"]
            filepath = KB / fn
            if not filepath.exists():
                continue
            try:
                content = filepath.read_text(errors='ignore')[:3000].lower()
            except:
                continue
            
            matched = [kw for kw in all_search_terms if len(kw) >= 2 and kw.lower() in content]
            if matched:
                results.append({
                    "category": cat,
                    "title": a.get("title", fn[:40]),
                    "url": a.get("url", ""),
                    "quality": a.get("quality", ""),
                    "content_length": a.get("content_length", 0),
                    "score": len(matched),
                    "matched_keywords": list(set(matched))[:5],
                })
    
    # Sort and deduplicate
    results.sort(key=lambda x: (-x["score"], -x["content_length"]))
    seen_titles = set()
    unique = []
    for r in results:
        key = r["title"][:30].lower()
        if key not in seen_titles:
            seen_titles.add(key)
            unique.append(r)
    
    return {
        "domains": matched_domains,
        "categories": list(cats),
        "search_terms": list(all_search_terms)[:6],
        "matches": unique[:4],
        "advice": advices[:2] if advices else None,
    }


# ── Main ────────────────────────────────────────────────
h = TodoistHelper()

# Get all tasks, filter programmatically to:
# 1. Exclude Inbox (收集箱)
# 2. Only include tasks due today or overdue
today_str = date.today().strftime("%Y-%m-%d")
all_tasks = h.list_tasks()

tasks = []
for t in all_tasks:
    # Skip Inbox project
    if t.project_id == INBOX_PROJECT_ID:
        continue
    # Only include tasks with due date (today or overdue)
    if t.due and t.due.date:
        due_date = t.due.date
        # due_date format is YYYY-MM-DD
        if due_date <= today_str:
            tasks.append(t)

# Sort by priority (descending)
tasks.sort(key=lambda t: -t.priority)

prio_map = {1: "🔵", 2: "🟠", 3: "🔴", 4: "⚫"}

print("=" * 70)
print("📋 Todoist × 知识库智能方案（v3）")
print(f"⏰ 运行时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}")
print("=" * 70)

matched_count = 0
unmatched = []

for t in tasks:
    title = re.sub(r'https?://\S+', '', t.content).strip()
    if len(title) > 55:
        title = title[:55] + "..."
    
    result = match_task(t.content)
    prio = prio_map.get(t.priority, "🔵")
    
    print(f"\n{'─'*60}")
    print(f"{prio} {title}")
    
    if result["categories"]:
        print(f"   📂 分类: {', '.join(result['categories'][:3])}")
    
    if result["matches"]:
        matched_count += 1
        print(f"   ✅ 知识库匹配 ({len(result['matches'])} 篇):")
        for m in result["matches"][:3]:
            q = m["quality"] or "📄"
            kws = ", ".join(m["matched_keywords"][:3])
            print(f"      {q} {m['title'][:42]}")
            print(f"         [{m['category']}] 关键词: {kws}")
    else:
        unmatched.append(title)
        print(f"   ⚠️ 知识库无精确匹配")
    
    if result["advice"]:
        for adv in result["advice"]:
            print(f"   💡 {adv}")
    elif not result["matches"]:
        print(f"   💡 建议外部搜索: {', '.join(result['search_terms'][:3])}")

print(f"\n{'='*70}")
print(f"📊 汇总: {len(tasks)} 个任务 | {matched_count} 个有知识库匹配 | {len(unmatched)} 个待外部搜索")
if len(tasks) == 0:
    print(f"   (过滤条件: 今天/过期任务 + 排除收集箱)")
    print(f"   (已有 {len(all_tasks)} 个任务全在收集箱中或无截止日期)")
if unmatched:
    print(f"n🔍 以下任务需要补充知识库或外部搜索:")
    for u in unmatched:
        print(f"   • {u[:50]}")
