---
name: seo-log
description: >
  SEO作業履歴をGoogleスプレッドシートに記録するスキル。
  ~/.claude/scripts/log_seo.py を使い、~/.claude/.env の CLAUDE_GCP_CREDENTIALS で認証する。
  seo-engineer / wp-operator / writer が作業完了後に呼び出す。
---

# SEO作業ログスキル

## トリガー

SEO関連の作業が完了したとき。以下のエージェントが完了後に呼び出す：
- `writer` — 記事執筆・リライト完了後
- `seo-engineer` — メタ情報更新・施策実行後
- `wp-operator` — 記事投稿・AIOSEO設定変更後

## 前提確認

実行前に以下を確認する：

1. **`~/.claude/.env` の `CLAUDE_GCP_CREDENTIALS`** — サービスアカウントJSONファイルのパスが設定されているか
   - ※ `.env` の中身は読まない。存在確認のみ

2. **`.claude/settings.sheets.json` の存在確認** — プロジェクトルートの `.claude/` 内にあるか
   - なければ「初回セットアップ」フローへ

## 初回セットアップ（settings.sheets.json がない場合）

ユーザーに以下を確認してから `.claude/settings.sheets.json` を作成する：

```json
{
  "spreadsheet_id": "GoogleスプレッドシートのID（URLの /d/〇〇〇/ 部分）",
  "seo_sheet": "SEO作業履歴"
}
```

シートが存在しない場合、スクリプトが初回実行時にヘッダー行を自動作成する。

## 実行

```bash
python3.12 ~/.claude/scripts/log_seo.py \
  --type "作業種別" \
  --url "https://example.com/page" \
  --keywords "キーワードA, キーワードB" \
  --summary "作業内容の要約" \
  --agent "担当エージェント名" \
  --result "結果・メモ" \
  --detail "3C分析・競合調査・キーワードリスト等の詳細（長文可）"
```

`--url` / `--keywords` / `--detail` は省略可能。`--type` と `--summary` は必須。

### 作業種別の例

| 種別 | 使用場面 |
|---|---|
| `記事投稿` | 新規記事を公開したとき |
| `リライト` | 既存記事を加筆修正したとき |
| `メタ更新` | AIOSEOのタイトル・ディスクリプションを変更したとき |
| `AIOSEO設定` | プラグイン設定（サイトマップ等）を変更したとき |
| `サイト設定` | サイトタイトル・テーマ設定を変更したとき |
| `内部リンク` | 内部リンクを追加・変更したとき |

### 実行例

```bash
# キーワード調査・3C分析後
python3.12 ~/.claude/scripts/log_seo.py \
  --type "キーワード調査" \
  --url "https://example.com/blog/seo-kiso" \
  --keywords "SEO対策, 内部リンク" \
  --summary "競合上位5サイトの構成・文字数を調査" \
  --agent "seo-analyst" \
  --result "優先KW確定" \
  --detail "【3C分析】自社: ドメイン弱め / 競合: A社が1位・平均5000字 / 市場: 情報収集フェーズ多い"

# 記事投稿後
python3.12 ~/.claude/scripts/log_seo.py \
  --type "記事投稿" \
  --url "https://example.com/blog/seo-kiso" \
  --keywords "SEO基礎" \
  --summary "「SEO基礎知識」記事を新規投稿（4200字）" \
  --agent "writer" \
  --result "公開完了 post_id=123"

# AIOSEOメタ更新後
python3.12 ~/.claude/scripts/log_seo.py \
  --type "メタ更新" \
  --url "https://example.com/blog/seo-kiso" \
  --summary "タイトルタグ・メタディスクリプションをAIOSEOで更新" \
  --agent "seo-engineer" \
  --result "スコア改善: 72→88"
```

## スプレッドシートの列構成

| A: 日付 | B: 作業種別 | C: URL | D: キーワード | E: 作業内容 | F: 担当エージェント | G: 結果・メモ | H: 詳細 |
|---|---|---|---|---|---|---|---|
| 2026-05-15 14:30 | 記事投稿 | /blog/seo-kiso | SEO対策 | SEO基礎知識記事を新規投稿 | writer | 公開完了 | （3C分析等） |

---

## キーワード順位遷移の記録

```bash
python3.12 ~/.claude/scripts/seo_ranking.py \
  --keyword "SEO対策" \
  --url "https://example.com/blog/seo" \
  --rank 5
# --date "2026-05-15" で日付を指定可能（省略時は今日）
```

### シートのデザイン

| 要素 | 仕様 |
|---|---|
| ヘッダー | ネイビー背景・白文字・太字 |
| キーワード列 | ラベンダー背景・太字 |
| 順位セル（改善） | ライトグリーン |
| 順位セル（悪化） | ライトレッド |
| 順位セル（初回） | ライトブルー |
| トレンド列 | スパークライン（折れ線グラフ）自動更新 |
| 行 | 交互ストライプ |
| 固定 | 1行目 + キーワード・URL列を固定 |

### settings.sheets.json に追加が必要なキー

```json
{
  "ranking_sheet": "キーワード順位遷移"
}
```

---

## エラー対応

| エラー | 対処 |
|---|---|
| `CLAUDE_GCP_CREDENTIALS が未設定` | `~/.claude/.env` に `CLAUDE_GCP_CREDENTIALS=/path/to/key.json` を追記 |
| `settings.sheets.json が見つかりません` | 初回セットアップフローへ |
| `spreadsheet_id がありません` | `settings.sheets.json` の `spreadsheet_id` を確認 |
| 権限エラー | サービスアカウントのメールアドレスをスプレッドシートの編集者として共有 |
| `SERVICE_DISABLED` | GCPコンソールで Google Sheets API を有効化する（有効化後1〜2分待つ） |
