# GitHub Repository Batch Audit & Cleanup

> **Created**: 2026-06-28
> **Source**: Session cleaning 104→61 repos for user szwnba
> **Use**: When user asks to audit, review, or clean up their GitHub repos

## Pattern: Audit → Categorize → Recommend → Delete

### Step 1: Fetch All Repos (with pagination)

```python
import json, os
token = os.popen("cat /root/.github_token.b64 | base64 -d").read().strip()
import urllib.request

all_repos = []
page = 1
while True:
    url = f"https://api.github.com/user/repos?per_page=100&page={page}&sort=updated"
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    })
    data = json.loads(urllib.request.urlopen(req).read())
    if not data:
        break
    all_repos.extend(data)
    page += 1
```

### Step 2: Categorize & Analyze

Useful categorizations for cleanup recommendations:

| Dimension | Buckets | Action |
|-----------|---------|--------|
| **Activity** | Active (>current year), Dormant (>1yr), Dead (>3yr) | Dead → delete candidates |
| **Size** | <5MB, 5-50MB, >50MB | Large dormant → delete candidates |
| **Stars** | 0 stars, 1+ stars | 0-star dormant → low value |
| **Visibility** | Private 🔒, Public 🌐 | Private dormant → safe to delete |
| **Language** | null/empty → likely fork or template | Consider cleanup |

### Step 3: Present Audit Table

Format output as a table sorted by last push date. Include:
- Lock/Public icon
- Repo name, branch, size, language
- Stars count
- Last push date

### Step 4: Batch Delete (user confirms)

```python
repos_to_delete = ["repo1", "repo2", ...]
ok, fail = 0, 0
for repo in repos_to_delete:
    url = f"https://api.github.com/repos/{owner}/{repo}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }, method="DELETE")
    try:
        urllib.request.urlopen(req)
        print(f"✅ {repo}")
        ok += 1
    except urllib.error.HTTPError as e:
        print(f"❌ {repo}: {e.code}")
        fail += 1
```

### Pitfalls

- **403 Forbidden**: Some repos can't be deleted via API even if owned (token scope issues, protection rules). Fall back to web UI.
- **Hermes truncates API tokens**: Always read from `~/.github_token.b64` via `os.popen()`, never assign to a variable named `GITHUB_TOKEN`.
- **`language: null`**: Doesn't mean empty repo — often a fork or binary-heavy repo. Check `size` field instead.
- **Size units**: API returns KB. `r['size'] > 50 * 1024` means >50MB.
- **Pagination**: Must loop pages; 100 repos per page max. Single-page fetch misses repos beyond page 1.
- **User preference**: This user prefers direct action — present the table, then delete immediately when confirmed, don't ask for re-confirmation on each batch.
