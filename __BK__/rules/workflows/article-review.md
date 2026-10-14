# 記事レビューワークフロー

記事・ブログ・SEOコンテンツの品質レビューは **必ず `~/.claude/scripts/article_review.sh` 経由で実行する**。
Agent ツールや各エンジンの CLI を直接呼び出した場合、ログ全文がコンテキストに乗りトークンを大量消費するため禁止。

---

## 実行方法

```bash
ARTICLE=$(cat "<article_file_path>")
bash ~/.claude/scripts/article_review.sh "$ARTICLE" "<追加指示>"
```

- スクリプトは構造化 JSON サマリーのみを stdout に返す（70〜85% のトークン削減）
- 全ログは `$(pwd)/.codex/logs/` に自動保存される
- JSON の `log_file` フィールドにログのフルパスが含まれる → サマリーに必ず記載する
- 詳細確認が必要なときは `! cat <log_file>` で任意に参照できる

---

## 優先順位とフォールバック

```
article_review.sh（振り分け担当）
  ↓ 1. Codex が使えるか確認 → OK なら article_review_codex.sh で実行
  ↓ Codex NG
  ↓ 2. Gemini が使えるか確認 → OK なら article_review_gemini.sh で実行
  ↓ Gemini NG（exit 2 / fallback: true）
  ↓ 3. article-reviewer エージェントに切り替え（Claude が判断）
```

### 内部スクリプト構成（直接呼び出し禁止）

| スクリプト | 役割 |
|---|---|
| `article_review.sh` | メイン振り分け担当（これだけ呼ぶ） |
| `article_review_codex.sh` | Codex 実行 → NG なら Gemini へ自動移譲 |
| `article_review_gemini.sh` | Gemini CLI 実行 |

---

## フォールバック③: article-reviewer エージェント（最終手段）

`article_review.sh` が **exit 2** を返した場合（`"fallback": true`）、**即座に** `article-reviewer` エージェントに切り替える。スクリプトの再試行は禁止。

```
Agent(subagent_type="article-reviewer", prompt="記事ファイル: <path> をレビューしてください。...")
```

- `article-reviewer` は WebSearch で事実確認・ハルシネーション検証もできる
- スコア80点以上で合格の基準は同じ

---

## レビュー結果 JSON の構造

```json
{
  "score": 85,
  "pass": true,
  "summary": "全体評価を1〜2文で",
  "issues": [
    {
      "severity": "high|medium|low",
      "category": "事実誤認|SEO|構成|文章品質|その他",
      "message": "指摘内容"
    }
  ],
  "improvement": "writerへの改善指示",
  "log_file": "/path/to/log"
}
```

- `pass: true`（score 80以上）→ wp-operator に投稿依頼
- `pass: false` → writer にフィードバックを渡して再執筆 → 再レビュー（合格まで繰り返す）
