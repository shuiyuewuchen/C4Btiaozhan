#!/usr/bin/env python3
"""
WeChat Publisher Pro — Markdown/Word → 公众号 HTML 增强版

在 starter kit 基础上新增能力：
  1. 多主题支持（default / blue / warm / minimal / forest）
  2. Callout 高亮框（> [!NOTE] / [!TIP] / [!WARNING] / [!QUOTE]）
  3. 自动目录（从 h2/h3 生成内嵌 TOC）
  4. 文章元数据 frontmatter（title / author / date / abstract）
  5. 页脚版权声明（自动追加）
  6. 中文排版优化（中英文/数字之间自动加空格）
  7. 图片响应式（max-width: 100%）

Usage:
    python convert_to_wechat.py input.md output.html [--theme blue] [--toc] [--footer]
    python convert_to_wechat.py report.docx output.html --theme warm --author "张三"
"""

import sys
import os
import re
import argparse
from pathlib import Path

# --- Auto-install dependencies ---
def install_dependencies():
    missing = []
    try:
        import markdown  # noqa
    except ImportError:
        missing.append("markdown")
    try:
        from bs4 import BeautifulSoup  # noqa
    except ImportError:
        missing.append("beautifulsoup4")
    try:
        import lxml  # noqa
    except ImportError:
        missing.append("lxml")

    if missing:
        print(f"Installing missing packages: {', '.join(missing)}...")
        import subprocess
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", *missing,
            "--break-system-packages", "-q"
        ])
        print("Done!\n")

install_dependencies()

import markdown
from bs4 import BeautifulSoup, NavigableString

# ============================================================
# THEME SYSTEM — 多主题配色
# ============================================================

