# Failure Report Template for Intelligence Agent Cron Jobs

When all data collection tools fail, produce this structured failure report instead of silently delivering nothing.

## Template

```
🔴 **情报官每日简报 — 采集失败报告**

**时间**: [YYYY-MM-DD HH:MM] (cron 触发)

---

### ⚠️ 采集状态总览

| 工具/来源 | 状态 | 原因 |
|-----------|------|------|
| `terminal` (脚本执行) | ❌ 失败 | 安全扫描拦截 (`tirith:unknown`) |
| `execute_code` (Python) | ❌ 失败 | Cron 模式禁止运行 |
| `web_search` (Tavily) | ❌ 失败 | API 401 Unauthorized |
| `web_extract` (Tavily) | ❌ 失败 | API 401 Unauthorized |
| `browser_navigate` | ❌ 失败 | 连接超时 (60s) |

---

### 📊 GitHub Trending
⚠️ **采集失败** — [具体原因]

### 📝 arXiv 论文
⚠️ **采集失败** — [具体原因]

### 📰 RSS 资讯
⚠️ **采集失败** — [具体原因]

### 🐦 X/Twitter
⚠️ **采集失败** — [具体原因]

---

### 🔧 建议修复措施

1. **[Issue]**: [具体建议]
2. **[Issue]**: [具体建议]

---

_数据来源: GitHub, arXiv, RSS | 每日 08:00 自动推送_  
⚠️ **本次采集完全失败，请检查上述基础设施问题**
```

## Common Failure Patterns and Remediation

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `tirith:unknown` on terminal | Security scanner not whitelisting command | Update tirith config or whitelist the command |
| `execute_code` BLOCKED | Cron mode blocks arbitrary Python | Use `web_extract` or direct curl instead |
| `web_search` 401 Unauthorized | Tavily API key expired/missing | Check `~/.hermes/.env` for `TAVILY_API_KEY` |
| `browser_navigate` timeout | Chromium not running | Check `ps aux | grep -i chrom` |
| All tools fail | Network/DNS issue | Check `ping 8.8.8.8` and `nslookup api.tavily.com` |
