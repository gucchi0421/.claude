#!/usr/bin/env bash
# Stop hook: プロジェクトの .claude/logs/summary/YYYYMMDD.md に当日の作業を上書き保存する
# Gemini不使用・work logをそのまま整形するだけ

set -euo pipefail

# プロジェクトの .claude ディレクトリを探す
find_project_root() {
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

PROJECT_ROOT=$(find_project_root) || exit 0

SUMMARY_DIR="$PROJECT_ROOT/.claude/logs/summary"
mkdir -p "$SUMMARY_DIR"

TODAY=$(date +%Y%m%d)
SUMMARY_FILE="$SUMMARY_DIR/${TODAY}.md"

WORK_DIR="$PROJECT_ROOT/.claude/logs/work"
WORK_LOG=$(find "$WORK_DIR" -name "${TODAY}*" 2>/dev/null | sort | xargs cat 2>/dev/null || echo "")

if [[ -z "$WORK_LOG" ]]; then
  exit 0
fi

# 操作一覧を抽出（### HH:MM - Action(file) の行だけ）
OPERATIONS=$(echo "$WORK_LOG" | grep '^### ' || echo "（操作なし）")

# 変更ファイル一覧を抽出（重複除去）
CHANGED_FILES=$(echo "$WORK_LOG" | grep '^### ' \
  | sed 's/^### [0-9:]\+ - [A-Za-z]\+(\(.*\))$/\1/' \
  | grep -v '^$' \
  | sort -u \
  || echo "（なし）")

PROJECT_NAME=$(basename "$PROJECT_ROOT")

{
  echo "# 作業サマリー $(date '+%Y-%m-%d') — ${PROJECT_NAME}"
  echo ""
  echo "## 操作ログ"
  echo ""
  echo "$OPERATIONS"
  echo ""
  echo "## 変更ファイル"
  echo ""
  echo "$CHANGED_FILES" | while read -r f; do
    echo "- \`$f\`"
  done
  echo ""
  echo "---"
  echo "_最終更新: $(date '+%H:%M:%S')_"
} > "$SUMMARY_FILE"
