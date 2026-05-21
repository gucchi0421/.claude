#!/usr/bin/env bash
# Gemini CLI にレビューを委託し、構造化サマリーだけ返す。全ログはファイル保存する。
# Usage: review_gemini.sh "<article_content>" "<extra_instructions>"

set -euo pipefail

ARTICLE="${1:-}"
EXTRA="${2:-}"
LOG_DIR="$(pwd)/.codex/logs"
mkdir -p "$LOG_DIR"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
LOG_FILE="${LOG_DIR}/gemini-review-${TIMESTAMP}.log"

if [[ -z "$ARTICLE" ]]; then
  echo "Usage: $0 <article_content> [extra_instructions]" >&2
  exit 1
fi

PROMPT="以下の記事をレビューしてください。

---
${ARTICLE}
---

${EXTRA}

レビュー完了後、**必ず最後に**以下の JSON ブロックだけを出力してください（他のテキストは JSON の前に置くこと）：

\`\`\`json
{
  \"score\": <0-100の整数>,
  \"pass\": <true|false (80点以上でtrue)>,
  \"summary\": \"<全体評価を1〜2文で>\",
  \"issues\": [
    {
      \"severity\": \"high|medium|low\",
      \"category\": \"事実誤認|SEO|構成|文章品質|その他\",
      \"message\": \"<指摘内容>\"
    }
  ],
  \"improvement\": \"<writerへの改善指示を具体的に>\"
}
\`\`\`"

# Gemini が利用可能か確認（応答チェック）
if ! GEMINI_CLI_TRUST_WORKSPACE=true gemini -p "ping" --output-format json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d.get('response') else 1)" 2>/dev/null; then
  echo "{\"score\": null, \"pass\": false, \"summary\": \"Gemini利用不可\", \"issues\": [], \"improvement\": \"\", \"log_file\": \"\", \"fallback\": true}"
  exit 2
fi

# Gemini 実行・全ログ保存
GEMINI_CLI_TRUST_WORKSPACE=true gemini -p "$PROMPT" --output-format json 2>/dev/null | tee "$LOG_FILE" || true

# JSON レスポンスから response フィールドを抽出し、その中の ```json ブロックを取り出す
JSON=$(python3 -c "
import sys, json, re
try:
    data = json.load(open('${LOG_FILE}'))
    response = data.get('response', '')
    m = re.search(r'\`\`\`json\s*(.*?)\s*\`\`\`', response, re.DOTALL)
    print(m.group(1) if m else '')
except Exception:
    print('')
" 2>/dev/null)

if [[ -z "$JSON" ]]; then
  echo "⚠️  JSON の抽出に失敗したのだ。生ログを確認してほしいのだ: ${LOG_FILE}" >&2
  echo "{\"score\": null, \"pass\": false, \"summary\": \"JSON抽出失敗\", \"issues\": [], \"improvement\": \"\", \"log_file\": \"${LOG_FILE}\"}"
  exit 1
fi

# log_file フィールドを注入して返す
echo "$JSON" | python3 -c "
import sys, json
data = json.load(sys.stdin)
data['log_file'] = '${LOG_FILE}'
print(json.dumps(data, ensure_ascii=False, indent=2))
"
