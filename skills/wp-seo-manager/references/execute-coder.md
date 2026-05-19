# execute-coder.md（コーダー担当）

**前提: ディレクターからバックアップ完了の連絡とcontext.mdを受け取ってから着手する。**
**すべての変更はdiffを提示してディレクター経由でユーザー承認を得てから実行する。**

---

## 1. functions.phpへのJSON-LD直接埋め込み

AIOSEOのスキーマ機能でカバーできない構造化データを埋め込む場合に実施。

### 手順

1. WP管理画面 → 外観 → テーマファイルエディター → functions.php を開く
2. 現在のコードを確認し、既存のJSON-LD出力がないかチェック
3. 以下の形式でdiffを作成してディレクターに提示:

```
【変更対象】
ファイル: wp-content/themes/[テーマ名]/functions.php
追加箇所: ファイル末尾

【追加内容】
add_action('wp_head', function() {
  if (is_front_page()) {
    echo '<script type="application/ld+json">';
    echo json_encode([/* plan.mdで生成したJSON-LD */], JSON_UNESCAPED_UNICODE);
    echo '</script>';
  }
});
```

4. 承認を受けてから「ファイルを更新」で保存
5. トップページのソース（`<head>`内）を確認してJSON-LDが出力されているかチェック

---

## 2. タイトル・ディスクリプションのべた書き削除

テーマがタイトルやメタをべた書きしていてAIOSEOと競合している場合に実施。
（SEOエンジニアのauditでテーマべた書きと確定した場合のみ）

### 手順

1. 対象ファイル（header.php等）を開いて該当箇所を特定
2. diffを作成してディレクターに提示:

```
【変更対象】
ファイル: wp-content/themes/[テーマ名]/header.php
行: XX〜XX行目

【変更前】
<title><?php echo get_the_title(); ?> | サイト名</title>
<meta name="description" content="固定のテキスト">

【変更後】
<?php /* タイトル・ディスクリプションはAIOSEOが出力するため削除 */ ?>
```

3. 承認後に変更を実行・保存
4. ページのソースを確認してAIOSEOのタグが正しく出力されているかチェック

---

## 3. PageSpeed改善（優先Cの場合）

### 画像最適化

- 対象画像をダウンロード → WebP変換 → 再アップロード
- またはWPプラグイン（Smush・EWWW等）の一括変換を実行
- プラグインの設定変更が必要な場合はdiffではなくスクリーンショットをディレクターに提示して承認を取る

### レンダリングブロックリソース対応

- auditで特定されたスクリプト・CSSを確認
- functions.phpでの `defer` / `async` 属性付与の場合はdiffを提示・承認後に実施

---

## 完了後の確認チェックリスト

- [ ] 変更後のファイルを再表示して意図通りに保存されているか
- [ ] 対象ページをブラウザで開いて表示崩れがないか
- [ ] ページのソース（`<head>`内）を確認して意図した出力になっているか
- [ ] Googleの構造化データテストでスキーマが認識されるか（JSON-LD追加の場合）

完了したらcontext.mdに変更記録を記載してディレクターに渡す。
