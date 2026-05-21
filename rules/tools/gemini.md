# Gemini CLI 連携ルール

## 基本コマンド

```bash
# 非インタラクティブ実行（headless モード）
GEMINI_CLI_TRUST_WORKSPACE=true gemini -p "<プロンプト>" --output-format json 2>/dev/null

# 疎通確認
GEMINI_CLI_TRUST_WORKSPACE=true gemini -p "ping" --output-format json 2>/dev/null
```

- `GEMINI_CLI_TRUST_WORKSPACE=true` は必須（未設定だと trusted directory エラーで終了する）
- `2>/dev/null` で "Ripgrep not available" 等の stderr 警告を除去する
- `--output-format json` を付けると `{ "response": "...", "stats": {...} }` 形式で返る

## レスポンス構造

```json
{
  "session_id": "...",
  "response": "<モデルの回答テキスト>",
  "stats": { "models": { ... }, "tools": { ... } }
}
```

`response` フィールドだけ取り出す場合は Python で処理する：

```bash
GEMINI_CLI_TRUST_WORKSPACE=true gemini -p "$PROMPT" --output-format json 2>/dev/null \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('response',''))"
```

---

## 注意事項

- Gemini CLI はエージェントとして動作し、ファイルシステムへのアクセス・シェル実行も行う
- `.env` 等の機密ファイルを含むディレクトリで実行する場合は注意する
- モデルは自動選択（gemini-3-flash-preview 等）され、タスク内容によって切り替わる
