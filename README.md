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
| 锁定设计契约 | 逐项确定版式、间距、文字参数、缩进、色彩角色、图像、几何、动效选择与降级方案 |
| 综合风格 | 从动态设计语法生成本文专属的色彩、构图、媒介节奏与视觉母题 |
| 组织文字 | 为标题、章节、正文、标签、说明和数据建立带实际数值的中文移动排版层级 |
| 构建文章 | 生成带内联样式的公众号 HTML 片段，并为不稳定效果提供静态降级 |
| 管理版本 | 每篇文章使用独立工作区，同步片段、预览、草稿 JSON、资产与历史版本 |
| 校验交付 | 审查受众边界、宽度、字距、对比度与编辑器兼容性；后端就绪时自动写入新草稿，否则生成本地预览 |

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

完整的图片生成、上传、封面处理、草稿校验和幂等规则见 [`references/direct-publishing.md`](references/direct-publishing.md)。三个变量齐全且健康检查成功时，普通的新文章或实质性改版会在终审通过后自动创建新草稿，无需二次确认；写入草稿箱不等于正式群发，最终由用户审阅和决定。

## 文章工作区

先为文章建立独立目录，避免下一篇文章覆盖当前资产：

```powershell
python scripts/article_workspace.py create --title '文章标题' --date 'YYYY-MM-DD'
```

若三个 Console 配置完整且状态健康，默认直接交付草稿，建工作区时使用 `--no-preview`；用户明确要求只预览，或后端未配置/不可用时，才使用默认的本地预览路线。

只编辑工作区中的 `design-contract.json`，确认裸文、版式、文字排版、颜色、图像、几何、动效选择和静态降级均已确定，将状态改为 `PLANNED` 并执行计划门：

```powershell
python scripts/article_workspace.py plan '.\articles\日期_标题'
```

随后实现 `fragment.html` 并编辑 `article.json`。不要手工设置 `READY` 或正文摘要；统一发布命令会绑定最终片段、执行全部审查、选择路线并完成草稿或预览交付。`design-contract.md` 是自动生成的内部阅读视图，不应手工编辑：

```powershell
python scripts/release_article.py deliver '.\articles\日期_标题'
```

发布命令会拒绝未记录计划、提前实现 HTML、未完成契约、过期正文摘要或任一审查错误；标题、作者、摘要和本地片段先通过终审，才允许上传素材。后端健康时自动创建新草稿，否则只生成无脚本预览。缺少必需图片时会返回 `attempt_id`；真实生成失败后，必须同时提交该 ID 和失败原因才可转为预览。正文、元数据、契约、资产或预览变化都会递增版本，仅草稿载荷变化才轮换幂等 ID。详见 [`references/article-workspaces.md`](references/article-workspaces.md)。

升级旧文章工作区时先运行：

```powershell
python scripts/article_workspace.py migrate '.\articles\日期_标题'
```

草稿请求超时或结果未知会持久化锁定工作区。用户检查真实草稿箱后，使用 `resolve-draft --outcome created` 或 `--outcome not-created` 记录唯一结论，再决定是否继续。

## SVG 互动排版

SVG 是 Creative 模式中的稳定编辑能力。需要揭晓、对比、切换、横向序列、形态变化或节奏强调时，按 [`references/svg-design-genes.md`](references/svg-design-genes.md) 从文章内容和 Visual DNA 原创组件。关键信息应在初始状态或相邻正文中完整可读，不需要重复的静态回退块或额外的 SVG 验证流程。

## 持续学习

学习新设计来源时，只把可复用的文字、构图、媒介、节奏和交互关系合并进核心设计语法；全部研究过程材料都留在 Skill 之外并在综合后丢弃。

## 验证

```powershell
$env:PYTHONUTF8='1'
python "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" .
python -B -c "import ast,pathlib; [ast.parse(p.read_text(encoding='utf-8')) for p in pathlib.Path('scripts').glob('*.py')]"
python -m ruff check --no-cache .
python -m unittest discover -s tests -v
python scripts/audit_release_hygiene.py . --clean
```

生成文章后再运行受众边界、移动宽度、中文排版和颜色对比审查：

```powershell
python scripts/audit_wechat_markup.py article.html --contract design-contract.json
python scripts/audit_audience_boundary.py article.html --contract design-contract.json
python scripts/audit_wechat_widths.py article.html --contract design-contract.json
python scripts/audit_wechat_typography.py article.html --contract design-contract.json
python scripts/audit_wechat_contrast.py article.html --contract design-contract.json
python scripts/audit_design_contract.py article.html --contract design-contract.json
```

浏览器预览不能替代微信公众号编辑器与手机预览。仓库不携带固定文章 HTML、研究过程数据、本地文章数据或真实公众号凭据。

## License

MIT License. See [`LICENSE`](LICENSE).
