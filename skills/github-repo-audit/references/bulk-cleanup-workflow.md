# Bulk GitHub Repo Cleanup Workflow

## When to Use
User has many repos (50+) and wants to audit/delete stale ones in bulk.

## Workflow

### Step 1: Fetch All Repos (paginated)
```python
import urllib.request, json, os
token = os.popen("cat /root/.github_token.b64 | base64 -d").read().strip()
all_repos = []
page = 1
while True:
    url = f"https://api.github.com/user/repos?per_page=100&page={page}&sort=updated"
    req = urllib.request.Request(url, headers={"Authorization": f"token {token}"})
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read())
    if not data:
        break
    all_repos.extend(data)
    page += 1
```

### Step 2: Categorize
- Active: `pushed_at > '2024-01-01'`
- Dormant: `pushed_at <= '2024-01-01'`
- Large: `size >= 50*1024` (50MB)
- Very old: `pushed_at < '2020-01-01'`

### Step 3: Confirm Before Deleting
Always show the user a table and ask for confirmation. Never auto-delete more than 10 repos.

### Step 4: Batch Delete via API
```python
for repo in confirmed_list:
    url = f"https://api.github.com/repos/owner/{repo}"
    req = urllib.request.Request(url, headers={"Authorization": f"token {token}"}, method="DELETE")
    urllib.request.urlopen(req)
```

### Step 5: Report Results
Show success/failure for each. 403 errors mean manual deletion needed.

## Pitfalls
- 403 Forbidden: Some repos return 403 even when owned. Delete via web UI.
- Pagination: Always fetch all pages before listing.
- Duplicate names with different owners possible.
