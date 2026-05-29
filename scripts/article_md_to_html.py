#!/usr/bin/env python3
"""
Markdown記事 → e-webseisaku.comクラス付きHTML変換スクリプト

使い方:
  python3 article_md_to_html.py input.md [output.html]

Frontmatter (---で囲む):
  title, slug, meta_description, post_type, post_author

Markdownの変換ルール:
  # H1            → <title> + <h1>
  冒頭段落        → <p class="article-lead">
  ## H2           → <section class="article-section" id="section-N">
  ### H3          → <h3>
  - リスト        → <ul class="article-list">
  1. リスト       → <ol class="article-list-ordered">
  > 引用          → <blockquote class="article-quote">
  > [!NOTE]等     → <div class="article-callout">
  | テーブル      → <div class="article-table"><table>
  ```lang...```   → <pre><code class="language-lang">
  [text](url)     → <a href="url">
  **text**        → <strong>
  *text*          → <em>
  `code`          → <code>

特殊記法 (MDで表現しにくい要素):
  :::faq          → <div class="article-faq">
  Q. ...          →   <div class="article-faq__item"><p class="article-faq__q">
  A. ...          →   <p class="article-faq__a">
  [[link-card]]url|テキスト → <a class="article-link-card" href="url">テキスト</a>
"""

import re
import sys
import os
import argparse
from pathlib import Path


def escape_html(text):
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def inline_convert(text):
    """インライン要素の変換（HTMLエスケープ不要な文脈で使う）"""
    # リンクカード [[link-card]]url|テキスト
    text = re.sub(
        r'\[\[link-card\]\]([^\|]+)\|(.+)',
        r'<a class="article-link-card" href="\1">\2</a>',
        text
    )
    # 通常リンク [text](url)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    # 太字 **text**
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    # 斜体 *text*（太字と区別するため**処理後に）
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    # インラインコード `code`（中身をHTMLエスケープして<>の暴走を防ぐ）
    text = re.sub(r'`([^`]+)`', lambda m: f'<code>{escape_html(m.group(1))}</code>', text)
    return text


def parse_frontmatter(lines):
    """---で囲まれたFrontmatterを解析して残りの行を返す"""
    meta = {}
    if not lines or lines[0].strip() != '---':
        return meta, lines

    i = 1
    while i < len(lines) and lines[i].strip() != '---':
        line = lines[i]
        m = re.match(r'^(\w+):\s*(.*)$', line)
        if m:
            key, val = m.group(1), m.group(2).strip().strip('"')
            meta[key] = val
        i += 1

    return meta, lines[i + 1:]


def parse_table(table_lines):
    rows = []
    for line in table_lines:
        if re.match(r'^\|[-| :]+\|$', line.strip()):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        rows.append(cells)

    if not rows:
        return ''

    html = '<div class="article-table">\n<table>\n'
    html += '<thead><tr>'
    for cell in rows[0]:
        html += f'<th>{inline_convert(cell)}</th>'
    html += '</tr></thead>\n'
    if len(rows) > 1:
        html += '<tbody>\n'
        for row in rows[1:]:
            html += '<tr>'
            for cell in row:
                html += f'<td>{inline_convert(cell)}</td>'
            html += '</tr>\n'
        html += '</tbody>\n'
    html += '</table>\n</div>'
    return html


def parse_list(list_lines, ordered=False):
    tag = 'ol' if ordered else 'ul'
    cls = 'article-list-ordered' if ordered else 'article-list'
    html = f'<{tag} class="{cls}">\n'
    for line in list_lines:
        content = re.sub(r'^(\d+\.|[-*+])\s+', '', line.strip())
        html += f'  <li>{inline_convert(content)}</li>\n'
    html += f'</{tag}>'
    return html


def parse_faq_block(faq_lines):
    """:::faq〜:::ブロック内のQ/Aを article-faq 構造に変換"""
    html = '<div class="article-faq">\n'
    current_q = None
    current_a = None

    def flush(q, a):
        if q is None:
            return ''
        out = '  <div class="article-faq__item">\n'
        out += f'    <p class="article-faq__q">{inline_convert(q)}</p>\n'
        out += f'    <p class="article-faq__a">{inline_convert(a or "")}</p>\n'
        out += '  </div>\n'
        return out

    for line in faq_lines:
        line = line.strip()
        if line.startswith('Q.') or line.startswith('Q．'):
            html += flush(current_q, current_a)
            current_q = line
            current_a = None
        elif line.startswith('A.') or line.startswith('A．'):
            current_a = line
        elif line and current_a is not None:
            current_a += ' ' + line

    html += flush(current_q, current_a)
    html += '</div>'
    return html


