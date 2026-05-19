---
paths:
  - "**/*.php"
---

# WordPress テンプレートコーディングスタイル

## ロジックと描画の分離

- テンプレートファイルの冒頭にデータ準備のロジックをまとめる
- 描画部分（HTML）にビジネスロジックを混在させない
- 条件分岐・ループは必要最小限に留める
- 変数名は役割が分かる名前にし、意図が伝わりづらい場合はコメントを残す
- 関数はコメントブロックで詳細なコメントを残す
- 冗長な書き方は PHP8 系をベースに修正し可読性を保つ
- 変数の上書きは避ける（例: $img / $index などの再利用）

```php
<?php
// ここにロジック（データ準備）をまとめる
$post_id  = get_the_ID();
$post_cat = get_the_terms($post_id, 'news_cat');
$cat_name = (!is_wp_error($post_cat) && !empty($post_cat)) ? $post_cat[0]->name : '';
?>

<main class="p-news -single">
    <!-- ここは描画のみ -->
</main>
```

# セキュリティルール

## 出力エスケープ

- HTML 出力は必ずエスケープする。生の変数を直接 echo しない
- `htmlspecialchars($val, ENT_QUOTES, 'UTF-8', false)` または同等のラッパーを使う
- URL 出力は `esc_url()` を通す
- JavaScript へ値を渡す場合は `json_encode()` + `ENT_QUOTES` でエスケープする

## SQL

- 生の SQL 文字列結合は禁止。`$wpdb->prepare()` を必ず使う
- ユーザー入力を直接クエリに埋め込まない

## 入力値の検証

- `$_GET` / `$_POST` / `$_REQUEST` は必ずサニタイズしてから使う
- 期待する型・形式を明示的に検証する（`is_numeric()`, `filter_var()` 等）
- WordPress の関数を使う場合は `sanitize_text_field()`, `absint()`, `wp_kses()` 等を活用する

## CSRF

- フォーム送信には WordPress nonce を必ず付与する（`wp_nonce_field()` / `check_admin_referer()`）
- Ajax リクエストも nonce で検証する（`wp_verify_nonce()`）

## 権限チェック

- 管理系の処理は実行前に `current_user_can()` で権限を確認する
- 権限のないリクエストは早期リターンで処理を止める

```php
if (!current_user_can('edit_posts')) {
    return;
}
```

## ファイルアップロード

- アップロードファイルは拡張子・MIME タイプの両方を検証する
- `wp_check_filetype_and_ext()` を使用する
- アップロード先は Web ルート外か、直接実行できない場所にする

## エラーメッセージ

- 本番環境では内部エラーの詳細（スタックトレース・ファイルパス・DB 情報）をクライアントに返さない
- エラー ID のみ返し、詳細はサーバーログに記録する

## 外部リクエスト

- 外部 URL へのリクエストはホワイトリスト方式で許可する URL を制限する
- `CURLOPT_SSL_VERIFYPEER` を無効化しない
- タイムアウトを必ず設定する

## 設定・シークレット

- API キー・パスワード・シークレットはコードにハードコードしない
- 環境変数または `wp-config.php` に定義し、`config/` から参照する

## ファイルインクルード

- ユーザー入力をファイルパスに使用しない
- `include` / `require` に変数を使う場合は値を厳格に検証する
