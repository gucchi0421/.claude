---
name: seo-setup
description: >
  新規SEOプロジェクトのセットアップスキル。
  質問に答えるだけで ~/.claude/examples/seo/ の雛形をコピーし、
  CLAUDE.local.md・settings*.json・crontab を自動構成する。
---

# SEOプロジェクトセットアップスキル

## トリガー

ユーザーが `/setup-seo` を実行したとき。

## 概要

このスキルは以下を自動で行う：

1. ユーザーに質問して設定値を収集する
2. `~/.claude/examples/seo/` の雛形をプロジェクトディレクトリにコピーする
3. 以下のファイルを生成する：
   - `CLAUDE.local.md` — プロジェクト設定の主ファイル
   - `.claude/settings.json` — パーミッション設定
   - `.claude/settings.seo.json` — GSC・GA4・SEO設定
   - `.claude/settings.ssh.json` — SSH接続設定
   - `.claude/settings.local.json` — MCP有効化・サンドボックス設定
   - `.claude/logs/schedule/index.md` — cron引き継ぎログ初期値
4. crontab に自動実行タスクを追加する（確認後）

---

## Step 1: 質問収集

AskUserQuestion ツールで最大4問ずつまとめて聞く。

### 質問セット①（サイト・接続情報）

1. プロジェクトディレクトリの絶対パス（例: `/home/username/documents/claude/mysite.com`）
2. サイト名（例: `example.com`）
3. 業種・サービス内容（例: `ホームページ制作会社（大阪）`）
4. メインターゲットキーワード（例: `ホームページ制作 大阪 / WEB制作 大阪`）

### 質問セット②（WordPress・GSC・GA4）

5. GSCサイトURL（例: `https://www.example.com/`）
6. GA4プロパティID（例: `properties/123456789`）
7. SSH接続先エイリアス（例: `webchecker5`）
8. WordPressの絶対パス（例: `/home/user/public_html/wp`）

### 質問セット③（オプション）

9. テストサイトURL（本番と別の場合。例: `https://test.example.com/`）
10. WP管理者ユーザーID（デフォルト: `1`）
11. SEO記事の投稿タイプ（デフォルト: `column`）
12. cronタスクを登録するか？（yes / no）

---

## Step 2: 雛形コピー

```bash
mkdir -p {PROJECT_DIR}/.claude
cp -r ~/.claude/examples/seo/. {PROJECT_DIR}/.claude/examples/seo/
```

---

## Step 3: CLAUDE.local.md を生成

`{PROJECT_DIR}/CLAUDE.local.md` に書き込む：

```markdown
# {サイト名} プロジェクト

## サイト概要

- **サイト名**: {サイト名}
- **業種**: {業種・サービス内容}
- **メインターゲットキーワード**: {メインターゲットキーワード}
- **コンテンツ目標**: 月間PV・CV率の向上

## 接続情報

- **GSC サイトURL**: `{GSC サイトURL}`
- **GA4 プロパティID**: `{GA4 プロパティID}`
- **SSH接続**: `ssh {SSH接続先エイリアス}`
- **WordPressパス**: `{WordPress の絶対パス}`

## 環境について

- **作業環境（テストサイト）**: `{テストサイトURL}` — SSH接続先はここ。実質的な作業本番環境として扱う
- **GSCのみ本番**: GSCは `{GSC サイトURL}` の本番データを参照する
- **動作確認はテストサイトのURLで行う**
- 本番サイトのSSH接続情報は未取得

## WordPress 構成

- WordPressはサブディレクトリ `wp/` にインストールされている
- カスタム投稿タイプ `{SEO記事の投稿タイプ}` がSEO記事用として存在する
- 記事のURLは `/{SEO記事の投稿タイプ}/ID/` 形式
- WP-CLIで `post_name` を取得するとURLエンコードされた日本語スラッグが返る（IDで管理する方が確実）

## 自律行動ルール

- ユーザーに確認せず、自律的に判断・実行する
- 気づき・判断根拠は積極的に `.claude/logs/summary/YYYYMMDD.md` にメモする
- **約10分考えても方針が定まらない・認識の前提が怪しいと感じたら、即中断してユーザーを呼ぶ（これだけは必須）**

## 主な作業内容

- `{SEO記事の投稿タイプ}` カスタム投稿タイプのSEO記事を更新・新規作成する
- WP-CLIはSSH経由で `--path` を明示して実行する

## WP-CLI 注意事項

- 記事の投稿・更新時は必ず `--post_author={WP管理者ユーザーID}` を明示すること
  - 省略すると `post_author=0` になり著者情報が取得できずPHP警告が発生する

## WP-CLI 実行例

```bash
ssh {SSH接続先エイリアス} "wp post list --post_type={SEO記事の投稿タイプ} --fields=ID,post_title,post_status --path={WordPress の絶対パス}"
```
```

