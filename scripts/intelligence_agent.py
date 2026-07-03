#!/usr/bin/env python3
"""
情报官 (Intelligence Officer) Agent
Collects daily intelligence from multiple sources.

Usage:
    python3 intelligence_agent.py [--date YYYY-MM-DD]

Output: JSON report to stdout, formatted report to stderr
"""
import os
import sys
import json
import base64
import subprocess
import urllib.request
import re
from datetime import datetime, timedelta
from pathlib import Path

# === Config ===
HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
PROFILES = HERMES_HOME / "profiles" / "collector"
SCRIPTS_DIR = PROFILES / "scripts"
GITHUB_TOKEN_B64 = Path("/root/.github_token.b64")
TODOIST_ENV = PROFILES / ".env"

# === Helpers ===

def load_github_token():
    """Load GitHub token from base64 file, avoiding Hermes truncation."""
    try:
        with open(GITHUB_TOKEN_B64) as f:
            return base64.b64decode(f.read().strip()).decode().strip()
    except Exception:
        return None

def load_env(env_file):
    """Parse .env file for key=value pairs."""
    env = {}
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env

def run_cmd(cmd, timeout=30):
    """Run shell command safely."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result.stdout.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return None, 1
    except Exception as e:
        return str(e), 1

def fetch_json(url, headers=None, retries=2, timeout=15):
    """Fetch JSON from URL with retry on transient errors."""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers or {})
            resp = urllib.request.urlopen(req, timeout=timeout)
            return json.loads(resp.read())
        except urllib.error.URLError as e:
            if attempt < retries - 1 and "timed out" in str(e).lower():
                continue
            raise
        except Exception:
            if attempt < retries - 1:
                continue
            raise

def fetch_xml(url, retries=2, timeout=15):
    """Fetch XML from URL with retry on transient errors."""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url)
            resp = urllib.request.urlopen(req, timeout=timeout)
            return resp.read().decode()
        except urllib.error.URLError as e:
            if attempt < retries - 1 and "timed out" in str(e).lower():
                continue
            raise
        except Exception:
            if attempt < retries - 1:
                continue
            raise

# === Collectors ===

def collect_github_trending():
    """Collect top trending repos from last 24h by stars."""
    token = load_github_token()
    if not token:
        return {"error": "GitHub token unavailable"}
    
    since = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Hermes-Agent"
    }
    
    try:
        # Search repos pushed recently with AI/agent keywords
        data = fetch_json(
            f"https://api.github.com/search/repositories?q=pushed:>={since}+topic:ai+topic:agent+stars:>100&sort=stars&order=desc&per_page=10",
            headers=headers,
            retries=3,
            timeout=20
        )
        repos = []
        for r in data.get("items", [])[:10]:
            desc = r.get("description") or "No description"
            repos.append({
                "name": r["full_name"],
                "stars": r["stargazers_count"],
                "description": desc[:120],
                "language": r.get("language", ""),
                "url": r["html_url"]
            })
        return {"count": len(repos), "repos": repos}
    except Exception as e:
        return {"error": str(e)}

def collect_arxiv_papers():
    """Collect latest papers from cs.AI and cs.LG, focusing on agents."""
    try:
        xml = fetch_xml(
            "https://export.arxiv.org/api/query?search_query=(cat:cs.AI+OR+cat:cs.LG)+AND+(all:agent+OR+all:LLM+OR+all:reinforcement+learning+OR+all:multimodal)&sortBy=submittedDate&sortOrder=descending&max_results=8",
            retries=3,
            timeout=20
        )
        entries = re.findall(r'<entry>(.*?)</entry>', xml, re.DOTALL)
        papers = []
        for entry in entries:
            title = re.search(r'<title>(.*?)</title>', entry, re.DOTALL)
            title = title.group(1).strip().replace('\n', ' ') if title else "Unknown"
            arxiv_id = re.search(r'<id>.*?abs/(.*?)</id>', entry)
            arxiv_id = arxiv_id.group(1) if arxiv_id else ""
            published = re.search(r'<published>(.*?)</published>', entry)
            published = published.group(1)[:10] if published else ""
            summary = re.search(r'<summary>(.*?)</summary>', entry, re.DOTALL)
            summary = summary.group(1).strip()[:250].replace('\n', ' ') if summary else ""
            authors_el = re.findall(r'<name>(.*?)</name>', entry)
            authors = authors_el[:3] if authors_el else []
            papers.append({
                "title": title[:100],
                "arxiv_id": arxiv_id,
                "date": published,
                "abstract": summary,
                "authors": ", ".join(authors[:3]) if authors else ""
            })
        return {"count": len(papers), "papers": papers}
    except Exception as e:
        return {"error": str(e)}

def collect_rss_articles():
    """Collect articles from blogwatcher RSS feeds."""
    out, rc = run_cmd("blogwatcher-cli articles 2>&1 | head -60", timeout=20)
    if rc != 0 or not out or "not found" in out.lower():
        return {"error": "blogwatcher-cli unavailable", "raw": out or ""}
    
    # Parse article lines
    articles = []
    current = {}
    for line in out.split('\n'):
        line = line.strip()
        if line.startswith('['):
            if current:
                articles.append(current)
            current = {"title": re.sub(r'^\[.*?\]\s*', '', line)}
        elif line and current and 'title' in current:
            current.setdefault('meta', []).append(line)
    if current:
        articles.append(current)
    
    return {"count": len(articles), "articles": articles[:10]}

def collect_twitter_ai_news():
    """Search X/Twitter for AI agent news using xurl."""
    # Check if xurl is available
    which_out, _ = run_cmd("which xurl", timeout=5)
    if not which_out:
        return {"error": "xurl not installed"}
    
    out, rc = run_cmd('xurl search "AI agent" --limit 10 2>&1', timeout=30)
    if rc != 0 or not out:
        # Try alternative search terms
        out, rc = run_cmd('xurl search "LLM agent 2026" --limit 5 2>&1', timeout=30)
    
    return {"raw": out or "", "rc": rc}

# === Report Builder ===

def build_report(results):
    """Build formatted report from collected data."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = []
    lines.append("🔍 **情报官每日简报** {}".format(now))
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    # GitHub
    gh = results.get("github", {})
    lines.append("")
    lines.append("📊 **GitHub Trending（AI/Agent 方向，过去24h Star 增长）**")
    if "error" in gh:
        lines.append("⚠️ 采集失败: {}".format(gh["error"]))
    else:
        lines.append("```")
        for r in gh.get("repos", [])[:5]:
            lines.append("★{stars} {name}".format(**r))
            lines.append("  {language} | {description}".format(**r))
            lines.append("  {url}".format(**r))
            lines.append("")
        lines.append("```")
    
    # arXiv
    arxiv = results.get("arxiv", {})
    lines.append("")
    lines.append("📝 **arXiv 最新论文（AI Agent / LLM / RL）**")
    if "error" in arxiv:
        lines.append("⚠️ 采集失败: {}".format(arxiv["error"]))
    else:
        for p in arxiv.get("papers", [])[:5]:
            lines.append("**[{}]** {}".format(p["arxiv_id"], p["title"]))
            if p.get("authors"):
                lines.append("_{}_".format(p["authors"]))
            lines.append("{}".format(p["abstract"][:100]))
            lines.append("🔗 https://arxiv.org/abs/{}".format(p["arxiv_id"]))
            lines.append("")
    
    # RSS
    rss = results.get("rss", {})
    lines.append("")
    lines.append("📰 **RSS 资讯**")
    if "error" in rss:
        lines.append("️️⚠️ {}".format(rss["error"]))
    else:
        for a in rss.get("articles", [])[:5]:
            lines.append("- {}".format(a.get("title", "unknown")[:70]))
    
    # Twitter
    tw = results.get("twitter", {})
    lines.append("")
    lines.append("🐦 **X/Twitter AI 动态**")
    if "error" in tw:
        lines.append("⚠️ {}".format(tw.get("error", "N/A")))
    elif tw.get("raw"):
        text = tw["raw"].strip()
        if text:
            for line in text.split('\n')[:5]:
                if line.strip():
                    lines.append("{}".format(line.strip()[:80]))
        else:
            lines.append("(无新动态)")
    
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("_回复序号深挖某个方向 | 数据来源: GitHub, arXiv, RSS_")
    return "\n".join(lines)


# === Main ===

def main():
    import argparse
    parser = argparse.ArgumentParser(description="情报官 Intelligence Agent")
    parser.add_argument("--date", help="Override date YYYY-MM-DD")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()
    
    print("[情报官] 开始采集...", file=sys.stderr)
    
    results = {}
    
    print("[情报官] 1/4 GitHub Trending...", file=sys.stderr)
    results["github"] = collect_github_trending()
    
    print("[情报官] 2/4 arXiv Papers...", file=sys.stderr)
    results["arxiv"] = collect_arxiv_papers()
    
    print("[情报官] 3/4 Blogwatcher RSS...", file=sys.stderr)
    results["rss"] = collect_rss_articles()
    
    print("[情报官] 4/4 X/Twitter...", file=sys.stderr)
    results["twitter"] = collect_twitter_ai_news()
    
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(build_report(results))

if __name__ == "__main__":
    main()
