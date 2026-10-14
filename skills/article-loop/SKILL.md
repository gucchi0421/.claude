---
name: article-loop
description: >
  記事自動生成ループを起動するスキル（v2）。
  /loop と Workflow スクリプト（article-pipeline.js）を組み合わせて
  リサーチ → 執筆 → ファクトチェック → 品質ゲート → WP下書き保存 → Chatwork承認依頼
  を自律的に繰り返す。承認（予約投稿への変更）は必ずCEOが行う。
  プロジェクトルートに .claude/settings.seo.json が必要。
---

# 記事自動生成ループ スキル（v2）

## 概要

このスキルを呼ぶと、以下のいずれかの方法で記事生成パイプラインを起動する。

- **セッション中に定期実行**: `/loop` コマンドで指定インターバルごとに Workflow を起動
- **GitHub Actions から起動**: cronトリガー で `article-pipeline.js` を実行（推奨）
- **一回フル実行**: Workflow ツールで `article-pipeline.js` を直接起動

---

## 前提確認

実行前に以下を確認する：

1. **`.claude/settings.seo.json`** がプロジェクトルートの `.claude/` 内にあるか
2. **GitHub Secrets** に以下が登録されているか
   - `WP_APP_PASSWORD`（または `WP_APP_PASSWORD_STAGING`）
   - 各AI APIキー（`ANTHROPIC_API_KEY` / `OPENAI_API_KEY` / `GEMINI_API_KEY`）
3. **通知先**: `chatwork_room_id` が settings.seo.json に設定されているか

---

## settings.seo.json フォーマット（v2）

```json
{
  "env": "staging",
  "production": {
    "site_url": "https://example.com",
    "site_name": "サイト名",
    "wp_api_url": "https://example.com/wp-json/wp/v2",
    "wp_app_password_key": "WP_APP_PASSWORD"
  },
  "staging": {
    "site_url": "https://staging.example.com",
    "site_name": "サイト名（ステージング）",
    "wp_api_url": "https://staging.example.com/wp-json/wp/v2",
    "wp_app_password_key": "WP_APP_PASSWORD_STAGING"
  },
  "articles_dir": "/absolute/path/to/.claude/articles",
  "max_review_retry": 3,
  "target_keywords": ["キーワードA", "キーワードB"],
  "notify_chatwork": true,
  "chatwork_room_id": "123456789",
  "image_mode": "manual"
}
```

| キー | 説明 |
|---|---|
| `env` | `staging` / `production` を切り替える |
| `wp_api_url` | WordPress REST API のベースURL |
| `wp_app_password_key` | GitHub Secrets のキー名（実値ではない） |
| `articles_dir` | 記事Markdownの保存先（絶対パス） |
| `max_review_retry` | 品質ゲートの差し戻し上限（デフォルト3） |
| `notify_chatwork` | 完了・承認依頼をChatworkに通知するか |
| `chatwork_room_id` | 通知先ChatworkルームID |
| `image_mode` | `manual`（CEO手動設定）/ 将来: `adobe_stock` |

---

## 起動方法

### A: GitHub Actions から起動（推奨・本番運用）

`.github/workflows/weekly-article.yml` の cron でトリガーする。
セッションを閉じても動く。7日制限なし。

```yaml
# 毎週月曜 6:00 JST（21:00 UTC）
on:
  schedule:
    - cron: '0 21 * * 0'
```

### B: セッション中に定期実行

```
/loop 1d 記事生成ループを起動して。設定は .claude/settings.seo.json を参照
```

※セッションを閉じると止まる。7日で自動失効。開発・テスト用途向け。

### C: 一回だけ実行

```js
Workflow({ name: "article-pipeline", args: { project_dir: process.cwd(), seo_config: {...} } })
```

---

## 実行フロー

1. `.claude/settings.seo.json` を読み込む
2. `articles_dir` を絶対パスとして確認
3. Workflow ツールで `~/.claude/workflows/article-pipeline.js` を起動する
4. Workflow 完了後、Chatworkに承認依頼通知（`notify_chatwork: true` の場合）

---

## 承認フロー

1. Workflow完了 → ChatworkにWordPress下書きURLが届く
2. CEOが下書きを確認・修正・アイキャッチ画像を設定
3. ステータスを「予約投稿」に変更 = 承認
4. **自動公開は絶対にしない。必ずCEOの承認を経る**

---

## 画像について

現在は `image_mode: "manual"` で運用。
CEO が WordPress 下書き上でアイキャッチ画像を手動設定する。

将来的に `image_mode: "adobe_stock"` で Adobe Stock API / SVG自動生成に差し替え予定。
`article-pipeline.js` の画像phaseにプレースホルダーが用意されている。

---

## エラー対応

| 状況 | 対処 |
|---|---|
| `settings.seo.json` がない | ユーザーに確認して作成してから再実行 |
| 品質ゲートが3回連続不合格 | Chatworkに通知して停止 |
| wp-operator が失敗 | 下書き保存前のMarkdownファイルパスをChatworkに通知 |
| Workflow タイムアウト | `.claude/articles/` の最新ファイルを確認して手動で続行 |
| 48時間経過しても承認なし | wp-operatorが自動で再通知 |
