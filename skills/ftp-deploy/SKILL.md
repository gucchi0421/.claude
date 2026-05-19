---
name: ftp-deploy
description: >
  プロジェクトの変更ファイルを FTP で本番サーバーへアップロードするスキル。
  ~/.claude/scripts/ftp_deploy.py を使い、プロジェクト直下の .env から接続情報を読む。
---

# FTP デプロイスキル

## トリガー

`/ftp_deploy` が呼ばれたとき。

## 前提確認

実行前に以下を確認する：

1. **`.env` の存在確認** — プロジェクトルート直下に `.env` があり、以下が設定されているか
   - `CLAUDE_FTP_HOST` / `CLAUDE_FTP_USERNAME` / `CLAUDE_FTP_PASSWORD`
   - ※ `.env` の中身は読まない。`ls` でファイルの存在のみ確認する

2. **`settings.ftp.json` の存在確認** — `.claude/settings.ftp.json` があるか
   - なければ「初回セットアップ」フローへ

3. **アップロード対象の確認** — `.claude/logs/deploy/.pendings.md` の内容を表示してユーザーに確認を求める

## 接続テスト

アップロードせず接続確認・リモートの ls をしたいときは：

```bash
python3 ~/.claude/scripts/ftp_deploy.py --test
```

接続成功でカレントディレクトリとディレクトリ一覧が表示される。

## 初回セットアップ（settings.ftp.json がない場合）

`settings.ftp.json` がなければ、以下の手順でマッピングを作成する。

### 1. リモート構造を確認する

```bash
python3 ~/.claude/scripts/ftp_deploy.py --test
```

リモートのディレクトリ一覧をユーザーに見せる。

### 2. マッピングをユーザーに聞く

「ローカルのどのフォルダ」→「リモートのどのパス」に対応するかを聞く。

例：
- ローカル: `wp-content/themes/my-theme/`
- リモート: `/public_html/wp-content/themes/my-theme/`

複数フォルダがある場合はすべて確認する。

### 3. settings.ftp.json を書く

`.claude/settings.ftp.json` に Write ツールで作成する：

```json
{
    "_comment": "ローカルの相対パスプレフィックス → リモートの絶対パスプレフィックス",
    "wp-content/themes/my-theme/": "/public_html/wp-content/themes/my-theme/"
}
```

形式は最長一致で解決するため、具体的なパスほど優先される。

## 通常デプロイ手順

### 1. pending ファイルの表示

```bash
cat .claude/logs/deploy/.pendings.md 2>/dev/null || echo "（対象ファイルなし）"
```

内容を確認してユーザーに「このファイルをアップロードしますか？」と確認を求める。

### 2. デプロイ実行

ユーザーが承認したら実行する：

```bash
python3 ~/.claude/scripts/ftp_deploy.py
```

### 3. 結果報告

- アップロードされたファイル一覧
- エラーがあれば内容と対処法

## 禁止事項

- アップロード先のパスについて「意図と異なる可能性」「Dockerマウントの構造上〜」などの推測・提案をしない
- バックアップはパス階層をそのまま踏襲するだけ。余計な解釈は不要
- FTP操作のためのインラインスクリプトを書かない。必ず `python3 ~/.claude/scripts/ftp_deploy.py` を使う

## エラー対応

| エラー | 対処 |
|--------|------|
| `.env` がない | プロジェクトルートに `CLAUDE_FTP_HOST` / `CLAUDE_FTP_USERNAME` / `CLAUDE_FTP_PASSWORD` を記載した `.env` を作るよう案内 |
| `settings.ftp.json` がない | 初回セットアップフローへ |
| 接続失敗（FTPS 非対応） | サーバーが FTPS 未対応の可能性。`ftp_deploy.py` の `FTP_TLS` を `FTP` に変更するか確認する |
