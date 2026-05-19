---
name: ga4-fetch
description: >
  プロジェクトの .claude/ga4_settings.json を参照して GA4 Data API からデータを取得し JSON で stdout に出力するスキル。
  data-analyst エージェントに渡す用途を想定。
---

# GA4 データ取得スキル

プロジェクトの `.claude/ga4_settings.json` に定義されたプロパティ・ディメンション・メトリクスで GA4 からデータを取得し、JSON を stdout に出力するのだ！

## 実行前チェック（必須）

スクリプトを実行する前に以下を確認し、不足があればユーザーに案内してから止まること。

### 1. ライブラリ確認
```bash
python3.12 -c "import google.analytics.data_v1beta" 2>&1
```
失敗したら案内する：
> `google-analytics-data` が未インストールなのだ！`pip install google-analytics-data` を実行してほしいのだ！

### 2. 認証情報確認
```bash
grep "CLAUDE_GCP_CREDENTIALS" ~/.claude/.env 2>/dev/null
```
見つからなければ案内する：
> `~/.claude/.env` に `CLAUDE_GCP_CREDENTIALS=/path/to/key.json` を追加してほしいのだ！GCP サービスアカウントの JSON キーファイルのパスを設定するのだ！

### 3. settings.json 確認
`.claude/ga4_settings.json` の `properties` に実際のプロパティIDが設定されているか確認する。`YOUR_PROPERTY_ID` のままなら案内する：
> `ga4_settings.json` の `properties[].id` に GA4 プロパティID を設定してほしいのだ！

全チェックが通ったら実行するのだ！

## 実行コマンド

```bash
# settings の date_range を使って全プロパティ取得
python3.12 ~/.claude/scripts/ga4_fetch.py

# 日付を指定
python3.12 ~/.claude/scripts/ga4_fetch.py --start-date 2024-01-01 --end-date 2024-01-31

# 特定プロパティのみ
python3.12 ~/.claude/scripts/ga4_fetch.py --property-id 123456789
```

## オプション

| オプション | デフォルト | 説明 |
|---|---|---|
| `--start-date` | settings の `date_range.start` | 開始日（`30daysAgo` / `YYYY-MM-DD`） |
| `--end-date` | settings の `date_range.end` | 終了日（`today` / `YYYY-MM-DD`） |
| `--property-id` | settings の全 properties | 単一プロパティのみ取得 |

## 出力形式（JSON）

```json
[
  {
    "property_id": "123456789",
    "property_name": "サイトA",
    "start_date": "30daysAgo",
    "end_date": "today",
    "row_count": 42,
    "rows": [
      { "date": "20240101", "pagePath": "/", "sessions": "123", ... }
    ]
  }
]
```

## data-analyst エージェントへの渡し方

```bash
python3.12 ~/.claude/scripts/ga4_fetch.py
```

の出力を Bash ツールで受け取り、そのまま data-analyst エージェントに渡すのだ！

## エラー対処

| エラーメッセージ | 対処 |
|---|---|
| `CLAUDE_GCP_CREDENTIALS が見つかりません` | `~/.claude/.env` に `CLAUDE_GCP_CREDENTIALS=` を追記 |
| `ga4_settings.json が見つかりません` | `.claude/ga4_settings.json` を作成 |
| `403 / Permission denied` | GA4 プロパティにサービスアカウントを「閲覧者」で追加 |
