---
name: chatwork
description: >
  Chatwork の指定ルームにメッセージを送信するスキル。
  ~/.claude/scripts/chatwork_send.py を使い、プロジェクト直下の .env から API キーを読む。
---

# Chatwork 送信スキル

## トリガー

```
/chatwork <room_id> <<EOF
メッセージ本文
EOF
```

例：
```
/chatwork rid311735252 <<EOF
作業が完了しました！
確認をお願いします。
EOF
```

## 実行コマンド

```bash
python3 ~/.claude/scripts/chatwork_send.py <room_id> <<EOF
メッセージ本文
EOF
```

## 前提確認

実行前に以下を確認する：

1. **`.env` の存在確認** — プロジェクトルート直下に `.env` があり `CLAUDE_CHATWORK_API_KEY` が設定されているか
   - ※ `.env` の中身は読まない。`ls` でファイルの存在のみ確認する
2. **room_id の確認** — `/chatwork` の直後に続く数値または `rid` プレフィックス付き文字列をルームIDとして使う

## room_id の解釈

| 入力 | 使用するルームID |
|---|---|
| `rid311735252` | `311735252` |
| `311735252` | `311735252` |

## エラー対応

| エラー | 対処 |
|---|---|
| `.env` がない / キーがない | プロジェクトルートに `CLAUDE_CHATWORK_API_KEY=<token>` を追記するよう案内 |
| 401 Unauthorized | API キーが無効。Chatwork の設定画面でトークンを確認するよう案内 |
| 404 Not Found | ルームIDが間違っているか、アクセス権がない |
