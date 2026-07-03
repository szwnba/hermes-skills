# Cron Prompt Patterns for Intelligence Reports

## Pattern 1: Direct Script Run + Format

Best when the script is stable and produces consistent JSON output.

```
Run the intelligence collection script and deliver the report:

1. `python3 /root/.hermes/profiles/collector/scripts/intelligence_agent.py --json`
2. Parse the JSON output into a structured report
3. For each source: show top 5 items with key details
4. If a source shows "error", mark with ⚠️ and continue
5. Format for Feishu delivery with clear section headers
```

## Pattern 2: Fallback Chain

Best when sources are unreliable — try multiple approaches per source.

```
Collect today's intelligence with fallback chain:

GitHub:
- Primary: `python3 /root/.hermes/profiles/collector/scripts/intelligence_agent.py --source github`
- Fallback: `curl` to GitHub API directly
- Last resort: web_search for "GitHub trending repositories today"

arXiv:
- Primary: script's arxiv collector
- Fallback: web_search for "arxiv cs.AI latest papers"

RSS:
- Primary: blogwatcher-cli articles
- Fallback: skip if not installed

Twitter:
- Primary: xurl search
- Fallback: skip if auth not configured

Format all successful sources into one report. Mark failures with ⚠️.
```

## Pattern 3: Multi-Stage with Context

Best when the cron job needs to reference previous runs or other data.

```
Step 1: Run intelligence script
Step 2: Check yesterday's report for continuity (session_search)
Step 3: Highlight what's NEW since yesterday
Step 4: Deliver delta report
```

## Pattern 4: Complete Failure Mode

When ALL data collection tools fail (terminal blocked by security scan, web_search 401, browser timeout), produce a structured failure report. This is better than silently delivering nothing.

```
Attempt to collect intelligence data:
1. Try terminal: `python3 /root/.hermes/profiles/collector/scripts/intelligence_agent.py --json`
   - If blocked by security scan (tirith:unknown), note the error
2. Try web_search / web_extract for each source
   - If 401 Unauthorized, note the error
3. Try browser_navigate to GitHub/arXiv
   - If timeout, note the error

If ALL tools fail:
- Produce a failure report using the template from `references/failure-report-template.md`
- List each attempted tool and its specific error
- Suggest concrete remediation steps
- Deliver the failure report (don't stay silent)
```

## Key Principles

1. **Always handle partial failure** — never let one broken source kill the whole report
2. **Specify output format** — tell the cron LLM exactly how to structure the report
3. **Include fallback instructions** — what to do if primary method fails
4. **Keep it self-contained** — cron jobs run without user context, don't reference "ask the user"
5. **Use `--json` flag** — structured output is easier for the cron LLM to parse and format
6. **Handle complete failure** — when ALL tools fail, deliver a diagnostic report, not silence
