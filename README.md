# WeChat Article Designer

[![Release](https://img.shields.io/github/v/release/juneme/wechat-article-designer?style=flat-square&color=07C160)](https://github.com/juneme/wechat-article-designer/releases/latest)
[![CI](https://img.shields.io/github/actions/workflow/status/juneme/wechat-article-designer/ci.yml?branch=main&style=flat-square&label=CI)](https://github.com/juneme/wechat-article-designer/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/juneme/wechat-article-designer?style=flat-square)](LICENSE)
[![Console Server](https://img.shields.io/badge/companion-wechat--console--server-F1C75B?style=flat-square&logo=github&logoColor=171712)](https://github.com/juneme/wechat-console-server)

![WeChat Article Designer：从内容地图、动态设计语法到移动排版与草稿交付](docs/images/article-designer-hero.svg)

面向微信公众号的 Codex Skill。它先理解文章的读者、事实、图片与行动目标，再综合持续学习的设计语法，为当前内容生成专属结构和移动排版；不是从固定 HTML 模板中挑一个套用。

## 完整项目 = Skill + Server

| 设计端：本仓库 | 交付端：[`wechat-console-server`](https://github.com/juneme/wechat-console-server) |
|---|---|
| 内容地图、原创视觉综合、中文移动排版、兼容性审查 | 加密托管公众号凭据、上传图片、接口诊断、幂等写入草稿箱 |
| 安装在运行 Codex 的电脑上 | 部署在有固定公网出口 IP 的服务器上 |
| 不读取 AppSecret，不自动群发 | 不负责写文章，不向浏览器或 AI 暴露 AppSecret |

![从文章内容经 Article Designer 和 Console Server 进入微信公众号草稿箱的完整流程](docs/images/project-flow.svg)

## 它如何设计

| 阶段 | 产出 |
|---|---|
| 理解内容 | 读者、叙事、事实、图片、证据与行动目标的内容地图 |
| 综合风格 | 从动态设计语法生成本文专属的色彩、构图、媒介节奏与视觉母题 |
| 组织文字 | 为标题、章节、正文、标签、说明和数据建立中文移动排版层级 |
| 构建文章 | 生成带内联样式的公众号 HTML 片段，并为不稳定效果提供静态降级 |
| 校验交付 | 审查受众边界、宽度、字距、对比度与编辑器兼容性，按授权预览或写入草稿 |

设计知识会持续扩展，但不会变成模板选择器。每次创作都必须从当前文章重新建立内容结构与设计契约；历史案例只提供可组合的设计能力。

## 安装

```powershell
git clone https://github.com/juneme/wechat-article-designer.git "$env:USERPROFILE\.codex\skills\wechat-article-designer"
```

重新启动 Codex 或创建新任务，使 Skill 完成重新发现。然后可以直接说：

```text
使用 $wechat-article-designer 制作这篇公众号文章，先预览，不要写入草稿箱。
```

## 连接 Console Server

先按 [`wechat-console-server` 部署说明](https://github.com/juneme/wechat-console-server#三步开始)准备服务端，再从控制台“API 接入 → Skill 客户端配置”取得以下三个变量：

```text
WECHAT_CONSOLE_URL
WECHAT_IMAGE_API_KEY
WECHAT_PUBLISH_API_KEY
```

密钥只配置在运行 Codex 的用户环境中，不得写入 Skill、文章 JSON、Issue 或公开仓库。连接后可先执行只读检查：

```powershell
python scripts/wechat_console_api.py status
```

完整的图片上传、封面处理、草稿校验和幂等规则见 [`references/direct-publishing.md`](references/direct-publishing.md)。预览、排版和上传图片都不代表授权创建草稿；写入草稿箱也不等于正式群发。

## 持续学习

学习新设计来源时，Skill 会覆盖公开集合与详情页，将观察结果结构化为色彩、文字、构图、媒介、节奏、证据边界和可降级行为，再把真正新增的能力合并进动态设计语法。来源条目数只用于覆盖审计，不限定可用风格数量。

当前 Superdesign 学习快照与逐条索引：

- [`references/superdesign-study-2026-08-20.md`](references/superdesign-study-2026-08-20.md)
- [`references/superdesign-record-index-2026-08-20.md`](references/superdesign-record-index-2026-08-20.md)

## 验证

```powershell
$env:PYTHONUTF8='1'
python "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" .
python -m compileall -q scripts
python -m ruff check .
```

生成文章后再运行受众边界、移动宽度、中文排版和颜色对比审查：

```powershell
python scripts/audit_audience_boundary.py article.html
python scripts/audit_wechat_widths.py article.html
python scripts/audit_wechat_typography.py article.html
python scripts/audit_wechat_contrast.py article.html
```

浏览器预览不能替代微信公众号编辑器与手机预览。仓库不携带固定文章 HTML、项目测试数据或真实公众号凭据。

## License

MIT License. See [`LICENSE`](LICENSE).
