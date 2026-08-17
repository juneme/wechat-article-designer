# WeChat Article Designer

一套面向微信公众号文章的 Codex Skill。它从 24 种内部视觉 DNA 中按内容重新合成原创版式，并输出适合公众号编辑器的移动端 HTML、图片占位、封面方案与发布前审查结果。

![24-style visual DNA gallery](assets/previews/template-gallery.png)

## 核心能力

- 24 种可组合视觉 DNA，不把模板换色当作原创设计。
- Steady / Creative 两种交付模式与明确的兼容性降级规则。
- Paper Cut Artbook、Contour Field Notes、Still-frame Cinema 等艺术编辑方向。
- 手机优先排版、照片占位、手动横向滑块和发布前风险审查。
- 强制区分聊天上下文与公开文章，发布前自动扫描“根据你的要求”“我已经为你”等对话残留。
- 照片框采用实测通过的可编辑段落锚点：视觉样式和高度留在 `section`，1px `p` 只负责提供光标，点击空白框即可直接粘贴。
- 公众号正文保持静态，不包含动效或状态性交互。
- 通过独立服务器 API 上传正文图片和封面；选择完整直发流程后，校验通过即自动写入微信公众号草稿箱，无需二次确认。

## 安装

```powershell
git clone https://github.com/juneme/wechat-article-designer.git "$HOME/.codex/skills/wechat-article-designer"
```

重新启动 Codex，或开启一个新任务让 skill 被重新发现。

直发模式还需要在运行 Codex 的环境中配置：

```text
WECHAT_CONSOLE_URL=http://你的控制台地址
WECHAT_IMAGE_API_KEY=服务器 AI_API_KEY
WECHAT_PUBLISH_API_KEY=服务器 PUBLISH_API_KEY
```

完整流程见 `references/direct-publishing.md`。密钥不得写入 Skill、文章 JSON 或公开仓库。

没有域名时可直接填写 `http://服务器IP:8787`，无需 SSH 隧道。客户端会继续执行并返回未加密传输警告；HTTP 会明文传输 Bearer Key 和文章数据，条件具备后仍建议升级为 HTTPS。

## 使用

```text
$wechat-article-designer 根据这篇稿件设计一个有纸艺画册感、适合公众号发布的原创版本。
```

没有明确指定模板时，skill 会根据主题、受众、图片职责、信息密度和期望行动，从多个 DNA 维度重新合成设计指纹。只有用户明确要求浏览风格时，才展示 24 种 DNA 总览。

## 目录

```text
wechat-article-designer/
├── SKILL.md
├── GALLERY.md
├── agents/
├── assets/
├── references/
└── scripts/
```

## 验证

在已安装 Codex 内置 `skill-creator` 的环境中运行：

```powershell
$env:PYTHONUTF8='1'
python "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" .
python scripts/audit_audience_boundary.py article.html
```

## 发布边界

- 最终公众号正文不使用脚本、事件处理器、外部样式表或本地图片路径。
- 写入草稿箱不等于正式发布；最终群发仍需在微信公众号后台预览并扫码或人工确认。
- 手动换图时直接点击空白照片框插入图片，不要全选、退格或删除框内的 1px 段落锚点。
- 手动横向滑块是经过保留的静态例外，必须同时提供可读的单列降级结构。
- 浏览器预览通过不等于公众号编辑器通过；真实发布仍需草稿箱粘贴和手机预览。

## License

MIT License. See `LICENSE` in the project root.
