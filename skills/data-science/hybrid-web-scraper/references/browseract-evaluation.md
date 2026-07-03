# BrowserAct 实测评估 (2026-07-01)

## 测试环境
- browser-act 1.0.3
- API Key: app-Yc9hpNcE6Cl2DpzdUzIP8Jp8 (免费账号)
- 服务器: Linux, 无 GUI

## 功能矩阵

| 功能 | 免费 | 付费 | 实测结果 |
|------|------|------|---------|
| stealth-extract | ✅ | ✅ | ✅ 可用，默认中国 IP (120.229.x.x) |
| --content-type markdown/html | ✅ | ✅ | ✅ |
| --timeout / --output | ✅ | ✅ | ✅ |
| --custom-proxy | ✅ | ✅ | ✅ 可用自己的代理 |
| --dynamic-proxy | ❌ | ✅ | 未测试 |
| --static-proxy | ❌ | ✅ | 未测试 |
| browser create (chrome) | ✅ | ✅ | ✅ 可创建 |
| browser open (交互) | ❌ 需 GUI | ❌ 需 GUI | ❌ 服务器不可用 |
| stealth browser | ✅ (≤5) | ✅ | ⚠️ 需授权链接 |
| solve-captcha | ❌ | ✅ | 未测试 |
| remote-assist | ❌ | ✅ | 未测试 |

## 实测结论

### ✅ 优点
- stealth-extract 一条命令提取渲染后内容，比 Playwright 脚本更简洁
- 输出 Markdown 格式，适合 AI Agent 消费
- 跨会话 IP 一致（默认代理池行为）
- 对国内站点友好

### ⚠️ 限制
- 强反爬站点（Reddit/Product Hunt/Cloudflare JS Challenge）免费 tier 403
- browser open 交互式功能需 GUI 环境
- 微信公众号文章不可用（平台级验证码，非浏览器指纹问题）

### 对比 Playwright
| 维度 | BrowserAct | Playwright |
|------|-----------|------------|
| 安装 | `uv tool install` (一键) | `pip install + playwright install` |
| 使用 | CLI 一行命令 | Python/JS 脚本 |
| 反爬 | ⚠️ 免费有限 | ⚠️ 需手动配置 |
| 验证码 | ⚠️ 需付费 | ❌ 需手动处理 |
| 学习曲线 | 低 | 中 |
| 灵活性 | 中 | 高 |

**建议**: 简单页面提取用 BrowserAct，复杂自动化用 Playwright，两者互补。

## 关键发现
- BrowserAct stealth-extract 对微信公众号触发 302 → wappoc_appmsgcaptcha
- curl 直连反而可以绕过微信反爬（无浏览器指纹）
- 这印证了微信反爬是平台级验证码，非浏览器指纹检测
