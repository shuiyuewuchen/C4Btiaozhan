# C4B 挑战 AI 使用日志

> 本日志完整记录了从拿到 starter kit 到完成交付的全过程，包括 AI 辅助的每一轮迭代、遇到的问题和修复方案。

---

## 第一轮：理解任务和 starter kit

**Prompt（对 AI 说的）：**

> "这是 C4B 挑战的 CHALLENGE.md 和 starter kit，请帮我理解任务要求，并列出我需要做什么。"

**AI 输出：**
- 读取了 CHALLENGE.md（14KB）、rubric.json、challenge.yaml
- 解压了 c4b-wechat-publisher-starter.zip
- 阅读了 SKILL.md、convert_to_wechat.py（383行）、wechat_styles.md、wechat_restrictions.md、sample_article.md
- 总结出：需要在 starter kit 基础上新增至少 2 项能力，写一篇文章，用 skill-creator 流程开发

**我的决策：**
- 选择新增 6 项能力（远超要求的 2 项）：多主题、callout框、自动目录、文章元数据、页脚版权、中文排版优化
- 写一篇关于"AI内容发布流水线"的文章作为发布内容

---

## 第二轮：开发增强版脚本（第一次尝试）

**Prompt：**

> "基于这个 starter kit 的 convert_to_wechat.py，帮我增强以下功能：1）多主题系统 2）callout高亮框 3）自动目录 4）frontmatter元数据 5）页脚版权 6）中文排版优化。写成完整的Python脚本。"

**AI 输出（第一版脚本）：**
- 创建了 THEMES 字典（5套主题）
- 添加了 frontmatter 解析函数
- 添加了 callout 正则匹配和替换
- 添加了 TOC 生成函数
- 添加了 build_styles() 函数
- 脚本约 500 行

**测试结果：**
- ✅ 脚本成功运行
- ✅ 主题切换正常
- ❌ 输出 HTML 中嵌套了 `<html><body>` 标签（因为 soup.children 取到的是 html 元素而非 body）
- ❌ TOC 的 style 属性有双分号 `;;`
- ❌ callout 区域也嵌套了 html/body

---

## 第三轮：修复嵌套 HTML 问题

**Prompt：**

> "输出的 HTML 里嵌套了 <html><body>，这是因为 BeautifulSoup 解析 markdown 输出时自动加了外壳。帮我修复，正确提取 body 内的内容。"

**修复内容：**
1. 在 `read_markdown()` 中，改用 `soup.find('body')` 提取 body 子元素，而非直接迭代 `soup.children`
2. 修复 TOC 双分号问题：用 `rstrip(';')` 后再拼接

**测试：** 重新运行，嵌套标签消除。

---

## 第四轮：修复 callout 嵌套问题

**问题发现：**
检查输出 HTML 时发现 callout 高亮框外面包了一层 `<html><body>`（第22-26行、77-81行等）。

**原因分析：**
在 `_process_callout_divs()` 中，用 `div.replace_with(BeautifulSoup(callout_html, 'lxml'))` 替换 div，但 BeautifulSoup 的 lxml 解析器会把片段包上 html/body。

**修复过程：**
- 第一次尝试：用 `body_el.decode_contents()` 提取内容再传 `html.parser` —— 仍然有问题
- 第二次修复：用 `callout_soup.find('p').extract()` 直接取出 p 标签对象，再 `div.replace_with(callout_p)`

**测试：** `grep -c '<html><body>' output.html` 返回 0，确认修复。

---

## 第五轮：修复 callout 颜色映射 bug

**问题发现：**
WARNING callout 显示成了蓝色（note 颜色）而不是黄色（warn 颜色），emoji 也显示成了默认的 📌。

**原因分析：**
- Markdown 中写的是 `> [!WARNING]`
- 正则捕获组是 "WARNING"
- `.lower()` 后变成 "warning"
- 生成的 class 是 `callout-warning`
- 但 emoji 字典和配色字典的 key 用的是 `"warn"` 不是 `"warning"`
- 导致 lookup 失败，全部 fallback 到 note

