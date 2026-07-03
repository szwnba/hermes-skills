---
name: github-repo-audit
description: Systematic auditing of GitHub repositories — local filesystem scanning, remote API analysis, cleanup recommendations.
---

# GitHub Repository Audit

Systematic auditing of GitHub repositories. Useful for cleanup, inventory, and analysis.

## Local Repo Scanning

Find all git repos on the filesystem:

```bash
find /root /home /opt /var /tmp -maxdepth 4 -name ".git" -type d 2>/dev/null
```

For each repo, gather: name, owner (from remote URL), branch, commit count, size, last commit.

## Remote Repo Analysis (GitHub API)

```python
import urllib.request, json, os
token = os.popen("cat /root/.github_token.b64 | base64 -d").read().strip()

all_repos = []
page = 1
while True:
    url = f"https://api.github.com/user/repos?per_page=100&page={page}&sort=updated"
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    })
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read())
    if not data:
        break
    all_repos.extend(data)
    page += 1
```

## Key Metrics

| Metric | Query |
|--------|-------|
| Total repos | `len(repos)` |
| Active (>2025) | `[r for r in repos if r.get('pushed_at','') > '2025-01-01']` |
| Dormant (<2025) | `[r for r in repos if r.get('pushed_at','') <= '2025-01-01']` |
| Largest repos | `sorted(repos, key=lambda r: r['size'], reverse=True)[:10]` |
| No stars | `[r for r in repos if (r.get('stargazers_count') or 0) == 0]` |
| Private | `[r for r in repos if r.get('private')]` |
| Very old (>5 yrs) | `[r for r in repos if r.get('pushed_at','') < '2020-01-01']` |
| Big repos (>50MB) | `[r for r in repos if r['size'] > 50*1024]` |

## Size Conversion

GitHub API `size` is in KB. Convert to MB: `size_kb // 1024`.

## Bulk Delete Repositories (Remote)

**Pattern**: Use `urllib` + DELETE API (no `gh` CLI dependency):

```python
import os
token = os.popen("cat /root/.github_token.b64 | base64 -d").read().strip()
import urllib.request

repos = ["repo1", "repo2", "repo3"]
for repo in repos:
    url = f"https://api.github.com/repos/{owner}/{repo}"
    req = urllib.request.Request(url, headers={"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}, method="DELETE")
    try:
        resp = urllib.request.urlopen(req)
        print(f"✅ {repo}")
    except urllib.error.HTTPError as e:
        print(f"❌ {repo}: {e.code}")
```

**Pitfall**: 403 Forbidden can occur even on repos you own — likely due to API token scope or repo protection rules. For 403s, delete manually via GitHub web UI.

**Pitfall**: `rm -rf` only deletes the LOCAL copy. Remote repo survives. Always use the DELETE API (above) to remove from GitHub.

## Cleanup Workflow

Recommended order for repo cleanup:
1. `curl` API to list all repos with metadata (size, age, activity)
2. Categorize: active vs dormant, large vs small, old vs new
3. Delete oldest/smallest first (low risk)
4. Verify deletion by re-fetching the list

## Pitfalls

1. **Duplicate repos**: Same name may exist in multiple locations — check before deleting
2. **Pagination**: GitHub API returns max 100 per page — always paginate until empty list
3. **Token expiry**: If API returns 401, regenerate token at GitHub settings
4. **Owner detection**: Remote URL may be SSH (`git@`) or HTTPS — parse both formats
5. **Local vs remote**: `rm -rf` only deletes local copy; remote survives. Use DELETE API or `gh repo delete` for remote.
6. **403 on delete**: Some repos may return 403 even if you own them (token scope, protection rules). Fall back to manual web UI deletion.
7. **Bulk delete script**: Always batch deletions — one script per session, check results after each batch. Don't delete more than 10 repos in one batch without confirming.

## Support Files
- `references/bulk-cleanup-workflow.md` — Step-by-step bulk cleanup workflow with code templates
