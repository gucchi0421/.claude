# 認証情報ファイルのセットアップガイド

## ファイル構成

```
~/wp-credentials/
├── .gitignore        ← このフォルダ自体をGit管理外に
├── client-a.json
├── client-b.json
└── ...
```

## JSONファイルのフォーマット

```json
{
  "site_name": "株式会社〇〇",
  "wp_admin_url": "https://example.com/wp-admin/",
  "wp_username": "admin",
  "wp_password": "your-password-here"
}
```

## セットアップ手順

### 1. フォルダを作成する

```bash
mkdir -p ~/wp-credentials
```

### 2. .gitignoreを設定する（既存プロジェクト管理している場合）

```bash
echo "wp-credentials/" >> ~/.gitignore
```

または各プロジェクトの `.gitignore` に追記：
```
wp-credentials/
*.credentials.json
```

### 3. ファイルのパーミッションを制限する（Mac/Linux）

```bash
chmod 600 ~/wp-credentials/client-a.json
```

## Coworkでの渡し方

Coworkのチャットに以下のように指示する：

```
WordPressのマニュアルを作成してください。
認証情報ファイル: ~/wp-credentials/example-site.json
雛形PPTX: ~/Documents/manual-template.pptx
```

**NG例（やってはいけないこと）：**
```
# ❌ チャットに直接貼り付けない
URL: https://example.com/wp-admin/
ユーザー名: admin
パスワード: password123
```

## セキュリティチェックリスト

- [ ] `wp-credentials/` フォルダが `.gitignore` に含まれている
- [ ] ファイルをDropbox・iCloud等のクラウドストレージと同期していない
- [ ] チャット画面にパスワードを貼り付けていない
- [ ] 完了後もファイルを安全な場所に保管している（使い回し可）
