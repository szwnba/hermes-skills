# 🛠️ Hermes Agent Skills Backup

This repository contains all the skills and scripts from the `collector` profile of Hermes Agent.

## 📁 Structure

```
skills/
├── data-science/          # hybrid-web-scraper, jupyter-live-kernel
├── productivity/          # intelligence-agent-builder, knowledge-base-utilization, etc.
├── note-taking/           # obsidian
├── github/                # github-*, codebase-inspection
├── autonomous-ai-agents/  # hermes-agent, claude-code, codex, opencode
├── creative/              # architecture-diagram, ascii-art, etc.
├── research/              # arxiv, blogwatcher, polymarket
├── social-media/          # xurl
├── media/                 # gif-search, youtube-content
├── mlops/                 # huggingface-hub, serving-llms-vllm
├── smart-home/            # openhue
├── email/                 # himalaya
├── devops/                # kanban-worker, kanban-orchestrator
├── dogfood/               # dogfood
├── todoist/               # todoist
└── yuanbao/               # yuanbao

scripts/
├── intelligence_agent.py  # Daily intelligence collection
├── cron_matcher.py        # Todoist-KB matcher
└── ...

.env.example               # Template for environment variables
```

## 🚀 Installation

To use these skills with Hermes Agent:

```bash
# Clone this repo
git clone https://github.com/szwnba/hermes-skills.git

# Copy skills to your Hermes profile
cp -r hermes-skills/skills/* ~/.hermes/skills/

# Or for a specific profile
cp -r hermes-skills/skills/* ~/.hermes/profiles/collector/skills/
```

## 📜 License

MIT License