THEMES = {
    "default": {
        "name": "默认灰调",
        "h2_color": "#333333",
        "h3_color": "#333333",
        "body_color": "#3f3f3f",
        "accent": "#333333",
        "blockquote_border": "#cccccc",
        "blockquote_bg": "#f7f7f7",
        "link_color": "#0366d6",
        "code_bg": "#f5f5f5",
        "code_color": "#d73a49",
        "table_header_bg": "#f6f8fa",
        "callout_note_bg": "#e8f4fd",
        "callout_note_border": "#1890ff",
        "callout_tip_bg": "#f6ffed",
        "callout_tip_border": "#52c41a",
        "callout_warn_bg": "#fffbe6",
        "callout_warn_border": "#faad14",
        "callout_quote_bg": "#f9f9f9",
        "callout_quote_border": "#999999",
        "toc_bg": "#fafafa",
        "toc_border": "#e8e8e8",
        "footer_color": "#999999",
        "meta_color": "#888888",
    },
    "blue": {
        "name": "商务蓝",
        "h2_color": "#1a73e8",
        "h3_color": "#1a73e8",
        "body_color": "#333333",
        "accent": "#1a73e8",
        "blockquote_border": "#1a73e8",
        "blockquote_bg": "#f0f7ff",
        "link_color": "#1a73e8",
        "code_bg": "#eef4fc",
        "code_color": "#1a73e8",
        "table_header_bg": "#e8f0fe",
        "callout_note_bg": "#e8f0fe",
        "callout_note_border": "#1a73e8",
        "callout_tip_bg": "#e6f4ea",
        "callout_tip_border": "#137333",
        "callout_warn_bg": "#fef7e0",
        "callout_warn_border": "#e37400",
        "callout_quote_bg": "#f1f3f4",
        "callout_quote_border": "#5f6368",
        "toc_bg": "#f8fafd",
        "toc_border": "#d2e3fc",
        "footer_color": "#80868b",
        "meta_color": "#5f6368",
    },
    "warm": {
        "name": "暖橙风",
        "h2_color": "#d84315",
        "h3_color": "#e65100",
        "body_color": "#4e342e",
        "accent": "#ff6f00",
        "blockquote_border": "#ff9800",
        "blockquote_bg": "#fff8e1",
        "link_color": "#e65100",
        "code_bg": "#fff3e0",
        "code_color": "#d84315",
        "table_header_bg": "#ffe0b2",
        "callout_note_bg": "#fff3e0",
        "callout_note_border": "#ef6c00",
        "callout_tip_bg": "#f1f8e9",
        "callout_tip_border": "#689f38",
        "callout_warn_bg": "#fff8e1",
        "callout_warn_border": "#ff8f00",
        "callout_quote_bg": "#fbe9e7",
        "callout_quote_border": "#bf360c",
        "toc_bg": "#fffde7",
        "toc_border": "#ffe082",
        "footer_color": "#a1887f",
        "meta_color": "#8d6e63",
    },
    "minimal": {
        "name": "极简黑白",
        "h2_color": "#000000",
        "h3_color": "#000000",
        "body_color": "#222222",
        "accent": "#000000",
        "blockquote_border": "#bbbbbb",
        "blockquote_bg": "#fafafa",
        "link_color": "#000000",
        "code_bg": "#f0f0f0",
        "code_color": "#555555",
        "table_header_bg": "#eeeeee",
        "callout_note_bg": "#f5f5f5",
        "callout_note_border": "#333333",
        "callout_tip_bg": "#f5f5f5",
        "callout_tip_border": "#333333",
        "callout_warn_bg": "#f5f5f5",
        "callout_warn_border": "#333333",
        "callout_quote_bg": "#f5f5f5",
        "callout_quote_border": "#333333",
        "toc_bg": "#fafafa",
        "toc_border": "#dddddd",
        "footer_color": "#aaaaaa",
        "meta_color": "#999999",
    },
    "forest": {
        "name": "森系绿",
        "h2_color": "#2e7d32",
        "h3_color": "#388e3c",
        "body_color": "#33691e",
        "accent": "#43a047",
        "blockquote_border": "#66bb6a",
        "blockquote_bg": "#f1f8e9",
        "link_color": "#2e7d32",
        "code_bg": "#e8f5e9",
        "code_color": "#2e7d32",
        "table_header_bg": "#c8e6c9",
        "callout_note_bg": "#e8f5e9",
        "callout_note_border": "#43a047",
        "callout_tip_bg": "#f1f8e9",
        "callout_tip_border": "#7cb342",
        "callout_warn_bg": "#fff8e1",
        "callout_warn_border": "#f9a825",
        "callout_quote_bg": "#e0f2f1",
        "callout_quote_border": "#00897b",
        "toc_bg": "#f9fbe7",
        "toc_border": "#dcedc8",
        "footer_color": "#7cb342",
        "meta_color": "#558b2f",
    },
}

# Tags that WeChat allows
ALLOWED_TAGS = {
    'p', 'h2', 'h3', 'ul', 'ol', 'li', 'span', 'img', 'a',
    'table', 'tr', 'th', 'td', 'br', 'strong', 'em',
}

# Callout type mapping: markdown marker → (emoji, css key)
CALLOUT_TYPES = {
    "NOTE":    ("📘", "note"),
    "TIP":     ("💡", "tip"),
    "WARNING": ("⚠️", "warn"),
    "QUOTE":   ("💬", "quote"),
    "SUCCESS": ("✅", "tip"),
    "DANGER":  ("🚫", "warn"),
}


# ============================================================
# THEME → STYLES 构建器
# ============================================================

