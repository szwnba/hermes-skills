# Evolution Pattern: Raw → Wiki → Outputs

## Origin
Inspired by Andrej Karpathy's personal knowledge base approach (shared on X, Jan 2025), documented by Nick Spisak.

## Concept
Don't manually organize notes. Instead:
1. **Raw** — dump everything into `00_Inbox/` unorganized
2. **Wiki** — AI reads raw, compiles themed wiki pages with cross-links
3. **Outputs** — AI generates analyses, briefs, Q&A from the wiki
4. **Evolve** — new raw material → recompile wiki → better answers → update wiki

## Implementation in This Vault

### Directory Layout
```
Vault/
├── KNOWLEDGE_BASE.md   ← Schema (the "instruction manual" for AI)
├── 00_Inbox/           ← Raw: uncategorized scraped articles
├── 20_Wiki/            ← Wiki: AI-compiled themed pages + INDEX.md
├── 30_Outputs/         ← Outputs: AI-generated analyses and briefs
├── 00_文章看板.md      ← Dashboard: all raw articles table
└── Templates/          ← Note templates
```

### How It Works

**Step 1: Collect**
- Use `batch_scrape.py` to scrape bookmarks into `00_Inbox/`
- Each note has frontmatter: title, folder, url, date, source

**Step 2: Compile Wiki**
- Run `compile_wiki.py --vault /path/to/vault`
- Script reads all `00_Inbox/*.md`, groups by folder/topic
- Generates `20_Wiki/{topic}.md` with article tables and cross-links
- Maintains `20_Wiki/INDEX.md` as the master index

**Step 3: Query & Analyze**
- Ask AI: "基于 Wiki 回答：Browser Use 和 Stagehand 的区别？"
- AI reads wiki pages + raw articles to answer
- Store analysis in `30_Outputs/`

**Step 4: Health Check**
- Periodically: "审查整个 wiki/ 目录，标记矛盾，找空白"
- AI suggests new articles to fill gaps

### Topic Clusters (in compile_wiki.py)
Folders map to clusters:
- AI Agent 与自主代理: OpenClaw, AI_Skill, AI智能体
- 浏览器自动化: BrowserUse, AgentBrowser, Playwright_MCP, Stagehand
- 编程助手: ClaudeCode, Claude_OpenCode
- 测试自动化: 测试用例, 测试Agent, 视觉AI测试
- 开源平台与工具: 开源平台, Onboarding
- 投资与交易: 投资

### Quality Rating
- 🟢 >3000 bytes — good quality
- 🟡 1000-3000 bytes — medium
- 🔴 <1000 bytes — needs improvement

## Key Insight
The power comes from automation + iteration. Don't spend time organizing manually. Let AI do it. Each compilation cycle produces a better wiki. The system evolves.
