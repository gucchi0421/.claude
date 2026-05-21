#!/usr/bin/env bash
# 記事レビューの振り分けスクリプト。優先順位: Codex > Gemini > article-reviewer(Claude)
# Usage: article_review.sh "<article_content>" "<extra_instructions>"
# Exit codes:
#   0: レビュー成功（JSON を stdout に出力）
#   2: 全エンジン利用不可（"fallback": true の JSON を stdout に出力）→ article-reviewer エージェントに切り替える

set -euo pipefail

ARTICLE="${1:-}"
EXTRA="${2:-}"
SCRIPT_DIR="$(dirname "$0")"

if [[ -z "$ARTICLE" ]]; then
  echo "Usage: $0 <article_content> [extra_instructions]" >&2
  exit 1
fi

# 1. Codex → 失敗したら Gemini に自動フォールバック（article_review_codex.sh が内部処理）
RESULT=$(bash "${SCRIPT_DIR}/article_review_codex.sh" "$ARTICLE" "$EXTRA" 2>&1)
EXIT_CODE=$?

if [[ $EXIT_CODE -eq 0 ]]; then
  echo "$RESULT"
  exit 0
fi

# 2. Codex・Gemini 両方 NG → article-reviewer へのフォールバック指示を返す
echo "{\"score\": null, \"pass\": false, \"summary\": \"Codex・Gemini両方利用不可\", \"issues\": [], \"improvement\": \"\", \"log_file\": \"\", \"fallback\": true}"
exit 2
