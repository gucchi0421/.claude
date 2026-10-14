---
name: article-loop
description: >
  記事自動生成ループを起動するスキル。
  /loop と Workflow スクリプト（article-pipeline.js）を組み合わせて
  記事生成 → レビュー → WP投稿を自律的に繰り返す。
  プロジェクトルートに .claude/settings.seo.json が必要。
---

# 記事自動生成ループ スキル

## 概要

このスキルを呼ぶと、以下のいずれかの方法で記事生成グラフを起動する。

- **セッション中に定期実行**: `/loop` コマンドで指定インターバルごとに Workflow を起動
- **一回フル実行**: Workflow ツールで `article-pipeline.js` を直接起動

---

## 前提確認

実行前に以下を確認する：

1. **`.claude/settings.seo.json`** がプロジェクトルートの `.claude/` 内にあるか
   - なければユーザーに内容を確認してから作成する（後述のフォーマット参照）
2. **MCPサーバー** — `mcp__gsc__*` と `mcp__analytics-mcp__*` が有効か
   - Loopモードでは不要（Workflowスクリプト内でデータ取得をスキップ or キャッシュ利用）
3. **WP-CLI** — `wp-operator` が使える環境か（SSH設定等）

---

## settings.seo.json フォーマット

```json
{
  "site_url": "https://example.com",
  "site_name": "サイト名",
  "articles_dir": "/absolute/path/to/.claude/articles",
  "wp_post_status": "draft",
  "max_review_retry": 3,
  "target_keywords": ["キーワードA", "キーワードB"],
  "notify_chatwork": true
}
```

| キー | 説明 |
|---|---|
| `site_url` | サイトURL（GSC・競合調査に使用） |
| `site_name` | サイト名（writerへの指示に含める） |
| `articles_dir` | 記事の保存先（絶対パス必須） |
| `wp_post_status` | `draft`（テスト中）/ `publish`（本番） |
| `max_review_retry` | reviewerの差し戻し上限（デフォルト3） |
| `target_keywords` | 優先的に狙うキーワード群（省略可） |
| `notify_chatwork` | 完了時にChatworkへ通知するか |

---

## 起動方法

### A: セッション中の定期自動実行（推奨）

```
/loop 1d 記事生成ループを起動して。設定は .claude/settings.seo.json を参照
```

Loopが起動されたら、このスキルのフロー（後述）に従って Workflow を実行する。

### B: 一回だけ実行

Workflow ツールで以下のように起動する：

```js
Workflow({ name: "article-pipeline", args: { project_dir: process.cwd() } })
```

---

## 実行フロー

このスキルが呼ばれたら以下を実行する：

1. `.claude/settings.seo.json` を読み込む
2. `settings.seo.json` の `articles_dir` を絶対パスとして確認
3. Workflow ツールで `~/.claude/workflows/article-pipeline.js` を起動する

```js
Workflow({
  scriptPath: "~/.claude/workflows/article-pipeline.js",
  args: {
    project_dir: "<カレントディレクトリの絶対パス>",
    seo_config: "<settings.seo.json の内容をオブジェクトで渡す>"
  }
})
```

4. Workflow 完了後、`notify_chatwork: true` の場合は `chatwork` スキルで完了通知
5. ログを `.claude/logs/article-loop-YYYY-MM-DD.md` に記録（recorder エージェント）

---

## エラー対応

| 状況 | 対処 |
|---|---|
| `settings.seo.json` がない | ユーザーに確認して作成してから再実行 |
| reviewer が3回連続不合格 | Chatworkに通知して停止 |
| wp-operator が失敗 | 下書き保存済みのファイルパスをChatworkに通知 |
| Workflow タイムアウト | `.claude/articles/` の最新ファイルを確認して手動で続行 |
