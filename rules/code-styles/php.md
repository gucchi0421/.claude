---
paths:
  - "**/*.php"
---

# PHP コーディングスタイル

**既存ソースコードの PHP 記述から PHP バージョンが古いことを推測できる場合は、下記の規則は必ずしも適応するべきではなく、既存のソースコードに合わせること**

## 命名規則

- クラス名: PascalCase（ファイル名と 1 対 1 対応、PSR-4）
- メソッド名: camelCase（小文字始まり）
- 変数・プロパティ: snake_case（`$snake_case`）
- 定数: UPPER_SNAKE_CASE

## 型（）

- すべてのメソッドに return type を明示する
- すべての引数に型ヒントを付ける
- `mixed` は最小限に留め、具体的な型 / union 型を優先する
- nullable は `?Type` または `Type|null` で明示する
- `never` を使える場面では積極的に使う

```php
public function build(): \WP_Query {}
public function setPerPage(int $per_page): self {}
public static function get(string $key, mixed $default = null): mixed {}
public static function abort(\Throwable $throwable): never {}
```

## クラス設計

- インターフェースを積極的に定義し、具象クラスに実装させる
- 共通処理は抽象クラスに集約し、`abstract` メソッドで契約を定義する
- プロパティは `private readonly` を基本とし、不変性を保つ
- ファクトリメソッドは `new(): self` の static メソッドで提供する

```php
public static function new(): self
{
    return new self();
}
```

- ビルダーパターンのメソッドチェーンは戻り値を `self` に統一する

```php
public function setPostType(string|array $post_type): self
{
    $this->args['post_type'] = $post_type;
    return $this;
}
```

## メソッド設計

- 1 メソッド = 1 責務
- 目安は 10〜30 行、長くても 50 行程度
- early return でネストを浅く保つ

```php
if (wp_is_post_autosave($post_id) || wp_is_post_revision($post_id)) {
    return;
}
```

## コメント

- ファイル冒頭にクラスの役割を複数行コメントで記述する
- メソッドには 1 行の docblock で責務を記述する
- インラインコメントは「何をしているか」ではなく「なぜそうしているか」を書く
- グローバルヘルパー関数には使用例をコメント内に示す

```php
/**
 * テーマ初期設定フッククラス
 * - WordPress 標準機能の有効／無効を制御する
 * - テーマサポート・セッション・抜粋設定などを集中管理
 */
class SetupTheme implements BootableWpHookInterface
```

## ユーティリティクラス

- メソッドはすべて `public static`
- 副作用なし（Pure Function）
- 引数・戻り値に型を付ける

## エラーハンドリング

- 例外はキャッチして意味のあるメッセージと共にログに記録する
- 開発環境と本番環境で出力内容を切り替える（スタックトレース vs 安全なメッセージ）
- `try/catch` ブロックの catch は `\Throwable` を捕捉する

## 静的解析

- PHPStan レベル 8 相当を目標とする
- `declare(strict_types=1)` を全ファイルに付ける
