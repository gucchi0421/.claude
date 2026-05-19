# WP管理画面 巡回ルート詳細

## URL構造の基本

すべてのURLは `{admin_url}` をベースとする。
例: `https://example.com/wp-admin/` → `{admin_url}`

ログイン後は**URLを直接入力**してナビゲート（サイドバークリックは最小限にする）。

---

## 巡回ルート一覧

### フェーズ1: 全体把握

| # | 画面 | URL | 取得情報 | SS名 |
|---|---|---|---|---|
| 1 | ダッシュボード | `{admin_url}` | サイドバーメニュー全項目のリスト | `ss_01_dashboard.png` |

**ダッシュボードで必ずやること:**
- サイドバーの全メニュー項目を記録
- 標準メニュー以外 = カスタム投稿タイプとして記録

標準メニューリスト:
```
ダッシュボード / Dashboard
投稿 / Posts
メディア / Media
固定ページ / Pages
コメント / Comments
外観 / Appearance
プラグイン / Plugins
ユーザー / Users
ツール / Tools
設定 / Settings
```

---

### フェーズ2: 標準機能の確認

| # | 画面 | URL | 取得情報 | SS名 |
|---|---|---|---|---|
| 2 | 投稿一覧 | `{admin_url}edit.php` | 投稿の一覧UI・操作ボタンの位置 | `ss_02_post_list.png` |
| 3 | 投稿編集画面 | `{admin_url}post-new.php` | エディタ種類・フィールド構成 | `ss_03_post_edit.png` |
| 4 | メディアライブラリ | `{admin_url}upload.php` | メディア管理UI | `ss_04_media_library.png` |
| 5 | メディアアップロード | `{admin_url}media-new.php` | アップロードUI | `ss_05_media_upload.png` |
| 6 | 固定ページ一覧 | `{admin_url}edit.php?post_type=page` | ページ構成・テンプレート使用有無 | `ss_06_page_list.png` |

**エディタ種類の判定:**
- Gutenbergエディタ: 「ブロックを追加」ボタンまたは `/` コマンドが存在
- クラシックエディタ: 「ビジュアル」「テキスト」タブが存在
- Elementor/Divi等のページビルダー: 「〇〇で編集」ボタンが存在

---

### フェーズ3: カスタム投稿タイプの確認

フェーズ1で検出したカスタム投稿タイプごとに実施。

カスタム投稿タイプのURL構造:
```
一覧: {admin_url}edit.php?post_type={post_type_slug}
新規: {admin_url}post-new.php?post_type={post_type_slug}
```

**post_type_slug の特定方法:**
サイドバーのメニューリンクにカーソルを当て、ブラウザのステータスバーに表示されるURLの `post_type=` 以降の値を確認する。

| # | 画面 | URL | SS名 |
|---|---|---|---|
| A | カスタム投稿一覧 | `{admin_url}edit.php?post_type={slug}` | `ss_custom_{slug}_list.png` |
| B | カスタム投稿編集 | 既存記事の編集URLを開く | `ss_custom_{slug}_edit.png` |

**編集画面で確認すること:**
- タイトル・本文フィールドの有無
- ACFカスタムフィールドの有無と種類
  - テキスト系: text, textarea, number
  - メディア系: image, gallery, file
  - 選択系: select, checkbox, radio, true/false
  - 複合系: repeater（繰り返し）, flexible_content
- アイキャッチ画像の有無
- カテゴリ・タグの有無

---

### フェーズ4: 任意確認項目

クライアントが使用する可能性がある場合のみ確認。

| 条件 | 画面 | URL | SS名 |
|---|---|---|---|
| メニュー管理が必要 | 外観→メニュー | `{admin_url}nav-menus.php` | `ss_07_menu.png` |
| ウィジェット使用 | 外観→ウィジェット | `{admin_url}widgets.php` | `ss_08_widget.png` |
| お問い合わせフォーム | CF7等の管理ページ | プラグイン依存 | `ss_09_form.png` |
| SEO設定 | AIOSEOまたはYoast | プラグイン依存 | スキップ可 |

---

## ACFフィールドグループの確認（管理者権限がある場合）

```
URL: {admin_url}edit.php?post_type=acf-field-group
```

アクセスできれば:
- フィールドグループ名と適用先を記録
- 各グループの編集画面でフィールドタイプを確認（**保存・変更は禁止**）

アクセスできなければ（編集者権限等）:
- 編集画面に表示されるフィールドから種類を推測する

---

## スクリーンショット撮影のコツ

1. **ブラウザは1280px幅に統一**する（スライドへの挿入時に縦横比が一定になる）
2. **サイドバーが表示された状態で撮影**する（メニュー構成が分かるように）
3. **ログイン画面はパスワード欄が空の状態で撮影**する（入力前のスクリーンショット）
4. **編集画面は新規作成（空）の状態で撮影**する（既存データが映らないように）

---

## スクリーンショット命名規則

```
ss_01_dashboard.png           # ダッシュボード
ss_02_post_list.png           # 投稿一覧
ss_03_post_edit.png           # 投稿編集画面
ss_04_media_library.png       # メディアライブラリ
ss_05_media_upload.png        # メディアアップロード画面
ss_06_page_list.png           # 固定ページ一覧
ss_07_menu.png                # メニュー管理（任意）
ss_08_widget.png              # ウィジェット（任意）
ss_custom_{slug}_list.png     # カスタム投稿一覧
ss_custom_{slug}_edit.png     # カスタム投稿編集画面
```
