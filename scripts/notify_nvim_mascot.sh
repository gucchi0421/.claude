#!/usr/bin/env bash
# neovim の全セッションにマスコットイベントを送る
# 使い方:
#   notify_nvim_mascot.sh show [id] [char]
#   notify_nvim_mascot.sh hide [id]
#
# stdin から Claude Code の hook JSON を受け取り、エージェント名を自動判定する

ACTION="${1:-show}"
ID="${2:-}"
CHAR="${3:-}"

SOCK_DIR="$HOME/.cache/nvim/claude_mascot"

if [ ! -d "$SOCK_DIR" ]; then
  exit 0
fi

# stdin から hook JSON を読み取ってエージェント名を抽出
HOOK_JSON=""
if [ -t 0 ]; then
  : # 端末から直接呼ばれた場合はスキップ
else
  HOOK_JSON=$(cat 2>/dev/null)
fi

# エージェント名を決定（優先順位: 引数 > hook JSON の agent_name > デフォルト）
if [ -z "$CHAR" ] && [ -n "$HOOK_JSON" ]; then
  AGENT_NAME=$(echo "$HOOK_JSON" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    # agent_name フィールドを探す
    name = data.get('agent_name') or data.get('agentName') or data.get('agent') or ''
    print(name.lower().strip())
except:
    print('')
" 2>/dev/null)
  CHAR="${AGENT_NAME:-claude}"
fi

[ -z "$CHAR" ] && CHAR="claude"
[ -z "$ID"   ] && ID="$CHAR"

# JSON を構築
if [ "$ACTION" = "show" ]; then
  MSG="{\"action\":\"show\",\"id\":\"$ID\",\"char\":\"$CHAR\"}"
else
  MSG="{\"action\":\"hide\",\"id\":\"$ID\"}"
fi

# ディレクトリ内の全 .sock ファイルに送信（複数 nvim セッション対応）
for sock_file in "$SOCK_DIR"/*.sock; do
  [ -f "$sock_file" ] || continue
  SOCK_PATH=$(cat "$sock_file" 2>/dev/null)
  [ -z "$SOCK_PATH" ] && continue
  [ -S "$SOCK_PATH" ] || continue
  echo "$MSG" | socat - UNIX-CONNECT:"$SOCK_PATH" 2>/dev/null || true
done

exit 0
