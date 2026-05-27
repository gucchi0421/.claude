#!/usr/bin/env bash
# セッション終了時に振り返りを行い、ルール改善提案をJSONで保存する
# Stop hook から呼ばれる: bash ~/.claude/scripts/session_review.sh

set -euo pipefail

RULES_DIR="$HOME/documents/dotfiles/packages/claude/.claude/rules"
LOGS_DIR="$HOME/.claude/logs"
PROPOSALS_JSON="$LOGS_DIR/pending_proposals.json"

mkdir -p "$LOGS_DIR"

# 今日のセッションログを収集
TODAY=$(date +%Y%m%d)
SESSION_LOGS=$(find ".claude/logs/work" -name "${TODAY}*_session.md" 2>/dev/null | sort | tail -1)

if [[ -z "$SESSION_LOGS" || ! -f "$SESSION_LOGS" ]]; then
  exit 0
fi

SESSION_CONTENT=$(cat "$SESSION_LOGS")
if [[ -z "$(echo "$SESSION_CONTENT" | grep -v '^#' | grep -v '^$')" ]]; then
  exit 0
fi

# 既存ルールの概要を収集
RULES_SUMMARY=$(find "$RULES_DIR" -name "*.md" | while read -r f; do
  echo "=== $(basename "$f") ==="
  head -20 "$f"
  echo ""
done)

PROMPT="あなたはClaudeの動作改善を分析する専門家です。
以下のセッションログを分析して、Claudeのルールファイルに追加・修正すべき内容を提案してください。

## 分析の観点
1. ユーザーが修正・指摘した行動パターンはあったか
2. 繰り返し発生した非効率な操作はあったか
3. 新しいワークフローや操作パターンが確立されたか
4. 既存ルールと矛盾する行動があったか

## 出力形式（JSONのみ返す）
{
  \"has_proposals\": true/false,
  \"proposals\": [
    {
      \"target_file\": \"rules/_core/session-start.md など相対パス\",
      \"type\": \"add|update|create\",
      \"summary\": \"提案の一行説明\",
      \"reason\": \"なぜこの変更が必要か\",
      \"content\": \"追加・変更するMarkdownの内容\"
    }
  ]
}

提案がない場合は has_proposals: false で proposals は空配列にしてください。
JSONのみ返し、説明文は不要です。

## 今日のセッションログ
$SESSION_CONTENT

## 既存ルールの概要
$RULES_SUMMARY"

RESULT=$(GEMINI_CLI_TRUST_WORKSPACE=true gemini -p "$PROMPT" --output-format json 2>/dev/null \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('response',''))" 2>/dev/null || echo "")

if [[ -z "$RESULT" ]]; then
  exit 0
fi

# JSON抽出・検証
JSON=$(echo "$RESULT" | python3 -c "
import sys, re, json
text = sys.stdin.read()
# コードブロック内のJSONを抽出
match = re.search(r'\`\`\`(?:json)?\s*([\s\S]*?)\`\`\`', text)
if match:
    text = match.group(1).strip()
# パース確認
data = json.loads(text)
if data.get('has_proposals'):
    print(text)
" 2>/dev/null || echo "")

if [[ -z "$JSON" ]]; then
  exit 0
fi

# 保存（次セッション開始時にClaudeが読む）
echo "$JSON" > "$PROPOSALS_JSON"