def render_body(body_lines):
    """セクション本文行列をHTMLに変換"""
    html = ''
    j = 0
    while j < len(body_lines):
        line = body_lines[j]

        # 空行
        if line.strip() == '':
            j += 1
            continue

        # 区切り線
        if line.strip() == '---':
            j += 1
            continue

        # コードブロック ```lang
        if line.strip().startswith('```'):
            lang_match = re.match(r'^```(\w*)', line.strip())
            lang = lang_match.group(1) if lang_match else ''
            code_lines = []
            j += 1
            while j < len(body_lines) and not body_lines[j].strip().startswith('```'):
                code_lines.append(body_lines[j])
                j += 1
            j += 1  # 終端```
            code_content = escape_html('\n'.join(code_lines))
            lang_class = f' class="language-{lang}"' if lang else ''
            html += f'<pre><code{lang_class}>{code_content}</code></pre>\n'
            continue

        # FAQブロック :::faq
        if line.strip() == ':::faq':
            faq_lines = []
            j += 1
            while j < len(body_lines) and body_lines[j].strip() != ':::':
                faq_lines.append(body_lines[j])
                j += 1
            j += 1  # :::
            html += parse_faq_block(faq_lines) + '\n'
            continue

        # JSON-LDブロック :::schema
        if line.strip() == ':::schema':
            schema_lines = []
            j += 1
            while j < len(body_lines) and body_lines[j].strip() != ':::':
                schema_lines.append(body_lines[j])
                j += 1
            j += 1
            html += '<script type="application/ld+json">\n'
            html += '\n'.join(schema_lines) + '\n'
            html += '</script>\n'
            continue

        # H3
        if line.startswith('### '):
            h3_text = re.sub(r'\s*\{#[^}]+\}', '', line[4:].strip())
            html += f'<h3>{inline_convert(h3_text)}</h3>\n'
            j += 1
            continue

        # H4
        if line.startswith('#### '):
            h4_text = re.sub(r'\s*\{#[^}]+\}', '', line[5:].strip())
            html += f'<h4>{inline_convert(h4_text)}</h4>\n'
            j += 1
            continue

        # テーブル
        if line.startswith('|') and j + 1 < len(body_lines) and re.match(r'^\|[-| :]+\|$', body_lines[j + 1].strip()):
            table_lines = []
            while j < len(body_lines) and body_lines[j].strip().startswith('|'):
                table_lines.append(body_lines[j].strip())
                j += 1
            html += parse_table(table_lines) + '\n'
            continue

        # 引用・callout
        if line.startswith('> '):
            quote_lines = []
            while j < len(body_lines) and body_lines[j].startswith('> '):
                quote_lines.append(body_lines[j][2:])
                j += 1
            content = ' '.join(l.strip() for l in quote_lines if l.strip())
            callout_match = re.match(r'\[!(NOTE|TIP|WARNING|INFO|POINT)\]\s*(.*)', content, re.DOTALL)
            if callout_match:
                inner = callout_match.group(2)
                html += f'<div class="article-callout"><p>{inline_convert(inner)}</p></div>\n'
            else:
                html += f'<blockquote class="article-quote"><p>{inline_convert(content)}</p></blockquote>\n'
            continue

        # 番号付きリスト
        if re.match(r'^\d+\.\s', line):
            list_lines = []
            while j < len(body_lines) and re.match(r'^\d+\.\s', body_lines[j]):
                list_lines.append(body_lines[j])
                j += 1
            html += parse_list(list_lines, ordered=True) + '\n'
            continue

        # 箇条書きリスト
        if re.match(r'^[-*+]\s', line):
            list_lines = []
            while j < len(body_lines) and re.match(r'^[-*+]\s', body_lines[j]):
                list_lines.append(body_lines[j])
                j += 1
            html += parse_list(list_lines) + '\n'
            continue

        # リンクカード単独行 [[link-card]]
        if line.strip().startswith('[[link-card]]'):
            m = re.match(r'\[\[link-card\]\]([^\|]+)\|(.+)', line.strip())
            if m:
                html += f'<a class="article-link-card" href="{m.group(1).strip()}">{inline_convert(m.group(2).strip())}</a>\n'
            j += 1
            continue

        # 通常段落（連続行をまとめる）
        para_lines = []
        while j < len(body_lines):
            l = body_lines[j]
            if l.strip() == '':
                break
            if l.startswith(('## ', '### ', '#### ', '> ', '---', ':::')):
                break
            if re.match(r'^[-*+]\s', l) or re.match(r'^\d+\.\s', l):
                break
            if l.strip().startswith('|') and j + 1 < len(body_lines) and re.match(r'^\|[-| :]+\|$', body_lines[j + 1].strip()):
                break
            if l.strip().startswith('```'):
                break
            if l.strip().startswith('[[link-card]]'):
                break
            para_lines.append(l.strip())
            j += 1

        if para_lines:
            para_text = ' '.join(para_lines)
            html += f'<p>{inline_convert(para_text)}</p>\n'

    return html


