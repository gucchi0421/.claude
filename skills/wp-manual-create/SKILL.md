---
name: wp-manual-create
description: >
  WordPressの更新マニュアルを自動作成するスキル。
  「マニュアルを作って」「WordPressのマニュアル」「WP更新手順書」「マニュアル作成」
  などの依頼で必ずこのスキルを使う。
disable-model-invocation: true
---

# WordPress 更新マニュアル自動生成スキル

---

## ⚠️ 絶対厳守ルール（全 STEP で常に適用）

- 認証情報ファイルの内容を**チャット・出力ファイル・ログに一切表示しない**
- WP 管理画面は**閲覧のみ**。投稿・設定変更・削除は絶対禁止
- フォーム入力は**ログインフォームのみ**
- 各画面へは**URL を直接入力**してナビゲート

---

## 🟢 START: 起動時の質問フロー

「マニュアルを作って」などの依頼を受けたら、**まず以下を順番に確認する。**
情報が揃うまで作業を開始しない。

### 質問 1: 認証情報ファイルの確認

以下のように聞く：

```
認証情報ファイルのパスを教えてください。
例: ~/wp-credentials/client-a.json

まだ作成していない場合は「まだ」と教えてください。
作成方法をご案内します。
```

→ パスが返ってきたら STEP 0 へ進む
→「まだ」の場合は以下を案内してから終了：

```
ターミナルで以下を実行して作成してください：

cat > ~/wp-credentials/[案件名].json << 'EOF'
{
  "site_name": "クライアント名",
  "wp_admin_url": "https://example.com/wp-admin/",
  "wp_username": "manual-user",
  "wp_password": "パスワード"
}
EOF

作成できたらもう一度「マニュアルを作って」と声をかけてください。
```

### 質問 2: 雛形 PPTX の確認

```
雛形PPTXのパスを教えてください。
例: ~/Desktop/_汎用_WP更新マニュアル.pptx
     ~/Desktop/_縦書_HP更新マニュアル_ver2.pptx
```

→ パスが返ってきたら STEP 0 へ進む

### 質問 3: 出力先の確認（省略可）

```
出力先を指定しますか？
指定しない場合はデスクトップに以下の名前で保存します：
~/Desktop/[サイト名]_更新マニュアル.pptx
```

→ 「そのままでいい」または返答なし → デフォルトで進む

---

## STEP 0: インプット検証

受け取った情報を検証する：

```python
import json, os

# 認証情報ファイルを読み込む（内容は表示しない）
cred_path = os.path.expanduser(credentials_file)
with open(cred_path) as f:
    creds = json.load(f)

# 必須項目チェック
assert 'wp_admin_url' in creds, "wp_admin_urlが見つかりません"
assert 'wp_username' in creds, "wp_usernameが見つかりません"
assert 'wp_password' in creds, "wp_passwordが見つかりません"
assert creds['wp_admin_url'].endswith('/'), "wp_admin_urlは/で終わる必要があります"

site_name = creds.get('site_name', 'クライアント')
admin_url  = creds['wp_admin_url']

# 出力パスを設定
output_pptx = os.path.expanduser(
    output_path if output_path
    else f"~/Desktop/{site_name}_更新マニュアル.pptx"
)

# スクリーンショット保存先を作成
ss_dir = os.path.expanduser("~/wp-manual-screenshots/")
os.makedirs(ss_dir, exist_ok=True)
```

検証 OK なら作業開始を宣言する：

```
✅ 情報を確認しました。マニュアル作成を開始します。
サイト: [site_name]
出力先: [output_pptx]
---
```

---

## STEP 1: 雛形 PPTX 解析

```bash
python ~/wp-manual-v2/scripts/analyze_template.py <template_pptx_path> \
  --output ~/wp-manual-screenshots/template_map.json
```

スライドの役割を判定してマップを作成する。判定ルール：

| テキストに含まれる語句              | 役割              |
| ----------------------------------- | ----------------- |
| ログイン / login / wp-admin         | `LOGIN_SLIDE`     |
| 目次 / contents                     | `TOC_SLIDE`       |
| 投稿 / 一覧 / 新規追加              | `POST_LIST_SLIDE` |
| タイトル / 本文 / 公開 / プレビュー | `POST_EDIT_SLIDE` |
| メディア / 画像 / アップロード      | `MEDIA_SLIDE`     |
| テキスト / 書式 / エディター        | `EDITOR_SLIDE`    |
| それ以外                            | `GENERIC_SLIDE`   |

---

## STEP 2: WP 管理画面ログイン

```
1. Chromeで {admin_url} を開く
2. ログインフォームにユーザー名・パスワードを入力
3. ログインボタンをクリック
4. ダッシュボードが表示されたことを確認
→ 認証情報の使用はここで終了（以降は一切参照しない）
```

ログイン失敗時：