---

## Step 4: .claude/settings.seo.json を生成

GSC・GA4・SEO関連の設定：

```json
{
  "gsc_site_url": "{GSC サイトURL}",
  "ga4_property_id": "{GA4 プロパティID}",
  "target_topics": [
    "{メインターゲットキーワード1}",
    "{メインターゲットキーワード2}"
  ],
  "content_goals": "月間PV・CV率の向上"
}
```

---

## Step 5: .claude/settings.ssh.json を生成

SSH接続設定：

```json
{
  "_comment": "SSH接続設定。プロジェクト直下の .claude/settings.ssh.json に配置する",
  "connection": "{SSH接続先エイリアス}",
  "config": "~/.ssh/config",
  "allowed_dirs": [
    "{WordPress の絶対パスの親ディレクトリ（public_html以下）}"
  ],
  "local": false
}
```

---

## Step 6: .claude/settings.json を生成

パーミッション設定（`{PROJECT_DIR}` のパスも反映）：

```json
{
  "permissions": {
    "allow": [
      "Bash(ssh {SSH接続先エイリアス} *)",
      "Bash(scp * {SSH接続先エイリアス}:{WordPress の絶対パス}*)",
      "Bash(scp * {SSH接続先エイリアス}:/tmp/*)",
      "Bash(python3 *)",
      "Bash(bash *)",
      "Bash(wp *)",
      "Bash(git *)",
      "Bash(cat *)",
      "Bash(ls *)",
      "Bash(grep *)",
      "Bash(find *)",
      "Bash(curl *)",
      "Bash(mkdir *)",
      "Bash(cp *)",
      "Bash(mv *)",
      "Write({PROJECT_DIR}/**)",
      "Write(/tmp/**)",
      "Edit({PROJECT_DIR}/**)",
      "Edit(/tmp/**)",
      "Read({PROJECT_DIR}/**)",
      "Read(/tmp/**)",
      "mcp__gsc__*",
      "mcp__analytics-mcp__*"
    ],
    "deny": [
      "Bash(rm -rf*)",
      "Bash(ssh {SSH接続先エイリアス} * rm -rf*)",
      "Bash(dd *)",
      "Bash(mkfs*)"
    ]
  }
}
```

---

## Step 7: .claude/settings.local.json を生成

MCP有効化・サンドボックス設定：

```json
{
  "enabledMcpjsonServers": [
    "analytics-mcp",
    "gsc",
    "JapaneseTextAnalyzer",
    "chatwork"
  ],
  "sandbox": {
    "enabled": false,
    "autoAllowBashIfSandboxed": false
  }
}
```

---

## Step 8: ディレクトリ構造を作成

```bash
mkdir -p {PROJECT_DIR}/.claude/logs/schedule
mkdir -p {PROJECT_DIR}/.claude/logs/summary
mkdir -p {PROJECT_DIR}/.claude/articles
```

`{PROJECT_DIR}/.claude/logs/schedule/index.md` を作成：

```markdown
# スケジュールエージェント引き継ぎログ

## 最終更新

（まだ実行されていません）

## 各タスクの状態

| タスク | 最終実行 | 状態 | 次回やること |
|---|---|---|---|
| rewrite | — | 未実行 | 下書き記事をリライトして公開 |
| new-article | — | 未実行 | GSC分析→完全新規記事を執筆・公開 |
| seo | — | 未実行 | クイックウィン記事のタイトル・AIOSEO改善 |
| pdca | — | 未実行 | PHP/CSS/導線レベルの構造改善 |
```

---

## Step 9: crontab 登録（cronタスク = yes の場合）

現在のcrontabを表示して確認後、以下を追記：

```
10 * * * * bash ~/.claude/scripts/run-seo-agent.sh rewrite {PROJECT_DIR}
20 * * * * bash ~/.claude/scripts/run-seo-agent.sh new-article {PROJECT_DIR}
30 * * * * bash ~/.claude/scripts/run-seo-agent.sh seo {PROJECT_DIR}
40 * * * * bash ~/.claude/scripts/run-seo-agent.sh pdca {PROJECT_DIR}
```

---

## 完了メッセージ

```
✅ セットアップ完了！

作成されたファイル：
- {PROJECT_DIR}/CLAUDE.local.md
- {PROJECT_DIR}/.claude/settings.json
- {PROJECT_DIR}/.claude/settings.seo.json
- {PROJECT_DIR}/.claude/settings.ssh.json
- {PROJECT_DIR}/.claude/settings.local.json
- {PROJECT_DIR}/.claude/logs/schedule/index.md

次のステップ：
1. CLAUDE.local.md を開いて内容を確認・修正する
2. claude でプロジェクトディレクトリを開く
3. cron が動き始めるまで待つ（毎時10/20/30/40分）
```
