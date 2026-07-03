# 13 篇永久丢失的微信公众号文章

**记录时间**: 2026-06-28
**原因**: 作者删除或设置访问限制，Tavily Extract + Playwright 均无法访问

## 判断标准（对应 SKILL.md pitfall #10）

当 **Tavily Extract** 和 **Playwright** 都失败时，文章已永久丢失，不要重试。

- Tavily Extract 失败特征：`"Error fetching content"` 或 `"Failed to fetch url"`
- Playwright 失败特征：`Timeout 30000ms exceeded` on `div.rich_media_content`

## 清单

| # | 标题 | 原始分类 | 失败原因 |
|---|------|----------|----------|
| 1 | Firecrawl | 爬虫 | Extract: Error fetching content |
| 2 | (URL直出) | openclaw | Extract: Error fetching content |
| 3 | 免费！OpenCodeUI 让你随时随地 AI Coding | opencode | Extract: Failed to fetch url |
| 4 | 自建中转站，每天烧掉1亿token实现GPT-5.4自由 | 大模型 | Extract: Error fetching content |
| 5 | 如何让AI帮你做前端自动化测试？我们这样落地了 | AI前沿理念 | Extract: Error fetching content |
| 6 | Playwright + DeepSeek 实战：AI自动生成 POM | Playwright × AI实战索引 | Extract: Failed to fetch url |
| 7 | 从录制到生产：Playwright 自动化录制→AI优化→POM化 | Playwright × AI实战索引 | Extract: Failed to fetch url |
| 8 | AI操作网页：browser-use和AI大模型互动解析 | BrowserUse | Extract: Error fetching content |
| 9 | 30行代码让DeepSeek做Web自动化测试 | BrowserUse | Extract: Failed to fetch url |
| 10 | 快速上手：LangChain + AgentRun 浏览器沙箱 | BrowserUse | Extract: Failed to fetch url |
| 11 | 如何让AI帮你做前端自动化测试？我们这样落地了 | BrowserUse | Extract: Error fetching content |
| 12 | 从录制到生产：Playwright 自动化录制→AI优化→POM化 | playwright 集成AI+自愈 | Extract: Failed to fetch url |
| 13 | 打造Cursor + Playwright自动化测试环境【实战教程】 | Playwright MCP | Extract: Failed to fetch url |

## 备注

- 第 5/11 篇和第 7/12 篇是重复标题（不同 URL），可能来自不同公众号转载
- 最终采集率：308/321 ≈ 95.9%（目标 321 篇，成功 308 篇，丢失 13 篇）
