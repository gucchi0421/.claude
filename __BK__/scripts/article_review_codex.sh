#!/usr/bin/env bash
# Codex にレビューを委託し、構造化サマリーだけ返す。全ログはファイル保存する。
# Usage: article_review_codex.sh "<article_content>" "<extra_instructions>"

set -euo pipefail

ARTICLE="${1:-}"
EXTRA="${2:-}"
LOG_DIR="$(pwd)/.codex/logs"
mkdir -p "$LOG_DIR"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
LOG_FILE="${LOG_DIR}/codex-review-${TIMESTAMP}.log"

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

# Codex が利用可能か確認（レート制限・障害チェック）
if ! codex doctor --summary --ascii --no-color &>/dev/null; then
  # Gemini にフォールバック
  exec bash "$(dirname "$0")/article_review_gemini.sh" "$ARTICLE" "$EXTRA"
fi

# Codex 実行・全ログ保存（exit code が非0でも続行する）
codex exec "$PROMPT" 2>&1 | tee "$LOG_FILE" || true

# JSON ブロック抽出
JSON=$(awk '/^```json/{found=1; next} /^```/{if(found) exit} found{print}' "$LOG_FILE")

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
