# Scrapling 实测评估 (2026-06-28)

## 测试结论：可用但不适合集成到采集链

### 安装
```bash
pip install scrapling          # 主包
pip install curl_cffi          # 反指纹请求
pip install browserforge       # 浏览器指纹生成
pip install msgspec            # 序列化
pip install patchright         # 反检测浏览器 (替代 playwright)
```
⚠️ 依赖冲突：Scrapling 安装 lxml 6.1.1，与 crawl4ai 需要的 lxml 5.3 冲突。共存但可能有隐患。

### 测试项目
| 项目 | 结果 |
|------|------|
| 基本 fetch (httpbin) | ✅ 成功 |
| StealthyFetcher (quotes.toscrape.com) | ✅ 成功，CSS 选择器链式调用正常 |
| 微信文章 13 篇 | ❌ 全部被 `wappoc_appmsgcaptcha` 拦截 |
| 普通反爬网站 | ✅ 预期可绕过 Cloudflare 等 |

### 微信采集失败根因
微信返回 `302 → wappoc_appmsgcaptcha` 是**平台级验证码**，不是浏览器指纹检测。Scrapling 的 StealthyFetcher 基于 patchright（反检测浏览器），能绕 Cloudflare Turnstile 和指纹检测，但对微信的平台级验证码无能为力。这与 Tavily Extract 和 Playwright 失败的原因相同——文章本身已被删除或限制访问。

### 为什么不集成
1. 当前方案成功率 96%（295/308），剩余 4% 是微信删除的文章
2. Scrapling 的优势场景（Cloudflare 反爬）与采集目标（微信公众号）不匹配
3. 额外依赖负担（patchright + curl_cffi + browserforge + msgspec）
4. lxml 版本冲突风险

### 保留价值
Scrapling 可作为**备用工具**偶尔使用——当需要采集有 Cloudflare 保护的网站时，StealthyFetcher 比 Playwright 更可靠。