```
ログインに失敗しました。
認証情報ファイルのURLとパスワードをご確認ください。
（内容はお伝えできません。ファイルを直接ご確認ください）
```

---

## STEP 3: サイト構成の巡回・スクリーンショット取得

各 URL に直接アクセスしてスクリーンショットを取得する。
保存先: `~/wp-manual-screenshots/`

| 優先度 | 画面            | URL                                  | SS 名                    |
| ------ | --------------- | ------------------------------------ | ------------------------ |
| 必須   | ダッシュボード  | `{admin_url}`                        | `ss_01_dashboard.png`    |
| 必須   | 投稿一覧        | `{admin_url}edit.php`                | `ss_02_post_list.png`    |
| 必須   | 投稿編集        | `{admin_url}post-new.php`            | `ss_03_post_edit.png`    |
| 必須   | メディア一覧    | `{admin_url}upload.php`              | `ss_04_media.png`        |
| 必須   | メディア追加    | `{admin_url}media-new.php`           | `ss_05_media_upload.png` |
| 必須   | 固定ページ一覧  | `{admin_url}edit.php?post_type=page` | `ss_06_page_list.png`    |
| 任意   | 外観 → メニュー | `{admin_url}nav-menus.php`           | `ss_07_menu.png`         |
| 任意   | プラグイン一覧  | `{admin_url}plugins.php`             | `ss_08_plugins.png`      |

### カスタム投稿タイプの検出

ダッシュボードのサイドバーから標準メニュー以外の項目を検出する。

標準メニュー（これ以外がカスタム投稿タイプ）:

```
ダッシュボード / 投稿 / メディア / 固定ページ / コメント
外観 / プラグイン / ユーザー / ツール / 設定
```

---

## STEP 4: カスタム投稿タイプの詳細把握

検出したカスタム投稿タイプごとに：

```
1. 一覧ページ: {admin_url}edit.php?post_type={slug}
   → SS保存: ss_custom_{slug}_list.png

2. 編集画面（既存記事があれば開く・新規作成しない）
   → SS保存: ss_custom_{slug}_edit.png

3. 編集画面でカスタムフィールドの種類を確認
   （テキスト / 画像 / ギャラリー / 繰り返し等）
```

---

## STEP 5: site_info.json を生成

```python
import json

site_info = {
    "site_name": site_name,
    "admin_url": admin_url,
    "editor_type": "gutenberg",  # 実際に確認した値
    "custom_posts": [
        {
            "name": "カスタム投稿名",
            "slug": "slug",
            "has_custom_fields": True,
            "fields": ["フィールド名1", "フィールド名2"],
            "screenshots": {
                "list": "ss_custom_{slug}_list.png",
                "edit": "ss_custom_{slug}_edit.png"
            }
        }
    ],
    "plugins_notable": ["All in One SEO", "Contact Form 7"]
}

with open(f"{ss_dir}site_info.json", "w", encoding="utf-8") as f:
    json.dump(site_info, f, ensure_ascii=False, indent=2)
```

---

## STEP 6: PPTX マニュアル生成

```bash
python ~/wp-manual-v2/scripts/generate_manual.py \
  --template <template_pptx_path> \
  --site-info ~/wp-manual-screenshots/site_info.json \
  --screenshots-dir ~/wp-manual-screenshots/ \
  --output <output_pptx>
```

---

## STEP 7: QA チェック

```bash
python ~/wp-manual-v2/scripts/qa_check.py <output_pptx>
```

QA 合格なら次へ。不合格なら問題箇所を修正してから次へ。

---

## STEP 8: 完了・ファイルを開く

```bash
# MacOS: Finderでファイルを表示
open -R <output_pptx>
```

完了メッセージを出力する：

```
✅ マニュアル作成が完了しました！

📄 出力ファイル: [output_pptx]
   （Finderで場所を開きました）

📋 作成内容:
  ・ログイン方法
  ・投稿の更新方法
  ・メディアのアップロード方法
  ・[カスタム投稿タイプ名] の更新方法（検出された場合）

⚠️ 確認をお願いする箇所:
  ・スクリーンショットが正しい画面か目視確認
  ・赤枠の注釈位置が合っているか確認
  ・必要に応じてPowerPointで微調整

🔒 セキュリティ:
  ・パスワードは記載されていません（●●●●で表示）
  ・作業後はWordPressの閲覧専用アカウントを削除してください
```

---

## エラー対応

| ケース                   | 対応                                                      |
| ------------------------ | --------------------------------------------------------- |
| ログイン失敗             | 認証ファイルの確認を案内（内容は表示しない）              |
| 管理画面に入れない       | 購読者権限でも管理画面に入れるか確認を案内                |
| スクリーンショットが空白 | ページ読み込み完了を待って再取得                          |
| PPTX が生成されない      | python-pptx のインストール確認: `pip install python-pptx` |
| カスタム投稿が見えない   | 購読者権限ではサイドバーに表示されない場合あり            |
