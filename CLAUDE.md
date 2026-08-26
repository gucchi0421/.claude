# CLAUDE.md

# コア設定（全セッション必須）

@./claude/rules/\_core/persona.md
@./claude/rules/\_core/output-format.md
@./claude/rules/\_core/session-start.md
@./claude/rules/\_core/token-efficiency.md

# Git 規約

@./claude/rules/workflows/git-workflow.md

# セキュリティ

@./claude/rules/\_core/security.md

# 外部ツール連携

@./claude/rules/tools/codex.md
@./claude/rules/tools/gemini.md

## 概要

WordPress カスタムテーマ。PHP 8.2 / WordPress 6.0+ 対象。

## 作業ルール

### 変更前の確認

一定量以上の変更を伴う場合は、Plan モードで変更内容を検証してから実装する。

### コメント

ソースコードには以下を必ず含める：

- クラスの役割と使い方
- メソッドの意図
- 複雑な処理の説明

### コミットメッセージ

日本語で簡潔に何をしたか書く。変更が複数ある場合はメインのみ記載し省略してよい。

### バージョン記録

機能追加・変更を行った際は `VERSION.md` に記録する。

## コマンド

```bash
# Sass コンパイル + Browser-Sync
make dev type=style        # style.scss 監視
make dev type=include      # include.scss 監視

# 静的解析・リファクタリング
make stan                  # PHPStan（結果: storage/logs/phpstan/phpstan.log）
make rector                # Rector 確認（dry-run）
make rector-fix            # Rector 適用

# Composer（PHP 8.2 固定）
make composer c="install"
```

## アーキテクチャ

### 起動フロー

`functions.php` → `bootstrap/app.php`（App クラス）→ `HooksAutoLoader` が `app/` を再帰スキャン → `BootableWpHookInterface` 実装クラスの `boot()` を自動実行。

### Hook の追加

`app/Hooks/` に `BootableWpHookInterface` を実装したクラスを置くだけで自動起動する。`add_action` / `add_filter` は `boot()` に書く。

### 設定

`config/` の PHP ファイルが中心。`config('キー.サブキー')` でどこからでも参照できる。案件固有のカスタマイズは主にここ（`cms.php`, `acf.php`, `assets.php` 等）を編集する。

### テンプレート（views/）

Blade 未使用の PHP テンプレート。ロジックはファイル上部にまとめ、描画部分と分離する。グローバル関数（`bootstrap/functions.php` 定義）経由で呼び出す。描画系関数は `the_○○` と命名する。

### app/ の役割分担

| ディレクトリ  | 役割                                      |
| ------------- | ----------------------------------------- |
| `Hooks/`      | WordPress hook 登録                       |
| `Presenters/` | View 向けデータ組み立て                   |
| `Services/`   | 汎用処理（Config, Logger, Query, CSV 等） |
| `Helpers/`    | 小型ユーティリティ                        |
| `Project/`    | 案件固有の使い捨て実装                    |

## 注意事項

- `vendor/` は git 管理に含まれている（デプロイ先に composer 環境がないため）
- npm / package.json は存在しない。Sass・Browser-Sync・Concurrently はグローバルインストール前提（`npx` で実行）
- デプロイ先は Xserver（PHP 8.2 固定）