def build_styles(theme_key):
    """根据主题构建全套 inline CSS 样式字典。"""
    t = THEMES.get(theme_key, THEMES["default"])
    return {
        "h2": (
            f'font-size: 22px; font-weight: bold; line-height: 1.5; '
            f'color: {t["h2_color"]}; margin: 28px 0 14px 0; '
            f'padding-bottom: 8px; border-bottom: 2px solid {t["accent"]};'
        ),
        "h3": (
            f'font-size: 18px; font-weight: bold; line-height: 1.5; '
            f'color: {t["h3_color"]}; margin: 20px 0 10px 0;'
        ),
        "p": (
            f'font-size: 16px; line-height: 1.8; color: {t["body_color"]}; '
            f'margin: 12px 0; letter-spacing: 0.5px;'
        ),
        "li": (
            f'font-size: 16px; line-height: 1.8; color: {t["body_color"]}; '
            f'margin: 6px 0;'
        ),
        "code_inline": (
            f'background-color: {t["code_bg"]}; color: {t["code_color"]}; '
            f'font-size: 14px; padding: 2px 6px; border-radius: 3px;'
        ),
        "code_block": (
            f'background-color: #f6f8fa; color: #24292e; font-size: 14px; '
            f'line-height: 1.6; padding: 16px; margin: 12px 0; '
            f'border-radius: 6px; font-family: "SF Mono", Monaco, Consolas, monospace;'
        ),
        "blockquote": (
            f'background-color: {t["blockquote_bg"]}; color: #666; '
            f'padding: 12px 16px; margin: 14px 0; '
            f'border-left: 4px solid {t["blockquote_border"]}; border-radius: 0 4px 4px 0;'
        ),
        "table": (
            f'border-collapse: collapse; margin: 14px 0; font-size: 14px; '
            f'width: 100%;'
        ),
        "th": (
            f'background-color: {t["table_header_bg"]}; color: #24292e; '
            f'font-weight: bold; padding: 10px 8px; text-align: left; '
            f'border: 1px solid #ddd;'
        ),
        "td": f'padding: 10px 8px; border: 1px solid #ddd; color: {t["body_color"]};',
        "a": f'color: {t["link_color"]}; text-decoration: underline;',
        "img": 'max-width: 100%; height: auto; border-radius: 6px; margin: 10px 0;',
        "meta_title": (
            f'font-size: 24px; font-weight: bold; line-height: 1.4; '
            f'color: {t["h2_color"]}; margin: 0 0 8px 0;'
        ),
        "meta_info": f'font-size: 14px; color: {t["meta_color"]}; margin: 4px 0;',
        "meta_abstract": (
            f'font-size: 15px; color: #666; margin: 12px 0 20px 0; '
            f'padding: 12px 16px; background-color: {t["blockquote_bg"]}; '
            f'border-radius: 6px; line-height: 1.7;'
        ),
        "toc_container": (
            f'background-color: {t["toc_bg"]}; border: 1px solid {t["toc_border"]}; '
            f'border-radius: 8px; padding: 16px 20px; margin: 20px 0 28px 0;'
        ),
        "toc_title": (
            f'font-size: 15px; font-weight: bold; color: {t["h2_color"]}; '
            f'margin: 0 0 8px 0;'
        ),
        "toc_item": f'font-size: 14px; line-height: 2; color: {t["link_color"]};',
        "footer": (
            f'font-size: 13px; color: {t["footer_color"]}; text-align: center; '
            f'margin: 40px 0 10px 0; line-height: 1.8;'
        ),
        "divider": (
            f'border: none; border-top: 1px solid {t["toc_border"]}; '
            f'margin: 30px 0;'
        ),
        # Callout 配色（从主题字典透传）
        "callout_note_bg": t["callout_note_bg"],
        "callout_note_border": t["callout_note_border"],
        "callout_tip_bg": t["callout_tip_bg"],
        "callout_tip_border": t["callout_tip_border"],
        "callout_warn_bg": t["callout_warn_bg"],
        "callout_warn_border": t["callout_warn_border"],
        "callout_quote_bg": t["callout_quote_bg"],
        "callout_quote_border": t["callout_quote_border"],
    }


# ============================================================
# FRONTMATTER 解析（YAML-like，无需 pyyaml 依赖）
# ============================================================

def parse_frontmatter(text):
    """解析 Markdown 文件顶部的 --- frontmatter --- 块。"""
    meta = {}
    body = text
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n', text, re.DOTALL)
    if m:
        fm = m.group(1)
        body = text[m.end():]
        for line in fm.split('\n'):
            if ':' in line:
                key, _, val = line.partition(':')
                key = key.strip().lower()
                val = val.strip().strip('"').strip("'")
                if key:
                    meta[key] = val
    return meta, body