def convert(md_path):
    text = Path(md_path).read_text(encoding='utf-8')
    lines = text.splitlines()

    # Frontmatter解析
    meta, lines = parse_frontmatter(lines)

    title = meta.get('title', '')
    meta_description = meta.get('meta_description', '')

    i = 0

    # H1タイトル取得（Frontmatterにtitleがない場合）
    if not title:
        while i < len(lines):
            if lines[i].startswith('# '):
                title = lines[i][2:].strip()
                i += 1
                break
            i += 1
    else:
        # Frontmatterにtitleがある場合もH1行をスキップ
        while i < len(lines):
            if lines[i].startswith('# '):
                i += 1
                break
            i += 1

    # リード文（最初のH2より前）
    lead_lines = []
    while i < len(lines):
        if lines[i].startswith('## '):
            break
        if lines[i].strip() != '---':
            lead_lines.append(lines[i])
        i += 1

    lead_paragraphs = '\n'.join(lead_lines).strip()
    lead_html = ''
    if lead_paragraphs:
        paras = [p.strip() for p in re.split(r'\n{2,}', lead_paragraphs) if p.strip()]
        if len(paras) == 1:
            lead_html = f'<p class="article-lead">{inline_convert(paras[0])}</p>'
        else:
            lead_html = '\n'.join(
                f'<p class="article-lead">{inline_convert(p)}</p>' for p in paras
            )

    # metaディスクリプション自動生成
    if not meta_description and lead_paragraphs:
        first = re.split(r'\n{2,}', lead_paragraphs)[0].strip()
        meta_description = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', first)
        meta_description = re.sub(r'\*+', '', meta_description)[:120]

    # セクション解析
    sections = []
    toc_items = []
    section_count = 0
    current_h2 = None
    current_lines = []

    def flush_section(h2_text, body_lines):
        nonlocal section_count
        if h2_text is None:
            return
        section_count += 1
        # FAQセクションはid="section-faq"
        if re.search(r'(よくある質問|FAQ)', h2_text):
            sid = 'section-faq'
        else:
            sid = f'section-{section_count}'
        toc_items.append((sid, h2_text))
        html = f'<section class="article-section" id="{sid}">\n'
        html += f'  <h2>{inline_convert(h2_text)}</h2>\n'
        html += render_body(body_lines)
        html += '</section>'
        sections.append(html)

    while i < len(lines):
        line = lines[i]
        if line.startswith('## '):
            flush_section(current_h2, current_lines)
            h2_text = line[3:].strip()
            # {#anchor} 記法を除去
            h2_text = re.sub(r'\s*\{#[^}]+\}', '', h2_text).strip()
            # 「目次」セクションはスキップ（article-tocで自動生成するため）
            if h2_text in ('目次', 'Table of Contents', 'TOC'):
                current_h2 = None
                current_lines = []
                i += 1
                # 次の ## まで読み飛ばす
                while i < len(lines) and not lines[i].startswith('## '):
                    i += 1
                continue
            current_h2 = h2_text
            current_lines = []
        else:
            current_lines.append(line)
        i += 1

    flush_section(current_h2, current_lines)

    # 目次
    toc_html = '<nav class="article-toc">\n  <ol>\n'
    for sid, h2_text in toc_items:
        toc_html += f'    <li><a href="#{sid}">{inline_convert(h2_text)}</a></li>\n'
    toc_html += '  </ol>\n</nav>'

    # 組み立て
    parts = []
    if lead_html:
        parts.append(lead_html)
    if toc_items:
        parts.append(toc_html)
    parts.extend(sections)

    article_body = '\n\n'.join(parts)

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>{escape_html(title)}</title>
  <meta name="description" content="{escape_html(meta_description)}">
</head>
<body>
<article>

{article_body}

</article>
</body>
</html>"""

    return html, title, meta


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Markdown → e-webseisaku HTML変換')
    parser.add_argument('input', help='入力Markdownファイル')
    parser.add_argument('output', nargs='?', help='出力HTMLファイル（省略時はstdout）')
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f'Error: {args.input} not found', file=sys.stderr)
        sys.exit(1)

    html, title, meta = convert(args.input)

    if args.output:
        Path(args.output).write_text(html, encoding='utf-8')
        print(f'Written: {args.output}')
        print(f'Title: {title}')
        if meta.get('slug'):
            print(f'Slug: {meta["slug"]}')
    else:
        print(html)
