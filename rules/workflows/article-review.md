# 記事レビュールール（v2）

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

---

## 品質ゲート 6項目（v2追加）

レビュー時は必ず以下6項目をすべてチェックすること：

| チェック項目 | 合格基準 | 不合格時の処理 |
|---|---|---|
| **文字数・構造** | 2,500字以上、h1〜h3の見出し、title/descriptionの文字数（120〜160字） | 自動修正指示（writerに差し戻し） |
| **ファクト** | 数値・固有名詞に出典URL、別モデルで検証済みか | 「要確認」フラグを付けて通知 |
| **重複** | 既存記事と主題が重複しない | テーマ再選定（seo-analystに差し戻し） |
| **表現** | NGワード・誇大表現なし・定型句の多用なし | 自動で書き直し指示 |
| **構造化データ** | Article / FAQPage（JSON-LD）が付いている | 自動付与指示 |
| **著作権** | 他サイト文章の転載なし（要約＋出典のみ） | 該当箇所を書き直し指示 |

## AIO要件チェック（v2追加）

- [ ] 冒頭（H1直後）に結論を200字以内で書いているか
- [ ] FAQ が 3〜5問あり、FAQPage JSON-LDスキーマが付いているか
- [ ] 数値・固有名詞に出典URLが付いているか
- [ ] 著者・監修者情報が記載されているか

---

## フォールバック③: article-reviewer エージェント（最終手段）

`article_review.sh` が **exit 2** を返した場合（`"fallback": true`）、**即座に** `article-reviewer` エージェントに切り替える。スクリプトの再試行は禁止。

```
Agent(subagent_type="article-reviewer", prompt="記事ファイル: <path> をレビューしてください。品質ゲート6項目とAIO要件を含めて評価すること。")
```

---

## レビュー結果 JSON の構造（v2）

```json
{
  "score": 88,
  "pass": true,
  "summary": "全体評価を1〜2文で",
  "gate_results": {
    "word_count": "pass",
    "fact": "flag",
    "duplicate": "pass",
    "expression": "pass",
    "structured_data": "auto_fix_needed",
    "copyright": "pass"
  },
  "aio_check": {
    "conclusion_first": true,
    "faq": true,
    "citations": false,
    "author": true
  },
  "issues": [
    {
      "severity": "high|medium|low",
      "category": "事実誤認|SEO|構成|文章品質|AIO|その他",
      "message": "指摘内容"
    }
  ],
  "improvement": "writerへの改善指示",
  "log_file": "/path/to/log"
}
```

- `pass: true`（score 85以上）→ wp-operator に下書き保存を依頼
- `pass: false` → writer にフィードバックを渡して再執筆 → 再レビュー（合格まで繰り返す。最大3回）
- 3回不合格 → Chatworkに通知して停止