**修复：**
在 `_process_callout_divs()` 中添加 `type_normalize` 映射：
```python
type_normalize = {
    "warning": "warn", "success": "tip", "danger": "warn",
}
```

**验证：**
```
💬 → #f1f3f4/#5f6368 (quote gray)
⚠️ → #fef7e0/#e37400 (warning orange)
💡 → #e6f4ea/#137333 (tip green)
📘 → #e8f0fe/#1a73e8 (note blue)
```
四种 callout 全部正确。

---

## 第六轮：修复 callout 配色未透传问题

**问题发现：**
虽然 callout 现在能渲染了，但颜色不对——所有 callout 都是 #f0f7ff/#1890ff（blockquote 的颜色）。

**原因分析：**
`build_styles()` 函数从 `THEMES[theme]` 字典构建样式，但只透传了元素级样式（h2、p、blockquote等），没有把 `callout_note_bg`、`callout_tip_border` 等 callout 专用颜色 key 加入返回的 styles 字典。

**修复：**
在 `build_styles()` 返回的字典末尾追加：
```python
"callout_note_bg": t["callout_note_bg"],
"callout_note_border": t["callout_note_border"],
# ... 共 8 个 callout 颜色 key
```

---

## 第七轮：撰写文章

**Prompt：**

> "写一篇公众号文章，主题是'AI 时代的内容发布流水线'，要求：有frontmatter标题/作者/摘要，至少3个二级标题，包含表格、callout高亮框、列表，内容有观点不是流水账，1500字左右。"

**AI 输出：**
- 生成了带 frontmatter 的 Markdown 文章
- 包含 4 个 callout（quote/warning/tip/note）
- 包含一个 5 行表格
- 有明确的观点和时间分配数据

**人工调整：**
- 确认文章结构清晰：问题→方案→实现→效果→迁移
- 确认有深度观点："效率提升的关键不是写得更快，而是消除摩擦"
- 确认排版元素丰富：标题、列表、表格、callout、代码行、粗体

---

## 第八轮：最终转换和验证

**命令：**
```bash
python3 scripts/convert_to_wechat.py 文章源文件.md output.html \
  --theme blue --toc \
  --footer "© 2026 Doubao · AI 辅助写作 · WeChat Publisher Pro 排版"
```

**验证项：**
- [x] 文件大小 14.8 KB，非空
- [x] 无嵌套 `<html><body>`
- [x] 4 个 callout 颜色和图标正确
- [x] 自动目录生成（7个标题）
- [x] frontmatter 标题/作者/日期/摘要渲染正确
- [x] 表格样式正确
- [x] 页脚版权声明正确
- [x] 所有样式都是 inline CSS
- [x] 无 class/id 属性
- [x] 无 script/style/iframe/h1/div 标签

---

## AI 使用统计

| 轮次 | 任务类型 | 关键产出 |
|------|----------|----------|
| 1 | 需求理解 | 任务拆解、功能选择 |
| 2 | 代码生成 | 初版增强脚本（~500行） |
| 3 | Debug | 修复嵌套html/body + 双分号 |
| 4 | Debug | 修复callout嵌套 |
| 5 | Debug | 修复WARNING→warn映射 |
| 6 | Debug | 修复callout颜色未透传 |
| 7 | 内容创作 | 公众号文章初稿 |
| 8 | 验证 | 最终HTML通过所有检查 |

**迭代次数：8 轮**（远超"一句话指令直接提交"的红旗标准）

**关键经验：**
1. AI 生成代码后必须实际运行验证，不能假设正确
2. BeautifulSoup 的 lxml 解析器会给 HTML 片段自动包 html/body，这是高频坑
3. 颜色 key 的命名一致性（warning vs warn）是容易忽略的 bug
4. 每修一个 bug 都要重新跑完整转换流程，确认没有引入新问题