# ============================================================
# CALLOUT 解析
# 语法：> [!NOTE] / [!TIP] / [!WARNING] / [!QUOTE]
# ============================================================

CALLOUT_PATTERN = re.compile(
    r'^> \[!(NOTE|TIP|WARNING|QUOTE|SUCCESS|DANGER)\]\s*\n((?:>.*(?:\n|$))+)',
    re.MULTILINE
)

def extract_callouts(html):
    """
    在 markdown → html 之后，blockquote 已经变成 <blockquote>。
    我们改为在 markdown 转换前处理 callout，把它替换为特殊 HTML 标记。
    这里作为后处理函数，直接操作原始 markdown 文本。
    """
    return html  # placeholder, actual work done in process_markdown_text


def replace_callouts_in_markdown(md_text):
    """在 markdown 文本中识别 callout 语法，替换为占位 HTML。"""
    def _replace(match):
        ctype = match.group(1)
        content_lines = match.group(2).strip().split('\n')
        # 去掉每行开头的 "> "
        inner = '\n'.join(
            re.sub(r'^>\s?', '', line) for line in content_lines
        )
        # 用一个特殊的 markdown callout 标记，后续转换后替换
        return f'\n\n<div class="callout callout-{ctype.lower()}">\n\n{inner}\n\n</div>\n\n'

    return CALLOUT_PATTERN.sub(_replace, md_text)


# ============================================================
# 中文排版优化
# ============================================================

# 中文字符范围（CJK Unified Ideographs）
CJK_RE = re.compile(r'([\u4e00-\u9fff\u3000-\u303f\uff00-\uffef])')
# 英文字母/数字
LATIN_RE = re.compile(r'([a-zA-Z0-9])')

def optimize_chinese_typography(text):
    """在中文与英文/数字之间自动加空格（但不要修改 HTML 标签内的内容）。"""
    # 简单处理：在纯文本节点中加空格
    # 我们不在 HTML 层面做，避免破坏标签；这里对 markdown 源文本做
    # 中文后紧跟英文 → 加空格
    text = re.sub(r'([\u4e00-\u9fff])([a-zA-Z])', r'\1 \2', text)
    # 英文后紧跟中文 → 加空格
    text = re.sub(r'([a-zA-Z])([\u4e00-\u9fff])', r'\1 \2', text)
    # 中文后紧跟数字
    text = re.sub(r'([\u4e00-\u9fff])([0-9])', r'\1 \2', text)
    # 数字后紧跟中文
    text = re.sub(r'([0-9])([\u4e00-\u9fff])', r'\1 \2', text)
    return text


# ============================================================
# INPUT READERS
# ============================================================

