# WeChat Publisher Pro — 教学说明

> 这是一个把 Markdown / Word 文档一键转换为微信公众号精美 HTML 的技能。

## 一、安装

### 1. 环境要求

- Python 3.8+
- 操作系统：macOS / Windows / Linux 均可

### 2. 安装依赖

```bash
pip install markdown beautifulsoup4 python-docx lxml
```

> 脚本首次运行时会自动检测并安装缺失依赖，你也可以手动装。

### 3. 获取技能

把整个 `doubao_C4B_wechat-publisher/` 文件夹放到你喜欢的位置即可，无需额外安装。

## 二、快速使用

### 最简用法

```bash
python scripts/convert_to_wechat.py 你的文章.md output.html
```

运行后会在当前目录生成 `output.html`。

### 指定主题

```bash
python scripts/convert_to_wechat.py 你的文章.md output.html --theme blue
```

五套主题任选：

| 主题值 | 风格 | 适合 |
|--------|------|------|
| `default` | 中性灰 | 通用 |
| `blue` | 商务蓝 | 技术/商业 |
| `warm` | 暖橙风 | 生活/随笔 |
| `minimal` | 极简黑白 | 设计/文艺 |
| `forest` | 森系绿 | 自然/读书 |

### 开启自动目录

```bash
python scripts/convert_to_wechat.py 你的文章.md output.html --toc
```

文章超过 3 个标题时，自动在开头生成目录卡片。

### 指定作者和页脚

```bash
python scripts/convert_to_wechat.py 你的文章.md output.html \
  --author "张三" \
  --footer "© 2026 张三 保留所有权利"
```

### 完整参数一览

```
python convert_to_wechat.py <input> <output> [选项]

必填：
  input              输入文件 (.md / .docx / .html)
  output             输出 HTML 路径

可选：
  --theme NAME       配色主题 (default/blue/warm/minimal/forest)
  --toc              自动生成文章目录
  --author NAME      文章作者名
  --footer TEXT      自定义页脚版权文字
  --no-typography    关闭中英文自动加空格
```

## 三、写作规范

### 文章头部（frontmatter）

在 Markdown 文件最开头用 `---` 包裹元数据：

```markdown
---
title: "文章标题"
author: "作者名"
date: 2026-10-09
abstract: "一句话摘要，会显示在标题下方。"
---

正文从这里开始...
```

### Callout 高亮框

用 GitHub 风格语法写高亮提示框：

```markdown
> [!NOTE]
> 普通提示（蓝色框）

> [!TIP]
> 技巧分享（绿色框）

> [!WARNING]
> 注意警告（黄色框）

> [!QUOTE]
> 金句引用（灰色框）
```

### 支持的 Markdown 语法

- 标题（`#` → h2，`##` → h3）
- 粗体、斜体
- 有序/无序列表
- 表格
- 代码块（```` ``` ````）
- 行内代码（`` `code` ``）
- 引用（`>`）
- 链接

## 四、发布流程（SOP）

```
写 Markdown → 运行转换命令 → 浏览器预览 → 复制粘贴 → 公众号后台发布
```

详细步骤：

1. **写文章**：用任意编辑器写 Markdown
2. **转换**：运行 `python scripts/convert_to_wechat.py article.md output.html --theme blue --toc`
3. **预览**：用浏览器打开 `output.html`，检查排版效果
4. **复制**：在浏览器里按 `Cmd+A`（全选）→ `Cmd+C`（复制）
5. **粘贴**：打开 [mp.weixin.qq.com](https://mp.weixin.qq.com) → 新建图文 → `Cmd+V` 粘贴
6. **传图**：如果有本地图片，在公众号编辑器里手动上传
7. **预览**：手机扫码预览
8. **发布**：满意后点击发布

## 五、常见问题

**Q: 粘贴后格式丢了怎么办？**
A: 确保你是从 `output.html` 的浏览器预览页面复制的，不是从代码里复制。本技能输出的是纯 inline CSS，不会被公众号过滤。

**Q: 图片怎么办？**
A: 公众号不支持外部图片链接。转换后需要在公众号编辑器里重新上传图片，或者把图片转成 base64 嵌入 HTML。

**Q: 支持 Word 文档吗？**
A: 支持 `.docx`，会提取标题、段落和粗体斜体格式。

**Q: 怎么自定义颜色？**
A: 编辑 `scripts/convert_to_wechat.py` 里的 `THEMES` 字典，改对应颜色值即可。
