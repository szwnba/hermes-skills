# 微信公众号文章 curl + Python 解析模式

> 适用于从服务器 IP（无浏览器指纹）抓取微信文章。
> 2026-07-01 实测验证通过。

## 为什么 curl 可以绕过微信反爬

微信公众号的反爬是**平台级验证码**（302 → wappoc_appmsgcaptcha），基于**浏览器行为检测**而非 IP 封锁。curl 不执行 JS、无浏览器指纹、无鼠标移动/点击事件，反而不会被拦截。

| 工具 | 结果 | 原因 |
|------|------|------|
| Playwright (headless) | ❌ 失败 (0 chars) | 无头浏览器触发验证码 |
| BrowserAct stealth-extract | ❌ 失败 (302→captcha) | stealth 浏览器仍被检测 |
| **curl + Python** | ✅ 成功 (4000+ chars) | 无浏览器指纹，直接返回完整 HTML |

## 解析代码

```python
import re, html, time

with open('/tmp/wx_article.html', 'r', encoding='utf-8') as f:
    page_html = f.read()

# 1. 标题 — <meta property="og:title" content="...">
title_m = re.search(r'<meta property="og:title" content="(.*?)"', page_html)
title = html.unescape(title_m.group(1)) if title_m else 'Unknown'

# 2. 作者 — 从正文末尾 "作者: xxx" 提取（最可靠）
author_m = re.search(r'作者[：:]\s*([^\s<]+)\s*</', page_html)
author = author_m.group(1) if author_m else 'Unknown'

# 备用：从 profile 区域提取
# author_m = re.search(r'id="profileBt".*?>(.*?)</a>', page_html, re.DOTALL)
# author = re.sub(r'<[^>]+>', '', author_m.group(1)).strip()

# 3. 发布日期 — var ct = "unix_timestamp"
date_m = re.search(r'var ct = "(\d+)"', page_html)
date_str = time.strftime('%Y-%m-%d %H:%M', time.localtime(int(date_m.group(1)))) if date_m else 'Unknown'

# 4. 正文 — id="js_content" div 内
content_m = re.search(r'id="js_content"[^>]*>(.*?)</div>\s*<script', page_html, re.DOTALL)
if content_m:
    content_html = content_m.group(1)
    text = re.sub(r'<br\s*/?>', '\n', content_html)
    text = re.sub(r'</p>', '\n\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = html.unescape(text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
else:
    text = '内容提取失败'
```

## 完整采集流程

```bash
# Step 1: curl 抓取
curl -s -L \
  -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
  "https://mp.weixin.qq.com/s/ARTICLE_ID" \
  --max-time 15 \
  -o /tmp/wx_article.html

# Step 2: Python 解析（见上方代码）

# Step 3: 保存到 Obsidian
# 文件名: YYYY-MM-DD_标题.md
# 路径: ~/Documents/Obsidian Vault/00_Inbox/
```

## 判断文章已被删除

如果 curl 返回的 HTML 中：
- 不包含 `id="js_content"`
- 不包含 `rich_media_content`
- 不包含 `var ct = "..."`（日期变量）

则说明文章已被作者删除或设置了访问限制，不要继续重试。

## 注意事项

1. **User-Agent**: 使用 Chrome UA，不要太新或太旧（120.0 实测可用）
2. **超时**: `--max-time 15` 足够，微信响应通常 <5s
3. **编码**: 始终使用 `utf-8` 读取保存的文件
4. **正则**: `<meta property="og:title">` 比 `var msg_title` 更可靠（后者格式多变）
5. **作者**: 正文末尾 "作者: xxx" 最稳定，profile 区域格式因文章类型而异