def read_markdown(filepath, theme_key="default", toc=False, footer_text=None,
                  author=None, optimize_typography=True):
    """Convert Markdown file to WeChat-ready HTML string."""
    with open(filepath, 'r', encoding='utf-8') as f:
        raw = f.read()

    # 1. 解析 frontmatter
    meta, body = parse_frontmatter(raw)

    # 2. 中文排版优化
    if optimize_typography:
        body = optimize_chinese_typography(body)

    # 3. 处理 callout（在 markdown → html 之前）
    body = replace_callouts_in_markdown(body)

    # 4. Markdown → HTML
    html = markdown.markdown(body, extensions=[
        'extra', 'fenced_code', 'nl2br', 'sane_lists', 'tables',
    ])

    styles = build_styles(theme_key)
    soup = BeautifulSoup(html, 'lxml')

    # 5. 处理 callout div（我们之前插入的）
    _process_callout_divs(soup, styles)

    # 6. Sanitize
    soup = _sanitize(soup, styles)

    # 7. 应用样式
    soup = _apply_styles(soup, styles)

    # 8. 清理属性
    soup = _clean_attributes(soup)

    # 9. 组装文章头部（元数据）
    parts = []
    title = meta.get("title") or Path(filepath).stem.replace('-', ' ').title()
    author_name = author or meta.get("author", "")
    date_str = meta.get("date", "")
    abstract = meta.get("abstract", "")

    # 标题区域
    parts.append(f'<p style="{styles["meta_title"]}">{title}</p>')
    if author_name or date_str:
        meta_line_parts = []
        if author_name:
            meta_line_parts.append(f'作者：{author_name}')
        if date_str:
            meta_line_parts.append(date_str)
        parts.append(
            f'<p style="{styles["meta_info"]}">{" ｜ ".join(meta_line_parts)}</p>'
        )
    if abstract:
        parts.append(f'<p style="{styles["meta_abstract"]}">{abstract}</p>')

    # 10. 自动目录
    if toc:
        toc_html = _build_toc(soup, styles)
        if toc_html:
            parts.append(toc_html)

    # 11. 正文（提取 body 内的内容，去掉 html/body 外壳）
    body_el = soup.find('body')
    if body_el:
        body_content = '\n'.join(
            str(child) for child in body_el.children if str(child).strip()
        )
    else:
        body_content = '\n'.join(
            str(child) for child in soup.children if str(child).strip()
        )
    parts.append(body_content)

    # 12. 分隔线
    parts.append(f'<hr style="{styles["divider"]}"/>')

    # 13. 页脚
    if footer_text:
        parts.append(f'<p style="{styles["footer"]}">{footer_text}</p>')
    else:
        parts.append(
            f'<p style="{styles["footer"]}">本文由 WeChat Publisher Pro 技能生成<br/>'
            f'AI 辅助写作 · 一键排版发布</p>'
        )

    return '\n'.join(parts)


def read_docx(filepath, theme_key="default", toc=False, footer_text=None,
              author=None, optimize_typography=True):
    """Convert Word .docx to WeChat HTML."""
    from docx import Document
    doc = Document(filepath)
    parts = []

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        style_name = para.style.name if para.style else ''
        if style_name.startswith('Heading'):
            level = style_name.replace('Heading ', '')
            tag = 'h2' if level in ('1', '2') else 'h3'
            parts.append(f'<{tag}>{text}</{tag}>')
        else:
            p_html = '<p>'
            for run in para.runs:
                t = run.text
                if not t:
                    continue
                if run.bold and run.italic:
                    p_html += f'<span style="font-weight:bold;font-style:italic;">{t}</span>'
                elif run.bold:
                    p_html += f'<span style="font-weight:bold;">{t}</span>'
                elif run.italic:
                    p_html += f'<span style="font-style:italic;">{t}</span>'
                else:
                    p_html += t
            p_html += '</p>'
            parts.append(p_html)

    html = '\n'.join(parts)
    styles = build_styles(theme_key)
    soup = BeautifulSoup(html, 'lxml')
    soup = _sanitize(soup, styles)
    soup = _apply_styles(soup, styles)
    soup = _clean_attributes(soup)

    content = '\n'.join(str(child) for child in soup.children if str(child).strip())
    return content


# ============================================================
# HTML 处理函数
# ============================================================

