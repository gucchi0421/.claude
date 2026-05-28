# 記事作成ワークフロー

記事・ブログ・コラム・SEOコンテンツの執筆依頼があった場合は **必ず** 以下のパイプラインを実行する。Claude 単独での執筆は禁止。

**MCPはサブエージェントから使えない。GA4・GSCデータは必ずメインClaudeが取得してからエージェントに渡す。**
プロジェクト設定は `.claude/settings.seo.json` に記載する。

1. **メインClaude** — `mcp__gsc__*` と `mcp__analytics-mcp__*` でGSC・GA4データを取得・分析まで行う
2. **`competitor-analyst`** — メインの分析結果を渡して並列で競合調査を起動する（`data-analyst` は不要）
3. **`seo-analyst`** — メインの分析結果 + competitor-analyst の調査結果を渡してキーワード選定・執筆指示書を作成する
4. **`writer`** — 執筆指示書 + `ARTICLES_DIR={プロジェクト絶対パス}/.claude/articles` を渡して執筆・保存させる
   - **出力はMarkdown（`.md`）のみ。HTMLは書かない**
   - Frontmatterに `title` / `slug` / `post_type` / `post_author: 1` を必ず含める
   - HTML構造・クラス名はwriterが意識しなくてよい（変換スクリプトが付与する）
5. **MD→HTML変換** — メインClaudeが変換スクリプトを実行してHTMLを生成する
   ```bash
   python3 ~/.claude/scripts/article_md_to_html.py {ARTICLES_DIR}/{slug}.md {ARTICLES_DIR}/{slug}.html
   ```
6. **品質レビュー** — `article_review.sh` で実施する（詳細は `workflows/article-review.md`）
7. 不合格の場合は **`writer`** にフィードバックを渡して `.md` を再執筆 → 変換 → 再レビュー（合格まで繰り返す）
8. 合格後は **`wp-operator`** に `ARTICLES_DIR={プロジェクト絶対パス}/.claude/articles` を渡して WordPress に投稿・公開させる

**`ARTICLES_DIR` はメインClaudeが絶対パスで算出して渡す。サブエージェントが自己解決しない。**
