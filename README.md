# C4B 挑战交付：WeChat Publisher Pro

> 公众号文章生成技能 —— 把 Markdown / Word 文档一键转换为微信可直接粘贴发布的精美 HTML。

- **作者：** Doubao
- **挑战：** C4B 公众号文章生成技能（WeChat Article Pipeline Skill）
- **发布日期：** 2026-10-09
- **已发布文章：** https://mp.weixin.qq.com/s/KS4auWplEjFH3GUJG7kTxw

---

## 一、这是什么

本项目基于 C4B starter kit，用 AI 辅助开发了一个公众号文章生成技能 **WeChat Publisher Pro**。

在 starter kit 原有的「读取 Markdown/Word → 清洗标签 → 应用 inline CSS → 输出公众号兼容 HTML」四阶段流水线之上，新增了 **6 项能力**：

| 新增能力 | 说明 |
|----------|------|
| 🎨 多主题 | 5 套配色（default / blue / warm / minimal / forest） |
| 📘 Callout 高亮框 | `> [!NOTE]` / `[!TIP]` / `[!WARNING]` / `[!QUOTE]` 四种类型 |
| 📑 自动目录 | 文章超过 3 个标题时自动生成内嵌目录卡片 |
| 📝 文章元数据 | frontmatter 自动渲染标题、作者、日期、摘要 |
| 📄 页脚版权 | 自动追加分隔线 + 版权声明 |
| 🔤 中文排版优化 | 中英文/数字之间自动加空格，行高与字距优化 |

---

## 二、快速开始

### 1. 安装依赖

```bash
pip install markdown beautifulsoup4 python-docx lxml
```

### 2. 转换文章

```bash
python doubao_C4B_wechat-publisher/scripts/convert_to_wechat.py \
  你的文章.md output.html \
  --theme blue --toc --author "你的名字"
```

### 3. 发布到公众号

浏览器打开 `output.html` → `Cmd+A` 全选 → `Cmd+C` 复制 → 登录 mp.weixin.qq.com 新建图文 → `Cmd+V` 粘贴 → 预览 → 发布。

> 完整参数说明见 [`doubao_C4B_教学说明.md`](doubao_C4B_教学说明.md)。

---

## 三、交付物清单

| 文件 | 说明 |
|------|------|
| [`README.md`](README.md) | 本文件，项目总览 |
| [`doubao_C4B_wechat-publisher/`](doubao_C4B_wechat-publisher/) | 技能包（SKILL.md + scripts + references + examples） |
| [`doubao_C4B_output.html`](doubao_C4B_output.html) | 公众号文章成品 HTML（可直接粘贴发布） |
| [`doubao_C4B_文章源文件.md`](doubao_C4B_文章源文件.md) | 文章 Markdown 源文件 |
| [`doubao_C4B_文章链接.md`](doubao_C4B_文章链接.md) | 发布说明、文章链接与传播数据 |
| [`doubao_C4B_AI日志.md`](doubao_C4B_AI日志.md) | AI 使用日志（8 轮迭代全过程） |
| [`doubao_C4B_拿来说明.md`](doubao_C4B_拿来说明.md) | 从 starter kit 拿了什么、改了什么、为什么改 |
| [`doubao_C4B_教学说明.md`](doubao_C4B_教学说明.md) | 安装、使用、写作规范与发布 SOP |
| [`doubao_C4B_AAR复盘.md`](doubao_C4B_AAR复盘.md) | AAR 复盘（失败经验、根因分析、改进方案） |

---

## 四、开发概要

- **迭代轮次：** 8 轮
- **修复真实 bug：** 4 个
  1. 嵌套 `<html><body>` 标签（BeautifulSoup 解析器包裹行为）
  2. TOC 样式双分号 `;;`（字符串拼接 CSS）
  3. WARNING callout 类型映射错误（`warning` vs `warn` 命名不一致）
  4. callout 颜色未透传（`build_styles()` 漏掉 8 个 callout 颜色 key）
- **合规检查：** 无 class/id、无 script/iframe、全 inline CSS、无 h1/div、无嵌套 html/body
- **发布数据（截至 2026-10-09）：** 阅读 10 / 点赞 5 / 在看 4 / 转发 9
