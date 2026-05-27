#!/usr/bin/env bash
# セッション終了時にプロジェクトの .claude/logs/summary/YYYYMMDD時分秒.md を書く
# Stop hook から呼ばれる: bash ~/.claude/scripts/session_summary.sh

set -euo pipefail

# プロジェクトの .claude ディレクトリを探す
find_project_claude() {
  local dir="$PWD"
  while [[ "$dir" != "/" ]]; do
    if [[ -d "$dir/.claude" ]]; then
      echo "$dir"
      return 0
    fi
    dir="$(dirname "$dir")"
  done
  return 1
}

PROJECT_ROOT=$(find_project_claude) || exit 0

SUMMARY_DIR="$PROJECT_ROOT/.claude/logs/summary"
mkdir -p "$SUMMARY_DIR"

TIMESTAMP=$(date +%Y%m%d%H%M%S)
SUMMARY_FILE="$SUMMARY_DIR/${TIMESTAMP}.md"

# 今日の work ログを収集
TODAY=$(date +%Y%m%d)
WORK_LOG=$(find "$PROJECT_ROOT/.claude/logs/work" -name "${TODAY}*" 2>/dev/null | sort | xargs cat 2>/dev/null || echo "")

if [[ -z "$WORK_LOG" ]]; then
  exit 0
fi

PROMPT="以下の作業ログを読んで、このセッションの作業サマリーをMarkdown形式で書いてください。

## 出力形式
\`\`\`markdown
# セッションサマリー YYYY-MM-DD HH:MM

## 実施した作業
- 箇条書きで簡潔に

## 変更したファイル
- ファイルパスと変更内容を簡潔に

## 残課題・次回やること
- あれば記載（なければ「なし」）
\`\`\`

Markdownのみ返してください。説明文は不要です。

## 作業ログ
$WORK_LOG"

RESULT=$(GEMINI_CLI_TRUST_WORKSPACE=true gemini -p "$PROMPT" --output-format json 2>/dev/null \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('response',''))" 2>/dev/null || echo "")

if [[ -z "$RESULT" ]]; then
  # Gemini が使えない場合は work ログをそのまま保存
  {
    echo "# セッションサマリー $(date '+%Y-%m-%d %H:%M')"
    echo ""
    echo "## 作業ログ（raw）"
    echo "$WORK_LOG"
  } > "$SUMMARY_FILE"
  exit 0
fi

# コードブロックを除去して保存
echo "$RESULT" | python3 -c "
import sys, re
text = sys.stdin.read()
match = re.search(r'\`\`\`(?:markdown)?\s*([\s\S]*?)\`\`\`', text)
if match:
    print(match.group(1).strip())
else:
    print(text.strip())
" > "$SUMMARY_FILE"
