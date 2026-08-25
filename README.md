# WeChat Article Designer

[![Release](https://img.shields.io/github/v/release/juneme/wechat-article-designer?style=flat-square&color=07C160)](https://github.com/juneme/wechat-article-designer/releases/latest)
[![CI](https://img.shields.io/github/actions/workflow/status/juneme/wechat-article-designer/ci.yml?branch=main&style=flat-square&label=CI)](https://github.com/juneme/wechat-article-designer/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/juneme/wechat-article-designer?style=flat-square)](LICENSE)
[![Console Server](https://img.shields.io/badge/companion-wechat--console--server-F1C75B?style=flat-square&logo=github&logoColor=171712)](https://github.com/juneme/wechat-console-server)

![WeChat Article Designer](docs/images/article-designer-hero.svg)

面向微信公众号的 Codex Skill。它同时负责文章写作与视觉设计，根据当前内容原创移动端排版，并在完成作品后进行安全、可读性和发布检查。

v4 的核心是“自由创作优先，成品终审”：没有 Creative/Steady 分级，不需要先填写设计契约，也不要求文字角色、模块、密度、间距、几何或色板标记。设计不再为了通过机器矩阵而收敛；机器只阻止危险代码、真实溢出、不可读正文、错误缩进、内部话术泄漏和草稿状态冲突。

## 完整项目

| 本仓库 | [`wechat-console-server`](https://github.com/juneme/wechat-console-server) |
|---|---|
| 写作、原创视觉综合、HTML/SVG 排版、终审、版本工作区 | 托管公众号凭据、上传图片、接口诊断、幂等写入草稿箱 |
| 安装在运行 Codex 的电脑 | 部署在有固定公网出口 IP 的服务器 |
| 不读取 AppSecret，不群发 | 不写文章，不向 AI 暴露 AppSecret |

![从内容创作到草稿交付](docs/images/project-flow.svg)

## 安装

```powershell
git clone https://github.com/juneme/wechat-article-designer.git "$env:USERPROFILE\.agents\skills\wechat-article-designer"
```

重新启动 Codex 或创建新任务，使 Skill 重新发现。自然语言示例：

```text
使用 $wechat-article-designer 写作并设计这篇公众号文章，先预览，不要写入草稿箱。
```

## 创作模型

新文章和实质性改版执行完整流程：

1. 确定读者、事实边界、文章判断、阅读收益与行动目标。
2. 完成裸文，清除对话、提示词和工作流话术。
3. 从主题、图像、物件、节奏、情绪和证据中提炼视觉母题。
4. 自由组合字体、色彩、留白、边框、图片、卡片、SVG/SMIL、渐变和动势。
5. 对完成品执行发布终审，不与预设设计契约比对。
6. 后端健康则直接写入新草稿，否则生成本地预览。

大标题和章节标题在语义与构图允许时尽量保持移动端单行，但不以删改成普通标题或强制 `nowrap` 为代价。普通连续正文默认使用 `text-indent:2em`，并只在这些段落上添加 `data-indent-role="body-paragraph"`；标题、导语、列表、引用、问答、题注、卡片、行动区、结语和所有容器不缩进。

SVG 是正常设计能力，不是特殊模式。只要初始状态可读、关键信息有相邻正文承接并能在真实编辑器检查，就可以使用一个或多个场景、渐变、蒙版、裁剪、滤镜、文字路径、形变和环境动效。兼容性不确定会产生警告，不会自动把版式降为规矩模板。

## Console Server

从 Console Server 的“API 接入 → Skill 客户端配置”取得：

```text
WECHAT_CONSOLE_URL
WECHAT_IMAGE_API_KEY
WECHAT_PUBLISH_API_KEY
```

密钥只配置在运行 Codex 的用户环境，不得写入 Skill、文章文件、Issue 或公开仓库。只读检查：

```powershell
python scripts/wechat_console_api.py status
```

三个变量存在且健康检查成功时，普通制作请求在终审通过后自动创建一次新草稿，无需二次确认。草稿不等于正式发布或群发，最终由用户审阅。

## 文章工作区

后端可用时创建无预览工作区；后端不可用或用户要求预览时使用默认命令：

```powershell
python scripts/article_workspace.py create --title "文章标题" --date YYYY-MM-DD --no-preview
python scripts/article_workspace.py create --title "文章标题" --date YYYY-MM-DD
```

主要文件：

- `fragment.html`：唯一可编辑的发布片段，带复制边界注释。
- `article.json`：标题、作者、摘要、正文与草稿参数。
- `release-manifest.json`：只记录媒体与交付状态，不记录设计规则。
- `assets/`：正文图片和 2.35:1 封面。
- `revisions/`：正文、元数据、媒体、资产、预览和兼容资料的事务快照。

完成设计后直接发布：

```powershell
python scripts/release_article.py deliver ".\articles\日期_标题"
```

`release_article.py` 会先审查本地成品，再上传图片并复查托管后的正文。后端健康时不生成或遗留 `preview.html`；变量缺失、健康检查失败、图片上传失败或明确的草稿前错误会立即转本地预览。

缺少必需图片时返回 `image-generation-required` 和 `attempt_id`。智能体应先自动生成图片；只有真实生成失败后，才能用同一个 ID 和失败原因转预览。草稿请求一旦进入超时、`502`、pending 或 unknown 状态就锁定工作区，不自动重试，也不转预览。用户检查草稿箱后执行：

```powershell
python scripts/article_workspace.py resolve-draft WORKSPACE --outcome created
python scripts/article_workspace.py resolve-draft WORKSPACE --outcome not-created
```

升级 v2/v3 工作区：

```powershell
python scripts/article_workspace.py migrate WORKSPACE
```

迁移会从旧契约提取媒体信息到 `release-manifest.json`，旧 `design-contract.*` 原样保留为内部历史，不再阻止创作或交付。`plan` 只作为非阻断的 `inspect` 兼容别名；可选设计报告发生在成品之后。

## 发布硬边界

- 不允许脚本、事件处理器、外部 CSS/字体、危险链接和活动嵌入。
- CSS 固定宽度不得超过 320px，百分比不得超过 100%。SVG `viewBox` 坐标不作为 CSS 像素。
- 连续正文显式字号不得小于 14px，显式行高不得小于 1.5。
- 仅正文段落可缩进，且标记段落必须为 `2em`；禁止空格模拟缩进。
- 可计算的文字对比度不得低于 3:1；图片、渐变和滤镜背景由人工检查。
- 发布正文和元数据不得包含智能体工作话术、对话历史、本地路径、缓存或实验内容。
- 直接草稿必须使用微信托管正文图片和有效的 2.35:1 封面。

未知或表现性 CSS、SVG 动画、多色板、非常规间距、紧凑标签等只产生兼容性提示，不属于风格错误。

## 验证与发布

```powershell
$env:PYTHONUTF8='1'
python "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" .
python scripts/quick_validate.py .
python -B -c "import ast,pathlib; [ast.parse(p.read_text(encoding='utf-8')) for p in pathlib.Path('scripts').glob('*.py')]"
python -m ruff check --no-cache .
python scripts/audit_release_hygiene.py . --clean
```

发布 ZIP 必须直接来自 Git `HEAD`，确保 `main` 与 ZIP 除 `.git` 外逐文件一致：

```powershell
git -c core.autocrlf=false archive --format=zip --prefix=wechat-article-designer/ --output=wechat-article-designer.zip HEAD
```

独立审查命令不需要设计契约：

```powershell
python scripts/audit_wechat_markup.py fragment.html
python scripts/audit_audience_boundary.py article.json
python scripts/audit_wechat_widths.py fragment.html
python scripts/audit_wechat_typography.py fragment.html
python scripts/audit_wechat_contrast.py fragment.html
```

浏览器预览不能替代微信公众号编辑器与手机预览。仓库不包含固定文章模板、研究过程数据、本地文章数据、`work/` 实验或真实公众号凭据。

## License

MIT License. See [`LICENSE`](LICENSE).
