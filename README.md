# WeChat Article Designer

面向微信公众号文章设计、校验与草稿交付的 Codex Skill。它把持续学习的设计知识归一为色彩、文字、结构、媒介、节奏和证据边界，再根据每篇文章的内容生成专属设计，而不是套用固定 HTML 模板。

## 核心能力

- 从受众、目的、事实、图片和行动目标建立内容地图。
- 先规划语义模块与中文移动排版，再形成文章专属设计契约。
- 通过持续扩展的设计语法综合生成风格，不限定模板数量。
- 提供 Steady / Creative 两种交付模式和静态降级规则。
- 审查受众边界、移动宽度、文字排版、颜色对比和公众号兼容性。
- 支持图片上传、封面上传、草稿校验和经授权的草稿箱写入。

## 设计学习

学习新来源时，需要覆盖当前全部公开条目、读取每条详情、维护结构化索引，并把真正新增的能力合并到动态设计语法。某次学习观察到的条目数只用于覆盖审计，不代表可用风格数量。

当前 Superdesign 学习快照与逐条索引位于：

- `references/superdesign-study-2026-08-20.md`
- `references/superdesign-record-index-2026-08-20.md`

## 安装

```powershell
git clone https://github.com/juneme/wechat-article-designer.git "$HOME/.codex/skills/wechat-article-designer"
```

重新启动 Codex 或创建新任务，使 Skill 完成重新发现。

直发模式需要在运行环境配置 `WECHAT_CONSOLE_URL`、`WECHAT_IMAGE_API_KEY` 和 `WECHAT_PUBLISH_API_KEY`。密钥不得写入 Skill、文章 JSON 或公开仓库。完整流程见 `references/direct-publishing.md`。

## 发布结构

```text
wechat-article-designer/
|-- SKILL.md
|-- GALLERY.md
|-- agents/
|-- references/
|-- scripts/
|-- .github/workflows/
|-- pyproject.toml
|-- requirements-dev.txt
`-- LICENSE
```

仓库不携带固定文章 HTML、预览图片、测试数据或项目专属封面生成器。

## 验证

```powershell
$env:PYTHONUTF8='1'
python "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" .
python -m compileall -q scripts
python -m ruff check .
```

生成文章后再运行：

```powershell
python scripts/audit_audience_boundary.py article.html
python scripts/audit_wechat_widths.py article.html
python scripts/audit_wechat_typography.py article.html
python scripts/audit_wechat_contrast.py article.html
```

浏览器预览不能替代微信公众号编辑器与手机预览。写入草稿箱也不等于正式发布；最终群发仍需在微信公众号后台确认。

## License

MIT License. See `LICENSE`.
