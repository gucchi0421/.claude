# Claude Code 現状の設定・活用まとめ 20260518

自社の Web 制作・SEO 業務に Claude Code を導入し、専門エージェントの分業・自動化パイプライン・セキュリティ設計を構築した記録。

---

## 目次

1. [今できること](#今できること)
2. [気になってる機能](#気になってる機能)
3. [現在の課題](#現在の課題)
4. [セキュリティ設計](#セキュリティ設計)
5. [エージェント体制](#エージェント体制)
6. [スキル（スラッシュコマンド）](#スキルスラッシュコマンド)
7. [自動化パイプライン](#自動化パイプライン)
8. [プラグイン](#プラグイン)
9. [MCP（外部サービス連携）](#mcp外部サービス連携)
10. [ディレクトリ構成](#ディレクトリ構成)

## 今できること

1. コーディング → 本アップ

   - 認証情報は渡さずにプログラム中継で対応
   - 固定で依頼がある保守案件は少しずつ SKILL に落とし込み中（現在は仲庭ランキング、猟友会のみ）

2. ブログ執筆 → 指定サイトへ公開

   - クオリティ・信ぴょう性・レビュー制度・トークン消費量など調整中
   - 調べればわかる内容をあえて書かせて事実ベースで書けるか調査中（コーラゼロは何故 0 カロリーにできるのかなど..）

3. SEO 監視 →AIOSEO 調整

   - まだ言わないと何もできないのでブログのクオリティと同時進行で調整中
   - ここはブラウザを直接操作できる Cowork が向いているので分業予定

4. アクセス解析（Cowork）

   - ブラウザで GA4 を開いて指定条件で絞り込んだレポートを指定場所へ保存を顧客分作業してチャットワークに通知

5. Wordpress マニュアル作成（Cowork）

   - 谷上さんのベースを活用して調整中、ずれがおおくまだ使える状態ではない。

6. 平日昼に複数サイトから取得した AI 最新情報記事のまとめをチャットに送信（Cowork）

7. サポートにくるメールを取得して Notion に自動投稿でタスク化（削除予定）
   - （Notion タスク DB）
   - Cowork 出始めに意気揚々とやったがトークンの無駄

---

## 気になってる機能

- [Claude For Small Business](https://note.com/vesslabs/n/n882ba23cf7e2)

---

## 現在の課題

### トークン消費が多い

- エージェントの並列実行やスキルの連鎖実行でコンテキストが肥大化しやすい。特に `commander` が複数エージェントを起動する際、各エージェントへ渡すコンテキストが重複して積み上がるため、1 セッションあたりのトークン消費が大きい。

- 記事執筆するには、エージェントがそれぞれ独立して調査 → 執筆 → レビュー → 添削 → レビュー → 公開の手順を踏むので 1 記事生成に 5h トークンの 15%~20%を消費する

  - claude のレビュー制度が少し弱かったのでを codex5.5 にレビューを委託して記事の信ぴょう性を向上、claude トークンを節約

- Claude Code でエージェント、セキュリティ、スキルなどコツコツ育てているがエージェントのみ Claude Cowork への移植が難しい、スキルとセキュリティは zip などでインポートできる

- Cowork と Claude Code の使い分けがまだできていない
  - Cowork は computer use によるブラウザ操作が可能、Code はプログラム的な中継が必要

---

## セキュリティ設計

[`settings.json`](https://github.com/gucchi0421/.claude/blob/master/settings.json) と [`rules/security.md`](https://github.com/gucchi0421/.claude/blob/master/rules/security.md) で定義している。

### 1. 操作の完全禁止（deny）

Claude がどれだけ指示されても実行できないようハードブロックしている。

| 対象                 | 禁止パターン                                                           | 理由                                                   |
| -------------------- | ---------------------------------------------------------------------- | ------------------------------------------------------ |
| 機密ファイル読み取り | `Read(**/.env)` `Read(**/.env.*)` `Read(**/*.pem)` `Read(**/*secret*)` | API キー・証明書・パスワードを Claude の文脈に乗せない |
| 機密ファイル編集     | `Edit(**/.env)` `Edit(**/.env.*)`                                      | 環境変数ファイルの意図しない書き換えを防止             |
| CI/CD 編集           | `Edit(/.github/workflows/**)`                                          | ワークフロー改ざんによるサプライチェーン攻撃を防止     |
| 強制プッシュ         | `Bash(git push -f *)` `Bash(git push --force *)`                       | リモートの履歴破壊を防止                               |
| 履歴リセット         | `Bash(git reset --hard *)`                                             | 作業内容の意図しない消失を防止                         |
| 再帰削除             | `Bash(rm -rf *)`                                                       | ディレクトリごと誤削除するリスクを排除                 |
| 直接ネットワーク通信 | `Bash(curl *)` `Bash(wget *)`                                          | 任意 URL へのデータ送信・外部スクリプト取得を遮断      |

### 2. 実行前にユーザー確認（ask）

変更を本番環境や外部に反映する操作は、必ず人間が承認する。

| 操作                   | パターン                       |
| ---------------------- | ------------------------------ |
| ファイル書き込み・編集 | `Write` / `Edit`               |
| Git コミット           | `Bash(git commit*)`            |
| Git プッシュ           | `Bash(git push*)`              |
| npm パッケージ公開     | `Bash(npm publish*)`           |
| 本番デプロイ           | `Bash(wrangler pages deploy*)` |

### 3. 安全な操作は自動許可（allow）

確認コスト削減のため、破壊的操作を含まない読み取り・確認系は自動で実行できる。

`Read` / `Glob` / `Grep` / `WebFetch` / `WebSearch` / `Bash(ls)` / `Bash(find)` / `Bash(git status/diff/log)` / `Bash(* --version)` など。

### 4. 実行前後に割り込む自動ガード（フック）

#### `.env` の誤コミットを防ぐ（PreToolUse）

`git add` 直前に、ステージングエリアに `.env` が含まれていないかをチェックする。含まれていれば `exit 1` で強制中断し警告を表示する。

```sh
git diff --cached --name-only | grep -E '(^|/)\.env' \
  && echo '🚨 .env をステージしようとしています！' && exit 1 || exit 0
```

#### ファイル削除を 5 秒遅延させる（PreToolUse）

`rm` コマンド実行直前に 5 秒遅延させ、誤操作の取り消し猶予を確保する。（`rm -rf` は deny で別途完全禁止済み）

#### 作業内容を自動記録する（PostToolUse）

Edit・Write・rm が実行されるたびに [`log_work.py`](https://github.com/gucchi0421/.claude/blob/master/scripts/log_work.py) が自動起動し、以下を更新する。

- **セッションログ** `.claude/logs/work/YYYYMMDDHHMMSS_session.md` — 時刻・操作種別・diff を記録
- **デプロイ pending リスト** `.claude/logs/deploy/.pendings.md` — FTP アップロード待ちファイルを自動管理

### 5. 機密情報を Claude に見せずに外部接続する仕組み

**Claude（AI）は接続先のパスワード・API キーを「一切知らない」設計になっている。**

パスワードが AI の文脈に乗ると会話ログに残るリスクがある。そのため、接続情報は `.env` に分離し、Python スクリプトが実行時にのみ `os.environ` 経由で参照する。Claude は `.env` の「存在確認（`ls`）」だけ行い、中身は deny ルールで強制的に読めない。

#### FTP 接続（[`ftp_deploy.py`](https://github.com/gucchi0421/.claude/blob/master/scripts/ftp_deploy.py)）

1. 開発者が `.env` に `CLAUDE_FTP_HOST` / `CLAUDE_FTP_USERNAME` / `CLAUDE_FTP_PASSWORD` を記載（Claude は読まない）
2. Claude はパスマッピング（[`settings.ftp.json`](https://github.com/gucchi0421/.claude/blob/master/.claude/settings.ftp.json)）だけ書く。パスワードは含まれない
3. `/ftp-deploy` 実行時に `ftp_deploy.py` が `.env` を読み込み FTPS（暗号化通信）で接続
4. アップロード前に既存ファイルをリモートにバックアップしてからアップ

#### SSH 接続（[`settings.ssh.json`](https://github.com/gucchi0421/.claude/blob/master/.claude/settings.ssh.json)）

SSH は公開鍵認証を使い、パスワードを使わない設計。Claude が知るのは接続名（Host 名）だけ。
`allowed_dirs` でサーバー上の操作可能ディレクトリをホワイトリスト制限している。

```json
{
  "connection": "mysite",
  "config": "~/.ssh/config",
  "allowed_dirs": ["/var/www/html"]
}
```

#### その他 API キーの格納先

| サービス                 | 格納場所                                                       | Claude の関与                                                   |
| ------------------------ | -------------------------------------------------------------- | --------------------------------------------------------------- |
| Chatwork API             | プロジェクト直下 `.env`（`CLAUDE_CHATWORK_API_KEY`）           | 存在確認のみ                                                    |
| Google Analytics (GA4)   | `~/.claude/.env`（`CLAUDE_GCP_CREDENTIALS=/path/to/key.json`） | パスのみ知る。内容は読まない                                    |
| Google Sheets (SEO ログ) | `~/.claude/.env`（GCP 認証情報を共用）                         | 同上                                                            |
| WordPress ログイン情報   | `~/wp-credentials/[案件名].json`                               | Playwright でブラウザのログインフォームに入力。会話には戻さない |

### 6. コード品質・セキュリティルール

全プロジェクト共通で以下の規約を Claude に適用している。（[`rules/security.md`](https://github.com/gucchi0421/.claude/blob/master/rules/security.md)）

| 脆弱性               | 禁止                               | 必須対応                             |
| -------------------- | ---------------------------------- | ------------------------------------ |
| XSS                  | ユーザー入力をそのまま HTML 出力   | サニタイズ・エスケープ必須           |
| SQL インジェクション | 文字列結合でクエリ組み立て         | プリペアドステートメント必須         |
| 認証不備             | 認証チェックのバイパス             | 全リクエストで認証状態を検証         |
| シークレット漏洩     | API キー・パスワードのハードコード | 環境変数 / `wp-config.php` で管理    |
| CSRF                 | nonce なしのフォーム・Ajax         | nonce の付与と検証を必須化           |
| オープンリダイレクト | 入力 URL への無制限リダイレクト    | リダイレクト先をホワイトリストで制限 |

---

## エージェント体制

Claude に「役割」を持たせた専門エージェントを 18 種類定義している。
`commander` がユーザーのリクエストを受け取り、適切なエージェントへ自動で振り分ける構成。

### マネジメント系

| エージェント                                                                             | 役割                                                               | 定義ファイル             |
| ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------ | ------------------------ |
| [commander](https://github.com/gucchi0421/.claude/blob/master/agents/commander.md)       | 全体統括。タスクを分析し最適なエージェントへ自動振り分け・並列実行 | `agents/commander.md`    |
| [director](https://github.com/gucchi0421/.claude/blob/master/agents/director.md)         | 企画・要件定義・仕様書作成・施策優先順位付け                       | `agents/director.md`     |
| [pm](https://github.com/gucchi0421/.claude/blob/master/agents/pm.md)                     | タスク分解・工数見積・スケジュール管理・ボトルネック特定           | `agents/pm.md`           |
| [recorder](https://github.com/gucchi0421/.claude/blob/master/agents/recorder.md)         | セッション終了後に日報・作業サマリーを自動生成・保存               | `agents/recorder.md`     |
| [sales-bridge](https://github.com/gucchi0421/.claude/blob/master/agents/sales-bridge.md) | クライアントメールをディレクション用語に変換・回答文案作成         | `agents/sales-bridge.md` |

### Web 制作・開発系

| エージェント                                                                                     | 役割                                                                 | 定義ファイル                 |
| ------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------- | ---------------------------- |
| [coder](https://github.com/gucchi0421/.claude/blob/master/agents/coder.md)                       | 実装・バグ修正・コードレビュー・API 設計                             | `agents/coder.md`            |
| [designer](https://github.com/gucchi0421/.claude/blob/master/agents/designer.md)                 | HTML/CSS 実装・UI 改善・デザインシステム整備                         | `agents/designer.md`         |
| [design-analyst](https://github.com/gucchi0421/.claude/blob/master/agents/design-analyst.md)     | 競合サイトのデザイントレンド調査・ベンチマーク分析                   | `agents/design-analyst.md`   |
| [security-analyst](https://github.com/gucchi0421/.claude/blob/master/agents/security-analyst.md) | XSS・SQLi・依存パッケージ脆弱性チェック・リスクレポート生成          | `agents/security-analyst.md` |
| [wp-operator](https://github.com/gucchi0421/.claude/blob/master/agents/wp-operator.md)           | WordPress 管理画面操作（記事公開・プラグイン設定・バックアップ取得） | `agents/wp-operator.md`      |

### SEO・コンテンツ系

| エージェント                                                                                     | 役割                                                                  | 定義ファイル                 |
| ------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------- | ---------------------------- |
| [seo-analyst](https://github.com/gucchi0421/.claude/blob/master/agents/seo-analyst.md)           | キーワード調査・競合分析・3C 分析・SEO 課題の優先度付け               | `agents/seo-analyst.md`      |
| [seo-engineer](https://github.com/gucchi0421/.claude/blob/master/agents/seo-engineer.md)         | メタタグ・構造化データ・AIOSEO 設定・Core Web Vitals 改善             | `agents/seo-engineer.md`     |
| [writer](https://github.com/gucchi0421/.claude/blob/master/agents/writer.md)                     | SEO 記事・LP コピー・リライト・FAQ 執筆（品質パイプライン適用）       | `agents/writer.md`           |
| [article-reviewer](https://github.com/gucchi0421/.claude/blob/master/agents/article-reviewer.md) | 記事品質を多角的にスコアリング（80 点以上で合格）・改善フィードバック | `agents/article-reviewer.md` |
| [data-analyst](https://github.com/gucchi0421/.claude/blob/master/agents/data-analyst.md)         | GA4・Search Console のデータ分析・KPI 異常検知                        | `agents/data-analyst.md`     |

### ビジネス系

| エージェント                                                                         | 役割                                                 | 定義ファイル           |
| ------------------------------------------------------------------------------------ | ---------------------------------------------------- | ---------------------- |
| [accountant](https://github.com/gucchi0421/.claude/blob/master/agents/accountant.md) | 請求書・振替一覧の金額照合・未入金検出・見積概算作成 | `agents/accountant.md` |
| [ad-manager](https://github.com/gucchi0421/.claude/blob/master/agents/ad-manager.md) | Google/Meta 広告レポート分析・改善提案・予算配分     | `agents/ad-manager.md` |
| [notifier](https://github.com/gucchi0421/.claude/blob/master/agents/notifier.md)     | Chatwork への作業完了通知・承認依頼の自動送信        | `agents/notifier.md`   |

---

## スキル（スラッシュコマンド）

`/コマンド名` で呼び出す、再利用可能な自動化ワークフロー。
各スキルは独立した指示書（`SKILL.md`）で定義されており、複数のエージェントを組み合わせて動く。

### 全プロジェクト共通スキル

| コマンド                                                                                                    | 内容                                                                                  | 外部連携                 | 定義ファイル                        |
| ----------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- | ------------------------ | ----------------------------------- |
| [`/chatwork`](https://github.com/gucchi0421/.claude/blob/master/skills/chatwork/SKILL.md)                   | 指定ルームへメッセージ送信。`.env` の API キーを自動参照                              | Chatwork API             | `skills/chatwork/SKILL.md`          |
| [`/ftp-deploy`](https://github.com/gucchi0421/.claude/blob/master/skills/ftp-deploy/SKILL.md)               | 変更ファイルを FTP で本番へ自動アップ。バックアップ →pending 確認 → 実行の 3 ステップ | FTP サーバー             | `skills/ftp-deploy/SKILL.md`        |
| [`/ga4-fetch`](https://github.com/gucchi0421/.claude/blob/master/skills/ga4-fetch/SKILL.md)                 | GA4 Data API からデータ取得 → JSON 出力 → `data-analyst` へ渡す                       | Google Analytics         | `skills/ga4-fetch/SKILL.md`         |
| [`/seo-log`](https://github.com/gucchi0421/.claude/blob/master/skills/seo-log/SKILL.md)                     | SEO 作業履歴を Google スプレッドシートへ自動記録                                      | Google Sheets            | `skills/seo-log/SKILL.md`           |
| [`/ut-ai-news-report`](https://github.com/gucchi0421/.claude/blob/master/skills/ut-ai-news-report/SKILL.md) | 毎平日 12 時に 4 サイトを並列スクレイプ → カテゴリ分類 → Chatwork 自動投稿            | Chatwork                 | `skills/ut-ai-news-report/SKILL.md` |
| [`/wp-seo-manager`](https://github.com/gucchi0421/.claude/blob/master/skills/wp-seo-manager/SKILL.md)       | WordPress サイトの SEO 対策を一気通貫で自動化（調査 → 承認 → 実行 →Notion 記録）      | WP 管理画面 / Notion     | `skills/wp-seo-manager/SKILL.md`    |
| [`/wp-manual-create`](https://github.com/gucchi0421/.claude/blob/master/skills/wp-manual-create/SKILL.md)   | WP 管理画面をクロールしてスクショ付き PPTX マニュアルを自動生成                       | WP 管理画面 / PowerPoint | `skills/wp-manual-create/SKILL.md`  |

### Cowork 環境スキル（`.cowork/`）

Cowork（Windows デスクトップ共有環境）に接続した状態で使うスキル群。現在は運用途中。

| コマンド                                                                                                              | 内容                                                                                    | 定義ファイル                                 |
| --------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- | -------------------------------------------- |
| [`/ut-ga4-auto-report`](https://github.com/gucchi0421/.claude/blob/master/skills/.cowork/ut-ga4-auto-report/SKILL.md) | 毎月の GA4 アクセス解析レポートを全顧客分 PDF ダウンロードし、Chatwork へ通知・ZIP 送付 | `skills/.cowork/ut-ga4-auto-report/SKILL.md` |
| [`/ut-risona-matching`](https://github.com/gucchi0421/.claude/blob/master/skills/.cowork/ut-risona-matching/SKILL.md) | りそな振替一覧と請求書 PDF の金額照合・未入金検出                                       | `skills/.cowork/ut-risona-matching/SKILL.md` |

---

## 自動化パイプライン

### SEO 記事執筆パイプライン（品質保証付き）

Claude 単独での執筆は禁止し、必ず以下の順番で 3 エージェントが連携する。

```
seo-analyst  ──→  競合調査・検索意図分析
     ↓
  writer      ──→  調査結果ベースで執筆
     ↓
article-reviewer ──→  スコアリング（80点以上で合格）
     ↓ 不合格
  writer      ──→  フィードバックを受けて再執筆
     ↓ 合格
   完成
```

### WordPress SEO 対策パイプライン

全ての変更は承認後のみ実行される。実行前に必ずバックアップを取得。

```
ディレクター
  └── SEOエンジニア（audit + 競合調査 + 対策計画）
          ↓
  Excel レポート生成 → Chatwork で承認待ち
          ↓ Go サイン
  バックアップ取得（WPvivid）
          ↓
  SEOエンジニア（AIOSEO 設定変更）
  ├── ライター（本文追記・リライト・FAQ）  ← 並列実行
  └── コーダー（テーマ修正・diff 承認必須）
          ↓ 全完了
  Notion 記録 → Chatwork 完了通知 → 4 週間後に効果検証スケジュール設定
```

### FTP デプロイパイプライン

ファイルの編集・保存のたびに pending リストへ自動追記。まとめてデプロイできる。

```
ファイル編集（Edit/Write/rm）
  └── log_work.py（PostToolUse フック）が自動起動
          ↓
  .claude/logs/deploy/.pendings.md に追記
          ↓
  /ftp-deploy スキル呼び出し
  └── pending リストをユーザーに提示・承認
          ↓ 承認
  ftp_deploy.py がバックアップ → FTPS でアップロード
          ↓
  デプロイログ（.claude/logs/deploy/YYYYMMDDHHMMSS.md）を生成
```

### AI ニュース自動配信（スケジュール実行）

```
毎平日 12 時（スケジューラー起動）
  └── 4 サイトを並列フェッチ
      （ledge.ai / ai-news.dev / Zenn / Qiita）
          ↓
  カテゴリ分類（リリース / 開発 / ビジネス / ハード / 研究 / 政策）
          ↓
  各記事を 2 行要約 + URL にまとめる
          ↓
  Chatwork に自動投稿（/chatwork スキル経由）
```

---

## プラグイン

Claude Code のプラグインシステムで追加機能を拡張している。（[`settings.json`](https://github.com/gucchi0421/.claude/blob/master/settings.json) の `enabledPlugins` で管理）

### 言語サポート（LSP）

| プラグイン    | 機能                                        |
| ------------- | ------------------------------------------- |
| `php-lsp`     | PHP の構文チェック・補完・型エラー検出      |
| `gopls-lsp`   | Go 言語の補完・定義ジャンプ・エラー検出     |
| `pyright-lsp` | Python の型チェック・補完（Pyright ベース） |

### 開発ワークフロー

| プラグイン          | 機能                                                                                   |
| ------------------- | -------------------------------------------------------------------------------------- |
| `playwright`        | ブラウザ自動操作。WP 管理画面・GA4・Chatwork の操作に使用                              |
| `frontend-design`   | デザインクオリティの高いフロントエンドコードを生成する `/frontend-design` スキルを提供 |
| `commit-commands`   | `/commit` `/commit-push-pr` で Conventional Commits 形式のコミット・PR 作成を自動化    |
| `feature-dev`       | 機能開発のアーキテクチャ設計・コードベース調査・レビューを行う専門エージェントを追加   |
| `code-simplifier`   | 変更後のコードを自動的にレビュー・簡素化する `/simplify` スキルを提供                  |
| `github`            | GitHub の Issue・PR・ブランチ操作をエージェントから直接実行                            |
| `claude-code-setup` | Claude Code の設定最適化を提案する `/claude-automation-recommender` スキルを提供       |

### 外部ツール連携

| プラグイン             | 機能                                                                         |
| ---------------------- | ---------------------------------------------------------------------------- |
| `figma`                | Figma ファイルの読み書き・デザインシステムとコードの同期（Code Connect）     |
| `codex` (openai-codex) | OpenAI Codex CLI と連携。詰まった実装や大規模タスクを `/codex:rescue` で委譲 |
| `security-guidance`    | セキュリティレビュー・脆弱性チェックの専門的なガイダンスを提供               |

---

## MCP（外部サービス連携）

MCP（Model Context Protocol）で Claude から外部サービスを直接操作できる。

### 常時有効（クラウド MCP）

claude.ai 経由で接続しており、認証はブラウザの OAuth フローで完結する。

| MCP                     | 主な用途                                             |
| ----------------------- | ---------------------------------------------------- |
| **Notion**              | SEO 対策レポートの DB 管理・作業記録の保存           |
| **Figma**               | デザインファイルの読み書き・コンポーネント情報の参照 |
| **Google Drive**        | 資料・レポートファイルの参照・保存                   |
| **Gmail**               | メール確認・文案の送信準備                           |
| **Google Calendar**     | スケジュール確認・タスク期日管理                     |
| **Microsoft 365**       | Office 文書の操作・Teams 連携                        |
| **Adobe**               | 画像編集・ベクター変換・Firefly による生成           |
| **Canva**               | デザインテンプレートの生成・編集                     |
| **Ahrefs**              | SEO キーワード調査・被リンク分析                     |
| **MCP（ドメイン管理）** | DNS レコードの追加・削除・ドメイン購入               |

### プロジェクト有効（プラグイン経由）

| MCP                       | 主な用途                                                           |
| ------------------------- | ------------------------------------------------------------------ |
| **playwright**            | ブラウザ自動操作（WP 管理画面・GA4・Chatwork）                     |
| **context7**              | ライブラリ・フレームワークの最新ドキュメントをリアルタイム参照     |
| **memory**                | エンティティ・関係グラフとして情報を永続化。会話をまたいだ知識管理 |
| **figma（プラグイン版）** | Figma ファイルへのコメント投稿・ノード参照                         |

---

## ディレクトリ構成

```
.claude/
├── agents/                     # 専門エージェント定義（18種）
│   ├── commander.md
│   ├── director.md
│   ├── coder.md
│   └── ...
├── rules/                      # 全プロジェクト共通ルール
│   ├── code-styles/            # 言語別コーディング規約
│   │   ├── php.md
│   │   ├── typescript.md
│   │   └── ...
│   ├── security.md             # セキュリティルール
│   ├── git-workflow.md         # Git規約
│   └── persona.md              # Claude のキャラクター設定
├── scripts/                    # 自動化Pythonスクリプト群
│   ├── ftp_deploy.py           # FTPデプロイ（機密情報はos.environ経由）
│   ├── chatwork_send.py        # Chatwork送信
│   ├── ga4_fetch.py            # GA4データ取得
│   ├── seo_log.py              # SEO作業ログ → Googleスプレッドシート
│   ├── log_work.py             # PostToolUseフック：作業を自動記録
│   ├── add_mcp_to_setup.py     # MCPサーバー追加時に設定を自動反映
│   └── ...
├── skills/                     # スラッシュコマンド定義
│   ├── chatwork/SKILL.md
│   ├── ftp-deploy/SKILL.md
│   ├── ga4-fetch/SKILL.md
│   ├── seo-log/SKILL.md
│   ├── ut-ai-news-report/SKILL.md
│   ├── wp-manual-create/       # 複合スキル（scripts・references付き）
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   └── references/
│   ├── wp-seo-manager/         # 複合スキル（agents・references付き）
│   │   ├── SKILL.md
│   │   ├── agents/             # スキル専用サブエージェント
│   │   ├── references/         # 参照ドキュメント群
│   │   └── scripts/
│   └── .cowork/                # Cowork環境専用スキル（運用途中）
│       ├── ut-ga4-auto-report/SKILL.md
│       └── ut-risona-matching/SKILL.md
├── .claude/                    # プロジェクト固有の実行時データ
│   ├── logs/
│   │   ├── work/               # セッション作業ログ（PostToolUseで自動生成）
│   │   └── deploy/
│   │       └── .pendings.md    # FTPデプロイ待ちファイル一覧
│   ├── backup/                 # デプロイ前バックアップ
│   ├── settings.ftp.json       # ローカル→リモートパスマッピング
│   ├── settings.ssh.json       # SSH接続設定
│   ├── settings.ga4.json       # GA4プロパティ設定
│   └── settings.local.json     # ローカル専用パーミッション設定
├── CLAUDE.md                   # Claude へのメイン指示書
├── README.md                   # 本ファイル
└── settings.json               # Claude Code 設定（deny/ask/allow/hooks）
```
