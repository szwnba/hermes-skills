# 知识库维护工作流（Vault Maintenance）

**适用场景**: Inbox 积累了大量文章后，需要整理分类、重编 Wiki、生成分析报告。

## 三步流程

### Step 1: 分类归一化（Normalize Folders）

书签导入时 folder 名称来自浏览器书签文件夹，常有大小写/命名差异（如 `openclaw` vs `OpenClaw` vs `OpenClaw测试`）。需要建立映射表，批量更新 frontmatter。

**操作**: 遍历 `00_Inbox/*.md`，读取 `folder:` 字段，按映射表替换。

```python
import os, re
from collections import Counter

folder_map = {
    'openclaw': 'OpenClaw', 'OpenClaw': 'OpenClaw',
    'OpenClaw测试': 'OpenClaw', 'OpenClaw自动化测试': 'OpenClaw',
    'Playwright_MCP': 'Playwright AI', 'Playwright MCP': 'Playwright AI',
    # ... 完整映射见下方
}
# 替换 frontmatter 中的 folder 字段
old_str = f'folder: {old_folder}'
new_str = f'folder: {new_folder}'
content = content.replace(old_str, new_str, 1)
```

**验证**: 替换后统计分类数（应从 40+ 降到 ~12）。

### Step 2: 重编 Wiki（Recompile Wiki）

清空 `20_Wiki/*.md`，基于全量 Inbox 文章重新生成主题页面。

每个主题页面包含：
- 摘要（文章数、总大小、主题描述）
- 文章表格（按内容长度排序，带质量标记 🟢🟡🔴）
- `[[wikilink]]` 格式链接到原始笔记
- 相关主题交叉链接

**INDEX.md** 包含所有主题的总览表格。

### Step 3: 生成分析报告（Generate Output）

在 `30_Outputs/` 生成知识库全景分析报告，包括：
- 知识库概览（总数、来源、质量分布）
- 主题分布表与核心主题解读
- 高频关键词分析
- Top 20 高质量文章
- 技术栈画像（ASCII 图）
- 行动建议

## 归一化映射表（308 篇实际数据）

42 个原始分类 → 13 个规范分类：

| 规范分类 | 合并的原始分类 |
|----------|----------------|
| OpenClaw | openclaw, OpenClaw, OpenClaw测试, OpenClaw自动化测试 |
| Playwright AI | Playwright_MCP, Playwright MCP, Playwright测试, Playwright_AI, playwright 集成AI+自愈, playwright CLI skill, playwright test agent |
| 测试工程 | 测试skill, 测试用例生成, 测试用例, 测试Agent开发, 测试Agent, 视觉AI测试 |
| 投资与变现 | 投资, 量化交易 |
| 浏览器自动化 | BrowserUse, AgentBrowser, Agent Browser, Stagehand |
| AI Skill | AI_Skill, AI Skill |
| Claude Code & OpenCode | claudecode, ClaudeCode, opencode, Claude_OpenCode, Claude Opencode CLI 自动化 |
| AI 理念与范式 | AI前沿理念, AI范式, 大模型 |
| Onboarding | onboarding, Onboarding |
| AI Agent | AI智能体, 工作流 |
| 开源工具 | 开源平台, 爬虫 |
| Hermes | Hermes |

## 质量标记标准

- 🟢 `content_length > 5000` (高质量，完整采集)
- 🟡 `1000 < content_length <= 5000` (部分采集)
- 🔴 `content_length <= 1000` (采集失败或截断)
