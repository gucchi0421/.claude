#!/usr/bin/env python3
"""HTMLファイルから <article> タグの中身を抽出して stdout に出力する"""
import sys
from html.parser import HTMLParser
from html import escape


class ArticleExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_article = False
        self.in_pre = False
        self.depth = 0
        self.content = []

    def handle_starttag(self, tag, attrs):
        if tag == 'article':
            self.in_article = True
            self.depth = 1
            return
        if self.in_article:
            self.depth += 1
            attr_str = ''.join(f' {k}="{v}"' for k, v in attrs if v)
            self.content.append(f'<{tag}{attr_str}>')
            if tag == 'pre':
                self.in_pre = True

    def handle_endtag(self, tag):
        if self.in_article:
            if tag == 'article':
                self.depth -= 1
                if self.depth == 0:
                    self.in_article = False
                return
            if tag == 'pre':
                self.in_pre = False
            self.content.append(f'</{tag}>')

    def handle_data(self, data):
        if self.in_article:
            # <pre>内はHTMLエスケープして再エスケープ済み状態を保つ
            if self.in_pre:
                self.content.append(escape(data, quote=False))
            else:
                self.content.append(data)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: article_extract_html.py <html_file>', file=sys.stderr)
        sys.exit(1)

    parser = ArticleExtractor()
    parser.feed(open(sys.argv[1], encoding='utf-8').read())
    print(''.join(parser.content))
