# 云浪公众号排版（Yunoe）

[![CI](https://img.shields.io/github/actions/workflow/status/juneme/wechat-article-designer/ci.yml?branch=main&style=flat-square&label=CI)](https://github.com/juneme/wechat-article-designer/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/juneme/wechat-article-designer?style=flat-square)](LICENSE)
[![Console](https://img.shields.io/badge/companion-云浪控制台-173f3a?style=flat-square)](https://github.com/juneme/wechat-console-server)

面向微信公众号的轻量 Codex Skill。Yunoe 根据文章内容自主完成写作与视觉设计，在真实验证过的微信边界内组合 HTML、内联 CSS、SVG/SMIL、图片及其他兼容媒介，并默认把成稿写入微信公众号草稿箱。

它不包含排版模板、预设主题、案例库、设计评分或固定工作流。文章的结构、审美、层级与媒介选择由 AI 根据当前内容独立完成。

## 两个核心能力

1. 原创公众号文章设计：兼顾中文可读性、移动适配和微信清洗边界。
2. 连接云浪控制台：上传图片并对本地记录或真实微信草稿执行新增、查询、修改和删除。

文章设计默认执行以下交付约束：

- 写作开始时检查控制台连接状态。
- 缺少配对时打开本地验证码窗口，验证码不进入聊天或命令行。
- 保留与提交正文一致的本地 HTML 对比文件。
- 后端可用时默认写入真实草稿箱，但绝不自动发布或群发。

## 安装

```powershell
git clone https://github.com/juneme/wechat-article-designer.git "$env:USERPROFILE\.codex\skills\yunoe"
```

重新启动 Codex 或创建新任务，使 Skill 完成发现。随后可直接使用：

```text
使用 $yunoe 写一篇公众号文章。
```

## 本地安全配对

先部署配套的 [云浪控制台](https://github.com/juneme/wechat-console-server)，登录控制台生成 60 秒动态验证码，然后在本地运行：

```powershell
python scripts/wechat_console.py pair-ui --server http://SERVER:8791
```

服务端地址与验证码只在本地窗口填写。配对成功后，统一客户端令牌保存于用户目录但不会打印；Codex、Trae 等客户端各自配对不会使其他客户端失效，服务端为每个用户保留最近使用的 16 枚令牌。可信个人环境可使用 HTTP，公网环境应配置 HTTPS。

## 客户端命令

```text
status
pair-ui --server URL
image-upload --mode article|material|both FILE [FILE ...]
temp-upload FILE [FILE ...]
temp-list [--limit 500]
draft-create --json FILE
draft-list / draft-get / draft-update / draft-delete
wechat-list / wechat-get / wechat-update / wechat-delete
```

完整参数见：

```powershell
python scripts/wechat_console.py --help
```

## 设计与安全边界

- [微信发布边界](references/wechat-boundary.md)
- [中文排版边界](references/typography.md)
- [云浪控制台客户端](references/backend.md)

客户端不读取或保存公众号 AppSecret。不要提交本地令牌、验证码、文章工作文件或真实公众号数据。

## 验证

```powershell
$env:PYTHONUTF8='1'
python "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" .
python -m py_compile scripts/wechat_console.py
```

## License

MIT License. See [LICENSE](LICENSE).
