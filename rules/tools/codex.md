# Codex 連携ルール

## Codex が呼ばれる条件

### 自動（プロアクティブ）
`codex:rescue` サブエージェントは以下の状況で Claude が自律的に呼び出す：

- Claude 自身が実装・デバッグで詰まったとき
- 根本原因の調査に深い反復が必要なとき
- 大規模・複数ファイルにまたがる実装タスク
- 二重チェック・別視点のレビューが有効なとき

### 明示指示
ユーザーが「Codex と相談しながら進めて」と言ったとき。

### 呼ばれない条件
- Claude 単独で素早く完結できる小さなタスク
- 単純な質問・説明・検索

---

## セキュリティリスクと対策

### リスク
- Codex は `Bash` ツールのみを持ち、ファイルシステムに直接アクセスできる
- Claude の `deny` 設定（`.env` 読み取り禁止など）は **Codex には適用されない**
- タスクの文脈に機密情報が含まれていた場合、Codex が参照・送信する可能性がある

### 禁止事項
- `.env` / `*secret*` / `*.pem` 等の機密ファイルを読むタスクを Codex に渡さない
- API キー・パスワード・トークンを含むプロンプトを Codex に渡さない
- 認証情報が必要な操作（デプロイ・push 等）を Codex に単独で実行させない

### Codex に渡すタスクの指針
- スコープをコードの実装・修正・レビューに限定する
- 「このファイルを読んで」ではなく「この仕様を実装して」と伝える
- 渡すコンテキストに機密値が入っていないか確認してから委譲する

---

## 記事レビューの委託方法

### 優先: Codex CLI が使える場合

記事レビューは **必ず `~/.claude/scripts/article_review.sh` 経由で実行する**。
Agent ツールや `codex:rescue` を直接使った場合、ログ全文がコンテキストに乗りトークンを大量消費するため禁止。

```bash
ARTICLE=$(cat "<article_file_path>")
bash ~/.claude/scripts/article_review.sh "$ARTICLE" "<追加指示>"
```

- スクリプトは構造化 JSON サマリーのみを stdout に返す（70〜85% のトークン削減）
- 優先順位: **Codex → Gemini → article-reviewer** の順で自動フォールバック
- 全ログは `$(pwd)/.codex/logs/` に自動保存される
- JSON の `log_file` フィールドにログのフルパスが含まれるので、サマリーに必ず記載して参照しやすくする
- 詳細確認が必要なときは `! cat <log_file>` で任意に参照できる

### 内部スクリプト構成（直接呼び出し禁止）

| スクリプト | 役割 |
|---|---|
| `article_review.sh` | メイン振り分け担当（これだけ呼ぶ） |
| `article_review_codex.sh` | Codex 実行 → NG なら Gemini へ自動移譲 |
| `article_review_gemini.sh` | Gemini CLI 実行 |

### フォールバック: article-reviewer エージェント（最終手段）

`article_review.sh` が **exit 2** を返した場合（`"fallback": true`）、**即座に** `article-reviewer` エージェントに切り替える。スクリプトの再試行は禁止。

```
Agent(subagent_type="article-reviewer", prompt="記事ファイル: <path> をレビューしてください。...")
```

- `article-reviewer` は WebSearch で事実確認・ハルシネーション検証もできる
- スコア80点以上で合格の基準は同じ

---

## Codex の動作仕様（把握しておくべき点）

- デフォルトは `--write` モード（ファイルを書き換える）
- `--background` を指定しない場合はフォアグラウンド実行
- タスクが複雑・長時間になりそうな場合は自動的に `--background` を選択
- `stop-review-gate` が有効な場合、変更後に adversarial レビューが走る
