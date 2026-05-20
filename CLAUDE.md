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

1. **`seo-analyst`** — キーワードまたは指定タイトルをもとに競合調査・検索意図の分析を行う
2. **`writer`** — seo-analyst の調査結果をベースに執筆する
3. **`article-reviewer`** — 品質レビューを実施する（スコア80点以上で合格）
4. 不合格の場合は **`writer`** にフィードバックを渡して再執筆 → `article-reviewer` で再評価（合格まで繰り返す）
