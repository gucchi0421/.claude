# コア設定（全セッション必須）

@rules/_core/persona.md
@rules/_core/output-format.md
@rules/_core/session-start.md
@rules/_core/token-efficiency.md

# Git 規約

@rules/workflows/git-workflow.md

# セキュリティ

@rules/_core/security.md

# Codex 連携

@rules/tools/codex.md

# 記事作成のルール

記事・ブログ・コラム・SEOコンテンツの執筆依頼があった場合は **必ず** 以下のパイプラインを実行する。Claude 単独での執筆は禁止。

**MCPはサブエージェントから使えない。GA4・GSCデータは必ずメインClaudeが取得してからエージェントに渡す。**
プロジェクト設定は `.claude/settings.seo.json` に記載する。

1. **メインClaude** — `mcp__gsc__*` と `mcp__analytics-mcp__*` でGSC・GA4データを取得・分析まで行う
2. **`competitor-analyst`** — メインの分析結果を渡して並列で競合調査を起動する（`data-analyst` は不要）
3. **`seo-analyst`** — メインの分析結果 + competitor-analyst の調査結果を渡してキーワード選定・執筆指示書を作成する
4. **`writer`** — 執筆指示書をベースに執筆する
5. **`article-reviewer`** — 品質レビューを実施する（スコア80点以上で合格）
6. 不合格の場合は **`writer`** にフィードバックを渡して再執筆 → `article-reviewer` で再評価（合格まで繰り返す）
7. 合格後は **`wp-operator`** が WordPress に投稿・公開する