def _process_callout_divs(soup, styles):
    """把 <div class="callout ..."> 转换成公众号兼容的 <p> 结构。"""
    callout_emoji = {
        "note": "📘", "tip": "💡", "warn": "⚠️", "quote": "💬",
    }
    # markdown 类型名 → 内部 key 映射（WARNING→warn, SUCCESS→tip, DANGER→warn）
    type_normalize = {
        "warning": "warn", "success": "tip", "danger": "warn",
    }
    for div in soup.find_all('div', class_=re.compile(r'callout')):
        classes = div.get('class', [])
        ctype = "note"
        for c in classes:
            if c.startswith('callout-'):
                raw = c.replace('callout-', '')
                ctype = type_normalize.get(raw, raw)
                break
        emoji = callout_emoji.get(ctype, "📌")
        bg_key = f"callout_{ctype}_bg" if f"callout_{ctype}_bg" in styles else "callout_note_bg"
        border_key = f"callout_{ctype}_border" if f"callout_{ctype}_border" in styles else "callout_note_border"
        bg = styles.get(bg_key, "#f0f7ff")
        border = styles.get(border_key, "#1890ff")

        inner_html = div.decode_contents()
        callout_html = (
            f'<p style="background-color: {bg}; border-left: 4px solid {border}; '
            f'padding: 14px 18px; margin: 16px 0; border-radius: 0 6px 6px 0; '
            f'font-size: 15px; line-height: 1.8; color: #444;">'
            f'<strong style="color: {border};">{emoji}</strong> '
            f'{inner_html}</p>'
        )
        # 解析 callout HTML，提取 <p> 标签本身（避免嵌套 html/body）
        callout_soup = BeautifulSoup(callout_html, 'lxml')
        callout_p = callout_soup.find('p')
        if callout_p:
            div.replace_with(callout_p.extract())
        else:
            div.replace_with(BeautifulSoup(callout_html, 'html.parser'))


def _sanitize(soup, styles):
    """Sanitize HTML for WeChat compatibility."""
    for tag_name in ('script', 'style', 'iframe'):
        for el in soup.find_all(tag_name):
            el.decompose()

    for h1 in soup.find_all('h1'):
        h1.name = 'h2'

    # div → p（但 callout div 已经处理过，跳过）
    for div in soup.find_all('div'):
        if 'callout' in (div.get('class') or []):
            continue
        div.name = 'p'

    # <pre><code> → 代码块
    for pre in soup.find_all('pre'):
        code = pre.find('code')
        code_text = code.get_text() if code else pre.get_text()
        p = soup.new_tag('p')
        p.string = code_text
        p['style'] = styles['code_block']
        pre.replace_with(p)

    # 内联 code
    for code in soup.find_all('code'):
        span = soup.new_tag('span')
        span.string = code.get_text()
        span['style'] = styles['code_inline']
        code.replace_with(span)

    # blockquote → 样式化 p
    for bq in soup.find_all('blockquote'):
        p = soup.new_tag('p')
        p.string = bq.get_text()
        p['style'] = styles['blockquote']
        bq.replace_with(p)

    # strong/b → span bold
    for tag in soup.find_all(['strong', 'b']):
        # 不替换 callout 里已经有样式的 strong
        if tag.get('style'):
            continue
        span = soup.new_tag('span')
        span.string = tag.get_text()
        span['style'] = 'font-weight: bold;'
        tag.replace_with(span)

    # em/i → span italic
    for tag in soup.find_all(['em', 'i']):
        if tag.get('style'):
            continue
        span = soup.new_tag('span')
        span.string = tag.get_text()
        span['style'] = 'font-style: italic;'
        tag.replace_with(span)

    # 图片响应式
    for img in soup.find_all('img'):
        img['style'] = styles['img']

    return soup


def _apply_styles(soup, styles):
    """Apply inline styles to all elements."""
    style_map = {
        'h2': styles['h2'],
        'h3': styles['h3'],
        'p': styles['p'],
        'li': styles['li'],
        'table': styles['table'],
        'th': styles['th'],
        'td': styles['td'],
        'a': styles['a'],
    }
    for tag_name, style in style_map.items():
        for el in soup.find_all(tag_name):
            existing = el.get('style', '')
            if existing:
                continue
            el['style'] = style
    return soup


def _clean_attributes(soup):
    """Remove class, id, and unwrap non-allowed tags."""
    for tag in soup.find_all(True):
        for attr in ('class', 'id'):
            if attr in tag.attrs:
                del tag.attrs[attr]
        if tag.name not in ALLOWED_TAGS and tag.name not in ('html', 'head', 'body', '[document]'):
            tag.unwrap()
    return soup


