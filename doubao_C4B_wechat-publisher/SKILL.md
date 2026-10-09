---
name: wechat-publisher-pro
description: >
  将 Markdown 或 Word 文档一键转换为微信公众号可直接粘贴发布的精美 HTML。
  支持 5 套配色主题、callout 高亮框、自动目录、文章元数据、页脚版权、
  中文排版自动优化。适用于任何需要把 .md / .docx 变成公众号排版的场景。
  触发词："公众号排版"、"转公众号格式"、"wechat article"、"公众号文章生成"、
  "md 转公众号"、"docx 转公众号"、"公众号 HTML"、"发布到微信公众号"。
  当用户提供 .md 或 .docx 文件并希望生成公众号格式时，自动调用本技能。
---

# WeChat Publisher Pro — 公众号文章一键排版技能

## 这个技能做什么

把一篇 Markdown 或 Word 文档，变成可以**直接复制粘贴到公众号编辑器**的精美 HTML。

它是 starter kit 的增强版，新增了 6 项能力：

| 新增能力 | 说明 |
|----------|------|
| 🎨 多主题 | 5 套配色（default / blue / warm / minimal / forest） |
| 📘 Callout 高亮框 | `> [!NOTE]` / `[!TIP]` / `[!WARNING]` / `[!QUOTE]` |
| 📑 自动目录 | 文章超过 3 个标题时自动生成内嵌目录 |
| 📝 文章元数据 | frontmatter 自动渲染标题、作者、日期、摘要 |
| 📄 页脚版权 | 自动追加分隔线 + 版权声明 |
| 🔤 中文排版优化 | 中英文/数字之间自动加空格 |

## 快速开始

```bash
# 基础用法
python scripts/convert_to_wechat.py article.md output.html

# 指定主题 + 自动目录
python scripts/convert_to_wechat.py article.md output.html --theme blue --toc

# 完整参数
python scripts/convert_to_wechat.py article.md output.html \
  --theme warm \
  --toc \
  --author "张三" \
  --footer "© 2026 张三 保留所有权利"
```

运行后：浏览器打开 `output.html` → Ctrl+A → Ctrl+C → 粘贴到公众号编辑器。

## 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `input` | 输入文件 (.md / .docx / .html) | 必填 |
| `output` | 输出 HTML 路径 | 必填 |
| `--theme` | 配色主题：default / blue / warm / minimal / forest | default |
| `--toc` | 自动生成文章目录 | 关闭 |
| `--author` | 文章作者（覆盖 frontmatter） | 无 |
| `--footer` | 自定义页脚文字 | 默认生成 |
| `--no-typography` | 关闭中英文自动加空格 | 开启 |

## 文章 frontmatter 写法

在 Markdown 文件顶部用 `---` 包裹元数据：

```markdown
---
title: 我的公众号文章标题
author: 张三
date: 2026-10-09
abstract: 这是一段摘要，会显示在标题下方，引导读者继续阅读。
---

# 正文从这里开始...
```

## Callout 高亮框写法

在 Markdown 中用 GitHub 风格的 callout 语法：

```markdown
> [!NOTE]
> 这是一个普通提示框，蓝色背景。

> [!TIP]
> 这是一个技巧框，绿色背景。

> [!WARNING]
> 这是一个警告框，黄色背景。

> [!QUOTE]
> 这是一个引用框，灰色背景。
```

转换后会自动变成带左边框、背景色的精美高亮块。

## 支持的输入格式

| 格式 | 处理方式 |
|------|----------|
| `.md` | markdown 库转换，支持表格、代码块、callout、frontmatter |
| `.docx` | python-docx 提取标题、段落、粗体斜体 |
| `.html` | 直接 sanitize + 应用样式 |

## 公众号限制合规说明

本技能自动处理以下公众号限制：

- `<h1>` → `<h2>`（公众号保留 h1 给文章标题）
- `<div>` → `<p>`（公众号不支持 div）
- `<script>` / `<style>` / `<iframe>` → 移除
- 所有样式 → inline CSS（无 class、无 id）
- `<pre><code>` → 样式化 `<p>` 代码块
- 图片自动加 `max-width: 100%`

## 依赖安装

```bash
pip install markdown beautifulsoup4 python-docx lxml
```

脚本首次运行时会自动检测并安装缺失依赖。

## 目录结构

```
wechat-publisher-pro/
├── SKILL.md                          ← 本文件
├── scripts/
│   └── convert_to_wechat.py          ← 主转换脚本
├── references/
│   ├── wechat_styles.md              ← 各主题样式参考
│   └── wechat_restrictions.md        ← 公众号 HTML 限制规则
└── examples/
    ├── sample_article.md             ← 示例输入（含 frontmatter + callout）
    └── sample_output.html            ← 示例输出
```

## 发布 SOP

1. 写好 Markdown 文章（可借助 AI 辅助）
2. 运行 `convert_to_wechat.py` 生成 HTML
3. 浏览器打开 HTML 预览效果
4. 满意后全选复制
5. 打开 mp.weixin.qq.com → 新建图文
6. 粘贴到编辑器
7. 上传本地图片到公众号素材库
8. 手机预览 → 调整 → 发布
