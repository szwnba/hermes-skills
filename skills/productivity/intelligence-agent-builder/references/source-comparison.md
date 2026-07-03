# Source Comparison: When to Use What

## GitHub Trending

| Approach | Pros | Cons | Best For |
|----------|------|------|----------|
| GitHub Search API | Structured JSON, star counts, filters | Rate limited (30/min), needs token | Daily trending repos |
| `gh` CLI | Simple, authenticated | Needs gh installed | Quick lookups |
| web_search | No auth needed | Unstructured, slow | Fallback |

**Recommendation**: Use GitHub API with `pushed:>=YYYY-MM-DD` + `sort=stars`. Token from `/root/.github_token.b64`.

## arXiv Papers

| Approach | Pros | Cons | Best For |
|----------|------|------|----------|
| arXiv API | Free, structured, no auth | XML parsing, rate limited (~1/3s) | Primary source |
| Semantic Scholar API | JSON, citations, recommendations | Rate limited (1/sec) | Impact assessment |
| web_search | Easy | Unstructured | Fallback |

**Recommendation**: arXiv API for discovery, Semantic Scholar for citation context.

## RSS/Blogs

| Approach | Pros | Cons | Best For |
|----------|------|------|----------|
| blogwatcher-cli | Tracks read/unread, OPML import | Needs setup/install | Primary |
| direct RSS fetch | No deps | No tracking, manual parsing | Fallback |
| web_search | No setup needed | Slow, unstructured | Last resort |

**Recommendation**: blogwatcher-cli for ongoing monitoring. Install once, maintain DB.

## Twitter/X

| Approach | Pros | Cons | Best For |
|----------|------|------|----------|
| xurl CLI | Official API, structured JSON | Paid tier, needs OAuth setup | Primary |
| web_search | No setup | Very limited, often blocked | Fallback |

**Recommendation**: xurl CLI if user has X API access. Otherwise skip — Twitter data is unreliable without auth.

## General Decision Tree

```
Need data from source X?
  ├─ Has dedicated API? → Use API (GitHub, arXiv, xurl)
  ├─ Has RSS? → Use blogwatcher-cli
  └─ Neither? → web_search as last resort
```

**Priority order for intelligence agents**:
1. GitHub API (trending repos)
2. arXiv API (latest papers)
3. blogwatcher-cli (RSS feeds)
4. xurl CLI (Twitter)
5. web_search (fallback for everything)
