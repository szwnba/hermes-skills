# 数据采集方案全景图（从 308 篇知识库提炼）

> 来源：用户知识库 308 篇文章中与「采集/爬虫/浏览器自动化/RSS/舆情」相关的内容分析。
> 更新时间：2026-06-28

## 五大采集方向

### 1. 自适应爬虫框架

| 工具 | 核心能力 | 适用场景 | 落地难度 |
|------|---------|---------|---------|
| **Scrapling** | CSS选择器失效后自动修复、Cloudflare反检测绕过 | 非微信网站/有反爬保护的公开网页 | ⚠️ 实测：对微信公众号无效（见 scrapling-evaluation.md） |
| **Firecrawl** | 面向 LLM 的爬虫，自动遍历网站→生成 Markdown | 批量采集喂给大模型 | 低（API 调用） |
| **Crawl4AI** | 已在 hybrid-web-scraper skill 中使用 | 通用网页采集 | ✅ 已落地 |
| **Jina.ai** | 多模态 AI 抓取 | 需要理解页面语义的采集 | 低（API 调用） |

**Scrapling 亮点**（2.5万 Star）：
- 解决"网站一改版，CSS选择器/XPath 全白搭"的痛点
- 自适应元素定位，选择器失效后自动修复
- 可与 OpenClaw 组合使用
- **⚠️ 实测结论（2026-06-28）**：StealthyFetcher 可绕 Cloudflare 等指纹检测，但对**微信公众号无效**——微信反爬是平台级验证码（`wappoc_appmsgcaptcha`），非指纹检测，任何浏览器工具都无法绕过。详见 `scrapling-evaluation.md`

### 2. AI 浏览器自动化框架（知识库 49 篇）

| 工具 | Star | 定位 | 特色 |
|------|------|------|------|
| **Browser-Use** | — | LLM 驱动的浏览器操控 | 支持 Pytest+DeepSeek，12 篇深度内容 |
| **Midscene** | — | 纯视觉驱动、跨端兼容 | 国产开源 SDK，AI UI 自动化 |
| **Stagehand** | — | AI Browser Automation Framework | Vercel/Browserbase 出品 |
| **Agent Browser** | 98.4K | 为大模型重新封装 Playwright | 结构化接口，摒弃浏览器复杂性 |
| **Dev Browser** | — | Claude Code 控制浏览器 | 轻量级，适合 Skill 集成 |
| **BrowserAct** | — | 面向 Agent 的浏览器自动化 CLI | stealth-extract 一键提取渲染页面，免费 tier 有中国 IP 池 |

**BrowserAct 实测（2026-07-01）**：
- ✅ stealth-extract 免费可用，默认中国 IP，跨会话 IP 一致
- ✅ Markdown 输出，适合 AI Agent 消费
- ⚠️ 强反爬站点（Product Hunt/Reddit）需付费代理
- ⚠️ browser open 需 GUI 环境，服务器不可用
- 详见 `references/browseract-evaluation.md`

**选型建议**：
- 需要 LLM 理解页面语义 → Browser-Use
- 需要纯视觉驱动（不依赖 DOM 结构） → Midscene
- 需要结构化 API 给 Agent 调用 → Agent Browser
- 已有 Claude Code/OpenClaw 环境 → Dev Browser
- **需要快速提取渲染页面内容 → BrowserAct stealth-extract（免费，中国 IP）**

### 3. RSS / 订阅 / 公众号采集

| 方案 | 核心思路 | 状态 |
|------|---------|------|
| 公众号 RSS | 让 Agent 替你刷公众号，WeChat RSS 订阅 | 方法可行，需找可用 RSS 源 |
| 多平台聚合 | OpenClaw 抓"没有 RSS 也没有订阅邮件的网站" | 可落地 |
| **当前已用** | Tavily Extract + Playwright（hybrid-web-scraper skill） | ✅ 已采集 308 篇 |

**注意**：微信公众号文章采集成功率约 93%，约 7% 的文章因被删除/设置访问限制而永久失败（详见 pitfall #10）。

### 4. 舆情监控 / 信息源整合

| 工具 | Star | 能力 | 落地优先级 |
|------|------|------|-----------|
| **TrendRadar** | 55.2K | 11 平台聚合（微博/知乎/抖音/B站等）+ RSS + AI 语义筛选 + 情感分析 | 🥇 强烈推荐 |
| OpenClaw 全网眼睛 | — | 一条命令给 OpenClaw 装上网络访问 | 可选 |

**TrendRadar 详情**：
- 三种推送模式：增量监控（盯盘）、当前榜单（自媒体）、AI 语义筛选（情感分析）
- 支持 Docker 部署，数据本地存储
- 内置 11 个主流平台，可自定义 RSS 源
- AI 分析内容情感倾向（利好/利空）

### 5. Hermes 采集链（当前已落地）

```
Edge 书签 → obsidian-bookmark-import skill 解析
  → hybrid-web-scraper 采集
    → Crawl4AI（主）→ Playwright（备）→ Tavily Extract（微信）
      → note_generator → 00_Inbox
        → 20_Wiki（主题整理）→ 30_Outputs（分析报告）
```

## 落地优先级建议

| 优先级 | 方案 | 理由 | 替代/补充当前方案的哪个环节 |
|--------|------|------|---------------------------|
| 🥇 | TrendRadar 舆情监控 | 一键 Docker 部署，11 平台 + AI 筛选 | 补充信息源获取（当前只靠书签导入） |
| 🥈 | BrowserAct stealth-extract | 一条命令提取渲染页面，Markdown 输出 | 补充 Crawl4AI 的备选方案，适合快速提取 |
| 🥉 | Scrapling 自愈爬虫 | 解决**非微信网站**选择器失效/Cloudflare 反爬 | 补充 Crawl4AI 的反指纹能力（微信场景不适用） |
| ④ | Browser-Use 自动采集 | LLM 驱动，适合需要登录/交互的页面 | 补充 Playwright 的智能化 |
| ⑤ | Firecrawl API | Markdown 输出，适合批量喂 AI | 补充 Tavily 的备选 |
