# トークン効率化

## 委任の原則

- 1〜2 ファイルの読み取り → Claude が直接対応
- 300 行超のファイル調査 → **Serena** の `get_symbols_overview` + `find_symbol` を使う
- コードベース全体の探索 → **Serena** に委任（Explore より優先）
- 50KB 超のコード分析 → **Serena** に委任

## Serena を使うべき操作

コーディングタスクでは以下の代替を徹底する：

| 禁止（非効率） | Serena の代替 |
|---|---|
| `Read` でファイル全文 | `get_symbols_overview` → `find_symbol(include_body=True)` |
| `Edit` でファイル編集 | `replace_symbol_body` / `replace_content` |
| `grep` → `Read` で確認 | `find_symbol` + `find_referencing_symbols` |

- コーディングタスク開始時に必ず `mcp__serena__initial_instructions` を呼ぶ
- Serena で読んだファイルは `Edit` ではなく Serena の編集ツールで変更する

## Serena が未インストールの場合

セッション開始時に Serena MCP が使えない場合は、インストールを提案する：

```bash
# Serena のインストール確認
claude mcp list | grep serena

# なければユーザーに確認してからインストール
claude mcp add --scope user serena uvx serena
```

インストール後にオンボーディング手順（`onboarding` ツール呼び出し）を実行する

## 出力の削減

- 自明なコードに説明コメントを付けない
- 「〜しました」「〜します」等の確認メッセージを省略する
- 実行前後のファイル全文を出力しない（diff のみ）

## コンテキスト保護

- コンテキスト使用率が高くなったら `/compact` を提案する
- 長い調査結果はサブエージェントで取得して要約を受け取る