def _build_toc(soup, styles):
    """从 h2/h3 标题生成目录 HTML。"""
    headings = soup.find_all(['h2', 'h3'])
    if len(headings) < 3:
        return ""  # 短文不需要目录

    items = []
    for h in headings:
        text = h.get_text().strip()
        if not text:
            continue
        indent = "padding-left: 12px; " if h.name == 'h3' else ""
        prefix = "└ " if h.name == "h3" else "▪ "
        item_style = styles["toc_item"].rstrip(';') + f'; {indent}margin: 2px 0;'
        items.append(
            f'<p style="{item_style}">{prefix}{text}</p>'
        )

    toc_inner = f'<p style="{styles["toc_title"]}">📑 本文目录</p>' + '\n'.join(items)
    return f'<p style="{styles["toc_container"]}">{toc_inner}</p>'


# ============================================================
# MAIN CONVERTER
# ============================================================

def convert(input_path, output_path, theme="default", toc=False, footer=None,
            author=None, no_typography=False):
    """Main conversion pipeline."""
    path = Path(input_path)
    if not path.exists():
        print(f"❌ Error: File '{input_path}' not found.")
        return False

    ext = path.suffix.lower()
    theme = theme if theme in THEMES else "default"

    print(f"📖 Reading {path.name} ({ext})...")
    if ext == '.md':
        content_html = read_markdown(
            input_path, theme_key=theme, toc=toc, footer_text=footer,
            author=author, optimize_typography=not no_typography,
        )
    elif ext == '.docx':
        content_html = read_docx(
            input_path, theme_key=theme, toc=toc, footer_text=footer,
            author=author, optimize_typography=not no_typography,
        )
    elif ext in ('.html', '.htm'):
        with open(input_path, 'r', encoding='utf-8') as f:
            content_html = f.read()
    else:
        print(f"❌ Unsupported format: {ext}")
        return False

    # Wrap in HTML shell for browser preview
    theme_name = THEMES[theme]["name"]
    output_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>WeChat Publisher Pro — {theme_name} 主题预览</title>
</head>
<body style="max-width: 600px; margin: 0 auto; padding: 24px; background: #ffffff; font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;">
{content_html}
</body>
</html>"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_html)

    size_kb = os.path.getsize(output_path) / 1024
    print(f"\n✅ Done! {output_path} ({size_kb:.1f} KB)")
    print(f"   主题: {theme_name}（{theme}）")
    print(f"   目录: {'已生成' if toc else '未启用'}")
    print(f"   页脚: {'自定义' if footer else '默认'}")
    print(f"\n📋 Next steps:")
    print(f"   1. Open {output_path} in a browser to preview")
    print(f"   2. Ctrl+A → Ctrl+C (select all, copy)")
    print(f"   3. Go to mp.weixin.qq.com → create new article")
    print(f"   4. Ctrl+V (paste into editor)")
    print(f"   5. Upload images via WeChat media library")
    print(f"   6. Preview on phone → publish!")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="WeChat Publisher Pro — Markdown/Word → 公众号 HTML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python convert_to_wechat.py article.md output.html
  python convert_to_wechat.py article.md output.html --theme blue --toc
  python convert_to_wechat.py report.docx output.html --theme warm --author "张三" --footer "© 2026 张三 保留所有权利"
        """
    )
    parser.add_argument("input", help="输入文件路径 (.md / .docx / .html)")
    parser.add_argument("output", help="输出 HTML 文件路径")
    parser.add_argument("--theme", default="default",
                        choices=list(THEMES.keys()),
                        help="配色主题 (default/blue/warm/minimal/forest)")
    parser.add_argument("--toc", action="store_true",
                        help="自动生成文章目录")
    parser.add_argument("--footer", default=None,
                        help="自定义页脚版权文字")
    parser.add_argument("--author", default=None,
                        help="文章作者名（覆盖 frontmatter）")
    parser.add_argument("--no-typography", action="store_true",
                        help="关闭中文排版自动加空格")

    args = parser.parse_args()
    success = convert(
        args.input, args.output,
        theme=args.theme, toc=args.toc, footer=args.footer,
        author=args.author, no_typography=args.no_typography,
    )
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
